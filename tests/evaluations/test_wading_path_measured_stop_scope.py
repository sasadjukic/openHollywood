"""Protect the observed S1 scope error, its five controls and the exact source contrast."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.ordinary_v61_capture import file_hash
from scripts.wading_path_visit_position import regression, stop_scope

OBSERVED = Path(__file__).parents[1] / "fixtures/wading_path_measured_stop_observed.json"


def test_portable_observations() -> None:
    snapshot = json.loads(OBSERVED.read_bytes())
    rows = snapshot["rows"]
    assert snapshot["archive_sha256"] == regression.SEAL
    assert snapshot["evidence_decisions_sha256"] == regression.EVIDENCE_SEAL
    assert {
        k: (r["gold"], r["returned"], r["judgment"], r["evidence"]) for k, r in rows.items()
    } == {
        "S1-B": ("uncertain", "unsupported", "fail", "fail"),
        "X1-B": ("unsupported", "unsupported", "pass", "pass"),
        "S2-B": ("unsupported", "unsupported", "pass", "pass"),
        "X2-B": ("unsupported", "unsupported", "pass", "pass"),
        "A1-B": ("supported", "supported", "pass", "pass"),
        "A2-B": ("supported", "supported", "pass", "pass"),
    }
    assert all(
        r["citations"] == ["E1420"] and r["draft_version"] in r["reason"] for r in rows.values()
    )
    assert len({r["generation_terminal_sha256"] for r in rows.values()}) == 6
    assert (
        "The full sequence shows no earlier arrival followed by retreat" in rows["S1-B"]["reason"]
    )
    assert "do not establish reaching the housing" in rows["S1-B"]["reason"]
    assert "neither had ever been closer" in rows["X1-B"]["reason"]


@pytest.fixture
def archive(monkeypatch: pytest.MonkeyPatch) -> Path:
    def deny(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("network attempted during local replay")

    monkeypatch.setattr(socket, "getaddrinfo", deny)
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket.socket, "connect_ex", deny)
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private six-delivery archive")
    return regression.ARCHIVE


def test_archive_reproduces_portable_rows(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rows = json.loads(OBSERVED.read_bytes())["rows"]
    read = Path.read_bytes

    def from_archive(path: Path) -> bytes:
        assert path.is_relative_to(archive)
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", from_archive)
    replay = regression.replay(archive)
    assert (replay["slots"], replay["live_calls"], replay["decision"]) == (
        12,
        0,
        "hold_claim_scope",
    )
    assert rows.keys() == replay["rows"].keys()
    capture = archive / "capture"
    gold = json.loads((capture / "run/gold.json").read_bytes())
    sheet = json.loads((capture / "operator/evidence-sheet.json").read_bytes())
    explanations = {r["case"]: r for r in sheet["rows"]}
    for cell, observed in rows.items():
        case = cell.split("-")[0]
        scores = replay["rows"][cell]
        (terminal,) = (capture / "run/output").glob(f"*-{cell}-generation-outcome.json")
        assert observed == dict(
            claim=gold[case]["claim"],
            draft_version=gold[case]["draft_version"],
            gold=gold[case]["gold"],
            returned=scores["returned"],
            judgment=scores["judgment"],
            evidence=scores["evidence"],
            citations=explanations[case]["citations"],
            reason=explanations[case]["reason"],
            evidence_basis=scores["basis"],
            generation_terminal_sha256=file_hash(terminal),
        )


def test_temporal_witnesses(archive: Path) -> None:
    audit = stop_scope.audit(archive)
    sources = audit["sources"]
    stop, exclusion, arrival, retreat = (
        sources[k]["passages"] for k in ("stop", "exclusion", "arrival", "retreat")
    )
    assert audit["live_calls"] == 0 and len({s["version"] for s in sources.values()}) == 4
    assert "at some time" in audit["visit_claim"] and "final narrated instant" in audit["cut_claim"]
    assert "interval or instant" in audit["brief"]["temporal_scope"]
    for name in ("opening", "crossing", "entry", "look", "housing"):
        assert stop[name] == exclusion[name] == arrival[name] == retreat[name]
    assert "reached the eastern wall" in stop["entry"]["quote"]
    assert stop["persistent_gap"] == exclusion["persistent_gap"]
    gap = stop["persistent_gap"]
    assert (gap["start"], gap["end"]) == (4806, 4945)
    assert "three full strides short" in gap["quote"] and "stayed there" in gap["quote"]
    assert "exclusion" not in stop
    bound = exclusion["exclusion"]
    assert (bound["start"], bound["end"]) == (4947, 5149)
    assert (
        "From the moment they huddled" in bound["quote"]
        and "had ever been closer" in bound["quote"]
    )
    assert retreat["arrival"] == arrival["arrival"]
    assert "Elias and Maya reached" in retreat["arrival"]["quote"]
    assert retreat["arrival"]["end"] < retreat["retreat"]["start"]
    assert "stepped back three full strides" in retreat["retreat"]["quote"]
    assert audit["historical_retreat_visit"]["returned"] == "supported"
    assert audit["historical_retreat_visit"]["evidence"] == "pass"


@pytest.mark.parametrize(
    ("member", "swap"),
    [
        (
            "run/output/07-S1-B-generation-outcome.json",
            "run/output/11-X1-B-generation-outcome.json",
        ),
        ("run/output/01-S1-B-input_count-outcome.json", None),
        ("run/requests/S1-B-generation.json", "run/requests/X1-B-generation.json"),
        ("source/prior-locations.json", None),
        ("run/gold.json", None),
        ("run/sealed-evidence-decisions.json", None),
    ],
)
def test_reject_damaged_archive(
    archive: Path, tmp_path: Path, member: str, swap: str | None
) -> None:
    copy = tmp_path / "archive"
    shutil.copytree(archive / "capture", copy / "capture")
    shutil.copyfile(archive / "capture-manifest.json", copy / "capture-manifest.json")
    target = copy / "capture" / member
    if swap is None:
        target.unlink()
    else:
        shutil.copyfile(copy / "capture" / swap, target)
    with pytest.raises(EvidenceError, match="visit_position_archive_members"):
        regression.replay(copy)
