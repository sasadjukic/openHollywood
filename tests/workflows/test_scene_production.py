"""Tests for the bounded scene/chapter production loop."""

from __future__ import annotations

import json
from collections import Counter
from typing import cast
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

import pytest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from open_hollywood_engine.artifacts import (
    ArtifactKind,
    Critique,
    CritiqueVerdict,
    DialogueBriefing,
    DialogueEvaluation,
    DialogueTurn,
    EmotionalArcStage,
    RubricScore,
    SceneDraft,
)
from open_hollywood_engine.models import ModelCallBudget
from open_hollywood_engine.workflows import (
    ArtifactReference,
    CharacterTurnResult,
    CharacterTurnTask,
    DialogueIntegrationTask,
    DialoguePassConfiguration,
    DialogueSubgraphExecutor,
    DirectorBriefingResult,
    DirectorBriefingTask,
    DirectorEvaluationResult,
    DirectorEvaluationTask,
    ProductionCharacterReference,
    ProductionGraphState,
    ProductionUnitInput,
    RetryableSceneProductionError,
    SceneCritiqueResult,
    SceneCritiqueTask,
    SceneDraftResult,
    SceneProductionExecutor,
    SceneProductionInput,
    SceneProductionStateError,
    SceneWritingTask,
    UnitAcceptanceReason,
    build_scene_production_graph,
    initial_production_state,
    production_result_from_state,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class FakeProductionExecutor(SceneProductionExecutor):
    """Deterministic writer/critic with configurable bounded revisions."""

    def __init__(
        self,
        *,
        fail_first_write_once: bool = False,
        wrong_critique_target: bool = False,
        incomplete_draft: bool = False,
    ) -> None:
        self._fail_first_write_once = fail_first_write_once
        self._wrong_critique_target = wrong_critique_target
        self._incomplete_draft = incomplete_draft
        self._version = 0
        self.calls: list[str] = []
        self.writing_tasks: list[SceneWritingTask] = []
        self.integration_tasks: list[DialogueIntegrationTask] = []
        self.critique_tasks: list[SceneCritiqueTask] = []

    async def write(self, task: SceneWritingTask) -> SceneDraftResult:
        self.calls.append(f"write:{task.unit.unit_id}:{task.revision_number}")
        self.writing_tasks.append(task)
        if self._fail_first_write_once:
            self._fail_first_write_once = False
            raise RetryableSceneProductionError("temporary writer failure")
        return self._draft_result(
            task.unit,
            task.revision_number,
            integrated=False,
        )

    async def integrate_dialogue(
        self,
        task: DialogueIntegrationTask,
    ) -> SceneDraftResult:
        self.calls.append(f"integrate:{task.unit.unit_id}:{task.revision_number}")
        self.integration_tasks.append(task)
        return self._draft_result(
            task.unit,
            task.revision_number,
            integrated=True,
        )

    async def critique(self, task: SceneCritiqueTask) -> SceneCritiqueResult:
        self.calls.append(f"critique:{task.unit.unit_id}:{task.revision_number}")
        self.critique_tasks.append(task)
        verdict = (
            CritiqueVerdict.PASS
            if task.unit.unit_id == "scene-1"
            or (task.unit.unit_id == "scene-2" and task.revision_number == 1)
            else CritiqueVerdict.REVISE
        )
        target_key = "wrong-target" if self._wrong_critique_target else task.draft.artifact_key
        critique = Critique(
            target_artifact_kind=ArtifactKind.SCENE_DRAFT,
            target_artifact_key=target_key,
            target_artifact_version_id=task.draft.version_id,
            rubric_name="scene-production",
            rubric_version="1",
            summary=f"Critique for {task.unit.unit_id}.",
            strengths=("The scene follows its planned turn.",),
            scores=(
                RubricScore(
                    dimension="dramatic_progress",
                    score=4,
                    rationale="The scene changes the story state.",
                ),
            ),
            overall_score=4.0,
            verdict=verdict,
        )
        return SceneCritiqueResult(
            critique=critique,
            artifact=self._reference(ArtifactKind.CRITIQUE, f"{task.unit.unit_id}-critique"),
        )

    def _draft_result(
        self,
        unit: ProductionUnitInput,
        revision_number: int,
        *,
        integrated: bool,
    ) -> SceneDraftResult:
        label = "integrated" if integrated else "writer"
        prose = f"Secret prose from {label} for {unit.unit_id}, revision {revision_number}."
        return SceneDraftResult(
            draft=SceneDraft(
                scene_id=unit.unit_id,
                scene_number=unit.unit_number,
                title=f"Scene {unit.unit_number}",
                revision_number=revision_number,
                prose=prose,
                is_complete=not self._incomplete_draft,
            ),
            artifact=self._reference(ArtifactKind.SCENE_DRAFT, unit.unit_id),
        )

    def _reference(self, kind: ArtifactKind, key: str) -> ArtifactReference:
        self._version += 1
        return _reference(kind, key, 100 + self._version)


class FakeDialogueExecutor(DialogueSubgraphExecutor):
    """One-round dialogue executor used through the embedded Step 14 graph."""

    def __init__(self) -> None:
        self._version = 0
        self.calls: list[str] = []

    async def brief(self, task: DirectorBriefingTask) -> DirectorBriefingResult:
        self.calls.append(f"brief:{task.scene.scene_id}")
        return DirectorBriefingResult(
            briefing=DialogueBriefing(
                chosen_ending=task.scene.ending_options[0],
                pacing_notes="Reach the planned turn quickly.",
            ),
            artifact=self._reference(
                ArtifactKind.DIALOGUE_BRIEFING,
                f"{task.scene.scene_id}-briefing",
            ),
        )

    async def perform(self, task: CharacterTurnTask) -> CharacterTurnResult:
        self.calls.append(f"actor:{task.character.character_id}")
        return CharacterTurnResult(
            turn=DialogueTurn(
                scene_id=task.scene.scene_id,
                round_number=task.round_number,
                sequence_number=task.sequence_number,
                character_id=task.character.character_id,
                dialogue=f"Secret line from {task.character.character_id}.",
            ),
            artifact=self._reference(
                ArtifactKind.DIALOGUE_TURN,
                f"{task.scene.scene_id}-turn",
            ),
        )

    async def evaluate(
        self,
        task: DirectorEvaluationTask,
    ) -> DirectorEvaluationResult:
        self.calls.append(f"evaluate:{task.scene.scene_id}")
        return DirectorEvaluationResult(
            evaluation=DialogueEvaluation(
                round_number=task.round_number,
                emotional_arc=EmotionalArcStage.CLIMAX,
                arc_stages_hit=(
                    EmotionalArcStage.OPENING,
                    EmotionalArcStage.TENSION,
                    EmotionalArcStage.CLIMAX,
                ),
                closure_detected=True,
                ending_type=task.scene.ending_options[0],
                scene_end=True,
            ),
            artifact=self._reference(
                ArtifactKind.DIALOGUE_EVALUATION,
                f"{task.scene.scene_id}-evaluation",
            ),
        )

    def _reference(self, kind: ArtifactKind, key: str) -> ArtifactReference:
        self._version += 1
        return _reference(kind, key, 200 + self._version)


async def test_production_loop_sequences_units_dialogue_and_bounded_revision() -> None:
    executor = FakeProductionExecutor()
    dialogue = FakeDialogueExecutor()
    production = _production_input(maximum_revision_cycles=1)
    graph = build_scene_production_graph(
        executor,
        dialogue,
        checkpointer=InMemorySaver(),
    )

    final_state = cast(
        ProductionGraphState,
        await graph.ainvoke(
            initial_production_state(production),
            config=_graph_config(production),
        ),
    )
    result = production_result_from_state(final_state)

    assert [unit.unit_id for unit in result.accepted_units] == [
        "scene-1",
        "scene-2",
        "scene-3",
    ]
    assert [unit.acceptance_reason for unit in result.accepted_units] == [
        UnitAcceptanceReason.PASSED_RUBRIC,
        UnitAcceptanceReason.PASSED_RUBRIC,
        UnitAcceptanceReason.REVISION_LIMIT_REACHED,
    ]
    assert [unit.revision_cycles_used for unit in result.accepted_units] == [0, 1, 1]
    assert [unit.dialogue_runs for unit in result.accepted_units] == [0, 2, 0]
    assert dialogue.calls == [
        "brief:scene-2",
        "actor:alice",
        "actor:bob",
        "evaluate:scene-2",
        "brief:scene-2",
        "actor:alice",
        "actor:bob",
        "evaluate:scene-2",
    ]
    assert executor.writing_tasks[1].accepted_units == (result.accepted_units[0].artifact,)
    assert executor.writing_tasks[-1].previous_critique is not None

    checkpoint_json = json.dumps(final_state, sort_keys=True)
    assert "Secret prose" not in checkpoint_json
    assert "Secret line" not in checkpoint_json
    assert "Critique for scene" not in checkpoint_json


async def test_retryable_writer_failure_retries_only_writer_node() -> None:
    executor = FakeProductionExecutor(fail_first_write_once=True)
    dialogue = FakeDialogueExecutor()
    production = _passing_production_input()
    graph = build_scene_production_graph(executor, dialogue)

    final_state = cast(
        ProductionGraphState,
        await graph.ainvoke(
            initial_production_state(production),
            config=_graph_config(production),
        ),
    )

    assert len(production_result_from_state(final_state).accepted_units) == 3
    counts = Counter(executor.calls)
    assert counts["write:scene-1:0"] == 2
    assert counts["critique:scene-1:0"] == 1


async def test_critique_must_target_exact_draft_version() -> None:
    executor = FakeProductionExecutor(wrong_critique_target=True)
    production = _passing_production_input()
    graph = build_scene_production_graph(executor, FakeDialogueExecutor())

    with pytest.raises(
        SceneProductionStateError,
        match="does not target its assigned draft",
    ):
        await graph.ainvoke(
            initial_production_state(production),
            config=_graph_config(production),
        )


async def test_incomplete_scene_cannot_advance_to_critique() -> None:
    executor = FakeProductionExecutor(incomplete_draft=True)
    production = _passing_production_input()
    graph = build_scene_production_graph(executor, FakeDialogueExecutor())

    with pytest.raises(
        SceneProductionStateError,
        match="incomplete scene draft cannot advance",
    ):
        await graph.ainvoke(
            initial_production_state(production),
            config=_graph_config(production),
        )

    assert not executor.critique_tasks


def test_production_input_rejects_noncontiguous_units() -> None:
    units = list(_units(dialogue=False))
    units[1] = ProductionUnitInput(
        unit_id=units[1].unit_id,
        unit_number=3,
        plan=units[1].plan,
        characters=units[1].characters,
    )

    with pytest.raises(ValueError, match="ordered and contiguous"):
        _production_input(units=tuple(units))


def _production_input(
    *,
    maximum_revision_cycles: int = 1,
    units: tuple[ProductionUnitInput, ...] | None = None,
) -> SceneProductionInput:
    return SceneProductionInput(
        workflow_run_id=uuid4(),
        model_profile_id=uuid4(),
        approved_blueprint=_reference(
            ArtifactKind.STORY_BLUEPRINT,
            "approved-blueprint",
            1,
        ),
        units=units or _units(dialogue=True),
        global_context_artifacts=(_reference(ArtifactKind.WORLD_RULE, "world-rule", 2),),
        call_budget=ModelCallBudget(
            max_input_tokens=8_000,
            max_output_tokens=2_000,
        ),
        maximum_revision_cycles=maximum_revision_cycles,
    )


def _passing_production_input() -> SceneProductionInput:
    production = _production_input(
        maximum_revision_cycles=0,
        units=_units(dialogue=False),
    )
    return production


def _units(*, dialogue: bool) -> tuple[ProductionUnitInput, ...]:
    alice = ProductionCharacterReference(
        character_id="alice",
        artifact=_reference(ArtifactKind.CHARACTER, "alice", 10),
    )
    bob = ProductionCharacterReference(
        character_id="bob",
        artifact=_reference(ArtifactKind.CHARACTER, "bob", 11),
    )
    return tuple(
        ProductionUnitInput(
            unit_id=f"scene-{number}",
            unit_number=number,
            plan=_reference(
                ArtifactKind.SCENE_PLAN,
                f"scene-{number}-plan",
                20 + number,
            ),
            characters=(alice, bob),
            dialogue_pass=(
                DialoguePassConfiguration(
                    character_ids=("alice", "bob"),
                    ending_options=("REVELATION", "WITHDRAWAL"),
                    minimum_rounds=1,
                    maximum_rounds=1,
                )
                if dialogue and number == 2
                else None
            ),
        )
        for number in range(1, 4)
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


def _graph_config(production: SceneProductionInput) -> RunnableConfig:
    return {
        "configurable": {
            "thread_id": str(UUID(int=production.workflow_run_id.int)),
        },
        "recursion_limit": production.max_graph_steps + 2,
    }
