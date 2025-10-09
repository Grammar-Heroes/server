"""set python default cleared_nodes node0_0

Revision ID: 6d7217c42bbd
Revises: 8e8894fc3e8f
Create Date: 2025-10-08 22:31:01.944166

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d7217c42bbd'
down_revision: Union[str, Sequence[str], None] = '8e8894fc3e8f'
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