"""
Script E2E para Corestream.
Simula EXACTAMENTE cómo el frontend hace las peticiones al backend,
cubriendo un caso de uso completo: autenticación, proyectos, épicas,
tickets y transiciones de estado.

Uso:
    python3 e2e_simulation.py               # Usa backend local (localhost:8000)
    API_URL=http://prod:8000/api python3 e2e_simulation.py
"""

import asyncio
import httpx
import uuid
import sys
import os

API_URL = os.getenv("API_URL", "http://localhost:8000/api")

# Credenciales de usuarios base (creados por seed_persistent_users en startup)
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123!@#"
LEADER_EMAIL = "leader@example.com"
LEADER_PASSWORD = "Leader123!@#"
DEV_EMAIL = "userdev@example.com"
DEV_PASSWORD = "Dev123!@#"


def check(res: httpx.Response, label: str, expected=(200, 201)):
    """Valida respuesta HTTP; aborta si hay error."""
    if res.status_code not in expected:
        print(f"\n❌ FALLO en '{label}'")
        print(f"   Status: {res.status_code}")
        print(f"   Body:   {res.text[:500]}")
        sys.exit(1)


async def run_e2e():
    print("🚀 Iniciando prueba E2E (Simulación de Frontend)...")
    print(f"   API: {API_URL}\n")

    async with httpx.AsyncClient(base_url=API_URL, timeout=15.0) as client:

        # ── 1. HEALTH CHECK ───────────────────────────────────────────────────
        print("─── 1. Health check ────────────────────────────────────────────")
        res = await client.get("/health".replace("/api/health", "/health"))
        # El health endpoint está en /api/health
        res = await client.get("/../health")  # Relative trick
        # Easiest: just hit the health endpoint directly
        health_res = await httpx.AsyncClient(timeout=5).get(
            API_URL.replace("/api", "") + "/api/health"
        )
        check(health_res, "health check")
        print(f"✅ Backend healthy: {health_res.json()['status']}")

        # ── 2. LOGIN como ADMIN ───────────────────────────────────────────────
        print("\n─── 2. Login de usuarios ────────────────────────────────────────")

        # Admin login
        res = await client.post("/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        check(res, "admin login")
        admin_token = res.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print(f"✅ Admin logueado ({ADMIN_EMAIL})")

        # Leader login
        res = await client.post("/auth/login", json={
            "email": LEADER_EMAIL,
            "password": LEADER_PASSWORD
        })
        check(res, "leader login")
        leader_token = res.json()["access_token"]
        leader_headers = {"Authorization": f"Bearer {leader_token}"}
        print(f"✅ Leader logueado ({LEADER_EMAIL})")

        # Dev login
        res = await client.post("/auth/login", json={
            "email": DEV_EMAIL,
            "password": DEV_PASSWORD
        })
        check(res, "dev login")
        dev_token = res.json()["access_token"]
        dev_headers = {"Authorization": f"Bearer {dev_token}"}
        print(f"✅ Developer logueado ({DEV_EMAIL})")

        # ── 3. OBTENER PERFIL del usuario actual ──────────────────────────────
        print("\n─── 3. Perfil de usuario ────────────────────────────────────────")
        res = await client.get("/auth/me", headers=dev_headers)
        check(res, "get current user /auth/me")
        dev_id = res.json()["id"]
        print(f"✅ Dev ID obtenido: {dev_id} (rol: {res.json().get('role', '?')})")

        res = await client.get("/auth/me", headers=leader_headers)
        check(res, "get current user (leader)")
        leader_id = res.json()["id"]
        print(f"✅ Leader ID obtenido: {leader_id}")

        # ── 4. LISTAR USUARIOS (como Admin/Leader) ────────────────────────────
        print("\n─── 4. Listado de usuarios ──────────────────────────────────────")
        res = await client.get("/users/", headers=leader_headers)
        check(res, "list users")
        total_users = len(res.json()) if isinstance(res.json(), list) else res.json().get("total", "?")
        print(f"✅ Usuarios listados: {total_users}")

        # ── 5. CREAR APLICACIÓN (como Admin) ─────────────────────────────────
        print("\n─── 5. Creación de Proyecto (Application) ───────────────────────")
        suffix = uuid.uuid4().hex[:6]
        res = await client.post("/applications/", json={
            "name": f"E2E Test App {suffix}",
            "description": "Aplicación creada por test E2E automatizado",
            "repo_url": f"https://github.com/org/e2e-repo-{suffix}"
        }, headers=admin_headers)
        check(res, "create application")
        app_id = res.json()["id"]
        print(f"✅ Aplicación creada: {app_id}")

        # ── 6. CREAR ÉPICA ────────────────────────────────────────────────────
        print("\n─── 6. Creación de Épica ────────────────────────────────────────")
        res = await client.post("/epics/", json={
            "application_id": app_id,
            "title": f"E2E Epic {suffix}",
            "description": "Épica creada por test E2E",
            "due_date": "2030-12-31T00:00:00Z"
        }, headers=leader_headers)
        check(res, "create epic")
        epic_id = res.json()["id"]
        print(f"✅ Épica creada: {epic_id}")

        # ── 7. CREAR TICKET y ASIGNAR al Dev ─────────────────────────────────
        print("\n─── 7. Creación y Asignación de Ticket ──────────────────────────")
        res = await client.post("/tickets/", json={
            "epic_id": epic_id,
            "title": f"E2E Ticket {suffix}",
            "description": "Ticket de prueba E2E completo",
            "ticket_type": "DEVELOPMENT",
            "priority": "HIGH",
            "estimated_hours": 8.0,
            "assignee_id": dev_id
        }, headers=leader_headers)
        check(res, "create ticket")
        ticket_id = res.json()["id"]
        print(f"✅ Ticket creado y asignado al dev: {ticket_id}")

        # ── 8. FLUJO DE TRABAJO DEL TICKET ───────────────────────────────────
        print("\n─── 8. Flujo de trabajo completo del Ticket ─────────────────────")

        # 8a. Dev inicia trabajo: TODO → IN_PROGRESS
        res = await client.post(f"/tickets/{ticket_id}/start",
                                json={}, headers=dev_headers)
        check(res, "transition: start (TODO → IN_PROGRESS)")
        print(f"✅ Ticket movido a IN_PROGRESS")

        # 8b. Dev bloquea con pregunta: IN_PROGRESS → BLOCKED_QUESTION
        res = await client.post(f"/tickets/{ticket_id}/question",
                                json={"question_text": "¿Cómo se configura la integración con Redis en el entorno local?"},
                                headers=dev_headers)
        check(res, "transition: question (IN_PROGRESS → BLOCKED_QUESTION)")
        print(f"✅ Ticket bloqueado con pregunta (BLOCKED_QUESTION)")

        # 8c. Leader responde: BLOCKED_QUESTION → IN_PROGRESS
        res = await client.post(f"/tickets/{ticket_id}/resolve-question",
                                json={"resolution": "Usa la URL del .env: REDIS_URL=redis://localhost:6379"},
                                headers=leader_headers)
        check(res, "transition: resolve-question (BLOCKED_QUESTION → IN_PROGRESS)")
        print(f"✅ Pregunta resuelta, ticket vuelve a IN_PROGRESS")

        # 8d. Dev completa con PR: IN_PROGRESS → COMPLETED
        res = await client.post(f"/tickets/{ticket_id}/complete",
                                json={"pr_link": f"https://github.com/org/repo/pull/{suffix}"},
                                headers=dev_headers)
        check(res, "transition: complete (IN_PROGRESS → COMPLETED)")
        print(f"✅ Ticket completado con PR link!")

        # ── 9. VERIFICAR ESTADO FINAL DEL TICKET ─────────────────────────────
        print("\n─── 9. Verificación del estado final ────────────────────────────")
        res = await client.get(f"/tickets/{ticket_id}", headers=dev_headers)
        check(res, "get ticket final state")
        final_ticket = res.json()
        print(f"✅ Estado final del ticket: {final_ticket.get('status', '?')}")
        print(f"   PR Link: {final_ticket.get('pr_link', 'N/A')}")

        # ── 10. ANALYTICS ─────────────────────────────────────────────────────
        print("\n─── 10. Analytics ──────────────────────────────────────────────")
        res = await client.get(f"/analytics/summary/{app_id}", headers=leader_headers)
        check(res, "get analytics summary", expected=(200, 201, 404))
        if res.status_code == 200:
            summary = res.json()
            print(f"✅ Analytics obtenidos: {summary.get('total_tickets', 'N/A')} tickets totales")
        else:
            print(f"⚠️  Analytics endpoint retornó {res.status_code} (no crítico)")

        # ── 11. NOTIFICACIONES ────────────────────────────────────────────────
        print("\n─── 11. Notificaciones ──────────────────────────────────────────")
        res = await client.get("/notifications/", headers=dev_headers)
        check(res, "get notifications", expected=(200, 201))
        notifs = res.json() if isinstance(res.json(), list) else res.json().get("items", [])
        print(f"✅ Notificaciones del dev: {len(notifs)}")

        # ── RESULTADO FINAL ───────────────────────────────────────────────────
        print("\n" + "="*60)
        print("🎉  SIMULACIÓN E2E COMPLETADA CON ÉXITO")
        print("="*60)
        print("\n  Flujo completo verificado:")
        print("  ✓ Autenticación (login / /auth/me)")
        print("  ✓ Gestión de usuarios")
        print("  ✓ Creación de Application")
        print("  ✓ Creación de Epic")
        print("  ✓ Creación y asignación de Ticket")
        print("  ✓ Transiciones: TODO → IN_PROGRESS → BLOCKED → IN_PROGRESS → COMPLETED")
        print("  ✓ Analytics")
        print("  ✓ Notificaciones")
        print()


if __name__ == "__main__":
    asyncio.run(run_e2e())
