"""Convert currency fields to kopecks

Revision ID: 333333333333
Revises: 222222222222
Create Date: 2025-08-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '333333333333'
down_revision = '222222222222'
branch_labels = None
depends_on = None

def upgrade():
    # MarketItems price conversion
    op.alter_column('market_items', 'price',
                   type_=sa.Integer(),
                   postgresql_using="ROUND(price * 100)")
    
    # Payments amount conversion
    op.alter_column('payments', 'amount',
                   type_=sa.Integer(),
                   postgresql_using="ROUND(amount * 100)")

def downgrade():
    # Revert MarketItems
    op.alter_column('market_items', 'price',
                   type_=sa.Numeric(10, 2),
                   postgresql_using="price / 100.0")
    
    # Revert Payments
    op.alter_column('payments', 'amount',
                   type_=sa.Numeric(10, 2),
                   postgresql_using="amount / 100.0")