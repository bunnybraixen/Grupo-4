"""
Tests unitarios para TicketStateMachine (app/services/ticket_state_machine.py).

Sección A: can_transition contra el grafo real VALID_TRANSITIONS
           (TODO / IN_PROGRESS / BLOCKED / REDIRECTED / DONE).
Sección B: transition_to_in_progress y transition_to_completed — las dos
           transiciones que usan los routers (POST /tickets/{id}/start y
           /complete). Se mockea TransitionAuditService para aislar la lógica.
Sección C: log_ticket_event con DB SQLite real (fixture sample_ticket).
Sección D: métodos heredados basados en dict (transition, complete_ticket,
           raise_question, resolve_question, redirect_ticket). Ningún router
           los usa hoy; se cubren sus validaciones de entrada.

NOTA: versiones anteriores de este fichero esperaban estados BLOCKED_QUESTION
y COMPLETED, un TimerService dentro de la máquina de estados y métodos
transition_to_blocked / transition_to_redirected. Nada de eso existe ya.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TicketEvent, TicketEventType, TicketStatus
from app.services import ticket_state_machine as tsm_module
from app.services.ticket_state_machine import TicketStateMachine

ALL_STATES = [s.value for s in TicketStatus]

# Aristas válidas según VALID_TRANSITIONS
VALID_EDGES = {
    ("TODO", "IN_PROGRESS"),
    ("IN_PROGRESS", "BLOCKED"),
    ("IN_PROGRESS", "REDIRECTED"),
    ("IN_PROGRESS", "DONE"),
    ("BLOCKED", "IN_PROGRESS"),
    ("REDIRECTED", "IN_PROGRESS"),
}


# ─────────────────────────────────────────────────────────────────────────────
# Sección A — can_transition (síncrono, sin dependencias externas)
# ─────────────────────────────────────────────────────────────────────────────

class TestCanTransition:
    """Valida todas las aristas del grafo de transiciones y los casos borde."""

    def test_grafo_cubre_todos_los_estados_del_enum(self):
        # Si se añade un estado a TicketStatus sin reglas de transición, la
        # máquina lo trataría como desconocido y bloquearía el ticket.
        assert set(TicketStateMachine.VALID_TRANSITIONS) == set(ALL_STATES)

    def test_destinos_del_grafo_son_estados_validos(self):
        for destinos in TicketStateMachine.VALID_TRANSITIONS.values():
            assert set(destinos) <= set(ALL_STATES)

    @pytest.mark.parametrize("current,new", sorted(VALID_EDGES))
    def test_transiciones_validas(self, current, new):
        assert TicketStateMachine.can_transition(current, new) is True

    @pytest.mark.parametrize(
        "current,new",
        sorted(
            (a, b)
            for a in ALL_STATES
            for b in ALL_STATES
            if a != b and (a, b) not in VALID_EDGES
        ),
    )
    def test_transiciones_invalidas(self, current, new):
        assert TicketStateMachine.can_transition(current, new) is False

    def test_done_es_estado_terminal(self):
        assert TicketStateMachine.VALID_TRANSITIONS["DONE"] == []

    @pytest.mark.parametrize("state", ALL_STATES)
    def test_mismo_estado_devuelve_false(self, state):
        assert TicketStateMachine.can_transition(state, state) is False

    def test_none_current_status_devuelve_false(self):
        assert TicketStateMachine.can_transition(None, "IN_PROGRESS") is False

    def test_none_new_status_devuelve_false(self):
        assert TicketStateMachine.can_transition("TODO", None) is False

    def test_estado_desconocido_devuelve_false(self):
        assert TicketStateMachine.can_transition("UNKNOWN", "IN_PROGRESS") is False

    def test_estados_legacy_ya_no_existen(self):
        # BLOCKED_QUESTION y COMPLETED eran los nombres antiguos
        assert TicketStateMachine.can_transition("IN_PROGRESS", "BLOCKED_QUESTION") is False
        assert TicketStateMachine.can_transition("IN_PROGRESS", "COMPLETED") is False

    def test_cadena_vacia_devuelve_false(self):
        assert TicketStateMachine.can_transition("", "IN_PROGRESS") is False

    def test_comparacion_es_sensible_a_mayusculas(self):
        assert TicketStateMachine.can_transition("todo", "in_progress") is False

    def test_acepta_miembros_del_enum(self):
        # TicketStatus hereda de str, así que el enum se compara igual que su valor
        assert TicketStateMachine.can_transition(
            TicketStatus.TODO, TicketStatus.IN_PROGRESS
        ) is True


# ─────────────────────────────────────────────────────────────────────────────
# Helpers para crear dobles de ticket y usuario
# ─────────────────────────────────────────────────────────────────────────────

def make_ticket(status: TicketStatus, assignee_id=None) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(), status=status, assignee_id=assignee_id, pr_link=None
    )


def make_orm_user() -> SimpleNamespace:
    """Usuario estilo modelo ORM (expone .id como UUID)."""
    return SimpleNamespace(id=uuid4(), role="DEVELOPER")


def make_token_user() -> SimpleNamespace:
    """Usuario estilo TokenPayload (expone .sub como str, sin .id)."""
    return SimpleNamespace(sub=str(uuid4()), role="DEVELOPER")


# ─────────────────────────────────────────────────────────────────────────────
# Sección B — transition_to_in_progress / transition_to_completed
# ─────────────────────────────────────────────────────────────────────────────

AUDIT = "app.services.ticket_state_machine.TransitionAuditService.record_transition"


class TestTransitionToInProgress:

    async def test_valida_desde_todo(self):
        ticket = make_ticket(TicketStatus.TODO)
        user = make_orm_user()
        with patch(AUDIT, new=AsyncMock()):
            result = await TicketStateMachine.transition_to_in_progress(ticket, user, MagicMock())

        assert result["status"] == "success"
        assert result["ticket_id"] == str(ticket.id)
        assert result["previous_status"] == "TODO"
        assert result["new_status"] == "IN_PROGRESS"
        assert ticket.status == TicketStatus.IN_PROGRESS

    async def test_ticket_libre_se_asigna_a_quien_lo_inicia(self):
        ticket = make_ticket(TicketStatus.TODO, assignee_id=None)
        user = make_orm_user()
        with patch(AUDIT, new=AsyncMock()):
            result = await TicketStateMachine.transition_to_in_progress(ticket, user, MagicMock())

        assert ticket.assignee_id == user.id
        assert result["assignee_id"] == str(user.id)

    async def test_actor_desde_jwt_se_normaliza_a_uuid(self):
        # current_user puede ser un TokenPayload: el sub (str) se convierte a UUID
        ticket = make_ticket(TicketStatus.TODO, assignee_id=None)
        user = make_token_user()
        with patch(AUDIT, new=AsyncMock()) as audit:
            await TicketStateMachine.transition_to_in_progress(ticket, user, MagicMock())

        assert isinstance(ticket.assignee_id, UUID)
        assert ticket.assignee_id == UUID(user.sub)
        assert audit.await_args.kwargs["user_id"] == UUID(user.sub)

    async def test_no_reasigna_un_ticket_ya_asignado(self):
        # La comprobación de "robo" la hace claim_or_assert_assignee en el
        # router; la máquina de estados respeta el assignee existente.
        original = uuid4()
        ticket = make_ticket(TicketStatus.TODO, assignee_id=original)
        with patch(AUDIT, new=AsyncMock()):
            await TicketStateMachine.transition_to_in_progress(ticket, make_orm_user(), MagicMock())

        assert ticket.assignee_id == original

    @pytest.mark.parametrize("status", ["IN_PROGRESS", "DONE"])
    async def test_invalida_lanza_400_y_no_audita(self, status):
        ticket = make_ticket(TicketStatus(status))
        with patch(AUDIT, new=AsyncMock()) as audit:
            with pytest.raises(HTTPException) as exc:
                await TicketStateMachine.transition_to_in_progress(
                    ticket, make_orm_user(), MagicMock()
                )

        assert exc.value.status_code == 400
        assert ticket.status == TicketStatus(status)
        audit.assert_not_awaited()

    @pytest.mark.parametrize("status", ["BLOCKED", "REDIRECTED"])
    async def test_reanudar_desde_blocked_o_redirected(self, status):
        ticket = make_ticket(TicketStatus(status), assignee_id=uuid4())
        with patch(AUDIT, new=AsyncMock()):
            result = await TicketStateMachine.transition_to_in_progress(
                ticket, make_orm_user(), MagicMock()
            )
        assert result["previous_status"] == status
        assert ticket.status == TicketStatus.IN_PROGRESS

    async def test_registra_auditoria_con_from_y_to(self):
        ticket = make_ticket(TicketStatus.TODO)
        db = MagicMock()
        with patch(AUDIT, new=AsyncMock()) as audit:
            await TicketStateMachine.transition_to_in_progress(ticket, make_orm_user(), db)

        audit.assert_awaited_once()
        kwargs = audit.await_args.kwargs
        assert kwargs["db"] is db
        assert kwargs["ticket_id"] == ticket.id
        assert kwargs["event_type"] == TicketEventType.STATUS_CHANGED
        assert kwargs["from_status"] == "TODO"
        assert kwargs["to_status"] == "IN_PROGRESS"
        assert kwargs["extra"] == {"action": "start"}

    async def test_no_hace_commit(self):
        # El commit lo hace el router para que estado y evento sean atómicos
        db = MagicMock()
        db.commit = AsyncMock()
        with patch(AUDIT, new=AsyncMock()):
            await TicketStateMachine.transition_to_in_progress(
                make_ticket(TicketStatus.TODO), make_orm_user(), db
            )
        db.commit.assert_not_called()


class TestTransitionToCompleted:

    async def test_valida_desde_in_progress(self):
        ticket = make_ticket(TicketStatus.IN_PROGRESS, assignee_id=uuid4())
        pr_url = "https://github.com/org/repo/pull/42"
        with patch(AUDIT, new=AsyncMock()):
            result = await TicketStateMachine.transition_to_completed(
                ticket, make_orm_user(), pr_url, MagicMock()
            )

        assert result["status"] == "success"
        assert result["new_status"] == "DONE"
        assert result["pr_link"] == pr_url
        assert ticket.status == TicketStatus.DONE
        assert ticket.pr_link == pr_url

    async def test_sin_pr_link_no_sobrescribe_el_existente(self):
        ticket = make_ticket(TicketStatus.IN_PROGRESS, assignee_id=uuid4())
        ticket.pr_link = "https://github.com/org/repo/pull/1"
        with patch(AUDIT, new=AsyncMock()):
            result = await TicketStateMachine.transition_to_completed(
                ticket, make_orm_user(), None, MagicMock()
            )

        assert ticket.pr_link == "https://github.com/org/repo/pull/1"
        assert result["pr_link"] is None

    async def test_registra_auditoria(self):
        ticket = make_ticket(TicketStatus.IN_PROGRESS, assignee_id=uuid4())
        with patch(AUDIT, new=AsyncMock()) as audit:
            await TicketStateMachine.transition_to_completed(
                ticket, make_orm_user(), "https://x/pull/1", MagicMock()
            )

        kwargs = audit.await_args.kwargs
        assert kwargs["from_status"] == "IN_PROGRESS"
        assert kwargs["to_status"] == "DONE"
        assert kwargs["extra"] == {"action": "complete", "pr_link": "https://x/pull/1"}

    @pytest.mark.parametrize("status", ["TODO", "BLOCKED", "REDIRECTED", "DONE"])
    async def test_invalida_lanza_400(self, status):
        ticket = make_ticket(TicketStatus(status))
        with patch(AUDIT, new=AsyncMock()) as audit:
            with pytest.raises(HTTPException) as exc:
                await TicketStateMachine.transition_to_completed(
                    ticket, make_orm_user(), "https://x/pull/1", MagicMock()
                )
        assert exc.value.status_code == 400
        assert ticket.status == TicketStatus(status)
        audit.assert_not_awaited()


class TestModuleAliases:
    """Los routers llaman a estas funciones como atributos del MÓDULO."""

    def test_alias_de_modulo_apuntan_a_la_clase(self):
        assert tsm_module.log_ticket_event is TicketStateMachine.log_ticket_event
        assert tsm_module.transition_to_in_progress is TicketStateMachine.transition_to_in_progress
        assert tsm_module.transition_to_completed is TicketStateMachine.transition_to_completed


# ─────────────────────────────────────────────────────────────────────────────
# Sección C — log_ticket_event con DB SQLite real
# ─────────────────────────────────────────────────────────────────────────────

class TestLogTicketEvent:

    async def test_detail_string_se_envuelve_en_dict(self, db_session: AsyncSession, sample_ticket):
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

    async def test_detail_string_json_se_parsea(self, db_session: AsyncSession, sample_ticket):
        event = await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=sample_ticket.id,
            event_type=TicketEventType.UPDATED,
            user_id=sample_ticket.assignee_id,
            detail='{"campo": "title"}',
        )

        assert event.detail["campo"] == "title"
        assert "message" not in event.detail

    async def test_detail_dict_agrega_timestamp(self, db_session: AsyncSession, sample_ticket):
        original = {"texto": "comentario de prueba"}
        event = await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=sample_ticket.id,
            event_type=TicketEventType.COMMENT,
            user_id=sample_ticket.assignee_id,
            detail=original,
        )

        assert event.detail["texto"] == "comentario de prueba"
        assert "timestamp" in event.detail
        # No muta el dict del llamador
        assert "timestamp" not in original

    async def test_detail_none_solo_lleva_timestamp(self, db_session: AsyncSession, sample_ticket):
        event = await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=sample_ticket.id,
            event_type=TicketEventType.CREATED,
            user_id=sample_ticket.assignee_id,
        )
        assert set(event.detail) == {"timestamp"}

    async def test_event_type_enum_se_conserva(self, db_session: AsyncSession, sample_ticket):
        event = await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=sample_ticket.id,
            event_type=TicketEventType.COMPLETED,
            user_id=sample_ticket.assignee_id,
            detail="completado",
        )
        assert event.event_type == TicketEventType.COMPLETED

    async def test_event_type_string_se_normaliza(self, db_session: AsyncSession, sample_ticket):
        event = await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=sample_ticket.id,
            event_type="QUESTION_RAISED",
            user_id=sample_ticket.assignee_id,
            detail={"pregunta": "¿cuándo?"},
        )

        assert event.event_type == TicketEventType.QUESTION_RAISED
        assert event.ticket_id == sample_ticket.id

    async def test_evento_queda_persistido(self, db_session: AsyncSession, sample_ticket):
        await TicketStateMachine.log_ticket_event(
            db=db_session,
            ticket_id=sample_ticket.id,
            event_type=TicketEventType.MOVED,
            user_id=sample_ticket.assignee_id,
        )
        rows = (
            await db_session.execute(
                select(TicketEvent).where(TicketEvent.ticket_id == sample_ticket.id)
            )
        ).scalars().all()
        assert [e.event_type for e in rows] == [TicketEventType.MOVED]

    async def test_event_type_desconocido_lanza_500_y_hace_rollback(self):
        db = MagicMock()
        db.rollback = AsyncMock()
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.log_ticket_event(
                db=db, ticket_id=uuid4(), event_type="NO_EXISTE", user_id=uuid4()
            )
        assert exc.value.status_code == 500
        db.rollback.assert_awaited_once()
        db.add.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# Sección D — Métodos heredados basados en dict (sin uso desde los routers)
# ─────────────────────────────────────────────────────────────────────────────

def ticket_dict(status: str) -> dict:
    return {"id": str(uuid4()), "status": status, "time_spent_seconds": 0}


class TestLegacyDictMethods:
    """Solo se cubren las validaciones previas a tocar la base de datos."""

    async def test_transition_invalida_lanza_400(self):
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.transition(MagicMock(), ticket_dict("DONE"), "TODO", "u")
        assert exc.value.status_code == 400

    @pytest.mark.parametrize("pr_link", ["", "   ", "github.com/org/repo/pull/1"])
    async def test_complete_ticket_rechaza_pr_link_invalido(self, pr_link):
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.complete_ticket(
                MagicMock(), ticket_dict("IN_PROGRESS"), "u", pr_link
            )
        assert exc.value.status_code == 400

    @pytest.mark.parametrize("status", ["BLOCKED", "REDIRECTED", "DONE"])
    async def test_complete_ticket_rechaza_estado(self, status):
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.complete_ticket(
                MagicMock(), ticket_dict(status), "u", "https://x/pull/1"
            )
        assert exc.value.status_code == 400

    async def test_raise_question_requiere_in_progress(self):
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.raise_question(MagicMock(), ticket_dict("TODO"), "u", "¿?")
        assert exc.value.status_code == 400

    async def test_raise_question_requiere_texto(self):
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.raise_question(
                MagicMock(), ticket_dict("IN_PROGRESS"), "u", "   "
            )
        assert exc.value.status_code == 400

    async def test_resolve_question_requiere_blocked(self):
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.resolve_question(MagicMock(), ticket_dict("IN_PROGRESS"), "u")
        assert exc.value.status_code == 400

    async def test_redirect_requiere_motivo_de_10_caracteres(self):
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.redirect_ticket(
                MagicMock(), ticket_dict("IN_PROGRESS"), "a", "b", "corto"
            )
        assert exc.value.status_code == 400

    async def test_redirect_a_si_mismo_lanza_400(self):
        with pytest.raises(HTTPException) as exc:
            await TicketStateMachine.redirect_ticket(
                MagicMock(), ticket_dict("IN_PROGRESS"), "a", "a", "motivo suficientemente largo"
            )
        assert exc.value.status_code == 400

    async def test_raise_question_registra_evento(self, db_session: AsyncSession, sample_ticket):
        await TicketStateMachine.raise_question(
            db_session,
            {"id": sample_ticket.id, "status": "IN_PROGRESS"},
            sample_ticket.assignee_id,
            "¿Cuál es el criterio de aceptación?",
        )
        event = (
            await db_session.execute(
                select(TicketEvent).where(TicketEvent.ticket_id == sample_ticket.id)
            )
        ).scalar_one()
        assert event.event_type == TicketEventType.QUESTION_RAISED
        assert event.detail["question"] == "¿Cuál es el criterio de aceptación?"

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "BUG: TicketStateMachine.transition registra el evento con "
            "event_type='STATE_CHANGED' (ticket_state_machine.py:458), que no "
            "existe en TicketEventType (es STATUS_CHANGED): toda transición "
            "válida termina en HTTP 500. Igual pasa con 'TICKET_COMPLETED' "
            "(línea 609) y 'TICKET_REDIRECTED' (línea 1002). Código sin uso "
            "desde los routers, pero público."
        ),
    )
    async def test_transition_valida_registra_evento(self, db_session: AsyncSession, sample_ticket):
        await TicketStateMachine.transition(
            db_session,
            {"id": sample_ticket.id, "status": "TODO"},
            "IN_PROGRESS",
            sample_ticket.assignee_id,
        )
