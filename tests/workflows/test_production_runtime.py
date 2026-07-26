"""Application-level budget controls for durable scene production."""

from __future__ import annotations

from decimal import Decimal

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    InvocationStatus,
    Project,
    RunStatus,
    WorkflowRun,
)
from open_hollywood_api.services.production_workflow import (
    SqlAlchemySceneProductionObserver,
)
from open_hollywood_api.services.run_controls import (
    RunControlStore,
    WorkflowPausedSignal,
)
from open_hollywood_engine.workflows import (
    ProductionNode,
    RunBudget,
    RunPauseReason,
)
from sqlalchemy import Engine


@pytest.mark.anyio
async def test_production_reserves_budget_before_the_next_model_call(
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)
    budget = RunBudget(
        max_graph_steps=20,
        max_model_calls=1,
        max_input_tokens=20_000,
        max_output_tokens=8_000,
        max_cost_usd=Decimal("1"),
        per_call_input_tokens=10_000,
        per_call_output_tokens=4_000,
        per_call_cost_usd=Decimal("0.25"),
    )
    with session_factory.begin() as session:
        project = Project(name="Budgeted production")
        run = WorkflowRun(
            project=project,
            workflow_name="scene_production",
            graph_version="1",
            status=RunStatus.RUNNING,
            budget=budget.to_data(),
        )
        session.add_all((project, run))
        session.flush()
        session.add(
            AgentInvocation(
                workflow_run=run,
                specialist_role="scene_writer",
                provider="fixture",
                model_identifier="fixture-model",
                status=InvocationStatus.SUCCEEDED,
                request_settings={},
                prompt_sha256="0" * 64,
            )
        )
        run_id = run.id
    observer = SqlAlchemySceneProductionObserver(
        session_factory,
        RunControlStore(session_factory),
    )

    with pytest.raises(
        WorkflowPausedSignal,
        match="budget",
    ):
        await observer.node_started(run_id, ProductionNode.CRITIQUE)

    with session_factory() as session:
        persisted = session.get(WorkflowRun, run_id)
        assert persisted is not None
        assert persisted.status is RunStatus.PAUSED
        assert persisted.pause_reason is RunPauseReason.BUDGET
        assert persisted.current_node == ProductionNode.CRITIQUE.value
