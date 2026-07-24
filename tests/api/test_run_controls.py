"""API integration tests for durable workflow run controls."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient, Response
from open_hollywood_api.app import create_app
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    InvocationStatus,
    RunStatus,
    WorkflowRun,
    WorkflowRunControl,
)
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.workflow_events import WorkflowEventStore
from open_hollywood_engine.workflows import (
    BlueprintNode,
    RunControlStatus,
    RunPauseReason,
)
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from tests.workflows.test_blueprint_workflow import PersistingExecutor, _persist_run

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Keep API tests on the asyncio backend used by FastAPI."""
    return "asyncio"


@asynccontextmanager
async def _run_control_client(
    migrated_database_path: Path,
    database_engine: Engine,
) -> AsyncIterator[
    tuple[
        AsyncClient,
        UUID,
        PersistingExecutor,
        sessionmaker[Session],
        BlueprintWorkflowService,
    ]
]:
    session_factory = create_session_factory(database_engine)
    workflow_run_id = _persist_run(session_factory)
    executor = PersistingExecutor(session_factory)
    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        executor,
    ) as service:
        application = create_app(
            WorkflowEventStore(session_factory),
            service,
        )
        transport = ASGITransport(app=application)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, workflow_run_id, executor, session_factory, service


async def test_pause_resume_and_stop_commands_are_idempotent(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    async with _run_control_client(
        migrated_database_path,
        database_engine,
    ) as (client, workflow_run_id, _, session_factory, _):
        pause_id = uuid4()
        pause = await _control(
            client,
            workflow_run_id,
            {"action": "pause", "command_id": str(pause_id)},
        )
        duplicate = await _control(
            client,
            workflow_run_id,
            {"action": "pause", "command_id": str(pause_id)},
        )

        assert pause.status_code == 200
        assert duplicate.json() == pause.json()
        assert pause.json()["workflow_status"] == "paused"
        assert pause.json()["pause_reason"] == "user"

        resume = await _control(
            client,
            workflow_run_id,
            {"action": "resume", "command_id": str(uuid4())},
        )
        assert resume.status_code == 200
        assert resume.json()["workflow_status"] == "paused"
        assert resume.json()["pause_reason"] == "human_approval"

        stop = await _control(
            client,
            workflow_run_id,
            {"action": "stop", "command_id": str(uuid4())},
        )
        assert stop.status_code == 200
        assert stop.json()["workflow_status"] == "cancelled"

        with session_factory() as session:
            workflow_run = session.get(WorkflowRun, workflow_run_id)
            assert workflow_run is not None
            assert workflow_run.status is RunStatus.CANCELLED
            assert workflow_run.pause_reason is None
            assert len(workflow_run.control_commands) == 3


async def test_budget_exhaustion_pauses_before_model_call_and_can_resume(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    async with _run_control_client(
        migrated_database_path,
        database_engine,
    ) as (client, workflow_run_id, executor, session_factory, service):
        with session_factory.begin() as session:
            workflow_run = session.get(WorkflowRun, workflow_run_id)
            assert workflow_run is not None
            workflow_run.budget = {
                "max_graph_steps": 12,
                "max_model_calls": 1,
            }
            session.add(
                AgentInvocation(
                    workflow_run_id=workflow_run_id,
                    specialist_role="prior_test_call",
                    provider="test",
                    model_identifier="deterministic",
                    status=InvocationStatus.SUCCEEDED,
                    request_settings={},
                    prompt_sha256="0" * 64,
                    input_tokens=10,
                    output_tokens=10,
                )
            )

        execution = await service.execute(workflow_run_id)
        assert not execution.awaiting_approval
        assert executor.calls == []
        with session_factory() as session:
            paused = session.get(WorkflowRun, workflow_run_id)
            assert paused is not None
            assert paused.status is RunStatus.PAUSED
            assert paused.pause_reason is RunPauseReason.BUDGET
            assert paused.current_node == BlueprintNode.BRIEF.value

        budget = await _control(
            client,
            workflow_run_id,
            {
                "action": "update_budget",
                "budget": {"max_model_calls": 10},
                "command_id": str(uuid4()),
            },
        )
        assert budget.status_code == 200
        assert budget.json()["budget"]["max_model_calls"] == 10

        resume = await _control(
            client,
            workflow_run_id,
            {"action": "resume", "command_id": str(uuid4())},
        )
        assert resume.status_code == 200
        assert resume.json()["pause_reason"] == "human_approval"
        assert executor.calls[0] is BlueprintNode.BRIEF


async def test_retry_from_node_creates_child_and_preserves_source_history(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    async with _run_control_client(
        migrated_database_path,
        database_engine,
    ) as (client, workflow_run_id, executor, session_factory, service):
        await service.execute(workflow_run_id)
        initial_call_count = len(executor.calls)
        command_id = uuid4()
        request = {
            "action": "retry_from_node",
            "command_id": str(command_id),
            "target_node": BlueprintNode.INTEGRATION.value,
        }

        response = await _control(client, workflow_run_id, request)

        assert response.status_code == 200
        payload = response.json()
        child_run_id = UUID(payload["resulting_workflow_run_id"])
        assert child_run_id != workflow_run_id
        assert payload["command_status"] == "applied"
        assert executor.calls[initial_call_count:] == [
            BlueprintNode.INTEGRATION,
            BlueprintNode.EVALUATION,
        ]

        with session_factory() as session:
            source = session.get(WorkflowRun, workflow_run_id)
            child = session.get(WorkflowRun, child_run_id)
            command = session.get(WorkflowRunControl, command_id)
            assert source is not None
            assert source.status is RunStatus.CANCELLED
            assert child is not None
            assert child.parent_workflow_run_id == source.id
            assert child.status is RunStatus.PAUSED
            assert child.pause_reason is RunPauseReason.HUMAN_APPROVAL
            assert command is not None
            assert command.resulting_workflow_run_id == child.id

        calls_after_child_completed = len(executor.calls)
        with session_factory.begin() as session:
            command = session.get(WorkflowRunControl, command_id)
            assert command is not None
            command.status = RunControlStatus.PENDING
            command.applied_at = None

        recovered = await _control(client, workflow_run_id, request)
        duplicate = await _control(client, workflow_run_id, request)

        assert recovered.json() == response.json()
        assert duplicate.json() == response.json()
        assert len(executor.calls) == calls_after_child_completed


async def test_retry_rejects_nonretryable_node(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    async with _run_control_client(
        migrated_database_path,
        database_engine,
    ) as (client, workflow_run_id, _, _, service):
        await service.execute(workflow_run_id)
        response = await _control(
            client,
            workflow_run_id,
            {
                "action": "retry_from_node",
                "command_id": str(uuid4()),
                "target_node": BlueprintNode.APPROVAL.value,
            },
        )

        assert response.status_code == 409
        assert "cannot be retried" in response.json()["detail"]


async def _control(
    client: AsyncClient,
    workflow_run_id: UUID,
    payload: Mapping[str, object],
) -> Response:
    return await client.post(
        f"/api/v1/workflow-runs/{workflow_run_id}/controls",
        json=payload,
    )
