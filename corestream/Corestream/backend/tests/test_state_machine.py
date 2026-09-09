"""
Tests unitarios para TicketStateMachine — CS-044.

Sección A: can_transition (función pura, sin DB ni mocks).
Sección B: métodos de transición async con TimerService y TransitionAuditService mockeados.
Sección C: log_ticket_event con DB SQLite real (usa fixture sample_ticket).
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TicketEventType, TicketStatus
from app.services.ticket_state_machine import TicketStateMachine

# ─────────────────────────────────────────────────────────────────────────────
# Sección A — can_transition (síncrono, sin dependencias externas)
# ─────────────────────────────────────────────────────────────────────────────

class TestCanTransition:
    """Valida todas las aristas del grafo de transiciones y los casos borde."""

    # Transiciones VÁLIDAS
    def test_valid_todo_to_in_progress(self):
        assert TicketStateMachine.can_transition("TODO", "IN_PROGRESS") is True

    def test_valid_in_progress_to_blocked_question(self):
        assert TicketStateMachine.can_transition("IN_PROGRESS", "BLOCKED_QUESTION") is True

    def test_valid_in_progress_to_redirected(self):
        assert TicketStateMachine.can_transition("IN_PROGRESS", "REDIRECTED") is True

    def test_valid_in_progress_to_completed(self):
        assert TicketStateMachine.can_transition("IN_PROGRESS", "COMPLETED") is True

    def test_valid_blocked_to_in_progress(self):
        assert TicketStateMachine.can_transition("BLOCKED", "IN_PROGRESS") is True

    def test_valid_blocked_question_to_in_progress(self):
        assert TicketStateMachine.can_transition("BLOCKED_QUESTION", "IN_PROGRESS") is True

    def test_valid_redirected_to_todo(self):
        assert TicketStateMachine.can_transition("REDIRECTED", "TODO") is True

    # Transiciones INVÁLIDAS
    def test_invalid_completed_to_in_progress(self):
        assert TicketStateMachine.can_transition("COMPLETED", "IN_PROGRESS") is False

    def test_invalid_completed_to_todo(self):
        assert TicketStateMachine.can_transition("COMPLETED", "TODO") is False

    def test_invalid_todo_to_completed(self):
        assert TicketStateMachine.can_transition("TODO", "COMPLETED") is False

    def test_invalid_todo_to_blocked_question(self):
        assert TicketStateMachine.can_transition("TODO", "BLOCKED_QUESTION") is False

    def test_invalid_in_progress_to_todo(self):
        assert TicketStateMachine.can_transition("IN_PROGRESS", "TODO") is False

    def test_invalid_completed_to_blocked(self):
        assert TicketStateMachine.can_transition("COMPLETED", "BLOCKED_QUESTION") is False

    # Mismo estado → siempre False
    def test_same_state_todo_returns_false(self):
        assert TicketStateMachine.can_transition("TODO", "TODO") is False

    def test_same_state_in_progress_returns_false(self):
        assert TicketStateMachine.can_transition("IN_PROGRESS", "IN_PROGRESS") is False

    def test_same_state_completed_returns_false(self):
        assert TicketStateMachine.can_transition("COMPLETED", "COMPLETED") is False

    # Valores inválidos
    def test_none_current_status_returns_false(self):
        assert TicketStateMachine.can_transition(None, "IN_PROGRESS") is False

    def test_none_new_status_returns_false(self):
        assert TicketStateMachine.can_transition("TODO", None) is False

    def test_unknown_current_state_returns_false(self):
        assert TicketStateMachine.can_transition("UNKNOWN", "IN_PROGRESS") is False

    def test_empty_string_current_returns_false(self):
        assert TicketStateMachine.can_transition("", "IN_PROGRESS") is False


# ─────────────────────────────────────────────────────────────────────────────
# Helpers para crear mocks de ticket y usuario
# ─────────────────────────────────────────────────────────────────────────────

def make_ticket(status: TicketStatus) -> MagicMock:
    ticket = MagicMock()
    ticket.id = uuid4()
    ticket.status = status
    ticket.assignee_id = uuid4()
    return ticket


def make_user() -> MagicMock:
    user = MagicMock()
    user.id = uuid4()
    return user


def make_db() -> MagicMock:
    return MagicMock()


# ─────────────────────────────────────────────────────────────────────────────
# Sección B — Transiciones async (TimerService y TransitionAuditService mockeados)
# ─────────────────────────────────────────────────────────────────────────────

class TestTransitionToInProgress:

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_valid_from_todo(self, mock_timer, mock_audit):
        mock_audit.record_transition = AsyncMock()
        ticket = make_ticket(TicketStatus.TODO)
        user = make_user()
        db = make_db()

        result = await TicketStateMachine.transition_to_in_progress(ticket, user, db)

        assert result["status"] == "success"
        assert result["ticket_id"] == str(ticket.id)
        assert ticket.status == TicketStatus.IN_PROGRESS
        assert ticket.assignee_id == user.id

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_invalid_from_completed_raises_400(self, mock_timer, mock_audit):
        ticket = make_ticket(TicketStatus.COMPLETED)
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.transition_to_in_progress(ticket, make_user(), make_db())
        assert exc.value.status_code == 400

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_invalid_from_in_progress_raises_400(self, mock_timer, mock_audit):
        ticket = make_ticket(TicketStatus.IN_PROGRESS)
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.transition_to_in_progress(ticket, make_user(), make_db())
        assert exc.value.status_code == 400

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_audit_record_called(self, mock_timer, mock_audit):
        mock_audit.record_transition = AsyncMock()
        ticket = make_ticket(TicketStatus.TODO)

        await TicketStateMachine.transition_to_in_progress(ticket, make_user(), make_db())

        mock_audit.record_transition.assert_called_once()


class TestTransitionToBlocked:

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_valid_from_in_progress(self, mock_timer, mock_audit):
        mock_timer.return_value.pause_timer = AsyncMock()
        mock_audit.record_transition = AsyncMock()
        ticket = make_ticket(TicketStatus.IN_PROGRESS)
        question = "¿Cuál es el criterio de aceptación?"

        result = await TicketStateMachine.transition_to_blocked(ticket, make_user(), question, make_db())

        assert result["status"] == "success"
        assert ticket.status == TicketStatus.BLOCKED_QUESTION
        assert ticket.block_reason == question

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_pause_timer_called(self, mock_timer, mock_audit):
        mock_timer.return_value.pause_timer = AsyncMock()
        mock_audit.record_transition = AsyncMock()
        ticket = make_ticket(TicketStatus.IN_PROGRESS)

        await TicketStateMachine.transition_to_blocked(ticket, make_user(), "pregunta", make_db())

        mock_timer.return_value.pause_timer.assert_called_once()

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_invalid_from_todo_raises_400(self, mock_timer, mock_audit):
        ticket = make_ticket(TicketStatus.TODO)
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.transition_to_blocked(ticket, make_user(), "pregunta", make_db())
        assert exc.value.status_code == 400

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_invalid_from_completed_raises_400(self, mock_timer, mock_audit):
        ticket = make_ticket(TicketStatus.COMPLETED)
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.transition_to_blocked(ticket, make_user(), "pregunta", make_db())
        assert exc.value.status_code == 400


class TestTransitionFromBlocked:

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_valid_from_blocked_question(self, mock_timer, mock_audit):
        mock_timer.return_value.resume_timer = AsyncMock()
        mock_audit.record_transition = AsyncMock()
        ticket = make_ticket(TicketStatus.BLOCKED_QUESTION)
        ticket.block_reason = "pregunta anterior"

        result = await TicketStateMachine.transition_to_in_progress_from_blocked(
            ticket, make_user(), "resolución documentada", make_db()
        )

        assert result["status"] == "success"
        assert ticket.status == TicketStatus.IN_PROGRESS
        assert ticket.block_reason is None

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_resume_timer_called(self, mock_timer, mock_audit):
        mock_timer.return_value.resume_timer = AsyncMock()
        mock_audit.record_transition = AsyncMock()
        ticket = make_ticket(TicketStatus.BLOCKED_QUESTION)

        await TicketStateMachine.transition_to_in_progress_from_blocked(
            ticket, make_user(), "resuelto", make_db()
        )

        mock_timer.return_value.resume_timer.assert_called_once()

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_invalid_from_redirected_raises_400(self, mock_timer, mock_audit):
        # REDIRECTED → IN_PROGRESS no es una transición válida
        ticket = make_ticket(TicketStatus.REDIRECTED)
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.transition_to_in_progress_from_blocked(
                ticket, make_user(), "resolución", make_db()
            )
        assert exc.value.status_code == 400

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_invalid_from_completed_raises_400(self, mock_timer, mock_audit):
        ticket = make_ticket(TicketStatus.COMPLETED)
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.transition_to_in_progress_from_blocked(
                ticket, make_user(), "resolución", make_db()
            )
        assert exc.value.status_code == 400


class TestTransitionToRedirected:

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_valid_from_in_progress(self, mock_timer, mock_audit):
        mock_timer.return_value.pause_timer = AsyncMock()
        mock_audit.record_event = AsyncMock()
        old_assignee = uuid4()
        new_assignee = uuid4()
        ticket = make_ticket(TicketStatus.IN_PROGRESS)
        ticket.assignee_id = old_assignee

        result = await TicketStateMachine.transition_to_redirected(
            ticket, make_user(), new_assignee, "reasignado por carga", make_db()
        )

        assert result["status"] == "success"
        assert result["from_user_id"] == str(old_assignee)
        assert ticket.assignee_id == new_assignee
        assert ticket.status == TicketStatus.TODO

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_pause_timer_called_only_when_in_progress(self, mock_timer, mock_audit):
        mock_timer.return_value.pause_timer = AsyncMock()
        mock_audit.record_event = AsyncMock()
        ticket = make_ticket(TicketStatus.IN_PROGRESS)

        await TicketStateMachine.transition_to_redirected(
            ticket, make_user(), uuid4(), "motivo", make_db()
        )

        mock_timer.return_value.pause_timer.assert_called_once()

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_valid_from_todo_no_timer_pause(self, mock_timer, mock_audit):
        mock_timer.return_value.pause_timer = AsyncMock()
        mock_audit.record_event = AsyncMock()
        ticket = make_ticket(TicketStatus.TODO)

        await TicketStateMachine.transition_to_redirected(
            ticket, make_user(), uuid4(), "motivo", make_db()
        )

        mock_timer.return_value.pause_timer.assert_not_called()

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_invalid_from_completed_raises_400(self, mock_timer, mock_audit):
        ticket = make_ticket(TicketStatus.COMPLETED)
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.transition_to_redirected(
                ticket, make_user(), uuid4(), "motivo", make_db()
            )
        assert exc.value.status_code == 400

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_null_old_assignee_returns_none(self, mock_timer, mock_audit):
        mock_timer.return_value.pause_timer = AsyncMock()
        mock_audit.record_event = AsyncMock()
        ticket = make_ticket(TicketStatus.IN_PROGRESS)
        ticket.assignee_id = None

        result = await TicketStateMachine.transition_to_redirected(
            ticket, make_user(), uuid4(), "sin asignado previo", make_db()
        )

        assert result["from_user_id"] is None


class TestTransitionToCompleted:

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_valid_from_in_progress(self, mock_timer, mock_audit):
        mock_timer.return_value.stop_timer = AsyncMock()
        mock_audit.record_transition = AsyncMock()
        ticket = make_ticket(TicketStatus.IN_PROGRESS)
        pr_url = "https://github.com/org/repo/pull/42"

        result = await TicketStateMachine.transition_to_completed(
            ticket, make_user(), pr_url, make_db()
        )

        assert result["status"] == "success"
        assert ticket.status == TicketStatus.COMPLETED
        assert ticket.pr_link == pr_url
        assert ticket.completed_at is not None

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_completed_at_is_utc(self, mock_timer, mock_audit):
        mock_timer.return_value.stop_timer = AsyncMock()
        mock_audit.record_transition = AsyncMock()
        ticket = make_ticket(TicketStatus.IN_PROGRESS)
        before = datetime.now(timezone.utc)

        await TicketStateMachine.transition_to_completed(ticket, make_user(), "pr_url", make_db())

        after = datetime.now(timezone.utc)
        assert before <= ticket.completed_at <= after

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_stop_timer_called(self, mock_timer, mock_audit):
        mock_timer.return_value.stop_timer = AsyncMock()
        mock_audit.record_transition = AsyncMock()
        ticket = make_ticket(TicketStatus.IN_PROGRESS)

        await TicketStateMachine.transition_to_completed(ticket, make_user(), "url", make_db())

        mock_timer.return_value.stop_timer.assert_called_once()

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_invalid_from_todo_raises_400(self, mock_timer, mock_audit):
        ticket = make_ticket(TicketStatus.TODO)
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.transition_to_completed(ticket, make_user(), "url", make_db())
        assert exc.value.status_code == 400

    @patch("app.services.ticket_state_machine.TransitionAuditService")
    @patch("app.services.ticket_state_machine.TimerService")
    async def test_invalid_from_blocked_raises_400(self, mock_timer, mock_audit):
        ticket = make_ticket(TicketStatus.BLOCKED_QUESTION)
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.transition_to_completed(ticket, make_user(), "url", make_db())
        assert exc.value.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# Sección C — log_ticket_event con DB SQLite real
# ─────────────────────────────────────────────────────────────────────────────

class TestLogTicketEvent:

    async def test_string_detail_wraps_in_dict(self, db_session: AsyncSession, sample_ticket):
        event = await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=sample_ticket.id,
            event_type=TicketEventType.STATUS_CHANGED,
            user_id=sample_ticket.assignee_id,
            detail="cambio de estado manual",
        )

        assert isinstance(event.detail, dict)
        assert event.detail["message"] == "cambio de estado manual"
        assert "timestamp" in event.detail

    async def test_dict_detail_adds_timestamp(self, db_session: AsyncSession, sample_ticket):
        event = await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=sample_ticket.id,
            event_type=TicketEventType.COMMENT,
            user_id=sample_ticket.assignee_id,
            detail={"texto": "comentario de prueba"},
        )

        assert event.detail["texto"] == "comentario de prueba"
        assert "timestamp" in event.detail

    async def test_enum_event_type_stored_as_string(self, db_session: AsyncSession, sample_ticket):
        event = await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=sample_ticket.id,
            event_type=TicketEventType.COMPLETED,
            user_id=sample_ticket.assignee_id,
            detail="completado",
        )

        event_type_val = (
            event.event_type.value
            if hasattr(event.event_type, "value")
            else event.event_type
        )
        assert event_type_val == "COMPLETED"

    async def test_string_event_type_accepted(self, db_session: AsyncSession, sample_ticket):
        event = await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=sample_ticket.id,
            event_type="QUESTION_RAISED",
            user_id=sample_ticket.assignee_id,
            detail={"pregunta": "¿cuándo?"},
        )

        assert event is not None
        assert event.ticket_id == sample_ticket.id
