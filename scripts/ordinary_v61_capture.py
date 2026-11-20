"""Verify the frozen ordinary critic capture, or spend its single approved dispatch."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import shutil
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Literal, cast
from uuid import UUID

import httpx
from open_hollywood_api.persistence.database import create_session_factory, create_sqlite_engine
from open_hollywood_api.persistence.models import AgentInvocation, ArtifactVersion, WorkflowRun
from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_api.services.assessment_intake import collect_intakes
from open_hollywood_api.services.production_model_executor import (
    ProfileRoutedProductionExecutor,
    _critique_inputs,
    _reference,
)
from open_hollywood_api.services.review_evidence_export import collect_export, write_export
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import Digest, Record, require, strict_object
from open_hollywood_engine.models.ollama import OllamaGateway
from open_hollywood_engine.workflows import SceneCritiqueTask
from open_hollywood_engine.workflows.production_graph import (
    ProductionGraphState,
    _production_from_state,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "data/diagnostics/ordinary-v61-single-capture-2026-11-20"
SOURCE = REPO / "data/benchmarks/v0.1/formal-cloud-v33-2026-09-29/campaign.db"
URL = "http://127.0.0.1:11434/api/chat"
WIRE_SHA = "35452ffd86fe44f4639f3fada86b7d00a97c1aaece16911dcba5e6195392bc51"
MESSAGE_SHA = "2a6de460883c71b08c6f5c6a7e89405385d1802bb88227affbc282c2dbec96f7"


class SourceVersion(Record):
    version: UUID
    sha256: Digest


class Plan(Record):
    contract: Literal["single-ordinary-v61-critic-1"]
    run_id: UUID
    live_directory: str
    source_invocation: UUID
    source_files: dict[str, Digest]
    inputs: dict[str, SourceVersion]
    seed_sha256: Digest
    task_sha256: Digest
    implementation: dict[str, Digest]
    request_sha256: Digest
    prompt_sha256: Digest
    request_bytes: int
    destination: Literal["http://127.0.0.1:11434/api/chat"]
    model: Literal["gemma4:31b-cloud"]
    input_tokens: Literal[24000]
    output_tokens: Literal[8000]
    reserved_usd: Literal["0.20"]
    deadline_seconds: Literal[300]
    generations: Literal[1]
    counts: Literal[0]
    retries: Literal[0]
    payload: str
    stops: tuple[str, ...]


def file_hash(path: Path) -> str:
    with storage._unlinked(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_plan(root: Path, approval: str) -> Plan:
    plan_bytes = storage._read(root / "plan.json")
    require(hashlib.sha256(plan_bytes).hexdigest() == approval, "approval_hash_mismatch")
    plan = Plan.model_validate_json(plan_bytes)
    require(plan.live_directory == str(ROOT), "registration_location_mismatch")
    require(plan.request_sha256 == WIRE_SHA and plan.prompt_sha256 == MESSAGE_SHA, "wrong_request")
    require(file_hash(root / "request.json") == WIRE_SHA, "frozen_wire_drift")
    require((root / "request.json").stat().st_size == plan.request_bytes, "frozen_size_drift")
    require(file_hash(root / "task.json") == plan.task_sha256, "frozen_task_drift")
    require(file_hash(root / "seed.db") == plan.seed_sha256, "frozen_database_drift")
    for path, digest in plan.implementation.items():
        require(file_hash(REPO / path) == digest, "implementation_drift")
    source_files = {
        suffix: file_hash(member)
        for suffix in ("", "-shm", "-wal", "-journal")
        if (member := Path(str(SOURCE) + suffix)).exists()
    }
    require(source_files == plan.source_files, "archived_source_drift")
    return plan


def initialize_ledger(root: Path, approval: str) -> None:
    """Offline issuance only. An existing ledger or output always consumes this path."""
    require(not (root / "output").exists(), "existing_capture_output")
    path = storage._unlinked(root / "dispatch.sqlite3")
    path.touch(exist_ok=False)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("PRAGMA synchronous=FULL")
        db.execute(
            "CREATE TABLE dispatch(slot INTEGER PRIMARY KEY CHECK(slot=1), approval TEXT NOT NULL,"
            " state TEXT NOT NULL CHECK(state IN ('ready','claimed','dispatched')),"
            " changed_at TEXT)"
        )
        db.execute("INSERT INTO dispatch VALUES(1, ?, 'ready', NULL)", (approval,))


def ledger_state(root: Path, approval: str, transition: tuple[str, str] | None = None) -> str:
    # mode=rw refuses a lost ledger. Only the offline freeze creates the ready row.
    ledger = storage._unlinked(root / "dispatch.sqlite3")
    uri = ledger.as_uri() + ("?mode=ro" if transition is None else "?mode=rw")
    with closing(sqlite3.connect(uri, uri=True, timeout=10)) as db, db:
        if transition is not None:
            require(
                transition in {("ready", "claimed"), ("claimed", "dispatched")},
                "invalid_transition",
            )
            db.execute("PRAGMA synchronous=FULL")
            old, new = transition
            changed = db.execute(
                "UPDATE dispatch SET state=?, changed_at=? WHERE slot=1 AND approval=? AND state=?",
                (new, datetime.now(UTC).isoformat(), approval, old),
            ).rowcount
            require(changed == 1, "attempt_already_consumed_or_wrong_ledger")
        row = db.execute("SELECT state FROM dispatch WHERE slot=1 AND approval=?", (approval,))
        found = row.fetchone()
        require(found is not None, "unregistered_ledger")
        return str(found[0])


class SinglePost(httpx.AsyncBaseTransport):
    """Commit the intent before handing any bytes to the underlying transport."""

    def __init__(self, root: Path, approval: str, transport: httpx.AsyncBaseTransport) -> None:
        self.root = root
        self.approval = approval
        self.transport = transport

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        require(request.method == "POST" and str(request.url) == URL, "endpoint_drift")
        require(hashlib.sha256(request.content).hexdigest() == WIRE_SHA, "wire_drift")
        ledger_state(self.root, self.approval, ("claimed", "dispatched"))
        response = await self.transport.handle_async_request(request)
        try:
            raw = await response.aread()
            receipt: dict[str, object] = {
                "http_status": response.status_code,
                "response_sha256": hashlib.sha256(raw).hexdigest(),
                "input_tokens": None,
                "output_tokens": None,
            }
            try:
                payload = strict_object(raw.decode("utf-8"))
                active_secret_guard().ensure_safe(payload, destination="private capture receipt")
            except (ValueError, UnicodeError):
                payload = {}
            else:
                for field, key in (
                    ("input_tokens", "prompt_eval_count"),
                    ("output_tokens", "eval_count"),
                ):
                    value = payload.get(key)
                    if type(value) is int and value >= 0:
                        receipt[field] = value
                receipt["response"] = payload
            _durable_write(self.root / "output/http.json", encoded(receipt))
            # Preserve ordinary error classification for 4xx/5xx replies.
            if response.status_code < 400:
                require(response.status_code == 200, "unexpected_http_status")
                require(
                    payload.get("done") is True and payload.get("done_reason") == "stop",
                    "incomplete_or_truncated_delivery",
                )
            return response
        finally:
            await response.aclose()

    async def aclose(self) -> None:
        await self.transport.aclose()


def load_task(session: Session, root: Path, plan: Plan) -> SceneCritiqueTask:
    state = cast(ProductionGraphState, json.loads(storage._read(root / "task.json")))
    production = _production_from_state(state)
    run = session.get(WorkflowRun, plan.run_id)
    require(run is not None and production.workflow_run_id == plan.run_id, "wrong_run")
    assert run is not None
    require(
        run.input_state.get("execution_kind") == "isolated_ordinary_critic_capture"
        and run.graph_version == "9"
        and production.prompt_template_version == "61",
        "wrong_run_contract",
    )
    require(
        not session.scalars(
            select(AgentInvocation.id).where(AgentInvocation.workflow_run_id == plan.run_id)
        ).first(),
        "prior_invocation_or_replay",
    )
    versions = {}
    for kind, pin in plan.inputs.items():
        version = session.get(ArtifactVersion, pin.version)
        require(version is not None, "missing_input")
        assert version is not None
        require(
            version.artifact.artifact_type == kind
            and version.artifact.project_id == run.project_id
            and canonical_sha256(version.content) == version.content_sha256 == pin.sha256,
            "wrong_source_version",
        )
        versions[kind] = _reference(version)
    task = SceneCritiqueTask(
        production,
        production.units[0],
        versions["scene_draft"],
        (),
        production.initial_story_bible,
        0,
    )
    require(set(_critique_inputs(task)) == set(versions.values()), "task_binding_drift")
    return task


async def capture(root: Path, approval: str, *, fixture: httpx.MockTransport | None = None) -> str:
    require((fixture is None) == (storage._unlinked(root) == ROOT), "live_root_is_fixed")
    plan = load_plan(root, approval)
    ledger_state(root, approval, ("ready", "claimed"))
    out = storage._unlinked(root / "output")
    out.mkdir(exist_ok=False)
    database = out / "workspace.db"
    shutil.copyfile(root / "seed.db", database)
    require(file_hash(database) == plan.seed_sha256, "working_copy_drift")
    engine = create_sqlite_engine(database)
    sessions = create_session_factory(engine)
    terminal: dict[str, object] = {
        "approval_sha256": approval,
        "run_id": str(plan.run_id),
        "origin": "injected" if fixture is not None else "isolated_provider_capture",
        "status": "stopped",
        "input_tokens": None,
        "output_tokens": None,
    }
    started = monotonic()
    try:
        with sessions() as session:
            task = load_task(session, root, plan)
        inner = (
            fixture if fixture is not None else httpx.AsyncHTTPTransport(retries=0, trust_env=False)
        )
        gate = SinglePost(root, approval, inner)
        async with (
            asyncio.timeout(plan.deadline_seconds),
            httpx.AsyncClient(
                base_url=URL.removesuffix("/api/chat"),
                transport=gate,
                timeout=plan.deadline_seconds,
                follow_redirects=False,
                trust_env=False,
            ) as client,
        ):
            executor = ProfileRoutedProductionExecutor(
                session_factory=sessions, gateway=OllamaGateway(client=client)
            )
            result = await executor.critique(task)
        require(ledger_state(root, approval) == "dispatched", "cached_result_refused")
        with sessions() as session:
            invocation = session.scalars(
                select(AgentInvocation).where(AgentInvocation.workflow_run_id == plan.run_id)
            ).one()
            require(
                invocation.retry_count == 0
                and invocation.prompt_sha256 == MESSAGE_SHA
                and invocation.schema_validation_succeeded is True,
                "wrong_invocation",
            )
            invocation_id = invocation.id
        exported = collect_export(database, (invocation_id,))
        entry = exported.entries[0]
        require(entry.reason == "compatible" and entry.snapshot is not None, "incompatible_export")
        assert entry.snapshot is not None
        require(
            entry.snapshot.critique.version_id == str(result.artifact.version_id)
            and entry.snapshot.draft_version_id == str(plan.inputs["scene_draft"].version)
            and entry.snapshot.plan_version_id == str(plan.inputs["scene_plan"].version),
            "wrong_output_binding",
        )
        intake = collect_intakes("saved_review", database, (str(invocation_id),))
        require(intake.entries[0].reason == "compatible", "incompatible_intake")
        write_export(out / "export", exported)
        terminal.update(
            status="captured",
            invocation_id=str(invocation_id),
            critique_version=str(result.artifact.version_id),
        )
    except (Exception, asyncio.CancelledError) as exc:
        terminal["error_type"] = type(exc).__name__
        chain: list[str] = []
        cause: BaseException | None = exc
        while cause is not None and len(chain) < 12:
            chain.append(type(cause).__name__)
            cause = cause.__cause__ or cause.__context__
        terminal["error_chain"] = chain
        raise
    finally:
        engine.dispose()
        terminal["elapsed_seconds"] = round(monotonic() - started, 3)
        terminal["dispatch_state"] = ledger_state(root, approval)
        terminal["database_sha256"] = file_hash(database)
        if (out / "http.json").exists():
            raw = (out / "http.json").read_bytes()
            report = json.loads(raw)
            terminal.update(
                http_sha256=hashlib.sha256(raw).hexdigest(),
                http_status=report["http_status"],
                input_tokens=report["input_tokens"],
                output_tokens=report["output_tokens"],
            )
        _durable_write(out / "terminal.json", encoded(terminal))
    return str(terminal["status"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    commands.add_parser("verify")
    run = commands.add_parser("run")
    run.add_argument("--approved-plan-sha256", required=True)
    run.add_argument("--send-full-prose", action="store_true", required=True)
    args = parser.parse_args()
    try:
        if args.mode == "verify":
            approval = file_hash(ROOT / "plan.json")
            load_plan(ROOT, approval)
            print(json.dumps({"plan_sha256": approval, "slot": ledger_state(ROOT, approval)}))
        else:
            print(asyncio.run(capture(ROOT, args.approved_plan_sha256)))
        return 0
    except (ValueError, OSError, sqlite3.Error, RuntimeError) as exc:
        print(json.dumps({"status": "stopped", "error_type": type(exc).__name__}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
