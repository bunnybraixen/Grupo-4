"""
Tests unitarios para RBAC y JWT: app/middleware/rbac.py y app/middleware/auth.py.

Funciones puras (sin DB). La carga del usuario desde BD en get_current_user,
el refresh token y el flujo de login se prueban en tests/test_auth.py.

NOTA: la versión anterior importaba `_normalize_role_value` de
app.middleware.auth (ya no existe) y probaba require_role con objetos de rol
que exponían .value/.name. Hoy require_role recibe siempre el TokenPayload de
get_current_user, cuyo `role` es un str con el valor de la BD.
"""

import base64
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import get_settings
from app.middleware.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    require_role,
    verify_password,
    verify_token,
)
from app.middleware.rbac import (
    RBACRole,
    _extract_current_role,
    _normalize_role,
    require_permissions,
)
from app.models.user import UserRole
from app.routers.documents import _normalize_role as normalize_document_role

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def encode(payload: dict, key: str | None = None) -> str:
    settings = get_settings()
    return jwt.encode(payload, key or settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def base64url(data: dict) -> str:
    raw = json.dumps(data).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def future(hours: int = 1) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=hours)


def token_user(role: str) -> SimpleNamespace:
    """Doble de TokenPayload (lo que entrega get_current_user)."""
    return SimpleNamespace(sub=str(uuid4()), role=role, exp=0)


# ─────────────────────────────────────────────────────────────────────────────
# Tests: _normalize_role (rbac.py)
# ─────────────────────────────────────────────────────────────────────────────

class TestNormalizeRole:

    def test_enum_admin_returns_uppercase_string(self):
        assert _normalize_role(RBACRole.ADMIN) == "ADMIN"

    def test_enum_team_leader_returns_uppercase_string(self):
        assert _normalize_role(RBACRole.TEAM_LEADER) == "TEAM_LEADER"

    def test_enum_developer_returns_uppercase_string(self):
        assert _normalize_role(RBACRole.DEVELOPER) == "DEVELOPER"

    def test_lowercase_string_normalized_to_uppercase(self):
        assert _normalize_role("admin") == "ADMIN"

    def test_mixed_case_string_normalized(self):
        assert _normalize_role("Team_Leader") == "TEAM_LEADER"

    def test_invalid_role_raises_value_error(self):
        with pytest.raises(ValueError):
            _normalize_role("SUPERUSER")

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            _normalize_role("")

    def test_acepta_miembros_de_userrole_comunes(self):
        assert _normalize_role(UserRole.ADMIN) == "ADMIN"
        assert _normalize_role(UserRole.DEVELOPER) == "DEVELOPER"

    def test_acepta_group_leader_del_modelo(self):
        assert _normalize_role(UserRole.GROUP_LEADER) == "GROUP_LEADER"


class TestNormalizeDocumentRole:
    """Helper de rol de routers/documents.py."""

    def test_enum_member(self):
        assert normalize_document_role(UserRole.ADMIN) == "ADMIN"
        assert normalize_document_role(UserRole.GROUP_LEADER) == "GROUP_LEADER"

    def test_none_devuelve_cadena_vacia(self):
        assert normalize_document_role(None) == ""

    def test_string_con_prefijo_de_enum_y_guiones(self):
        assert normalize_document_role("UserRole.group-leader") == "GROUP_LEADER"
        assert normalize_document_role("  developer ") == "DEVELOPER"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: _extract_current_role (rbac.py)
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractCurrentRole:

    def test_extracts_role_from_enum_attribute(self):
        assert _extract_current_role(SimpleNamespace(role=RBACRole.ADMIN)) == "ADMIN"

    def test_extracts_role_from_plain_string_attribute(self):
        assert _extract_current_role(SimpleNamespace(role="DEVELOPER")) == "DEVELOPER"

    def test_extracts_role_from_dict(self):
        assert _extract_current_role({"role": "TEAM_LEADER"}) == "TEAM_LEADER"

    def test_none_user_raises_runtime_error(self):
        with pytest.raises(RuntimeError):
            _extract_current_role(None)

    def test_user_without_role_raises_runtime_error(self):
        with pytest.raises(RuntimeError):
            _extract_current_role(SimpleNamespace())

    def test_dict_without_role_raises_runtime_error(self):
        with pytest.raises(RuntimeError):
            _extract_current_role({})


# ─────────────────────────────────────────────────────────────────────────────
# Tests: require_permissions (rbac.py)
# ─────────────────────────────────────────────────────────────────────────────

class TestRequirePermissions:

    def test_no_roles_raises_value_error(self):
        with pytest.raises(ValueError):
            require_permissions()

    def test_rol_no_soportado_falla_al_decorar(self):
        with pytest.raises(ValueError):
            require_permissions("ROOT")

    async def test_allowed_role_executes_decorated_function(self):
        @require_permissions("ADMIN")
        async def endpoint(**kwargs):
            return "ok"

        assert await endpoint(current_user=SimpleNamespace(role=RBACRole.ADMIN)) == "ok"

    async def test_sync_function_tambien_soportada(self):
        @require_permissions(RBACRole.DEVELOPER)
        def endpoint(**kwargs):
            return "sync-ok"

        assert await endpoint(current_user={"role": "developer"}) == "sync-ok"

    async def test_forbidden_role_raises_403(self):
        @require_permissions("ADMIN")
        async def endpoint(**kwargs):
            return "ok"

        with pytest.raises(HTTPException) as exc:
            await endpoint(current_user=SimpleNamespace(role=RBACRole.DEVELOPER))
        assert exc.value.status_code == 403

    async def test_multiple_allowed_roles_any_passes(self):
        @require_permissions("ADMIN", "TEAM_LEADER")
        async def endpoint(**kwargs):
            return "ok"

        assert await endpoint(current_user=SimpleNamespace(role=RBACRole.TEAM_LEADER)) == "ok"

    async def test_admin_no_tiene_bypass_implicito(self):
        # A diferencia de require_role, aquí ADMIN solo entra si se lista
        @require_permissions("DEVELOPER")
        async def endpoint(**kwargs):
            return "ok"

        with pytest.raises(HTTPException) as exc:
            await endpoint(current_user=SimpleNamespace(role="ADMIN"))
        assert exc.value.status_code == 403

    async def test_403_detail_lists_allowed_roles(self):
        @require_permissions("ADMIN")
        async def endpoint(**kwargs):
            return "ok"

        with pytest.raises(HTTPException) as exc:
            await endpoint(current_user=SimpleNamespace(role=RBACRole.DEVELOPER))
        assert "ADMIN" in exc.value.detail

    async def test_sin_current_user_lanza_runtime_error(self):
        @require_permissions("ADMIN")
        async def endpoint(**kwargs):
            return "ok"

        with pytest.raises(RuntimeError):
            await endpoint()


# ─────────────────────────────────────────────────────────────────────────────
# Tests: require_role (auth.py) — factory de dependencias FastAPI
# ─────────────────────────────────────────────────────────────────────────────

class TestRequireRole:
    """
    Se llama directamente a la función interna verify_role con un
    current_user simulado (evita el sistema de dependencias de FastAPI).
    """

    async def test_allowed_role_string_returns_user(self):
        user = token_user("GROUP_LEADER")
        assert await require_role("GROUP_LEADER")(current_user=user) is user

    async def test_allowed_role_enum_returns_user(self):
        user = token_user("GROUP_LEADER")
        verify = require_role([UserRole.ADMIN, UserRole.GROUP_LEADER])
        assert await verify(current_user=user) is user

    async def test_comparacion_insensible_a_mayusculas(self):
        user = token_user("developer")
        assert await require_role(UserRole.DEVELOPER)(current_user=user) is user

    async def test_forbidden_role_raises_403(self):
        with pytest.raises(HTTPException) as exc:
            await require_role(UserRole.ADMIN)(current_user=token_user("DEVELOPER"))
        assert exc.value.status_code == 403

    async def test_group_leader_no_entra_en_endpoint_solo_admin(self):
        with pytest.raises(HTTPException) as exc:
            await require_role([UserRole.ADMIN])(current_user=token_user("GROUP_LEADER"))
        assert exc.value.status_code == 403

    @pytest.mark.parametrize("required", [UserRole.DEVELOPER, [UserRole.GROUP_LEADER], "DEVELOPER"])
    async def test_admin_siempre_tiene_acceso(self, required):
        user = token_user("ADMIN")
        assert await require_role(required)(current_user=user) is user

    @pytest.mark.parametrize("role", [None, ""])
    async def test_rol_vacio_raises_403(self, role):
        with pytest.raises(HTTPException) as exc:
            await require_role(["ADMIN"])(current_user=token_user(role))
        assert exc.value.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Tests: hash_password / verify_password (auth.py)
# ─────────────────────────────────────────────────────────────────────────────

class TestPasswordHashing:

    def test_hash_returns_bcrypt_string(self):
        hashed = hash_password("miContraseña123")
        assert hashed.startswith("$2b$")
        assert "miContraseña123" not in hashed

    def test_verify_correct_password_returns_true(self):
        assert verify_password("secreto", hash_password("secreto")) is True

    def test_verify_wrong_password_returns_false(self):
        assert verify_password("equivocado", hash_password("secreto")) is False

    def test_same_password_produces_different_hashes_due_to_salt(self):
        h1 = hash_password("misma")
        h2 = hash_password("misma")
        # bcrypt usa salt aleatorio → hashes diferentes, ambos verificables
        assert h1 != h2
        assert verify_password("misma", h1) is True
        assert verify_password("misma", h2) is True


# ─────────────────────────────────────────────────────────────────────────────
# Tests: JWT tokens (auth.py)
# ─────────────────────────────────────────────────────────────────────────────

class TestJWTTokens:

    def test_access_token_payload_conserva_claims_y_agrega_exp(self):
        settings = get_settings()
        user_id = str(uuid4())
        token = create_access_token({"sub": user_id, "role": "DEVELOPER", "type": "access"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload["sub"] == user_id
        assert payload["role"] == "DEVELOPER"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_access_token_no_muta_el_dict_de_entrada(self):
        data = {"sub": "x", "role": "ADMIN"}
        create_access_token(data)
        assert data == {"sub": "x", "role": "ADMIN"}

    def test_access_token_with_custom_expires_delta(self):
        settings = get_settings()
        token = create_access_token(
            {"sub": str(uuid4()), "role": "ADMIN"}, expires_delta=timedelta(minutes=5)
        )
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        delta = exp_dt - datetime.now(timezone.utc)
        assert 0 < delta.total_seconds() <= 310  # 5 min + margen de 10s

    def test_refresh_token_dura_mas_que_el_access(self):
        settings = get_settings()
        data = {"sub": str(uuid4()), "role": "ADMIN"}
        access = jwt.decode(create_access_token(data), settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        refresh = jwt.decode(create_refresh_token(data), settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert refresh["exp"] > access["exp"]


class TestVerifyToken:

    def test_access_token_valido_devuelve_payload(self):
        user_id = str(uuid4())
        token_data = verify_token(encode({"sub": user_id, "role": "ADMIN", "type": "access", "exp": future()}))

        assert token_data.sub == user_id
        assert token_data.role == "ADMIN"
        assert isinstance(token_data.exp, int)

    @pytest.mark.parametrize("token_type", ["refresh", None, "ACCESS", ""])
    def test_rechaza_tokens_que_no_son_de_acceso(self, token_type):
        # Un refresh token (7 días) no debe servir como Bearer
        payload = {"sub": str(uuid4()), "role": "ADMIN", "exp": future()}
        if token_type is not None:
            payload["type"] = token_type
        with pytest.raises(HTTPException) as exc:
            verify_token(encode(payload))
        assert exc.value.status_code == 401

    def test_token_creado_sin_type_es_rechazado(self):
        # create_access_token del middleware no añade `type`; quien lo use sin
        # pasar type="access" obtiene un token inútil (auth_service sí lo pasa).
        with pytest.raises(HTTPException) as exc:
            verify_token(create_access_token({"sub": str(uuid4()), "role": "ADMIN"}))
        assert exc.value.status_code == 401

    def test_expired_raises_401(self):
        token = create_access_token(
            {"sub": str(uuid4()), "role": "ADMIN", "type": "access"},
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(HTTPException) as exc:
            verify_token(token)
        assert exc.value.status_code == 401

    def test_invalid_signature_raises_401(self):
        token = encode(
            {"sub": str(uuid4()), "role": "ADMIN", "type": "access", "exp": future()},
            key="clave-diferente-invalida",
        )
        with pytest.raises(HTTPException) as exc:
            verify_token(token)
        assert exc.value.status_code == 401

    def test_algoritmo_none_rechazado(self):
        # Token sin firma construido a mano: {"alg": "none"} . {sub, role, type}
        header = base64url({"alg": "none", "typ": "JWT"})
        body = base64url({"sub": "x", "role": "ADMIN", "type": "access"})
        token = f"{header}.{body}."
        with pytest.raises(HTTPException) as exc:
            verify_token(token)
        assert exc.value.status_code == 401

    def test_basura_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            verify_token("esto-no-es-un-jwt")
        assert exc.value.status_code == 401

    @pytest.mark.parametrize("missing", ["sub", "role"])
    def test_falta_campo_requerido_raises_401(self, missing):
        payload = {"sub": str(uuid4()), "role": "ADMIN", "type": "access", "exp": future()}
        del payload[missing]
        with pytest.raises(HTTPException) as exc:
            verify_token(encode(payload))
        assert exc.value.status_code == 401
