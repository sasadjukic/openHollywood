"""API tests for Story Blueprint human decisions."""

from collections.abc import AsyncIterator
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from open_hollywood_api.app import create_app
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.workflow_events import WorkflowEventStore
from open_hollywood_engine.workflows import BlueprintDecisionAction
from sqlalchemy import Engine

from tests.workflows.test_blueprint_workflow import PersistingExecutor, _persist_run

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Keep API tests on the asyncio backend used by FastAPI."""
    return "asyncio"


@pytest.fixture
async def interrupted_client(
    migrated_database_path: Path,
    database_engine: Engine,
) -> AsyncIterator[tuple[AsyncClient, UUID, str]]:
    """Expose an API backed by a real interrupted SQLite workflow."""
    session_factory = create_session_factory(database_engine)
    workflow_run_id = _persist_run(session_factory)
    executor = PersistingExecutor(session_factory)
    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        executor,
    ) as service:
        interrupted = await service.execute(workflow_run_id)
        assert interrupted.interrupt_id is not None
        application = create_app(
            WorkflowEventStore(session_factory),
            service,
        )
        transport = ASGITransport(app=application)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, workflow_run_id, interrupted.interrupt_id


async def test_approve_endpoint_resumes_the_exact_interrupt(
    interrupted_client: tuple[AsyncClient, UUID, str],
) -> None:
    client, workflow_run_id, interrupt_id = interrupted_client
    decision_id = uuid4()

    response = await client.post(
        f"/api/v1/workflow-runs/{workflow_run_id}/decisions",
        json={
            "action": BlueprintDecisionAction.APPROVE.value,
            "decision_id": str(decision_id),
            "interrupt_id": interrupt_id,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["workflow_run_id"] == str(workflow_run_id)
    assert payload["awaiting_approval"] is False
    assert payload["interrupt_id"] is None
    assert len(payload["artifacts"]) == 9

    duplicate = await client.post(
        f"/api/v1/workflow-runs/{workflow_run_id}/decisions",
        json={
            "action": BlueprintDecisionAction.APPROVE.value,
            "decision_id": str(decision_id),
            "interrupt_id": interrupt_id,
        },
    )
    assert duplicate.status_code == 200
    assert duplicate.json() == payload


async def test_revision_endpoint_requires_an_instruction(
    interrupted_client: tuple[AsyncClient, UUID, str],
) -> None:
    client, workflow_run_id, interrupt_id = interrupted_client

    response = await client.post(
        f"/api/v1/workflow-runs/{workflow_run_id}/decisions",
        json={
            "action": BlueprintDecisionAction.REVISE.value,
            "decision_id": str(uuid4()),
            "interrupt_id": interrupt_id,
        },
    )

    assert response.status_code == 422
