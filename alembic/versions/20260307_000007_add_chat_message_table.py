"""add_chat_message_table

Revision ID: 20260307_000007
Revises: 20260307_000006
Create Date: 2026-03-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260307_000007'
down_revision = '20260307_000006'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'chatmessage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('sender', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_chatmessage_id'), 'chatmessage', ['id'], unique=False)
    op.create_index(op.f('ix_chatmessage_user_id'), 'chatmessage', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_chatmessage_user_id'), table_name='chatmessage')
    op.drop_index(op.f('ix_chatmessage_id'), table_name='chatmessage')
    op.drop_table('chatmessage')
