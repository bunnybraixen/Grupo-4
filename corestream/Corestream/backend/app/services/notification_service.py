"""
Servicio de notificaciones para CoreStream — CS-025.

Patrón de dos pasos:
  1. create_notification()  → guarda en DB (síncrono con la sesión del caller)
  2. enqueue_notification() → encola en ARQ para entrega WebSocket (post-commit)

Separar persistencia de entrega garantiza que la notificación nunca se pierda
aunque el WebSocket no esté disponible: ARQ reintenta hasta 3 veces.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from arq import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, NotificationType

logger = logging.getLogger(__name__)

# Pool ARQ global — se inicializa en el startup de FastAPI y se cierra en shutdown.
_arq_pool: Optional[ArqRedis] = None


def set_arq_pool(pool: ArqRedis) -> None:
    """Llamar desde main.py lifespan después de crear el pool."""
    global _arq_pool
    _arq_pool = pool


def get_arq_pool() -> Optional[ArqRedis]:
    return _arq_pool


# ---------------------------------------------------------------------------
# Paso 1: Persistencia (sincrónica con la sesión del caller)
# ---------------------------------------------------------------------------

async def create_notification(
    db: AsyncSession,
    *,
    user_id: UUID | str,
    title: str,
    message: str,
    notification_type: str,
    ticket_id: Optional[UUID | str] = None,
) -> Notification:
    """
    Guarda la notificación en PostgreSQL usando la sesión activa del caller.

    NO hace commit propio — el caller debe commitear para mantener atomicidad
    con la operación que disparó la notificación (ej. cambio de estado de ticket).

    Después del commit del caller, llamar a enqueue_notification() con el
    objeto Notification resultante para disparar la entrega WebSocket.
    """
    uid = UUID(str(user_id)) if not isinstance(user_id, UUID) else user_id
    tid = UUID(str(ticket_id)) if ticket_id and not isinstance(ticket_id, UUID) else ticket_id

    # Validar que el tipo existe en el enum
    try:
        ntype = NotificationType(notification_type)
    except ValueError:
        ntype = NotificationType.SYSTEM

    notification = Notification(
        user_id=uid,
        ticket_id=tid,
        title=title[:255],
        message=message[:1000],
        type=ntype,
        is_read=False,
    )
    db.add(notification)
    return notification


# ---------------------------------------------------------------------------
# Paso 2: Entrega en tiempo real (post-commit, vía ARQ)
# ---------------------------------------------------------------------------

async def enqueue_notification(notification: Notification) -> bool:
    """
    Encola la entrega WebSocket de la notificación ya persistida.

    Debe llamarse DESPUÉS del commit del caller para que el ID sea válido.
    Fallos silenciosos — la notificación ya está en DB aunque no llegue
    en tiempo real.
    """
    pool = get_arq_pool()
    if pool is None:
        logger.warning("ARQ pool no inicializado; entrega WebSocket omitida para notificación %s", notification.id)
        return False

    try:
        await pool.enqueue_job(
            "deliver_notification",
            user_id=str(notification.user_id),
            notification_id=str(notification.id),
            title=notification.title,
            message=notification.message,
            notification_type=notification.type.value,
            ticket_id=str(notification.ticket_id) if notification.ticket_id else None,
            created_at=notification.created_at.isoformat() if notification.created_at else datetime.now(timezone.utc).isoformat(),
        )
        logger.debug("Notificación %s encolada para usuario %s", notification.id, notification.user_id)
        return True
    except Exception as exc:
        logger.error("Error al encolar notificación %s: %s", notification.id, exc)
        return False


# ---------------------------------------------------------------------------
# Helpers de alto nivel — llamar desde routers / services
# ---------------------------------------------------------------------------

async def notify_ticket_assigned(
    db: AsyncSession,
    *,
    ticket_id: UUID | str,
    assignee_id: UUID | str,
    assigner_name: str,
    ticket_title: str,
) -> None:
    """Notifica al nuevo asignado cuando se le asigna un ticket."""
    notif = await create_notification(
        db,
        user_id=assignee_id,
        title="Ticket asignado",
        message=f'{assigner_name} te asignó el ticket "{ticket_title}"',
        notification_type=NotificationType.TICKET_ASSIGNED.value,
        ticket_id=ticket_id,
    )
    db.info["_pending_notifications"] = db.info.get("_pending_notifications", [])
    db.info["_pending_notifications"].append(notif)


async def notify_status_changed(
    db: AsyncSession,
    *,
    ticket_id: UUID | str,
    owner_id: UUID | str,
    actor_name: str,
    ticket_title: str,
    new_status: str,
) -> None:
    """Notifica al creador del ticket cuando el estado cambia."""
    notif = await create_notification(
        db,
        user_id=owner_id,
        title="Estado de ticket actualizado",
        message=f'{actor_name} cambió "{ticket_title}" a {new_status}',
        notification_type=NotificationType.STATUS_CHANGED.value,
        ticket_id=ticket_id,
    )
    db.info["_pending_notifications"] = db.info.get("_pending_notifications", [])
    db.info["_pending_notifications"].append(notif)


async def notify_ticket_redirected(
    db: AsyncSession,
    *,
    ticket_id: UUID | str,
    new_assignee_id: UUID | str,
    redirector_name: str,
    ticket_title: str,
    justification: str,
) -> None:
    """Notifica al nuevo asignado en una redirección."""
    notif = await create_notification(
        db,
        user_id=new_assignee_id,
        title="Ticket redirigido a ti",
        message=f'{redirector_name} te redirigió "{ticket_title}". Motivo: {justification[:200]}',
        notification_type=NotificationType.TICKET_REDIRECTED.value,
        ticket_id=ticket_id,
    )
    db.info["_pending_notifications"] = db.info.get("_pending_notifications", [])
    db.info["_pending_notifications"].append(notif)


async def notify_ticket_completed(
    db: AsyncSession,
    *,
    ticket_id: UUID | str,
    owner_id: UUID | str,
    developer_name: str,
    ticket_title: str,
) -> None:
    """Notifica al líder/creador cuando un ticket se completa."""
    notif = await create_notification(
        db,
        user_id=owner_id,
        title="Ticket completado",
        message=f'{developer_name} completó el ticket "{ticket_title}"',
        notification_type=NotificationType.TICKET_COMPLETED.value,
        ticket_id=ticket_id,
    )
    db.info["_pending_notifications"] = db.info.get("_pending_notifications", [])
    db.info["_pending_notifications"].append(notif)


async def notify_question_raised(
    db: AsyncSession,
    *,
    ticket_id: UUID | str,
    owner_id: UUID | str,
    developer_name: str,
    ticket_title: str,
) -> None:
    """Notifica al líder cuando se levanta una pregunta bloqueante."""
    notif = await create_notification(
        db,
        user_id=owner_id,
        title="Pregunta bloqueante en ticket",
        message=f'{developer_name} levantó una pregunta en "{ticket_title}"',
        notification_type=NotificationType.QUESTION_RAISED.value,
        ticket_id=ticket_id,
    )
    db.info["_pending_notifications"] = db.info.get("_pending_notifications", [])
    db.info["_pending_notifications"].append(notif)


async def flush_pending_notifications(db: AsyncSession) -> None:
    """
    Encola todas las notificaciones pendientes de la sesión actual.

    Llamar DESPUÉS de db.commit() para que los IDs de notificación
    sean válidos y la entrega pueda referenciarlos.

    Patrón de uso en un router:
        notif = await notify_ticket_assigned(db, ...)
        await db.commit()
        await flush_pending_notifications(db)
    """
    pending = db.info.pop("_pending_notifications", [])
    for notif in pending:
        await enqueue_notification(notif)


# Instancia singleton para compatibilidad con código que usa notification_service.X
notification_service = None  # La nueva API es funcional (no basada en instancias)
