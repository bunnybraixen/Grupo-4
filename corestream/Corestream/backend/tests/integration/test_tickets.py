"""
Ciclo de vida de tickets, subtareas y máquina de estados.

Incluye los tres HTTP 500 por MissingGreenlet detectados en la auditoría
(fase 2.3 del plan). Son especialmente importantes porque el fallo no está en
la lógica sino en la serialización: el endpoint hace su trabajo, commitea, y
revienta al construir la respuesta.
"""

import uuid

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------

async def test_listar_tickets(client, dev_headers, ticket):
    res = await client.get("/api/tickets/", headers=dev_headers)
    assert res.status_code == 200
    assert any(t["id"] == ticket["id"] for t in res.json())


async def test_mi_workbench(client, dev_headers, ticket):
    res = await client.get("/api/tickets/my-workbench", headers=dev_headers)
    assert res.status_code == 200
    assert any(t["id"] == ticket["id"] for t in res.json())


async def test_detalle_de_ticket(client, dev_headers, ticket):
    res = await client.get(f"/api/tickets/{ticket['id']}", headers=dev_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Ticket de prueba"


async def test_eventos_de_ticket(client, dev_headers, ticket):
    res = await client.get(f"/api/tickets/{ticket['id']}/events", headers=dev_headers)
    assert res.status_code == 200


async def test_miembros_del_equipo(client, dev_headers, epic):
    res = await client.get(
        "/api/tickets/team-members", params={"epic_id": epic["id"]}, headers=dev_headers
    )
    assert res.status_code == 200


async def test_listar_tickets_por_epica(client, dev_headers, epic, ticket):
    """
    Antes fallaba con 500 siempre que la épica tenía al menos un ticket
    (faltaba selectinload de subtasks/assignee en tickets.py:115).
    Lo usa AssignmentPanel.vue a través de ticketsStore.fetchByEpic.
    """
    res = await client.get(f"/api/tickets/by-epic/{epic['id']}", headers=dev_headers)
    assert res.status_code == 200, res.text[:200]
    assert len(res.json()) == 1


async def test_listar_tickets_de_epica_vacia(client, leader_headers, application):
    """La misma ruta funciona si la épica no tiene tickets: confirma la causa."""
    epica = await client.post(
        "/api/epics/",
        json={"application_id": application["id"], "title": "Vacía"},
        headers=leader_headers,
    )
    res = await client.get(
        f"/api/tickets/by-epic/{epica.json()['id']}", headers=leader_headers
    )
    assert res.status_code == 200
    assert res.json() == []


# ---------------------------------------------------------------------------
# Escritura y reordenación
# ---------------------------------------------------------------------------

async def test_crear_ticket(client, leader_headers, epic, dev_id):
    res = await client.post(
        "/api/tickets/",
        json={
            "epic_id": epic["id"],
            "title": "Otro ticket",
            "priority": "LOW",
            "assignee_id": dev_id,
        },
        headers=leader_headers,
    )
    assert res.status_code == 201
    assert res.json()["assignee_id"] == dev_id


async def test_crear_ticket_con_epica_inexistente(client, leader_headers):
    res = await client.post(
        "/api/tickets/", json={"epic_id": str(uuid.uuid4()), "title": "Huérfano"},
        headers=leader_headers,
    )
    assert res.status_code in (400, 404, 422)


async def test_crear_ticket_con_prioridad_invalida(client, leader_headers, epic):
    res = await client.post(
        "/api/tickets/",
        json={"epic_id": epic["id"], "title": "X", "priority": "SUPER_URGENTE"},
        headers=leader_headers,
    )
    assert res.status_code == 422


async def test_crear_ticket_con_titulo_vacio(client, leader_headers, epic):
    res = await client.post(
        "/api/tickets/", json={"epic_id": epic["id"], "title": ""}, headers=leader_headers
    )
    assert res.status_code == 422


async def test_titulo_excesivamente_largo_lo_rechaza_el_esquema(client, leader_headers, epic):
    res = await client.post(
        "/api/tickets/",
        json={"epic_id": epic["id"], "title": "A" * 100_000},
        headers=leader_headers,
    )
    assert res.status_code == 422


async def test_mover_ticket_entre_epicas(client, leader_headers, application, ticket):
    otra = await client.post(
        "/api/epics/",
        json={"application_id": application["id"], "title": "Destino"},
        headers=leader_headers,
    )
    res = await client.patch(
        f"/api/tickets/{ticket['id']}/move",
        json={"new_epic_id": otra.json()["id"]},
        headers=leader_headers,
    )
    assert res.status_code == 200


async def test_reordenar_ticket(client, leader_headers, ticket):
    """
    Es el drag & drop de tickets dentro de una épica.
    Antes fallaba con 500: reorder no cargaba ninguna relación (tickets.py:623).
    """
    res = await client.patch(
        f"/api/tickets/{ticket['id']}/reorder", json={"new_index": 0}, headers=leader_headers
    )
    assert res.status_code == 200, res.text[:200]


async def test_reordenar_ticket_a_otra_posicion(client, leader_headers, epic, dev_id):
    """Cubre también la rama que sí mueve el índice, no solo el caso trivial."""
    t1 = (
        await client.post(
            "/api/tickets/",
            json={"epic_id": epic["id"], "title": "Primero", "assignee_id": dev_id},
            headers=leader_headers,
        )
    ).json()
    # Segundo ticket: solo necesitamos que exista en la épica para que
    # mover el primero al índice 1 tenga sentido.
    await client.post(
        "/api/tickets/",
        json={"epic_id": epic["id"], "title": "Segundo", "assignee_id": dev_id},
        headers=leader_headers,
    )

    res = await client.patch(
        f"/api/tickets/{t1['id']}/reorder", json={"new_index": 1}, headers=leader_headers
    )
    assert res.status_code == 200, res.text[:200]
    assert res.json()["order_index"] == 1


async def test_asignar_y_desasignar(client, leader_headers, ticket, dev2_id):
    res = await client.put(
        f"/api/tickets/{ticket['id']}", json={"assignee_id": dev2_id}, headers=leader_headers
    )
    assert res.status_code == 200
    assert res.json()["assignee_id"] == dev2_id

    res = await client.put(
        f"/api/tickets/{ticket['id']}", json={"assignee_id": None}, headers=leader_headers
    )
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# Máquina de estados
# ---------------------------------------------------------------------------

async def test_flujo_completo(client, dev_headers, leader_headers, ticket):
    tid = ticket["id"]

    res = await client.post(f"/api/tickets/{tid}/start", json={}, headers=dev_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "IN_PROGRESS"

    res = await client.post(
        f"/api/tickets/{tid}/question",
        json={"question_text": "¿Cómo configuro el entorno local?"},
        headers=dev_headers,
    )
    assert res.status_code == 200

    res = await client.post(
        f"/api/tickets/{tid}/resolve-question",
        json={"resolution": "Mira el README, sección de entorno"},
        headers=leader_headers,
    )
    assert res.status_code == 200

    res = await client.post(
        f"/api/tickets/{tid}/complete",
        json={"pr_link": "https://github.com/org/repo/pull/1"},
        headers=dev_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "COMPLETED"


async def test_no_se_puede_iniciar_dos_veces(client, dev_headers, ticket):
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    res = await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    assert res.status_code in (400, 409, 422)


async def test_no_se_puede_completar_desde_todo(client, dev_headers, ticket):
    res = await client.post(
        f"/api/tickets/{ticket['id']}/complete",
        json={"pr_link": "https://github.com/x/y/pull/1"},
        headers=dev_headers,
    )
    assert res.status_code in (400, 409, 422)


async def test_completar_exige_pr_link(client, dev_headers, ticket):
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    res = await client.post(f"/api/tickets/{ticket['id']}/complete", json={}, headers=dev_headers)
    assert res.status_code in (400, 422)


async def test_pregunta_exige_longitud_minima(client, dev_headers, ticket):
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    res = await client.post(
        f"/api/tickets/{ticket['id']}/question", json={"question_text": "¿eh?"}, headers=dev_headers
    )
    assert res.status_code == 422


async def test_resolver_pregunta_sin_estar_bloqueado(client, leader_headers, ticket):
    res = await client.post(
        f"/api/tickets/{ticket['id']}/resolve-question",
        json={"resolution": "nada que resolver"},
        headers=leader_headers,
    )
    assert res.status_code == 400


async def test_redirigir_ticket(client, dev_headers, ticket, dev2_id):
    await client.post(f"/api/tickets/{ticket['id']}/start", json={}, headers=dev_headers)
    res = await client.post(
        f"/api/tickets/{ticket['id']}/redirect",
        json={"to_user_id": dev2_id, "justification": "No es mi área de especialidad"},
        headers=dev_headers,
    )
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# Subtareas
# ---------------------------------------------------------------------------

async def test_ciclo_de_subtareas(client, dev_headers, ticket):
    tid = ticket["id"]

    a = await client.post(
        f"/api/tickets/{tid}/subtasks/", json={"title": "Primera", "ticket_id": tid},
        headers=dev_headers,
    )
    assert a.status_code == 201
    b = await client.post(
        f"/api/tickets/{tid}/subtasks/", json={"title": "Segunda", "ticket_id": tid},
        headers=dev_headers,
    )
    assert b.status_code == 201

    res = await client.get(f"/api/tickets/{tid}/subtasks/", headers=dev_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2

    res = await client.put(
        f"/api/tickets/{tid}/subtasks/{a.json()['id']}",
        json={"title": "Primera (hecha)", "is_completed": True, "order_index": 0},
        headers=dev_headers,
    )
    assert res.status_code == 200
    assert res.json()["is_completed"] is True

    res = await client.patch(
        f"/api/tickets/{tid}/subtasks/reorder",
        json={"subtask_ids": [b.json()["id"], a.json()["id"]]},
        headers=dev_headers,
    )
    assert res.status_code == 200

    res = await client.delete(
        f"/api/tickets/{tid}/subtasks/{a.json()['id']}", headers=dev_headers
    )
    assert res.status_code == 204


# ---------------------------------------------------------------------------
# Paginación y entradas límite
# ---------------------------------------------------------------------------

async def test_limite_de_paginacion_tiene_tope(client, dev_headers):
    res = await client.get("/api/tickets/", params={"limit": 100000}, headers=dev_headers)
    assert res.status_code == 422


async def test_limite_negativo_se_rechaza(client, dev_headers):
    res = await client.get("/api/tickets/", params={"limit": -1}, headers=dev_headers)
    assert res.status_code == 422


async def test_uuid_malformado_en_la_ruta(client, dev_headers):
    res = await client.get("/api/tickets/no-es-un-uuid", headers=dev_headers)
    assert res.status_code == 422
