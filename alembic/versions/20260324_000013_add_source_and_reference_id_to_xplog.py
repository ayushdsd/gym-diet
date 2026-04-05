"""add source and reference_id to xplog

Revision ID: 20260324_000013
Revises: 20260307_000012
Create Date: 2026-03-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260324_000013'
down_revision = '20260307_000012'
branch_labels = None
depends_on = None


def upgrade():
    # Add source column with default value
    op.add_column('xplog', sa.Column('source', sa.String(length=50), nullable=False, server_default='meal_log'))
    
    # Add reference_id column (nullable)
    op.add_column('xplog', sa.Column('reference_id', sa.Integer(), nullable=True))
    
    # Create indexes
    op.create_index(op.f('ix_xplog_source'), 'xplog', ['source'], unique=False)
    op.create_index(op.f('ix_xplog_reference_id'), 'xplog', ['reference_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_xplog_reference_id'), table_name='xplog')
    op.drop_index(op.f('ix_xplog_source'), table_name='xplog')
    
    # Drop columns
    op.drop_column('xplog', 'reference_id')
    op.drop_column('xplog', 'source')
