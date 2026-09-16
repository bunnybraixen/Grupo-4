"""
Router de Gestión de Documentos.

Proporciona endpoints para:
- Listar documentos por épica o ticket
- Cargar nuevos documentos (multipart)
- Descargar archivos
- Eliminar documentos
"""

import os
import re
from datetime import datetime
from pathlib import Path as FilePath
from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import Document, Epic, User
from app.schemas.document import DocumentResponse, TranslateRequest, TranslateResponse
from app.services.ticket_permissions import is_admin_or_leader
from app.services.translation_service import (
    create_translated_file,
    extract_text_from_file,
    translate_long_text,
)

router = APIRouter(tags=["Documentos"])

# Antes hardcodeado a "/app/storage/documents": settings.UPLOAD_DIR existía
# en .env.example documentado como "el sitio donde configurar esto" pero
# nadie lo leía (plan fase 7.2). Subcarpeta "documents" para no mezclar con
# los adjuntos genéricos de uploads.py (services/file_service.py), que
# comparten la misma raíz configurable.
UPLOAD_DIR = os.path.join(get_settings().UPLOAD_DIR, "documents")
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

ALLOWED_EXTENSIONS = {
    # Code
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".cs",
    ".rb", ".go", ".rs", ".php", ".swift", ".kt", ".scala",
    # Documentation
    ".md", ".pdf", ".docx", ".txt", ".rst", ".doc",
    # Data
    ".json", ".yaml", ".yml", ".xml", ".sql", ".csv", ".toml", ".env",
}


@router.get(
    "/",
    response_model=List[DocumentResponse],
    summary="Listar documentos",
    description="Obtiene documentos filtrados por épica o ticket"
)
async def list_documents(
    epic_id: Optional[UUID] = Query(None, alias="epicId"),
    ticket_id: Optional[UUID] = Query(None, alias="ticketId"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[DocumentResponse]:
    query = select(Document).options(selectinload(Document.uploaded_by))
    if epic_id:
        query = query.where(Document.epic_id == epic_id)
    elif ticket_id:
        query = query.where(Document.ticket_id == ticket_id)
    query = query.order_by(Document.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cargar documento",
    description="Carga un archivo y lo asocia a una épica o ticket"
)
async def upload_document(
    file: UploadFile = File(...),
    epicId: Optional[str] = Form(None),
    ticketId: Optional[str] = Form(None),
    docType: Optional[str] = Form("DOCUMENTATION"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    # Convert empty strings to None
    epic_id = UUID(epicId) if epicId and epicId.strip() else None
    ticket_id = UUID(ticketId) if ticketId and ticketId.strip() else None

    if epic_id:
        result = await db.execute(select(Epic).where(Epic.id == epic_id))
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Épica con ID {epic_id} no encontrada"
            )

    # Validate file extension
    if file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext and ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extensión '{ext}' no permitida. Tipos soportados: código, documentación y datos."
            )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo supera el límite de 25 MB"
        )

    # ── Sanitize filename ────────────────────────────────────────────────────
    raw_name = file.filename or "document"
    path_obj = FilePath(raw_name)
    ext = path_obj.suffix.lower()   # Only the last extension (e.g. ".docx")
    stem = path_obj.stem            # Everything before the last dot

    # If the stem itself ends with a known extension (double-extension like
    # "report.docx.md"), strip that inner extension too.
    inner_ext = FilePath(stem).suffix.lower()
    if inner_ext and inner_ext in ALLOWED_EXTENSIONS:
        stem = FilePath(stem).stem

    # Strip OS copy-suffixes from the stem: " (1)", " (2)", " copy", etc.
    stem = re.sub(r'\s*\(\d+\)\s*$', '', stem).strip()
    stem = re.sub(r'\s+copy\s*$', '', stem, flags=re.IGNORECASE).strip()

    clean_filename = f"{stem}{ext}" if ext else stem

    # ── Deduplicate within the same epic/ticket context ──────────────────────
    name_query = select(Document.filename)
    if epic_id:
        name_query = name_query.where(Document.epic_id == epic_id)
    elif ticket_id:
        name_query = name_query.where(Document.ticket_id == ticket_id)
    names_result = await db.execute(name_query)
    existing_names = {row[0] for row in names_result.fetchall()}

    if clean_filename in existing_names:
        counter = 1
        while f"{stem} ({counter}){ext}" in existing_names:
            counter += 1
        clean_filename = f"{stem} ({counter}){ext}"
    # ────────────────────────────────────────────────────────────────────────

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S%f")
    safe_filename = f"{timestamp}_{clean_filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as f:  # noqa: ASYNC230 — deuda conocida: bloquea el event loop (plan fase 7.2)
        f.write(contents)

    # Validate doc_type against allowed values
    allowed_types = {"CODE", "DOCUMENTATION"}
    resolved_doc_type = (docType or "DOCUMENTATION").upper()
    if resolved_doc_type not in allowed_types:
        resolved_doc_type = "DOCUMENTATION"

    document = Document(
        epic_id=epic_id,
        ticket_id=ticket_id,
        filename=clean_filename,
        file_path=file_path,
        file_size=len(contents),
        mime_type=file.content_type or "application/octet-stream",
        doc_type=resolved_doc_type,
        uploaded_by_id=current_user.id,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


@router.get(
    "/{doc_id}/download",
    summary="Descargar documento",
    description="Descarga el archivo de un documento"
)
async def download_document(
    doc_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento con ID {doc_id} no encontrado"
        )

    if not os.path.exists(document.file_path):  # noqa: ASYNC240 — deuda conocida: bloquea el event loop (plan fase 7.2)
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Archivo no encontrado en el sistema de archivos"
        )

    return FileResponse(
        path=document.file_path,
        filename=document.filename,
        media_type=document.mime_type,
    )


# MIME types soportados para traducción.
# Incluye texto plano, formatos estructurados y binarios con extracción de texto.
TRANSLATABLE_MIME_TYPES = {
    # Texto plano / estructurado
    "text/plain",
    "text/markdown",
    "text/html",
    "text/xml",
    "text/yaml",
    "text/csv",
    "application/json",
    "application/xml",
    "application/yaml",
    # CSV variantes
    "application/csv",
    # PDF
    "application/pdf",
    # DOCX / DOC
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}

# Extensiones que también se aceptan aunque el MIME no coincida exactamente
TRANSLATABLE_EXTENSIONS = {".pdf", ".docx", ".doc", ".csv", ".md", ".txt", ".rst",
                            ".json", ".yaml", ".yml", ".xml", ".html", ".toml", ".env"}


@router.post(
    "/{doc_id}/translate",
    response_model=TranslateResponse,
    summary="Traducir documento",
    description="Traduce el contenido de un documento de texto usando Azure Translator"
)
async def translate_document(
    doc_id: UUID,
    req: TranslateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TranslateResponse:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento con ID {doc_id} no encontrado"
        )

    # Verificar que el tipo de archivo es traducible (por MIME o extensión)
    base_mime = document.mime_type.split(";")[0].strip().lower()
    ext = os.path.splitext(document.filename or "")[1].lower()
    if base_mime not in TRANSLATABLE_MIME_TYPES and ext not in TRANSLATABLE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"El tipo de archivo '{document.mime_type}' no es compatible con la traducción. "
                "Se admiten: texto plano, Markdown, JSON, HTML, XML, YAML, CSV, PDF y DOCX."
            ),
        )

    if not os.path.exists(document.file_path):  # noqa: ASYNC240 — deuda conocida: bloquea el event loop (plan fase 7.2)
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Archivo no encontrado en el sistema de archivos"
        )

    content = extract_text_from_file(document.file_path, document.mime_type, document.filename or "")

    translated = await translate_long_text(content, "auto", req.target_language)

    return TranslateResponse(
        document_id=document.id,
        original_filename=document.filename,
        target_language=req.target_language,
        translated_text=translated,
    )


@router.post(
    "/{doc_id}/translate/download",
    summary="Descargar traducción",
    description="Traduce el archivo preservando su formato y lo devuelve como descarga"
)
async def translate_document_download(
    doc_id: UUID,
    req: TranslateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento con ID {doc_id} no encontrado"
        )

    base_mime = document.mime_type.split(";")[0].strip().lower()
    ext = os.path.splitext(document.filename or "")[1].lower()
    if base_mime not in TRANSLATABLE_MIME_TYPES and ext not in TRANSLATABLE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"El tipo de archivo '{document.mime_type}' no es compatible con la traducción. "
                "Se admiten: texto plano, Markdown, JSON, HTML, XML, YAML, CSV, PDF y DOCX."
            ),
        )

    if not os.path.exists(document.file_path):  # noqa: ASYNC240 — deuda conocida: bloquea el event loop (plan fase 7.2)
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Archivo no encontrado en el sistema de archivos"
        )

    content_bytes, output_filename, media_type = await create_translated_file(
        document.file_path,
        document.mime_type,
        document.filename or "document",
        req.target_language,
    )

    return Response(
        content=content_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{output_filename}"'},
    )


@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar documento",
    description="Elimina un documento y su archivo del disco"
)
async def delete_document(
    doc_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento con ID {doc_id} no encontrado"
        )

    if document.uploaded_by_id != current_user.id and not is_admin_or_leader(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo quien subió el documento, ADMIN o TEAM_LEADER pueden eliminarlo",
        )

    if os.path.exists(document.file_path):  # noqa: ASYNC240 — deuda conocida: bloquea el event loop (plan fase 7.2)
        os.remove(document.file_path)

    await db.delete(document)
    await db.commit()
