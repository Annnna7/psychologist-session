"""remove_user_id_from_notifications

Revision ID: c222da420547
Revises: 32892c397ca1
Create Date: 2025-04-16 01:38:13.686756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c222da420547'
down_revision: Union[str, None] = '32892c397ca1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

def upgrade():
    # Удаляем столбец user_id
    op.drop_column('notifications', 'user_id')
    
def downgrade():
    # Восстанавливаем столбец (для возможности отката)
    op.add_column('notifications',
                 sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')))