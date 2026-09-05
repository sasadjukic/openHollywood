"""Offline regressions for status-dependent Story Bible thread changes."""

from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation, InvocationStatus, RunStatus
from open_hollywood_api.services.agentic_benchmark import AgenticBenchmarkBlueprintService
from open_hollywood_api.services.blueprint_model_executor import BenchmarkBlueprintNodeExecutor
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.model_profiles import BUILTIN_PROFILE_IDS, ModelProfileStore
from open_hollywood_api.services.production_model_executor import (
    BenchmarkProductionExecutor,
    _materialize_thread_change,
    _Operation,
    _output_schema,
    _schema_repair_guidance,
    _structured_failure_issues,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_workflow import BenchmarkSceneProductionService
from open_hollywood_engine.artifacts import ArtifactKind, StoryBibleThread
from open_hollywood_engine.evaluations import (
    BenchmarkCase,
    BenchmarkProfileSnapshot,
    BenchmarkSystem,
    load_benchmark_corpus,
)
from open_hollywood_engine.models import (
    ModelDeployment,
    ModelProfileMode,
    ModelRequest,
    ModelResponse,
    ModelSelection,
)
from open_hollywood_engine.workflows import (
    BlueprintDecisionAction,
    BlueprintHumanDecision,
    RetryableSceneProductionError,
)
from sqlalchemy import Engine, select

from tests.evaluations.test_agentic_blueprint import CAMPAIGN_ID, CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


def _thread_change(**updates: object) -> dict[str, object]:
    return {
        "id": "thread_door",
        "kind": "mystery",
        "statement": "Why was the door locked?",
        "status": "resolved",
        "resolution": "The keeper admits locking it to protect the archive.",
        **updates,
    }


def test_model_thread_schema_requires_resolution_only_for_resolved_status() -> None:
    schema = _output_schema(_Operation.STORY_BIBLE_UPDATE, continuity_schema_variant=None)
    definitions = schema["$defs"]
    branches = definitions["StoryBibleThread"]["anyOf"]
    assert len(branches) == 2
    by_status = {}
    for reference in branches:
        branch = definitions[reference["$ref"].rsplit("/", 1)[-1]]
        by_status[branch["properties"]["status"]["const"]] = branch
        assert "resolved_scene_id" not in branch["properties"]
        assert branch["additionalProperties"] is False
    assert by_status["open"]["properties"]["resolution"]["type"] == "null"
    assert "resolution" not in by_status["open"]["required"]
    assert by_status["resolved"]["properties"]["resolution"]["type"] == "string"
    assert by_status["resolved"]["properties"]["resolution"]["minLength"] == 1
    assert "resolution" in by_status["resolved"]["required"]


def test_resolved_thread_derives_missing_scene_without_inventing_explanation() -> None:
    change = _thread_change()
    materialized = _materialize_thread_change(change, "scene_2", {})
    thread = StoryBibleThread.model_validate(materialized)
    assert thread.introduced_scene_id == thread.resolved_scene_id == "scene_2"
    assert thread.resolution == change["resolution"]
    assert "resolved_scene_id" not in change


def test_resolved_thread_preserves_existing_resolution_origin() -> None:
    existing = StoryBibleThread.model_validate(
        _thread_change(introduced_scene_id="scene_1", resolved_scene_id="scene_2")
    )
    thread = StoryBibleThread.model_validate(
        _materialize_thread_change(
            _thread_change(resolved_scene_id="invented_scene"),
            "scene_3",
            {existing.id: existing},
        )
    )
    assert thread.introduced_scene_id == "scene_1"
    assert thread.resolved_scene_id == "scene_2"


@pytest.mark.parametrize("resolution", [None, "", " \n ", 42])
def test_resolved_thread_missing_explanation_has_field_specific_safe_diagnostic(
    resolution: object,
) -> None:
    with pytest.raises(_StructuredOutputContractError) as caught:
        _materialize_thread_change(
            _thread_change(resolution=resolution), "scene_2", {}, location="thread_changes.3"
        )
    issues = _structured_failure_issues(caught.value)
    assert issues[0]["location"] == "thread_changes.3.resolution"
    assert issues[0]["type"] == "resolved_thread_missing_resolution"
    assert "requires a non-empty resolution" in issues[0]["message"]
    assert "received_value" not in issues[0]
    guidance = _schema_repair_guidance(
        operation=_Operation.STORY_BIBLE_UPDATE,
        deployment=ModelDeployment.LOCAL,
        previous_failure={
            "error_code": "schema_validation_failed",
            "validation_issues": list(issues),
        },
    )
    assert guidance is not None
    assert guidance["focus_locations"] == ["thread_changes.3.resolution"]
    assert "instead of inventing a resolution" in str(guidance["directives"])


def test_open_thread_clears_stale_application_owned_scene() -> None:
    thread = StoryBibleThread.model_validate(
        _materialize_thread_change(
            _thread_change(status="open", resolution=None, resolved_scene_id="invented_scene"),
            "scene_2",
            {},
        )
    )
    assert thread.resolved_scene_id is None
    assert thread.resolution is None


def test_open_thread_rejects_stale_explanation_without_echoing_it() -> None:
    with pytest.raises(_StructuredOutputContractError) as caught:
        _materialize_thread_change(
            _thread_change(status="open", resolution="PRIVATE EXPLANATION"),
            "scene_2",
            {},
            location="thread_changes.0",
        )
    issues = _structured_failure_issues(caught.value)
    assert issues[0]["location"] == "thread_changes.0.resolution"
    assert issues[0]["type"] == "open_thread_has_resolution"
    assert "PRIVATE EXPLANATION" not in json.dumps(issues)


class ThreadRepairGateway(ProductionFixtureGateway):
    """Omit explanation once or repeatedly; successful repair still omits scene lineage."""

    def __init__(self, prompt_text: str, prompt: Any, *, recover: bool) -> None:
        super().__init__(prompt_text, prompt)
        self.recover = recover
        self.first_scene_bible_calls = 0
        self.repair_payloads: list[dict[str, Any]] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        if request.invocation.specialist_role != "story_bible_maintainer":
            return response
        payload = json.loads(request.messages[-1].content)
        if payload["assignment"]["unit_number"] != 1:
            return response
        self.first_scene_bible_calls += 1
        if "schema_repair" in payload:
            self.repair_payloads.append(payload)
        content = json.loads(response.content)
        change = _thread_change()
        if not self.recover or self.first_scene_bible_calls == 1:
            change.pop("resolution")
        content["thread_changes"] = [change]
        return replace(response, content=json.dumps(content))


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
@pytest.mark.parametrize("recover", [True, False])
async def test_story_thread_repair_is_actionable_persisted_and_bounded(
    recover: bool,
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    session_factory = create_session_factory(database_engine)
    profile = ModelProfileStore(session_factory).configure_profile(
        BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL],
        local_model=ModelSelection(
            provider="ollama", model_identifier="local-fixture", deployment=ModelDeployment.LOCAL
        ),
        cloud_model=None,
    )
    case = BenchmarkCase(
        case_id=uuid4(),
        prompt_id=prompt.prompt_id,
        prompt_version=prompt.version,
        system=BenchmarkSystem.AGENTIC,
        run_seed=prompt.random_seed,
        profile=BenchmarkProfileSnapshot.from_configuration(
            profile_id=profile.id, configuration=profile.configuration
        ),
    )
    gateway = ThreadRepairGateway(prompt.prompt, prompt, recover=recover)
    blueprint_service = AgenticBenchmarkBlueprintService(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    prepared = await blueprint_service.prepare(case, prompt)
    assert prepared.interrupt_id is not None
    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        BenchmarkBlueprintNodeExecutor(session_factory=session_factory, gateway=gateway),
    ) as workflow:
        approved = await workflow.resume(
            prepared.workflow_run_id,
            BlueprintHumanDecision(
                id=uuid4(),
                interrupt_id=prepared.interrupt_id,
                action=BlueprintDecisionAction.APPROVE,
            ),
        )
    blueprint = next(
        item for item in approved.artifacts if item.kind is ArtifactKind.STORY_BLUEPRINT
    )
    async with BenchmarkSceneProductionService(
        database_path=migrated_database_path,
        session_factory=session_factory,
        executor=BenchmarkProductionExecutor(session_factory=session_factory, gateway=gateway),
        cost_ceiling_usd=Decimal("5.00"),
    ) as production:
        if recover:
            result = await production.execute(prepared.workflow_run_id, blueprint)
            assert result.status is RunStatus.SUCCEEDED
        else:
            with pytest.raises(RetryableSceneProductionError, match="invalid structured output"):
                await production.execute(prepared.workflow_run_id, blueprint)

    assert gateway.first_scene_bible_calls == 2
    assert len(gateway.repair_payloads) == 1
    repair = gateway.repair_payloads[0]["schema_repair"]
    assert repair["focus_locations"] == ["thread_changes.0.resolution"]
    assert "instead of inventing a resolution" in str(repair["directives"])
    with session_factory() as session:
        invocations = session.scalars(
            select(AgentInvocation)
            .where(AgentInvocation.specialist_role == "story_bible_maintainer")
            .order_by(AgentInvocation.started_at)
        ).all()
    assert [item.retry_count for item in invocations[:2]] == [0, 1]
    assert invocations[0].status is InvocationStatus.FAILED
    assert invocations[1].status is (
        InvocationStatus.SUCCEEDED if recover else InvocationStatus.FAILED
    )
    diagnostic = invocations[0].request_settings["structured_failure"]["issues"][0]
    assert diagnostic["location"] == "thread_changes.0.resolution"
    assert diagnostic["type"] == "resolved_thread_missing_resolution"
