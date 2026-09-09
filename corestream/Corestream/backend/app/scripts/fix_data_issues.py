"""
Script de corrección de datos en la base de datos.

Fixes aplicados:
  BUG-12  — Traduce contenido de demo que quedó en inglés (épicas, tickets, apps)
  BUG-15  — Corrige nombre de archivo malformado con doble extensión y sufijo de copia
  BUG-16  — Elimina ticket de prueba "aaaaaaa" y registros inválidos similares
  BUG-20  — Agrega tildes faltantes en títulos de tickets del Sprint 9

Ejecutar con:
    python -m app.scripts.fix_data_issues
"""

from __future__ import annotations

import psycopg2

from app.config import get_settings


def _sync_url(database_url: str) -> str:
    return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


# ---------------------------------------------------------------------------
# Datos de corrección
# ---------------------------------------------------------------------------

# BUG-12: contenido en inglés → español
APP_DESCRIPTION_FIXES: list[tuple[str, str]] = [
    ("Demo application for testing", "Aplicación demo para pruebas"),
]

EPIC_DESCRIPTION_FIXES: list[tuple[str, str]] = [
    ("Demo epic for QA testing", "Épica demo para testing de QA"),
]

TICKET_TITLE_FIXES_BUG12: list[tuple[str, str]] = [
    ("Implement user authentication",   "Implementar autenticación de usuario"),
    ("Setup database schema",           "Configurar esquema de base de datos"),
    ("Fix API response timeout",        "Corregir tiempo de respuesta de API"),
    ("Fix API response",                "Corregir respuesta de API"),
    ("Create project documentation",    "Crear documentación del proyecto"),
    ("Optimize ticket filtering",       "Optimizar filtrado de tickets"),
    (
        "Review team performance metrics",
        "Revisar métricas de rendimiento del equipo",
    ),
]

# BUG-20: tildes faltantes
TICKET_TITLE_FIXES_BUG20: list[tuple[str, str]] = [
    (
        "Documentacion tecnica y guia de despliegue",
        "Documentación técnica y guía de despliegue",
    ),
    (
        "Optimizacion de rendimiento y lazy loading",
        "Optimización de rendimiento y lazy loading",
    ),
    (
        "Traduccion automatica de documentos",
        "Traducción automática de documentos",
    ),
    (
        "Vinculacion de PR al completar ticket",
        "Vinculación de PR al completar ticket",
    ),
    (
        "Sprint de correccion de bugs y polish",
        "Sprint de corrección de bugs y polish",
    ),
]

# BUG-15: nombre de archivo malformado
DOCUMENT_FILENAME_FIXES: list[tuple[str, str]] = [
    (
        "CoreStream-Plan-Desarrollo.docx (1).md",
        "CoreStream-Plan-Desarrollo.md",
    ),
]

# BUG-16: títulos que son claramente datos de prueba inválidos
INVALID_TICKET_TITLES: list[str] = [
    "aaaaaaa",
    "aaaaaa",
    "aaaaa",
    "test",
    "asdf",
    "qwerty",
]


def run_fixes() -> None:
    settings = get_settings()
    conn = psycopg2.connect(_sync_url(settings.DATABASE_URL))
    try:
        cur = conn.cursor()

        # -- BUG-12: application descriptions ------------------------------------
        for old, new in APP_DESCRIPTION_FIXES:
            cur.execute(
                "UPDATE applications SET description = %s WHERE description = %s",
                (new, old),
            )
            if cur.rowcount:
                print(f"  [BUG-12] app desc: '{old}' → '{new}'")

        # -- BUG-12: epic descriptions -------------------------------------------
        for old, new in EPIC_DESCRIPTION_FIXES:
            cur.execute(
                "UPDATE epics SET description = %s WHERE description = %s",
                (new, old),
            )
            if cur.rowcount:
                print(f"  [BUG-12] epic desc: '{old}' → '{new}'")

        # -- BUG-12 & BUG-20: ticket title fixes ---------------------------------
        for old, new in TICKET_TITLE_FIXES_BUG12 + TICKET_TITLE_FIXES_BUG20:
            cur.execute(
                "UPDATE tickets SET title = %s WHERE title = %s",
                (new, old),
            )
            if cur.rowcount:
                print(f"  [BUG-12/20] ticket: '{old}' → '{new}'")

        # -- BUG-15: document filename fix ----------------------------------------
        for old, new in DOCUMENT_FILENAME_FIXES:
            cur.execute(
                "UPDATE documents SET filename = %s WHERE filename = %s",
                (new, old),
            )
            if cur.rowcount:
                print(f"  [BUG-15] document filename: '{old}' → '{new}'")

        # -- BUG-16: delete invalid test tickets ---------------------------------
        for title in INVALID_TICKET_TITLES:
            # Delete subtasks first (FK constraint)
            cur.execute(
                "DELETE FROM subtasks WHERE ticket_id IN "
                "(SELECT id FROM tickets WHERE title = %s)",
                (title,),
            )
            # Delete ticket events
            cur.execute(
                "DELETE FROM ticket_events WHERE ticket_id IN "
                "(SELECT id FROM tickets WHERE title = %s)",
                (title,),
            )
            cur.execute(
                "DELETE FROM tickets WHERE title = %s",
                (title,),
            )
            if cur.rowcount:
                print(f"  [BUG-16] deleted test ticket: '{title}'")

        conn.commit()
        print("✅ Correcciones de datos aplicadas exitosamente.")

    except Exception as exc:
        conn.rollback()
        print(f"❌ Error al aplicar correcciones: {exc}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_fixes()
