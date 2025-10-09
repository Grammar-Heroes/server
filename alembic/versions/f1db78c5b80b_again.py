"""again

Revision ID: f1db78c5b80b
Revises: 6d7217c42bbd
Create Date: 2025-10-08 22:36:14.975628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1db78c5b80b'
down_revision: Union[str, Sequence[str], None] = '6d7217c42bbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "adventure",
        "cleared_nodes",
        existing_type=sa.ARRAY(sa.String()),
        server_default=None
      )


def downgrade():
        op.alter_column(
        "adventure",
        "cleared_nodes",
        existing_type=sa.ARRAY(sa.String()),
        server_default=None
    )
