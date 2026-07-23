"""Regression tests for the isolated legacy character-dialogue experiment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

import pytest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from open_hollywood_engine.artifacts import (
    ArtifactKind,
    DialogueBriefing,
    DialogueEvaluation,
    DialogueTurn,
    EmotionalArcStage,
)
from open_hollywood_engine.models import ModelCallBudget
from open_hollywood_engine.workflows import (
    ArtifactReference,
    CharacterTurnResult,
    CharacterTurnTask,
    DialogueCharacterReference,
    DialogueCompletionReason,
    DialogueGraphState,
    DialogueSceneInput,
    DialogueStateError,
    DialogueSubgraphExecutor,
    DirectorBriefingResult,
    DirectorBriefingTask,
    DirectorEvaluationResult,
    DirectorEvaluationTask,
    RetryableDialogueError,
    build_dialogue_subgraph,
    dialogue_result_from_state,
    initial_dialogue_state,
)

pytestmark = pytest.mark.anyio
FIXTURE_PATH = Path("tests/fixtures/legacy/director_flow.json")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FixtureDialogueExecutor(DialogueSubgraphExecutor):
    """Deterministic executor preserving the legacy orchestration contract."""

    def __init__(
        self,
        *,
        ending_round: int | None = None,
        fail_first_actor_once: bool = False,
        invalid_turn_kind: bool = False,
    ) -> None:
        self._fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self._ending_round = ending_round
        self._fail_first_actor_once = fail_first_actor_once
        self._invalid_turn_kind = invalid_turn_kind
        self.calls: list[str] = []
        self.tasks: list[object] = []

    async def brief(self, task: DirectorBriefingTask) -> DirectorBriefingResult:
        self.calls.append("briefing")
        self.tasks.append(task)
        fixture = self._fixture["briefing_result"]
        return DirectorBriefingResult(
            briefing=DialogueBriefing.model_validate(fixture),
            artifact=_reference(ArtifactKind.DIALOGUE_BRIEFING, "briefing", 1),
        )

    async def perform(self, task: CharacterTurnTask) -> CharacterTurnResult:
        self.calls.append(task.character.character_id)
        self.tasks.append(task)
        if self._fail_first_actor_once:
            self._fail_first_actor_once = False
            raise RetryableDialogueError("temporary actor failure")
        kind = ArtifactKind.CHARACTER if self._invalid_turn_kind else ArtifactKind.DIALOGUE_TURN
        return CharacterTurnResult(
            turn=DialogueTurn(
                scene_id=task.scene.scene_id,
                round_number=task.round_number,
                sequence_number=task.sequence_number,
                character_id=task.character.character_id,
                dialogue=f"Line {task.sequence_number} from {task.character.character_id}.",
            ),
            artifact=_reference(
                kind,
                f"turn-{task.sequence_number}",
                task.sequence_number,
            ),
        )

    async def evaluate(
        self,
        task: DirectorEvaluationTask,
    ) -> DirectorEvaluationResult:
        self.calls.append("director")
        self.tasks.append(task)
        fixture = dict(self._fixture["director_result"])
        fixture["round_number"] = task.round_number
        fixture.pop("turn_count")
        if self._ending_round == task.round_number:
            fixture.update(
                {
                    "arc_stages_hit": ["opening", "tension", "climax"],
                    "closure_detected": True,
                    "emotional_arc": "climax",
                    "ending_type": "ABSOLUTION",
                    "scene_end": True,
                }
            )
        return DirectorEvaluationResult(
            evaluation=DialogueEvaluation.model_validate(fixture),
            artifact=_reference(
                ArtifactKind.DIALOGUE_EVALUATION,
                f"evaluation-{task.round_number}",
                task.round_number,
            ),
        )


async def test_legacy_director_flow_preserves_seven_call_contract() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    executor = FixtureDialogueExecutor()
    scene = _scene_input(minimum_rounds=1, maximum_rounds=2)
    graph = build_dialogue_subgraph(executor, checkpointer=InMemorySaver())

    final_state = cast(
        DialogueGraphState,
        await graph.ainvoke(
            initial_dialogue_state(scene),
            config=_graph_config(scene),
        ),
    )
    result = dialogue_result_from_state(final_state)

    assert executor.calls == [
        "briefing",
        "priest",
        "sinner",
        "director",
        "priest",
        "sinner",
        "director",
    ]
    assert len(executor.calls) == fixture["contract"]["expected_total_model_calls"]
    assert len(result.dialogue_turn_artifacts) == fixture["contract"]["expected_dialogue_callbacks"]
    assert len(result.evaluation_artifacts) == 2
    assert result.rounds_completed == fixture["contract"]["rounds_in_legacy_test"]
    assert result.completion_reason is DialogueCompletionReason.MAXIMUM_ROUNDS

    checkpoint_json = json.dumps(final_state, sort_keys=True)
    assert fixture["briefing_result"]["pacing_notes"] not in checkpoint_json
    assert "Line 1 from priest." not in checkpoint_json


async def test_director_cannot_end_before_minimum_rounds() -> None:
    executor = FixtureDialogueExecutor(ending_round=1)
    scene = _scene_input(minimum_rounds=2, maximum_rounds=4)
    graph = build_dialogue_subgraph(executor)

    final_state = cast(
        DialogueGraphState,
        await graph.ainvoke(
            initial_dialogue_state(scene),
            config=_graph_config(scene),
        ),
    )
    result = dialogue_result_from_state(final_state)

    assert result.rounds_completed == 4
    assert result.completion_reason is DialogueCompletionReason.MAXIMUM_ROUNDS


async def test_director_ends_after_closure_at_or_after_minimum_rounds() -> None:
    executor = FixtureDialogueExecutor(ending_round=2)
    scene = _scene_input(minimum_rounds=2, maximum_rounds=4)
    graph = build_dialogue_subgraph(executor)

    final_state = cast(
        DialogueGraphState,
        await graph.ainvoke(
            initial_dialogue_state(scene),
            config=_graph_config(scene),
        ),
    )
    result = dialogue_result_from_state(final_state)

    assert result.rounds_completed == 2
    assert result.completion_reason is DialogueCompletionReason.DIRECTOR_ENDED
    assert len(result.dialogue_turn_artifacts) == 4


async def test_retryable_actor_failure_retries_only_its_registered_node() -> None:
    executor = FixtureDialogueExecutor(
        ending_round=1,
        fail_first_actor_once=True,
    )
    scene = _scene_input(minimum_rounds=1, maximum_rounds=1)
    graph = build_dialogue_subgraph(executor)

    final_state = cast(
        DialogueGraphState,
        await graph.ainvoke(
            initial_dialogue_state(scene),
            config=_graph_config(scene),
        ),
    )

    assert dialogue_result_from_state(final_state).rounds_completed == 1
    assert executor.calls == [
        "briefing",
        "priest",
        "priest",
        "sinner",
        "director",
    ]


async def test_executor_output_kind_is_validated_at_subgraph_boundary() -> None:
    executor = FixtureDialogueExecutor(invalid_turn_kind=True)
    scene = _scene_input(minimum_rounds=1, maximum_rounds=1)
    graph = build_dialogue_subgraph(executor)

    with pytest.raises(
        DialogueStateError,
        match="expected dialogue_turn output",
    ):
        await graph.ainvoke(
            initial_dialogue_state(scene),
            config=_graph_config(scene),
        )


def test_dialogue_artifacts_reject_invalid_director_termination() -> None:
    with pytest.raises(
        ValueError,
        match="scene_end requires closure",
    ):
        DialogueEvaluation(
            round_number=1,
            emotional_arc=EmotionalArcStage.TENSION,
            arc_stages_hit=(EmotionalArcStage.OPENING,),
            closure_detected=False,
            ending_type="ABSOLUTION",
            scene_end=True,
        )


def _scene_input(
    *,
    minimum_rounds: int,
    maximum_rounds: int,
) -> DialogueSceneInput:
    return DialogueSceneInput(
        workflow_run_id=uuid4(),
        model_profile_id=uuid4(),
        scene_id="confession",
        scene_plan=_reference(ArtifactKind.SCENE_PLAN, "scene-plan", 1),
        characters=(
            DialogueCharacterReference(
                character_id="priest",
                artifact=_reference(ArtifactKind.CHARACTER, "priest", 1),
            ),
            DialogueCharacterReference(
                character_id="sinner",
                artifact=_reference(ArtifactKind.CHARACTER, "sinner", 2),
            ),
        ),
        context_artifacts=(_reference(ArtifactKind.RELATIONSHIP, "relationship", 1),),
        ending_options=(
            "ABSOLUTION",
            "REFUSAL",
            "FAITH_CRISIS",
            "UNEXPECTED_BOND",
            "DEFLECTION",
        ),
        call_budget=ModelCallBudget(
            max_input_tokens=8_000,
            max_output_tokens=1_000,
        ),
        minimum_rounds=minimum_rounds,
        maximum_rounds=maximum_rounds,
    )


def _reference(
    kind: ArtifactKind,
    artifact_key: str,
    index: int,
) -> ArtifactReference:
    return ArtifactReference(
        kind=kind,
        artifact_key=artifact_key,
        version_id=uuid5(NAMESPACE_URL, f"{kind.value}:{artifact_key}:{index}"),
        schema_version="1",
    )


def _graph_config(scene: DialogueSceneInput) -> RunnableConfig:
    return {
        "configurable": {"thread_id": str(UUID(int=scene.workflow_run_id.int))},
        "recursion_limit": scene.max_graph_steps + 2,
    }
