"""
Router de Gestión de Documentos.

Proporciona endpoints para:
- Listar documentos de una épica
- Cargar nuevos documentos (multipart)
- Descargar archivos
- Eliminar documentos
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
from datetime import datetime

from app.database import get_db
from app.models import Document, Epic, TicketEvent, TicketEventType
from app.schemas import DocumentResponse
from app.services import ticket_state_machine
from app.middleware.auth import get_current_user

# Router para documentos
router = APIRouter(prefix="/documents", tags=["Documentos"])

# Directorio base para almacenar documentos (ajustar según configuración)
UPLOAD_DIR = "/tmp/corestream_documents"


@router.get(
    "/by-epic/{epic_id}",
    response_model=List[DocumentResponse],
    summary="Listar documentos de épica",
    description="Obtiene todos los documentos asociados a una épica"
)
async def get_epic_documents(
    epic_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[DocumentResponse]:
    """
    Lista todos los documentos de una épica.

    Args:
        epic_id (int): ID de la épica
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[DocumentResponse]: Lista de documentos

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

    # Obtener documentos de la épica
    result = await db.execute(
        select(Document)
        .where(Document.epic_id == epic_id)
        .order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()

    return [DocumentResponse.from_orm(doc) for doc in documents]


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cargar documento",
    description="Carga un archivo de documentación a una épica"
)
async def upload_document(
    file: UploadFile = File(...),
    epic_id: int = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """
    Carga un archivo de documentación.

    Args:
        file (UploadFile): Archivo a cargar
        epic_id (int): ID de la épica donde cargar el documento
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        DocumentResponse: Documento creado

    Raises:
        HTTPException: Si la épica no existe (404) o hay error en carga (400)
    """
    # Verificar que la épica existe si se proporciona
    if epic_id:
        epic_check = await db.execute(
            select(Epic).where(Epic.id == epic_id)
        )
        if not epic_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Épica con ID {epic_id} no encontrada"
            )

    try:
        # Crear directorio si no existe
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Generar nombre único para el archivo
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # Guardar archivo
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Crear registro en base de datos
        document = Document(
            epic_id=epic_id,
            filename=file.filename,
            file_path=file_path,
            file_size=len(contents),
            mime_type=file.content_type,
            uploaded_by=current_user.id
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)

        return DocumentResponse.from_orm(document)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al cargar documento: {str(e)}"
        )


@router.get(
    "/{doc_id}/download",
    summary="Descargar documento",
    description="Descarga un archivo de documentación"
)
async def download_document(
    doc_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """
    Descarga un documento.

    Args:
        doc_id (int): ID del documento a descargar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        FileResponse: Archivo para descargar

    Raises:
        HTTPException: Si el documento no existe (404) o no se puede descargar (400)
    """
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento con ID {doc_id} no encontrado"
        )

    # Verificar que el archivo existe
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archivo no encontrado en el sistema de archivos"
        )

    try:
        return FileResponse(
            path=document.file_path,
            filename=document.filename,
            media_type=document.mime_type
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al descargar documento: {str(e)}"
        )


@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar documento",
    description="Elimina un documento de forma permanente"
)
async def delete_document(
    doc_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Elimina un documento.

    Args:
        doc_id (int): ID del documento a eliminar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Raises:
        HTTPException: Si el documento no existe (404) o hay error en eliminación (400)
    """
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento con ID {doc_id} no encontrado"
        )

    try:
        # Eliminar archivo del sistema de archivos
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Eliminar registro de base de datos
        await db.delete(document)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar documento: {str(e)}"
        )
