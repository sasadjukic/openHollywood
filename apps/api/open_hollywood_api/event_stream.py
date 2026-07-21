"""Server-Sent Event encoding and durable replay loop."""

from collections.abc import AsyncGenerator
from functools import partial
from time import monotonic
from typing import Protocol
from uuid import UUID

import anyio

from open_hollywood_api.event_models import WorkflowEventEnvelope
from open_hollywood_api.services.workflow_events import WorkflowEventRecord, WorkflowEventStore

STREAM_BATCH_SIZE = 100
STREAM_POLL_SECONDS = 0.5
STREAM_HEARTBEAT_SECONDS = 15.0


class DisconnectProbe(Protocol):
    """Minimal request behavior needed by the streaming loop."""

    async def is_disconnected(self) -> bool:
        """Return whether the streaming client has disconnected."""


def encode_server_sent_event(event: WorkflowEventRecord) -> str:
    """Encode one record as an SSE frame with its durable ID."""
    data = WorkflowEventEnvelope.from_record(event).model_dump_json()
    return f"id: {event.id}\nevent: {event.event_type}\ndata: {data}\n\n"


async def stream_workflow_events(
    request: DisconnectProbe,
    event_store: WorkflowEventStore,
    workflow_run_id: UUID,
    after_event_id: int,
    *,
    follow: bool,
    poll_seconds: float = STREAM_POLL_SECONDS,
    heartbeat_seconds: float = STREAM_HEARTBEAT_SECONDS,
) -> AsyncGenerator[str]:
    """Replay after an exclusive cursor, then poll SQLite until disconnected."""
    cursor = after_event_id
    last_output_at = monotonic()

    while True:
        records = await anyio.to_thread.run_sync(
            partial(
                event_store.list_after,
                workflow_run_id,
                cursor,
                limit=STREAM_BATCH_SIZE,
            )
        )
        if records:
            for record in records:
                cursor = record.id
                yield encode_server_sent_event(record)
            last_output_at = monotonic()
            continue

        if not follow or await request.is_disconnected():
            return

        now = monotonic()
        if now - last_output_at >= heartbeat_seconds:
            yield ": keep-alive\n\n"
            last_output_at = now
        await anyio.sleep(poll_seconds)
