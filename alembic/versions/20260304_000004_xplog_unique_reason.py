from alembic import op
import sqlalchemy as sa

revision = "20260304_000004"
down_revision = "20260304_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_xplog_user_gym_reason", "xplog", ["user_id", "gym_id", "reason"])


def downgrade() -> None:
    op.drop_constraint("uq_xplog_user_gym_reason", "xplog", type_="unique")

