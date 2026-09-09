"""
Blinda la convención documentada en app/models/base.py: toda relationship()
debe declarar lazy="raise_on_sql".

Sin este test, alguien puede añadir una relación nueva sin darse cuenta de que
el valor por defecto (lazy="select") vuelve a abrir la puerta a los 500 por
MissingGreenlet que motivaron esta convención (ver fase 2.3 y 2.4 del plan).
"""

from sqlalchemy import inspect
from sqlalchemy.orm import RelationshipProperty

from app.models.base import Base


def test_toda_relacion_declara_raise_on_sql():
    infracciones = []

    for mapper in Base.registry.mappers:
        for prop in mapper.iterate_properties:
            if not isinstance(prop, RelationshipProperty):
                continue
            if prop.lazy != "raise_on_sql":
                infracciones.append(
                    f"{mapper.class_.__name__}.{prop.key} tiene lazy={prop.lazy!r}"
                )

    assert not infracciones, (
        "Relaciones sin lazy=\"raise_on_sql\" (ver convención en app/models/base.py):\n"
        + "\n".join(infracciones)
    )


def test_no_hay_mappers_sin_registrar():
    """Sanity check: que la introspección anterior efectivamente vio los modelos."""
    clases = {m.class_.__name__ for m in Base.registry.mappers}
    esperadas = {"User", "Role", "Application", "Epic", "Ticket", "Subtask", "TicketEvent"}
    faltantes = esperadas - clases
    assert not faltantes, f"la introspección no encontró: {faltantes}"


def test_inspeccion_directa_de_una_relacion_conocida():
    """Doble comprobación con la API pública de inspect(), no solo el registro interno."""
    from app.models import Ticket

    assignee_rel = inspect(Ticket).relationships["assignee"]
    assert assignee_rel.lazy == "raise_on_sql"
