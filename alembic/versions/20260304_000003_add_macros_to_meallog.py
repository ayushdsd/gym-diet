from alembic import op
import sqlalchemy as sa

revision = "20260304_000003"
down_revision = "20260304_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("meallog", sa.Column("protein", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("meallog", sa.Column("carbs", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("meallog", sa.Column("fats", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("meallog", "protein", server_default=None)
    op.alter_column("meallog", "carbs", server_default=None)
    op.alter_column("meallog", "fats", server_default=None)


def downgrade() -> None:
    op.drop_column("meallog", "fats")
    op.drop_column("meallog", "carbs")
    op.drop_column("meallog", "protein")

