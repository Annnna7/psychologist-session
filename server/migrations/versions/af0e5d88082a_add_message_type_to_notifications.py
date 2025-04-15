"""add_message_type_to_notifications

Revision ID: af0e5d88082a
Revises: 10e1e0a97080
Create Date: 2025-04-16 01:20:30.486011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af0e5d88082a'
down_revision: Union[str, None] = '10e1e0a97080'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
