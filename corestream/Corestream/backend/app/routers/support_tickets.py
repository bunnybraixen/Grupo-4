"""
Router de Tickets de Soporte.

Gestiona los bugs de producción (tickets de tipo SUPPORT).
Workflow propio: REPORTED → INVESTIGATING → RESOLVED.

Permisos:
- Crear / listar / ver / actualizar: cualquier usuario autenticado (Developer, Team Leader, Admin)
- Asignar a un developer: solo TEAM_LEADER
- Cambiar estado (investigate/resolve): cualquier usuario autenticado
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models import Ticket, TicketEvent, TicketEventType, TicketStatus, TicketType, User
from app.models.role import UserRole
from app.schemas.ticket import (
    SupportTicketAssign,
    SupportTicketCreate,
    SupportTicketUpdate,
    TicketComplete,
    TicketEventResponse,
    TicketResponse,
)
from app.services.ticket_state_machine import TicketStateMachine

router = APIRouter(tags=["Support Tickets"])


async def _get_support_ticket_or_404(ticket_id: UUID, db: AsyncSession) -> Ticket:
    """Obtiene un ticket de soporte por ID o lanza 404."""
    result = await db.execute(
        select(Ticket)
        .execution_options(populate_existing=True)
        .options(
            selectinload(Ticket.assignee).selectinload(User.role),
            selectinload(Ticket.created_by).selectinload(User.role),
            selectinload(Ticket.subtasks),
            selectinload(Ticket.linked_ticket).selectinload(Ticket.epic),
        )
        .where(Ticket.id == ticket_id, Ticket.ticket_type == TicketType.SUPPORT)
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket de soporte no encontrado",
        )
    return ticket


@router.get("/", response_model=List[TicketResponse])
async def list_support_tickets(
    status_filter: Optional[str] = Query(None, description="Filtrar por estado (REPORTED, INVESTIGATING, RESOLVED)"),
    severity_filter: Optional[str] = Query(None, description="Filtrar por severidad (CRITICAL, HIGH, MEDIUM, LOW)"),
    assignee_id: Optional[UUID] = Query(None, description="Filtrar por developer asignado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[TicketResponse]:
    """Lista todos los tickets de soporte con filtros opcionales."""
    query = (
        select(Ticket)
        .options(
            selectinload(Ticket.assignee).selectinload(User.role),
            selectinload(Ticket.created_by).selectinload(User.role),
            selectinload(Ticket.subtasks),
            selectinload(Ticket.linked_ticket).selectinload(Ticket.epic),
        )
        .where(Ticket.ticket_type == TicketType.SUPPORT)
        .order_by(Ticket.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    if status_filter:
        try:
            ts = TicketStatus(status_filter.upper())
            query = query.where(Ticket.status == ts)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido: {status_filter}",
            )

    if severity_filter:
        query = query.where(Ticket.severity == severity_filter.upper())

    if assignee_id:
        query = query.where(Ticket.assignee_id == assignee_id)

    result = await db.execute(query)
    tickets = result.scalars().all()
    return [TicketResponse.model_validate(t) for t in tickets]


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_support_ticket(
    ticket_data: SupportTicketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Crea un nuevo ticket de soporte (reportar un bug de producción)."""
    new_ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        ticket_type=TicketType.SUPPORT,
        status=TicketStatus.REPORTED,
        severity=ticket_data.severity,
        stack_trace=ticket_data.stack_trace,
        reproduction_steps=ticket_data.reproduction_steps,
        browser=ticket_data.browser,
        operating_system=ticket_data.operating_system,
        linked_ticket_id=ticket_data.linked_ticket_id,
        created_by_id=current_user.id,
        # Los tickets de soporte no requieren épica; epic_id es None
    )
    db.add(new_ticket)
    # Necesario para generar new_ticket.id antes de registrar evento de auditoría.
    await db.flush()

    await TicketStateMachine.log_ticket_event(
        db=db,
        ticket_id=new_ticket.id,
        event_type=TicketEventType.CREATED,
        user_id=current_user.id,
        detail={"message": "Ticket de soporte creado", "title": ticket_data.title},
    )

    ticket = await _get_support_ticket_or_404(new_ticket.id, db)
    return TicketResponse.model_validate(ticket)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_support_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Obtiene los detalles de un ticket de soporte."""
    ticket = await _get_support_ticket_or_404(ticket_id, db)
    return TicketResponse.model_validate(ticket)


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_support_ticket(
    ticket_id: UUID,
    ticket_update: SupportTicketUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Actualiza los campos de un ticket de soporte (excluye cambios de estado)."""
    ticket = await _get_support_ticket_or_404(ticket_id, db)

    update_data = ticket_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)

    await TicketStateMachine.log_ticket_event(
        db=db,
        ticket_id=ticket.id,
        event_type=TicketEventType.UPDATED,
        user_id=current_user.id,
        detail={"fields_updated": list(update_data.keys())},
    )

    ticket = await _get_support_ticket_or_404(ticket.id, db)
    return TicketResponse.model_validate(ticket)


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_support_ticket(
    ticket_id: UUID,
    assignment: SupportTicketAssign,
    current_user: User = Depends(require_role([UserRole.TEAM_LEADER])),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """
    Asigna un ticket de soporte a un developer.
    Solo puede hacerlo el TEAM_LEADER.
    """
    ticket = await _get_support_ticket_or_404(ticket_id, db)

    # Validar que el assignee existe
    result = await db.execute(select(User).where(User.id == assignment.assignee_id))
    assignee = result.scalar_one_or_none()
    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer asignado no encontrado",
        )

    old_assignee_id = ticket.assignee_id
    ticket.assignee_id = assignment.assignee_id

    await TicketStateMachine.log_ticket_event(
        db=db,
        ticket_id=ticket.id,
        event_type=TicketEventType.ASSIGNED,
        user_id=current_user.id,
        detail={
            "from_assignee_id": str(old_assignee_id) if old_assignee_id else None,
            "to_assignee_id": str(assignment.assignee_id),
        },
    )

    ticket = await _get_support_ticket_or_404(ticket.id, db)
    return TicketResponse.model_validate(ticket)


@router.post("/{ticket_id}/investigate", response_model=TicketResponse)
async def investigate_support_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """
    Transiciona el ticket de soporte de REPORTED a INVESTIGATING.
    Indica que alguien está investigando activamente el bug.
    """
    ticket = await _get_support_ticket_or_404(ticket_id, db)

    await TicketStateMachine.transition_to_investigating(
        ticket=ticket,
        current_user=current_user,
        db=db,
    )
    await db.commit()

    ticket = await _get_support_ticket_or_404(ticket.id, db)
    return TicketResponse.model_validate(ticket)


@router.post("/{ticket_id}/resolve", response_model=TicketResponse)
async def resolve_support_ticket(
    ticket_id: UUID,
    resolution: TicketComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """
    Transiciona el ticket de soporte de INVESTIGATING a RESOLVED.
    Requiere un enlace al PR que corrige el bug.
    """
    ticket = await _get_support_ticket_or_404(ticket_id, db)

    await TicketStateMachine.transition_to_resolved(
        ticket=ticket,
        current_user=current_user,
        pr_link=resolution.pr_link,
        db=db,
    )
    await db.commit()

    ticket = await _get_support_ticket_or_404(ticket.id, db)
    return TicketResponse.model_validate(ticket)


@router.get("/{ticket_id}/events", response_model=List[TicketEventResponse])
async def get_support_ticket_events(
    ticket_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[TicketEventResponse]:
    """Devuelve el historial de eventos de un ticket de soporte."""
    await _get_support_ticket_or_404(ticket_id, db)

    # TicketEventResponse (app.schemas.ticket) serializa user como UserResponse,
    # cuyo campo `role` es un str derivado de user.role.name — sin cargar
    # también esa relación, el lazy-load fuera de contexto async revienta con
    # 500 (MissingGreenlet) en cuanto el ticket tiene algún evento con usuario.
    result = await db.execute(
        select(TicketEvent)
        .options(selectinload(TicketEvent.user).selectinload(User.role))
        .where(TicketEvent.ticket_id == ticket_id)
        .order_by(TicketEvent.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    events = result.scalars().all()
    return [TicketEventResponse.model_validate(e) for e in events]
