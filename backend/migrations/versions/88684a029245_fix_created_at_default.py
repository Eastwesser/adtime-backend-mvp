"""fix_created_at_default

Revision ID: 88684a029245
Revises: 3d2db5f4c33c
Create Date: 2025-08-14 02:42:05.383663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '88684a029245'
down_revision: Union[str, Sequence[str], None] = '3d2db5f4c33c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('users', 'created_at',
                   existing_type=sa.DateTime(timezone=True),
                   server_default=sa.text('NOW()'),
                   nullable=False)


def downgrade():
    op.alter_column('users', 'created_at',
                   server_default=None,
                   nullable=True)
