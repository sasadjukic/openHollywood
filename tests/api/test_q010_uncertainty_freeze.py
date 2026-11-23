"""Exercise both frozen endpoint registrations against their own eight private controls."""

from __future__ import annotations

import asyncio
import json
import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_compact_presentation import SYSTEM
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretValue

from scripts import ordinary_v61_capture as ledger
from scripts import q010_uncertainty_plan, q010_uncertainty_run, verify_q010_endpoint_controls
from scripts.fresh_endpoint_repeat import controls as fresh_controls
from scripts.fresh_endpoint_repeat import plan as fresh_plan
from scripts.fresh_endpoint_repeat import run as fresh_run
from scripts.q010_uncertainty_plan import ADDITION, BASE, INPUT, MODEL
from scripts.q010_uncertainty_run import evidence_sheet


@dataclass(frozen=True)
class Study:
    plan: ModuleType
    run: ModuleType
    sources: Path
    families: tuple[str, str]
    missing: tuple[str, str]


@pytest.fixture(
    scope="module",
    params=[
        Study(
            q010_uncertainty_plan,
            q010_uncertainty_run,
            verify_q010_endpoint_controls.ROOT,
            ("E", "L"),
            ("P03", "P08"),
        ),
        Study(fresh_plan, fresh_run, fresh_controls.ROOT, ("D", "T"), ("R03", "R05")),
    ],
    ids=["anchor", "fresh"],
)
def study(request: pytest.FixtureRequest) -> Study:
    value = request.param
    assert isinstance(value, Study)
    if not (value.sources / "frozen/seal.json").is_file():
        pytest.skip("private admitted sources required")
    return value


@pytest.fixture(scope="module")
def frozen(tmp_path_factory: pytest.TempPathFactory, study: Study) -> tuple[Path, str]:
    root = tmp_path_factory.mktemp("issued") / "fixture"
    return root, study.plan.issue(root)


def test_source_only_pairing(frozen: tuple[Path, str], study: Study) -> None:
    root, approval = frozen
    gold = json.loads((study.sources / "frozen/gold.json").read_bytes())["cases"]

    def neutral(path: Path) -> bytes:
        assert path.name == "seal.json" or path.parent.name in ("packets", "previews")
        return path.read_bytes()

    with patch.object(study.plan, "_read", neutral):
        cells = study.plan.render()
    first: dict[str, str] = {}
    for cell in cells:
        case, arm = cell.name.split("-")
        first.setdefault(case, arm)
        a, b = (json.loads(e.body_utf8) for e in cell.wire.endpoints)
        assert a == {key: b[key] for key in ("input", "model", "reasoning", "text")}
        assert b["reasoning"] == {"effort": "high"} and b["max_output_tokens"] == 4096
        assert b["input"][0]["content"] == (
            SYSTEM if arm == "B" else SYSTEM.replace(BASE, BASE + " " + ADDITION)
        )
        user = json.loads(b["input"][1]["content"])
        assert set(user) == {"packet", "work_brief", "native_work_view", "active_unit_ids"}
        assert user["packet"] == json.loads(
            (study.sources / "frozen/packets" / (case + ".json")).read_bytes()
        )
        assert user["work_brief"] == json.loads(cell.work.context.messages[0].content)["work_brief"]
        assert cell.wire.active_unit_ids == (user["packet"]["claim_id"],)
        reads = [s["ref"] for s in user["packet"]["sources"]]
        assert ("S02" not in reads) == (case in study.missing)
    assert Counter((r["family"], first[r["case_id"]]) for r in gold) == {
        (f, a): 2 for f in study.families for a in ("B", "C")
    }
    assert all(n == 1 for n in Counter((r["state"], first[r["case_id"]]) for r in gold).values())
    report = study.run.audit(root, approval)
    assert report["ledger"] == "ready" and len(report["slots"]) == 32
    assert all(r["state"] == "not_attempted" for r in report["slots"])


def test_drift(frozen: tuple[Path, str], tmp_path: Path, study: Study) -> None:
    src, approval = frozen
    root = tmp_path / "copy"
    shutil.copytree(src, root)
    with pytest.raises(EvidenceError, match="approval"):
        study.plan.verify(root, "0" * 64)
    next((root / "requests").glob("*-B-input_count.json")).write_bytes(b"{}")
    with pytest.raises(EvidenceError, match="request_drift"):
        study.plan.verify(root, approval)
    assert ledger.ledger_state(root, approval) == "ready"


@pytest.mark.parametrize(
    ("fault", "attempts", "expected"),
    [
        ("success", 32, "bound_unassessed"),
        ("last_count_limit", 16, "count_rejected"),
        ("duplicate_count", 1, "invalid_response"),
        ("http", 1, "http_error"),
        ("absent_ref", 21, "invalid_claim_or_citation"),
        ("missing_usage", 17, "accounting_hold"),
        ("bad_model", 17, "invalid_response"),
        ("interrupt", 17, "intent_without_terminal"),
    ],
)
def test_single_use_transport(
    frozen: tuple[Path, str], tmp_path: Path, fault: str, attempts: int, expected: str, study: Study
) -> None:
    src, approval = frozen
    root = tmp_path / "rehearsal"
    shutil.copytree(src, root)
    slots = json.loads((root / "plan.json").read_bytes())["slots"]
    seen: list[str] = []

    def reply(req: httpx.Request) -> httpx.Response:
        i = len(seen)
        slot = slots[i]
        assert req.content == (root / "requests" / slot["filename"]).read_bytes()
        assert str(req.url) == slot["destination"] + slot["path"]
        assert (
            root / "output" / f"{i + 1:02d}-{slot['cell']}-{slot['stage']}-intent.json"
        ).exists()
        seen.append(slot["stage"])
        if fault == "http":
            return httpx.Response(500, json={"error": {"code": "server_error"}})
        if fault == "duplicate_count":
            return httpx.Response(200, content=b'{"input_tokens":100,"input_tokens":1}')
        if i < 16:
            tokens = INPUT + 1 if fault == "last_count_limit" and i == 15 else 1100
            return httpx.Response(200, json={"input_tokens": tokens})
        if fault == "interrupt":
            raise asyncio.CancelledError()
        user = json.loads(json.loads(req.content)["input"][1]["content"])
        # Intentionally wrong for six cases. Semantic outcomes must never stop dispatch.
        final = {
            "assessments": {
                user["packet"]["claim_id"]: {
                    "support": "supported",
                    "evidence": ["S02" if fault == "absent_ref" and i == 20 else "S01"],
                    "reason": "The earlier eyewitness establishes the first action.",
                }
            }
        }
        body: dict[str, object] = {
            "model": "other" if fault == "bad_model" else MODEL,
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": json.dumps(final)}],
                }
            ],
            "usage": {
                "input_tokens": 1100,
                "output_tokens": 70,
                "total_tokens": 1170,
                "output_tokens_details": {"reasoning_tokens": 30},
            },
        }
        if fault == "missing_usage":
            del body["usage"]
        return httpx.Response(200, json=body)

    def attempt() -> str:
        result = asyncio.run(
            study.run.dispatch(
                root,
                approval,
                httpx.MockTransport(reply),
                SecretValue("injected-qualification-only"),
            )
        )
        assert isinstance(result, str)
        return result

    if fault == "interrupt":
        with pytest.raises(asyncio.CancelledError):
            attempt()
    else:
        assert attempt() == expected
    report = study.run.audit(root, approval)
    assert report["state"] == expected and report["closed"] == (fault != "interrupt")
    assert seen == (["input_count"] * 16 + ["generation"] * 16)[:attempts]
    assert sum(r["state"] != "not_attempted" for r in report["slots"]) == attempts
    assert not any(r["eligible"] for r in report["slots"]) and not evidence_sheet(report)
    with pytest.raises(EvidenceError, match="consumed"):
        attempt()
    assert len(seen) == attempts
    if fault == "success":
        # Exercise the worksheet with fixture eligibility only in this in-memory copy.
        for row in report["slots"][16:]:
            row["eligible"] = True
        sheet = evidence_sheet(report)
        assert len({r["scoring_id"] for r in sheet}) == 16
        assert all(
            set(r) == {"case", "claim_id", "scoring_id", "citations", "reason"} for r in sheet
        )
        target = next((root / "output").glob("32-*-generation-outcome.json"))
        target.write_bytes(target.read_bytes() + b" ")
        with pytest.raises(EvidenceError, match="chain"):
            study.run.audit(root, approval)
