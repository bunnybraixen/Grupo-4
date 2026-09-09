"""
Router de WebSocket para Notificaciones en Tiempo Real.

El cliente se conecta a /api/ws/{user_id}?ticket=TICKET (ver websocket_notifications
más abajo para el porqué de un ticket y no el JWT directamente) y recibe
eventos cada vez que hay actividad relevante para ese usuario (asignaciones,
cambios de estado, preguntas, redirecciones) o cambios generales de tickets.

DISEÑO DE LA ESPERA (importante, ver nota histórica más abajo):

Por cada conexión se lanzan dos tareas de larga vida que compiten en
asyncio.wait(..., return_when=FIRST_COMPLETED):

  - _forward_redis_messages: espera con pubsub.get_message(timeout=N) hasta
    N segundos por un mensaje. Es una espera async real (delegada al socket
    de Redis), no un sondeo. Si no llega nada en ese intervalo, envía un
    ping — así el heartbeat y el reenvío de mensajes comparten una sola
    espera, sin una tarea de heartbeat aparte.

  - _listen_for_client: espera en bucle a que el cliente mande algo (p. ej.
    'pong') y, sobre todo, a que se desconecte. `receive_text()` levanta
    WebSocketDisconnect en cuanto el cliente cierra, que es justo la señal
    que usamos para liberar la conexión.

En cuanto una de las dos termina (desconexión, o un fallo de Redis), se
cancela la otra y se limpia todo en el `finally`. Ninguna de las dos tareas
se recrea en cada vuelta: viven mientras dura la conexión.

NOTA HISTÓRICA — por qué esto no era así:
Antes, cada iteración del bucle llamaba a pubsub.get_message() SIN timeout
(por defecto es 0.0, que pide una lectura no bloqueante e inmediata) y creaba
un par de tareas nuevas (receive_text/get_message) que se cancelaban en cada
vuelta. El resultado medido: 0 conexiones = ~0% de CPU, 3 conexiones inactivas
= ~104% de CPU, y la cifra no bajaba al cerrar los clientes porque
`receive_text()` se cancelaba antes de tener ocasión de recibir el mensaje de
desconexión, así que la corrutina nunca se enteraba de que debía terminar.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select

from app.config import get_settings
from app.database import get_session_maker
from app.models import User
from app.redis_client import (
    TICKETS_UPDATES_CHANNEL,
    consume_ws_ticket,
    user_notifications_channel,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

settings = get_settings()
REDIS_URL = settings.REDIS_URL

# Intervalo tanto del heartbeat como del máximo tiempo de espera por un
# mensaje de Redis antes de comprobar que la conexión sigue viva.
HEARTBEAT_INTERVAL_SECONDS = 30.0


class ConnectionManager:
    """
    Registro de conexiones activas, usado para diagnóstico y limpieza local.

    La entrega real de mensajes va por Redis pub/sub (publish_ticket_event),
    no por este registro: en producción, con varios workers de uvicorn, cada
    uno ve solo sus propias conexiones aquí, pero todos están suscritos a los
    mismos canales de Redis, así que la entrega funciona igual. No usar
    active_connections para nada que no sea contar/depurar conexiones locales.
    """

    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        self.active_connections.setdefault(user_id, []).append(websocket)
        logger.info(
            "Usuario %s conectado. Total conexiones: %d",
            user_id,
            len(self.active_connections[user_id]),
        )

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        conexiones = self.active_connections.get(user_id)
        if not conexiones:
            return
        with contextlib.suppress(ValueError):
            conexiones.remove(websocket)
        if not conexiones:
            del self.active_connections[user_id]
        logger.info("Usuario %s desconectado", user_id)

    async def init_redis(self) -> None:
        if not self.redis_client:
            self.redis_client = redis.from_url(REDIS_URL)

    async def publish_ticket_event(
        self, event_type: str, ticket_data: dict, target_user_id: str | None = None
    ) -> None:
        """
        Publica eventos de tickets para notificaciones en tiempo real.

        Args:
            event_type: Tipo de evento (TICKET_ASSIGNED, TICKET_STATUS_CHANGED, TIMER_SYNC)
            ticket_data: Datos del ticket
            target_user_id: ID del usuario destino (si aplica)
        """
        try:
            await self.init_redis()

            event_data = {
                "type": event_type,
                "data": ticket_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if target_user_id:
                channel = user_notifications_channel(target_user_id)
                await self.redis_client.publish(channel, json.dumps(event_data))
                logger.info("Evento %s publicado para usuario %s", event_type, target_user_id)

            await self.redis_client.publish(TICKETS_UPDATES_CHANNEL, json.dumps(event_data))

        except Exception:
            logger.exception("Error publicando evento %s", event_type)


manager = ConnectionManager()


async def _forward_redis_messages(pubsub, websocket: WebSocket, user_id: str) -> None:
    """
    Reenvía al cliente los mensajes de los canales suscritos; si no llega
    ninguno en HEARTBEAT_INTERVAL_SECONDS, envía un ping.

    El plazo del heartbeat se mide por reloj (deadline), no por número de
    llamadas a get_message(): con ignore_subscribe_messages=True, las
    confirmaciones de subscribe/unsubscribe TAMBIÉN devuelven None — igual que
    un timeout genuino — así que contar "None" como "no llegó nada" enviaba un
    ping de más justo al conectar (una confirmación por canal suscrito). Con
    un deadline explícito, esas confirmaciones solo acortan el timeout de la
    siguiente espera, sin adelantar el heartbeat.

    Termina propagando la excepción si Redis falla — eso hace que la tarea
    hermana (_listen_for_client) se cancele y la conexión se cierre, en vez de
    quedar viva sin poder entregar nada.
    """
    loop = asyncio.get_event_loop()
    deadline = loop.time() + HEARTBEAT_INTERVAL_SECONDS

    while True:
        remaining = deadline - loop.time()
        if remaining <= 0:
            await websocket.send_json({
                "type": "ping",
                "message": "Heartbeat",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            deadline = loop.time() + HEARTBEAT_INTERVAL_SECONDS
            continue

        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=remaining)

        if message is None:
            # Timeout genuino, o una confirmación de subscribe/unsubscribe
            # filtrada: en ambos casos, solo re-evaluamos el deadline.
            continue

        deadline = loop.time() + HEARTBEAT_INTERVAL_SECONDS

        try:
            notification_data = json.loads(message.get("data", "{}"))
        except json.JSONDecodeError:
            logger.error("Mensaje de Redis con JSON inválido en canal %s", message.get("channel"))
            continue

        canal = message.get("channel", "")
        if isinstance(canal, bytes):
            canal = canal.decode()

        await websocket.send_json({
            "type": "update" if canal == TICKETS_UPDATES_CHANNEL else "notification",
            "data": notification_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("Mensaje WS reenviado a usuario %s (canal %s)", user_id, canal)


async def _listen_for_client(websocket: WebSocket, user_id: str) -> None:
    """
    Espera indefinidamente mensajes del cliente. No necesitamos su contenido
    más allá de un posible 'pong'; lo que de verdad importa es que
    receive_text() levanta WebSocketDisconnect en cuanto el cliente cierra,
    que es la señal para terminar esta tarea y liberar la conexión.
    """
    while True:
        raw = await websocket.receive_text()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if data.get("type") == "pong":
            logger.debug("Pong recibido de usuario %s", user_id)


@router.websocket("/ws/{user_id}")
async def websocket_notifications(
    websocket: WebSocket, user_id: str, ticket: Optional[str] = Query(None)
) -> None:
    """
    Endpoint WebSocket para recibir notificaciones en tiempo real.

    El cliente se conecta con: ws://host/api/ws/{user_id}?ticket=TICKET

    Antes (plan 3.2) se conectaba con ?token=JWT_TOKEN — el JWT completo
    quedaba escrito en los logs de acceso de cualquier proxy delante de la
    app (Nginx incluido) durante los 30 minutos de vida del token. El cliente
    ahora cambia su access token por un ticket opaco de un solo uso llamando
    a POST /api/auth/ws-ticket antes de abrir el socket; ese ticket se borra
    de Redis en cuanto se consume aquí, así que aunque termine en un log ya
    es inútil para cuando alguien lo lea.
    """
    if not ticket:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Ticket no proporcionado")
        logger.warning("Intento de conexión sin ticket para usuario %s", user_id)
        return

    ticket_user_id = await consume_ws_ticket(ticket)
    if ticket_user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Ticket inválido o expirado")
        logger.warning("Ticket inválido o ya usado en conexión WebSocket para usuario %s", user_id)
        return

    if ticket_user_id != user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Ticket user mismatch")
        logger.warning("Ticket user mismatch: ticket=%s, solicitado=%s", ticket_user_id, user_id)
        return

    async with get_session_maker()() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        if result.scalar_one_or_none() is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Usuario no encontrado")
            logger.warning("Intento de conexión con usuario inexistente: %s", user_id)
            return

    await manager.init_redis()
    await manager.connect(websocket, user_id)

    channel = user_notifications_channel(user_id)
    pubsub = manager.redis_client.pubsub()
    await pubsub.subscribe(channel, TICKETS_UPDATES_CHANNEL)

    await websocket.send_json({
        "type": "connected",
        "message": f"Conectado exitosamente. Usuario ID: {user_id}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    logger.info("Usuario %s suscrito al canal %s", user_id, channel)

    redis_task = asyncio.create_task(_forward_redis_messages(pubsub, websocket, user_id))
    client_task = asyncio.create_task(_listen_for_client(websocket, user_id))

    try:
        await asyncio.wait({redis_task, client_task}, return_when=asyncio.FIRST_COMPLETED)
    except WebSocketDisconnect:
        pass
    finally:
        for task in (redis_task, client_task):
            if not task.done():
                task.cancel()
        # return_exceptions=True: no dejamos que un WebSocketDisconnect o un
        # fallo de Redis en una de las tareas impida limpiar la otra.
        resultados = await asyncio.gather(redis_task, client_task, return_exceptions=True)
        for resultado in resultados:
            if isinstance(resultado, Exception) and not isinstance(
                resultado, (WebSocketDisconnect, asyncio.CancelledError)
            ):
                logger.error("Error en tarea de WebSocket para usuario %s: %s", user_id, resultado)

        manager.disconnect(websocket, user_id)

        with contextlib.suppress(Exception):
            await pubsub.unsubscribe(channel, TICKETS_UPDATES_CHANNEL)
            await pubsub.close()

        logger.info("Usuario %s desconectado de notificaciones", user_id)
