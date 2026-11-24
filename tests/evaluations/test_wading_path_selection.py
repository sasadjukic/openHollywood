"""Exercise the Wading Path source, whole-field selection and the offline gold join."""

from __future__ import annotations

import json
import socket
from copy import deepcopy
from pathlib import Path
from typing import Any, Literal, NoReturn

import pytest
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.q011_transfer import wading_path_selection as rehearsal


@pytest.fixture(scope="module")
def source() -> IntakeSource:
    if not rehearsal.DATABASE.exists():
        pytest.skip("requires the private Wading Path capture")
    return rehearsal.load_source()


@pytest.fixture(scope="module")
def rows(source: IntakeSource) -> list[dict[str, Any]]:
    return [rehearsal.select(source, u, a) for u, a in rehearsal.PREVIEWS]


def test_three_whole_fields_against_sealed_gold(
    source: IntakeSource, rows: list[dict[str, Any]]
) -> None:
    proof = rehearsal.verify_gold(source, rows)
    assert {u: c["label"] for u, c in proof["criteria"].items()} == {
        "Q010": "uncertain",
        "Q011": "uncertain",
        "Q008": "unsupported",
    }
    assert proof["evidence_witnesses_checked"] == 7 and len(proof["binding"]["inputs"]) == 7
    assert len({r["work_sha256"] for r in rows}) == 3
    for r in rows:
        assert r["active_units"] == [r["unit"]] and r["status"] == "pending_assessment"
        assert (
            r["span"] == [0, len(r["text"])] and r["declaration"]["statement"]["quote"] == r["text"]
        )
        assert r["assessment_result"] is r["completion_receipt"] is None
        assert r["factual_support"] == r["evidence_adequacy"] == "unassessed"
        assert r["model_input"] is r["writer_dispatch_authorized"] is False
        assert "evidence_pass_requires" not in json.dumps(r)


def test_position_and_assignment_pairs_keep_their_own_predicates(
    rows: list[dict[str, Any]],
) -> None:
    by_key = {(r["unit"], r["arm"]): r for r in rows}
    for unit, refs, target in (
        ("Q010", ["E1420"], "Elias and Maya standing before the master breaker panel housing"),
        (
            "Q011",
            ["E1420", "E0258", "E0254"],
            "Elias and Maya having reached the housing and standing before the final barrier",
        ),
    ):
        b, e = (by_key[unit, a] for a in ("B", "E"))
        assert b["source_refs"] == e["source_refs"] == refs
        assert b["scope"] == e["scope"] and b["declaration"] == e["declaration"]
        assert e["brief"]["evidence_obligation"].endswith(target + " at the scene cut.")
        assert "Identify the draft observation" not in b["brief"]["evidence_obligation"]
    control = by_key["Q008", "B"]
    assert control["source_refs"] == ["E1420", "E0258"] and ("Q008", "E") not in by_key
    assert "what actions does the draft narrate" in control["brief"]["question"]
    assert "standing" not in json.dumps(control["brief"])


def test_repeat_after_switch_uses_neither_gold_nor_transport(
    source: IntakeSource, rows: list[dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("selection consulted a scorer file or opened a network connection")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    for unit in ("Q010", "Q008", "Q011", "Q010"):
        arm: Literal["B", "E"] = "B" if unit == "Q008" else "E"
        assert rehearsal.select(source, unit, arm) == next(
            r for r in rows if (r["unit"], r["arm"]) == (unit, arm)
        )


def test_wrong_source_control_route_and_unregistered_field(source: IntakeSource) -> None:
    for change in ({"review_id": "different-review"}, {"source_sha256": "0" * 64}):
        with pytest.raises(EvidenceError, match="wading_source"):
            rehearsal.select(source.model_copy(update=change), "Q010", "E")
    with pytest.raises(EvidenceError, match="wading_arm"):
        rehearsal.select(source, "Q008", "E")
    with pytest.raises(EvidenceError, match="wading_field"):
        rehearsal.select(source, "Q007", "B")


def test_changed_gold_is_rejected(
    source: IntakeSource,
    rows: list[dict[str, Any]],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    changed = json.loads(rehearsal.GOLD.read_bytes())
    changed["claims"][0]["label"] = "uncertain"
    local = tmp_path / "gold.json"
    local.write_text(json.dumps(changed), encoding="utf-8")
    monkeypatch.setattr(rehearsal, "GOLD", local)
    with pytest.raises(EvidenceError, match="source_drift"):
        rehearsal.verify_gold(source, rows)


@pytest.mark.parametrize(
    "damage", ["shortened", "pointer", "plan_ref", "wrong_question", "control_obligation"]
)
def test_drift_is_rejected(source: IntakeSource, rows: list[dict[str, Any]], damage: str) -> None:
    changed = deepcopy(rows)
    q10 = next(r for r in changed if (r["unit"], r["arm"]) == ("Q010", "E"))
    q11 = next(r for r in changed if (r["unit"], r["arm"]) == ("Q011", "E"))
    control = next(r for r in changed if r["unit"] == "Q008")
    if damage == "shortened":
        q10["text"] = q10["text"].split(" and are standing")[0]
    elif damage == "pointer":
        q10["pointer"] = q11["pointer"]
    elif damage == "plan_ref":
        q11["source_refs"].remove("E0258")
    elif damage == "wrong_question":
        q11["brief"]["evidence_obligation"] = q10["brief"]["evidence_obligation"]
    else:
        control["brief"]["evidence_obligation"] = q10["brief"]["evidence_obligation"]
    with pytest.raises(EvidenceError, match="wading_(arm_drift|baseline_drift|gold_selection)"):
        rehearsal.verify_gold(source, changed)
