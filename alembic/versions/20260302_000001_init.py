from alembic import op
import sqlalchemy as sa

revision = "20260302_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gym",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="member"),
        sa.Column("total_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gym_id", sa.Integer(), sa.ForeignKey("gym.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_id", "user", ["id"])
    op.create_index("ix_user_email", "user", ["email"])
    op.create_index("ix_user_gym_id", "user", ["gym_id"])

    op.create_table(
        "meallog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("gym_id", sa.Integer(), sa.ForeignKey("gym.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("calories", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_meallog_id", "meallog", ["id"])
    op.create_index("ix_meallog_user_id", "meallog", ["user_id"])
    op.create_index("ix_meallog_gym_id", "meallog", ["gym_id"])

    op.create_table(
        "xplog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("gym_id", sa.Integer(), sa.ForeignKey("gym.id", ondelete="CASCADE"), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_xplog_id", "xplog", ["id"])
    op.create_index("ix_xplog_user_id", "xplog", ["user_id"])
    op.create_index("ix_xplog_gym_id", "xplog", ["gym_id"])


def downgrade() -> None:
    op.drop_index("ix_xplog_gym_id", table_name="xplog")
    op.drop_index("ix_xplog_user_id", table_name="xplog")
    op.drop_index("ix_xplog_id", table_name="xplog")
    op.drop_table("xplog")

    op.drop_index("ix_meallog_gym_id", table_name="meallog")
    op.drop_index("ix_meallog_user_id", table_name="meallog")
    op.drop_index("ix_meallog_id", table_name="meallog")
    op.drop_table("meallog")

    op.drop_index("ix_user_gym_id", table_name="user")
    op.drop_index("ix_user_email", table_name="user")
    op.drop_index("ix_user_id", table_name="user")
    op.drop_table("user")

    op.drop_table("gym")

