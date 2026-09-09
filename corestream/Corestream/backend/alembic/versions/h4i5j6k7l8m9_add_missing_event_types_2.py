"""add_missing_event_types_2

Revision ID: h4i5j6k7l8m9
Revises: g3h4i5j6k7l8
Create Date: 2026-06-07 03:30:00.000000

"""
from typing import Sequence, Union
from alembic import op


revision: str = 'h4i5j6k7l8m9'
down_revision: Union[str, None] = 'g3h4i5j6k7l8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing values to ticket_event_type_enum that exist in the Python model
    # but were never added to the DB type.
    op.execute("ALTER TYPE ticket_event_type_enum ADD VALUE IF NOT EXISTS 'TICKET_ASSIGNED'")
    op.execute("ALTER TYPE ticket_event_type_enum ADD VALUE IF NOT EXISTS 'STATUS_CHANGED'")
    op.execute("ALTER TYPE ticket_event_type_enum ADD VALUE IF NOT EXISTS 'MOVED'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values without recreating the type.
    pass
