
# Archivo de configuración de SQLAlchemy para operaciones de base de datos

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base

from app.config import get_settings

settings = get_settings()

# Asegurar que PostgreSQL use el controlador asíncrono asyncpg
database_url = settings.DATABASE_URL

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+asyncpg://", 1
    )
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
elif database_url.startswith("postgresql+psycopg2://"):
    database_url = database_url.replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://", 1
    )

# Crear el motor SQLAlchemy asíncrono
engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
)

# Crear la fábrica de sesiones asíncronas
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Clase base para los modelos ORM
Base = declarative_base()


def get_session_maker() -> async_sessionmaker:
    """Devuelve la fábrica de sesiones asíncronas."""
    return async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos por solicitud."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
