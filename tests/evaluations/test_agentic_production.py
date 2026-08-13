"""Approved Blueprint to durable agentic scene-production integration tests."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    InvocationStatus,
    RunStatus,
    WorkflowRun,
)
from open_hollywood_api.services.agentic_benchmark import (
    AgenticBenchmarkBlueprintService,
    AgenticBenchmarkCaseExecutor,
)
from open_hollywood_api.services.blueprint_model_executor import (
    BenchmarkBlueprintNodeExecutor,
)
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.evaluation_campaign import (
    approve_agentic_cases,
    approve_reviewed_agentic_cases,
    build_blueprint_review_packet,
    prepare_agentic_cases,
    run_agentic_cases,
)
from open_hollywood_api.services.model_profiles import (
    BUILTIN_PROFILE_IDS,
    ModelProfileStore,
)
from open_hollywood_api.services.production_model_executor import (
    BenchmarkProductionExecutor,
    ContinuityRecheckStagnationError,
    _materialize_continuity_finding,
    _Operation,
    _select_production_model,
    _stagnant_continuity_finding_ids,
    _structured_failure_message,
)
from open_hollywood_api.services.production_workflow import (
    BenchmarkSceneProductionService,
)
from open_hollywood_engine.artifacts import (
    ArtifactKind,
    ContinuityCategory,
    ContinuityFinding,
    ContinuityReport,
    Critique,
    CritiqueVerdict,
    RubricScore,
    SceneDraft,
    StoryBible,
    StoryBibleInvariantError,
    StoryBibleScene,
    StoryBibleTimelineEvent,
    StoryBibleUpdate,
)
from open_hollywood_engine.evaluations import (
    BenchmarkCase,
    BenchmarkCaseExecutionError,
    BenchmarkCaseStatus,
    BenchmarkPlan,
    BenchmarkProfileSnapshot,
    BenchmarkSystem,
    build_benchmark_plan,
    load_benchmark_corpus,
    parse_blueprint_review_csv,
    render_blueprint_review_csv,
    render_blueprint_review_guide,
)
from open_hollywood_engine.models import (
    MODEL_PRESETS,
    ModelDeployment,
    ModelProfileMode,
    ModelRequest,
    ModelResponse,
    ModelSelection,
    ModelTiming,
    ModelUsage,
)
from open_hollywood_engine.workflows import (
    SCENE_PRODUCTION_GRAPH_VERSION,
    STORY_BLUEPRINT_GRAPH_VERSION,
    BlueprintDecisionAction,
    BlueprintHumanDecision,
    RetryableSceneProductionError,
)
from sqlalchemy import Engine, func, select

from scripts.evaluation_harness import AtomicJsonReportCheckpoint
from tests.evaluations.test_agentic_blueprint import (
    CAMPAIGN_ID,
    CORPUS_PATH,
    BlueprintFixtureGateway,
)


class ProductionFixtureGateway(BlueprintFixtureGateway):
    """Add production responses with deliberately invented application lineage."""

    async def generate(self, request: ModelRequest) -> ModelResponse:
        if request.invocation.specialist_role in {
            "brief_architect",
            "premise_architect",
            "world_builder",
            "character_architect",
            "blueprint_integrator",
            "blueprint_critic",
        }:
            return await super().generate(request)
        self.requests.append(request)
        payload = json.loads(request.messages[-1].content)
        input_items = payload["input_artifacts"]
        inputs = {item["artifact_kind"]: item for item in input_items}
        assignment = payload["assignment"]
        role = request.invocation.specialist_role
        value: Any
        if role == "scene_writer":
            plan = inputs[ArtifactKind.SCENE_PLAN.value]["content"]
            value = SceneDraft(
                scene_id=plan["id"],
                scene_number=plan["scene_number"],
                title=plan["title"],
                revision_number=assignment["revision_number"],
                prose=(
                    f"{plan['title']} opens with a concrete choice. "
                    "The characters act, conflict, and alter the situation. "
                    f"The scene reaches its planned turn: {plan['turning_point']} "
                    f"It closes in the declared exit state: {plan['exit_state']}"
                ),
                is_complete=True,
            )
        elif role == "scene_critic":
            draft = next(
                item
                for item in input_items
                if item["artifact_kind"] == ArtifactKind.SCENE_DRAFT.value
                and item["content"]["scene_id"] == assignment["unit_id"]
            )
            value = Critique(
                target_artifact_kind=ArtifactKind.SCENE_DRAFT,
                target_artifact_key=draft["artifact_key"],
                target_artifact_version_id=draft["artifact_version_id"],
                rubric_name="scene-production",
                rubric_version="1",
                summary="The complete scene reaches its planned dramatic turn.",
                strengths=("The scene changes the story state.",),
                scores=(
                    RubricScore(
                        dimension="dramatic_progress",
                        score=4,
                        rationale="The planned outcome is earned on the page.",
                    ),
                ),
                overall_score=4.0,
                verdict=CritiqueVerdict.PASS,
            )
        elif role == "continuity_supervisor":
            plan = inputs[ArtifactKind.SCENE_PLAN.value]
            draft = next(
                item
                for item in input_items
                if item["artifact_kind"] == ArtifactKind.SCENE_DRAFT.value
                and item["content"]["scene_id"] == assignment["unit_id"]
            )
            bible = inputs[ArtifactKind.STORY_BIBLE.value]
            value = ContinuityReport(
                story_bible_version_id=bible["artifact_version_id"],
                scene_version_id=draft["artifact_version_id"],
                scene_plan_version_id=plan["artifact_version_id"],
                scene_id=plan["content"]["id"],
                scene_number=plan["content"]["scene_number"],
                checked_categories=tuple(ContinuityCategory),
            )
        elif role == "story_bible_maintainer":
            plan = inputs[ArtifactKind.SCENE_PLAN.value]
            draft = next(
                item
                for item in input_items
                if item["artifact_kind"] == ArtifactKind.SCENE_DRAFT.value
                and item["content"]["scene_id"] == assignment["unit_id"]
            )
            report = next(
                item
                for item in input_items
                if item["artifact_kind"] == ArtifactKind.CONTINUITY_REPORT.value
                and item["content"]["scene_id"] == assignment["unit_id"]
            )
            bible_input = inputs[ArtifactKind.STORY_BIBLE.value]
            bible = StoryBible.model_validate(bible_input["content"])
            scene_id = plan["content"]["id"]
            value = StoryBibleUpdate(
                source_story_bible_version_id=bible_input["artifact_version_id"],
                continuity_report_version_id=report["artifact_version_id"],
                accepted_scene=StoryBibleScene(
                    scene_id=scene_id,
                    scene_number=plan["content"]["scene_number"],
                    artifact_version_id=draft["artifact_version_id"],
                ),
                timeline_events=(
                    StoryBibleTimelineEvent(
                        id=f"{scene_id}_event",
                        sequence=len(bible.timeline) + 1,
                        scene_id=scene_id,
                        time_context=plan["content"]["time_context"],
                        summary=plan["content"]["outcome"],
                        character_ids=tuple(plan["content"]["character_ids"]),
                        location_id=plan["content"]["location_id"],
                    ),
                ),
            )
        else:
            raise AssertionError(f"unexpected specialist role {role}")
        content = json.loads(value.model_dump_json())
        invented_version_id = "20240730-a1b2-43d4-a5f6-7890abcdef00"
        if role == "scene_writer":
            content["scene_id"] = "model_invented_scene"
            content["scene_number"] = 999
            content["revision_number"] = 999
        elif role == "scene_critic":
            content["target_artifact_key"] = "model_invented_draft"
            content["target_artifact_version_id"] = invented_version_id
        elif role == "continuity_supervisor":
            content.update(
                story_bible_version_id=invented_version_id,
                scene_version_id=invented_version_id,
                scene_plan_version_id=invented_version_id,
                scene_id="model_invented_scene",
                scene_number=999,
            )
        elif role == "story_bible_maintainer":
            content["source_story_bible_version_id"] = invented_version_id
            content["continuity_report_version_id"] = invented_version_id
            content["accepted_scene"].update(
                scene_id="model_invented_scene",
                scene_number=999,
                artifact_version_id=invented_version_id,
            )
            for event in content["timeline_events"]:
                event["scene_id"] = "model_invented_scene"
                event["id"] = "model_invented_event"
                event["sequence"] = 999
            content["prohibited_contradictions"] = [
                "fixture canonical prohibition",
                "fixture canonical prohibition",
            ]
        return ModelResponse(
            provider=self.provider,
            model_identifier=request.model_identifier,
            deployment=(
                ModelDeployment.CLOUD
                if request.model_identifier == "cloud-fixture"
                else ModelDeployment.LOCAL
            ),
            content=json.dumps(content),
            thinking=None,
            finish_reason="stop",
            created_at=datetime.now(UTC),
            usage=ModelUsage(input_tokens=400, output_tokens=600),
            timing=ModelTiming(total_ms=120),
            estimated_cost_usd=Decimal("0"),
        )


class FirstBlueprintFailureGateway(ProductionFixtureGateway):
    """Exhaust integration repair for the first case, then return valid outputs."""

    def __init__(self, prompt_text: str, prompt: Any) -> None:
        super().__init__(prompt_text, prompt)
        self.invalid_integrations = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        if (
            request.invocation.specialist_role == "blueprint_integrator"
            and self.invalid_integrations < 2
        ):
            self.invalid_integrations += 1
            content = json.loads(response.content)
            content["scene_plans"][0]["location_id"] = "null"
            return replace(response, content=json.dumps(content))
        return response


class OneProductionRepairGateway(ProductionFixtureGateway):
    """Omit one required continuity resolution, then return a valid repair."""

    def __init__(
        self,
        prompt_text: str,
        prompt: Any,
        *,
        repeat_invalid: bool = False,
    ) -> None:
        super().__init__(prompt_text, prompt)
        self.invalid_sent = False
        self.repeat_invalid = repeat_invalid
        self.output_requirements: list[dict[str, object]] = []
        self.repair_contexts: list[dict[str, object]] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        if request.invocation.specialist_role != "continuity_supervisor":
            return await super().generate(request)
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        output_requirements = payload.get("output_requirements")
        if isinstance(output_requirements, dict):
            self.output_requirements.append(output_requirements)
        retry_context = payload.get("retry_context")
        if isinstance(retry_context, dict):
            self.repair_contexts.append(retry_context)
        if not self.invalid_sent or self.repeat_invalid:
            self.invalid_sent = True
            content = json.loads(response.content)
            content["findings"] = [
                {
                    "id": "model_finding_without_resolution",
                    "severity": "error",
                    "category": "fact",
                    "summary": "The candidate conflicts with an established fact.",
                    "evidence": ["The candidate and Story Bible disagree."],
                    "related_scene_ids": ["model_invented_scene"],
                    "recommended_resolution": None,
                    "blocks_approval": False,
                }
            ]
            return replace(response, content=json.dumps(content))
        return response


class ContinuityRevisionFeedbackGateway(ProductionFixtureGateway):
    """Capture one blocking report across its writer and continuity re-check lineage."""

    recommended_resolution = (
        "Keep Mara at the east door and have her return the brass key before she leaves."
    )

    def __init__(self, prompt_text: str, prompt: Any) -> None:
        super().__init__(prompt_text, prompt)
        self.blocking_report_sent = False
        self.missing_resolution_recheck_sent = False
        self.writer_revision_prompts: list[str] = []
        self.writer_revision_reports: list[dict[str, object]] = []
        self.continuity_recheck_prompts: list[str] = []
        self.continuity_recheck_reports: list[dict[str, object]] = []
        self.continuity_recheck_contracts: list[dict[str, object]] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        role = request.invocation.specialist_role
        revision_number = 0
        if role == "scene_writer":
            prompt = request.messages[-1].content
            payload = json.loads(prompt)
            revision_number = payload["assignment"]["revision_number"]
            if revision_number > 0:
                reports = [
                    item["content"]
                    for item in payload["input_artifacts"]
                    if item["artifact_kind"] == ArtifactKind.CONTINUITY_REPORT.value
                ]
                self.writer_revision_prompts.append(prompt)
                self.writer_revision_reports.extend(reports)
            return await super().generate(request)

        if role == "continuity_supervisor":
            prompt = request.messages[-1].content
            payload = json.loads(prompt)
            revision_number = payload["assignment"]["revision_number"]
            if revision_number > 0:
                reports = [
                    item["content"]
                    for item in payload["input_artifacts"]
                    if item["artifact_kind"] == ArtifactKind.CONTINUITY_REPORT.value
                ]
                recheck = payload.get("continuity_recheck")
                assert isinstance(recheck, dict)
                self.continuity_recheck_prompts.append(prompt)
                self.continuity_recheck_reports.extend(reports)
                self.continuity_recheck_contracts.append(recheck)

        response = await super().generate(request)
        if role != "continuity_supervisor":
            return response

        if not self.blocking_report_sent:
            self.blocking_report_sent = True
            return self._blocking_response(response, resolution=self.recommended_resolution)
        if revision_number == 1 and not self.missing_resolution_recheck_sent:
            self.missing_resolution_recheck_sent = True
            return self._blocking_response(
                response,
                resolution=None,
                summary="Mara still holds the brass key after crossing the east door.",
                evidence=["The revised draft says Mara pockets the key after crossing."],
            )
        return response

    def _blocking_response(
        self,
        response: ModelResponse,
        *,
        resolution: str | None,
        summary: str = "Mara changes doors without returning the established key.",
        evidence: list[str] | None = None,
    ) -> ModelResponse:
        content = json.loads(response.content)
        content["findings"] = [
            {
                "id": "east_door_key_continuity",
                "severity": "blocking",
                "category": "fact",
                "summary": summary,
                "evidence": evidence
                or ["The Story Bible places Mara at the east door with the brass key."],
                "related_scene_ids": ["model_invented_scene"],
                "recommended_resolution": resolution,
                "blocks_approval": False,
            }
        ]
        return replace(response, content=json.dumps(content))


class HybridStagnationEscalationGateway(ProductionFixtureGateway):
    """Repeat one local re-check judgment, then converge on its cloud retry."""

    recommended_resolution = (
        "Keep Mara at the east door and have her return the brass key before she leaves."
    )

    def __init__(self, prompt_text: str, prompt: Any) -> None:
        super().__init__(prompt_text, prompt)
        self.initial_blocker_sent = False
        self.escalated_retry_payloads: list[dict[str, object]] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        if request.invocation.specialist_role != "continuity_supervisor":
            return response

        payload = json.loads(request.messages[-1].content)
        assignment = payload["assignment"]
        revision_number = assignment["revision_number"]
        if not self.initial_blocker_sent:
            self.initial_blocker_sent = True
            return self._blocking_response(response)
        if revision_number == 1 and request.model_identifier == "local-fixture":
            return self._blocking_response(response)
        if revision_number == 1 and request.model_identifier == "cloud-fixture":
            self.escalated_retry_payloads.append(payload)
        return response

    def _blocking_response(self, response: ModelResponse) -> ModelResponse:
        content = json.loads(response.content)
        content["findings"] = [
            {
                "id": "east_door_key_continuity",
                "severity": "blocking",
                "category": "fact",
                "summary": "Mara changes doors without returning the established key.",
                "evidence": ["The Story Bible places Mara at the east door with the brass key."],
                "related_scene_ids": ["model_invented_scene"],
                "recommended_resolution": self.recommended_resolution,
                "blocks_approval": False,
            }
        ]
        return replace(response, content=json.dumps(content))


class RepeatedInvalidStoryBibleGateway(ProductionFixtureGateway):
    """Repeat an unknown canonical ID after receiving actionable repair context."""

    def __init__(self, prompt_text: str, prompt: Any, *, invalid_kind: str) -> None:
        super().__init__(prompt_text, prompt)
        self.invalid_kind = invalid_kind
        self.repair_contexts: list[dict[str, object]] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        if request.invocation.specialist_role != "story_bible_maintainer":
            return response
        payload = json.loads(request.messages[-1].content)
        retry_context = payload.get("retry_context")
        if isinstance(retry_context, dict):
            self.repair_contexts.append(retry_context)
        content = json.loads(response.content)
        if self.invalid_kind == "character":
            content["character_states"] = [
                {
                    "character_id": "model_invented_character",
                    "physical_state": "Unchanged.",
                    "emotional_state": "Alert.",
                    "current_goal": "Complete the scene.",
                    "last_updated_scene_id": "model_invented_scene",
                }
            ]
        elif self.invalid_kind == "location":
            content["location_states"] = [
                {
                    "location_id": "model_invented_location",
                    "state": "The scene changed this place.",
                    "last_updated_scene_id": "model_invented_scene",
                }
            ]
        else:
            raise AssertionError(f"unexpected invalid kind {self.invalid_kind}")
        return replace(response, content=json.dumps(content))


def test_continuity_routing_flag_is_derived_from_blocking_severity() -> None:
    finding = _materialize_continuity_finding(
        {
            "severity": "blocking",
            "blocks_approval": False,
            "related_scene_ids": ["model_invented_scene"],
        },
        "scene_1",
    )

    assert isinstance(finding, dict)
    assert finding["blocks_approval"] is True
    assert finding["related_scene_ids"] == ["model_invented_scene", "scene_1"]


def test_new_continuity_finding_cannot_inherit_another_findings_resolution() -> None:
    finding = _materialize_continuity_finding(
        {
            "id": "new_blocker",
            "severity": "blocking",
            "category": "fact",
            "summary": "A newly reported contradiction.",
            "evidence": ["Exact current draft evidence."],
            "related_scene_ids": [],
            "recommended_resolution": None,
            "blocks_approval": False,
        },
        "scene_1",
        prior_resolutions={"prior_blocker": "Preserve this exact prior repair."},
    )

    assert isinstance(finding, dict)
    assert finding["recommended_resolution"] is None
    with pytest.raises(ValueError, match="requires a resolution"):
        ContinuityFinding.model_validate(finding)


def test_continuity_recheck_rejects_stagnation_but_allows_convergence() -> None:
    prior_finding = {
        "id": "stalled_blocker",
        "severity": "blocking",
        "category": "fact",
        "summary": "The transition lacks a causal bridge.",
        "evidence": ["The original draft jumps directly to ambition."],
        "recommended_resolution": "Connect system failure directly to the need for control.",
    }
    prior_report: dict[str, object] = {"findings": [prior_finding]}

    assert _stagnant_continuity_finding_ids([dict(prior_finding)], prior_report) == (
        "stalled_blocker",
    )
    fresh_finding = {
        **prior_finding,
        "summary": "The attempted bridge remains abstract rather than causal.",
        "evidence": ["The revised draft names control but not the failed decision."],
    }
    assert _stagnant_continuity_finding_ids([fresh_finding], prior_report) == ()
    assert _stagnant_continuity_finding_ids([], prior_report) == ()


def test_stagnation_diagnostic_is_actionable_without_provider_content() -> None:
    private_response_content = "provider response body must remain private"
    response = ModelResponse(
        provider="fixture",
        model_identifier="fixture-model",
        deployment=ModelDeployment.LOCAL,
        content=private_response_content,
        thinking=None,
        finish_reason="stop",
        created_at=datetime.now(UTC),
        usage=ModelUsage(input_tokens=10, output_tokens=20),
        timing=ModelTiming(total_ms=30),
        estimated_cost_usd=Decimal("0"),
    )
    error = ContinuityRecheckStagnationError(
        "continuity re-check repeated blocking finding IDs without revised-draft "
        "analysis: ['stalled_blocker']"
    )

    diagnostic = _structured_failure_message(error, response)

    assert "ContinuityRecheckStagnationError" in diagnostic
    assert "stalled_blocker" in diagnostic
    assert private_response_content not in diagnostic


@pytest.mark.parametrize(
    ("mode", "expected_deployment", "expects_fallback"),
    (
        (ModelProfileMode.LOCAL, ModelDeployment.LOCAL, False),
        (ModelProfileMode.CLOUD, ModelDeployment.CLOUD, False),
        (ModelProfileMode.HYBRID, ModelDeployment.CLOUD, True),
    ),
)
def test_continuity_stagnation_escalates_only_hybrid_retry(
    mode: ModelProfileMode,
    expected_deployment: ModelDeployment,
    expects_fallback: bool,
) -> None:
    local = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    cloud = ModelSelection(
        provider="ollama",
        model_identifier="cloud-fixture",
        deployment=ModelDeployment.CLOUD,
    )
    configuration = MODEL_PRESETS[mode].configuration(
        local_model=local if mode is not ModelProfileMode.CLOUD else None,
        cloud_model=cloud if mode is not ModelProfileMode.LOCAL else None,
    )

    selection, fallback_history = _select_production_model(
        operation=_Operation.CONTINUITY,
        specialist_role="continuity_supervisor",
        configuration=configuration,
        attempt_number=2,
        previous_failure={
            "error_code": "continuity_recheck_stagnated",
            "message": "the local re-check repeated its prior judgment",
        },
    )

    assert selection.deployment is expected_deployment
    assert bool(fallback_history) is expects_fallback
    if expects_fallback:
        assert fallback_history == (
            {
                "reason": "continuity_recheck_stagnated",
                "attempt_number": 2,
                "from_provider": "ollama",
                "from_model_identifier": "local-fixture",
                "from_deployment": "local",
                "to_provider": "ollama",
                "to_model_identifier": "cloud-fixture",
                "to_deployment": "cloud",
            },
        )


def test_hybrid_does_not_escalate_unrelated_continuity_validation_failure() -> None:
    local = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    cloud = ModelSelection(
        provider="ollama",
        model_identifier="cloud-fixture",
        deployment=ModelDeployment.CLOUD,
    )
    configuration = MODEL_PRESETS[ModelProfileMode.HYBRID].configuration(
        local_model=local,
        cloud_model=cloud,
    )

    selection, fallback_history = _select_production_model(
        operation=_Operation.CONTINUITY,
        specialist_role="continuity_supervisor",
        configuration=configuration,
        attempt_number=2,
        previous_failure={
            "error_code": "schema_validation_failed",
            "message": "a required field was missing",
        },
    )

    assert selection is local
    assert fallback_history == ()


@pytest.mark.anyio
async def test_hybrid_continuity_stagnation_retry_uses_cloud_and_records_fallback(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    prompt = corpus.prompts[0]
    local = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    cloud = ModelSelection(
        provider="ollama",
        model_identifier="cloud-fixture",
        deployment=ModelDeployment.CLOUD,
    )
    session_factory = create_session_factory(database_engine)
    profile_id = BUILTIN_PROFILE_IDS[ModelProfileMode.HYBRID]
    profile = ModelProfileStore(session_factory).configure_profile(
        profile_id,
        local_model=local,
        cloud_model=cloud,
    )
    case = BenchmarkCase(
        case_id=UUID("acacacac-acac-4aca-8aca-acacacacacac"),
        prompt_id=prompt.prompt_id,
        prompt_version=prompt.version,
        system=BenchmarkSystem.AGENTIC,
        run_seed=prompt.random_seed,
        profile=BenchmarkProfileSnapshot.from_configuration(
            profile_id=profile.id,
            configuration=profile.configuration,
        ),
    )
    gateway = HybridStagnationEscalationGateway(prompt.prompt, prompt)
    blueprint_service = AgenticBenchmarkBlueprintService(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    prepared = await blueprint_service.prepare(case, prompt)
    assert prepared.interrupt_id is not None
    decision = BlueprintHumanDecision(
        id=uuid4(),
        interrupt_id=prepared.interrupt_id,
        action=BlueprintDecisionAction.APPROVE,
    )
    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        BenchmarkBlueprintNodeExecutor(
            session_factory=session_factory,
            gateway=gateway,
        ),
    ) as workflow:
        approved = await workflow.resume(prepared.workflow_run_id, decision)
    blueprint = next(
        reference
        for reference in approved.artifacts
        if reference.kind is ArtifactKind.STORY_BLUEPRINT
    )

    async with BenchmarkSceneProductionService(
        database_path=migrated_database_path,
        session_factory=session_factory,
        executor=BenchmarkProductionExecutor(
            session_factory=session_factory,
            gateway=gateway,
        ),
        cost_ceiling_usd=Decimal("5.00"),
    ) as production_service:
        execution = await production_service.execute(
            prepared.workflow_run_id,
            blueprint,
        )

    assert execution.status is RunStatus.SUCCEEDED
    assert len(gateway.escalated_retry_payloads) == 1
    retry_context = gateway.escalated_retry_payloads[0]["retry_context"]
    assert isinstance(retry_context, dict)
    assert retry_context["error_code"] == "continuity_recheck_stagnated"
    with session_factory() as session:
        production_run = session.get(WorkflowRun, execution.workflow_run_id)
        assert production_run is not None
        invocations = session.scalars(
            select(AgentInvocation)
            .where(
                AgentInvocation.workflow_run_id == production_run.id,
                AgentInvocation.specialist_role == "continuity_supervisor",
            )
            .order_by(AgentInvocation.started_at, AgentInvocation.id)
        ).all()
        failed = next(
            invocation
            for invocation in invocations
            if invocation.error_code == "continuity_recheck_stagnated"
        )
        escalated = next(invocation for invocation in invocations if invocation.fallback_history)
        assert failed.model_identifier == "local-fixture"
        assert failed.request_settings["deployment"] == "local"
        assert escalated.status is InvocationStatus.SUCCEEDED
        assert escalated.model_identifier == "cloud-fixture"
        assert escalated.request_settings["deployment"] == "cloud"
        assert escalated.request_settings["schema_enforced"] is False
        assert escalated.request_settings["fallback_applied"] is True
        assert escalated.retry_count == 1
        assert (
            escalated.request_settings["task_fingerprint"]
            == failed.request_settings["task_fingerprint"]
        )
        assert escalated.fallback_history == [
            {
                "reason": "continuity_recheck_stagnated",
                "attempt_number": 2,
                "from_provider": "ollama",
                "from_model_identifier": "local-fixture",
                "from_deployment": "local",
                "to_provider": "ollama",
                "to_model_identifier": "cloud-fixture",
                "to_deployment": "cloud",
            }
        ]


@pytest.mark.anyio
async def test_same_continuity_finding_inherits_resolution_across_recheck(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    prompt = corpus.prompts[0]
    selection = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    session_factory = create_session_factory(database_engine)
    profile_id = BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL]
    profile = ModelProfileStore(session_factory).configure_profile(
        profile_id,
        local_model=selection,
        cloud_model=None,
    )
    case = BenchmarkCase(
        case_id=UUID("abababab-abab-4aba-8aba-abababababab"),
        prompt_id=prompt.prompt_id,
        prompt_version=prompt.version,
        system=BenchmarkSystem.AGENTIC,
        run_seed=prompt.random_seed,
        profile=BenchmarkProfileSnapshot.from_configuration(
            profile_id=profile.id,
            configuration=profile.configuration,
        ),
    )
    gateway = ContinuityRevisionFeedbackGateway(prompt.prompt, prompt)
    blueprint_service = AgenticBenchmarkBlueprintService(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    prepared = await blueprint_service.prepare(case, prompt)
    assert prepared.interrupt_id is not None
    decision = BlueprintHumanDecision(
        id=uuid4(),
        interrupt_id=prepared.interrupt_id,
        action=BlueprintDecisionAction.APPROVE,
    )
    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        BenchmarkBlueprintNodeExecutor(
            session_factory=session_factory,
            gateway=gateway,
        ),
    ) as workflow:
        approved = await workflow.resume(prepared.workflow_run_id, decision)
    blueprint = next(
        reference
        for reference in approved.artifacts
        if reference.kind is ArtifactKind.STORY_BLUEPRINT
    )

    async with BenchmarkSceneProductionService(
        database_path=migrated_database_path,
        session_factory=session_factory,
        executor=BenchmarkProductionExecutor(
            session_factory=session_factory,
            gateway=gateway,
        ),
        cost_ceiling_usd=Decimal("5.00"),
    ) as production_service:
        execution = await production_service.execute(
            prepared.workflow_run_id,
            blueprint,
        )

    assert execution.status is RunStatus.SUCCEEDED
    assert len(gateway.writer_revision_prompts) == 2
    assert all(
        gateway.recommended_resolution in prompt for prompt in gateway.writer_revision_prompts
    )
    assert len(gateway.writer_revision_reports) == 2
    for report in gateway.writer_revision_reports:
        findings = report["findings"]
        assert isinstance(findings, list)
        assert findings[0]["recommended_resolution"] == gateway.recommended_resolution
    assert len(gateway.continuity_recheck_prompts) == 2
    assert all(
        gateway.recommended_resolution in prompt for prompt in gateway.continuity_recheck_prompts
    )
    assert gateway.continuity_recheck_reports == gateway.writer_revision_reports
    for recheck_contract in gateway.continuity_recheck_contracts:
        assert "previous_report_version_ids" in recheck_contract
        assert "audit every prior error or blocking finding" in str(
            recheck_contract["verification_contract"]
        )
        assert "contradictory guidance" in str(recheck_contract["verification_contract"])
    recheck_payload = json.loads(gateway.continuity_recheck_prompts[0])
    output_requirements = recheck_payload["output_requirements"]
    assert "story-wide completion gates" in output_requirements["requirement_scope"]
    assert "planned outcome or exit_state" in output_requirements["requirement_scope"]


@pytest.mark.parametrize(
    "invariant_message",
    (
        "unknown character-state character IDs: ['model_invented_character']",
        "unknown location-state location IDs: ['model_invented_location']",
    ),
)
def test_story_bible_invariant_diagnostic_is_actionable_without_provider_content(
    invariant_message: str,
) -> None:
    private_response_content = "provider response body must remain private"
    response = ModelResponse(
        provider="fixture",
        model_identifier="fixture-model",
        deployment=ModelDeployment.LOCAL,
        content=private_response_content,
        thinking=None,
        finish_reason="stop",
        created_at=datetime.now(UTC),
        usage=ModelUsage(input_tokens=10, output_tokens=20),
        timing=ModelTiming(total_ms=30),
        estimated_cost_usd=Decimal("0"),
    )

    diagnostic = _structured_failure_message(
        StoryBibleInvariantError(f"  {invariant_message}\n"),
        response,
    )

    assert f"$:StoryBibleInvariantError:{invariant_message}" in diagnostic
    assert private_response_content not in diagnostic


@pytest.mark.anyio
async def test_repeated_missing_continuity_resolution_fails_after_bounded_retry(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    prompt = corpus.prompts[0]
    selection = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    session_factory = create_session_factory(database_engine)
    profile_id = BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL]
    profile = ModelProfileStore(session_factory).configure_profile(
        profile_id,
        local_model=selection,
        cloud_model=None,
    )
    case = BenchmarkCase(
        case_id=UUID("eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"),
        prompt_id=prompt.prompt_id,
        prompt_version=prompt.version,
        system=BenchmarkSystem.AGENTIC,
        run_seed=prompt.random_seed,
        profile=BenchmarkProfileSnapshot.from_configuration(
            profile_id=profile.id,
            configuration=profile.configuration,
        ),
    )
    gateway = OneProductionRepairGateway(
        prompt.prompt,
        prompt,
        repeat_invalid=True,
    )
    blueprint_service = AgenticBenchmarkBlueprintService(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    prepared = await blueprint_service.prepare(case, prompt)
    assert prepared.interrupt_id is not None
    decision = BlueprintHumanDecision(
        id=uuid4(),
        interrupt_id=prepared.interrupt_id,
        action=BlueprintDecisionAction.APPROVE,
    )
    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        BenchmarkBlueprintNodeExecutor(
            session_factory=session_factory,
            gateway=gateway,
        ),
    ) as workflow:
        approved = await workflow.resume(prepared.workflow_run_id, decision)
    blueprint = next(
        reference
        for reference in approved.artifacts
        if reference.kind is ArtifactKind.STORY_BLUEPRINT
    )
    production_executor = BenchmarkProductionExecutor(
        session_factory=session_factory,
        gateway=gateway,
    )

    async with BenchmarkSceneProductionService(
        database_path=migrated_database_path,
        session_factory=session_factory,
        executor=production_executor,
        cost_ceiling_usd=Decimal("5.00"),
    ) as production_service:
        with pytest.raises(
            RetryableSceneProductionError,
            match="invalid structured output",
        ):
            await production_service.execute(prepared.workflow_run_id, blueprint)

    assert len(gateway.output_requirements) == 2
    assert all(
        "recommended_resolution" in str(requirements)
        for requirements in gateway.output_requirements
    )
    assert len(gateway.repair_contexts) == 1
    repair_context = gateway.repair_contexts[0]
    assert "requires a resolution" in str(repair_context["message"])
    assert "recommended_resolution" in str(repair_context["required_correction"])
    with session_factory() as session:
        production_run = session.scalar(
            select(WorkflowRun).where(
                WorkflowRun.parent_workflow_run_id == prepared.workflow_run_id
            )
        )
        assert production_run is not None
        assert production_run.status is RunStatus.FAILED
        assert production_run.current_node == "continuity"
        invocations = session.scalars(
            select(AgentInvocation)
            .where(
                AgentInvocation.workflow_run_id == production_run.id,
                AgentInvocation.specialist_role == "continuity_supervisor",
            )
            .order_by(AgentInvocation.started_at)
        ).all()
        assert len(invocations) == 2
        assert [invocation.status for invocation in invocations] == [
            InvocationStatus.FAILED,
            InvocationStatus.FAILED,
        ]
        assert [invocation.retry_count for invocation in invocations] == [0, 1]
        assert all(
            "requires a resolution" in (invocation.error_message or "")
            for invocation in invocations
        )


@pytest.mark.parametrize(
    ("invalid_kind", "expected_detail"),
    (
        (
            "character",
            "unknown character-state character IDs: ['model_invented_character']",
        ),
        (
            "location",
            "unknown location-state location IDs: ['model_invented_location']",
        ),
    ),
)
@pytest.mark.anyio
async def test_repeated_story_bible_invariant_failure_is_actionable_and_bounded(
    invalid_kind: str,
    expected_detail: str,
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    prompt = corpus.prompts[0]
    selection = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    session_factory = create_session_factory(database_engine)
    profile_id = BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL]
    profile = ModelProfileStore(session_factory).configure_profile(
        profile_id,
        local_model=selection,
        cloud_model=None,
    )
    case = BenchmarkCase(
        case_id=uuid4(),
        prompt_id=prompt.prompt_id,
        prompt_version=prompt.version,
        system=BenchmarkSystem.AGENTIC,
        run_seed=prompt.random_seed,
        profile=BenchmarkProfileSnapshot.from_configuration(
            profile_id=profile.id,
            configuration=profile.configuration,
        ),
    )
    gateway = RepeatedInvalidStoryBibleGateway(
        prompt.prompt,
        prompt,
        invalid_kind=invalid_kind,
    )
    blueprint_service = AgenticBenchmarkBlueprintService(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    prepared = await blueprint_service.prepare(case, prompt)
    assert prepared.interrupt_id is not None
    decision = BlueprintHumanDecision(
        id=uuid4(),
        interrupt_id=prepared.interrupt_id,
        action=BlueprintDecisionAction.APPROVE,
    )
    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        BenchmarkBlueprintNodeExecutor(
            session_factory=session_factory,
            gateway=gateway,
        ),
    ) as workflow:
        approved = await workflow.resume(prepared.workflow_run_id, decision)
    blueprint = next(
        reference
        for reference in approved.artifacts
        if reference.kind is ArtifactKind.STORY_BLUEPRINT
    )
    production_executor = BenchmarkProductionExecutor(
        session_factory=session_factory,
        gateway=gateway,
    )

    async with BenchmarkSceneProductionService(
        database_path=migrated_database_path,
        session_factory=session_factory,
        executor=production_executor,
        cost_ceiling_usd=Decimal("5.00"),
    ) as production_service:
        with pytest.raises(
            RetryableSceneProductionError,
            match="invalid structured output",
        ):
            await production_service.execute(prepared.workflow_run_id, blueprint)

    assert len(gateway.repair_contexts) == 1
    repair_message = str(gateway.repair_contexts[0]["message"])
    assert expected_detail in repair_message
    with session_factory() as session:
        production_run = session.scalar(
            select(WorkflowRun).where(
                WorkflowRun.parent_workflow_run_id == prepared.workflow_run_id
            )
        )
        assert production_run is not None
        assert production_run.status is RunStatus.FAILED
        invocations = session.scalars(
            select(AgentInvocation)
            .where(
                AgentInvocation.workflow_run_id == production_run.id,
                AgentInvocation.specialist_role == "story_bible_maintainer",
            )
            .order_by(AgentInvocation.started_at)
        ).all()
        assert len(invocations) == 2
        assert [invocation.status for invocation in invocations] == [
            InvocationStatus.FAILED,
            InvocationStatus.FAILED,
        ]
        assert [invocation.retry_count for invocation in invocations] == [0, 1]
        assert all(
            expected_detail in (invocation.error_message or "") for invocation in invocations
        )


@pytest.mark.anyio
async def test_approved_blueprint_runs_durable_production_and_replays(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    prompt = corpus.prompts[0]
    selection = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    session_factory = create_session_factory(database_engine)
    profile_id = BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL]
    profile = ModelProfileStore(session_factory).configure_profile(
        profile_id,
        local_model=selection,
        cloud_model=None,
    )
    case = BenchmarkCase(
        case_id=UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
        prompt_id=prompt.prompt_id,
        prompt_version=prompt.version,
        system=BenchmarkSystem.AGENTIC,
        run_seed=prompt.random_seed,
        profile=BenchmarkProfileSnapshot.from_configuration(
            profile_id=profile.id,
            configuration=profile.configuration,
        ),
    )
    gateway = OneProductionRepairGateway(prompt.prompt, prompt)
    blueprint_service = AgenticBenchmarkBlueprintService(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    prepared = await blueprint_service.prepare(case, prompt)
    assert prepared.interrupt_id is not None
    waiting_executor = AgenticBenchmarkCaseExecutor(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    with pytest.raises(
        BenchmarkCaseExecutionError,
        match="mandatory Story Blueprint approval",
    ):
        await waiting_executor.execute(case, prompt)
    assert len(gateway.requests) == 6
    decision = BlueprintHumanDecision(
        id=uuid4(),
        interrupt_id=prepared.interrupt_id,
        action=BlueprintDecisionAction.APPROVE,
    )
    async with BlueprintWorkflowService(
        migrated_database_path,
        session_factory,
        BenchmarkBlueprintNodeExecutor(
            session_factory=session_factory,
            gateway=gateway,
        ),
    ) as workflow:
        approved = await workflow.resume(prepared.workflow_run_id, decision)
    blueprint = next(
        reference
        for reference in approved.artifacts
        if reference.kind is ArtifactKind.STORY_BLUEPRINT
    )
    production_executor = BenchmarkProductionExecutor(
        session_factory=session_factory,
        gateway=gateway,
    )
    async with BenchmarkSceneProductionService(
        database_path=migrated_database_path,
        session_factory=session_factory,
        executor=production_executor,
        cost_ceiling_usd=Decimal("5.00"),
    ) as production_service:
        execution = await production_service.execute(
            prepared.workflow_run_id,
            blueprint,
        )
        request_count = len(gateway.requests)
        replay = await production_service.execute(
            prepared.workflow_run_id,
            blueprint,
        )

    assert execution == replay
    assert execution.status is RunStatus.SUCCEEDED
    assert execution.result is not None
    assert len(execution.result.accepted_units) == 3
    assert len(gateway.requests) == request_count == 19
    assert len(gateway.output_requirements) == 4
    assert all(
        "recommended_resolution" in str(requirements)
        for requirements in gateway.output_requirements
    )
    assert len(gateway.repair_contexts) == 1
    assert "Structured output validation failed" in str(gateway.repair_contexts[0]["message"])
    assert "recommended_resolution" in str(gateway.repair_contexts[0]["required_correction"])
    production_requests = [
        request
        for request in gateway.requests
        if request.invocation.specialist_role
        in {
            "scene_writer",
            "scene_critic",
            "continuity_supervisor",
            "story_bible_maintainer",
        }
    ]
    assert all(request.invocation.prompt_template_version == "7" for request in production_requests)
    assert all(request.response_schema is not None for request in gateway.requests)
    with session_factory() as session:
        production_run = session.get(WorkflowRun, execution.workflow_run_id)
        assert production_run is not None
        assert production_run.parent_workflow_run_id == prepared.workflow_run_id
        assert production_run.status is RunStatus.SUCCEEDED
        assert production_run.checkpoint_id == execution.checkpoint_id
        assert production_run.budget["max_cost_usd"] == "5.00"
        assert session.scalar(select(func.count()).select_from(AgentInvocation)) == 19
        production_invocations = session.scalars(
            select(AgentInvocation).where(
                AgentInvocation.workflow_run_id == execution.workflow_run_id
            )
        ).all()
        assert len(production_invocations) == 13
        assert all(invocation.input_versions for invocation in production_invocations)
        assert sum(invocation.retry_count == 1 for invocation in production_invocations) == 1

    case_executor = AgenticBenchmarkCaseExecutor(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    output = await case_executor.execute(case, prompt)
    output_replay = await case_executor.execute(case, prompt)

    assert output == output_replay
    assert output.workflow_run_id == execution.workflow_run_id
    assert len(output.invocation_ids) == 19
    assert len(output.artifact_version_ids) == 6
    assert output.content.count("\n\n") == 2
    assert len(gateway.requests) == request_count


@pytest.mark.anyio
async def test_operator_runs_agentic_case_only_after_explicit_approval(
    migrated_database_path: Path,
    database_engine: Engine,
    tmp_path: Path,
) -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    local = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    cloud = ModelSelection(
        provider="ollama",
        model_identifier="cloud-fixture",
        deployment=ModelDeployment.CLOUD,
    )
    full_plan = build_benchmark_plan(
        campaign_id=CAMPAIGN_ID,
        corpus=corpus,
        baseline_model=cloud,
        profiles={
            ModelProfileMode.LOCAL: BenchmarkProfileSnapshot.from_configuration(
                profile_id=BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL],
                configuration=MODEL_PRESETS[ModelProfileMode.LOCAL].configuration(
                    local_model=local
                ),
            ),
            ModelProfileMode.CLOUD: BenchmarkProfileSnapshot.from_configuration(
                profile_id=BUILTIN_PROFILE_IDS[ModelProfileMode.CLOUD],
                configuration=MODEL_PRESETS[ModelProfileMode.CLOUD].configuration(
                    cloud_model=cloud
                ),
            ),
            ModelProfileMode.HYBRID: BenchmarkProfileSnapshot.from_configuration(
                profile_id=BUILTIN_PROFILE_IDS[ModelProfileMode.HYBRID],
                configuration=MODEL_PRESETS[ModelProfileMode.HYBRID].configuration(
                    local_model=local,
                    cloud_model=cloud,
                ),
            ),
        },
        workflow_versions={
            "story_blueprint": STORY_BLUEPRINT_GRAPH_VERSION,
            "scene_production": SCENE_PRODUCTION_GRAPH_VERSION,
        },
    )
    local_case = next(case for case in full_plan.cases if case.target_key == "local")
    plan = BenchmarkPlan(
        schema_version=full_plan.schema_version,
        campaign_id=full_plan.campaign_id,
        corpus_id=full_plan.corpus_id,
        corpus_version=full_plan.corpus_version,
        corpus_sha256=full_plan.corpus_sha256,
        workflow_versions=full_plan.workflow_versions,
        cases=(local_case,),
    )
    session_factory = create_session_factory(database_engine)
    ModelProfileStore(session_factory).configure_profile(
        BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL],
        local_model=local,
        cloud_model=None,
    )
    gateway = ProductionFixtureGateway(corpus.prompts[0].prompt, corpus.prompts[0])
    report_path = tmp_path / "campaign" / "report.json"

    prepared = await prepare_agentic_cases(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
        target_keys=frozenset({"local"}),
    )

    assert len(prepared) == 1
    assert prepared[0].awaiting_approval is True
    assert len(gateway.requests) == 6
    with pytest.raises(ValueError, match="explicit Blueprint approval"):
        await run_agentic_cases(
            plan=plan,
            corpus=corpus,
            database_path=migrated_database_path,
            session_factory=session_factory,
            gateway=gateway,
            prior_report=None,
            checkpoint=AtomicJsonReportCheckpoint(report_path, plan),
            target_keys=frozenset({"local"}),
        )
    assert not report_path.exists()

    packet = await build_blueprint_review_packet(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        target_keys=frozenset({"local"}),
    )
    form = render_blueprint_review_csv(packet, reviewer_id="human-reviewer")
    with pytest.raises(ValueError, match="must contain 'yes'"):
        parse_blueprint_review_csv(packet, form)
    approvals = parse_blueprint_review_csv(packet, form.replace(",,\n", ",yes,\n"))
    guide = render_blueprint_review_guide(packet, reviewer_id="human-reviewer")
    approved = await approve_reviewed_agentic_cases(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        packet=packet,
        approvals=approvals,
        target_keys=frozenset({"local"}),
    )
    approval_replay = await approve_reviewed_agentic_cases(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        packet=packet,
        approvals=approvals,
        target_keys=frozenset({"local"}),
    )
    report = await run_agentic_cases(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
        prior_report=None,
        checkpoint=AtomicJsonReportCheckpoint(report_path, plan),
        target_keys=frozenset({"local"}),
    )
    request_count = len(gateway.requests)
    replay = await run_agentic_cases(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
        prior_report=report,
        checkpoint=AtomicJsonReportCheckpoint(report_path, plan),
        target_keys=frozenset({"local"}),
    )

    assert approved[0].awaiting_approval is False
    assert approval_replay == approved
    assert packet.content_sha256 in guide
    assert local_case.prompt_id in guide
    assert len(report.results) == 1
    assert report.results[0].output is not None
    assert replay == report
    assert len(gateway.requests) == request_count == 18


@pytest.mark.anyio
async def test_operator_isolates_failed_blueprint_and_runs_approved_sibling(
    migrated_database_path: Path,
    database_engine: Engine,
    tmp_path: Path,
) -> None:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    local = ModelSelection(
        provider="ollama",
        model_identifier="local-fixture",
        deployment=ModelDeployment.LOCAL,
    )
    cloud = ModelSelection(
        provider="ollama",
        model_identifier="cloud-fixture",
        deployment=ModelDeployment.CLOUD,
    )
    snapshots = {
        mode: BenchmarkProfileSnapshot.from_configuration(
            profile_id=BUILTIN_PROFILE_IDS[mode],
            configuration=MODEL_PRESETS[mode].configuration(
                local_model=local if mode is not ModelProfileMode.CLOUD else None,
                cloud_model=cloud if mode is not ModelProfileMode.LOCAL else None,
            ),
        )
        for mode in ModelProfileMode
    }
    full_plan = build_benchmark_plan(
        campaign_id=CAMPAIGN_ID,
        corpus=corpus,
        baseline_model=cloud,
        profiles=snapshots,
        workflow_versions={
            "story_blueprint": STORY_BLUEPRINT_GRAPH_VERSION,
            "scene_production": SCENE_PRODUCTION_GRAPH_VERSION,
        },
    )
    local_cases = tuple(case for case in full_plan.cases if case.target_key == "local")[:2]
    plan = full_plan.model_copy(update={"cases": local_cases})
    session_factory = create_session_factory(database_engine)
    ModelProfileStore(session_factory).configure_profile(
        BUILTIN_PROFILE_IDS[ModelProfileMode.LOCAL],
        local_model=local,
        cloud_model=None,
    )
    gateway = FirstBlueprintFailureGateway(corpus.prompts[0].prompt, corpus.prompts[0])

    prepared = await prepare_agentic_cases(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
        target_keys=frozenset({"local"}),
    )

    assert [item.case_id for item in prepared] == [local_cases[1].case_id]
    request_count = len(gateway.requests)
    replayed_preparation = await prepare_agentic_cases(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
        target_keys=frozenset({"local"}),
    )
    assert replayed_preparation == prepared
    assert len(gateway.requests) == request_count
    await approve_agentic_cases(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
        case_ids=(local_cases[1].case_id,),
        target_keys=frozenset({"local"}),
    )
    report = await run_agentic_cases(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
        prior_report=None,
        checkpoint=AtomicJsonReportCheckpoint(tmp_path / "report.json", plan),
        target_keys=frozenset({"local"}),
    )

    assert [result.status for result in report.results] == [
        BenchmarkCaseStatus.FAILED,
        BenchmarkCaseStatus.SUCCEEDED,
    ]
    assert report.results[0].error_code == "artifact_contract_failed"
    assert report.results[1].output is not None
