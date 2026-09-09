"""add_support_ticket_fields

Revision ID: b5c6d7e8f9a0
Revises: a9b0c1d2e3f4, 9ea5a499b156
Create Date: 2026-06-26 00:00:00.000000

Extiende el modelo de tickets para soportar tickets de soporte/bugs de producción.
No crea una tabla nueva — usa el mismo modelo con discriminador ticket_type.

Cambios:
- Nuevos valores en ticket_status_enum: REPORTED, INVESTIGATING, RESOLVED
- Nuevo enum ticket_type_enum: DEVELOPMENT, SUPPORT
- Nuevo enum support_severity_enum: CRITICAL, HIGH, MEDIUM, LOW
- Nuevas columnas en tickets: ticket_type, stack_trace, reproduction_steps,
  browser, operating_system, severity, linked_ticket_id
- epic_id pasa a nullable (tickets de soporte no pertenecen a una épica)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'b5c6d7e8f9a0'
down_revision: Union[str, Sequence[str], None] = ('a9b0c1d2e3f4', '9ea5a499b156')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Extender el enum de estado con los valores del workflow de soporte
    op.execute("ALTER TYPE ticket_status_enum ADD VALUE IF NOT EXISTS 'REPORTED'")
    op.execute("ALTER TYPE ticket_status_enum ADD VALUE IF NOT EXISTS 'INVESTIGATING'")
    op.execute("ALTER TYPE ticket_status_enum ADD VALUE IF NOT EXISTS 'RESOLVED'")

    # 2. Crear enum de tipo de ticket
    op.execute(
        "CREATE TYPE ticket_type_enum AS ENUM ('DEVELOPMENT', 'SUPPORT')"
    )

    # 3. Crear enum de severidad para tickets de soporte
    op.execute(
        "CREATE TYPE support_severity_enum AS ENUM ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')"
    )

    # 4. Agregar columnas de soporte a la tabla tickets
    op.add_column(
        'tickets',
        sa.Column(
            'ticket_type',
            postgresql.ENUM('DEVELOPMENT', 'SUPPORT', name='ticket_type_enum', create_type=False),
            nullable=False,
            server_default='DEVELOPMENT',
        ),
    )
    op.add_column('tickets', sa.Column('stack_trace', sa.Text(), nullable=True))
    op.add_column('tickets', sa.Column('reproduction_steps', sa.Text(), nullable=True))
    op.add_column('tickets', sa.Column('browser', sa.String(100), nullable=True))
    op.add_column('tickets', sa.Column('operating_system', sa.String(100), nullable=True))
    op.add_column(
        'tickets',
        sa.Column(
            'severity',
            postgresql.ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', name='support_severity_enum', create_type=False),
            nullable=True,
        ),
    )
    op.add_column(
        'tickets',
        sa.Column(
            'linked_ticket_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('tickets.id', ondelete='SET NULL'),
            nullable=True,
        ),
    )

    # 5. Hacer epic_id nullable (tickets de soporte no pertenecen a una épica)
    op.alter_column('tickets', 'epic_id', nullable=True)

    # 6. Índice en ticket_type para filtrado eficiente
    op.create_index('ix_tickets_ticket_type', 'tickets', ['ticket_type'])


def downgrade() -> None:
    op.drop_index('ix_tickets_ticket_type', table_name='tickets')
    op.alter_column('tickets', 'epic_id', nullable=False)
    op.drop_column('tickets', 'linked_ticket_id')
    op.drop_column('tickets', 'severity')
    op.drop_column('tickets', 'operating_system')
    op.drop_column('tickets', 'browser')
    op.drop_column('tickets', 'reproduction_steps')
    op.drop_column('tickets', 'stack_trace')
    op.drop_column('tickets', 'ticket_type')
    op.execute("DROP TYPE IF EXISTS support_severity_enum")
    op.execute("DROP TYPE IF EXISTS ticket_type_enum")
    # No se pueden eliminar valores de un enum de PostgreSQL sin recrearlo
