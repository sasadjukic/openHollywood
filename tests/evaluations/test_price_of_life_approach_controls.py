"""Bind three default-brief approach controls to the exact saved ordinary review."""

import json
import shutil
from hashlib import sha256
from typing import Any

import pytest
from open_hollywood_api.services.assessment_intake import collect_intakes
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource

from scripts.q011_arrival.sources import REPO

CONTROLS = REPO / "tests/fixtures/price_of_life_v61_approach_controls.json"
DATA = REPO / "data/diagnostics"
CAPTURE = DATA / "price-of-life-v61-budget-capture-2026-11-24/output"
SCREEN = DATA / "price-of-life-v61-budget-results-2026-11-24/field-screen.json"
CASES = ("Q008", "Q010", "Q011")


def test_three_whole_fields_stay_on_the_default_factual_brief() -> None:
    controls = json.loads(CONTROLS.read_bytes())
    assert controls["expected_brief"] == "B" and controls["requires_position_at_cut"] is False
    fields = controls["controls"]
    assert tuple(fields) == CASES and len({f["pointer"] for f in fields.values()}) == 3
    assert [fields[k]["plan_fields"] for k in CASES] == [["outcome"], [], ["outcome", "exit_state"]]
    assert all(60 in f["draft_excerpts"] and f["evidence_obligation"] for f in fields.values())


@pytest.fixture(scope="module")
def saved(tmp_path_factory: pytest.TempPathFactory) -> tuple[IntakeSource, dict[str, Any]]:
    if not CAPTURE.is_dir():
        pytest.skip("requires the private ordinary Gemma capture")
    terminal = json.loads((CAPTURE / "terminal.json").read_bytes())
    assert terminal["status"] == "captured"
    db = tmp_path_factory.mktemp("price-of-life-source") / "workspace.db"
    shutil.copyfile(CAPTURE / db.name, db)
    assert sha256(db.read_bytes()).hexdigest() == terminal["database_sha256"]
    controls = json.loads(CONTROLS.read_bytes())
    assert terminal["invocation_id"] == controls["invocation"]
    assert terminal["critique_version"] == controls["critique"]
    (entry,) = collect_intakes("saved_review", db, (controls["invocation"],)).entries
    assert entry.reason == "compatible" and entry.source is not None
    return entry.source, controls


@pytest.mark.parametrize("unit", CASES)
def test_approach_control_matches_its_review_and_evidence(
    saved: tuple[IntakeSource, dict[str, Any]], unit: str
) -> None:
    source, controls = saved
    historical = SCREEN.read_bytes()
    assert sha256(historical).hexdigest() == (
        "581aa23c3db392433b513afe4b74f22a4cd389958500396dba19664e43e27144"
    )
    screen = json.loads(historical)
    assert all(screen[key] == controls[key] for key in ("invocation", "critique", "draft", "plan"))
    assert source.review_id == controls["invocation"]
    ctx = source.inventory_work.context
    (provenance,) = (doc for doc in ctx.documents if doc.kind == "scope")
    snap = json.loads(provenance.content_json)["snapshot"]
    assert snap["critique"]["version_id"] == controls["critique"]
    assert snap["draft_version_id"] == controls["draft"]
    assert snap["plan_version_id"] == controls["plan"]
    (field,) = (field for field in ctx.report_fields if field.field_id == unit)
    (statement,) = (stmt for stmt in ctx.statements if stmt.unit_id == unit)
    (prior,) = (row for row in screen["fields"] if row["field_id"] == unit)
    case = controls["controls"][unit]
    assert field.pointer == case["pointer"] == prior["pointer"]
    assert field.text == case["text"] == prior["text"] == statement.quote
    assert (statement.field_id, statement.start, statement.end) == (unit, 0, len(field.text))
    assert prior["position_eligible"] is controls["requires_position_at_cut"] is False
    artifacts = {s["version_id"]: s["content"] for s in snap["sources"]}
    draft = artifacts[controls["draft"]]["prose"]
    inputs = json.loads(snap["messages"][1]["content"])["input_artifacts"]
    (catalog,) = (
        i["content"]["evidence_catalog"]
        for i in inputs
        if i["artifact_version_id"] == controls["draft"]
    )
    for number in case["draft_excerpts"]:
        ref = f"draft_evidence_{number:04}_{controls['draft'].replace('-', '')}"
        (witness,) = (w for w in screen["draft_witnesses"] if w["evidence_ref"] == ref)
        assert witness == catalog[number - 1] and witness["exact_excerpt"] in draft
    assert draft.rstrip().endswith(catalog[59]["exact_excerpt"])
    for key in case["plan_fields"]:
        assert artifacts[controls["plan"]][key] == screen["plan_witnesses"][key]
