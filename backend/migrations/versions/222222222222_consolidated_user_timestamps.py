"""Consolidated user timestamp changes

Revision ID: 222222222222
Revises: 466b80ceb431
Create Date: 2025-08-14 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '222222222222'
down_revision = '466b80ceb431'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', 
        sa.Column('created_at', 
            sa.DateTime(timezone=True), 
            server_default=sa.text('NOW()'), 
            nullable=False
        )
    )

def downgrade():
    op.drop_column('users', 'created_at')