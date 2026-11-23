"""Protect the observed B/E pairs and the chronology of the authored transfer candidates."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.q011_evidence_check import regression, transfer_audit


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("regression and source admission must remain offline")

    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)


@pytest.fixture
def archive() -> Path:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private Q011 B/E capture")
    return regression.ARCHIVE


def test_five_observed_pairs(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    read = Path.read_bytes

    def archive_only(path: Path) -> bytes:
        assert path.is_relative_to(archive)
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", archive_only)
    result = regression.replay(archive)
    assert (result["members"], result["slots"], result["live_calls"]) == (78, 20, 0)
    assert (
        result["decision"] == "genuine_paired_recovery"
        and result["genuine_baseline_recovery"] is False
    )
    pairs = result["pairs"]
    labels = dict(
        approach="uncertain",
        arrival="supported",
        stop="unsupported",
        **{"gap-at-cut": "unsupported", "gap-before-motion": "uncertain"},
    )
    assert set(pairs) == set(labels)
    for case, gold in labels.items():
        p = pairs[case]
        b, e = p["arms"]["B"], p["arms"]["E"]
        assert p["gold"] == gold and (e["returned"], e["judgment"], e["evidence"]) == (
            gold,
            "pass",
            "pass",
        )
        if gold == "uncertain":
            assert (b["returned"], b["judgment"], b["evidence"]) == ("unsupported", "fail", "fail")
            assert p["movement"] == dict(judgment="gain", evidence="gain")
        else:
            assert (b["returned"], b["judgment"], b["evidence"]) == (gold, "pass", "pass")
            assert p["movement"] == dict(judgment="retained_pass", evidence="retained_pass")


@pytest.mark.parametrize(
    ("member", "substitute"),
    [
        (
            "run/output/12-AP-E-generation-outcome.json",
            "run/output/11-AP-B-generation-outcome.json",
        ),
        ("source/gap-at-cut.json", "source/gap-before-motion.json"),
        ("run/requests/GM-E-input_count.json", "run/requests/GM-B-input_count.json"),
        ("run/sealed-evidence-decisions.json", None),
        ("operator/scores.json", None),
    ],
)
def test_rejects_mixed_or_missing_capture(
    archive: Path, tmp_path: Path, member: str, substitute: str | None
) -> None:
    copy = tmp_path / "archive"
    shutil.copytree(archive / "capture", copy / "capture")
    shutil.copyfile(archive / "capture-manifest.json", copy / "capture-manifest.json")
    target = copy / "capture" / member
    if substitute:
        target.write_bytes((copy / "capture" / substitute).read_bytes())
    else:
        target.unlink()
    with pytest.raises(EvidenceError, match="regression_(inventory|member)"):
        regression.replay(copy)


@pytest.fixture
def admission() -> Path:
    if not transfer_audit.ROOT.is_dir():
        pytest.skip("requires the private Q011 source admission")
    return transfer_audit.ROOT


def test_freshness_and_source_only_admission(
    admission: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    read = Path.read_bytes

    def source_only(path: Path) -> bytes:
        assert path.is_relative_to(admission) or (
            path.parent.name == "requests" and path.name.endswith("-generation.json")
        )
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", source_only)
    result = transfer_audit.verify(admission)
    assert (
        result["saved_screened"],
        result["saved_admitted"],
        result["admitted_cases"],
        result["prior_generation_bodies"],
        result["live_calls"],
    ) == (6, 0, 8, 50, 0)
    assert len(result["authored_families"]) == 2


@pytest.mark.parametrize("damage", ["order", "version", "offset"])
def test_rejects_wrong_time_or_witness(admission: Path, damage: str) -> None:
    cases = json.loads((admission / "gold.json").read_bytes())["cases"]
    rows: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for key in ("T01", "T03", "T05", "T07"):
        rows[cases[key]["state"]] = (
            json.loads((admission / f"packets/{key}.json").read_bytes()),
            cases[key],
        )
    packet, row = rows["earlier_gap"]
    if damage == "order":
        packet["draft"]["content"]["prose"] = rows["terminal_gap"][0]["draft"]["content"]["prose"]
    elif damage == "version":
        row["witnesses"]["gap"]["draft_version"] = rows["terminal_gap"][0]["draft"]["version"]
    else:
        row["witnesses"]["gap"]["start"] += 1
    with pytest.raises(EvidenceError, match="transfer_(timing_or_source|witness)"):
        transfer_audit.check_family(rows)
