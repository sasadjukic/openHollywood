"""Pin each observed judgment and evidence score to its original Q011 subject and draft."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.q011_scope import regression


@pytest.fixture
def archive(monkeypatch: pytest.MonkeyPatch) -> Path:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private Q011 scope captures")

    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("regression replay must be offline")

    monkeypatch.setattr(socket, "getaddrinfo", offline)
    monkeypatch.setattr(socket.socket, "connect", offline)
    monkeypatch.setattr(socket.socket, "connect_ex", offline)
    return regression.ARCHIVE


def test_observed_scores(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    read = Path.read_bytes

    def archived_only(path: Path) -> bytes:
        assert path.is_relative_to(archive)
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", archived_only)
    result = regression.replay(archive)
    assert (result["slots"], result["live_calls"], result["decision"]) == (12, 0, "hold")
    assert result["original_pair"]["outcome"] == "hold"
    assert result["clear_controls"]["outcome"] == "pass"
    rows = result["original_pair"]["cases"] + result["clear_controls"]["cases"]
    assert [
        (r["case"], r["expected"], r["returned"], r["judgment"], r["evidence"]) for r in rows
    ] == [
        ("approach-position", "uncertain", "unsupported", "fail", "fail"),
        ("approach-depiction", "unsupported", "unsupported", "pass", "pass"),
        ("arrival-depiction", "supported", "supported", "pass", "pass"),
        ("arrival-position", "supported", "supported", "pass", "pass"),
        ("stop-position", "unsupported", "unsupported", "pass", "pass"),
        ("stop-depiction", "unsupported", "unsupported", "pass", "pass"),
    ]


def test_source_instant_and_landmark(archive: Path) -> None:
    capture = archive / "capture"
    witnesses = json.loads((capture / "run/witnesses.json").read_bytes())
    readback = json.loads((capture / "operator/audit.json").read_bytes())
    texts = {}
    for name, keys in (
        ("approach", ("AP", "AD")),
        ("arrival", ("RD", "RP")),
        ("stop", ("SP", "SD")),
    ):
        draft = json.loads((capture / f"source/{name}.json").read_bytes())["assessment_draft"]
        prose = draft["content"]["prose"]
        texts[name] = prose
        for key in keys:
            w = witnesses[key]
            assert draft["version"] == w["draft_version"]
            start, end = w["paragraph_span"]
            assert (
                end == len(prose)
                and prose[start:end] == w["paragraph"] == prose.rsplit("\n\n", 1)[-1]
            )
            (delivery,) = [
                r for r in readback["slots"] if r["cell"] == key + "-B" and r["eligible"]
            ]
            assert delivery["final"]["assessments"]["Q011-scope"]["evidence"] == [
                "E0233",
                "E0229",
                "E0883",
                "D01",
            ]
    genuine = texts["approach"]
    assert genuine[1470:1484] == "Elias stopped." and genuine[1595:1613] == "He stepped forward"
    assert genuine[3129:3164] == "He stepped past the circle of shoes"
    assert genuine[3169:3206] == "moved toward the dark, open threshold" and len(genuine) == 3284
    assert texts["arrival"] == genuine + " Elias stood at the threshold."
    assert (
        texts["stop"]
        == genuine
        + " He came to a standstill a full stride short of the sill, both feet planted in the dirt."
    )


@pytest.mark.parametrize(
    ("member", "substitute"),
    [
        (
            "run/output/07-AP-B-generation-outcome.json",
            "run/output/08-AD-B-generation-outcome.json",
        ),
        (
            "run/output/11-SP-B-generation-outcome.json",
            "run/output/12-SD-B-generation-outcome.json",
        ),
        ("source/stop.json", "source/arrival.json"),
        ("run/requests/RD-B-generation.json", "run/requests/RP-B-generation.json"),
        ("run/sealed-evidence-decisions.json", None),
        ("run/gold.json", None),
        ("operator/scores.json", None),
    ],
)
def test_rejects_mixed_or_incomplete_regressions(
    archive: Path, tmp_path: Path, member: str, substitute: str | None
) -> None:
    root = tmp_path / "copy"
    shutil.copytree(archive / "capture", root / "capture")
    shutil.copyfile(archive / "capture-manifest.json", root / "capture-manifest.json")
    target = root / "capture" / member
    if substitute:
        target.write_bytes((root / "capture" / substitute).read_bytes())
    else:
        target.unlink()
    with pytest.raises(EvidenceError, match="q011_scope_regression_(member|inventory)"):
        regression.replay(root)
