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
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Epic, Role, Ticket, TicketEvent, TicketStatus, User

# Tipos de evento que NO representan trabajo real sobre un ticket, sino acciones de
# gestión o autoría (crearlo, asignarlo, editar sus campos, moverlo entre épicas).
# No deben contar para "tickets procesados": un TEAM_LEADER que crea 50 tickets en el
# Builder y los asigna a developers no los "trabajó". Los tickets que sí trabajó
# quedan capturados por eventos de trabajo real (STATUS_CHANGED, COMPLETED,
# QUESTION_RAISED, REDIRECTED, TIMER_*, SUBTASK_*, COMMENT, etc.), porque esos eventos
# también agregan el ticket_id al set de procesados.
#
# Nota: la asignación de tickets de desarrollo se hace vía PATCH /tickets/{id}
# (endpoint genérico de update → evento UPDATED con user_id = quien asigna), por eso
# UPDATED también se excluye aquí.
NON_WORK_EVENT_TYPES = frozenset({
    "CREATED",
    "UPDATED",
    "MOVED",
    "ASSIGNED",
    "TICKET_ASSIGNED",
})


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
        app_id: int,
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        db: AsyncSession
    ) -> List[dict]:
        """
        Obtiene métricas de desempeño detalladas para cada usuario.
        
        Analiza el comportamiento de usuarios dentro de un rango de fechas,
        calculando métricas clave que reflejan productividad, calidad, y
        eficiencia en la ejecución de tareas.
        
        Args:
            app_id (int): ID de la aplicación/proyecto a analizar
            date_from (datetime): Fecha inicial del período de análisis
            date_to (datetime): Fecha final del período de análisis (inclusive)
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            
        Returns:
            List[dict]: Lista de diccionarios con métricas de cada usuario
            
        Estructura de cada elemento:
            {
                'user_id': uuid,
                'user_name': str,
                'tickets_processed': int,        # Total de tickets trabajados
                'tickets_completed': int,       # Total de tickets terminados (DONE)
                'questions_raised': int,        # Preguntas planteadas
                'redirections': int,      # Tickets redirigidos
                'avg_time_hours': float,    # Promedio en horas
                'efficiency': float,      # Tickets/hora (0-100 escala)
                'blocking_index': float,        # % de tiempo bloqueado (0-100)
                'churn_index': float,           # % de tickets redirigidos (0-100)
            }
            
        Raises:
            HTTPException(400): Rango de fechas inválido (from > to)
            HTTPException(500): Error en cálculo de métricas
            
        Detalle técnico:
            - Agrupa por user_id para consolidar métricas
            - Filtra eventos dentro del rango de fechas
            - Evita divisiones por cero
        """
        try:
            if date_from and date_to and date_from > date_to:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha inicial debe ser menor o igual a la fecha final"
                )
            
            # Obtener todos los tickets de la aplicación
            stmt_tickets = select(Ticket).join(Epic).where(Epic.application_id == app_id)
            result = await db.execute(stmt_tickets)
            app_tickets = result.scalars().all()
            ticket_ids = [t.id for t in app_tickets]

            if not ticket_ids:
                return []

            # Calcular tiempos y conteo de tickets asignados por usuario
            user_ticket_data: dict = {}
            for ticket in app_tickets:
                if ticket.assignee_id:
                    uid = str(ticket.assignee_id)
                    if uid not in user_ticket_data:
                        user_ticket_data[uid] = {"assigned": 0, "total_seconds": 0}
                    user_ticket_data[uid]["assigned"] += 1
                    user_ticket_data[uid]["total_seconds"] += ticket.time_spent_seconds or 0

            # Obtener todos los eventos de esos tickets
            stmt_events = select(TicketEvent).where(TicketEvent.ticket_id.in_(ticket_ids))
            if date_from:
                stmt_events = stmt_events.where(TicketEvent.created_at >= date_from)
            if date_to:
                date_to_end = date_to.replace(hour=23, minute=59, second=59)
                stmt_events = stmt_events.where(TicketEvent.created_at <= date_to_end)
                
            result_events = await db.execute(stmt_events)
            events = result_events.scalars().all()

            # Procesamiento en Python para máxima compatibilidad con asyncpg
            user_stats = {}
            for event in events:
                uid = str(event.user_id)
                if uid not in user_stats:
                    user_stats[uid] = {
                        "tickets_processed": set(),
                        "tickets_completed": 0,
                        "questions_raised": 0,
                        "redirections": 0,
                    }
                
                ev_type = event.event_type.value if hasattr(event.event_type, 'value') else event.event_type

                # Solo cuentan como "procesados" los tickets sobre los que el usuario
                # ejecutó trabajo real. Los eventos de gestión/autoría (crear, asignar,
                # editar, mover) se excluyen — ver NON_WORK_EVENT_TYPES. Esto evita que
                # un TEAM_LEADER que crea y asigna tickets a developers los cuente como
                # propios sin haberlos trabajado.
                if ev_type not in NON_WORK_EVENT_TYPES:
                    user_stats[uid]["tickets_processed"].add(event.ticket_id)

                if ev_type == 'COMPLETED':
                    user_stats[uid]["tickets_completed"] += 1
                elif ev_type == 'QUESTION_RAISED':
                    user_stats[uid]["questions_raised"] += 1
                elif ev_type == 'REDIRECTED':
                    user_stats[uid]["redirections"] += 1

            # Obtener datos de los usuarios encontrados — DEVELOPER y TEAM_LEADER
            # (los TEAM_LEADER también trabajan tickets: asignan, aprueban, completan)
            user_ids = [UUID(uid) for uid in user_stats.keys()]
            users = []
            if user_ids:
                stmt_users = (
                    select(User)
                    .join(User.role)
                    .where(User.id.in_(user_ids), Role.name.in_(["DEVELOPER", "TEAM_LEADER"]))
                )
                res_users = await db.execute(stmt_users)
                users = {str(u.id): u for u in res_users.scalars().all()}

            # Formatear la salida según el esquema UserPerformance
            performance_list = []
            for uid, stats in user_stats.items():
                user_obj = users.get(uid)
                if not user_obj:
                    continue
                
                processed = len(stats["tickets_processed"])
                completed = stats["tickets_completed"]
                questions = stats["questions_raised"]
                redirections = stats["redirections"]

                ticket_data = user_ticket_data.get(uid, {"assigned": 0, "total_seconds": 0})
                assigned = ticket_data["assigned"]
                total_seconds = ticket_data["total_seconds"]

                # avg_time_hours: promedio de tiempo real desde time_spent_seconds
                avg_time_hours = (total_seconds / 3600) / assigned if assigned > 0 else 0.0

                # Eficiencia normalizada: 1 ticket/hora = 100% (spec CS-031)
                # 3 tickets en 3 horas → total_hours=3, completed=3 → 100%
                total_hours = total_seconds / 3600
                efficiency = (completed / total_hours) * 100 if total_hours > 0 else 0.0

                # Índice de Bloqueo = Preguntas levantadas / Tickets procesados
                blocking_index = (questions / processed * 100) if processed > 0 else 0.0

                # Índice de Rotación = Redirecciones / Tickets asignados
                churn = (redirections / assigned * 100) if assigned > 0 else 0.0

                performance_list.append({
                    "user_id": user_obj.id,
                    "user_name": user_obj.full_name,
                    "avatar_url": user_obj.avatar_url,
                    "tickets_processed": processed,
                    "tickets_completed": completed,
                    "questions_raised": questions,
                    "redirections": redirections,
                    "avg_time_hours": round(avg_time_hours, 2),
                    "efficiency": round(min(100.0, efficiency), 2),
                    "blocking_index": round(min(100.0, blocking_index), 2),
                    "churn_index": round(min(100.0, churn), 2),
                    "total_activity": len(events) # Para el router de summary
                })

            return performance_list
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al calcular métricas de desempeño de usuarios: {str(e)}"
            )

    @staticmethod
    async def get_activity_heatmap(
        app_id: int,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
        ) -> List[dict]:
        """
        Genera datos de heatmap de productividad por usuario y día de semana.
        
        Proporciona una visualización de patrones de productividad mostrando
        cuántos tickets completaron usuarios en cada día de la semana. Útil
        para identificar patrones de actividad y bottlenecks por día.
        """
        try:
            # Empezamos la consulta base
            stmt = select(TicketEvent).join(Ticket).join(Epic).where(
                Epic.application_id == app_id,
                TicketEvent.event_type == 'COMPLETED'
            )

            # Filtramos por las fechas que manda el frontend
            if start_date:
                stmt = stmt.where(TicketEvent.created_at >= start_date)
            if end_date:
                end_date_eod = end_date.replace(hour=23, minute=59, second=59)  
                stmt = stmt.where(TicketEvent.created_at <= end_date_eod)

            # Ejecutamos la consulta
            result = await db.execute(stmt)
            events = result.scalars().all()

            user_activity = {}
            for event in events:
                uid = str(event.user_id)
                if uid not in user_activity:
                    user_activity[uid] = [0, 0, 0, 0, 0, 0, 0]
                
                # weekday(): 0 es Lunes, 6 es Domingo
                day_index = event.created_at.weekday()
                user_activity[uid][day_index] += 1

            # Obtener nombres de usuarios
            user_ids = [UUID(uid) for uid in user_activity.keys()]
            users = {}
            if user_ids:
                stmt_users = select(User).where(User.id.in_(user_ids))
                res_users = await db.execute(stmt_users)
                users = {str(u.id): u for u in res_users.scalars().all()}

            heatmap_data = []
            for uid, data in user_activity.items():
                if uid in users:
                    heatmap_data.append({
                        "user_id": users[uid].id,
                        "user_name": users[uid].full_name,
                        "data": data
                    })

            return heatmap_data
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar datos de heatmap: {str(e)}"
            )

    @staticmethod
    async def get_burndown_chart(epic_id: int, db: AsyncSession) -> dict:
        """
        Calcula datos de burndown chart para un epic.
        
        Genera datos para visualizar progreso de completación de un epic,
        mostrando línea ideal de completación versus línea actual. Útil
        para identificar si el epic se completará a tiempo.
        """
        try:
            stmt = select(Epic).where(Epic.id == epic_id)
            result = await db.execute(stmt)
            epic = result.scalar_one_or_none()

            if not epic:
                raise HTTPException(status_code=404, detail="Epic no encontrado")

            stmt_tickets = select(Ticket).where(Ticket.epic_id == epic_id)
            result_tickets = await db.execute(stmt_tickets)
            tickets = result_tickets.scalars().all()

            total_tickets = len(tickets)
            
            # Generar datos simulados de burndown lineal para el gráfico
            start_date = epic.created_at
            end_date = epic.due_date if epic.due_date else (start_date + timedelta(days=14))
            
            total_days = (end_date - start_date).days
            if total_days <= 0:
                total_days = 1

            ideal_points = []
            actual_points = []
            
            # Encontrar tickets que ya están completados y cuándo se completaron
            # Asumimos que los tickets completados tienen un completed_at. 
            # Si no lo tienen, puedes usar la fecha de actualización (updated_at)
            completed_tickets = [t for t in tickets if t.status == TicketStatus.COMPLETED and t.completed_at is not None]
            
            
            for day in range(total_days + 1):
                current_date = start_date + timedelta(days=day)
                date_str = current_date.strftime("%Y-%m-%d")
                
                # Punto ideal: línea recta desde total_tickets hasta 0
                ideal_points.append({
                    'date': date_str,
                    'points': max(0, total_tickets - (total_tickets * day / total_days))
                })
                
                # Punto real (Cuántos tickets quedaban vivos ESE día en específico)
                # Contamos cuántos tickets se completaron exactamente en esta fecha o antes
                tickets_completed_by_this_date = len([
                    t for t in completed_tickets 
                    if t.completed_at.date() <= current_date.date()
                ])
                
                actual_remaining = total_tickets - tickets_completed_by_this_date
                
                # No dibujar línea real en el futuro (si current_date > hoy)
                if current_date.date() <= datetime.utcnow().date():
                    actual_points.append({
                        'date': date_str,
                        'points': actual_remaining
                    })
            
            return {
                'ideal': ideal_points,
                'actual': actual_points,
                'total_tickets': total_tickets,
                'completed': len(completed_tickets)
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener datos de burndown: {str(e)}"
            )

# Instancia global del servicio de análisis
analytics_service = AnalyticsService()