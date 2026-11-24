"""Rehearse three time- and source-specific claims on the same four Wading Path drafts."""

from __future__ import annotations

import socket
from copy import deepcopy
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.wading_path_be.rehearsal import FIXTURES, read
from scripts.wading_path_observations import regression
from scripts.wading_path_observations import three_claims as rehearsal


def fixture(name: str) -> dict[str, Any]:
    data = read(FIXTURES / f"wading_path_three_claims_{name}.json")
    assert isinstance(data, dict)
    return data


@pytest.fixture(scope="module")
def sources() -> dict[str, str]:
    if not regression.ARCHIVE.exists():
        pytest.skip("requires the private Wading Path observation archive")
    return rehearsal.drafts(regression.ARCHIVE, fixture("gold"))


@pytest.fixture(scope="module")
def report(sources: dict[str, str]) -> dict[str, Any]:
    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("rehearsal attempted network access")

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(socket, "getaddrinfo", offline)
        patch.setattr(socket.socket, "connect", offline)
        patch.setattr(socket.socket, "connect_ex", offline)
        return rehearsal.rehearse()


def test_portable_fixture_seals() -> None:
    assert canonical_sha256(fixture("gold")) == rehearsal.GOLD_SHA
    assert canonical_sha256(fixture("answers")) == rehearsal.ANSWERS_SHA
    assert canonical_sha256(fixture("evidence")) == rehearsal.DECISIONS_SHA


@pytest.mark.parametrize(
    ("ending", "labels"),
    [
        ("original", ("unsupported", "uncertain", "uncertain")),
        ("arrival", ("supported", "supported", "supported")),
        ("stop", ("unsupported", "uncertain", "unsupported")),
        ("retreat", ("supported", "supported", "unsupported")),
    ],
)
def test_primary_scores(report: dict[str, Any], ending: str, labels: tuple[str, str, str]) -> None:
    for claim, label in zip(("narrated", "reached", "at_cut"), labels, strict=True):
        row = report["rows"][f"{ending}/{claim}"]
        assert row["returned"] == row["expected"] == label
        assert (row["judgment"], row["evidence"]) == (1, 1)
        assert row["origin"] == "authored_local_response"


def test_retreat_and_citations(report: dict[str, Any], sources: dict[str, str]) -> None:
    gold = fixture("gold")
    assert (
        sources["retreat"]
        == sources["arrival"] + "\n\n" + gold["endings"]["retreat"]["append_paragraph"]
    )
    assert sources["arrival"].startswith(sources["original"] + "\n\n")
    assert sources["retreat"][4806:4920] == sources["arrival"][4806:]
    assert (
        sources["retreat"][4922:]
        == "Then Elias and Maya stepped back three full strides from the housing and stayed there."
    )
    assert len({v["version"] for v in gold["endings"].values()}) == 4
    for key, row in report["rows"].items():
        ending, claim, *_ = key.split("/")
        view = report["evidence_sheet"][row["evidence_id"]]
        assert set(view) == {"claim", "reason", "draft_version", "prose_sha256", "citations"}
        assert view["claim"] == gold["claims"][claim]
        assert view["draft_version"] == row["draft_version"] == gold["endings"][ending]["version"]
        for span in view["citations"]:
            assert sources[ending][span["start"] : span["end"]] == span["quote"]
    control = report["historical_q008_b"]
    assert (control["returned"], control["judgment"], control["evidence"]) == (
        "unsupported",
        "pass",
        "pass",
    )
    assert report["live_calls"] == 0


def test_wrong_scope_and_label_only_controls(report: dict[str, Any]) -> None:
    rows = report["rows"]
    assert len(rows) == 17 and len(report["evidence_sheet"]) == 16
    expected = {
        "original/narrated/physical_impossibility": (1, 0),
        "original/reached/omission": (0, 0),
        "stop/reached/final_position_only": (1, 0),
        "retreat/at_cut/denied_visit": (1, 0),
        "retreat/reached/changed_label": (0, 1),
    }
    assert {
        k: (v["judgment"], v["evidence"]) for k, v in rows.items() if k.count("/") == 2
    } == expected
    assert (
        rows["retreat/reached"]["evidence_id"]
        == rows["retreat/reached/changed_label"]["evidence_id"]
    )


@pytest.mark.parametrize(
    ("damage", "error"),
    [
        ("gold", "three_claims_gold"),
        ("decision", "three_claims_evidence_seal"),
        ("old_version", "three_claims_source_binding"),
        ("prose", "three_claims_source_binding"),
        ("past_end", "three_claims_span"),
        ("missing_claim", "three_claims_missing_answer"),
        ("earlier_passage", "three_claims_unreviewed_evidence"),
        ("altered_reason", "three_claims_unreviewed_evidence"),
    ],
)
def test_drift_and_unreviewed_answers(sources: dict[str, str], damage: str, error: str) -> None:
    gold, answers, decisions = (fixture(k) for k in ("gold", "answers", "evidence"))
    selected = dict(sources)
    retreat = answers["retreat"]
    answer = retreat["responses"]["at_cut"]
    if damage == "gold":
        gold["endings"]["retreat"]["cells"]["at_cut"][0] = "supported"
    elif damage == "decision":
        decisions[next(iter(decisions))]["adequate"] = None
    elif damage == "old_version":
        retreat["draft_version"] = answers["arrival"]["draft_version"]
    elif damage == "prose":
        selected["retreat"] = selected["arrival"]
    elif damage == "past_end":
        answer["spans"] = [[4922, 5009]]
    elif damage == "missing_claim":
        del retreat["responses"]["at_cut"]
    elif damage == "earlier_passage":
        answer["spans"] = [[4806, 4920]]
    else:
        answer["reason"] += " They never arrived."
    with pytest.raises(EvidenceError, match=error):
        rehearsal.grade_answers(gold, selected, answers, decisions)


def test_label_change_preserves_evidence(sources: dict[str, str]) -> None:
    gold, answers, decisions = (fixture(k) for k in ("gold", "answers", "evidence"))
    before, sheet = rehearsal.grade_answers(gold, sources, answers, decisions)
    changed = deepcopy(answers)
    changed["original"]["responses"]["at_cut"]["support"] = "unsupported"
    after, changed_sheet = rehearsal.grade_answers(gold, sources, changed, decisions)
    assert sheet == changed_sheet
    assert before["original/at_cut"]["judgment"] == 1 and after["original/at_cut"]["judgment"] == 0
    assert before["original/at_cut"]["evidence"] == after["original/at_cut"]["evidence"] == 1
