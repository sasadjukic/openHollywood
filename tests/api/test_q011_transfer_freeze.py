"""Exercise the two-family comparison using only local packets and injected terminals."""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_compact_presentation import SYSTEM, compact
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretValue

from scripts.q010_uncertainty_plan import MODEL, digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.q011_arrival.scope_rehearsal import UNIT
from scripts.q011_evidence_check import transfer_audit
from scripts.q011_transfer import evidence, plan, run, scoring

ORDER = [
    "T01-B",
    "T01-E",
    "T02-E",
    "T02-B",
    "T03-E",
    "T03-B",
    "T04-B",
    "T04-E",
    "T05-B",
    "T05-E",
    "T06-E",
    "T06-B",
    "T07-E",
    "T07-B",
    "T08-B",
    "T08-E",
]


@pytest.fixture(scope="module")
def issued(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str]:
    if not transfer_audit.ROOT.is_dir():
        pytest.skip("requires private authored admission")
    root = tmp_path_factory.mktemp("transfer") / "frozen"
    return root, plan.issue(root)


def test_frozen_bodies(issued: tuple[Path, str]) -> None:
    root, approval = issued
    m = json.loads((root / "plan.json").read_bytes())
    cells = plan.verify(root, approval)
    assert [c.name for c in cells] == ORDER
    assert [s["cell"] for s in m["slots"]] == ORDER * 2
    assert [s["stage"] for s in m["slots"]] == ["input_count"] * 16 + ["generation"] * 16
    assert m["budget"] == dict(
        input_counts=16,
        max_generations=16,
        retries=0,
        input_per_generation=16384,
        output_per_generation=4096,
        aggregate_generation_input=262144,
        aggregate_generation_output=65536,
        max_usd_per_generation="0.08192",
        aggregate_generation_usd="1.31072",
        count_seconds=120,
        generation_seconds=300,
        wall_seconds=6720,
    )
    assert (root / "gold.json").read_bytes() == (transfer_audit.ROOT / "gold.json").read_bytes()
    normalized = {}
    for count, gen in zip(m["slots"][:16], m["slots"][16:], strict=True):
        for slot in (count, gen):
            raw = (root / slot["filename"]).read_bytes()
            assert digest(raw) == slot["body_bytes_sha256"] and len(raw) == slot["http_body_bytes"]
            assert slot["destination"] == "https://api.openai.com"
        assert (count["path"], gen["path"]) == ("/v1/responses/input_tokens", "/v1/responses")
        c, g = (json.loads((root / s["filename"]).read_bytes()) for s in (count, gen))
        assert c == {k: g[k] for k in ("model", "input", "reasoning", "text")}
        assert g["model"] == MODEL and g["reasoning"] == {"effort": "high"}
        assert g["store"] is False and g["max_output_tokens"] == 4096
        assert g["input"][0] == {"role": "system", "content": SYSTEM}
        payload = json.loads(g["input"][1]["content"])
        assert set(payload) == {"active_unit_ids", "claim", "documents", "work_brief"}
        key, arm = gen["cell"].split("-")
        name = f"packets/{key}.json"
        raw = (root / name).read_bytes()
        assert raw == (transfer_audit.ROOT / name).read_bytes()
        packet = json.loads(raw)
        assert payload["claim"]["text"] == packet["claim"] and payload["active_unit_ids"] == [UNIT]
        assert set(payload["work_brief"]) == {
            "unit_id",
            "question",
            "temporal_scope",
            "source_authority",
            "evidence_obligation",
        }
        docs = {d["identity"]: d for d in payload["documents"]}
        assert set(docs) == {"plan", "context", "draft", "authored-claim", "registry"}
        assert docs["authored-claim"]["structured_content"] == {"claim": packet["claim"]}
        for role in ("context", "plan", "draft"):
            assert docs[role]["version"] == packet[role]["version"]
            assert docs[role]["structured_content"] == packet[role]["content"]
        registry = docs["registry"]
        assert registry["whole_field_locations"] == [
            ["E0233", "plan", "/outcome"],
            ["E0229", "plan", "/exit_state"],
            ["E0883", "draft", "/prose"],
        ]
        (last,) = registry["paragraph_locations"]
        prose = packet["draft"]["content"]["prose"]
        assert last["ref"] == "D01" and last["end"] == len(prose)
        assert last["quote"] == prose[last["start"] :] == prose.rsplit("\n\n", 1)[-1]
        if arm == "E":
            suffix = " " + plan.addition(packet["family"])
            brief = payload["work_brief"]
            assert brief["evidence_obligation"].endswith(suffix)
            brief["evidence_obligation"] = brief["evidence_obligation"].removesuffix(suffix)
            g["input"][1]["content"] = compact(payload)
        normalized[gen["cell"]] = g
    for key in m["cases"]:
        assert normalized[key + "-B"] == normalized[key + "-E"]
    assert [c["label"] for c in m["cases"].values()] == [
        "uncertain",
        "uncertain",
        "supported",
        "supported",
        "unsupported",
        "unsupported",
        "uncertain",
        "uncertain",
    ]
    for category in ("family", "state"):
        for group in {c[category] for c in m["cases"].values()}:
            first = [m["first_arm"][k] for k, c in m["cases"].items() if c[category] == group]
            assert first.count("B") == first.count("E")


def test_tamper_and_single_issue(issued: tuple[Path, str], tmp_path: Path) -> None:
    src, approval = issued
    root = tmp_path / "freeze"
    shutil.copytree(src, root)
    for member in (
        "packets/T08.json",
        "gold.json",
        "scoring.json",
        "evidence-form-schema.json",
        "witnesses.json",
        "requests/T02-E-input_count.json",
        "requests/T01-B-generation.json",
    ):
        p = root / member
        original = p.read_bytes()
        p.write_bytes(original + b" ")
        with pytest.raises(EvidenceError, match="frozen_member_drift"):
            plan.verify(root, approval)
        p.write_bytes(original)
    with pytest.raises(EvidenceError, match="approval_or_source_drift"):
        plan.verify(root, "0" * 64)
    with pytest.raises(FileExistsError):
        plan.issue(root)
    assert run.audit(root, approval)["ledger"] == "ready"


@pytest.mark.parametrize(
    ("fault", "sent", "last"),
    [
        ("complete", 32, "bound_unassessed"),
        ("last_count", 16, "count_rejected"),
        ("cancel", 17, "intent_without_terminal"),
        ("late_error", 32, "http_error"),
        ("missing_usage", 17, "accounting_hold"),
        ("bad_ref", 17, "invalid_claim_or_citation"),
    ],
)
def test_dispatch(
    issued: tuple[Path, str], tmp_path: Path, fault: str, sent: int, last: str
) -> None:
    src, approval = issued
    root = tmp_path / "fixture"
    shutil.copytree(src, root)
    slots = json.loads((root / "plan.json").read_bytes())["slots"]
    calls: list[str] = []

    def reply(request: httpx.Request) -> httpx.Response:
        s = slots[len(calls)]
        calls.append(s["stage"])
        assert str(request.url) == s["destination"] + s["path"]
        assert request.content == (root / s["filename"]).read_bytes()
        assert (
            root / "output" / f"{len(calls):02d}-{s['cell']}-{s['stage']}-intent.json"
        ).is_file()
        if s["stage"] == "input_count":
            return httpx.Response(
                200,
                json={
                    "input_tokens": 16385 if fault == "last_count" and len(calls) == 16 else 1500
                },
            )
        if fault == "cancel":
            raise asyncio.CancelledError
        if fault == "late_error" and len(calls) == 32:
            return httpx.Response(503, json={"error": {"code": "server_error"}})
        # Deliberate semantic misses are valid deliveries and must not stop later cells.
        answer = dict(
            support="unsupported",
            evidence=["unknown" if fault == "bad_ref" else "E0883"],
            reason="Fixture reason.",
        )
        content = dict(type="output_text", text=json.dumps({"assessments": {UNIT: answer}}))
        body = dict(
            model=MODEL,
            status="completed",
            output=[dict(type="message", role="assistant", status="completed", content=[content])],
            usage=dict(input_tokens=1500, output_tokens=100, total_tokens=1600),
        )
        if fault == "missing_usage":
            del body["usage"]
        return httpx.Response(200, json=body)

    def dispatch() -> str:
        return asyncio.run(
            run.dispatch(root, approval, httpx.MockTransport(reply), SecretValue("fixture-only"))
        )

    if fault == "cancel":
        with pytest.raises(asyncio.CancelledError):
            dispatch()
    else:
        assert dispatch() == last
    report = run.audit(root, approval)
    assert len(report["slots"]) == 32 and report["state"] == last
    assert calls == (["input_count"] * 16 + ["generation"] * 16)[:sent]
    assert all(s["state"] == "not_attempted" for s in report["slots"][sent:])
    assert not any(s["eligible"] for s in report["slots"])
    with pytest.raises(EvidenceError, match="consumed"):
        dispatch()
    assert len(calls) == sent


def score_fixture(
    root: Path, approval: str, label_misses: set[str], evidence_misses: set[str], missing: str = ""
) -> tuple[Audit, dict[str, Any], dict[str, Any], bytes]:
    # Synthetic score inputs never reach a provider or an eligible on-disk journal.
    gold = (root / "gold.json").read_bytes()
    cases = json.loads(gold)["cases"]
    witnesses = json.loads((root / "witnesses.json").read_bytes())
    rows: list[dict[str, object]] = []
    decisions = {}
    for cell in ORDER:
        key = cell.split("-")[0]
        case = cases[key]
        sid = digest(cell.encode())
        if cell == missing:
            rows.append(dict(cell=cell, stage="generation", eligible=False, state="http_error"))
            continue
        label = case["label"]
        if cell in label_misses:
            label = "unsupported" if label == "uncertain" else "uncertain"
        answer = dict(
            support=label,
            evidence=["E0233", "E0229", "E0883", "D01"],
            reason="Fixture explanation.",
        )
        rows.append(
            dict(
                cell=cell,
                stage="generation",
                eligible=True,
                state="bound_unassessed",
                final={"assessments": {UNIT: answer}},
                scoring_id=sid,
            )
        )
        spans = case["witnesses"]
        w = spans[
            {
                "approach": "approach",
                "arrival": "arrival",
                "terminal_gap": "gap",
                "earlier_gap": "renewed_motion",
            }[case["state"]]
        ]
        decisions[sid] = dict(
            case=key,
            outcome="fail" if cell in evidence_misses else "pass",
            basis="Fixture evidence review.",
            first_action=dict(ref="E0883", **spans["first_fact"]),
            passage=dict(ref="D01", **w),
            instant="at_cut",
            relation={
                "uncertain": "leaves_open",
                "unsupported": "excludes",
                "supported": "establishes",
            }[case["label"]],
        )
    report: Audit = dict(
        approval=approval,
        ledger="dispatched",
        closed=True,
        origin="observed_openai_transport",
        state="fixture",
        slots=rows,
    )
    sheet = evidence_sheet(report)
    assert all(set(r) == {"case", "claim_id", "reason", "citations", "scoring_id"} for r in sheet)
    form = dict(approval_sha256=approval, sheet_sha256=digest(encoded(sheet)), decisions=decisions)
    return report, form, witnesses, gold


@pytest.mark.parametrize(
    ("label", "ev", "missing", "expected"),
    [
        ({"T01-B"}, {"T08-B"}, "", "cross_family_recovery"),
        ({"T01-B", "T07-B"}, set(), "", "family_specific_recovery"),
        (set(), set(), "", "no_recovery_opportunity"),
        ({"T04-B"}, set(), "", "control_only_gains"),
        ({"T01-B", "T02-B"}, {"T04-E"}, "", "hold"),
        ({"T01-B"}, {"T07-E"}, "", "hold"),
        ({"T01-B", "T02-B"}, set(), "T08-E", "inconclusive"),
    ],
)
def test_join(
    issued: tuple[Path, str], label: set[str], ev: set[str], missing: str, expected: str
) -> None:
    report, form, witnesses, gold = score_fixture(*issued, label, ev, missing)
    result = scoring.scores(report, encoded(form), witnesses, gold)
    assert result["decision"] == expected
    assert set(result["unresolved"]) == {"T01", "T02", "T07", "T08"}
    assert set(result["determinate_movement"]) == {"T03", "T04", "T05", "T06"}
    if expected == "cross_family_recovery":
        assert result["pairs"]["T01"]["movement"] == dict(judgment="gain", evidence="retained_pass")
        assert result["pairs"]["T08"]["movement"] == dict(judgment="retained_pass", evidence="gain")
        assert result["baseline_joint_passes"] == ["T02", "T03", "T04", "T05", "T06", "T07"]
    if missing:
        assert result["unresolved"]["T08"]["recovered"] is None
        assert result["pairs"]["T08"]["movement"] == dict(judgment="unscored", evidence="unscored")


def test_evidence_binding(issued: tuple[Path, str]) -> None:
    report, form, witnesses, _ = score_fixture(*issued, set(), set())
    decision = form["decisions"][digest(b"T02-E")]
    # The hoist is in the second paragraph, outside the closing-paragraph citation.
    decision["first_action"]["ref"] = "D01"
    with pytest.raises(EvidenceError, match="wrong_first_action_span"):
        evidence.checked(report, encoded(form), witnesses)
    decision["first_action"]["ref"] = "E0883"
    decision["passage"]["draft_version"] = witnesses["T04"]["draft_version"]
    with pytest.raises(EvidenceError, match="wrong_position_span"):
        evidence.checked(report, encoded(form), witnesses)
