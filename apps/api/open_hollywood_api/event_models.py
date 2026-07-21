"""Public API contracts for resumable workflow events."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from open_hollywood_api.services.workflow_events import (
    WorkflowEventPageRecord,
    WorkflowEventRecord,
)


class WorkflowEventEnvelope(BaseModel):
    """One durable, UI-safe workflow timeline event."""

    model_config = ConfigDict(frozen=True)

    id: int
    workflow_run_id: UUID
    event_type: str
    source: str | None
    schema_version: str
    payload: dict[str, Any]
    occurred_at: datetime

    @classmethod
    def from_record(cls, record: WorkflowEventRecord) -> "WorkflowEventEnvelope":
        """Convert the persistence-neutral service record to the API contract."""
        return cls(
            id=record.id,
            workflow_run_id=record.workflow_run_id,
            event_type=record.event_type,
            source=record.source,
            schema_version=record.schema_version,
            payload=record.payload,
            occurred_at=record.occurred_at,
        )


class WorkflowEventPage(BaseModel):
    """Exclusive-cursor replay page for a workflow run."""

    model_config = ConfigDict(frozen=True)

    events: list[WorkflowEventEnvelope]
    next_after: int
    has_more: bool

    @classmethod
    def from_record(cls, page: WorkflowEventPageRecord) -> "WorkflowEventPage":
        """Convert a service page to its public API representation."""
        return cls(
            events=[WorkflowEventEnvelope.from_record(event) for event in page.events],
            next_after=page.next_after,
            has_more=page.has_more,
        )
