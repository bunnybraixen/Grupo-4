"""
Tests unitarios para RBAC y autenticación JWT — CS-044.

Cubre middleware/rbac.py y middleware/auth.py.
La mayoría son funciones puras (sin DB), exceptuando require_permissions
que necesita un mock de current_user.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import get_settings
from app.middleware.auth import (
    _normalize_role_value,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.middleware.rbac import (
    RBACRole,
    _extract_current_role,
    _normalize_role,
    require_permissions,
)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_user_with_role(role_value: str | RBACRole) -> MagicMock:
    user = MagicMock()
    if isinstance(role_value, RBACRole):
        user.role = role_value
    else:
        mock_role = MagicMock()
        mock_role.value = role_value
        user.role = mock_role
    return user


# ─────────────────────────────────────────────────────────────────────────────
# Tests: _normalize_role (rbac.py)
# ─────────────────────────────────────────────────────────────────────────────

class TestNormalizeRole:

    def test_enum_admin_returns_uppercase_string(self):
        assert _normalize_role(RBACRole.ADMIN) == "ADMIN"

    def test_enum_group_leader_returns_uppercase_string(self):
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


# ─────────────────────────────────────────────────────────────────────────────
# Tests: _extract_current_role (rbac.py)
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractCurrentRole:

    def test_extracts_role_from_enum_attribute(self):
        user = MagicMock()
        user.role = RBACRole.ADMIN
        assert _extract_current_role(user) == "ADMIN"

    def test_extracts_role_from_plain_string_attribute(self):
        # user.role es una cadena directa (ej: rol normalizado a string)
        user = MagicMock()
        user.role = "DEVELOPER"
        assert _extract_current_role(user) == "DEVELOPER"

    def test_extracts_role_from_dict(self):
        user_dict = {"role": "TEAM_LEADER"}
        assert _extract_current_role(user_dict) == "TEAM_LEADER"

    def test_none_user_raises_runtime_error(self):
        with pytest.raises(RuntimeError):
            _extract_current_role(None)

    def test_user_with_none_role_raises_runtime_error(self):
        user = MagicMock(spec=[])  # sin atributo 'role'
        with pytest.raises(RuntimeError):
            _extract_current_role(user)


# ─────────────────────────────────────────────────────────────────────────────
# Tests: require_permissions (rbac.py)
# ─────────────────────────────────────────────────────────────────────────────

class TestRequirePermissions:

    def test_no_roles_raises_value_error(self):
        with pytest.raises(ValueError):
            require_permissions()

    async def test_allowed_role_executes_decorated_function(self):
        @require_permissions("ADMIN")
        async def endpoint(**kwargs):
            return "ok"

        user = make_user_with_role(RBACRole.ADMIN)
        result = await endpoint(current_user=user)
        assert result == "ok"

    async def test_forbidden_role_raises_403(self):
        @require_permissions("ADMIN")
        async def endpoint(**kwargs):
            return "ok"

        user = make_user_with_role(RBACRole.DEVELOPER)
        with pytest.raises(HTTPException) as exc:
            await endpoint(current_user=user)
        assert exc.value.status_code == 403

    async def test_multiple_allowed_roles_any_passes(self):
        @require_permissions("ADMIN", "TEAM_LEADER")
        async def endpoint(**kwargs):
            return "ok"

        user = make_user_with_role(RBACRole.TEAM_LEADER)
        result = await endpoint(current_user=user)
        assert result == "ok"

    async def test_developer_blocked_when_only_admin_allowed(self):
        @require_permissions("ADMIN", "TEAM_LEADER")
        async def endpoint(**kwargs):
            return "ok"

        user = make_user_with_role(RBACRole.DEVELOPER)
        with pytest.raises(HTTPException) as exc:
            await endpoint(current_user=user)
        assert exc.value.status_code == 403

    async def test_403_detail_lists_allowed_roles(self):
        @require_permissions("ADMIN")
        async def endpoint(**kwargs):
            return "ok"

        user = make_user_with_role(RBACRole.DEVELOPER)
        with pytest.raises(HTTPException) as exc:
            await endpoint(current_user=user)
        assert "ADMIN" in exc.value.detail


# ─────────────────────────────────────────────────────────────────────────────
# Tests: hash_password / verify_password (auth.py)
# ─────────────────────────────────────────────────────────────────────────────

class TestPasswordHashing:

    def test_hash_returns_bcrypt_string(self):
        hashed = hash_password("miContraseña123")
        assert hashed.startswith("$2b$")

    def test_verify_correct_password_returns_true(self):
        hashed = hash_password("secreto")
        assert verify_password("secreto", hashed) is True

    def test_verify_wrong_password_returns_false(self):
        hashed = hash_password("secreto")
        assert verify_password("equivocado", hashed) is False

    def test_different_passwords_produce_different_hashes(self):
        h1 = hash_password("pass1")
        h2 = hash_password("pass2")
        assert h1 != h2

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

    def test_create_access_token_returns_string(self):
        token = create_access_token({"sub": str(uuid4()), "role": "ADMIN"})
        assert isinstance(token, str)
        assert len(token) > 10

    def test_access_token_payload_contains_sub_and_role(self):
        settings = get_settings()
        user_id = str(uuid4())
        token = create_access_token({"sub": user_id, "role": "DEVELOPER"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert payload["sub"] == user_id
        assert payload["role"] == "DEVELOPER"
        assert "exp" in payload

    def test_access_token_with_custom_expires_delta(self):
        settings = get_settings()
        token = create_access_token(
            {"sub": str(uuid4()), "role": "ADMIN"},
            expires_delta=timedelta(minutes=5),
        )
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # exp debe estar aprox a 5 minutos desde ahora
        exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        delta = exp_dt - datetime.now(timezone.utc)
        assert 0 < delta.total_seconds() <= 310  # 5 min + margen de 10s

    async def test_verify_token_valid_returns_token_payload(self):
        user_id = str(uuid4())
        token = create_access_token({"sub": user_id, "role": "ADMIN"})
        token_data = await verify_token(token)

        assert token_data.sub == user_id
        assert token_data.role == "ADMIN"

    async def test_verify_token_expired_raises_401(self):
        token = create_access_token(
            {"sub": str(uuid4()), "role": "ADMIN"},
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(HTTPException) as exc:
            await verify_token(token)
        assert exc.value.status_code == 401

    async def test_verify_token_invalid_signature_raises_401(self):
        # Token firmado con clave diferente
        invalid_token = jwt.encode(
            {"sub": str(uuid4()), "role": "ADMIN", "exp": datetime.utcnow() + timedelta(hours=1)},
            "clave-diferente-invalida",
            algorithm="HS256",
        )
        with pytest.raises(HTTPException) as exc:
            await verify_token(invalid_token)
        assert exc.value.status_code == 401

    async def test_verify_token_missing_role_field_raises_401(self):
        settings = get_settings()
        # Token sin campo "role"
        incomplete_token = jwt.encode(
            {"sub": str(uuid4()), "exp": datetime.utcnow() + timedelta(hours=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        with pytest.raises(HTTPException) as exc:
            await verify_token(incomplete_token)
        assert exc.value.status_code == 401

    async def test_verify_token_missing_sub_field_raises_401(self):
        settings = get_settings()
        # Token sin campo "sub"
        incomplete_token = jwt.encode(
            {"role": "ADMIN", "exp": datetime.utcnow() + timedelta(hours=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        with pytest.raises(HTTPException) as exc:
            await verify_token(incomplete_token)
        assert exc.value.status_code == 401

    def test_create_refresh_token_has_longer_expiry_than_access(self):
        settings = get_settings()
        data = {"sub": str(uuid4()), "role": "ADMIN"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        access_payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        refresh_payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        assert refresh_payload["exp"] > access_payload["exp"]

    def test_refresh_token_is_valid_jwt(self):
        settings = get_settings()
        token = create_refresh_token({"sub": str(uuid4())})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "sub" in payload
        assert "exp" in payload


# ─────────────────────────────────────────────────────────────────────────────
# Tests: _normalize_role_value (auth.py)
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Tests: require_role (auth.py) — factory para dependencias FastAPI
# ─────────────────────────────────────────────────────────────────────────────

class TestRequireRole:
    """
    Prueba require_role llamando directamente a la función interna verify_role
    con un current_user mock (evita el sistema de dependencias de FastAPI).
    """

    async def test_allowed_role_string_returns_user(self):
        from app.middleware.auth import require_role

        mock_user = MagicMock()
        mock_user.role = "ADMIN"

        verify_role = require_role("ADMIN")
        result = await verify_role(current_user=mock_user)

        assert result is mock_user

    async def test_allowed_role_list_returns_user(self):
        from app.middleware.auth import require_role

        mock_user = MagicMock()
        mock_user.role = "DEVELOPER"

        verify_role = require_role(["ADMIN", "DEVELOPER"])
        result = await verify_role(current_user=mock_user)

        assert result is mock_user

    async def test_forbidden_role_raises_403(self):
        from app.middleware.auth import require_role

        mock_user = MagicMock()
        mock_user.role = "DEVELOPER"

        verify_role = require_role(["ADMIN"])
        with pytest.raises(HTTPException) as exc:
            await verify_role(current_user=mock_user)
        assert exc.value.status_code == 403

    async def test_user_with_role_value_attr_passes(self):
        from app.middleware.auth import require_role

        mock_user = MagicMock()
        role_obj = MagicMock(spec=["value"])
        role_obj.value = "ADMIN"
        mock_user.role = role_obj

        verify_role = require_role(["ADMIN"])
        result = await verify_role(current_user=mock_user)
        assert result is mock_user

    async def test_user_with_role_name_attr_passes(self):
        from app.middleware.auth import require_role

        mock_user = MagicMock()
        role_obj = MagicMock(spec=["name"])
        role_obj.name = "TEAM_LEADER"
        mock_user.role = role_obj

        verify_role = require_role(["TEAM_LEADER"])
        result = await verify_role(current_user=mock_user)
        assert result is mock_user

    async def test_user_no_role_attr_raises_403(self):
        from app.middleware.auth import require_role

        mock_user = MagicMock()
        mock_user.role = None  # role atribute es None

        verify_role = require_role(["ADMIN"])
        with pytest.raises(HTTPException) as exc:
            await verify_role(current_user=mock_user)
        assert exc.value.status_code == 403


class TestNormalizeRoleValue:

    def test_none_returns_empty_string(self):
        assert _normalize_role_value(None) == ""

    def test_object_with_name_attr_uses_name(self):
        obj = MagicMock()
        obj.name = "ADMIN"
        del obj.value  # aseguramos que no tiene .value
        # _normalize_role_value prefiere .name sobre .value
        result = _normalize_role_value(obj)
        assert result == "ADMIN"

    def test_plain_string_returns_uppercase(self):
        assert _normalize_role_value("developer") == "DEVELOPER"

    def test_object_with_value_attr_uses_value_when_no_name(self):
        obj = MagicMock(spec=["value"])
        obj.value = "TEAM_LEADER"
        result = _normalize_role_value(obj)
        assert result == "TEAM_LEADER"
