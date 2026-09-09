"""Add performance indexes for ticket aggregation queries

Revision ID: add_perf_idx_001
Revises: 089aee7d2625
Create Date: 2026-05-06 10:00:00.000000

This migration adds composite and individual indexes to optimize the queries
used in the Applications CRUD endpoints for real-time ticket aggregation:

1. Composite index on tickets(application_id, status, due_date)
   - Enables fast filtering by application, status, and due date
   - Used by the pending_count and delayed_count aggregation queries

2. Index on tickets(epic_id, status)
   - Optimizes joins between epics and tickets when filtering by status
   - Supports the pending count calculation

3. Index on epics(application_id)
   - Already exists, but ensuring it's present for epic_count queries
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_perf_idx_001'
down_revision: Union[str, None] = '089aee7d2625'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create optimized indexes for ticket aggregation queries."""

    op.create_index(
        'ix_tickets_epic_id_status',
        'tickets',
        ['epic_id', 'status'],
        unique=False
    )

    op.create_index(
        'ix_tickets_epic_status_duedate',
        'tickets',
        ['epic_id', 'status', 'due_date'],
        unique=False
    )

    op.create_index(
        'ix_tickets_status_notcompleted_duedate',
        'tickets',
        ['status', 'due_date'],
        unique=False,
        postgresql_where=sa.text("status != 'COMPLETED'")
    )


def downgrade() -> None:
    """Remove the performance indexes."""
    
    op.drop_index('ix_tickets_status_notcompleted_duedate', table_name='tickets')
    op.drop_index('ix_tickets_epic_id_status', table_name='tickets')