"""Actual-byte fixture capture, durable intent, read-only audit and source protection."""

from __future__ import annotations

import json
import os
import socket
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services import assessment_delivery as service
from open_hollywood_api.services import assessment_intake as intake_service
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_delivery import Endpoint, parse_request_set
from open_hollywood_engine.evaluations.review_evidence import JsonObject
from open_hollywood_engine.secrets import SecretLeakError

from scripts import assessment_delivery as cli
from tests.api.test_assessment_completion import prepare, snapshot
from tests.assessment_delivery_fixtures import fixtures_for, safe_response
from tests.assessment_intake_fixtures import choice_for, plan_for


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Fixture capture must not access network or SQLite")

    for owner, name in (
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "create_connection"),
        (socket, "getaddrinfo"),
        (httpx.Client, "send"),
        (httpx.AsyncClient, "send"),
        (sqlite3, "connect"),
    ):
        monkeypatch.setattr(owner, name, deny)


@dataclass
class Delivery:
    intake: Path
    preparation: Path
    fixtures: Path
    journal: Path
    audit: Path


def setup_delivery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, multi: bool = False
) -> Delivery:
    previous = prepare(tmp_path, monkeypatch)
    intake = previous.intake
    if multi:
        collection = intake_service.collect_intakes(
            "diagnostic_probe", previous.fixture.live, (previous.fixture.trial,)
        )
        source = collection.entries[0].source
        assert source is not None
        fields = source.inventory_work.context.report_fields
        plan = plan_for(
            source, choice_for(source, fields[0].field_id), choice_for(source, fields[1].field_id)
        )
        plans = intake_service.IntakeBatchPlan(
            plans={source.review_id: plan.model_copy(update={"maximum_units": 1})}
        )
        intake = tmp_path / "multi-intake" / "review-01.json"
        intake_service.write_intake(intake.parent, collection, plans)
    p = Delivery(
        intake,
        tmp_path / "requests",
        tmp_path / "fixtures.json",
        tmp_path / "journal",
        tmp_path / "audit",
    )
    assert service.prepare_requests(p.intake, p.preparation, run_id="local-test") == "created"
    request_set = parse_request_set((p.preparation / "request-set.json").read_bytes())
    finals = {
        m.payload.batch_id: json.dumps(
            {
                "assessments": {
                    u: {
                        "support": "uncertain",
                        "evidence": [],
                        "reason": "Authored only 🔑 ``` </script>",
                    }
                    for u in m.payload.active_unit_ids
                }
            }
        )
        for m in request_set.payload.requests
    }
    p.fixtures.write_bytes(encoded(fixtures_for(request_set, finals)))
    return p


@pytest.fixture
def delivery(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Delivery:
    return setup_delivery(tmp_path, monkeypatch)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def capture(p: Delivery) -> str:
    return service.capture_fixtures(p.intake, p.preparation, p.fixtures, p.journal)


def audit(p: Delivery) -> dict[str, Any]:
    assert service.audit_terminal(p.intake, p.preparation, p.journal, p.audit) == "created"
    return load(p.audit / "audit.json")


def alter_response(p: Delivery, index: int, **updates: Any) -> None:
    data = load(p.fixtures)
    body = json.loads(data["replies"][index]["response_body_utf8"])
    body.update(updates)
    data["replies"][index]["response_body_utf8"] = json.dumps(body)
    p.fixtures.write_bytes(encoded(data))


def test_registered_source_prepare_capture_audit_and_exact_reuse(delivery: Delivery) -> None:
    p = delivery
    before = snapshot(p.intake.parent), snapshot(p.preparation)
    assert service.prepare_requests(p.intake, p.preparation, run_id="local-test") == "reused"
    assert capture(p) == "complete"
    journal_before = snapshot(p.journal)
    result = audit(p)
    assert result["completion_eligible"] and result["publication_state"] == "bound_unassessed"
    assert result["completion"]["known_input_tokens"] == 100
    assert result["fixture_count_attempts"] == result["fixture_generation_attempts"] == 1
    assert result["intake"] == load(p.intake)
    assert not result["writer_dispatch_authorized"] and not result["model_evidence"]
    assert result["source_receipt"]["assessment_delivery_authenticated"] is False
    assert result["actual_billed_cost"] is None and result["evidence_adequacy"] == "unassessed"
    view = (p.audit / "view.md").read_text(encoding="utf-8")
    assert json.loads(view.split("````json\n")[1].rsplit("\n````", 1)[0]) == result
    output_before = snapshot(p.audit)
    assert service.audit_terminal(p.intake, p.preparation, p.journal, p.audit) == "reused"
    assert output_before == snapshot(p.audit) and journal_before == snapshot(p.journal)
    assert before == (snapshot(p.intake.parent), snapshot(p.preparation))
    with pytest.raises(ValueError, match="journal_already_exists_no_retry"):
        capture(p)
    assert journal_before == snapshot(p.journal)


def test_intent_is_flushed_before_injected_transport_and_captures_observed_body(
    delivery: Delivery,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p = delivery
    fixture = load(p.fixtures)
    calls: list[bytes] = []
    flushes: list[int] = []
    fsync = os.fsync

    def sync(fd: int) -> None:
        flushes.append(fd)
        fsync(fd)

    monkeypatch.setattr(os, "fsync", sync)

    def handle(request: httpx.Request) -> httpx.Response:
        n = len(calls)
        event = load(p.journal / f"event-{2 * n + 1:04d}.json")["payload"]
        assert event["kind"] == "intent"
        assert event["endpoint"]["body_utf8"].encode("utf-8") == request.content
        assert len(flushes) >= 3 + 2 * n
        calls.append(request.content)
        # Observed safe response IDs are retained even when absent from the authored reply file.
        body = json.loads(fixture["replies"][n]["response_body_utf8"])
        body["response_id"] = "observed-fixture-id"
        return httpx.Response(200, content=encoded(body))

    assert (
        service.capture_fixtures(
            p.intake, p.preparation, p.fixtures, p.journal, transport=httpx.MockTransport(handle)
        )
        == "complete"
    )
    result = audit(p)
    assert len(calls) == 2
    exchange = result["terminals"][0]["evidence"]["exchanges"][-1]
    assert exchange["retained_response"]["response_id"] == "observed-fixture-id"
    assert (
        exchange["observed_raw_http_bytes_sha256"] != exchange["retained_response_canonical_sha256"]
    )
    assert exchange["raw_http_bytes_retained"] is False


@pytest.mark.parametrize("mutation", ["body", "destination", "method", "headers"])
def test_actual_request_mismatch_refused_before_callback(
    delivery: Delivery, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    build = service._build_request
    calls: list[bool] = []

    def changed(endpoint: Endpoint) -> httpx.Request:
        req = build(endpoint)
        return httpx.Request(
            "GET" if mutation == "method" else req.method,
            "https://other.invalid" if mutation == "destination" else req.url,
            content=req.content + b" " if mutation == "body" else req.content,
            headers={"x-api-key": "fixture-only"} if mutation == "headers" else None,
        )

    monkeypatch.setattr(service, "_build_request", changed)

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(True)
        return httpx.Response(200)

    with pytest.raises(ValueError):
        service.capture_fixtures(
            delivery.intake,
            delivery.preparation,
            delivery.fixtures,
            delivery.journal,
            transport=httpx.MockTransport(handle),
        )
    assert not calls and set(snapshot(delivery.journal)) == {"header.json", "fixtures.json"}
    result = audit(delivery)
    assert not result["completion_eligible"] and result["fixture_generation_attempts"] == 0


@pytest.mark.parametrize(
    "stage,behavior", [(0, "interrupt"), (1, "interrupt"), (1, "cancelled"), (1, "transport_error")]
)
def test_interrupted_and_failed_transport_consumes_intent_without_retry(
    delivery: Delivery, stage: int, behavior: str
) -> None:
    p = delivery
    data = load(p.fixtures)
    data["replies"][stage].update(behavior=behavior, http_status=None, response_body_utf8="")
    p.fixtures.write_bytes(encoded(data))
    if behavior == "interrupt":
        with pytest.raises(service.FixtureInterrupted):
            capture(p)
    else:
        assert capture(p) == "halted"
    before = snapshot(p.journal)
    result = audit(p)
    assert not result["completion_eligible"]
    assert result["fixture_count_attempts"] == 1
    assert result["fixture_generation_attempts"] == stage
    assert result["unknown_elapsed_endpoints"] == int(behavior == "interrupt")
    assert result["journal_closed"] == (behavior != "interrupt")
    if stage:
        assert result["terminals"][0]["usage_state"] == "unknown"
        assert result["completion"]["unknown_usage_attempts"] == 1
    with pytest.raises(ValueError, match="no_retry"):
        capture(p)
    assert snapshot(p.journal) == before


@pytest.mark.parametrize(
    "failure",
    [
        "length",
        "refusal",
        "empty",
        "malformed_final",
        "malformed_http",
        "extra_field",
        "wrong_model",
        "non200",
    ],
)
def test_terminal_failures_are_exported_without_success(delivery: Delivery, failure: str) -> None:
    p = delivery
    if failure in {"length", "refusal"}:
        alter_response(p, 1, state=failure)
    elif failure == "empty":
        alter_response(p, 1, raw_final="")
    elif failure == "malformed_final":
        alter_response(p, 1, raw_final="{")
    elif failure == "extra_field":
        alter_response(p, 1, reasoning_text="This undeclared content must not be retained")
    elif failure == "wrong_model":
        alter_response(p, 1, returned_model="unexpected")
    else:
        data = load(p.fixtures)
        if failure == "malformed_http":
            data["replies"][1]["response_body_utf8"] = "{"
        else:
            data["replies"][1]["http_status"] = 500  # Body still claims complete/200.
        p.fixtures.write_bytes(encoded(data))
    assert capture(p) == "halted"
    result = audit(p)
    assert not result["completion_eligible"]
    assert result["terminals"][0]["state"] == "failed"
    assert result["terminals"][0]["bound_result"] is None


def test_non200_gateway_chain_and_unknown_usage_remain_visible(delivery: Delivery) -> None:
    chain = [
        {
            "layer": layer,
            "category": "unavailable",
            "code": "500",
            "safe_message": "Authored failure",
        }
        for layer in ["daemon", "gateway", "provider"]
    ]
    usage = dict.fromkeys(
        ["input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens"]
    )
    alter_response(
        delivery, 1, http_status=500, state="error", error_chain=chain, usage=usage, raw_final=None
    )
    data = load(delivery.fixtures)
    data["replies"][1]["http_status"] = 500
    delivery.fixtures.write_bytes(encoded(data))
    assert capture(delivery) == "halted"
    result = audit(delivery)
    terminal = result["terminals"][0]
    assert terminal["failure_code"] == "non_200" and terminal["usage_state"] == "unknown"
    assert terminal["evidence"]["exchanges"][-1]["retained_response"]["error_chain"] == chain


@pytest.mark.parametrize(
    "failure",
    ["count_error", "count_unknown", "unknown_usage", "partial_usage", "generation_failure"],
)
def test_global_stop_prevents_later_batches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    p = setup_delivery(tmp_path, monkeypatch, multi=True)
    if failure == "count_error":
        alter_response(p, 0, state="error")
    elif failure == "count_unknown":
        alter_response(p, 0, counted_input_tokens=None)
    elif failure == "generation_failure":
        alter_response(p, 1, state="length")
    else:
        usage = dict.fromkeys(
            ["input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens"]
        )
        if failure == "partial_usage":
            usage["input_tokens"] = 100
        alter_response(p, 1, usage=usage)
    assert capture(p) == "halted"
    result = audit(p)
    assert not result["completion_eligible"] and len(result["terminals"]) == 2
    assert result["terminals"][1]["state"] == "generation_not_started"
    assert result["fixture_generation_attempts"] == int(not failure.startswith("count"))


def test_unknown_usage_can_bind_last_batch_without_claiming_known_cost(delivery: Delivery) -> None:
    alter_response(
        delivery,
        1,
        usage=dict.fromkeys(
            ["input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens"]
        ),
    )
    assert capture(delivery) == "halted"
    result = audit(delivery)
    assert result["completion_eligible"] and result["stop_reason"] == "halted"
    assert result["completion"]["unknown_usage_attempts"] == 1
    assert (
        result["actual_billed_cost"] is None and not result["terminals"][0]["next_dispatch_allowed"]
    )


def test_cancel_before_dispatch_has_no_attempts(delivery: Delivery) -> None:
    data = load(delivery.fixtures)
    data["cancel_before_dispatch"] = True
    delivery.fixtures.write_bytes(encoded(data))
    assert capture(delivery) == "cancelled_before_dispatch"
    result = audit(delivery)
    assert result["fixture_count_attempts"] == result["fixture_generation_attempts"] == 0
    assert result["terminals"][0]["native_receipt"] is None and not result["completion_eligible"]


@pytest.mark.parametrize(
    "mutation",
    ["header", "body", "chain", "gap", "duplicate_key", "extra", "forged_origin", "stop"],
)
def test_journal_tampering_is_refused(delivery: Delivery, mutation: str) -> None:
    p = delivery
    capture(p)
    path = p.journal / "event-0001.json"
    if mutation == "gap":
        path.unlink()
    elif mutation == "extra":
        (p.journal / "extra").write_text("{}", encoding="utf-8")
    elif mutation == "duplicate_key":
        path.write_bytes(path.read_bytes().replace(b'"sequence": 1', b'"sequence":1,"sequence":1'))
    else:
        if mutation in {"header", "forged_origin"}:
            path = p.journal / "header.json"
        elif mutation == "stop":
            path = p.journal / "event-0005.json"
        value = load(path)
        if mutation == "body":
            value["payload"]["endpoint"]["body_utf8"] += " "
        elif mutation == "header":
            value["request_set_canonical_sha256"] = "f" * 64
        elif mutation == "forged_origin":
            value["origin"] = "authenticated_model_delivery"
        elif mutation == "stop":
            value["payload"]["reason"] = "halted"
        else:
            value["previous_bytes_sha256"] = "f" * 64
        path.write_bytes(encoded(value))
    before = snapshot(p.journal)
    with pytest.raises(ValueError):
        service.audit_terminal(p.intake, p.preparation, p.journal, p.audit)
    assert snapshot(p.journal) == before and not p.audit.exists()


def test_missing_final_stop_keeps_journal_incomplete(delivery: Delivery) -> None:
    capture(delivery)
    (delivery.journal / "event-0005.json").unlink()
    result = audit(delivery)
    assert result["completion"]["complete_delivery"]
    assert not result["completion_eligible"] and not result["journal_closed"]


@pytest.mark.parametrize("where", ["preparation", "intake", "journal", "ancestor"])
def test_protected_output_paths_are_refused(delivery: Delivery, where: str) -> None:
    p = delivery
    capture(p)
    output = {
        "preparation": p.preparation / "output",
        "intake": p.intake.parent / "output",
        "journal": p.journal / "output",
        "ancestor": p.intake.parent.parent,
    }[where]
    with pytest.raises(ValueError, match="completion_protected_path"):
        service.audit_terminal(p.intake, p.preparation, p.journal, output)


@pytest.mark.parametrize("kind", ["partial", "changed", "extra"])
def test_audit_output_is_not_silently_repaired(delivery: Delivery, kind: str) -> None:
    capture(delivery)
    audit(delivery)
    if kind == "partial":
        (delivery.audit / "manifest.json").unlink()
    elif kind == "changed":
        (delivery.audit / "audit.json").write_bytes(b"changed")
    else:
        (delivery.audit / "extra").write_bytes(b"extra")
    before = snapshot(delivery.audit)
    with pytest.raises(ValueError):
        service.audit_terminal(
            delivery.intake, delivery.preparation, delivery.journal, delivery.audit
        )
    assert snapshot(delivery.audit) == before


def test_response_secret_is_not_persisted_and_cannot_complete(
    delivery: Delivery, monkeypatch: pytest.MonkeyPatch
) -> None:
    p = delivery
    sentinel = "private-value-that-must-not-be-retained"

    class Guard:
        def ensure_safe(self, value: Any, **kwargs: Any) -> None:
            if sentinel in str(value):
                raise SecretLeakError("fixture", "$")

    monkeypatch.setattr(service, "active_secret_guard", lambda: Guard())

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("count"):
            return httpx.Response(
                200, content=safe_response(counted_input_tokens=5).model_dump_json()
            )
        return httpx.Response(200, content=safe_response(sentinel).model_dump_json())

    assert (
        service.capture_fixtures(
            p.intake, p.preparation, p.fixtures, p.journal, transport=httpx.MockTransport(handle)
        )
        == "halted"
    )
    assert all(sentinel.encode() not in data for data, _ in snapshot(p.journal).values())
    result = audit(p)
    assert result["terminals"][0]["evidence"]["exchanges"][-1]["disposition"] == "capture_error"
    assert not result["completion_eligible"]


def test_cli_interrupt_and_redacted_errors(
    delivery: Delivery, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    p = delivery
    data = load(p.fixtures)
    data["replies"][1].update(behavior="interrupt", http_status=None, response_body_utf8="")
    p.fixtures.write_bytes(encoded(data))
    args = [
        "capture-fixture",
        "--intake",
        str(p.intake),
        "--preparation",
        str(p.preparation),
        "--fixtures",
        str(p.fixtures),
        "--output",
        str(p.journal),
    ]
    assert cli.main(args) == 130
    assert json.loads(capsys.readouterr().out)["status"] == "interrupted_no_retry"
    assert (
        cli.main(
            [
                "audit",
                "--intake",
                str(p.intake),
                "--preparation",
                str(p.preparation),
                "--journal",
                str(p.journal),
                "--output",
                str(p.audit),
            ]
        )
        == 0
    )
    capsys.readouterr()

    def fail(*args: Any, **kwargs: Any) -> Any:
        raise ValueError("UNPUBLISHED_PROSE")

    monkeypatch.setattr(cli, "capture_fixtures", fail)
    assert cli.main(args) == 2
    assert "UNPUBLISHED" not in capsys.readouterr().out


def test_source_drift_between_endpoints_prevents_generation(
    delivery: Delivery,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p = delivery
    original = p.intake.read_bytes()
    calls: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        p.intake.write_bytes(original + b" ")
        return httpx.Response(200, content=safe_response(counted_input_tokens=1).model_dump_json())

    with pytest.raises(ValueError):
        service.capture_fixtures(
            p.intake, p.preparation, p.fixtures, p.journal, transport=httpx.MockTransport(handle)
        )
    assert calls == ["/fixture/count"]
    with pytest.raises(ValueError):
        service.audit_terminal(p.intake, p.preparation, p.journal, p.audit)
    assert not p.audit.exists()
    p.intake.write_bytes(original)  # Authored test-only source restoration.
    result = audit(p)
    assert not result["journal_closed"] and result["fixture_generation_attempts"] == 0


def test_journal_change_after_render_prevents_publication(
    delivery: Delivery,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    capture(delivery)
    render = service._literal

    def changing(title: str, value: JsonObject) -> bytes:
        if title == "Fixture terminal audit":
            (delivery.journal / "header.json").write_bytes(b"{}")
        return render(title, value)

    monkeypatch.setattr(service, "_literal", changing)
    with pytest.raises(ValueError, match="journal_changed_during_audit"):
        service.audit_terminal(
            delivery.intake, delivery.preparation, delivery.journal, delivery.audit
        )
    assert not delivery.audit.exists()


def test_fsync_failure_never_reaches_transport(
    delivery: Delivery, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = os.fsync
    calls: list[bool] = []
    flushes: list[int] = []

    def failed(fd: int) -> None:
        flushes.append(fd)
        if len(flushes) == 3:
            raise OSError("Simulated disk failure before intent durability")
        original(fd)

    monkeypatch.setattr(os, "fsync", failed)

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(True)
        return httpx.Response(200)

    with pytest.raises(OSError):
        service.capture_fixtures(
            delivery.intake,
            delivery.preparation,
            delivery.fixtures,
            delivery.journal,
            transport=httpx.MockTransport(handle),
        )
    assert not calls


@pytest.mark.parametrize("limit", ["MAX_RESPONSE_BYTES", "MAX_BYTES"])
def test_resource_limit_prevents_success(
    delivery: Delivery, monkeypatch: pytest.MonkeyPatch, limit: str
) -> None:
    if limit == "MAX_RESPONSE_BYTES":

        def oversized(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"x" * (service.MAX_RESPONSE_BYTES + 1))

        assert (
            service.capture_fixtures(
                delivery.intake,
                delivery.preparation,
                delivery.fixtures,
                delivery.journal,
                transport=httpx.MockTransport(oversized),
            )
            == "halted"
        )
        result = audit(delivery)
        assert result["fixture_generation_attempts"] == 0 and not result["completion_eligible"]
    else:
        monkeypatch.setattr(service, limit, 1)
        with pytest.raises(ValueError):
            capture(delivery)
        assert not delivery.journal.exists()


def test_predeclared_generation_only_request_and_template_author_required(
    delivery: Delivery,
) -> None:
    p = delivery
    p.preparation = p.preparation.with_name("no-count-requests")
    assert (
        service.prepare_requests(p.intake, p.preparation, run_id="no-count", with_count=False)
        == "created"
    )
    request_set = parse_request_set((p.preparation / "request-set.json").read_bytes())
    template = (p.preparation / "fixtures.template.json").read_bytes()
    with pytest.raises(ValueError):
        service.parse_fixtures(template, request_set)
    raw = json.loads(load(p.fixtures)["replies"][-1]["response_body_utf8"])["raw_final"]
    p.fixtures.write_bytes(
        encoded(fixtures_for(request_set, {request_set.payload.requests[0].payload.batch_id: raw}))
    )
    assert capture(p) == "complete"
    result = audit(p)
    assert result["completion_eligible"] and result["fixture_count_attempts"] == 0


def test_transport_type_cannot_select_a_real_client(delivery: Delivery) -> None:
    bad_transport: Any = object()
    with pytest.raises(ValueError, match="fixture_transport_required"):
        service.capture_fixtures(
            delivery.intake,
            delivery.preparation,
            delivery.fixtures,
            delivery.journal,
            transport=bad_transport,
        )
    assert not delivery.journal.exists()


def test_supported_schema_files_match_parsers() -> None:
    from open_hollywood_engine.evaluations.assessment_delivery import (
        RequestSet,
        RetainedResponse,
        TerminalEvidence,
        TerminalReceipt,
    )

    root = Path(__file__).resolve().parents[2]
    for name, model in (
        ("assessment-fixture-request-set-1", RequestSet),
        ("assessment-fixture-terminal-evidence-1", TerminalEvidence),
        ("assessment-fixture-terminal-receipt-1", TerminalReceipt),
        ("assessment-fixture-safe-response-1", RetainedResponse),
        ("assessment-transport-fixtures-1", service.TransportFixtures),
        ("assessment-fixture-journal-event-1", service.JournalEvent),
    ):
        schema = model.model_json_schema()
        schema["$comment"] = (
            "Runtime fixture-only contract. Source, actual-byte capture and completion "
            "are verified "
            "by the application; shape or caller hashes do not authenticate a model delivery."
        )
        assert (root / "docs/contracts" / (name + ".schema.json")).read_bytes() == encoded(schema)
