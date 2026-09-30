"""
Router de SLA (Service Level Agreement) a nivel de TICKET.

El SLA se define por TICKET (no por Sprint): según la prioridad/severidad y la
configuración de tiempos objetivo del ADMIN, se calcula el tiempo transcurrido
y restante, se detectan incumplimientos y se generan alertas para tickets
próximos a vencer o ya vencidos.

Endpoints:
- GET  /sla/configs            -> objetivos por prioridad (los edita el ADMIN)
- PUT  /sla/configs/{priority} -> ajuste de objetivos (solo ADMIN)
- GET  /sla/statuses           -> estado de SLA de los tickets (con filtros)
- GET  /sla/alerts             -> tickets próximos a vencer o incumplidos
- GET  /sla/tickets/{id}       -> estado de SLA de un ticket
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
from app.models import Epic, SLAConfig, Ticket, TicketPriority
from app.schemas import (
    SLAConfigListResponse,
    SLAConfigResponse,
    SLAConfigUpdate,
    SLAStatusListResponse,
    TicketSLAStatus,
)
from app.services import sla_service
from app.services.ticket_permissions import get_role_name, get_user_id

router = APIRouter(prefix="/sla", tags=["SLA"])

# Estados de SLA que requieren atención
ALERT_STATES = {sla_service.STATE_AT_RISK, sla_service.STATE_BREACHED}


def _require_admin(current_user) -> None:
    """El SLA se configura solo desde ADMIN (regla de negocio del módulo)."""
    if get_role_name(current_user) != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un ADMIN puede configurar el SLA",
        )


def _sla_ticket_query():
    """Consulta base de tickets con las relaciones que enriquece el SLA."""
    return select(Ticket).options(
        selectinload(Ticket.assignee),
        selectinload(Ticket.epic),
        selectinload(Ticket.sprint),
    )


async def _collect_statuses(
    db: AsyncSession,
    application_id: Optional[UUID] = None,
    sprint_id: Optional[UUID] = None,
    epic_id: Optional[UUID] = None,
    only_alerts: bool = False,
    include_resolved: bool = True,
    limit: int = 500,
) -> tuple[List[TicketSLAStatus], dict]:
    """
    Calcula el estado de SLA de los tickets que cumplen los filtros.

    Returns:
        (lista de estados ordenada por urgencia, resumen agregado)
    """
    query = _sla_ticket_query()

    if application_id is not None:
        query = query.join(Epic, Ticket.epic_id == Epic.id).where(
            Epic.application_id == application_id
        )
    if epic_id is not None:
        query = query.where(Ticket.epic_id == epic_id)
    if sprint_id is not None:
        query = query.where(Ticket.sprint_id == sprint_id)

    result = await db.execute(query.order_by(Ticket.created_at.desc()).limit(limit))
    tickets = list(result.scalars().all())

    configs = await sla_service.load_sla_configs(db)
    now = datetime.now(timezone.utc)

    statuses = [
        TicketSLAStatus(**sla_service.compute_ticket_sla(ticket, configs, now))
        for ticket in tickets
    ]

    if not include_resolved:
        statuses = [item for item in statuses if not item.is_resolved]
    if only_alerts:
        statuses = [item for item in statuses if item.state in ALERT_STATES]

    # Orden por urgencia: primero lo ya incumplido, luego lo que vence antes.
    def sort_key(item: TicketSLAStatus):
        breached_first = 0 if item.state == sla_service.STATE_BREACHED else 1
        minutes = item.minutes_to_next_deadline
        return (breached_first, minutes if minutes is not None else 10**9)

    statuses.sort(key=sort_key)

    return statuses, sla_service.summarize_sla([item.model_dump() for item in statuses])


@router.get(
    "/configs",
    response_model=SLAConfigListResponse,
    summary="Obtener configuración de SLA",
    description="Objetivos de respuesta y resolución por prioridad de ticket",
)
async def get_sla_configs(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SLAConfigListResponse:
    """
    Devuelve las reglas de SLA por prioridad.

    Si todavía no existe configuración, se crean las filas con los valores por
    defecto para que el ADMIN tenga qué ajustar en el panel.
    """
    await sla_service.ensure_default_configs(db)

    result = await db.execute(select(SLAConfig))
    configs = {
        str(getattr(config.priority, "value", config.priority)).upper(): config
        for config in result.scalars().all()
    }

    responses: list[SLAConfigResponse] = []
    for priority in TicketPriority:
        config = configs.get(priority.value)
        if config is not None:
            responses.append(
                SLAConfigResponse(
                    id=config.id,
                    priority=priority.value,
                    response_minutes=int(config.response_minutes),
                    resolution_minutes=int(config.resolution_minutes),
                    warn_threshold_percent=int(config.warn_threshold_percent or 80),
                    is_active=bool(config.is_active),
                    is_default=False,
                    updated_at=config.updated_at.isoformat() if config.updated_at else None,
                )
            )
            continue

        default_response, default_resolution = sla_service.DEFAULT_TARGETS[priority.value]
        responses.append(
            SLAConfigResponse(
                priority=priority.value,
                response_minutes=default_response,
                resolution_minutes=default_resolution,
                warn_threshold_percent=sla_service.DEFAULT_WARN_THRESHOLD_PERCENT,
                is_active=True,
                is_default=True,
            )
        )

    return SLAConfigListResponse(configs=responses)


@router.put(
    "/configs/{priority}",
    response_model=SLAConfigResponse,
    summary="Configurar SLA por prioridad",
    description="Ajusta los tiempos objetivo de respuesta y resolución (solo ADMIN)",
)
async def update_sla_config(
    priority: str,
    payload: SLAConfigUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SLAConfigResponse:
    """Crea o actualiza la regla de SLA de una prioridad. Solo ADMIN."""
    _require_admin(current_user)

    normalized = str(priority).upper()
    valid_priorities = {item.value for item in TicketPriority}
    if normalized not in valid_priorities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prioridad inválida. Valores permitidos: {', '.join(sorted(valid_priorities))}",
        )

    result = await db.execute(
        select(SLAConfig).where(SLAConfig.priority == TicketPriority(normalized))
    )
    config = result.scalar_one_or_none()

    default_response, default_resolution = sla_service.DEFAULT_TARGETS[normalized]

    if config is None:
        config = SLAConfig(
            priority=TicketPriority(normalized),
            response_minutes=default_response,
            resolution_minutes=default_resolution,
            warn_threshold_percent=sla_service.DEFAULT_WARN_THRESHOLD_PERCENT,
            is_active=True,
        )
        db.add(config)

    try:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(config, field, value)

        if int(config.resolution_minutes) < int(config.response_minutes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tiempo objetivo de resolución no puede ser menor que el de respuesta",
            )

        config.updated_by_id = UUID(get_user_id(current_user))
        await db.commit()
        await db.refresh(config)
    except HTTPException:
        await db.rollback()
        raise
    except Exception as exc:  # pragma: no cover - error de BD
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar la configuración de SLA: {exc}",
        )

    return SLAConfigResponse(
        id=config.id,
        priority=normalized,
        response_minutes=int(config.response_minutes),
        resolution_minutes=int(config.resolution_minutes),
        warn_threshold_percent=int(config.warn_threshold_percent or 80),
        is_active=bool(config.is_active),
        is_default=False,
        updated_at=config.updated_at.isoformat() if config.updated_at else None,
    )


@router.get(
    "/statuses",
    response_model=SLAStatusListResponse,
    summary="Estado de SLA de tickets",
    description="Calcula tiempo transcurrido/restante y estado del SLA por ticket",
)
async def get_sla_statuses(
    application_id: Optional[UUID] = Query(None, description="Filtrar por proyecto"),
    sprint_id: Optional[UUID] = Query(None, description="Filtrar por Sprint"),
    epic_id: Optional[UUID] = Query(None, description="Filtrar por épica"),
    only_alerts: bool = Query(False, description="Solo tickets con alerta o incumplidos"),
    include_resolved: bool = Query(True, description="Incluir tickets completados"),
    limit: int = Query(500, ge=1, le=2000),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SLAStatusListResponse:
    """
    Estado de SLA de los tickets, con el resumen agregado.

    Es la fuente que consumen el Builder, el Workbench y el Command Center para
    mostrar, en cada tarjeta de ticket, el estado de su SLA.
    """
    statuses, summary = await _collect_statuses(
        db,
        application_id=application_id,
        sprint_id=sprint_id,
        epic_id=epic_id,
        only_alerts=only_alerts,
        include_resolved=include_resolved,
        limit=limit,
    )
    return SLAStatusListResponse(summary=summary, statuses=statuses)


@router.get(
    "/alerts",
    response_model=List[TicketSLAStatus],
    summary="Alertas de SLA",
    description="Tickets próximos a vencer (AT_RISK) o con SLA incumplido (BREACHED)",
)
async def get_sla_alerts(
    application_id: Optional[UUID] = Query(None, description="Filtrar por proyecto"),
    sprint_id: Optional[UUID] = Query(None, description="Filtrar por Sprint"),
    limit: int = Query(200, ge=1, le=1000),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[TicketSLAStatus]:
    """Alertas ordenadas por urgencia (primero los incumplidos)."""
    statuses, _ = await _collect_statuses(
        db,
        application_id=application_id,
        sprint_id=sprint_id,
        only_alerts=True,
        include_resolved=False,
        limit=limit,
    )
    return statuses


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketSLAStatus,
    summary="Estado de SLA de un ticket",
    description="Tiempo transcurrido/restante y estado del SLA para un ticket",
)
async def get_ticket_sla(
    ticket_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TicketSLAStatus:
    """Estado de SLA de un ticket individual."""
    result = await db.execute(_sla_ticket_query().where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado",
        )

    configs = await sla_service.load_sla_configs(db)
    return TicketSLAStatus(**sla_service.compute_ticket_sla(ticket, configs))
