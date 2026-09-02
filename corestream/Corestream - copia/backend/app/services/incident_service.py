"""
Servicio de lógica de negocio para gestión de incidentes en CoreStream.

Implementa operaciones complejas sobre incidentes, incluyendo creación, actualización,
cambios de estado, asignación, y cálculo de estadísticas. Maneja notificaciones
y auditoría de cambios sobre incidentes.

Autor: CoreStream Development Team
Fecha: 2026
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from sqlalchemy import select, func, and_, or_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.incident import (
    Incident,
    IncidentComment,
    IncidentCategory,
    IncidentStatus,
    IncidentSeverity
)
from app.models.user import User
from app.models.application import Application
from app.models.notification import Notification, NotificationType
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
    IncidentCommentCreate,
    IncidentCommentResponse,
    DashboardStats,
    IncidentsByTeamResponse,
    ByCategoryResponse,
    PriorityUpdateRequest,
    UserResponse,
)


class IncidentService:
    """
    Servicio de negocio para gestión de incidentes.

    Proporciona métodos asincronos para operaciones CRUD, gestión de estado,
    asignación, comentarios y generación de estadísticas. Integra notificaciones
    para mantener a usuarios informados sobre cambios en incidentes.
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio de incidentes.

        Args:
            db: Sesión asincrónica de SQLAlchemy para operaciones de base de datos
        """
        self.db = db

    # ========================================================================
    # OPERACIONES CRUD BÁSICAS
    # ========================================================================

    async def create_incident(
        self,
        incident_data: IncidentCreate,
        reporter_id: str,
        db: AsyncSession
    ) -> IncidentResponse:
        """
        Crea un nuevo incidente en el sistema.

        Valida que la aplicación exista, crea el incidente con el usuario
        actual como reportero, y opcionalmente lo asigna a otro usuario.

        Args:
            incident_data: Datos del incidente a crear
            reporter_id: ID del usuario que reporta el incidente
            db: Sesión de base de datos

        Returns:
            IncidentResponse: Incidente creado con todos sus datos

        Raises:
            ValueError: Si la aplicación no existe
        """
        # Validar que la aplicación existe
        app_query = select(Application).where(
            Application.id == incident_data.application_id
        )
        app_result = await db.execute(app_query)
        app = app_result.scalar_one_or_none()

        if not app:
            raise ValueError(
                f"Aplicación con ID {incident_data.application_id} no existe"
            )

        # Crear nuevo incidente
        incident = Incident(
            title=incident_data.title,
            description=incident_data.description,
            application_id=incident_data.application_id,
            category=incident_data.category,
            severity=incident_data.severity,
            assignee_id=incident_data.assignee_id,
            reporter_id=reporter_id,
            environment=incident_data.environment,
            steps_to_reproduce=incident_data.steps_to_reproduce,
            expected_behavior=incident_data.expected_behavior,
            actual_behavior=incident_data.actual_behavior,
            due_date=incident_data.due_date,
            priority_order=0
        )

        db.add(incident)
        await db.flush()

        # Crear notificación si se asignó inmediatamente
        if incident_data.assignee_id:
            await self._create_notification(
                user_id=incident_data.assignee_id,
                notification_type=NotificationType.INCIDENT_ASSIGNED,
                title=f"Nuevo incidente asignado: {incident.title}",
                message=f"Se te ha asignado el incidente: {incident.title}",
                related_id=incident.id,
                db=db
            )

        await db.commit()
        return await self._format_incident_response(incident, db)

    async def get_incident(
        self,
        incident_id: str,
        db: AsyncSession
    ) -> Optional[IncidentResponse]:
        """
        Obtiene un incidente específico por su ID.

        Args:
            incident_id: ID del incidente a recuperar
            db: Sesión de base de datos

        Returns:
            Optional[IncidentResponse]: Datos del incidente o None si no existe

        """
        query = select(Incident).where(
            Incident.id == incident_id
        ).options(
            joinedload(Incident.assignee),
            joinedload(Incident.reporter),
            joinedload(Incident.application),
            joinedload(Incident.comments).joinedload(IncidentComment.user)
        )

        result = await db.execute(query)
        incident = result.unique().scalar_one_or_none()

        if not incident:
            return None

        return await self._format_incident_response(incident, db)

    async def get_incidents(
        self,
        skip: int = 0,
        limit: int = 50,
        category: Optional[IncidentCategory] = None,
        severity: Optional[IncidentSeverity] = None,
        status: Optional[IncidentStatus] = None,
        assignee_id: Optional[str] = None,
        app_id: Optional[str] = None,
        search: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> IncidentListResponse:
        """
        Obtiene un listado paginado de incidentes con filtros avanzados.

        Permite filtrar por múltiples criterios y realizar búsqueda de texto
        en títulos y descripciones. Retorna estadísticas agregadas.

        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            category: Filtro opcional por categoría
            severity: Filtro opcional por severidad
            status: Filtro opcional por estado
            assignee_id: Filtro opcional por usuario asignado
            app_id: Filtro opcional por aplicación
            search: Término de búsqueda en título/descripción
            db: Sesión de base de datos

        Returns:
            IncidentListResponse: Listado paginado con estadísticas
        """
        if db is None:
            db = self.db

        # Construir consulta base
        query = select(Incident).options(
            joinedload(Incident.assignee),
            joinedload(Incident.reporter),
            joinedload(Incident.application)
        )

        # Aplicar filtros
        filters = []

        if category:
            filters.append(Incident.category == category)
        if severity:
            filters.append(Incident.severity == severity)
        if status:
            filters.append(Incident.status == status)
        if assignee_id:
            filters.append(Incident.assignee_id == assignee_id)
        if app_id:
            filters.append(Incident.application_id == app_id)
        if search:
            search_filter = or_(
                Incident.title.ilike(f"%{search}%"),
                Incident.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)

        if filters:
            query = query.where(and_(*filters))

        # Ejecutar consulta con paginación
        query = query.order_by(
            Incident.priority_order,
            Incident.created_at.desc()
        )

        result = await db.execute(query)
        incidents = result.unique().scalars().all()

        total = len(incidents)
        paginated = incidents[skip:skip + limit]

        # Formatear respuestas
        formatted_incidents = []
        for incident in paginated:
            formatted = await self._format_incident_response(incident, db)
            formatted_incidents.append(formatted)

        # Calcular estadísticas
        by_category = self._calculate_by_category(incidents)
        by_severity = self._calculate_by_severity(incidents)

        return IncidentListResponse(
            items=formatted_incidents,
            total=total,
            by_category=by_category,
            by_severity=by_severity
        )

    async def update_incident(
        self,
        incident_id: str,
        incident_data: IncidentUpdate,
        db: AsyncSession
    ) -> IncidentResponse:
        """
        Actualiza parcialmente los datos de un incidente.

        Permite actualizar campos selectivos. Registra cambios de estado
        significativos en auditoría.

        Args:
            incident_id: ID del incidente a actualizar
            incident_data: Datos a actualizar (solo campos presentes)
            db: Sesión de base de datos

        Returns:
            IncidentResponse: Incidente actualizado

        Raises:
            ValueError: Si el incidente no existe
        """
        query = select(Incident).where(Incident.id == incident_id)
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            raise ValueError(f"Incidente {incident_id} no encontrado")

        # Actualizar campos presentes
        update_data = incident_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:
                setattr(incident, field, value)

        incident.updated_at = datetime.utcnow()
        await db.commit()

        return await self._format_incident_response(incident, db)

    async def delete_incident(
        self,
        incident_id: str,
        db: AsyncSession
    ) -> bool:
        """
        Elimina un incidente del sistema.

        Operación en cascada que también elimina comentarios asociados.

        Args:
            incident_id: ID del incidente a eliminar
            db: Sesión de base de datos

        Returns:
            bool: True si fue eliminado, False si no existía
        """
        query = select(Incident).where(Incident.id == incident_id)
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            return False

        await db.delete(incident)
        await db.commit()
        return True

    # ========================================================================
    # OPERACIONES DE ASIGNACIÓN
    # ========================================================================

    async def assign_incident(
        self,
        incident_id: str,
        assignee_id: str,
        assigner_id: str,
        reason: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> IncidentResponse:
        """
        Asigna un incidente a un usuario del equipo.

        Registra la asignación y crea una notificación para el usuario asignado.

        Args:
            incident_id: ID del incidente
            assignee_id: ID del usuario a asignar
            assigner_id: ID del usuario que realiza la asignación
            reason: Razón opcional de la asignación
            db: Sesión de base de datos

        Returns:
            IncidentResponse: Incidente actualizado

        Raises:
            ValueError: Si incidente o usuario no existe
        """
        if db is None:
            db = self.db

        query = select(Incident).where(Incident.id == incident_id)
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            raise ValueError(f"Incidente {incident_id} no encontrado")

        # Validar que el usuario existe
        user_query = select(User).where(User.id == assignee_id)
        user_result = await db.execute(user_query)
        if not user_result.scalar_one_or_none():
            raise ValueError(f"Usuario {assignee_id} no encontrado")

        incident.assignee_id = assignee_id
        await db.commit()

        # Crear notificación
        await self._create_notification(
            user_id=assignee_id,
            notification_type=NotificationType.INCIDENT_ASSIGNED,
            title=f"Incidente asignado: {incident.title}",
            message=f"Se te ha asignado: {incident.title}" +
                   (f"\nRazón: {reason}" if reason else ""),
            related_id=incident.id,
            db=db
        )

        return await self._format_incident_response(incident, db)

    async def unassign_incident(
        self,
        incident_id: str,
        db: Optional[AsyncSession] = None
    ) -> IncidentResponse:
        """
        Desasigna un incidente (elimina asignación).

        Args:
            incident_id: ID del incidente
            db: Sesión de base de datos

        Returns:
            IncidentResponse: Incidente sin asignación

        Raises:
            ValueError: Si el incidente no existe
        """
        if db is None:
            db = self.db

        query = select(Incident).where(Incident.id == incident_id)
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            raise ValueError(f"Incidente {incident_id} no encontrado")

        incident.assignee_id = None
        await db.commit()

        return await self._format_incident_response(incident, db)

    # ========================================================================
    # OPERACIONES DE CAMBIO DE ESTADO
    # ========================================================================

    async def change_status(
        self,
        incident_id: str,
        new_status: IncidentStatus,
        user_id: str,
        db: Optional[AsyncSession] = None
    ) -> IncidentResponse:
        """
        Cambia el estado de un incidente.

        Actualiza timestamps relevantes según el estado (resolved_at, closed_at).
        Crea notificaciones para usuarios interesados.

        Args:
            incident_id: ID del incidente
            new_status: Nuevo estado
            user_id: ID del usuario que realiza el cambio
            db: Sesión de base de datos

        Returns:
            IncidentResponse: Incidente con nuevo estado

        Raises:
            ValueError: Si el incidente no existe
        """
        if db is None:
            db = self.db

        query = select(Incident).where(Incident.id == incident_id)
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            raise ValueError(f"Incidente {incident_id} no encontrado")

        old_status = incident.status
        incident.status = new_status

        # Actualizar timestamps según estado
        if new_status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.utcnow()
        elif new_status == IncidentStatus.CLOSED:
            incident.closed_at = datetime.utcnow()

        await db.commit()

        # Crear notificación de cambio de estado
        await self._create_notification(
            user_id=incident.reporter_id,
            notification_type=NotificationType.INCIDENT_STATUS_CHANGED,
            title=f"Cambio de estado: {incident.title}",
            message=f"Estado cambió de {old_status.value} a {new_status.value}",
            related_id=incident.id,
            db=db
        )

        # Si se asignó, notificar también al asignado
        if incident.assignee_id and incident.assignee_id != incident.reporter_id:
            await self._create_notification(
                user_id=incident.assignee_id,
                notification_type=NotificationType.INCIDENT_STATUS_CHANGED,
                title=f"Cambio de estado: {incident.title}",
                message=f"Estado cambió de {old_status.value} a {new_status.value}",
                related_id=incident.id,
                db=db
            )

        return await self._format_incident_response(incident, db)

    async def resolve_incident(
        self,
        incident_id: str,
        resolution_notes: str,
        fixed_in_version: Optional[str] = None,
        user_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> IncidentResponse:
        """
        Resuelve un incidente registrando notas y versión de corrección.

        Marca el incidente como RESOLVED con timestamp de resolución.

        Args:
            incident_id: ID del incidente
            resolution_notes: Notas técnicas de resolución
            fixed_in_version: Versión en que se corrigió (opcional)
            user_id: ID del usuario que resuelve (opcional)
            db: Sesión de base de datos

        Returns:
            IncidentResponse: Incidente resuelto

        Raises:
            ValueError: Si el incidente no existe
        """
        if db is None:
            db = self.db

        query = select(Incident).where(Incident.id == incident_id)
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            raise ValueError(f"Incidente {incident_id} no encontrado")

        incident.status = IncidentStatus.RESOLVED
        incident.resolution_notes = resolution_notes
        if fixed_in_version:
            incident.fixed_in_version = fixed_in_version
        incident.resolved_at = datetime.utcnow()

        await db.commit()

        return await self._format_incident_response(incident, db)

    # ========================================================================
    # OPERACIONES DE COMENTARIOS
    # ========================================================================

    async def add_comment(
        self,
        incident_id: str,
        user_id: str,
        content: str,
        db: Optional[AsyncSession] = None
    ) -> IncidentCommentResponse:
        """
        Agrega un comentario a un incidente.

        Args:
            incident_id: ID del incidente
            user_id: ID del usuario que comenta
            content: Contenido del comentario
            db: Sesión de base de datos

        Returns:
            IncidentCommentResponse: Comentario creado

        Raises:
            ValueError: Si el incidente no existe
        """
        if db is None:
            db = self.db

        # Validar que el incidente existe
        incident_query = select(Incident).where(Incident.id == incident_id)
        incident_result = await db.execute(incident_query)
        incident = incident_result.scalar_one_or_none()

        if not incident:
            raise ValueError(f"Incidente {incident_id} no encontrado")

        # Crear comentario
        comment = IncidentComment(
            incident_id=incident_id,
            user_id=user_id,
            content=content
        )

        db.add(comment)
        await db.commit()

        # Notificar a partes interesadas
        await self._create_notification(
            user_id=incident.reporter_id,
            notification_type=NotificationType.INCIDENT_COMMENT_ADDED,
            title=f"Nuevo comentario en: {incident.title}",
            message="Se agregó un comentario a tu incidente reportado",
            related_id=incident.id,
            db=db
        )

        # Notificar al asignado si es diferente
        if incident.assignee_id and incident.assignee_id != incident.reporter_id:
            await self._create_notification(
                user_id=incident.assignee_id,
                notification_type=NotificationType.INCIDENT_COMMENT_ADDED,
                title=f"Nuevo comentario en: {incident.title}",
                message="Se agregó un comentario al incidente asignado",
                related_id=incident.id,
                db=db
            )

        return await self._format_comment_response(comment, db)

    async def get_incident_comments(
        self,
        incident_id: str,
        db: Optional[AsyncSession] = None
    ) -> List[IncidentCommentResponse]:
        """
        Obtiene todos los comentarios de un incidente.

        Ordenados cronológicamente del más antiguo al más reciente.

        Args:
            incident_id: ID del incidente
            db: Sesión de base de datos

        Returns:
            List[IncidentCommentResponse]: Lista de comentarios
        """
        if db is None:
            db = self.db

        query = select(IncidentComment).where(
            IncidentComment.incident_id == incident_id
        ).options(
            joinedload(IncidentComment.user)
        ).order_by(IncidentComment.created_at.asc())

        result = await db.execute(query)
        comments = result.unique().scalars().all()

        formatted = []
        for comment in comments:
            formatted_comment = await self._format_comment_response(comment, db)
            formatted.append(formatted_comment)

        return formatted

    # ========================================================================
    # OPERACIONES DE PRIORIDAD
    # ========================================================================

    async def update_priority(
        self,
        incident_id: str,
        new_priority_order: int,
        db: Optional[AsyncSession] = None
    ) -> IncidentResponse:
        """
        Actualiza el orden de prioridad de un incidente.

        Útil para operaciones de drag-and-drop en interfaz.

        Args:
            incident_id: ID del incidente
            new_priority_order: Nuevo valor de priority_order
            db: Sesión de base de datos

        Returns:
            IncidentResponse: Incidente con prioridad actualizada

        Raises:
            ValueError: Si el incidente no existe
        """
        if db is None:
            db = self.db

        query = select(Incident).where(Incident.id == incident_id)
        result = await db.execute(query)
        incident = result.scalar_one_or_none()

        if not incident:
            raise ValueError(f"Incidente {incident_id} no encontrado")

        incident.priority_order = new_priority_order
        await db.commit()

        return await self._format_incident_response(incident, db)

    async def reorder_priorities(
        self,
        updates: List[PriorityUpdateRequest],
        db: Optional[AsyncSession] = None
    ) -> int:
        """
        Actualiza prioridades de múltiples incidentes en lote.

        Operación atómica para actualizar múltiples priority_order.

        Args:
            updates: Lista de actualizaciones (incident_id, new_priority_order)
            db: Sesión de base de datos

        Returns:
            int: Número de incidentes actualizados
        """
        if db is None:
            db = self.db

        updated_count = 0

        for update in updates:
            query = select(Incident).where(
                Incident.id == update.incident_id
            )
            result = await db.execute(query)
            incident = result.scalar_one_or_none()

            if incident:
                incident.priority_order = update.new_priority_order
                updated_count += 1

        if updated_count > 0:
            await db.commit()

        return updated_count

    # ========================================================================
    # OPERACIONES DE AGRUPACIÓN Y ESTADÍSTICAS
    # ========================================================================

    async def get_incidents_grouped_by_category(
        self,
        app_id: str,
        db: Optional[AsyncSession] = None
    ) -> List[ByCategoryResponse]:
        """
        Obtiene incidentes de una aplicación agrupados por categoría.

        Ordena por priority_order dentro de cada categoría.

        Args:
            app_id: ID de la aplicación
            db: Sesión de base de datos

        Returns:
            List[ByCategoryResponse]: Incidentes agrupados por categoría
        """
        if db is None:
            db = self.db

        query = select(Incident).where(
            Incident.application_id == app_id
        ).options(
            joinedload(Incident.assignee),
            joinedload(Incident.reporter),
            joinedload(Incident.application)
        ).order_by(
            Incident.category,
            Incident.priority_order
        )

        result = await db.execute(query)
        incidents = result.unique().scalars().all()

        # Agrupar por categoría
        grouped: Dict[IncidentCategory, List] = {}
        for incident in incidents:
            if incident.category not in grouped:
                grouped[incident.category] = []
            grouped[incident.category].append(incident)

        # Formatear respuesta
        response = []
        for category, category_incidents in grouped.items():
            formatted_incidents = []
            for incident in category_incidents:
                formatted = await self._format_incident_response(incident, db)
                formatted_incidents.append(formatted)

            response.append(ByCategoryResponse(
                category=category,
                count=len(formatted_incidents),
                incidents=formatted_incidents
            ))

        return response

    async def get_incidents_by_team(
        self,
        db: Optional[AsyncSession] = None
    ) -> List[IncidentsByTeamResponse]:
        """
        Obtiene incidentes agrupados por usuario asignado (equipo).

        Útil para análisis de carga de trabajo.

        Args:
            db: Sesión de base de datos

        Returns:
            List[IncidentsByTeamResponse]: Incidentes por miembro del equipo
        """
        if db is None:
            db = self.db

        # Obtener todos los incidentes con asignación
        query = select(Incident).where(
            Incident.assignee_id != None
        ).options(
            joinedload(Incident.assignee),
            joinedload(Incident.reporter),
            joinedload(Incident.application)
        ).order_by(
            Incident.assignee_id,
            Incident.priority_order
        )

        result = await db.execute(query)
        incidents = result.unique().scalars().all()

        # Agrupar por asignado
        grouped: Dict[str, List] = {}
        for incident in incidents:
            if incident.assignee_id not in grouped:
                grouped[incident.assignee_id] = []
            grouped[incident.assignee_id].append(incident)

        # Formatear respuesta
        response = []
        for assignee_id, assignee_incidents in grouped.items():
            # Obtener datos del usuario
            user_query = select(User).where(User.id == assignee_id)
            user_result = await db.execute(user_query)
            assignee = user_result.scalar_one_or_none()

            if not assignee:
                continue

            formatted_incidents = []
            by_severity: Dict[str, int] = {}
            open_count = 0
            in_progress_count = 0

            for incident in assignee_incidents:
                formatted = await self._format_incident_response(incident, db)
                formatted_incidents.append(formatted)

                # Contabilizar
                severity_key = incident.severity.value
                by_severity[severity_key] = by_severity.get(severity_key, 0) + 1

                if incident.status == IncidentStatus.OPEN:
                    open_count += 1
                elif incident.status == IncidentStatus.IN_PROGRESS:
                    in_progress_count += 1

            response.append(IncidentsByTeamResponse(
                assignee_id=assignee_id,
                assignee_name=assignee.full_name,
                total_assigned=len(formatted_incidents),
                open_count=open_count,
                in_progress_count=in_progress_count,
                by_severity=by_severity,
                incidents=formatted_incidents
            ))

        return response

    async def get_user_incidents(
        self,
        user_id: str,
        db: Optional[AsyncSession] = None
    ) -> IncidentListResponse:
        """
        Obtiene incidentes del usuario (reportados y asignados).

        Args:
            user_id: ID del usuario
            db: Sesión de base de datos

        Returns:
            IncidentListResponse: Incidentes del usuario
        """
        if db is None:
            db = self.db

        query = select(Incident).where(
            or_(
                Incident.reporter_id == user_id,
                Incident.assignee_id == user_id
            )
        ).options(
            joinedload(Incident.assignee),
            joinedload(Incident.reporter),
            joinedload(Incident.application)
        ).order_by(
            Incident.priority_order,
            Incident.created_at.desc()
        )

        result = await db.execute(query)
        incidents = result.unique().scalars().all()

        formatted_incidents = []
        for incident in incidents:
            formatted = await self._format_incident_response(incident, db)
            formatted_incidents.append(formatted)

        by_category = self._calculate_by_category(incidents)
        by_severity = self._calculate_by_severity(incidents)

        return IncidentListResponse(
            items=formatted_incidents,
            total=len(incidents),
            by_category=by_category,
            by_severity=by_severity
        )

    async def get_dashboard_stats(
        self,
        db: Optional[AsyncSession] = None
    ) -> DashboardStats:
        """
        Calcula estadísticas agregadas del sistema de incidentes.

        Proporciona métricas de alto nivel para monitoreo de salud.

        Args:
            db: Sesión de base de datos

        Returns:
            DashboardStats: Estadísticas del dashboard
        """
        if db is None:
            db = self.db

        # Obtener todos los incidentes
        query = select(Incident)
        result = await db.execute(query)
        all_incidents = result.scalars().all()

        # Contabilizar por estado
        by_status = {}
        by_severity = {}
        by_category = {}

        open_incidents = 0
        in_progress_incidents = 0
        resolved_incidents = 0
        overdue_count = 0
        critical_unresolved = 0

        total_resolution_days = 0
        resolved_count = 0

        for incident in all_incidents:
            # Por estado
            status_key = incident.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

            # Por severidad
            severity_key = incident.severity.value
            by_severity[severity_key] = by_severity.get(severity_key, 0) + 1

            # Por categoría
            category_key = incident.category.value
            by_category[category_key] = by_category.get(category_key, 0) + 1

            # Contadores específicos
            if incident.status == IncidentStatus.OPEN:
                open_incidents += 1
            elif incident.status == IncidentStatus.IN_PROGRESS:
                in_progress_incidents += 1
            elif incident.status == IncidentStatus.RESOLVED:
                resolved_incidents += 1

            # Vencidos
            if incident.is_overdue():
                overdue_count += 1

            # Críticos sin resolver
            if (incident.severity == IncidentSeverity.CRITICAL and
                incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]):
                critical_unresolved += 1

            # Promedio de resolución
            if incident.resolved_at:
                resolution_days = (incident.resolved_at - incident.created_at).days
                total_resolution_days += resolution_days
                resolved_count += 1

        avg_resolution_time = None
        if resolved_count > 0:
            avg_resolution_time = total_resolution_days / resolved_count

        return DashboardStats(
            total_incidents=len(all_incidents),
            open_incidents=open_incidents,
            in_progress_incidents=in_progress_incidents,
            resolved_incidents=resolved_incidents,
            by_status=by_status,
            by_severity=by_severity,
            by_category=by_category,
            avg_resolution_time_days=avg_resolution_time,
            overdue_count=overdue_count,
            critical_unresolved=critical_unresolved
        )

    # ========================================================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ========================================================================

    async def _format_incident_response(
        self,
        incident: Incident,
        db: AsyncSession
    ) -> IncidentResponse:
        """
        Formatea un modelo Incident a esquema IncidentResponse.

        Calcula campos derivados como comment_count, days_open, is_overdue.
        Obtiene nombres de aplicación y datos de usuarios.

        Args:
            incident: Modelo de incidente
            db: Sesión de base de datos

        Returns:
            IncidentResponse: Esquema formateado
        """
        assignee_response = None
        if incident.assignee:
            assignee_response = UserResponse(
                id=incident.assignee.id,
                email=incident.assignee.email,
                full_name=incident.assignee.full_name,
                avatar_url=getattr(incident.assignee, "avatar_url", None)
            )

        reporter_response = UserResponse(
            id=incident.reporter.id,
            email=incident.reporter.email,
            full_name=incident.reporter.full_name,
            avatar_url=getattr(incident.reporter, "avatar_url", None)
        )

        # Contar comentarios
        comment_count = len(incident.comments) if incident.comments else 0

        return IncidentResponse(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            application_id=incident.application_id,
            application_name=incident.application.name if incident.application else "N/A",
            category=incident.category,
            status=incident.status,
            severity=incident.severity,
            priority_order=incident.priority_order,
            assignee=assignee_response,
            reporter=reporter_response,
            resolution_notes=incident.resolution_notes,
            environment=incident.environment,
            steps_to_reproduce=incident.steps_to_reproduce,
            expected_behavior=incident.expected_behavior,
            actual_behavior=incident.actual_behavior,
            affected_version=incident.affected_version,
            fixed_in_version=incident.fixed_in_version,
            due_date=incident.due_date,
            resolved_at=incident.resolved_at,
            closed_at=incident.closed_at,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
            comment_count=comment_count,
            days_open=incident.days_open(),
            is_overdue=incident.is_overdue()
        )

    async def _format_comment_response(
        self,
        comment: IncidentComment,
        db: AsyncSession
    ) -> IncidentCommentResponse:
        """
        Formatea un modelo IncidentComment a esquema IncidentCommentResponse.

        Args:
            comment: Modelo de comentario
            db: Sesión de base de datos

        Returns:
            IncidentCommentResponse: Esquema formateado
        """
        user_response = UserResponse(
            id=comment.user.id,
            email=comment.user.email,
            full_name=comment.user.full_name,
            avatar_url=getattr(comment.user, "avatar_url", None)
        )

        return IncidentCommentResponse(
            id=comment.id,
            incident_id=comment.incident_id,
            user=user_response,
            content=comment.content,
            created_at=comment.created_at
        )

    def _calculate_by_category(
        self,
        incidents: List[Incident]
    ) -> Dict[str, int]:
        """
        Calcula conteo de incidentes por categoría.

        Args:
            incidents: Lista de incidentes

        Returns:
            Dict[str, int]: Diccionario con conteos por categoría
        """
        result = {}
        for incident in incidents:
            key = incident.category.value
            result[key] = result.get(key, 0) + 1
        return result

    def _calculate_by_severity(
        self,
        incidents: List[Incident]
    ) -> Dict[str, int]:
        """
        Calcula conteo de incidentes por severidad.

        Args:
            incidents: Lista de incidentes

        Returns:
            Dict[str, int]: Diccionario con conteos por severidad
        """
        result = {}
        for incident in incidents:
            key = incident.severity.value
            result[key] = result.get(key, 0) + 1
        return result

    async def _create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        related_id: str,
        db: AsyncSession
    ) -> None:
        """
        Crea una notificación para un usuario.

        Integración con el sistema de notificaciones de CoreStream.

        Args:
            user_id: ID del usuario destinatario
            notification_type: Tipo de notificación
            title: Título de la notificación
            message: Mensaje de la notificación
            related_id: ID del incidente relacionado
            db: Sesión de base de datos
        """
        try:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                related_id=related_id
            )
            db.add(notification)
            await db.flush()
        except Exception:
            # No fallar operación principal si hay error en notificación
            pass
