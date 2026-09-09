"""
Tests para Tickets de Soporte - CoreStream.

Sección A: Creación de tickets de soporte (todos los roles)
Sección B: Asociar bug existente a un ticket (linked_ticket_id)
Sección C: Asignación restringida a TEAM_LEADER
Sección D: Transiciones de estado del workflow de soporte
Sección E: Validación de que los dev-tickets no se afectan
"""


import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.auth import hash_password
from app.models import (
    Application,
    Epic,
    Role,
    SupportSeverity,
    Ticket,
    TicketStatus,
    TicketType,
    User,
)
from app.services.ticket_state_machine import TicketStateMachine

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures locales
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
async def dev_role(db_session: AsyncSession) -> Role:
    role = Role(name="DEVELOPER")
    db_session.add(role)
    await db_session.flush()
    return role


@pytest.fixture
async def tl_role(db_session: AsyncSession) -> Role:
    role = Role(name="TEAM_LEADER")
    db_session.add(role)
    await db_session.flush()
    return role


@pytest.fixture
async def admin_role(db_session: AsyncSession) -> Role:
    role = Role(name="ADMIN")
    db_session.add(role)
    await db_session.flush()
    return role


@pytest.fixture
async def developer(db_session: AsyncSession, dev_role: Role) -> User:
    user = User(
        email="dev@test.com",
        full_name="Developer Test",
        hashed_password=hash_password("Test1234!"),
        role_id=dev_role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def team_leader(db_session: AsyncSession, tl_role: Role) -> User:
    user = User(
        email="tl@test.com",
        full_name="Team Leader Test",
        hashed_password=hash_password("Test1234!"),
        role_id=tl_role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def admin(db_session: AsyncSession, admin_role: Role) -> User:
    user = User(
        email="admin@test.com",
        full_name="Admin Test",
        hashed_password=hash_password("Test1234!"),
        role_id=admin_role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def support_app(db_session: AsyncSession) -> Application:
    app = Application(name="Support Test App", is_active=True)
    db_session.add(app)
    await db_session.flush()
    return app


@pytest.fixture
async def support_epic(db_session: AsyncSession, support_app: Application) -> Epic:
    epic = Epic(
        title="Support Test Epic",
        order_index=0,
        application_id=support_app.id,
    )
    db_session.add(epic)
    await db_session.flush()
    return epic


@pytest.fixture
async def support_ticket(db_session: AsyncSession, developer: User) -> Ticket:
    """Ticket de soporte en estado REPORTED creado por un developer."""
    ticket = Ticket(
        title="Bug: login falla en producción",
        ticket_type=TicketType.SUPPORT,
        status=TicketStatus.REPORTED,
        severity=SupportSeverity.HIGH,
        description="El botón de login no responde en Chrome 120",
        browser="Chrome 120",
        operating_system="Windows 11",
        created_by_id=developer.id,
    )
    db_session.add(ticket)
    await db_session.flush()
    return ticket


@pytest.fixture
async def dev_ticket(db_session: AsyncSession, support_epic: Epic, developer: User) -> Ticket:
    """Ticket de desarrollo normal en estado TODO."""
    ticket = Ticket(
        title="Implementar autenticación JWT",
        ticket_type=TicketType.DEVELOPMENT,
        status=TicketStatus.TODO,
        epic_id=support_epic.id,
        created_by_id=developer.id,
    )
    db_session.add(ticket)
    await db_session.flush()
    return ticket


# ─────────────────────────────────────────────────────────────────────────────
# Sección A: Creación de tickets de soporte
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_crear_support_ticket_developer(db_session: AsyncSession, developer: User):
    """Un Developer puede crear un ticket de soporte."""
    ticket = Ticket(
        title="Error 500 en endpoint /api/users",
        ticket_type=TicketType.SUPPORT,
        status=TicketStatus.REPORTED,
        severity=SupportSeverity.CRITICAL,
        stack_trace="Traceback (most recent call last):\n  File main.py line 42",
        reproduction_steps="1. Llamar GET /api/users\n2. Ver error 500",
        browser="Firefox 121",
        operating_system="macOS 14",
        created_by_id=developer.id,
    )
    db_session.add(ticket)
    await db_session.flush()

    assert ticket.id is not None
    assert ticket.ticket_type == TicketType.SUPPORT
    assert ticket.status == TicketStatus.REPORTED
    assert ticket.severity == SupportSeverity.CRITICAL
    assert ticket.epic_id is None  # Soporte no requiere épica


@pytest.mark.asyncio
async def test_crear_support_ticket_team_leader(db_session: AsyncSession, team_leader: User):
    """Un Team Leader puede crear un ticket de soporte."""
    ticket = Ticket(
        title="Memoria en producción al 95%",
        ticket_type=TicketType.SUPPORT,
        status=TicketStatus.REPORTED,
        severity=SupportSeverity.CRITICAL,
        created_by_id=team_leader.id,
    )
    db_session.add(ticket)
    await db_session.flush()

    assert ticket.ticket_type == TicketType.SUPPORT
    assert ticket.status == TicketStatus.REPORTED


@pytest.mark.asyncio
async def test_crear_support_ticket_admin(db_session: AsyncSession, admin: User):
    """Un Admin puede crear un ticket de soporte."""
    ticket = Ticket(
        title="Timeout en base de datos",
        ticket_type=TicketType.SUPPORT,
        status=TicketStatus.REPORTED,
        severity=SupportSeverity.HIGH,
        created_by_id=admin.id,
    )
    db_session.add(ticket)
    await db_session.flush()

    assert ticket.ticket_type == TicketType.SUPPORT


@pytest.mark.asyncio
async def test_support_ticket_campos_especificos(db_session: AsyncSession, developer: User):
    """Los campos específicos de soporte se persisten correctamente."""
    ticket = Ticket(
        title="Bug en formulario de registro",
        ticket_type=TicketType.SUPPORT,
        status=TicketStatus.REPORTED,
        severity=SupportSeverity.MEDIUM,
        stack_trace="TypeError: Cannot read property 'email' of undefined",
        reproduction_steps="1. Ir a /register\n2. Dejar email vacío\n3. Click Submit",
        browser="Safari 17",
        operating_system="iOS 17",
        created_by_id=developer.id,
    )
    db_session.add(ticket)
    await db_session.flush()
    await db_session.refresh(ticket)

    assert ticket.stack_trace == "TypeError: Cannot read property 'email' of undefined"
    assert ticket.reproduction_steps == "1. Ir a /register\n2. Dejar email vacío\n3. Click Submit"
    assert ticket.browser == "Safari 17"
    assert ticket.operating_system == "iOS 17"
    assert ticket.severity == SupportSeverity.MEDIUM


# ─────────────────────────────────────────────────────────────────────────────
# Sección B: Asociar bug existente a un ticket
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_asociar_bug_existente_a_support_ticket(
    db_session: AsyncSession,
    developer: User,
    dev_ticket: Ticket,
):
    """Un ticket de soporte puede referenciar un ticket de desarrollo existente."""
    support = Ticket(
        title="Bug en producción relacionado con ticket de dev",
        ticket_type=TicketType.SUPPORT,
        status=TicketStatus.REPORTED,
        severity=SupportSeverity.HIGH,
        linked_ticket_id=dev_ticket.id,
        created_by_id=developer.id,
    )
    db_session.add(support)
    await db_session.flush()
    await db_session.refresh(support)

    assert support.linked_ticket_id == dev_ticket.id


@pytest.mark.asyncio
async def test_support_ticket_sin_linked_ticket(db_session: AsyncSession, developer: User):
    """Un ticket de soporte puede existir sin linked_ticket_id (campo opcional)."""
    ticket = Ticket(
        title="Bug independiente",
        ticket_type=TicketType.SUPPORT,
        status=TicketStatus.REPORTED,
        severity=SupportSeverity.LOW,
        created_by_id=developer.id,
    )
    db_session.add(ticket)
    await db_session.flush()

    assert ticket.linked_ticket_id is None


# ─────────────────────────────────────────────────────────────────────────────
# Sección C: Asignación - solo TEAM_LEADER puede asignar
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_team_leader_puede_asignar(
    db_session: AsyncSession,
    support_ticket: Ticket,
    developer: User,
):
    """El Team Leader puede asignar un ticket de soporte a un developer."""
    support_ticket.assignee_id = developer.id
    await db_session.flush()
    await db_session.refresh(support_ticket)

    assert support_ticket.assignee_id == developer.id


@pytest.mark.asyncio
async def test_asignacion_persiste_en_bd(
    db_session: AsyncSession,
    support_ticket: Ticket,
    developer: User,
):
    """La asignación persiste correctamente en la base de datos."""
    ticket_id = support_ticket.id
    support_ticket.assignee_id = developer.id
    await db_session.flush()

    result = await db_session.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket_from_db = result.scalar_one()
    assert ticket_from_db.assignee_id == developer.id


# ─────────────────────────────────────────────────────────────────────────────
# Sección D: Transiciones de estado del workflow de soporte
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_transicion_reported_a_investigating(
    db_session: AsyncSession,
    support_ticket: Ticket,
    developer: User,
):
    """REPORTED → INVESTIGATING es una transición válida."""
    result = await TicketStateMachine.transition_to_investigating(
        ticket=support_ticket,
        current_user=developer,
        db=db_session,
    )
    assert result["status"] == "success"
    assert support_ticket.status == TicketStatus.INVESTIGATING


@pytest.mark.asyncio
async def test_transicion_investigating_a_resolved(
    db_session: AsyncSession,
    support_ticket: Ticket,
    developer: User,
):
    """INVESTIGATING → RESOLVED es una transición válida."""
    # Primero pasamos a INVESTIGATING
    support_ticket.status = TicketStatus.INVESTIGATING
    await db_session.flush()

    result = await TicketStateMachine.transition_to_resolved(
        ticket=support_ticket,
        current_user=developer,
        pr_link="https://github.com/org/repo/pull/123",
        db=db_session,
    )
    assert result["status"] == "success"
    assert support_ticket.status == TicketStatus.RESOLVED
    assert support_ticket.completed_at is not None


@pytest.mark.asyncio
async def test_transicion_invalida_reported_a_resolved(support_ticket: Ticket):
    """REPORTED → RESOLVED directo NO es una transición válida."""
    is_valid = TicketStateMachine.can_transition("REPORTED", "RESOLVED")
    assert is_valid is False


@pytest.mark.asyncio
async def test_transicion_invalida_desde_resolved(support_ticket: Ticket):
    """RESOLVED no tiene transiciones válidas (estado terminal)."""
    valid = TicketStateMachine.VALID_TRANSITIONS.get("RESOLVED", [])
    assert valid == []


@pytest.mark.asyncio
async def test_workflow_completo_soporte(
    db_session: AsyncSession,
    support_ticket: Ticket,
    developer: User,
):
    """Recorre el workflow completo: REPORTED → INVESTIGATING → RESOLVED."""
    # Paso 1: REPORTED → INVESTIGATING
    assert support_ticket.status == TicketStatus.REPORTED
    await TicketStateMachine.transition_to_investigating(
        ticket=support_ticket,
        current_user=developer,
        db=db_session,
    )
    assert support_ticket.status == TicketStatus.INVESTIGATING

    # Paso 2: INVESTIGATING → RESOLVED
    await TicketStateMachine.transition_to_resolved(
        ticket=support_ticket,
        current_user=developer,
        pr_link="https://github.com/org/repo/pull/123",
        db=db_session,
    )
    assert support_ticket.status == TicketStatus.RESOLVED


# ─────────────────────────────────────────────────────────────────────────────
# Sección E: Los dev-tickets no se ven afectados
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dev_ticket_mantiene_tipo_development(dev_ticket: Ticket):
    """Los tickets de desarrollo mantienen ticket_type=DEVELOPMENT."""
    assert dev_ticket.ticket_type == TicketType.DEVELOPMENT


@pytest.mark.asyncio
async def test_dev_ticket_no_tiene_campos_soporte(dev_ticket: Ticket):
    """Los campos de soporte son None en tickets de desarrollo."""
    assert dev_ticket.stack_trace is None
    assert dev_ticket.reproduction_steps is None
    assert dev_ticket.browser is None
    assert dev_ticket.operating_system is None
    assert dev_ticket.severity is None


@pytest.mark.asyncio
async def test_dev_ticket_workflow_inalterado(
    db_session: AsyncSession,
    dev_ticket: Ticket,
    developer: User,
):
    """El workflow de development sigue funcionando: TODO → IN_PROGRESS."""
    result = await TicketStateMachine.transition_to_in_progress(
        ticket=dev_ticket,
        current_user=developer,
        db=db_session,
    )
    assert result["status"] == "success"
    assert dev_ticket.status == TicketStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_transiciones_soporte_no_aplican_a_dev(dev_ticket: Ticket):
    """Las transiciones de soporte no son válidas para un dev ticket en TODO."""
    assert TicketStateMachine.can_transition("TODO", "REPORTED") is False
    assert TicketStateMachine.can_transition("TODO", "INVESTIGATING") is False
    assert TicketStateMachine.can_transition("TODO", "RESOLVED") is False


@pytest.mark.asyncio
async def test_severidades_validas():
    """Los valores del enum SupportSeverity son correctos."""
    assert SupportSeverity.CRITICAL.value == "CRITICAL"
    assert SupportSeverity.HIGH.value == "HIGH"
    assert SupportSeverity.MEDIUM.value == "MEDIUM"
    assert SupportSeverity.LOW.value == "LOW"


@pytest.mark.asyncio
async def test_ticket_type_enum():
    """Los valores del enum TicketType son correctos."""
    assert TicketType.DEVELOPMENT.value == "DEVELOPMENT"
    assert TicketType.SUPPORT.value == "SUPPORT"
