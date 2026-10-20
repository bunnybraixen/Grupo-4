"""Endpoints para adjuntar archivos a tickets y épicas."""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import Application, Document, DocumentType, Epic, Team, Ticket, User
from app.schemas import DocumentResponse

router = APIRouter(prefix="/documents", tags=["Documentos"])
logger = logging.getLogger("corestream.documents")
UPLOAD_DIR = Path(get_settings().UPLOAD_DIR) / "documents"
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".cs", ".rb", ".go", ".rs",
    ".php", ".swift", ".kt", ".scala",
    ".md", ".pdf", ".docx", ".txt", ".rst", ".doc",
    ".json", ".yaml", ".yml", ".xml", ".sql", ".csv", ".toml",
}


def _normalize_role(value: str | Enum | None) -> str:
    if value is None:
        return ""
    if isinstance(value, Enum):
        value = value.value
    role_name = str(value).strip().upper().replace("USERROLE.", "")
    return role_name.replace("-", "_")


async def _leader_app_ids(db: AsyncSession, user_uuid: UUID) -> set[UUID]:
    """Aplicaciones de un líder: las de sus equipos más las que posee."""
    team_rows = (await db.execute(select(Team))).scalars().all()
    user_email = (await db.execute(select(User.email).where(User.id == user_uuid))).scalar_one_or_none()
    user_email_l = (user_email or "").strip().lower()
    app_ids: set[UUID] = set()
    for team in team_rows:
        if user_email_l in {str(email).strip().lower() for email in (team.member_emails or [])}:
            for app_id in team.application_ids or []:
                try:
                    app_ids.add(UUID(str(app_id)))
                except (TypeError, ValueError):
                    continue
    owned_apps = (await db.execute(select(Application.id).where(Application.owner_id == user_uuid))).scalars().all()
    app_ids.update(owned_apps)
    return app_ids


def _stored_path(document: Document) -> Path | None:
    """
    Ruta del archivo en disco, solo si está dentro de UPLOAD_DIR.

    Defensa en profundidad: `file_path` viene de la BD y una fila manipulada
    (como permitía el antiguo POST /epics/{id}/documents) no debe poder hacer
    que se sirva o se borre un archivo arbitrario del servidor.
    """
    path = Path(document.file_path).resolve()
    if not path.is_relative_to(UPLOAD_DIR.resolve()):
        logger.warning("Documento %s apunta fuera de UPLOAD_DIR", document.id)
        return None
    return path


async def _can_access_document(db: AsyncSession, current_user, document: Document) -> bool:
    role = _normalize_role(getattr(current_user, "role", None))
    user_uuid = UUID(str(current_user.sub))

    if role == "ADMIN":
        return True

    if document.ticket_id is not None:
        ticket = (await db.execute(select(Ticket).where(Ticket.id == document.ticket_id))).scalar_one_or_none()
        if ticket is None:
            return False

        if role in {"GROUP_LEADER", "TEAM_LEADER"}:
            epic = (await db.execute(select(Epic).where(Epic.id == ticket.epic_id))).scalar_one_or_none()
            if epic is None:
                return False
            return epic.application_id in await _leader_app_ids(db, user_uuid)

        if role == "DEVELOPER":
            return ticket.assignee_id == user_uuid

    if document.epic_id is not None:
        epic = (await db.execute(select(Epic).where(Epic.id == document.epic_id))).scalar_one_or_none()
        if epic is None:
            return False
        if role in {"GROUP_LEADER", "TEAM_LEADER"}:
            return epic.application_id in await _leader_app_ids(db, user_uuid)

        if role == "DEVELOPER":
            return False

    return False


async def _require_document_access(db: AsyncSession, current_user, doc_id: UUID) -> Document:
    document = (await db.execute(select(Document).where(Document.id == doc_id))).scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    if not await _can_access_document(db, current_user, document):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no disponible para este usuario")
    return document


@router.get("/", response_model=list[DocumentResponse], summary="Listar documentos visibles")
async def list_documents(
    ticketId: str | None = Query(default=None, alias="ticketId"),
    epicId: str | None = Query(default=None, alias="epicId"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentResponse]:
    query = select(Document).options(selectinload(Document.uploaded_by))
    if ticketId and ticketId.strip() and ticketId.strip().lower() not in {"null", "undefined", "none"}:
        try:
            query = query.where(Document.ticket_id == UUID(ticketId.strip()))
        except (ValueError, TypeError):
            pass
    if epicId and epicId.strip() and epicId.strip().lower() not in {"null", "undefined", "none"}:
        try:
            query = query.where(Document.epic_id == UUID(epicId.strip()))
        except (ValueError, TypeError):
            pass
    query = query.order_by(Document.created_at.desc())

    result = await db.execute(query)
    documents = result.scalars().all()

    allowed_documents = []
    for document in documents:
        if await _can_access_document(db, current_user, document):
            allowed_documents.append(document)

    return [DocumentResponse.model_validate(doc) for doc in allowed_documents]


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED, summary="Subir documento a ticket o épica")
async def upload_document(
    file: UploadFile = File(...),
    ticketId: str | None = Form(default=None),
    epicId: str | None = Form(default=None),
    docType: str = Form(default="DOCUMENTATION"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre de archivo inválido")

    filename = Path(file.filename).name
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Extensión no permitida: {extension}")

    ticket_uuid: UUID | None = None
    if ticketId and ticketId.strip() and ticketId.strip().lower() not in {"null", "undefined", "none"}:
        try:
            ticket_uuid = UUID(ticketId.strip())
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de ticket inválido")

    epic_uuid: UUID | None = None
    if epicId and epicId.strip() and epicId.strip().lower() not in {"null", "undefined", "none"}:
        try:
            epic_uuid = UUID(epicId.strip())
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de épica inválido")

    if ticket_uuid:
        ticket = (await db.execute(select(Ticket).where(Ticket.id == ticket_uuid))).scalar_one_or_none()
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
    if epic_uuid:
        epic = (await db.execute(select(Epic).where(Epic.id == epic_uuid))).scalar_one_or_none()
        if epic is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Épica no encontrada")

    role = _normalize_role(getattr(current_user, "role", None))
    user_uuid = UUID(str(current_user.sub))
    if role == "DEVELOPER":
        if not ticket_uuid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los desarrolladores solo pueden adjuntar archivos a tickets asignados")
        ticket = (await db.execute(select(Ticket).where(Ticket.id == ticket_uuid))).scalar_one_or_none()
        if ticket is None or ticket.assignee_id != user_uuid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puedes adjuntar archivos a tus tickets asignados")
    elif role in {"GROUP_LEADER", "TEAM_LEADER"}:
        authorized_app_ids = await _leader_app_ids(db, user_uuid)
        if ticket_uuid:
            ticket = (await db.execute(select(Ticket).where(Ticket.id == ticket_uuid))).scalar_one_or_none()
            if ticket is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
            epic = (await db.execute(select(Epic).where(Epic.id == ticket.epic_id))).scalar_one_or_none()
            if epic is None or epic.application_id not in authorized_app_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a ese proyecto")
        if epic_uuid:
            epic = (await db.execute(select(Epic).where(Epic.id == epic_uuid))).scalar_one_or_none()
            if epic is None or epic.application_id not in authorized_app_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esa épica")

    # Se lee por bloques para no cargar en memoria archivos mayores al límite
    chunks: list[bytes] = []
    size = 0
    while chunk := await file.read(1024 * 1024):
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="El archivo supera el máximo de 10 MB")
        chunks.append(chunk)
    contents = b"".join(chunks)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4()}_{filename}"
    target_path = UPLOAD_DIR / safe_name
    with open(target_path, "wb") as fh:
        fh.write(contents)

    doc_type = DocumentType.DOCUMENTATION
    requested = str(docType or "DOCUMENTATION").upper()
    if requested == "CODE":
        doc_type = DocumentType.CODE
    elif requested == "DOCUMENTATION":
        doc_type = DocumentType.DOCUMENTATION

    document = Document(
        filename=filename,
        file_path=str(target_path),
        file_size=len(contents),
        mime_type=file.content_type or "application/octet-stream",
        epic_id=epic_uuid,
        ticket_id=ticket_uuid,
        uploaded_by_id=user_uuid,
        doc_type=doc_type,
    )
    db.add(document)
    await db.commit()

    stmt = (
        select(Document)
        .options(selectinload(Document.uploaded_by))
        .where(Document.id == document.id)
    )
    loaded_doc = (await db.execute(stmt)).scalar_one()
    return DocumentResponse.model_validate(loaded_doc)


@router.get("/{doc_id}/download", summary="Descargar documento")
async def download_document(
    doc_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    document = await _require_document_access(db, current_user, doc_id)
    path = _stored_path(document)
    if path is None or not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado en el sistema")
    # octet-stream: no se sirve con el content-type que declaró el cliente al
    # subirlo (un .html con text/html se ejecutaría en el origen de la app).
    return FileResponse(path=path, filename=document.filename, media_type="application/octet-stream")


@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
    summary="Eliminar documento",
)
async def delete_document(
    doc_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    document = await _require_document_access(db, current_user, doc_id)
    try:
        path = _stored_path(document)
        if path is not None and path.exists():
            path.unlink()
        await db.delete(document)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:  # pragma: no cover - error de I/O
        await db.rollback()
        logger.exception("Error al eliminar el documento %s", doc_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al eliminar documento") from exc
