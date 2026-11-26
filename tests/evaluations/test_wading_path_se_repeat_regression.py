"""Observed Astra X repeatability on a fixed request, with opposite determinate controls."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.ordinary_v61_capture import file_hash
from scripts.wading_path_se_repeat import regression
from scripts.wading_path_sol_versions.evidence_coverage import coverage


@pytest.fixture(scope="module")
def rows() -> dict[str, Any]:
    fixture = json.loads(regression.FIXTURE.read_bytes())
    assert file_hash(regression.FIXTURE) == (
        "16044c7ab4378adca3bfc913936efca35c0571f8c678a3edc2d87c3a3bfe4f18"
    )
    assert fixture["approval_sha256"] == regression.APPROVAL
    assert fixture["archive_sha256"] == regression.ARCHIVE_SHA
    assert fixture["evidence_decisions_sha256"] == regression.READINGS_SHA
    result: dict[str, Any] = fixture["rows"]
    return result


@pytest.mark.parametrize(
    ("cell", "slot", "history", "label", "denial"),
    [
        ("SE-AX-1", 27, "stop", "unsupported", "They never reach the housing during scene four."),
        ("SE-AX-2", 36, "stop", "unsupported", "They never reach it during the scene."),
        ("SE-AX-3", 38, "stop", "uncertain", None),
        ("SE-AX-4", 45, "stop", "unsupported", "neither covers the remaining distance."),
        ("VE-AX-1", 29, "visit", "supported", None),
        ("XE-AX-1", 44, "exclusion", "unsupported", None),
    ],
)
def test_sealed_reading(
    rows: dict[str, Any], cell: str, slot: int, history: str, label: str, denial: str | None
) -> None:
    gold = json.loads(
        regression.FIXTURE.with_name("wading_path_narration_event_gold.json").read_bytes()
    )
    row = rows[cell]
    ending = gold["endings"][history]
    assert row["claim"] == gold["claims"]["reached"]
    assert row["gold"] == ending["cells"]["reached"][0]
    assert (row["draft_version"], row["prose_sha256"]) == (
        ending["version"],
        ending["prose_sha256"],
    )
    assert row["unit"] == "A001" and row["citations"] == ["E1420"]
    assert (row["model"], row["reasoning"]) == ("gpt-6.2-astra", "high")
    assert (row["count"]["slot"], row["generation"]["slot"]) == (slot - 24, slot)
    assert row["count"]["input_tokens"] == row["usage"]["input_tokens"]
    assert row["returned"] == label and row["false_denial_excerpt"] == denial
    assert row["false_scene_wide_denial"] is (denial is not None)
    expected = "fail" if denial else "pass"
    assert tuple(
        row[k] for k in ("judgment", "factual_sufficiency", "diagnostic_completeness")
    ) == (expected, expected, expected)
    assert row["diagnostic_basis"] and row["factual_basis"]
    if history == "stop":
        assert gold["fixed_stop"]["quote"] in row["draft_excerpt"]
        assert (denial or "the closing observation does not rule out an earlier arrival") in row[
            "reason"
        ]
        assertions = {"no_visit"} if denial else {"open_visit"}
        findings = coverage(
            "event", assertions, {"approach", "gap"}, {"account", "approach", "gap"}
        )
        assert findings == (["insufficient_evidence_for_no_visit"] if denial else [])
    else:
        assert ending["append_paragraph"] in row["draft_excerpt"]
        assertion = "visit_occurred" if history == "visit" else "no_visit"
        assert coverage("event", {assertion}, {history}, {history, "approach", "gap"}) == []


def test_repeats_share_input_and_keep_distinct_deliveries(rows: dict[str, Any]) -> None:
    assert set(rows) == {*(f"SE-AX-{i}" for i in range(1, 5)), "XE-AX-1", "VE-AX-1"}
    repeats = [rows[f"SE-AX-{i}"] for i in range(1, 5)]
    for stage in ("count", "generation"):
        assert len({r[stage]["request_sha256"] for r in repeats}) == 1
        assert len({r[stage]["request_sha256"] for r in rows.values()}) == 3
    assert len({r["scoring_id"] for r in rows.values()}) == 6
    assert (
        len({r[s]["terminal_sha256"] for r in rows.values() for s in ("count", "generation")}) == 12
    )


@pytest.fixture
def archive() -> Path:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private six-delivery archive")
    return regression.ARCHIVE


def test_archive_only_replay(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    portable = json.loads(regression.FIXTURE.read_bytes())

    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("network access during regression replay")

    read = Path.read_bytes

    def local(path: Path) -> bytes:
        assert path.is_relative_to(archive)
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", local)
    monkeypatch.setattr(socket, "getaddrinfo", offline)
    monkeypatch.setattr(socket.socket, "connect", offline)
    monkeypatch.setattr(socket.socket, "connect_ex", offline)
    assert regression.replay(archive) == portable


def test_damage_and_repeat_substitution(archive: Path, tmp_path: Path) -> None:
    copy = tmp_path / "archive"
    shutil.copytree(archive, copy)
    capture = copy / "capture"
    for name, replacement in (
        ("output/38-SE-AX-3-generation-outcome.json", "output/36-SE-AX-2-generation-outcome.json"),
        (
            "output/03-SE-AX-1-input_count-outcome.json",
            "output/21-SE-AX-4-input_count-outcome.json",
        ),
        ("requests/XE-AX-1-generation.json", "requests/VE-AX-1-generation.json"),
        ("drafts.json", None),
        ("sealed-evidence-decisions.json", None),
    ):
        path = capture / name
        saved = path.read_bytes()
        path.write_bytes((capture / replacement).read_bytes() if replacement else saved + b" ")
        with pytest.raises(EvidenceError, match="repeat_archive_members"):
            regression.replay(copy)
        path.write_bytes(saved)
    manifest = copy / "capture-manifest.json"
    manifest.write_bytes(manifest.read_bytes() + b" ")
    with pytest.raises(EvidenceError, match="repeat_archive_seal"):
        regression.replay(copy)
