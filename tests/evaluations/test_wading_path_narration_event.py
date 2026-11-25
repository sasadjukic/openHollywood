"""Six fixed-stop cases, label-masked evidence grading and the observed S2 endpoint."""

from __future__ import annotations

import socket
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.wading_path_be.rehearsal import FIXTURES, read
from scripts.wading_path_visit_position import narration_event as rehearsal
from scripts.wading_path_visit_position import regression


def fixtures() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    def load(name: str) -> dict[str, Any]:
        value = read(FIXTURES / f"wading_path_narration_event_{name}.json")
        assert isinstance(value, dict)
        return value

    return load("gold"), load("answers"), load("evidence")


def test_portable_freezes() -> None:
    gold, answers, decisions = fixtures()
    assert canonical_sha256(gold) == rehearsal.GOLD_SHA
    assert canonical_sha256(answers) == rehearsal.ANSWERS_SHA
    assert canonical_sha256(decisions) == rehearsal.EVIDENCE_SHA
    assert set(gold["endings"]) == {"stop", "exclusion", "visit"}
    assert set(gold["claims"]) == {"narrated", "reached"}
    assert len(decisions) == 12


@pytest.fixture(scope="module")
def drafts() -> dict[str, str]:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private S1/S2 regression archive")
    return rehearsal.sources(regression.ARCHIVE, fixtures()[0])


@pytest.fixture(scope="module")
def report(drafts: dict[str, str]) -> dict[str, Any]:
    def deny(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("network attempted during local rehearsal")

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(socket, "getaddrinfo", deny)
        patch.setattr(socket.socket, "connect", deny)
        patch.setattr(socket.socket, "connect_ex", deny)
        return rehearsal.rehearse()


def test_histories_preserve_stop(drafts: dict[str, str]) -> None:
    gold = fixtures()[0]
    stop = drafts["stop"]
    assert len(stop) == 4945
    assert stop[4806:] == gold["fixed_stop"]["quote"]
    assert "three full strides short" in stop[4806:] and stop.endswith("and stayed there.")
    for name, extent in (("exclusion", 5149), ("visit", 5132)):
        addition = gold["endings"][name]["append_paragraph"]
        assert drafts[name] == stop + "\n\n" + addition
        assert drafts[name][4947:extent] == addition and len(drafts[name]) == extent
    assert "neither Elias nor Maya had ever been closer" in drafts["exclusion"][4947:]
    assert "before the light steadied" in drafts["visit"][4947:]
    assert "had reached the master breaker panel housing together" in drafts["visit"][4947:]


@pytest.mark.parametrize(
    ("history", "claim", "label", "gap_judgment"),
    [
        ("stop", "narrated", "unsupported", 1),
        ("stop", "reached", "uncertain", 0),
        ("exclusion", "narrated", "unsupported", 1),
        ("exclusion", "reached", "unsupported", 1),
        ("visit", "narrated", "supported", 0),
        ("visit", "reached", "supported", 0),
    ],
)
def test_scope_scores(
    report: dict[str, Any], history: str, claim: str, label: str, gap_judgment: int
) -> None:
    row = report["rows"][f"{history}/{claim}"]
    control = report["rows"][f"{history}/{claim}/gap_only"]
    assert row["origin"] == "authored_local_response"
    assert (row["expected"], row["returned"], row["judgment"], row["evidence"]) == (
        label,
        label,
        1,
        1,
    )
    assert (control["returned"], control["judgment"], control["evidence"]) == (
        "unsupported",
        gap_judgment,
        0,
    )
    (cite,) = report["evidence_sheet"][control["evidence_id"]]["citations"]
    assert (cite["start"], cite["end"], cite["quote"]) == (
        4806,
        4945,
        fixtures()[0]["fixed_stop"]["quote"],
    )


def test_mask_and_historical_endpoint(drafts: dict[str, str], report: dict[str, Any]) -> None:
    assert len(report["rows"]) == len(report["evidence_sheet"]) == 12
    for key, score in report["rows"].items():
        history = key.split("/")[0]
        view = report["evidence_sheet"][score["evidence_id"]]
        assert set(view) == {"claim", "draft_version", "prose_sha256", "citations", "reason"}
        assert (
            canonical_sha256(view) == score["evidence_id"]
            and view["draft_version"] == score["draft_version"]
        )
        for cite in view["citations"]:
            assert drafts[history][cite["start"] : cite["end"]] == cite["quote"]
    assert (
        report["live_calls"] == 0 and report["historical_evidence_seal"] == regression.EVIDENCE_SEAL
    )
    s1, s2 = (report["historical_rows"][k] for k in ("S1-B", "S2-B"))
    assert (s1["returned"], s1["judgment"], s1["evidence"]) == ("unsupported", "fail", "fail")
    assert (s2["returned"], s2["judgment"], s2["evidence"]) == ("unsupported", "pass", "pass")


def test_label_only_changes_judgment(drafts: dict[str, str]) -> None:
    gold, answers, decisions = fixtures()
    original, sheet = rehearsal.grade(gold, drafts, answers, decisions)
    answers["stop"]["responses"]["reached"]["support"] = "unsupported"
    changed, masked = rehearsal.grade(gold, drafts, answers, decisions)
    assert sheet == masked
    before, after = (rows["stop/reached"] for rows in (original, changed))
    assert before["evidence_id"] == after["evidence_id"]
    assert (before["judgment"], after["judgment"], before["evidence"], after["evidence"]) == (
        1,
        0,
        1,
        1,
    )


@pytest.mark.parametrize(
    ("fault", "error"),
    [
        ("wrong_version", "three_claims_source_binding"),
        ("wrong_story", "three_claims_source_binding"),
        ("citation", "narration_event_unreviewed_evidence"),
        ("missing", "three_claims_missing_answer"),
        ("gold", "narration_event_gold"),
        ("decision", "narration_event_evidence_seal"),
    ],
)
def test_reject_drift(drafts: dict[str, str], fault: str, error: str) -> None:
    gold, answers, decisions = fixtures()
    sources = drafts.copy()
    if fault == "wrong_version":
        answers["visit"]["draft_version"] = answers["exclusion"]["draft_version"]
    elif fault == "wrong_story":
        sources["visit"] = sources["exclusion"]
    elif fault == "citation":
        answers["visit"]["responses"]["reached"]["spans"] = [[4806, 4945]]
    elif fault == "missing":
        del answers["stop"]["responses"]["narrated"]
    elif fault == "gold":
        gold["endings"]["stop"]["cells"]["reached"][0] = "unsupported"
    else:
        decisions[next(iter(decisions))]["adequate"] = None
    with pytest.raises(EvidenceError, match=error):
        rehearsal.grade(gold, sources, answers, decisions)
