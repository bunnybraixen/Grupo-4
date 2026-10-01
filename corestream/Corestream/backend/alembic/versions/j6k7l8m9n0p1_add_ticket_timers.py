"""add ticket work/blocked timers (WEB-09/WEB-12)

Revision ID: j6k7l8m9n0p1
Revises: i5j6k7l8m9n0
Create Date: 2026-10-02 00:00:00.000000

Añade los temporizadores de trabajo en curso y de bloqueo activo. El frontend
los usa para mostrar el tiempo trabajado/bloqueado EN VIVO y el backend para
acumular time_spent_seconds/blocked_time_seconds al cambiar de estado.
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'j6k7l8m9n0p1'
down_revision: Union[str, None] = 'i5j6k7l8m9n0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # IF NOT EXISTS: tolera bases creadas con create_all (sin alembic_version)
    op.execute("ALTER TABLE tickets ADD COLUMN IF NOT EXISTS timer_started_at TIMESTAMPTZ")
    op.execute(
        "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS blocked_timer_started_at TIMESTAMPTZ"
    )


def downgrade() -> None:
    op.drop_column('tickets', 'blocked_timer_started_at')
    op.drop_column('tickets', 'timer_started_at')
