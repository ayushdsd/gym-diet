from alembic import op
import sqlalchemy as sa

revision = "20260304_000002"
down_revision = "20260302_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_user_role_valid",
        "user",
        "role in ('member','admin')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_user_role_valid", "user", type_="check")

