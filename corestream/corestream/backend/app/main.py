# Archivo principal de la aplicación FastAPI
# Configura la aplicación, middleware, rutas, eventos de startup/shutdown y WebSockets

import logging
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from app.config import get_settings
from app.database import dispose_engine, get_session_maker
from app.logging_config import configure_logging
from app.middleware.request_id import RequestIDMiddleware, get_request_id
from app.redis_client import ARQ_QUEUE_NAME, close_redis, get_redis, init_redis

# Importar routers (estos se crearían en carpetas routers/)
# Mantenemos las importaciones individuales para asegurar que cada módulo cargue bien
from app.routers import (
    analytics,
    applications,
    auth,
    documents,
    epics,
    incidents,
    invitations,
    meetings,
    notifications,
    subtasks,
    support_tickets,
    ticket_redirection,
    tickets,
    uploads,
    users,
    websocket,
)
from app.services.notification_service import set_arq_pool

logger = logging.getLogger("corestream")

# Obtener configuración
settings = get_settings()


# Contexto de ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de contexto que controla el ciclo de vida de la aplicación FastAPI.
    
    Maneja eventos de startup (inicialización) y shutdown (cierre) de la aplicación.
    En startup se inicializan conexiones a recursos externos como BD y Redis.
    En shutdown se cierran correctamente todas las conexiones.
    
    Args:
        app: Instancia de FastAPI
        
    Yields:
        Control a FastAPI durante la ejecución
    """
    # Evento de STARTUP - Ejecuta cuando la aplicación inicia
    configure_logging(settings.LOG_LEVEL)
    logger.info("Iniciando aplicación CoreStream...")

    try:
        # Inicializar conexión a Redis para sistema de notificaciones
        await init_redis()
        logger.info("Redis inicializado correctamente")
    except Exception:
        logger.exception("Redis no disponible al arrancar")

    try:
        # Inicializar pool ARQ para encolar notificaciones.
        # default_queue_name debe coincidir con queue_name de WorkerSettings
        # (worker/settings.py) — de lo contrario el worker nunca ve estos jobs.
        arq_pool = await create_pool(
            RedisSettings.from_dsn(settings.REDIS_URL),
            default_queue_name=ARQ_QUEUE_NAME,
        )
        set_arq_pool(arq_pool)
        logger.info("ARQ pool inicializado correctamente")
    except Exception:
        logger.exception("ARQ pool no disponible")

    # El esquema lo gestiona SOLO Alembic (el comando del contenedor corre
    # "alembic upgrade head" antes de levantar uvicorn). Antes había DOS
    # mecanismos compitiendo: create_all() aquí Y las migraciones — con
    # --reload, cada recarga por un cambio de código volvía a ejecutar
    # create_all() contra el Postgres ya migrado, y en cuanto una migración
    # nueva intentaba crear una tabla que create_all ya había creado por su
    # cuenta, Alembic fallaba con "relation ya existe" en el SIGUIENTE
    # arranque limpio. Ocurrió de verdad al añadir la tabla invitations de
    # esta misma fase — no es hipotético.

    # Antes de aquí (plan 3.6) el arranque creaba SIEMPRE, sin condición, un
    # ADMIN con contraseña conocida (admin@example.com / Admin123!@#) —
    # publicada en este mismo repositorio. Ya no existe ningún seed de
    # usuarios en el arranque: el primer ADMIN se crea a mano, una vez, con
    # `python -m app.scripts.create_admin` (ver ese fichero). El resto de
    # usuarios se crean por invitación (POST /api/invitations).

    logger.info("Aplicación CoreStream iniciada")

    # Ceder control a FastAPI
    yield

    # Evento de SHUTDOWN - Ejecuta cuando la aplicación se detiene
    logger.info("Cerrando aplicación CoreStream...")

    try:
        # Cerrar pool ARQ
        from app.services.notification_service import get_arq_pool
        pool = get_arq_pool()
        if pool:
            await pool.close()
            logger.info("ARQ pool cerrado correctamente")

        # Cerrar conexión a Redis
        await close_redis()
        logger.info("Redis cerrado correctamente")

        # Cerrar conexión a la base de datos
        await dispose_engine()
        logger.info("Base de datos desconectada")

        logger.info("Aplicación CoreStream cerrada correctamente")

    except Exception:
        logger.exception("Error durante shutdown")


# Documentación de la API abierta y sin autenticar (plan fase 9): en
# producción se deshabilita del todo — no es información que deba quedar
# expuesta al dominio público.
_docs_enabled = settings.ENVIRONMENT != "production"

# Crear instancia de la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API RESTful para gestión de aplicaciones, épicas, tickets y analítica de equipo",
    version="1.0.0",
    docs_url="/api/docs" if _docs_enabled else None,
    redoc_url="/api/redoc" if _docs_enabled else None,
    openapi_url="/api/openapi.json" if _docs_enabled else None,
    lifespan=lifespan,
)

# request_id primero: los middlewares se ejecutan en orden inverso al de
# registro para la fase de request, así que registrarlo antes que CORS
# asegura que el id ya existe para cualquier log emitido más adentro.
app.add_middleware(RequestIDMiddleware)

# Configurar CORS (Cross-Origin Resource Sharing)
# Permite solicitudes desde el frontend en localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Métricas Prometheus en /metrics (plan fase 8). No debe quedar expuesto por
# el Nginx público — solo accesible dentro de la red interna/VM (ver
# docs/DEPLOYMENT.md, que no debe incluir una location para /metrics).
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


# Incluir routers con prefijos de API
# Cada router maneja un dominio específico de la aplicación
# Estos routers se crearían en carpeta app/routers/

app.include_router(auth.router, prefix="/api/auth")
app.include_router(users.router, prefix="/api/users")
app.include_router(invitations.router)  # prefijo embebido en el router: /api/invitations
app.include_router(applications.router, prefix="/api/applications")
app.include_router(epics.router, prefix="/api/epics") # Resulta en /api/epics/...
app.include_router(ticket_redirection.router)  # Ticket redirection endpoints: /api/tickets/... — MUST come before tickets.router
app.include_router(tickets.router, prefix="/api/tickets")
app.include_router(subtasks.router, prefix="/api/tickets/{ticket_id}/subtasks")
app.include_router(analytics.router, prefix="/api/analytics")
app.include_router(documents.router, prefix="/api/documents")
app.include_router(notifications.router, prefix="/api/notifications")
app.include_router(websocket.router, prefix="/api")  # WebSocket endpoints: /api/ws/...
app.include_router(uploads.router)  # prefijo embebido en el router: /api/uploads
app.include_router(support_tickets.router, prefix="/api/support-tickets")
app.include_router(incidents.router, prefix="/api")
app.include_router(meetings.router, prefix="/api")


# Endpoint raíz de salud — Railway lo usa como healthcheck en /health
@app.get("/health", tags=["Health"], include_in_schema=False)
async def health_check_root():
    return {"status": "ok", "service": "CoreStream API"}


# Endpoint de salud para verificar que la API está funcionando
@app.get(
    "/api/health",
    tags=["Health"],
    summary="Verificar salud de la API",
    description=(
        "Sonda de disponibilidad (readiness): comprueba PostgreSQL y Redis "
        "de verdad, no solo que el proceso esté vivo. Devuelve 503 si alguno "
        "de los dos falla, para que el orquestador pueda dejar de enrutar "
        "tráfico a esta instancia en vez de servir peticiones que van a fallar."
    ),
)
async def health_check() -> JSONResponse:
    """
    Antes este endpoint devolvía {"status": "ok"} sin comprobar nada — un
    contenedor con Postgres o Redis caídos pasaba por "sano" indefinidamente,
    y con --restart unless-stopped eso significa que solo se reinicia un
    proceso muerto, nunca uno que está vivo pero no puede servir peticiones.
    """
    from datetime import datetime, timezone

    checks: dict[str, str] = {}
    ok = True

    try:
        async with get_session_maker()() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"
        ok = False

    try:
        redis_client = await get_redis()
        await redis_client.ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {exc}"
        ok = False

    body = {
        "status": "ok" if ok else "degraded",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(status_code=200 if ok else 503, content=body)


# Endpoint raíz con información de la API
@app.get(
    "/api",
    tags=["Root"],
    summary="Información de la API",
    description="Retorna información general sobre la API CoreStream"
)
async def root():
    """
    Endpoint raíz que proporciona información sobre la API.
    
    Returns:
        dict: Información de la aplicación, versión y enlaces a documentación
    """
    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "API RESTful para gestión de aplicaciones, épicas y tickets",
        "documentation": "/api/docs",
        "redoc": "/api/redoc",
        "openapi_schema": "/api/openapi.json",
    }


# Manejo de errores global para excepciones no capturadas
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Manejador global de excepciones para cualquier error no capturado.

    Antes: logging.error(f"...: {exc}") sin exc_info — un 500 no dejaba
    traza alguna en los logs, solo el mensaje de la excepción. Los tres 500
    de MissingGreenlet de la fase 2 solo se vieron porque uvicorn los
    imprime por su cuenta; nuestro propio logging no ayudaba a diagnosticar.
    """
    logger.error(
        "Error no manejado en %s %s", request.method, request.url,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": "Se ha producido un error inesperado.",
            "request_id": get_request_id(),
        }
    )


# Punto de entrada para ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    
    # Ejecutar servidor Uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,  # Recargar automáticamente en cambios (desarrollo)
        log_level="info",
    )