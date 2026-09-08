"""Isolated probes exercise real production validation without mutating their source."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from scripts.production_probe import load_probe, probe_request, run_probe
from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class RepairProbeGateway(V26Gateway):
    def __init__(self, *args: Any, always_invalid: bool = False, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.enabled = False
        self.probe_calls = 0
        self.always_invalid = always_invalid

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        if self.enabled:
            self.probe_calls += 1
            if self.probe_calls == 1 or self.always_invalid:
                raw = json.loads(response.content)
                raw["point_of_view_check"] = {
                    "status": "violation",
                    "draft_evidence": "Not a quote",
                }
                return replace(response, content=json.dumps(raw))
        return response


@pytest.mark.anyio
@pytest.mark.parametrize("operation", ["critique", "story_bible_update"])
async def test_frozen_probe_uses_real_boundary_and_preserves_database(
    operation: str,
    migrated_database_path: Path,
    database_engine: Engine,
    tmp_path: Path,
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = V26Gateway(prompt.prompt, prompt, mode="thread_echo")
    await _run_gateway(gateway, migrated_database_path, database_engine)
    sessions = create_session_factory(database_engine)
    with sessions() as session:
        invocation = next(
            item
            for item in session.scalars(select(AgentInvocation)).all()
            if item.request_settings.get("operation") == operation
        )
        invocation_id = invocation.id
    before = hashlib.sha256(migrated_database_path.read_bytes()).hexdigest()
    probe = load_probe(migrated_database_path, invocation_id)
    request = probe_request(probe, probe.execution)
    assert request.invocation.input_artifact_version_ids == probe.execution.input_version_ids
    assert probe.manifest["input_artifact_sha256"]
    count = len(gateway.requests)
    output = tmp_path / "isolated-result"
    summary = await run_probe(probe, gateway, output)
    assert summary["status"] == "validated"
    assert len(gateway.requests) == count + 1
    assert (output / "attempt-1-request.json").exists()
    record = json.loads((output / "attempt-1-result.json").read_text(encoding="utf-8"))
    if operation == "story_bible_update":
        assert record["successor_bible"]["threads"][0]["resolved_scene_id"] == "scene_1"
    assert hashlib.sha256(migrated_database_path.read_bytes()).hexdigest() == before
    with pytest.raises(FileExistsError):
        await run_probe(probe, gateway, output)
    with pytest.raises(ValueError, match="protected canary"):
        await run_probe(probe, gateway, migrated_database_path.parent / "unsafe")
    cloud = replace(
        probe,
        execution=replace(
            probe.execution,
            selection=replace(probe.execution.selection, deployment=ModelDeployment.CLOUD),
        ),
    )
    with pytest.raises(ValueError, match="allow-cloud"):
        await run_probe(cloud, gateway, tmp_path / "cloud-not-authorized")
    assert len(gateway.requests) == count + 1


@pytest.mark.anyio
@pytest.mark.parametrize("always_invalid", [False, True])
async def test_probe_allows_only_one_response_repair_never_writer_revisions(
    always_invalid: bool,
    migrated_database_path: Path,
    database_engine: Engine,
    tmp_path: Path,
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = RepairProbeGateway(
        prompt.prompt, prompt, mode="thread_echo", always_invalid=always_invalid
    )
    await _run_gateway(gateway, migrated_database_path, database_engine)
    sessions = create_session_factory(database_engine)
    with sessions() as session:
        invocation = next(
            item
            for item in session.scalars(select(AgentInvocation)).all()
            if item.request_settings.get("operation") == "critique"
        )
        invocation_id = invocation.id
    gateway.enabled = True
    probe = load_probe(migrated_database_path, invocation_id)
    summary = await run_probe(probe, gateway, tmp_path / "repair-probe")
    assert summary["status"] == ("failed" if always_invalid else "validated")
    assert gateway.probe_calls == summary["attempts"] == 2
    payload = json.loads(gateway.requests[-1].messages[-1].content)
    assert payload["assignment"]["operation"] == "critique"
    assert payload["retry_context"]["manuscript_defect_established"] is False
    assert "Not a quote" not in json.dumps(payload)
