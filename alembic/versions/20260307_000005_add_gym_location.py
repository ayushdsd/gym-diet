"""add gym location

Revision ID: 20260307_000005
Revises: 20260304_000004
Create Date: 2026-03-07 13:42:54

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260307_000005'
down_revision = '20260304_000004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add location column with a default value
    op.add_column('gym', sa.Column('location', sa.String(length=255), nullable=False, server_default='Unknown'))
    # Create index on location
    op.create_index(op.f('ix_gym_location'), 'gym', ['location'], unique=False)
    # Remove server default after adding the column
    op.alter_column('gym', 'location', server_default=None)


def downgrade() -> None:
    op.drop_index(op.f('ix_gym_location'), table_name='gym')
    op.drop_column('gym', 'location')
