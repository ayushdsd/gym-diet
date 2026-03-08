"""create streak_history table

Revision ID: 20260307_000012
Revises: 20260307_000011
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260307_000012'
down_revision = '20260307_000011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create streak_history table
    op.create_table(
        'streak_history',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('date', sa.Date(), nullable=False, index=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=False),
        sa.Column('freeze_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    
    # Create composite unique constraint for one entry per user per day
    op.create_unique_constraint('uq_user_date', 'streak_history', ['user_id', 'date'])


def downgrade() -> None:
    # Drop streak_history table
    op.drop_table('streak_history')
