"""One-shot four-work transport qualification; all sources and responses are authored."""

from __future__ import annotations

import asyncio
import json
import os
import socket
import sqlite3
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_delivery as io
from open_hollywood_api.services import assessment_openai_delivery as rehearsal
from open_hollywood_api.services import assessment_openai_smoke as service
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import compile_intake
from open_hollywood_engine.models.assessment_openai_manifest import make_request_set
from open_hollywood_engine.secrets import SecretValue

from scripts import assessment_openai_smoke as cli
from tests.assessment_intake_fixtures import authored_source, choice_for, plan_for
from tests.authored_completion_fixtures import context_for, submission_for
from tests.evaluations.test_assessment_presentation import settings
from tests.models.test_assessment_openai import provider_body


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("No real network or database in smoke qualification")

    original_connect = socket.socket.connect

    def local_loop(sock: socket.socket, address: Any) -> Any:
        # Windows asyncio creates a local socket pair for its wakeup pipe.
        if isinstance(address, tuple) and address[0] in ("127.0.0.1", "::1"):
            return original_connect(sock, address)
        return deny()

    for owner, name in (
        (socket.socket, "connect_ex"),
        (socket, "create_connection"),
        (socket, "getaddrinfo"),
        (sqlite3, "connect"),
        (httpx.AsyncHTTPTransport, "handle_async_request"),
    ):
        monkeypatch.setattr(owner, name, deny)
    monkeypatch.setattr(socket.socket, "connect", local_loop)


def load(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(result, dict)
    return result


@pytest.fixture
def frozen(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, dict[str, Any]]:
    source = authored_source()
    records, works, replies = {}, [], []
    config = settings().model_copy(update={"max_input_tokens": 272000, "max_cost_usd": "1.00"})
    choices = (("Q001",), ("Q002",), ("Q005",), ("Q001", "Q002"))
    for name, ids in zip(service.NAMES, choices, strict=True):
        context = context_for(
            compile_intake(source, plan_for(source, *(choice_for(source, q) for q in ids)))
        )
        requests = make_request_set(context, name, config, rehearsal._implementation())
        preparation = tmp_path / name / "requests"
        preparation.mkdir(parents=True)
        files = rehearsal._files(context, requests)
        for member, raw in files.items():
            (preparation / member).write_bytes(raw)
        intake = tmp_path / name / "intake.json"
        intake.write_bytes(context.exact_intake)
        prepared = rehearsal._Prepared(storage._Collected(context, (intake,), {}), requests, files)
        records[str(preparation)] = prepared
        works.append(
            service.Work(
                name=name,
                intake=str(intake),
                preparation=str(preparation),
                request_set_sha256=requests.payload_canonical_sha256,
                preparation_manifest_sha256=io._sha(files["manifest.json"]),
            )
        )
        replies.append(provider_body(submission_for(context).attempts[0].raw_final))

    def collect(intake: Path, preparation: Path) -> rehearsal._Prepared:
        prepared = records[str(preparation)]
        assert intake.read_bytes() == prepared.collected.context.exact_intake
        for member, raw in prepared.files.items():
            assert (preparation / member).read_bytes() == raw
        return prepared

    monkeypatch.setattr(rehearsal, "_load", collect)
    path = tmp_path / "plan.json"
    service.freeze(tuple(works), path, tmp_path / "live")
    return path, {"records": records, "replies": replies}


def execute(
    frozen: tuple[Path, dict[str, Any]], handler: Any, name: str = "journal"
) -> tuple[str, Path]:
    path, _ = frozen
    journal = path.parent / name
    return asyncio.run(service.qualify(path, journal, httpx.MockTransport(handler))), journal


def report(frozen: tuple[Path, dict[str, Any]], journal: Path) -> dict[str, Any]:
    path, _ = frozen
    output = journal.with_name(journal.name + "-audit")
    service.audit(path, journal, output)
    return load(output / "audit.json")


def test_all_eight_slots_exact_client_bytes_headers_and_fsynced_intent(
    frozen: tuple[Path, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path, data = frozen
    plan = service.load_plan(path)
    calls: list[str] = []
    flushes: list[int] = []
    fsync = os.fsync

    def sync(fd: int) -> None:
        fsync(fd)
        flushes.append(fd)

    monkeypatch.setattr(os, "fsync", sync)

    def handler(request: httpx.Request) -> httpx.Response:
        n = len(calls)
        work = plan.works[n % 4]
        endpoint = service._work(work).request_set.payload.requests[0].payload.endpoints[n // 4]
        assert request.content == endpoint.body_utf8.encode()
        assert str(request.url) == endpoint.destination + endpoint.path
        assert request.headers["authorization"] == "Bearer local-smoke-fixture-token"
        assert set(request.headers) == {"host", "content-length", "content-type", "authorization"}
        assert request.extensions["timeout"]["connect"] <= 30
        intent = load(path.parent / "journal" / f"event-{2 * n + 1:04d}.json")
        assert intent["payload"]["body_bytes_sha256"] == endpoint.body_bytes_sha256
        assert len(flushes) >= 2 * n + 3
        calls.append(request.url.path)
        return httpx.Response(
            200,
            content=encoded({"input_tokens": 100} if n < 4 else data["replies"][n % 4]),
            headers={"x-request-id": f"req_{n}"},
        )

    status, journal = execute(frozen, handler)
    assert (
        status == "complete" and calls == ["/v1/responses/input_tokens"] * 4 + ["/v1/responses"] * 4
    )
    result = report(frozen, journal)
    assert len(result["slots"]) == 8 and all(w["completion_eligible"] for w in result["works"])
    assert result["count_intents"] == result["generation_intents"] == 4
    assert result["origin"] == "injected_transport_fixture" and not result["model_observation"]
    assert result["actual_billed_cost"] is None and not result["writer_dispatch_authorized"]
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in journal.iterdir()}
    with pytest.raises(ValueError, match="no_resume"):
        execute(frozen, handler)
    assert len(calls) == 8
    output = journal.with_name(journal.name + "-audit")
    assert service.audit(path, journal, output) == "reused"
    assert before == {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in journal.iterdir()}
    assert "local-smoke-fixture-token" not in "".join(
        p.read_text(encoding="utf-8") for p in journal.iterdir()
    )


@pytest.mark.parametrize(
    "failure",
    [
        "500",
        "302",
        "count_missing",
        "count_large",
        "timeout",
        "empty",
        "length",
        "refusal",
        "invalid",
        "duplicate_id",
        "unknown_usage",
        "unknown_cache",
        "over_usage",
        "secret",
        "wrong_model",
    ],
)
def test_failure_stops_without_recovery(frozen: tuple[Path, dict[str, Any]], failure: str) -> None:
    _, data = frozen
    calls: list[str] = []
    count_failure = failure in {"500", "302", "count_missing", "count_large", "timeout"}

    def handler(request: httpx.Request) -> httpx.Response:
        n = len(calls)
        calls.append(request.url.path)
        if n < 4:
            if count_failure:
                if failure == "timeout":
                    raise httpx.ReadTimeout("private exception")
                if failure in {"500", "302"}:
                    return httpx.Response(
                        int(failure),
                        json={"error": {"code": "gateway_error"}},
                        headers={"location": "https://example.invalid/"},
                    )
                return httpx.Response(
                    200, json={} if failure == "count_missing" else {"input_tokens": 272001}
                )
            return httpx.Response(200, json={"input_tokens": 100})
        body = json.loads(json.dumps(data["replies"][0]))
        if failure == "empty":
            body["output"] = []
        elif failure == "length":
            body.update(status="incomplete", incomplete_details={"reason": "max_output_tokens"})
        elif failure == "refusal":
            body["output"][-1]["content"] = [{"type": "refusal", "refusal": "no"}]
        elif failure in {"invalid", "duplicate_id"}:
            body["output"][-1]["content"][0]["text"] = (
                "{}" if failure == "invalid" else '{"assessments":{"Q001":{},"Q001":{}}}'
            )
        elif failure == "unknown_usage":
            body.pop("usage")
        elif failure == "unknown_cache":
            body["usage"].pop("input_tokens_details")
        elif failure == "over_usage":
            body["usage"].update(input_tokens=272001, total_tokens=272021)
        elif failure == "secret":
            body["output"][-1]["content"][0]["text"] = "local-smoke-fixture-token"
        elif failure == "wrong_model":
            body["model"] = "gpt-6-luna"
        return httpx.Response(200, json=body)

    status, journal = execute(frozen, handler)
    assert status == "halted" and len(calls) == (1 if count_failure else 5)
    result = report(frozen, journal)
    assert len(result["slots"]) == 8 and not result["works"][-1]["completion_eligible"]
    assert sum(s["state"] == "not_dispatched" for s in result["slots"]) == (
        7 if count_failure else 3
    )


@pytest.mark.parametrize("position", [0, 4])
def test_cancellation_preserves_pending_consumed_slot(
    frozen: tuple[Path, dict[str, Any]], position: int
) -> None:
    calls: list[str] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        n = len(calls)
        calls.append(request.url.path)
        if n == position:
            raise asyncio.CancelledError()
        return httpx.Response(200, json={"input_tokens": 100})

    with pytest.raises(asyncio.CancelledError):
        execute(frozen, handler)
    result = report(frozen, frozen[0].parent / "journal")
    assert not result["journal_closed"] and result["unknown_elapsed_endpoints"] == 1
    assert result["count_intents"] == min(position + 1, 4) and result["generation_intents"] == int(
        position == 4
    )
    assert len(result["slots"]) == 8


def test_elapsed_deadline_interrupts_transport_and_counts_attempt(
    frozen: tuple[Path, dict[str, Any]],
) -> None:
    prepared = service._work(service.load_plan(frozen[0]).works[0])

    async def handler(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(1)
        return httpx.Response(200, json={"input_tokens": 100})

    async def run() -> None:
        async with service._client(httpx.MockTransport(handler)) as client:
            exchange, _ = await service._exchange(
                client, prepared, "input_count", SecretValue("synthetic-timeout-test-key"), 0.01
            )
        assert exchange.disposition == "transport_error" and exchange.response is None

    asyncio.run(run())


@pytest.mark.parametrize("count_failure", [False, True])
def test_live_construction_requires_exact_approval_fixed_path_and_zero_retry_transport(
    frozen: tuple[Path, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
    count_failure: bool,
) -> None:
    path, data = frozen
    live = Path(service.load_plan(path).live_journal)
    made = []
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        n = len(calls)
        calls.append(request.url.path)
        assert request.headers["authorization"] == "Bearer synthetic-live-path-key"
        if count_failure:
            return httpx.Response(500, json={"error": {"code": "gateway_error"}})
        return httpx.Response(200, json={"input_tokens": 100} if n < 4 else data["replies"][n % 4])

    def transport(**kwargs: Any) -> httpx.MockTransport:
        made.append(kwargs)
        return httpx.MockTransport(handler)

    monkeypatch.setattr(httpx, "AsyncHTTPTransport", transport)
    secret = SecretValue("synthetic-live-path-key")
    with pytest.raises(ValueError):
        asyncio.run(service.run_live(path, live, "0" * 64, secret))
    digest = io._sha(path.read_bytes())
    with pytest.raises(ValueError):
        asyncio.run(service.run_live(path, live.with_name("other"), digest, secret))
    assert not made
    assert asyncio.run(service.run_live(path, live, digest, secret)) == (
        "halted" if count_failure else "complete"
    )
    assert made == [{"retries": 0, "verify": True, "trust_env": False}]
    assert len(calls) == (1 if count_failure else 8)
    with pytest.raises(ValueError):
        asyncio.run(service.run_live(path, live, digest, secret))
    assert len(made) == 1
    result = report(frozen, live)
    assert result["origin"] == "observed_openai_transport"
    assert result["transport_observation"] and result["model_observation"] is not count_failure


@pytest.mark.parametrize(
    "change", ["chain", "origin", "extra", "wrong_stop", "missing_stop", "outcome_hash"]
)
def test_journal_mutations_or_incomplete_close(
    frozen: tuple[Path, dict[str, Any]], change: str
) -> None:
    _, data = frozen
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        n = len(calls)
        calls.append(n)
        return httpx.Response(200, json={"input_tokens": 100} if n < 4 else data["replies"][n % 4])

    _, journal = execute(frozen, handler)
    if change == "extra":
        (journal / "extra.json").write_text("{}", encoding="utf-8")
    elif change == "missing_stop":
        (journal / "event-0017.json").unlink()
    else:
        target = journal / (
            "header.json"
            if change == "origin"
            else "event-0017.json"
            if change == "wrong_stop"
            else "event-0002.json"
        )
        obj = load(target)
        if change == "origin":
            obj["origin"] = "observed_openai_transport"
        elif change == "chain":
            obj["previous_bytes_sha256"] = "0" * 64
        elif change == "wrong_stop":
            obj["payload"]["reason"] = "halted"
        else:
            obj["payload"]["exchange"]["retained_response_canonical_sha256"] = "0" * 64
        target.write_bytes(encoded(obj))
    if change == "missing_stop":
        result = report(frozen, journal)
        assert not result["journal_closed"] and not any(
            w["completion_eligible"] for w in result["works"]
        )
    else:
        with pytest.raises(ValueError):
            report(frozen, journal)


def test_pre_send_fsync_and_source_failures_no_callback(
    frozen: tuple[Path, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(fd: int) -> None:
        raise OSError("injected disk failure")

    monkeypatch.setattr(os, "fsync", fail)
    calls = []
    with pytest.raises(OSError):
        execute(frozen, lambda r: calls.append(r))
    assert not calls


def test_cli_verify_never_loads_key_and_no_implicit_run(
    frozen: tuple[Path, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def deny() -> SecretValue:
        raise AssertionError("key read")

    monkeypatch.setattr(cli, "_secret", deny)
    assert cli.main(["verify", "--plan", str(frozen[0])]) == 0
    with pytest.raises(SystemExit):
        cli.main(["run", "--plan", str(frozen[0]), "--journal", "unused"])


def test_source_drift_after_count_refuses_next_dispatch(
    frozen: tuple[Path, dict[str, Any]],
) -> None:
    path, _ = frozen
    plan = service.load_plan(path)
    intake = Path(plan.works[1].intake)
    original = intake.read_bytes()
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        intake.write_bytes(original + b" ")
        return httpx.Response(200, json={"input_tokens": 100})

    with pytest.raises(AssertionError):
        execute(frozen, handler)
    assert len(calls) == 1
    intake.write_bytes(original)  # Restore authored test input to inspect its interrupted prefix.
    result = report(frozen, path.parent / "journal")
    assert not result["journal_closed"] and result["generation_intents"] == 0


def test_run_deadline_no_dispatch(
    frozen: tuple[Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    ticks = iter((0.0, 3601.0, 3602.0))
    monkeypatch.setattr(service, "perf_counter", lambda: next(ticks))
    calls: list[httpx.Request] = []
    status, journal = execute(frozen, lambda request: calls.append(request))
    assert status == "deadline" and not calls
    result = report(frozen, journal)
    assert result["count_intents"] == result["generation_intents"] == 0


@pytest.mark.parametrize("change", ["request", "source", "settings", "order", "code", "scoring"])
def test_plan_or_preparation_drift_refused(
    frozen: tuple[Path, dict[str, Any]],
    change: str,
) -> None:
    path, _ = frozen
    plan = load(path)
    if change in ("request", "source", "settings"):
        key = "request_set_sha256" if change == "request" else "preparation_manifest_sha256"
        plan["works"][0][key] = "0" * 64
    elif change == "order":
        plan["works"].reverse()
    elif change == "code":
        plan["implementation_sha256"] = "0" * 64
    else:
        plan["scoring"] = "silently count partial success"
    path.write_bytes(encoded(plan))
    with pytest.raises(ValueError):
        execute(frozen, lambda request: pytest.fail("unexpected callback"))
    assert not (path.parent / "journal").exists()


def test_partial_export_is_not_repaired(frozen: tuple[Path, dict[str, Any]]) -> None:
    _, journal = execute(
        frozen, lambda request: httpx.Response(500, json={"error": {"code": "unavailable"}})
    )
    output = journal.with_name(journal.name + "-audit")
    output.mkdir()
    (output / "audit.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        report(frozen, journal)
    assert (output / "audit.json").read_text(encoding="utf-8") == "{}"
