"""add gamification fields

Revision ID: 20260307_000008
Revises: 20260307_000007
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260307_000008'
down_revision = '20260307_000007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add gamification fields to user table
    op.add_column('user', sa.Column('streak_freeze_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('highest_streak', sa.Integer(), nullable=False, server_default='0'))
    
    # Update existing users: set highest_streak = current_streak where current_streak > 0
    op.execute('UPDATE "user" SET highest_streak = current_streak WHERE current_streak > 0')


def downgrade() -> None:
    # Remove gamification fields
    op.drop_column('user', 'highest_streak')
    op.drop_column('user', 'streak_freeze_count')
