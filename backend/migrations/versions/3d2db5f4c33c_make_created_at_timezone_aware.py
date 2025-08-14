"""make_created_at_timezone_aware

Revision ID: 3d2db5f4c33c
Revises: 863ffe69d8af
Create Date: 2025-08-14 02:21:00.201674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d2db5f4c33c'
down_revision: Union[str, Sequence[str], None] = '863ffe69d8af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('users', 'created_at', 
                   type_=sa.DateTime(timezone=True),
                   postgresql_using="created_at AT TIME ZONE 'UTC'")

def downgrade():
    op.alter_column('users', 'created_at',
                   type_=sa.DateTime(timezone=False),
                   postgresql_using="created_at AT TIME ZONE 'UTC'")
