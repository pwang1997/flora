"""create document tables

Revision ID: 7c1d8f2e4b6a
Revises: f09a7c3f5f47
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c1d8f2e4b6a"
down_revision: Union[str, Sequence[str], None] = "f09a7c3f5f47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "source_documents",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.String(length=32), nullable=False),
        sa.Column("external_id", sa.String(length=512), nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=False),
        sa.Column("uri", sa.String(length=2048), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("last_modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(trim(external_id)) > 0", name="ck_source_documents_external_id_not_blank"),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_source_documents_title_not_blank"),
        sa.CheckConstraint("length(trim(content_hash)) > 0", name="ck_source_documents_content_hash_not_blank"),
        sa.CheckConstraint("status IN ('active', 'deleted')", name="ck_source_documents_status_valid"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_source_documents_source_external_id"),
    )
    op.create_index("ix_source_documents_source_id", "source_documents", ["source_id"], unique=False)

    op.create_table(
        "document_versions",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("document_id", sa.String(length=32), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("change_type", sa.String(length=32), nullable=False, server_default="created"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(trim(content_hash)) > 0", name="ck_document_versions_content_hash_not_blank"),
        sa.CheckConstraint("length(trim(content)) > 0", name="ck_document_versions_content_not_blank"),
        sa.CheckConstraint("version_number > 0", name="ck_document_versions_version_number_positive"),
        sa.CheckConstraint(
            "change_type IN ('created', 'updated', 'deleted', 'restored')",
            name="ck_document_versions_change_type_valid",
        ),
        sa.ForeignKeyConstraint(["document_id"], ["source_documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "content_hash", name="uq_document_versions_document_hash"),
        sa.UniqueConstraint("document_id", "version_number", name="uq_document_versions_document_version"),
    )
    op.create_index("ix_document_versions_document_id", "document_versions", ["document_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_document_versions_document_id", table_name="document_versions")
    op.drop_table("document_versions")
    op.drop_index("ix_source_documents_source_id", table_name="source_documents")
    op.drop_table("source_documents")
