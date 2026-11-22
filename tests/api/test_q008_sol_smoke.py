"""Exercise the single-claim journals at the HTTP boundary using a portable saved review."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import ModuleType

import httpx
import pytest
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_openai_fixture as wire
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts import ordinary_v61_capture as ledger
from scripts import q008_sol_smoke, q010_assessment, q010_sol_smoke, q013_sol_smoke
from tests.api.test_saved_review_completion import anyio_backend as anyio_backend
from tests.api.test_saved_review_completion import archive as archive
from tests.api.test_saved_review_completion import prepared as prepared
from tests.api.test_saved_review_completion import source as source

pytestmark = pytest.mark.anyio


@pytest.fixture(
    params=(q008_sol_smoke, q013_sol_smoke, q010_sol_smoke), ids=("q008", "q013", "q010")
)
def smoke(request: pytest.FixtureRequest) -> ModuleType:
    runner = request.param
    assert isinstance(runner, ModuleType)
    return runner


@pytest.fixture
def issued(
    archive: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, smoke: ModuleType
) -> tuple[Path, str, wire._Plan]:
    # The source fixture blocks sockets. Keep AsyncClient.send available for MockTransport.
    def deny_real_transport(*args: object, **kwargs: object) -> None:
        pytest.fail("Qualification attempted to construct a network transport")

    monkeypatch.setattr(httpx, "AsyncHTTPTransport", deny_real_transport)
    gold = tmp_path / "scorer" / "gold.json"
    gold.parent.mkdir()
    gold.write_bytes(encoded({"scorer_only": "private-operator-witness"}))
    monkeypatch.setattr(smoke, "GOLD", gold)
    monkeypatch.setattr(smoke, "GOLD_SHA", ledger.file_hash(gold))
    p = wire._prepare("unit", None)
    binding = (
        q010_assessment.Plan(p.work, p.source.selected, p.source.pin.draft, p.wire, p.files)
        if smoke is q010_sol_smoke
        else p
    )
    monkeypatch.setattr(smoke, "source", lambda: binding)
    folder = tmp_path / "qualification"
    folder.mkdir()
    raw = smoke._plan(binding)
    for name, body in (p.files | {"plan.json": raw}).items():
        (folder / name).write_bytes(body)
    digest = storage._sha(raw)
    ledger.initialize_ledger(folder, digest)
    return folder, digest, p


@pytest.mark.parametrize(
    ("fault", "expected", "attempts"),
    [
        ("success", "bound_unassessed", 2),
        ("count-limit", "count_rejected", 1),
        ("server-error", "http_error", 1),
        ("missing-claim", "invalid_claim_or_citation", 2),
        ("missing-usage", "accounting_hold", 2),
        ("lost-connection", "transport_error", 2),
    ],
)
async def test_dispatch_order_terminal_and_no_restart(
    issued: tuple[Path, str, wire._Plan],
    fault: str,
    expected: str,
    attempts: int,
    smoke: ModuleType,
) -> None:
    folder, approval, p = issued
    seen: list[str] = []

    def handle(req: httpx.Request) -> httpx.Response:
        end = p.wire.endpoints[len(seen)]
        assert req.content == (folder / (end.stage + "-request.json")).read_bytes()
        assert str(req.url) == end.destination + end.path
        assert (folder / "output" / (end.stage + "-intent.json")).is_file()
        assert ledger.ledger_state(folder, approval) == "dispatched"
        assert b"private-operator-witness" not in req.content
        seen.append(end.stage)
        if fault == "server-error":
            return httpx.Response(500, json={"error": {"code": "server_error"}})
        body = json.loads(wire._reply(p, end, "complete"))
        if end.stage == "input_count" and fault == "count-limit":
            body["input_tokens"] = p.wire.max_input_tokens + 1
        if end.stage == "generation":
            if fault == "missing-claim":
                body["output"][0]["content"][0]["text"] = '{"assessments":{}}'
            if fault == "missing-usage":
                del body["usage"]
            if fault == "lost-connection":
                raise httpx.ReadError("injected")
        return httpx.Response(200, json=body)

    transport = httpx.MockTransport(handle)
    assert await smoke.qualify(folder, approval, transport) == expected
    audit = smoke.audit(folder, approval)
    assert audit["closed"] and audit["state"] == expected and not audit["eligible_for_scoring"]
    assert (audit["bound_result"] is not None) == (fault == "success")
    assert seen == ["input_count", "generation"][:attempts]
    with pytest.raises(EvidenceError, match="consumed"):
        await smoke.qualify(folder, approval, transport)
    assert len(seen) == attempts
    if fault == "success":
        target = folder / "output/generation-outcome.json"
        terminal = json.loads(target.read_bytes())
        terminal["elapsed_seconds"] += 1
        target.write_bytes(encoded(terminal))
        with pytest.raises(EvidenceError, match="chain"):
            smoke.audit(folder, approval)


async def test_cancelled_generation_and_preflight(
    issued: tuple[Path, str, wire._Plan], smoke: ModuleType
) -> None:
    folder, approval, p = issued
    seen = []

    def handle(req: httpx.Request) -> httpx.Response:
        seen.append(req.url.path)
        if len(seen) == 2:
            raise asyncio.CancelledError()
        return httpx.Response(200, content=wire._reply(p, p.wire.endpoints[0], "complete"))

    transport = httpx.MockTransport(handle)
    with pytest.raises(EvidenceError, match="approval_hash"):
        await smoke.qualify(folder, "f" * 64, transport)
    request = folder / "generation-request.json"
    original = request.read_bytes()
    request.write_bytes(original + b" ")
    with pytest.raises(EvidenceError, match="wire_drift"):
        await smoke.qualify(folder, approval, transport)
    request.write_bytes(original)
    assert not seen and ledger.ledger_state(folder, approval) == "ready"
    with pytest.raises(asyncio.CancelledError):
        await smoke.qualify(folder, approval, transport)
    audit = smoke.audit(folder, approval)
    assert audit["state"] == "possibly_sent" and not audit["closed"] and not audit["bound_result"]
    with pytest.raises(EvidenceError, match="consumed"):
        await smoke.qualify(folder, approval, transport)
    assert len(seen) == 2
