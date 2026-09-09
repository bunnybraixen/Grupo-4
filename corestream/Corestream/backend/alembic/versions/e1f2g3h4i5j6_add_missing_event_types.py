"""add_missing_event_types

Revision ID: e1f2g3h4i5j6
Revises: dc9d591ca71e
Create Date: 2026-06-07 03:00:00.000000

"""
from typing import Sequence, Union
from alembic import op


revision: str = 'e1f2g3h4i5j6'
down_revision: Union[str, None] = 'dc9d591ca71e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing values to ticket_event_type_enum that were defined in the model
    # but never added to the DB enum via migration.
    op.execute("ALTER TYPE ticket_event_type_enum ADD VALUE IF NOT EXISTS 'UPDATED'")
    op.execute("ALTER TYPE ticket_event_type_enum ADD VALUE IF NOT EXISTS 'SUBTASK_CREATED'")
    op.execute("ALTER TYPE ticket_event_type_enum ADD VALUE IF NOT EXISTS 'SUBTASK_COMPLETED'")
    op.execute("ALTER TYPE ticket_event_type_enum ADD VALUE IF NOT EXISTS 'SUBTASK_DELETED'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values without recreating the type.
    pass
