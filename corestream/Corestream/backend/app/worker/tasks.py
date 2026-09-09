"""
ARQ worker tasks para el sistema de notificaciones de CoreStream.

Flujo:
  HTTP handler
      └─► notification_service.enqueue_notification()   [fire-and-forget]
                  └─► ARQ Redis queue
                              └─► deliver_notification()  [este archivo]
                                      ├─► redis.publish("corestream:user:{id}:notifications", …)
                                      └─► retry automático (max_tries=3, backoff=5 s)

El DB save ocurre ANTES de encolar (en notification_service.create_notification,
dentro de la sesión del caller) para mantener atomicidad con el ticket.
Este task solo hace la entrega en tiempo real vía Redis pub/sub.
"""

from __future__ import annotations

import json
import logging

import redis.asyncio as aioredis

from app.config import get_settings
from app.redis_client import user_notifications_channel

logger = logging.getLogger(__name__)
settings = get_settings()


async def deliver_notification(
    ctx: dict,
    *,
    user_id: str,
    notification_id: str,
    title: str,
    message: str,
    notification_type: str,
    ticket_id: str | None = None,
    created_at: str,
) -> None:
    """
    ARQ task: publica la notificación al canal Redis correcto para
    que el WebSocket la reenvíe al cliente en tiempo real.

    El canal `corestream:user:{user_id}:notifications` es el mismo al que
    `websocket.py` está suscrito, cerrando el circuito.

    Parámetros se pasan como keyword-only para claridad y para que ARQ
    los serialice correctamente en Redis.
    """
    redis: aioredis.Redis = ctx["redis"]

    # Publicar solo el contenido plano de la notificación.
    # websocket.py lo envolverá en {"type": "notification", "data": <este payload>}
    # antes de enviarlo al cliente WebSocket.
    payload = json.dumps({
        "id": notification_id,
        "type": notification_type,
        "title": title,
        "message": message,
        "ticket_id": ticket_id,
        "is_read": False,
        "created_at": created_at,
    })

    channel = user_notifications_channel(user_id)
    subscribers = await redis.publish(channel, payload)
    logger.info(
        "Notificación entregada | canal=%s | tipo=%s | suscriptores=%d",
        channel, notification_type, subscribers,
    )
