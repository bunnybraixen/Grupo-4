"""
Router de Gestión de Épicas.

Gestiona el ciclo de vida de épicas:
- Listar, crear, obtener, actualizar y eliminar épicas
- Reordenar épicas dentro de una aplicación
- Cargar documentos relacionados con épicas
- Épicas contienen tickets que son los elementos de trabajo reales
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models import Epic, Application, Ticket, TicketStatus
from app.schemas import EpicResponse, EpicCreate, EpicUpdate, DocumentResponse
from app.middleware.auth import get_current_user

# Router para épicas
router = APIRouter(prefix="/epics", tags=["Épicas"])


@router.get(
    "/by-app/{app_id}",
    response_model=List[EpicResponse],
    summary="Listar épicas de una aplicación",
    description="Obtiene todas las épicas de una aplicación ordenadas por índice de orden"
)
async def get_application_epics(
    app_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[EpicResponse]:
    """
    Lista todas las épicas de una aplicación específica ordenadas por order_index.

    Args:
        app_id (int): ID de la aplicación
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[EpicResponse]: Lista de épicas ordenadas

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

    # Obtener todas las épicas ordenadas por índice de orden
    result = await db.execute(
        select(Epic)
        .where(Epic.application_id == app_id)
        .order_by(Epic.order_index.asc())
    )
    epics = result.scalars().all()

    return [EpicResponse.from_orm(epic) for epic in epics]


@router.post(
    "/",
    response_model=EpicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva épica",
    description="Crea una nueva épica dentro de una aplicación"
)
async def create_epic(
    epic_data: EpicCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EpicResponse:
    """
    Crea una nueva épica en una aplicación.

    Args:
        epic_data (EpicCreate): Datos de la nueva épica
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        EpicResponse: Épica creada

    Raises:
        HTTPException: Si la aplicación no existe (404) o hay error en creación (400)
    """
    # Verificar que la aplicación existe
    app_check = await db.execute(
        select(Application).where(Application.id == epic_data.application_id)
    )
    if not app_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aplicación con ID {epic_data.application_id} no encontrada"
        )

    try:
        # Obtener el siguiente order_index disponible
        max_order = await db.execute(
            select(func.max(Epic.order_index))
            .where(Epic.application_id == epic_data.application_id)
        )
        next_order = (max_order.scalar() or -1) + 1

        # Crear nueva épica
        new_epic = Epic(
            **epic_data.dict(),
            order_index=next_order
        )
        db.add(new_epic)
        await db.commit()
        await db.refresh(new_epic)

        return EpicResponse.from_orm(new_epic)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear épica: {str(e)}"
        )


@router.get(
    "/{epic_id}",
    response_model=EpicResponse,
    summary="Obtener épica por ID",
    description="Recupera los detalles de una épica incluyendo información de progreso"
)
async def get_epic(
    epic_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EpicResponse:
    """
    Obtiene los detalles de una épica con información de progreso.

    Args:
        epic_id (int): ID de la épica
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        EpicResponse: Datos de la épica con información de progreso

    Raises:
        HTTPException: Si la épica no existe (404)
    """
    result = await db.execute(
        select(Epic).where(Epic.id == epic_id)
    )
    epic = result.scalar_one_or_none()

    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    # Precargar información de tickets relacionados
    await db.refresh(epic)

    return EpicResponse.from_orm(epic)


@router.put(
    "/{epic_id}",
    response_model=EpicResponse,
    summary="Actualizar épica",
    description="Modifica los datos de una épica existente"
)
async def update_epic(
    epic_id: int,
    epic_update: EpicUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EpicResponse:
    """
    Actualiza los datos de una épica.

    Args:
        epic_id (int): ID de la épica a actualizar
        epic_update (EpicUpdate): Nuevos datos de la épica
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        EpicResponse: Épica actualizada

    Raises:
        HTTPException: Si la épica no existe (404) o hay error en actualización (400)
    """
    result = await db.execute(
        select(Epic).where(Epic.id == epic_id)
    )
    epic = result.scalar_one_or_none()

    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    try:
        # Aplicar cambios únicamente a campos proporcionados
        update_data = epic_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(epic, field, value)

        await db.commit()
        await db.refresh(epic)

        return EpicResponse.from_orm(epic)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar épica: {str(e)}"
        )


@router.delete(
    "/{epic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar épica",
    description="Elimina una épica y todos sus tickets relacionados"
)
async def delete_epic(
    epic_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Elimina una épica del sistema de forma permanente.

    Args:
        epic_id (int): ID de la épica a eliminar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Raises:
        HTTPException: Si la épica no existe (404) o hay error en eliminación (400)
    """
    result = await db.execute(
        select(Epic).where(Epic.id == epic_id)
    )
    epic = result.scalar_one_or_none()

    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    try:
        # Eliminar en cascada todos los tickets de la épica
        await db.delete(epic)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar épica: {str(e)}"
        )


@router.patch(
    "/{epic_id}/reorder",
    response_model=EpicResponse,
    summary="Reordenar épica",
    description="Cambia la posición de una épica y ajusta otros órdenes en consecuencia"
)
async def reorder_epic(
    epic_id: int,
    new_order: dict,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EpicResponse:
    """
    Reordena una épica cambiando su order_index y ajustando los demás.

    Args:
        epic_id (int): ID de la épica a reordenar
        new_order (dict): Contiene 'new_index' con la nueva posición
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        EpicResponse: Épica reordenada

    Raises:
        HTTPException: Si la épica no existe (404) o índice inválido (400)
    """
    result = await db.execute(
        select(Epic).where(Epic.id == epic_id)
    )
    epic = result.scalar_one_or_none()

    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    try:
        new_index = new_order.get("new_index", 0)
        old_index = epic.order_index

        # Obtener todas las épicas de la misma aplicación
        epics = await db.execute(
            select(Epic)
            .where(Epic.application_id == epic.application_id)
            .order_by(Epic.order_index)
        )
        all_epics = epics.scalars().all()

        if new_index < 0 or new_index >= len(all_epics):
            raise ValueError("Índice de orden fuera de rango")

        # Si el nuevo índice es mayor, desplazar épicas hacia atrás
        if new_index > old_index:
            for ep in all_epics:
                if old_index < ep.order_index <= new_index:
                    ep.order_index -= 1

        # Si el nuevo índice es menor, desplazar épicas hacia adelante
        elif new_index < old_index:
            for ep in all_epics:
                if new_index <= ep.order_index < old_index:
                    ep.order_index += 1

        # Asignar nuevo índice a la épica
        epic.order_index = new_index

        await db.commit()
        await db.refresh(epic)

        return EpicResponse.from_orm(epic)

    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al reordenar épica: {str(e)}"
        )


@router.post(
    "/{epic_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cargar documento a épica",
    description="Carga un archivo de documentación a una épica"
)
async def upload_epic_document(
    epic_id: int,
    file_data: dict,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """
    Carga un documento a una épica específica.

    Args:
        epic_id (int): ID de la épica
        file_data (dict): Datos del archivo a cargar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        DocumentResponse: Documento creado

    Raises:
        HTTPException: Si la épica no existe (404) o hay error en carga (400)
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

    try:
        # Implementar lógica de carga de archivo
        # Este es un placeholder que debería conectar con el servicio de documentos
        from app.models import Document

        new_document = Document(
            epic_id=epic_id,
            **file_data
        )
        db.add(new_document)
        await db.commit()
        await db.refresh(new_document)

        return DocumentResponse.from_orm(new_document)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al cargar documento: {str(e)}"
        )
