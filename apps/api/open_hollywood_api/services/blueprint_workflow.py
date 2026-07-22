"""SQLite-backed execution service for the first persisted LangGraph."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import aiosqlite
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from open_hollywood_engine.workflows import (
    DEFAULT_MAX_GRAPH_STEPS,
    STORY_BLUEPRINT_GRAPH_VERSION,
    STORY_BLUEPRINT_WORKFLOW_NAME,
    ArtifactReference,
    BlueprintCompiledGraph,
    BlueprintGraphState,
    BlueprintNode,
    BlueprintNodeExecutor,
    BlueprintWorkflowObserver,
    artifact_references_from_state,
    build_blueprint_graph,
    initial_blueprint_state,
)
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import RunStatus, WorkflowEvent, WorkflowRun
from open_hollywood_api.persistence.secret_policy import active_secret_guard

_MIN_GRAPH_STEPS = 8
_MAX_GRAPH_STEPS = 64


@dataclass(frozen=True, slots=True)
class BlueprintWorkflowExecution:
    """Durable result returned when the graph reaches blueprint review."""

    workflow_run_id: UUID
    checkpoint_id: str
    artifacts: tuple[ArtifactReference, ...]
    awaiting_approval: bool


class BlueprintWorkflowRunError(RuntimeError):
    """Raised for unknown or incompatible persisted workflow runs."""


class SqlAlchemyBlueprintWorkflowObserver(BlueprintWorkflowObserver):
    """Mirror graph lifecycle into WorkflowRun and its append-only event log."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    async def node_started(self, workflow_run_id: UUID, node: BlueprintNode) -> None:
        await asyncio.to_thread(self._node_started, workflow_run_id, node)

    def _node_started(self, workflow_run_id: UUID, node: BlueprintNode) -> None:
        with self._session_factory.begin() as session:
            workflow_run = _require_run(session, workflow_run_id)
            workflow_run.status = RunStatus.RUNNING
            workflow_run.current_node = node.value
            workflow_run.started_at = workflow_run.started_at or datetime.now(UTC)
            workflow_run.error_code = None
            workflow_run.error_message = None
            _add_event(
                session,
                workflow_run_id,
                "workflow.node.started",
                {"node": node.value},
                source=node.value,
            )

    async def node_completed(
        self,
        workflow_run_id: UUID,
        node: BlueprintNode,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        await asyncio.to_thread(self._node_completed, workflow_run_id, node, artifacts)

    def _node_completed(
        self,
        workflow_run_id: UUID,
        node: BlueprintNode,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        with self._session_factory.begin() as session:
            _require_run(session, workflow_run_id)
            _add_event(
                session,
                workflow_run_id,
                "workflow.node.completed",
                {
                    "node": node.value,
                    "output_artifacts": [_artifact_payload(artifact) for artifact in artifacts],
                },
                source=node.value,
            )

    async def awaiting_approval(
        self,
        workflow_run_id: UUID,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        await asyncio.to_thread(self._awaiting_approval, workflow_run_id, artifacts)

    def _awaiting_approval(
        self,
        workflow_run_id: UUID,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        with self._session_factory.begin() as session:
            workflow_run = _require_run(session, workflow_run_id)
            workflow_run.status = RunStatus.PAUSED
            workflow_run.current_node = BlueprintNode.APPROVAL.value
            _add_event(
                session,
                workflow_run_id,
                "workflow.awaiting_approval",
                {
                    "artifacts": [_artifact_payload(artifact) for artifact in artifacts],
                    "checkpoint": "story_blueprint",
                },
                source=BlueprintNode.APPROVAL.value,
            )

    async def workflow_failed(self, workflow_run_id: UUID, error: Exception) -> None:
        safe_message = active_secret_guard().redact_text(str(error))[:2000]
        await asyncio.to_thread(self._workflow_failed, workflow_run_id, safe_message)

    def _workflow_failed(self, workflow_run_id: UUID, safe_message: str) -> None:
        with self._session_factory.begin() as session:
            workflow_run = _require_run(session, workflow_run_id)
            workflow_run.status = RunStatus.FAILED
            workflow_run.error_code = "workflow_execution_failed"
            workflow_run.error_message = safe_message
            _add_event(
                session,
                workflow_run_id,
                "workflow.failed",
                {
                    "error_code": "workflow_execution_failed",
                    "node": workflow_run.current_node,
                },
                source=workflow_run.current_node,
            )


class BlueprintWorkflowService:
    """Own the async SQLite checkpointer and execute or resume one graph thread."""

    def __init__(
        self,
        database_path: Path,
        session_factory: sessionmaker[Session],
        executor: BlueprintNodeExecutor,
    ) -> None:
        self._database_path = database_path
        self._session_factory = session_factory
        self._executor = executor
        self._connection: aiosqlite.Connection | None = None
        self._checkpointer: AsyncSqliteSaver | None = None
        self._graph: BlueprintCompiledGraph | None = None

    async def __aenter__(self) -> BlueprintWorkflowService:
        self._connection = await aiosqlite.connect(str(self._database_path))
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA busy_timeout=5000")
        await self._connection.commit()
        serializer = JsonPlusSerializer(allowed_msgpack_modules=None)
        self._checkpointer = AsyncSqliteSaver(self._connection, serde=serializer)
        self._graph = build_blueprint_graph(
            self._executor,
            checkpointer=self._checkpointer,
            observer=SqlAlchemyBlueprintWorkflowObserver(self._session_factory),
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        del exc_type, exc_value, traceback
        if self._connection is not None:
            await self._connection.close()
        self._connection = None
        self._checkpointer = None
        self._graph = None

    async def execute(self, workflow_run_id: UUID) -> BlueprintWorkflowExecution:
        """Start a new graph thread or resume its latest failed super-step."""
        graph, checkpointer = self._require_open()
        max_graph_steps, status = self._run_configuration(workflow_run_id)
        if status is RunStatus.PAUSED:
            raise BlueprintWorkflowRunError("workflow is already awaiting approval")
        if status not in {RunStatus.PENDING, RunStatus.RUNNING, RunStatus.FAILED}:
            raise BlueprintWorkflowRunError(f"workflow cannot execute from status {status.value}")

        config: RunnableConfig = {
            "configurable": {"thread_id": str(workflow_run_id)},
            "recursion_limit": max_graph_steps,
        }
        existing = await checkpointer.aget_tuple(config)
        graph_input = None if existing is not None else initial_blueprint_state(workflow_run_id)
        observer = SqlAlchemyBlueprintWorkflowObserver(self._session_factory)
        try:
            result = cast(BlueprintGraphState, await graph.ainvoke(graph_input, config=config))
        except Exception as exc:
            await observer.workflow_failed(workflow_run_id, exc)
            await self._sync_checkpoint_id(workflow_run_id, graph, config)
            raise

        checkpoint_id = await self._sync_checkpoint_id(workflow_run_id, graph, config)
        awaiting_approval = bool(result.get("awaiting_approval"))
        if not awaiting_approval:
            error = BlueprintWorkflowRunError("blueprint graph ended before approval")
            await observer.workflow_failed(workflow_run_id, error)
            raise error
        return BlueprintWorkflowExecution(
            workflow_run_id=workflow_run_id,
            checkpoint_id=checkpoint_id,
            artifacts=artifact_references_from_state(result),
            awaiting_approval=True,
        )

    def _run_configuration(self, workflow_run_id: UUID) -> tuple[int, RunStatus]:
        with self._session_factory() as session:
            workflow_run = _require_run(session, workflow_run_id)
            if workflow_run.workflow_name != STORY_BLUEPRINT_WORKFLOW_NAME:
                raise BlueprintWorkflowRunError("workflow_run has an incompatible workflow_name")
            if workflow_run.graph_version != STORY_BLUEPRINT_GRAPH_VERSION:
                raise BlueprintWorkflowRunError("workflow_run has an incompatible graph_version")
            raw_steps = workflow_run.budget.get("max_graph_steps", DEFAULT_MAX_GRAPH_STEPS)
            if (
                not isinstance(raw_steps, int)
                or isinstance(raw_steps, bool)
                or not _MIN_GRAPH_STEPS <= raw_steps <= _MAX_GRAPH_STEPS
            ):
                raise BlueprintWorkflowRunError(
                    f"max_graph_steps must be between {_MIN_GRAPH_STEPS} and {_MAX_GRAPH_STEPS}"
                )
            return raw_steps, workflow_run.status

    async def _sync_checkpoint_id(
        self,
        workflow_run_id: UUID,
        graph: BlueprintCompiledGraph,
        config: RunnableConfig,
    ) -> str:
        snapshot = await graph.aget_state(config)
        configurable = snapshot.config.get("configurable", {})
        checkpoint_id = configurable.get("checkpoint_id")
        if not isinstance(checkpoint_id, str) or not checkpoint_id:
            raise BlueprintWorkflowRunError("LangGraph did not persist a checkpoint ID")
        with self._session_factory.begin() as session:
            workflow_run = _require_run(session, workflow_run_id)
            workflow_run.checkpoint_id = checkpoint_id
        return checkpoint_id

    def _require_open(self) -> tuple[BlueprintCompiledGraph, AsyncSqliteSaver]:
        if self._graph is None or self._checkpointer is None:
            raise RuntimeError("BlueprintWorkflowService must be used as an async context manager")
        return self._graph, self._checkpointer


def _require_run(session: Session, workflow_run_id: UUID) -> WorkflowRun:
    workflow_run = session.get(WorkflowRun, workflow_run_id)
    if workflow_run is None:
        raise BlueprintWorkflowRunError(f"unknown workflow run {workflow_run_id}")
    return workflow_run


def _add_event(
    session: Session,
    workflow_run_id: UUID,
    event_type: str,
    payload: dict[str, Any],
    *,
    source: str | None,
) -> None:
    session.add(
        WorkflowEvent(
            workflow_run_id=workflow_run_id,
            event_type=event_type,
            source=source,
            schema_version="1",
            payload=payload,
        )
    )


def _artifact_payload(artifact: ArtifactReference) -> dict[str, str]:
    return {
        "artifact_kind": artifact.kind.value,
        "artifact_key": artifact.artifact_key,
        "artifact_version_id": str(artifact.version_id),
        "schema_version": artifact.schema_version,
    }
