from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import Application, Document, Epic, Team, Ticket, User
from app.models.incident import Incident
from app.models.user import UserRole

router = APIRouter(prefix="/search", tags=["Search"])


def _result_item(resource_type: str, item: Any, title_field: str = "title", subtitle_field: str | None = None, link: str | None = None) -> dict[str, Any]:
    title = getattr(item, title_field, str(item))
    subtitle = getattr(item, subtitle_field, None) if subtitle_field else None
    return {
        "type": resource_type,
        "id": str(getattr(item, "id", "")),
        "title": str(title),
        "subtitle": str(subtitle) if subtitle is not None else None,
        "link": link or f"/{resource_type}/{getattr(item, 'id', '')}",
    }


@router.get("/", summary="Búsqueda global unificada", description="Busca tickets, incidentes, proyectos, documentos y usuarios con permisos aplicados.")
async def global_search(
    q: str = Query(..., min_length=1, description="Texto a buscar"),
    limit: int = Query(10, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    term = q.strip()
    if not term:
        return {"tickets": [], "incidents": [], "projects": [], "documents": [], "users": []}

    role_name = getattr(getattr(current_user, "role", None), "value", getattr(current_user, "role", None))
    is_admin = str(role_name or "").upper() == "ADMIN"
    # `get_current_user` devuelve un TokenPayload (sub, role, exp) que NO tiene
    # email ni id, así que hay que cargar el usuario real desde la DB.
    try:
        current_user_uuid = UUID(str(current_user.sub))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido: subject inválido")
    db_user = (
        await db.execute(select(User).where(User.id == current_user_uuid))
    ).scalar_one_or_none()
    if db_user is None:
        raise HTTPException(status_code=401, detail="Token inválido: usuario no encontrado")

    team_rows = [] if is_admin else (await db.execute(select(Team))).scalars().all()
    user_email = str(db_user.email or "").strip().lower()
    user_teams = [
        team for team in team_rows
        if user_email in {str(email).strip().lower() for email in (team.member_emails or [])}
    ]
    authorized_application_ids: set[UUID] = set()
    for team in user_teams:
        for application_id in team.application_ids or []:
            try:
                authorized_application_ids.add(UUID(str(application_id)))
            except (TypeError, ValueError):
                continue
    owned_application_ids = (
        await db.execute(select(Application.id).where(Application.owner_id == db_user.id))
    ).scalars().all() if not is_admin else []
    authorized_application_ids.update(owned_application_ids)
    authorized_user_emails = {user_email}
    for team in user_teams:
        authorized_user_emails.update(
            str(email).strip().lower() for email in (team.member_emails or [])
        )

    results: dict[str, list[dict[str, Any]]] = {
        "tickets": [],
        "incidents": [],
        "projects": [],
        "documents": [],
        "users": [],
    }

    ticket_query = select(Ticket).options(
        selectinload(Ticket.assignee),
        selectinload(Ticket.epic),
    ).where(
        or_(
            Ticket.title.ilike(f"%{term}%"),
            Ticket.description.ilike(f"%{term}%"),
        )
    )
    if not is_admin:
        ticket_query = ticket_query.join(Ticket.epic).where(
            Epic.application_id.in_(authorized_application_ids)
        )
        if str(role_name or "").upper() == "DEVELOPER":
            ticket_query = ticket_query.where(Ticket.assignee_id == db_user.id)
    ticket_rows = (await db.execute(ticket_query.limit(limit))).scalars().all()
    results["tickets"] = [
        _result_item("ticket", ticket, title_field="title", subtitle_field="description", link=f"/tickets/{ticket.id}")
        for ticket in ticket_rows
    ]

    incident_query = select(Incident).where(
        or_(Incident.title.ilike(f"%{term}%"), Incident.description.ilike(f"%{term}%"))
    )
    if not is_admin:
        incident_query = incident_query.where(Incident.assignee_id == str(db_user.id))
    incident_rows = (await db.execute(incident_query.limit(limit))).scalars().all()
    results["incidents"] = [
        _result_item("incident", incident, title_field="title", subtitle_field="description", link=f"/incidents/{incident.id}")
        for incident in incident_rows
    ]

    project_query = select(Application).where(Application.name.ilike(f"%{term}%"))
    if not is_admin:
        project_query = project_query.where(
            Application.is_active.is_(True),
            Application.id.in_(authorized_application_ids),
        )
    project_rows = (await db.execute(project_query.limit(limit))).scalars().all()
    results["projects"] = [
        _result_item("project", project, title_field="name", subtitle_field="description", link=f"/applications/{project.id}")
        for project in project_rows
    ]

    document_query = select(Document).where(Document.filename.ilike(f"%{term}%"))
    if not is_admin:
        document_query = document_query.where(Document.uploaded_by_id == db_user.id)
    document_rows = (await db.execute(document_query.limit(limit))).scalars().all()
    results["documents"] = [
        _result_item("document", document, title_field="filename", subtitle_field="mime_type", link=f"/documents/{document.id}")
        for document in document_rows
    ]

    user_query = select(User).where(
        or_(
            User.full_name.ilike(f"%{term}%"),
            User.email.ilike(f"%{term}%"),
        )
    )
    if not is_admin:
        user_query = user_query.where(User.email.in_(authorized_user_emails))
    user_rows = (await db.execute(user_query.limit(limit))).scalars().all()
    results["users"] = [
        _result_item("user", user, title_field="full_name", subtitle_field="email", link=f"/users/{user.id}")
        for user in user_rows
    ]

    return results
