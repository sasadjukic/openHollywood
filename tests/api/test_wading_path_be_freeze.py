"""Verify the fixed Wading Path wires, injected dispatch stops and two-axis scoring."""

from __future__ import annotations

import asyncio
import json
import re
import shutil
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_compact_presentation import SYSTEM, compact
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretValue

from scripts.q010_uncertainty_plan import MODEL, Cell, digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.q011_transfer import wading_path_selection as selection
from scripts.wading_path_be import plan, run, scoring

ORDER = ["Q010-B", "Q010-E", "Q008-B", "Q011-E", "Q011-B"]
Materials = tuple[list[Cell], dict[str, bytes], bytes]


@pytest.fixture(scope="module")
def issued(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str, Materials]:
    if not selection.DATABASE.exists():
        pytest.skip("requires the private Wading Path archive")
    root = tmp_path_factory.mktemp("wading") / "frozen"
    sha = plan.issue(root)
    rebuilt = plan.materials()
    assert sha == digest(rebuilt[2])
    return root, sha, rebuilt


@pytest.fixture
def fixture_run(
    issued: tuple[Path, str, Materials], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, str]:
    src, sha, materials = issued
    # The clean rebuild above is shared. Every simulated dispatch still verifies every disk byte.
    monkeypatch.setattr(plan, "materials", lambda: materials)
    root = tmp_path / "fixture"
    shutil.copytree(src, root)
    return root, sha


def test_frozen_wires(issued: tuple[Path, str, Materials]) -> None:
    root, sha, (cells, assets, manifest) = issued
    m = json.loads(manifest)
    assert sha == digest((root / "plan.json").read_bytes())
    assert all((root / k).read_bytes() == raw for k, raw in assets.items())
    assert [c.name for c in cells] == m["ordered_cells"] == ORDER
    assert [s["cell"] for s in m["slots"]] == ORDER * 2
    assert [s["stage"] for s in m["slots"]] == ["input_count"] * 5 + ["generation"] * 5
    assert m["budget"] == dict(
        input_counts=5,
        max_generations=5,
        retries=0,
        input_per_generation=160000,
        output_per_generation=4096,
        aggregate_generation_input=800000,
        aggregate_generation_output=20480,
        max_usd_per_generation="0.44096",
        aggregate_generation_usd="2.20480",
        count_seconds=120,
        generation_seconds=300,
        wall_seconds=2100,
    )
    assert assets["gold.json"] == selection.GOLD.read_bytes()
    gold = json.loads(assets["gold.json"])
    assert set(m["source_version_ids"]) == {
        gold["binding"]["critique"],
        *(v["version"] for v in gold["binding"]["inputs"].values()),
    }
    rows = json.loads(assets["selections.json"])
    normalized = {}
    for i, (cell, r) in enumerate(zip(cells, rows, strict=True)):
        count, gen = (m["slots"][i + offset] for offset in (0, 5))
        for s in (count, gen):
            raw = assets[s["filename"]]
            assert digest(raw) == s["body_bytes_sha256"] and len(raw) == s["http_body_bytes"]
            assert s["destination"] == "https://api.openai.com"
        assert (count["path"], gen["path"]) == ("/v1/responses/input_tokens", "/v1/responses")
        c, g = (json.loads(assets[s["filename"]]) for s in (count, gen))
        assert c == {k: g[k] for k in ("model", "input", "text", "reasoning")}
        assert g["model"] == MODEL and g["reasoning"] == {"effort": "high"}
        assert g["store"] is False and g["max_output_tokens"] == 4096
        assert g["input"][0] == {"role": "system", "content": SYSTEM}
        user = json.loads(g["input"][1]["content"])
        unit, arm = cell.name.split("-")
        assert user["active_unit_ids"] == [unit] and user["work_brief"] == r["brief"]
        assert user["claim_scope"] == r["declaration"] and cell.work.fingerprint == r["work_sha256"]
        assert set(user) == {
            "contract",
            "native_work_view",
            "work_brief",
            "claim_scope",
            "active_unit_ids",
            "field_dispositions",
            "availability_notice",
        }
        assert [u for u, s in user["field_dispositions"].items() if s == "pending_assessment"] == [
            unit
        ]
        ctx = user["native_work_view"]["context"]
        assert ctx["messages"] == [
            msg.model_dump(mode="json") for msg in cell.work.context.messages
        ]
        for doc, visible in zip(cell.work.context.documents, ctx["documents"], strict=True):
            if doc.kind in ("source", "report"):
                assert visible["structured_content"] == json.loads(doc.content_json)
            elif doc.kind == "scope":
                assert visible["local_only"] is True and "structured_content" not in visible
            else:
                refs = json.loads(doc.content_json)["entries"]
                assert visible["whole_field_locations"] == [
                    [v["ref"], v["document_id"], v["field_pointer"]] for v in refs
                ]
        assert len(ctx["statements"]) == 1 and ctx["statements"][0]["quote"] == r["text"]
        fmt = g["text"]["format"]
        props = fmt["schema"]["properties"]["assessments"]
        assert fmt["strict"] is True and props["required"] == [unit]
        items = props["properties"][unit]["properties"]["evidence"]["items"]
        assert items["minLength"] == items["maxLength"] == 5
        assert [n for n in range(10000) if re.fullmatch(items["pattern"], f"E{n:04d}")] == list(
            range(1, 1421)
        )
        for invalid in ("E1", "E00123", "e1420", "E00X1"):
            assert not re.fullmatch(items["pattern"], invalid)
        text = g["input"][1]["content"]
        assert selection.GOLD_SHA not in text and "evidence_pass_requires" not in text
        assert all(
            rule not in text for claim in gold["claims"] for rule in claim["evidence_pass_requires"]
        )
        if arm == "E":
            base = next(v for v in rows if v["unit"] == unit and v["arm"] == "B")
            user["work_brief"]["evidence_obligation"] = base["brief"]["evidence_obligation"]
            g["input"][1]["content"] = compact(user)
        normalized[cell.name] = g
    assert normalized["Q010-B"] == normalized["Q010-E"]
    assert normalized["Q011-B"] == normalized["Q011-E"]


def test_approval_and_damage(fixture_run: tuple[Path, str]) -> None:
    root, sha = fixture_run
    with pytest.raises(EvidenceError, match="approval_or_source_drift"):
        plan.verify(root, "0" * 64)
    for name in (
        "requests/Q011-E-input_count.json",
        "requests/Q008-B-generation.json",
        "gold.json",
        "scoring.json",
    ):
        p = root / name
        raw = p.read_bytes()
        p.write_bytes(raw + b" ")
        with pytest.raises(EvidenceError, match="frozen_member_drift"):
            plan.verify(root, sha)
        p.write_bytes(raw)
    assert run.audit(root, sha)["state"] == "unused"


@pytest.mark.parametrize(
    ("fault", "sent", "state"),
    [
        ("complete", 10, "bound_unassessed"),
        ("fifth_count", 5, "count_rejected"),
        ("zero", 1, "count_rejected"),
        ("local_cancel", 6, "intent_without_terminal"),
        ("late_http", 10, "http_error"),
        ("bad_ref", 6, "invalid_claim_or_citation"),
        ("wrong_unit", 6, "invalid_claim_or_citation"),
        ("usage", 6, "accounting_hold"),
        ("length", 6, "length"),
        ("timeout", 1, "timeout"),
    ],
)
def test_journal(fixture_run: tuple[Path, str], fault: str, sent: int, state: str) -> None:
    root, sha = fixture_run
    slots = json.loads((root / "plan.json").read_bytes())["slots"]
    calls: list[str] = []

    def reply(req: httpx.Request) -> httpx.Response:
        slot = slots[len(calls)]
        calls.append(slot["stage"])
        assert (
            root / "output" / f"{len(calls):02d}-{slot['cell']}-{slot['stage']}-intent.json"
        ).exists()
        assert (
            str(req.url) == slot["destination"] + slot["path"]
            and req.content == (root / slot["filename"]).read_bytes()
        )
        if fault == "timeout":
            raise httpx.ReadTimeout("fixture timeout")
        if slot["stage"] == "input_count":
            value = plan.INPUT + 1 if fault == "fifth_count" and len(calls) == 5 else plan.INPUT
            return httpx.Response(200, json={"input_tokens": 0 if fault == "zero" else value})
        if fault == "local_cancel":
            raise asyncio.CancelledError
        if fault == "late_http" and len(calls) == 10:
            return httpx.Response(503, json={"error": {"code": "server_error"}})
        unit = "Q007" if fault == "wrong_unit" else slot["cell"].split("-")[0]
        answer = dict(
            support="supported",
            reason="Injected terminal.",
            evidence=["E1421" if fault == "bad_ref" else "E1420"],
        )
        content = dict(type="output_text", text=json.dumps({"assessments": {unit: answer}}))
        body = dict(
            model=MODEL,
            status="completed",
            output=[dict(type="message", role="assistant", status="completed", content=[content])],
            usage=dict(input_tokens=plan.INPUT, output_tokens=100, total_tokens=plan.INPUT + 100),
        )
        if fault == "usage":
            del body["usage"]
        if fault == "length":
            body.update(status="incomplete", incomplete_details={"reason": "max_output_tokens"})
        return httpx.Response(200, json=body)

    def dispatch() -> str:
        return asyncio.run(
            run.dispatch(root, sha, httpx.MockTransport(reply), SecretValue("fixture-only"))
        )

    if fault == "local_cancel":
        with pytest.raises(asyncio.CancelledError):
            dispatch()
    else:
        assert dispatch() == state
    report = run.audit(root, sha)
    assert report["state"] == state and len(report["slots"]) == 10
    assert sum(s["state"] != "not_attempted" for s in report["slots"]) == sent
    assert calls == (["input_count"] * 5 + ["generation"] * 5)[:sent]
    assert not any(s["eligible"] for s in report["slots"])
    with pytest.raises(EvidenceError, match="consumed"):
        dispatch()
    assert len(calls) == sent


@pytest.mark.parametrize(
    ("label_miss", "evidence_miss", "missing", "expected"),
    [
        (set(), set(), "", "no_headroom"),
        ({"Q010-B"}, {"Q011-B"}, "", "within_review_gain"),
        ({"Q010-B"}, {"Q011-E"}, "", "hold"),
        (set(), {"Q008-B"}, "", "hold"),
        ({"Q011-B", "Q011-E"}, set(), "", "no_gain"),
        (set(), set(), "Q010-E", "inconclusive"),
    ],
)
def test_independent_scores(
    issued: tuple[Path, str, Materials],
    label_miss: set[str],
    evidence_miss: set[str],
    missing: str,
    expected: str,
) -> None:
    _, sha, (_, assets, _) = issued
    gold = assets["gold.json"]
    labels = {c["field_id"]: c["label"] for c in json.loads(gold)["claims"]}
    report: Audit = dict(
        approval=sha,
        origin="observed_openai_transport",
        ledger="dispatched",
        closed=True,
        state="fixture",
        slots=[],
    )
    decisions = {}
    for name in ORDER:
        unit = name.split("-")[0]
        sid = digest(name.encode())
        row: dict[str, Any] = dict(
            cell=name,
            stage="generation",
            eligible=name != missing,
            state="http_error" if name == missing else "bound_unassessed",
        )
        if name != missing:
            row.update(
                scoring_id=sid,
                final={
                    "assessments": {
                        unit: dict(
                            support="supported" if name in label_miss else labels[unit],
                            reason="Fixture basis.",
                            evidence=["E1420"],
                        )
                    }
                },
            )
            decisions[sid] = dict(
                case=unit,
                outcome="fail" if name in evidence_miss else "pass",
                basis="Fixture located passage.",
            )
        report["slots"].append(row)
    sheet = evidence_sheet(report)
    assert all(set(r) == {"scoring_id", "case", "claim_id", "citations", "reason"} for r in sheet)
    form = encoded(
        dict(approval_sha256=sha, sheet_sha256=digest(encoded(sheet)), decisions=decisions)
    )
    result = scoring.scores(report, form, gold)
    assert result["decision"] == expected and set(result["movement"]) == {"Q010", "Q011"}
    if expected == "within_review_gain":
        assert result["movement"]["Q010"] == dict(judgment="gain", evidence="retained_pass")
        assert result["movement"]["Q011"] == dict(judgment="retained_pass", evidence="gain")
    if missing:
        assert (
            result["rows"][missing]["judgment"] == result["rows"][missing]["evidence"] == "unscored"
        )
