"""merge all heads

Revision ID: e77c19d87edb
Revises: af0e5d88082a, ddb71edf27fb
Create Date: 2025-04-16 01:21:26.069630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e77c19d87edb'
down_revision: Union[str, None] = ('af0e5d88082a', 'ddb71edf27fb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
