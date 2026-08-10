"""SQLite-backed execution service for approved-Blueprint scene production."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, NoReturn, cast
from uuid import UUID, uuid5

import aiosqlite
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import StateSnapshot
from open_hollywood_engine.artifacts import (
    ArtifactKind,
    Character,
    ScenePlan,
    StoryBible,
    StoryBlueprint,
)
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.models import ModelCallBudget
from open_hollywood_engine.workflows import (
    PRODUCTION_NODE_DEFINITIONS,
    SCENE_PRODUCTION_GRAPH_VERSION,
    SCENE_PRODUCTION_WORKFLOW_NAME,
    ArtifactReference,
    CharacterTurnResult,
    CharacterTurnTask,
    DialogueSubgraphExecutor,
    DirectorBriefingResult,
    DirectorBriefingTask,
    DirectorEvaluationResult,
    DirectorEvaluationTask,
    ProductionCharacterReference,
    ProductionCompiledGraph,
    ProductionGraphState,
    ProductionNode,
    ProductionUnitInput,
    RunBudget,
    SceneProductionExecutor,
    SceneProductionInput,
    SceneProductionResult,
    SceneProductionWorkflowObserver,
    build_scene_production_graph,
    initial_production_state,
    production_result_from_state,
)
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, sessionmaker

from open_hollywood_api.persistence.models import (
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    RunStatus,
    WorkflowEvent,
    WorkflowRun,
)
from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services.run_controls import (
    RunControlStore,
    WorkflowPausedSignal,
    WorkflowStoppedSignal,
    abandon_active_interval,
    finish_active_interval,
    start_active_interval,
)

MAX_PRODUCTION_GRAPH_STEPS = 128
AGENTIC_BENCHMARK_PRODUCTION_MAX_REVISION_CYCLES = 2


@dataclass(frozen=True, slots=True)
class SceneProductionWorkflowExecution:
    """Latest durable state of one benchmark scene-production run."""

    workflow_run_id: UUID
    checkpoint_id: str
    status: RunStatus
    result: SceneProductionResult | None


class SceneProductionWorkflowRunError(RuntimeError):
    """Raised for invalid or incompatible production-run transitions."""


class SqlAlchemySceneProductionObserver(SceneProductionWorkflowObserver):
    """Mirror production nodes into run budgets and append-only events."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        run_controls: RunControlStore,
    ) -> None:
        self._session_factory = session_factory
        self._run_controls = run_controls

    async def node_started(
        self,
        workflow_run_id: UUID,
        node: ProductionNode,
    ) -> None:
        await asyncio.to_thread(self._node_started, workflow_run_id, node)

    def _node_started(
        self,
        workflow_run_id: UUID,
        node: ProductionNode,
    ) -> None:
        self._run_controls.before_node(
            workflow_run_id,
            node.value,
            includes_model_call=(PRODUCTION_NODE_DEFINITIONS[node].specialist_role is not None),
            default_max_graph_steps=MAX_PRODUCTION_GRAPH_STEPS,
        )
        with self._session_factory.begin() as session:
            run = _require_run(session, workflow_run_id)
            run.status = RunStatus.RUNNING
            run.current_node = node.value
            run.started_at = run.started_at or datetime.now(UTC)
            start_active_interval(run)
            run.error_code = None
            run.error_message = None
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
        node: ProductionNode,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        await asyncio.to_thread(
            self._node_completed,
            workflow_run_id,
            node,
            artifacts,
        )

    def _node_completed(
        self,
        workflow_run_id: UUID,
        node: ProductionNode,
        artifacts: tuple[ArtifactReference, ...],
    ) -> None:
        with self._session_factory.begin() as session:
            run = _require_run(session, workflow_run_id)
            finish_active_interval(run)
            if node is ProductionNode.ACCEPT:
                for reference in artifacts:
                    version = session.get(ArtifactVersion, reference.version_id)
                    if version is not None and reference.kind in {
                        ArtifactKind.SCENE_DRAFT,
                        ArtifactKind.STORY_BIBLE_UPDATE,
                        ArtifactKind.STORY_BIBLE,
                    }:
                        version.artifact.status = ArtifactStatus.APPROVED
            _add_event(
                session,
                workflow_run_id,
                "workflow.node.completed",
                {
                    "node": node.value,
                    "output_artifacts": [_artifact_payload(reference) for reference in artifacts],
                },
                source=node.value,
            )


class _DisabledDialogueExecutor(DialogueSubgraphExecutor):
    async def brief(self, task: DirectorBriefingTask) -> DirectorBriefingResult:
        del task
        return _dialogue_disabled()

    async def perform(self, task: CharacterTurnTask) -> CharacterTurnResult:
        del task
        return _dialogue_disabled()

    async def evaluate(
        self,
        task: DirectorEvaluationTask,
    ) -> DirectorEvaluationResult:
        del task
        return _dialogue_disabled()


def _dialogue_disabled() -> NoReturn:
    raise SceneProductionWorkflowRunError(
        "benchmark production does not enable the optional dialogue subgraph"
    )


class SceneProductionService:
    """Materialize an approved handoff and run the durable production graph."""

    def __init__(
        self,
        *,
        database_path: Path,
        session_factory: sessionmaker[Session],
        executor: SceneProductionExecutor,
        cost_ceiling_usd: Decimal | None = None,
    ) -> None:
        if cost_ceiling_usd is not None and (
            not cost_ceiling_usd.is_finite() or cost_ceiling_usd < Decimal("0.20")
        ):
            raise ValueError("cost_ceiling_usd must be at least the per-call ceiling")
        self._database_path = database_path
        self._session_factory = session_factory
        self._executor = executor
        self._cost_ceiling_usd = cost_ceiling_usd
        self._connection: aiosqlite.Connection | None = None
        self._checkpointer: AsyncSqliteSaver | None = None
        self._graph: ProductionCompiledGraph | None = None
        self._run_controls = RunControlStore(session_factory)
        self._observer = SqlAlchemySceneProductionObserver(
            session_factory,
            self._run_controls,
        )

    async def __aenter__(self) -> SceneProductionService:
        self._connection = await aiosqlite.connect(str(self._database_path))
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA busy_timeout=5000")
        await self._connection.commit()
        serializer = JsonPlusSerializer(allowed_msgpack_modules=None)
        self._checkpointer = AsyncSqliteSaver(self._connection, serde=serializer)
        self._graph = build_scene_production_graph(
            self._executor,
            _DisabledDialogueExecutor(),
            checkpointer=self._checkpointer,
            observer=self._observer,
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

    async def execute(
        self,
        blueprint_run_id: UUID,
        approved_blueprint: ArtifactReference,
    ) -> SceneProductionWorkflowExecution:
        """Create or resume production from one exact approved Blueprint."""
        graph, checkpointer = self._require_open()
        production = await self.prepare(
            blueprint_run_id,
            approved_blueprint,
        )
        max_steps, status = self._run_configuration(production.workflow_run_id)
        if status is RunStatus.SUCCEEDED:
            return await self.inspect(production.workflow_run_id)
        if status is RunStatus.PAUSED:
            return await self.inspect(production.workflow_run_id)
        if status not in {RunStatus.PENDING, RunStatus.RUNNING, RunStatus.FAILED}:
            raise SceneProductionWorkflowRunError(
                f"production cannot execute from status {status.value}"
            )
        if status is RunStatus.RUNNING:
            await asyncio.to_thread(
                self._recover_interrupted_run,
                production.workflow_run_id,
            )
        config = _graph_config(production.workflow_run_id, max_steps)
        existing = await checkpointer.aget_tuple(config)
        graph_input = None if existing is not None else initial_production_state(production)
        try:
            await graph.ainvoke(graph_input, config=config)
            self._run_controls.execution_boundary(production.workflow_run_id)
        except (WorkflowPausedSignal, WorkflowStoppedSignal):
            await self._sync_checkpoint(production.workflow_run_id, graph, config)
            return await self.inspect(production.workflow_run_id)
        except Exception as error:
            await asyncio.to_thread(
                self._fail_run,
                production.workflow_run_id,
                error,
            )
            await self._sync_checkpoint(production.workflow_run_id, graph, config)
            raise
        snapshot = await graph.aget_state(config)
        state = _snapshot_state(snapshot)
        result = production_result_from_state(state)
        checkpoint_id = await self._sync_checkpoint(
            production.workflow_run_id,
            graph,
            config,
            snapshot=snapshot,
        )
        await asyncio.to_thread(
            self._complete_run,
            production.workflow_run_id,
            result,
        )
        return SceneProductionWorkflowExecution(
            workflow_run_id=production.workflow_run_id,
            checkpoint_id=checkpoint_id,
            status=RunStatus.SUCCEEDED,
            result=result,
        )

    async def prepare(
        self,
        blueprint_run_id: UUID,
        approved_blueprint: ArtifactReference,
    ) -> SceneProductionInput:
        """Idempotently persist the approved, immutable production handoff."""
        return await asyncio.to_thread(
            self._materialize_handoff,
            blueprint_run_id,
            approved_blueprint,
        )

    async def inspect(
        self,
        workflow_run_id: UUID,
    ) -> SceneProductionWorkflowExecution:
        """Read the latest production checkpoint without advancing it."""
        graph, _ = self._require_open()
        max_steps, status = self._run_configuration(workflow_run_id)
        snapshot = await graph.aget_state(_graph_config(workflow_run_id, max_steps))
        checkpoint_id = _checkpoint_id(snapshot)
        state = _snapshot_state(snapshot)
        result = (
            production_result_from_state(state)
            if state.get("production_complete") is True
            else None
        )
        return SceneProductionWorkflowExecution(
            workflow_run_id=workflow_run_id,
            checkpoint_id=checkpoint_id,
            status=status,
            result=result,
        )

    def _materialize_handoff(
        self,
        blueprint_run_id: UUID,
        approved_blueprint: ArtifactReference,
    ) -> SceneProductionInput:
        with self._session_factory.begin() as session:
            blueprint_run = _require_run(session, blueprint_run_id)
            if blueprint_run.status is not RunStatus.SUCCEEDED:
                raise SceneProductionWorkflowRunError(
                    "scene production requires a successfully approved Blueprint run"
                )
            blueprint_version = _load_version(
                session,
                approved_blueprint,
                project_id=blueprint_run.project_id,
            )
            if blueprint_version.artifact.status is not ArtifactStatus.APPROVED:
                raise SceneProductionWorkflowRunError(
                    "scene production requires an approved Blueprint artifact"
                )
            invocation = blueprint_version.created_by_invocation
            if (
                invocation is None
                or invocation.workflow_run_id != blueprint_run_id
                or approved_blueprint.kind is not ArtifactKind.STORY_BLUEPRINT
            ):
                raise SceneProductionWorkflowRunError(
                    "approved Blueprint lineage does not match its workflow run"
                )
            blueprint = StoryBlueprint.model_validate(blueprint_version.content)
            scene_plans = tuple(
                _materialize_schema_artifact(
                    session,
                    project_id=blueprint_run.project_id,
                    artifact_key=f"scene_plan_{plan.id}",
                    kind=ArtifactKind.SCENE_PLAN,
                    title=plan.title,
                    content=plan,
                    summary="Materialized from the approved Story Blueprint.",
                )
                for plan in blueprint.scene_plans
            )
            character_references = {
                character.id: _matching_character_reference(
                    session,
                    blueprint_run.project_id,
                    character,
                )
                for character in blueprint.characters
            }
            initial_bible = StoryBible(
                source_blueprint_version_id=approved_blueprint.version_id,
                character_ids=tuple(character.id for character in blueprint.characters),
                relationship_ids=tuple(relationship.id for relationship in blueprint.relationships),
                location_ids=tuple(location.id for location in blueprint.locations),
                world_rule_ids=tuple(rule.id for rule in blueprint.world_rules),
            )
            initial_bible_reference = _materialize_schema_artifact(
                session,
                project_id=blueprint_run.project_id,
                artifact_key="canonical_story_bible",
                kind=ArtifactKind.STORY_BIBLE,
                title="Canonical Story Bible",
                content=initial_bible,
                summary="Initialized deterministically from the approved Story Blueprint.",
            )
            profile_id = _uuid_input(blueprint_run.input_state, "model_profile_id")
            configuration = dict(
                _mapping_input(
                    blueprint_run.input_state,
                    "model_profile_configuration",
                )
            )
            configuration_sha256 = _text_input(
                blueprint_run.input_state,
                "model_profile_configuration_sha256",
            )
            run_seed = _integer_input(blueprint_run.input_state, "run_seed")
            constraints = dict(_mapping_input(blueprint_run.input_state, "benchmark_constraints"))
            production_run_id = uuid5(
                blueprint_run_id,
                "agentic-scene-production-workflow",
            )
            call_budget = ModelCallBudget(
                max_input_tokens=20_000,
                max_output_tokens=8_000,
                max_cost_usd=Decimal("0.20"),
            )
            units = tuple(
                ProductionUnitInput(
                    unit_id=plan.id,
                    unit_number=plan.scene_number,
                    plan=plan_reference,
                    characters=tuple(
                        ProductionCharacterReference(
                            character_id=character_id,
                            artifact=character_references[character_id],
                        )
                        for character_id in plan.character_ids
                    ),
                )
                for plan, plan_reference in zip(
                    blueprint.scene_plans,
                    scene_plans,
                    strict=True,
                )
            )
            provisional = SceneProductionInput(
                workflow_run_id=production_run_id,
                model_profile_id=profile_id,
                approved_blueprint=approved_blueprint,
                initial_story_bible=initial_bible_reference,
                units=units,
                global_context_artifacts=(),
                call_budget=call_budget,
                maximum_revision_cycles=(AGENTIC_BENCHMARK_PRODUCTION_MAX_REVISION_CYCLES),
            )
            budget = RunBudget(
                max_graph_steps=provisional.max_graph_steps,
                max_model_calls=len(units) * 8,
                max_input_tokens=len(units) * 8 * call_budget.max_input_tokens,
                max_output_tokens=len(units) * 8 * call_budget.max_output_tokens,
                max_cost_usd=(
                    self._cost_ceiling_usd
                    if self._cost_ceiling_usd is not None
                    else Decimal(len(units) * 8) * call_budget.max_cost_usd
                ),
                max_wall_clock_seconds=7_200,
                per_call_input_tokens=call_budget.max_input_tokens,
                per_call_output_tokens=call_budget.max_output_tokens,
                per_call_cost_usd=call_budget.max_cost_usd,
            )
            expected_input = {
                "benchmark_constraints": constraints,
                "blueprint_workflow_run_id": str(blueprint_run_id),
                "approved_blueprint_version_id": str(approved_blueprint.version_id),
                "model_profile_id": str(profile_id),
                "model_profile_configuration": configuration,
                "model_profile_configuration_sha256": configuration_sha256,
                "run_seed": run_seed,
            }
            for optional_key in (
                "benchmark_campaign_id",
                "benchmark_case_id",
                "execution_kind",
            ):
                optional_value = blueprint_run.input_state.get(optional_key)
                if optional_value is not None:
                    if not isinstance(optional_value, str) or not optional_value:
                        raise SceneProductionWorkflowRunError(
                            f"Blueprint workflow input {optional_key!r} must be text"
                        )
                    expected_input[optional_key] = optional_value
            production_run = session.get(WorkflowRun, production_run_id)
            if production_run is None:
                production_run = WorkflowRun(
                    id=production_run_id,
                    project_id=blueprint_run.project_id,
                    parent_workflow_run_id=blueprint_run_id,
                    workflow_name=SCENE_PRODUCTION_WORKFLOW_NAME,
                    graph_version=SCENE_PRODUCTION_GRAPH_VERSION,
                    status=RunStatus.PENDING,
                    input_state=expected_input,
                    budget=budget.to_data(),
                )
                session.add(production_run)
            elif (
                production_run.project_id != blueprint_run.project_id
                or production_run.parent_workflow_run_id != blueprint_run_id
                or production_run.workflow_name != SCENE_PRODUCTION_WORKFLOW_NAME
                or production_run.graph_version != SCENE_PRODUCTION_GRAPH_VERSION
                or production_run.input_state != expected_input
            ):
                raise SceneProductionWorkflowRunError(
                    "persisted production lineage conflicts with the approved handoff"
                )
            session.flush()
            return provisional

    def _run_configuration(
        self,
        workflow_run_id: UUID,
    ) -> tuple[int, RunStatus]:
        with self._session_factory() as session:
            run = _require_run(session, workflow_run_id)
            if (
                run.workflow_name != SCENE_PRODUCTION_WORKFLOW_NAME
                or run.graph_version != SCENE_PRODUCTION_GRAPH_VERSION
            ):
                raise SceneProductionWorkflowRunError(
                    "workflow run is not compatible with scene production"
                )
            max_steps = run.budget.get("max_graph_steps")
            if (
                not isinstance(max_steps, int)
                or isinstance(max_steps, bool)
                or not 1 <= max_steps <= MAX_PRODUCTION_GRAPH_STEPS
            ):
                raise SceneProductionWorkflowRunError("production max_graph_steps is invalid")
            return max_steps, run.status

    async def _sync_checkpoint(
        self,
        workflow_run_id: UUID,
        graph: ProductionCompiledGraph,
        config: RunnableConfig,
        *,
        snapshot: StateSnapshot | None = None,
    ) -> str:
        current = snapshot or await graph.aget_state(config)
        checkpoint_id = _checkpoint_id(current)
        with self._session_factory.begin() as session:
            _require_run(session, workflow_run_id).checkpoint_id = checkpoint_id
        return checkpoint_id

    def _complete_run(
        self,
        workflow_run_id: UUID,
        result: SceneProductionResult,
    ) -> None:
        with self._session_factory.begin() as session:
            run = _require_run(session, workflow_run_id)
            if run.status is RunStatus.SUCCEEDED:
                return
            run.status = RunStatus.SUCCEEDED
            finish_active_interval(run)
            run.pause_reason = None
            run.completed_at = datetime.now(UTC)
            run.error_code = None
            run.error_message = None
            _add_event(
                session,
                workflow_run_id,
                "workflow.production.completed",
                {
                    "accepted_scene_version_ids": [
                        str(unit.artifact.version_id) for unit in result.accepted_units
                    ],
                    "final_story_bible_version_id": str(result.final_story_bible.version_id),
                },
                source=ProductionNode.ACCEPT.value,
            )

    def _recover_interrupted_run(self, workflow_run_id: UUID) -> None:
        with self._session_factory.begin() as session:
            run = _require_run(session, workflow_run_id)
            abandon_active_interval(run)
            run.status = RunStatus.PENDING
            _add_event(
                session,
                workflow_run_id,
                "workflow.execution.recovered",
                {"node": run.current_node},
                source="system",
            )

    def _fail_run(self, workflow_run_id: UUID, error: Exception) -> None:
        safe_message = active_secret_guard().redact_text(str(error))[:2_000]
        with self._session_factory.begin() as session:
            run = _require_run(session, workflow_run_id)
            run.status = RunStatus.FAILED
            finish_active_interval(run)
            run.pause_reason = None
            run.error_code = "workflow_execution_failed"
            run.error_message = safe_message
            _add_event(
                session,
                workflow_run_id,
                "workflow.failed",
                {
                    "error_code": "workflow_execution_failed",
                    "node": run.current_node,
                },
                source=run.current_node,
            )

    def _require_open(
        self,
    ) -> tuple[ProductionCompiledGraph, AsyncSqliteSaver]:
        if self._graph is None or self._checkpointer is None:
            raise RuntimeError("SceneProductionService must be used as an async context manager")
        return self._graph, self._checkpointer


def _materialize_schema_artifact(
    session: Session,
    *,
    project_id: UUID,
    artifact_key: str,
    kind: ArtifactKind,
    title: str,
    content: ScenePlan | StoryBible,
    summary: str,
) -> ArtifactReference:
    payload = content.model_dump(mode="json")
    version_id = uuid5(project_id, f"{artifact_key}:version:1")
    artifact = session.scalar(
        select(Artifact)
        .where(
            Artifact.project_id == project_id,
            Artifact.artifact_key == artifact_key,
        )
        .options(joinedload(Artifact.versions))
    )
    if artifact is None:
        artifact = Artifact(
            project_id=project_id,
            artifact_key=artifact_key,
            artifact_type=kind.value,
            title=title[:200],
            status=ArtifactStatus.APPROVED,
        )
        version = ArtifactVersion(
            id=version_id,
            artifact=artifact,
            version_number=1,
            schema_version="1",
            content=payload,
            content_sha256=canonical_sha256(payload),
            change_summary=summary,
        )
        session.add_all((artifact, version))
        session.flush()
        return _reference(version)
    if artifact.artifact_type != kind.value:
        raise SceneProductionWorkflowRunError(
            f"deterministic handoff artifact {artifact_key!r} has conflicting lineage"
        )
    existing_version = next(
        (candidate for candidate in artifact.versions if candidate.id == version_id),
        None,
    )
    if existing_version is None:
        raise SceneProductionWorkflowRunError(
            f"deterministic handoff artifact {artifact_key!r} has no initial version"
        )
    if existing_version.content != payload or existing_version.content_sha256 != canonical_sha256(
        payload
    ):
        raise SceneProductionWorkflowRunError(
            f"deterministic handoff artifact {artifact_key!r} has conflicting content"
        )
    artifact.status = ArtifactStatus.APPROVED
    return _reference(existing_version)


def _matching_character_reference(
    session: Session,
    project_id: UUID,
    character: Character,
) -> ArtifactReference:
    artifact = session.scalar(
        select(Artifact)
        .where(
            Artifact.project_id == project_id,
            Artifact.artifact_key == f"character_{character.id}",
            Artifact.artifact_type == ArtifactKind.CHARACTER.value,
        )
        .options(joinedload(Artifact.versions))
    )
    expected = character.model_dump(mode="json")
    if artifact is None:
        raise SceneProductionWorkflowRunError(
            f"approved Blueprint character {character.id!r} has no specialist artifact"
        )
    version = next(
        (candidate for candidate in reversed(artifact.versions) if candidate.content == expected),
        None,
    )
    if version is None:
        raise SceneProductionWorkflowRunError(
            f"approved Blueprint character {character.id!r} changed its specialist artifact"
        )
    return _reference(version)


def _load_version(
    session: Session,
    reference: ArtifactReference,
    *,
    project_id: UUID,
) -> ArtifactVersion:
    version = session.scalar(
        select(ArtifactVersion)
        .where(ArtifactVersion.id == reference.version_id)
        .options(
            joinedload(ArtifactVersion.artifact),
            joinedload(ArtifactVersion.created_by_invocation),
        )
    )
    if (
        version is None
        or version.artifact.project_id != project_id
        or version.artifact.artifact_key != reference.artifact_key
        or version.artifact.artifact_type != reference.kind.value
        or version.schema_version != reference.schema_version
    ):
        raise SceneProductionWorkflowRunError("approved Blueprint artifact lineage is invalid")
    return version


def _graph_config(workflow_run_id: UUID, max_steps: int) -> RunnableConfig:
    return {
        "configurable": {"thread_id": str(workflow_run_id)},
        "recursion_limit": max_steps,
    }


def _snapshot_state(snapshot: StateSnapshot) -> ProductionGraphState:
    if not isinstance(snapshot.values, dict):
        raise SceneProductionWorkflowRunError("LangGraph production checkpoint state is invalid")
    return cast(ProductionGraphState, snapshot.values)


def _checkpoint_id(snapshot: StateSnapshot) -> str:
    configurable = snapshot.config.get("configurable", {})
    checkpoint_id = configurable.get("checkpoint_id")
    if not isinstance(checkpoint_id, str) or not checkpoint_id:
        raise SceneProductionWorkflowRunError(
            "LangGraph did not persist a production checkpoint ID"
        )
    return checkpoint_id


def _require_run(session: Session, workflow_run_id: UUID) -> WorkflowRun:
    run = session.get(WorkflowRun, workflow_run_id)
    if run is None:
        raise SceneProductionWorkflowRunError(f"unknown workflow run {workflow_run_id}")
    return run


def _reference(version: ArtifactVersion) -> ArtifactReference:
    return ArtifactReference(
        kind=ArtifactKind(version.artifact.artifact_type),
        artifact_key=version.artifact.artifact_key,
        version_id=version.id,
        schema_version=version.schema_version,
    )


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


def _artifact_payload(reference: ArtifactReference) -> dict[str, str]:
    return {
        "artifact_kind": reference.kind.value,
        "artifact_key": reference.artifact_key,
        "artifact_version_id": str(reference.version_id),
        "schema_version": reference.schema_version,
    }


def _mapping_input(value: dict[str, Any], key: str) -> dict[str, object]:
    result = value.get(key)
    if not isinstance(result, dict):
        raise SceneProductionWorkflowRunError(f"Blueprint workflow input {key!r} must be an object")
    return cast(dict[str, object], result)


def _text_input(value: dict[str, Any], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise SceneProductionWorkflowRunError(f"Blueprint workflow input {key!r} must be text")
    return result


def _uuid_input(value: dict[str, Any], key: str) -> UUID:
    try:
        return UUID(_text_input(value, key))
    except ValueError as error:
        raise SceneProductionWorkflowRunError(
            f"Blueprint workflow input {key!r} must be a UUID"
        ) from error


def _integer_input(value: dict[str, Any], key: str) -> int:
    result = value.get(key)
    if not isinstance(result, int) or isinstance(result, bool):
        raise SceneProductionWorkflowRunError(
            f"Blueprint workflow input {key!r} must be an integer"
        )
    return result


# Preserve the public name used by the frozen evaluation harness.
BenchmarkSceneProductionService = SceneProductionService
