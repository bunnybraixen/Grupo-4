"""Merge multiple heads

Revision ID: 9ea5a499b156
Revises: a1b2c3d4e5f6
Create Date: 2026-05-09 06:48:47.943691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = '9ea5a499b156'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
