"""Transactional access to the durable workflow event log."""

from dataclasses import dataclass
from datetime import UTC, datetime
from re import Pattern, compile
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import WorkflowEvent, WorkflowRun

EVENT_TYPE_PATTERN: Pattern[str] = compile(r"^[a-z][a-z0-9_.-]{0,99}$")


@dataclass(frozen=True, slots=True)
class WorkflowEventRecord:
    """Persistence-neutral event returned to API and workflow consumers."""

    id: int
    workflow_run_id: UUID
    event_type: str
    source: str | None
    schema_version: str
    payload: dict[str, Any]
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class WorkflowEventPageRecord:
    """Exclusive-cursor page from a single workflow run."""

    events: list[WorkflowEventRecord]
    next_after: int
    has_more: bool


class WorkflowRunNotFoundError(LookupError):
    """Raised when an event operation targets an unknown workflow run."""


def _event_record(event: WorkflowEvent) -> WorkflowEventRecord:
    occurred_at = event.occurred_at
    if occurred_at.tzinfo is None:
        occurred_at = occurred_at.replace(tzinfo=UTC)
    return WorkflowEventRecord(
        id=event.id,
        workflow_run_id=event.workflow_run_id,
        event_type=event.event_type,
        source=event.source,
        schema_version=event.schema_version,
        payload=event.payload,
        occurred_at=occurred_at,
    )


class WorkflowEventStore:
    """Append and replay workflow events using short-lived SQLAlchemy sessions."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def workflow_run_exists(self, workflow_run_id: UUID) -> bool:
        """Return whether the requested run exists."""
        with self._session_factory() as session:
            return session.get(WorkflowRun, workflow_run_id) is not None

    def append(
        self,
        workflow_run_id: UUID,
        event_type: str,
        payload: dict[str, Any],
        *,
        source: str | None = None,
        schema_version: str = "1",
    ) -> WorkflowEventRecord:
        """Atomically append one UI-safe event and return its durable cursor."""
        if EVENT_TYPE_PATTERN.fullmatch(event_type) is None:
            raise ValueError(
                "event_type must start with a lowercase letter and contain only "
                "lowercase letters, digits, dots, underscores, or hyphens"
            )
        if not schema_version.strip() or len(schema_version) > 50:
            raise ValueError("schema_version must contain between 1 and 50 characters")
        if source is not None and (not source.strip() or len(source) > 100):
            raise ValueError("source must contain between 1 and 100 characters")

        with self._session_factory.begin() as session:
            if session.get(WorkflowRun, workflow_run_id) is None:
                raise WorkflowRunNotFoundError(str(workflow_run_id))
            event = WorkflowEvent(
                workflow_run_id=workflow_run_id,
                event_type=event_type,
                source=source,
                schema_version=schema_version,
                payload=dict(payload),
            )
            session.add(event)
            session.flush()
            return _event_record(event)

    def list_after(
        self, workflow_run_id: UUID, after_event_id: int, *, limit: int
    ) -> list[WorkflowEventRecord]:
        """Return events for one run in ascending order, excluding the cursor."""
        if after_event_id < 0:
            raise ValueError("after_event_id must be nonnegative")
        if limit < 1:
            raise ValueError("limit must be positive")

        with self._session_factory() as session:
            events = session.scalars(
                select(WorkflowEvent)
                .where(
                    WorkflowEvent.workflow_run_id == workflow_run_id,
                    WorkflowEvent.id > after_event_id,
                )
                .order_by(WorkflowEvent.id)
                .limit(limit)
            ).all()
            return [_event_record(event) for event in events]

    def page_after(
        self, workflow_run_id: UUID, after_event_id: int, *, limit: int
    ) -> WorkflowEventPageRecord:
        """Return a bounded replay page and the cursor for its last event."""
        if not self.workflow_run_exists(workflow_run_id):
            raise WorkflowRunNotFoundError(str(workflow_run_id))
        records = self.list_after(workflow_run_id, after_event_id, limit=limit + 1)
        has_more = len(records) > limit
        events = records[:limit]
        next_after = events[-1].id if events else after_event_id
        return WorkflowEventPageRecord(
            events=events,
            next_after=next_after,
            has_more=has_more,
        )
