# Archivo de configuración de Redis para caché y sistema de notificaciones
# Proporciona funciones para conectar, publicar y suscribirse a canales Redis

import json
from typing import Any, Optional

import redis.asyncio as aioredis

from app.config import get_settings

# Variable global para almacenar la conexión a Redis
# Se inicializa en el evento startup de FastAPI
_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """
    Obtiene la instancia de conexión a Redis, inicializándola si es necesario.
    
    Esta función proporciona acceso a la conexión global de Redis, asegurando
    que solo existe una conexión durante toda la vida de la aplicación.
    
    Returns:
        aioredis.Redis: Instancia de cliente Redis asincrónico
        
    Raises:
        RuntimeError: Si la conexión a Redis no ha sido inicializada
        
    Ejemplo:
        redis = await get_redis()
        await redis.set("key", "value")
        value = await redis.get("key")
    """
    global _redis_client
    
    if _redis_client is None:
        raise RuntimeError(
            "Conexión a Redis no inicializada. "
            "Asegúrate de que startup_event se haya ejecutado correctamente."
        )
    
    return _redis_client


async def init_redis() -> None:
    """
    Inicializa la conexión a Redis desde la URL configurada.
    
    Esta función debe ser llamada en el evento startup de FastAPI para
    establecer la conexión a Redis antes de procesar solicitudes.
    
    La URL de Redis se obtiene de las variables de configuración.
    
    Raises:
        ConnectionError: Si no se puede conectar al servidor Redis
        
    Ejemplo en main.py:
        @app.on_event("startup")
        async def startup_event():
            await init_redis()
    """
    global _redis_client
    
    settings = get_settings()
    
    try:
        # Crear conexión a Redis con reintentos automáticos
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf8",
            decode_responses=True,
            health_check_interval=30,  # Verificar salud cada 30 segundos
        )
        
        # Verificar la conexión
        await _redis_client.ping()
        print("Conexión a Redis establecida correctamente")
    except Exception as e:
        print(f"Error al conectar a Redis: {e}")
        raise


async def close_redis() -> None:
    """
    Cierra la conexión a Redis de forma segura.
    
    Esta función debe ser llamada en el evento shutdown de FastAPI para
    liberar recursos y cerrar la conexión correctamente.
    
    Ejemplo en main.py:
        @app.on_event("shutdown")
        async def shutdown_event():
            await close_redis()
    """
    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        print("Conexión a Redis cerrada")


async def publish_message(channel: str, data: dict[str, Any]) -> int:
    """
    Publica un mensaje en un canal Redis para notificaciones en tiempo real.
    
    Esta función serializa datos a JSON y los envía a un canal Redis específico,
    permitiendo que múltiples suscriptores (como WebSockets) reciban el mensaje.
    
    Args:
        channel: Nombre del canal Redis donde publicar el mensaje
            Típicamente formato: "notifications:{user_id}", "updates:{resource_type}"
        data: Diccionario con datos a serializar y enviar
        
    Returns:
        int: Número de suscriptores que recibieron el mensaje
        
    Raises:
        RuntimeError: Si Redis no está conectado
        json.JSONDecodeError: Si los datos no pueden serializarse a JSON
        
    Ejemplo:
        # Notificar a un usuario cuando se le asigna un ticket
        await publish_message(
            f"notifications:{user_id}",
            {
                "type": "TICKET_ASSIGNED",
                "ticket_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Arreglar bug crítico",
            }
        )
    """
    redis = await get_redis()
    
    # Serializar los datos a JSON
    message = json.dumps(data)
    
    # Publicar en el canal y retornar número de suscriptores alcanzados
    subscribers_count = await redis.publish(channel, message)
    
    return subscribers_count


async def subscribe_channel(channel: str) -> aioredis.client.PubSub:
    """
    Se suscribe a un canal Redis para recibir mensajes en tiempo real.
    
    Esta función se utiliza típicamente en conexiones WebSocket para recibir
    notificaciones en tiempo real de eventos del servidor.
    
    Args:
        channel: Nombre del canal Redis a suscribirse
            Típicamente formato: "notifications:{user_id}"
            
    Returns:
        aioredis.client.PubSub: Objeto PubSub para escuchar mensajes
        
    Raises:
        RuntimeError: Si Redis no está conectado
        
    Ejemplo:
        # En un endpoint WebSocket
        pubsub = await subscribe_channel(f"notifications:{user_id}")
        async for message in pubsub.listen():
            if message["type"] == "message":
                notification = json.loads(message["data"])
                await websocket.send_json(notification)
    """
    redis = await get_redis()
    
    # Crear un objeto PubSub para escuchar en el canal
    pubsub = redis.pubsub()
    
    # Suscribirse al canal
    await pubsub.subscribe(channel)
    
    return pubsub


async def get_cached_value(key: str) -> Optional[Any]:
    """
    Obtiene un valor almacenado en caché desde Redis.
    
    Args:
        key: Clave para buscar en Redis
        
    Returns:
        El valor almacenado o None si la clave no existe
        
    Raises:
        RuntimeError: Si Redis no está conectado
    """
    redis = await get_redis()
    
    value = await redis.get(key)
    
    if value:
        try:
            # Intentar deserializar como JSON
            return json.loads(value)
        except json.JSONDecodeError:
            # Si no es JSON válido, retornar como string
            return value
    
    return None


async def set_cached_value(
    key: str,
    value: Any,
    ttl_seconds: Optional[int] = None
) -> bool:
    """
    Almacena un valor en caché en Redis con tiempo de expiración opcional.
    
    Args:
        key: Clave para almacenar
        value: Valor a almacenar (se serializa a JSON)
        ttl_seconds: Tiempo de vida en segundos (None para almacenamiento permanente)
        
    Returns:
        True si se almacenó correctamente
        
    Raises:
        RuntimeError: Si Redis no está conectado
    """
    redis = await get_redis()
    
    # Serializar el valor a JSON
    serialized_value = json.dumps(value) if not isinstance(value, str) else value
    
    # Almacenar en Redis con TTL opcional
    await redis.set(
        key,
        serialized_value,
        ex=ttl_seconds
    )
    
    return True


async def delete_cached_value(key: str) -> bool:
    """
    Elimina un valor del caché de Redis.
    
    Args:
        key: Clave a eliminar
        
    Returns:
        True si se eliminó, False si la clave no existía
        
    Raises:
        RuntimeError: Si Redis no está conectado
    """
    redis = await get_redis()
    
    result = await redis.delete(key)
    
    return result > 0
