"""
Router de Autenticación y Autorización.

Gestiona todos los endpoints relacionados con:
- Registro de nuevos usuarios
- Login y generación de tokens JWT
- Refresco de tokens de acceso
- Gestión del perfil del usuario actual
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, TokenResponse, UserRegister, UserLogin, UserUpdate
from app.services import auth_service
from app.middleware.auth import get_current_user

# Creación del router con prefijo y etiqueta para documentación automática
router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario con email y contraseña"
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Registra un nuevo usuario en el sistema.

    Args:
        user_data (UserRegister): Datos del usuario a registrar (email, contraseña, nombre)
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        UserResponse: Objeto con los datos del usuario creado

    Raises:
        HTTPException: Si el email ya existe (estado 409)
    """
    # Verificar si el usuario ya existe en la base de datos
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado"
        )

    # Crear nuevo usuario con contraseña hasheada
    new_user = await auth_service.create_user(db, user_data)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse.from_orm(new_user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Autentica un usuario y devuelve tokens JWT"
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Autentica un usuario y genera tokens de acceso.

    Args:
        credentials (UserLogin): Email y contraseña del usuario
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TokenResponse: Contiene access_token y refresh_token

    Raises:
        HTTPException: Si las credenciales son inválidas (estado 401)
    """
    # Buscar el usuario por email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()

    # Validar que el usuario existe y la contraseña es correcta
    if not user or not auth_service.verify_password(
        credentials.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generar tokens JWT
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refrescar token de acceso",
    description="Genera un nuevo access_token usando un refresh_token válido"
)
async def refresh_token(
    token_data: dict,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Refresca el token de acceso usando un refresh_token.

    Args:
        token_data (dict): Contiene el refresh_token
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TokenResponse: Nuevo access_token

    Raises:
        HTTPException: Si el refresh_token es inválido (estado 401)
    """
    # Validar y extraer información del refresh_token
    user_id = await auth_service.verify_refresh_token(token_data.get("refresh_token"))

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verificar que el usuario aún existe
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    # Generar nuevo access_token
    new_access_token = auth_service.create_access_token(user_id)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=token_data.get("refresh_token"),
        token_type="bearer",
        expires_in=3600
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil del usuario actual",
    description="Devuelve los datos del usuario autenticado"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Obtiene el perfil del usuario autenticado actualmente.

    Args:
        current_user (User): Usuario autenticado (inyectado por dependencia)
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        UserResponse: Datos del usuario autenticado
    """
    # Refrescar datos del usuario desde la BD para garantizar información actualizada
    await db.refresh(current_user)
    return UserResponse.from_orm(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Actualizar perfil del usuario actual",
    description="Permite al usuario modificar su propia información (nombre, avatar, etc.)"
)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Actualiza el perfil del usuario autenticado.

    Args:
        user_update (UserUpdate): Datos a actualizar (nombre, avatar, etc.)
        current_user (User): Usuario autenticado (inyectado por dependencia)
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        UserResponse: Datos actualizados del usuario

    Raises:
        HTTPException: Si la actualización falla (estado 400)
    """
    try:
        # Actualizar únicamente los campos proporcionados
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)

        await db.commit()
        await db.refresh(current_user)

        return UserResponse.from_orm(current_user)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el perfil: {str(e)}"
        )
