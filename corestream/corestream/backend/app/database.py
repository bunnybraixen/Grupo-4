# Archivo de configuración de SQLAlchemy para operaciones de base de datos
# Proporciona el motor async, sesiones y funciones de inyección de dependencias

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base

from app.config import get_settings

# Obtener la URL de conexión de la configuración
settings = get_settings()

# Crear el motor SQLAlchemy asincrónico
# El motor maneja la conexión a la base de datos con soporte para operaciones async/await
# echo=True imprime las sentencias SQL en logs (desactivar en producción)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_size=20,  # Número de conexiones a mantener en el pool
    max_overflow=10,  # Conexiones adicionales que se pueden crear cuando pool está lleno
)

# Crear una fábrica de sesiones asincrónicas
# AsyncSessionLocal se utiliza para crear sesiones para cada solicitud HTTP
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # No expira objetos después de un commit
    autoflush=False,  # Control manual de flush para mejor rendimiento
)

# Crear la clase base para todos los modelos ORM
# Todos los modelos de la base de datos heredarán de esta clase
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Generador asincrónico que proporciona sesiones de base de datos para inyección de dependencias.
    
    Esta función se utiliza como dependencia en endpoints FastAPI para proporcionar
    una sesión de base de datos. Garantiza que la sesión se crea al principio de la
    solicitud y se cierra correctamente al finalizar, incluso si ocurren errores.
    
    La sesión proporciona operaciones CRUD y transacciones para interactuar con
    la base de datos PostgreSQL.
    
    Yields:
        AsyncSession: Sesión de base de datos asincrónica para la solicitud actual
        
    Ejemplo en un endpoint:
        @app.get("/users/{user_id}")
        async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
            user = await db.get(User, user_id)
            return user
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            # La sesión se cierra automáticamente al salir del contexto
            await session.close()
