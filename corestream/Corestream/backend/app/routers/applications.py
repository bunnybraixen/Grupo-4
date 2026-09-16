"""
Router de Gestión de Aplicaciones.

Maneja operaciones CRUD para aplicaciones del sistema:
- Crear, listar, obtener, actualizar y eliminar aplicaciones
- Cada aplicación contiene épicas que contienen tickets
- Requiere permisos de ADMIN para crear, actualizar y eliminar
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models import Application, UserRole, Epic, Ticket, TicketStatus
from app.schemas import ApplicationResponse, ApplicationCreate, ApplicationUpdate
from app.middleware.auth import get_current_user, require_role

# Router para endpoints de aplicaciones
router = APIRouter(prefix="/applications", tags=["Aplicaciones"])


@router.get(
    "/",
    response_model=List[ApplicationResponse],
    summary="Listar todas las aplicaciones",
    description="Obtiene una lista de todas las aplicaciones disponibles en el sistema"
)
async def list_applications(
    skip: int = Query(0, ge=0, description="Número de aplicaciones a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de aplicaciones a retornar"),
    current_user: Application = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ApplicationResponse]:
    """
    Lista todas las aplicaciones con información de épicas y tickets.

    Args:
        skip (int): Número de registros a omitir para paginación
        limit (int): Número máximo de registros a retornar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[ApplicationResponse]: Lista paginada de aplicaciones
    """
    result = await db.execute(
        select(Application)
        .order_by(Application.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    applications = result.scalars().all()

    return [ApplicationResponse.from_orm(app) for app in applications]


@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva aplicación",
    description="Crea una nueva aplicación en el sistema (requiere permisos ADMIN)"
)
async def create_application(
    app_data: ApplicationCreate,
    current_user: Application = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> ApplicationResponse:
    """
    Crea una nueva aplicación en el sistema.

    Args:
        app_data (ApplicationCreate): Datos de la nueva aplicación
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        ApplicationResponse: Aplicación creada

    Raises:
        HTTPException: Si el nombre ya existe (409) o hay error en creación (400)
    """
    # Verificar que no existe una aplicación con el mismo nombre
    existing = await db.execute(
        select(Application).where(Application.name == app_data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una aplicación con el nombre '{app_data.name}'"
        )

    try:
        # Crear nueva instancia de aplicación
        new_app = Application(**app_data.dict())
        db.add(new_app)
        await db.commit()
        await db.refresh(new_app)

        return ApplicationResponse.from_orm(new_app)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear aplicación: {str(e)}"
        )


@router.get(
    "/{app_id}",
    response_model=ApplicationResponse,
    summary="Obtener aplicación por ID",
    description="Recupera los detalles completos de una aplicación, incluyendo conteos"
)
async def get_application(
    app_id: int,
    current_user: Application = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ApplicationResponse:
    """
    Obtiene los detalles de una aplicación específica con información de épicas.

    Args:
        app_id (int): ID de la aplicación a obtener
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        ApplicationResponse: Datos de la aplicación con conteos

    Raises:
        HTTPException: Si la aplicación no existe (404)
    """
    result = await db.execute(
        select(Application).where(Application.id == app_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aplicación con ID {app_id} no encontrada"
        )

    # Precargar información de épicas relacionadas
    await db.refresh(application)

    return ApplicationResponse.from_orm(application)


@router.put(
    "/{app_id}",
    response_model=ApplicationResponse,
    summary="Actualizar aplicación",
    description="Modifica los datos de una aplicación existente (requiere permisos ADMIN)"
)
async def update_application(
    app_id: int,
    app_update: ApplicationUpdate,
    current_user: Application = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> ApplicationResponse:
    """
    Actualiza los datos de una aplicación específica.

    Args:
        app_id (int): ID de la aplicación a actualizar
        app_update (ApplicationUpdate): Nuevos datos de la aplicación
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        ApplicationResponse: Aplicación actualizada

    Raises:
        HTTPException: Si la aplicación no existe (404) o hay error en actualización (400)
    """
    result = await db.execute(
        select(Application).where(Application.id == app_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aplicación con ID {app_id} no encontrada"
        )

    # Verificar si se intenta cambiar el nombre a uno que ya existe
    if app_update.name and app_update.name != application.name:
        existing = await db.execute(
            select(Application).where(Application.name == app_update.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una aplicación con el nombre '{app_update.name}'"
            )

    try:
        # Aplicar cambios a los campos proporcionados
        update_data = app_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)

        await db.commit()
        await db.refresh(application)

        return ApplicationResponse.from_orm(application)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar aplicación: {str(e)}"
        )


@router.delete(
    "/{app_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar aplicación",
    description="Elimina una aplicación del sistema y todos sus datos relacionados"
)
async def delete_application(
    app_id: int,
    current_user: Application = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Elimina una aplicación del sistema de forma permanente.

    Args:
        app_id (int): ID de la aplicación a eliminar
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Raises:
        HTTPException: Si la aplicación no existe (404) o hay error en eliminación (400)
    """
    result = await db.execute(
        select(Application).where(Application.id == app_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aplicación con ID {app_id} no encontrada"
        )

    try:
        # Eliminar todas las épicas y tickets relacionados en cascada
        await db.delete(application)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar aplicación: {str(e)}"
        )
