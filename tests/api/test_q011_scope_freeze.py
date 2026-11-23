"""Six source-bound cases, two scoring axes and twelve single-use local transport slots."""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretValue

from scripts.q010_uncertainty_plan import MODEL, digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.q011_arrival import scope_rehearsal as rehearsal
from scripts.q011_scope import plan, run, scoring


@pytest.fixture(scope="module")
def issued(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str]:
    if not (rehearsal.ROOT / "scores.json").is_file():
        pytest.skip("requires the private Q011 rehearsal")
    root = tmp_path_factory.mktemp("scope") / "issued"
    return root, plan.issue(root)


def test_exact_work_and_budget(issued: tuple[Path, str]) -> None:
    root, approval = issued
    cells = plan.verify(root, approval)
    manifest = json.loads((root / "plan.json").read_bytes())
    slots = manifest["slots"]
    assert [s["stage"] for s in slots] == ["input_count"] * 6 + ["generation"] * 6
    order = ["AP-B", "AD-B", "RD-B", "RP-B", "SP-B", "SD-B"]
    assert [s["cell"] for s in slots] == order * 2
    scores = rehearsal.replay()["scores"]
    known = {r["case"]: r["work_sha256"] for r in scores}
    gold = (root / "gold.json").read_bytes()
    assert gold == (rehearsal.ROOT / "gold.json").read_bytes() and digest(gold) == rehearsal.GOLD
    witnesses = json.loads((root / "witnesses.json").read_bytes())
    for cell, a, b in zip(cells, slots[:6], slots[6:], strict=True):
        assert cell.work.fingerprint == a["work_sha256"] == b["work_sha256"] == known[a["case"]]
        bodies = []
        for slot in (a, b):
            raw = (root / slot["filename"]).read_bytes()
            assert digest(raw) == slot["body_bytes_sha256"] and len(raw) == slot["http_body_bytes"]
            assert slot["destination"] == "https://api.openai.com" and slot["method"] == "POST"
            bodies.append(json.loads(raw))
        count, gen = bodies
        assert [a["path"], b["path"]] == ["/v1/responses/input_tokens", "/v1/responses"]
        assert count == {k: gen[k] for k in ("input", "model", "reasoning", "text")}
        assert gen["input"] == [m.model_dump(mode="json") for m in cell.work.context.messages]
        assert gen["model"] == MODEL and gen["reasoning"] == {"effort": "high"}
        assert (
            not gen["store"]
            and gen["truncation"] == "disabled"
            and gen["max_output_tokens"] == 4096
        )
        schema = gen["text"]["format"]["schema"]["properties"]["assessments"]
        assert schema["required"] == list(schema["properties"]) == [rehearsal.UNIT]
        user = json.loads(gen["input"][1]["content"])
        assert set(user) == {"active_unit_ids", "claim", "documents", "work_brief"}
        assert user["claim"]["text"] == json.loads(gold)["cases"][a["case"]]["derived_claim"]
        source = dict(json.loads(gold)["cases"][a["case"]])
        source.pop("gold")
        assert witnesses[cell.name.removesuffix("-B")] == source
    assert len({s["body_bytes_sha256"] for s in slots}) == 12
    assert (
        manifest["budget"]["retries"] == 0
        and manifest["budget"]["aggregate_generation_usd"] == "0.49152"
    )
    assert run.audit(root, approval)["state"] == "unused"


def score_as_observed(report: Audit, root: Path, fault: str) -> None:
    # Exercise the scoring join in memory. The original mock journal is always ineligible.
    report["origin"] = "observed_openai_transport"
    for slot in report["slots"]:
        slot["eligible"] = slot["state"] == "bound_unassessed"
    sheet = evidence_sheet(report)
    assert all(set(r) == {"case", "claim_id", "scoring_id", "citations", "reason"} for r in sheet)
    form = dict(
        approval_sha256=report["approval"],
        sheet_sha256=digest(encoded(sheet)),
        decisions={
            r["scoring_id"]: dict(
                case=r["case"],
                outcome="fail" if fault == "mixed" and r["case"] == "AD" else "pass",
                basis="Read the two plan obligations and final placement in the assessed draft.",
            )
            for r in sheet
        },
    )
    gold = (root / "gold.json").read_bytes()
    result = scoring.scores(report, encoded(form), gold)
    grouped = json.loads(encoded(result))
    original = grouped["original_pair"]
    controls = grouped["clear_controls"]
    if fault == "mixed":
        assert [(r["judgment"], r["evidence"]) for r in original["cases"]] == [
            ("fail", "pass"),
            ("pass", "fail"),
        ]
        assert (original["outcome"], controls["outcome"], grouped["decision"]) == (
            "hold",
            "pass",
            "hold",
        )
    elif fault == "last_http":
        assert (
            original["outcome"] == "pass"
            and grouped["decision"] == controls["outcome"] == "inconclusive"
        )
        assert controls["cases"][-1]["judgment"] == controls["cases"][-1]["evidence"] == "unscored"
    else:
        assert grouped["decision"] == "grounded_scope_split"
        assert all(
            r["judgment"] == r["evidence"] == "pass" for r in original["cases"] + controls["cases"]
        )
    with pytest.raises(EvidenceError, match="wrong_worksheet"):
        scoring.scores(report, encoded(form | {"sheet_sha256": "0" * 64}), gold)


@pytest.mark.parametrize(
    ("fault", "attempts", "state"),
    [
        ("grounded", 12, "bound_unassessed"),
        ("mixed", 12, "bound_unassessed"),
        ("sixth_count", 6, "count_rejected"),
        ("duplicate", 1, "invalid_response"),
        ("first_http", 1, "http_error"),
        ("last_http", 12, "http_error"),
        ("missing_usage", 7, "accounting_hold"),
        ("bad_unit", 7, "invalid_claim_or_citation"),
        ("bad_ref", 7, "invalid_claim_or_citation"),
        ("cancel", 7, "intent_without_terminal"),
        ("timeout", 7, "timeout"),
        ("model", 7, "model_mismatch"),
        ("truncated", 7, "length"),
        ("wall_limit", 6, "deadline"),
        ("usage_limit", 7, "accounting_hold"),
        ("refusal", 7, "refusal"),
    ],
)
def test_single_use_dispatch(
    issued: tuple[Path, str],
    tmp_path: Path,
    fault: str,
    attempts: int,
    state: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    src, approval = issued
    root = tmp_path / "copy"
    shutil.copytree(src, root)
    steps = json.loads((root / "plan.json").read_bytes())["slots"]
    fixtures = {
        f["id"]: f["answer"]
        for f in json.loads((rehearsal.ROOT / "authored-fixtures.json").read_bytes())
    }
    sent: list[str] = []
    if fault == "wall_limit":
        monkeypatch.setattr(run, "monotonic", lambda: 0 if len(sent) < 6 else plan.WALL_SECONDS)

    def reply(request: httpx.Request) -> httpx.Response:
        step = steps[len(sent)]
        i = step["slot"]
        assert request.content == (root / step["filename"]).read_bytes()
        assert str(request.url) == step["destination"] + step["path"]
        assert (root / "output" / f"{i:02d}-{step['cell']}-{step['stage']}-intent.json").is_file()
        sent.append(step["stage"])
        if fault == "first_http" or (fault == "last_http" and i == 12):
            return httpx.Response(503, json={"error": {"code": "server_error"}})
        if fault == "duplicate":
            return httpx.Response(200, content=b'{"input_tokens":1,"input_tokens":2}')
        if i <= 6:
            return httpx.Response(
                200, json={"input_tokens": 16385 if i == 6 and fault == "sixth_count" else 8000}
            )
        if fault == "cancel":
            raise asyncio.CancelledError
        if fault == "timeout":
            raise httpx.ReadTimeout("injected")
        fixture = "grounded-" + step["case"]
        if fault == "mixed":
            fixture = {7: "label-only", 8: "word-search"}.get(i, fixture)
        answer = dict(fixtures[fixture])
        if fault == "bad_ref":
            answer["evidence"] = ["unregistered"]
        final = json.dumps(
            {"assessments": {"Q011" if fault == "bad_unit" else rehearsal.UNIT: answer}}
        )
        payload: dict[str, Any] = dict(
            model="wrong" if fault == "model" else MODEL,
            status="completed",
            output=[
                dict(
                    type="message",
                    role="assistant",
                    status="completed",
                    content=[dict(type="output_text", text=final)],
                )
            ],
            usage=dict(input_tokens=8000, output_tokens=80, total_tokens=8080),
        )
        if fault == "missing_usage":
            del payload["usage"]
        if fault == "usage_limit":
            payload["usage"] = dict(input_tokens=8000, output_tokens=4097, total_tokens=12097)
        if fault == "refusal":
            payload["output"][0]["content"] = [dict(type="refusal", refusal="fixture")]
        if fault == "truncated":
            payload.update(status="incomplete", incomplete_details={"reason": "max_output_tokens"})
        return httpx.Response(200, json=payload)

    def execute() -> str:
        return asyncio.run(
            run.dispatch(root, approval, httpx.MockTransport(reply), SecretValue("injected-only"))
        )

    if fault == "cancel":
        with pytest.raises(asyncio.CancelledError):
            execute()
    else:
        assert execute() == state
    report = run.audit(root, approval)
    assert report["state"] == state and report["closed"] == (fault != "cancel")
    assert len(report["slots"]) == 12 and not any(s["eligible"] for s in report["slots"])
    assert all(s["state"] == "not_attempted" for s in report["slots"][attempts:])
    with pytest.raises(EvidenceError, match="consumed"):
        execute()
    assert sent == (["input_count"] * 6 + ["generation"] * 6)[:attempts]
    if fault in ("grounded", "mixed", "last_http"):
        score_as_observed(report, root, fault)


def test_modified_member_rejected(issued: tuple[Path, str], tmp_path: Path) -> None:
    src, approval = issued
    root = tmp_path / "copy"
    shutil.copytree(src, root)
    for member in (
        "gold.json",
        "witnesses.json",
        "scoring.json",
        "requests/AP-B-generation.json",
        "requests/AD-B-input_count.json",
    ):
        path = root / member
        body = path.read_bytes()
        path.write_bytes(body + b" ")
        with pytest.raises(EvidenceError, match="frozen_member_drift"):
            plan.verify(root, approval)
        path.write_bytes(body)
    assert run.audit(root, approval)["ledger"] == "ready"
