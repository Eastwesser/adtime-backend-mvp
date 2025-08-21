"""add_is_liked_to_generations

Revision ID: 12e666579334
Revises: 333333333333
Create Date: 2025-08-21 13:58:33.010878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12e666579334'
down_revision: Union[str, Sequence[str], None] = '333333333333'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('generations', sa.Column('is_liked', sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
