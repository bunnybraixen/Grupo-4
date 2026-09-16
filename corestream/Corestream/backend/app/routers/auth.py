"""
Router de Autenticación y Autorización.

Gestiona:
- Login y generación de tokens JWT
- Refresco de tokens de acceso (rotación del refresh token)
- Cierre de sesión con revocación real
- Gestión del perfil del usuario actual
- Intercambio de un ticket de un solo uso para el handshake del WebSocket

El registro público (POST /auth/register) se eliminó: se sustituyó por
invitaciones por enlace (ver app/routers/invitations.py, plan 3.7). Un SaaS
interno bajo un dominio público no debe dejar que cualquiera se cree una
cuenta.
"""

import secrets
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import get_access_token_payload, get_current_user
from app.middleware.rate_limit import rate_limit_login
from app.models import Role, User
from app.redis_client import create_ws_ticket, revoke_jti
from app.schemas import (
    LogoutRequest,
    RefreshRequest,
    TokenPayload,
    TokenResponse,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from app.schemas.user import PasswordChange
from app.services.auth_service import AuthService

router = APIRouter(tags=["Autenticación"])

REFRESH_COOKIE_NAME = "refresh_token"
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "x-csrf-token"

# El refresh token no tiene motivo para viajar en cada petición a la API
# (eso es justamente lo que hacía localStorage + Authorization en todas
# partes, el problema que esto reemplaza) — el navegador solo lo adjunta en
# peticiones a esta ruta.
_REFRESH_COOKIE_PATH = "/api/auth"

# csrf_token, en cambio, DEBE ser legible por el JS de la SPA desde
# cualquier página (document.cookie) para poder mandarlo de vuelta como
# cabecera. Un cookie solo es visible vía document.cookie en páginas cuyo
# path coincide con el Path del cookie o es subdirectorio suyo — con
# Path=/api/auth (el valor de antes, copiado sin pensar del refresh token)
# la SPA, servida en "/", nunca podía leerlo: refresh() mandaba siempre la
# cabecera vacía y el backend rechazaba TODO refresh con 403, en cualquier
# navegador real, no solo en tests. Detectado recargando la página tras un
# login real y mirando qué cabecera llegaba de verdad al backend.
_CSRF_COOKIE_PATH = "/"


def _cookie_secure() -> bool:
    """
    Secure exige HTTPS. En local (http://localhost) tiene que ir en False o
    el navegador descarta la cookie silenciosamente y el login "funciona"
    pero el refresh nunca encuentra la cookie.
    """
    return get_settings().ENVIRONMENT == "production"


def _set_auth_cookies(response: Response, *, refresh_token: str, csrf_token: str) -> None:
    secure = _cookie_secure()
    max_age = get_settings().REFRESH_TOKEN_EXPIRE_DAYS * 86_400

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=max_age,
        path=_REFRESH_COOKIE_PATH,
        httponly=True,
        secure=secure,
        samesite="strict",
    )
    # csrf_token NO es httponly: el frontend debe poder leerlo para mandarlo
    # de vuelta como cabecera (patrón de doble envío).
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        max_age=max_age,
        path=_CSRF_COOKIE_PATH,
        httponly=False,
        secure=secure,
        samesite="strict",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE_NAME, path=_REFRESH_COOKIE_PATH)
    response.delete_cookie(CSRF_COOKIE_NAME, path=_CSRF_COOKIE_PATH)


def _verify_csrf(request: Request) -> None:
    """
    Doble envío: la cookie csrf_token y la cabecera X-CSRF-Token deben
    coincidir. Solo se exige en /refresh cuando el refresh token llega por
    cookie (no cuando un cliente no-navegador lo manda explícito en el
    cuerpo, donde no hay cookie de la que abusar). /logout no lo necesita:
    ya exige un Bearer access token válido, que un atacante CSRF no puede
    leer ni adjuntar por su cuenta — la cookie ahí solo decide QUÉ refresh
    token revocar, no autoriza nada por sí sola.
    """
    cookie_value = request.cookies.get(CSRF_COOKIE_NAME)
    header_value = request.headers.get(CSRF_HEADER_NAME)

    if not cookie_value or not header_value or not secrets.compare_digest(cookie_value, header_value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token CSRF inválido o ausente",
        )


def _remaining_seconds(exp: int) -> int:
    return max(0, exp - int(datetime.now(timezone.utc).timestamp()))


async def _to_user_response(db: AsyncSession, user: User) -> UserResponse:
    """Construye UserResponse evitando lazy-load async de user.role."""
    role_name = "DEVELOPER"
    if user.role_id:
        role_result = await db.execute(select(Role).where(Role.id == user.role_id))
        role = role_result.scalar_one_or_none()
        if role:
            role_name = role.name

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        specialty=user.specialty,
        role=role_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        created_at=user.created_at,
        preferences=user.preferences,
        must_change_password=user.must_change_password,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Autentica un usuario, entrega el access token en el cuerpo y el refresh token en una cookie httpOnly",
)
async def login(
    login_data: UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Autentica un usuario y genera tokens de acceso.

    El refresh_token YA NO viaja en el cuerpo de la respuesta (plan 3.2):
    se entrega como cookie HttpOnly, así que un script en la página nunca
    puede leerlo. El access_token sí va en el cuerpo — el frontend lo
    mantiene en memoria (nunca en localStorage) y lo usa como Bearer.
    """
    await rate_limit_login(request, login_data.email)

    email_search = login_data.email.lower()

    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.email == email_search)
    )
    user = result.unique().scalar_one_or_none()

    if not user or not AuthService.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada",
        )

    role_name = user.role.name if user.role else "DEVELOPER"
    access_token = AuthService.create_access_token(user, role_name=role_name)
    refresh_token = AuthService.create_refresh_token(user)
    csrf_token = secrets.token_urlsafe(32)

    _set_auth_cookies(response, refresh_token=refresh_token, csrf_token=csrf_token)

    settings = get_settings()
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        must_change_password=user.must_change_password,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refrescar token de acceso",
    description="Genera un nuevo access_token y rota el refresh_token (cookie httpOnly)",
)
async def refresh_token_endpoint(
    request: Request,
    response: Response,
    body: Optional[RefreshRequest] = None,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Refresca el token de acceso.

    El refresh token se lee de la cookie httpOnly, no del cuerpo — por eso
    esta ruta exige el token CSRF de doble envío. Se acepta refresh_token en
    el cuerpo como alternativa solo para clientes no-navegador (scripts,
    tests); en ese caso no se exige CSRF, porque no hay cookie de la que
    abusar.

    Rota el refresh token en cada uso: el que se acaba de consumir se revoca,
    y se emite uno nuevo. Si alguien roba un refresh token y lo usa, el
    usuario legítimo lo notará en su siguiente intento (token revocado) en
    vez de que el atacante conserve acceso indefinido en silencio.
    """
    cookie_token = request.cookies.get(REFRESH_COOKIE_NAME)
    raw_token = cookie_token or (body.refresh_token if body else None)

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó refresh_token",
        )

    if cookie_token:
        _verify_csrf(request)

    token_data: TokenPayload | None = await AuthService.verify_refresh_token(raw_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(User, Role.name).join(Role, User.role_id == Role.id).where(User.id == token_data.sub)
    )
    row = result.first()
    user, role_name = (row[0], row[1]) if row else (None, None)

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    # Revocar el refresh token consumido antes de emitir el siguiente.
    await revoke_jti(token_data.jti, _remaining_seconds(token_data.exp))

    new_access_token = AuthService.create_access_token(user, role_name=role_name)

    if cookie_token:
        new_refresh_token = AuthService.create_refresh_token(user, role_name=role_name)
        new_csrf_token = secrets.token_urlsafe(32)
        _set_auth_cookies(response, refresh_token=new_refresh_token, csrf_token=new_csrf_token)

    settings = get_settings()
    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        must_change_password=user.must_change_password,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión",
    description="Revoca el access token y el refresh token actuales y limpia las cookies",
)
async def logout(
    request: Request,
    response: Response,
    body: Optional[LogoutRequest] = None,
    token_data: TokenPayload = Depends(get_access_token_payload),
) -> dict:
    """
    Antes este endpoint no existía (404) y el frontend lo llamaba igual,
    tragándose el error: "cerrar sesión" solo borraba localStorage, el
    access token seguía siendo válido hasta que expirase por su cuenta
    (plan 3.3). Ahora revoca explícitamente ambos jti.
    """
    await revoke_jti(token_data.jti, _remaining_seconds(token_data.exp))

    cookie_token = request.cookies.get(REFRESH_COOKIE_NAME)
    raw_refresh = cookie_token or (body.refresh_token if body else None)
    if raw_refresh:
        refresh_payload = await AuthService.verify_refresh_token(raw_refresh)
        if refresh_payload:
            await revoke_jti(refresh_payload.jti, _remaining_seconds(refresh_payload.exp))

    _clear_auth_cookies(response)
    return {"message": "Sesión cerrada"}


@router.post(
    "/ws-ticket",
    status_code=status.HTTP_200_OK,
    summary="Obtener ticket de un solo uso para el WebSocket",
    description=(
        "Cambia el access token actual por un ticket opaco de vida muy corta "
        "(15s) para abrir el WebSocket sin exponer el JWT en el query string"
    ),
)
async def get_ws_ticket(current_user: User = Depends(get_current_user)) -> dict:
    """
    El JWT en el query string del WebSocket queda escrito en los logs de
    acceso de cualquier proxy delante de la app (plan 3.2). Este ticket es
    aleatorio, de un solo uso y expira en 15s — aunque termine en un log,
    ya está consumido para cuando alguien lo lea.
    """
    ticket = await create_ws_ticket(str(current_user.id))
    return {"ticket": ticket}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil del usuario actual",
    description="Devuelve los datos del usuario autenticado",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    await db.refresh(current_user)
    return await _to_user_response(db, current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Actualizar perfil del usuario actual",
    description="Permite al usuario modificar su propia información (nombre, avatar, etc.)",
)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    try:
        update_data = user_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(current_user, field, value)

        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)

        return await _to_user_response(db, current_user)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar el perfil: {str(e)}",
        )


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Cambiar contraseña",
    description="Permite al usuario autenticado cambiar su propia contraseña",
)
async def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    await AuthService.change_password(
        db=db,
        user_id=str(current_user.id),
        old_password=payload.old_password,
        new_password=payload.new_password,
    )
    return {"message": "Contraseña actualizada exitosamente"}
