"""Workflow event replay and SSE boundary tests."""

import json
from collections.abc import AsyncIterator
from uuid import UUID

import anyio
import pytest
from httpx import ASGITransport, AsyncClient
from open_hollywood_api.app import create_app
from open_hollywood_api.event_stream import stream_workflow_events
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.services.workflow_events import WorkflowEventStore
from sqlalchemy import Engine

from tests.factories import persist_workflow_run

pytestmark = pytest.mark.anyio


class ConnectedRequest:
    """Disconnect probe that stays connected until its stream is closed."""

    async def is_disconnected(self) -> bool:
        return False


@pytest.fixture
def anyio_backend() -> str:
    """Keep event tests on the asyncio backend used by FastAPI."""
    return "asyncio"


@pytest.fixture
def event_store(database_engine: Engine) -> WorkflowEventStore:
    """Create an event store using the isolated migrated database."""
    return WorkflowEventStore(create_session_factory(database_engine))


@pytest.fixture
def workflow_run_id(database_engine: Engine) -> UUID:
    """Persist a run that API tests can replay."""
    session_factory = create_session_factory(database_engine)
    with session_factory() as session:
        return persist_workflow_run(session).id


@pytest.fixture
async def event_client(event_store: WorkflowEventStore) -> AsyncIterator[AsyncClient]:
    """Create an API client with the isolated event store injected."""
    transport = ASGITransport(app=create_app(event_store))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_replay_endpoint_pages_after_last_event_id(
    event_client: AsyncClient,
    event_store: WorkflowEventStore,
    workflow_run_id: UUID,
) -> None:
    first = event_store.append(workflow_run_id, "run.started", {"node": "intake"})
    second = event_store.append(workflow_run_id, "node.started", {"node": "brief"})
    third = event_store.append(workflow_run_id, "node.completed", {"node": "brief"})

    response = await event_client.get(
        f"/api/v1/workflow-runs/{workflow_run_id}/events",
        params={"after": first.id, "limit": 1},
    )

    assert response.status_code == 200
    page = response.json()
    assert [event["id"] for event in page["events"]] == [second.id]
    assert page["next_after"] == second.id
    assert page["has_more"] is True

    next_response = await event_client.get(
        f"/api/v1/workflow-runs/{workflow_run_id}/events",
        params={"after": page["next_after"], "limit": 10},
    )
    assert [event["id"] for event in next_response.json()["events"]] == [third.id]


async def test_sse_reconnect_replays_only_events_after_last_event_id(
    event_client: AsyncClient,
    event_store: WorkflowEventStore,
    workflow_run_id: UUID,
) -> None:
    first = event_store.append(workflow_run_id, "run.started", {})
    second = event_store.append(workflow_run_id, "node.started", {"node": "brief"})
    third = event_store.append(workflow_run_id, "node.completed", {"node": "brief"})

    response = await event_client.get(
        f"/api/v1/workflow-runs/{workflow_run_id}/events/stream",
        params={"after": 0, "follow": "false"},
        headers={"Last-Event-ID": str(first.id)},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["cache-control"] == "no-cache, no-store"
    frames = [frame for frame in response.text.split("\n\n") if frame]
    ids = [int(frame.splitlines()[0].removeprefix("id: ")) for frame in frames]
    data = [json.loads(frame.splitlines()[2].removeprefix("data: ")) for frame in frames]
    assert ids == [second.id, third.id]
    assert [event["id"] for event in data] == ids


async def test_live_stream_polls_for_events_appended_after_connection(
    event_store: WorkflowEventStore,
    workflow_run_id: UUID,
) -> None:
    stream = stream_workflow_events(
        ConnectedRequest(),
        event_store,
        workflow_run_id,
        0,
        follow=True,
        poll_seconds=0.01,
        heartbeat_seconds=60,
    )

    async def append_later() -> None:
        await anyio.sleep(0.02)
        await anyio.to_thread.run_sync(
            lambda: event_store.append(workflow_run_id, "run.started", {})
        )

    async with anyio.create_task_group() as task_group:
        task_group.start_soon(append_later)
        frame = await anext(stream)
        task_group.cancel_scope.cancel()

    assert "event: run.started" in frame
    await stream.aclose()


async def test_unknown_workflow_run_returns_not_found(
    event_client: AsyncClient,
) -> None:
    unknown_run_id = "00000000-0000-0000-0000-000000000000"
    response = await event_client.get(
        f"/api/v1/workflow-runs/{unknown_run_id}/events",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Workflow run not found"}
