# Configuración de SQLAlchemy para operaciones de base de datos.
#
# IMPORTANTE: este módulo NO debe tener efectos secundarios al importarse.
# El engine se crea de forma perezosa en la primera llamada a get_engine().
#
# Antes, el engine se construía a nivel de módulo con pool_size/max_overflow,
# lo que hacía imposible importar la aplicación sin un PostgreSQL disponible y
# obligaba a los tests a sustituir el módulo entero por un mock
# (sys.modules["app.database"] = MagicMock()). Eso dejaba la capa de acceso a
# datos sin cobertura real. Con la factoría perezosa, importar la app es
# gratis y los tests pueden inyectar su propia URL.

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

# Instancias perezosas. No se tocan al importar el módulo.
_engine: Optional[AsyncEngine] = None
_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def _build_engine(database_url: str) -> AsyncEngine:
    """
    Construye el engine asíncrono con las opciones adecuadas al dialecto.

    Las opciones de pool (pool_size, max_overflow, pool_pre_ping) solo aplican a
    backends con pool real. SQLite en memoria, usado por los tests unitarios,
    las rechaza, así que se omiten.
    """
    settings = get_settings()

    kwargs: dict = {
        "echo": settings.SQL_ECHO,
        "future": True,
    }

    if not database_url.startswith("sqlite"):
        kwargs.update(
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            # Verifica la conexión antes de usarla. Imprescindible cuando la
            # base de datos es remota o compartida y puede cerrar conexiones
            # ociosas por su cuenta: sin esto, la primera petición tras un
            # corte devuelve un 500 en lugar de reconectar.
            pool_pre_ping=True,
            pool_recycle=settings.DB_POOL_RECYCLE,
        )

    return create_async_engine(database_url, **kwargs)


def get_engine() -> AsyncEngine:
    """Devuelve el engine global, creándolo en la primera llamada."""
    global _engine

    if _engine is None:
        _engine = _build_engine(get_settings().DATABASE_URL)

    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Devuelve la fábrica de sesiones global, creándola en la primera llamada."""
    global _session_maker

    if _session_maker is None:
        _session_maker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,  # No expira objetos después de un commit
            autoflush=False,  # Control manual de flush
        )

    return _session_maker


def configure_engine(database_url: str) -> AsyncEngine:
    """
    Reemplaza el engine global por uno apuntando a `database_url`.

    Pensado para los tests de integración, que necesitan dirigir la aplicación
    a una base de datos efímera antes de levantarla. En producción no se usa:
    el engine se deriva de la configuración.
    """
    global _engine, _session_maker

    _engine = _build_engine(database_url)
    _session_maker = None  # se reconstruye contra el nuevo engine

    return _engine


async def dispose_engine() -> None:
    """Cierra el engine global y libera el pool. Se llama en el shutdown."""
    global _engine, _session_maker

    if _engine is not None:
        await _engine.dispose()

    _engine = None
    _session_maker = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia de FastAPI que proporciona una sesión de base de datos por petición.

    Garantiza que la sesión se cierra al terminar la petición, incluso si el
    endpoint lanza una excepción.

    Ejemplo en un endpoint:
        @app.get("/users/{user_id}")
        async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
            return await db.get(User, user_id)
    """
    async with get_session_maker()() as session:
        yield session
