"""Check the observed ordinary-review decisions, their source scope and archive integrity."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.wading_path_be import regression


@pytest.fixture
def archive(monkeypatch: pytest.MonkeyPatch) -> Path:
    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("replay attempted a network connection")

    monkeypatch.setattr(socket, "getaddrinfo", offline)
    monkeypatch.setattr(socket.socket, "connect", offline)
    monkeypatch.setattr(socket.socket, "connect_ex", offline)
    if not regression.ARCHIVE.exists():
        pytest.skip("requires the private Wading Path regression archive")
    return regression.ARCHIVE


def test_standalone_observed_pairs(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    read = Path.read_bytes

    def archived(path: Path) -> bytes:
        assert path.is_relative_to(archive)
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", archived)
    result = regression.replay(archive)
    assert (result["slots"], result["members"], result["live_calls"]) == (10, 46, 0)
    assert result["decision"] == "hold" and result["baseline_joint_passes"] == []
    assert result["movement"] == {
        "Q010": {"judgment": "retained_fail", "evidence": "retained_fail"},
        "Q011": {"judgment": "retained_fail", "evidence": "loss"},
    }
    assert {
        name: (r["returned"], r["judgment"], r["evidence"]) for name, r in result["rows"].items()
    } == {
        "Q010-B": ("unsupported", "fail", "fail"),
        "Q010-E": ("unsupported", "fail", "fail"),
        "Q008-B": ("unsupported", "pass", "pass"),
        "Q011-E": ("unsupported", "fail", "fail"),
        "Q011-B": ("unsupported", "fail", "pass"),
    }


def test_scope_and_decisive_language(archive: Path) -> None:
    capture, _ = regression.verified_capture(archive)
    audit = json.loads((capture / "operator/audit.json").read_bytes())
    claims = {
        "Q010-B": ("misstates the depicted endpoint", ["E1420"]),
        "Q010-E": ("conflicts with the depicted staging", ["E1420"]),
        "Q011-E": ("depicts an earlier stopping point", ["E0258", "E0254", "E1420"]),
        "Q011-B": (
            "does not establish the pair's assigned standing position",
            ["E0258", "E0254", "E1420"],
        ),
        "Q008-B": (
            "no onward traversal or arrival there occurs in the account",
            ["E0258", "E1420"],
        ),
    }
    for row in audit["slots"][5:]:
        name = row["cell"]
        unit = name.split("-")[0]
        answer = row["final"]["assessments"][unit]
        phrase, refs = claims[name]
        assert phrase in answer["reason"] and answer["evidence"] == refs
        body = json.loads((capture / f"run/requests/{name}-generation.json").read_bytes())
        assert (
            "Unsupported means a material part is contradicted by supplied evidence."
            in body["input"][0]["content"]
        )
        packet = json.loads(body["input"][1]["content"])
        assert packet["active_unit_ids"] == [unit]
        assert (
            packet["work_brief"]["temporal_scope"]
            == "Scene four through its final narrated instant."
        )
    gold = json.loads((capture / "run/gold.json").read_bytes())
    assert {c["field_id"]: c["label"] for c in gold["claims"]} == {
        "Q010": "uncertain",
        "Q011": "uncertain",
        "Q008": "unsupported",
    }
    w = gold["draft_witnesses"]
    assert "they looked deeper" in w["0067"]["quote"]
    assert "stood the heavy steel housing" in w["0068"]["quote"]
    assert w["0069"]["end"] == 4804


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (
            "run/output/09-Q011-E-generation-outcome.json",
            "run/output/10-Q011-B-generation-outcome.json",
        ),
        ("run/requests/Q010-B-input_count.json", "run/requests/Q010-E-input_count.json"),
        ("run/output/08-Q008-B-generation-outcome.json", None),
        ("source/intake.json", None),
        ("run/gold.json", None),
        ("run/sealed-evidence-decisions.json", None),
        ("operator/scores.json", None),
    ],
)
def test_damaged_copy(archive: Path, tmp_path: Path, path: str, replacement: str | None) -> None:
    copied = tmp_path / "copied"
    shutil.copytree(archive, copied)
    base = copied / "capture"
    if replacement:
        (base / path).write_bytes((base / replacement).read_bytes())
        error = "wading_regression_member"
    else:
        (base / path).unlink()
        error = "wading_regression_inventory"
    with pytest.raises(EvidenceError, match=error):
        regression.replay(copied)
