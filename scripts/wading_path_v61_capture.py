"""Single-use ordinary scene-four critic capture for The Wading Path."""

import json
from pathlib import Path
from typing import Literal, cast
from unittest.mock import patch
from uuid import UUID

from open_hollywood_api.persistence.models import AgentInvocation, WorkflowRun
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services.production_model_executor import _critique_inputs, _reference
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import require
from open_hollywood_engine.workflows import SceneCritiqueTask
from open_hollywood_engine.workflows.production_graph import (
    ProductionGraphState,
    _production_from_state,
)
from pydantic import create_model
from sqlalchemy import select
from sqlalchemy.orm import Session

from scripts import ordinary_v61_capture as capture

ROOT = capture.REPO / "data/diagnostics/wading-path-v61-capture-2026-11-24"
SOURCE_CRITIC = UUID("7e0eb43f-d9ee-4a0c-b224-189dbe6ae449")
WIRE_SHA = "e7694a69180226289e6215d7fdefd7d01d3da10b825777edec5d4642225418d1"
MESSAGE_SHA = "a61b35dcd4a3ad0cb5119bfbe6cc4053568185390a10c8e573b70b0120f62e2a"
HISTORY = ("accepted_scene_1", "accepted_scene_2", "accepted_scene_3")
KEYS = {
    "scene_draft": "scene_draft_scene_4",
    "scene_plan": "scene_plan_scene_4",
    "story_bible": "canonical_story_bible",
    "story_blueprint": "integration_story_blueprint",
    **{role: f"scene_draft_scene_{i}" for i, role in enumerate(HISTORY, 1)},
}
CapturePlan = create_model(
    "WadingPathCapturePlan",
    __base__=capture.Plan,
    contract=(Literal["single-ordinary-v61-wading-path-1"], ...),
    input_tokens=(Literal[40000], ...),
    context_tokens=(Literal[48000], ...),
)


def load_task(session: Session, root: Path, plan: capture.Plan) -> SceneCritiqueTask:
    state = cast(ProductionGraphState, json.loads(storage._read(root / "task.json")))
    production = _production_from_state(state)
    run = session.get(WorkflowRun, plan.run_id)
    original = session.get(AgentInvocation, SOURCE_CRITIC)
    require(run is not None and original is not None, "missing_source_run")
    assert run is not None and original is not None
    require(
        plan.source_invocation == SOURCE_CRITIC
        and run.input_state.get("diagnostic_source_invocation_id") == str(SOURCE_CRITIC)
        and run.input_state.get("diagnostic_source_run_id") == str(original.workflow_run_id)
        and run.input_state.get("execution_kind") == "isolated_ordinary_critic_capture"
        and run.id == production.workflow_run_id
        and run.graph_version == "9"
        and production.prompt_template_version == "61",
        "wrong_run_contract",
    )
    require(
        session.scalar(select(AgentInvocation.id).where(AgentInvocation.workflow_run_id == run.id))
        is None,
        "prior_invocation_or_replay",
    )
    versions = {v.artifact.artifact_key: v for v in original.input_versions}
    require(set(versions) == set(KEYS.values()) and set(plan.inputs) == set(KEYS), "wrong_inputs")
    for role, key in KEYS.items():
        v = versions[key]
        pin = plan.inputs[role]
        require(
            v.id == pin.version
            and v.artifact.project_id == run.project_id
            and v.artifact.artifact_type == ("scene_draft" if role in HISTORY else role)
            and canonical_sha256(v.content) == v.content_sha256 == pin.sha256,
            "wrong_source_version",
        )
    bible = versions[KEYS["story_bible"]]
    history = tuple(_reference(versions[KEYS[role]]) for role in HISTORY)
    require(
        bible.content["accepted_scenes"]
        == [
            dict(scene_id=f"scene_{i}", scene_number=i, artifact_version_id=str(ref.version_id))
            for i, ref in enumerate(history, 1)
        ],
        "history_binding_drift",
    )
    unit = production.units[3]
    require(unit.unit_id == "scene_4" and unit.unit_number == 4, "wrong_target_scene")
    task = SceneCritiqueTask(
        production, unit, _reference(versions[KEYS["scene_draft"]]), history, _reference(bible), 0
    )
    require(
        {r.version_id for r in _critique_inputs(task)} == {p.version for p in plan.inputs.values()},
        "task_binding_drift",
    )
    return task


def main() -> int:
    with patch.multiple(
        capture,
        ROOT=ROOT,
        Plan=CapturePlan,
        WIRE_SHA=WIRE_SHA,
        MESSAGE_SHA=MESSAGE_SHA,
        load_task=load_task,
    ):
        return capture.main()


if __name__ == "__main__":
    raise SystemExit(main())
