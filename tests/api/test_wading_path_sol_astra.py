"""Offline qualification of the two-by-two diagnostic, single-use dispatch and score gate."""

from __future__ import annotations

import asyncio
import json
import shutil
from itertools import combinations
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import _registry
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, text_hash
from open_hollywood_engine.secrets import SecretValue

from scripts.q010_uncertainty_plan import Cell, digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.wading_path_sol_astra import plan, run, scoring
from scripts.wading_path_sol_versions import regression

Materials = tuple[list[Cell], dict[str, bytes], bytes]


@pytest.fixture(scope="module")
def frozen(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str, Materials]:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the sealed Wading Path comparison archive")
    root = tmp_path_factory.mktemp("sol-astra") / "freeze"
    material = plan.materials()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(plan, "materials", lambda: material)
        sha = plan.issue(root)
    return root, sha, material


def test_pair_parity_sources_and_budget(frozen: tuple[Path, str, Materials]) -> None:
    root, sha, (cells, assets, manifest) = frozen
    p = json.loads(manifest)
    assert digest(manifest) == sha and p["members"] == {k: digest(v) for k, v in assets.items()}
    assert all((root / k).read_bytes() == v for k, v in assets.items())
    assert len(p["slots"]) == 48 and len({c.wire.native_request_sha256 for c in cells}) == 24
    assert [(s["stage"], s["cell"]) for s in p["slots"]] == [
        (stage, k) for stage in ("input_count", "generation") for k in plan.ORDER
    ]
    assert p["budget"]["aggregate_generation_usd"] == "26.45760" and p["budget"]["retries"] == 0
    assert p["budget"]["per_model_generation_usd"] == {"S": "5.29152", "A": "21.16608"}
    for a, b in combinations(plan.ARMS, 2):
        assert sum(g.split().index(a) < g.split().index(b) for g in plan.QUARTETS) == 3
    bodies = {}
    gold = json.loads(assets["gold.json"])
    archive = regression.ARCHIVE / "capture/run"
    assert assets["gold.json"] == (archive / "gold.json").read_bytes()
    assert assets["evidence-criteria.json"] == (archive / "evidence-criteria.json").read_bytes()
    assert {k: v["gold"] for k, v in gold.items()} == {
        "SE": "uncertain",
        "SN": "unsupported",
        "XE": "unsupported",
        "XN": "unsupported",
        "VN": "supported",
        "VE": "supported",
    }
    for c in cells:
        case, arm = c.name.split("-")
        count, gen = c.wire.endpoints
        body = json.loads(gen.body_utf8)
        assert json.loads(count.body_utf8) == {
            k: body[k] for k in ("model", "input", "text", "reasoning")
        }
        assert body["model"] == plan.MODELS[arm[0]] and body["reasoning"]["effort"] == "high"
        assert body["store"] is False and body["max_output_tokens"] == 4096
        assert (count.path, gen.path) == ("/v1/responses/input_tokens", "/v1/responses")
        assert count.destination == gen.destination == "https://api.openai.com"
        row = gold[case]
        ref = next(r for r in _registry(c.work).entries if r.ref == "E1420")
        assert (
            ref.document_version == row["draft_version"]
            and text_hash(ref.quote) == row["prose_sha256"]
        )
        user = json.loads(body["input"][1]["content"])
        assert user["active_unit_ids"] == ["A001"]
        assert user["claim_scope"]["statement"]["quote"] == row["claim"]
        assert all(rule not in body["input"][1]["content"] for rule in row["evidence_requirements"])
        assert user["claim_scope"]["source_scopes"] == [
            dict(coverage="complete_fields", role="draft", evidence_refs=["E1420"])
        ]
        if arm == "SB":
            for end in c.wire.endpoints:
                old = archive / f"requests/{case}-62-{end.stage}.json"
                assert end.body_utf8.encode() == old.read_bytes()
        bodies[c.name] = body
    for case, (_, predicate) in plan.CASES.items():
        for suffix in ("B", "X"):
            sol, astra = (bodies[f"{case}-{m}{suffix}"] for m in ("S", "A"))
            assert astra == sol | {"model": "gpt-6.2-astra"}
        baseline, explicit = (bodies[f"{case}-S{x}"] for x in ("B", "X"))
        assert baseline | {"input": explicit["input"]} == explicit
        assert baseline["input"][0] == explicit["input"][0]
        u, x = (json.loads(b["input"][1]["content"]) for b in (baseline, explicit))
        assert x["claim_scope"].pop("assessment_target") == plan.TARGET[predicate]
        assert u == x


@pytest.mark.parametrize(
    ("fault", "sent", "state"),
    [
        ("none", 48, "bound_unassessed"),
        ("last_count", 24, "count_rejected"),
        ("http_error", 24, "http_error"),
        ("wrong_model", 25, "model_mismatch"),
        ("wrong_astra", 26, "model_mismatch"),
        ("missing_model", 25, "invalid_response"),
        ("wrong_ref", 25, "invalid_claim_or_citation"),
        ("wrong_unit", 25, "invalid_claim_or_citation"),
        ("interrupted", 25, "intent_without_terminal"),
    ],
)
def test_transport(
    frozen: tuple[Path, str, Materials],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fault: str,
    sent: int,
    state: str,
) -> None:
    src, sha, material = frozen
    monkeypatch.setattr(plan, "materials", lambda: material)
    root = tmp_path / "injected"
    shutil.copytree(src, root)
    slots = json.loads(material[2])["slots"]
    stages: list[str] = []

    def reply(req: httpx.Request) -> httpx.Response:
        s = slots[len(stages)]
        stages.append(s["stage"])
        assert req.content == (root / s["filename"]).read_bytes()
        assert str(req.url) == s["destination"] + s["path"]
        assert (
            root / "output" / f"{len(stages):02d}-{s['cell']}-{s['stage']}-intent.json"
        ).exists()
        if s["stage"] == "input_count":
            if fault == "http_error" and len(stages) == 24:
                return httpx.Response(503, json={"error": "fixture"})
            return httpx.Response(
                200,
                json={
                    "input_tokens": 160001 if len(stages) == 24 and fault == "last_count" else 90000
                },
            )
        if fault == "interrupted":
            raise asyncio.CancelledError
        model = s["expected_model"]
        if fault == "wrong_model":
            model = plan.MODELS["A"]
        elif fault == "wrong_astra" and model == plan.MODELS["A"]:
            model = plan.MODELS["S"]
        answer = dict(
            support="uncertain",
            evidence=["E9999" if fault == "wrong_ref" else "E1420"],
            reason="Injected response.",
        )
        msg = json.dumps({"assessments": {"Q011" if fault == "wrong_unit" else "A001": answer}})
        return httpx.Response(
            200,
            json=dict(
                model=None if fault == "missing_model" else model,
                status="completed",
                output=[
                    dict(
                        type="message",
                        role="assistant",
                        status="completed",
                        content=[dict(type="output_text", text=msg)],
                    )
                ],
                usage=dict(input_tokens=90000, output_tokens=20, total_tokens=90020),
            ),
        )

    def execute() -> str:
        return asyncio.run(
            run.dispatch(
                root, sha, httpx.MockTransport(reply), SecretValue("local-synthetic-qualification")
            )
        )

    if fault == "interrupted":
        with pytest.raises(asyncio.CancelledError):
            execute()
    else:
        assert execute() == state
    audit = run.audit(root, sha)
    assert audit["state"] == state and len(audit["slots"]) == 48
    assert stages == (["input_count"] * 24 + ["generation"] * 24)[:sent]
    assert all(r["state"] == "not_attempted" for r in audit["slots"][sent:])
    assert not any(r["eligible"] for r in audit["slots"])
    with pytest.raises(EvidenceError, match="consumed"):
        execute()
    assert len(stages) == sent


@pytest.mark.parametrize(
    ("wrong", "poor", "missing", "decision"),
    [
        ("", "", "", "all_arms_pass_no_differential"),
        ("SE-SB", "SN-SB", "", "mixed_within_scene"),
        ("", "XE-AX", "", "mixed_within_scene"),
        ("", "SE-all", "", "hold"),
        ("", "", "VE-SX", "inconclusive"),
    ],
)
def test_independent_scores_and_gate(
    frozen: tuple[Path, str, Materials], wrong: str, poor: str, missing: str, decision: str
) -> None:
    _, sha, (_, assets, _) = frozen
    gold = json.loads(assets["gold.json"])
    report: Audit = dict(
        approval=sha,
        ledger="dispatched",
        closed=True,
        origin="observed_openai_transport",
        state="fixture_only",
        slots=[],
    )
    decisions = {}
    for name in plan.ORDER:
        case = name.split("-")[0]
        expected = gold[case]["gold"]
        row: dict[str, Any] = dict(
            cell=name,
            stage="generation",
            eligible=name != missing,
            state="not_attempted" if name == missing else "bound_unassessed",
        )
        if name != missing:
            label = (
                ("supported" if expected != "supported" else "uncertain")
                if name == wrong
                else expected
            )
            sid = digest(name.encode())
            row.update(
                scoring_id=sid,
                final={
                    "assessments": {
                        "A001": dict(support=label, evidence=["E1420"], reason="Fixture.")
                    }
                },
            )
            decisions[sid] = dict(
                case=case,
                outcome="fail" if poor in {name, case + "-all"} else "pass",
                basis="Fixture span.",
            )
        report["slots"].append(row)
    sheet = evidence_sheet(report)
    assert all(set(r) == {"scoring_id", "case", "claim_id", "citations", "reason"} for r in sheet)
    form = encoded(
        dict(approval_sha256=sha, sheet_sha256=digest(encoded(sheet)), decisions=decisions)
    )
    out = scoring.scores(report, form, assets["gold.json"])
    assert out["decision"] == decision
    if wrong:
        assert out["paired_axes"]["model_on_B"]["SE"] == {
            "judgment": "gain",
            "evidence": "both_pass",
        }
        assert out["paired_axes"]["scope_on_Sol"]["SN"] == {
            "judgment": "both_pass",
            "evidence": "gain",
        }
    if poor == "XE-AX":
        assert "AX" not in out["qualified_arms"]
        assert not out["arms"]["AX"]["control_joint"]["XE"]
        assert out["paired_axes"]["model_on_X"]["XE"]["evidence"] == "loss"
    if missing:
        assert not out["qualified_arms"] and out["rows"][missing]["evidence"] == "unscored"


def test_freeze_rejects_tampering(
    frozen: tuple[Path, str, Materials], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src, sha, material = frozen
    monkeypatch.setattr(plan, "materials", lambda: material)
    root = tmp_path / "copy"
    shutil.copytree(src, root)
    for member in (
        "requests/SE-SB-input_count.json",
        "requests/SN-AX-generation.json",
        "gold.json",
        "evidence-criteria.json",
        "scoring.json",
    ):
        p = root / member
        raw = p.read_bytes()
        p.write_bytes(raw + b" ")
        with pytest.raises(EvidenceError, match="frozen_member_drift"):
            plan.verify(root, sha)
        p.write_bytes(raw)
    assert run.audit(root, sha)["state"] == "unused"
