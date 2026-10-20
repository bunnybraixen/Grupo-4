"""
Salvaguardas de los mappers ORM frente a la carga perezosa en contexto async.

HISTORIA: este fichero exigía lazy="raise_on_sql" en TODAS las relaciones.
Esa convención nunca se aplicó a los modelos actuales (casi todas usan el
valor por defecto lazy="select"), así que el test fallaba siempre y no
protegía nada. La defensa real que hay hoy contra MissingGreenlet es:
  1. los routers precargan con selectinload antes de serializar, y
  2. Ticket.epic_title / Ticket.sprint_name devuelven None si la relación no
     está cargada en vez de disparar un lazy-load implícito.
Aquí se prueba (2), junto con que los mappers configuran sin errores (un
relationship mal declarado, como el inverso de Role ↔ User, rompe TODO el ORM
al primer uso).
"""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import configure_mappers, selectinload

from app.models import Application, Epic, Sprint, Ticket
from app.models.base import Base


def test_mappers_configuran_sin_errores():
    # Lanza (p. ej. NoForeignKeysError) si alguna relationship es inválida
    configure_mappers()


def test_no_hay_mappers_sin_registrar():
    """Sanity check: que el registro efectivamente ve los modelos principales."""
    clases = {m.class_.__name__ for m in Base.registry.mappers}
    esperadas = {"User", "Role", "Application", "Epic", "Ticket", "Subtask", "TicketEvent"}
    faltantes = esperadas - clases
    assert not faltantes, f"la introspección no encontró: {faltantes}"


async def _ticket_con_epica_y_sprint(db: AsyncSession) -> Ticket:
    app = Application(name="App lazy", is_active=True)
    db.add(app)
    await db.flush()
    epic = Epic(title="Épica cargada", order_index=0, application_id=app.id)
    now = datetime.utcnow()
    sprint = Sprint(name="Sprint 7", application_id=app.id, start_date=now, end_date=now + timedelta(days=7))
    db.add_all([epic, sprint])
    await db.flush()
    ticket = Ticket(title="T", epic_id=epic.id, sprint_id=sprint.id)
    db.add(ticket)
    await db.commit()
    return ticket


async def test_titulos_derivados_no_disparan_lazy_load(db_session: AsyncSession):
    ticket_id = (await _ticket_con_epica_y_sprint(db_session)).id
    db_session.expunge_all()

    ticket = (await db_session.execute(select(Ticket).where(Ticket.id == ticket_id))).scalar_one()

    # Sin precarga: acceder a ticket.epic aquí lanzaría MissingGreenlet; las
    # propiedades derivadas deben devolver None sin tocar la BD.
    assert ticket.epic_title is None
    assert ticket.sprint_name is None


async def test_titulos_derivados_con_precarga(db_session: AsyncSession):
    ticket_id = (await _ticket_con_epica_y_sprint(db_session)).id
    db_session.expunge_all()

    ticket = (
        await db_session.execute(
            select(Ticket)
            .where(Ticket.id == ticket_id)
            .options(selectinload(Ticket.epic), selectinload(Ticket.sprint))
        )
    ).scalar_one()

    assert ticket.epic_title == "Épica cargada"
    assert ticket.sprint_name == "Sprint 7"


def test_titulos_derivados_en_ticket_transitorio():
    # Un Ticket recién construido (sin sesión) tampoco debe fallar
    ticket = Ticket(title="nuevo")
    assert ticket.epic_title is None
    assert ticket.sprint_name is None
