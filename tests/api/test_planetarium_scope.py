"""Offline qualification of the planetarium sources, four arms and single-use comparison."""

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
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, text_hash
from open_hollywood_engine.secrets import SecretValue

from scripts.planetarium_scope import plan, run, scoring
from scripts.planetarium_scope.presentation import version
from scripts.q010_uncertainty_plan import Cell, digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.wading_path_sol_astra.plan import MODELS

Materials = tuple[list[Cell], dict[str, bytes], bytes]


@pytest.fixture(scope="module")
def frozen(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str, Materials]:
    root = tmp_path_factory.mktemp("planetarium") / "freeze"
    material = plan.materials()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(plan, "materials", lambda: material)
        sha = plan.issue(root)
    return root, sha, material


def test_sources_and_gold(frozen: tuple[Path, str, Materials]) -> None:
    _, _, (_, assets, _) = frozen
    source, gold = (json.loads(assets[n]) for n in ("sources.json", "gold.json"))
    assert {c: r["gold"] for c, r in gold.items()} == {
        "ON": "unsupported",
        "OE": "uncertain",
        "DN": "unsupported",
        "DE": "unsupported",
        "PN": "supported",
        "PE": "supported",
    }
    drafts = source["drafts"]
    common = drafts["open"].split("\n\n")
    for history in ("excluded", "confirmed"):
        paragraphs = drafts[history].split("\n\n")
        assert paragraphs[:-2] + paragraphs[-1:] == common
        assert (
            paragraphs[-2]
            == gold["DE" if history == "excluded" else "PE"]["spans"]["retrospective"]["quote"]
        )
    for case, row in gold.items():
        history, kind = plan.CASES[case]
        prose = drafts[history]
        assert row["claim"] == source["claims"][kind]
        assert row["prose_sha256"] == text_hash(prose)
        assert row["draft_version"] == version("draft", text_hash(prose))
        assert row["ref"] == "E1420" and row["unit"] == "A001"
        for span in row["spans"].values():
            assert span["quote"] and span["quote"] == prose[span["start"] : span["end"]]
        assert row["spans"]["closing"]["quote"] == common[-1]


def test_requests_and_counterbalance(frozen: tuple[Path, str, Materials]) -> None:
    root, sha, (cells, assets, manifest) = frozen
    p = json.loads(manifest)
    assert digest(manifest) == sha and len(p["members"]) == 52
    assert p["members"] == {k: digest((root / k).read_bytes()) for k in assets}
    assert [(s["stage"], s["cell"]) for s in p["slots"]] == [
        (stage, name) for stage in ("input_count", "generation") for name in plan.ORDER
    ]
    assert len({c.wire.native_request_sha256 for c in cells}) == 24
    assert p["budget"]["retries"] == 0 and p["budget"]["aggregate_generation_usd"] == "26.45760"
    assert p["budget"]["per_model_generation_usd"] == {"A": "21.16608", "S": "5.29152"}
    for left, right in combinations(plan.ARMS, 2):
        assert (
            sum(
                plan.ORDER.index(f"{case}-{left}") < plan.ORDER.index(f"{case}-{right}")
                for case in plan.CASES
            )
            == 3
        )
    sources, gold = (json.loads(assets[n]) for n in ("sources.json", "gold.json"))
    bodies = {}
    for cell in cells:
        case, arm = cell.name.split("-")
        count, gen = cell.wire.endpoints
        body = json.loads(gen.body_utf8)
        assert json.loads(count.body_utf8) == {
            k: body[k] for k in ("model", "input", "text", "reasoning")
        }
        assert (count.path, gen.path) == ("/v1/responses/input_tokens", "/v1/responses")
        assert count.destination == gen.destination == "https://api.openai.com"
        assert body["model"] == MODELS[arm[0]] and body["reasoning"]["effort"] == "high"
        assert body["store"] is False and body["max_output_tokens"] == 4096
        assert (
            digest(body["input"][0]["content"].encode())
            == "9b95b4fda41557bcc730fa821b7ba96cda2ab711cebd79d011730cd35686549b"
        )
        user = json.loads(body["input"][1]["content"])
        assert (
            digest(encoded(user["work_brief"]))
            == "87bb997fa586d23adf20ae6380d06fd225d75635cd2f18c8cbf8b6eace7e460d"
        )
        assert user["active_unit_ids"] == ["A001"]
        assert user["claim_scope"]["statement"]["quote"] == gold[case]["claim"]
        assert user["claim_scope"]["source_scopes"] == [
            dict(coverage="complete_fields", role="draft", evidence_refs=["E1420"])
        ]
        ctx = user["native_work_view"]["context"]
        assert ctx["writer_dispatch_authorized"] is False
        docs = {d["identity"]: d for d in ctx["documents"]}
        assert set(docs) == {
            "draft",
            "registry",
            "authored-diagnostic-claim",
            "scene_plan",
            "review_request",
            "saved_review",
        }
        assert {k: d["version"] for k, d in docs.items()} == p["source_versions"][case]
        assert docs["draft"]["structured_content"] == {
            "prose": sources["drafts"][gold[case]["history"]]
        }
        for k in ("scene_plan", "review_request", "saved_review"):
            assert docs[k]["structured_content"] == sources[k]
        assert docs["draft"]["version"] == gold[case]["draft_version"]
        assert ["E1420", "draft", "/prose"] in docs["registry"]["whole_field_locations"]
        assert all(
            r["evidence_criterion"] not in body["input"][1]["content"] for r in gold.values()
        )
        assert all(
            paragraph not in body["input"][1]["content"]
            for other in ("DE", "PE")
            if gold[case]["history"] != gold[other]["history"]
            for paragraph in [gold[other]["spans"]["retrospective"]["quote"]]
        )
        bodies[cell.name] = body
    for case, (_, kind) in plan.CASES.items():
        for suffix in ("B", "X"):
            sol, astra = (bodies[f"{case}-{m}{suffix}"] for m in ("S", "A"))
            assert astra == sol | {"model": "gpt-6.2-astra"}
        b, x = (bodies[f"{case}-S{a}"] for a in ("B", "X"))
        assert b | {"input": x["input"]} == x and b["input"][0] == x["input"][0]
        ub, ux = (json.loads(v["input"][1]["content"]) for v in (b, x))
        assert ux["claim_scope"].pop("assessment_target") == p["explicit_scope"][kind]
        assert ub == ux


@pytest.mark.parametrize(
    ("fault", "sent", "state"),
    [
        ("none", 48, "bound_unassessed"),
        ("last_count", 24, "count_rejected"),
        ("http_error", 24, "http_error"),
        ("astra_returned_sol", 25, "model_mismatch"),
        ("sol_returned_astra", 26, "model_mismatch"),
        ("wrong_ref", 25, "invalid_claim_or_citation"),
        ("wrong_claim", 25, "invalid_claim_or_citation"),
        ("over_budget", 25, "accounting_hold"),
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
        slot = slots[len(stages)]
        stages.append(slot["stage"])
        assert req.content == (root / slot["filename"]).read_bytes()
        assert str(req.url) == slot["destination"] + slot["path"]
        assert (
            root / "output" / f"{len(stages):02d}-{slot['cell']}-{slot['stage']}-intent.json"
        ).exists()
        if slot["stage"] == "input_count":
            if fault == "http_error" and len(stages) == 24:
                return httpx.Response(503, json={"error": "injected"})
            return httpx.Response(
                200,
                json={
                    "input_tokens": 160001 if fault == "last_count" and len(stages) == 24 else 6000
                },
            )
        if fault == "interrupted":
            raise asyncio.CancelledError
        model = slot["expected_model"]
        if fault == "astra_returned_sol":
            model = MODELS["S"]
        elif fault == "sol_returned_astra":
            model = MODELS["A"]
        unit = "Q011" if fault == "wrong_claim" else "A001"
        final = {
            "assessments": {
                unit: dict(
                    support="uncertain",
                    evidence=["E9999" if fault == "wrong_ref" else "E1420"],
                    reason="Injected.",
                )
            }
        }
        tokens = 4097 if fault == "over_budget" else 20
        return httpx.Response(
            200,
            json=dict(
                model=model,
                status="completed",
                output=[
                    dict(
                        type="message",
                        role="assistant",
                        status="completed",
                        content=[dict(type="output_text", text=json.dumps(final))],
                    )
                ],
                usage=dict(input_tokens=6000, output_tokens=tokens, total_tokens=6000 + tokens),
            ),
        )

    def execute() -> str:
        return asyncio.run(
            run.dispatch(root, sha, httpx.MockTransport(reply), SecretValue("offline-fixture"))
        )

    if fault == "interrupted":
        with pytest.raises(asyncio.CancelledError):
            execute()
    else:
        assert execute() == state
    audit = run.audit(root, sha)
    assert audit["state"] == state and stages == (["input_count"] * 24 + ["generation"] * 24)[:sent]
    assert all(r["state"] == "not_attempted" for r in audit["slots"][sent:])
    assert not any(r["eligible"] for r in audit["slots"])
    with pytest.raises(EvidenceError, match="consumed"):
        execute()
    assert len(stages) == sent


@pytest.mark.parametrize(
    ("shared", "lose_control", "missing", "decision"),
    [
        ("", False, "", "astra_explicit_only_transfer"),
        ("SB", False, "", "shared_open_event_recovery"),
        ("SX", False, "", "shared_open_event_recovery"),
        ("AB", False, "", "shared_open_event_recovery"),
        ("", True, "", "hold_astra_scope"),
        ("", False, "DN-AB", "inconclusive"),
    ],
)
def test_rehearsal_and_scoring(
    frozen: tuple[Path, str, Materials],
    shared: str,
    lose_control: bool,
    missing: str,
    decision: str,
) -> None:
    _, sha, (_, assets, _) = frozen
    gold = json.loads(assets["gold.json"])
    # Authored answers with independently supplied evidence decisions, never model output.
    adequate = (
        "The slide is on the console. The middle pages pass without a cue-by-cue account. "
        "The dome is blank from the closing cue onward, leaving an earlier projection open."
    )
    from_end = (
        "The dome is blank when the house lights come up, so the comet never appeared in rehearsal."
    )
    from_plan = "The comet is on the cue sheet and the slide is ready, so it must have appeared."
    open_answers = {
        "AX": ("uncertain", adequate, True),
        "SB": ("unsupported", from_end, False),
        "AB": ("supported", from_plan, False),
        "SX": ("unsupported", adequate, True),
    }
    if shared:
        open_answers[shared] = open_answers["AX"]
    report: Audit = dict(
        approval=sha,
        ledger="dispatched",
        closed=True,
        origin="observed_openai_transport",
        state="synthetic_score_fixture",
        slots=[],
    )
    decisions = {}
    for name in plan.ORDER:
        case, arm = name.split("-")
        label, reason, passes = (
            open_answers[arm]
            if case == "OE"
            else (gold[case]["gold"], "Grounded control fixture.", True)
        )
        if name == "DE-AX" and lose_control:
            reason, passes = from_end, False
        row: dict[str, Any] = dict(
            cell=name,
            stage="generation",
            eligible=name != missing,
            state="not_attempted" if name == missing else "bound_unassessed",
        )
        if name != missing:
            sid = digest(name.encode())
            row.update(
                scoring_id=sid,
                final={
                    "assessments": {"A001": dict(support=label, reason=reason, evidence=["E1420"])}
                },
            )
            decisions[sid] = dict(
                case=case,
                outcome="pass" if passes else "fail",
                basis=gold[case]["evidence_criterion"],
            )
        report["slots"].append(row)
    sheet = evidence_sheet(report)
    assert all(set(r) == {"scoring_id", "case", "claim_id", "citations", "reason"} for r in sheet)
    form = encoded(
        dict(approval_sha256=sha, sheet_sha256=digest(encoded(sheet)), decisions=decisions)
    )
    result = scoring.scores(report, form, assets["gold.json"])
    assert result["decision"] == decision
    assert result["sol_B_open_recovery"] == (shared == "SB")
    assert (
        all(len(v) == 6 for v in result["paired_axes"].values()) and len(result["paired_axes"]) == 4
    )
    for arm, (label, _, passes) in open_answers.items():
        row = result["rows"]["OE-" + arm]
        assert (row["judgment"] == "pass", row["evidence"] == "pass") == (
            label == "uncertain",
            passes,
        )
    if lose_control:
        assert (
            result["rows"]["DE-AX"]["judgment"] == "pass"
            and result["rows"]["DE-AX"]["evidence"] == "fail"
        )
    if missing:
        assert result["rows"][missing]["judgment"] == "unscored" and not result["qualified_arms"]


def test_tamper_and_unused(
    frozen: tuple[Path, str, Materials], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src, sha, material = frozen
    monkeypatch.setattr(plan, "materials", lambda: material)
    root = tmp_path / "copy"
    shutil.copytree(src, root)
    for member in (
        "requests/OE-AX-input_count.json",
        "requests/DE-SB-generation.json",
        "gold.json",
        "sources.json",
        "scoring.json",
    ):
        p = root / member
        raw = p.read_bytes()
        p.write_bytes(raw + b" ")
        with pytest.raises(EvidenceError, match="frozen_member_drift"):
            plan.verify(root, sha)
        p.write_bytes(raw)
    audit = run.audit(root, sha)
    assert audit["state"] == "unused" and len(audit["slots"]) == 48
    assert all(s["state"] == "not_attempted" for s in audit["slots"])
