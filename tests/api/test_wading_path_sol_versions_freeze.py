"""Check paired inputs, model attribution, the global count barrier and independent scores."""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource
from open_hollywood_engine.evaluations.assessment_result import _registry
from open_hollywood_engine.evaluations.assessment_work import ContextDocument
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, text_hash
from open_hollywood_engine.secrets import SecretValue

from scripts.q010_uncertainty_plan import Cell, digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.wading_path_sol_versions import plan, run, scoring
from scripts.wading_path_visit_position import regression

Materials = tuple[list[Cell], dict[str, bytes], bytes]
ORDER = (
    "SN-61",
    "SN-62",
    "XE-62",
    "XE-61",
    "VN-61",
    "VN-62",
    "SE-62",
    "SE-61",
    "XN-61",
    "XN-62",
    "VE-62",
    "VE-61",
)


@pytest.fixture(scope="module")
def frozen(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str, Materials]:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private Wading Path capture")
    root = tmp_path_factory.mktemp("visit-position") / "plan"
    sha = plan.issue(root)
    materials = plan.materials()
    assert digest(materials[2]) == sha
    return root, sha, materials


def test_paired_wires_and_source_authority(frozen: tuple[Path, str, Materials]) -> None:
    root, _, (cells, assets, manifest) = frozen
    m = json.loads(manifest)
    assert tuple(m["ordered_cells"]) == ORDER and len(m["slots"]) == 24
    assert [(s["stage"], s["cell"]) for s in m["slots"]] == [
        (stage, name) for stage in ("input_count", "generation") for name in ORDER
    ]
    assert all((root / k).read_bytes() == raw for k, raw in assets.items())
    assert m["members"] == {k: digest(v) for k, v in assets.items()}
    assert m["budget"]["input_counts"] == m["budget"]["max_generations"] == 12
    assert m["budget"]["per_model_counts"] == m["budget"]["per_model_max_generations"] == 6
    assert m["budget"]["retries"] == 0 and m["budget"]["aggregate_generation_usd"] == "5.29152"
    assert m["budget"]["per_model_generation_usd"] == {"61": "2.64576", "62": "2.64576"}
    key = json.loads(assets["gold.json"])
    assert {k: v["gold"] for k, v in key.items()} == dict(
        SN="unsupported",
        SE="uncertain",
        XN="unsupported",
        XE="unsupported",
        VN="supported",
        VE="supported",
    )
    assert digest(assets["gold.json"]) == m["gold_sha256"] == scoring.GOLD_SHA
    criteria = json.loads(assets["evidence-criteria.json"])
    assert criteria == {k: {a: b for a, b in v.items() if a != "gold"} for k, v in key.items()}
    capture = regression.ARCHIVE / "capture"
    source = IntakeSource.model_validate_json((capture / "source/intake.json").read_bytes())
    histories = {d.identity: d for d in source.inventory_work.context.documents}
    drafts: dict[str, dict[str, ContextDocument]] = {}
    briefs = []
    for cell in cells:
        case, arm = cell.name.split("-")
        info = key[case]
        count, generate = cell.wire.endpoints
        c, g = json.loads(count.body_utf8), json.loads(generate.body_utf8)
        assert c == {k: g[k] for k in ("model", "input", "text", "reasoning")}
        assert g["model"] == plan.MODELS[arm] and g["reasoning"]["effort"] == "high"
        assert g["max_output_tokens"] == 4096 and g["store"] is False
        assert cell.wire.active_unit_ids == (info["unit"],)
        assert count.path == "/v1/responses/input_tokens" and generate.path == "/v1/responses"
        assert count.destination == generate.destination == "https://api.openai.com"
        user = json.loads(g["input"][1]["content"])
        assert user["active_unit_ids"] == [info["unit"]]
        assert user["claim_scope"]["statement"]["quote"] == info["claim"]
        assert all(rule not in g["input"][1]["content"] for rule in info["evidence_requirements"])
        assert "exact_observations" not in user["work_brief"]
        assert set(user) == {
            "contract",
            "active_unit_ids",
            "native_work_view",
            "claim_scope",
            "work_brief",
            "availability_notice",
            "field_dispositions",
        }
        assert set(g["text"]["format"]["schema"]["properties"]["assessments"]["properties"]) == {
            info["unit"]
        }
        ctx = cell.work.context
        assert ctx.messages == source.inventory_work.context.messages
        docs = {d.identity: d for d in ctx.documents}
        for historical in ("whole-review", "visible-request"):
            assert docs[historical].content_json == histories[historical].content_json
        refs = {e.ref: e for e in _registry(cell.work).entries}
        draft = refs["E1420"]
        assert (
            draft.document_version == info["draft_version"]
            and text_hash(draft.quote) == info["prose_sha256"]
        )
        assert refs["E0258"].quote == "They reach the breaker panel housing."
        assert refs["E0254"].quote == "They are standing before the final barrier."
        assert ctx.provenance == "synthetic_fixture"
        assert [f.field_id for f in ctx.report_fields] == ["A001"]
        assert user["claim_scope"]["source_scopes"] == [
            dict(role="draft", coverage="complete_fields", evidence_refs=["E1420"])
        ]
        assert json.loads(docs["authored-diagnostic-claim"].content_json) == {
            "authored_claim": info["claim"]
        }
        assert set(user["field_dispositions"]) == {"A001"}
        assert all(
            k not in user["work_brief"]
            for k in ("gold", "predicate", "ending", "evidence_requirements")
        )
        for other in {r["claim"] for r in key.values()} - {info["claim"]}:
            assert other not in g["input"][1]["content"]
        story_context = {k: v for k, v in docs.items() if k != "authored-diagnostic-claim"}
        assert drafts.setdefault(info["ending"], story_context) == story_context
        briefs.append(user["work_brief"])
    assert len(briefs) == 12 and all(b == briefs[0] for b in briefs)
    pairs = {c.name: c for c in cells}
    for case in key:
        a, b = (pairs[case + "-" + arm] for arm in ("61", "62"))
        assert (
            a.work.fingerprint == b.work.fingerprint
            and a.wire.native_request_sha256 != b.wire.native_request_sha256
        )
        for left, right in zip(a.wire.endpoints, b.wire.endpoints, strict=True):
            old_line, new_line = (f'\n  "model": "{plan.MODELS[arm]}",' for arm in ("61", "62"))
            assert left.body_utf8.count(old_line) == 1
            assert left.body_utf8.replace(old_line, new_line, 1) == right.body_utf8
    stop, excluded, visited = (
        json.loads(drafts[k]["catalog-complete-current-draft"].content_json)["prose"]
        for k in ("stop", "exclusion", "visit")
    )
    assert stop[4806:] == m["fixed_stop"]["quote"] and len(stop) == 4945
    assert excluded.startswith(stop + "\n\n") and visited.startswith(stop + "\n\n")
    assert "neither Elias nor Maya had ever been closer" in excluded[4947:]
    assert "had reached the master breaker panel housing together" in visited[4947:]
    assert len({c.wire.native_request_sha256 for c in cells}) == 12


@pytest.mark.parametrize(
    ("fault", "sent", "state"),
    [
        ("none", 24, "bound_unassessed"),
        ("last_count", 12, "count_rejected"),
        ("incomplete_message", 13, "invalid_response"),
        ("bad_citation", 13, "invalid_claim_or_citation"),
        ("wrong_unit", 13, "invalid_claim_or_citation"),
        ("sibling_62", 14, "model_mismatch"),
        ("sibling_61", 13, "model_mismatch"),
        ("missing_model", 13, "invalid_response"),
        ("interruption", 13, "intent_without_terminal"),
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
            count = 160001 if len(calls) == 12 and fault == "last_count" else 75000
            return httpx.Response(200, json={"input_tokens": count})
        if fault == "interruption":
            raise asyncio.CancelledError
        answer = dict(
            support="uncertain",
            evidence=["E1421" if fault == "bad_citation" else "E1420"],
            reason="Injected fixture.",
        )
        content = dict(
            type="output_text",
            text=json.dumps({"assessments": {"Q011" if fault == "wrong_unit" else "A001": answer}}),
        )
        return httpx.Response(
            200,
            json=dict(
                model=(
                    None
                    if fault == "missing_model"
                    else plan.MODELS["62"]
                    if fault == "sibling_61"
                    else plan.MODELS["61"]
                    if fault == "sibling_62"
                    else json.loads(req.content)["model"]
                ),
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
    assert audit["state"] == state and len(audit["slots"]) == 24
    assert calls == (["input_count"] * 12 + ["generation"] * 12)[:sent]
    assert not any(s["eligible"] for s in audit["slots"])
    assert all(s["state"] == "not_attempted" for s in audit["slots"][sent:])
    with pytest.raises(EvidenceError, match="consumed"):
        dispatch()
    assert len(calls) == sent


@pytest.mark.parametrize(
    ("wrong", "poor", "missing", "gate"),
    [
        ("", "", "", "complete_within_scene"),
        ("SE-61", "", "", "complete_within_scene"),
        ("", "SE-62", "", "complete_within_scene"),
        ("XN-62", "XN-62", "", "complete_within_scene"),
        ("", "", "SE-61", "inconclusive"),
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
    assert result["decision"] == gate
    assert result["open_event_recovery_62"] == (None if missing else wrong == "SE-61")
    if wrong == "SE-61":
        assert result["paired_axes"]["SE"] == dict(judgment="gain_62", evidence="both_pass")
    if poor == "SE-62":
        assert result["paired_axes"]["SE"] == dict(judgment="both_pass", evidence="loss_62")
    for name, scored in result["rows"].items():
        if name == missing:
            assert scored["judgment"] == scored["evidence"] == "unscored"
        else:
            assert scored["judgment"] == ("fail" if name == wrong else "pass")
            assert scored["evidence"] == ("fail" if name == poor else "pass")


def test_damaged_wires_and_gold(
    frozen: tuple[Path, str, Materials], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src, sha, materials = frozen
    root = tmp_path / "damaged"
    shutil.copytree(src, root)
    monkeypatch.setattr(plan, "materials", lambda: materials)
    for path in (
        "requests/SE-61-input_count.json",
        "requests/XE-62-generation.json",
        "gold.json",
        "evidence-criteria.json",
    ):
        p = root / path
        raw = p.read_bytes()
        p.write_bytes(raw + b" ")
        with pytest.raises(EvidenceError, match="frozen_member_drift"):
            plan.verify(root, sha)
        p.write_bytes(raw)
    assert run.audit(root, sha)["state"] == "unused"
