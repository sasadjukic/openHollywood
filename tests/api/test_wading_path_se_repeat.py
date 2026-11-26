"""Local wire, journal, masking and advancement checks for the single-family SE repeat."""

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
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretValue

from scripts.q010_uncertainty_plan import Cell, digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.wading_path_se_repeat import plan, run, scoring
from scripts.wading_path_sol_astra import regression

Materials = tuple[list[Cell], dict[str, bytes], bytes]
Freeze = tuple[Path, str, Materials]


@pytest.fixture(scope="module")
def frozen(tmp_path_factory: pytest.TempPathFactory) -> Freeze:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the sealed November 25 Sol/Astra capture")
    root = tmp_path_factory.mktemp("se-repeat") / "freeze"
    material = plan.materials()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(plan, "materials", lambda: material)
        sha = plan.issue(root)
    return root, sha, material


def test_wire_identity_balance_and_gold(frozen: Freeze) -> None:
    root, sha, (_, assets, manifest) = frozen
    p = json.loads(manifest)
    assert digest(manifest) == sha and p["members"] == {k: digest(v) for k, v in assets.items()}
    assert [(s["stage"], s["cell"]) for s in p["slots"]] == [
        (stage, name) for stage in ("input_count", "generation") for name in plan.ORDER
    ]
    assert len(plan.ORDER) == len(set(plan.ORDER)) == 24
    archive = regression.ARCHIVE / "capture/run"
    key = json.loads(assets["gold.json"])
    refs = json.loads(assets["drafts.json"])
    assert {k: v["gold"] for k, v in key.items()} == {
        "SE": "uncertain",
        "XE": "unsupported",
        "VE": "supported",
    }
    bodies: dict[tuple[str, str], dict[str, Any]] = {}
    for s in p["slots"]:
        case, arm, _ = s["cell"].split("-")
        path = f"requests/{case}-{arm}-{s['stage']}.json"
        assert s["archived_filename"] == path
        raw = (root / s["filename"]).read_bytes()
        assert raw == (archive / path).read_bytes() and digest(raw) == s["body_bytes_sha256"]
        b = json.loads(raw)
        assert b["model"] == p["models"][arm[0]] and b["reasoning"]["effort"] == "high"
        assert refs[case]["document_version"] == key[case]["draft_version"]
        assert digest(refs[case]["quote"].encode()) == key[case]["prose_sha256"]
        u = json.loads(b["input"][1]["content"])
        assert u["claim_scope"]["statement"]["quote"] == key[case]["claim"]
        assert u["active_unit_ids"] == ["A001"]
        assert u["claim_scope"].get("assessment_target") == (
            None if arm[1] == "B" else p["explicit_event_scope"]
        )
        documents = u["native_work_view"]["context"]["documents"]
        assert documents[1]["structured_content"]["prose"] == refs[case]["quote"]
        assert s["destination"] == "https://api.openai.com"
        if s["stage"] == "generation":
            assert s["path"] == "/v1/responses" and b["max_output_tokens"] == 4096
            assert b["store"] is False
            assert bodies[(s["cell"], "input_count")] == {
                k: b[k] for k in ("model", "input", "text", "reasoning")
            }
        else:
            assert s["path"] == "/v1/responses/input_tokens"
        bodies[(s["cell"], s["stage"])] = b
    assert len({s["body_bytes_sha256"] for s in p["slots"]}) == 24
    groups = [g.split() for case, _, g in plan.BLOCKS if case == "SE"]
    for a in plan.ARMS:
        assert sorted(g.index(a) for g in groups) == list(range(4))
    for a, b in combinations(plan.ARMS, 2):
        assert sum(g.index(a) < g.index(b) for g in groups) == 2
        assert sum(g.split().index(a) < g.split().index(b) for _, _, g in plan.BLOCKS) == 3
    assert p["budget"]["input_counts"] == p["budget"]["max_generations"] == 24
    assert p["budget"]["aggregate_generation_usd"] == "26.45760" and p["budget"]["retries"] == 0


@pytest.mark.parametrize(
    ("fault", "sent", "expected"),
    [
        ("none", 48, "bound_unassessed"),
        ("last_count", 24, "count_rejected"),
        ("wrong_model", 25, "model_mismatch"),
        ("interrupted", 25, "intent_without_terminal"),
    ],
)
def test_transport(
    frozen: Freeze,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fault: str,
    sent: int,
    expected: str,
) -> None:
    original, sha, material = frozen
    monkeypatch.setattr(plan, "materials", lambda: material)
    root = tmp_path / "mock"
    shutil.copytree(original, root)
    slots = json.loads(material[2])["slots"]
    attempts: list[str] = []

    def respond(req: httpx.Request) -> httpx.Response:
        s = slots[len(attempts)]
        attempts.append(s["stage"])
        assert req.content == (root / s["filename"]).read_bytes()
        assert str(req.url) == s["destination"] + s["path"]
        assert (
            root / "output" / f"{len(attempts):02d}-{s['cell']}-{s['stage']}-intent.json"
        ).is_file()
        if s["stage"] == "input_count":
            n = 160001 if fault == "last_count" and len(attempts) == 24 else 90000
            return httpx.Response(200, json={"input_tokens": n})
        if fault == "interrupted":
            raise asyncio.CancelledError
        answer = {"support": "unsupported", "reason": "Identical fixture.", "evidence": ["E1420"]}
        msg = json.dumps({"assessments": {"A001": answer}})
        return httpx.Response(
            200,
            json=dict(
                model="gpt-6.2-astra" if fault == "wrong_model" else s["expected_model"],
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
                root, sha, httpx.MockTransport(respond), SecretValue("local-only-mock-key")
            )
        )

    if fault == "interrupted":
        with pytest.raises(asyncio.CancelledError):
            execute()
    else:
        assert execute() == expected
    audit = run.audit(root, sha)
    assert attempts == (["input_count"] * 24 + ["generation"] * 24)[:sent]
    assert audit["state"] == expected and len(audit["slots"]) == 48
    assert all(r["state"] == "not_attempted" for r in audit["slots"][sent:])
    assert not any(r["eligible"] for r in audit["slots"])
    if fault == "none":
        assert len({r["scoring_id"] for r in audit["slots"][24:]}) == 24
    with pytest.raises(EvidenceError, match="consumed"):
        execute()
    assert len(attempts) == sent


@pytest.mark.parametrize(
    ("candidate", "nearest", "fault", "decision"),
    [
        (3, 1, "", "consider_held_out_family"),
        (4, 2, "", "consider_held_out_family"),
        (2, 0, "", "hold"),
        (3, 2, "", "hold"),
        (4, 0, "control", "hold"),
        (3, 1, "missing", "inconclusive"),
        (3, 1, "target_diagnostic", "consider_held_out_family"),
    ],
)
def test_mask_scores_denials_and_gate(
    frozen: Freeze, candidate: int, nearest: int, fault: str, decision: str
) -> None:
    _, sha, (_, assets, _) = frozen
    key = json.loads(assets["gold.json"])
    report: Audit = dict(
        approval=sha,
        ledger="dispatched",
        closed=True,
        origin="observed_openai_transport",
        state="test_only",
        slots=[],
    )
    grades = {}
    for name in plan.ORDER:
        case, arm, rep = name.split("-")
        eligible = not (fault == "missing" and name == "VE-SB-1")
        row: dict[str, Any] = dict(
            cell=name,
            stage="generation",
            eligible=eligible,
            state="bound_unassessed" if eligible else "not_attempted",
        )
        if eligible:
            sid = digest(name.encode())
            good = case != "SE" or int(rep) <= (candidate if arm == "AX" else nearest)
            label = key[case]["gold"] if good or arm == "SB" else "unsupported"
            reason = "Source-bound explanation." if good or arm == "SX" else "They never visited."
            factual = good or arm == "SX"
            diagnostic = factual and not (
                fault == "control"
                and name == "XE-AX-1"
                or fault == "target_diagnostic"
                and case == "SE"
                and arm == "AX"
            )
            row.update(
                scoring_id=sid,
                final={
                    "assessments": {"A001": dict(support=label, evidence=["E1420"], reason=reason)}
                },
            )
            grades[sid] = dict(
                case=case,
                reason_excerpt=reason,
                draft_excerpt="three full strides",
                factual_basis="Synthetic grade.",
                diagnostic_basis="Synthetic locator.",
                factual_sufficiency="pass" if factual else "fail",
                diagnostic_completeness="pass" if diagnostic else "fail",
                false_denial_excerpt=None if factual else reason,
            )
        report["slots"].append(row)
    sheet = evidence_sheet(report)
    assert all(set(r) == {"scoring_id", "case", "claim_id", "citations", "reason"} for r in sheet)
    payload = dict(approval_sha256=sha, sheet_sha256=digest(encoded(sheet)), decisions=grades)
    result = scoring.scores(report, encoded(payload), assets["drafts.json"], assets["gold.json"])
    assert result["decision"] == decision
    assert result["arms"]["AX"]["hard_grounded"] == candidate
    assert result["arms"]["SB"]["hard_false_denials"] == 4 - nearest
    assert result["arms"]["SX"]["hard_false_denials"] == 0
    assert result["arms"]["SX"]["hard_axis_passes"]["factual_sufficiency"] == 4
    if fault == "missing":
        assert result["rows"]["VE-SB-1"]["false_scene_wide_denial"] is None
    if fault == "target_diagnostic":
        assert result["arms"]["AX"]["hard_axis_passes"]["diagnostic_completeness"] == 0
    grades.pop(next(iter(grades)))
    with pytest.raises(EvidenceError, match="decision_ids"):
        scoring.checked(report, encoded(payload), assets["drafts.json"])


def test_freeze_rejects_drift(
    frozen: Freeze, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    original, sha, material = frozen
    monkeypatch.setattr(plan, "materials", lambda: material)
    root = tmp_path / "changed"
    shutil.copytree(original, root)
    assert run.audit(root, sha)["state"] == "unused"
    for name in ("requests/SE-SB-4-generation.json", "gold.json", "scoring.json", "drafts.json"):
        path = root / name
        raw = path.read_bytes()
        path.write_bytes(raw + b" ")
        with pytest.raises(EvidenceError, match="frozen_member_drift"):
            plan.verify(root, sha)
        path.write_bytes(raw)
