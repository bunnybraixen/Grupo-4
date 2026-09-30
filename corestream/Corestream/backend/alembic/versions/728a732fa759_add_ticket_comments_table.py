"""add ticket_comments table

Revision ID: 728a732fa759
Revises: d4e5f6a7b8c9
Create Date: 2026-09-30 01:07:15.214358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = '728a732fa759'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ticket_comments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('ticket_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_ticket_comments_ticket_created',
        'ticket_comments',
        ['ticket_id', 'created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_ticket_comments_ticket_id'),
        'ticket_comments',
        ['ticket_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_ticket_comments_user_id'),
        'ticket_comments',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_ticket_comments_user_id'), table_name='ticket_comments')
    op.drop_index(op.f('ix_ticket_comments_ticket_id'), table_name='ticket_comments')
    op.drop_index('ix_ticket_comments_ticket_created', table_name='ticket_comments')
    op.drop_table('ticket_comments')
