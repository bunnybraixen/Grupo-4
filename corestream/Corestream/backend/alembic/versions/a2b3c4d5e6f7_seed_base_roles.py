"""seed base roles (ADMIN, TEAM_LEADER, DEVELOPER)

Revision ID: a2b3c4d5e6f7
Revises: f3a4b5c6d7e8
Create Date: 2026-08-04 00:00:01.000000

Los tres roles son datos de referencia que el sistema entero asume que
existen (todo FK de rol, todo require_role(), el propio bootstrap del primer
ADMIN) — no son "datos de demostración". Antes se creaban como efecto
secundario de seed_persistent_users.py, que se elimina en esta misma fase
(plan 3.6) por crear además un ADMIN con contraseña conocida en cada
arranque. Al quitar ese script sin más, la tabla roles quedaba vacía y
NADA podía funcionar: ni login, ni create_admin.py, ni un registro por
invitación. Los roles pasan a ser responsabilidad de una migración, como
cualquier otro dato de referencia — se crean una vez, con la base, sin
depender de que alguien ejecute un script a mano en el orden correcto.
"""
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, insert as pg_insert

from alembic import op

revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, None] = 'f3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROLES_TABLE = sa.table(
    'roles',
    sa.column('id', UUID(as_uuid=True)),
    sa.column('name', sa.String),
    sa.column('description', sa.String),
)

ROLES = [
    ('ADMIN', 'Administrador con acceso total al sistema'),
    ('TEAM_LEADER', 'Líder de equipo con permisos expandidos'),
    ('DEVELOPER', 'Desarrollador regular'),
]


def upgrade() -> None:
    conn = op.get_bind()
    for name, description in ROLES:
        stmt = (
            pg_insert(ROLES_TABLE)
            .values(id=uuid.uuid4(), name=name, description=description)
            .on_conflict_do_nothing(index_elements=['name'])
        )
        conn.execute(stmt)


def downgrade() -> None:
    # Deliberadamente no se borran: si hay usuarios referenciando estos
    # roles, borrarlos rompería el FK. Downgrade de esta migración es un
    # no-op intencional.
    pass
