"""Replay the observed R1/P1 failures and five controls, then check exact temporal coverage."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.wading_path_three_claims import coverage, regression


@pytest.fixture
def archive(monkeypatch: pytest.MonkeyPatch) -> Path:
    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("network attempted in local audit")

    monkeypatch.setattr(socket, "getaddrinfo", offline)
    monkeypatch.setattr(socket.socket, "connect", offline)
    monkeypatch.setattr(socket.socket, "connect_ex", offline)
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private three-claim capture")
    return regression.ARCHIVE


def test_seven_observed_assessments(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    read = Path.read_bytes

    def local_only(path: Path) -> bytes:
        assert path.is_relative_to(archive)
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", local_only)
    result = regression.replay(archive)
    assert (result["slots"], result["live_calls"], result["decision"]) == (
        14,
        0,
        "hold_claim_scope",
    )
    assert result["evidence_decisions_sha256"] == regression.EVIDENCE_SEAL
    gold = json.loads((archive / "capture/run/gold.json").read_bytes())
    assert {
        k: (gold[k.split("-")[0]]["gold"], v["returned"], v["judgment"], v["evidence"])
        for k, v in result["rows"].items()
    } == {
        "R1-B": ("uncertain", "unsupported", "fail", "fail"),
        "P1-B": ("uncertain", "unsupported", "fail", "fail"),
        "N1-B": ("unsupported", "unsupported", "pass", "pass"),
        "N2-B": ("supported", "supported", "pass", "pass"),
        "R2-B": ("supported", "supported", "pass", "pass"),
        "P2-B": ("unsupported", "unsupported", "pass", "pass"),
        "Q008-B": ("unsupported", "unsupported", "pass", "pass"),
    }
    sheet = json.loads((archive / "capture/operator/evidence-sheet.json").read_bytes())
    rows = {r["case"]: r for r in sheet["rows"]}
    assert "without their traversing the passage" in rows["R1"]["reason"]
    assert "This staging places the housing ahead of them" in rows["P1"]["reason"]
    assert all(
        r["citations"] == (["E0258", "E1420"] if k == "Q008" else ["E1420"])
        for k, r in rows.items()
    )
    assert len({r["scoring_id"] for r in rows.values()}) == 7


def test_visit_and_cut_contrasts(archive: Path) -> None:
    audit = coverage.audit(archive)
    assert audit["live_calls"] == 0 and audit["whole_scene_exclusions"] == []
    cases = audit["drafts"]
    assert {
        k: (r["findings"]["reached"]["label"], r["findings"]["at_cut"]["label"])
        for k, r in cases.items()
    } == {
        "original": ("uncertain", "uncertain"),
        "stop": ("uncertain", "unsupported"),
        "retreat": ("supported", "unsupported"),
        "arrival": ("supported", "supported"),
    }
    assert len({r["version"] for r in cases.values()}) == 4
    original = cases["original"]["passages"]
    for name in ("opening", "crossing", "entry", "look", "housing"):
        assert all(r["passages"][name] == original[name] for r in cases.values())
    assert "center of the room" in original["opening"]["quote"]
    assert "reached the eastern wall" in original["entry"]["quote"]
    assert "looked deeper" in original["look"]["quote"]
    assert "stood the heavy steel housing" in original["housing"]["quote"]
    assert original["housing"]["end"] == 4804
    stop = cases["stop"]["passages"]["persistent_gap"]
    assert stop["end"] == 4945 and "short of" in stop["quote"] and "stayed there" in stop["quote"]
    arrival = cases["arrival"]["passages"]["arrival"]
    retreat = cases["retreat"]["passages"]["retreat"]
    assert cases["retreat"]["passages"]["arrival"] == arrival
    assert arrival["end"] == 4920 and "Elias and Maya reached" in arrival["quote"]
    assert retreat["start"] == arrival["end"] + 2 and retreat["end"] == 5008
    assert (
        "stepped back three full strides" in retreat["quote"] and "stayed there" in retreat["quote"]
    )
    assert audit["assignment"]["quote"] == "They reach the breaker panel housing."


@pytest.mark.parametrize(
    ("member", "substitute"),
    [
        (
            "run/output/13-R1-B-generation-outcome.json",
            "run/output/10-P1-B-generation-outcome.json",
        ),
        ("run/output/11-Q008-B-generation-outcome.json", None),
        ("run/requests/P2-B-generation.json", "run/requests/P1-B-generation.json"),
        ("run/output/01-N1-B-input_count-outcome.json", None),
        ("run/gold.json", None),
        ("run/sealed-evidence-decisions.json", None),
        ("operator/cited-locations.json", None),
        ("source/previous-locations.json", None),
    ],
)
def test_reject_damage(archive: Path, tmp_path: Path, member: str, substitute: str | None) -> None:
    copied = tmp_path / "archive"
    shutil.copytree(archive / "capture", copied / "capture")
    shutil.copyfile(archive / "capture-manifest.json", copied / "capture-manifest.json")
    target = copied / "capture" / member
    if substitute is None:
        target.unlink()
    else:
        shutil.copyfile(copied / "capture" / substitute, target)
    with pytest.raises(EvidenceError, match="three_claims_archive_members"):
        regression.replay(copied)
