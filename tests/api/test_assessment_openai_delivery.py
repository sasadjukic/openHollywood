"""OpenAI wire fixtures through source-bound preparation, durable intent and read-only audit."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services import assessment_delivery as fixture_io
from open_hollywood_api.services import assessment_openai_delivery as service
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.models.assessment_openai_manifest import parse_set
from open_hollywood_engine.secrets import SecretLeakGuard, SecretValue

from scripts import assessment_openai_delivery as cli
from tests.api.test_assessment_completion import snapshot
from tests.api.test_assessment_delivery import Delivery, offline, setup_delivery
from tests.evaluations.test_assessment_presentation import settings
from tests.models.test_assessment_openai import provider_body

__all__ = ["offline"]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def setup(tmp: Path, monkeypatch: pytest.MonkeyPatch, *, multi: bool = False) -> Delivery:
    old = setup_delivery(tmp, monkeypatch, multi=multi)
    p = Delivery(
        old.intake,
        tmp / "openai-requests",
        tmp / "openai-fixtures.json",
        tmp / "openai-journal",
        tmp / "openai-audit",
    )
    service.prepare_requests(p.intake, p.preparation, run_id="openai-test", settings=settings())
    plan = parse_set((p.preparation / "request-set.json").read_bytes())
    old_raw = [
        json.loads(r["response_body_utf8"])["raw_final"]
        for r in load(old.fixtures)["replies"]
        if r["stage"] == "generation"
    ]
    fixture = load(p.preparation / "fixtures.template.json")
    fixture["authored_by"] = "Authored provider-format test"
    for i, reply in enumerate(fixture["replies"]):
        reply["response_body_utf8"] = json.dumps(
            {"input_tokens": 100}
            if reply["stage"] == "input_count"
            else provider_body(old_raw[i // 2])
        )
    p.fixtures.write_bytes(encoded(fixture))
    assert len(plan.payload.requests) == len(old_raw)
    return p


@pytest.fixture
def delivery(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Delivery:
    return setup(tmp_path, monkeypatch)


def capture(p: Delivery, transport: httpx.MockTransport | None = None) -> str:
    return service.capture_fixtures(
        p.intake, p.preparation, p.fixtures, p.journal, transport=transport
    )


def audit(p: Delivery) -> dict[str, Any]:
    service.audit_terminal(p.intake, p.preparation, p.journal, p.audit)
    return load(p.audit / "audit.json")


def mutate_reply(p: Delivery, stage: str, change: Any) -> None:
    data = load(p.fixtures)
    reply = next(r for r in data["replies"] if r["stage"] == stage)
    change(reply)
    p.fixtures.write_bytes(encoded(data))


def test_complete_actual_bytes_durable_intent_and_immutable_reuse(
    delivery: Delivery, monkeypatch: pytest.MonkeyPatch
) -> None:
    p = delivery
    frozen = snapshot(p.preparation)
    original = snapshot(p.intake.parent)
    replies = iter(load(p.fixtures)["replies"])
    fsync = os.fsync
    syncs: list[int] = []

    def sync(fd: int) -> None:
        fsync(fd)
        syncs.append(fd)

    monkeypatch.setattr(os, "fsync", sync)
    called: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        reply = next(replies)
        n = len(called) * 2 + 1
        intent = load(p.journal / f"event-{n:04d}.json")["payload"]
        assert len(syncs) >= n + 2
        assert request.content == intent["endpoint"]["body_utf8"].encode()
        assert (
            intent["request_payload_canonical_sha256"]
            == load(p.preparation / "request-set.json")["payload"]["requests"][0][
                "payload_canonical_sha256"
            ]
        )
        called.append(request.url.path)
        return httpx.Response(200, content=reply["response_body_utf8"])

    assert capture(p, httpx.MockTransport(handler)) == "complete"
    result = audit(p)
    assert result["completion_eligible"] and result["completion"]["binding"] == "complete"
    assert result["intake"] == load(p.intake)
    assert result["fixture_generation_attempts"] == result["fixture_count_attempts"] == 1
    assert result["actual_billed_cost"] is None and not result["model_evidence"]
    assert result["origin"] == "injected_fixture"
    assert not result["writer_dispatch_authorized"]
    journal, output = snapshot(p.journal), snapshot(p.audit)
    with pytest.raises(ValueError, match="journal_already_exists"):
        capture(p, httpx.MockTransport(handler))
    assert len(called) == 2
    assert (
        service.prepare_requests(p.intake, p.preparation, run_id="openai-test", settings=settings())
        == "reused"
    )
    assert service.audit_terminal(p.intake, p.preparation, p.journal, p.audit) == "reused"
    assert original == snapshot(p.intake.parent) and frozen == snapshot(p.preparation)
    assert journal == snapshot(p.journal) and output == snapshot(p.audit)


@pytest.mark.parametrize(
    "failure",
    [
        "http500",
        "missing_count",
        "over_budget",
        "length",
        "refusal",
        "empty",
        "duplicate_id",
        "wrong_model",
        "unknown_usage",
        "unknown_cache",
        "error",
        "multi_message",
    ],
)
def test_failure_and_accounting_stops(delivery: Delivery, failure: str) -> None:
    p = delivery
    stage = (
        "input_count" if failure in {"http500", "missing_count", "over_budget"} else "generation"
    )

    def change(reply: dict[str, Any]) -> None:
        body = json.loads(reply["response_body_utf8"])
        if failure == "http500":
            reply["http_status"] = 500
        elif failure == "missing_count":
            body = {}
        elif failure == "over_budget":
            body["input_tokens"] = 24001
        elif failure == "length":
            body.update(status="incomplete", incomplete_details={"reason": "max_output_tokens"})
        elif failure == "refusal":
            body["output"][1]["content"] = [{"type": "refusal", "refusal": "fixture"}]
        elif failure == "empty":
            body["output"][1]["content"][0]["text"] = ""
        elif failure == "wrong_model":
            body["model"] = "other"
        elif failure == "unknown_usage":
            body.pop("usage")
        elif failure == "unknown_cache":
            body["usage"].pop("input_tokens_details")
        elif failure == "error":
            body["error"] = {"code": "server_error", "message": "no raw error retention"}
        elif failure == "multi_message":
            body["output"].append(body["output"][1])
        else:
            text = body["output"][1]["content"][0]["text"]
            body["output"][1]["content"][0]["text"] = text.replace(
                '"assessments":', '"assessments":{},"assessments":'
            )
        reply["response_body_utf8"] = json.dumps(body)

    mutate_reply(p, stage, change)
    assert capture(p) == "halted"
    result = audit(p)
    assert result["fixture_count_attempts"] == 1
    assert result["fixture_generation_attempts"] == int(stage == "generation")
    if failure in {"unknown_usage", "unknown_cache"}:
        assert result["completion_eligible"] and result["accounting_hold"]
        assert result["terminals"][0]["state"] == "bound_unassessed"
    else:
        assert not result["completion_eligible"]


@pytest.mark.parametrize("stage", ["input_count", "generation"])
@pytest.mark.parametrize("behavior", ["interrupt", "cancelled", "transport_error"])
def test_interrupted_or_cancelled_intent_consumed(
    delivery: Delivery, stage: str, behavior: str
) -> None:
    p = delivery
    mutate_reply(
        p, stage, lambda r: r.update(behavior=behavior, http_status=None, response_body_utf8="")
    )
    if behavior == "interrupt":
        with pytest.raises(fixture_io.FixtureInterrupted):
            capture(p)
    else:
        assert capture(p) == "halted"
    result = audit(p)
    assert result["fixture_count_attempts"] == 1
    assert result["fixture_generation_attempts"] == int(stage == "generation")
    assert not result["completion_eligible"]
    assert result["unknown_elapsed_endpoints"] == int(behavior == "interrupt")
    assert result["terminals"][0]["usage"]["output_tokens"] is None


def test_failed_second_batch_never_publishes_subset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    p = setup(tmp_path, monkeypatch, multi=True)
    data = load(p.fixtures)
    data["replies"][3]["http_status"] = 500
    p.fixtures.write_bytes(encoded(data))
    assert capture(p) == "halted"
    result = audit(p)
    assert result["fixture_generation_attempts"] == 2 and not result["completion_eligible"]
    assert result["completion"]["completed_batches"] == 1


def test_unknown_first_batch_usage_stops_before_second(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    p = setup(tmp_path, monkeypatch, multi=True)
    data = load(p.fixtures)
    body = json.loads(data["replies"][1]["response_body_utf8"])
    body.pop("usage")
    data["replies"][1]["response_body_utf8"] = json.dumps(body)
    p.fixtures.write_bytes(encoded(data))
    assert capture(p) == "halted"
    result = audit(p)
    assert result["fixture_generation_attempts"] == 1 and not result["completion_eligible"]
    assert result["completion"]["unknown_usage_attempts"] == 1


def rechain(journal: Path) -> None:
    previous = fixture_io._sha((journal / "header.json").read_bytes())
    for p in sorted(journal.glob("event-*.json")):
        data = load(p)
        data["previous_bytes_sha256"] = previous
        if data["payload"]["kind"] == "outcome":
            data["payload"]["intent_bytes_sha256"] = previous
        p.write_bytes(encoded(data))
        previous = fixture_io._sha(p.read_bytes())


@pytest.mark.parametrize(
    "change",
    [
        "chain",
        "request_hash",
        "endpoint",
        "origin",
        "gap",
        "duplicate_key",
        "extra",
        "stop",
        "model",
        "http",
        "response_hash",
    ],
)
def test_journal_drift_or_forged_terminal_refused(delivery: Delivery, change: str) -> None:
    p = delivery
    capture(p)
    file = p.journal / "event-0001.json"
    if change == "gap":
        file.unlink()
    elif change == "extra":
        (p.journal / "extra").write_bytes(b"{}")
    elif change == "duplicate_key":
        file.write_bytes(file.read_bytes().replace(b'"sequence": 1', b'"sequence":1,"sequence":1'))
    else:
        if change == "origin":
            file = p.journal / "header.json"
        elif change == "stop":
            file = p.journal / "event-0005.json"
        elif change in {"model", "http", "response_hash"}:
            file = p.journal / "event-0004.json"
        data = load(file)
        if change == "chain":
            data["previous_bytes_sha256"] = "a" * 64
        elif change == "origin":
            data["origin"] = "authenticated_model_delivery"
        elif change == "request_hash":
            data["payload"]["request_payload_canonical_sha256"] = "b" * 64
        elif change == "endpoint":
            data["payload"]["endpoint"]["body_utf8"] += " "
        elif change == "stop":
            data["payload"]["reason"] = "halted"
        else:
            exchange = data["payload"]["exchange"]
            if change == "model":
                exchange["response"]["returned_model"] = "other"
            elif change == "http":
                exchange["response"]["http_status"] = exchange["observed_http_status"] = 500
            else:
                exchange["response"]["raw_final_utf8_sha256"] = "f" * 64
            exchange["retained_response_canonical_sha256"] = canonical_sha256(exchange["response"])
        file.write_bytes(encoded(data))
        if change in {"model", "http", "response_hash"}:
            rechain(p.journal)
    before = snapshot(p.journal)
    with pytest.raises(ValueError):
        audit(p)
    assert before == snapshot(p.journal) and not p.audit.exists()


def test_missing_stop_does_not_complete_publication(delivery: Delivery) -> None:
    capture(delivery)
    (delivery.journal / "event-0005.json").unlink()
    result = audit(delivery)
    assert result["completion"]["complete_delivery"] and not result["completion_eligible"]


def test_cancel_before_dispatch_and_no_live_option(delivery: Delivery) -> None:
    data = load(delivery.fixtures)
    data["cancel_before_dispatch"] = True
    delivery.fixtures.write_bytes(encoded(data))
    assert capture(delivery) == "cancelled_before_dispatch"
    result = audit(delivery)
    assert result["fixture_count_attempts"] == result["fixture_generation_attempts"] == 0
    with pytest.raises(SystemExit):
        cli.main(["run-live"])


def test_fsync_failure_blocks_transport(
    delivery: Delivery, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = os.fsync
    calls: list[int] = []

    def failed(fd: int) -> None:
        calls.append(fd)
        if len(calls) == 3:
            raise OSError("authored fsync failure")
        original(fd)

    monkeypatch.setattr(os, "fsync", failed)
    with pytest.raises(OSError):
        capture(
            delivery,
            httpx.MockTransport(lambda r: (_ for _ in ()).throw(AssertionError("not reached"))),
        )


@pytest.mark.parametrize("change", ["body", "destination", "headers"])
def test_changed_actual_request_refused_before_callback(
    delivery: Delivery, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    build = service._build_request

    def changed(endpoint: Any) -> httpx.Request:
        original = build(endpoint)
        return httpx.Request(
            "POST",
            str(original.url) if change != "destination" else "https://other.invalid",
            content=original.content + (b" " if change == "body" else b""),
            headers={"Authorization": "fixture"} if change == "headers" else {},
        )

    monkeypatch.setattr(service, "_build_request", changed)
    with pytest.raises(ValueError):
        capture(delivery)
    assert len(list(delivery.journal.iterdir())) == 2


def test_secret_is_not_retained(delivery: Delivery, monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = "synthetic-private-value"
    monkeypatch.setattr(
        service, "active_secret_guard", lambda: SecretLeakGuard((SecretValue(sentinel),))
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"input_tokens": 100}
            if request.url.path.endswith("input_tokens")
            else provider_body(sentinel),
        )

    assert capture(delivery, httpx.MockTransport(handler)) == "halted"
    assert all(sentinel.encode() not in b for b, _ in snapshot(delivery.journal).values())
    assert not audit(delivery)["completion_eligible"]


def test_transport_time_limit_stops_after_observed_count(delivery: Delivery) -> None:
    p = delivery
    p.preparation = p.preparation.with_name("short-deadline")
    config = settings().model_copy(update={"max_transport_seconds": 1e-12})
    service.prepare_requests(p.intake, p.preparation, run_id="time", settings=config)
    fixture = load(p.fixtures)
    new = load(p.preparation / "fixtures.template.json")
    for row, old in zip(new["replies"], fixture["replies"], strict=True):
        row["response_body_utf8"] = old["response_body_utf8"]
    new["authored_by"] = "time fixture"
    p.fixtures.write_bytes(encoded(new))
    assert capture(p) == "halted"
    result = audit(p)
    assert result["transport_time_limit_reached"] and result["fixture_generation_attempts"] == 0


@pytest.mark.parametrize("where", ["intake", "preparation", "journal", "ancestor"])
def test_protected_destination_refused(delivery: Delivery, where: str) -> None:
    capture(delivery)
    destination = {
        "intake": delivery.intake.parent / "out",
        "preparation": delivery.preparation / "out",
        "journal": delivery.journal / "out",
        "ancestor": delivery.intake.parent.parent,
    }[where]
    with pytest.raises(ValueError):
        service.audit_terminal(delivery.intake, delivery.preparation, delivery.journal, destination)


def test_source_drift_after_count_blocks_generation(delivery: Delivery) -> None:
    old = delivery.intake.read_bytes()
    called: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        called.append(request.url.path)
        delivery.intake.write_bytes(old + b" ")
        return httpx.Response(200, json={"input_tokens": 100})

    with pytest.raises(ValueError):
        capture(delivery, httpx.MockTransport(handler))
    assert called == ["/v1/responses/input_tokens"]
    delivery.intake.write_bytes(old)  # Restore authored test source only.
    result = audit(delivery)
    assert result["fixture_generation_attempts"] == 0 and not result["journal_closed"]


@pytest.mark.parametrize("change", ["partial", "changed", "extra"])
def test_audit_publication_never_repaired(delivery: Delivery, change: str) -> None:
    capture(delivery)
    audit(delivery)
    p = delivery.audit / (
        "manifest.json" if change == "partial" else "audit.json" if change == "changed" else "extra"
    )
    if change == "partial":
        p.unlink()
    else:
        p.write_bytes(b"changed")
    before = snapshot(delivery.audit)
    with pytest.raises(ValueError):
        audit(delivery)
    assert snapshot(delivery.audit) == before


def test_cli_redacts_errors(
    delivery: Delivery, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail(*args: Any, **kwargs: Any) -> Any:
        raise ValueError("PRIVATE_PROSE")

    monkeypatch.setattr(cli, "audit_terminal", fail)
    assert (
        cli.main(
            [
                "audit",
                "--intake",
                str(delivery.intake),
                "--preparation",
                str(delivery.preparation),
                "--journal",
                str(delivery.journal),
                "--output",
                str(delivery.audit),
            ]
        )
        == 2
    )
    assert "PRIVATE_PROSE" not in capsys.readouterr().out


def test_runtime_schema_files_match() -> None:
    from open_hollywood_engine.models.assessment_openai_manifest import (
        RequestSet,
        Settings,
        Terminal,
    )

    root = Path(__file__).resolve().parents[2]
    for name, model in (
        ("assessment-openai-rehearsal-settings-1", Settings),
        ("assessment-openai-intake-set-1", RequestSet),
        ("assessment-openai-transport-fixtures-1", service.TransportFixtures),
        ("assessment-openai-fixture-event-1", service.JournalEvent),
        ("assessment-openai-rehearsal-terminal-1", Terminal),
    ):
        schema = model.model_json_schema()
        schema["$comment"] = (
            "Local OpenAI wire rehearsal only. Source authentication, exact request "
            "regeneration, durable intent and native completion are application checks. "
            "No live authorization or model-delivery provenance follows from schema validity."
        )
        assert (root / "docs/contracts" / (name + ".schema.json")).read_bytes() == encoded(schema)


@pytest.mark.parametrize("failure", ["blank_author", "origin", "coverage", "wrong_set"])
def test_fixture_admission_rejects_unbound_or_promoted_origin(
    delivery: Delivery, failure: str
) -> None:
    data = load(delivery.fixtures)
    if failure == "blank_author":
        data["authored_by"] = ""
    elif failure == "origin":
        data["origin"] = "authenticated_model_delivery"
    elif failure == "coverage":
        data["replies"].reverse()
    else:
        data["request_set_canonical_sha256"] = "f" * 64
    delivery.fixtures.write_bytes(encoded(data))
    with pytest.raises(ValueError):
        capture(delivery)
    assert not delivery.journal.exists()


def test_source_or_journal_change_after_render_blocks_publication(
    delivery: Delivery, monkeypatch: pytest.MonkeyPatch
) -> None:
    capture(delivery)
    render = service._literal

    def changed(title: str, value: Any) -> bytes:
        result = render(title, value)
        if title == "OpenAI rehearsal audit":
            (delivery.journal / "header.json").write_bytes(b"{}")
        return result

    monkeypatch.setattr(service, "_literal", changed)
    with pytest.raises(ValueError):
        audit(delivery)
    assert not delivery.audit.exists()


def test_oversized_observed_response_and_real_transport_refused(delivery: Delivery) -> None:
    with pytest.raises(ValueError, match="mock_transport_required"):
        capture(delivery, object())  # type: ignore[arg-type]
    assert not delivery.journal.exists()
    assert (
        capture(
            delivery,
            httpx.MockTransport(lambda r: httpx.Response(200, content=b"x" * (1024 * 1024 + 1))),
        )
        == "halted"
    )
    result = audit(delivery)
    assert not result["completion_eligible"] and result["fixture_generation_attempts"] == 0


def test_preparation_drift_refused_even_with_modified_saved_hashes(delivery: Delivery) -> None:
    path = delivery.preparation / "request-set.json"
    data = load(path)
    payload = data["payload"]["requests"][0]["payload"]
    payload["endpoints"][1]["body_utf8"] += " "
    data["payload"]["requests"][0]["payload_canonical_sha256"] = canonical_sha256(payload)
    data["payload_canonical_sha256"] = canonical_sha256(data["payload"])
    path.write_bytes(encoded(data))
    with pytest.raises(ValueError):
        capture(delivery)
    assert not delivery.journal.exists()
