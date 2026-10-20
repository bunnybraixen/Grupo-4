"""
Tests de Validación para FIX-001, FIX-002, FIX-003 (Sprints 3-4).

Se llama directamente a las funciones de los routers (sin HTTP) sobre SQLite
en memoria, pasando `current_user` como lo inyectaría get_current_user: un
objeto con `sub` y `role` (TokenPayload).

1. Reordenamiento de épicas: índices únicos y secuenciales (FIX-001).
2. Mover ticket entre épicas: permisos y validación cross-app (FIX-002).
3. Listado de aplicaciones: filtro por rol y conteos (FIX-003).
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Application,
    Epic,
    Ticket,
    TicketEventType,
    TicketStatus,
    User,
    UserRole,
)
from app.routers.applications import list_applications
from app.routers.epics import reorder_epic
from app.routers.tickets import move_ticket_to_epic
from app.services import ticket_state_machine as tsm_module


def actor(role: str, user_id=None) -> SimpleNamespace:
    """Doble de TokenPayload: lo que get_current_user entrega a los routers."""
    return SimpleNamespace(sub=str(user_id or uuid4()), role=role)


async def make_user(db: AsyncSession, role: UserRole = UserRole.DEVELOPER) -> User:
    user = User(
        email=f"{uuid4()}@test.com",
        full_name="Usuario de prueba",
        hashed_password="x",
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


async def make_app_with_epics(db: AsyncSession, n_epics: int, name: str | None = None):
    app = Application(name=name or f"App-{uuid4()}", is_active=True)
    db.add(app)
    await db.flush()
    epics = [
        Epic(title=f"Epic {i + 1}", order_index=i, application_id=app.id)
        for i in range(n_epics)
    ]
    db.add_all(epics)
    await db.flush()
    return app, epics


# ═════════════════════════════════════════════════════════════════════
# TEST #1: REORDENAMIENTO - FIX-001
# ═════════════════════════════════════════════════════════════════════

async def test_reorder_secuencial_mantiene_indices_unicos(db_session: AsyncSession):
    """
    App con 3 épicas (0, 1, 2). Se mueve Epic 1 de 0 → 2 y luego Epic 2 de
    1 → 0. Los índices deben seguir siendo únicos y secuenciales.

    (Una AsyncSession no admite operaciones concurrentes, así que la lógica
    de desplazamiento se valida de forma secuencial.)
    """
    _, (epic1, epic2, epic3) = await make_app_with_epics(db_session, 3)
    await db_session.commit()
    admin = actor("ADMIN")

    await reorder_epic(epic_id=epic1.id, new_order={"new_index": 2}, current_user=admin, db=db_session)
    await reorder_epic(epic_id=epic2.id, new_order={"new_index": 0}, current_user=admin, db=db_session)

    for epic in (epic1, epic2, epic3):
        await db_session.refresh(epic)

    # Orden inicial [1, 2, 3] → tras mover 1 al final [2, 3, 1] → tras mover
    # 2 (ya en 0) a 0 no cambia.
    assert (epic2.order_index, epic3.order_index, epic1.order_index) == (0, 1, 2)


async def test_reorder_hacia_atras_desplaza_las_intermedias(db_session: AsyncSession):
    _, (epic1, epic2, epic3) = await make_app_with_epics(db_session, 3)
    await db_session.commit()

    await reorder_epic(
        epic_id=epic3.id, new_order={"new_index": 0}, current_user=actor("GROUP_LEADER"), db=db_session
    )
    for epic in (epic1, epic2, epic3):
        await db_session.refresh(epic)

    assert (epic3.order_index, epic1.order_index, epic2.order_index) == (0, 1, 2)


async def test_reorder_indice_fuera_de_rango_lanza_400(db_session: AsyncSession):
    _, (epic1, *_rest) = await make_app_with_epics(db_session, 2)
    await db_session.commit()

    with pytest.raises(HTTPException) as exc:
        await reorder_epic(
            epic_id=epic1.id, new_order={"new_index": 5}, current_user=actor("ADMIN"), db=db_session
        )
    assert exc.value.status_code == 400


async def test_reorder_developer_recibe_403(db_session: AsyncSession):
    _, (epic1, *_rest) = await make_app_with_epics(db_session, 2)
    await db_session.commit()

    with pytest.raises(HTTPException) as exc:
        await reorder_epic(
            epic_id=epic1.id, new_order={"new_index": 1}, current_user=actor("DEVELOPER"), db=db_session
        )
    assert exc.value.status_code == 403
    await db_session.refresh(epic1)
    assert epic1.order_index == 0


async def test_reorder_epica_inexistente_lanza_404(db_session: AsyncSession):
    with pytest.raises(HTTPException) as exc:
        await reorder_epic(
            epic_id=uuid4(), new_order={"new_index": 0}, current_user=actor("ADMIN"), db=db_session
        )
    assert exc.value.status_code == 404


# ═════════════════════════════════════════════════════════════════════
# TEST #2: MOVER TICKET ENTRE ÉPICAS - FIX-002
# ═════════════════════════════════════════════════════════════════════

async def test_move_ticket_misma_app_va_al_final_y_registra_evento(db_session: AsyncSession):
    dev = await make_user(db_session)
    _, (epic_a, epic_b) = await make_app_with_epics(db_session, 2)
    existentes = [
        Ticket(title=f"Destino {i}", epic_id=epic_b.id, order_index=i) for i in range(2)
    ]
    ticket = Ticket(title="A mover", epic_id=epic_a.id, assignee_id=dev.id, order_index=0)
    db_session.add_all([*existentes, ticket])
    await db_session.commit()

    # Un DEVELOPER puede mover un ticket que tiene asignado.
    # log_ticket_event se mockea: el router le pasa el user_id como str (válido
    # con asyncpg), pero el tipo UUID de SQLAlchemy sobre SQLite exige un UUID
    # real al insertar, así que aquí solo se comprueba que se invoca.
    with patch.object(tsm_module, "log_ticket_event", new=AsyncMock()) as log_event:
        response = await move_ticket_to_epic(
            ticket_id=ticket.id,
            move_data={"epic_id": epic_b.id},
            current_user=actor("DEVELOPER", dev.id),
            db=db_session,
        )

    assert response.epic_id == epic_b.id
    assert response.order_index == 2
    log_event.assert_awaited_once()
    args = log_event.await_args.args
    assert args[1] == ticket.id
    assert args[2] == TicketEventType.MOVED
    assert args[3] == str(dev.id)


async def test_move_ticket_ajeno_por_developer_lanza_403(db_session: AsyncSession):
    owner = await make_user(db_session)
    _, (epic_a, epic_b) = await make_app_with_epics(db_session, 2)
    ticket = Ticket(title="Ajeno", epic_id=epic_a.id, assignee_id=owner.id)
    db_session.add(ticket)
    await db_session.commit()

    with pytest.raises(HTTPException) as exc:
        await move_ticket_to_epic(
            ticket_id=ticket.id,
            move_data={"epic_id": epic_b.id},
            current_user=actor("DEVELOPER"),
            db=db_session,
        )
    assert exc.value.status_code == 403
    await db_session.refresh(ticket)
    assert ticket.epic_id == epic_a.id


async def test_move_ticket_a_epica_inexistente_lanza_404(db_session: AsyncSession):
    _, (epic_a,) = await make_app_with_epics(db_session, 1)
    ticket = Ticket(title="T", epic_id=epic_a.id)
    db_session.add(ticket)
    await db_session.commit()

    with pytest.raises(HTTPException) as exc:
        await move_ticket_to_epic(
            ticket_id=ticket.id,
            move_data={"epic_id": uuid4()},
            current_user=actor("ADMIN"),
            db=db_session,
        )
    assert exc.value.status_code == 404


@pytest.mark.xfail(
    strict=True,
    reason=(
        "BUG: move_ticket_to_epic (app/routers/tickets.py, PATCH /tickets/{id}/move) "
        "solo comprueba que la épica destino exista; no valida que pertenezca "
        "a la misma aplicación que la de origen. FIX-002 ya no está aplicado: "
        "un ticket puede saltar a otra aplicación."
    ),
)
async def test_move_ticket_prevents_cross_app_movement(db_session: AsyncSession):
    """
    App A con Epic A1 y App B con Epic B1. Mover un ticket de A1 a B1 debe
    responder 400 y dejar el ticket en A1.
    """
    _, (epic_a,) = await make_app_with_epics(db_session, 1, name="App A (E-Commerce)")
    _, (epic_b,) = await make_app_with_epics(db_session, 1, name="App B (CRM)")
    ticket = Ticket(title="Ticket 101 - Fix button color", status=TicketStatus.TODO, epic_id=epic_a.id)
    db_session.add(ticket)
    await db_session.commit()

    with patch.object(tsm_module, "log_ticket_event", new=AsyncMock()):
        with pytest.raises(HTTPException) as exc:
            await move_ticket_to_epic(
                ticket_id=ticket.id,
                move_data={"epic_id": epic_b.id},
                current_user=actor("ADMIN"),
                db=db_session,
            )
    assert exc.value.status_code == 400
    await db_session.refresh(ticket)
    assert ticket.epic_id == epic_a.id


# ═════════════════════════════════════════════════════════════════════
# TEST #3: LISTADO DE APLICACIONES - FIX-003
# ═════════════════════════════════════════════════════════════════════

async def test_list_applications_oculta_inactivas_a_no_admin(db_session: AsyncSession):
    db_session.add_all([
        Application(name="Activa", is_active=True),
        Application(name="Archivada", is_active=False),
    ])
    await db_session.commit()

    as_dev = await list_applications(skip=0, limit=20, current_user=actor("DEVELOPER"), db=db_session)
    as_leader = await list_applications(skip=0, limit=20, current_user=actor("GROUP_LEADER"), db=db_session)
    as_admin = await list_applications(skip=0, limit=20, current_user=actor("ADMIN"), db=db_session)

    assert {a.name for a in as_dev} == {"Activa"}
    assert {a.name for a in as_leader} == {"Activa"}
    assert {a.name for a in as_admin} == {"Activa", "Archivada"}


async def test_list_applications_respeta_paginacion(db_session: AsyncSession):
    db_session.add_all([Application(name=f"App {i}", is_active=True) for i in range(5)])
    await db_session.commit()

    page = await list_applications(skip=1, limit=2, current_user=actor("ADMIN"), db=db_session)
    assert len(page) == 2


@pytest.mark.xfail(
    strict=True,
    reason=(
        "BUG: list_applications (app/routers/applications.py:35-66) ya no calcula "
        "epic_count / pending_count / delayed_count; ApplicationResponse los "
        "documenta pero siempre salen con el valor por defecto 0 (regresión de FIX-003)."
    ),
)
async def test_application_list_has_real_counts(db_session: AsyncSession):
    """
    App con 3 épicas; Epic 1: 5 TODO + 2 DONE; Epic 2: 3 TODO + 1 retrasado.
    Esperado: epic_count=3, pending_count=8 (TODO), delayed_count=1.
    """
    app, (epic1, epic2, _epic3) = await make_app_with_epics(db_session, 3)
    now = datetime.now(timezone.utc)
    futuro = now + timedelta(days=5)

    tickets = [Ticket(title=f"T{i}", status=TicketStatus.TODO, epic_id=epic1.id, due_date=futuro) for i in range(5)]
    tickets += [Ticket(title=f"D{i}", status=TicketStatus.DONE, epic_id=epic1.id, due_date=futuro) for i in range(2)]
    tickets += [Ticket(title=f"E{i}", status=TicketStatus.TODO, epic_id=epic2.id, due_date=futuro) for i in range(3)]
    tickets.append(
        Ticket(title="Retrasado", status=TicketStatus.IN_PROGRESS, epic_id=epic2.id, due_date=now - timedelta(days=1))
    )
    db_session.add_all(tickets)
    await db_session.commit()

    result = await list_applications(skip=0, limit=20, current_user=actor("ADMIN"), db=db_session)
    app_response = next(a for a in result if a.id == app.id)

    assert app_response.epic_count == 3
    assert app_response.pending_count == 8
    assert app_response.delayed_count == 1
