"""require source path

Revision ID: f09a7c3f5f47
Revises: cd8db0fcb7d7
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f09a7c3f5f47"
down_revision: Union[str, Sequence[str], None] = "cd8db0fcb7d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        UPDATE sources
        SET config = jsonb_set(config::jsonb, '{source_path}', config::jsonb -> 'root_path', true)::json
        WHERE config ->> 'source_path' IS NULL
          AND config ->> 'root_path' IS NOT NULL
        """
    )
    op.create_check_constraint(
        "ck_sources_config_source_path_not_blank",
        "sources",
        "config ->> 'source_path' IS NOT NULL AND length(btrim(config ->> 'source_path')) > 0",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_sources_config_source_path_not_blank", "sources", type_="check")
