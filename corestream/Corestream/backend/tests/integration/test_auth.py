"""
Autenticación y gestión de sesión.

Los xfail de este módulo corresponden a la fase 3 del plan. Son strict: cuando
el fallo se corrija, el test dará XPASS y obligará a retirar la marca.

`client` es un fixture de sesión (un solo httpx.AsyncClient para toda la
suite, con su propio cookie jar) — necesario para no relogear en cada test y
chocar con el rate limiter, pero significa que las cookies de refresh_token/
csrf_token de un login anterior (de este archivo o de las fixtures
admin_headers/leader_headers/dev_headers/dev2_headers de otros tests) siguen
ahí. Los tests que dependen de cookies llaman `client.cookies.clear()`
primero para no heredar sesión de otro test.
"""

import pytest

from .conftest import ADMIN, DEV

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def _tokens(client, user):
    res = await client.post(
        "/api/auth/login", json={"email": user["email"], "password": user["password"]}
    )
    assert res.status_code == 200
    return res.json()


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

async def test_login_correcto_devuelve_ambos_tokens(client):
    """
    El refresh_token YA NO viaja en el cuerpo (plan 3.2): llega como cookie
    httpOnly. httpx sí puede leer cookies httpOnly (esa restricción es del
    navegador, no del cliente HTTP), así que se verifica ahí.
    """
    client.cookies.clear()
    body = await _tokens(client, DEV)
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert "refresh_token" not in body
    assert client.cookies.get("refresh_token")
    assert client.cookies.get("csrf_token")


async def test_csrf_token_tiene_path_raiz(client):
    """
    Regresión: csrf_token estuvo con Path=/api/auth (copiado sin pensar del
    refresh_token) hasta que se detectó que document.cookie —restringido
    por Path, a diferencia del cookie jar de httpx/el propio navegador
    adjuntando la cookie en la petición— nunca lo veía desde la SPA, servida
    en "/". El resultado: /auth/refresh rechazaba con 403 (CSRF ausente) la
    primerísima recarga de página tras cualquier login real, en cualquier
    navegador, siempre — no un caso raro. httpx no lo detecta solo (no
    aplica el scoping por Path al leer cookies), así que se verifica el
    atributo Path del Set-Cookie crudo, no que la cookie "esté".
    """
    client.cookies.clear()
    res = await client.post(
        "/api/auth/login", json={"email": DEV["email"], "password": DEV["password"]}
    )
    assert res.status_code == 200

    set_cookie_headers = res.headers.get_list("set-cookie")
    csrf_header = next(h for h in set_cookie_headers if h.startswith("csrf_token="))
    refresh_header = next(h for h in set_cookie_headers if h.startswith("refresh_token="))

    assert "path=/;" in csrf_header.lower() or csrf_header.lower().endswith("path=/")
    # El refresh token, en cambio, sigue restringido a /api/auth a propósito
    # (el navegador no necesita adjuntarlo en cada petición a la API).
    assert "path=/api/auth" in refresh_header.lower()


async def test_login_con_password_incorrecta(client):
    res = await client.post(
        "/api/auth/login", json={"email": DEV["email"], "password": "no-es-la-buena"}
    )
    assert res.status_code == 401


async def test_login_con_email_inexistente(client):
    res = await client.post(
        "/api/auth/login", json={"email": "nadie@corestream-tests.com", "password": "X1234567!"}
    )
    assert res.status_code == 401


async def test_login_es_insensible_a_mayusculas_en_email(client):
    res = await client.post(
        "/api/auth/login", json={"email": DEV["email"].upper(), "password": DEV["password"]}
    )
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# Separación entre access token y refresh token (plan 3.1)
# ---------------------------------------------------------------------------

async def test_el_refresh_token_no_sirve_como_access_token(client):
    """
    Un refresh token (7 días) no debe poder usarse como Bearer.

    Antes sí funcionaba, lo que convertía ACCESS_TOKEN_EXPIRE_MINUTES=30 en
    ficción: un token robado valía una semana y se podía renovar indefinidamente.
    """
    client.cookies.clear()
    await _tokens(client, ADMIN)
    refresh_token = client.cookies.get("refresh_token")
    assert refresh_token

    res = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert res.status_code == 401


async def test_el_access_token_no_sirve_para_refrescar(client):
    client.cookies.clear()
    tokens = await _tokens(client, ADMIN)
    client.cookies.clear()  # sin cookie de refresh, /refresh usa el cuerpo y no exige CSRF
    res = await client.post(
        "/api/auth/refresh", json={"refresh_token": tokens["access_token"]}
    )
    assert res.status_code == 401


async def test_refresh_con_token_valido_funciona(client):
    """
    El refresh token viaja en la cookie httpOnly; el doble envío exige además
    la cabecera X-CSRF-Token con el valor de la cookie csrf_token legible.
    """
    client.cookies.clear()
    await _tokens(client, DEV)
    csrf_token = client.cookies.get("csrf_token")
    assert csrf_token

    res = await client.post("/api/auth/refresh", headers={"x-csrf-token": csrf_token})
    assert res.status_code == 200
    assert res.json()["access_token"]


async def test_refresh_sin_csrf_token_falla(client):
    """Cookie de refresh válida, pero sin la cabecera de doble envío: 403."""
    client.cookies.clear()
    await _tokens(client, DEV)
    res = await client.post("/api/auth/refresh")
    assert res.status_code == 403


async def test_refresh_con_token_basura(client):
    """Sin cookie de refresh, el cuerpo con un token inválido no exige CSRF."""
    client.cookies.clear()
    res = await client.post("/api/auth/refresh", json={"refresh_token": "aaa.bbb.ccc"})
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# Validación de tokens
# ---------------------------------------------------------------------------

async def test_token_con_alg_none_se_rechaza(client):
    """Un JWT sin firma no debe aceptarse aunque declare rol ADMIN."""
    forjado = (
        "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0."
        "eyJzdWIiOiJ4Iiwicm9sZSI6IkFETUlOIiwiZXhwIjo5OTk5OTk5OTk5fQ."
    )
    res = await client.get("/api/tickets/", headers={"Authorization": f"Bearer {forjado}"})
    assert res.status_code == 401


async def test_token_basura_se_rechaza(client):
    res = await client.get("/api/tickets/", headers={"Authorization": "Bearer aaa.bbb.ccc"})
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# Coherencia de la sesión (plan 3.9)
# ---------------------------------------------------------------------------

async def test_expires_in_coincide_con_la_configuracion(client):
    from app.config import get_settings

    body = await _tokens(client, DEV)
    assert body["expires_in"] == get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * 60


# ---------------------------------------------------------------------------
# Logout y revocación (plan 3.3)
# ---------------------------------------------------------------------------

async def test_logout_existe(client):
    """
    Usa un token propio, no la fixture `dev_headers` compartida: esa fixture
    es de sesión (una sola vez, para no chocar con el rate limiter de
    /auth/login — plan 4) y logout revoca el token, lo que dejaría a
    `dev_headers` inválido para el resto de la sesión de pytest.
    """
    tokens = await _tokens(client, DEV)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    res = await client.post("/api/auth/logout", headers=headers)
    assert res.status_code in (200, 204)


async def test_tras_logout_el_token_deja_de_valer(client):
    tokens = await _tokens(client, DEV)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    assert (await client.get("/api/auth/me", headers=headers)).status_code == 200
    await client.post("/api/auth/logout", headers=headers)
    assert (await client.get("/api/auth/me", headers=headers)).status_code == 401


# ---------------------------------------------------------------------------
# Registro público (plan 3.7)
# ---------------------------------------------------------------------------

async def test_el_registro_publico_esta_cerrado(client):
    res = await client.post(
        "/api/auth/register",
        json={
            "email": "intruso@corestream-tests.com",
            "full_name": "Intruso",
            "password": "Intruso123!@#",
        },
    )
    assert res.status_code in (403, 404, 405)


async def test_el_registro_no_permite_elegir_rol(client):
    """
    Mass assignment de rol: aunque se pida ADMIN, debe crearse como DEVELOPER.

    Esto ya está bien resuelto hoy y el test lo blinda contra regresiones.
    """
    res = await client.post(
        "/api/auth/register",
        json={
            "email": "escalada@corestream-tests.com",
            "full_name": "Escalada",
            "password": "Escalada123!@#",
            "role": "ADMIN",
        },
    )
    if res.status_code == 201:
        assert res.json()["role"] == "DEVELOPER"


# ---------------------------------------------------------------------------
# Fuerza bruta (plan 3.5)
# ---------------------------------------------------------------------------

async def test_login_tiene_rate_limiting(client):
    codigos = []
    for _ in range(25):
        res = await client.post(
            "/api/auth/login", json={"email": ADMIN["email"], "password": "incorrecta"}
        )
        codigos.append(res.status_code)
        if res.status_code == 429:
            break
    assert 429 in codigos, "25 intentos fallidos consecutivos sin bloqueo"


# ---------------------------------------------------------------------------
# Cambio de contraseña
# ---------------------------------------------------------------------------

async def test_cambio_de_password_exige_la_actual(client, dev_headers):
    res = await client.post(
        "/api/auth/change-password",
        json={"old_password": "la-que-no-es", "new_password": "NuevaClave123!@#"},
        headers=dev_headers,
    )
    assert res.status_code == 400


async def test_cambio_de_password_valida_la_nueva(client, dev_headers):
    res = await client.post(
        "/api/auth/change-password",
        json={"old_password": DEV["password"], "new_password": "corta"},
        headers=dev_headers,
    )
    # 422 si la rechaza el esquema de Pydantic, 400 si la rechaza AuthService
    assert res.status_code in (400, 422)


async def test_cambio_de_password_funciona_y_la_vieja_deja_de_valer(client):
    tokens = await _tokens(client, DEV)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    nueva = "OtraClaveValida123!@#"

    res = await client.post(
        "/api/auth/change-password",
        json={"old_password": DEV["password"], "new_password": nueva},
        headers=headers,
    )
    assert res.status_code == 200

    assert (
        await client.post(
            "/api/auth/login", json={"email": DEV["email"], "password": nueva}
        )
    ).status_code == 200
    assert (
        await client.post(
            "/api/auth/login", json={"email": DEV["email"], "password": DEV["password"]}
        )
    ).status_code == 401


# ---------------------------------------------------------------------------
# Perfil
# ---------------------------------------------------------------------------

async def test_actualizar_perfil_propio(client, dev_headers):
    res = await client.put(
        "/api/auth/me", json={"full_name": "Nombre Cambiado"}, headers=dev_headers
    )
    assert res.status_code == 200
    assert res.json()["full_name"] == "Nombre Cambiado"
