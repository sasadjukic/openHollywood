"""Distinguish provider cost evidence from numeric placeholders.

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Preserve historical amounts without inventing their missing provenance."""
    op.add_column(
        "agent_invocations",
        sa.Column("cost_basis", sa.String(24), nullable=False, server_default="UNKNOWN"),
    )


def downgrade() -> None:
    """Remove provenance while leaving the original numeric amounts untouched."""
    op.drop_column("agent_invocations", "cost_basis")
