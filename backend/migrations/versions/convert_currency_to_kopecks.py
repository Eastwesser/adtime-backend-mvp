"""Convert currency fields to kopecks

Revision ID: 123456789abc
Revises: 1d3e005ea667
Create Date: 2025-08-16 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '123456789abc'
down_revision = '1d3e005ea667'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Step 1: Add temporary columns for data conversion
    op.add_column('payments', sa.Column('amount_kopecks', sa.Integer(), nullable=True))
    op.add_column('market_items', sa.Column('price_kopecks', sa.Integer(), nullable=True))
    
    # Step 2: Convert existing data (multiply by 100 and round)
    op.execute("""
        UPDATE payments 
        SET amount_kopecks = ROUND(amount * 100)
        WHERE amount IS NOT NULL
    """)
    
    op.execute("""
        UPDATE market_items 
        SET price_kopecks = ROUND(price * 100)
        WHERE price IS NOT NULL
    """)
    
    # Step 3: Drop old columns
    op.drop_column('payments', 'amount')
    op.drop_column('market_items', 'price')
    
    # Step 4: Rename temporary columns to original names
    op.alter_column('payments', 'amount_kopecks', new_column_name='amount')
    op.alter_column('market_items', 'price_kopecks', new_column_name='price')
    
    # Step 5: Add NOT NULL constraints
    op.alter_column('payments', 'amount', nullable=False)
    op.alter_column('market_items', 'price', nullable=False)

def downgrade() -> None:
    # Reverse process for downgrade
    
    # Step 1: Add temporary columns for data conversion
    op.add_column('payments', sa.Column('amount_rub', sa.Numeric(10, 2), nullable=True))
    op.add_column('market_items', sa.Column('price_rub', sa.Numeric(10, 2), nullable=True))
    
    # Step 2: Convert data back (divide by 100)
    op.execute("""
        UPDATE payments 
        SET amount_rub = amount / 100.0
        WHERE amount IS NOT NULL
    """)
    
    op.execute("""
        UPDATE market_items 
        SET price_rub = price / 100.0
        WHERE price IS NOT NULL
    """)
    
    # Step 3: Drop integer columns
    op.drop_column('payments', 'amount')
    op.drop_column('market_items', 'price')
    
    # Step 4: Rename temporary columns to original names
    op.alter_column('payments', 'amount_rub', new_column_name='amount')
    op.alter_column('market_items', 'price_rub', new_column_name='price')
    
    # Step 5: Add NOT NULL constraints
    op.alter_column('payments', 'amount', nullable=False)
    op.alter_column('market_items', 'price', nullable=False)
    