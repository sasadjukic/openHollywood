"""Regress the local label substitutions independently of the source-bound evidence scores."""

from __future__ import annotations

import socket
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, text_hash

from scripts.wading_path_be import regression, rehearsal


@pytest.fixture(scope="module")
def report() -> dict[str, Any]:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private Wading Path regression archive")

    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("local rehearsal attempted a network connection")

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(socket, "getaddrinfo", offline)
        patch.setattr(socket.socket, "connect", offline)
        patch.setattr(socket.socket, "connect_ex", offline)
        return rehearsal.rehearse()


@pytest.mark.parametrize(("arm", "evidence"), [("B", 1), ("E", 0)])
def test_only_support_changes(report: dict[str, Any], arm: str, evidence: int) -> None:
    row = report["label_substitutions"][arm]
    archive, _ = regression.verified_capture(regression.ARCHIVE)
    audit = rehearsal.read(archive / "operator/audit.json")
    slot = next(s for s in audit["slots"] if s["eligible"] and s["cell"] == f"Q011-{arm}")
    original = slot["final"]["assessments"]["Q011"]
    assert row["observed_answer"] == original and original["support"] == "unsupported"
    assert row["local_label_only_answer"] == {**original, "support": "uncertain"}
    assert row["observed_scores"] == {"judgment": 0, "evidence": evidence}
    assert row["local_scores"] == {"judgment": 1, "evidence": evidence}


@pytest.mark.parametrize(
    ("name", "label", "reach", "standing"),
    [
        ("original", "uncertain", "open", "open"),
        ("arrival", "supported", "established", "established"),
        ("stop_short", "unsupported", "open", "contradicted"),
    ],
)
def test_ending_controls(
    report: dict[str, Any], name: str, label: str, reach: str, standing: str
) -> None:
    controls = report["authored_responses"]
    row = controls[name]
    assert (row["gold"], row["reach"], row["standing_at_cut"]) == (label, reach, standing)
    assert row["scores"] == {"judgment": 1, "evidence": 1}
    assert len({v["draft_version"] for v in controls.values()}) == 3
    capture = regression.ARCHIVE / "capture"
    original = rehearsal.read(capture / "operator/cited-locations.json")["E1420"]["quote"]
    addition = row["append_paragraph"]
    selected = original + ("\n\n" + addition if addition else "")
    start, end = row["cut_span"]
    assert text_hash(selected) == row["response"]["prose_sha256"]
    assert selected[start:end] == row["cut_quote"] and end == len(selected)
    assert row["response"]["evidence"] == ["E0258", "E0254", row["draft_ref"]]
    assert selected[4707:4804] == row["barrier_witness"]


def test_wrong_version_and_narration_controls(report: dict[str, Any]) -> None:
    assert report["live_calls"] == 0
    assert report["unchanged_text_on_other_drafts"] == {
        f"{case}-{arm}": {"judgment": 0, "evidence": 0}
        for case in ("arrival", "stop_short")
        for arm in ("B", "E")
    }
    control = report["narrated_arrival_control"]
    assert (control["returned"], control["judgment"], control["evidence"]) == (
        "unsupported",
        "pass",
        "pass",
    )


def test_seals_without_private_archive() -> None:
    for name, expected in [
        ("wading_path_q011_endings.json", rehearsal.GOLD_SHA),
        ("wading_path_q011_evidence_decisions.json", rehearsal.DECISIONS_SHA),
    ]:
        assert canonical_sha256(rehearsal.read(rehearsal.FIXTURES / name)) == expected


def test_changed_reason_requires_new_evidence_grade(
    report: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    label, reason = rehearsal.ANSWERS["stop_short"]
    monkeypatch.setitem(
        rehearsal.ANSWERS, "stop_short", (label, reason + " They never reached it.")
    )
    with pytest.raises(EvidenceError, match="ungraded_evidence"):
        rehearsal.rehearse()


def test_changed_label_leaves_masked_grade_intact(
    report: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, reason = rehearsal.ANSWERS["arrival"]
    monkeypatch.setitem(rehearsal.ANSWERS, "arrival", ("uncertain", reason))
    result = rehearsal.rehearse()["authored_responses"]["arrival"]
    assert result["scores"] == {"judgment": 0, "evidence": 1}
