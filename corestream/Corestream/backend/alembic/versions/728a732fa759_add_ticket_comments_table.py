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
    pass


def downgrade() -> None:
    pass
