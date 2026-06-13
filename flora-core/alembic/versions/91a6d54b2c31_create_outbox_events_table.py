"""create outbox events table

Revision ID: 91a6d54b2c31
Revises: 7c1d8f2e4b6a
Create Date: 2026-06-06 22:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "91a6d54b2c31"
down_revision: Union[str, Sequence[str], None] = "7c1d8f2e4b6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("source_document_id", sa.String(length=32), nullable=False),
        sa.Column("document_version_id", sa.String(length=32), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("retries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.String(), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("claimed_by", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'publishing', 'published', 'failed')",
            name="ck_outbox_events_status_valid",
        ),
        sa.CheckConstraint("retries >= 0", name="ck_outbox_events_retries_non_negative"),
        sa.CheckConstraint("length(trim(event_type)) > 0", name="ck_outbox_events_event_type_not_blank"),
        sa.CheckConstraint("length(trim(topic)) > 0", name="ck_outbox_events_topic_not_blank"),
        sa.CheckConstraint("length(trim(key)) > 0", name="ck_outbox_events_key_not_blank"),
        sa.CheckConstraint(
            "length(trim(idempotency_key)) > 0",
            name="ck_outbox_events_idempotency_key_not_blank",
        ),
        sa.ForeignKeyConstraint(["source_document_id"], ["source_documents.id"]),
        sa.ForeignKeyConstraint(["document_version_id"], ["document_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("ix_outbox_events_document_version_id", "outbox_events", ["document_version_id"], unique=False)
    op.create_index("ix_outbox_events_source_document_id", "outbox_events", ["source_document_id"], unique=False)
    op.create_index(
        "ix_outbox_events_source_document_status",
        "outbox_events",
        ["source_document_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_outbox_events_status_next_attempt_created",
        "outbox_events",
        ["status", "next_attempt_at", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_outbox_events_status_next_attempt_created", table_name="outbox_events")
    op.drop_index("ix_outbox_events_source_document_status", table_name="outbox_events")
    op.drop_index("ix_outbox_events_source_document_id", table_name="outbox_events")
    op.drop_index("ix_outbox_events_document_version_id", table_name="outbox_events")
    op.drop_table("outbox_events")
