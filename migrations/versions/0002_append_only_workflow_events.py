"""Add the append-only workflow event stream.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create a globally ordered event log protected against mutation."""
    op.create_table(
        "workflow_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("schema_version", sa.String(length=50), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_workflow_events_workflow_run_id_workflow_runs"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflow_events")),
    )
    op.create_index(
        "ix_workflow_events_workflow_run_id_id",
        "workflow_events",
        ["workflow_run_id", "id"],
    )
    op.execute(
        """
        CREATE TRIGGER workflow_events_reject_update
        BEFORE UPDATE ON workflow_events
        BEGIN
            SELECT RAISE(ABORT, 'workflow_events are append-only');
        END
        """
    )
    op.execute(
        """
        CREATE TRIGGER workflow_events_reject_delete
        BEFORE DELETE ON workflow_events
        BEGIN
            SELECT RAISE(ABORT, 'workflow_events are append-only');
        END
        """
    )


def downgrade() -> None:
    """Remove the workflow event log and its mutation guards."""
    op.execute("DROP TRIGGER IF EXISTS workflow_events_reject_delete")
    op.execute("DROP TRIGGER IF EXISTS workflow_events_reject_update")
    op.drop_index("ix_workflow_events_workflow_run_id_id", table_name="workflow_events")
    op.drop_table("workflow_events")
