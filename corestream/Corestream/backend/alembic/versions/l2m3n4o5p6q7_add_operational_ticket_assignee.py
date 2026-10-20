"""add assignee to operational support tickets

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
"""
from typing import Sequence, Union

from alembic import op


revision: str = "l2m3n4o5p6q7"
down_revision: Union[str, None] = "k1l2m3n4o5p6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE operational_support_tickets "
        "ADD COLUMN IF NOT EXISTS assignee_id UUID "
        "REFERENCES users(id) ON DELETE SET NULL"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_operational_support_tickets_assignee_id "
        "ON operational_support_tickets (assignee_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_operational_support_tickets_assignee_id")
    op.execute(
        "ALTER TABLE operational_support_tickets DROP COLUMN IF EXISTS assignee_id"
    )