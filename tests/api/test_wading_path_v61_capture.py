"""Keep the initial scene-four review bound to its three ordered accepted drafts."""

import shutil
from pathlib import Path

import pytest
from open_hollywood_api.persistence.database import create_session_factory, create_sqlite_engine
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts import ordinary_v61_capture as capture
from scripts import wading_path_v61_capture as scene


def test_single_use_budget() -> None:
    fields = scene.CapturePlan.model_json_schema()["properties"]
    for field, value in {
        "input_tokens": 40000,
        "output_tokens": 8000,
        "context_tokens": 48000,
        "generations": 1,
        "counts": 0,
        "retries": 0,
    }.items():
        assert fields[field]["const"] == value
    assert capture.Plan.model_json_schema()["properties"]["input_tokens"]["const"] == 24000


def test_separate_target_history_and_source_critic(tmp_path: Path) -> None:
    if not (scene.ROOT / "plan.json").exists():
        pytest.skip("requires the private Wading Path registration")
    plan = scene.CapturePlan.model_validate_json((scene.ROOT / "plan.json").read_bytes())
    db = tmp_path / "seed-copy.db"
    shutil.copyfile(scene.ROOT / "seed.db", db)
    engine = create_sqlite_engine(db)
    try:
        with create_session_factory(engine)() as session:
            task = scene.load_task(session, scene.ROOT, plan)
            assert task.unit.unit_id == "scene_4" and task.revision_number == 0
            assert task.draft.version_id == plan.inputs["scene_draft"].version
            assert task.story_bible.version_id == plan.inputs["story_bible"].version
            assert [r.version_id for r in task.accepted_units] == [
                plan.inputs[k].version for k in scene.HISTORY
            ]
            assert not task.critique_history
            for left, right in [
                ("accepted_scene_1", "accepted_scene_3"),
                ("scene_draft", "accepted_scene_3"),
            ]:
                pins = dict(plan.inputs)
                pins[left], pins[right] = pins[right], pins[left]
                with pytest.raises(EvidenceError, match="wrong_source_version"):
                    scene.load_task(session, scene.ROOT, plan.model_copy(update={"inputs": pins}))
            missing = dict(plan.inputs)
            del missing["accepted_scene_2"]
            with pytest.raises(EvidenceError, match="wrong_inputs"):
                scene.load_task(session, scene.ROOT, plan.model_copy(update={"inputs": missing}))
            with pytest.raises(EvidenceError, match="wrong_run_contract"):
                scene.load_task(
                    session, scene.ROOT, plan.model_copy(update={"source_invocation": plan.run_id})
                )
    finally:
        engine.dispose()
