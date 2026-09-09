"""
Configuración del worker ARQ para CoreStream.

Para correr el worker:
    python -m arq app.worker.settings.WorkerSettings

En Docker Compose el servicio `worker` ejecuta este comando.
"""

from __future__ import annotations

import logging

from arq.connections import RedisSettings

from app.config import get_settings
from app.redis_client import ARQ_HEALTH_CHECK_KEY, ARQ_QUEUE_NAME
from app.worker.tasks import deliver_notification

logger = logging.getLogger(__name__)
settings = get_settings()


async def startup(ctx: dict) -> None:
    """Inicializa recursos del worker (el cliente Redis lo inyecta ARQ automáticamente)."""
    logger.info("ARQ worker iniciado")


async def shutdown(ctx: dict) -> None:
    logger.info("ARQ worker detenido")


class WorkerSettings:
    """Configuración central del worker ARQ."""

    functions = [deliver_notification]

    # ARQ usa su propia conexión Redis (ctx['redis']) para las tareas.
    # RedisSettings.from_dsn acepta URLs redis:// o rediss://
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

    # Nombre de cola propio (plan 6.5): debe coincidir con el
    # default_queue_name del pool creado en main.py, o el worker nunca ve
    # los jobs que encola la app.
    queue_name = ARQ_QUEUE_NAME

    # Concurrencia y reintentos
    max_jobs = 20
    job_timeout = 30        # segundos antes de matar el job
    max_tries = 3           # intentos máximos antes de marcar como fallido
    retry_delay = 5         # segundos entre reintentos

    on_startup = startup
    on_shutdown = shutdown

    # Los jobs fallidos se guardan en Redis por 24 h para diagnóstico
    keep_result_forever = False
    keep_result = 86_400

    # ARQ escribe la clave ARQ_HEALTH_CHECK_KEY en Redis cada vez que
    # transcurre este intervalo, con una expiración a juego. El healthcheck
    # de Docker (docker-compose.yml) comprueba que esa clave exista para
    # saber si el worker sigue vivo. El valor por defecto de ARQ es 3600s
    # (una hora) — demasiado lento para detectar un worker colgado a tiempo.
    health_check_interval = 30
    health_check_key = ARQ_HEALTH_CHECK_KEY
