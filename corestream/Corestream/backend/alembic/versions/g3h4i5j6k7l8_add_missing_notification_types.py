"""add_missing_notification_types

Revision ID: g3h4i5j6k7l8
Revises: f2g3h4i5j6k7
Create Date: 2026-06-07 03:15:00.000000

"""
from typing import Sequence, Union
from alembic import op


revision: str = 'g3h4i5j6k7l8'
down_revision: Union[str, None] = 'f2g3h4i5j6k7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The Python NotificationType enum uses different values than the initial DB enum.
    # Add all missing Python enum values to the PostgreSQL type.
    op.execute("ALTER TYPE notification_type_enum ADD VALUE IF NOT EXISTS 'TICKET_ASSIGNED'")
    op.execute("ALTER TYPE notification_type_enum ADD VALUE IF NOT EXISTS 'STATUS_CHANGED'")
    op.execute("ALTER TYPE notification_type_enum ADD VALUE IF NOT EXISTS 'TICKET_REDIRECTED'")
    op.execute("ALTER TYPE notification_type_enum ADD VALUE IF NOT EXISTS 'TICKET_COMPLETED'")
    op.execute("ALTER TYPE notification_type_enum ADD VALUE IF NOT EXISTS 'QUESTION_RAISED'")


def downgrade() -> None:
    pass
