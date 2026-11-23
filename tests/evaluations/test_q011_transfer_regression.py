"""Protect the observed pairs and the exact whole-field boundary of the local scope audit."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import NoReturn

import pytest
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.q011_transfer import regression, scope_audit


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("the archive and source-scope audit must remain offline")

    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    monkeypatch.setattr(socket.socket, "connect", refuse)


@pytest.fixture
def archive() -> Path:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private observed transfer archive")
    return regression.ARCHIVE


@pytest.fixture
def audit() -> Path:
    if not scope_audit.ROOT.is_dir():
        pytest.skip("requires the private ordinary-review scope selection")
    return scope_audit.ROOT


def test_archive_alone(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    read = Path.read_bytes

    def archived(path: Path) -> bytes:
        assert path.is_relative_to(archive)
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", archived)
    replay = regression.replay(archive)
    assert replay["slots"] == 32 and replay["members"] == 118 and replay["live_calls"] == 0
    assert replay["decision"] == "cross_family_recovery"
    assert replay["baseline_joint_passes"] == ["T03", "T04", "T05", "T06", "T08"]
    for case, pair in replay["pairs"].items():
        assert pair["arms"]["E"]["judgment"] == pair["arms"]["E"]["evidence"] == "pass"
        baseline = "fail" if case in ("T01", "T02", "T07") else "pass"
        assert pair["arms"]["B"]["judgment"] == pair["arms"]["B"]["evidence"] == baseline
    assert set(replay["unresolved"]) == {"T01", "T02", "T07", "T08"}


@pytest.mark.parametrize(
    ("target", "substitute"),
    [
        (
            "run/output/17-T01-B-generation-outcome.json",
            "run/output/18-T01-E-generation-outcome.json",
        ),
        ("run/packets/T08.json", "run/packets/T06.json"),
        ("run/requests/T07-E-input_count.json", "run/requests/T07-B-input_count.json"),
        ("run/sealed-evidence-decisions.json", None),
        ("operator/scores.json", None),
    ],
)
def test_changed_capture(
    archive: Path, tmp_path: Path, target: str, substitute: str | None
) -> None:
    copy = tmp_path / "copy"
    shutil.copytree(archive, copy)
    path = copy / "capture" / target
    if substitute:
        path.write_bytes((copy / "capture" / substitute).read_bytes())
    else:
        path.unlink()
    with pytest.raises(EvidenceError, match="transfer_regression_(inventory|member)"):
        regression.replay(copy)


def test_selected_claims(audit: Path) -> None:
    result = scope_audit.verify(audit)
    assert (result["reviews"], result["fields"], result["reviews_with_E"]) == (6, 59, ["S01"])
    assert result["live_calls"] == 0
    rows = json.loads((audit / "scope-decisions.json").read_bytes())
    admitted = {path for path, field in rows["S01"]["fields"].items() if field["route"] == "E"}
    assert admitted == {"/native/check/achieved_state", "/native/check/current_endpoint_comparison"}
    assert rows["S01"]["fields"]["/native/check/next_scene_comparison"]["route"] == "B"
    assert rows["S02"]["fields"][rows["S02"]["focus"]]["route"] == "hold"
    # The plan places the three people in the cellar. Its critic's whole summary judges craft.
    assert rows["S04"]["fields"][rows["S04"]["focus"]]["route"] == "hold"


@pytest.mark.parametrize("change", ["version", "clause", "offset", "missing_field"])
def test_rejects_broken_source_binding(audit: Path, change: str) -> None:
    packet = json.loads((audit / "packets/S01.json").read_bytes())
    rows = json.loads((audit / "scope-decisions.json").read_bytes())
    row = rows["S01"]
    if change == "version":
        row["versions"]["draft"] = rows["S02"]["versions"]["draft"]
    elif change == "clause":
        row["fields"][row["focus"]]["text"] = "Elias stands at the threshold."
    elif change == "offset":
        row["witnesses"][-1]["start"] += 1
    else:
        del row["fields"]["/native/check/next_scene_comparison"]
    with pytest.raises(EvidenceError, match="scope_(field_inventory|whole_field|witness)"):
        scope_audit.check_decisions(packet, row)


def test_changed_scope_decision(audit: Path, tmp_path: Path) -> None:
    copy = tmp_path / "scope"
    shutil.copytree(audit, copy)
    path = copy / "scope-decisions.json"
    rows = json.loads(path.read_bytes())
    rows["S04"]["fields"][rows["S04"]["focus"]]["route"] = "E"
    path.write_bytes(encoded(rows))
    with pytest.raises(EvidenceError, match="scope_member"):
        scope_audit.verify(copy)
