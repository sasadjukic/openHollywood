"""Single-use registration for the ordinary scene-two critique of The Price of Life."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
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
from sqlalchemy import select
from sqlalchemy.orm import Session

from scripts import ordinary_v61_capture as capture

ROOT = capture.REPO / "data/diagnostics/price-of-life-v61-capture-2026-11-24"
SOURCE_CRITIC = UUID("ff193b4e-3de7-4f88-bc9c-f113785f903d")
WIRE_SHA = "a996098f8b671c7b86f9b9d2543c2809607159ad49e7fd8ffa6043d33b16b9f9"
MESSAGE_SHA = "0dadf1e059ea936515cfbef229fbd7d6be13949862842f3857f885abd5730aee"


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
        and run.id == production.workflow_run_id
        and run.input_state.get("execution_kind") == "isolated_ordinary_critic_capture"
        and run.graph_version == "9"
        and production.prompt_template_version == "61",
        "wrong_run_contract",
    )
    require(
        session.scalar(select(AgentInvocation.id).where(AgentInvocation.workflow_run_id == run.id))
        is None,
        "prior_invocation_or_replay",
    )
    keys = {
        "scene_draft": "scene_draft_scene_2",
        "accepted_scene_draft": "scene_draft_scene_1",
        "scene_plan": "scene_plan_scene_2",
        "story_blueprint": "integration_story_blueprint",
        "story_bible": "canonical_story_bible",
    }
    sources = {v.artifact.artifact_key: v for v in original.input_versions}
    require(set(sources) == set(keys.values()) and set(plan.inputs) == set(keys), "wrong_input_set")
    for role, key in keys.items():
        version, pin = sources[key], plan.inputs[role]
        require(
            version.id == pin.version
            and version.artifact.project_id == run.project_id
            and version.artifact.artifact_type == role.removeprefix("accepted_")
            and canonical_sha256(version.content) == version.content_sha256 == pin.sha256,
            "wrong_source_version",
        )
    unit = production.units[1]
    require(unit.unit_number == 2 and unit.unit_id == "scene_2", "wrong_target_scene")
    task = SceneCritiqueTask(
        production,
        unit,
        _reference(sources[keys["scene_draft"]]),
        (_reference(sources[keys["accepted_scene_draft"]]),),
        _reference(sources[keys["story_bible"]]),
        0,
    )
    require(
        {r.version_id for r in _critique_inputs(task)} == {p.version for p in plan.inputs.values()},
        "task_binding_drift",
    )
    return task


def main() -> int:
    # Scope the case bindings to this CLI invocation. Historical registrations keep their pins.
    with patch.multiple(
        capture, ROOT=ROOT, WIRE_SHA=WIRE_SHA, MESSAGE_SHA=MESSAGE_SHA, load_task=load_task
    ):
        return capture.main()


if __name__ == "__main__":
    raise SystemExit(main())
