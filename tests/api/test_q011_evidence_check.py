"""Verify the five paired requests, count gate, single-use journal and independent scoring."""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_compact_presentation import compact
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretValue

from scripts.q010_uncertainty_plan import MODEL, digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.q011_arrival import scope_rehearsal as baseline
from scripts.q011_evidence_check import plan, run, scoring
from scripts.q011_scope import position_rehearsal as pos
from scripts.q011_scope import regression

ORDER = ["AP-B", "AP-E", "RP-E", "RP-B", "SP-B", "SP-E", "GC-E", "GC-B", "GM-B", "GM-E"]


@pytest.fixture(scope="module")
def issued(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str]:
    if not (pos.ROOT / "scores.json").is_file() or not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private five-case Q011 rehearsal and source archive")
    root = tmp_path_factory.mktemp("q011") / "issued"
    return root, plan.issue(root)


def test_pair_isolation(issued: tuple[Path, str]) -> None:
    root, approval = issued
    manifest = json.loads((root / "plan.json").read_bytes())
    cells = plan.verify(root, approval)
    rehearsal = pos.replay()
    known = {r["case"]: r["work_sha256"] for r in rehearsal["authored"]}
    assert [r["case"] for r in rehearsal["saved_depictions"]] == [
        "approach-depiction",
        "arrival-depiction",
        "stop-depiction",
    ]
    assert [s["cell"] for s in manifest["slots"]] == ORDER * 2
    assert [s["stage"] for s in manifest["slots"]] == ["input_count"] * 10 + ["generation"] * 10
    assert manifest["budget"] == dict(
        input_counts=10,
        max_generations=10,
        retries=0,
        input_per_generation=16384,
        output_per_generation=4096,
        aggregate_generation_input=163840,
        aggregate_generation_output=40960,
        max_usd_per_generation="0.08192",
        aggregate_generation_usd="0.81920",
        count_seconds=120,
        generation_seconds=300,
        wall_seconds=4200,
    )
    assert (root / "gold.json").read_bytes() == (pos.ROOT / "gold.json").read_bytes()
    packets = pos.packets()
    normalized = {}
    for cell, count, gen in zip(cells, manifest["slots"][:10], manifest["slots"][10:], strict=True):
        key, arm = cell.name.split("-")
        case = plan.CASES[key]
        for step in (count, gen):
            body = (root / step["filename"]).read_bytes()
            assert digest(body) == step["body_bytes_sha256"]
            assert step["work_sha256"] == cell.work.fingerprint
            assert step["case"] == case and step["destination"] == "https://api.openai.com"
            if arm == "B" and key in {"AP", "RP", "SP"}:
                archived = regression.ARCHIVE / "capture/run" / step["filename"]
                assert archived.read_bytes() == body
        assert (count["path"], gen["path"]) == ("/v1/responses/input_tokens", "/v1/responses")
        if arm == "B":
            assert cell.work.fingerprint == known[case]
        request = json.loads((root / gen["filename"]).read_bytes())
        assert json.loads((root / count["filename"]).read_bytes()) == {
            k: request[k] for k in ("input", "model", "reasoning", "text")
        }
        assert request["reasoning"] == {"effort": "high"} and request["model"] == MODEL
        assert request["max_output_tokens"] == 4096 and request["store"] is False
        payload = json.loads(request["input"][1]["content"])
        assert set(payload) == {"work_brief", "active_unit_ids", "claim", "documents"}
        assert payload["claim"]["text"] == baseline.CLAIMS["position"]
        assert payload["active_unit_ids"] == [baseline.UNIT]
        docs = {d["identity"]: d for d in payload["documents"]}
        packet = packets[case]
        for name, source in packet["context"].items():
            assert (docs[name]["version"], docs[name]["structured_content"]) == (
                source["version"],
                source["content"],
            )
        assert docs["historical-review"]["structured_content"] == packet["historical_review"]
        draft = packet["assessment_draft"]
        assert docs["assessment_draft"]["version"] == draft["version"]
        assert docs["assessment_draft"]["structured_content"] == draft["content"] | {
            "ending_excerpt": draft["content"]["prose"].rsplit("\n\n", 1)[-1]
        }
        if arm == "E":
            brief = payload["work_brief"]
            assert brief["evidence_obligation"].endswith(" " + plan.ADDITION)
            brief["evidence_obligation"] = brief["evidence_obligation"].removesuffix(
                " " + plan.ADDITION
            )
            request["input"][1]["content"] = compact(payload)
        normalized[cell.name] = request
    for key in plan.CASES:
        assert normalized[key + "-B"] == normalized[key + "-E"]
    assert run.audit(root, approval)["state"] == "unused"


def form_for(report: Audit, witnesses: dict[str, Any]) -> dict[str, Any]:
    sheet = evidence_sheet(report)
    assert all(set(r) == {"case", "claim_id", "scoring_id", "reason", "citations"} for r in sheet)
    decisions = {}
    for row in sheet:
        key = str(row["case"])
        w = witnesses[key]
        quote = w["fields"]["D01"]
        end = len(w["fields"]["E0883"])
        decisions[str(row["scoring_id"])] = dict(
            case=key,
            outcome="pass",
            basis="Fixture evidence decision on the located ending.",
            passage=dict(
                ref="D01",
                draft_version=w["draft_version"],
                quote=quote,
                start=end - len(quote),
                end=end,
            ),
            instant="at_cut",
            relation={"RP": "establishes", "SP": "excludes", "GC": "excludes"}.get(
                key, "leaves_open"
            ),
        )
    return dict(
        approval_sha256=report["approval"], sheet_sha256=digest(encoded(sheet)), decisions=decisions
    )


@pytest.mark.parametrize(
    ("fault", "sent", "state"),
    [
        ("complete", 20, "bound_unassessed"),
        ("baseline_recovery", 20, "bound_unassessed"),
        ("count10", 10, "count_rejected"),
        ("cancel", 11, "intent_without_terminal"),
        ("http20", 20, "http_error"),
        ("missing_usage", 11, "accounting_hold"),
        ("bad_citation", 11, "invalid_claim_or_citation"),
        ("refused", 11, "refusal"),
        ("deadline", 10, "deadline"),
    ],
)
def test_dispatch(
    issued: tuple[Path, str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fault: str,
    sent: int,
    state: str,
) -> None:
    src, approval = issued
    root = tmp_path / "fixture"
    shutil.copytree(src, root)
    manifest = json.loads((root / "plan.json").read_bytes())
    fixtures = baseline.pinned(pos.ROOT / "authored-fixtures.json", pos.FIXTURES)
    answers = {f["case"]: f["answer"] for f in fixtures[:5]}
    calls: list[str] = []
    if fault == "deadline":
        monkeypatch.setattr(run, "monotonic", lambda: 0 if len(calls) < 10 else plan.WALL_SECONDS)

    def reply(request: httpx.Request) -> httpx.Response:
        step = manifest["slots"][len(calls)]
        calls.append(step["stage"])
        assert request.content == (root / step["filename"]).read_bytes()
        assert str(request.url) == step["destination"] + step["path"]
        assert (
            root / "output" / f"{len(calls):02d}-{step['cell']}-{step['stage']}-intent.json"
        ).is_file()
        if len(calls) <= 10:
            return httpx.Response(
                200,
                json={"input_tokens": 16385 if fault == "count10" and len(calls) == 10 else 8000},
            )
        if fault == "http20" and len(calls) == 20:
            return httpx.Response(503, json={"error": {"code": "server_error"}})
        if fault == "cancel":
            raise asyncio.CancelledError
        answer = dict(answers[step["case"]])
        if step["cell"] == "AP-B" and fault != "baseline_recovery":
            answer["support"] = "unsupported"  # Valid semantic miss must not stop later slots.
        if fault == "bad_citation":
            answer["evidence"] = ["unknown"]
        content = dict(
            type="output_text", text=json.dumps({"assessments": {baseline.UNIT: answer}})
        )
        if fault == "refused":
            content = dict(type="refusal", refusal="fixture")
        body: dict[str, Any] = dict(
            model=MODEL,
            status="completed",
            output=[dict(type="message", role="assistant", status="completed", content=[content])],
            usage=dict(input_tokens=8000, output_tokens=80, total_tokens=8080),
        )
        if fault == "missing_usage":
            del body["usage"]
        return httpx.Response(200, json=body)

    def dispatch() -> str:
        return asyncio.run(
            run.dispatch(root, approval, httpx.MockTransport(reply), SecretValue("injected-only"))
        )

    if fault == "cancel":
        with pytest.raises(asyncio.CancelledError):
            dispatch()
    else:
        assert dispatch() == state
    report = run.audit(root, approval)
    assert calls == (["input_count"] * 10 + ["generation"] * 10)[:sent]
    assert report["state"] == state and len(report["slots"]) == 20
    assert not any(s["eligible"] for s in report["slots"])
    assert all(s["state"] == "not_attempted" for s in report["slots"][sent:])
    with pytest.raises(EvidenceError, match="consumed"):
        dispatch()
    if fault not in {"complete", "baseline_recovery", "http20"}:
        return
    # Score a synthetic observed view in memory only. The fixture journal stays ineligible.
    report["origin"] = "observed_openai_transport"
    for slot in report["slots"]:
        slot["eligible"] = slot["state"] == "bound_unassessed"
    witnesses = json.loads((root / "witnesses.json").read_bytes())
    gold = (root / "gold.json").read_bytes()
    form = form_for(report, witnesses)
    result = scoring.scores(report, encoded(form), witnesses, gold)
    if fault == "baseline_recovery":
        assert result["decision"] == "genuine_baseline_recovery"
        assert result["genuine_baseline_recovery"] is True
        assert result["pairs"]["approach"]["movement"] == dict(
            judgment="retained_pass", evidence="retained_pass"
        )
        return
    assert result["decision"] == (
        "genuine_paired_recovery" if fault == "complete" else "inconclusive"
    )
    assert result["pairs"]["approach"]["movement"] == {
        "judgment": "gain",
        "evidence": "retained_pass",
    }
    if fault == "http20":
        assert result["pairs"]["gap-before-motion"]["arms"]["E"]["evidence"] == "unscored"
        return
    slots = {s["cell"]: s for s in report["slots"] if s["eligible"]}
    d = form["decisions"][slots["GC-E"]["scoring_id"]]
    d["outcome"] = "fail"
    held = scoring.scores(report, encoded(form), witnesses, gold)
    assert (
        held["decision"] == "hold" and held["pairs"]["gap-at-cut"]["movement"]["evidence"] == "loss"
    )
    d["outcome"] = "pass"
    d["passage"]["draft_version"] = witnesses["GM"]["draft_version"]
    with pytest.raises(EvidenceError, match="wrong_position_span"):
        scoring.checked(report, encoded(form), witnesses)


def test_drift(issued: tuple[Path, str], tmp_path: Path) -> None:
    src, approval = issued
    root = tmp_path / "freeze"
    shutil.copytree(src, root)
    for member in (
        "gold.json",
        "scoring.json",
        "witnesses.json",
        "requests/GM-E-input_count.json",
        "requests/AP-B-generation.json",
    ):
        path = root / member
        raw = path.read_bytes()
        path.write_bytes(raw + b" ")
        with pytest.raises(EvidenceError, match="frozen_member_drift"):
            run.audit(root, approval)
        path.write_bytes(raw)
    with pytest.raises(FileExistsError):
        plan.issue(root)
    assert run.audit(root, approval)["ledger"] == "ready"
