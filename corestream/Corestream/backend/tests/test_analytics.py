"""
Tests unitarios para app/services/analytics_service.py.

Sección A: get_ticket_metrics — la única función con lógica real, usada por
           GET /analytics/application/{app_id}. Se ejecuta contra SQLite en
           memoria con datos creados explícitamente dentro de cada test.
Sección B: AnalyticsService — hoy son esqueletos (devuelven listas/dicts
           vacíos); solo se cubre la validación del rango de fechas.
Sección C: contrato entre routers/analytics.py y el servicio.

NOTA: la versión anterior probaba métodos (eficiencia, churn, heatmap por día
de la semana, burndown) que ya no existen en el servicio.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Application,
    Epic,
    Sprint,
    Ticket,
    TicketEvent,
    TicketEventType,
    TicketPriority,
    TicketStatus,
    User,
    UserRole,
)
from app.services import analytics_service
from app.services.analytics_service import AnalyticsService, get_ticket_metrics

# ─────────────────────────────────────────────────────────────────────────────
# Helpers de creación de entidades
# ─────────────────────────────────────────────────────────────────────────────


async def create_user(db: AsyncSession, full_name: str = "Dev User") -> User:
    user = User(
        email=f"{uuid4()}@test.com",
        full_name=full_name,
        hashed_password="x",
        role=UserRole.DEVELOPER,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


async def create_app(db: AsyncSession) -> Application:
    app = Application(name=f"App-{uuid4()}", is_active=True)
    db.add(app)
    await db.flush()
    return app


async def create_epic(db: AsyncSession, app_id) -> Epic:
    epic = Epic(title=f"Epic-{uuid4()}", order_index=0, application_id=app_id)
    db.add(epic)
    await db.flush()
    return epic


async def create_ticket(
    db: AsyncSession,
    epic_id,
    status=TicketStatus.TODO,
    priority=TicketPriority.MEDIUM,
    assignee_id=None,
    time_spent: int = 0,
    due_date=None,
    sprint_id=None,
) -> Ticket:
    ticket = Ticket(
        title=f"Ticket-{uuid4()}",
        status=status,
        priority=priority,
        epic_id=epic_id,
        assignee_id=assignee_id,
        time_spent_seconds=time_spent,
        due_date=due_date,
        sprint_id=sprint_id,
    )
    db.add(ticket)
    await db.flush()
    return ticket


@pytest.fixture
async def app_epic(db_session: AsyncSession):
    app = await create_app(db_session)
    epic = await create_epic(db_session, app.id)
    return app, epic


# ─────────────────────────────────────────────────────────────────────────────
# Sección A — get_ticket_metrics
# ─────────────────────────────────────────────────────────────────────────────

class TestGetTicketMetrics:

    async def test_app_vacia_devuelve_ceros(self, db_session: AsyncSession, app_epic):
        app, _ = app_epic
        m = await get_ticket_metrics(db_session, app.id)

        assert m["total_tickets"] == 0
        assert m["completion_percentage"] == 0.0
        assert m["blocked_percentage"] == 0.0
        assert m["avg_time_hours"] == 0.0
        # Todas las claves de estado y prioridad presentes aunque estén a 0
        assert m["by_status"] == {s.value: 0 for s in TicketStatus}
        assert m["by_priority"] == {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "URGENT": 0}
        assert m["bottlenecks"] == []
        assert m["redirection_events"] == []

    async def test_conteos_por_estado_y_porcentajes(self, db_session: AsyncSession, app_epic):
        app, epic = app_epic
        for status, n in [
            (TicketStatus.TODO, 3),
            (TicketStatus.IN_PROGRESS, 2),
            (TicketStatus.BLOCKED, 1),
            (TicketStatus.REDIRECTED, 1),
            (TicketStatus.DONE, 3),
        ]:
            for _ in range(n):
                await create_ticket(db_session, epic.id, status=status)

        m = await get_ticket_metrics(db_session, app.id)

        assert m["total_tickets"] == 10
        assert m["completed_tickets"] == 3
        assert m["blocked_tickets"] == 1
        assert m["pending_tickets"] == 7
        assert m["redirected_tickets"] == 1
        assert m["by_status"] == {
            "TODO": 3, "IN_PROGRESS": 2, "BLOCKED": 1, "REDIRECTED": 1, "DONE": 3,
        }
        assert m["completion_percentage"] == 30.0
        assert m["blocked_percentage"] == 10.0

    async def test_conteos_por_prioridad(self, db_session: AsyncSession, app_epic):
        app, epic = app_epic
        await create_ticket(db_session, epic.id, priority=TicketPriority.URGENT)
        await create_ticket(db_session, epic.id, priority=TicketPriority.URGENT)
        await create_ticket(db_session, epic.id, priority=TicketPriority.LOW)

        m = await get_ticket_metrics(db_session, app.id)
        assert m["by_priority"] == {"LOW": 1, "MEDIUM": 0, "HIGH": 0, "URGENT": 2}

    async def test_excluye_tickets_de_otras_aplicaciones(self, db_session: AsyncSession, app_epic):
        app, epic = app_epic
        other_app = await create_app(db_session)
        other_epic = await create_epic(db_session, other_app.id)
        await create_ticket(db_session, epic.id)
        await create_ticket(db_session, other_epic.id)
        await create_ticket(db_session, other_epic.id)

        m = await get_ticket_metrics(db_session, app.id)
        assert m["total_tickets"] == 1

    async def test_filtro_por_assignee(self, db_session: AsyncSession, app_epic):
        app, epic = app_epic
        dev1 = await create_user(db_session)
        dev2 = await create_user(db_session)
        await create_ticket(db_session, epic.id, assignee_id=dev1.id, status=TicketStatus.DONE)
        await create_ticket(db_session, epic.id, assignee_id=dev2.id)
        await create_ticket(db_session, epic.id)

        m = await get_ticket_metrics(db_session, app.id, assignee_id=dev1.id)
        assert m["total_tickets"] == 1
        assert m["completion_percentage"] == 100.0

    async def test_filtro_por_sprint(self, db_session: AsyncSession, app_epic):
        app, epic = app_epic
        now = datetime.utcnow()
        sprint = Sprint(
            name="Sprint 1", application_id=app.id,
            start_date=now, end_date=now + timedelta(days=14),
        )
        db_session.add(sprint)
        await db_session.flush()
        await create_ticket(db_session, epic.id, sprint_id=sprint.id)
        await create_ticket(db_session, epic.id, sprint_id=sprint.id)
        await create_ticket(db_session, epic.id)

        m = await get_ticket_metrics(db_session, app.id, sprint_id=sprint.id)
        assert m["total_tickets"] == 2

    async def test_vencidos_excluyen_done_y_sin_fecha(self, db_session: AsyncSession, app_epic):
        app, epic = app_epic
        ayer = datetime.utcnow() - timedelta(days=1)
        manana = datetime.utcnow() + timedelta(days=1)
        await create_ticket(db_session, epic.id, status=TicketStatus.IN_PROGRESS, due_date=ayer)
        await create_ticket(db_session, epic.id, status=TicketStatus.BLOCKED, due_date=ayer)
        await create_ticket(db_session, epic.id, status=TicketStatus.DONE, due_date=ayer)
        await create_ticket(db_session, epic.id, status=TicketStatus.TODO, due_date=manana)
        await create_ticket(db_session, epic.id, status=TicketStatus.TODO)

        m = await get_ticket_metrics(db_session, app.id)

        assert m["overdue_tickets"] == 2
        assert m["overdue_by_status"] == {"IN_PROGRESS": 1, "BLOCKED": 1}
        assert m["by_group_status"]["overdue"] == {"IN_PROGRESS": 1, "BLOCKED": 1}

    async def test_agrupaciones_por_grupo(self, db_session: AsyncSession, app_epic):
        app, epic = app_epic
        await create_ticket(db_session, epic.id, status=TicketStatus.DONE, priority=TicketPriority.HIGH)
        await create_ticket(db_session, epic.id, status=TicketStatus.BLOCKED, priority=TicketPriority.LOW)
        await create_ticket(db_session, epic.id, status=TicketStatus.TODO, priority=TicketPriority.LOW)

        m = await get_ticket_metrics(db_session, app.id)

        assert m["by_group_status"]["completed"] == {"DONE": 1}
        assert m["by_group_status"]["pending"] == {"BLOCKED": 1, "TODO": 1}
        assert m["by_group_status"]["blocked"] == {"BLOCKED": 1}
        assert m["by_group_status"]["redirected"] == {}
        assert m["by_group_priority"]["pending"] == {"LOW": 2}
        assert m["by_group_priority"]["completed"] == {"HIGH": 1}

    async def test_tiempo_medio_ignora_tickets_sin_tiempo(self, db_session: AsyncSession, app_epic):
        app, epic = app_epic
        await create_ticket(db_session, epic.id, time_spent=3600)
        await create_ticket(db_session, epic.id, time_spent=7200)
        await create_ticket(db_session, epic.id, time_spent=0)

        m = await get_ticket_metrics(db_session, app.id)
        assert m["avg_time_hours"] == 1.5

    async def test_eventos_de_redireccion(self, db_session: AsyncSession, app_epic):
        app, epic = app_epic
        dev1 = await create_user(db_session)
        dev2 = await create_user(db_session)
        ticket = await create_ticket(db_session, epic.id, status=TicketStatus.REDIRECTED)
        db_session.add_all([
            TicketEvent(
                ticket_id=ticket.id, user_id=dev1.id,
                event_type=TicketEventType.REDIRECTED,
                from_user_id=dev1.id, to_user_id=dev2.id,
                detail={"reason": "carga de trabajo"},
            ),
            # Un evento de otro tipo no cuenta como redirección
            TicketEvent(
                ticket_id=ticket.id, user_id=dev1.id,
                event_type=TicketEventType.COMMENT, detail={},
            ),
        ])
        await db_session.flush()

        m = await get_ticket_metrics(db_session, app.id)

        assert m["redirection_events_count"] == 1
        [evento] = m["redirection_events"]
        assert evento["ticket_id"] == str(ticket.id)
        assert evento["ticket_title"] == ticket.title
        assert evento["from_user_id"] == str(dev1.id)
        assert evento["to_user_id"] == str(dev2.id)
        assert evento["detail"] == {"reason": "carga de trabajo"}

    async def test_cuellos_de_botella_excluyen_done(self, db_session: AsyncSession, app_epic):
        app, epic = app_epic
        await create_ticket(db_session, epic.id, status=TicketStatus.BLOCKED)
        await create_ticket(db_session, epic.id, status=TicketStatus.BLOCKED)
        await create_ticket(db_session, epic.id, status=TicketStatus.TODO)
        await create_ticket(db_session, epic.id, status=TicketStatus.DONE)

        m = await get_ticket_metrics(db_session, app.id)

        by_status = {b["status"]: b for b in m["bottlenecks"]}
        assert set(by_status) == {"BLOCKED", "TODO"}
        assert by_status["BLOCKED"]["ticket_count"] == 2
        assert len(by_status["BLOCKED"]["tickets"]) == 2
        for b in m["bottlenecks"]:
            assert b["average_hours"] >= 0
            assert b["max_hours"] >= b["average_hours"]
        # Ordenados de mayor a menor tiempo medio
        medias = [b["average_hours"] for b in m["bottlenecks"]]
        assert medias == sorted(medias, reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sección B — AnalyticsService (validación del rango de fechas)
# ─────────────────────────────────────────────────────────────────────────────

class TestAnalyticsServiceDateRange:

    @pytest.mark.parametrize(
        "method", [AnalyticsService.get_user_performance, AnalyticsService.get_heatmap_data]
    )
    async def test_rango_invertido_lanza_400(self, method):
        now = datetime.utcnow()
        with pytest.raises(HTTPException) as exc:
            await method(None, str(uuid4()), now, now - timedelta(days=1))
        assert exc.value.status_code == 400

    @pytest.mark.parametrize(
        "method", [AnalyticsService.get_user_performance, AnalyticsService.get_heatmap_data]
    )
    async def test_mismo_dia_es_rango_valido(self, method):
        now = datetime.utcnow()
        result = await method(None, str(uuid4()), now, now)
        assert isinstance(result, list)


# ─────────────────────────────────────────────────────────────────────────────
# Sección C — Contrato routers/analytics.py ↔ servicio
# ─────────────────────────────────────────────────────────────────────────────

def test_funcion_usada_por_el_endpoint_de_metricas_existe():
    assert callable(getattr(analytics_service, "get_ticket_metrics", None))


@pytest.mark.xfail(
    strict=True,
    reason=(
        "BUG: routers/analytics.py llama a analytics_service.get_user_performance "
        "(líneas 172 y 308), get_activity_heatmap (221) y get_burndown_chart (264) "
        "como funciones del MÓDULO, pero el módulo solo define get_ticket_metrics "
        "(los otros son métodos de AnalyticsService con otra firma o no existen). "
        "Los endpoints /performance, /heatmap, /burndown y /export/csv terminan en "
        "AttributeError -> HTTP 500."
    ),
)
@pytest.mark.parametrize(
    "name", ["get_user_performance", "get_activity_heatmap", "get_burndown_chart"]
)
def test_funciones_usadas_por_el_router_existen_en_el_modulo(name):
    assert callable(getattr(analytics_service, name, None))
