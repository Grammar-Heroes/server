"""BKT params need not be NULL

Revision ID: 188cca7c3da9
Revises: f5421b632b9a
Create Date: 2025-09-15 20:42:09.103614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '188cca7c3da9'
down_revision: Union[str, Sequence[str], None] = 'f5421b632b9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    """Upgrade schema: set defaults for BKT columns."""

    # 1. Fix existing NULL values first
    op.execute("UPDATE knowledge_progress SET p_know = 0.2 WHERE p_know IS NULL")
    op.execute("UPDATE knowledge_progress SET slip = 0.1 WHERE slip IS NULL")
    op.execute("UPDATE knowledge_progress SET guess = 0.2 WHERE guess IS NULL")
    op.execute("UPDATE knowledge_progress SET transit = 0.15 WHERE transit IS NULL")

    # 2. Then enforce defaults and NOT NULL
    op.alter_column(
        "knowledge_progress",
        "p_know",
        existing_type=sa.Float(),
        nullable=False,
        server_default="0.2",
    )
    op.alter_column(
        "knowledge_progress",
        "slip",
        existing_type=sa.Float(),
        nullable=False,
        server_default="0.1",
    )
    op.alter_column(
        "knowledge_progress",
        "guess",
        existing_type=sa.Float(),
        nullable=False,
        server_default="0.2",
    )
    op.alter_column(
        "knowledge_progress",
        "transit",
        existing_type=sa.Float(),
        nullable=False,
        server_default="0.15",
    )


def downgrade() -> None:
    """Downgrade schema: revert defaults for BKT columns."""
    op.alter_column(
        "knowledge_progress",
        "p_know",
        existing_type=sa.Float(),
        nullable=True,
        server_default=None,
    )
    op.alter_column(
        "knowledge_progress",
        "slip",
        existing_type=sa.Float(),
        nullable=True,
        server_default=None,
    )
    op.alter_column(
        "knowledge_progress",
        "guess",
        existing_type=sa.Float(),
        nullable=True,
        server_default=None,
    )
    op.alter_column(
        "knowledge_progress",
        "transit",
        existing_type=sa.Float(),
        nullable=True,
        server_default=None,
    )
