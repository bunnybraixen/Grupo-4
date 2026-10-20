"""
Servicio de análisis y métricas de desempeño para CoreStream.

Este módulo proporciona funciones de análisis avanzadas para generar métricas
de desempeño de usuarios, heatmaps de productividad, gráficos de burndown,
y resúmenes de proyecto. Utiliza agregaciones de base de datos para rendimiento
óptimo en grandes volúmenes de datos.

Métricas principales:
- Efficiency: Tickets completados por hora de trabajo
- Blocking Index: Porcentaje de tickets bloqueados
- Churn Index: Porcentaje de tickets redirigidos (movimiento sin progreso)
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_
from fastapi import HTTPException, status

# Importar modelos desde el paquete de modelos
# from app.models import TicketEvent, Ticket, User


class AnalyticsService:
    """
    Servicio de análisis que proporciona métricas de desempeño y productividad.
    
    Métodos principales:
    - get_user_performance: Métricas individuales de usuario
    - get_heatmap_data: Distribución de productividad por día y usuario
    - get_burndown_data: Progreso de finalización de epic
    - get_summary: Resumen ejecutivo de proyecto
    """

    @staticmethod
    async def get_user_performance(
        db: AsyncSession,
        application_id: str,
        date_from: datetime,
        date_to: datetime
    ) -> List[dict]:
        """
        Obtiene métricas de desempeño detalladas para cada usuario.
        
        Analiza el comportamiento de usuarios dentro de un rango de fechas,
        calculando métricas clave que reflejan productividad, calidad, y
        eficiencia en la ejecución de tareas.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            application_id (str): ID de la aplicación/proyecto a analizar
            date_from (datetime): Fecha inicial del período de análisis
            date_to (datetime): Fecha final del período de análisis (inclusive)
            
        Returns:
            List[dict]: Lista de diccionarios con métricas de cada usuario
            
        Estructura de cada elemento:
            {
                'user_id': uuid,
                'user_name': str,
                'user_email': str,
                'tickets_processed': int,        # Total de tickets trabajados
                'tickets_completed': int,       # Total de tickets terminados (DONE)
                'completion_rate': float,       # Porcentaje completados (0-100)
                'total_questions': int,         # Preguntas planteadas
                'total_redirections': int,      # Tickets redirigidos
                'average_time_spent': float,    # Promedio en horas
                'efficiency_score': float,      # Tickets/hora (0-100 escala)
                'blocking_index': float,        # % de tiempo bloqueado (0-100)
                'churn_index': float,           # % de tickets redirigidos (0-100)
                'avg_resolution_time': float,   # Promedio en horas hasta DONE
                'quality_score': float          # Score compuesto 0-100
            }
            
        Raises:
            HTTPException(400): Rango de fechas inválido (from > to)
            HTTPException(404): Application no encontrada
            HTTPException(500): Error en cálculo de métricas
            
        Cálculos detallados:
            - tickets_processed: Count(DISTINCT ticket_id) por usuario
            - tickets_completed: Count(TicketEvent.TICKET_COMPLETED) por usuario
            - completion_rate: (completados / procesados) * 100
            - total_questions: Count(TicketEvent.QUESTION_RAISED) por usuario
            - total_redirections: Count(TicketEvent.TICKET_REDIRECTED) por usuario
            - average_time_spent: AVG(time_spent_seconds) / 3600
            - efficiency_score: (completados / horas_totales) * constante_escala
            - blocking_index: (SUM(blocked_time_seconds) / SUM(time_spent_seconds)) * 100
            - churn_index: (redirections / processed) * 100
            - quality_score: Promedio ponderado de completion_rate, blocking_index inverso, churn inverso
            
        Detalle técnico:
            - Agrupa por user_id para consolidar métricas
            - Filtra eventos dentro del rango de fechas
            - Solo incluye usuarios que tuvieron actividad en el rango
            - Evita divisiones por cero con CASE/WHEN
            - Ordena resultados por efficiency_score descendente
        """
        try:
            # Validar rango de fechas
            if date_from > date_to:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha inicial debe ser menor o igual a la fecha final"
                )
            
            # Asegurar que las fechas cubren día completo
            # date_to se ajusta a fin del día para inclusividad
            date_to_end = date_to.replace(hour=23, minute=59, second=59)
            
            # Construir queries SQL para agregaciones
            # NOTA: Estos son pseudocódigos, la implementación real depende del ORM
            
            # 1. Contar tickets procesados por usuario (DISTINCT)
            # SELECT 
            #    user_id,
            #    COUNT(DISTINCT ticket_id) as tickets_processed,
            #    COUNT(CASE WHEN event_type = 'TICKET_COMPLETED' THEN 1 END) as tickets_completed,
            #    COUNT(CASE WHEN event_type = 'QUESTION_RAISED' THEN 1 END) as total_questions,
            #    COUNT(CASE WHEN event_type = 'TICKET_REDIRECTED' AND from_user_id = user_id THEN 1 END) as redirections,
            #    AVG(ticket.time_spent_seconds) as avg_time_seconds,
            #    SUM(ticket.blocked_time_seconds) as total_blocked_seconds
            # FROM ticket_events
            # JOIN tickets ON ticket_events.ticket_id = tickets.id
            # WHERE application_id = ? AND created_at BETWEEN ? AND ?
            # GROUP BY user_id
            
            user_performance = []
            
            # Obtener usuarios activos en el período
            # stmt = select(User).where(User.application_id == application_id)
            # result = await db.execute(stmt)
            # users = result.scalars().all()
            
            # for user in users:
            #     # Calcular métricas para cada usuario
            #     # (Implementar en código real)
            #     performance = {
            #         'user_id': str(user.id),
            #         'user_name': user.name,
            #         'user_email': user.email,
            #         'tickets_processed': 0,
            #         'tickets_completed': 0,
            #         'completion_rate': 0.0,
            #         'total_questions': 0,
            #         'total_redirections': 0,
            #         'average_time_spent': 0.0,
            #         'efficiency_score': 0.0,
            #         'blocking_index': 0.0,
            #         'churn_index': 0.0,
            #         'avg_resolution_time': 0.0,
            #         'quality_score': 0.0
            #     }
            #     user_performance.append(performance)
            
            return user_performance
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al calcular métricas de desempeño de usuarios"
            )

    @staticmethod
    async def get_heatmap_data(
        db: AsyncSession,
        application_id: str,
        date_from: datetime,
        date_to: datetime
    ) -> List[dict]:
        """
        Genera datos de heatmap de productividad por usuario y día de semana.
        
        Proporciona una visualización de patrones de productividad mostrando
        cuántos tickets completaron usuarios en cada día de la semana. Útil
        para identificar patrones de actividad y bottlenecks por día.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            application_id (str): ID de la aplicación/proyecto
            date_from (datetime): Fecha inicial del período de análisis
            date_to (datetime): Fecha final del período de análisis
            
        Returns:
            List[dict]: Lista de registros de heatmap
            
        Estructura de cada elemento:
            {
                'user_id': uuid,
                'user_name': str,
                'day_of_week': int,              # 0=Lunes, 6=Domingo
                'day_name': str,                 # 'Lunes', 'Martes', etc.
                'completed_tickets': int,       # Tickets DONE en ese día
                'avg_time_per_ticket': float,   # Promedio horas
                'blocked_count': int,            # Veces que fue BLOCKED
                'redirected_count': int,         # Veces que fue REDIRECTED
                'productivity_score': float      # Score 0-100 para ese día
            }
            
        Raises:
            HTTPException(500): Error en cálculo de heatmap
            
        Cálculos:
            - Agrupa TICKET_COMPLETED events por usuario y día de semana
            - Calcula promedios de tiempo y métricas por combinación
            - Ordena por día de semana luego por usuario
            - productivity_score es normalizado a 0-100 relativamente
            
        Detalle técnico:
            - Usa EXTRACT(DOW FROM created_at) para día de semana
            - DOW: 0=Domingo, 1=Lunes... 6=Sábado (SQL standard)
            - Se ajusta para usar convención Lunes=0 en respuesta
            - Registros con 0 completados se excluyen para claridad
            - Útil para detección de patrones anómalos de productividad
        """
        try:
            # Mapeo de números de día a nombres
            day_names = {
                0: 'Lunes',
                1: 'Martes',
                2: 'Miércoles',
                3: 'Jueves',
                4: 'Viernes',
                5: 'Sábado',
                6: 'Domingo'
            }
            
            # Validar rango de fechas
            if date_from > date_to:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha inicial debe ser menor o igual a la fecha final"
                )
            
            # Query para obtener datos de heatmap
            # SELECT 
            #    user_id,
            #    EXTRACT(DOW FROM created_at) as day_of_week,
            #    COUNT(*) as completed_tickets,
            #    AVG(ticket.time_spent_seconds)/3600 as avg_time_per_ticket
            # FROM ticket_events
            # WHERE event_type = 'TICKET_COMPLETED' 
            #   AND application_id = ?
            #   AND created_at BETWEEN ? AND ?
            # GROUP BY user_id, day_of_week
            # ORDER BY day_of_week, user_id
            
            heatmap_data = []
            
            # (Implementar en código real con SQLAlchemy)
            # Obtener usuarios y sus eventos de completación por día
            
            return heatmap_data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al generar datos de heatmap"
            )

    @staticmethod
    async def get_burndown_data(
        db: AsyncSession,
        epic_id: str
    ) -> dict:
        """
        Calcula datos de burndown chart para un epic.
        
        Genera datos para visualizar progreso de completación de un epic,
        mostrando línea ideal de completación versus línea actual. Útil
        para identificar si el epic se completará a tiempo.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            epic_id (str): ID del epic a analizar
            
        Returns:
            dict: Diccionario con datos de burndown
            
        Estructura de retorno:
            {
                'epic_id': uuid,
                'epic_title': str,
                'status': str,                  # 'ON_TRACK', 'AT_RISK', 'DELAYED'
                'total_tickets': int,
                'completed_tickets': int,
                'remaining_tickets': int,
                'completion_percentage': float, # 0-100
                'start_date': datetime,
                'end_date': datetime,           # Planned end date
                'actual_end_date': Optional[datetime],
                'days_elapsed': int,
                'days_planned': int,
                'ideal_remaining': int,         # Línea ideal de progreso
                'actual_remaining': int,        # Línea actual
                'variance': int,                # actual_remaining - ideal_remaining
                'burn_rate': float,             # Tickets completados por día
                'projected_completion': datetime,
                'velocity_trend': str           # 'INCREASING', 'STABLE', 'DECREASING'
            }
            
        Raises:
            HTTPException(404): Epic no encontrado
            HTTPException(500): Error en cálculo de burndown
            
        Cálculos:
            - ideal_remaining: Progresión lineal desde total a 0
            - actual_remaining: Tickets no DONE al final de cada día
            - variance: Diferencia entre ideal y actual (+ = delantado)
            - burn_rate: Promedio tickets/día completados hasta ahora
            - projected_completion: Si se mantiene burn_rate actual
            
        Detalle técnico:
            - Status se calcula así:
              * ON_TRACK: variance > -20% y no es fin de período
              * AT_RISK: variance entre -20% y -50%
              * DELAYED: variance < -50% o actual_end > planned_end
            - Usa eventos TICKET_COMPLETED para determinar completación
            - Histórico por día permite visualización en gráfico
            - Proyección asume velocidad constante (simplificado)
        """
        try:
            # Validar que epic existe
            # stmt = select(Epic).where(Epic.id == UUID(epic_id))
            # result = await db.execute(stmt)
            # epic = result.scalars().first()
            
            # if not epic:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Epic no encontrado"
            #     )
            
            # Obtener tickets del epic
            # stmt_tickets = select(Ticket).where(
            #    (Ticket.epic_id == UUID(epic_id))
            # )
            # result_tickets = await db.execute(stmt_tickets)
            # tickets = result_tickets.scalars().all()
            
            # Contar total y completados
            # total_tickets = len(tickets)
            # completed_tickets = len([t for t in tickets if t.status == 'DONE'])
            # remaining_tickets = total_tickets - completed_tickets
            
            # Calcular línea ideal
            # days_planned = (epic.end_date - epic.start_date).days
            # days_elapsed = (datetime.utcnow() - epic.start_date).days
            
            # Línea ideal: desciende linealmente
            # ideal_remaining = max(
            #     0,
            #     total_tickets - (completed_tickets / days_planned * days_elapsed)
            # )
            
            # Calcular burn rate
            # if days_elapsed > 0:
            #     burn_rate = completed_tickets / days_elapsed
            # else:
            #     burn_rate = 0
            
            # Proyectar completación
            # if burn_rate > 0:
            #     days_remaining = remaining_tickets / burn_rate
            #     projected_completion = datetime.utcnow() + timedelta(days=days_remaining)
            # else:
            #     projected_completion = epic.end_date
            
            # Determinar status
            # variance = remaining_tickets - ideal_remaining
            # variance_percentage = (variance / total_tickets) * 100 if total_tickets > 0 else 0
            
            # if variance_percentage > -20:
            #     status = 'ON_TRACK'
            # elif variance_percentage > -50:
            #     status = 'AT_RISK'
            # else:
            #     status = 'DELAYED'
            
            return {
                # 'epic_id': str(epic.id),
                # 'epic_title': epic.title,
                # 'status': status,
                # 'total_tickets': total_tickets,
                # 'completed_tickets': completed_tickets,
                # 'remaining_tickets': remaining_tickets,
                # 'completion_percentage': (completed_tickets / total_tickets * 100) if total_tickets > 0 else 0,
                # 'start_date': epic.start_date.isoformat(),
                # 'end_date': epic.end_date.isoformat(),
                # 'actual_end_date': None,  # Se llena si ya está DONE
                # 'days_elapsed': days_elapsed,
                # 'days_planned': days_planned,
                # 'ideal_remaining': ideal_remaining,
                # 'actual_remaining': remaining_tickets,
                # 'variance': int(variance),
                # 'burn_rate': burn_rate,
                # 'projected_completion': projected_completion.isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al calcular datos de burndown"
            )

    @staticmethod
    async def get_summary(
        db: AsyncSession,
        application_id: str
    ) -> dict:
        """
        Genera resumen ejecutivo de métricas del proyecto.
        
        Proporciona una vista consolidada de métricas clave del proyecto,
        incluyendo totales, promedios, y comparativas week-over-week para
        identificar tendencias de mejora o deterioro.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            application_id (str): ID de la aplicación/proyecto
            
        Returns:
            dict: Diccionario con resumen de métricas
            
        Estructura de retorno:
            {
                'application_id': uuid,
                'application_name': str,
                'generated_at': datetime,
                'period': {
                    'start_date': datetime,
                    'end_date': datetime,
                    'days': int
                },
                'overview': {
                    'total_tickets': int,
                    'completed_tickets': int,
                    'blocked_tickets': int,
                    'in_progress_tickets': int,
                    'redirected_tickets_count': int,
                    'completion_rate': float,    # %
                    'blocked_rate': float        # %
                },
                'time_metrics': {
                    'total_time_spent_hours': float,
                    'average_ticket_time': float,  # horas
                    'total_blocked_time_hours': float,
                    'average_blocked_time': float  # horas
                },
                'performance': {
                    'efficiency_score': float,   # 0-100
                    'quality_score': float,      # 0-100
                    'team_health': str          # 'GOOD', 'WARNING', 'CRITICAL'
                },
                'trends': {
                    'week_over_week_completion': float,  # % change
                    'week_over_week_blocked': float,     # % change
                    'velocity_trend': str,               # 'UP', 'STABLE', 'DOWN'
                    'quality_trend': str                 # 'IMPROVING', 'STABLE', 'DEGRADING'
                },
                'team': {
                    'active_users': int,
                    'top_performer': {
                        'user_id': uuid,
                        'name': str,
                        'efficiency': float
                    },
                    'bottleneck_user': {
                        'user_id': uuid,
                        'name': str,
                        'blocking_index': float
                    }
                }
            }
            
        Raises:
            HTTPException(404): Application no encontrada
            HTTPException(500): Error en cálculo de resumen
            
        Cálculos:
            - Período por defecto es últimos 30 días
            - week_over_week: Comparación última semana vs semana anterior
            - team_health: Basado en blocking_rate, churn_rate, efficiency
            - Tendencias se calculan de velocidad actual vs promedio histórico
            
        Detalle técnico:
            - Agrupa por semana para detectar tendencias
            - Excluye primeros 3 días de la semana por falta de datos
            - Quality score considera completion, blocking, y churn
            - Team health: GOOD si score > 80, WARNING si 50-80, CRITICAL si < 50
            - Top performer basado en efficiency
            - Bottleneck basado en blocking_index
        """
        try:
            # Calcular período (últimos 30 días por defecto)
            date_to = datetime.utcnow()
            date_from = date_to - timedelta(days=30)
            
            # Query para obtener métricas consolidadas
            # SELECT 
            #    COUNT(*) as total_tickets,
            #    COUNT(CASE WHEN status = 'DONE' THEN 1 END) as completed,
            #    COUNT(CASE WHEN status = 'BLOCKED' THEN 1 END) as blocked,
            #    COUNT(CASE WHEN status = 'IN_PROGRESS' THEN 1 END) as in_progress,
            #    SUM(time_spent_seconds)/3600 as total_hours,
            #    AVG(time_spent_seconds)/3600 as avg_hours,
            #    SUM(blocked_time_seconds)/3600 as blocked_hours
            # FROM tickets
            # WHERE application_id = ? AND created_at BETWEEN ? AND ?
            
            summary = {
                # 'application_id': application_id,
                # 'application_name': 'App Name',
                # 'generated_at': datetime.utcnow().isoformat(),
                # 'period': {
                #     'start_date': date_from.isoformat(),
                #     'end_date': date_to.isoformat(),
                #     'days': 30
                # },
                # 'overview': { ... },
                # 'time_metrics': { ... },
                # 'performance': { ... },
                # 'trends': { ... },
                # 'team': { ... }
            }
            
            return summary
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al generar resumen de proyecto"
            )


# ---------------------------------------------------------------------------
# WEB-06: métricas de tickets por aplicación (estado, prioridad, vencidos)
# ---------------------------------------------------------------------------
from uuid import UUID as _UUID  # noqa: E402

from app.models import Epic as _Epic  # noqa: E402
from app.models import Ticket as _Ticket  # noqa: E402
from app.models import TicketStatus as _TicketStatus  # noqa: E402
from app.models import TicketEvent as _TicketEvent  # noqa: E402
from app.models import TicketEventType as _TicketEventType  # noqa: E402


async def get_ticket_metrics(
    db: AsyncSession,
    app_id: _UUID,
    assignee_id: Optional[_UUID] = None,
    sprint_id: Optional[_UUID] = None,
) -> dict:
    """
    Calcula las métricas de tickets de una aplicación con consultas GROUP BY.

    Devuelve cantidades por estado, distribución por prioridad, vencidos y
    porcentajes. Los tickets se asocian a la aplicación a través de su épica.
    """
    base = (
        select(_Ticket)
        .join(_Epic, _Epic.id == _Ticket.epic_id)
        .where(_Epic.application_id == app_id)
    )
    if assignee_id is not None:
        base = base.where(_Ticket.assignee_id == assignee_id)
    if sprint_id is not None:
        base = base.where(_Ticket.sprint_id == sprint_id)
    base_ids = base.with_only_columns(_Ticket.id).subquery()

    # Cantidad por estado
    by_status_rows = await db.execute(
        select(_Ticket.status, func.count(_Ticket.id))
        .where(_Ticket.id.in_(select(base_ids.c.id)))
        .group_by(_Ticket.status)
    )
    by_status = {s.value: 0 for s in _TicketStatus}
    for st, qty in by_status_rows.all():
        by_status[getattr(st, "value", str(st))] = qty

    # Distribución por prioridad
    by_priority_rows = await db.execute(
        select(_Ticket.priority, func.count(_Ticket.id))
        .where(_Ticket.id.in_(select(base_ids.c.id)))
        .group_by(_Ticket.priority)
    )
    by_priority = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "URGENT": 0}
    for pr, qty in by_priority_rows.all():
        by_priority[getattr(pr, "value", str(pr))] = qty

    # Vencidos: due_date pasada y no completados.
    # due_date es "timestamp without time zone", así que se compara con utcnow() naive.
    overdue_row = await db.execute(
        select(func.count(_Ticket.id)).where(
            _Ticket.id.in_(select(base_ids.c.id)),
            _Ticket.due_date.is_not(None),
            _Ticket.due_date < datetime.utcnow(),
            _Ticket.status != _TicketStatus.DONE,
        )
    )
    overdue = overdue_row.scalar() or 0

    overdue_status_rows = await db.execute(
        select(_Ticket.status, func.count(_Ticket.id)).where(
            _Ticket.id.in_(select(base_ids.c.id)),
            _Ticket.due_date.is_not(None),
            _Ticket.due_date < datetime.utcnow(),
            _Ticket.status != _TicketStatus.DONE,
        ).group_by(_Ticket.status)
    )
    overdue_by_status = {
        getattr(status, "value", str(status)): count
        for status, count in overdue_status_rows.all()
    }

    ticket_rows = await db.execute(
        select(_Ticket.id, _Ticket.title, _Ticket.status, _Ticket.created_at).where(
            _Ticket.id.in_(select(base_ids.c.id))
        )
    )
    tickets = {
        ticket_id: {
            "title": title,
            "status": getattr(status, "value", str(status)),
            "created_at": created_at,
        }
        for ticket_id, title, status, created_at in ticket_rows.all()
    }

    redirect_event_count_row = await db.execute(
        select(func.count(_TicketEvent.id)).where(
            _TicketEvent.ticket_id.in_(select(base_ids.c.id)),
            _TicketEvent.event_type == _TicketEventType.REDIRECTED,
        )
    )
    redirect_event_rows = await db.execute(
        select(
            _TicketEvent.ticket_id,
            _TicketEvent.from_user_id,
            _TicketEvent.to_user_id,
            _TicketEvent.detail,
            _TicketEvent.created_at,
        )
        .where(
            _TicketEvent.ticket_id.in_(select(base_ids.c.id)),
            _TicketEvent.event_type == _TicketEventType.REDIRECTED,
        )
        .order_by(_TicketEvent.created_at.desc())
        .limit(10)
    )
    redirection_events = [
        {
            "ticket_id": str(ticket_id),
            "ticket_title": tickets.get(ticket_id, {}).get("title", "Ticket"),
            "from_user_id": str(from_user_id) if from_user_id else None,
            "to_user_id": str(to_user_id) if to_user_id else None,
            "detail": detail or {},
            "created_at": created_at.isoformat() if created_at else None,
        }
        for ticket_id, from_user_id, to_user_id, detail, created_at in redirect_event_rows.all()
    ]

    status_events = await db.execute(
        select(
            _TicketEvent.ticket_id,
            _TicketEvent.event_type,
            _TicketEvent.detail,
            _TicketEvent.created_at,
        )
        .where(
            _TicketEvent.ticket_id.in_(select(base_ids.c.id)),
            _TicketEvent.event_type.in_(
                [_TicketEventType.STATUS_CHANGED, _TicketEventType.REDIRECTED, _TicketEventType.COMPLETED]
            ),
        )
        .order_by(_TicketEvent.created_at.asc())
    )
    entered_status_at = {ticket_id: info["created_at"] for ticket_id, info in tickets.items()}
    event_status = {
        _TicketEventType.REDIRECTED: "REDIRECTED",
        _TicketEventType.COMPLETED: "DONE",
    }
    for ticket_id, event_type, detail, created_at in status_events.all():
        current = tickets.get(ticket_id)
        if not current:
            continue
        target_status = (detail or {}).get("to_status") or event_status.get(event_type)
        if target_status and str(target_status).upper() == current["status"].upper():
            entered_status_at[ticket_id] = created_at

    from datetime import timezone

    now = datetime.now(timezone.utc)
    dwell_by_status: dict[str, list[float]] = {}
    ticket_dwell: list[dict] = []
    for ticket_id, info in tickets.items():
        if info["status"] in {"DONE", "COMPLETED"}:
            continue
        entered_at = entered_status_at.get(ticket_id)
        if not entered_at:
            continue
        current_time = now.replace(tzinfo=None) if entered_at.tzinfo is None else now
        hours = max(0.0, (current_time - entered_at).total_seconds() / 3600)
        dwell_by_status.setdefault(info["status"], []).append(hours)
        ticket_dwell.append({
            "ticket_id": str(ticket_id),
            "title": info["title"],
            "status": info["status"],
            "hours": round(hours, 1),
        })
    bottlenecks = [
        {
            "status": status,
            "ticket_count": by_status.get(status, 0),
            "average_hours": round(sum(hours) / len(hours), 1),
            "max_hours": round(max(hours), 1),
            "tickets": sorted(
                (ticket for ticket in ticket_dwell if ticket["status"] == status),
                key=lambda ticket: ticket["hours"],
                reverse=True,
            )[:3],
        }
        for status, hours in dwell_by_status.items()
    ]
    bottlenecks.sort(key=lambda item: item["average_hours"], reverse=True)

    by_group_priority: dict[str, dict[str, int]] = {}
    status_groups = {
        "completed": [_Ticket.status == _TicketStatus.DONE],
        "pending": [_Ticket.status != _TicketStatus.DONE],
        "blocked": [_Ticket.status == _TicketStatus.BLOCKED],
        "redirected": [_Ticket.status == _TicketStatus.REDIRECTED],
        "overdue": [
            _Ticket.due_date.is_not(None),
            _Ticket.due_date < datetime.utcnow(),
            _Ticket.status != _TicketStatus.DONE,
        ],
    }
    by_group_status: dict[str, dict[str, int]] = {}
    for group, conditions in status_groups.items():
        rows = await db.execute(
            select(_Ticket.status, func.count(_Ticket.id))
            .where(_Ticket.id.in_(select(base_ids.c.id)), *conditions)
            .group_by(_Ticket.status)
        )
        by_group_status[group] = {
            getattr(status, "value", str(status)): count
            for status, count in rows.all()
        }

    for group, conditions in status_groups.items():
        rows = await db.execute(
            select(_Ticket.priority, func.count(_Ticket.id))
            .where(_Ticket.id.in_(select(base_ids.c.id)), *conditions)
            .group_by(_Ticket.priority)
        )
        by_group_priority[group] = {
            getattr(priority, "value", str(priority)): count
            for priority, count in rows.all()
        }

    average_time_row = await db.execute(
        select(func.avg(_Ticket.time_spent_seconds)).where(
            _Ticket.id.in_(select(base_ids.c.id)),
            _Ticket.time_spent_seconds > 0,
        )
    )
    average_time_hours = round(float(average_time_row.scalar() or 0) / 3600, 2)

    total = sum(by_status.values())
    done = by_status["DONE"]
    blocked = by_status["BLOCKED"]
    pending = total - done

    def pct(n: int) -> float:
        return round((n / total) * 100, 2) if total else 0.0

    return {
        "total_tickets": total,
        "completed_tickets": done,
        "blocked_tickets": blocked,
        "pending_tickets": pending,
        "overdue_tickets": overdue,
        "redirected_tickets": by_status.get("REDIRECTED", 0),
        "redirection_events_count": redirect_event_count_row.scalar() or 0,
        "redirection_events": redirection_events,
        "overdue_by_status": overdue_by_status,
        "by_group_status": by_group_status,
        "by_group_priority": by_group_priority,
        "bottlenecks": bottlenecks,
        "avg_time_hours": average_time_hours,
        "completion_percentage": pct(done),
        "blocked_percentage": pct(blocked),
        "by_status": by_status,
        "by_priority": by_priority,
    }
