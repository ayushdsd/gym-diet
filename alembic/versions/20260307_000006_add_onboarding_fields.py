"""add onboarding fields

Revision ID: 20260307_000006
Revises: 20260307_000005
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260307_000006'
down_revision = '20260307_000005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add onboarding fields to user table
    op.add_column('user', sa.Column('onboarding_completed', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('gender', sa.String(length=10), nullable=True))
    op.add_column('user', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('height', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('weight', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('goal_type', sa.String(length=20), nullable=True))
    op.add_column('user', sa.Column('target_calories', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('target_protein', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('target_carbs', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('target_fats', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove onboarding fields
    op.drop_column('user', 'target_fats')
    op.drop_column('user', 'target_carbs')
    op.drop_column('user', 'target_protein')
    op.drop_column('user', 'target_calories')
    op.drop_column('user', 'goal_type')
    op.drop_column('user', 'weight')
    op.drop_column('user', 'height')
    op.drop_column('user', 'age')
    op.drop_column('user', 'gender')
    op.drop_column('user', 'onboarding_completed')
