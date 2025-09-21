"""add retries/locks to tasks

Revision ID: fa41fa957c22
Revises: 0c827b4f8610
Create Date: 2025-09-20 18:51:40.165295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'fa41fa957c22'
down_revision: Union[str, Sequence[str], None] = '0c827b4f8610'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("tasks", sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("tasks", sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"))
    op.add_column("tasks", sa.Column("last_error", sa.Text(), nullable=True))
    op.add_column("tasks", sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("locked_by", sa.String(length=64), nullable=True))
    op.alter_column("tasks", "attempt_count", server_default=None)
    op.alter_column("tasks", "max_attempts", server_default=None)

def downgrade() -> None:
    op.drop_column("tasks", "locked_by")
    op.drop_column("tasks", "locked_at")
    op.drop_column("tasks", "next_attempt_at")
    op.drop_column("tasks", "last_error")
    op.drop_column("tasks", "max_attempts")
    op.drop_column("tasks", "attempt_count")