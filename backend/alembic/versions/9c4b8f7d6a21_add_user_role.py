"""add_user_role

Revision ID: 9c4b8f7d6a21
Revises: 6bcc67eb49fd
Create Date: 2026-05-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c4b8f7d6a21"
down_revision: Union[str, None] = "6bcc67eb49fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
    )
    op.create_check_constraint(
        "ck_users_role_allowed",
        "users",
        "role IN ('user', 'admin')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_role_allowed", "users", type_="check")
    op.drop_column("users", "role")
