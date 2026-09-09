"""
Autorización por rol y por pertenencia.

Todos los casos de esta fase (4) ya están resueltos: routers/tickets.py y
routers/epics.py usan require_role() y los helpers de
app/services/ticket_permissions.py para las comprobaciones de pertenencia.
Ya no quedan xfail — cualquier regresión aquí debe fallar en rojo.
"""

import uuid

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ---------------------------------------------------------------------------
# Usuarios: hoy correcto, protegemos contra regresiones
# ---------------------------------------------------------------------------

async def test_dev_no_lista_usuarios(client, dev_headers):
    res = await client.get("/api/users/", headers=dev_headers)
    assert res.status_code == 403


async def test_leader_si_lista_usuarios(client, leader_headers):
    res = await client.get("/api/users/", headers=leader_headers)
    assert res.status_code == 200


async def test_dev_no_cambia_roles(client, dev_headers, leader_id):
    res = await client.post(
        f"/api/users/{leader_id}/change-role", json={"role": "ADMIN"}, headers=dev_headers
    )
    assert res.status_code == 403


async def test_dev_no_se_autopromueve(client, dev_headers, dev_id):
    res = await client.post(
        f"/api/users/{dev_id}/change-role", json={"role": "ADMIN"}, headers=dev_headers
    )
    assert res.status_code == 403


async def test_dev_no_borra_usuarios(client, dev_headers, leader_id):
    res = await client.delete(f"/api/users/{leader_id}", headers=dev_headers)
    assert res.status_code == 403


async def test_dev_no_edita_perfiles_ajenos(client, dev_headers, leader_id):
    res = await client.put(
        f"/api/users/{leader_id}", json={"full_name": "Secuestrado"}, headers=dev_headers
    )
    assert res.status_code == 403


async def test_admin_puede_cambiar_roles(client, admin_headers, dev_id):
    res = await client.post(
        f"/api/users/{dev_id}/change-role", json={"role": "TEAM_LEADER"}, headers=admin_headers
    )
    assert res.status_code == 200
    assert res.json()["role"] == "TEAM_LEADER"


# ---------------------------------------------------------------------------
# Aplicaciones: hoy correcto
# ---------------------------------------------------------------------------

async def test_dev_no_crea_aplicaciones(client, dev_headers):
    res = await client.post(
        "/api/applications/", json={"name": "No permitida", "description": "x"}, headers=dev_headers
    )
    assert res.status_code == 403


async def test_team_leader_crea_aplicaciones(client, leader_headers):
    """
    ADMIN ya no es el único que puede crear aplicaciones: obligaba al admin a
    crear cada proyecto nuevo en persona, sin poder delegarlo en quien lleva
    el día a día del equipo. Invitar usuarios, cambiar roles y resetear
    contraseñas siguen siendo solo de ADMIN — esto solo afecta aplicaciones,
    igual que epics.py ya permitía para épicas/tickets.
    """
    res = await client.post(
        "/api/applications/",
        json={"name": "App de Team Leader", "description": "x"},
        headers=leader_headers,
    )
    assert res.status_code == 201, res.text[:200]


# ---------------------------------------------------------------------------
# Épicas
# ---------------------------------------------------------------------------

async def test_dev_no_crea_epicas(client, dev_headers, application):
    res = await client.post(
        "/api/epics/",
        json={"application_id": application["id"], "title": "Épica no autorizada"},
        headers=dev_headers,
    )
    assert res.status_code == 403


async def test_dev_no_borra_epicas(client, dev_headers, epic):
    res = await client.delete(f"/api/epics/{epic['id']}", headers=dev_headers)
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

async def test_dev_no_borra_tickets_ajenos(client, dev2_headers, ticket):
    """
    El borrado es permanente y en cascada (subtareas, eventos, documentos):
    solo ADMIN/TEAM_LEADER pueden ejecutarlo.
    """
    res = await client.delete(f"/api/tickets/{ticket['id']}", headers=dev2_headers)
    assert res.status_code == 403


async def test_dev_no_inicia_tickets_ajenos(client, dev2_headers, ticket, dev_id):
    res = await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev2_headers)
    assert res.status_code == 403


async def test_start_no_reasigna_el_ticket(client, dev2_headers, ticket, dev_id):
    """Si el ticket ya está asignado a otro, /start no debe robar la asignación."""
    res = await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev2_headers)
    assert res.status_code == 403
    res_ticket = await client.get(f"/api/tickets/{ticket['id']}", headers=dev2_headers)
    assert res_ticket.json()["assignee_id"] == dev_id


async def test_dev_no_completa_tickets_ajenos(client, dev_headers, dev2_headers, ticket):
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    res = await client.post(
        f"/api/tickets/{ticket['id']}/complete",
        json={"pr_link": "https://github.com/x/y/pull/1"},
        headers=dev2_headers,
    )
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# Coherencia de los nombres de rol
# ---------------------------------------------------------------------------

def test_rbacrole_usa_los_mismos_nombres_que_la_base():
    """
    middleware/rbac.py definía GROUP_LEADER mientras la base y el resto del
    código usan TEAM_LEADER — usar el decorador con GROUP_LEADER denegaba a
    todos en silencio, porque ningún usuario tenía jamás ese rol. Se unificó
    a TEAM_LEADER; este test protege contra que alguien lo reintroduzca.
    """
    from app.middleware.rbac import RBACRole
    from app.models import UserRole

    nombres_rbac = {r.value for r in RBACRole}
    nombres_modelo = {r.value for r in UserRole}
    assert nombres_rbac == nombres_modelo, (
        f"desalineados: solo en RBACRole={nombres_rbac - nombres_modelo}, "
        f"solo en UserRole={nombres_modelo - nombres_rbac}"
    )


# ---------------------------------------------------------------------------
# Aislamiento de datos
# ---------------------------------------------------------------------------

async def test_recurso_inexistente_da_404(client, admin_headers):
    res = await client.get(f"/api/tickets/{uuid.uuid4()}", headers=admin_headers)
    assert res.status_code == 404
