"""Verify the later-scene registration keeps its accepted history and its target distinct."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from open_hollywood_api.persistence.database import create_session_factory, create_sqlite_engine
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from sqlalchemy.orm import Session

from scripts import ordinary_v61_capture as capture
from scripts import price_of_life_v61_capture as scene


def check_task(session: Session, plan: capture.Plan) -> None:
    task = scene.load_task(session, scene.ROOT, plan)
    assert task.unit.unit_number == 2 and task.unit.unit_id == "scene_2"
    assert task.draft.version_id == plan.inputs["scene_draft"].version
    assert [r.version_id for r in task.accepted_units] == [
        plan.inputs["accepted_scene_draft"].version
    ]
    assert task.story_bible.version_id == plan.inputs["story_bible"].version
    assert task.revision_number == 0 and not task.critique_history

    pins = dict(plan.inputs)
    pins["scene_draft"], pins["accepted_scene_draft"] = (
        pins["accepted_scene_draft"],
        pins["scene_draft"],
    )
    with pytest.raises(EvidenceError, match="wrong_source_version"):
        scene.load_task(session, scene.ROOT, plan.model_copy(update={"inputs": pins}))
    del pins["accepted_scene_draft"]
    with pytest.raises(EvidenceError, match="wrong_input_set"):
        scene.load_task(session, scene.ROOT, plan.model_copy(update={"inputs": pins}))
    with pytest.raises(EvidenceError, match="wrong_run_contract"):
        scene.load_task(
            session, scene.ROOT, plan.model_copy(update={"source_invocation": plan.run_id})
        )


def test_scene_two_keeps_its_accepted_predecessor(tmp_path: Path) -> None:
    if not (scene.ROOT / "plan.json").is_file():
        pytest.skip("requires the private Price of Life freeze")
    plan = capture.Plan.model_validate_json((scene.ROOT / "plan.json").read_bytes())
    db = tmp_path / "seed-copy.db"
    shutil.copyfile(scene.ROOT / "seed.db", db)
    engine = create_sqlite_engine(db)
    try:
        with create_session_factory(engine)() as session:
            check_task(session, plan)
    finally:
        engine.dispose()
