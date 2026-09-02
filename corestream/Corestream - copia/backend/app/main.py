# Archivo principal de la aplicación FastAPI
# Configura la aplicación, middleware, rutas, eventos de startup/shutdown y WebSockets

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import engine, Base, get_db
from app.redis_client import (
    init_redis,
    close_redis,
    subscribe_channel,
    publish_message,
)
from app.middleware import get_current_user
from app.schemas import TokenPayload

# Importar routers (estos se crearían en carpetas routers/)
# from app.routers import auth, users, applications, epics, tickets, subtasks, analytics, documents, notifications

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
    print("Iniciando aplicación CoreStream...")
    
    try:
        # Inicializar conexión a Redis para sistema de notificaciones
        await init_redis()
        print("Redis inicializado correctamente")
        
        # Crear tablas de base de datos si no existen
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("Tablas de base de datos inicializadas")
        
        print("Aplicación CoreStream iniciada exitosamente")
        
    except Exception as e:
        print(f"Error durante startup: {e}")
        raise
    
    # Ceder control a FastAPI
    yield
    
    # Evento de SHUTDOWN - Ejecuta cuando la aplicación se detiene
    print("Cerrando aplicación CoreStream...")
    
    try:
        # Cerrar conexión a Redis
        await close_redis()
        print("Redis cerrado correctamente")
        
        # Cerrar conexión a la base de datos
        await engine.dispose()
        print("Base de datos desconectada")
        
        print("Aplicación CoreStream cerrada correctamente")
        
    except Exception as e:
        print(f"Error durante shutdown: {e}")


# Crear instancia de la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API RESTful para gestión de aplicaciones, épicas, tickets y analítica de equipo",
    version="1.0.0",
    docs_url="/api/docs",  # Documentación Swagger UI
    redoc_url="/api/redoc",  # Documentación ReDoc
    openapi_url="/api/openapi.json",  # Esquema OpenAPI JSON
    lifespan=lifespan,
)


# Configurar CORS (Cross-Origin Resource Sharing)
# Permite solicitudes desde el frontend en localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los headers
)


# Incluir routers con prefijos de API
# Cada router maneja un dominio específico de la aplicación
# Estos routers se crearían en carpeta app/routers/

# router_auth = APIRouter(prefix="/api/auth", tags=["auth"])
# router_users = APIRouter(prefix="/api/users", tags=["users"])
# router_applications = APIRouter(prefix="/api/applications", tags=["applications"])
# router_epics = APIRouter(prefix="/api/epics", tags=["epics"])
# router_tickets = APIRouter(prefix="/api/tickets", tags=["tickets"])
# router_subtasks = APIRouter(prefix="/api/subtasks", tags=["subtasks"])
# router_analytics = APIRouter(prefix="/api/analytics", tags=["analytics"])
# router_documents = APIRouter(prefix="/api/documents", tags=["documents"])
# router_notifications = APIRouter(prefix="/api/notifications", tags=["notifications"])

# app.include_router(router_auth)
# app.include_router(router_users)
# app.include_router(router_applications)
# app.include_router(router_epics)
# app.include_router(router_tickets)
# app.include_router(router_subtasks)
# app.include_router(router_analytics)
# app.include_router(router_documents)
# app.include_router(router_notifications)


# Endpoint de salud para verificar que la API está funcionando
@app.get(
    "/api/health",
    tags=["Health"],
    summary="Verificar salud de la API",
    description="Endpoint para monitoreo que verifica si la API está funcionando correctamente"
)
async def health_check():
    """
    Verifica el estado de la API.
    
    Retorna un estado OK si la aplicación está funcionando correctamente.
    Se utiliza típicamente para health checks en orquestadores como Kubernetes.
    
    Returns:
        dict: Mensaje de estado con timestamp
    """
    from datetime import datetime
    
    return {
        "status": "ok",
        "message": "API CoreStream funcionando correctamente",
        "timestamp": datetime.now().isoformat(),
    }


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


# WebSocket para notificaciones en tiempo real
@app.websocket("/api/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """
    Endpoint WebSocket para recibir notificaciones en tiempo real.
    
    Los clientes se conectan a este endpoint y reciben notificaciones cuando se
    producen eventos relevantes (tickets asignados, preguntas, etc.).
    
    El cliente debe proporcionar un token JWT válido en la querystring:
    ws://localhost:8000/api/ws/notifications/user-id?token=jwt-token
    
    Args:
        websocket: Conexión WebSocket del cliente
        user_id: ID del usuario para el cual recibir notificaciones
        
    Raises:
        WebSocketDisconnect: Cuando el cliente desconecta
        
    Ejemplo de cliente JavaScript:
        const token = localStorage.getItem('access_token');
        const ws = new WebSocket(
            `ws://localhost:8000/api/ws/notifications/${userId}?token=${token}`
        );
        ws.onmessage = (event) => {
            const notification = JSON.parse(event.data);
            console.log('Notificación:', notification);
        };
    """
    # Extraer token del query string
    token = websocket.query_params.get("token")
    
    if not token:
        # Cerrar la conexión si no se proporciona token
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    try:
        # Validar el token JWT
        from app.middleware import verify_token
        
        token_data = verify_token(token)
        
        # Verificar que el usuario está accediendo sus propias notificaciones
        if token_data.sub != user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Aceptar la conexión WebSocket
        await websocket.accept()
        
        # Suscribirse al canal de notificaciones del usuario
        channel = f"notifications:{user_id}"
        pubsub = await subscribe_channel(channel)
        
        try:
            # Escuchar mensajes del canal Redis
            async for message in pubsub.listen():
                if message["type"] == "message":
                    # Enviar el mensaje al cliente WebSocket
                    await websocket.send_text(message["data"])
                    
        except WebSocketDisconnect:
            # Cliente desconectó
            await pubsub.unsubscribe(channel)
            print(f"Usuario {user_id} desconectado de notificaciones")
            
    except Exception as e:
        # Error en validación o suscripción
        print(f"Error en WebSocket: {e}")
        await websocket.close(code=status.WS_1011_SERVER_ERROR)


# Manejo de errores global para excepciones no capturadas
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Manejador global de excepciones para cualquier error no capturado.
    
    Registra la excepción y retorna una respuesta JSON con estado 500.
    
    Args:
        request: Solicitud HTTP que causó el error
        exc: Excepción no capturada
        
    Returns:
        JSONResponse: Respuesta con detalles del error
    """
    print(f"Error no manejado: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc) if settings.DEBUG else "Error interno",
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
