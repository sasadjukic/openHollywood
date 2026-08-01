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
    prepare_agentic_cases,
    run_agentic_cases,
)
from open_hollywood_api.services.model_profiles import (
    BUILTIN_PROFILE_IDS,
    ModelProfileStore,
)
from open_hollywood_api.services.production_model_executor import (
    BenchmarkProductionExecutor,
)
from open_hollywood_api.services.production_workflow import (
    BenchmarkSceneProductionService,
)
from open_hollywood_engine.artifacts import (
    ArtifactKind,
    ContinuityCategory,
    ContinuityReport,
    Critique,
    CritiqueVerdict,
    RubricScore,
    SceneDraft,
    StoryBible,
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
)
from sqlalchemy import Engine, func, select

from scripts.evaluation_harness import AtomicJsonReportCheckpoint
from tests.evaluations.test_agentic_blueprint import (
    CAMPAIGN_ID,
    CORPUS_PATH,
    BlueprintFixtureGateway,
)


class ProductionFixtureGateway(BlueprintFixtureGateway):
    """Add coherent production-role responses to the Blueprint fixture."""

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
        return ModelResponse(
            provider=self.provider,
            model_identifier=request.model_identifier,
            deployment=ModelDeployment.LOCAL,
            content=value.model_dump_json(),
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
    gateway = ProductionFixtureGateway(prompt.prompt, prompt)
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
    assert len(gateway.requests) == request_count == 18
    assert all(request.response_schema is not None for request in gateway.requests)
    with session_factory() as session:
        production_run = session.get(WorkflowRun, execution.workflow_run_id)
        assert production_run is not None
        assert production_run.parent_workflow_run_id == prepared.workflow_run_id
        assert production_run.status is RunStatus.SUCCEEDED
        assert production_run.checkpoint_id == execution.checkpoint_id
        assert session.scalar(select(func.count()).select_from(AgentInvocation)) == 18
        production_invocations = session.scalars(
            select(AgentInvocation).where(
                AgentInvocation.workflow_run_id == execution.workflow_run_id
            )
        ).all()
        assert len(production_invocations) == 12
        assert all(invocation.input_versions for invocation in production_invocations)

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
    assert len(output.invocation_ids) == 18
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

    approved = await approve_agentic_cases(
        plan=plan,
        corpus=corpus,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
        case_ids=(local_case.case_id,),
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
