"""create user_badge table

Revision ID: 20260307_000011
Revises: 20260307_000010
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260307_000011'
down_revision = '20260307_000010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_badge table
    op.create_table(
        'user_badge',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('badge_id', sa.Integer(), sa.ForeignKey('badge.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    
    # Create composite unique constraint to prevent duplicate badge unlocks
    op.create_unique_constraint('uq_user_badge', 'user_badge', ['user_id', 'badge_id'])


def downgrade() -> None:
    # Drop user_badge table
    op.drop_table('user_badge')
