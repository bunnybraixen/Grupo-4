"""
Router de Sprints - Planificación y seguimiento de períodos de trabajo.

Un Sprint es INDEPENDIENTE de la Épica: la Épica representa el área funcional
del proyecto y el Sprint un período de trabajo. Un Ticket puede pertenecer a la
vez a una Épica (`epic_id`) y a un Sprint (`sprint_id`); asociar tickets a un
Sprint NO modifica la relación Épica -> Ticket.

Endpoints:
- CRUD de Sprints (crear/editar/eliminar: ADMIN y GROUP_LEADER)
- Asociar/quitar Tickets existentes a un Sprint
- Resumen de tickets pendientes, completados y bloqueados + progreso
- Tablero por estado (reutiliza el Kanban del Builder/Workbench)
- Cierre de Sprint con cálculo automático de Velocity
- Métricas agregadas de SLA del Sprint (el SLA se calcula por ticket)
"""

from datetime import datetime, timezone
from math import ceil
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import (
    Application,
    Epic,
    Sprint,
    SprintStatus,
    Ticket,
    TicketStatus,
)
from app.schemas import (
    SprintCreate,
    SprintUpdate,
    SprintTicketAssignment,
    SprintTicketStoryPoints,
    SprintResponse,
    SprintSummaryResponse,
    SprintVelocityResponse,
    TicketResponse,
)
from app.services import sla_service
from app.services.ticket_permissions import (
    get_user_id,
    require_admin_or_leader,
)

router = APIRouter(prefix="/sprints", tags=["Sprints"])

# Estados terminales del ticket (el modelo usa DONE; COMPLETED se tolera por
# compatibilidad con datos históricos).
DONE_STATUSES = {"DONE", "COMPLETED"}

# Etiquetas usadas por el tablero del Sprint (mismas que el Kanban existente)
STATUS_LABELS = {
    TicketStatus.TODO.value: "Por Hacer",
    TicketStatus.IN_PROGRESS.value: "En Curso",
    TicketStatus.BLOCKED.value: "Bloqueado",
    TicketStatus.REDIRECTED.value: "Redirigido",
    TicketStatus.DONE.value: "Completado",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _as_aware(value: Optional[datetime]) -> Optional[datetime]:
    """Normaliza un datetime a UTC-aware (la BD mezcla naive y aware)."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _status_value(value) -> str:
    """Valor string de un enum/estado (DONE, IN_PROGRESS, ...)."""
    return str(getattr(value, "value", value) or "").upper()


def _ticket_query():
    """
    Consulta base de tickets de un Sprint con TODAS las relaciones que
    serializa `TicketResponse` (así se reutiliza en el tablero del Kanban).
    """
    return select(Ticket).options(
        selectinload(Ticket.assignee),
        selectinload(Ticket.subtasks),
        selectinload(Ticket.tags),
        selectinload(Ticket.epic),
        selectinload(Ticket.sprint),
    )


def _sprint_query():
    """Consulta base de Sprints con su proyecto (aplicación) precargado."""
    return select(Sprint).options(selectinload(Sprint.application))


async def _get_sprint_or_404(db: AsyncSession, sprint_id: UUID) -> Sprint:
    """Recupera un Sprint o lanza 404."""
    result = await db.execute(_sprint_query().where(Sprint.id == sprint_id))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sprint con ID {sprint_id} no encontrado",
        )
    return sprint


async def _load_sprint_tickets(db: AsyncSession, sprint_id: UUID) -> List[Ticket]:
    """Tickets asociados al Sprint, ordenados por índice y fecha de creación."""
    result = await db.execute(
        _ticket_query()
        .where(Ticket.sprint_id == sprint_id)
        .order_by(Ticket.order_index.asc(), Ticket.created_at.asc())
    )
    return list(result.scalars().all())


def _compute_metrics(sprint: Sprint, tickets: List[Ticket]) -> dict:
    """
    Calcula el avance, el resumen de estados y la Velocity del Sprint.

    Velocity: puntos/esfuerzo de los tickets completados. Si ningún ticket
    completado tiene puntos de historia asignados, se usa 1 punto por ticket
    completado (así la métrica nunca queda en 0 por falta de estimación).
    """
    total = len(tickets)
    completed = [ticket for ticket in tickets if _status_value(ticket.status) in DONE_STATUSES]
    blocked = [ticket for ticket in tickets if _status_value(ticket.status) == "BLOCKED"]
    in_progress = [ticket for ticket in tickets if _status_value(ticket.status) == "IN_PROGRESS"]
    redirected = [ticket for ticket in tickets if _status_value(ticket.status) == "REDIRECTED"]

    story_points_total = sum(int(getattr(ticket, "story_points", 0) or 0) for ticket in tickets)
    story_points_completed = sum(
        int(getattr(ticket, "story_points", 0) or 0) for ticket in completed
    )
    velocity = float(story_points_completed) if story_points_completed else float(len(completed))

    now = datetime.now(timezone.utc)
    start_date = _as_aware(sprint.start_date) or now
    end_date = _as_aware(sprint.end_date) or now
    duration_days = max(0, (end_date.date() - start_date.date()).days)
    days_remaining = ceil((end_date - now).total_seconds() / 86400)
    sprint_status = _status_value(sprint.status)
    is_overdue = bool(days_remaining < 0 and sprint_status != SprintStatus.COMPLETED.value)

    return {
        "total_tickets": total,
        "pending_tickets": total - len(completed),
        "in_progress_tickets": len(in_progress),
        "completed_tickets": len(completed),
        "blocked_tickets": len(blocked),
        "redirected_tickets": len(redirected),
        "progress": round((len(completed) / total) * 100, 2) if total else 0.0,
        "story_points_total": story_points_total,
        "story_points_completed": story_points_completed,
        "computed_velocity": velocity,
        "duration_days": duration_days,
        "days_remaining": days_remaining,
        "is_overdue": is_overdue,
    }


def _to_sprint_response(
    sprint: Sprint,
    tickets: List[Ticket],
    sla_map: dict,
    include_tickets: bool = False,
    include_board: bool = False,
) -> SprintResponse:
    """Construye la respuesta de un Sprint con métricas, SLA y (opcional) tablero."""
    metrics = _compute_metrics(sprint, tickets)
    sprint_status = _status_value(sprint.status)

    # Velocity publicada: la persistida al cerrar el Sprint, o la proyectada
    # con el trabajo ya completado mientras sigue abierto.
    velocity = (
        float(sprint.velocity or 0)
        if sprint_status == SprintStatus.COMPLETED.value
        else metrics["computed_velocity"]
    )

    sla_summary = sla_service.summarize_sla(
        [sla_map[ticket.id] for ticket in tickets if ticket.id in sla_map]
    )

    board = []
    if include_board:
        for status_value in (
            TicketStatus.TODO.value,
            TicketStatus.IN_PROGRESS.value,
            TicketStatus.BLOCKED.value,
            TicketStatus.REDIRECTED.value,
            TicketStatus.DONE.value,
        ):
            board.append(
                {
                    "status": status_value,
                    "label": STATUS_LABELS.get(status_value, status_value),
                    "tickets": [
                        TicketResponse.from_orm(ticket)
                        for ticket in tickets
                        if _status_value(ticket.status) == status_value
                    ],
                }
            )

    application = sprint.__dict__.get("application")

    return SprintResponse(
        id=sprint.id,
        name=sprint.name,
        goal=sprint.goal,
        application_id=sprint.application_id,
        application_name=getattr(application, "name", None),
        start_date=sprint.start_date,
        end_date=sprint.end_date,
        status=sprint_status,
        velocity=velocity,
        created_at=sprint.created_at,
        sla=sla_summary,
        tickets=[TicketResponse.from_orm(ticket) for ticket in tickets] if include_tickets else [],
        board=board,
        **{key: value for key, value in metrics.items() if key != "computed_velocity"},
    )


# ---------------------------------------------------------------------------
# CRUD de Sprints
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=List[SprintResponse],
    summary="Listar Sprints",
    description="Lista los Sprints de un proyecto con su avance, Velocity y SLA agregado",
)
async def list_sprints(
    application_id: Optional[UUID] = Query(None, description="Filtrar por proyecto (aplicación)"),
    sprint_status: Optional[SprintStatus] = Query(
        None, alias="status", description="Filtrar por estado (PLANNED, ACTIVE, COMPLETED)"
    ),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[SprintResponse]:
    """
    Lista Sprints con métricas agregadas.

    El resumen incluye tickets pendientes/completados/bloqueados, progreso,
    Velocity (proyectada si el Sprint sigue abierto) y métricas de SLA.
    """
    query = _sprint_query()

    if application_id is not None:
        query = query.where(Sprint.application_id == application_id)
    if sprint_status is not None:
        query = query.where(Sprint.status == sprint_status)

    result = await db.execute(query.order_by(Sprint.start_date.desc()))
    sprints = list(result.scalars().all())

    # Tickets de TODOS los sprints en una sola consulta (evita N+1)
    tickets_by_sprint: dict = {}
    sprint_ids = [sprint.id for sprint in sprints]
    if sprint_ids:
        tickets_result = await db.execute(_ticket_query().where(Ticket.sprint_id.in_(sprint_ids)))
        for ticket in tickets_result.scalars().all():
            tickets_by_sprint.setdefault(ticket.sprint_id, []).append(ticket)

    configs = await sla_service.load_sla_configs(db)
    now = datetime.now(timezone.utc)

    return [
        _to_sprint_response(
            sprint,
            tickets_by_sprint.get(sprint.id, []),
            sla_service.build_sla_map(tickets_by_sprint.get(sprint.id, []), configs, now),
        )
        for sprint in sprints
    ]


@router.post(
    "/",
    response_model=SprintResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Sprint",
    description="Crea un Sprint (ADMIN o GROUP_LEADER) dentro de un proyecto",
)
async def create_sprint(
    sprint_data: SprintCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SprintResponse:
    """Crea un Sprint asociado a un proyecto. Solo ADMIN y GROUP_LEADER."""
    require_admin_or_leader(current_user)

    application = await db.execute(
        select(Application).where(Application.id == sprint_data.application_id)
    )
    if not application.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proyecto con ID {sprint_data.application_id} no encontrado",
        )

    try:
        sprint = Sprint(
            name=sprint_data.name,
            goal=sprint_data.goal,
            application_id=sprint_data.application_id,
            start_date=sprint_data.start_date,
            end_date=sprint_data.end_date,
            status=sprint_data.status,
            created_by_id=UUID(get_user_id(current_user)),
        )
        db.add(sprint)
        await db.commit()
        await db.refresh(sprint)
    except Exception as exc:  # pragma: no cover - error de BD
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el Sprint: {exc}",
        )

    return _to_sprint_response(
        await _get_sprint_or_404(db, sprint.id),
        [],
        {},
        include_tickets=True,
        include_board=True,
    )


@router.get(
    "/{sprint_id}",
    response_model=SprintResponse,
    summary="Detalle de un Sprint",
    description="Devuelve el Sprint con sus tickets, tablero por estado, avance y SLA",
)
async def get_sprint(
    sprint_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SprintResponse:
    """Detalle completo del Sprint: tickets asociados + tablero + métricas."""
    sprint = await _get_sprint_or_404(db, sprint_id)
    tickets = await _load_sprint_tickets(db, sprint_id)
    configs = await sla_service.load_sla_configs(db)

    return _to_sprint_response(
        sprint,
        tickets,
        sla_service.build_sla_map(tickets, configs),
        include_tickets=True,
        include_board=True,
    )


@router.put(
    "/{sprint_id}",
    response_model=SprintResponse,
    summary="Editar Sprint",
    description="Actualiza nombre, objetivo, fechas o estado de un Sprint",
)
async def update_sprint(
    sprint_id: UUID,
    sprint_data: SprintUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SprintResponse:
    """Edición parcial del Sprint (ADMIN o GROUP_LEADER)."""
    require_admin_or_leader(current_user)

    sprint = await _get_sprint_or_404(db, sprint_id)
    update_data = sprint_data.model_dump(exclude_unset=True)

    start_date = update_data.get("start_date", sprint.start_date)
    end_date = update_data.get("end_date", sprint.end_date)
    if start_date and end_date and _as_aware(end_date) < _as_aware(start_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de término no puede ser anterior a la de inicio",
        )

    try:
        for field, value in update_data.items():
            setattr(sprint, field, value)
        await db.commit()
    except Exception as exc:  # pragma: no cover - error de BD
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el Sprint: {exc}",
        )

    sprint = await _get_sprint_or_404(db, sprint_id)
    tickets = await _load_sprint_tickets(db, sprint_id)
    configs = await sla_service.load_sla_configs(db)

    return _to_sprint_response(
        sprint,
        tickets,
        sla_service.build_sla_map(tickets, configs),
        include_tickets=True,
        include_board=True,
    )


@router.delete(
    "/{sprint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Sprint",
    description="Elimina un Sprint; sus tickets vuelven a quedar sin Sprint (no se borran)",
)
async def delete_sprint(
    sprint_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Elimina el Sprint. Los tickets NO se eliminan: solo pierden el sprint_id."""
    require_admin_or_leader(current_user)

    sprint = await _get_sprint_or_404(db, sprint_id)

    try:
        # Desasociar explícitamente los tickets para no depender del ON DELETE
        # SET NULL (y para no borrar trabajo al eliminar la planificación).
        tickets = await _load_sprint_tickets(db, sprint_id)
        for ticket in tickets:
            ticket.sprint_id = None

        await db.delete(sprint)
        await db.commit()
    except Exception as exc:  # pragma: no cover - error de BD
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar el Sprint: {exc}",
        )

    return None


# ---------------------------------------------------------------------------
# Asociación de tickets existentes + esfuerzo
# ---------------------------------------------------------------------------

async def _sprint_detail_response(db: AsyncSession, sprint_id: UUID) -> SprintResponse:
    """Reutiliza el detalle del Sprint (tickets + tablero + SLA) tras un cambio."""
    sprint = await _get_sprint_or_404(db, sprint_id)
    tickets = await _load_sprint_tickets(db, sprint_id)
    configs = await sla_service.load_sla_configs(db)

    return _to_sprint_response(
        sprint,
        tickets,
        sla_service.build_sla_map(tickets, configs),
        include_tickets=True,
        include_board=True,
    )


@router.post(
    "/{sprint_id}/tickets",
    response_model=SprintResponse,
    summary="Asociar tickets existentes al Sprint",
    description="Asocia uno o más tickets existentes a un Sprint (sprint_id)",
)
async def assign_tickets_to_sprint(
    sprint_id: UUID,
    assignment: SprintTicketAssignment,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SprintResponse:
    """
    Asocia tickets EXISTENTES al Sprint sin tocar su Épica.

    Se valida que los tickets pertenezcan al mismo proyecto que el Sprint,
    para mantener la coherencia de la planificación (el Sprint es un período
    de trabajo de UN proyecto).
    """
    require_admin_or_leader(current_user)

    sprint = await _get_sprint_or_404(db, sprint_id)
    result = await db.execute(
        select(Ticket)
        .options(selectinload(Ticket.epic))
        .where(Ticket.id.in_(assignment.ticket_ids))
    )
    tickets = list(result.scalars().all())

    found_ids = {ticket.id for ticket in tickets}
    missing = [str(ticket_id) for ticket_id in assignment.ticket_ids if ticket_id not in found_ids]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tickets no encontrados: {', '.join(missing)}",
        )

    mismatched = [
        ticket.title
        for ticket in tickets
        if getattr(ticket.__dict__.get("epic"), "application_id", sprint.application_id)
        != sprint.application_id
    ]
    if mismatched:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Los siguientes tickets pertenecen a otro proyecto y no pueden "
                f"asociarse a este Sprint: {', '.join(mismatched)}"
            ),
        )

    try:
        for ticket in tickets:
            ticket.sprint_id = sprint.id
        await db.commit()
    except Exception as exc:  # pragma: no cover - error de BD
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al asociar tickets al Sprint: {exc}",
        )

    return await _sprint_detail_response(db, sprint_id)


@router.delete(
    "/{sprint_id}/tickets/{ticket_id}",
    response_model=SprintResponse,
    summary="Quitar un ticket del Sprint",
    description="Desasocia el ticket del Sprint; el ticket y su Épica no se modifican",
)
async def remove_ticket_from_sprint(
    sprint_id: UUID,
    ticket_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SprintResponse:
    """Quita el ticket del Sprint (sprint_id = NULL). La Épica sigue intacta."""
    require_admin_or_leader(current_user)

    sprint = await _get_sprint_or_404(db, sprint_id)

    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado",
        )
    if ticket.sprint_id != sprint.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ticket no pertenece a este Sprint",
        )

    try:
        ticket.sprint_id = None
        await db.commit()
    except Exception as exc:  # pragma: no cover - error de BD
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al quitar el ticket del Sprint: {exc}",
        )

    return await _sprint_detail_response(db, sprint_id)


@router.patch(
    "/{sprint_id}/tickets/{ticket_id}",
    response_model=SprintResponse,
    summary="Definir los puntos de esfuerzo de un ticket",
    description="Actualiza los story points del ticket que alimentan la Velocity del Sprint",
)
async def update_ticket_story_points(
    sprint_id: UUID,
    ticket_id: UUID,
    payload: SprintTicketStoryPoints,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SprintResponse:
    """Define los puntos/esfuerzo del ticket planificado en el Sprint."""
    require_admin_or_leader(current_user)

    sprint = await _get_sprint_or_404(db, sprint_id)

    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado",
        )
    if ticket.sprint_id != sprint.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ticket no pertenece a este Sprint",
        )

    try:
        ticket.story_points = payload.story_points
        await db.commit()
    except Exception as exc:  # pragma: no cover - error de BD
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar los puntos del ticket: {exc}",
        )

    return await _sprint_detail_response(db, sprint_id)


# ---------------------------------------------------------------------------
# Resumen y cierre (Velocity)
# ---------------------------------------------------------------------------

@router.get(
    "/{sprint_id}/summary",
    response_model=SprintSummaryResponse,
    summary="Resumen del Sprint",
    description="Tickets pendientes/completados/bloqueados, progreso, Velocity y SLA",
)
async def get_sprint_summary(
    sprint_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SprintSummaryResponse:
    """Métricas agregadas del Sprint (avance, Velocity y SLA)."""
    sprint = await _get_sprint_or_404(db, sprint_id)
    tickets = await _load_sprint_tickets(db, sprint_id)
    configs = await sla_service.load_sla_configs(db)
    metrics = _compute_metrics(sprint, tickets)
    sprint_status = _status_value(sprint.status)

    velocity = (
        float(sprint.velocity or 0)
        if sprint_status == SprintStatus.COMPLETED.value
        else metrics["computed_velocity"]
    )

    by_status: dict[str, int] = {}
    for ticket in tickets:
        key = _status_value(ticket.status)
        by_status[key] = by_status.get(key, 0) + 1

    return SprintSummaryResponse(
        sprint_id=sprint.id,
        sprint_name=sprint.name,
        status=sprint_status,
        start_date=sprint.start_date,
        end_date=sprint.end_date,
        velocity=velocity,
        by_status=by_status,
        sla=sla_service.summarize_sla(sla_service.build_sla_map(tickets, configs)),
        **{key: value for key, value in metrics.items() if key != "computed_velocity"},
    )


@router.post(
    "/{sprint_id}/complete",
    response_model=SprintVelocityResponse,
    summary="Cerrar Sprint y calcular Velocity",
    description="Marca el Sprint como COMPLETED y guarda la Velocity calculada",
)
async def complete_sprint(
    sprint_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SprintVelocityResponse:
    """
    Cierra el Sprint: calcula automáticamente la Velocity con los puntos de los
    tickets completados y la persiste en `sprints.velocity`.
    """
    require_admin_or_leader(current_user)

    sprint = await _get_sprint_or_404(db, sprint_id)
    tickets = await _load_sprint_tickets(db, sprint_id)
    metrics = _compute_metrics(sprint, tickets)

    try:
        sprint.status = SprintStatus.COMPLETED
        sprint.velocity = metrics["computed_velocity"]
        await db.commit()
    except Exception as exc:  # pragma: no cover - error de BD
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al cerrar el Sprint: {exc}",
        )

    return SprintVelocityResponse(
        sprint_id=sprint.id,
        sprint_name=sprint.name,
        status=SprintStatus.COMPLETED.value,
        velocity=metrics["computed_velocity"],
        story_points_completed=metrics["story_points_completed"],
        completed_tickets=metrics["completed_tickets"],
        message=(
            f"Sprint cerrado. Velocity = {metrics['computed_velocity']} "
            f"({metrics['completed_tickets']} tickets completados)"
        ),
    )
