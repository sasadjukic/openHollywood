"""Provider-neutral run-budget and retry-state tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import NAMESPACE_URL, uuid4, uuid5

import pytest
from open_hollywood_api.persistence.models import RunStatus, WorkflowRun
from open_hollywood_api.services.run_controls import (
    abandon_active_interval,
    finish_active_interval,
    run_usage,
    start_active_interval,
)
from open_hollywood_engine.artifacts import ArtifactKind
from open_hollywood_engine.workflows import (
    ArtifactReference,
    BlueprintNode,
    BudgetLimit,
    RunBudget,
    RunControlAction,
    RunControlCommand,
    RunUsage,
    initial_blueprint_retry_state,
    projected_budget_limits,
    retry_artifacts_for_node,
)


def test_legacy_budget_upgrades_to_canonical_hard_limits() -> None:
    budget = RunBudget.from_data({"max_graph_steps": 12})

    assert budget.max_graph_steps == 12
    assert budget.max_model_calls == 32
    assert budget.max_cost_usd == Decimal("2.00")
    assert RunBudget.from_data(budget.to_data()) == budget


def test_next_model_call_is_reserved_before_budget_is_spent() -> None:
    budget = RunBudget(
        max_model_calls=2,
        max_input_tokens=10_000,
        max_output_tokens=3_000,
        max_cost_usd=Decimal("0.50"),
        per_call_input_tokens=4_000,
        per_call_output_tokens=2_000,
        per_call_cost_usd=Decimal("0.25"),
    )
    usage = RunUsage(
        model_calls=1,
        input_tokens=7_000,
        output_tokens=1_500,
        cost_usd=Decimal("0.30"),
    )

    assert projected_budget_limits(
        budget,
        usage,
        includes_model_call=True,
    ) == (
        BudgetLimit.INPUT_TOKENS,
        BudgetLimit.OUTPUT_TOKENS,
        BudgetLimit.COST,
    )
    assert (
        projected_budget_limits(
            budget,
            usage,
            includes_model_call=False,
        )
        == ()
    )


def test_run_control_commands_reject_action_specific_extra_data() -> None:
    with pytest.raises(ValueError, match="requires target_node"):
        RunControlCommand(id=uuid4(), action=RunControlAction.RETRY_FROM_NODE)
    with pytest.raises(ValueError, match="only valid"):
        RunControlCommand(
            id=uuid4(),
            action=RunControlAction.PAUSE,
            target_node="brief",
        )
    with pytest.raises(ValueError, match="requires at least one"):
        RunControlCommand(
            id=uuid4(),
            action=RunControlAction.UPDATE_BUDGET,
            budget_updates={},
        )


def test_active_runtime_excludes_pauses_and_replaces_interrupted_interval() -> None:
    started = datetime(2026, 8, 10, 10, 0, tzinfo=UTC)
    run = WorkflowRun(
        project_id=uuid4(),
        workflow_name="fixture",
        graph_version="1",
        status=RunStatus.RUNNING,
        input_state={},
        budget={},
        active_elapsed_seconds=7,
    )

    start_active_interval(run, now=started)
    abandon_active_interval(run)
    start_active_interval(run, now=started + timedelta(minutes=30))
    finish_active_interval(run, now=started + timedelta(minutes=30, seconds=5))
    run.status = RunStatus.PAUSED

    assert run_usage(run).wall_clock_seconds == 12
    assert run.active_started_at is None


def test_retry_state_keeps_only_exact_prerequisites_and_independent_sibling() -> None:
    artifacts = tuple(
        _reference(kind, index)
        for index, kind in enumerate(
            (
                ArtifactKind.CREATIVE_BRIEF,
                ArtifactKind.PREMISE,
                ArtifactKind.LOCATION,
                ArtifactKind.WORLD_RULE,
                ArtifactKind.CHARACTER,
                ArtifactKind.RELATIONSHIP,
                ArtifactKind.STORY_BLUEPRINT,
                ArtifactKind.CRITIQUE,
            ),
            start=1,
        )
    )

    retained = retry_artifacts_for_node(
        artifacts,
        BlueprintNode.WORLD_SPECIALIST,
    )
    state = initial_blueprint_retry_state(
        uuid4(),
        artifacts,
        BlueprintNode.WORLD_SPECIALIST,
        uuid4(),
    )

    assert {artifact.kind for artifact in retained} == {
        ArtifactKind.CREATIVE_BRIEF,
        ArtifactKind.PREMISE,
        ArtifactKind.CHARACTER,
        ArtifactKind.RELATIONSHIP,
    }
    assert state["entry_mode"] == "retry"
    assert state["retry_node"] == BlueprintNode.WORLD_SPECIALIST.value
    assert state["run_control_id"]


def _reference(kind: ArtifactKind, index: int) -> ArtifactReference:
    return ArtifactReference(
        kind=kind,
        artifact_key=f"{kind.value}_{index}",
        version_id=uuid5(NAMESPACE_URL, f"{kind.value}:{index}"),
        schema_version="1",
    )
