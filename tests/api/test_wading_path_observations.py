"""Check the exact observation intervention, two-axis scoring and seven-count barrier."""

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
from open_hollywood_engine.evaluations.assessment_result import _registry
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, text_hash
from open_hollywood_engine.secrets import SecretValue

from scripts.q010_uncertainty_plan import MODEL, Cell, digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.wading_path_be import regression
from scripts.wading_path_observations import plan, run, scoring

Materials = tuple[list[Cell], dict[str, bytes], bytes]
ORDER = ("K1-B", "K2-O", "K3-B", "Q008-B", "K1-O", "K2-B", "K3-O")


@pytest.fixture(scope="module")
def frozen(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str, Materials]:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private Wading Path capture")
    root = tmp_path_factory.mktemp("observations") / "plan"
    sha = plan.issue(root)
    materials = plan.materials()
    assert digest(materials[2]) == sha
    return root, sha, materials


def test_paired_wires_and_source_authority(frozen: tuple[Path, str, Materials]) -> None:
    root, _, (cells, assets, manifest) = frozen
    m = json.loads(manifest)
    assert tuple(m["ordered_cells"]) == ORDER and len(m["slots"]) == 14
    assert [s["stage"] for s in m["slots"]] == ["input_count"] * 7 + ["generation"] * 7
    assert [s["cell"] for s in m["slots"]] == list(ORDER) * 2
    assert all((root / k).read_bytes() == raw for k, raw in assets.items())
    assert m["members"] == {k: digest(raw) for k, raw in assets.items()}
    assert m["budget"] == dict(
        input_counts=7,
        max_generations=7,
        retries=0,
        input_per_generation=160000,
        output_per_generation=4096,
        aggregate_generation_input=1120000,
        aggregate_generation_output=28672,
        max_usd_per_generation="0.44096",
        aggregate_generation_usd="3.08672",
        count_seconds=120,
        generation_seconds=300,
        wall_seconds=2940,
    )
    key = json.loads(assets["gold.json"])
    assert {k: v["gold"] for k, v in key.items()} == dict(
        K1="uncertain", K2="supported", K3="unsupported", Q008="unsupported"
    )
    assert digest(assets["gold.json"]) == m["gold_sha256"] == scoring.GOLD_SHA
    quotes = json.loads(assets["observations.json"])
    assert list(map(len, (quotes["K1"], quotes["K2"], quotes["K3"]))) == [3, 4, 4]
    normalized = {}
    works = {cell.name: cell.work for cell in cells}
    archive_run = regression.ARCHIVE / "capture/run/requests"
    original_docs = {d.identity: d for d in works["K1-B"].context.documents}
    for cell in cells:
        case, arm = cell.name.split("-")
        info = key[case]
        count, generate = cell.wire.endpoints
        c, g = json.loads(count.body_utf8), json.loads(generate.body_utf8)
        assert c == {k: g[k] for k in ("model", "input", "text", "reasoning")}
        assert g["model"] == MODEL == "gpt-6.1-sol" and g["reasoning"]["effort"] == "high"
        assert g["max_output_tokens"] == 4096 and g["store"] is False
        assert cell.wire.active_unit_ids == (info["unit"],)
        assert count.path == "/v1/responses/input_tokens" and generate.path == "/v1/responses"
        assert count.destination == generate.destination == "https://api.openai.com"
        if cell.name in ("K1-B", "Q008-B"):
            for end in (count, generate):
                filename = f"{info['unit']}-B-{end.stage}.json"
                assert end.body_utf8.encode() == (archive_run / filename).read_bytes()
        user = json.loads(g["input"][1]["content"])
        assert user["active_unit_ids"] == [info["unit"]]
        assert user["claim_scope"]["statement"]["quote"] == info["claim"]
        assert all(rule not in g["input"][1]["content"] for rule in info["evidence_requirements"])
        assert all(d not in user for d in ("gold", "ending", "reach", "standing_at_cut"))
        ctx = cell.work.context
        assert ctx.messages == works["K1-B"].context.messages
        docs = {d.identity: d for d in ctx.documents}
        for historical in ("whole-review", "visible-request"):
            assert docs[historical] == original_docs[historical]
        refs = {e.ref: e for e in _registry(cell.work).entries}
        draft = refs["E1420"]
        assert draft.document_version == info["draft_version"]
        assert text_hash(draft.quote) == info["prose_sha256"]
        assert refs["E0258"].quote == "They reach the breaker panel housing."
        assert refs["E0254"].quote == "They are standing before the final barrier."
        if arm == "O":
            excerpts = user["work_brief"].pop("exact_observations")
            assert excerpts == quotes[case]
            assert excerpts[0]["start"] == 3995 and excerpts[-1]["end"] == len(draft.quote)
            for q in excerpts:
                assert q == dict(
                    ref="E1420",
                    draft_version=draft.document_version,
                    start=q["start"],
                    end=q["end"],
                    quote=draft.quote[q["start"] : q["end"]],
                )
            g["input"][1]["content"] = compact(user)
        else:
            assert "exact_observations" not in user["work_brief"]
        normalized[cell.name] = g
    for case in ("K1", "K2", "K3"):
        assert normalized[case + "-O"] == normalized[case + "-B"]
        assert works[case + "-B"].fingerprint == works[case + "-O"].fingerprint
    assert len({c.wire.native_request_sha256 for c in cells}) == 7


@pytest.mark.parametrize(
    ("fault", "sent", "state"),
    [
        ("none", 14, "bound_unassessed"),
        ("last_count", 7, "count_rejected"),
        ("incomplete_message", 8, "invalid_response"),
        ("bad_citation", 8, "invalid_claim_or_citation"),
        ("interruption", 8, "intent_without_terminal"),
    ],
)
def test_single_use_schedule(
    frozen: tuple[Path, str, Materials],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fault: str,
    sent: int,
    state: str,
) -> None:
    issued, sha, materials = frozen
    monkeypatch.setattr(plan, "materials", lambda: materials)
    root = tmp_path / "isolated"
    shutil.copytree(issued, root)
    slots = json.loads(materials[2])["slots"]
    calls: list[str] = []

    def reply(req: httpx.Request) -> httpx.Response:
        slot = slots[len(calls)]
        calls.append(slot["stage"])
        assert str(req.url) == slot["destination"] + slot["path"]
        assert req.content == (root / slot["filename"]).read_bytes()
        assert (
            root / "output" / f"{len(calls):02d}-{slot['cell']}-{slot['stage']}-intent.json"
        ).is_file()
        if slot["stage"] == "input_count":
            count = 160001 if len(calls) == 7 and fault == "last_count" else 75000
            return httpx.Response(200, json={"input_tokens": count})
        if fault == "interruption":
            raise asyncio.CancelledError
        unit = "Q008" if slot["cell"] == "Q008-B" else "Q011"
        answer = dict(
            support="uncertain",
            evidence=["E1421" if fault == "bad_citation" else "E1420"],
            reason="Injected fixture.",
        )
        content = dict(type="output_text", text=json.dumps({"assessments": {unit: answer}}))
        return httpx.Response(
            200,
            json=dict(
                model=MODEL,
                status="completed",
                output=[
                    dict(
                        type="message",
                        role="assistant",
                        status="in_progress" if fault == "incomplete_message" else "completed",
                        content=[content],
                    )
                ],
                usage=dict(input_tokens=75000, output_tokens=50, total_tokens=75050),
            ),
        )

    def dispatch() -> str:
        return asyncio.run(
            run.dispatch(
                root, sha, httpx.MockTransport(reply), SecretValue("offline-test-6f8a1cf8")
            )
        )

    if fault == "interruption":
        with pytest.raises(asyncio.CancelledError):
            dispatch()
    else:
        assert dispatch() == state
    audit = run.audit(root, sha)
    assert audit["state"] == state and len(audit["slots"]) == 14
    assert calls == (["input_count"] * 7 + ["generation"] * 7)[:sent]
    assert not any(s["eligible"] for s in audit["slots"])
    assert all(s["state"] == "not_attempted" for s in audit["slots"][sent:])
    with pytest.raises(EvidenceError, match="consumed"):
        dispatch()
    assert len(calls) == sent


@pytest.mark.parametrize(
    ("wrong", "poor", "missing", "gate"),
    [
        ("", "", "", "no_original_headroom"),
        ("K1-B", "", "", "within_scene_recovery"),
        ("", "K1-B", "", "within_scene_recovery"),
        ("", "K1-O", "", "hold_original"),
        ("K2-B", "", "", "hold_controls"),
        ("", "K3-O", "", "hold_controls"),
        ("", "Q008-B", "", "hold_controls"),
        ("", "", "K1-O", "inconclusive"),
    ],
)
def test_two_scores(
    frozen: tuple[Path, str, Materials], wrong: str, poor: str, missing: str, gate: str
) -> None:
    _, sha, (_, assets, _) = frozen
    key = json.loads(assets["gold.json"])
    audit: Audit = dict(
        approval=sha,
        ledger="dispatched",
        closed=True,
        origin="observed_openai_transport",
        state="test_only",
        slots=[],
    )
    decisions = {}
    for name in ORDER:
        case = name.split("-")[0]
        sid = digest(name.encode())
        row: dict[str, Any] = dict(
            cell=name,
            stage="generation",
            eligible=name != missing,
            state="bound_unassessed" if name != missing else "http_error",
        )
        if name != missing:
            expected = key[case]["gold"]
            other = "unsupported" if expected == "uncertain" else "uncertain"
            answer = dict(
                support=other if name == wrong else expected, evidence=["E1420"], reason="Fixture."
            )
            row.update(scoring_id=sid, final={"assessments": {key[case]["unit"]: answer}})
            decisions[sid] = dict(
                case=case,
                outcome="fail" if name == poor else "pass",
                basis="Reviewed fixture span.",
            )
        audit["slots"].append(row)
    sheet = evidence_sheet(audit)
    assert all(set(s) == {"scoring_id", "case", "claim_id", "citations", "reason"} for s in sheet)
    form = encoded(
        dict(approval_sha256=sha, sheet_sha256=digest(encoded(sheet)), decisions=decisions)
    )
    result = scoring.scores(audit, form, assets["gold.json"])
    assert result["decision"] == gate and result["original_baseline_recovery"] == (
        "K1-B" not in (wrong, poor)
    )
    for name, scored in result["rows"].items():
        if name == missing:
            assert scored["judgment"] == scored["evidence"] == "unscored"
        else:
            assert scored["judgment"] == ("fail" if name == wrong else "pass")
            assert scored["evidence"] == ("fail" if name == poor else "pass")
    if wrong == "K1-B":
        assert result["movement"]["K1"] == dict(judgment="gain", evidence="retained_pass")
    if poor == "K1-B":
        assert result["movement"]["K1"] == dict(judgment="retained_pass", evidence="gain")


def test_damaged_wires_and_gold(
    frozen: tuple[Path, str, Materials], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src, sha, materials = frozen
    root = tmp_path / "damaged"
    shutil.copytree(src, root)
    monkeypatch.setattr(plan, "materials", lambda: materials)
    for path in (
        "requests/K1-O-input_count.json",
        "requests/K3-B-generation.json",
        "gold.json",
        "observations.json",
    ):
        p = root / path
        raw = p.read_bytes()
        p.write_bytes(raw + b" ")
        with pytest.raises(EvidenceError, match="frozen_member_drift"):
            plan.verify(root, sha)
        p.write_bytes(raw)
    assert run.audit(root, sha)["state"] == "unused"
