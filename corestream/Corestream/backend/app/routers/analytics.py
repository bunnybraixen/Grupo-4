"""
Router de Analíticas e Informes.

Proporciona endpoints para análisis y visualización de datos:
- Resumen de métricas de aplicaciones
- Desempeño individual de usuarios
- Mapas de calor de actividad
- Gráficos burndown de épicas
- Exportación de datos en CSV
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models import Application, Epic
from app.services import analytics_service
from app.middleware.auth import require_role
from app.models import UserRole

logger = logging.getLogger("corestream.analytics")

# Router para analíticas
router = APIRouter(prefix="/analytics", tags=["Analíticas"])


@router.get(
    "/summary/{app_id}",
    summary="Resumen de métricas de aplicación",
    description="Retorna estadísticas resumidas de una aplicación"
)
async def get_application_summary(
    app_id: UUID,
    assignee_id: Optional[UUID] = Query(None, description="Filtrar por desarrollador asignado"),
    sprint_id: Optional[UUID] = Query(None, description="Filtrar por Sprint"),
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.GROUP_LEADER])),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Obtiene un resumen de métricas de una aplicación.

    Args:
        app_id (UUID): ID de la aplicación
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        dict: Diccionario con métricas resumidas (totales, estados,
        prioridades, bloqueados, pendientes y vencidos)

    Raises:
        HTTPException: Si la aplicación no existe (404)
    """
    # Verificar que la aplicación existe
    app_check = await db.execute(
        select(Application).where(Application.id == app_id)
    )
    if not app_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aplicación con ID {app_id} no encontrada"
        )

    # Métricas de tickets (estado, prioridad, vencidos) con consultas GROUP BY
    metrics = await analytics_service.get_ticket_metrics(
        db, app_id, assignee_id=assignee_id, sprint_id=sprint_id
    )

    # Contar épicas
    epics = await db.execute(
        select(func.count(Epic.id))
        .where(Epic.application_id == app_id)
    )
    epic_count = epics.scalar()

    return {
        "application_id": app_id,
        # Campos que ya consumía el frontend (se conservan)
        "total_tickets": metrics["total_tickets"],
        "completed_tickets": metrics["completed_tickets"],
        "in_progress_tickets": metrics["by_status"]["IN_PROGRESS"],
        "todo_tickets": metrics["by_status"]["TODO"],
        "total_epics": epic_count,
        "completion_percentage": metrics["completion_percentage"],
        # Campos nuevos (WEB-06: bloqueados, métricas y salud del proyecto)
        "blocked_tickets": metrics["blocked_tickets"],
        "blocked_percentage": metrics["blocked_percentage"],
        "pending_tickets": metrics["pending_tickets"],
        "overdue_tickets": metrics["overdue_tickets"],
        "redirected_tickets": metrics["redirected_tickets"],
        "redirection_events_count": metrics["redirection_events_count"],
        "redirection_events": metrics["redirection_events"],
        "overdue_by_status": metrics["overdue_by_status"],
        "by_group_status": metrics["by_group_status"],
        "by_group_priority": metrics["by_group_priority"],
        "bottlenecks": metrics["bottlenecks"],
        "avg_time_hours": metrics["avg_time_hours"],
        "by_status": metrics["by_status"],
        "by_priority": metrics["by_priority"],
    }
