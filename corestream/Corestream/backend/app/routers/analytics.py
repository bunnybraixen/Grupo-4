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
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
from datetime import datetime
import csv
import io

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


@router.get(
    "/performance/{app_id}",
    summary="Datos de desempeño de usuarios",
    description="Retorna métricas de desempeño por usuario en una aplicación"
)
async def get_performance_data(
    app_id: UUID,
    start_date: Optional[str] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.GROUP_LEADER])),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Obtiene datos de desempeño de usuarios en una aplicación.

    Args:
        app_id (int): ID de la aplicación
        start_date (str): Fecha de inicio para filtrar (opcional)
        end_date (str): Fecha de fin para filtrar (opcional)
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        dict: Diccionario con métricas de desempeño por usuario

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

    # Parsear fechas si se proporcionan
    start = None
    end = None
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de start_date inválido (use YYYY-MM-DD)"
            )

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de end_date inválido (use YYYY-MM-DD)"
            )

    # Usar servicio de analíticas para obtener datos
    performance_data = await analytics_service.get_user_performance(
        app_id, start, end, db
    )

    return {
        "application_id": app_id,
        "period": {
            "start": start_date,
            "end": end_date
        },
        "user_performance": performance_data
    }


@router.get(
    "/heatmap/{app_id}",
    summary="Mapa de calor de actividad",
    description="Retorna datos de actividad en formato de mapa de calor"
)
async def get_heatmap_data(
    app_id: UUID,
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.GROUP_LEADER])),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Obtiene datos de actividad en formato de mapa de calor.

    Args:
        app_id (int): ID de la aplicación
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        dict: Datos del mapa de calor

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

    # Usar servicio de analíticas
    heatmap_data = await analytics_service.get_activity_heatmap(app_id, db)

    return {
        "application_id": app_id,
        "heatmap": heatmap_data
    }


@router.get(
    "/burndown/{epic_id}",
    summary="Gráfico burndown de épica",
    description="Retorna datos del gráfico burndown de una épica"
)
async def get_burndown_chart(
    epic_id: UUID,
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.GROUP_LEADER])),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Obtiene datos del gráfico burndown para una épica.

    Args:
        epic_id (int): ID de la épica
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        dict: Datos del burndown chart

    Raises:
        HTTPException: Si la épica no existe (404)
    """
    # Verificar que la épica existe
    epic_check = await db.execute(
        select(Epic).where(Epic.id == epic_id)
    )
    if not epic_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    # Usar servicio de analíticas
    burndown_data = await analytics_service.get_burndown_chart(epic_id, db)

    return {
        "epic_id": epic_id,
        "burndown": burndown_data
    }


@router.get(
    "/export/csv/{app_id}",
    summary="Exportar datos a CSV",
    description="Exporta datos de desempeño de una aplicación en formato CSV"
)
async def export_performance_csv(
    app_id: UUID,
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.GROUP_LEADER])),
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """
    Exporta datos de desempeño en formato CSV.

    Args:
        app_id (int): ID de la aplicación
        current_user (User): Usuario autenticado con rol ADMIN o GROUP_LEADER
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        StreamingResponse: Archivo CSV con datos de desempeño

    Raises:
        HTTPException: Si la aplicación no existe (404) o no tiene permisos (403)
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

    try:
        # Obtener datos de desempeño
        performance_data = await analytics_service.get_user_performance(
            app_id, None, None, db
        )

        # Crear archivo CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)

        # Escribir encabezados
        writer.writerow([
            "Usuario", "Tickets Completados", "Tickets en Progreso",
            "Tickets TODO", "Actividad Total", "Porcentaje Completación"
        ])

        # Escribir datos
        for user_data in performance_data:
            writer.writerow([
                user_data.get("user_name", "Desconocido"),
                user_data.get("completed_tickets", 0),
                user_data.get("in_progress_tickets", 0),
                user_data.get("todo_tickets", 0),
                user_data.get("total_activity", 0),
                user_data.get("completion_percentage", 0)
            ])

        # Preparar respuesta como descarga
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=performance_{app_id}.csv"}
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error al exportar CSV")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al exportar CSV"
        )
