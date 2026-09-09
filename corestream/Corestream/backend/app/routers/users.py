"""
Router de Gestión de Usuarios.

Proporciona endpoints para:
- Listar, crear, actualizar y eliminar usuarios (requiere rol ADMIN)
- Gestionar roles de usuario (promover/degradar a líder de equipo)
- Obtener estadísticas y métricas de usuarios individuales
"""

import logging
import secrets
import string
import traceback
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import TokenPayload, get_current_user, require_role
from app.models import Role, Ticket, TicketEvent, TicketStatus, User, UserRole
from app.schemas import AdminPasswordResetResponse, UserCreate, UserResponse, UserUpdate
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

# Router con prefijo y etiqueta para la documentación
router = APIRouter(tags=["Usuarios"])


# Modelos de solicitud
class ChangeRoleRequest(BaseModel):
    role: str


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario validando unicidad de email y almacenando contraseña hasheada"
)
async def create_user(
    user_data: UserCreate,
    current_user: TokenPayload = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Crea un nuevo usuario en el sistema.

    - Verifica que el email no exista previamente.
    - Hashea la contraseña antes de persistir.
    """
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya existe"
        )

    dev_role_result = await db.execute(
        select(Role).where(Role.name == UserRole.DEVELOPER.value)
    )
    dev_role = dev_role_result.scalar_one_or_none()
    if not dev_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rol DEVELOPER no encontrado en el sistema"
        )

    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        specialty=user_data.specialty,
        # AuthService.hash_password (no middleware.auth.hash_password): el
        # login verifica con AuthService.verify_password, que aplica un
        # pre-hash SHA-256 antes de bcrypt; el otro hash_password es bcrypt
        # liso y un usuario creado así nunca podría iniciar sesión — bug
        # preexistente en este endpoint, detectado al escribir create_admin.py.
        hashed_password=AuthService.hash_password(user_data.password),
        role_id=dev_role.id,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user, attribute_names=['role'])

    return UserResponse.model_validate(new_user)


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Listar todos los usuarios",
    description="Obtiene una lista paginada de todos los usuarios del sistema"
)
async def list_users(
    skip: int = Query(0, ge=0, description="Número de usuarios a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de usuarios a retornar"),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TEAM_LEADER])),
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
    try:
        # Consulta asíncrona con paginación - eager load role relationship
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.is_active)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        users = result.unique().scalars().all()
        logger.info(f"DEBUG list_users: Fetched {len(users)} users")

        validated_users = []
        for i, user in enumerate(users):
            try:
                logger.info(f"DEBUG: Validating user {i}: id={user.id}, email={user.email}, role={user.role}, role_type={type(user.role)}")
                validated = UserResponse.model_validate(user)
                validated_users.append(validated)
            except Exception as e:
                logger.error(f"ERROR validating user {i} (id={user.id}): {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

        return validated_users

    except Exception as e:
        logger.error(f"ERROR in list_users: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users: {str(e)}"
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Recupera los detalles de un usuario específico"
)
async def get_user(
    user_id: str,
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
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id)
    )
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario",
    description="Modifica los datos de un usuario (requiere permisos de ADMIN)"
)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
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
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id)
    )
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    try:
        # Aplicar cambios únicamente a campos proporcionados
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user, attribute_names=['role'])

        return UserResponse.model_validate(user)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar usuario: {str(e)}"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar o desactivar usuario",
    description="Marca un usuario como inactivo (preservando el historial) o lo elimina del sistema"
)
async def delete_user(
    user_id: str,
    hard_delete: bool = Query(False, description="⚠️ PELIGRO: Si es True, elimina físicamente al usuario y todo su historial. Si es False, solo lo desactiva."),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
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
    # Cargar usuario y su rol
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    # Proteger contra eliminación del último administrador
    if user.role and user.role.name == UserRole.ADMIN.value:
        admin_count = await db.execute(
            select(func.count(User.id))
            .select_from(User)
            .join(Role)
            .where(Role.name == UserRole.ADMIN.value, User.is_active)
        )
        admin_total = int(admin_count.scalar() or 0)
        if admin_total <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el último administrador del sistema"
            )

    try:
        # Lógica bifurcada según lo que pida el frontend
        if hard_delete:
            # Elimina el registro por completo de la base de datos
            await db.delete(user)
        else:
            # Soft Delete: Solo lo marca como inactivo
            user.is_active = False
            
        await db.commit()

    except Exception as e:
        await db.rollback()
        
        # Si da error en hard_delete, suele ser por llaves foráneas (el usuario tiene tickets y la BD bloquea el borrado para no dejar tickets huérfanos)
        error_msg = str(e)
        if "Foreign key violation" in error_msg or "violates foreign key constraint" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede hacer Hard Delete: El usuario tiene tickets o eventos asociados. Utiliza Soft Delete (hard_delete=false) o reasigna sus tickets primero."
            )
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar la eliminación: {error_msg}"
        )


@router.post(
    "/{user_id}/promote",
    response_model=UserResponse,
    summary="Promover usuario a líder",
    description="Asciende a un usuario a rol de TEAM_LEADER (requiere ADMIN)"
)
async def promote_user(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
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
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id)
    )
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    # Buscar el rol TEAM_LEADER en BD para comparar y asignar por FK
    leader_role_result = await db.execute(
        select(Role).where(Role.name == UserRole.TEAM_LEADER)
    )
    team_leader_role = leader_role_result.scalar_one_or_none()

    if not team_leader_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rol TEAM_LEADER no configurado en el sistema"
        )

    if user.role_id == team_leader_role.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya es líder de equipo"
        )

    try:
        user.role_id = team_leader_role.id
        # Get the TEAM_LEADER role from database
        role_result = await db.execute(
            select(Role).where(Role.name == UserRole.TEAM_LEADER.value)
        )
        team_leader_role = role_result.scalar_one()
        user.role = team_leader_role
        await db.commit()
        await db.refresh(user, attribute_names=['role'])

        return UserResponse.model_validate(user)

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
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
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
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id)
    )
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    # Buscar TEAM_LEADER y DEVELOPER en BD para comparar y asignar por FK
    leader_role_result = await db.execute(
        select(Role).where(Role.name == UserRole.TEAM_LEADER)
    )
    team_leader_role = leader_role_result.scalar_one_or_none()

    if not team_leader_role or user.role_id != team_leader_role.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no es líder de equipo"
        )

    dev_role_result = await db.execute(
        select(Role).where(Role.name == UserRole.DEVELOPER)
    )
    developer_role = dev_role_result.scalar_one_or_none()

    try:
        user.role_id = developer_role.id
        await db.commit()
        await db.refresh(user, attribute_names=['role'])

        return UserResponse.model_validate(user)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al degradar usuario: {str(e)}"
        )


@router.post(
    "/{user_id}/change-role",
    response_model=UserResponse,
    summary="Cambiar rol de usuario",
    description="Cambia el rol de un usuario (requiere ADMIN)"
)
async def change_user_role(
    user_id: str,
    role_data: ChangeRoleRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Cambia el rol de un usuario a uno especificado.

    Args:
        user_id (int): ID del usuario cuyo rol se va a cambiar
        role_data (ChangeRoleRequest): Datos con el nuevo rol
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        UserResponse: Usuario con rol actualizado

    Raises:
        HTTPException: Si el usuario no existe (404) o el rol es inválido (400)
    """
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id)
    )
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )

    # Validar que el nuevo rol sea válido
    valid_roles = {UserRole.ADMIN, UserRole.TEAM_LEADER, UserRole.DEVELOPER}
    if role_data.role not in [r.value for r in valid_roles]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Roles válidos: {', '.join(r.value for r in valid_roles)}"
        )

    try:
        # Get the role from database
        role_result = await db.execute(
            select(Role).where(Role.name == role_data.role)
        )
        new_role = role_result.scalar_one()
        user.role = new_role
        await db.commit()
        await db.refresh(user, attribute_names=['role'])

        return UserResponse.model_validate(user)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al cambiar rol: {str(e)}"
        )


@router.get(
    "/{user_id}/stats",
    summary="Obtener estadísticas del usuario",
    description="Retorna métricas de desempeño y actividad del usuario"
)
async def get_user_stats(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict[str, int | str | None]:
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
    completed_result = await db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.assignee_id == user_id,
            Ticket.status == TicketStatus.COMPLETED
        )
    )
    completed_count = int(completed_result.scalar() or 0)

    # Contar tickets en progreso
    in_progress_result = await db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.assignee_id == user_id,
            Ticket.status == TicketStatus.IN_PROGRESS
        )
    )
    in_progress_count = int(in_progress_result.scalar() or 0)

    # Contar tickets bloqueados
    blocked_result = await db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.assignee_id == user_id,
            Ticket.status == TicketStatus.BLOCKED
        )
    )
    blocked_count = int(blocked_result.scalar() or 0)

    # Contar eventos (actividad) del usuario
    activity_result = await db.execute(
        select(func.count(TicketEvent.id)).where(
            TicketEvent.user_id == user_id
        )
    )
    activity_count = int(activity_result.scalar() or 0)

    return {
        "user_id": user_id,
        "completed_tickets": completed_count,
        "in_progress_tickets": in_progress_count,
        "blocked_tickets": blocked_count,
        "total_activity": activity_count,
        "join_date": user.created_at.isoformat() if user.created_at else None
    }


def _generate_temporary_password(length: int = 16) -> str:
    """
    Genera una contraseña temporal aleatoria que cumple la política de
    validación de AuthService._validate_password (mayúscula, minúscula,
    dígito y símbolo).
    """
    alphabet = string.ascii_letters + string.digits
    body = "".join(secrets.choice(alphabet) for _ in range(length - 4))
    # Se garantizan las cuatro clases de carácter exigidas, en posiciones
    # aleatorias, para no sesgar el prefijo de todas las contraseñas emitidas.
    forced = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()"),
    ]
    chars = list(body) + forced
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


@router.post(
    "/{user_id}/reset-password",
    response_model=AdminPasswordResetResponse,
    summary="Resetear la contraseña de un usuario",
    description=(
        "Genera una contraseña temporal aleatoria para el usuario indicado y "
        "marca must_change_password. Solo ADMIN. La contraseña se devuelve "
        "una única vez en esta respuesta."
    ),
)
async def reset_user_password(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
) -> AdminPasswordResetResponse:
    """
    Antes no existía ninguna forma de fijar o resetear la contraseña de un
    usuario desde la aplicación (plan 3.8): team.addMember mandaba una
    contraseña fija ('TemporaryPassword123!') para todo el mundo, y
    requestPasswordReset lanzaba 'no implementada'. Quien olvidaba su clave
    necesitaba que alguien entrara a Postgres a mano.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado",
        )

    temporary_password = _generate_temporary_password()
    user.hashed_password = AuthService.hash_password(temporary_password)
    user.must_change_password = True
    await db.commit()

    return AdminPasswordResetResponse(user_id=user.id, temporary_password=temporary_password)
