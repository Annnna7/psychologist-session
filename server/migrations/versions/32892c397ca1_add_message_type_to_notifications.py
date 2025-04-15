"""add_message_type_to_notifications

Revision ID: 32892c397ca1
Revises: e77c19d87edb
Create Date: 2025-04-16 01:21:50.526493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32892c397ca1'
down_revision: Union[str, None] = 'e77c19d87edb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

def upgrade():
    op.add_column('notifications', 
                 sa.Column('message_type', sa.String(length=1000), nullable=False))
    
def downgrade():
    op.drop_column('notifications', 'message_type')