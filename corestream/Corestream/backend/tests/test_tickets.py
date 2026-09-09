"""
Tests para tickets y ticket state machine — CoreStream.

Sección A: can_transition (pura, sin DB) — complementa test_state_machine.py con casos extra.
Sección B: Ticket CRUD en SQLite en memoria.
Sección C: State transitions con log de eventos.
Sección D: Prioridades y filtrado.
"""


import pytest
from sqlalchemy import select
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
from app.services.ticket_state_machine import TicketStateMachine

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures locales (nombres distintos a los del conftest para evitar conflictos)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
async def dev_role(db_session: AsyncSession) -> Role:
    role = Role(name="DEVELOPER")
    db_session.add(role)
    await db_session.flush()
    return role


@pytest.fixture
async def dev_user(db_session: AsyncSession, dev_role: Role) -> User:
    user = User(
        email="dev@test.com",
        full_name="Test Developer",
        hashed_password=hash_password("Test1234!"),
        role_id=dev_role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_app(db_session: AsyncSession) -> Application:
    app = Application(
        name="Test App",
        is_active=True,
    )
    db_session.add(app)
    await db_session.flush()
    return app


@pytest.fixture
async def test_epic(db_session: AsyncSession, test_app: Application) -> Epic:
    epic = Epic(
        title="Test Epic",
        application_id=test_app.id,
        order_index=0,
    )
    db_session.add(epic)
    await db_session.flush()
    return epic


@pytest.fixture
async def todo_ticket(
    db_session: AsyncSession,
    test_epic: Epic,
    dev_user: User,
) -> Ticket:
    ticket = Ticket(
        title="Ticket de prueba",
        status=TicketStatus.TODO,
        priority="MEDIUM",
        epic_id=test_epic.id,
        assignee_id=dev_user.id,
    )
    db_session.add(ticket)
    await db_session.flush()
    return ticket


@pytest.fixture
async def in_progress_ticket(
    db_session: AsyncSession,
    test_epic: Epic,
    dev_user: User,
) -> Ticket:
    ticket = Ticket(
        title="Ticket en progreso",
        status=TicketStatus.IN_PROGRESS,
        priority="HIGH",
        epic_id=test_epic.id,
        assignee_id=dev_user.id,
        order_index=1,
    )
    db_session.add(ticket)
    await db_session.flush()
    return ticket


# ─────────────────────────────────────────────────────────────────────────────
# Sección A: can_transition — casos adicionales a test_state_machine.py
# ─────────────────────────────────────────────────────────────────────────────

class TestCanTransitionExtra:
    """Casos borde no cubiertos en test_state_machine.py."""

    def test_none_current_returns_false(self):
        assert TicketStateMachine.can_transition(None, "IN_PROGRESS") is False

    def test_none_new_returns_false(self):
        assert TicketStateMachine.can_transition("TODO", None) is False

    def test_empty_string_current_returns_false(self):
        assert TicketStateMachine.can_transition("", "IN_PROGRESS") is False

    def test_same_status_returns_false(self):
        assert TicketStateMachine.can_transition("TODO", "TODO") is False

    def test_unknown_status_returns_false(self):
        assert TicketStateMachine.can_transition("INVALID_STATUS", "IN_PROGRESS") is False

    def test_todo_cannot_go_to_blocked_question(self):
        assert TicketStateMachine.can_transition("TODO", "BLOCKED_QUESTION") is False

    def test_completed_has_no_valid_transitions(self):
        targets = ["TODO", "IN_PROGRESS", "BLOCKED_QUESTION", "REDIRECTED", "COMPLETED"]
        for target in targets:
            assert TicketStateMachine.can_transition("COMPLETED", target) is False

    def test_all_valid_transitions(self):
        valid = [
            ("TODO", "IN_PROGRESS"),
            ("IN_PROGRESS", "BLOCKED_QUESTION"),
            ("IN_PROGRESS", "REDIRECTED"),
            ("IN_PROGRESS", "COMPLETED"),
            ("BLOCKED", "IN_PROGRESS"),
            ("BLOCKED_QUESTION", "IN_PROGRESS"),
            ("REDIRECTED", "TODO"),
        ]
        for current, new in valid:
            assert TicketStateMachine.can_transition(current, new) is True, \
                f"Expected {current} → {new} to be valid"


# ─────────────────────────────────────────────────────────────────────────────
# Sección B: Ticket CRUD en SQLite en memoria
# ─────────────────────────────────────────────────────────────────────────────

class TestTicketCRUD:

    async def test_create_ticket_persists(
        self, db_session: AsyncSession, test_epic: Epic, dev_user: User
    ):
        ticket = Ticket(
            title="Nuevo ticket",
            status=TicketStatus.TODO,
            priority="LOW",
            epic_id=test_epic.id,
            assignee_id=dev_user.id,
        )
        db_session.add(ticket)
        await db_session.flush()

        result = await db_session.execute(
            select(Ticket).where(Ticket.title == "Nuevo ticket")
        )
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.status == TicketStatus.TODO
        assert found.priority == "LOW"

    async def test_ticket_starts_as_todo(
        self, db_session: AsyncSession, todo_ticket: Ticket
    ):
        result = await db_session.execute(
            select(Ticket).where(Ticket.id == todo_ticket.id)
        )
        ticket = result.scalar_one()
        assert ticket.status == TicketStatus.TODO

    async def test_ticket_status_update(
        self, db_session: AsyncSession, todo_ticket: Ticket
    ):
        todo_ticket.status = TicketStatus.IN_PROGRESS
        await db_session.flush()
        await db_session.refresh(todo_ticket)
        assert todo_ticket.status == TicketStatus.IN_PROGRESS

    async def test_ticket_assign_user(
        self, db_session: AsyncSession, todo_ticket: Ticket, dev_user: User
    ):
        todo_ticket.assignee_id = dev_user.id
        await db_session.flush()
        await db_session.refresh(todo_ticket)
        assert todo_ticket.assignee_id == dev_user.id

    async def test_multiple_tickets_same_epic(
        self, db_session: AsyncSession, test_epic: Epic, dev_user: User
    ):
        for i in range(3):
            ticket = Ticket(
                title=f"Ticket {i}",
                status=TicketStatus.TODO,
                priority="MEDIUM",
                epic_id=test_epic.id,
                assignee_id=dev_user.id,
                order_index=i,
            )
            db_session.add(ticket)
        await db_session.flush()

        result = await db_session.execute(
            select(Ticket).where(Ticket.epic_id == test_epic.id)
        )
        tickets = result.scalars().all()
        assert len(tickets) == 3

    async def test_ticket_with_pr_link(
        self, db_session: AsyncSession, in_progress_ticket: Ticket
    ):
        pr_url = "https://github.com/owner/repo/pull/42"
        in_progress_ticket.pr_link = pr_url
        in_progress_ticket.status = TicketStatus.COMPLETED
        await db_session.flush()
        await db_session.refresh(in_progress_ticket)

        assert in_progress_ticket.pr_link == pr_url
        assert in_progress_ticket.status == TicketStatus.COMPLETED


# ─────────────────────────────────────────────────────────────────────────────
# Sección C: State transitions + log de eventos
# ─────────────────────────────────────────────────────────────────────────────

class TestTicketStateTransitions:

    async def test_start_working_changes_status(
        self, db_session: AsyncSession, todo_ticket: Ticket
    ):
        assert TicketStateMachine.can_transition("TODO", "IN_PROGRESS")
        todo_ticket.status = TicketStatus.IN_PROGRESS
        await db_session.flush()
        await db_session.refresh(todo_ticket)
        assert todo_ticket.status == TicketStatus.IN_PROGRESS

    async def test_complete_ticket_with_pr(
        self, db_session: AsyncSession, in_progress_ticket: Ticket
    ):
        assert TicketStateMachine.can_transition("IN_PROGRESS", "COMPLETED")
        in_progress_ticket.pr_link = "https://github.com/repo/pull/1"
        in_progress_ticket.status = TicketStatus.COMPLETED
        await db_session.flush()
        await db_session.refresh(in_progress_ticket)
        assert in_progress_ticket.status == TicketStatus.COMPLETED

    async def test_raise_question_blocks_ticket(
        self, db_session: AsyncSession, in_progress_ticket: Ticket
    ):
        assert TicketStateMachine.can_transition("IN_PROGRESS", "BLOCKED_QUESTION")
        in_progress_ticket.status = TicketStatus.BLOCKED_QUESTION
        await db_session.flush()
        await db_session.refresh(in_progress_ticket)
        assert in_progress_ticket.status == TicketStatus.BLOCKED_QUESTION

    async def test_resolve_question_returns_to_in_progress(
        self, db_session: AsyncSession, in_progress_ticket: Ticket
    ):
        in_progress_ticket.status = TicketStatus.BLOCKED_QUESTION
        await db_session.flush()

        assert TicketStateMachine.can_transition("BLOCKED_QUESTION", "IN_PROGRESS")
        in_progress_ticket.status = TicketStatus.IN_PROGRESS
        await db_session.flush()
        await db_session.refresh(in_progress_ticket)
        assert in_progress_ticket.status == TicketStatus.IN_PROGRESS

    async def test_log_ticket_event_persists(
        self, db_session: AsyncSession, todo_ticket: Ticket, dev_user: User
    ):
        await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=todo_ticket.id,
            event_type=TicketEventType.STATUS_CHANGED,
            user_id=dev_user.id,
            detail="Ticket iniciado",
        )

        result = await db_session.execute(
            select(TicketEvent).where(TicketEvent.ticket_id == todo_ticket.id)
        )
        events = result.scalars().all()
        assert len(events) == 1
        assert events[0].event_type == TicketEventType.STATUS_CHANGED

    async def test_multiple_events_logged(
        self, db_session: AsyncSession, in_progress_ticket: Ticket, dev_user: User
    ):
        event_types = [
            TicketEventType.STATUS_CHANGED,
            TicketEventType.QUESTION_RAISED,
            TicketEventType.QUESTION_RESOLVED,
        ]
        for et in event_types:
            await TicketStateMachine.log_ticket_event(
                db=db_session,
                ticket_id=in_progress_ticket.id,
                event_type=et,
                user_id=dev_user.id,
                detail=f"Evento {et.value}",
            )

        result = await db_session.execute(
            select(TicketEvent)
            .where(TicketEvent.ticket_id == in_progress_ticket.id)
            .order_by(TicketEvent.created_at)
        )
        events = result.scalars().all()
        assert len(events) == 3
        assert events[1].event_type == TicketEventType.QUESTION_RAISED
        assert events[2].event_type == TicketEventType.QUESTION_RESOLVED

    def test_completed_cannot_restart(self):
        assert TicketStateMachine.can_transition("COMPLETED", "IN_PROGRESS") is False


# ─────────────────────────────────────────────────────────────────────────────
# Sección D: Prioridades y ordenamiento
# ─────────────────────────────────────────────────────────────────────────────

class TestTicketPriorities:

    async def test_all_priorities_accepted(
        self, db_session: AsyncSession, test_epic: Epic, dev_user: User
    ):
        priorities = ["LOW", "MEDIUM", "HIGH", "URGENT"]
        for i, priority in enumerate(priorities):
            ticket = Ticket(
                title=f"Ticket {priority}",
                status=TicketStatus.TODO,
                priority=priority,
                epic_id=test_epic.id,
                assignee_id=dev_user.id,
                order_index=i,
            )
            db_session.add(ticket)
        await db_session.flush()

        result = await db_session.execute(
            select(Ticket).where(Ticket.epic_id == test_epic.id)
        )
        tickets = result.scalars().all()
        assert len(tickets) == 4
        found_priorities = {t.priority for t in tickets}
        assert found_priorities == {"LOW", "MEDIUM", "HIGH", "URGENT"}

    async def test_tickets_ordered_by_index(
        self, db_session: AsyncSession, test_epic: Epic, dev_user: User
    ):
        for i in [2, 0, 1]:
            ticket = Ticket(
                title=f"Ticket orden {i}",
                status=TicketStatus.TODO,
                priority="MEDIUM",
                epic_id=test_epic.id,
                assignee_id=dev_user.id,
                order_index=i,
            )
            db_session.add(ticket)
        await db_session.flush()

        result = await db_session.execute(
            select(Ticket)
            .where(Ticket.epic_id == test_epic.id)
            .order_by(Ticket.order_index)
        )
        tickets = result.scalars().all()
        assert [t.order_index for t in tickets] == [0, 1, 2]

    async def test_filter_tickets_by_status(
        self, db_session: AsyncSession, test_epic: Epic, dev_user: User
    ):
        statuses = [
            TicketStatus.TODO,
            TicketStatus.IN_PROGRESS,
            TicketStatus.COMPLETED,
        ]
        for i, status in enumerate(statuses):
            ticket = Ticket(
                title=f"Ticket {status.value}",
                status=status,
                priority="MEDIUM",
                epic_id=test_epic.id,
                assignee_id=dev_user.id,
                order_index=i,
            )
            db_session.add(ticket)
        await db_session.flush()

        result = await db_session.execute(
            select(Ticket).where(
                Ticket.epic_id == test_epic.id,
                Ticket.status == TicketStatus.TODO,
            )
        )
        todo_tickets = result.scalars().all()
        assert len(todo_tickets) == 1
        assert todo_tickets[0].status == TicketStatus.TODO
