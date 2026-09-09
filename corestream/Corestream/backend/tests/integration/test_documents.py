"""
Documentos y subida de ficheros.

Cubre las dos rutas de almacenamiento (/api/documents/* y /api/uploads/*),
que cuelgan de subcarpetas distintas ("documents" y "uploads") de la misma
raíz configurable settings.UPLOAD_DIR (plan 7.2).
"""

import io

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


# ---------------------------------------------------------------------------
# Configuración de almacenamiento (plan 7.2)
# ---------------------------------------------------------------------------

def test_file_service_respeta_la_configuracion():
    """
    settings.UPLOAD_DIR es la raíz configurable de almacenamiento; FileService
    cuelga su subcarpeta "uploads" de esa raíz (no de una ruta fija calculada
    desde __file__, como antes de la fase 7.2).
    """
    from pathlib import Path

    from app.config import get_settings
    from app.services.file_service import UPLOAD_DIR

    assert Path(UPLOAD_DIR).parent == Path(get_settings().UPLOAD_DIR)


def test_el_router_de_documentos_respeta_la_configuracion():
    from pathlib import Path

    from app.config import get_settings
    from app.routers.documents import UPLOAD_DIR

    assert Path(UPLOAD_DIR).parent == Path(get_settings().UPLOAD_DIR)


def test_ambas_rutas_de_subida_comparten_raiz():
    """
    Documentos y uploads viven en subcarpetas distintas ("documents" y
    "uploads") a propósito, para no mezclar tipos de fichero, pero ambas
    cuelgan de la misma raíz persistente (settings.UPLOAD_DIR) en vez de una
    en el volumen y la otra en una capa efímera del contenedor.
    """
    from pathlib import Path

    from app.routers.documents import UPLOAD_DIR as DOCS_DIR
    from app.services.file_service import UPLOAD_DIR as UPLOADS_DIR

    assert Path(DOCS_DIR).parent == Path(UPLOADS_DIR).parent


# ---------------------------------------------------------------------------
# /api/documents
# ---------------------------------------------------------------------------

async def test_subir_y_descargar_documento(client, dev_headers, ticket, epic):
    res = await client.post(
        "/api/documents/",
        files={"file": ("notas.txt", b"contenido de prueba", "text/plain")},
        data={"ticketId": ticket["id"], "epicId": epic["id"], "docType": "OTHER"},
        headers=dev_headers,
    )
    assert res.status_code == 201, res.text[:300]
    doc_id = res.json()["id"]

    res = await client.get(f"/api/documents/{doc_id}/download", headers=dev_headers)
    assert res.status_code == 200
    assert res.content == b"contenido de prueba"


async def test_listar_documentos_de_un_ticket(client, dev_headers, ticket):
    await client.post(
        "/api/documents/",
        files={"file": ("a.txt", b"x", "text/plain")},
        data={"ticketId": ticket["id"], "epicId": "", "docType": "OTHER"},
        headers=dev_headers,
    )
    res = await client.get(
        "/api/documents/", params={"ticketId": ticket["id"]}, headers=dev_headers
    )
    assert res.status_code == 200
    assert len(res.json()) >= 1


async def test_rechaza_extension_no_permitida(client, dev_headers, ticket):
    res = await client.post(
        "/api/documents/",
        files={"file": ("malicioso.sh", b"#!/bin/sh\nrm -rf /", "application/x-sh")},
        data={"ticketId": ticket["id"], "epicId": "", "docType": "OTHER"},
        headers=dev_headers,
    )
    assert res.status_code in (400, 415, 422)


async def test_sanea_el_path_traversal_en_el_nombre(client, dev_headers, ticket):
    """El nombre debe quedar reducido al fichero, sin componentes de ruta."""
    res = await client.post(
        "/api/documents/",
        files={"file": ("../../../../tmp/escapado.txt", b"x", "text/plain")},
        data={"ticketId": ticket["id"], "epicId": "", "docType": "OTHER"},
        headers=dev_headers,
    )
    assert res.status_code == 201
    nombre = res.json()["filename"]
    assert "/" not in nombre and ".." not in nombre
    assert nombre == "escapado.txt"


async def test_rechaza_ficheros_demasiado_grandes(client, dev_headers, ticket):
    grande = io.BytesIO(b"A" * (60 * 1024 * 1024))
    res = await client.post(
        "/api/documents/",
        files={"file": ("enorme.bin", grande, "application/octet-stream")},
        data={"ticketId": ticket["id"], "epicId": "", "docType": "OTHER"},
        headers=dev_headers,
    )
    assert res.status_code in (400, 413, 422)


async def test_borrar_documento(client, dev_headers, ticket):
    res = await client.post(
        "/api/documents/",
        files={"file": ("borrable.txt", b"x", "text/plain")},
        data={"ticketId": ticket["id"], "epicId": "", "docType": "OTHER"},
        headers=dev_headers,
    )
    doc_id = res.json()["id"]

    res = await client.delete(f"/api/documents/{doc_id}", headers=dev_headers)
    assert res.status_code in (200, 204)


# ---------------------------------------------------------------------------
# /api/uploads
# ---------------------------------------------------------------------------

def _file_id(payload: dict) -> str:
    """El router de uploads envuelve la respuesta en {status, message, data}."""
    cuerpo = payload.get("data", payload)
    return cuerpo.get("id") or cuerpo.get("file_id")


async def test_ciclo_de_uploads(client, dev_headers):
    res = await client.post(
        "/api/uploads/upload",
        files={"file": ("codigo.py", b"print('hola')", "text/x-python")},
        headers=dev_headers,
    )
    assert res.status_code == 200, res.text[:300]
    file_id = _file_id(res.json())
    assert file_id

    assert (await client.get("/api/uploads/list", headers=dev_headers)).status_code == 200
    assert (
        await client.get(f"/api/uploads/info/{file_id}", headers=dev_headers)
    ).status_code == 200

    res = await client.get(f"/api/uploads/download/{file_id}", headers=dev_headers)
    assert res.status_code == 200
    assert res.content == b"print('hola')"


async def test_uploads_requiere_autenticacion(client, dev_headers):
    res = await client.post(
        "/api/uploads/upload",
        files={"file": ("x.py", b"x", "text/x-python")},
        headers=dev_headers,
    )
    file_id = _file_id(res.json())

    sin_auth = await client.get(f"/api/uploads/download/{file_id}")
    assert sin_auth.status_code in (401, 403)


async def test_un_usuario_no_descarga_los_ficheros_de_otro(client, dev_headers, dev2_headers):
    res = await client.post(
        "/api/uploads/upload",
        files={"file": ("privado.py", b"secreto", "text/x-python")},
        headers=dev_headers,
    )
    file_id = _file_id(res.json())

    ajeno = await client.get(f"/api/uploads/download/{file_id}", headers=dev2_headers)
    assert ajeno.status_code in (403, 404)
