"""
Router de Gestión de Aplicaciones.

Maneja operaciones CRUD para aplicaciones del sistema:
- Crear, listar, obtener, actualizar y eliminar aplicaciones
- Cada aplicación contiene épicas que contienen tickets
- Requiere permisos de ADMIN o TEAM_LEADER para crear, actualizar y eliminar
"""

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, case, func, select
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware import get_current_user, require_role
from app.models import Application, Epic, Ticket, TicketStatus, User, UserRole
from app.schemas import ApplicationCreate, ApplicationResponse, ApplicationUpdate

# Router para endpoints de aplicaciones
router = APIRouter(tags=["Aplicaciones"])

# ADMIN y TEAM_LEADER gestionan aplicaciones — igual que ya hace epics.py con
# épicas/tickets (_MANAGERS ahí). Antes esto era ADMIN-only: en la práctica
# obligaba al admin a crear cada aplicación nueva en persona, sin poder
# delegarlo en quien lleve el día a día del equipo. Invitar usuarios,
# cambiar roles y resetear contraseñas siguen siendo solo de ADMIN (ver
# users.py e invitations.py) — esto solo afecta a las aplicaciones.
_MANAGERS = [UserRole.ADMIN, UserRole.TEAM_LEADER]


@router.get(
    "/",
    response_model=List[ApplicationResponse],
    summary="Listar todas las aplicaciones",
    description="Obtiene una lista de todas las aplicaciones disponibles en el sistema"
)
async def list_applications(
    skip: int = Query(0, ge=0, description="Número de aplicaciones a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de aplicaciones a retornar"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ApplicationResponse]:
    """
    Lista todas las aplicaciones con CONTEOS REALES dinámicos.
    
    Conteos calculados EN TIEMPO REAL:
    - epic_count: Total de épicas en la app (que no estén archivadas)
    - pending_count: Tickets con status = TODO
    - overdue_count: Tickets con due_date < hoy y status != COMPLETED
    
    OPTIMIZACIÓN: Usa índices de BD para evitar scans completos
    - idx_epic_application_id: Conteo de épicas rápido
    - idx_ticket_status_epic: Conteo de TODO rápido
    - idx_ticket_overdue: Conteo de retrasados rápido

    Args:
        skip (int): Número de registros a omitir para paginación
        limit (int): Número máximo de registros a retornar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[ApplicationResponse]: Lista paginada de aplicaciones con conteos reales
    """
    # Antes: 1 query para listar + 3 queries POR aplicación (épicas,
    # pendientes, retrasados) — con 5 apps son 16 queries, con 100 son más de
    # 300 por carga de página (plan fase 9). Una sola query agregada con
    # LEFT JOIN + COUNT(DISTINCT ...) condicional evita el N+1: el DISTINCT
    # protege los conteos del fan-out que produce el join con Ticket (una
    # épica con varios tickets no debe inflar epic_count).
    now = datetime.now(timezone.utc)

    epic_count_expr = func.count(func.distinct(Epic.id))
    pending_count_expr = func.count(
        func.distinct(case((Ticket.status == TicketStatus.TODO, Ticket.id)))
    )
    overdue_count_expr = func.count(
        func.distinct(
            case((and_(Ticket.due_date < now, Ticket.status != TicketStatus.COMPLETED), Ticket.id))
        )
    )

    result = await db.execute(
        select(Application, epic_count_expr, pending_count_expr, overdue_count_expr)
        .outerjoin(Epic, Epic.application_id == Application.id)
        .outerjoin(Ticket, Ticket.epic_id == Epic.id)
        .group_by(Application.id)
        .order_by(Application.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    app_responses = []
    for app, epic_count, pending_count, overdue_count in result.all():
        app_view = ApplicationResponse.model_validate(app)
        app_view.epic_count = epic_count
        app_view.pending_count = pending_count
        app_view.delayed_count = overdue_count
        app_responses.append(app_view)

    return app_responses


@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva aplicación",
    description="Crea una nueva aplicación en el sistema (requiere ADMIN o TEAM_LEADER)"
)
async def create_application(
    app_data: ApplicationCreate,
    current_user: User = Depends(require_role(_MANAGERS)),
    db: AsyncSession = Depends(get_db)
) -> ApplicationResponse:
    """
    Crea una nueva aplicación en el sistema.

    Args:
        app_data (ApplicationCreate): Datos de la nueva aplicación
        current_user (User): Usuario autenticado con rol ADMIN o TEAM_LEADER
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
        new_app = Application(**app_data.dict(), owner_id=current_user.id)
        db.add(new_app)
        await db.commit()
        await db.refresh(new_app)

        # Obtener conteos para la nueva aplicación (serán 0 inicialmente)
        epic_count = 0
        pending_count = 0
        delayed_count = 0
        
        return ApplicationResponse(
            id=new_app.id,
            name=new_app.name,
            description=new_app.description,
            color=new_app.color,
            icon=new_app.icon,
            owner_id=new_app.owner_id,
            is_active=new_app.is_active,
            created_at=new_app.created_at,
            epic_count=epic_count,
            pending_count=pending_count,
            delayed_count=delayed_count
        )

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
    app_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ApplicationResponse:
    """
    Obtiene los detalles de una aplicación específica con información de épicas.

    Args:
        app_id (UUID): ID de la aplicación a obtener
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

    # Obtener conteos para aplicación individual
    epic_count_result = await db.execute(
        select(func.count(Epic.id))
        .where(Epic.application_id == app_id)
    )
    epic_count = epic_count_result.scalar() or 0
    
    # Para tickets, necesitamos la tabla tickets (si existe)
    pending_count_result = await db.execute(
        select(func.count(Ticket.id))
        .join(Epic)
        .where(Epic.application_id == app_id)
        .where(Ticket.status == TicketStatus.TODO)
    )
    pending_count = pending_count_result.scalar() or 0
    
    return ApplicationResponse(
        id=application.id,
        name=application.name,
        description=application.description,
        color=application.color,
        icon=application.icon,
        owner_id=application.owner_id,
        is_active=application.is_active,
        created_at=application.created_at,
        epic_count=epic_count,
        pending_count=pending_count,
        delayed_count=0
    )


@router.put(
    "/{app_id}",
    response_model=ApplicationResponse,
    summary="Actualizar aplicación",
    description="Modifica los datos de una aplicación existente (requiere ADMIN o TEAM_LEADER)"
)
async def update_application(
    app_id: UUID,
    app_update: ApplicationUpdate,
    current_user: User = Depends(require_role(_MANAGERS)),
    db: AsyncSession = Depends(get_db)
) -> ApplicationResponse:
    """
    Actualiza los datos de una aplicación específica.

    Args:
        app_id (UUID): ID de la aplicación a actualizar
        app_update (ApplicationUpdate): Nuevos datos de la aplicación
        current_user (User): Usuario autenticado con rol ADMIN o TEAM_LEADER
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

        return ApplicationResponse.model_validate(application)

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
    app_id: UUID,
    current_user: User = Depends(require_role(_MANAGERS)),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Elimina una aplicación del sistema de forma permanente.

    Args:
        app_id (UUID): ID de la aplicación a eliminar
        current_user (User): Usuario autenticado con rol ADMIN o TEAM_LEADER
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
        await db.execute(sa_delete(Application).where(Application.id == app_id))
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar aplicación: {str(e)}"
        )
