"""
Router de Gestión de Usuarios.

Proporciona endpoints para:
- Listar, crear, actualizar y eliminar usuarios (requiere rol ADMIN)
- Gestionar roles de usuario (promover/degradar a líder de equipo)
- Obtener estadísticas y métricas de usuarios individuales
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models import User, UserRole, Ticket, TicketEvent
from app.schemas import UserResponse, UserCreate, UserUpdate
from app.middleware.auth import get_current_user, require_role

# Router con prefijo y etiqueta para la documentación
router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Listar todos los usuarios",
    description="Obtiene una lista paginada de todos los usuarios del sistema"
)
async def list_users(
    skip: int = Query(0, ge=0, description="Número de usuarios a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de usuarios a retornar"),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> List[UserResponse]:
    """
    Lista todos los usuarios del sistema con paginación.

    Args:
        skip (int): Número de registros a omitir (para paginación)
        limit (int): Número máximo de registros a retornar
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[UserResponse]: Lista de usuarios paginada

    Raises:
        HTTPException: Si el usuario no tiene permiso (estado 403)
    """
    # Consulta asíncrona con paginación
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    return [UserResponse.from_orm(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Recupera los detalles de un usuario específico"
)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Obtiene los detalles de un usuario específico.

    Args:
        user_id (int): ID del usuario a obtener
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        UserResponse: Datos del usuario solicitado

    Raises:
        HTTPException: Si el usuario no existe (estado 404)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    return UserResponse.from_orm(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario",
    description="Modifica los datos de un usuario (requiere permisos de ADMIN)"
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Actualiza los datos de un usuario específico.

    Args:
        user_id (int): ID del usuario a actualizar
        user_update (UserUpdate): Nuevos datos del usuario
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        UserResponse: Usuario actualizado

    Raises:
        HTTPException: Si el usuario no existe (404) o hay error en actualización (400)
    """
    # Buscar el usuario a actualizar
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    try:
        # Aplicar cambios únicamente a campos proporcionados
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)

        return UserResponse.from_orm(user)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar usuario: {str(e)}"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Marca un usuario como inactivo o lo elimina del sistema"
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Elimina un usuario del sistema.

    Args:
        user_id (int): ID del usuario a eliminar
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Raises:
        HTTPException: Si el usuario no existe (404) o es el último admin (400)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    # Proteger contra eliminación del último administrador
    if user.role == UserRole.ADMIN:
        admin_count = await db.execute(
            select(func.count(User.id)).where(User.role == UserRole.ADMIN)
        )
        if admin_count.scalar() <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el último administrador del sistema"
            )

    try:
        await db.delete(user)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar usuario: {str(e)}"
        )


@router.post(
    "/{user_id}/promote",
    response_model=UserResponse,
    summary="Promover usuario a líder",
    description="Asciende a un usuario a rol de TEAM_LEADER (requiere ADMIN)"
)
async def promote_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Promueve un usuario regular a líder de equipo.

    Args:
        user_id (int): ID del usuario a promover
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        UserResponse: Usuario con nuevo rol actualizado

    Raises:
        HTTPException: Si el usuario no existe (404) o ya es líder (400)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    if user.role == UserRole.TEAM_LEADER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya es líder de equipo"
        )

    try:
        user.role = UserRole.TEAM_LEADER
        await db.commit()
        await db.refresh(user)

        return UserResponse.from_orm(user)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al promover usuario: {str(e)}"
        )


@router.post(
    "/{user_id}/demote",
    response_model=UserResponse,
    summary="Degradar usuario de líder",
    description="Reduce el rol de un líder de equipo a usuario regular (requiere ADMIN)"
)
async def demote_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Degrada un líder de equipo a usuario regular.

    Args:
        user_id (int): ID del usuario a degradar
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        UserResponse: Usuario con rol actualizado

    Raises:
        HTTPException: Si el usuario no existe (404) o no es líder (400)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    if user.role != UserRole.TEAM_LEADER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no es líder de equipo"
        )

    try:
        user.role = UserRole.USER
        await db.commit()
        await db.refresh(user)

        return UserResponse.from_orm(user)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al degradar usuario: {str(e)}"
        )


@router.get(
    "/{user_id}/stats",
    summary="Obtener estadísticas del usuario",
    description="Retorna métricas de desempeño y actividad del usuario"
)
async def get_user_stats(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Obtiene estadísticas y métricas de un usuario.

    Args:
        user_id (int): ID del usuario del cual obtener estadísticas
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        dict: Diccionario con estadísticas del usuario

    Raises:
        HTTPException: Si el usuario no existe (404)
    """
    # Verificar que el usuario existe
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    # Contar tickets completados por el usuario
    completed_tickets = await db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.assigned_to == user_id,
            Ticket.status == "COMPLETED"
        )
    )
    completed_count = completed_tickets.scalar()

    # Contar tickets en progreso
    in_progress = await db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.assigned_to == user_id,
            Ticket.status == "IN_PROGRESS"
        )
    )
    in_progress_count = in_progress.scalar()

    # Contar eventos (actividad) del usuario
    activity = await db.execute(
        select(func.count(TicketEvent.id)).where(
            TicketEvent.user_id == user_id
        )
    )
    activity_count = activity.scalar()

    return {
        "user_id": user_id,
        "completed_tickets": completed_count,
        "in_progress_tickets": in_progress_count,
        "total_activity": activity_count,
        "join_date": user.created_at.isoformat() if user.created_at else None
    }
