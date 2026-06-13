"""remove source document content hash

Revision ID: a4f2c8d9e1b0
Revises: 91a6d54b2c31
Create Date: 2026-06-08 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4f2c8d9e1b0"
down_revision: Union[str, Sequence[str], None] = "91a6d54b2c31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "ck_source_documents_content_hash_not_blank",
        "source_documents",
        type_="check",
    )
    op.drop_column("source_documents", "content_hash")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "source_documents",
        sa.Column("content_hash", sa.String(length=64), nullable=True),
    )
    op.execute("UPDATE source_documents SET content_hash = 'unknown' WHERE content_hash IS NULL")
    op.alter_column("source_documents", "content_hash", nullable=False)
    op.create_check_constraint(
        "ck_source_documents_content_hash_not_blank",
        "source_documents",
        "length(trim(content_hash)) > 0",
    )
