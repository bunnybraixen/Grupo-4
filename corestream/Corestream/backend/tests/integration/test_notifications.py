"""
Sistema de notificaciones.

Los hallazgos de la auditoría en esta área (plan 5.2 y el bug de
`not Notification.is_read`) ya están resueltos — ver tickets.py
(create_ticket/update_ticket llaman a notify_ticket_assigned) y
notifications.py (los tres `not <columna>` pasaron a `~<columna>`).
"""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def _notificaciones_de(client, headers) -> list:
    res = await client.get("/api/notifications/", headers=headers)
    assert res.status_code == 200
    cuerpo = res.json()
    return cuerpo if isinstance(cuerpo, list) else cuerpo.get("items", [])


async def _tipos(client, headers) -> set:
    return {n.get("type") for n in await _notificaciones_de(client, headers)}


# ---------------------------------------------------------------------------
# Asignación
# ---------------------------------------------------------------------------

async def test_asignar_un_ticket_notifica_al_asignado(
    client, leader_headers, dev_headers, epic, dev_id
):
    await client.post(
        "/api/tickets/",
        json={
            "epic_id": epic["id"],
            "title": "Ticket que debería notificar",
            "assignee_id": dev_id,
            "priority": "HIGH",
        },
        headers=leader_headers,
    )
    assert "TICKET_ASSIGNED" in await _tipos(client, dev_headers)


async def test_reasignar_notifica_al_nuevo_responsable(
    client, leader_headers, dev2_headers, ticket, dev2_id
):
    await client.put(
        f"/api/tickets/{ticket['id']}", json={"assignee_id": dev2_id}, headers=leader_headers
    )
    assert "TICKET_ASSIGNED" in await _tipos(client, dev2_headers)


# ---------------------------------------------------------------------------
# Lo que sí funciona hoy: protegemos contra regresiones
# ---------------------------------------------------------------------------

async def test_una_pregunta_bloqueante_notifica_al_lider(
    client, dev_headers, leader_headers, ticket
):
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    await client.post(
        f"/api/tickets/{ticket['id']}/question",
        json={"question_text": "¿Qué credenciales uso para el entorno de staging?"},
        headers=dev_headers,
    )
    assert "QUESTION_RAISED" in await _tipos(client, leader_headers)


async def test_completar_notifica_al_lider(client, dev_headers, leader_headers, ticket):
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    await client.post(
        f"/api/tickets/{ticket['id']}/complete",
        json={"pr_link": "https://github.com/org/repo/pull/9"},
        headers=dev_headers,
    )
    assert "TICKET_COMPLETED" in await _tipos(client, leader_headers)


async def test_redirigir_notifica_al_destinatario(
    client, dev_headers, dev2_headers, ticket, dev2_id
):
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    await client.post(
        f"/api/tickets/{ticket['id']}/redirect",
        json={"to_user_id": dev2_id, "justification": "Es de tu especialidad"},
        headers=dev_headers,
    )
    assert "TICKET_REDIRECTED" in await _tipos(client, dev2_headers)


# ---------------------------------------------------------------------------
# Gestión de la bandeja
# ---------------------------------------------------------------------------

async def _generar_notificacion_para_el_lider(client, dev_headers, ticket):
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    await client.post(
        f"/api/tickets/{ticket['id']}/question",
        json={"question_text": "Una pregunta lo bastante larga para pasar la validación"},
        headers=dev_headers,
    )


def _contador(payload) -> int:
    if isinstance(payload, int):
        return payload
    return payload.get("unread_count", payload.get("count", 0))


async def test_contador_de_no_leidas_refleja_la_realidad(
    client, dev_headers, leader_headers, ticket
):
    antes = _contador(
        (await client.get("/api/notifications/unread-count", headers=leader_headers)).json()
    )

    await _generar_notificacion_para_el_lider(client, dev_headers, ticket)

    despues = _contador(
        (await client.get("/api/notifications/unread-count", headers=leader_headers)).json()
    )
    assert despues > antes


async def test_filtro_de_solo_no_leidas(client, dev_headers, leader_headers, ticket):
    await _generar_notificacion_para_el_lider(client, dev_headers, ticket)

    res = await client.get(
        "/api/notifications/", params={"unread_only": True}, headers=leader_headers
    )
    assert res.status_code == 200
    cuerpo = res.json()
    items = cuerpo if isinstance(cuerpo, list) else cuerpo.get("items", [])
    assert items, "hay notificaciones sin leer pero el filtro devuelve una lista vacía"


async def test_marcar_todas_como_leidas_marca_de_verdad(
    client, dev_headers, leader_headers, ticket
):
    await _generar_notificacion_para_el_lider(client, dev_headers, ticket)

    pendientes_antes = [
        n for n in await _notificaciones_de(client, leader_headers) if not n.get("is_read")
    ]
    assert pendientes_antes, "precondición: el líder debe tener notificaciones sin leer"

    res = await client.post("/api/notifications/mark-all-read", headers=leader_headers)
    assert res.status_code == 200

    pendientes_despues = [
        n for n in await _notificaciones_de(client, leader_headers) if not n.get("is_read")
    ]
    assert not pendientes_despues, "siguen sin leer tras marcar todas como leídas"


async def test_marcar_como_leida(client, dev_headers, leader_headers, ticket):
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    await client.post(
        f"/api/tickets/{ticket['id']}/question",
        json={"question_text": "Otra pregunta lo bastante larga para validar"},
        headers=dev_headers,
    )

    pendientes = await _notificaciones_de(client, leader_headers)
    assert pendientes, "el líder debería tener al menos una notificación"

    res = await client.post(
        "/api/notifications/mark-read",
        json={"notification_ids": [pendientes[0]["id"]]},
        headers=leader_headers,
    )
    assert res.status_code == 200


async def test_las_notificaciones_no_se_filtran_entre_usuarios(
    client, dev_headers, dev2_headers, leader_headers, ticket
):
    """Un desarrollador no debe ver la bandeja de otro."""
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    await client.post(
        f"/api/tickets/{ticket['id']}/question",
        json={"question_text": "Pregunta suficientemente larga para el validador"},
        headers=dev_headers,
    )

    del_lider = await _notificaciones_de(client, leader_headers)
    del_dev2 = await _notificaciones_de(client, dev2_headers)

    ids_lider = {n["id"] for n in del_lider}
    ids_dev2 = {n["id"] for n in del_dev2}
    assert not (ids_lider & ids_dev2), "hay notificaciones visibles para quien no es su destinatario"


# ---------------------------------------------------------------------------
# Borrado (plan 5: DELETE /notifications/{id} y DELETE /notifications/read
# no existían — el cliente los llamaba y el backend devolvía 404)
# ---------------------------------------------------------------------------

async def test_borrar_una_notificacion(client, dev_headers, leader_headers, ticket):
    await _generar_notificacion_para_el_lider(client, dev_headers, ticket)
    pendientes = await _notificaciones_de(client, leader_headers)
    assert pendientes

    res = await client.delete(
        f"/api/notifications/{pendientes[0]['id']}", headers=leader_headers
    )
    assert res.status_code == 204

    ids_restantes = {n["id"] for n in await _notificaciones_de(client, leader_headers)}
    assert pendientes[0]["id"] not in ids_restantes


async def test_no_se_puede_borrar_la_notificacion_de_otro(
    client, dev_headers, leader_headers, ticket
):
    await _generar_notificacion_para_el_lider(client, dev_headers, ticket)
    pendientes = await _notificaciones_de(client, leader_headers)
    assert pendientes

    res = await client.delete(
        f"/api/notifications/{pendientes[0]['id']}", headers=dev_headers
    )
    assert res.status_code == 404


async def test_borrar_notificaciones_leidas(client, dev_headers, leader_headers, ticket):
    await _generar_notificacion_para_el_lider(client, dev_headers, ticket)
    pendientes = await _notificaciones_de(client, leader_headers)
    assert pendientes

    await client.post(
        "/api/notifications/mark-read",
        json={"notification_ids": [pendientes[0]["id"]]},
        headers=leader_headers,
    )

    res = await client.delete("/api/notifications/read", headers=leader_headers)
    assert res.status_code == 204

    restantes = await _notificaciones_de(client, leader_headers)
    assert pendientes[0]["id"] not in {n["id"] for n in restantes}
