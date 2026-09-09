"""
Servicio de auditoría de transiciones de estado para tickets.

Responsabilidad única: registrar cada cambio de estado con un timestamp
UTC preciso embebido en el campo JSONB detail del TicketEvent.

El TicketEvent.created_at (server_default=func.now()) es el timestamp
autoritativo del lado del servidor. El campo detail.transitioned_at
embebe una copia ISO 8601 para acceso directo sin JOIN y para
garantizar trazabilidad even si el created_at por alguna razón difiere.

Uso:
    from app.services.transition_audit import TransitionAuditService

    await TransitionAuditService.record_transition(
        db=db,
        ticket_id=ticket.id,
        user_id=current_user.id,
        event_type=TicketEventType.STATUS_CHANGED,
        from_status="TODO",
        to_status="IN_PROGRESS",
    )
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket_event import TicketEvent, TicketEventType


class TransitionAuditService:
    """
    Registra transiciones de estado con timestamps precisos en UTC.

    Cada transición exitosa genera un TicketEvent cuyo campo detail
    contiene:
      - from_status: estado origen
      - to_status:   estado destino
      - transitioned_at: timestamp ISO 8601 UTC (client-side precision)
      - cualquier campo extra que el caller quiera incluir

    El TicketEvent.created_at es el timestamp server-side autoritativo.
    """

    @staticmethod
    async def record_transition(
        db: AsyncSession,
        ticket_id: UUID,
        user_id: UUID,
        event_type: TicketEventType,
        from_status: str,
        to_status: str,
        extra: Optional[dict] = None,
    ) -> TicketEvent:
        """
        Crea un TicketEvent de transición con timestamp preciso.

        Args:
            db:           Sesión async de SQLAlchemy.
            ticket_id:    UUID del ticket que transiciona.
            user_id:      UUID del usuario que ejecuta la transición.
            event_type:   Tipo de evento (TicketEventType enum).
            from_status:  Valor de estado origen (str del enum TicketStatus).
            to_status:    Valor de estado destino (str del enum TicketStatus).
            extra:        Campos adicionales que se mezclan en detail (opcional).

        Returns:
            TicketEvent ya agregado a la sesión (sin commit — el commit
            se delega al router para que sea atómico con el cambio de estado).

        Raises:
            HTTPException 500: Si falla la creación del evento de auditoría.
        """
        try:
            transitioned_at = datetime.now(timezone.utc).isoformat()

            detail: dict = {
                "from_status": from_status,
                "to_status": to_status,
                "transitioned_at": transitioned_at,
            }

            if extra:
                detail.update(extra)

            event = TicketEvent(
                ticket_id=ticket_id,
                user_id=user_id,
                event_type=event_type,
                detail=detail,
            )
            db.add(event)
            return event

        except Exception as exc:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar auditoría de transición: {exc}",
            )

    @staticmethod
    async def record_event(
        db: AsyncSession,
        ticket_id: UUID,
        user_id: UUID,
        event_type: TicketEventType,
        detail: dict,
    ) -> TicketEvent:
        """
        Crea un TicketEvent genérico (no de transición) con timestamp UTC.

        Útil para eventos como QUESTION_RAISED, QUESTION_RESOLVED,
        REDIRECTED, COMMENT, etc., donde el detail es libre pero se
        quiere garantizar que siempre lleve un campo 'recorded_at'.

        Args:
            db:         Sesión async de SQLAlchemy.
            ticket_id:  UUID del ticket al que pertenece el evento.
            user_id:    UUID del usuario que genera el evento.
            event_type: Tipo de evento (TicketEventType enum).
            detail:     Diccionario con datos del evento.

        Returns:
            TicketEvent ya agregado a la sesión (sin commit).
        """
        try:
            detail.setdefault("recorded_at", datetime.now(timezone.utc).isoformat())

            event = TicketEvent(
                ticket_id=ticket_id,
                user_id=user_id,
                event_type=event_type,
                detail=detail,
            )
            db.add(event)
            return event

        except Exception as exc:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar evento de auditoría: {exc}",
            )
