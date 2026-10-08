"""Servicio de incidentes: CRUD, estados, comentarios y agregados.

El router `app/routers/incidents.py` delega aquí todas las operaciones.
Todos los métodos reciben la sesión `db` explícitamente (así lo llama el router).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Sequence

from fastapi import HTTPException, status as http_status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.incident import (
    Incident,
    IncidentCategory,
    IncidentComment,
    IncidentSeverity,
    IncidentStatus,
)
from app.models.user import User
from app.schemas.incident import (
    ByCategoryResponse,
    DashboardStats,
    IncidentCommentResponse,
    IncidentCreate,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdate,
    IncidentsByTeamResponse,
    PriorityUpdateRequest,
)

# Relaciones necesarias para serializar sin lazy-load (evita MissingGreenlet)
_LOAD = (
    selectinload(Incident.assignee),
    selectinload(Incident.reporter),
    selectinload(Incident.application),
)

_CLOSED_STATUSES = (IncidentStatus.RESOLVED, IncidentStatus.CLOSED)


def _user_payload(user: Optional[User]) -> Optional[Dict[str, Any]]:
    if user is None:
        return None
    return {"id": str(user.id), "email": user.email, "full_name": user.full_name, "avatar_url": user.avatar_url}


def _key(value: Any) -> str:
    return str(value.value if hasattr(value, "value") else value)


class IncidentService:
    """Operaciones de dominio para los tickets de incidente."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get(self, incident_id: str, db: AsyncSession) -> Optional[Incident]:
        result = await db.execute(
            select(Incident).options(*_LOAD).where(Incident.id == str(incident_id))
        )
        return result.scalar_one_or_none()

    async def _require(self, incident_id: str, db: AsyncSession) -> Incident:
        incident = await self._get(incident_id, db)
        if incident is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Incidente con ID {incident_id} no encontrado",
            )
        return incident

    @staticmethod
    def _response(incident: Incident, comment_count: Optional[int] = None) -> IncidentResponse:
        return IncidentResponse.model_validate(
            {
                "id": str(incident.id),
                "title": incident.title,
                "description": incident.description,
                "application_id": str(incident.application_id),
                "application_name": incident.application.name if incident.application else "",
                "category": incident.category,
                "status": incident.status,
                "severity": incident.severity,
                "priority_order": incident.priority_order,
                "assignee": _user_payload(incident.assignee),
                "reporter": _user_payload(incident.reporter),
                "resolution_notes": incident.resolution_notes,
                "environment": incident.environment,
                "steps_to_reproduce": incident.steps_to_reproduce,
                "expected_behavior": incident.expected_behavior,
                "actual_behavior": incident.actual_behavior,
                "affected_version": incident.affected_version,
                "fixed_in_version": incident.fixed_in_version,
                "due_date": incident.due_date,
                "resolved_at": incident.resolved_at,
                "closed_at": incident.closed_at,
                "created_at": incident.created_at,
                "updated_at": incident.updated_at,
                "comment_count": comment_count
                if comment_count is not None
                else len(incident.comments or []),
                "days_open": incident.days_open(),
                "is_overdue": incident.is_overdue(),
            }
        )

    @staticmethod
    def _filters(
        category: Optional[IncidentCategory] = None,
        severity: Optional[IncidentSeverity] = None,
        status_: Optional[IncidentStatus] = None,
        assignee_id: Optional[str] = None,
        app_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Any]:
        criteria: List[Any] = []
        if category is not None:
            criteria.append(Incident.category == category)
        if severity is not None:
            criteria.append(Incident.severity == severity)
        if status_ is not None:
            criteria.append(Incident.status == status_)
        if assignee_id:
            criteria.append(Incident.assignee_id == str(assignee_id))
        if app_id:
            criteria.append(Incident.application_id == str(app_id))
        if search:
            term = f"%{search.strip()}%"
            criteria.append(or_(Incident.title.ilike(term), Incident.description.ilike(term)))
        return criteria

    async def _list(
        self,
        criteria: Sequence[Any],
        db: AsyncSession,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> IncidentListResponse:
        total = (
            await db.execute(select(func.count()).select_from(Incident).where(*criteria))
        ).scalar() or 0

        cat_rows = (
            await db.execute(
                select(Incident.category, func.count())
                .select_from(Incident)
                .where(*criteria)
                .group_by(Incident.category)
            )
        ).all()
        sev_rows = (
            await db.execute(
                select(Incident.severity, func.count())
                .select_from(Incident)
                .where(*criteria)
                .group_by(Incident.severity)
            )
        ).all()

        query = (
            select(Incident)
            .options(*_LOAD)
            .where(*criteria)
            .order_by(Incident.priority_order, Incident.created_at)
        )
        if skip:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
        rows = (await db.execute(query)).scalars().unique().all()

        return IncidentListResponse(
            items=[self._response(incident) for incident in rows],
            total=total,
            by_category={_key(key): value for key, value in cat_rows},
            by_severity={_key(key): value for key, value in sev_rows},
        )

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #
    async def create_incident(
        self,
        incident_data: IncidentCreate,
        reporter_id: Any,
        db: AsyncSession,
    ) -> IncidentResponse:
        application = (
            await db.execute(
                select(Application).where(Application.id == str(incident_data.application_id))
            )
        ).scalar_one_or_none()
        if application is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Aplicación con ID {incident_data.application_id} no encontrada",
            )

        if incident_data.assignee_id:
            assignee = (
                await db.execute(select(User).where(User.id == str(incident_data.assignee_id)))
            ).scalar_one_or_none()
            if assignee is None:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"Usuario asignado con ID {incident_data.assignee_id} no encontrado",
                )

        incident = Incident(
            title=incident_data.title,
            description=incident_data.description,
            application_id=str(incident_data.application_id),
            category=incident_data.category,
            severity=incident_data.severity,
            assignee_id=str(incident_data.assignee_id) if incident_data.assignee_id else None,
            reporter_id=str(reporter_id),
            due_date=incident_data.due_date,
            environment=incident_data.environment,
            steps_to_reproduce=incident_data.steps_to_reproduce,
            expected_behavior=incident_data.expected_behavior,
            actual_behavior=incident_data.actual_behavior,
            status=IncidentStatus.OPEN,
        )
        db.add(incident)
        await db.commit()

        created = await self._require(incident.id, db)
        return self._response(created)

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
        db: Optional[AsyncSession] = None,
    ) -> IncidentListResponse:
        session = db or self.db
        criteria = self._filters(category, severity, status, assignee_id, app_id, search)
        return await self._list(criteria, session, skip=skip, limit=limit)

    async def get_incident(self, incident_id: str, db: AsyncSession) -> Optional[IncidentResponse]:
        incident = await self._get(incident_id, db)
        return self._response(incident) if incident else None

    async def update_incident(
        self,
        incident_id: str,
        incident_data: IncidentUpdate,
        db: AsyncSession,
    ) -> IncidentResponse:
        incident = await self._require(incident_id, db)
        payload = incident_data.model_dump(exclude_unset=True)
        for field, value in payload.items():
            setattr(incident, field, value)
        if incident.status in _CLOSED_STATUSES and incident.resolved_at is None:
            incident.resolved_at = datetime.utcnow()
        await db.commit()

        updated = await self._require(incident_id, db)
        return self._response(updated)

    async def delete_incident(self, incident_id: str, db: AsyncSession) -> bool:
        incident = await self._get(incident_id, db)
        if incident is None:
            return False
        await db.delete(incident)
        await db.commit()
        return True

    # ------------------------------------------------------------------ #
    # Asignación y estados
    # ------------------------------------------------------------------ #
    async def assign_incident(
        self,
        incident_id: str,
        assignee_id: str,
        assigner_id: Any,
        reason: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> IncidentResponse:
        session = db or self.db
        incident = await self._require(incident_id, session)
        assignee = (
            await session.execute(select(User).where(User.id == str(assignee_id)))
        ).scalar_one_or_none()
        if assignee is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {assignee_id} no encontrado",
            )
        incident.assignee_id = str(assignee_id)
        if incident.status == IncidentStatus.OPEN:
            incident.status = IncidentStatus.IN_PROGRESS
        await session.commit()

        updated = await self._require(incident_id, session)
        return self._response(updated)

    async def unassign_incident(self, incident_id: str, db: AsyncSession) -> IncidentResponse:
        incident = await self._require(incident_id, db)
        incident.assignee_id = None
        await db.commit()

        updated = await self._require(incident_id, db)
        return self._response(updated)

    async def change_status(
        self,
        incident_id: str,
        new_status: IncidentStatus,
        user_id: Any,
        db: AsyncSession,
    ) -> IncidentResponse:
        incident = await self._require(incident_id, db)
        incident.status = new_status
        now = datetime.utcnow()
        if new_status == IncidentStatus.RESOLVED:
            incident.resolved_at = now
        elif new_status == IncidentStatus.CLOSED:
            incident.closed_at = incident.closed_at or now
            incident.resolved_at = incident.resolved_at or now
        elif new_status == IncidentStatus.REOPENED:
            incident.resolved_at = None
            incident.closed_at = None
        await db.commit()

        updated = await self._require(incident_id, db)
        return self._response(updated)

    async def resolve_incident(
        self,
        incident_id: str,
        resolution_notes: str,
        fixed_in_version: Optional[str],
        user_id: Any,
        db: AsyncSession,
    ) -> IncidentResponse:
        incident = await self._require(incident_id, db)
        incident.status = IncidentStatus.RESOLVED
        incident.resolution_notes = resolution_notes
        if fixed_in_version:
            incident.fixed_in_version = fixed_in_version
        incident.resolved_at = datetime.utcnow()
        await db.commit()

        updated = await self._require(incident_id, db)
        return self._response(updated)

    async def update_priority(
        self,
        incident_id: str,
        new_priority_order: int,
        db: AsyncSession,
    ) -> IncidentResponse:
        incident = await self._require(incident_id, db)
        incident.priority_order = new_priority_order
        await db.commit()

        updated = await self._require(incident_id, db)
        return self._response(updated)

    async def reorder_priorities(
        self,
        updates: List[PriorityUpdateRequest],
        db: AsyncSession,
    ) -> int:
        count = 0
        for update in updates:
            incident = (
                await db.execute(
                    select(Incident).where(Incident.id == str(update.incident_id))
                )
            ).scalar_one_or_none()
            if incident is None:
                continue
            incident.priority_order = update.new_priority_order
            count += 1
        await db.commit()
        return count

    # ------------------------------------------------------------------ #
    # Comentarios
    # ------------------------------------------------------------------ #
    async def get_incident_comments(
        self, incident_id: str, db: AsyncSession
    ) -> List[IncidentCommentResponse]:
        rows = (
            await db.execute(
                select(IncidentComment)
                .options(selectinload(IncidentComment.user))
                .where(IncidentComment.incident_id == str(incident_id))
                .order_by(IncidentComment.created_at)
            )
        ).scalars().all()
        return [
            IncidentCommentResponse.model_validate(
                {
                    "id": str(comment.id),
                    "incident_id": str(comment.incident_id),
                    "user": _user_payload(comment.user),
                    "content": comment.content,
                    "created_at": comment.created_at,
                }
            )
            for comment in rows
        ]

    async def add_comment(
        self,
        incident_id: str,
        user_id: Any,
        content: str,
        db: AsyncSession,
    ) -> IncidentCommentResponse:
        comment = IncidentComment(
            incident_id=str(incident_id),
            user_id=str(user_id),
            content=content,
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)

        user = (
            await db.execute(select(User).where(User.id == str(user_id)))
        ).scalar_one_or_none()
        return IncidentCommentResponse.model_validate(
            {
                "id": str(comment.id),
                "incident_id": str(comment.incident_id),
                "user": _user_payload(user),
                "content": comment.content,
                "created_at": comment.created_at,
            }
        )

    # ------------------------------------------------------------------ #
    # Vistas y agregados
    # ------------------------------------------------------------------ #
    async def get_user_incidents(self, user_id: Any, db: AsyncSession) -> IncidentListResponse:
        criteria = [
            or_(
                Incident.reporter_id == str(user_id),
                Incident.assignee_id == str(user_id),
            )
        ]
        return await self._list(criteria, db)

    async def get_incidents_grouped_by_category(
        self, app_id: str, db: AsyncSession
    ) -> List[ByCategoryResponse]:
        rows = (
            await db.execute(
                select(Incident)
                .options(*_LOAD)
                .where(Incident.application_id == str(app_id))
                .order_by(Incident.priority_order, Incident.created_at)
            )
        ).scalars().unique().all()

        grouped: Dict[IncidentCategory, List[Incident]] = {}
        for incident in rows:
            grouped.setdefault(incident.category, []).append(incident)

        return [
            ByCategoryResponse(
                category=category,
                count=len(incidents),
                incidents=[self._response(incident) for incident in incidents],
            )
            for category, incidents in grouped.items()
        ]

    async def get_incidents_by_team(self, db: AsyncSession) -> List[IncidentsByTeamResponse]:
        rows = (
            await db.execute(
                select(Incident)
                .options(*_LOAD)
                .where(Incident.assignee_id.is_not(None))
                .order_by(Incident.priority_order, Incident.created_at)
            )
        ).scalars().unique().all()

        grouped: Dict[str, List[Incident]] = {}
        for incident in rows:
            grouped.setdefault(str(incident.assignee_id), []).append(incident)

        responses: List[IncidentsByTeamResponse] = []
        for assignee_id, incidents in grouped.items():
            severities: Dict[str, int] = {}
            for incident in incidents:
                key = _key(incident.severity)
                severities[key] = severities.get(key, 0) + 1
            assignee = incidents[0].assignee
            responses.append(
                IncidentsByTeamResponse(
                    assignee_id=assignee_id,
                    assignee_name=assignee.full_name if assignee else "Sin asignar",
                    total_assigned=len(incidents),
                    open_count=sum(
                        1
                        for incident in incidents
                        if incident.status in (IncidentStatus.OPEN, IncidentStatus.REOPENED)
                    ),
                    in_progress_count=sum(
                        1
                        for incident in incidents
                        if incident.status == IncidentStatus.IN_PROGRESS
                    ),
                    by_severity=severities,
                    incidents=[self._response(incident) for incident in incidents],
                )
            )
        return responses

    async def get_dashboard_stats(self, db: AsyncSession) -> DashboardStats:
        status_rows = (
            await db.execute(select(Incident.status, func.count()).group_by(Incident.status))
        ).all()
        severity_rows = (
            await db.execute(select(Incident.severity, func.count()).group_by(Incident.severity))
        ).all()
        category_rows = (
            await db.execute(select(Incident.category, func.count()).group_by(Incident.category))
        ).all()

        by_status = {_key(key): value for key, value in status_rows}
        by_severity = {_key(key): value for key, value in severity_rows}
        by_category = {_key(key): value for key, value in category_rows}

        pending_rows = (
            await db.execute(
                select(
                    Incident.created_at,
                    Incident.resolved_at,
                    Incident.due_date,
                    Incident.severity,
                    Incident.status,
                )
            )
        ).all()

        resolutions = [
            (resolved_at - created_at).total_seconds() / 86400
            for created_at, resolved_at, _, _, _ in pending_rows
            if resolved_at is not None
        ]
        today = date.today()
        overdue_count = sum(
            1
            for _, _, due_date, _, status in pending_rows
            if due_date is not None and due_date < today and status not in _CLOSED_STATUSES
        )
        critical_unresolved = sum(
            1
            for _, _, _, severity, status in pending_rows
            if severity == IncidentSeverity.CRITICAL and status not in _CLOSED_STATUSES
        )

        return DashboardStats(
            total_incidents=sum(by_status.values()),
            open_incidents=by_status.get("OPEN", 0) + by_status.get("REOPENED", 0),
            in_progress_incidents=by_status.get("IN_PROGRESS", 0),
            resolved_incidents=by_status.get("RESOLVED", 0) + by_status.get("CLOSED", 0),
            by_status=by_status,
            by_severity=by_severity,
            by_category=by_category,
            avg_resolution_time_days=(
                round(sum(resolutions) / len(resolutions), 2) if resolutions else None
            ),
            overdue_count=overdue_count,
            critical_unresolved=critical_unresolved,
        )



