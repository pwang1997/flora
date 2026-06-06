"""add unique source path

Revision ID: cd8db0fcb7d7
Revises: 581e70c72c0c
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cd8db0fcb7d7"
down_revision: Union[str, Sequence[str], None] = "581e70c72c0c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "uq_sources_config_source_path",
        "sources",
        [sa.text("(config ->> 'source_path')")],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("uq_sources_config_source_path", table_name="sources")
