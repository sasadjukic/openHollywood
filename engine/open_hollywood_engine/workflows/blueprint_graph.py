"""LangGraph adapter for the explicit, persisted story-blueprint workflow."""

from __future__ import annotations

from collections import Counter
from collections.abc import Awaitable, Callable
from typing import Annotated, Any, TypedDict
from uuid import UUID

from langchain_core.runnables import Runnable, RunnableLambda
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import RetryPolicy, interrupt

from open_hollywood_engine.artifacts import ArtifactKind
from open_hollywood_engine.workflows.contracts import (
    BLUEPRINT_NODE_DEFINITIONS,
    BLUEPRINT_NODE_ORDER,
    BLUEPRINT_RETRYABLE_NODES,
    ArtifactReference,
    BlueprintDecisionAction,
    BlueprintDecisionResume,
    BlueprintNode,
    BlueprintNodeDefinition,
    BlueprintNodeExecutor,
    BlueprintNodeResult,
    BlueprintNodeTask,
    BlueprintStateError,
    BlueprintWorkflowObserver,
    NullBlueprintWorkflowObserver,
    RetryableSpecialistError,
    node_sort_key,
)


class ArtifactReferenceState(TypedDict):
    """JSON-safe checkpoint representation of an artifact reference."""

    kind: str
    artifact_key: str
    version_id: str
    schema_version: str


class BlueprintGraphState(TypedDict, total=False):
    """Minimal checkpoint state; creative content remains in artifact versions."""

    workflow_run_id: str
    artifacts: Annotated[list[ArtifactReferenceState], _merge_artifact_states]
    completed_nodes: Annotated[list[str], _merge_completed_nodes]
    awaiting_approval: bool
    entry_mode: str
    human_decision_id: str
    human_action: str
    retry_node: str
    run_control_id: str


type BlueprintCompiledGraph = CompiledStateGraph[
    BlueprintGraphState,
    None,
    BlueprintGraphState,
    BlueprintGraphState,
]
type BlueprintNodeCallable = Callable[[BlueprintGraphState], Awaitable[dict[str, Any]]]


def initial_blueprint_state(workflow_run_id: UUID) -> BlueprintGraphState:
    """Create the only accepted input for a new workflow checkpoint thread."""
    return {
        "workflow_run_id": str(workflow_run_id),
        "artifacts": [],
        "completed_nodes": [],
        "awaiting_approval": False,
        "entry_mode": "new",
    }


def initial_blueprint_fork_state(
    workflow_run_id: UUID,
    artifacts: tuple[ArtifactReference, ...],
    human_decision_id: UUID,
) -> BlueprintGraphState:
    """Seed a child thread from exact parent versions before regenerating it."""
    return {
        "workflow_run_id": str(workflow_run_id),
        "artifacts": [_artifact_to_state(artifact) for artifact in artifacts],
        "completed_nodes": [],
        "awaiting_approval": False,
        "entry_mode": "fork",
        "human_decision_id": str(human_decision_id),
        "human_action": BlueprintDecisionAction.FORK.value,
    }


def initial_blueprint_retry_state(
    workflow_run_id: UUID,
    artifacts: tuple[ArtifactReference, ...],
    retry_node: BlueprintNode,
    run_control_id: UUID,
) -> BlueprintGraphState:
    """Seed a child thread at one registered node from compatible exact inputs."""
    if retry_node not in BLUEPRINT_RETRYABLE_NODES:
        raise ValueError(f"node {retry_node.value} cannot be retried")
    retained = retry_artifacts_for_node(artifacts, retry_node)
    _select_inputs(
        {
            "workflow_run_id": str(workflow_run_id),
            "artifacts": [_artifact_to_state(artifact) for artifact in retained],
        },
        BLUEPRINT_NODE_DEFINITIONS[retry_node],
    )
    return {
        "workflow_run_id": str(workflow_run_id),
        "artifacts": [_artifact_to_state(artifact) for artifact in retained],
        "completed_nodes": [],
        "awaiting_approval": False,
        "entry_mode": "retry",
        "retry_node": retry_node.value,
        "run_control_id": str(run_control_id),
    }


def retry_artifacts_for_node(
    artifacts: tuple[ArtifactReference, ...],
    retry_node: BlueprintNode,
) -> tuple[ArtifactReference, ...]:
    """Keep only immutable inputs and independent sibling work for a retry."""
    retained_kinds: dict[BlueprintNode, frozenset[ArtifactKind]] = {
        BlueprintNode.BRIEF: frozenset(),
        BlueprintNode.PREMISE: frozenset({ArtifactKind.CREATIVE_BRIEF}),
        BlueprintNode.WORLD_SPECIALIST: frozenset(
            {
                ArtifactKind.CREATIVE_BRIEF,
                ArtifactKind.PREMISE,
                ArtifactKind.CHARACTER,
                ArtifactKind.RELATIONSHIP,
            }
        ),
        BlueprintNode.CHARACTER_SPECIALIST: frozenset(
            {
                ArtifactKind.CREATIVE_BRIEF,
                ArtifactKind.PREMISE,
                ArtifactKind.LOCATION,
                ArtifactKind.WORLD_RULE,
            }
        ),
        BlueprintNode.INTEGRATION: frozenset(
            {
                ArtifactKind.CREATIVE_BRIEF,
                ArtifactKind.PREMISE,
                ArtifactKind.LOCATION,
                ArtifactKind.WORLD_RULE,
                ArtifactKind.CHARACTER,
                ArtifactKind.RELATIONSHIP,
            }
        ),
        BlueprintNode.EVALUATION: frozenset(
            {
                ArtifactKind.CREATIVE_BRIEF,
                ArtifactKind.PREMISE,
                ArtifactKind.LOCATION,
                ArtifactKind.WORLD_RULE,
                ArtifactKind.CHARACTER,
                ArtifactKind.RELATIONSHIP,
                ArtifactKind.STORY_BLUEPRINT,
            }
        ),
    }
    try:
        allowed = retained_kinds[retry_node]
    except KeyError as error:
        raise ValueError(f"node {retry_node.value} cannot be retried") from error
    return tuple(artifact for artifact in artifacts if artifact.kind in allowed)


def artifact_references_from_state(
    state: BlueprintGraphState,
) -> tuple[ArtifactReference, ...]:
    """Rehydrate immutable references from a checkpoint snapshot."""
    return tuple(_artifact_from_state(item) for item in state.get("artifacts", []))


def build_blueprint_graph(
    executor: BlueprintNodeExecutor,
    *,
    checkpointer: BaseCheckpointSaver[Any],
    observer: BlueprintWorkflowObserver | None = None,
) -> BlueprintCompiledGraph:
    """Compile the fixed graph with durable checkpointing and bounded retries."""
    lifecycle = observer or NullBlueprintWorkflowObserver()
    builder = StateGraph(BlueprintGraphState)
    builder.add_node(BlueprintNode.INTAKE.value, _runnable(_intake_node(lifecycle)))

    for node in BLUEPRINT_NODE_ORDER:
        definition = BLUEPRINT_NODE_DEFINITIONS[node]
        if definition.specialist_role is None:
            continue
        builder.add_node(
            node.value,
            _runnable(_specialist_node(definition, executor, lifecycle)),
            retry_policy=RetryPolicy(
                max_attempts=definition.max_attempts,
                jitter=False,
                retry_on=RetryableSpecialistError,
            ),
            timeout=definition.timeout_seconds,
        )

    builder.add_node(BlueprintNode.APPROVAL.value, _runnable(_approval_node(lifecycle)))
    builder.add_conditional_edges(
        START,
        _route_entry,
        {
            "new": BlueprintNode.INTAKE.value,
            "fork": BlueprintNode.PREMISE.value,
            **{f"retry:{node.value}": node.value for node in BLUEPRINT_RETRYABLE_NODES},
        },
    )
    builder.add_edge(BlueprintNode.INTAKE.value, BlueprintNode.BRIEF.value)
    builder.add_edge(BlueprintNode.BRIEF.value, BlueprintNode.PREMISE.value)
    builder.add_edge(BlueprintNode.PREMISE.value, BlueprintNode.WORLD_SPECIALIST.value)
    builder.add_edge(BlueprintNode.PREMISE.value, BlueprintNode.CHARACTER_SPECIALIST.value)
    builder.add_edge(BlueprintNode.WORLD_SPECIALIST.value, BlueprintNode.INTEGRATION.value)
    builder.add_edge(BlueprintNode.CHARACTER_SPECIALIST.value, BlueprintNode.INTEGRATION.value)
    builder.add_edge(BlueprintNode.INTEGRATION.value, BlueprintNode.EVALUATION.value)
    builder.add_edge(BlueprintNode.EVALUATION.value, BlueprintNode.APPROVAL.value)
    builder.add_conditional_edges(
        BlueprintNode.APPROVAL.value,
        _route_after_approval,
        {
            BlueprintDecisionAction.APPROVE.value: END,
            BlueprintDecisionAction.REVISE.value: BlueprintNode.INTEGRATION.value,
            BlueprintDecisionAction.REJECT.value: BlueprintNode.PREMISE.value,
            BlueprintDecisionAction.FORK.value: END,
        },
    )
    return builder.compile(checkpointer=checkpointer)


def _intake_node(
    observer: BlueprintWorkflowObserver,
) -> BlueprintNodeCallable:
    async def intake(state: BlueprintGraphState) -> dict[str, Any]:
        workflow_run_id = _workflow_run_id(state)
        await observer.node_started(workflow_run_id, BlueprintNode.INTAKE)
        await observer.node_completed(workflow_run_id, BlueprintNode.INTAKE, ())
        return {"completed_nodes": [BlueprintNode.INTAKE.value]}

    return intake


def _specialist_node(
    definition: BlueprintNodeDefinition,
    executor: BlueprintNodeExecutor,
    observer: BlueprintWorkflowObserver,
) -> BlueprintNodeCallable:
    async def execute(state: BlueprintGraphState) -> dict[str, Any]:
        workflow_run_id = _workflow_run_id(state)
        await observer.node_started(workflow_run_id, definition.node)
        inputs = _select_inputs(state, definition)
        role = definition.specialist_role
        if role is None:
            raise BlueprintStateError(f"node {definition.node.value} has no specialist role")
        result = await executor.execute(
            BlueprintNodeTask(
                workflow_run_id=workflow_run_id,
                node=definition.node,
                specialist_role=role,
                input_artifacts=inputs,
                human_decision_id=_human_decision_id(state),
                run_control_id=_run_control_id(state),
                reviewed_artifacts=_reviewed_artifacts(state),
            )
        )
        _validate_outputs(definition, result)
        await observer.node_completed(
            workflow_run_id,
            definition.node,
            result.artifacts,
        )
        return {
            "artifacts": [_artifact_to_state(artifact) for artifact in result.artifacts],
            "completed_nodes": [definition.node.value],
        }

    return execute


def _approval_node(
    observer: BlueprintWorkflowObserver,
) -> BlueprintNodeCallable:
    async def approval(state: BlueprintGraphState) -> dict[str, Any]:
        workflow_run_id = _workflow_run_id(state)
        definition = BLUEPRINT_NODE_DEFINITIONS[BlueprintNode.APPROVAL]
        artifacts = _select_inputs(state, definition)
        resumed = BlueprintDecisionResume.from_payload(
            interrupt(
                {
                    "kind": "story_blueprint_approval",
                    "allowed_actions": [action.value for action in BlueprintDecisionAction],
                    "artifacts": [_artifact_to_state(artifact) for artifact in artifacts],
                }
            )
        )
        await observer.node_completed(workflow_run_id, BlueprintNode.APPROVAL, artifacts)
        return {
            "awaiting_approval": False,
            "completed_nodes": [BlueprintNode.APPROVAL.value],
            "human_decision_id": str(resumed.decision_id),
            "human_action": resumed.action.value,
        }

    return approval


def _select_inputs(
    state: BlueprintGraphState,
    definition: BlueprintNodeDefinition,
) -> tuple[ArtifactReference, ...]:
    artifacts = tuple(_artifact_from_state(item) for item in state.get("artifacts", []))
    selected = tuple(artifact for artifact in artifacts if artifact.kind in definition.input_kinds)
    present_kinds = {artifact.kind for artifact in selected}
    missing = set(definition.input_kinds) - present_kinds
    if missing:
        names = sorted(kind.value for kind in missing)
        raise BlueprintStateError(
            f"node {definition.node.value} is missing input artifact kinds: {names}"
        )
    return tuple(sorted(selected, key=_artifact_sort_key))


def _validate_outputs(
    definition: BlueprintNodeDefinition,
    result: BlueprintNodeResult,
) -> None:
    if not result.artifacts:
        raise BlueprintStateError(f"node {definition.node.value} produced no artifacts")
    version_ids = [artifact.version_id for artifact in result.artifacts]
    if len(set(version_ids)) != len(version_ids):
        raise BlueprintStateError(f"node {definition.node.value} produced duplicate versions")
    artifact_keys = [artifact.artifact_key for artifact in result.artifacts]
    if len(set(artifact_keys)) != len(artifact_keys):
        raise BlueprintStateError(f"node {definition.node.value} produced duplicate artifact keys")

    counts = Counter(artifact.kind for artifact in result.artifacts)
    declared = {requirement.kind for requirement in definition.output_requirements}
    unexpected = set(counts) - declared
    if unexpected:
        names = sorted(kind.value for kind in unexpected)
        raise BlueprintStateError(
            f"node {definition.node.value} produced undeclared artifact kinds: {names}"
        )
    for requirement in definition.output_requirements:
        count = counts[requirement.kind]
        if count < requirement.minimum_count:
            raise BlueprintStateError(
                f"node {definition.node.value} requires {requirement.minimum_count} "
                f"{requirement.kind.value} outputs; received {count}"
            )
        if requirement.maximum_count is not None and count > requirement.maximum_count:
            raise BlueprintStateError(
                f"node {definition.node.value} allows at most {requirement.maximum_count} "
                f"{requirement.kind.value} outputs; received {count}"
            )


def _workflow_run_id(state: BlueprintGraphState) -> UUID:
    value = state.get("workflow_run_id")
    if value is None:
        raise BlueprintStateError("workflow_run_id is missing from checkpoint state")
    try:
        return UUID(value)
    except ValueError as exc:
        raise BlueprintStateError("workflow_run_id is not a valid UUID") from exc


def _human_decision_id(state: BlueprintGraphState) -> UUID | None:
    value = state.get("human_decision_id")
    if value is None:
        return None
    try:
        return UUID(value)
    except ValueError as exc:
        raise BlueprintStateError("human_decision_id is not a valid UUID") from exc


def _run_control_id(state: BlueprintGraphState) -> UUID | None:
    value = state.get("run_control_id")
    if value is None:
        return None
    try:
        return UUID(value)
    except ValueError as exc:
        raise BlueprintStateError("run_control_id is not a valid UUID") from exc


def _reviewed_artifacts(
    state: BlueprintGraphState,
) -> tuple[ArtifactReference, ...]:
    if _human_decision_id(state) is None:
        return ()
    reviewed_kinds = {ArtifactKind.STORY_BLUEPRINT, ArtifactKind.CRITIQUE}
    return tuple(
        sorted(
            (
                _artifact_from_state(item)
                for item in state.get("artifacts", [])
                if ArtifactKind(item["kind"]) in reviewed_kinds
            ),
            key=_artifact_sort_key,
        )
    )


def _route_entry(state: BlueprintGraphState) -> str:
    mode = state.get("entry_mode", "new")
    if mode == "retry":
        raw_node = state.get("retry_node")
        if raw_node is None:
            raise BlueprintStateError("checkpoint contains no retry_node")
        try:
            node = BlueprintNode(raw_node)
        except (TypeError, ValueError) as error:
            raise BlueprintStateError("checkpoint contains an invalid retry_node") from error
        if node not in BLUEPRINT_RETRYABLE_NODES:
            raise BlueprintStateError("checkpoint retry_node is not retryable")
        return f"retry:{node.value}"
    if mode not in {"new", "fork"}:
        raise BlueprintStateError("checkpoint contains an invalid entry_mode")
    return mode


def _route_after_approval(state: BlueprintGraphState) -> str:
    raw_action = state.get("human_action")
    if raw_action is None:
        raise BlueprintStateError("approval completed without a human action")
    try:
        return BlueprintDecisionAction(raw_action).value
    except ValueError as exc:
        raise BlueprintStateError("approval completed without a valid human action") from exc


def _artifact_to_state(reference: ArtifactReference) -> ArtifactReferenceState:
    return {
        "kind": reference.kind.value,
        "artifact_key": reference.artifact_key,
        "version_id": str(reference.version_id),
        "schema_version": reference.schema_version,
    }


def _artifact_from_state(value: ArtifactReferenceState) -> ArtifactReference:
    try:
        return ArtifactReference(
            kind=ArtifactKind(value["kind"]),
            artifact_key=value["artifact_key"],
            version_id=UUID(value["version_id"]),
            schema_version=value["schema_version"],
        )
    except (KeyError, ValueError) as exc:
        raise BlueprintStateError("checkpoint contains an invalid artifact reference") from exc


def _merge_artifact_states(
    left: list[ArtifactReferenceState],
    right: list[ArtifactReferenceState],
) -> list[ArtifactReferenceState]:
    by_key: dict[str, ArtifactReferenceState] = {}
    for item in [*left, *right]:
        artifact_key = item["artifact_key"]
        previous = by_key.get(artifact_key)
        if (
            previous is not None
            and previous["version_id"] == item["version_id"]
            and previous != item
        ):
            raise BlueprintStateError("one artifact version has conflicting checkpoint references")
        by_key[artifact_key] = item
    return sorted(
        by_key.values(),
        key=lambda item: (
            item["kind"],
            item["artifact_key"],
            item["version_id"],
        ),
    )


def _merge_completed_nodes(left: list[str], right: list[str]) -> list[str]:
    try:
        nodes = {BlueprintNode(value) for value in [*left, *right]}
    except ValueError as exc:
        raise BlueprintStateError("checkpoint contains an unknown completed node") from exc
    return [node.value for node in sorted(nodes, key=node_sort_key)]


def _artifact_sort_key(reference: ArtifactReference) -> tuple[str, str, str]:
    return reference.kind.value, reference.artifact_key, str(reference.version_id)


def _runnable(action: BlueprintNodeCallable) -> Runnable[BlueprintGraphState, Any]:
    return RunnableLambda(action)
