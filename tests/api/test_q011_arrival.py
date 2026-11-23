"""Qualify the two diagnostic inputs and the fixed schedule using only local fixtures."""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import EvidenceRegistry
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretValue

from scripts.q010_uncertainty_plan import MODEL, digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.q011_arrival import plan, run, scoring, sources


@pytest.fixture(scope="module")
def issued(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str]:
    if not sources.EXPORT.is_file() or not sources.REHEARSAL.is_file():
        pytest.skip("private registered Elias archive required")
    root = tmp_path_factory.mktemp("q011") / "issued"
    return root, plan.issue(root)


def test_pair_and_gold(issued: tuple[Path, str], monkeypatch: pytest.MonkeyPatch) -> None:
    root, approval = issued
    cases = plan.verify(root, approval)
    gold = json.loads((root / "gold.json").read_bytes())
    legacy = json.loads(json.loads(sources.REHEARSAL.read_bytes())["input"][1]["content"])
    original = json.loads(sources.EXPORT.read_bytes())["entries"][0]["snapshot"]
    artifacts = {a["artifact_kind"]: a for a in original["sources"]}
    allowed = {sources.EXPORT, sources.REHEARSAL}

    def fenced_read(path: Path) -> bytes:
        assert path in allowed, path
        return path.read_bytes()

    monkeypatch.setattr(sources, "_read", fenced_read)
    packets = sources.packets()
    normalized = []
    draft_ids = []
    for case, cell in zip(sources.CASES, cases, strict=True):
        assert plan.render(case, packets[case]) == cell
        count, generation = (json.loads(end.body_utf8) for end in cell.wire.endpoints)
        assert count == {k: generation[k] for k in ("input", "reasoning", "model", "text")}
        assert count["input"][0] == json.loads(sources.REHEARSAL.read_bytes())["input"][0]
        assert count["model"] == "gpt-6.1-sol" and count["reasoning"] == {"effort": "high"}
        assert not generation["store"] and generation["truncation"] == "disabled"
        schema = count["text"]["format"]["schema"]["properties"]["assessments"]
        assert schema["required"] == list(schema["properties"]) == ["Q011"]
        user = json.loads(count["input"][1]["content"])
        assert set(user) == {
            "active_unit_ids",
            "claim",
            "work_brief",
            "source_authority",
            "native_work_view",
        }
        row = gold["cases"][case]
        assert user["active_unit_ids"] == ["Q011"] and user["claim"]["text"] == row["claim"]
        assert [user["work_brief"]] == legacy["original_work_briefs"]["briefs"]
        docs = {d["identity"]: d for d in user["native_work_view"]["context"]["documents"]}
        for kind in ("scene_plan", "story_bible", "story_blueprint"):
            assert docs[kind]["version"] == artifacts[kind]["version_id"]
            assert docs[kind]["structured_content"] == artifacts[kind]["content"]
        history = docs["historical-review"]["structured_content"]
        assert history["content"] == original["critique"]["content"]
        assert history["saved_native_audit"] == original["native_audit"]
        assert history["original_candidate_version"] == original["draft_version_id"]
        draft = docs["assessment_draft"]
        draft_ids.append(draft["version"])
        assert draft["version"] == row["draft_version"]
        content = draft["structured_content"]
        original_draft = artifacts["scene_draft"]["content"]
        prose = original_draft["prose"] + ("" if case == "A" else " " + sources.ADDED)
        assert content == original_draft | {
            "prose": prose,
            "ending_excerpt": prose.rsplit("\n\n", 1)[-1],
        }
        assert row["whole_claim_gold"] == ("uncertain" if case == "A" else "supported")
        if case == "B":
            start, end = row["arrival"]["span"]
            assert prose[start:end] == sources.ADDED and end == len(prose)
        assert row["ending_rule"] not in str(user) and "whole_claim_gold" not in str(user)
        registry = EvidenceRegistry.model_validate_json(
            next(d.content_json for d in cell.work.context.documents if d.kind == "registry")
        )
        assert [[e.ref, e.document_id, e.field_pointer] for e in registry.entries] == docs[
            "registry"
        ]["whole_field_locations"]
        for e in registry.entries:
            doc = docs[e.document_id]
            assert (
                doc["version"] == e.document_version and doc["content_sha256"] == e.document_sha256
            )
            assert doc["structured_content"][e.field_pointer[1:]] == e.quote
        # Only these active draft components and their dependent binding digests may differ.
        draft["version"] = draft["content_sha256"] = docs["registry"]["content_sha256"] = "masked"
        content["prose"] = content["ending_excerpt"] = "masked"
        count["input"][1]["content"] = user
        normalized.append(count)
    assert normalized[0] == normalized[1]
    assert draft_ids[0] == original["draft_version_id"] != draft_ids[1]


@pytest.mark.parametrize(
    ("fault", "slots", "state"),
    [
        ("success", 4, "bound_unassessed"),
        ("grounded", 4, "bound_unassessed"),
        ("count_limit", 2, "count_rejected"),
        ("bad_count", 1, "invalid_response"),
        ("http", 3, "http_error"),
        ("last_http", 4, "http_error"),
        ("timeout", 3, "timeout"),
        ("invalid_ref", 3, "invalid_claim_or_citation"),
        ("wrong_unit", 3, "invalid_claim_or_citation"),
        ("length", 3, "length"),
        ("missing_usage", 3, "accounting_hold"),
        ("model_drift", 3, "model_mismatch"),
        ("cancel", 3, "intent_without_terminal"),
    ],
)
def test_journal(
    issued: tuple[Path, str], tmp_path: Path, fault: str, slots: int, state: str
) -> None:
    src, approval = issued
    root = tmp_path / "test-run"
    shutil.copytree(src, root)
    steps = json.loads((root / "plan.json").read_bytes())["slots"]
    sent: list[str] = []

    def reply(request: httpx.Request) -> httpx.Response:
        index = len(sent)
        step = steps[index]
        assert request.content == (root / step["filename"]).read_bytes()
        assert str(request.url) == step["destination"] + step["path"]
        assert (
            root / "output" / f"{index + 1:02d}-{step['cell']}-{step['stage']}-intent.json"
        ).exists()
        sent.append(step["stage"])
        if index < 2:
            if fault == "bad_count":
                return httpx.Response(200, content=b'{"input_tokens":1,"input_tokens":2}')
            return httpx.Response(
                200,
                json={
                    "input_tokens": plan.INPUT + 1
                    if fault == "count_limit" and index == 1
                    else 1800
                },
            )
        if fault == "http" or (fault == "last_http" and index == 3):
            return httpx.Response(503, json={"error": {"code": "service_unavailable"}})
        if fault == "timeout":
            raise httpx.ReadTimeout("fixture timeout", request=request)
        if fault == "cancel":
            raise asyncio.CancelledError
        answer = {
            "support": "supported",
            "evidence": ["X" if fault == "invalid_ref" else "E0229"],
            "reason": "The plan assigns a standing position.",
        }
        if fault == "grounded":
            ending = (
                "The draft ends on approach and leaves his position open."
                if index == 2
                else "The last sentence places him standing at the threshold."
            )
            answer = {
                "support": "uncertain" if index == 2 else "supported",
                "evidence": ["E0233", "E0229", "D01"],
                "reason": "The plan assigns attraction and standing. The last paragraph shows "
                "him drawn toward the opening. " + ending,
            }
        final = json.dumps({"assessments": {"Q012" if fault == "wrong_unit" else "Q011": answer}})
        body: dict[str, Any] = dict(
            model="other" if fault == "model_drift" else MODEL,
            status="completed",
            output=[
                dict(
                    type="message",
                    role="assistant",
                    status="completed",
                    content=[dict(type="output_text", text=final)],
                )
            ],
            usage=dict(input_tokens=1800, output_tokens=50, total_tokens=1850),
        )
        if fault == "length":
            body.update(status="incomplete", incomplete_details={"reason": "max_output_tokens"})
        if fault == "missing_usage":
            del body["usage"]
        return httpx.Response(200, json=body)

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
    assert not any(r["eligible"] for r in report["slots"])
    with pytest.raises(EvidenceError, match="consumed"):
        execute()
    assert sent == ["input_count", "input_count", "generation", "generation"][:slots]
    if fault in ("success", "last_http", "grounded"):
        check_scores(report, root, grounded=fault == "grounded")


def check_scores(report: Audit, root: Path, *, grounded: bool) -> None:
    # Exercise semantic scoring in memory only. Fixture journals remain ineligible.
    report["origin"] = "observed_openai_transport"
    for row in report["slots"]:
        row["eligible"] = row["state"] == "bound_unassessed"
    sheet = evidence_sheet(report)
    assert all("support" not in r and "returned" not in r for r in sheet)
    form = encoded(
        dict(
            approval_sha256=report["approval"],
            sheet_sha256=digest(encoded(sheet)),
            decisions={
                r["scoring_id"]: dict(
                    case=r["case"],
                    outcome="pass" if grounded else "fail",
                    basis="Both assignments and this draft's final position are addressed."
                    if grounded
                    else "Only the assigned position is cited.",
                )
                for r in sheet
            },
        )
    )
    scored = scoring.scores(report, form, (root / "gold.json").read_bytes())
    rows = scored["cases"]
    assert isinstance(rows, list)
    if grounded:
        assert all(r["judgment"] == r["evidence"] == "pass" for r in rows)
        assert scored["decision"] == "grounded_pair"
        return
    complete = report["state"] == "bound_unassessed"
    assert [(r["judgment"], r["evidence"]) for r in rows] == [
        ("fail", "fail"),
        ("pass", "fail") if complete else ("unscored", "unscored"),
    ]
    assert scored["decision"] == ("hold" if complete else "inconclusive")


def test_drift(issued: tuple[Path, str], tmp_path: Path) -> None:
    src, approval = issued
    root = tmp_path / "tampered"
    shutil.copytree(src, root)
    for path in (root / "gold.json", root / "scoring.json", root / "requests/A-B-generation.json"):
        data = path.read_bytes()
        path.write_bytes(data + b" ")
        with pytest.raises(EvidenceError, match="frozen_member_drift"):
            plan.verify(root, approval)
        path.write_bytes(data)
    assert run.audit(root, approval)["ledger"] == "ready"
