"""add sprints and sla (planificacion temporal + SLA por ticket)

Revision ID: i5j6k7l8m9n0
Revises: 728a732fa759
Create Date: 2026-09-30 00:00:00.000000

Módulo de planificación y seguimiento de Sprints y SLA:

- Tabla `sprints`: período de trabajo (independiente de las épicas).
- Tabla `sla_configs`: objetivos de respuesta/resolución por prioridad (ADMIN).
- `tickets.sprint_id`: asociación OPCIONAL del ticket a un Sprint, adicional a
  su `epic_id` (la relación Épica -> Ticket no cambia).
- `tickets.story_points`: esfuerzo usado para calcular la Velocity del Sprint.
- `tickets.first_response_at`: base del cálculo del SLA de respuesta.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'i5j6k7l8m9n0'
down_revision: Union[str, None] = '728a732fa759'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Sprints (planificación temporal)
    # ------------------------------------------------------------------
    op.create_table(
        'sprints',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('goal', sa.String(length=1000), nullable=True),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            'status',
            postgresql.ENUM('PLANNED', 'ACTIVE', 'COMPLETED', name='sprint_status_enum'),
            nullable=False,
            server_default='PLANNED',
        ),
        sa.Column('velocity', sa.Float(), nullable=False, server_default='0'),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_sprints_application_id'), 'sprints', ['application_id'], unique=False)
    op.create_index(op.f('ix_sprints_status'), 'sprints', ['status'], unique=False)
    op.create_index(op.f('ix_sprints_created_by_id'), 'sprints', ['created_by_id'], unique=False)
    op.create_index(op.f('ix_sprints_created_at'), 'sprints', ['created_at'], unique=False)

    # ------------------------------------------------------------------
    # Configuración de SLA por prioridad (la edita el ADMIN)
    # ------------------------------------------------------------------
    op.create_table(
        'sla_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            'priority',
            postgresql.ENUM(
                'LOW', 'MEDIUM', 'HIGH', 'URGENT',
                name='ticket_priority_enum',
                create_type=False,  # el tipo ya existe (tickets.priority)
            ),
            nullable=False,
        ),
        sa.Column('response_minutes', sa.Integer(), nullable=False, server_default='240'),
        sa.Column('resolution_minutes', sa.Integer(), nullable=False, server_default='1440'),
        sa.Column('warn_threshold_percent', sa.Integer(), nullable=False, server_default='80'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('updated_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('priority', name='uq_sla_configs_priority'),
    )
    op.create_index(op.f('ix_sla_configs_priority'), 'sla_configs', ['priority'], unique=False)
    op.create_index(op.f('ix_sla_configs_created_at'), 'sla_configs', ['created_at'], unique=False)

    # ------------------------------------------------------------------
    # Tickets: sprint opcional + esfuerzo + base del SLA de respuesta
    # ------------------------------------------------------------------
    op.add_column(
        'tickets',
        sa.Column('sprint_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        'fk_tickets_sprint_id',
        'tickets', 'sprints',
        ['sprint_id'], ['id'],
        ondelete='SET NULL',
    )
    op.create_index(op.f('ix_tickets_sprint_id'), 'tickets', ['sprint_id'], unique=False)

    # story_points se agrega nullable y se rellena para evitar NotNullViolation
    op.add_column('tickets', sa.Column('story_points', sa.Integer(), nullable=True))
    op.execute("UPDATE tickets SET story_points = 0 WHERE story_points IS NULL")
    op.alter_column('tickets', 'story_points', nullable=False, server_default='0')

    op.add_column(
        'tickets',
        sa.Column('first_response_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('tickets', 'first_response_at')
    op.drop_column('tickets', 'story_points')
    op.drop_index(op.f('ix_tickets_sprint_id'), table_name='tickets')
    op.drop_constraint('fk_tickets_sprint_id', 'tickets', type_='foreignkey')
    op.drop_column('tickets', 'sprint_id')

    op.drop_index(op.f('ix_sla_configs_created_at'), table_name='sla_configs')
    op.drop_index(op.f('ix_sla_configs_priority'), table_name='sla_configs')
    op.drop_table('sla_configs')

    op.drop_index(op.f('ix_sprints_created_at'), table_name='sprints')
    op.drop_index(op.f('ix_sprints_created_by_id'), table_name='sprints')
    op.drop_index(op.f('ix_sprints_status'), table_name='sprints')
    op.drop_index(op.f('ix_sprints_application_id'), table_name='sprints')
    op.drop_table('sprints')

    postgresql.ENUM(name='sprint_status_enum').drop(op.get_bind(), checkfirst=True)
