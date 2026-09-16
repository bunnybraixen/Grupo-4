"""Probe temporal de diagnóstico (WEB-08) - BORRAR DESPUÉS."""
import sys
import asyncio

sys.stdout.reconfigure(encoding="utf-8")

from app.config import get_settings
from app.database import Base

print("1) DATABASE_URL =", get_settings().DATABASE_URL)
print("2) tablas en Base.metadata (app.database):", sorted(Base.metadata.tables.keys()) or "(NINGUNA)")

try:
    import app.models  # fuerza el import de todos los modelos

    print("3) tras importar app.models:", sorted(Base.metadata.tables.keys()) or "(NINGUNA)")
except Exception as e:
    print("3) ERROR importando app.models:", type(e).__name__, e)

try:
    from app.models.base import Base as BaseModels

    print("4) Base de models es la MISMA que app.database?", BaseModels is Base)
except Exception as e:
    print("4) ERROR importando models.base:", type(e).__name__, e)


async def listar_tablas_bd():
    import asyncpg

    conn = await asyncpg.connect(
        host="postgres", user="corestream", password="corestream", database="corestream"
    )
    rows = await conn.fetch(
        "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY 1"
    )
    print("5) TABLAS REALES EN POSTGRES:", [r[0] for r in rows] or "(VACIA)")
    await conn.close()


asyncio.run(listar_tablas_bd())
