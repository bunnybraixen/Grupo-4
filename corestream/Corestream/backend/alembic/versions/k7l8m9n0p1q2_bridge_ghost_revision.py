"""bridge ghost revision k7l8m9n0p1q2

Revision ID: k7l8m9n0p1q2
Revises: j6k7l8m9n0p1
Create Date: 2026-10-14 00:00:00.000000

La base de datos de desarrollo tiene ``alembic_version = 'k7l8m9n0p1q2'``, una
revisión que NUNCA existió en el repositorio (el ticket de soporte se creó con
``k1l2m3n4o5p6`` como hija de ``j6k7l8m9n0p1``). Con ese valor, Alembic lanza
"Can't locate revision identified by 'k7l8m9n0p1q2'" y ``alembic upgrade head``
no aplica NINGUNA migración posterior, por lo que las columnas nuevas
(``assignee_id``) nunca llegaban a la base de datos y la API respondía 500.

Esta migración puente existe únicamente para reconstruir la cadena: no cambia
el esquema, solo sirve de punto de unión entre ``j6k7l8m9n0p1`` (padre real) y
``k1l2m3n4o5p6`` (soporte operacional). Es idempotente: todos los ``IF NOT
EXISTS`` la hacen segura sobre bases ya migradas.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "k7l8m9n0p1q2"
down_revision: Union[str, None] = "j6k7l8m9n0p1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No hay cambios de esquema: esta revisión solo repara la cadena de Alembic.
    pass


def downgrade() -> None:
    pass
