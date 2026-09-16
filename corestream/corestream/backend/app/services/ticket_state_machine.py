"""
Máquina de estados para la gestión de tickets en CoreStream.

Este módulo implementa la lógica central de transiciones de estado para tickets,
incluyendo validación de cambios permitidos, registros de eventos, y gestión de
timers de ejecución y bloqueo. Es el corazón de la gestión de proyectos en CoreStream.

Diagrama de transiciones de estado:
    TODO -----> IN_PROGRESS -----> BLOCKED
                     ^                |
                     |                v
                   REDIRECTED      (BLOCKED -> IN_PROGRESS via resolve)
                     ^
                     |
               IN_PROGRESS -----> COMPLETED
"""

from datetime import datetime, timezone
from typing import Union
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TicketEvent, TicketStatus
from app.models.ticket_event import TicketEventType
from app.services.timer_service import TimerService
from app.services.transition_audit import TransitionAuditService


class TicketStateMachine:
    """
    Clase que encapsula la máquina de estados de los tickets.

    Gestiona todas las transiciones de estado permitidas, valida que los cambios
    sean legales, registra eventos con timestamps precisos, y maneja las
    operaciones asociadas como pausa/reanudación de timers.

    Transiciones válidas:
        TODO        → IN_PROGRESS
        IN_PROGRESS → BLOCKED
        IN_PROGRESS → REDIRECTED  (semántico; el ticket vuelve a TODO del nuevo asignado)
        IN_PROGRESS → COMPLETED
        BLOCKED     → IN_PROGRESS
        REDIRECTED  → TODO        (reservado para futura lógica de aceptación)
        COMPLETED   → (ninguna)
    """

    VALID_TRANSITIONS: dict[str, list[str]] = {
        # Workflow de desarrollo (sin cambios)
        "TODO": ["IN_PROGRESS"],
        "IN_PROGRESS": ["BLOCKED_QUESTION", "REDIRECTED", "COMPLETED"],
        "BLOCKED": ["IN_PROGRESS"],
        "BLOCKED_QUESTION": ["IN_PROGRESS"],
        "REDIRECTED": ["TODO"],
        "COMPLETED": [],
        # Workflow de soporte
        "REPORTED": ["INVESTIGATING"],
        "INVESTIGATING": ["RESOLVED"],
        "RESOLVED": [],
    }

    # ------------------------------------------------------------------
    # Validación de transición
    # ------------------------------------------------------------------

    @staticmethod
    def can_transition(current_status: str, new_status: str) -> bool:
        """
        Verifica si una transición entre dos estados es válida.

        Args:
            current_status: Estado actual del ticket (valor del enum TicketStatus).
            new_status:     Estado destino deseado.

        Returns:
            True si la transición está permitida, False en caso contrario.
        """
        if not current_status or not new_status:
            return False
        if current_status not in TicketStateMachine.VALID_TRANSITIONS:
            return False
        if current_status == new_status:
            return False
        return new_status in TicketStateMachine.VALID_TRANSITIONS[current_status]

    # ------------------------------------------------------------------
    # Registro de eventos (compatibilidad hacia atrás)
    # ------------------------------------------------------------------

    @staticmethod
    async def log_ticket_event(
        db: AsyncSession,
        ticket_id: UUID,
        event_type: Union[str, TicketEventType],
        user_id: UUID,
        detail: Union[str, dict],
    ) -> TicketEvent:
        """
        Crea y registra un evento de auditoría para un ticket.

        Acepta tanto strings como dicts en el parámetro detail para mantener
        compatibilidad con llamadas existentes en el router.

        Args:
            db:         Sesión async de SQLAlchemy.
            ticket_id:  UUID del ticket.
            event_type: Tipo de evento (TicketEventType enum o string equivalente).
            user_id:    UUID del usuario que ejecuta la acción.
            detail:     Mensaje o diccionario con datos del evento.

        Returns:
            TicketEvent creado y agregado a la sesión (sin commit).
        """
        try:
            if isinstance(detail, str):
                detail_payload: dict = {
                    "message": detail,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            else:
                detail_payload = detail
                detail_payload.setdefault(
                    "timestamp", datetime.now(timezone.utc).isoformat()
                )
            
            # Extraemos el valor del Enum en formato string
            event_type_str = event_type.value if hasattr(event_type, "value") else str(event_type)

            new_event = TicketEvent(
                ticket_id=ticket_id,
                user_id=user_id,
                event_type=event_type_str,
                detail=detail_payload,
            )
            db.add(new_event)

            # Guardamos en la base de datos
            await db.commit()
            await db.refresh(new_event)

            return new_event

        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear evento de auditoría: {exc}",
            )

    # ------------------------------------------------------------------
    # Transición: TODO → IN_PROGRESS
    # ------------------------------------------------------------------

    @staticmethod
    async def transition_to_in_progress(
        ticket,
        current_user,
        db: AsyncSession,
    ) -> dict:
        """
        Transiciona el ticket de TODO a IN_PROGRESS.

        Valida la transición con can_transition, actualiza el estado,
        asigna el usuario actual como asignado, y registra el evento
        con timestamp preciso.

        Args:
            ticket:       ORM Ticket a transicionar.
            current_user: Usuario que inicia el trabajo.
            db:           Sesión async de SQLAlchemy.

        Returns:
            dict con status="success" y ticket_id.

        Raises:
            HTTPException 400: Si la transición no es válida.
        """
        current_status = (
            ticket.status.value if hasattr(ticket.status, "value") else ticket.status
        )

        if not TicketStateMachine.can_transition(current_status, "IN_PROGRESS"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede transicionar de {current_status} a IN_PROGRESS",
            )

        ticket.status = TicketStatus.IN_PROGRESS
        ticket.assignee_id = current_user.id

        await TransitionAuditService.record_transition(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            event_type=TicketEventType.STATUS_CHANGED,
            from_status=current_status,
            to_status="IN_PROGRESS",
        )

        return {"status": "success", "ticket_id": str(ticket.id)}

    # ------------------------------------------------------------------
    # Transición: IN_PROGRESS → BLOCKED
    # ------------------------------------------------------------------

    @staticmethod
    async def transition_to_blocked(
        ticket,
        current_user,
        question_text: str,
        db: AsyncSession,
    ) -> dict:
        """
        Transiciona el ticket de IN_PROGRESS a BLOCKED.

        Pausa el timer, actualiza el estado, guarda el motivo de bloqueo,
        y registra el evento con timestamp preciso.

        Args:
            ticket:        ORM Ticket a transicionar.
            current_user:  Usuario que plantea la pregunta bloqueante.
            question_text: Texto de la pregunta bloqueante.
            db:            Sesión async de SQLAlchemy.

        Returns:
            dict con status="success" y ticket_id.

        Raises:
            HTTPException 400: Si el ticket no está en IN_PROGRESS.
        """
        current_status = (
            ticket.status.value if hasattr(ticket.status, "value") else ticket.status
        )

        if not TicketStateMachine.can_transition(current_status, "BLOCKED_QUESTION"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede transicionar de {current_status} a BLOCKED_QUESTION",
            )

        await TimerService().pause_timer(ticket.id, db)

        ticket.status = TicketStatus.BLOCKED_QUESTION
        ticket.block_reason = question_text

        await TransitionAuditService.record_transition(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            event_type=TicketEventType.QUESTION_RAISED,
            from_status=current_status,
            to_status="BLOCKED_QUESTION",
            extra={"question": question_text},
        )

        return {"status": "success", "ticket_id": str(ticket.id)}

    # ------------------------------------------------------------------
    # Transición: BLOCKED → IN_PROGRESS
    # ------------------------------------------------------------------

    @staticmethod
    async def transition_to_in_progress_from_blocked(
        ticket,
        current_user,
        resolution: str,
        db: AsyncSession,
    ) -> dict:
        """
        Transiciona el ticket de BLOCKED a IN_PROGRESS (resolución de pregunta).

        Reanuda el timer, limpia el motivo de bloqueo, y registra el evento
        con timestamp preciso.

        Args:
            ticket:       ORM Ticket a transicionar.
            current_user: Usuario que resuelve la pregunta.
            resolution:   Texto de la resolución.
            db:           Sesión async de SQLAlchemy.

        Returns:
            dict con status="success" y ticket_id.

        Raises:
            HTTPException 400: Si el ticket no está en BLOCKED.
        """
        current_status = (
            ticket.status.value if hasattr(ticket.status, "value") else ticket.status
        )

        if not TicketStateMachine.can_transition(current_status, "IN_PROGRESS"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede transicionar de {current_status} a IN_PROGRESS",
            )

        await TimerService().resume_timer(ticket.id, db)

        ticket.status = TicketStatus.IN_PROGRESS
        ticket.block_reason = None

        await TransitionAuditService.record_transition(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            event_type=TicketEventType.QUESTION_RESOLVED,
            from_status=current_status,
            to_status="IN_PROGRESS",
            extra={"resolution": resolution},
        )

        return {"status": "success", "ticket_id": str(ticket.id)}

    # ------------------------------------------------------------------
    # Transición: IN_PROGRESS → TODO (vía redirección a otro usuario)
    # ------------------------------------------------------------------

    @staticmethod
    async def transition_to_redirected(
        ticket,
        current_user,
        to_user_id: UUID,
        reason: str,
        db: AsyncSession,
    ) -> dict:
        """
        Redirige el ticket a otro usuario: IN_PROGRESS → TODO (nuevo asignado).

        Pausa el timer si estaba activo, reasigna el ticket al nuevo usuario,
        establece el estado en TODO para que aparezca en la cola del nuevo
        asignado, y registra el evento con timestamp preciso.

        Args:
            ticket:       ORM Ticket a redirigir.
            current_user: Usuario que ejecuta la redirección.
            to_user_id:   UUID del usuario destino.
            reason:       Motivo documentado de la redirección.
            db:           Sesión async de SQLAlchemy.

        Returns:
            dict con status="success", ticket_id y from_user_id.

        Raises:
            HTTPException 400: Si el ticket no está en IN_PROGRESS.
        """
        current_status = (
            ticket.status.value if hasattr(ticket.status, "value") else ticket.status
        )

        if current_status not in ("IN_PROGRESS", "TODO"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Solo se puede redirigir un ticket en IN_PROGRESS o TODO. "
                    f"Estado actual: {current_status}"
                ),
            )

        old_assignee_id = ticket.assignee_id

        if current_status == "IN_PROGRESS":
            await TimerService().pause_timer(ticket.id, db)

        ticket.assignee_id = to_user_id
        ticket.block_reason = reason
        ticket.status = TicketStatus.TODO

        await TransitionAuditService.record_event(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            event_type=TicketEventType.REDIRECTED,
            detail={
                "from_status": current_status,
                "to_status": "TODO",
                "from_user_id": str(old_assignee_id) if old_assignee_id else None,
                "to_user_id": str(to_user_id),
                "reason": reason,
            },
        )

        return {
            "status": "success",
            "ticket_id": str(ticket.id),
            "from_user_id": str(old_assignee_id) if old_assignee_id else None,
        }

    # ------------------------------------------------------------------
    # Transición: IN_PROGRESS → COMPLETED
    # ------------------------------------------------------------------

    @staticmethod
    async def transition_to_completed(
        ticket,
        current_user,
        pr_link: str,
        db: AsyncSession,
    ) -> dict:
        """
        Completa un ticket transitando a COMPLETED con validaciones específicas.

        Detiene el timer, registra el timestamp de completación en
        ticket.completed_at, vincula el PR link, y registra el evento
        con timestamp preciso.

        Args:
            ticket:       ORM Ticket a completar.
            current_user: Usuario que completa el ticket.
            pr_link:      URL del pull request asociado.
            db:           Sesión async de SQLAlchemy.

        Returns:
            dict con status="success" y ticket_id.

        Raises:
            HTTPException 400: Si la transición no es válida.
        """
        current_status = (
            ticket.status.value if hasattr(ticket.status, "value") else ticket.status
        )

        if not TicketStateMachine.can_transition(current_status, "COMPLETED"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede transicionar de {current_status} a COMPLETED",
            )

        await TimerService().stop_timer(ticket.id, db)

        ticket.status = TicketStatus.COMPLETED
        ticket.pr_link = pr_link
        ticket.completed_at = datetime.now(timezone.utc)

        await TransitionAuditService.record_transition(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            event_type=TicketEventType.COMPLETED,
            from_status=current_status,
            to_status="COMPLETED",
            extra={"pr_link": pr_link},
        )

        return {"status": "success", "ticket_id": str(ticket.id)}

    # ------------------------------------------------------------------
    # Transición soporte: REPORTED → INVESTIGATING
    # ------------------------------------------------------------------

    @staticmethod
    async def transition_to_investigating(
        ticket,
        current_user,
        db: AsyncSession,
    ) -> dict:
        """Transiciona un ticket de soporte de REPORTED a INVESTIGATING."""
        current_status = (
            ticket.status.value if hasattr(ticket.status, "value") else ticket.status
        )

        if not TicketStateMachine.can_transition(current_status, "INVESTIGATING"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede transicionar de {current_status} a INVESTIGATING",
            )

        ticket.status = TicketStatus.INVESTIGATING

        await TransitionAuditService.record_transition(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            event_type=TicketEventType.STATUS_CHANGED,
            from_status=current_status,
            to_status="INVESTIGATING",
        )

        return {"status": "success", "ticket_id": str(ticket.id)}

    # ------------------------------------------------------------------
    # Transición soporte: INVESTIGATING → RESOLVED
    # ------------------------------------------------------------------

    @staticmethod
    async def transition_to_resolved(
        ticket,
        current_user,
        pr_link: str,
        db: AsyncSession,
    ) -> dict:
        """Transiciona un ticket de soporte de INVESTIGATING a RESOLVED. Requiere el PR que corrige el bug."""
        current_status = (
            ticket.status.value if hasattr(ticket.status, "value") else ticket.status
        )

        if not TicketStateMachine.can_transition(current_status, "RESOLVED"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede transicionar de {current_status} a RESOLVED",
            )

        ticket.status = TicketStatus.RESOLVED
        ticket.pr_link = pr_link
        ticket.completed_at = datetime.now(timezone.utc)

        await TransitionAuditService.record_transition(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            event_type=TicketEventType.STATUS_CHANGED,
            from_status=current_status,
            to_status="RESOLVED",
            extra={"pr_link": pr_link},
        )

        return {"status": "success", "ticket_id": str(ticket.id)}


# Instancia singleton para uso directo desde routers
ticket_state_machine = TicketStateMachine()
