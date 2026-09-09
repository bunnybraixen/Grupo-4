"""
Router de Analíticas e Informes.

Proporciona endpoints para análisis y visualización de datos:
- Resumen de métricas de aplicaciones
- Desempeño individual de usuarios
- Mapas de calor de actividad
- Gráficos burndown de épicas
- Exportación de datos en CSV
"""

import csv
import io
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models import (
    Application,
    Epic,
    SupportSeverity,
    Ticket,
    TicketStatus,
    TicketType,
    User,
    UserRole,
)
from app.schemas.analytics import SupportSummarySchema
from app.services.analytics_service import analytics_service

# Router para analíticas
router = APIRouter(tags=["Analíticas"])


@router.get(
    "/summary/{app_id}",
    summary="Resumen de métricas de aplicación",
    description="Retorna estadísticas resumidas de una aplicación"
)
async def get_application_summary(
    app_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Obtiene un resumen de métricas de una aplicación.

    Args:
        app_id (int): ID de la aplicación
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        dict: Diccionario con métricas resumidas

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

    # Contar tickets por estado
    total_tickets = await db.execute(
        select(func.count(Ticket.id))
        .join(Epic)
        .where(Epic.application_id == app_id)
    )
    total = total_tickets.scalar()

    completed = await db.execute(
        select(func.count(Ticket.id))
        .join(Epic)
        .where(Epic.application_id == app_id, Ticket.status == TicketStatus.COMPLETED)
    )
    completed_count = completed.scalar()

    in_progress = await db.execute(
        select(func.count(Ticket.id))
        .join(Epic)
        .where(Epic.application_id == app_id, Ticket.status == TicketStatus.IN_PROGRESS)
    )
    in_progress_count = in_progress.scalar()

    todo = await db.execute(
        select(func.count(Ticket.id))
        .join(Epic)
        .where(Epic.application_id == app_id, Ticket.status == TicketStatus.TODO)
    )
    todo_count = todo.scalar()

    # Contar tickets bloqueados (BLOCKED + BLOCKED_QUESTION)
    blocked = await db.execute(
        select(func.count(Ticket.id))
        .join(Epic)
        .where(
            Epic.application_id == app_id,
            Ticket.status.in_([TicketStatus.BLOCKED, TicketStatus.BLOCKED_QUESTION])
        )
    )
    blocked_count = blocked.scalar()

    # Contar tickets redirigidos
    redirected = await db.execute(
        select(func.count(Ticket.id))
        .join(Epic)
        .where(Epic.application_id == app_id, Ticket.status == TicketStatus.REDIRECTED)
    )
    redirected_count = redirected.scalar()

    # Contar épicas
    epics = await db.execute(
        select(func.count(Epic.id))
        .where(Epic.application_id == app_id)
    )
    epic_count = epics.scalar()

    # Calcular KPIs
    total_safe = total or 1
    completion_percentage = ((completed_count or 0) / total_safe) * 100
    efficiency_index = round(((completed_count or 0) / total_safe) * 100, 1)
    block_rate       = round(((blocked_count or 0)   / total_safe) * 100, 1)
    rotation_rate    = round(((redirected_count or 0) / total_safe) * 100, 1)

    return {
        "application_id": app_id,
        "total_tickets": total,
        "completed_tickets": completed_count,
        "in_progress_tickets": in_progress_count,
        "todo_tickets": todo_count,
        "blocked_tickets": blocked_count,
        "redirected_tickets": redirected_count,
        "total_epics": epic_count,
        "completion_percentage": round(completion_percentage, 2),
        "efficiency_index": efficiency_index,
        "block_rate": block_rate,
        "rotation_rate": rotation_rate,
    }


@router.get(
    "/support-summary",
    response_model=SupportSummarySchema,
    summary="Resumen de tickets de soporte",
    description="Retorna conteos por estado/severidad y el tiempo promedio de resolución de los tickets de soporte"
)
async def get_support_summary(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SupportSummarySchema:
    """
    Obtiene métricas agregadas de los tickets de soporte (ticket_type == SUPPORT).

    Los tickets de soporte tienen epic_id = NULL por diseño, por lo que quedan
    fuera de las métricas por-aplicación (que usan INNER JOIN Epic). Este endpoint
    los agrega de forma global e independiente, sin recibir app_id.

    Returns:
        SupportSummarySchema: conteos por estado, por severidad y tiempo promedio
        de resolución en horas.
    """
    # Conteo por estado (REPORTED / INVESTIGATING / RESOLVED)
    status_result = await db.execute(
        select(Ticket.status, func.count(Ticket.id))
        .where(Ticket.ticket_type == TicketType.SUPPORT)
        .group_by(Ticket.status)
    )
    by_status: dict[str, int] = {
        TicketStatus.REPORTED.value: 0,
        TicketStatus.INVESTIGATING.value: 0,
        TicketStatus.RESOLVED.value: 0,
    }
    for st, count in status_result.all():
        key = st.value if hasattr(st, "value") else str(st)
        by_status[key] = count

    # Conteo por severidad (CRITICAL / HIGH / MEDIUM / LOW) — solo tickets activos
    # (no resueltos), ya que esta sección representa bugs pendientes por severidad.
    severity_result = await db.execute(
        select(Ticket.severity, func.count(Ticket.id))
        .where(
            Ticket.ticket_type == TicketType.SUPPORT,
            Ticket.status != TicketStatus.RESOLVED,
        )
        .group_by(Ticket.severity)
    )
    by_severity: dict[str, int] = {
        SupportSeverity.CRITICAL.value: 0,
        SupportSeverity.HIGH.value: 0,
        SupportSeverity.MEDIUM.value: 0,
        SupportSeverity.LOW.value: 0,
    }
    for sev, count in severity_result.all():
        if sev is None:
            continue
        key = sev.value if hasattr(sev, "value") else str(sev)
        by_severity[key] = count

    # Tiempo promedio de resolución (completed_at - created_at) de los RESOLVED
    resolved_result = await db.execute(
        select(Ticket.created_at, Ticket.completed_at)
        .where(
            Ticket.ticket_type == TicketType.SUPPORT,
            Ticket.status == TicketStatus.RESOLVED,
            Ticket.completed_at.isnot(None),
        )
    )
    durations_hours: list[float] = []
    for created_at, completed_at in resolved_result.all():
        if created_at and completed_at:
            durations_hours.append((completed_at - created_at).total_seconds() / 3600.0)

    avg_resolution_time_hours = (
        round(sum(durations_hours) / len(durations_hours), 2) if durations_hours else 0.0
    )

    return SupportSummarySchema(
        by_status=by_status,
        by_severity=by_severity,
        avg_resolution_time_hours=avg_resolution_time_hours,
    )


@router.get(
    "/performance/{app_id}",
    summary="Datos de desempeño de usuarios",
    description="Retorna métricas de desempeño por usuario en una aplicación"
)
async def get_performance_data(
    app_id: UUID,
    start_date: Optional[str] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    current_user = Depends(get_current_user),
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

    # Parsear fechas si se proporcionan (soporta ISO y YYYY-MM-DD)
    start = None
    end = None
    if start_date:
        try:
            # Intenta ISO primero, luego YYYY-MM-DD
            if 'T' in start_date:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00')).replace(tzinfo=None)
            else:
                start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de start_date inválido (use ISO o YYYY-MM-DD)"
            )

    if end_date:
        try:
            # Intenta ISO primero, luego YYYY-MM-DD
            if 'T' in end_date:
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00')).replace(tzinfo=None)
            else:
                end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de end_date inválido (use ISO o YYYY-MM-DD)"
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
    start_date: Optional[str] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    current_user = Depends(get_current_user),
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
    # 1. Verificar que la aplicación existe
    app_check = await db.execute(
        select(Application).where(Application.id == app_id)
    )
    if not app_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aplicación con ID {app_id} no encontrada"
        )

    # 2. Determinar rango de fechas: usa params si se envían, sino últimos 30 días
    now = datetime.now(timezone.utc)
    if start_date:
        try:
            query_start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            query_start = now - timedelta(days=30)
    else:
        query_start = now - timedelta(days=30)

    if end_date:
        try:
            query_end = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            )
        except ValueError:
            query_end = now
    else:
        query_end = now

    # 3. Buscar todos los tickets completados en esta app en el rango seleccionado
    query = (
        select(User.full_name, User.email, Ticket.completed_at)
        .select_from(Ticket)
        .join(Epic, Ticket.epic_id == Epic.id)
        .outerjoin(User, Ticket.assignee_id == User.id)
        .where(
            Epic.application_id == app_id,
            Ticket.status == TicketStatus.COMPLETED,
            Ticket.completed_at >= query_start,
            Ticket.completed_at <= query_end,
        )
    )
    result = await db.execute(query)
    completed_tickets = result.all()

    # 4. Procesar y agrupar los datos por usuario
    user_activity = {}

    # Función auxiliar para sacar iniciales del avatar (ej: "Ana García" -> "AG")
    def get_initials(name: str) -> str:
        if not name:
            return "U"
        parts = [n for n in name.split() if n]
        return "".join([p for p in parts]).upper()[:2]

    for full_name, email, completed_at in completed_tickets:
        user_key = email or "sin_asignar" # Usamos el email como ID único
        
        if user_key not in user_activity:
            display_name = full_name or email or "Sin Asignar"
            user_activity[user_key] = {
                "name": display_name,
                "avatar": get_initials(display_name),
                "data": [0, 0, 0, 0, 0, 0, 0] # Array para Lunes(0) a Domingo(6)
            }

        if completed_at:
            # .weekday() devuelve 0 para Lunes y 6 para Domingo
            weekday = completed_at.weekday()
            user_activity[user_key]["data"][weekday] += 1

    # 5. Estructurar exactamente como lo pide el Frontend
    heatmap_data = list(user_activity.values())

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
    current_user = Depends(get_current_user),
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
    epic = epic_check.scalar_one_or_none()
    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    # Obtener los tickets de esta épica
    result = await db.execute(
        select(Ticket.created_at, Ticket.completed_at)
        .where(Ticket.epic_id == epic_id)
    )
    tickets = result.all()
    total_tickets = len(tickets)

    # Si no hay tickets, enviamos gráfico vacío
    if total_tickets == 0:
        return {"epic_id": epic_id, "burndown": {"dates": [], "ideal": [], "actual": []}}

    # Determinar el rango de tiempo (Eje X)
    now = datetime.now(timezone.utc)
    start_date = epic.created_at or (now - timedelta(days=14))
    end_date = epic.due_date or now

    # Convertir a datetime si vienen como date puro
    if isinstance(start_date, date) and not isinstance(start_date, datetime):
        start_date = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    if isinstance(end_date, date) and not isinstance(end_date, datetime):
        end_date = datetime.combine(end_date, datetime.min.time()).replace(tzinfo=timezone.utc)

    total_days = max((end_date - start_date).days, 1) # Evitar división por cero

    dates, ideal_data, actual_data = [], [], []

    # Generar la curva día por día
    for i in range(total_days + 1):
        current_day = start_date + timedelta(days=i)
        dates.append(current_day.strftime("%d %b")) # Ej: "15 May"

        # Curva Ideal: Baja como escalera recta desde Total hasta 0
        ideal_val = max(0, round(total_tickets - (total_tickets / total_days) * i, 1))
        ideal_data.append(ideal_val)

        # Curva Real: Si el día aún no llega (futuro), no hay dato
        if current_day.date() > now.date():
            actual_data.append(None)
        else:
            # Contamos cuántos tickets se habían completado hasta ese día
            completed = sum(1 for t in tickets if t.completed_at and t.completed_at.date() <= current_day.date())
            actual_data.append(total_tickets - completed)

    return {
        "epic_id": epic_id,
        "burndown": {
            "dates": dates,
            "ideal": ideal_data,
            "actual": actual_data
        }
    }


@router.get(
    "/export/csv/{app_id}",
    summary="Exportar datos a CSV",
    description="Exporta datos de desempeño de una aplicación en formato CSV"
)
async def export_performance_csv(
    app_id: UUID,
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.TEAM_LEADER])),
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """
    Exporta datos de desempeño en formato CSV.

    Args:
        app_id (int): ID de la aplicación
        current_user (User): Usuario autenticado con rol TEAM_LEADER
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

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al exportar CSV: {str(e)}"
        )
