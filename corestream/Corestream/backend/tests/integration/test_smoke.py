"""
Comprobaciones básicas de que la aplicación arranca y responde.

Si algo falla aquí, el resto de la suite de integración no es interpretable.
"""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_health(client):
    res = await client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


async def test_openapi_disponible(client):
    res = await client.get("/api/openapi.json")
    assert res.status_code == 200
    assert "paths" in res.json()


async def test_login_de_cada_rol(client, admin_headers, leader_headers, dev_headers):
    """Los tres roles pueden autenticarse y /auth/me devuelve el rol correcto."""
    for headers, esperado in [
        (admin_headers, "ADMIN"),
        (leader_headers, "TEAM_LEADER"),
        (dev_headers, "DEVELOPER"),
    ]:
        res = await client.get("/api/auth/me", headers=headers)
        assert res.status_code == 200, res.text[:200]
        assert res.json()["role"] == esperado


async def test_sin_token_rechaza(client):
    res = await client.get("/api/tickets/")
    assert res.status_code in (401, 403)


async def test_la_base_se_limpia_entre_tests(client, admin_headers, application):
    """Primera mitad: crea una aplicación."""
    res = await client.get("/api/applications/", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


async def test_la_base_se_limpia_entre_tests_2(client, admin_headers):
    """Segunda mitad: la aplicación del test anterior no debe existir."""
    res = await client.get("/api/applications/", headers=admin_headers)
    assert res.status_code == 200
    assert res.json() == [], "el truncado entre tests no está funcionando"
