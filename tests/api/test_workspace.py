"""Persisted workspace read-model and API integration tests."""

from collections.abc import AsyncIterator
from decimal import Decimal
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from open_hollywood_api.app import create_app
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    Conversation,
    Evaluation,
    InvocationStatus,
    Message,
    MessageRole,
    Project,
    RunStatus,
    WorkflowEvent,
    WorkflowRun,
    agent_invocation_inputs,
    langgraph_checkpoints,
    langgraph_writes,
)
from open_hollywood_api.services.workflow_events import WorkflowEventStore
from open_hollywood_api.services.workspace import WorkspaceStore
from open_hollywood_engine.workflows import RunPauseReason
from sqlalchemy import Engine, func, insert, select

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Keep API tests on the asyncio backend used by FastAPI."""
    return "asyncio"


def _persist_workspace(database_engine: Engine) -> tuple[UUID, UUID, UUID]:
    session_factory = create_session_factory(database_engine)
    with session_factory.begin() as session:
        project = Project(
            name="The Untouched Stroller",
            description="A supernatural horror story about an unfinished building.",
        )
        conversation = Conversation(project=project, title="Blueprint development")
        workflow_run = WorkflowRun(
            project=project,
            conversation=conversation,
            workflow_name="story_blueprint",
            graph_version="2",
            status=RunStatus.PAUSED,
            pause_reason=RunPauseReason.HUMAN_APPROVAL,
            current_node="approval",
        )
        conversation.messages.extend(
            [
                Message(
                    sequence_number=1,
                    role=MessageRole.USER,
                    content="A pristine stroller waits outside an abandoned building.",
                    workflow_run=workflow_run,
                ),
                Message(
                    sequence_number=2,
                    role=MessageRole.ASSISTANT,
                    content="The Story Blueprint is ready for your review.",
                    workflow_run=workflow_run,
                ),
            ]
        )
        artifact = Artifact(
            project=project,
            artifact_key="integration_story_blueprint",
            artifact_type="story_blueprint",
            title="Story Blueprint",
            status=ArtifactStatus.DRAFT,
        )
        first_version = ArtifactVersion(
            artifact=artifact,
            version_number=1,
            schema_version="1",
            content={
                "logline": "A grieving woman follows a stroller into a concrete ruin.",
                "story_arc": "Her search turns grief into a confrontation with memory.",
            },
            content_sha256="1" * 64,
            change_summary="Initial integrated blueprint",
        )
        invocation = AgentInvocation(
            workflow_run=workflow_run,
            specialist_role="blueprint_integrator",
            provider="test-provider",
            model_identifier="test-model",
            status=InvocationStatus.SUCCEEDED,
            request_settings={},
            prompt_sha256="3" * 64,
            input_tokens=100,
            output_tokens=200,
            estimated_cost_usd=Decimal("0"),
            schema_validation_succeeded=True,
            input_versions=[first_version],
        )
        second_version = ArtifactVersion(
            artifact=artifact,
            parent_version=first_version,
            created_by_invocation=invocation,
            version_number=2,
            schema_version="1",
            content={
                "logline": "A grieving woman follows an immaculate stroller into a ruin.",
                "story_arc": "Her search turns grief into a confrontation with memory.",
                "proposed_ending": "She leaves the stroller at sunrise.",
            },
            content_sha256="2" * 64,
            change_summary="Sharpened the ending and central image",
        )
        evaluation = Evaluation(
            project=project,
            workflow_run=workflow_run,
            artifact_version=second_version,
            rubric_name="blueprint-quality",
            rubric_version="1",
            scores={"causal_coherence": 4, "originality": 5},
            weighted_score=Decimal("88.50"),
            summary="The image system and ending now reinforce each other.",
        )
        session.add_all(
            [
                project,
                evaluation,
                WorkflowEvent(
                    workflow_run=workflow_run,
                    event_type="workflow.awaiting_approval",
                    source="approval",
                    payload={
                        "interrupt_id": "interrupt-workspace-1",
                        "checkpoint": "story_blueprint",
                    },
                ),
            ]
        )
        session.flush()
        return project.id, workflow_run.id, second_version.id


@pytest.fixture
async def workspace_client(
    database_engine: Engine,
) -> AsyncIterator[tuple[AsyncClient, UUID, UUID, UUID]]:
    """Expose the read API over a realistic persisted project."""
    project_id, workflow_run_id, artifact_version_id = _persist_workspace(database_engine)
    session_factory = create_session_factory(database_engine)
    application = create_app(
        workflow_event_store=WorkflowEventStore(session_factory),
        workspace_store=WorkspaceStore(session_factory),
    )
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, project_id, workflow_run_id, artifact_version_id


async def test_project_list_and_workspace_are_built_from_sqlite(
    workspace_client: tuple[AsyncClient, UUID, UUID, UUID],
) -> None:
    client, project_id, workflow_run_id, artifact_version_id = workspace_client

    projects_response = await client.get("/api/v1/projects")
    workspace_response = await client.get(f"/api/v1/projects/{project_id}/workspace")

    assert projects_response.status_code == 200
    projects = projects_response.json()["projects"]
    assert projects == [
        {
            **projects[0],
            "id": str(project_id),
            "name": "The Untouched Stroller",
            "conversation_count": 1,
            "artifact_count": 1,
            "latest_workflow_run_id": str(workflow_run_id),
            "latest_workflow_status": "paused",
        }
    ]

    assert workspace_response.status_code == 200
    workspace = workspace_response.json()
    assert [message["role"] for message in workspace["conversations"][0]["messages"]] == [
        "user",
        "assistant",
    ]
    assert workspace["workflow_runs"][0]["active_interrupt_id"] == "interrupt-workspace-1"
    artifact = workspace["artifacts"][0]
    assert artifact["active_version_id"] == str(artifact_version_id)
    assert [version["version_number"] for version in artifact["versions"]] == [2, 1]


async def test_artifact_detail_exposes_content_lineage_and_evaluation(
    workspace_client: tuple[AsyncClient, UUID, UUID, UUID],
) -> None:
    client, _, _, artifact_version_id = workspace_client

    response = await client.get(f"/api/v1/artifact-versions/{artifact_version_id}")

    assert response.status_code == 200
    detail = response.json()
    assert detail["selected_version"]["version_number"] == 2
    assert detail["selected_version"]["parent_version_id"] is not None
    assert detail["content"]["proposed_ending"] == "She leaves the stroller at sunrise."
    assert detail["content_sha256"] == "2" * 64
    assert detail["evaluations"][0]["weighted_score"] == "88.50"


async def test_budget_pause_does_not_expose_a_stale_human_interrupt(
    database_engine: Engine,
) -> None:
    project_id, workflow_run_id, _ = _persist_workspace(database_engine)
    session_factory = create_session_factory(database_engine)
    with session_factory.begin() as session:
        workflow_run = session.get(WorkflowRun, workflow_run_id)
        assert workflow_run is not None
        workflow_run.pause_reason = RunPauseReason.BUDGET

    application = create_app(
        workflow_event_store=WorkflowEventStore(session_factory),
        workspace_store=WorkspaceStore(session_factory),
    )
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/projects/{project_id}/workspace")

    assert response.status_code == 200
    assert response.json()["workflow_runs"][0]["active_interrupt_id"] is None


async def test_unknown_workspace_records_return_not_found(
    workspace_client: tuple[AsyncClient, UUID, UUID, UUID],
) -> None:
    client, _, _, _ = workspace_client
    missing_id = "00000000-0000-0000-0000-000000000000"

    project_response = await client.get(f"/api/v1/projects/{missing_id}/workspace")
    version_response = await client.get(f"/api/v1/artifact-versions/{missing_id}")

    assert project_response.status_code == 404
    assert version_response.status_code == 404


async def test_first_premise_creates_an_idempotent_usable_workspace(
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)
    application = create_app(
        workflow_event_store=WorkflowEventStore(session_factory),
        workspace_store=WorkspaceStore(session_factory),
    )
    transport = ASGITransport(app=application)
    request_id = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    request_body = {
        "request_id": request_id,
        "title": "The Last Light",
        "premise": "A lighthouse keeper receives a letter from tomorrow.",
    }

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/api/v1/projects", json=request_body)
        duplicate = await client.post("/api/v1/projects", json=request_body)

        assert created.status_code == 201
        assert duplicate.status_code == 201
        assert duplicate.json() == created.json()
        payload = created.json()
        assert payload["workflow_run_id"] == request_id
        assert payload["status"] == "pending"

        workspace_response = await client.get(f"/api/v1/projects/{payload['project_id']}/workspace")

    assert workspace_response.status_code == 200
    workspace = workspace_response.json()
    assert workspace["project"]["name"] == "The Last Light"
    assert workspace["conversations"][0]["messages"][0]["content"] == request_body["premise"]
    assert workspace["workflow_runs"][0]["status"] == "pending"

    with session_factory() as session:
        assert session.scalar(select(func.count(Project.id))) == 1
        assert session.scalar(select(func.count(WorkflowRun.id))) == 1
        assert session.scalar(select(func.count(Message.id))) == 1
        assert session.scalar(select(func.count(WorkflowEvent.id))) == 1


async def test_reused_intake_request_id_rejects_different_story(
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)
    application = create_app(workspace_store=WorkspaceStore(session_factory))
    transport = ASGITransport(app=application)
    request_id = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post(
            "/api/v1/projects",
            json={"request_id": request_id, "premise": "The first premise."},
        )
        conflicting = await client.post(
            "/api/v1/projects",
            json={"request_id": request_id, "premise": "A different premise."},
        )

    assert first.status_code == 201
    assert conflicting.status_code == 409


async def test_stopped_project_can_be_deleted_with_its_durable_workspace(
    database_engine: Engine,
) -> None:
    project_id, workflow_run_id, _ = _persist_workspace(database_engine)
    session_factory = create_session_factory(database_engine)
    application = create_app(
        workflow_event_store=WorkflowEventStore(session_factory),
        workspace_store=WorkspaceStore(session_factory),
    )
    transport = ASGITransport(app=application)
    with session_factory.begin() as session:
        session.execute(
            insert(langgraph_checkpoints).values(
                thread_id=str(workflow_run_id),
                checkpoint_ns="",
                checkpoint_id="checkpoint-delete-test",
                checkpoint=b"checkpoint",
                metadata=b"metadata",
            )
        )
        session.execute(
            insert(langgraph_writes).values(
                thread_id=str(workflow_run_id),
                checkpoint_ns="",
                checkpoint_id="checkpoint-delete-test",
                task_id="task-delete-test",
                idx=0,
                channel="result",
                value=b"value",
            )
        )

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/projects/{project_id}")
        missing_workspace = await client.get(f"/api/v1/projects/{project_id}/workspace")

    assert response.status_code == 204
    assert missing_workspace.status_code == 404
    with session_factory() as session:
        assert session.scalar(select(func.count(Project.id))) == 0
        assert session.scalar(select(func.count(Conversation.id))) == 0
        assert session.scalar(select(func.count(WorkflowRun.id))) == 0
        assert session.scalar(select(func.count(Message.id))) == 0
        assert session.scalar(select(func.count(Artifact.id))) == 0
        assert session.scalar(select(func.count(ArtifactVersion.id))) == 0
        assert session.scalar(select(func.count(AgentInvocation.id))) == 0
        assert session.scalar(select(func.count(Evaluation.id))) == 0
        assert session.scalar(select(func.count(WorkflowEvent.id))) == 0
        assert session.scalar(select(func.count()).select_from(agent_invocation_inputs)) == 0
        assert session.scalar(select(func.count()).select_from(langgraph_checkpoints)) == 0
        assert session.scalar(select(func.count()).select_from(langgraph_writes)) == 0
        assert session.get(WorkflowRun, workflow_run_id) is None


async def test_active_project_must_be_stopped_before_deletion(
    database_engine: Engine,
) -> None:
    project_id, workflow_run_id, _ = _persist_workspace(database_engine)
    session_factory = create_session_factory(database_engine)
    with session_factory.begin() as session:
        workflow_run = session.get(WorkflowRun, workflow_run_id)
        assert workflow_run is not None
        workflow_run.status = RunStatus.RUNNING

    application = create_app(workspace_store=WorkspaceStore(session_factory))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/projects/{project_id}")

    assert response.status_code == 409
    assert response.json()["detail"] == "Stop the active workflow before deleting this story"
    with session_factory() as session:
        assert session.get(Project, project_id) is not None
