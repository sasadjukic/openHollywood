"""LangGraph adapter for the isolated two-character dialogue experiment."""

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

from open_hollywood_engine.artifacts import ArtifactKind, EmotionalArcStage
from open_hollywood_engine.models.contracts import ModelCallBudget
from open_hollywood_engine.workflows.contracts import ArtifactReference
from open_hollywood_engine.workflows.dialogue_contracts import (
    DIALOGUE_NODE_DEFINITIONS,
    CharacterTurnResult,
    CharacterTurnTask,
    DialogueCharacterReference,
    DialogueCompletionReason,
    DialogueNode,
    DialogueSceneInput,
    DialogueSceneResult,
    DialogueStateError,
    DialogueSubgraphExecutor,
    DirectorBriefingResult,
    DirectorBriefingTask,
    DirectorEvaluationResult,
    DirectorEvaluationTask,
    RetryableDialogueError,
)


class DialogueArtifactReferenceState(TypedDict):
    """JSON-safe checkpoint representation of an immutable artifact version."""

    kind: str
    artifact_key: str
    version_id: str
    schema_version: str


class DialogueCharacterState(TypedDict):
    """Checkpoint-safe actor identity and dossier reference."""

    character_id: str
    artifact: DialogueArtifactReferenceState


class DialogueGraphState(TypedDict, total=False):
    """Coordination-only state for the bounded dialogue subgraph."""

    workflow_run_id: str
    model_profile_id: str
    scene_id: str
    scene_plan: DialogueArtifactReferenceState
    characters: list[DialogueCharacterState]
    context_artifacts: list[DialogueArtifactReferenceState]
    ending_options: list[str]
    max_input_tokens: int
    max_output_tokens: int
    max_cost_usd: str
    prompt_template_version: str
    minimum_rounds: int
    maximum_rounds: int
    current_round: int
    briefing_artifact: DialogueArtifactReferenceState
    dialogue_turn_artifacts: list[DialogueArtifactReferenceState]
    evaluation_artifacts: list[DialogueArtifactReferenceState]
    completion_reason: str


type DialogueCompiledGraph = CompiledStateGraph[
    DialogueGraphState,
    None,
    DialogueGraphState,
    DialogueGraphState,
]
type DialogueNodeCallable = Callable[
    [DialogueGraphState],
    Awaitable[dict[str, Any]],
]


def initial_dialogue_state(scene: DialogueSceneInput) -> DialogueGraphState:
    """Create JSON-safe input for one new dialogue checkpoint thread."""
    return {
        "workflow_run_id": str(scene.workflow_run_id),
        "model_profile_id": str(scene.model_profile_id),
        "scene_id": scene.scene_id,
        "scene_plan": _artifact_to_state(scene.scene_plan),
        "characters": [
            {
                "character_id": character.character_id,
                "artifact": _artifact_to_state(character.artifact),
            }
            for character in scene.characters
        ],
        "context_artifacts": [
            _artifact_to_state(reference) for reference in scene.context_artifacts
        ],
        "ending_options": list(scene.ending_options),
        "max_input_tokens": scene.call_budget.max_input_tokens,
        "max_output_tokens": scene.call_budget.max_output_tokens,
        "max_cost_usd": str(scene.call_budget.max_cost_usd),
        "prompt_template_version": scene.prompt_template_version,
        "minimum_rounds": scene.minimum_rounds,
        "maximum_rounds": scene.maximum_rounds,
        "current_round": 1,
        "dialogue_turn_artifacts": [],
        "evaluation_artifacts": [],
    }


def dialogue_result_from_state(state: DialogueGraphState) -> DialogueSceneResult:
    """Rehydrate the typed, reference-only result of a completed subgraph."""
    completion = state.get("completion_reason")
    briefing = state.get("briefing_artifact")
    if completion is None or briefing is None:
        raise DialogueStateError("dialogue checkpoint is not complete")
    try:
        reason = DialogueCompletionReason(completion)
    except ValueError as error:
        raise DialogueStateError("dialogue checkpoint has an invalid completion reason") from error
    evaluations = tuple(
        _artifact_from_state(reference) for reference in state.get("evaluation_artifacts", [])
    )
    return DialogueSceneResult(
        scene_id=_require_text(state, "scene_id"),
        briefing_artifact=_artifact_from_state(briefing),
        dialogue_turn_artifacts=tuple(
            _artifact_from_state(reference)
            for reference in state.get("dialogue_turn_artifacts", [])
        ),
        evaluation_artifacts=evaluations,
        rounds_completed=len(evaluations),
        completion_reason=reason,
    )


def build_dialogue_subgraph(
    executor: DialogueSubgraphExecutor,
    *,
    checkpointer: BaseCheckpointSaver[Any] | None = None,
) -> DialogueCompiledGraph:
    """Compile the fixed briefing → actor one → actor two → director loop."""
    builder = StateGraph(DialogueGraphState)
    builder.add_node(
        DialogueNode.DIRECTOR_BRIEFING.value,
        _runnable(_briefing_node(executor)),
        **_node_policy(DialogueNode.DIRECTOR_BRIEFING),
    )
    builder.add_node(
        DialogueNode.CHARACTER_ONE.value,
        _runnable(_character_node(executor, character_index=0)),
        **_node_policy(DialogueNode.CHARACTER_ONE),
    )
    builder.add_node(
        DialogueNode.CHARACTER_TWO.value,
        _runnable(_character_node(executor, character_index=1)),
        **_node_policy(DialogueNode.CHARACTER_TWO),
    )
    builder.add_node(
        DialogueNode.DIRECTOR_EVALUATION.value,
        _runnable(_director_node(executor)),
        **_node_policy(DialogueNode.DIRECTOR_EVALUATION),
    )
    builder.add_edge(START, DialogueNode.DIRECTOR_BRIEFING.value)
    builder.add_edge(
        DialogueNode.DIRECTOR_BRIEFING.value,
        DialogueNode.CHARACTER_ONE.value,
    )
    builder.add_edge(
        DialogueNode.CHARACTER_ONE.value,
        DialogueNode.CHARACTER_TWO.value,
    )
    builder.add_edge(
        DialogueNode.CHARACTER_TWO.value,
        DialogueNode.DIRECTOR_EVALUATION.value,
    )
    builder.add_conditional_edges(
        DialogueNode.DIRECTOR_EVALUATION.value,
        _route_after_director,
        {
            "continue": DialogueNode.CHARACTER_ONE.value,
            "complete": END,
        },
    )
    return builder.compile(checkpointer=checkpointer)


def _briefing_node(
    executor: DialogueSubgraphExecutor,
) -> DialogueNodeCallable:
    async def brief(state: DialogueGraphState) -> dict[str, Any]:
        scene = _scene_from_state(state)
        result = await executor.brief(DirectorBriefingTask(scene=scene))
        _validate_briefing(scene, result)
        return {"briefing_artifact": _artifact_to_state(result.artifact)}

    return brief


def _character_node(
    executor: DialogueSubgraphExecutor,
    *,
    character_index: int,
) -> DialogueNodeCallable:
    async def perform(state: DialogueGraphState) -> dict[str, Any]:
        scene = _scene_from_state(state)
        briefing = _briefing_reference(state)
        history = tuple(
            _artifact_from_state(reference)
            for reference in state.get("dialogue_turn_artifacts", [])
        )
        evaluations = tuple(
            _artifact_from_state(reference) for reference in state.get("evaluation_artifacts", [])
        )
        round_number = _require_integer(state, "current_round")
        expected_history_count = (round_number - 1) * 2 + character_index
        if len(history) != expected_history_count or len(evaluations) != round_number - 1:
            raise DialogueStateError("dialogue checkpoint has an invalid actor sequence")
        task = CharacterTurnTask(
            scene=scene,
            character=scene.characters[character_index],
            round_number=round_number,
            sequence_number=len(history) + 1,
            briefing_artifact=briefing,
            dialogue_history=history,
            previous_evaluation=evaluations[-1] if evaluations else None,
        )
        result = await executor.perform(task)
        _validate_turn(task, result)
        return {
            "dialogue_turn_artifacts": [
                *state.get("dialogue_turn_artifacts", []),
                _artifact_to_state(result.artifact),
            ]
        }

    return perform


def _director_node(
    executor: DialogueSubgraphExecutor,
) -> DialogueNodeCallable:
    async def evaluate(state: DialogueGraphState) -> dict[str, Any]:
        scene = _scene_from_state(state)
        history = tuple(
            _artifact_from_state(reference)
            for reference in state.get("dialogue_turn_artifacts", [])
        )
        evaluations = tuple(
            _artifact_from_state(reference) for reference in state.get("evaluation_artifacts", [])
        )
        round_number = _require_integer(state, "current_round")
        if len(history) != round_number * 2 or len(evaluations) != round_number - 1:
            raise DialogueStateError("dialogue checkpoint has an incomplete round")
        task = DirectorEvaluationTask(
            scene=scene,
            round_number=round_number,
            briefing_artifact=_briefing_reference(state),
            dialogue_history=history,
            previous_evaluation=evaluations[-1] if evaluations else None,
        )
        result = await executor.evaluate(task)
        _validate_evaluation(task, result)
        evaluation_states = [
            *state.get("evaluation_artifacts", []),
            _artifact_to_state(result.artifact),
        ]
        update: dict[str, Any] = {"evaluation_artifacts": evaluation_states}
        if (
            round_number >= scene.minimum_rounds
            and result.evaluation.scene_end
            and result.evaluation.closure_detected
            and result.evaluation.emotional_arc
            in {EmotionalArcStage.CLIMAX, EmotionalArcStage.RESOLUTION}
        ):
            update["completion_reason"] = DialogueCompletionReason.DIRECTOR_ENDED.value
        elif round_number >= scene.maximum_rounds:
            update["completion_reason"] = DialogueCompletionReason.MAXIMUM_ROUNDS.value
        else:
            update["current_round"] = round_number + 1
        return update

    return evaluate


def _validate_briefing(
    scene: DialogueSceneInput,
    result: DirectorBriefingResult,
) -> None:
    _require_artifact_kind(result.artifact, ArtifactKind.DIALOGUE_BRIEFING)
    _require_new_version(
        result.artifact,
        (
            scene.scene_plan,
            *(character.artifact for character in scene.characters),
            *scene.context_artifacts,
        ),
    )
    if result.briefing.chosen_ending not in scene.ending_options:
        raise DialogueStateError("director selected an undeclared ending")


def _validate_turn(
    task: CharacterTurnTask,
    result: CharacterTurnResult,
) -> None:
    _require_artifact_kind(result.artifact, ArtifactKind.DIALOGUE_TURN)
    _require_new_version(
        result.artifact,
        (
            task.briefing_artifact,
            *task.dialogue_history,
            *((task.previous_evaluation,) if task.previous_evaluation is not None else ()),
        ),
    )
    turn = result.turn
    if (
        turn.scene_id != task.scene.scene_id
        or turn.character_id != task.character.character_id
        or turn.round_number != task.round_number
        or turn.sequence_number != task.sequence_number
    ):
        raise DialogueStateError("character output does not match its assigned turn")


def _validate_evaluation(
    task: DirectorEvaluationTask,
    result: DirectorEvaluationResult,
) -> None:
    _require_artifact_kind(result.artifact, ArtifactKind.DIALOGUE_EVALUATION)
    _require_new_version(
        result.artifact,
        (
            task.briefing_artifact,
            *task.dialogue_history,
            *((task.previous_evaluation,) if task.previous_evaluation is not None else ()),
        ),
    )
    evaluation = result.evaluation
    if evaluation.round_number != task.round_number:
        raise DialogueStateError("director output does not match its assigned round")
    if (
        evaluation.ending_type is not None
        and evaluation.ending_type not in task.scene.ending_options
    ):
        raise DialogueStateError("director reported an undeclared ending")
    if evaluation.scene_end and evaluation.ending_type is None:
        raise DialogueStateError("director must name the ending when ending the scene")


def _require_artifact_kind(
    reference: ArtifactReference,
    expected: ArtifactKind,
) -> None:
    if reference.kind is not expected:
        raise DialogueStateError(
            f"expected {expected.value} output, received {reference.kind.value}"
        )


def _require_new_version(
    output: ArtifactReference,
    inputs: tuple[ArtifactReference, ...],
) -> None:
    if output.version_id in {reference.version_id for reference in inputs}:
        raise DialogueStateError("dialogue node reused an input artifact version as output")


def _route_after_director(state: DialogueGraphState) -> str:
    return "complete" if state.get("completion_reason") is not None else "continue"


def _scene_from_state(state: DialogueGraphState) -> DialogueSceneInput:
    raw_characters = state.get("characters")
    if raw_characters is None or len(raw_characters) != 2:
        raise DialogueStateError("dialogue checkpoint requires exactly two characters")
    try:
        return DialogueSceneInput(
            workflow_run_id=UUID(_require_text(state, "workflow_run_id")),
            model_profile_id=UUID(_require_text(state, "model_profile_id")),
            scene_id=_require_text(state, "scene_id"),
            scene_plan=_artifact_from_state(_require_artifact_state(state, "scene_plan")),
            characters=(
                _character_from_state(raw_characters[0]),
                _character_from_state(raw_characters[1]),
            ),
            context_artifacts=tuple(
                _artifact_from_state(reference) for reference in state.get("context_artifacts", [])
            ),
            ending_options=tuple(state.get("ending_options", [])),
            call_budget=ModelCallBudget(
                max_input_tokens=_require_integer(state, "max_input_tokens"),
                max_output_tokens=_require_integer(state, "max_output_tokens"),
                max_cost_usd=Decimal(_require_text(state, "max_cost_usd")),
            ),
            prompt_template_version=_require_text(
                state,
                "prompt_template_version",
            ),
            minimum_rounds=_require_integer(state, "minimum_rounds"),
            maximum_rounds=_require_integer(state, "maximum_rounds"),
        )
    except (ArithmeticError, KeyError, TypeError, ValueError) as error:
        raise DialogueStateError("dialogue checkpoint contains invalid scene input") from error


def _briefing_reference(state: DialogueGraphState) -> ArtifactReference:
    return _artifact_from_state(_require_artifact_state(state, "briefing_artifact"))


def _character_from_state(
    value: DialogueCharacterState,
) -> DialogueCharacterReference:
    try:
        return DialogueCharacterReference(
            character_id=value["character_id"],
            artifact=_artifact_from_state(value["artifact"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise DialogueStateError("dialogue checkpoint has an invalid character") from error


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
        raise DialogueStateError("dialogue checkpoint has an invalid artifact reference") from error


def _require_artifact_state(
    state: Mapping[str, object],
    key: str,
) -> DialogueArtifactReferenceState:
    value = state.get(key)
    if not isinstance(value, dict):
        raise DialogueStateError(f"{key} is missing from dialogue checkpoint")
    return cast(DialogueArtifactReferenceState, value)


def _require_text(state: Mapping[str, object], key: str) -> str:
    value = state.get(key)
    if not isinstance(value, str) or not value:
        raise DialogueStateError(f"{key} is missing from dialogue checkpoint")
    return value


def _require_integer(state: Mapping[str, object], key: str) -> int:
    value = state.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise DialogueStateError(f"{key} is missing from dialogue checkpoint")
    return value


def _node_policy(node: DialogueNode) -> dict[str, Any]:
    definition = DIALOGUE_NODE_DEFINITIONS[node]
    return {
        "retry_policy": RetryPolicy(
            max_attempts=definition.max_attempts,
            jitter=False,
            retry_on=RetryableDialogueError,
        ),
        "timeout": definition.timeout_seconds,
    }


def _runnable(action: DialogueNodeCallable) -> Runnable[DialogueGraphState, Any]:
    return RunnableLambda(action)
