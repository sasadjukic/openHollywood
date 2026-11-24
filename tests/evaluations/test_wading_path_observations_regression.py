"""Observed Q011 spatial and evidence-to-label failures, plus the Q008 depiction control."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.wading_path_observations import regression


@pytest.fixture
def archive(monkeypatch: pytest.MonkeyPatch) -> Path:
    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("regression replay attempted network access")

    monkeypatch.setattr(socket, "getaddrinfo", offline)
    monkeypatch.setattr(socket.socket, "connect", offline)
    monkeypatch.setattr(socket.socket, "connect_ex", offline)
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private Wading Path observation archive")
    return regression.ARCHIVE


def test_all_seven_observed_decisions(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    read = Path.read_bytes

    def private_only(p: Path) -> bytes:
        assert p.is_relative_to(archive)
        return read(p)

    monkeypatch.setattr(Path, "read_bytes", private_only)
    actual = regression.replay(archive)
    assert (actual["slots"], actual["live_calls"], actual["decision"]) == (14, 0, "hold_controls")
    assert actual["original_baseline_recovery"] is False
    assert {
        k: (r["returned"], r["judgment"], r["evidence"]) for k, r in actual["rows"].items()
    } == {
        "K1-B": ("unsupported", "fail", "fail"),
        "K1-O": ("unsupported", "fail", "pass"),
        "K2-B": ("supported", "pass", "pass"),
        "K2-O": ("supported", "pass", "pass"),
        "K3-B": ("unsupported", "pass", "fail"),
        "K3-O": ("unsupported", "pass", "fail"),
        "Q008-B": ("unsupported", "pass", "pass"),
    }
    assert actual["movement"] == {
        "K1": {"judgment": "retained_fail", "evidence": "gain"},
        "K2": {"judgment": "retained_pass", "evidence": "retained_pass"},
        "K3": {"judgment": "retained_pass", "evidence": "retained_fail"},
    }


def test_spatial_obligation_and_observed_interpretations(archive: Path) -> None:
    capture = regression.verified(archive)
    frozen = capture / "run"
    obs = json.loads((frozen / "observations.json").read_bytes())
    gold = json.loads((frozen / "gold.json").read_bytes())
    audit = json.loads((capture / "operator/audit.json").read_bytes())
    answers = {
        s["cell"]: next(iter(s["final"]["assessments"].values())) for s in audit["slots"][7:]
    }
    assert "establishes standing before the final barrier" in answers["K3-B"]["reason"]
    assert "requires no specified distance or contact" in answers["K3-O"]["reason"]
    assert "no subsequent movement brings them to it" in answers["K1-B"]["reason"]
    assert "ahead of their last narrated position" in answers["K1-O"]["reason"]
    assert "Through the final line" in answers["Q008-B"]["reason"]
    for case in ("K1", "K2", "K3"):
        for arm in ("B", "O"):
            name = case + "-" + arm
            assert answers[name]["evidence"] == ["E0258", "E0254", "E1420"]
            assert gold[case]["draft_version"] in answers[name]["reason"]
        assert all(q["draft_version"] == gold[case]["draft_version"] for q in obs[case])
    assert "three full strides short" in obs["K3"][-1]["quote"]
    assert "and stayed there." in obs["K3"][-1]["quote"]
    assert "stood side by side before it." in obs["K2"][-1]["quote"]
    assert [q["quote"] for q in obs["K1"]] == [q["quote"] for q in obs["K3"][:-1]]
    packet = json.loads((frozen / "requests/K1-B-generation.json").read_bytes())
    assert "Unsupported means a material part is contradicted" in packet["input"][0]["content"]
    user = json.loads(packet["input"][1]["content"])
    scope = user["claim_scope"]
    assert (
        scope["unresolved_qualifiers"] == [] and scope["observation_basis"] == "positive_depiction"
    )
    docs = user["native_work_view"]["context"]["documents"]
    visible = next(d["structured_content"] for d in docs if d["identity"] == "visible-request")
    contract = visible["scene_assignment_contract"]
    assert contract["outcome"] == "They reach the breaker panel housing."
    assert contract["exit_state"] == "They are standing before the final barrier."
    due = {r["id"]: r for r in visible["critic_requirement_scope"]["due_now"]}
    assert due["scene_plan_outcome"]["enforcement"] == "blocking"
    assert due["scene_plan_exit_state"]["enforcement"] == "advisory"


def test_historical_baseline_repeat_and_narration_control(archive: Path) -> None:
    capture = regression.verified(archive)
    previous = json.loads((capture / "source/previous-plan.json").read_bytes())
    old = json.loads((capture / "source/previous-scores.json").read_bytes())["rows"]
    manifest = json.loads((capture / "run/plan.json").read_bytes())
    bodies = {(s["cell"], s["stage"]): s["body_bytes_sha256"] for s in previous["slots"]}
    for slot in manifest["slots"]:
        if slot["cell"] in ("K1-B", "Q008-B"):
            orig = "Q011-B" if slot["cell"] == "K1-B" else "Q008-B"
            assert slot["body_bytes_sha256"] == bodies[orig, slot["stage"]]
    assert (old["Q011-B"]["judgment"], old["Q011-B"]["evidence"]) == ("fail", "pass")
    assert (old["Q008-B"]["judgment"], old["Q008-B"]["evidence"]) == ("pass", "pass")


@pytest.mark.parametrize(
    ("member", "replacement"),
    [
        (
            "run/output/10-K3-B-generation-outcome.json",
            "run/output/14-K3-O-generation-outcome.json",
        ),
        ("run/requests/K1-O-generation.json", "run/requests/K1-B-generation.json"),
        ("run/output/11-Q008-B-generation-outcome.json", None),
        ("run/output/07-K3-O-input_count-outcome.json", None),
        ("run/gold.json", None),
        ("run/sealed-evidence-decisions.json", None),
        ("operator/cited-locations.json", None),
        ("source/intake.json", None),
    ],
)
def test_damaged_archive(
    archive: Path, tmp_path: Path, member: str, replacement: str | None
) -> None:
    copied = tmp_path / "archive"
    shutil.copytree(archive / "capture", copied / "capture")
    shutil.copyfile(archive / "capture-manifest.json", copied / "capture-manifest.json")
    path = copied / "capture" / member
    if replacement:
        shutil.copyfile(copied / "capture" / replacement, path)
    else:
        path.unlink()
    with pytest.raises(EvidenceError, match="observation_archive_members"):
        regression.replay(copied)
