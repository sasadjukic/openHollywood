"""Verify the scene-wide exclusion contrast and the independent final-gap evidence grades."""

from __future__ import annotations

import socket
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, text_hash

from scripts.wading_path_be.rehearsal import FIXTURES, read
from scripts.wading_path_three_claims import regression
from scripts.wading_path_three_claims import visit_position as rehearsal


def fixture(name: str) -> dict[str, Any]:
    data = read(FIXTURES / f"wading_path_visit_position_{name}.json")
    assert isinstance(data, dict)
    return data


def test_frozen_fixtures() -> None:
    assert canonical_sha256(fixture("gold")) == rehearsal.GOLD_SHA
    assert canonical_sha256(fixture("answers")) == rehearsal.ANSWERS_SHA
    assert canonical_sha256(fixture("evidence")) == rehearsal.DECISIONS_SHA
    gold = fixture("gold")
    assert tuple(gold["claims"]) == ("reached", "at_cut")
    assert len({v["version"] for v in gold["endings"].values()}) == 5
    assert all(set(v["cells"]) == gold["claims"].keys() for v in gold["endings"].values())


@pytest.fixture(scope="module")
def sources() -> dict[str, str]:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private three-claim regression archive")
    return rehearsal.drafts(regression.ARCHIVE, fixture("gold"))


@pytest.fixture(scope="module")
def report(sources: dict[str, str]) -> dict[str, Any]:
    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("local rehearsal attempted network access")

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(socket, "getaddrinfo", offline)
        patch.setattr(socket.socket, "connect", offline)
        patch.setattr(socket.socket, "connect_ex", offline)
        return rehearsal.rehearse()


@pytest.mark.parametrize(
    ("ending", "visit", "position"),
    [
        ("original", "uncertain", "uncertain"),
        ("arrival", "supported", "supported"),
        ("stop", "uncertain", "unsupported"),
        ("retreat", "supported", "unsupported"),
        ("exclusion", "unsupported", "unsupported"),
    ],
)
def test_grounded_cells(report: dict[str, Any], ending: str, visit: str, position: str) -> None:
    for claim, label in (("reached", visit), ("at_cut", position)):
        row = report["rows"][f"{ending}/{claim}"]
        assert (
            row["origin"] == "authored_local_response"
            and row["returned"] == row["expected"] == label
        )
        assert (row["judgment"], row["evidence"]) == (1, 1)


def test_exact_exclusion_and_masked_spans(sources: dict[str, str], report: dict[str, Any]) -> None:
    gold = fixture("gold")
    new = gold["endings"]["exclusion"]
    assert sources["exclusion"] == sources["stop"] + "\n\n" + new["append_paragraph"]
    assert sources["exclusion"][4947:5149] == new["append_paragraph"]
    assert len(sources["stop"]) == 4945 and len(sources["exclusion"]) == 5149
    for name, row in report["rows"].items():
        ending, claim, *_ = name.split("/")
        view = report["evidence_sheet"][row["evidence_id"]]
        assert set(view) == {"claim", "draft_version", "prose_sha256", "citations", "reason"}
        assert view["claim"] == gold["claims"][claim]
        assert view["draft_version"] == gold["endings"][ending]["version"] == row["draft_version"]
        assert view["prose_sha256"] == text_hash(sources[ending])
        for span in view["citations"]:
            assert sources[ending][span["start"] : span["end"]] == span["quote"]


def test_same_gap_across_claims_and_versions(report: dict[str, Any]) -> None:
    rows = report["rows"]
    assert len(rows) == 12 and len(report["evidence_sheet"]) == 12
    views = []
    for ending, gap_judgment in (("stop", 0), ("exclusion", 1)):
        for name, expected in (("reached/gap_only", (gap_judgment, 0)), ("at_cut", (1, 1))):
            row = rows[f"{ending}/{name}"]
            assert (
                row["returned"] == "unsupported" and (row["judgment"], row["evidence"]) == expected
            )
            view = report["evidence_sheet"][row["evidence_id"]]
            (cite,) = view["citations"]
            assert (cite["start"], cite["end"]) == (4806, 4945)
            views.append((view["reason"], cite["quote"]))
    assert len(set(views)) == 1
    assert (
        report["live_calls"] == 0 and report["historical_evidence_seal"] == regression.EVIDENCE_SEAL
    )
    assert len(report["historical_rows"]) == 7
    assert {
        k for k, r in report["historical_rows"].items() if r["judgment"] == r["evidence"] == "pass"
    } == {"N1-B", "N2-B", "R2-B", "P2-B", "Q008-B"}
    assert all(
        report["historical_rows"][k]["judgment"]
        == report["historical_rows"][k]["evidence"]
        == "fail"
        for k in ("R1-B", "P1-B")
    )


def test_label_only_keeps_evidence(sources: dict[str, str]) -> None:
    gold, answers, decisions = (fixture(k) for k in ("gold", "answers", "evidence"))
    original, sheet = rehearsal.grade(gold, sources, answers, decisions)
    answers["exclusion"]["responses"]["reached"]["support"] = "uncertain"
    changed, masked = rehearsal.grade(gold, sources, answers, decisions)
    before, after = original["exclusion/reached"], changed["exclusion/reached"]
    assert sheet == masked and before["evidence_id"] == after["evidence_id"]
    assert (before["judgment"], after["judgment"], before["evidence"], after["evidence"]) == (
        1,
        0,
        1,
        1,
    )


@pytest.mark.parametrize(
    ("fault", "message"),
    [
        ("version", "three_claims_source_binding"),
        ("replace_draft", "three_claims_source_binding"),
        ("shift_gap", "visit_position_unreviewed_evidence"),
        ("drop_claim", "three_claims_missing_answer"),
        ("alter_gold", "visit_position_gold"),
        ("alter_evidence", "visit_position_evidence_seal"),
    ],
)
def test_reject_drift(sources: dict[str, str], fault: str, message: str) -> None:
    gold, answers, decisions = (fixture(k) for k in ("gold", "answers", "evidence"))
    selected = dict(sources)
    case = answers["exclusion"]
    if fault == "version":
        case["draft_version"] = answers["stop"]["draft_version"]
    elif fault == "replace_draft":
        selected["exclusion"] = selected["stop"]
    elif fault == "shift_gap":
        case["responses"]["reached/gap_only"]["spans"] = [[4947, 5149]]
    elif fault == "drop_claim":
        del case["responses"]["at_cut"]
    elif fault == "alter_gold":
        gold["endings"]["exclusion"]["cells"]["reached"][0] = "uncertain"
    else:
        decisions[next(iter(decisions))]["adequate"] = None
    with pytest.raises(EvidenceError, match=message):
        rehearsal.grade(gold, selected, answers, decisions)
