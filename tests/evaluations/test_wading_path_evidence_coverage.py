"""Replay the sealed Sol answers and distinguish the endpoint from the earlier interval."""

import socket
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.ordinary_v61_capture import file_hash
from scripts.wading_path_be.rehearsal import FIXTURES, read
from scripts.wading_path_sol_versions import evidence_coverage as check
from scripts.wading_path_sol_versions import regression
from scripts.wading_path_visit_position import regression as endpoint


def test_frozen_inputs() -> None:
    expected = read(check.EXPECTED)
    assert file_hash(check.EXPECTED) == check.EXPECTED_SHA
    assert file_hash(check.READINGS) == check.READINGS_SHA
    for filename, sha in expected["sources"].items():
        assert file_hash(FIXTURES / filename) == sha
    assert len({r["terminal_sha256"] for r in expected["saved"].values()}) == 13
    assert (
        expected["authored"]["gap_only_event"]["reason"]
        == (expected["authored"]["gap_only_cut"]["reason"])
    )
    assert read(check.READINGS)["gap_only_event"] == read(check.READINGS)["gap_only_cut"]


@pytest.fixture(scope="module")
def results() -> dict[str, Any]:
    if not (regression.ARCHIVE.is_dir() and endpoint.ARCHIVE.is_dir()):
        pytest.skip("requires the paired Sol and S2 private archives")

    def deny(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("network access during coverage rehearsal")

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(socket, "getaddrinfo", deny)
        patch.setattr(socket.socket, "connect", deny)
        patch.setattr(socket.socket, "connect_ex", deny)
        return check.rehearse()


def test_saved_decisions_and_original_scores(results: dict[str, Any]) -> None:
    rows = results["paired"]
    assert len(rows) == 12
    assert {k for k, r in rows.items() if r["decision"] == "flag"} == {
        "SN-61",
        "SN-62",
        "SE-61",
        "SE-62",
    }
    for arm in ("61", "62"):
        for case in ("XN", "XE", "VN", "VE"):
            row = rows[f"{case}-{arm}"]
            assert (row["decision"], row["judgment"], row["evidence"]) == ("pass", "pass", "pass")
            assert ("exclusion" if case.startswith("X") else "visit") in row["used_ranges"]
        assert rows[f"SN-{arm}"]["judgment"] == "pass"
        assert rows[f"SE-{arm}"]["judgment"] == "fail"
        for case in ("SN", "SE"):
            row = rows[f"{case}-{arm}"]
            assert row["returned"] == "unsupported" and row["evidence"] == "fail"
    assert rows["SE-61"]["findings"] == ["insufficient_evidence_for_no_visit"]
    assert rows["SE-62"]["findings"] == ["event_scope_unanswered"]
    s2 = results["endpoint"]
    assert (s2["scope"], s2["decision"], s2["judgment"], s2["evidence"]) == (
        "endpoint",
        "pass",
        "pass",
        "pass",
    )
    assert s2["used_ranges"]["gap"] == (4806, 4945)
    assert results["live_calls"] == 0


def test_authored_controls(results: dict[str, Any]) -> None:
    controls = results["authored"]
    assert {k: r["decision"] for k, r in controls.items()} == {
        "paraphrased_exclusion": "pass",
        "gap_only_event": "flag",
        "gap_only_cut": "pass",
        "narration_only": "pass",
        "open_interval": "pass",
    }
    assert controls["gap_only_event"]["used_ranges"] == controls["gap_only_cut"]["used_ranges"]
    assert controls["paraphrased_exclusion"]["used_ranges"] == {"exclusion": (4947, 5149)}


def test_same_gap_different_obligation() -> None:
    # Even with a real retrospective in the selected source, an unused passage earns no credit.
    available = {"gap", "exclusion"}
    assert check.coverage("endpoint", {"short_at_cut"}, {"gap"}, available) == []
    assert check.coverage("event", {"short_at_cut"}, {"gap"}, available) == [
        "event_scope_unanswered"
    ]
    assert check.coverage("event", {"no_visit"}, {"gap"}, available) == [
        "insufficient_evidence_for_no_visit"
    ]
    assert check.coverage("event", {"no_visit"}, {"exclusion"}, available) == []


def test_negative_account_and_event_need_distinct_coverage() -> None:
    facts = {"approach", "gap", "account"}
    assert check.coverage("narration", {"no_account"}, facts, facts) == []
    assert check.coverage("narration", {"no_account", "no_visit"}, facts, facts) == [
        "insufficient_evidence_for_no_visit"
    ]
    assert check.coverage("narration", {"no_account"}, {"account"}, facts)
    assert check.coverage("narration", {"no_account"}, facts, facts | {"visit"})
    assert check.coverage("event", {"open_visit"}, {"gap"}, facts | {"visit"})


def test_reject_unbound_annotation() -> None:
    reading = {
        "asserts": {"no_visit": "They never arrived"},
        "uses": {"exclusion": "kept away throughout"},
    }
    with pytest.raises(EvidenceError, match="reason_anchor"):
        check.assess("event", "They never arrived.", reading, {"exclusion": (4947, 5149)})
    with pytest.raises(EvidenceError, match="outside_selected_draft"):
        check.assess(
            "event", "They never arrived and kept away throughout.", reading, {"gap": (4806, 4945)}
        )


def test_substituted_version_rejected() -> None:
    gold = read(FIXTURES / "wading_path_narration_event_gold.json")
    stop, visit = (gold["endings"][h]["version"] for h in ("stop", "visit"))
    with pytest.raises(EvidenceError, match="source_version"):
        check.source_ranges(
            {"quote": gold["fixed_stop"]["quote"], "document_version": stop}, visit, gold
        )
