"""
Tests unitarios para AnalyticsService — CS-044.

Usa DB SQLite en memoria con datos creados explícitamente dentro de cada test.
Se validan cálculos de eficiencia, bloqueo, churn, heatmap y burndown.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.auth import hash_password
from app.models import (
    Application,
    Epic,
    Role,
    Ticket,
    TicketEvent,
    TicketEventType,
    TicketStatus,
    User,
)
from app.services.analytics_service import AnalyticsService

# Fecha fija de lunes conocido (2 Jun 2025 = weekday 0)
MONDAY_UTC = datetime(2025, 6, 2, 12, 0, 0, tzinfo=timezone.utc)
WEDNESDAY_UTC = datetime(2025, 6, 4, 12, 0, 0, tzinfo=timezone.utc)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de creación de entidades
# ─────────────────────────────────────────────────────────────────────────────

async def create_role(db: AsyncSession, name: str = "DEVELOPER") -> Role:
    role = Role(name=name)
    db.add(role)
    await db.flush()
    return role


async def create_user(db: AsyncSession, role_id, full_name: str = "Dev User") -> User:
    user = User(
        email=f"{uuid4()}@test.com",
        full_name=full_name,
        hashed_password=hash_password("pwd"),
        role_id=role_id,
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


async def create_epic(db: AsyncSession, app_id, due_date=None) -> Epic:
    epic = Epic(
        title=f"Epic-{uuid4()}",
        order_index=0,
        application_id=app_id,
        due_date=due_date,
    )
    db.add(epic)
    await db.flush()
    return epic


async def create_ticket(
    db: AsyncSession,
    epic_id,
    assignee_id=None,
    status=TicketStatus.TODO,
    time_spent: int = 0,
    completed_at=None,
) -> Ticket:
    ticket = Ticket(
        title=f"Ticket-{uuid4()}",
        status=status,
        epic_id=epic_id,
        assignee_id=assignee_id,
        time_spent_seconds=time_spent,
        completed_at=completed_at,
    )
    db.add(ticket)
    await db.flush()
    return ticket


async def create_event(
    db: AsyncSession,
    ticket_id,
    user_id,
    event_type: TicketEventType,
    created_at=None,
) -> TicketEvent:
    event = TicketEvent(
        ticket_id=ticket_id,
        user_id=user_id,
        event_type=event_type,
        detail={"test": True},
    )
    if created_at is not None:
        event.created_at = created_at
    db.add(event)
    await db.flush()
    return event


# ─────────────────────────────────────────────────────────────────────────────
# Tests: get_user_performance
# ─────────────────────────────────────────────────────────────────────────────

class TestGetUserPerformance:

    async def test_empty_app_returns_empty_list(self, db_session: AsyncSession):
        app = await create_app(db_session)

        result = await AnalyticsService.get_user_performance(
            app_id=app.id, date_from=None, date_to=None, db=db_session
        )

        assert result == []

    async def test_invalid_date_range_raises_400(self, db_session: AsyncSession):
        app = await create_app(db_session)
        date_from = datetime(2025, 6, 10, tzinfo=timezone.utc)
        date_to = datetime(2025, 6, 1, tzinfo=timezone.utc)

        with pytest.raises(HTTPException) as exc:
            await AnalyticsService.get_user_performance(
                app_id=app.id, date_from=date_from, date_to=date_to, db=db_session
            )
        assert exc.value.status_code == 400

    async def test_completed_event_increments_tickets_completed(self, db_session: AsyncSession):
        role = await create_role(db_session)
        user = await create_user(db_session, role.id)
        app = await create_app(db_session)
        epic = await create_epic(db_session, app.id)
        ticket = await create_ticket(db_session, epic.id, assignee_id=user.id, time_spent=3600)
        await create_event(db_session, ticket.id, user.id, TicketEventType.COMPLETED)

        result = await AnalyticsService.get_user_performance(
            app_id=app.id, date_from=None, date_to=None, db=db_session
        )

        assert len(result) == 1
        assert result[0]["tickets_completed"] == 1
        assert result[0]["user_id"] == user.id

    async def test_question_raised_increments_blocking_index(self, db_session: AsyncSession):
        role = await create_role(db_session)
        user = await create_user(db_session, role.id)
        app = await create_app(db_session)
        epic = await create_epic(db_session, app.id)
        ticket = await create_ticket(db_session, epic.id, assignee_id=user.id, time_spent=3600)
        # 1 pregunta sobre 1 ticket procesado → blocking_index = 100%
        await create_event(db_session, ticket.id, user.id, TicketEventType.QUESTION_RAISED)

        result = await AnalyticsService.get_user_performance(
            app_id=app.id, date_from=None, date_to=None, db=db_session
        )

        assert len(result) == 1
        assert result[0]["questions_raised"] == 1
        assert result[0]["blocking_index"] == 100.0

    async def test_churn_index_from_redirected_events(self, db_session: AsyncSession):
        role = await create_role(db_session)
        user = await create_user(db_session, role.id)
        app = await create_app(db_session)
        epic = await create_epic(db_session, app.id)
        ticket = await create_ticket(db_session, epic.id, assignee_id=user.id, time_spent=3600)
        # 1 redirección / 1 asignado → churn_index = 100%
        await create_event(db_session, ticket.id, user.id, TicketEventType.REDIRECTED)

        result = await AnalyticsService.get_user_performance(
            app_id=app.id, date_from=None, date_to=None, db=db_session
        )

        assert len(result) == 1
        assert result[0]["churn_index"] == 100.0

    async def test_efficiency_zero_when_no_time_spent(self, db_session: AsyncSession):
        role = await create_role(db_session)
        user = await create_user(db_session, role.id)
        app = await create_app(db_session)
        epic = await create_epic(db_session, app.id)
        ticket = await create_ticket(db_session, epic.id, assignee_id=user.id, time_spent=0)
        await create_event(db_session, ticket.id, user.id, TicketEventType.COMPLETED)

        result = await AnalyticsService.get_user_performance(
            app_id=app.id, date_from=None, date_to=None, db=db_session
        )

        assert result[0]["avg_time_hours"] == 0.0
        assert result[0]["efficiency"] == 0.0

    async def test_date_filter_excludes_old_events(self, db_session: AsyncSession):
        role = await create_role(db_session)
        user = await create_user(db_session, role.id)
        app = await create_app(db_session)
        epic = await create_epic(db_session, app.id)
        ticket = await create_ticket(db_session, epic.id, assignee_id=user.id, time_spent=3600)
        old_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        await create_event(db_session, ticket.id, user.id, TicketEventType.COMPLETED, created_at=old_date)

        date_from = datetime(2025, 1, 1, tzinfo=timezone.utc)
        date_to = datetime(2025, 12, 31, tzinfo=timezone.utc)
        result = await AnalyticsService.get_user_performance(
            app_id=app.id, date_from=date_from, date_to=date_to, db=db_session
        )

        assert result == []

    async def test_user_not_in_db_is_skipped(self, db_session: AsyncSession):
        app = await create_app(db_session)
        role = await create_role(db_session)
        user = await create_user(db_session, role.id)
        epic = await create_epic(db_session, app.id)
        ticket = await create_ticket(db_session, epic.id, assignee_id=user.id)
        # Evento con user_id que no existe en la tabla User
        ghost_user_id = uuid4()
        await create_event(db_session, ticket.id, ghost_user_id, TicketEventType.COMPLETED)

        result = await AnalyticsService.get_user_performance(
            app_id=app.id, date_from=None, date_to=None, db=db_session
        )

        # El ghost_user_id no existe → se omite del resultado
        assert all(entry["user_id"] != ghost_user_id for entry in result)

    async def test_multiple_events_same_ticket_counted_once_in_processed(self, db_session: AsyncSession):
        role = await create_role(db_session)
        user = await create_user(db_session, role.id)
        app = await create_app(db_session)
        epic = await create_epic(db_session, app.id)
        ticket = await create_ticket(db_session, epic.id, assignee_id=user.id, time_spent=3600)
        # 2 eventos del mismo ticket → tickets_processed = 1 (set deduplication)
        await create_event(db_session, ticket.id, user.id, TicketEventType.STATUS_CHANGED)
        await create_event(db_session, ticket.id, user.id, TicketEventType.COMPLETED)

        result = await AnalyticsService.get_user_performance(
            app_id=app.id, date_from=None, date_to=None, db=db_session
        )

        assert result[0]["tickets_processed"] == 1

    async def test_management_events_do_not_count_as_processed(self, db_session: AsyncSession):
        """
        Los eventos de gestión/autoría (CREATED, UPDATED, MOVED, ASSIGNED) NO deben
        contar como "tickets procesados": un TEAM_LEADER que crea y asigna tickets a
        otros no los trabajó. Solo el trabajo real (STATUS_CHANGED, COMPLETED, etc.)
        cuenta.
        """
        role = await create_role(db_session)
        lead = await create_user(db_session, role.id, full_name="Team Lead")
        app = await create_app(db_session)
        epic = await create_epic(db_session, app.id)

        # 3 tickets que el lead SOLO creó/editó/movió/asignó (sin trabajarlos)
        for ev in (
            TicketEventType.CREATED,
            TicketEventType.UPDATED,
            TicketEventType.MOVED,
            TicketEventType.ASSIGNED,
        ):
            t = await create_ticket(db_session, epic.id, assignee_id=lead.id, time_spent=0)
            await create_event(db_session, t.id, lead.id, ev)

        # 1 ticket que el lead SÍ trabajó (cambió de estado y completó)
        worked = await create_ticket(db_session, epic.id, assignee_id=lead.id, time_spent=3600)
        await create_event(db_session, worked.id, lead.id, TicketEventType.STATUS_CHANGED)
        await create_event(db_session, worked.id, lead.id, TicketEventType.COMPLETED)

        result = await AnalyticsService.get_user_performance(
            app_id=app.id, date_from=None, date_to=None, db=db_session
        )

        # Solo el ticket trabajado cuenta como procesado, no los 4 de gestión
        assert len(result) == 1
        assert result[0]["tickets_processed"] == 1
        assert result[0]["tickets_completed"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# Tests: get_activity_heatmap
# ─────────────────────────────────────────────────────────────────────────────

class TestGetActivityHeatmap:

    async def test_empty_app_returns_empty_list(self, db_session: AsyncSession):
        app = await create_app(db_session)

        result = await AnalyticsService.get_activity_heatmap(app_id=app.id, db=db_session)

        assert result == []

    async def test_completed_event_on_monday_increments_index_0(self, db_session: AsyncSession):
        role = await create_role(db_session)
        user = await create_user(db_session, role.id)
        app = await create_app(db_session)
        epic = await create_epic(db_session, app.id)
        ticket = await create_ticket(db_session, epic.id, assignee_id=user.id)
        await create_event(
            db_session, ticket.id, user.id, TicketEventType.COMPLETED,
            created_at=MONDAY_UTC
        )

        result = await AnalyticsService.get_activity_heatmap(app_id=app.id, db=db_session)

        assert len(result) == 1
        assert result[0]["data"][0] == 1   # lunes
        assert sum(result[0]["data"]) == 1

    async def test_completed_events_on_multiple_days(self, db_session: AsyncSession):
        role = await create_role(db_session)
        user = await create_user(db_session, role.id)
        app = await create_app(db_session)
        epic = await create_epic(db_session, app.id)
        ticket = await create_ticket(db_session, epic.id, assignee_id=user.id)
        await create_event(db_session, ticket.id, user.id, TicketEventType.COMPLETED, created_at=MONDAY_UTC)
        await create_event(db_session, ticket.id, user.id, TicketEventType.COMPLETED, created_at=WEDNESDAY_UTC)

        result = await AnalyticsService.get_activity_heatmap(app_id=app.id, db=db_session)

        assert result[0]["data"][0] == 1   # lunes
        assert result[0]["data"][2] == 1   # miércoles
        assert sum(result[0]["data"]) == 2

    async def test_non_completed_events_not_counted(self, db_session: AsyncSession):
        role = await create_role(db_session)
        user = await create_user(db_session, role.id)
        app = await create_app(db_session)
        epic = await create_epic(db_session, app.id)
        ticket = await create_ticket(db_session, epic.id, assignee_id=user.id)
        # Solo un evento STATUS_CHANGED (no COMPLETED)
        await create_event(db_session, ticket.id, user.id, TicketEventType.STATUS_CHANGED, created_at=MONDAY_UTC)

        result = await AnalyticsService.get_activity_heatmap(app_id=app.id, db=db_session)

        assert result == []


# ─────────────────────────────────────────────────────────────────────────────
# Tests: get_burndown_chart
# ─────────────────────────────────────────────────────────────────────────────

class TestGetBurndownChart:

    async def test_epic_not_found_raises_error(self, db_session: AsyncSession):
        # El servicio captura la HTTPException 404 y la envuelve en 500
        with pytest.raises(HTTPException) as exc:
            await AnalyticsService.get_burndown_chart(epic_id=uuid4(), db=db_session)
        assert exc.value.status_code == 500
        assert "Epic no encontrado" in exc.value.detail

    async def test_epic_no_tickets_returns_zero_totals(self, db_session: AsyncSession):
        app = await create_app(db_session)
        # Usamos due_date naive (sin timezone) para que coincida con created_at de SQLite
        epic = await create_epic(
            db_session, app.id,
            due_date=datetime.utcnow() + timedelta(days=7)
        )

        result = await AnalyticsService.get_burndown_chart(epic_id=epic.id, db=db_session)

        assert result["total_tickets"] == 0
        assert result["completed"] == 0

    async def test_ideal_line_starts_at_total_and_ends_at_zero(self, db_session: AsyncSession):
        app = await create_app(db_session)
        # due_date naive para compatibilidad con created_at naive de SQLite
        epic = await create_epic(db_session, app.id, due_date=datetime.utcnow() + timedelta(days=10))
        for _ in range(5):
            await create_ticket(db_session, epic.id)

        result = await AnalyticsService.get_burndown_chart(epic_id=epic.id, db=db_session)

        assert result["total_tickets"] == 5
        ideal = result["ideal"]
        assert ideal[0]["points"] == 5.0
        assert ideal[-1]["points"] == 0.0

    async def test_actual_line_reflects_completed_tickets(self, db_session: AsyncSession):
        app = await create_app(db_session)
        # completed_at naive para compatibilidad con el servicio (usa .date())
        yesterday_naive = datetime.utcnow() - timedelta(days=1)
        epic = await create_epic(db_session, app.id, due_date=datetime.utcnow() + timedelta(days=9))
        # 3 tickets: 2 completados ayer, 1 pendiente
        await create_ticket(
            db_session, epic.id,
            status=TicketStatus.COMPLETED, completed_at=yesterday_naive
        )
        await create_ticket(
            db_session, epic.id,
            status=TicketStatus.COMPLETED, completed_at=yesterday_naive
        )
        await create_ticket(db_session, epic.id)

        result = await AnalyticsService.get_burndown_chart(epic_id=epic.id, db=db_session)

        assert result["completed"] == 2
        # El último punto real debe reflejar 1 ticket pendiente (3 - 2)
        actual_last = result["actual"][-1]
        assert actual_last["points"] == 1

    async def test_future_dates_not_in_actual_line(self, db_session: AsyncSession):
        app = await create_app(db_session)
        # due_date naive con margen futuro amplio para asegurarnos de tener puntos futuros
        epic = await create_epic(db_session, app.id, due_date=datetime.utcnow() + timedelta(days=14))
        await create_ticket(db_session, epic.id)

        result = await AnalyticsService.get_burndown_chart(epic_id=epic.id, db=db_session)

        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        actual_dates = [pt["date"] for pt in result["actual"]]
        future_dates = [d for d in actual_dates if d > today_str]
        assert future_dates == []
