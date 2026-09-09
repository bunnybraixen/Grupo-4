"""
Fixtures compartidas para los tests unitarios.

Estos tests cubren lógica pura: máquina de estados de tickets, validaciones de
esquemas y cálculo de analítica. Usan SQLite en memoria, que es suficiente
porque no dependen de comportamiento específico de PostgreSQL.

Los tests que sí ejercitan la aplicación completa (HTTP, RBAC, contratos de
API) viven en tests/integration/ y corren contra PostgreSQL real.

NOTA HISTÓRICA: este fichero sustituía app.database, redis, arq y psycopg2 por
MagicMock antes de importar la aplicación. Eso hacía que 154 tests pasaran en
verde sin ejercitar nada de la capa de datos, y por eso no detectaron ninguno
de los fallos encontrados en la auditoría. El mock era necesario porque
app.database creaba el engine al importarse; ahora la creación es perezosa
(app/database.py: get_engine), así que importar la app no requiere PostgreSQL
y no hace falta falsear ningún módulo.
"""

import os
from datetime import datetime, timedelta, timezone

# ── Configuración para Settings, antes de que lru_cache la capture ──────────
os.environ.setdefault("SECRET_KEY", "test-secret-key-solo-para-tests-unitarios")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("ENVIRONMENT", "test")

# ── SQLite no tiene un compilador para JSONB (usado en TicketEvent.detail) ──
# Se delega al visitor de JSON, que es equivalente a efectos de estos tests.
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler


def _visit_JSONB(self, type_, **kw):
    return self.visit_JSON(type_, **kw)


SQLiteTypeCompiler.visit_JSONB = _visit_JSONB  # type: ignore[attr-defined]

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.middleware.auth import hash_password
from app.models import (
    Application,
    Base,
    Epic,
    Role,
    Ticket,
    TicketStatus,
    User,
)

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    """Sesión SQLite en memoria con todas las tablas. Se destruye tras cada test."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def sample_role(db_session: AsyncSession):
    """Rol ADMIN de prueba."""
    role = Role(name="ADMIN", description="Administrador del sistema")
    db_session.add(role)
    await db_session.flush()
    return role


@pytest.fixture
async def sample_user(db_session: AsyncSession, sample_role: Role):
    """Usuario de prueba con rol ADMIN."""
    user = User(
        email="test@corestream.com",
        full_name="Test User",
        hashed_password=hash_password("testpass123"),
        role_id=sample_role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def sample_app(db_session: AsyncSession):
    """Aplicación de prueba."""
    app = Application(name="Test Application", is_active=True)
    db_session.add(app)
    await db_session.flush()
    return app


@pytest.fixture
async def sample_epic(db_session: AsyncSession, sample_app: Application):
    """Épica de prueba dentro de sample_app."""
    epic = Epic(
        title="Test Epic",
        order_index=0,
        application_id=sample_app.id,
        due_date=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db_session.add(epic)
    await db_session.flush()
    return epic


@pytest.fixture
async def sample_ticket(db_session: AsyncSession, sample_epic: Epic, sample_user: User):
    """Ticket de prueba en estado TODO asignado a sample_user."""
    ticket = Ticket(
        title="Test Ticket",
        status=TicketStatus.TODO,
        epic_id=sample_epic.id,
        assignee_id=sample_user.id,
        time_spent_seconds=3600,
    )
    db_session.add(ticket)
    await db_session.flush()
    return ticket
