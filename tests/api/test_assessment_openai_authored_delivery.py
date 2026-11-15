"""Authored source/wire/journal qualification using injected transport only."""

from __future__ import annotations

import json
import os
import socket
import sqlite3
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services import assessment_authored_source as source_service
from open_hollywood_api.services import assessment_delivery as io
from open_hollywood_api.services import assessment_openai_authored_delivery as service
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import scope_for_batch
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.models import assessment_openai_authored as domain
from open_hollywood_engine.models.assessment_openai import check_outgoing, map_response
from open_hollywood_engine.models.contracts import ModelMessage
from open_hollywood_engine.secrets import EnvironmentSecretStore

from scripts import assessment_openai_authored_delivery as cli
from tests.authored_source_fixtures import make_archive, submission
from tests.evaluations.test_assessment_presentation import settings
from tests.models.test_assessment_openai import provider_body


def load(path: Path) -> Any:
    return json.loads(path.read_bytes())


def pins(path: Path) -> dict[str, tuple[bytes, int]]:
    return {
        p.relative_to(path).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
        for p in path.rglob("*")
        if p.is_file()
    }


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Network, clients, credentials and database forbidden")

    for target, name in (
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "getaddrinfo"),
        (httpx, "Client"),
        (httpx, "AsyncClient"),
        (sqlite3, "connect"),
        (EnvironmentSecretStore, "get"),
    ):
        monkeypatch.setattr(target, name, deny)
    # Keep pattern-based refusal active without resolving real secrets in test fixtures.
    monkeypatch.setattr(EnvironmentSecretStore, "configured_values", lambda self: ())


@dataclass
class Prepared:
    root: Path
    archive: Path
    preparation: Path
    loaded: service._Prepared


@pytest.fixture(scope="module")
def prepared(tmp_path_factory: pytest.TempPathFactory) -> Any:
    root = tmp_path_factory.mktemp("authored-openai")
    archive = root / "archive"
    with pytest.MonkeyPatch.context() as patcher:
        patcher.setattr(source_service, "REGISTERED", (make_archive(archive),))
        preparation = root / "preparation"
        assert (
            service.prepare_requests(
                source_service.SOURCE_ID, preparation, run_id="fixture-test", settings=settings()
            )
            == "created"
        )
        yield Prepared(
            root, archive, preparation, service._load(source_service.SOURCE_ID, preparation)
        )


def fixtures(p: Prepared, tmp: Path) -> tuple[Path, dict[str, Any]]:
    value = load(p.preparation / "fixtures.template.json")
    value["authored_by"] = "Authored OpenAI transport qualification; no model evidence"
    for reply, (manifest, endpoint) in zip(
        value["replies"], domain.ordered_endpoints(p.loaded.request_set), strict=True
    ):
        source = service._source_for(p.loaded, manifest)
        body = (
            {"input_tokens": 100}
            if endpoint.stage == "input_count"
            else provider_body(submission(source)["raw_final"])
        )
        reply["response_body_utf8"] = encoded(body).decode()
    path = tmp / "fixtures.json"
    path.write_bytes(encoded(value))
    return path, value


def capture(p: Prepared, path: Path, journal: Path, **kwargs: Any) -> str:
    return service.capture_fixtures(
        source_service.SOURCE_ID, p.preparation, path, journal, **kwargs
    )


def audit(p: Prepared, journal: Path) -> dict[str, Any]:
    return dict(service._audit(p.loaded, io._read_journal(journal)))


def test_mapping_exact_full_context_and_all_counts_first(prepared: Prepared) -> None:
    plan = prepared.loaded.request_set
    order = domain.ordered_endpoints(plan)
    assert [e.stage for _, e in order] == ["input_count"] * 3 + ["generation"] * 3
    for c, m in zip(prepared.loaded.collected, plan.payload.requests, strict=True):
        count, generation = [json.loads(e.body_utf8) for e in m.payload.endpoints]
        presentation = m.payload.presentation
        assert (
            count["input"]
            == generation["input"]
            == [v.model_dump(mode="json") for v in presentation.messages]
        )
        assert set(count) == {"model", "input", "text", "reasoning"}
        assert count["text"] == generation["text"] and count["reasoning"] == {"effort": "high"}
        assert generation["truncation"] == "disabled" and generation["store"] is False
        visible = json.loads(count["input"][1]["content"])
        assert visible["full_original_work"] == c.source.work.model_dump(mode="json")
        assert len(visible["whole_field_dispositions"]) == 4
        assert "OPERATOR_ONLY_GOLD_SENTINEL" not in m.model_dump_json()
        assert m.payload.work_sha256 == c.source.work.fingerprint
        assert c.source.work.context.provenance == "synthetic_fixture"
        assert c.source.result is None and c.source.receipt is None
        assert m.payload_canonical_sha256 != c.source.original_scope.request_sha256
        assert (
            m.payload.source.source_origin == "authored_diagnostic"
            and not m.payload.live_authorized
        )


def test_complete_durable_intent_exact_bytes_and_export(
    prepared: Prepared, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture_path, value = fixtures(prepared, tmp_path)
    journal = tmp_path / "journal"
    before, original = pins(prepared.preparation), pins(prepared.archive)
    syncs = []
    fsync = os.fsync

    def sync(fd: int) -> None:
        fsync(fd)
        syncs.append(fd)

    monkeypatch.setattr(os, "fsync", sync)
    replies = iter(value["replies"])
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        index = len(calls) * 2 + 1
        intent = load(journal / f"event-{index:04d}.json")["payload"]
        assert len(syncs) >= index + 2
        assert intent["endpoint"]["body_utf8"].encode() == request.content
        assert "authorization" not in request.headers
        calls.append(intent["endpoint"]["stage"])
        reply = next(replies)
        return httpx.Response(reply["http_status"], content=reply["response_body_utf8"].encode())

    assert (
        capture(prepared, fixture_path, journal, transport=httpx.MockTransport(handler))
        == "complete"
    )
    assert calls == ["input_count"] * 3 + ["generation"] * 3
    result = audit(prepared, journal)
    assert (
        result["completion_eligible"] and result["journal_closed"] and not result["accounting_hold"]
    )
    assert result["fixture_count_attempts"] == result["fixture_generation_attempts"] == 3
    assert all(s["consumed"] for s in result["slots"])
    assert all(c["complete_delivery"] and c["binding"] == "complete" for c in result["completions"])
    assert all(t["usage"]["cached_input_tokens"] == 10 for t in result["terminals"])
    assert result["factual_support"] == "unassessed" and not result["model_evidence"]
    assert not result["writer_dispatch_authorized"] and result["actual_billed_cost"] is None
    out = tmp_path / "audit"
    assert (
        service.audit_terminal(source_service.SOURCE_ID, prepared.preparation, journal, out)
        == "created"
    )
    saved = pins(out)
    assert (
        service.audit_terminal(source_service.SOURCE_ID, prepared.preparation, journal, out)
        == "reused"
    )
    assert (
        pins(out) == saved
        and pins(prepared.preparation) == before
        and pins(prepared.archive) == original
    )
    assert set(p.name for p in out.glob("*-evidence.md")) == {
        "F01-evidence.md",
        "F02-evidence.md",
        "F03-evidence.md",
    }
    with pytest.raises(ValueError, match="journal_already_exists_no_retry"):
        capture(prepared, fixture_path, journal)


@pytest.mark.parametrize("slot", range(6))
def test_interrupted_intents_consume_exact_fixed_slot(
    prepared: Prepared, tmp_path: Path, slot: int
) -> None:
    path, value = fixtures(prepared, tmp_path)
    value["replies"][slot].update(behavior="interrupt", http_status=None, response_body_utf8="")
    path.write_bytes(encoded(value))
    journal = tmp_path / "journal"
    with pytest.raises(io.FixtureInterrupted):
        capture(prepared, path, journal)
    before = pins(journal)
    result = audit(prepared, journal)
    assert not result["journal_closed"] and not result["completion_eligible"]
    assert sum(s["consumed"] for s in result["slots"]) == slot + 1
    assert result["slots"][slot]["status"] == "interrupted"
    assert all(s["status"] == "undispatched" for s in result["slots"][slot + 1 :])
    assert result["unknown_elapsed_endpoints"] == 1 and not result["next_dispatch_allowed"]
    assert result["fixture_count_attempts"] == min(slot + 1, 3)
    assert result["fixture_generation_attempts"] == max(slot - 2, 0)
    assert pins(journal) == before


@pytest.mark.parametrize(
    "mode",
    [
        "count_500",
        "count_missing",
        "count_over",
        "count_transport",
        "cancelled",
        "generation_500",
        "length",
        "refusal",
        "empty",
        "duplicate_id",
        "bad_ref",
        "missing_unit",
        "extra_field",
        "wrong_model",
        "unknown_usage",
        "over_usage",
    ],
)
def test_terminal_failures_stop_and_preserve_evidence(
    prepared: Prepared, tmp_path: Path, mode: str
) -> None:
    path, value = fixtures(prepared, tmp_path)
    index = 1 if mode.startswith("count_") else 3
    reply = value["replies"][index]
    body = json.loads(reply["response_body_utf8"])
    if mode in ("count_500", "generation_500"):
        reply["http_status"] = 500
        body = {"error": {"code": "server_error", "message": "fixture gateway failure"}}
    elif mode == "count_missing":
        body = {}
    elif mode == "count_over":
        body["input_tokens"] = 24001
    elif mode in ("count_transport", "cancelled"):
        reply.update(
            behavior="cancelled" if mode == "cancelled" else "transport_error",
            http_status=None,
            response_body_utf8="",
        )
    elif mode == "length":
        body.update(status="incomplete", incomplete_details={"reason": "max_output_tokens"})
    elif mode == "refusal":
        body["output"][1]["content"] = [{"type": "refusal", "refusal": "fixture"}]
    elif mode == "wrong_model":
        body["model"] = "wrong-model"
    elif mode == "unknown_usage":
        body["usage"].pop("input_tokens_details")
    elif mode == "over_usage":
        body["usage"].update(input_tokens=24001, total_tokens=24021)
    else:
        final = body["output"][1]["content"][0]["text"]
        if mode == "empty":
            final = ""
        elif mode == "duplicate_id":
            final = final.replace('"Q001":', '"Q002":')
        else:
            parsed = json.loads(final)
            if mode == "bad_ref":
                parsed["assessments"]["Q001"]["evidence"] = ["S404"]
            elif mode == "missing_unit":
                parsed["assessments"].pop("Q001")
            elif mode == "extra_field":
                parsed["assessments"]["Q001"]["effect_note"] = "extra"
            final = encoded(parsed).decode()
        body["output"][1]["content"][0]["text"] = final
    if reply["behavior"] == "response":
        reply["response_body_utf8"] = encoded(body).decode()
    path.write_bytes(encoded(value))
    journal = tmp_path / "journal"
    assert capture(prepared, path, journal) == "halted"
    result = audit(prepared, journal)
    assert result["journal_closed"] and not result["completion_eligible"]
    assert sum(s["consumed"] for s in result["slots"]) == index + 1
    if mode.startswith("count_"):
        assert result["fixture_generation_attempts"] == 0
    else:
        assert result["fixture_generation_attempts"] == 1
    if mode == "generation_500":
        terminal = result["terminals"][0]
        assert terminal["exchanges"][1]["response"]["error_codes"] == ["http_500", "server_error"]
        assert terminal["usage"]["input_tokens"] is None
    if mode in ("unknown_usage", "over_usage"):
        assert result["accounting_hold"]
        assert result["generations_with_unknown_usage"] == int(mode == "unknown_usage")
        assert result["terminals"][0]["state"] == "bound_unassessed"


@pytest.mark.parametrize(
    "change", ["origin", "source_origin", "request", "missing", "order", "duplicate_key"]
)
def test_invalid_fixture_refused_before_intent(
    prepared: Prepared, tmp_path: Path, change: str
) -> None:
    path, value = fixtures(prepared, tmp_path)
    if change == "origin":
        value["delivery_origin"] = "observed_openai_transport"
    elif change == "source_origin":
        value["source_origin"] = "diagnostic_probe"
    elif change == "request":
        value["request_set_canonical_sha256"] = "0" * 64
    elif change == "missing":
        value["replies"].pop()
    elif change == "order":
        value["replies"][0], value["replies"][3] = value["replies"][3], value["replies"][0]
    raw = encoded(value)
    if change == "duplicate_key":
        raw = raw.replace(b"{", b'{"delivery_origin":"injected_fixture",', 1)
    path.write_bytes(raw)
    with pytest.raises(ValueError):
        capture(prepared, path, tmp_path / "journal")
    assert not (tmp_path / "journal").exists()


def test_cancelled_before_dispatch_and_non_mock_refusal(prepared: Prepared, tmp_path: Path) -> None:
    path, value = fixtures(prepared, tmp_path)
    with pytest.raises(ValueError, match="mock_transport_required"):
        capture(prepared, path, tmp_path / "bad", transport=object())
    assert not (tmp_path / "bad").exists()
    value["cancel_before_dispatch"] = True
    path.write_bytes(encoded(value))
    assert capture(prepared, path, tmp_path / "cancelled") == "cancelled_before_dispatch"
    result = audit(prepared, tmp_path / "cancelled")
    assert not any(s["consumed"] for s in result["slots"])
    assert result["fixture_count_attempts"] == result["fixture_generation_attempts"] == 0


def test_fixture_drift_after_intent_refuses_dispatch(
    prepared: Prepared, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path, value = fixtures(prepared, tmp_path)
    original = io._durable_write
    called = []

    def write(target: Path, raw: bytes) -> None:
        original(target, raw)
        if target.name == "event-0001.json":
            path.write_bytes(encoded(value) + b" ")

    monkeypatch.setattr(io, "_durable_write", write)

    def never_dispatch(request: httpx.Request) -> httpx.Response:
        called.append(request)
        raise AssertionError("changed fixture must stop before transport")

    with pytest.raises(ValueError, match="fixtures_changed"):
        capture(
            prepared,
            path,
            tmp_path / "journal",
            transport=httpx.MockTransport(never_dispatch),
        )
    assert not called
    result = audit(prepared, tmp_path / "journal")
    assert result["slots"][0]["status"] == "interrupted"


@pytest.mark.parametrize("change", ["sequence", "previous", "endpoint", "origin", "receipt"])
def test_journal_tampering_refused(prepared: Prepared, tmp_path: Path, change: str) -> None:
    path, value = fixtures(prepared, tmp_path)
    value["replies"][0].update(behavior="interrupt", http_status=None, response_body_utf8="")
    path.write_bytes(encoded(value))
    journal = tmp_path / "journal"
    with pytest.raises(io.FixtureInterrupted):
        capture(prepared, path, journal)
    target = journal / ("header.json" if change == "origin" else "event-0001.json")
    event = load(target)
    if change == "sequence":
        event["sequence"] = 2
    elif change == "previous":
        event["previous_bytes_sha256"] = "0" * 64
    elif change == "endpoint":
        event["payload"]["endpoint"]["body_utf8"] += " "
    elif change == "origin":
        event["delivery_origin"] = "observed_openai_transport"
    else:
        event["payload"]["receipt"] = {"status": "valid"}
    target.write_bytes(encoded(event))
    with pytest.raises(ValueError):
        audit(prepared, journal)


def test_mapping_refuses_arbitrary_messages_and_wire_drift(
    prepared: Prepared, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = prepared.loaded.collected[0].source
    real = domain.prepare_authored_wire

    def mutate(source: Any, scope: Any, request: Any, spec: Any) -> Any:
        request = replace(
            request, messages=(ModelMessage(request.messages[0].role, "replacement"),)
        )
        return real(source, scope, request, spec)

    monkeypatch.setattr(domain, "prepare_authored_wire", mutate)
    with pytest.raises(ValueError, match="authored_wire_messages"):
        service._make(prepared.loaded.collected, "mutated", settings())
    m = prepared.loaded.request_set.payload.requests[0]
    e = m.payload.endpoints[0]
    assert scope_for_batch(
        source.work, m.payload.presentation.batch_id, m.payload_canonical_sha256
    ).active_unit_ids == ("Q001", "Q002", "Q003")
    for request in (
        httpx.Request("POST", e.destination + e.path, content=e.body_utf8.encode() + b" "),
        httpx.Request(
            "POST",
            e.destination + e.path,
            content=e.body_utf8.encode(),
            headers={"authorization": "fixture"},
        ),
    ):
        with pytest.raises(ValueError):
            check_outgoing(e, request)


def test_terminal_rejects_cross_source_or_response_hash(prepared: Prepared) -> None:
    m = prepared.loaded.request_set.payload.requests[0]
    source = prepared.loaded.collected[0].source
    e = m.payload.endpoints[0]
    mapped = map_response(
        "input_count", 200, b'{"input_tokens":100}', m.payload.settings.model_spec
    )
    exchange = service._interrupted(e).model_copy(
        update={
            "disposition": "response",
            "response": mapped,
            "observed_http_status": 200,
            "retained_response_canonical_sha256": "0" * 64,
        }
    )
    with pytest.raises(ValueError, match="response_hash"):
        domain.derive_terminal(source, m, (exchange,), 0.1)
    with pytest.raises(ValueError):
        domain.derive_terminal(prepared.loaded.collected[1].source, m, (), 0.0)


def test_cli_exposes_only_offline_commands(prepared: Prepared, tmp_path: Path) -> None:
    for args in (
        ["run"],
        [
            "prepare",
            "--source",
            source_service.SOURCE_ID,
            "--output",
            str(tmp_path / "out"),
            "--live",
        ],
    ):
        with pytest.raises(SystemExit):
            cli.main(args)
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize(
    "violation,inputs,outputs",
    [("input", 24001, 20), ("output", 100, 32001), ("context", 1050000, 20), ("cost", 100, 60001)],
)
def test_all_resource_dimensions_remain_separate_from_binding(
    prepared: Prepared, violation: str, inputs: int, outputs: int
) -> None:
    m = prepared.loaded.request_set.payload.requests[0]
    source = prepared.loaded.collected[0].source
    body = provider_body(submission(source)["raw_final"])
    body["usage"].update(input_tokens=inputs, output_tokens=outputs, total_tokens=inputs + outputs)
    exchanges = []
    for e, value in zip(m.payload.endpoints, ({"input_tokens": 100}, body), strict=True):
        mapped = map_response(e.stage, 200, encoded(value), m.payload.settings.model_spec)
        exchanges.append(
            service._interrupted(e).model_copy(
                update={
                    "disposition": "response",
                    "response": mapped,
                    "observed_http_status": 200,
                    "retained_response_canonical_sha256": canonical_sha256(
                        mapped.model_dump(mode="json")
                    ),
                }
            )
        )
    terminal = domain.derive_terminal(source, m, tuple(exchanges), 0.1)
    assert terminal.state == "bound_unassessed" and terminal.accounting_hold
    assert violation in terminal.budget_violations
    assert all(v is not None for v in terminal.usage.model_dump().values())


def test_transport_time_stop(
    prepared: Prepared, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path, _ = fixtures(prepared, tmp_path)
    ticks = iter((0.0, 601.0))
    monkeypatch.setattr(service, "perf_counter", lambda: next(ticks))
    assert capture(prepared, path, tmp_path / "journal") == "halted"
    result = audit(prepared, tmp_path / "journal")
    assert result["transport_time_limit_reached"] and result["fixture_count_attempts"] == 1
    assert result["fixture_generation_attempts"] == 0 and not result["completion_eligible"]


@pytest.mark.parametrize("unknown", [True, False])
def test_final_slot_accounting_hold_cannot_publish_complete_binding(
    prepared: Prepared, tmp_path: Path, unknown: bool
) -> None:
    path, value = fixtures(prepared, tmp_path)
    body = json.loads(value["replies"][5]["response_body_utf8"])
    if unknown:
        body["usage"].pop("input_tokens_details")
    else:
        body["usage"].update(input_tokens=24001, total_tokens=24021)
    value["replies"][5]["response_body_utf8"] = encoded(body).decode()
    path.write_bytes(encoded(value))
    assert capture(prepared, path, tmp_path / "journal") == "halted"
    result = audit(prepared, tmp_path / "journal")
    assert all(c["complete_delivery"] and c["binding"] == "complete" for c in result["completions"])
    assert result["fixture_count_attempts"] == result["fixture_generation_attempts"] == 3
    assert result["journal_closed"] and result["accounting_hold"]
    assert result["generations_with_unknown_usage"] == int(unknown)
    assert not result["completion_eligible"]
