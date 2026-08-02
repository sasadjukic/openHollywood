"""Allow explicit whole-project deletion without weakening event immutability.

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Authorize event removal only inside an explicit project teardown."""
    op.create_table(
        "project_deletion_requests",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_project_deletion_requests_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("project_id", name=op.f("pk_project_deletion_requests")),
    )
    op.execute("DROP TRIGGER workflow_events_reject_delete")
    op.execute(
        """
        CREATE TRIGGER workflow_events_reject_delete
        BEFORE DELETE ON workflow_events
        WHEN NOT EXISTS (
            SELECT 1
            FROM project_deletion_requests AS deletion
            JOIN workflow_runs AS run ON run.project_id = deletion.project_id
            WHERE run.id = OLD.workflow_run_id
        )
        BEGIN
            SELECT RAISE(ABORT, 'workflow_events are append-only');
        END
        """
    )


def downgrade() -> None:
    """Restore the unconditional workflow-event deletion guard."""
    op.execute("DROP TRIGGER workflow_events_reject_delete")
    op.execute(
        """
        CREATE TRIGGER workflow_events_reject_delete
        BEFORE DELETE ON workflow_events
        BEGIN
            SELECT RAISE(ABORT, 'workflow_events are append-only');
        END
        """
    )
    op.drop_table("project_deletion_requests")
