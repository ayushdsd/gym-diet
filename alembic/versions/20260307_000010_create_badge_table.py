"""create badge table with seed data

Revision ID: 20260307_000010
Revises: 20260307_000009
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260307_000010'
down_revision = '20260307_000009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create badge table
    op.create_table(
        'badge',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('tier', sa.String(20), nullable=False),
        sa.Column('icon', sa.String(10), nullable=False),
        sa.Column('unlock_condition', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    
    # Seed initial badges
    op.execute("""
        INSERT INTO badge (name, description, tier, icon, unlock_condition) VALUES
        ('First Steps', 'Logged your first meal', 'bronze', '🍽️', 'meal_count >= 1'),
        ('Consistent Logger', 'Logged meals 7 days in a row', 'silver', '📝', 'streak >= 7'),
        ('Macro Master', 'Hit daily goal 10 times', 'silver', '🎯', 'daily_goals >= 10'),
        ('Week Warrior', 'Maintained a 7-day streak', 'silver', '🔥', 'streak >= 7'),
        ('Month Champion', 'Maintained a 30-day streak', 'gold', '🏆', 'streak >= 30'),
        ('Century Club', 'Maintained a 100-day streak', 'gold', '💯', 'streak >= 100'),
        ('Level 10', 'Reached level 10', 'silver', '⭐', 'level >= 10'),
        ('Level 20', 'Reached level 20', 'gold', '🌟', 'level >= 20'),
        ('Level 50', 'Reached level 50', 'gold', '👑', 'level >= 50')
    """)


def downgrade() -> None:
    # Drop badge table (cascade will handle related records)
    op.drop_table('badge')
