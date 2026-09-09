"""add invitations table and users.must_change_password

Revision ID: f3a4b5c6d7e8
Revises: e8395d114663
Create Date: 2026-08-04 00:00:00.000000

Fase 3 del plan de producción: cierra el registro público (se sustituye por
invitaciones por enlace, fase 3.7) y añade la bandera que fuerza el cambio de
contraseña cuando un ADMIN resetea la de otro usuario (fase 3.8).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, None] = 'e8395d114663'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column(
            'must_change_password',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.create_table(
        'invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('token_hash'),
    )
    op.create_index('ix_invitations_email', 'invitations', ['email'])
    op.create_index('ix_invitations_token_hash', 'invitations', ['token_hash'])


def downgrade() -> None:
    op.drop_index('ix_invitations_token_hash', table_name='invitations')
    op.drop_index('ix_invitations_email', table_name='invitations')
    op.drop_table('invitations')
    op.drop_column('users', 'must_change_password')
