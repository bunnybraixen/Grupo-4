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
    OperationalTicketAssign,
    OperationalTicketCreate,
    OperationalTicketResolve,
    OperationalTicketResponse,
    OperationalTicketUser,
)
from app.services.ticket_permissions import (
    assert_can_assign_operational_ticket,
    assert_can_resolve_operational_ticket,
    assert_can_view_operational_ticket,
    can_see_all_operational_tickets,
    get_user_id,
)

router = APIRouter(prefix="/operational-support", tags=["Soporte Operacional"])


def _load_options():
    return (
        selectinload(OperationalTicket.created_by),
        selectinload(OperationalTicket.resolved_by),
        selectinload(OperationalTicket.assignee),
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
        assignee=_user(ticket.assignee),
        created_at=ticket.created_at,
    )


@router.get("/", response_model=List[OperationalTicketResponse])
async def list_operational_tickets(
    status_filter: Optional[str] = Query(None, description="OPEN o RESOLVED"),
    mine: bool = Query(False, description="True devuelve solo los tickets asignados a ti"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OperationalTicketResponse]:
    """
    Lista los tickets operacionales. status=RESOLVED devuelve los archivados.

    Visibilidad:
    - ADMIN/GROUP_LEADER ven TODOS los tickets.
    - DEVELOPER ve únicamente los tickets que tiene ASIGNADOS
      (o los que él mismo creó si no están asignados a nadie).
    Con `mine=true` se limita a los asignados al usuario actual.
    """
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

    user_id = UUID(str(get_user_id(current_user)))
    if not can_see_all_operational_tickets(current_user):
        # El DEVELOPER solo accede a lo que tiene asignado (o creó sin asignar).
        query = query.where(
            (OperationalTicket.assignee_id == user_id)
            | (
                (OperationalTicket.assignee_id.is_(None))
                & (OperationalTicket.created_by_id == user_id)
            )
        )
    elif mine:
        query = query.where(OperationalTicket.assignee_id == user_id)

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


@router.get("/assignable-users", response_model=List[OperationalTicketUser])
async def list_assignable_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OperationalTicketUser]:
    """
    Usuarios a los que se puede redirigir un ticket operacional.
    Solo ADMIN/GROUP_LEADER: el DEVELOPER no puede asignar, así que no ve la lista.
    """
    assert_can_assign_operational_ticket(current_user)

    result = await db.execute(
        select(User)
        .where(User.is_active.is_(True))
        .order_by(User.full_name.asc())
    )
    users = result.scalars().all()
    return [
        OperationalTicketUser(id=u.id, full_name=u.full_name, email=u.email)
        for u in users
    ]


@router.get("/{ticket_id}", response_model=OperationalTicketResponse)
async def get_operational_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperationalTicketResponse:
    """Detalle de un ticket operacional (incluye los cambios si está resuelto)."""
    ticket = await _get_or_404(ticket_id, db)
    assert_can_view_operational_ticket(ticket, current_user)
    return _to_response(ticket)


@router.post("/{ticket_id}/resolve", response_model=OperationalTicketResponse)
async def resolve_operational_ticket(
    ticket_id: UUID,
    data: OperationalTicketResolve,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperationalTicketResponse:
    """
    Marca el ticket como resuelto y lo archiva. Requiere el bloque de texto con
    los cambios realizados.

    ADMIN/GROUP_LEADER resuelven cualquier ticket; un DEVELOPER solo puede
    resolver los tickets que tiene asignados.
    """
    ticket = await _get_or_404(ticket_id, db)
    assert_can_resolve_operational_ticket(ticket, current_user)

    if ticket.status == OperationalTicketStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="El ticket ya está resuelto")

    ticket.resolve(
        notes=data.resolution_notes.strip(),
        user_id=UUID(str(get_user_id(current_user))),
    )
    await db.commit()
    return _to_response(await _get_or_404(ticket.id, db))


@router.post("/{ticket_id}/assign", response_model=OperationalTicketResponse)
async def assign_operational_ticket(
    ticket_id: UUID,
    data: OperationalTicketAssign,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperationalTicketResponse:
    """
    Redirige (asigna) el ticket operacional a otro usuario.

    Solo ADMIN y GROUP_LEADER pueden redirigir. Un DEVELOPER recibe 403.
    Enviar `assignee_id=null` deja el ticket sin asignar.
    """
    assert_can_assign_operational_ticket(current_user)

    ticket = await _get_or_404(ticket_id, db)
    if ticket.status == OperationalTicketStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="El ticket ya está resuelto")

    if data.assignee_id is None:
        ticket.assignee_id = None
    else:
        result = await db.execute(
            select(User).where(User.id == data.assignee_id)
        )
        assignee = result.scalar_one_or_none()
        if assignee is None:
            raise HTTPException(status_code=404, detail="Usuario destino no encontrado")
        ticket.assignee_id = assignee.id

    await db.commit()
    return _to_response(await _get_or_404(ticket.id, db))

