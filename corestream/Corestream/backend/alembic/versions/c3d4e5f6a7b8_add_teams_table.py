"""add teams table

Revision ID: c3d4e5f6a7b8
Revises: a2b3c4d5e6f7
Create Date: 2026-09-25 00:00:00.000000

Los equipos (nombre, miembros por email y aplicaciones asignadas) se guardaban
solo en el `localStorage` del navegador del ADMIN: en cualquier sesión nueva
—otro navegador, otro equipo, una ventana privada— desaparecían, mientras las
aplicaciones y épicas sí llegaban del backend. Esta tabla los persiste para que
el workbench muestre lo mismo a todo el mundo.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'a2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=512), nullable=True),
        sa.Column('member_emails', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('application_ids', sa.JSON(), nullable=False, server_default='[]'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_teams_created_at', 'teams', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_teams_created_at', table_name='teams')
    op.drop_table('teams')
