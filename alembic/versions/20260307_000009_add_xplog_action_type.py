"""add action_type field to xp_log

Revision ID: 20260307_000009
Revises: 20260307_000008
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260307_000009'
down_revision = '20260307_000008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add action_type field with default value 'meal_logged'
    op.add_column('xplog', sa.Column('action_type', sa.String(50), nullable=False, server_default='meal_logged'))
    
    # Create index on action_type for performance (filtering by action type)
    op.create_index('ix_xplog_action_type', 'xplog', ['action_type'])
    
    # Create index on created_at for history queries (time-based filtering)
    op.create_index('ix_xplog_created_at', 'xplog', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_xplog_created_at', 'xplog')
    op.drop_index('ix_xplog_action_type', 'xplog')
    
    # Drop action_type column
    op.drop_column('xplog', 'action_type')
