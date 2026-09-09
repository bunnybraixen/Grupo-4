"""add_blocked_question_support

Revision ID: c1d2e3f4g5h6
Revises: 5bf0e186bce7
Create Date: 2026-05-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4g5h6'
down_revision: Union[str, None] = '9ea5a499b156'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new enum value for BLOCKED_QUESTION status
    op.execute("ALTER TYPE ticket_status_enum ADD VALUE 'BLOCKED_QUESTION'")

    # Add new columns to tickets table
    op.add_column('tickets', sa.Column('blocked_question', sa.String(length=1000), nullable=True))
    op.add_column('tickets', sa.Column('blocked_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove columns
    op.drop_column('tickets', 'blocked_at')
    op.drop_column('tickets', 'blocked_question')

    # Remove BLOCKED_QUESTION from enum would require recreating the type
    # For now, we'll leave it as a backward-compatible change
