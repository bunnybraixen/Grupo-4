"""
Tests unitarios para app/services/ticket_permissions.py (matriz de permisos
sobre tickets compartida por routers/tickets.py y routers/subtasks.py).

current_user puede llegar como modelo ORM (User, con .id y role enum) o como
TokenPayload (con .sub y role str): ambos formatos se prueban.
"""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models import UserRole
from app.services.ticket_permissions import (
    assert_can_manage_ticket,
    assert_is_current_assignee,
    claim_or_assert_assignee,
    get_role_name,
    get_user_id,
    is_admin_or_leader,
    require_admin_or_leader,
    require_non_admin,
)


def token_user(role: str, user_id=None) -> SimpleNamespace:
    return SimpleNamespace(sub=str(user_id or uuid4()), role=role)


def orm_user(role: UserRole, user_id=None) -> SimpleNamespace:
    return SimpleNamespace(id=user_id or uuid4(), role=role)


def ticket(assignee_id=None) -> SimpleNamespace:
    return SimpleNamespace(id=uuid4(), assignee_id=assignee_id)


def assert_403(fn, *args):
    with pytest.raises(HTTPException) as exc:
        fn(*args)
    assert exc.value.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de identidad y rol
# ─────────────────────────────────────────────────────────────────────────────

class TestGetUserId:

    def test_prefiere_id_del_modelo(self):
        uid = uuid4()
        assert get_user_id(SimpleNamespace(id=uid, sub="otro")) == str(uid)

    def test_usa_sub_del_token(self):
        assert get_user_id(SimpleNamespace(sub="abc")) == "abc"

    def test_usa_user_id_como_ultimo_recurso(self):
        assert get_user_id(SimpleNamespace(user_id=7)) == "7"

    def test_sin_identificador_lanza_401(self):
        with pytest.raises(HTTPException) as exc:
            get_user_id(SimpleNamespace(role="ADMIN"))
        assert exc.value.status_code == 401


class TestGetRoleName:

    @pytest.mark.parametrize(
        "role,expected",
        [
            (UserRole.GROUP_LEADER, "GROUP_LEADER"),
            ("developer", "DEVELOPER"),
            (SimpleNamespace(name="admin"), "ADMIN"),  # modelo Role
            (None, ""),
        ],
    )
    def test_formatos_de_rol(self, role, expected):
        assert get_role_name(SimpleNamespace(role=role)) == expected

    def test_usuario_sin_atributo_role(self):
        assert get_role_name(SimpleNamespace()) == ""


class TestIsAdminOrLeader:

    @pytest.mark.parametrize("role", ["ADMIN", "GROUP_LEADER", "TEAM_LEADER", "group_leader"])
    def test_roles_de_gestion(self, role):
        assert is_admin_or_leader(token_user(role)) is True

    @pytest.mark.parametrize("role", ["DEVELOPER", "", None])
    def test_resto_de_roles(self, role):
        assert is_admin_or_leader(token_user(role)) is False


# ─────────────────────────────────────────────────────────────────────────────
# Guardas por rol
# ─────────────────────────────────────────────────────────────────────────────

class TestRequireNonAdmin:

    def test_admin_bloqueado(self):
        assert_403(require_non_admin, token_user("ADMIN"))
        assert_403(require_non_admin, orm_user(UserRole.ADMIN))

    @pytest.mark.parametrize("role", ["DEVELOPER", "GROUP_LEADER"])
    def test_resto_permitido(self, role):
        assert require_non_admin(token_user(role)) is None


class TestRequireAdminOrLeader:

    @pytest.mark.parametrize("user", [token_user("ADMIN"), orm_user(UserRole.GROUP_LEADER)])
    def test_gestion_permitida(self, user):
        assert require_admin_or_leader(user) is None

    def test_developer_bloqueado(self):
        assert_403(require_admin_or_leader, token_user("DEVELOPER"))
        assert_403(require_admin_or_leader, orm_user(UserRole.DEVELOPER))


# ─────────────────────────────────────────────────────────────────────────────
# Guardas sobre un ticket concreto
# ─────────────────────────────────────────────────────────────────────────────

class TestAssertCanManageTicket:

    @pytest.mark.parametrize("role", ["ADMIN", "GROUP_LEADER"])
    def test_gestion_puede_con_cualquier_ticket(self, role):
        assert assert_can_manage_ticket(ticket(uuid4()), token_user(role)) is None
        assert assert_can_manage_ticket(ticket(None), token_user(role)) is None

    def test_developer_asignado_puede(self):
        uid = uuid4()
        # assignee_id es UUID y el sub del token es str: se comparan como str
        assert assert_can_manage_ticket(ticket(uid), token_user("DEVELOPER", uid)) is None
        assert assert_can_manage_ticket(ticket(uid), orm_user(UserRole.DEVELOPER, uid)) is None

    def test_developer_no_asignado_bloqueado(self):
        assert_403(assert_can_manage_ticket, ticket(uuid4()), token_user("DEVELOPER"))

    def test_developer_y_ticket_sin_asignar_bloqueado(self):
        assert_403(assert_can_manage_ticket, ticket(None), token_user("DEVELOPER"))


class TestAssertIsCurrentAssignee:

    def test_asignado_puede(self):
        uid = uuid4()
        assert assert_is_current_assignee(ticket(uid), token_user("DEVELOPER", uid)) is None

    @pytest.mark.parametrize("role", ["DEVELOPER", "GROUP_LEADER", "ADMIN"])
    def test_sin_excepcion_de_rol(self, role):
        # Ni un líder puede completar el trabajo asignado a otro
        assert_403(assert_is_current_assignee, ticket(uuid4()), token_user(role))

    def test_ticket_sin_asignar_bloqueado(self):
        assert_403(assert_is_current_assignee, ticket(None), token_user("DEVELOPER"))


class TestClaimOrAssertAssignee:

    def test_ticket_libre_se_reclama(self):
        user = token_user("DEVELOPER")
        t = ticket(None)
        claim_or_assert_assignee(t, user)
        assert str(t.assignee_id) == user.sub

    def test_ticket_propio_no_cambia(self):
        uid = uuid4()
        t = ticket(uid)
        claim_or_assert_assignee(t, token_user("DEVELOPER", uid))
        assert t.assignee_id == uid

    @pytest.mark.parametrize("role", ["DEVELOPER", "GROUP_LEADER"])
    def test_no_se_puede_robar_un_ticket_ajeno(self, role):
        original = uuid4()
        t = ticket(original)
        assert_403(claim_or_assert_assignee, t, token_user(role))
        assert t.assignee_id == original
