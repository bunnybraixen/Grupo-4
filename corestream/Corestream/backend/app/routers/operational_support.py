"""
Router de Tickets Operacionales de Soporte.

Cualquier rol autenticado (ADMIN, GROUP_LEADER, DEVELOPER) levanta tickets con
título + problema; al crearse arranca el timer. Solo ADMIN/GROUP_LEADER pueden
resolverlos, y para eso deben enviar el bloque de texto con los cambios
realizados. Los resueltos quedan archivados (status=RESOLVED) y se pueden
revisar con sus detalles.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import OperationalTicket, OperationalTicketStatus, User
from app.models.user import UserRole
from app.schemas.operational_ticket import (
    OperationalTicketCreate,
    OperationalTicketResolve,
    OperationalTicketResponse,
    OperationalTicketUser,
)
from app.services.ticket_permissions import get_user_id, require_admin_or_leader

router = APIRouter(prefix="/operational-support", tags=["Soporte Operacional"])


def _load_options():
    return (
        selectinload(OperationalTicket.created_by),
        selectinload(OperationalTicket.resolved_by),
    )


async def _get_or_404(ticket_id: UUID, db: AsyncSession) -> OperationalTicket:
    result = await db.execute(
        select(OperationalTicket)
        .execution_options(populate_existing=True)
        .options(*_load_options())
        .where(OperationalTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket de soporte no encontrado")
    return ticket


def _to_response(ticket: OperationalTicket) -> OperationalTicketResponse:
    def _user(u) -> Optional[OperationalTicketUser]:
        if u is None:
            return None
        return OperationalTicketUser(id=u.id, full_name=u.full_name, email=u.email)

    return OperationalTicketResponse(
        id=ticket.id,
        title=ticket.title,
        problem=ticket.problem,
        status=ticket.status.value,
        timer_started_at=ticket.timer_started_at,
        resolved_at=ticket.resolved_at,
        elapsed_seconds=ticket.elapsed_seconds,
        current_elapsed_seconds=ticket.current_elapsed_seconds,
        resolution_notes=ticket.resolution_notes,
        created_by=_user(ticket.created_by),
        resolved_by=_user(ticket.resolved_by),
        created_at=ticket.created_at,
    )


@router.get("/", response_model=List[OperationalTicketResponse])
async def list_operational_tickets(
    status_filter: Optional[str] = Query(None, description="OPEN o RESOLVED"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OperationalTicketResponse]:
    """Lista los tickets operacionales. status=RESOLVED devuelve los archivados."""
    query = (
        select(OperationalTicket)
        .options(*_load_options())
        .order_by(OperationalTicket.created_at.desc())
        .limit(500)
    )
    if status_filter:
        try:
            query = query.where(
                OperationalTicket.status == OperationalTicketStatus(status_filter.upper())
            )
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Estado inválido: {status_filter}")

    result = await db.execute(query)
    return [_to_response(t) for t in result.scalars().all()]


@router.post(
    "/",
    response_model=OperationalTicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_operational_ticket(
    data: OperationalTicketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperationalTicketResponse:
    """Crea un ticket operacional. El timer arranca en el momento de la creación."""
    ticket = OperationalTicket(
        title=data.title.strip(),
        problem=data.problem.strip(),
        status=OperationalTicketStatus.OPEN,
        timer_started_at=datetime.now(timezone.utc),
        created_by_id=UUID(str(get_user_id(current_user))),
    )
    db.add(ticket)
    await db.commit()
    return _to_response(await _get_or_404(ticket.id, db))


@router.get("/{ticket_id}", response_model=OperationalTicketResponse)
async def get_operational_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperationalTicketResponse:
    """Detalle de un ticket operacional (incluye los cambios si está resuelto)."""
    return _to_response(await _get_or_404(ticket_id, db))


@router.post("/{ticket_id}/resolve", response_model=OperationalTicketResponse)
async def resolve_operational_ticket(
    ticket_id: UUID,
    data: OperationalTicketResolve,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperationalTicketResponse:
    """
    Marca el ticket como resuelto y lo archiva. Requiere rol ADMIN o
    GROUP_LEADER y el bloque de texto con los cambios realizados.
    """
    require_admin_or_leader(current_user)

    ticket = await _get_or_404(ticket_id, db)
    if ticket.status == OperationalTicketStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="El ticket ya está resuelto")

    ticket.resolve(
        notes=data.resolution_notes.strip(),
        user_id=UUID(str(get_user_id(current_user))),
    )
    await db.commit()
    return _to_response(await _get_or_404(ticket.id, db))
