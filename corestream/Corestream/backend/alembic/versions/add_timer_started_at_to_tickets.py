"""add timer_started_at to tickets

Revision ID: a9b0c1d2e3f4
Revises: 3eddc7d254c0
Create Date: 2026-06-18 00:00:00.000000

Persists the active-timer start timestamp to the DB so the frontend can
reconstruct elapsed time correctly after a server restart (previously the
value lived only in Redis, which caused 41+ hour phantom times when Redis
survived the restart with a stale key).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a9b0c1d2e3f4'
down_revision: Union[str, None] = '3eddc7d254c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'tickets',
        sa.Column('timer_started_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('tickets', 'timer_started_at')
