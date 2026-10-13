"""
Tests de los tickets operacionales de Soporte.

Cubre: creación con timer arrancado, congelado del timer al resolver, bloque de
cambios obligatorio y permisos (solo ADMIN/GROUP_LEADER resuelven).
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models import OperationalTicket, OperationalTicketStatus
from app.schemas.operational_ticket import (
    OperationalTicketCreate,
    OperationalTicketResolve,
)
from app.services.ticket_permissions import require_admin_or_leader


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def operational_ticket() -> OperationalTicket:
    """Ticket abierto recién creado (timer corriendo)."""
    return OperationalTicket(
        title="Login caído",
        problem="Los usuarios no pueden iniciar sesión desde producción",
        status=OperationalTicketStatus.OPEN,
        timer_started_at=datetime.now(timezone.utc) - timedelta(seconds=60),
        created_by_id=uuid4(),
    )


def _user(role: str) -> SimpleNamespace:
    """Sustituto ligero de TokenPayload/para require_admin_or_leader."""
    return SimpleNamespace(id=str(uuid4()), sub=str(uuid4()), role=role)


# ─────────────────────────────────────────────────────────────────────────────
# Timer
# ─────────────────────────────────────────────────────────────────────────────

def test_timer_arranca_al_crear(operational_ticket: OperationalTicket):
    """Al crearse, el ticket está OPEN y su timer ya acumula tiempo en vivo."""
    assert operational_ticket.status == OperationalTicketStatus.OPEN
    # elapsed_seconds solo se materializa al INSERTAR (default de SQLAlchemy)
    assert not operational_ticket.elapsed_seconds  # None o 0 antes del flush
    # ~60s de antigüedad: el timer en vivo debe reflejarlo (con margen)
    assert 55 <= operational_ticket.current_elapsed_seconds <= 70


def test_resolver_congela_el_timer(operational_ticket: OperationalTicket):
    """Al resolver, elapsed_seconds se congela y deja de avanzar."""
    resolved_at = datetime.now(timezone.utc)
    operational_ticket.resolve("Se revirtió el deploy", uuid4(), now=resolved_at)

    frozen = operational_ticket.elapsed_seconds
    assert operational_ticket.status == OperationalTicketStatus.RESOLVED
    assert 55 <= frozen <= 70
    # El valor en vivo queda igual al congelado
    assert operational_ticket.current_elapsed_seconds == frozen


def test_resolver_registra_fecha_y_autor(operational_ticket: OperationalTicket):
    resolver_id = uuid4()
    operational_ticket.resolve("Cambios aplicados", resolver_id)

    assert operational_ticket.resolved_by_id == resolver_id
    assert operational_ticket.resolved_at is not None
    assert operational_ticket.resolution_notes == "Cambios aplicados"


# ─────────────────────────────────────────────────────────────────────────────
# Permisos
# ─────────────────────────────────────────────────────────────────────────────

def test_admin_y_leader_pueden_resolver():
    require_admin_or_leader(_user("ADMIN"))
    require_admin_or_leader(_user("GROUP_LEADER"))  # no debe lanzar


def test_developer_no_puede_resolver():
    with pytest.raises(HTTPException) as exc:
        require_admin_or_leader(_user("DEVELOPER"))
    assert exc.value.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Esquemas (validación de los campos obligatorios)
# ─────────────────────────────────────────────────────────────────────────────

def test_create_requiere_titulo_y_problema():
    with pytest.raises(Exception):
        OperationalTicketCreate(title="ab", problem="x" * 10)
    with pytest.raises(Exception):
        OperationalTicketCreate(title="Título válido", problem="corto")

    ok = OperationalTicketCreate(title="Login caído", problem="No funciona el login")
    assert ok.title == "Login caído"


def test_resolve_requiere_bloque_de_cambios():
    with pytest.raises(Exception):
        OperationalTicketResolve(resolution_notes="ok")

    ok = OperationalTicketResolve(resolution_notes="Se revirtió el deploy v2")
    assert "revirtió" in ok.resolution_notes
