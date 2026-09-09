# Archivo de autenticación y autorización
# Proporciona funciones para crear tokens JWT, verificarlos y usar como dependencias FastAPI

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.redis_client import is_jti_revoked
from app.schemas import TokenPayload

# Esquema de seguridad Bearer para extraer tokens JWT del header Authorization
security = HTTPBearer()


def hash_password(password: str) -> str:
    """
    Hash una contraseña en texto plano.

    Delega en AuthService.hash_password (import diferido: evita un import
    circular, ya que app.services.auth_service importa de este módulo).

    Antes esta función hacía un bcrypt liso con pwd_context.hash(password)
    directamente, DISTINTO del hash que usa AuthService (que antepone un
    pre-hash SHA-256 para no truncar contraseñas largas contra el límite de
    72 bytes de bcrypt). El login siempre verificó contra el esquema de
    AuthService — cualquier contraseña hasheada con la versión antigua de
    esta función jamás podía volver a verificarse. Afectaba a create_admin.py,
    POST /api/users/ y el reseteo de contraseña de admin; se detectó porque
    el propio bootstrap del primer ADMIN fallaba con "credenciales incorrectas"
    usando la contraseña que él mismo acababa de crear.

    Args:
        password: Contraseña en texto plano a hashear

    Returns:
        str: Hash seguro de la contraseña
    """
    from app.services.auth_service import AuthService

    return AuthService.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que una contraseña en texto plano coincida con su hash.

    Delega en AuthService.verify_password por el mismo motivo que hash_password.
    """
    from app.services.auth_service import AuthService

    return AuthService.verify_password(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Crea un token JWT de acceso firmado, de vida corta.

    Args:
        data: Diccionario con datos a incluir en el token (ej: {"sub": user_id, "role": "admin"})
        expires_delta: Duración del token desde ahora (si es None, usa el valor por defecto de configuración)

    Returns:
        str: Token JWT codificado en formato string
    """
    return _create_token(
        data,
        token_type="access",
        expire=datetime.now(timezone.utc)
        + (expires_delta or timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)),
    )


def create_refresh_token(data: dict) -> str:
    """
    Crea un token JWT de refresco, de vida larga.

    Los tokens de refresco se utilizan para obtener nuevos access tokens
    sin requerer que el usuario vuelva a proporcionar sus credenciales.
    """
    settings = get_settings()
    return _create_token(
        data,
        token_type="refresh",
        expire=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def _create_token(data: dict, *, token_type: str, expire: datetime) -> str:
    """
    Firma un JWT con claims comunes a access y refresh.

    Añade dos claims que antes no existían y que son la causa de que un
    refresh token de 7 días colara como access token (plan 3.1):

      - type: "access" | "refresh" — verify_token() exige el tipo esperado
        según dónde se use el token, así uno nunca sirve para el otro.
      - jti:  identificador único del token — permite revocar UN token
        concreto en logout (plan 3.3) sin tener que invalidar toda la clave
        de firma ni mantener una lista de todos los tokens emitidos.
    """
    settings = get_settings()
    to_encode = data.copy()
    to_encode.update({
        "exp": expire,
        "type": token_type,
        "jti": uuid.uuid4().hex,
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def verify_token(token: str, expected_type: str = "access") -> TokenPayload:
    """
    Verifica, decodifica y valida el tipo de un token JWT.

    Args:
        token: Token JWT a verificar
        expected_type: "access" o "refresh" — el token debe declarar
            exactamente este tipo, o se rechaza aunque la firma sea válida.
            Esto es lo que impide que un refresh token (7 días) se use como
            access token, o viceversa.

    Returns:
        TokenPayload: Datos extraídos del token (sub, role, exp, type, jti)

    Raises:
        HTTPException 401: Si el token es inválido, expirado, del tipo
            equivocado, o fue revocado explícitamente (logout).
    """
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    role = payload.get("role")
    exp = payload.get("exp")
    jti = payload.get("jti")
    token_type = payload.get("type")

    if sub is None or role is None or exp is None or jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: faltan campos requeridos",
        )

    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Se esperaba un token de tipo '{expected_type}'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if await is_jti_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token fue revocado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenPayload(sub=sub, role=role, exp=exp, type=token_type, jti=jti)


async def get_access_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """
    Dependencia que extrae y valida el access token del header Authorization,
    sin tocar la base de datos.

    Separada de get_current_user para que /auth/logout pueda revocar el jti
    del token actual sin necesitar cargar el User completo.
    """
    return await verify_token(credentials.credentials, expected_type="access")


async def get_current_user(
    token_data: TokenPayload = Depends(get_access_token_payload),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependencia FastAPI que resuelve el usuario autenticado a partir del
    access token. Se utiliza en endpoints protegidos para verificar
    autenticación.

    Raises:
        HTTPException 401: Si el token es inválido, o el usuario ya no existe
    """
    from uuid import UUID

    try:
        user_id = UUID(token_data.sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: ID de usuario mal formado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def _normalize_role_value(role: object) -> str:
    """Normaliza diferentes representaciones de rol a texto en mayúsculas."""
    if role is None:
        return ""

    if hasattr(role, "name"):
        value = role.name
    elif hasattr(role, "value"):
        value = role.value
    else:
        value = role

    return str(value).upper()


def require_role(required_roles: list[str] | str):
    """
    Factory que crea una dependencia para verificar que el usuario tiene uno de los roles requeridos.

    Ejemplo:
        @app.delete("/users/{user_id}")
        async def delete_user(
            user_id: UUID,
            current_user: User = Depends(require_role(["admin"])),
        ):
            ...
    """
    normalized_required_roles = {
        _normalize_role_value(role)
        for role in (required_roles if isinstance(required_roles, (list, tuple, set)) else [required_roles])
    }

    async def verify_role(current_user: User = Depends(get_current_user)) -> User:
        role_obj = getattr(current_user, "role", None)
        if role_obj is None:
            user_role = ""
        elif hasattr(role_obj, "value"):
            user_role = str(role_obj.value)
        elif hasattr(role_obj, "name"):
            user_role = str(role_obj.name)
        else:
            user_role = str(role_obj)

        if user_role not in normalized_required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Se requiere uno de estos roles: "
                    + ", ".join(sorted(normalized_required_roles))
                ),
            )

        return current_user

    return verify_role
