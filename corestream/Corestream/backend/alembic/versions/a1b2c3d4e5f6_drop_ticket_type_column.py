"""drop_ticket_type_column

Revision ID: a1b2c3d4e5f6
Revises: 5bf0e186bce7
Create Date: 2026-05-09 07:00:00.000000

La columna ticket_type fue añadida directamente a la BD sin pasar por el ORM
ni por una migración. No está en el modelo Ticket ni en ningún ticket del plan
de desarrollo. Se elimina para desbloquear la creación de tickets.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = ('5bf0e186bce7', 'add_perf_idx_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the orphan column that was manually added to the DB.
    # The column has no corresponding ORM field, schema definition, or enum.
    # Use raw SQL with IF EXISTS to be safe across DB instances.
    op.execute("ALTER TABLE tickets DROP COLUMN IF EXISTS ticket_type")


def downgrade() -> None:
    # Not restoring — the column was never part of the codebase.
    pass
