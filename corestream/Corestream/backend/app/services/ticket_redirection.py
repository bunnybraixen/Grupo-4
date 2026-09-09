"""
Servicio para la lógica de redirección de tickets (CS-020).

Maneja el traspaso de responsabilidad de tickets entre usuarios,
incluyendo la máquina de estados, gestión de tiempo y trazabilidad.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Application, Ticket, TicketEvent, TicketEventType, TicketStatus, User
from app.routers.websocket import manager
from app.services.notification_service import flush_pending_notifications, notify_ticket_redirected
from app.services.timer_service import timer_service

logger = logging.getLogger("corestream.ticket_redirection")


class TicketRedirectionService:
    """Servicio para gestionar la redirección de tickets."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def redirect_ticket(
        self,
        ticket_id: UUID,
        from_user_id: UUID,
        to_user_id: UUID,
        justification: str
    ) -> Ticket:
        """
        Redirige un ticket de un usuario a otro de forma completamente atómica.

        Todos los cambios (assignee, status, timer, eventos) se persisten en un
        único commit. Si cualquier paso falla se ejecuta rollback completo,
        garantizando que nunca exista una redirección sin su evento de auditoría.

        Args:
            ticket_id: ID del ticket a redirigir
            from_user_id: ID del usuario actual asignado
            to_user_id: ID del nuevo usuario asignado
            justification: Justificación obligatoria del traspaso (min 10 chars)

        Returns:
            Ticket: El ticket actualizado y refrescado desde BD

        Raises:
            ValueError: Si la validación falla o se produce un error en la BD
        """
        if not justification or not justification.strip():
            raise ValueError("La justificación es obligatoria para redirigir un ticket")

        ticket: Optional[Ticket] = None

        try:
            # ── 1. Cargar ticket con lock pesimista (anti race-condition) ──────
            result = await self.db.execute(
                select(Ticket)
                .options(selectinload(Ticket.epic))
                .where(Ticket.id == ticket_id)
                .with_for_update()
            )
            ticket = result.scalar_one_or_none()

            if not ticket:
                raise ValueError(f"Ticket con ID {ticket_id} no encontrado")

            # ── 2. Cargar usuario solicitante y obtener su rol ───────────
            from_user_result = await self.db.execute(
                select(User).options(selectinload(User.role)).where(User.id == from_user_id)
            )
            from_user = from_user_result.scalar_one_or_none()
            
            user_role = ""
            if from_user and from_user.role:
                # Soporta tanto si role es un objeto (relación) o un string directo
                user_role = from_user.role.name if hasattr(from_user.role, 'name') else str(from_user.role)

            # ── 3. Validar permisos de redirección ───────────
            is_assignee = (ticket.assignee_id == from_user_id)
            is_privileged = user_role in ("ADMIN", "TEAM_LEADER", "GROUP_LEADER")

            if not is_assignee and not is_privileged:
                raise ValueError("Solo el usuario asignado, líderes o administradores pueden redirigir el ticket")

            # ── 3b. Seguridad cross-app: líder solo redirige sus apps ──────────
            # (El ADMIN global salta esta validación para poder mover todo)
            if is_privileged and user_role not in ("ADMIN", "TEAM_LEADER"):
                if ticket.epic and ticket.epic.application_id:
                    app_result = await self.db.execute(
                        select(Application).where(
                            Application.id == ticket.epic.application_id,
                            Application.owner_id == from_user_id,
                        )
                    )
                    if not app_result.scalar_one_or_none():
                        raise ValueError(
                            f"El líder solo puede redirigir tickets de aplicaciones que posee. "
                            f"Ticket {ticket_id} pertenece a la app {ticket.epic.application_id}."
                        )

            # ── 4. Validar usuario destino ────────────────────────────────────
            new_user_result = await self.db.execute(
                select(User).where(User.id == to_user_id)
            )
            if not new_user_result.scalar_one_or_none():
                raise ValueError(f"Usuario destino con ID {to_user_id} no encontrado")

            previous_status = (
                ticket.status.value if hasattr(ticket.status, "value") else str(ticket.status)
            )
            is_in_progress = previous_status == "IN_PROGRESS"

            # ── 5. Pausar timer en BD (modifica ticket.time_spent_seconds) ────
            # timer_service.pause_timer actualiza el objeto en sesión sin commit propio.
            if is_in_progress:
                await timer_service.pause_timer(ticket_id, self.db)

            # ── 6. Mutar ticket ───────────────────────────────────────────────
            ticket.assignee_id = to_user_id
            if is_in_progress:
                ticket.status = TicketStatus.TODO

            new_status = "TODO" if is_in_progress else previous_status

            # ── 7. Evento principal de redirección (obligatorio) ──────────────
            self.db.add(TicketEvent(
                ticket_id=ticket_id,
                user_id=from_user_id,
                event_type=TicketEventType.REDIRECTED,
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                detail={
                    "justification": justification,
                    "previous_status": previous_status,
                    "new_status": new_status,
                    "redirection_timestamp": datetime.now(timezone.utc).isoformat(),
                },
            ))

            # ── 8. Evento de cambio de estado (si aplica) ─────────────────────
            if is_in_progress:
                self.db.add(TicketEvent(
                    ticket_id=ticket_id,
                    user_id=from_user_id,
                    event_type=TicketEventType.STATUS_CHANGED,
                    detail={
                        "from_status": "IN_PROGRESS",
                        "to_status": "TODO",
                        "reason": "Redirección automática al cambiar de asignado",
                    },
                ))

            # ── 9. Evento de asignación para el nuevo usuario ─────────────────
            self.db.add(TicketEvent(
                ticket_id=ticket_id,
                user_id=from_user_id,
                event_type=TicketEventType.TICKET_ASSIGNED,
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                detail={
                    "justification": justification,
                    "assigned_at": datetime.now(timezone.utc).isoformat(),
                },
            ))

            # ── 9b. Notificación DB para el nuevo asignado (antes del commit) ──
            redirector_name = (
                from_user.full_name or from_user.email
                if from_user
                else str(from_user_id)
            )
            await notify_ticket_redirected(
                self.db,
                ticket_id=ticket_id,
                new_assignee_id=to_user_id,
                redirector_name=redirector_name,
                ticket_title=ticket.title,
                justification=justification,
            )

            # ── 10. ÚNICO COMMIT — todo entra o nada entra ────────────────────
            await self.db.commit()
            await self.db.refresh(ticket)

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as exc:
            await self.db.rollback()
            raise ValueError(f"Error en redirección atómica: {exc}") from exc

        # ── 11. Encolar entrega WebSocket de notificación (post-commit) ─────
        await flush_pending_notifications(self.db)

        # ── 12. Evento WebSocket en tiempo real para actualizar workbench ────
        await self._send_redirection_notification(
            ticket=ticket,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            justification=justification,
        )

        return ticket

    async def get_team_members(self, epic_id: UUID) -> list[User]:
        """
        Obtiene los miembros del equipo que pueden recibir tickets redirigidos.

        Args:
            epic_id: ID de la épica para filtrar miembros relevantes

        Returns:
            list[User]: Lista de usuarios disponibles para redirección
        """
        from app.models import Role

        # Only DEVELOPER and TEAM_LEADER can receive redirected tickets.
        # ADMIN accounts are excluded here and defensively in the frontend.
        allowed_roles = ["DEVELOPER", "TEAM_LEADER", "GROUP_LEADER"]
        result = await self.db.execute(
            select(User)
            .join(User.role)
            .options(selectinload(User.role))
            .where(User.is_active, Role.name.in_(allowed_roles))
            .order_by(User.full_name)
        )
        return result.scalars().all()

    async def _send_redirection_notification(
        self,
        ticket: Ticket,
        from_user_id: UUID,
        to_user_id: UUID,
        justification: str
    ):
        """
        Envía notificaciones push vía WebSocket para la redirección.
        
        Args:
            ticket: Ticket redirigido
            from_user_id: ID del usuario que redirige
            to_user_id: ID del usuario que recibe el ticket
            justification: Justificación del traspaso
        """
        try:
            # Notificación para el nuevo asignado - enviar Ticket completo
            ticket_data = {
                # Campos completos del modelo Ticket
                "id": str(ticket.id),
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status.value if hasattr(ticket.status, 'value') else str(ticket.status),
                "priority": ticket.priority.value if hasattr(ticket.priority, 'value') else str(ticket.priority),
                "assignee_id": str(ticket.assignee_id) if ticket.assignee_id else None,
                "epic_id": str(ticket.epic_id) if ticket.epic_id else None,
                "order_index": ticket.order_index,
                "time_spent_seconds": ticket.time_spent_seconds,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
                # Datos relacionados
                "epic": {
                    "id": str(ticket.epic.id),
                    "title": ticket.epic.title
                } if ticket.epic else None,
                # Metadatos de redirección
                "from_user_id": str(from_user_id),
                "justification": justification,
                "redirected_at": datetime.utcnow().isoformat(),
                "highlight": True  # Para resaltar en el workbench
            }
            
            await manager.publish_ticket_event(
                event_type="TICKET_ASSIGNED",
                ticket_data=ticket_data,
                target_user_id=str(to_user_id)
            )
            
            # Notificación de estado cambiado si aplica
            if ticket.status == "TODO":
                await manager.publish_ticket_event(
                    event_type="TICKET_STATUS_CHANGED",
                    ticket_data={
                        "ticket_id": str(ticket.id),
                        "from_status": "IN_PROGRESS",
                        "to_status": "TODO",
                        "reason": "Redirección automática"
                    },
                    target_user_id=str(to_user_id)
                )
                
        except Exception:
            # Log error pero no fallar la redirección
            logger.exception("Error enviando notificación de redirección")
