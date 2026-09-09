"""
Contrato entre el cliente del frontend y la API.

Cada test reproduce EXACTAMENTE la llamada que hace frontend/src/services/api.ts
—método HTTP, ruta y forma del payload— para detectar los desajustes que hoy se
manifiestan como botones que no hacen nada: los stores capturan el error y solo
escriben en consola.

Los xfail corresponden a la fase 5 del plan.
"""

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True, reason="plan 5: api.tickets.move usa POST, el backend expone PATCH"
)
async def test_move_con_el_metodo_del_frontend(client, leader_headers, application, ticket):
    otra = await client.post(
        "/api/epics/",
        json={"application_id": application["id"], "title": "Destino"},
        headers=leader_headers,
    )
    res = await client.post(
        f"/api/tickets/{ticket['id']}/move",
        json={"new_epic_id": otra.json()["id"]},
        headers=leader_headers,
    )
    assert res.status_code == 200


@pytest.mark.xfail(
    strict=True,
    reason="plan 5: api.tickets.getMyWorkbench llama a /tickets/workbench, que choca con /tickets/{id}",
)
async def test_workbench_por_la_ruta_del_frontend(client, dev_headers):
    res = await client.get("/api/tickets/workbench", headers=dev_headers)
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# Analítica
# ---------------------------------------------------------------------------

async def test_resumen_de_analitica(client, leader_headers, application):
    res = await client.get(f"/api/analytics/summary/{application['id']}", headers=leader_headers)
    assert res.status_code == 200


async def test_rendimiento_con_aplicacion(client, leader_headers, application):
    res = await client.get(
        f"/api/analytics/performance/{application['id']}", headers=leader_headers
    )
    assert res.status_code == 200


@pytest.mark.xfail(
    strict=True,
    reason="plan 5: api.analytics.getPerformance sin appId llama a /analytics/performance, que no existe",
)
async def test_rendimiento_sin_aplicacion(client, leader_headers):
    res = await client.get("/api/analytics/performance", headers=leader_headers)
    assert res.status_code == 200


async def test_heatmap(client, leader_headers, application):
    res = await client.get(f"/api/analytics/heatmap/{application['id']}", headers=leader_headers)
    assert res.status_code == 200


async def test_burndown_con_epica(client, leader_headers, epic):
    res = await client.get(f"/api/analytics/burndown/{epic['id']}", headers=leader_headers)
    assert res.status_code == 200


@pytest.mark.xfail(
    strict=True,
    reason="plan 5: el frontend pasa un application_id a burndown, pero el backend espera epic_id",
)
async def test_burndown_con_aplicacion(client, leader_headers, application):
    res = await client.get(
        f"/api/analytics/burndown/{application['id']}", headers=leader_headers
    )
    assert res.status_code == 200


async def test_export_csv_por_la_ruta_real(client, leader_headers, application):
    res = await client.get(
        f"/api/analytics/export/csv/{application['id']}", headers=leader_headers
    )
    assert res.status_code == 200


# exportCsv/exportPdf del cliente API se eliminaron (plan 5.1): eran código
# muerto (ningún componente los llamaba) que además apuntaba a rutas que no
# existen. La exportación real ya funciona enteramente en el cliente
# (ExportButton.vue + services/exportService.ts, con jsPDF), sin pasar por el
# backend — por diseño no hay /export/csv ni /export/pdf sin app_id, y no se
# van a añadir. No quedan tests xfail para esto: no es un bug pendiente.


async def test_resumen_de_soporte(client, leader_headers):
    res = await client.get("/api/analytics/support-summary", headers=leader_headers)
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# Notificaciones
# ---------------------------------------------------------------------------

async def test_listar_notificaciones(client, dev_headers):
    res = await client.get("/api/notifications/", headers=dev_headers)
    assert res.status_code == 200


async def test_contador_de_no_leidas(client, dev_headers):
    res = await client.get("/api/notifications/unread-count", headers=dev_headers)
    assert res.status_code == 200


async def test_marcar_todas_como_leidas(client, dev_headers):
    res = await client.post("/api/notifications/mark-all-read", headers=dev_headers)
    assert res.status_code == 200


async def test_borrar_notificaciones_leidas(client, dev_headers):
    res = await client.delete("/api/notifications/read", headers=dev_headers)
    assert res.status_code in (200, 204)


# ---------------------------------------------------------------------------
# Reuniones
# ---------------------------------------------------------------------------

@pytest.fixture
async def meeting(client, leader_headers, application):
    res = await client.post(
        "/api/meetings/",
        json={
            "title": "Daily de prueba",
            "meeting_type": "DAILY",
            "application_id": application["id"],
            "scheduled_at": "2030-01-01T10:00:00Z",
            "duration_minutes": 15,
        },
        headers=leader_headers,
    )
    assert res.status_code == 201, res.text[:300]
    return res.json()


async def test_actualizar_reunion_con_patch(client, leader_headers, meeting):
    res = await client.patch(
        f"/api/meetings/{meeting['id']}",
        json={"summary_markdown": "# Resumen"},
        headers=leader_headers,
    )
    assert res.status_code == 200


@pytest.mark.xfail(
    strict=True, reason="plan 5: api.meetings.update usa PUT, el backend solo expone PATCH"
)
async def test_actualizar_reunion_con_el_metodo_del_frontend(client, leader_headers, meeting):
    res = await client.put(
        f"/api/meetings/{meeting['id']}", json={"title": "Renombrada"}, headers=leader_headers
    )
    assert res.status_code == 200


async def test_registrar_asistencia(client, leader_headers, meeting, dev_id):
    """El backend acepta un registro por llamada, no una lista."""
    res = await client.post(
        f"/api/meetings/{meeting['id']}/attendance",
        json={"user_id": dev_id, "status": "PRESENT", "notes": "ok"},
        headers=leader_headers,
    )
    assert res.status_code in (200, 201), res.text[:300]


@pytest.mark.xfail(
    strict=True,
    reason="plan 5.3: api.meetings.setAttendance envía una lista; el backend espera un objeto",
)
async def test_registrar_asistencia_como_lista(client, leader_headers, meeting, dev_id):
    res = await client.post(
        f"/api/meetings/{meeting['id']}/attendance",
        json=[{"user_id": dev_id, "status": "PRESENT"}],
        headers=leader_headers,
    )
    assert res.status_code in (200, 201)


@pytest.mark.xfail(
    strict=True,
    reason="plan 5.3: el mapper del frontend lee is_present, el backend devuelve status",
)
async def test_la_respuesta_de_asistencia_trae_is_present(client, leader_headers, meeting, dev_id):
    res = await client.post(
        f"/api/meetings/{meeting['id']}/attendance",
        json={"user_id": dev_id, "status": "PRESENT"},
        headers=leader_headers,
    )
    assert "is_present" in res.json()


# ---------------------------------------------------------------------------
# Incidentes
# ---------------------------------------------------------------------------

@pytest.fixture
async def incident(client, leader_headers, application):
    res = await client.post(
        "/api/incidents/",
        json={
            "title": "Caída del servicio",
            "description": "Descripción del incidente",
            "application_id": application["id"],
            "severity": "P1",
            "affected_environment": "PRODUCTION",
        },
        headers=leader_headers,
    )
    assert res.status_code == 201, res.text[:300]
    return res.json()


async def test_listar_incidentes(client, dev_headers, incident):
    res = await client.get("/api/incidents/", headers=dev_headers)
    assert res.status_code == 200


async def test_cambiar_estado_de_incidente(client, leader_headers, incident):
    res = await client.patch(
        f"/api/incidents/{incident['id']}/status",
        json={"status": "MITIGATED"},
        headers=leader_headers,
    )
    assert res.status_code == 200


@pytest.mark.xfail(
    strict=True,
    reason="plan 5: ManageIncidentModal usa PUT /incidents/{id}, el backend solo expone PATCH",
)
async def test_actualizar_incidente_con_el_metodo_del_frontend(client, leader_headers, incident):
    res = await client.put(
        f"/api/incidents/{incident['id']}",
        json={"root_cause_analysis": "Causa raíz"},
        headers=leader_headers,
    )
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# Tickets de soporte
# ---------------------------------------------------------------------------

@pytest.fixture
async def support_ticket(client, dev_headers, ticket):
    res = await client.post(
        "/api/support-tickets/",
        json={
            "title": "Bug en producción",
            "description": "Algo se rompió",
            "severity": "HIGH",
            "stack_trace": "Traceback...",
            "reproduction_steps": "1. abrir 2. romper",
            "browser": "Firefox",
            "operating_system": "Linux",
            "linked_ticket_id": ticket["id"],
        },
        headers=dev_headers,
    )
    assert res.status_code == 201, res.text[:300]
    return res.json()


async def test_ciclo_de_soporte(client, dev_headers, leader_headers, support_ticket, dev_id):
    sid = support_ticket["id"]

    assert (await client.get("/api/support-tickets/", headers=dev_headers)).status_code == 200
    assert (await client.get(f"/api/support-tickets/{sid}", headers=dev_headers)).status_code == 200

    res = await client.post(
        f"/api/support-tickets/{sid}/assign", json={"assignee_id": dev_id}, headers=leader_headers
    )
    assert res.status_code == 200

    res = await client.post(f"/api/support-tickets/{sid}/investigate", headers=dev_headers)
    assert res.status_code == 200

    res = await client.post(
        f"/api/support-tickets/{sid}/resolve",
        json={"pr_link": "https://github.com/x/y/pull/2"},
        headers=dev_headers,
    )
    assert res.status_code == 200


async def test_eventos_de_ticket_de_soporte_sin_eventos(client, dev_headers, support_ticket):
    """Un ticket recién creado, sin eventos con usuario asociado, sí serializa."""
    res = await client.get(
        f"/api/support-tickets/{support_ticket['id']}/events", headers=dev_headers
    )
    assert res.status_code == 200


async def test_eventos_de_ticket_de_soporte_con_eventos(
    client, dev_headers, leader_headers, support_ticket, dev_id
):
    """
    Con eventos ya generados, antes la serialización intentaba un lazy-load de
    user.role fuera del contexto async y devolvía 500. Es el escenario real: la
    pestaña de historial se consulta después de trabajar el ticket, no antes.
    """
    sid = support_ticket["id"]
    await client.post(
        f"/api/support-tickets/{sid}/assign", json={"assignee_id": dev_id}, headers=leader_headers
    )
    await client.post(f"/api/support-tickets/{sid}/investigate", headers=dev_headers)

    res = await client.get(f"/api/support-tickets/{sid}/events", headers=dev_headers)
    assert res.status_code == 200, res.text[:200]


# ---------------------------------------------------------------------------
# Rutas duplicadas
# ---------------------------------------------------------------------------

def test_no_hay_operation_ids_duplicados():
    """
    Dos endpoints distintos registrados sobre el mismo método y path.

    Cuál se ejecuta depende del orden de include_router en main.py — de hecho hay
    un comentario en main.py:180 advirtiéndolo. La otra implementación no se
    ejecuta nunca, con el riesgo de que alguien la modifique creyendo que sí.
    """
    import warnings

    from app.main import app

    app.openapi_schema = None
    with warnings.catch_warnings(record=True) as capturados:
        warnings.simplefilter("always")
        app.openapi()

    duplicados = [
        str(w.message) for w in capturados if "Duplicate Operation ID" in str(w.message)
    ]
    assert not duplicados, "\n".join(duplicados)
