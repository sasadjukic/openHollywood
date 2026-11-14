"""Authored offline controls for observed admission, never new model evidence."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_observed_completion as service
from open_hollywood_api.services import assessment_openai_compact_smoke as smoke
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.models.assessment_openai_compact_manifest import derive_terminal
from open_hollywood_engine.secrets import SecretLeakGuard, SecretValue

from scripts import assessment_observed_completion as cli
from tests.api.test_assessment_openai_compact_smoke import frozen as frozen
from tests.api.test_assessment_openai_compact_smoke import load
from tests.api.test_assessment_openai_compact_smoke import offline as offline


@dataclass
class Capture:
    plan: smoke.Plan
    registration: service._Registration
    data: dict[str, Any]
    audit: dict[str, Any]
    output: Path


@pytest.fixture
def captured(frozen: tuple[Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch) -> Capture:
    path, data = frozen
    plan = smoke.load_plan(path)
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        n = len(calls)
        calls.append(request.url.path)
        return httpx.Response(200, json={"input_tokens": 100} if n < 4 else data["replies"][n % 4])

    async def author_journal() -> None:
        # Test-only synthetic observed-origin record in a temporary registry. It is
        # never copied into or accepted by the registered real-capture directory.
        async with smoke._client(httpx.MockTransport(handler)) as client:
            assert (
                await smoke._execute(
                    path,
                    Path(plan.live_journal),
                    client,
                    SecretValue("local-fixture-token"),
                    "observed_openai_transport",
                )
                == "complete"
            )

    asyncio.run(author_journal())
    assert len(calls) == 8
    audit = path.parent / "audit"
    smoke.audit(path, Path(plan.live_journal), audit)
    registration = service._Registration(
        "authored-test-only",
        path,
        audit,
        storage._sha(path.read_bytes()),
        storage._sha((audit / "manifest.json").read_bytes()),
    )
    monkeypatch.setattr(service, "REGISTERED", (registration,))

    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Publication must not dispatch, qualify transport or resolve a key")

    for owner, method in (
        (httpx.Client, "send"),
        (httpx.AsyncClient, "send"),
        (smoke, "run_live"),
        (smoke, "qualify"),
    ):
        monkeypatch.setattr(owner, method, deny)
    return Capture(plan, registration, data, load(audit / "audit.json"), path.parent / "output")


def test_complete_publication_exact_reuse_and_full_scope(captured: Capture) -> None:
    r = captured.registration
    source_before = service._snapshot((r.plan.parent / "live", r.audit))
    assert service.publish_observed(r.name, captured.output) == "created"
    files = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in captured.output.iterdir()}
    assert len(files) == 27
    assert service.publish_observed(r.name, captured.output) == "reused"
    assert files == {
        p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in captured.output.iterdir()
    }
    assert service._snapshot((r.plan.parent / "live", r.audit)) == source_before
    manifest = load(captured.output / "manifest.json")
    assert manifest["files_sha256"] == {
        n: storage._sha(v[0]) for n, v in files.items() if n != "manifest.json"
    }
    assert manifest["origin"] == "observed_openai_transport"
    assert manifest["source_origin"] == "registered_diagnostic_probe"
    assert not manifest["writer_dispatch_authorized"] and manifest["live_calls"] == 0
    for ref, original in zip(captured.plan.works, captured.audit["works"], strict=True):
        envelope = load(captured.output / f"{ref.name}.completion.json")
        assert envelope["intake"] == original["intake"]
        assert envelope["terminal"] == original["terminal"]
        assert envelope["completion"] == original["completion"]
        assert envelope["intake"]["assessment_result"] is None
        assert envelope["intake"]["completion_receipt"] is None
        assert "origin" not in envelope["terminal"] and "model_evidence" not in envelope["terminal"]
        assert envelope["semantic_support"] == envelope["craft"] == "unassessed"
        assert envelope["actual_billed_cost"] is None
        assert envelope["terminal"]["usage"]["cached_input_tokens"] == 10
        assert (captured.output / f"{ref.name}.intake.json").read_bytes() == Path(
            ref.intake
        ).read_bytes()
        assert service.NOTICE in (captured.output / f"{ref.name}.view.md").read_text(
            encoding="utf-8"
        )


@pytest.mark.parametrize(
    "change",
    [
        "fixture_origin",
        "wrong_plan",
        "unclosed",
        "halted",
        "unknown_usage",
        "accounting_hold",
        "missing_work",
        "duplicate_work",
        "reordered_work",
        "missing_slot",
        "undispatched",
        "writer",
        "semantic_credit",
        "invented_bill",
    ],
)
def test_audit_admission_refuses_nonobserved_partial_or_credited(
    captured: Capture, change: str
) -> None:
    value = deepcopy(captured.audit)
    if change == "fixture_origin":
        value["origin"] = "injected_transport_fixture"
    elif change == "wrong_plan":
        value["plan_sha256"] = "0" * 64
    elif change == "unclosed":
        value["journal_closed"] = False
    elif change == "halted":
        value["stop_reason"] = "halted"
    elif change == "unknown_usage":
        value["generations_with_unknown_usage"] = 1
    elif change == "accounting_hold":
        value["generations_with_accounting_hold"] = 1
    elif change == "missing_work":
        value["works"].pop()
    elif change == "duplicate_work":
        value["works"][1] = value["works"][0]
    elif change == "reordered_work":
        value["works"].reverse()
    elif change == "missing_slot":
        value["slots"].pop()
    elif change == "undispatched":
        value["slots"][0]["state"] = "not_dispatched"
    elif change == "writer":
        value["writer_dispatch_authorized"] = True
    elif change == "semantic_credit":
        value["semantic_support"] = "supported"
    else:
        value["actual_billed_cost"] = "0.01"
    with pytest.raises(ValueError):
        service._admit_audit(value, captured.plan, captured.registration.plan_sha256)
    assert not captured.output.exists()


@pytest.mark.parametrize(
    "change",
    [
        "cache_unknown",
        "excess_input",
        "length",
        "missing_slot",
        "duplicate_claim",
        "foreign_ref",
        "extra_claim",
        "request_hash",
        "changed_reason",
        "changed_intake",
        "false_complete",
    ],
)
def test_recomputed_work_rejects_accounting_delivery_and_binding(
    captured: Capture, change: str
) -> None:
    audit = deepcopy(captured.audit)
    ref = captured.plan.works[-1]  # Two active claims: no successful-sibling salvage.
    prepared = captured.data["records"][ref.preparation]
    row = audit["works"][-1]
    selected = [s for s in audit["slots"] if s["work"] == ref.name]
    exchange = selected[1]["outcome"]["exchange"]
    response = exchange["response"]
    if change == "cache_unknown":
        response["usage"]["cached_input_tokens"] = None
    elif change == "excess_input":
        response["usage"]["input_tokens"] = 272001
    elif change == "length":
        response["state"] = "length"
        response["terminal_status"] = "incomplete"
        response["incomplete_reason"] = "max_output_tokens"
    elif change in ("missing_slot", "duplicate_claim", "foreign_ref", "extra_claim"):
        value = service._object(response["raw_final"].encode())
        units = value["assessments"]
        assert isinstance(units, dict)
        first = next(iter(units))
        if change == "missing_slot":
            units.pop(first)
        elif change == "extra_claim":
            units["Q999"] = units[first]
        elif change == "foreign_ref":
            unit = units[first]
            assert isinstance(unit, dict)
            unit["evidence"] = ["not-a-location"]
        if change == "duplicate_claim":
            response["raw_final"] = '{"assessments":{"Q001":{},"Q001":{}}}'
        else:
            response["raw_final"] = encoded(value).decode()
        response["raw_final_utf8_sha256"] = storage._sha(response["raw_final"].encode())
    elif change == "request_hash":
        exchange["dispatched_body_bytes_sha256"] = "0" * 64
    elif change == "changed_reason":
        row["terminal"]["bound_result"]["units"][0]["model_assessment"]["reason"] = "Altered"
    elif change == "changed_intake":
        row["intake"]["source"]["review_id"] = "other"
    else:
        row["completion"]["binding"] = "unresolved"
    exchange["retained_response_canonical_sha256"] = canonical_sha256(response)
    if change not in ("request_hash", "changed_reason", "changed_intake", "false_complete"):
        outcomes = [smoke.Outcome.model_validate_json(encoded(s["outcome"])) for s in selected]
        terminal = derive_terminal(
            prepared.collected.context,
            prepared.request_set.payload.requests[0],
            tuple(o.exchange for o in outcomes),
            sum(o.elapsed_seconds for o in outcomes),
        )
        row["terminal"] = terminal.model_dump(
            mode="json", exclude={"contract", "origin", "model_evidence"}
        )
        # Keep the positive native eligibility flag: it must not bypass accounting.
        assert row["completion_eligible"] is True
        if change in ("cache_unknown", "excess_input"):
            assert terminal.bound_result is not None and terminal.accounting_hold
    with pytest.raises(ValueError):
        service._work_files(ref, prepared, row, audit, {})
    assert not captured.output.exists()


@pytest.mark.parametrize(
    "change", ["plan", "audit", "journal", "preparation", "source", "extra_audit"]
)
def test_registered_source_changes_refused(captured: Capture, change: str) -> None:
    r, work = captured.registration, captured.plan.works[0]
    target = {
        "plan": r.plan,
        "audit": r.audit / "audit.json",
        "journal": Path(captured.plan.live_journal) / "event-0002.json",
        "preparation": Path(work.preparation) / "local-provenance.json",
        "source": Path(work.intake),
        "extra_audit": r.audit / "extra.json",
    }[change]
    target.write_bytes((target.read_bytes() if target.exists() else b"{}") + b" ")
    with pytest.raises((ValueError, AssertionError)):
        service.publish_observed(r.name, captured.output)
    assert not captured.output.exists()


def test_unregistered_and_protected_destination(captured: Capture) -> None:
    with pytest.raises(ValueError, match="unregistered"):
        service.publish_observed("arbitrary", captured.output)
    with pytest.raises(ValueError, match="protected_path"):
        service.publish_observed(captured.registration.name, captured.registration.audit / "output")
    assert not (captured.registration.audit / "output").exists()


@pytest.mark.parametrize("change", ["write_failure", "source_drift", "implementation_drift"])
def test_manifest_last_failure_preserved(
    captured: Capture, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    original = storage._write_new
    writes: list[str] = []

    def write(path: Path, data: bytes) -> None:
        writes.append(path.name)
        if len(writes) == 2 and change == "write_failure":
            raise OSError("authored write failure")
        original(path, data)
        if len(writes) == 1 and change == "source_drift":
            (Path(captured.plan.works[0].preparation) / "extra.json").write_bytes(b"{}")
        elif len(writes) == 1 and change == "implementation_drift":
            monkeypatch.setattr(service, "_implementation", lambda: {"changed": True})

    monkeypatch.setattr(storage, "_write_new", write)
    with pytest.raises((OSError, ValueError)):
        service.publish_observed(captured.registration.name, captured.output)
    assert captured.output.is_dir() and not (captured.output / "manifest.json").exists()
    assert "manifest.json" not in writes


def test_existing_partial_or_extra_output_never_repaired(captured: Capture) -> None:
    captured.output.mkdir()
    marker = captured.output / "keep.json"
    marker.write_bytes(b"{}")
    with pytest.raises(ValueError, match="output_conflict"):
        service.publish_observed(captured.registration.name, captured.output)
    assert [p.name for p in captured.output.iterdir()] == ["keep.json"]
    assert marker.read_bytes() == b"{}"


def test_secret_refusal_cli_sanitized_and_no_output(
    captured: Capture, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    guard = SecretLeakGuard((SecretValue("Authored fixture"),))
    monkeypatch.setattr(storage, "active_secret_guard", lambda: guard)
    assert cli.main(["--source", captured.registration.name, "--output", str(captured.output)]) == 2
    assert (
        capsys.readouterr().out.strip() == '{"error": "secret_guard_rejected_observed_completion"}'
    )
    assert not captured.output.exists()
