"""Three authored works: injected real-client configuration, durable audit and fail-closed stops."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services import assessment_authored_source as source_service
from open_hollywood_api.services import assessment_delivery as io
from open_hollywood_api.services import assessment_openai_authored_delivery as rehearsal
from open_hollywood_api.services import assessment_openai_authored_smoke as service
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import text_hash
from open_hollywood_engine.secrets import SecretValue

from scripts import assessment_openai_authored_smoke as cli
from tests.api.test_assessment_openai_compact_smoke import offline as offline
from tests.authored_source_fixtures import make_archive, reseal, submission
from tests.evaluations.test_assessment_presentation import settings
from tests.models.test_assessment_openai import provider_body


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    assert isinstance(value, dict)
    return value


@pytest.fixture(scope="module")
def real_preparation(tmp_path_factory: pytest.TempPathFactory) -> Any:
    root = tmp_path_factory.mktemp("authored-smoke")
    archive = root / "archive"
    make_archive(archive)
    for family in service.NAMES:
        work = load(archive / "admitted" / family / "work.json")
        rows = []
        for statement, label in zip(
            work["context"]["statements"], ("supported", "unsupported", "uncertain"), strict=True
        ):
            rows.append(
                {
                    "unit_id": statement["unit_id"],
                    "whole_field": statement["quote"],
                    "whole_field_sha256": text_hash(statement["quote"]),
                    "judgment": label,
                    "rationale": "Fixture-only labels, not semantic truth; GOLD_SENTINEL",
                }
            )
        (archive / "admitted" / family / "admission.json").write_bytes(
            encoded({"family": family, "live_calls": 0, "rows": rows})
        )
    registration = reseal(archive)
    config = settings().model_copy(update={"max_input_tokens": 272000, "max_cost_usd": "1.00"})
    preparation = root / "preparation"
    with pytest.MonkeyPatch.context() as patcher:
        patcher.setattr(source_service, "REGISTERED", (registration,))
        rehearsal.prepare_requests(
            source_service.SOURCE_ID, preparation, run_id="smoke-fixture", settings=config
        )
        prepared = rehearsal._load(source_service.SOURCE_ID, preparation)
        yield preparation, prepared


@pytest.fixture
def frozen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, real_preparation: Any
) -> tuple[Path, dict[str, Any]]:
    preparation = real_preparation[0]
    prepared: rehearsal._Prepared = real_preparation[1]
    # Authenticate once with real registration, then retain exact source/preparation bytes.
    # Private qualification exercises repeated uncached collection on the actual three works.
    roots = [preparation, *prepared.collected[0].protected]
    pinned = {p: p.read_bytes() for root in roots for p in root.rglob("*") if p.is_file()}

    def collect(source_id: str, path: Path) -> rehearsal._Prepared:
        assert source_id == source_service.SOURCE_ID and path == preparation
        for p, raw in pinned.items():
            if p.read_bytes() != raw:
                raise ValueError("test_source_changed")
        return prepared

    monkeypatch.setattr(rehearsal, "_load", collect)
    scoring = tmp_path / "scoring.json"
    scoring.write_bytes(service.scoring_for(prepared))
    metadata = tmp_path / "metadata.json"
    metadata.write_bytes(
        encoded(
            {
                "provider_api_calls": 0,
                "model_spec": prepared.request_set.payload.settings.model_spec.model_dump(
                    mode="json"
                ),
            }
        )
    )
    path = tmp_path / "plan.json"
    service.freeze(
        source_service.SOURCE_ID, preparation, scoring, metadata, path, tmp_path / "live"
    )
    return path, {
        "prepared": prepared,
        "replies": [provider_body(submission(c.source)["raw_final"]) for c in prepared.collected],
    }


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


def test_all_six_slots_exact_client_bytes_headers_and_fsynced_intent(
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
        work = service._prepared(plan).request_set.payload.requests[n % 3]
        endpoint = work.payload.endpoints[n // 3]
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
            content=encoded({"input_tokens": 100} if n < 3 else data["replies"][n % 3]),
            headers={"x-request-id": f"req_{n}"},
        )

    status, journal = execute(frozen, handler)
    assert (
        status == "complete" and calls == ["/v1/responses/input_tokens"] * 3 + ["/v1/responses"] * 3
    )
    result = report(frozen, journal)
    assert len(result["slots"]) == 6 and all(w["completion_eligible"] for w in result["works"])
    assert result["count_intents"] == result["generation_intents"] == 3
    assert (
        result["delivery_origin"] == "injected_transport_fixture"
        and not result["model_observation"]
    )
    assert result["actual_billed_cost"] is None and not result["writer_dispatch_authorized"]
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in journal.iterdir()}
    with pytest.raises(ValueError, match="no_resume"):
        execute(frozen, handler)
    assert len(calls) == 6
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
        if n < 3:
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
    assert status == "halted" and len(calls) == (1 if count_failure else 4)
    result = report(frozen, journal)
    assert len(result["slots"]) == 6 and not result["works"][-1]["completion_eligible"]
    if failure == "over_usage":
        assert result["generations_with_unknown_usage"] == 0
        assert result["generations_with_accounting_hold"] == 1
    assert sum(s["state"] == "not_dispatched" for s in result["slots"]) == (
        5 if count_failure else 2
    )


@pytest.mark.parametrize("position", [0, 3])
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
    assert result["count_intents"] == min(position + 1, 3) and result["generation_intents"] == int(
        position == 3
    )
    assert len(result["slots"]) == 6


def test_elapsed_deadline_interrupts_transport_and_counts_attempt(
    frozen: tuple[Path, dict[str, Any]],
) -> None:
    prepared = service._prepared(service.load_plan(frozen[0])).request_set.payload.requests[0]

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
        return httpx.Response(200, json={"input_tokens": 100} if n < 3 else data["replies"][n % 3])

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
    assert len(calls) == (1 if count_failure else 6)
    with pytest.raises(ValueError):
        asyncio.run(service.run_live(path, live, digest, secret))
    assert len(made) == 1
    result = report(frozen, live)
    assert result["delivery_origin"] == "observed_openai_transport"
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
        return httpx.Response(200, json={"input_tokens": 100} if n < 3 else data["replies"][n % 3])

    _, journal = execute(frozen, handler)
    if change == "extra":
        (journal / "extra.json").write_text("{}", encoding="utf-8")
    elif change == "missing_stop":
        (journal / "event-0013.json").unlink()
    else:
        target = journal / (
            "header.json"
            if change == "origin"
            else "event-0013.json"
            if change == "wrong_stop"
            else "event-0002.json"
        )
        obj = load(target)
        if change == "origin":
            obj["delivery_origin"] = "observed_openai_transport"
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
    intake = Path(plan.scoring_path)
    original = intake.read_bytes()
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        intake.write_bytes(original + b" ")
        return httpx.Response(200, json={"input_tokens": 100})

    with pytest.raises(ValueError):
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


@pytest.mark.parametrize("position", [0, 1, 2])
def test_every_count_must_pass_before_any_generation(
    frozen: tuple[Path, dict[str, Any]], position: int
) -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(
            200, json={"input_tokens": 272001 if len(calls) == position + 1 else 100}
        )

    status, journal = execute(frozen, handler)
    assert status == "halted" and len(calls) == position + 1
    assert all(p == "/v1/responses/input_tokens" for p in calls)
    result = report(frozen, journal)
    assert result["generation_intents"] == 0
    assert len(result["slots"]) == 6


def test_deadline_after_durable_intent_does_not_send(
    frozen: tuple[Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    ticks = iter((0.0, 0.1, 3601.0))
    monkeypatch.setattr(service, "perf_counter", lambda: next(ticks))
    calls: list[httpx.Request] = []
    status, journal = execute(frozen, lambda request: calls.append(request))
    assert status == "deadline" and not calls
    result = report(frozen, journal)
    assert result["count_intents"] == 1 and result["generation_intents"] == 0
    assert result["slots"][0]["outcome"]["exchange"]["disposition"] == "cancelled"
    assert result["stop_reason"] == "deadline"


@pytest.mark.parametrize("failure", ["unknown_usage", "over_usage"])
def test_last_generation_accounting_hold_blocks_all_work_eligibility(
    frozen: tuple[Path, dict[str, Any]], failure: str
) -> None:
    _, data = frozen
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        n = len(calls)
        calls.append(request.url.path)
        body: dict[str, Any] = (
            {"input_tokens": 100} if n < 3 else json.loads(json.dumps(data["replies"][n % 3]))
        )
        if n == 5:
            if failure == "unknown_usage":
                body.pop("usage")
            else:
                body["usage"].update(input_tokens=272001, total_tokens=272021)
        return httpx.Response(200, json=body)

    status, journal = execute(frozen, handler)
    result = report(frozen, journal)
    assert status == "halted" and len(calls) == 6
    assert all(w["completion"]["complete_delivery"] for w in result["works"])
    assert not result["completion_eligible"]
    assert not any(w["completion_eligible"] for w in result["works"])
    assert result["generations_with_unknown_usage"] == int(failure == "unknown_usage")
    assert result["generations_with_accounting_hold"] == 1


@pytest.mark.parametrize("member", ["scoring_path", "metadata_path"])
def test_post_intent_drift_is_consumed_without_sending(
    frozen: tuple[Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch, member: str
) -> None:
    plan = service.load_plan(frozen[0])
    target = Path(getattr(plan, member))
    original = target.read_bytes()
    append = service.Journal.append

    def drift(self: service.Journal, payload: Any) -> str:
        result = append(self, payload)
        if isinstance(payload, service.Intent):
            target.write_bytes(original + b" ")
        return result

    monkeypatch.setattr(service.Journal, "append", drift)
    with pytest.raises(ValueError):
        execute(frozen, lambda request: pytest.fail("must not send after drift"))
    target.write_bytes(original)
    result = report(frozen, frozen[0].parent / "journal")
    assert result["count_intents"] == 1 and result["generation_intents"] == 0
    assert result["slots"][0]["state"] == "interrupted_unknown_usage"


@pytest.mark.parametrize(
    "field",
    [
        "request_set_sha256",
        "preparation_manifest_sha256",
        "implementation_sha256",
        "scoring_bytes_sha256",
        "metadata_bytes_sha256",
        "scoring",
        "stops",
    ],
)
def test_drift_refused_before_client_and_key(
    frozen: tuple[Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    path, _ = frozen
    obj = load(path)
    obj[field] = "0" * 64
    path.write_bytes(encoded(obj))
    monkeypatch.setattr(cli, "_secret", lambda: pytest.fail("key must not resolve"))
    assert (
        cli.main(
            [
                "run",
                "--plan",
                str(path),
                "--journal",
                obj["live_journal"],
                "--approved-plan-sha256",
                io._sha(path.read_bytes()),
                "--confirm-full-prose-openai-both-endpoints",
            ]
        )
        == 2
    )
    assert not Path(obj["live_journal"]).exists()


@pytest.mark.parametrize("relative", ["live", "live/child", "."])
def test_fixture_cannot_occupy_live_path_or_overlap(
    frozen: tuple[Path, dict[str, Any]], relative: str
) -> None:
    with pytest.raises(ValueError):
        asyncio.run(
            service.qualify(
                frozen[0],
                frozen[0].parent / relative,
                httpx.MockTransport(lambda request: pytest.fail("must not send")),
            )
        )


def test_audit_cannot_occupy_fixed_live_journal(frozen: tuple[Path, dict[str, Any]]) -> None:
    _, journal = execute(frozen, lambda request: httpx.Response(500, json={"error": {}}))
    with pytest.raises(ValueError):
        service.audit(frozen[0], journal, Path(service.load_plan(frozen[0]).live_journal))


def test_full_sources_gold_isolation_and_derived_authority(
    frozen: tuple[Path, dict[str, Any]],
) -> None:
    path, data = frozen
    plan = service.load_plan(path)
    prepared = service._prepared(plan)
    gold = load(Path(plan.scoring_path))
    assert len(gold["cases"]) == 3 and not gold["gold_in_model_input"]
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        n = len(calls)
        calls.append(request.url.path)
        assert b"GOLD_SENTINEL" not in request.content
        return httpx.Response(200, json={"input_tokens": 100} if n < 3 else data["replies"][n % 3])

    _, journal = execute(frozen, handler)
    result = report(frozen, journal)
    assert result["source_origin"] == "authored_diagnostic"
    assert result["semantic_support"] == result["evidence_adequacy"] == "unassessed"
    for c, row in zip(prepared.collected, result["works"], strict=True):
        assert row["source"] == c.source.model_dump(mode="json")
        assert row["source"]["result"] is None and row["source"]["receipt"] is None
        assert "delivery_origin" not in row["terminal"]  # no nested fixture label on observations
        assert len(row["terminal"]["bound_result"]["units"]) == 3
    assert len(list(journal.with_name("journal-audit").iterdir())) == 17
