"""LangGraph adapter for bounded scene-by-scene prose production."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from decimal import Decimal
from typing import Any, TypedDict, cast
from uuid import UUID

from langchain_core.runnables import Runnable, RunnableLambda
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import RetryPolicy

from open_hollywood_engine.artifacts import (
    ArtifactKind,
    CritiqueVerdict,
)
from open_hollywood_engine.models.contracts import ModelCallBudget
from open_hollywood_engine.workflows.contracts import ArtifactReference
from open_hollywood_engine.workflows.dialogue_contracts import (
    DialogueSceneInput,
    DialogueSubgraphExecutor,
)
from open_hollywood_engine.workflows.dialogue_graph import (
    DialogueArtifactReferenceState,
    DialogueGraphState,
    build_dialogue_subgraph,
    dialogue_result_from_state,
    initial_dialogue_state,
)
from open_hollywood_engine.workflows.production_contracts import (
    PRODUCTION_NODE_DEFINITIONS,
    AcceptedProductionUnit,
    DialogueIntegrationTask,
    DialoguePassConfiguration,
    ProductionCharacterReference,
    ProductionNode,
    ProductionUnitInput,
    RetryableSceneProductionError,
    SceneCritiqueResult,
    SceneCritiqueTask,
    SceneDraftResult,
    SceneProductionExecutor,
    SceneProductionInput,
    SceneProductionResult,
    SceneProductionStateError,
    SceneWritingTask,
    UnitAcceptanceReason,
)


class ProductionCharacterState(TypedDict):
    """Checkpoint-safe character identity and artifact reference."""

    character_id: str
    artifact: DialogueArtifactReferenceState


class DialoguePassConfigurationState(TypedDict):
    """JSON-safe configuration for one optional dialogue pass."""

    character_ids: list[str]
    ending_options: list[str]
    minimum_rounds: int
    maximum_rounds: int


class ProductionUnitState(TypedDict):
    """Checkpoint-safe planned production unit."""

    unit_id: str
    unit_number: int
    plan: DialogueArtifactReferenceState
    characters: list[ProductionCharacterState]
    context_artifacts: list[DialogueArtifactReferenceState]
    dialogue_pass: DialoguePassConfigurationState | None


class AcceptedProductionUnitState(TypedDict):
    """JSON-safe canonical-unit result."""

    unit_id: str
    unit_number: int
    artifact: DialogueArtifactReferenceState
    critique_artifact: DialogueArtifactReferenceState
    revision_cycles_used: int
    dialogue_runs: int
    acceptance_reason: str


class ProductionGraphState(DialogueGraphState, total=False):
    """Reference-only coordination state for the production parent graph."""

    approved_blueprint: DialogueArtifactReferenceState
    production_units: list[ProductionUnitState]
    global_context_artifacts: list[DialogueArtifactReferenceState]
    production_max_input_tokens: int
    production_max_output_tokens: int
    production_max_cost_usd: str
    production_prompt_template_version: str
    maximum_revision_cycles: int
    current_unit_index: int
    current_revision_number: int
    current_draft_artifact: DialogueArtifactReferenceState | None
    current_critique_artifact: DialogueArtifactReferenceState | None
    current_dialogue_runs: int
    current_acceptance_reason: str | None
    revision_scheduled: bool
    draft_artifacts: list[DialogueArtifactReferenceState]
    critique_artifacts: list[DialogueArtifactReferenceState]
    accepted_units: list[AcceptedProductionUnitState]
    production_complete: bool


type ProductionCompiledGraph = CompiledStateGraph[
    ProductionGraphState,
    None,
    ProductionGraphState,
    ProductionGraphState,
]
type ProductionNodeCallable = Callable[
    [ProductionGraphState],
    Awaitable[dict[str, Any]],
]


def initial_production_state(production: SceneProductionInput) -> ProductionGraphState:
    """Create JSON-safe input for one approved-blueprint production run."""
    return {
        "workflow_run_id": str(production.workflow_run_id),
        "model_profile_id": str(production.model_profile_id),
        "approved_blueprint": _artifact_to_state(production.approved_blueprint),
        "production_units": [_unit_to_state(unit) for unit in production.units],
        "global_context_artifacts": [
            _artifact_to_state(reference) for reference in production.global_context_artifacts
        ],
        "production_max_input_tokens": production.call_budget.max_input_tokens,
        "production_max_output_tokens": production.call_budget.max_output_tokens,
        "production_max_cost_usd": str(production.call_budget.max_cost_usd),
        "production_prompt_template_version": production.prompt_template_version,
        "maximum_revision_cycles": production.maximum_revision_cycles,
        "current_unit_index": 0,
        "current_revision_number": 0,
        "current_dialogue_runs": 0,
        "current_acceptance_reason": None,
        "revision_scheduled": False,
        "draft_artifacts": [],
        "critique_artifacts": [],
        "accepted_units": [],
        "production_complete": False,
    }


def production_result_from_state(
    state: ProductionGraphState,
) -> SceneProductionResult:
    """Rehydrate the reference-only result of a completed production run."""
    if state.get("production_complete") is not True:
        raise SceneProductionStateError("production checkpoint is not complete")
    production = _production_from_state(state)
    accepted = tuple(_accepted_from_state(item) for item in state.get("accepted_units", []))
    if len(accepted) != len(production.units):
        raise SceneProductionStateError(
            "completed production checkpoint has missing accepted units"
        )
    return SceneProductionResult(
        workflow_run_id=production.workflow_run_id,
        accepted_units=accepted,
    )


def build_scene_production_graph(
    executor: SceneProductionExecutor,
    dialogue_executor: DialogueSubgraphExecutor,
    *,
    checkpointer: BaseCheckpointSaver[Any] | None = None,
) -> ProductionCompiledGraph:
    """Compile the fixed writer → dialogue → critic → bounded-revision loop."""
    builder = StateGraph(ProductionGraphState)
    builder.add_node(
        ProductionNode.DRAFT.value,
        _runnable(_draft_node(executor)),
        **_node_policy(ProductionNode.DRAFT),
    )
    builder.add_node(
        ProductionNode.DIALOGUE_PASS.value,
        build_dialogue_subgraph(dialogue_executor),
    )
    builder.add_node(
        ProductionNode.DIALOGUE_INTEGRATION.value,
        _runnable(_dialogue_integration_node(executor)),
        **_node_policy(ProductionNode.DIALOGUE_INTEGRATION),
    )
    builder.add_node(
        ProductionNode.CRITIQUE.value,
        _runnable(_critique_node(executor)),
        **_node_policy(ProductionNode.CRITIQUE),
    )
    builder.add_node(
        ProductionNode.ACCEPT.value,
        _runnable(_accept_node()),
        **_node_policy(ProductionNode.ACCEPT),
    )
    builder.add_edge(START, ProductionNode.DRAFT.value)
    builder.add_conditional_edges(
        ProductionNode.DRAFT.value,
        _route_after_draft,
        {
            "dialogue": ProductionNode.DIALOGUE_PASS.value,
            "critique": ProductionNode.CRITIQUE.value,
        },
    )
    builder.add_edge(
        ProductionNode.DIALOGUE_PASS.value,
        ProductionNode.DIALOGUE_INTEGRATION.value,
    )
    builder.add_edge(
        ProductionNode.DIALOGUE_INTEGRATION.value,
        ProductionNode.CRITIQUE.value,
    )
    builder.add_conditional_edges(
        ProductionNode.CRITIQUE.value,
        _route_after_critique,
        {
            "revise": ProductionNode.DRAFT.value,
            "accept": ProductionNode.ACCEPT.value,
        },
    )
    builder.add_conditional_edges(
        ProductionNode.ACCEPT.value,
        _route_after_acceptance,
        {
            "next": ProductionNode.DRAFT.value,
            "complete": END,
        },
    )
    return builder.compile(checkpointer=checkpointer)


def _draft_node(executor: SceneProductionExecutor) -> ProductionNodeCallable:
    async def draft(state: ProductionGraphState) -> dict[str, Any]:
        production = _production_from_state(state)
        unit = _current_unit(state, production)
        revision_number = _require_integer(state, "current_revision_number")
        accepted = _accepted_artifacts(state)
        previous_draft = _optional_artifact_from_state(state.get("current_draft_artifact"))
        previous_critique = _optional_artifact_from_state(state.get("current_critique_artifact"))
        if revision_number == 0:
            previous_draft = None
            previous_critique = None
        elif previous_draft is None or previous_critique is None:
            raise SceneProductionStateError(
                "scene revision requires the previous draft and critique"
            )
        task = SceneWritingTask(
            production=production,
            unit=unit,
            accepted_units=accepted,
            revision_number=revision_number,
            previous_draft=previous_draft,
            previous_critique=previous_critique,
        )
        result = await executor.write(task)
        _validate_draft(task.unit, revision_number, result, _all_inputs(task))
        draft_state = _artifact_to_state(result.artifact)
        update: dict[str, Any] = {
            "current_draft_artifact": draft_state,
            "draft_artifacts": [*state.get("draft_artifacts", []), draft_state],
        }
        if unit.dialogue_pass is not None:
            dialogue_scene = _dialogue_scene_input(
                production,
                unit,
                result.artifact,
                accepted,
            )
            update.update(initial_dialogue_state(dialogue_scene))
        return update

    return draft


def _dialogue_integration_node(
    executor: SceneProductionExecutor,
) -> ProductionNodeCallable:
    async def integrate(state: ProductionGraphState) -> dict[str, Any]:
        production = _production_from_state(state)
        unit = _current_unit(state, production)
        if unit.dialogue_pass is None:
            raise SceneProductionStateError(
                "dialogue integration requires a configured dialogue pass"
            )
        source_draft = _required_current_artifact(
            state,
            "current_draft_artifact",
        )
        dialogue = dialogue_result_from_state(state)
        revision_number = _require_integer(state, "current_revision_number")
        task = DialogueIntegrationTask(
            production=production,
            unit=unit,
            source_draft=source_draft,
            dialogue=dialogue,
            revision_number=revision_number,
        )
        result = await executor.integrate_dialogue(task)
        dialogue_outputs = (
            dialogue.briefing_artifact,
            *dialogue.dialogue_turn_artifacts,
            *dialogue.evaluation_artifacts,
        )
        _validate_draft(
            unit,
            revision_number,
            result,
            (source_draft, *dialogue_outputs),
        )
        integrated_state = _artifact_to_state(result.artifact)
        return {
            "current_draft_artifact": integrated_state,
            "current_dialogue_runs": _require_integer(
                state,
                "current_dialogue_runs",
            )
            + 1,
            "draft_artifacts": [
                *state.get("draft_artifacts", []),
                integrated_state,
            ],
        }

    return integrate


def _critique_node(executor: SceneProductionExecutor) -> ProductionNodeCallable:
    async def critique(state: ProductionGraphState) -> dict[str, Any]:
        production = _production_from_state(state)
        unit = _current_unit(state, production)
        revision_number = _require_integer(state, "current_revision_number")
        draft = _required_current_artifact(state, "current_draft_artifact")
        task = SceneCritiqueTask(
            production=production,
            unit=unit,
            draft=draft,
            accepted_units=_accepted_artifacts(state),
            revision_number=revision_number,
        )
        result = await executor.critique(task)
        _validate_critique(task, result)
        critique_state = _artifact_to_state(result.artifact)
        update: dict[str, Any] = {
            "current_critique_artifact": critique_state,
            "current_acceptance_reason": (
                UnitAcceptanceReason.PASSED_RUBRIC.value
                if result.critique.verdict is CritiqueVerdict.PASS
                else UnitAcceptanceReason.REVISION_LIMIT_REACHED.value
            ),
            "revision_scheduled": False,
            "critique_artifacts": [
                *state.get("critique_artifacts", []),
                critique_state,
            ],
        }
        if (
            result.critique.verdict is not CritiqueVerdict.PASS
            and revision_number < production.maximum_revision_cycles
        ):
            update["current_revision_number"] = revision_number + 1
            update["current_acceptance_reason"] = None
            update["revision_scheduled"] = True
        return update

    return critique


def _accept_node() -> ProductionNodeCallable:
    async def accept(state: ProductionGraphState) -> dict[str, Any]:
        production = _production_from_state(state)
        unit_index = _require_integer(state, "current_unit_index")
        unit = _current_unit(state, production)
        draft = _required_current_artifact(state, "current_draft_artifact")
        critique = _required_current_artifact(state, "current_critique_artifact")
        revision_number = _require_integer(state, "current_revision_number")
        reason = _current_acceptance_reason(state)
        accepted: AcceptedProductionUnitState = {
            "unit_id": unit.unit_id,
            "unit_number": unit.unit_number,
            "artifact": _artifact_to_state(draft),
            "critique_artifact": _artifact_to_state(critique),
            "revision_cycles_used": revision_number,
            "dialogue_runs": _require_integer(state, "current_dialogue_runs"),
            "acceptance_reason": reason.value,
        }
        next_index = unit_index + 1
        return {
            "accepted_units": [*state.get("accepted_units", []), accepted],
            "current_unit_index": next_index,
            "current_revision_number": 0,
            "current_draft_artifact": None,
            "current_critique_artifact": None,
            "current_dialogue_runs": 0,
            "current_acceptance_reason": None,
            "revision_scheduled": False,
            "production_complete": next_index == len(production.units),
        }

    return accept


def _route_after_draft(state: ProductionGraphState) -> str:
    production = _production_from_state(state)
    unit = _current_unit(state, production)
    return "dialogue" if unit.dialogue_pass is not None else "critique"


def _route_after_critique(state: ProductionGraphState) -> str:
    return "revise" if state.get("revision_scheduled") is True else "accept"


def _route_after_acceptance(state: ProductionGraphState) -> str:
    return "complete" if state.get("production_complete") is True else "next"


def _current_acceptance_reason(
    state: ProductionGraphState,
) -> UnitAcceptanceReason:
    """Read the deterministic disposition derived by the critic node."""
    reason = state.get("current_acceptance_reason")
    if not isinstance(reason, str):
        raise SceneProductionStateError("current acceptance reason is missing")
    try:
        return UnitAcceptanceReason(reason)
    except ValueError as error:
        raise SceneProductionStateError("current acceptance reason is invalid") from error


def _dialogue_scene_input(
    production: SceneProductionInput,
    unit: ProductionUnitInput,
    draft: ArtifactReference,
    accepted: tuple[ArtifactReference, ...],
) -> DialogueSceneInput:
    configuration = unit.dialogue_pass
    if configuration is None:
        raise SceneProductionStateError("production unit has no dialogue configuration")
    return DialogueSceneInput(
        workflow_run_id=production.workflow_run_id,
        model_profile_id=production.model_profile_id,
        scene_id=unit.unit_id,
        scene_plan=unit.plan,
        characters=unit.dialogue_characters(),
        context_artifacts=_unique_references(
            (
                production.approved_blueprint,
                *production.global_context_artifacts,
                *unit.context_artifacts,
                *accepted,
                draft,
            )
        ),
        ending_options=configuration.ending_options,
        call_budget=production.call_budget,
        minimum_rounds=configuration.minimum_rounds,
        maximum_rounds=configuration.maximum_rounds,
    )


def _production_from_state(state: ProductionGraphState) -> SceneProductionInput:
    try:
        return SceneProductionInput(
            workflow_run_id=UUID(_require_text(state, "workflow_run_id")),
            model_profile_id=UUID(_require_text(state, "model_profile_id")),
            approved_blueprint=_artifact_from_state(
                _require_artifact_state(state, "approved_blueprint")
            ),
            units=tuple(_unit_from_state(unit) for unit in state.get("production_units", [])),
            global_context_artifacts=tuple(
                _artifact_from_state(reference)
                for reference in state.get("global_context_artifacts", [])
            ),
            call_budget=ModelCallBudget(
                max_input_tokens=_require_integer(
                    state,
                    "production_max_input_tokens",
                ),
                max_output_tokens=_require_integer(
                    state,
                    "production_max_output_tokens",
                ),
                max_cost_usd=Decimal(_require_text(state, "production_max_cost_usd")),
            ),
            prompt_template_version=_require_text(
                state,
                "production_prompt_template_version",
            ),
            maximum_revision_cycles=_require_integer(
                state,
                "maximum_revision_cycles",
            ),
        )
    except (ArithmeticError, KeyError, TypeError, ValueError) as error:
        raise SceneProductionStateError(
            "production checkpoint contains invalid run input"
        ) from error


def _current_unit(
    state: ProductionGraphState,
    production: SceneProductionInput,
) -> ProductionUnitInput:
    index = _require_integer(state, "current_unit_index")
    if index < 0 or index >= len(production.units):
        raise SceneProductionStateError("production checkpoint has no current unit")
    return production.units[index]


def _accepted_artifacts(
    state: ProductionGraphState,
) -> tuple[ArtifactReference, ...]:
    return tuple(_accepted_from_state(item).artifact for item in state.get("accepted_units", []))


def _validate_draft(
    unit: ProductionUnitInput,
    revision_number: int,
    result: SceneDraftResult,
    inputs: tuple[ArtifactReference, ...],
) -> None:
    _require_artifact_kind(result.artifact, ArtifactKind.SCENE_DRAFT)
    _require_new_version(result.artifact, inputs)
    draft = result.draft
    if (
        draft.scene_id != unit.unit_id
        or draft.scene_number != unit.unit_number
        or draft.revision_number != revision_number
    ):
        raise SceneProductionStateError("scene draft does not match its assigned production unit")
    if not draft.is_complete:
        raise SceneProductionStateError("incomplete scene draft cannot advance")


def _validate_critique(
    task: SceneCritiqueTask,
    result: SceneCritiqueResult,
) -> None:
    _require_artifact_kind(result.artifact, ArtifactKind.CRITIQUE)
    _require_new_version(result.artifact, (task.draft,))
    critique = result.critique
    if (
        critique.target_artifact_kind is not ArtifactKind.SCENE_DRAFT
        or critique.target_artifact_key != task.draft.artifact_key
        or critique.target_artifact_version_id != task.draft.version_id
    ):
        raise SceneProductionStateError("scene critique does not target its assigned draft version")


def _all_inputs(task: SceneWritingTask) -> tuple[ArtifactReference, ...]:
    return (
        task.production.approved_blueprint,
        task.unit.plan,
        *(character.artifact for character in task.unit.characters),
        *task.production.global_context_artifacts,
        *task.unit.context_artifacts,
        *task.accepted_units,
        *((task.previous_draft,) if task.previous_draft is not None else ()),
        *((task.previous_critique,) if task.previous_critique is not None else ()),
    )


def _unit_to_state(unit: ProductionUnitInput) -> ProductionUnitState:
    dialogue = unit.dialogue_pass
    return {
        "unit_id": unit.unit_id,
        "unit_number": unit.unit_number,
        "plan": _artifact_to_state(unit.plan),
        "characters": [
            {
                "character_id": character.character_id,
                "artifact": _artifact_to_state(character.artifact),
            }
            for character in unit.characters
        ],
        "context_artifacts": [
            _artifact_to_state(reference) for reference in unit.context_artifacts
        ],
        "dialogue_pass": (
            None
            if dialogue is None
            else {
                "character_ids": list(dialogue.character_ids),
                "ending_options": list(dialogue.ending_options),
                "minimum_rounds": dialogue.minimum_rounds,
                "maximum_rounds": dialogue.maximum_rounds,
            }
        ),
    }


def _unit_from_state(value: ProductionUnitState) -> ProductionUnitInput:
    try:
        raw_dialogue = value["dialogue_pass"]
        dialogue = (
            None
            if raw_dialogue is None
            else DialoguePassConfiguration(
                character_ids=cast(
                    tuple[str, str],
                    tuple(raw_dialogue["character_ids"]),
                ),
                ending_options=tuple(raw_dialogue["ending_options"]),
                minimum_rounds=raw_dialogue["minimum_rounds"],
                maximum_rounds=raw_dialogue["maximum_rounds"],
            )
        )
        return ProductionUnitInput(
            unit_id=value["unit_id"],
            unit_number=value["unit_number"],
            plan=_artifact_from_state(value["plan"]),
            characters=tuple(
                ProductionCharacterReference(
                    character_id=character["character_id"],
                    artifact=_artifact_from_state(character["artifact"]),
                )
                for character in value["characters"]
            ),
            context_artifacts=tuple(
                _artifact_from_state(reference) for reference in value["context_artifacts"]
            ),
            dialogue_pass=dialogue,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise SceneProductionStateError("production checkpoint has an invalid unit") from error


def _accepted_from_state(
    value: AcceptedProductionUnitState,
) -> AcceptedProductionUnit:
    try:
        return AcceptedProductionUnit(
            unit_id=value["unit_id"],
            unit_number=value["unit_number"],
            artifact=_artifact_from_state(value["artifact"]),
            critique_artifact=_artifact_from_state(value["critique_artifact"]),
            revision_cycles_used=value["revision_cycles_used"],
            dialogue_runs=value["dialogue_runs"],
            acceptance_reason=UnitAcceptanceReason(value["acceptance_reason"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise SceneProductionStateError(
            "production checkpoint has an invalid accepted unit"
        ) from error


def _artifact_to_state(
    reference: ArtifactReference,
) -> DialogueArtifactReferenceState:
    return {
        "kind": reference.kind.value,
        "artifact_key": reference.artifact_key,
        "version_id": str(reference.version_id),
        "schema_version": reference.schema_version,
    }


def _artifact_from_state(
    value: DialogueArtifactReferenceState,
) -> ArtifactReference:
    try:
        return ArtifactReference(
            kind=ArtifactKind(value["kind"]),
            artifact_key=value["artifact_key"],
            version_id=UUID(value["version_id"]),
            schema_version=value["schema_version"],
        )
    except (KeyError, TypeError, ValueError) as error:
        raise SceneProductionStateError(
            "production checkpoint has an invalid artifact reference"
        ) from error


def _optional_artifact_from_state(
    value: DialogueArtifactReferenceState | None,
) -> ArtifactReference | None:
    return None if value is None else _artifact_from_state(value)


def _required_current_artifact(
    state: ProductionGraphState,
    key: str,
) -> ArtifactReference:
    raw = state.get(key)
    if not isinstance(raw, dict):
        raise SceneProductionStateError(f"{key} is missing from production checkpoint")
    return _artifact_from_state(cast(DialogueArtifactReferenceState, raw))


def _require_artifact_state(
    state: Mapping[str, object],
    key: str,
) -> DialogueArtifactReferenceState:
    value = state.get(key)
    if not isinstance(value, dict):
        raise SceneProductionStateError(f"{key} is missing from production checkpoint")
    return cast(DialogueArtifactReferenceState, value)


def _require_text(state: Mapping[str, object], key: str) -> str:
    value = state.get(key)
    if not isinstance(value, str) or not value:
        raise SceneProductionStateError(f"{key} is missing from production checkpoint")
    return value


def _require_integer(state: Mapping[str, object], key: str) -> int:
    value = state.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise SceneProductionStateError(f"{key} is missing from production checkpoint")
    return value


def _require_artifact_kind(
    reference: ArtifactReference,
    expected: ArtifactKind,
) -> None:
    if reference.kind is not expected:
        raise SceneProductionStateError(
            f"expected {expected.value} output, received {reference.kind.value}"
        )


def _require_new_version(
    output: ArtifactReference,
    inputs: tuple[ArtifactReference, ...],
) -> None:
    if output.version_id in {reference.version_id for reference in inputs}:
        raise SceneProductionStateError(
            "production node reused an input artifact version as output"
        )


def _unique_references(
    references: tuple[ArtifactReference, ...],
) -> tuple[ArtifactReference, ...]:
    unique: dict[UUID, ArtifactReference] = {}
    for reference in references:
        unique.setdefault(reference.version_id, reference)
    return tuple(unique.values())


def _node_policy(node: ProductionNode) -> dict[str, Any]:
    definition = PRODUCTION_NODE_DEFINITIONS[node]
    return {
        "retry_policy": RetryPolicy(
            max_attempts=definition.max_attempts,
            jitter=False,
            retry_on=RetryableSceneProductionError,
        ),
        "timeout": definition.timeout_seconds,
    }


def _runnable(
    action: ProductionNodeCallable,
) -> Runnable[ProductionGraphState, Any]:
    return RunnableLambda(action)
