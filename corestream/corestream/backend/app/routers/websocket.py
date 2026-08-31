"""
Router de WebSocket para Notificaciones en Tiempo Real.

Proporciona conexión WebSocket para:
- Recibir notificaciones en tiempo real
- Mantener actualización automática de cambios
- Escuchar eventos de Redis pub/sub
- Enviar pings periódicos para mantener la conexión viva
- Manejar reconexiones y desconexiones graciosas

El cliente se conecta a /ws/notifications/{user_id} y recibe eventos
cada vez que hay actividad relevante para ese usuario.
"""

from fastapi import APIRouter, WebSocketDisconnect, HTTPException, status, WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
import json
import redis.asyncio as redis
from datetime import datetime
import logging

from app.database import get_db
from app.models import User
from app.middleware.auth import get_current_user

# Configurar logging para WebSocket
logger = logging.getLogger(__name__)

# Router para WebSocket
router = APIRouter(tags=["WebSocket"])

# Conexión global a Redis (ajustar según configuración)
REDIS_URL = "redis://localhost:6379/0"


class ConnectionManager:
    """
    Gestor de conexiones WebSocket para notificaciones en tiempo real.
    
    Maneja múltiples conexiones concurrentes y distribuye mensajes
    usando Redis pub/sub como backend de mensajería.
    """

    def __init__(self):
        # Almacenar conexiones activas: {user_id: [websocket, ...]}
        self.active_connections: dict = {}
        self.redis_client = None

    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Acepta una conexión WebSocket y la registra.

        Args:
            websocket (WebSocket): Conexión WebSocket
            user_id (int): ID del usuario que se conecta
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"Usuario {user_id} conectado. Total conexiones: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Registra una desconexión WebSocket.

        Args:
            websocket (WebSocket): Conexión WebSocket
            user_id (int): ID del usuario
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"Usuario {user_id} desconectado")

    async def broadcast_to_user(self, user_id: int, data: dict):
        """
        Envía un mensaje a todas las conexiones de un usuario.

        Args:
            user_id (int): ID del usuario
            data (dict): Datos del mensaje
        """
        if user_id in self.active_connections:
            # Crear copia de la lista para evitar modificación durante iteración
            connections = self.active_connections[user_id].copy()
            for connection in connections:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.error(f"Error enviando mensaje a usuario {user_id}: {str(e)}")
                    # Intentar desconectar si hay error
                    try:
                        self.disconnect(connection, user_id)
                    except:
                        pass

    async def init_redis(self):
        """Inicializa conexión a Redis si no existe."""
        if not self.redis_client:
            self.redis_client = await redis.from_url(REDIS_URL)


# Instancia global del gestor de conexiones
manager = ConnectionManager()


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: int):
    """
    Endpoint WebSocket para recibir notificaciones en tiempo real.

    El cliente se conecta con: ws://host/ws/notifications/{user_id}
    Recibe mensajes JSON con formato:
    {
        "type": "notification|ping|error",
        "data": {...}
    }

    Args:
        websocket (WebSocket): Conexión WebSocket
        user_id (int): ID del usuario

    El servidor:
    - Valida que el usuario existe
    - Se suscribe al canal Redis del usuario
    - Escucha eventos del canal
    - Envía pings cada 30 segundos para mantener la conexión
    - Maneja reconexiones y desconexiones graciosas
    """
    db: AsyncSession = None

    try:
        # Inicializar Redis si es necesario
        await manager.init_redis()

        # Verificar que el usuario existe en base de datos
        db = get_db()
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning(f"Intento de conexión con usuario inexistente: {user_id}")
            return

        # Aceptar conexión y registrarla
        await manager.connect(websocket, user_id)

        # Crear nombre del canal Redis
        channel = f"user:{user_id}:notifications"

        # Suscribirse al canal de Redis
        pubsub = manager.redis_client.pubsub()
        await pubsub.subscribe(channel)

        # Enviar mensaje de bienvenida
        await websocket.send_json({
            "type": "connected",
            "message": f"Conectado exitosamente. Usuario ID: {user_id}",
            "timestamp": datetime.utcnow().isoformat()
        })

        logger.info(f"Usuario {user_id} suscrito al canal {channel}")

        # Crear tarea para enviar pings periódicos
        ping_task = asyncio.create_task(send_periodic_pings(websocket, user_id))

        try:
            # Escuchar mensajes del cliente (para heartbeat de cliente)
            while True:
                # Escuchar tanto mensajes de cliente como de Redis concurrentemente
                client_msg = asyncio.create_task(websocket.receive_text())
                redis_msg = asyncio.create_task(pubsub.get_message())

                done, pending = await asyncio.wait(
                    [client_msg, redis_msg],
                    timeout=1.0,
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Procesar mensaje del cliente (heartbeat)
                if client_msg in done:
                    try:
                        message = client_msg.result()
                        # El cliente puede enviar pong para confirmar conexión viva
                        if message:
                            data = json.loads(message)
                            if data.get("type") == "pong":
                                logger.debug(f"Pong recibido de usuario {user_id}")
                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        logger.error(f"Error procesando mensaje del cliente: {str(e)}")
                else:
                    client_msg.cancel()

                # Procesar mensaje de Redis (notificación)
                if redis_msg in done:
                    try:
                        message = redis_msg.result()
                        if message and message.get("type") == "message":
                            # Parsear y enviar notificación al cliente
                            notification_data = json.loads(message.get("data", "{}"))
                            await websocket.send_json({
                                "type": "notification",
                                "data": notification_data,
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            logger.info(f"Notificación enviada a usuario {user_id}")
                    except json.JSONDecodeError:
                        logger.error("Error decodificando mensaje de Redis")
                    except Exception as e:
                        logger.error(f"Error procesando mensaje de Redis: {str(e)}")
                else:
                    redis_msg.cancel()

        except WebSocketDisconnect:
            logger.info(f"WebSocket desconectado para usuario {user_id}")
        except Exception as e:
            logger.error(f"Error en WebSocket: {str(e)}")
        finally:
            # Cancelar tarea de pings
            ping_task.cancel()

    except Exception as e:
        logger.error(f"Error en conexión WebSocket: {str(e)}")
        await websocket.close(code=status.WS_1011_SERVER_ERROR)
    finally:
        # Limpiar recursos
        if user_id in manager.active_connections:
            manager.disconnect(websocket, user_id)

        if pubsub:
            await pubsub.close()

        if db:
            await db.close()


async def send_periodic_pings(websocket: WebSocket, user_id: int, interval: int = 30):
    """
    Envía pings periódicos para mantener la conexión WebSocket activa.

    Args:
        websocket (WebSocket): Conexión WebSocket
        user_id (int): ID del usuario
        interval (int): Intervalo en segundos entre pings (default: 30)
    """
    try:
        while True:
            await asyncio.sleep(interval)
            try:
                await websocket.send_json({
                    "type": "ping",
                    "message": "Heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
                logger.debug(f"Ping enviado a usuario {user_id}")
            except Exception as e:
                logger.error(f"Error enviando ping: {str(e)}")
                break
    except asyncio.CancelledError:
        logger.info(f"Tarea de pings cancelada para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error en envío de pings: {str(e)}")


# Función auxiliar para publicar notificaciones en Redis
async def publish_notification(user_id: int, notification_data: dict):
    """
    Publica una notificación a un usuario específico a través de Redis.

    Esta función es utilizada por los servicios de notificación para
    enviar eventos en tiempo real a usuarios conectados.

    Args:
        user_id (int): ID del usuario destino
        notification_data (dict): Datos de la notificación
    """
    try:
        redis_client = await redis.from_url(REDIS_URL)
        channel = f"user:{user_id}:notifications"
        await redis_client.publish(channel, json.dumps(notification_data))
        await redis_client.close()
    except Exception as e:
        logger.error(f"Error publicando notificación: {str(e)}")
