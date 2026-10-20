"""
Tests unitarios de autenticación: get_current_user, auth_service y las
funciones de routers/auth.py llamadas directamente (sin HTTP).

Cubre los cambios de seguridad recientes:
  - verify_token solo acepta access tokens (ver test_rbac.py) y
    verify_refresh_token solo refresh tokens.
  - get_current_user carga el usuario desde la BD: rechaza usuarios
    inexistentes o inactivos y devuelve el rol de la BD, no el del token.
  - create_user no deduce el rol del correo (admin@... sigue siendo DEVELOPER).
  - PUT /auth/me (UserSelfUpdate) no permite cambiar rol ni email.
"""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.middleware.auth import get_current_user, hash_password, verify_token
from app.models import User, UserRole
from app.routers import auth as auth_router
from app.schemas import UserLogin, UserRegister, UserSelfUpdate
from app.services import auth_service

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


async def make_user(
    db: AsyncSession,
    role: UserRole = UserRole.DEVELOPER,
    is_active: bool = True,
    email: str | None = None,
    password: str = "Secreta123!",
) -> User:
    user = User(
        email=email or f"{uuid4()}@test.com",
        full_name="Usuario de prueba",
        hashed_password=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    await db.flush()
    return user


def bearer(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def decode(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# ─────────────────────────────────────────────────────────────────────────────
# get_current_user
# ─────────────────────────────────────────────────────────────────────────────

class TestGetCurrentUser:

    async def test_usuario_activo_devuelve_payload(self, db_session: AsyncSession):
        user = await make_user(db_session, role=UserRole.GROUP_LEADER)
        token = auth_service.create_access_token(user.id, user.role)

        current = await get_current_user(credentials=bearer(token), db=db_session)

        assert current.sub == str(user.id)
        assert current.role == "GROUP_LEADER"

    async def test_rol_viene_de_la_bd_no_del_token(self, db_session: AsyncSession):
        # Token emitido cuando era ADMIN; después se le degradó a DEVELOPER
        user = await make_user(db_session, role=UserRole.DEVELOPER)
        token = auth_service.create_access_token(user.id, UserRole.ADMIN)
        assert verify_token(token).role == "ADMIN"

        current = await get_current_user(credentials=bearer(token), db=db_session)
        assert current.role == "DEVELOPER"

    async def test_usuario_inactivo_lanza_401(self, db_session: AsyncSession):
        user = await make_user(db_session, is_active=False)
        token = auth_service.create_access_token(user.id, user.role)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=bearer(token), db=db_session)
        assert exc.value.status_code == 401

    async def test_usuario_inexistente_lanza_401(self, db_session: AsyncSession):
        token = auth_service.create_access_token(uuid4(), UserRole.ADMIN)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=bearer(token), db=db_session)
        assert exc.value.status_code == 401

    async def test_sub_no_uuid_lanza_401_sin_consultar_la_bd(self):
        token = auth_service.create_access_token("no-es-un-uuid", UserRole.ADMIN)
        db = MagicMock()
        db.execute = AsyncMock()

        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=bearer(token), db=db)
        assert exc.value.status_code == 401
        db.execute.assert_not_awaited()

    async def test_refresh_token_como_bearer_lanza_401(self, db_session: AsyncSession):
        user = await make_user(db_session)
        token = auth_service.create_refresh_token(user.id, user.role)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials=bearer(token), db=db_session)
        assert exc.value.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# auth_service: tokens
# ─────────────────────────────────────────────────────────────────────────────

class TestAuthServiceTokens:

    def test_access_token_lleva_type_access_y_rol(self):
        user_id = uuid4()
        payload = decode(auth_service.create_access_token(user_id, UserRole.GROUP_LEADER))
        assert payload["sub"] == str(user_id)
        assert payload["role"] == "GROUP_LEADER"
        assert payload["type"] == "access"

    def test_refresh_token_lleva_type_refresh(self):
        payload = decode(auth_service.create_refresh_token(uuid4(), UserRole.ADMIN))
        assert payload["type"] == "refresh"

    def test_rol_none_se_emite_como_developer(self):
        payload = decode(auth_service.create_access_token(uuid4(), None))
        assert payload["role"] == "DEVELOPER"

    async def test_verify_refresh_token_valido_devuelve_sub(self):
        user_id = uuid4()
        token = auth_service.create_refresh_token(user_id, UserRole.DEVELOPER)
        assert await auth_service.verify_refresh_token(token) == str(user_id)

    async def test_verify_refresh_token_rechaza_access_token(self):
        token = auth_service.create_access_token(uuid4(), UserRole.ADMIN)
        assert await auth_service.verify_refresh_token(token) is None

    @pytest.mark.parametrize("token", [None, "", "basura.no.jwt"])
    async def test_verify_refresh_token_invalido_devuelve_none(self, token):
        assert await auth_service.verify_refresh_token(token) is None

    async def test_verify_refresh_token_expirado_devuelve_none(self):
        from app.middleware.auth import create_access_token

        expired = create_access_token(
            {"sub": str(uuid4()), "role": "ADMIN", "type": "refresh"},
            expires_delta=timedelta(seconds=-1),
        )
        assert await auth_service.verify_refresh_token(expired) is None

    async def test_verify_refresh_token_sin_sub_devuelve_none(self):
        from app.middleware.auth import create_refresh_token

        assert await auth_service.verify_refresh_token(
            create_refresh_token({"role": "ADMIN", "type": "refresh"})
        ) is None


class TestAuthServicePasswords:

    def test_verify_password_correcta(self):
        assert auth_service.verify_password("abc12345", auth_service.hash_password("abc12345"))

    @pytest.mark.parametrize("plain,hashed", [("", "x"), ("x", ""), ("x", "hash-corrupto")])
    def test_verify_password_entradas_invalidas_no_lanzan(self, plain, hashed):
        assert auth_service.verify_password(plain, hashed) is False


# ─────────────────────────────────────────────────────────────────────────────
# auth_service.create_user
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateUser:

    async def test_rol_por_defecto_developer(self, db_session: AsyncSession):
        data = UserRegister(email="nuevo@test.com", full_name="Nuevo", password="Password1!")
        user = await auth_service.create_user(db_session, data)

        assert user.role == UserRole.DEVELOPER
        assert user.is_active is True
        assert user.id is not None  # hace flush

    @pytest.mark.parametrize("email", ["admin@corestream.com", "leader@corestream.com", "Admin@X.com"])
    async def test_no_deduce_el_rol_del_email(self, db_session: AsyncSession, email):
        data = UserRegister(email=email, full_name="X", password="Password1!")
        user = await auth_service.create_user(db_session, data)
        assert user.role == UserRole.DEVELOPER

    async def test_esquema_de_registro_ignora_un_rol_enviado(self, db_session: AsyncSession):
        # UserRegister no tiene campo `role`: un cliente no puede autoasignarse ADMIN
        data = UserRegister(email="x@test.com", full_name="X", password="Password1!", role="ADMIN")
        assert not hasattr(data, "role")
        user = await auth_service.create_user(db_session, data)
        assert user.role == UserRole.DEVELOPER

    async def test_rol_desconocido_cae_a_developer(self, db_session: AsyncSession):
        data = SimpleNamespace(email="x@test.com", full_name="X", password="Password1!", role="ROOT")
        user = await auth_service.create_user(db_session, data)
        assert user.role == UserRole.DEVELOPER

    async def test_email_normalizado_y_password_hasheada(self, db_session: AsyncSession):
        data = UserRegister(email="Mixto@Test.COM", full_name="X", password="Password1!")
        user = await auth_service.create_user(db_session, data)

        assert user.email == "mixto@test.com"
        assert user.hashed_password != "Password1!"
        assert auth_service.verify_password("Password1!", user.hashed_password)

    def test_password_corta_rechazada_por_el_esquema(self):
        with pytest.raises(ValueError):
            UserRegister(email="x@test.com", full_name="X", password="corta")


# ─────────────────────────────────────────────────────────────────────────────
# routers/auth.py — llamadas directas a las funciones del router
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def no_rate_limit():
    """El rate limit de login usa Redis: se sustituye por AsyncMock."""
    with patch.object(auth_router, "rate_limit_login", new=AsyncMock()) as rl, \
         patch.object(auth_router, "record_failed_login", new=AsyncMock()) as failed:
        yield SimpleNamespace(rate_limit=rl, record_failed=failed)


class TestLogin:

    async def test_login_correcto_emite_access_y_refresh(self, db_session, no_rate_limit):
        user = await make_user(db_session, role=UserRole.GROUP_LEADER, password="Clave1234!")
        result = await auth_router.login(
            UserLogin(email=user.email, password="Clave1234!"), MagicMock(), db_session
        )

        access = decode(result.access_token)
        refresh = decode(result.refresh_token)
        assert (access["type"], refresh["type"]) == ("access", "refresh")
        assert access["sub"] == refresh["sub"] == str(user.id)
        assert access["role"] == "GROUP_LEADER"
        no_rate_limit.rate_limit.assert_awaited_once()
        no_rate_limit.record_failed.assert_not_awaited()

    async def test_password_incorrecta_401_y_registra_fallo(self, db_session, no_rate_limit):
        user = await make_user(db_session, password="Clave1234!")
        with pytest.raises(HTTPException) as exc:
            await auth_router.login(
                UserLogin(email=user.email, password="otra"), MagicMock(), db_session
            )
        assert exc.value.status_code == 401
        no_rate_limit.record_failed.assert_awaited_once()

    async def test_email_inexistente_401(self, db_session, no_rate_limit):
        with pytest.raises(HTTPException) as exc:
            await auth_router.login(
                UserLogin(email="nadie@test.com", password="x"), MagicMock(), db_session
            )
        assert exc.value.status_code == 401
        no_rate_limit.record_failed.assert_awaited_once()

    async def test_usuario_inactivo_403(self, db_session, no_rate_limit):
        user = await make_user(db_session, is_active=False, password="Clave1234!")
        with pytest.raises(HTTPException) as exc:
            await auth_router.login(
                UserLogin(email=user.email, password="Clave1234!"), MagicMock(), db_session
            )
        assert exc.value.status_code == 403


def db_returning(user) -> MagicMock:
    """
    Sesión simulada cuyo execute() devuelve `user`. Se usa en /refresh porque
    el router filtra por User.id con el `sub` como str, que asyncpg acepta pero
    el tipo UUID sobre SQLite no.
    """
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db = MagicMock()
    db.execute = AsyncMock(return_value=result)
    return db


class TestRefresh:

    async def test_refresh_valido_emite_nuevo_access_con_rol_de_bd(self):
        user = SimpleNamespace(id=uuid4(), role=UserRole.DEVELOPER, is_active=True)
        refresh = auth_service.create_refresh_token(user.id, UserRole.ADMIN)

        result = await auth_router.refresh_token({"refresh_token": refresh}, db_returning(user))

        access = decode(result.access_token)
        assert access["type"] == "access"
        assert access["role"] == "DEVELOPER"
        assert result.refresh_token == refresh

    async def test_access_token_como_refresh_401(self):
        user = SimpleNamespace(id=uuid4(), role=UserRole.ADMIN, is_active=True)
        access = auth_service.create_access_token(user.id, user.role)
        db = db_returning(user)

        with pytest.raises(HTTPException) as exc:
            await auth_router.refresh_token({"refresh_token": access}, db)
        assert exc.value.status_code == 401
        db.execute.assert_not_awaited()

    @pytest.mark.parametrize(
        "user", [None, SimpleNamespace(id=uuid4(), role=UserRole.ADMIN, is_active=False)]
    )
    async def test_usuario_inexistente_o_inactivo_401(self, user):
        refresh = auth_service.create_refresh_token(uuid4(), UserRole.ADMIN)
        with pytest.raises(HTTPException) as exc:
            await auth_router.refresh_token({"refresh_token": refresh}, db_returning(user))
        assert exc.value.status_code == 401

    async def test_sin_refresh_token_401(self):
        with pytest.raises(HTTPException) as exc:
            await auth_router.refresh_token({}, db_returning(None))
        assert exc.value.status_code == 401


class TestSelfUpdate:

    def test_esquema_no_tiene_role_ni_email_ni_password(self):
        assert set(UserSelfUpdate.model_fields) == {"full_name", "specialty", "avatar_url"}

    def test_campos_extra_se_descartan(self):
        data = UserSelfUpdate(full_name="Nuevo", role="ADMIN", email="otro@test.com", is_active=False)
        assert data.model_dump(exclude_unset=True) == {"full_name": "Nuevo"}

    async def test_put_me_no_puede_escalar_rol_ni_cambiar_email(self, db_session: AsyncSession):
        user = await make_user(db_session, role=UserRole.DEVELOPER, email="dev@test.com")
        await db_session.commit()
        current = SimpleNamespace(sub=str(user.id), role="DEVELOPER")

        payload = UserSelfUpdate(
            full_name="Nombre Nuevo", specialty="Backend", role="ADMIN", email="admin@test.com"
        )
        response = await auth_router.update_current_user_profile(payload, current, db_session)

        assert response.full_name == "Nombre Nuevo"
        assert response.specialty == "Backend"
        stored = (await db_session.execute(select(User).where(User.id == user.id))).scalar_one()
        assert stored.role == UserRole.DEVELOPER
        assert stored.email == "dev@test.com"

    async def test_get_me_devuelve_el_usuario_del_token(self, db_session: AsyncSession):
        user = await make_user(db_session)
        current = SimpleNamespace(sub=str(user.id), role="DEVELOPER")

        response = await auth_router.get_current_user_profile(current, db_session)
        assert response.id == user.id
        assert response.email == user.email

    async def test_get_me_usuario_borrado_404(self, db_session: AsyncSession):
        current = SimpleNamespace(sub=str(uuid4()), role="DEVELOPER")
        with pytest.raises(HTTPException) as exc:
            await auth_router.get_current_user_profile(current, db_session)
        assert exc.value.status_code == 404
