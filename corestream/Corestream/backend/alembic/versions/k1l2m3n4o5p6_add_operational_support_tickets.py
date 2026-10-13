"""add operational_support_tickets

Revision ID: k1l2m3n4o5p6
Revises: j6k7l8m9n0p1
Create Date: 2026-10-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = 'k1l2m3n4o5p6'
down_revision: Union[str, None] = 'j6k7l8m9n0p1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # IF NOT EXISTS: tolera bases creadas con create_all (sin alembic_version)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE operational_ticket_status AS ENUM ('OPEN', 'RESOLVED');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS operational_support_tickets (
            id UUID PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            problem TEXT NOT NULL,
            status operational_ticket_status NOT NULL,
            timer_started_at TIMESTAMPTZ NOT NULL,
            resolved_at TIMESTAMPTZ,
            elapsed_seconds INTEGER NOT NULL DEFAULT 0,
            resolution_notes TEXT,
            created_by_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            resolved_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    # Existe en create_all pero no en bases antiguas: se tolera el duplicado.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_operational_support_tickets_status "
        "ON operational_support_tickets (status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_operational_support_tickets_created_at "
        "ON operational_support_tickets (created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_operational_support_tickets_created_by_id "
        "ON operational_support_tickets (created_by_id)"
    )


def downgrade() -> None:
    op.drop_table("operational_support_tickets")
    op.execute("DROP TYPE IF EXISTS operational_ticket_status")
