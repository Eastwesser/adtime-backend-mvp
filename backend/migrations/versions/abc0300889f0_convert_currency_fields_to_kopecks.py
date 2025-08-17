"""convert currency fields to kopecks

Revision ID: abc0300889f0
Revises: 88684a029245
Create Date: 2025-08-16 23:30:52.531764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc0300889f0'
down_revision: Union[str, Sequence[str], None] = '88684a029245'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
