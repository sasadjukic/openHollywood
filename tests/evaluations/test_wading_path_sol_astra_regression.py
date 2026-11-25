"""Verify the portable observations, the isolated journal replay and the open-event readings."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.ordinary_v61_capture import file_hash
from scripts.wading_path_sol_astra import plan, regression
from scripts.wading_path_sol_versions import evidence_coverage as coverage

FIXTURE = Path(__file__).parents[1] / "fixtures/wading_path_sol_astra_observed.json"


@pytest.fixture(scope="module")
def portable() -> dict[str, Any]:
    result: dict[str, Any] = json.loads(FIXTURE.read_bytes())
    return result


@pytest.fixture(scope="module")
def archive() -> Path:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private Sol/Astra capture")
    return regression.ARCHIVE


@pytest.mark.parametrize("case", plan.CASES)
def test_saved_pair_scores(portable: dict[str, Any], case: str) -> None:
    gold = {
        "SE": "uncertain",
        "SN": "unsupported",
        "XE": "unsupported",
        "XN": "unsupported",
        "VE": "supported",
        "VN": "supported",
    }
    for arm in ("SB", "SX", "AB", "AX"):
        row = portable["rows"][f"{case}-{arm}"]
        event_miss = case == "SE" and arm != "AX"
        evidence_miss = event_miss or (case == "SN" and arm in ("SB", "AB"))
        assert row["gold"] == gold[case]
        assert row["returned"] == ("unsupported" if event_miss else gold[case])
        assert (row["judgment"], row["evidence"]) == (
            "fail" if event_miss else "pass",
            "fail" if evidence_miss else "pass",
        )
        assert row["model"] == plan.MODELS[arm[0]] and row["citations"] == ["E1420"]
        assert row["draft_version"] in row["reason"] and row["evidence_basis"]


def test_complete_inventory(portable: dict[str, Any]) -> None:
    assert file_hash(FIXTURE) == "dea0ac80514ec3d5a8e5ef4c770fb517552416a6825fe5dee35f929f4c06a895"
    assert portable["approval_sha256"] == regression.APPROVAL
    assert portable["evidence_decisions_sha256"] == regression.EVIDENCE_SEAL
    assert portable["archive_sha256"] == regression.SEAL
    rows = portable["rows"]
    assert set(rows) == set(plan.ORDER)
    assert (
        len(
            {
                row[k]
                for row in rows.values()
                for k in ("count_terminal_sha256", "generation_terminal_sha256")
            }
        )
        == 48
    )
    for index, name in enumerate(plan.ORDER, 1):
        assert (rows[name]["count_slot"], rows[name]["generation_slot"]) == (index, index + 24)


def test_offline_replay(
    archive: Path, portable: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("network attempted during local replay")

    read = Path.read_bytes

    def read_archive(path: Path) -> bytes:
        assert path.is_relative_to(archive)
        return read(path)

    monkeypatch.setattr(socket, "getaddrinfo", offline)
    monkeypatch.setattr(socket.socket, "connect", offline)
    monkeypatch.setattr(socket.socket, "connect_ex", offline)
    monkeypatch.setattr(Path, "read_bytes", read_archive)
    assert regression.replay(archive) == portable
    capture = regression.verified(archive)
    previous = json.loads((capture / "source/previous-manifest.json").read_bytes())
    assert file_hash(capture / "source/previous-scores.json") == previous["operator/scores.json"]
    prior_scores = json.loads((capture / "source/previous-scores.json").read_bytes())["rows"]
    for case in plan.CASES:
        for axis in ("returned", "judgment", "evidence"):
            assert portable["rows"][case + "-SB"][axis] == prior_scores[case + "-62"][axis]
    findings = regression.open_event_audit(capture, portable["rows"])
    assert {arm: item["findings"] for arm, item in findings.items()} == {
        "SB": ["event_scope_unanswered"],
        "SX": ["insufficient_evidence_for_no_visit"],
        "AB": ["insufficient_evidence_for_no_visit"],
        "AX": [],
    }
    assert all(
        set(row["used_ranges"].values()) == {(3995, 4804), (4806, 4945)}
        for row in findings.values()
    )


def test_gold_and_claim_sensitive_coverage(archive: Path, portable: dict[str, Any]) -> None:
    capture = regression.verified(archive)
    loc = json.loads((capture / "operator/cited-locations.json").read_bytes())
    gold = json.loads((capture / "source/narration-event-gold.json").read_bytes())
    rows = portable["rows"]
    for case in ("SE", "XE", "VE"):
        ranges = coverage.source_ranges(
            loc[case]["E1420"], rows[f"{case}-AX"]["draft_version"], gold
        )
        assert ranges["gap"] == (4806, 4945)
        # The open-event explanation would overlook the decisive retrospective in both controls.
        findings = coverage.assess(
            "event", rows["SE-AX"]["reason"], regression.OPEN_EVENT_READINGS["AX"], ranges
        )
        assert findings["decision"] == ("pass" if case == "SE" else "flag")
    open_ranges = coverage.source_ranges(loc["SE"]["E1420"], rows["SE-SX"]["draft_version"], gold)
    with pytest.raises(EvidenceError, match="coverage_reason_anchor"):
        coverage.assess(
            "event", rows["SE-SX"]["reason"], regression.OPEN_EVENT_READINGS["AX"], open_ranges
        )
    assert coverage.coverage("event", {"no_visit"}, {"approach", "gap"}, set(open_ranges)) == [
        "insufficient_evidence_for_no_visit"
    ]


def test_damaged_or_substituted_capture(archive: Path, tmp_path: Path) -> None:
    copy = tmp_path / "archive"
    shutil.copytree(archive, copy)
    base = copy / "capture"
    changes = (
        (
            "run/output/37-SE-AX-generation-outcome.json",
            "run/output/40-SE-SX-generation-outcome.json",
        ),
        ("run/requests/SN-AX-generation.json", "run/requests/SN-AB-generation.json"),
        ("operator/cited-locations.json", None),
        ("run/sealed-evidence-decisions.json", None),
    )
    for member, replacement in changes:
        path = base / member
        original = path.read_bytes()
        if replacement:
            path.write_bytes((base / replacement).read_bytes())
        else:
            path.unlink()
        with pytest.raises(EvidenceError, match="scope_archive_members"):
            regression.replay(copy)
        path.write_bytes(original)
    assert regression.verified(copy) == base
