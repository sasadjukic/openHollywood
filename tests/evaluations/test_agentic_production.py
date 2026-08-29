"""Approved Blueprint to durable agentic scene-production integration tests."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    ArtifactVersion,
    InvocationStatus,
    RunStatus,
    WorkflowRun,
)
from open_hollywood_api.services.agentic_benchmark import (
    AgenticBenchmarkBlueprintService,
    AgenticBenchmarkCaseExecutor,
    _preferred_production_failure_detail,
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
    _benchmark_constraint_applicability,
    _continuity_model_context,
    _continuity_prompt_inputs,
    _continuity_recheck_observations,
    _continuity_requirement_catalogs,
    _ContinuityModelContext,
    _ContinuitySchemaVariant,
    _Execution,
    _invalid_continuity_recheck_finding_ids,
    _local_schema_repair_guidance,
    _materialize_continuity_evidence,
    _materialize_continuity_finding,
    _materialize_continuity_identity,
    _materialize_requirement_audit,
    _Operation,
    _output_schema,
    _scene_plan_requirement_applicability,
    _select_production_model,
    _structured_failure_message,
    _validate_continuity_finding_contract,
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
    HardGate,
    WordCountStatus,
    build_benchmark_plan,
    canonical_sha256,
    load_benchmark_corpus,
    parse_blueprint_review_csv,
    render_blueprint_review_csv,
    render_blueprint_review_guide,
)
from open_hollywood_engine.models import (
    MODEL_PRESETS,
    ModelCallBudget,
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
    SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
    STORY_BLUEPRINT_GRAPH_VERSION,
    BlueprintDecisionAction,
    BlueprintHumanDecision,
    RetryableSceneProductionError,
)
from sqlalchemy import Engine, func, select, update

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
        input_items = payload.get("input_artifacts", [])
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
            draft = payload["candidate_draft"]
            invented_lineage = UUID("20240730-a1b2-43d4-a5f6-7890abcdef00")
            value = ContinuityReport(
                story_bible_version_id=invented_lineage,
                scene_version_id=draft["artifact_version_id"],
                scene_plan_version_id=invented_lineage,
                scene_id=assignment["unit_id"],
                scene_number=assignment["unit_number"],
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
            content["overall_score"] = 999
        elif role == "continuity_supervisor":
            content.update(
                story_bible_version_id=invented_version_id,
                scene_version_id=invented_version_id,
                scene_plan_version_id=invented_version_id,
                scene_id="model_invented_scene",
                scene_number=999,
            )
            content["requirement_coverage"] = {
                entry["id"]: {
                    "status": "covered",
                    "coverage_assessment": "The candidate performs this exact obligation.",
                }
                for entry in payload["requirement_coverage_catalog"]
            }
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


def _v13_contradiction_inputs(payload: dict[str, object]) -> tuple[str, str]:
    draft = payload["candidate_draft"]
    assert isinstance(draft, dict)
    content = draft["content"]
    assert isinstance(content, dict)
    evidence_catalog = content["evidence_catalog"]
    assert isinstance(evidence_catalog, list)
    evidence = next(item for item in evidence_catalog if isinstance(item, dict))
    catalog = payload["canonical_source_catalog"]
    assert isinstance(catalog, list)
    source = next(item for item in catalog if isinstance(item, dict))
    return evidence["evidence_ref"], source["reference_id"]


def _schema_test_continuity_context(*, recheck: bool = False) -> _ContinuityModelContext:
    return _ContinuityModelContext(
        candidate_draft={
            "artifact_key": "scene_draft_scene_1",
            "artifact_kind": ArtifactKind.SCENE_DRAFT.value,
            "artifact_version_id": str(uuid4()),
            "content": {
                "scene_id": "scene_1",
                "revision_number": 1 if recheck else 0,
                "evidence_catalog": [
                    {
                        "evidence_ref": "draft_evidence_0001",
                        "exact_excerpt": "Mara pockets the brass key.",
                    }
                ],
            },
        },
        accepted_prior_drafts=(),
        previous_continuity_report=(
            {
                "artifact_key": "continuity_scene_1",
                "artifact_kind": ArtifactKind.CONTINUITY_REPORT.value,
                "artifact_version_id": str(uuid4()),
                "content": {"findings": []},
            }
            if recheck
            else None
        ),
        canonical_source_catalog=(
            {
                "reference_id": "canonical_source_0001",
                "artifact_kind": ArtifactKind.SCENE_PLAN.value,
                "artifact_key": "scene_plan_scene_1",
                "artifact_version_id": str(uuid4()),
                "source_path": "content.outcome",
                "claim": "Mara returns the brass key.",
            },
        ),
        requirement_catalog=(
            {
                "id": "required_element_1",
                "kind": "required_element",
                "category": "constraint",
                "text": "Mara returns the brass key.",
            },
        ),
        forbidden_shortcut_catalog=(
            {
                "id": "forbidden_shortcut_1",
                "kind": "forbidden_shortcut",
                "text": "The key vanishes by magic.",
            },
        ),
        requirement_kinds={
            "required_element_1": "required_element",
            "forbidden_shortcut_1": "forbidden_shortcut",
        },
        requirement_categories={"required_element_1": "constraint"},
        world_rule_ids=("world_rule_1",),
    )


def _v17_catalog_test_execution(
    *,
    required_elements: list[str] | None = None,
    forbidden_shortcuts: list[str] | None = None,
    scene_plan: dict[str, object] | None = None,
) -> _Execution:
    plan = {
        "id": "scene_1",
        "required_elements": required_elements or [],
        **(scene_plan or {}),
    }
    return _Execution(
        workflow_run_id=uuid4(),
        project_id=uuid4(),
        profile_id=uuid4(),
        configuration_sha256="a" * 64,
        selection=ModelSelection(
            provider="ollama",
            model_identifier="local-fixture",
            deployment=ModelDeployment.LOCAL,
        ),
        specialist_role="continuity_supervisor",
        input_version_ids=(),
        inputs=(
            {
                "artifact_kind": ArtifactKind.SCENE_PLAN.value,
                "artifact_key": "scene_1_plan",
                "artifact_version_id": str(uuid4()),
                "content": plan,
            },
            {
                "artifact_kind": ArtifactKind.SCENE_DRAFT.value,
                "artifact_key": "scene_1_draft",
                "artifact_version_id": str(uuid4()),
                "content": {
                    "scene_id": "scene_1",
                    "scene_number": 1,
                    "revision_number": 0,
                    "prose": "Mara pockets the brass key.",
                },
            },
            {
                "artifact_kind": ArtifactKind.STORY_BIBLE.value,
                "artifact_key": "story_bible",
                "artifact_version_id": str(uuid4()),
                "content": {"prohibited_contradictions": []},
            },
        ),
        constraints={
            "required_elements": required_elements or [],
            "forbidden_shortcuts": forbidden_shortcuts or [],
        },
        call_budget=ModelCallBudget(max_input_tokens=20_000, max_output_tokens=2_000),
        seed=1,
        task_fingerprint="fingerprint",
        unit_id="scene_1",
        unit_number=1,
        unit_count=1,
        revision_number=0,
        attempt_number=1,
        previous_failure=None,
        fallback_history=(),
    )


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
        self.constraint_applicabilities: list[dict[str, object]] = []
        self.repair_contexts: list[dict[str, object]] = []
        self.local_schema_repairs: list[dict[str, object]] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        if request.invocation.specialist_role != "continuity_supervisor":
            return await super().generate(request)
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        output_requirements = payload.get("output_requirements")
        if isinstance(output_requirements, dict):
            self.output_requirements.append(output_requirements)
        required_catalog = payload.get("requirement_coverage_catalog")
        forbidden_catalog = payload.get("forbidden_shortcut_catalog")
        assignment = payload.get("assignment")
        if (
            isinstance(required_catalog, list)
            and isinstance(forbidden_catalog, list)
            and isinstance(assignment, dict)
        ):
            self.constraint_applicabilities.append(
                {
                    "is_final_scene": assignment["unit_number"] == assignment["unit_count"],
                    "due_now": [*required_catalog, *forbidden_catalog],
                }
            )
        retry_context = payload.get("retry_context")
        if isinstance(retry_context, dict):
            self.repair_contexts.append(retry_context)
        local_schema_repair = payload.get("local_schema_repair")
        if isinstance(local_schema_repair, dict):
            self.local_schema_repairs.append(local_schema_repair)
        if not self.invalid_sent or self.repeat_invalid:
            self.invalid_sent = True
            content = json.loads(response.content)
            evidence_ref, source_ref = _v13_contradiction_inputs(payload)
            content["findings"] = [
                {
                    "severity": "error",
                    "summary": "The candidate conflicts with an established fact.",
                    "basis_details": {
                        "basis": "contradiction",
                        "draft_evidence_refs": [evidence_ref],
                        "canonical_source_refs": [source_ref],
                        "category_details": {"category": "fact"},
                    },
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
            evidence_ref, source_ref = _v13_contradiction_inputs(payload)
            if revision_number > 0:
                previous_report = payload.get("previous_continuity_report")
                assert isinstance(previous_report, dict)
                reports = [previous_report["content"]]
                recheck = payload.get("continuity_recheck")
                assert isinstance(recheck, dict)
                self.continuity_recheck_prompts.append(prompt)
                self.continuity_recheck_reports.extend(reports)
                self.continuity_recheck_contracts.append(recheck)
                evidence_refs = [evidence_ref]
            else:
                evidence_refs = [evidence_ref]

        response = await super().generate(request)
        if role != "continuity_supervisor":
            return response

        if not self.blocking_report_sent:
            self.blocking_report_sent = True
            return self._blocking_response(
                response,
                resolution=self.recommended_resolution,
                is_recheck=False,
                source_ref=source_ref,
                evidence_refs=evidence_refs,
            )
        if revision_number == 1 and not self.missing_resolution_recheck_sent:
            self.missing_resolution_recheck_sent = True
            return self._blocking_response(
                response,
                resolution=None,
                is_recheck=True,
                summary="Mara still holds the brass key after crossing the east door.",
                evidence_refs=evidence_refs,
                source_ref=source_ref,
            )
        return response

    def _blocking_response(
        self,
        response: ModelResponse,
        *,
        resolution: str | None,
        is_recheck: bool,
        source_ref: str,
        summary: str = "Mara changes doors without returning the established key.",
        evidence_refs: list[str] | None = None,
    ) -> ModelResponse:
        content = json.loads(response.content)
        selected_evidence_refs = evidence_refs or ["draft_evidence_0001"]
        finding: dict[str, object] = {
            "severity": "blocking",
            "summary": summary,
            "basis_details": {
                "basis": "contradiction",
                "canonical_source_refs": [source_ref],
                "category_details": {"category": "fact"},
            },
            "related_scene_ids": ["model_invented_scene"],
            "recommended_resolution": resolution,
            "blocks_approval": False,
        }
        if is_recheck:
            cast(dict[str, object], finding["basis_details"]).update(
                revised_draft_evidence_refs=selected_evidence_refs,
            )
            finding.update(
                prior_finding_id="continuity_finding_001",
                repair_assessment=("The revision leaves the conflicting key action in place."),
            )
        else:
            cast(dict[str, object], finding["basis_details"])["draft_evidence_refs"] = (
                selected_evidence_refs
            )
        content["findings"] = [finding]
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
            return self._blocking_response(response, payload)
        if revision_number == 1 and request.model_identifier == "local-fixture":
            return self._blocking_response(response, payload)
        if revision_number == 1 and request.model_identifier == "cloud-fixture":
            self.escalated_retry_payloads.append(payload)
        return response

    def _blocking_response(
        self,
        response: ModelResponse,
        payload: dict[str, object],
    ) -> ModelResponse:
        content = json.loads(response.content)
        evidence_ref, source_ref = _v13_contradiction_inputs(payload)
        finding: dict[str, object] = {
            "severity": "blocking",
            "summary": "Mara changes doors without returning the established key.",
            "basis_details": {
                "basis": "contradiction",
                "canonical_source_refs": [source_ref],
                "category_details": {"category": "fact"},
            },
            "related_scene_ids": ["model_invented_scene"],
            "recommended_resolution": self.recommended_resolution,
            "blocks_approval": False,
        }
        if payload.get("output_schema_variant") == "recheck":
            cast(dict[str, object], finding["basis_details"]).update(
                revised_draft_evidence_refs=[evidence_ref],
            )
            finding.update(
                prior_finding_id="continuity_finding_001",
                repair_assessment="The conflict remains unresolved.",
            )
        else:
            cast(dict[str, object], finding["basis_details"])["draft_evidence_refs"] = [
                evidence_ref
            ]
        content["findings"] = [finding]
        return replace(response, content=json.dumps(content))


class RepeatedInvalidStoryBibleGateway(ProductionFixtureGateway):
    """Repeat an unknown canonical ID after receiving actionable repair context."""

    def __init__(self, prompt_text: str, prompt: Any, *, invalid_kind: str) -> None:
        super().__init__(prompt_text, prompt)
        self.invalid_kind = invalid_kind
        self.repair_contexts: list[dict[str, object]] = []
        self.local_schema_repairs: list[dict[str, object]] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        if request.invocation.specialist_role != "story_bible_maintainer":
            return response
        payload = json.loads(request.messages[-1].content)
        retry_context = payload.get("retry_context")
        if isinstance(retry_context, dict):
            self.repair_contexts.append(retry_context)
        local_schema_repair = payload.get("local_schema_repair")
        if isinstance(local_schema_repair, dict):
            self.local_schema_repairs.append(local_schema_repair)
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

    advisory = _materialize_continuity_finding(
        {
            "severity": "warning",
            "blocks_approval": True,
            "related_scene_ids": [],
        },
        "scene_1",
    )
    assert isinstance(advisory, dict)
    assert "blocks_approval" not in advisory


def test_v13_evidence_handles_materialize_exact_candidate_excerpts() -> None:
    context = _schema_test_continuity_context()
    finding = _materialize_continuity_evidence(
        {
            "severity": "blocking",
            "basis": "contradiction",
            "draft_evidence_refs": ["draft_evidence_0001"],
        },
        context,
    )

    assert isinstance(finding, dict)
    assert finding["evidence"] == ["Mara pockets the brass key."]
    assert "draft_evidence_refs" not in finding

    recheck = _materialize_continuity_evidence(
        {
            "severity": "blocking",
            "basis": "forbidden_shortcut_violation",
            "revised_draft_evidence_refs": ["draft_evidence_0001"],
        },
        _schema_test_continuity_context(recheck=True),
    )
    assert isinstance(recheck, dict)
    assert recheck["evidence"] == ["Mara pockets the brass key."]
    assert recheck["revised_evidence"] == ["Mara pockets the brass key."]
    assert "revised_draft_evidence_refs" not in recheck


def test_v13_unknown_evidence_handle_fails_with_catalog_guidance() -> None:
    with pytest.raises(ValueError, match="candidate_draft.content.evidence_catalog"):
        _materialize_continuity_evidence(
            {
                "severity": "blocking",
                "basis": "contradiction",
                "draft_evidence_refs": ["invented_evidence"],
            },
            _schema_test_continuity_context(),
        )


def test_v17_keyed_requirement_coverage_materializes_stable_missing_finding() -> None:
    context = _schema_test_continuity_context()
    findings = _materialize_requirement_audit(
        {
            "requirement_coverage": {
                "required_element_1": {
                    "status": "missing",
                    "severity": "blocking",
                    "summary": "The brass key obligation is absent.",
                    "coverage_assessment": "No draft passage performs the required key action.",
                    "recommended_resolution": "Add the required brass key action.",
                }
            },
        },
        context,
    )

    assert findings == [
        {
            "requirement_id": "required_element_1",
            "severity": "blocking",
            "summary": "The brass key obligation is absent.",
            "coverage_assessment": "No draft passage performs the required key action.",
            "recommended_resolution": "Add the required brass key action.",
            "id": "missing_required_element_1",
            "category": "constraint",
            "basis": "missing_requirement",
            "evidence": [],
            "canonical_source_refs": [],
            "world_rule_ids": [],
            "related_character_ids": [],
            "related_location_ids": [],
            "related_beat_ids": [],
            "related_scene_ids": [],
        }
    ]
    with pytest.raises(ValueError, match="include every exact due requirement key"):
        _materialize_requirement_audit(
            {
                "requirement_coverage": {},
            },
            context,
        )


def test_v17_unified_catalog_deduplicates_final_scene_requirement_text() -> None:
    execution = _v17_catalog_test_execution(
        required_elements=["Mara returns the brass key."],
        forbidden_shortcuts=["The key vanishes by magic."],
    )

    required, forbidden = _continuity_requirement_catalogs(execution)

    assert [entry["id"] for entry in required] == ["required_element_1"]
    assert required[0]["source_fields"] == [
        "benchmark.required_elements",
        "scene_plan.required_elements",
    ]
    assert [entry["id"] for entry in forbidden] == ["forbidden_shortcut_1"]


def test_v17_scene_plan_scalar_missing_requirement_is_contract_valid() -> None:
    execution = _v17_catalog_test_execution(scene_plan={"outcome": "Mara returns the brass key."})
    context = _continuity_model_context(execution)
    findings = _materialize_requirement_audit(
        {
            "requirement_coverage": {
                "scene_plan_outcome": {
                    "status": "missing",
                    "severity": "blocking",
                    "summary": "The planned outcome is absent.",
                    "coverage_assessment": "The draft never returns the key.",
                    "recommended_resolution": "Have Mara return the brass key.",
                }
            }
        },
        context,
    )

    _validate_continuity_finding_contract(cast(list[object], findings), execution)
    assert findings[0]["requirement_id"] == "scene_plan_outcome"
    assert findings[0]["category"] == "fact"


def test_v17_recheck_identity_and_disposition_are_application_owned() -> None:
    prior_id = "prior_fact_blocker"
    context = replace(
        _schema_test_continuity_context(recheck=True),
        previous_continuity_report={
            "artifact_key": "continuity_scene_1",
            "artifact_kind": ArtifactKind.CONTINUITY_REPORT.value,
            "artifact_version_id": str(uuid4()),
            "content": {
                "findings": [
                    {
                        "id": prior_id,
                        "severity": "blocking",
                        "basis": "contradiction",
                    }
                ]
            },
        },
    )

    unresolved = _materialize_continuity_identity(
        {
            "id": "model_invented_id",
            "severity": "blocking",
            "prior_finding_id": prior_id,
            "repair_assessment": "The contradiction remains.",
        },
        context,
        index=0,
    )
    newly_exposed = _materialize_continuity_identity(
        {
            "severity": "blocking",
            "repair_assessment": "This blocker is newly exposed.",
        },
        context,
        index=1,
    )

    assert isinstance(unresolved, dict)
    assert isinstance(newly_exposed, dict)
    assert unresolved["id"] == prior_id
    assert unresolved["recheck_disposition"] == "still_blocking"
    assert "prior_finding_id" not in unresolved
    assert newly_exposed["id"] == "continuity_new_002"
    assert newly_exposed["recheck_disposition"] == "newly_exposed"


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


def test_continuity_recheck_requires_structured_analysis_not_rewording() -> None:
    prior_finding = {
        "id": "stalled_blocker",
        "severity": "blocking",
        "category": "fact",
        "summary": "The transition lacks a causal bridge.",
        "evidence": ["The original draft jumps directly to ambition."],
        "recommended_resolution": "Connect system failure directly to the need for control.",
    }
    prior_report: dict[str, object] = {"findings": [prior_finding]}

    assert _invalid_continuity_recheck_finding_ids([dict(prior_finding)], prior_report) == (
        "stalled_blocker",
    )
    assessed_finding = {
        **prior_finding,
        "recheck_disposition": "still_blocking",
        "repair_assessment": "The writer left the quoted transition unchanged.",
        "revised_evidence": ["The original draft jumps directly to ambition."],
    }
    assert _invalid_continuity_recheck_finding_ids([assessed_finding], prior_report) == ()
    assert _invalid_continuity_recheck_finding_ids([], prior_report) == ()


def test_initial_continuity_evidence_is_bound_to_the_current_draft() -> None:
    execution = _Execution(
        workflow_run_id=uuid4(),
        project_id=uuid4(),
        profile_id=uuid4(),
        configuration_sha256="a" * 64,
        selection=ModelSelection(
            provider="ollama",
            model_identifier="local-fixture",
            deployment=ModelDeployment.LOCAL,
        ),
        specialist_role="continuity_supervisor",
        input_version_ids=(),
        inputs=(
            {
                "artifact_kind": ArtifactKind.SCENE_DRAFT.value,
                "artifact_key": "scene_1_draft",
                "artifact_version_id": str(uuid4()),
                "content": {
                    "scene_id": "scene_1",
                    "revision_number": 0,
                    "prose": "Mara locks the east door and pockets the brass key.",
                },
            },
            {
                "artifact_kind": ArtifactKind.SCENE_PLAN.value,
                "artifact_key": "scene_1_plan",
                "artifact_version_id": str(uuid4()),
                "content": {
                    "id": "scene_1",
                    "required_elements": [],
                    "outcome": "Mara must return the brass key.",
                },
            },
            {
                "artifact_kind": ArtifactKind.STORY_BIBLE.value,
                "artifact_key": "story_bible",
                "artifact_version_id": str(uuid4()),
                "content": {"prohibited_contradictions": ["Mara must return the brass key."]},
            },
        ),
        constraints={"required_elements": [], "forbidden_shortcuts": []},
        call_budget=ModelCallBudget(max_input_tokens=100, max_output_tokens=100),
        seed=1,
        task_fingerprint="fingerprint",
        unit_id="scene_1",
        unit_number=1,
        unit_count=1,
        revision_number=0,
        attempt_number=1,
        previous_failure=None,
        fallback_history=(),
    )
    finding: dict[str, object] = {
        "id": "east_door_key_continuity",
        "severity": "blocking",
        "category": "fact",
        "basis": "contradiction",
        "summary": "Mara keeps the established key.",
        "evidence": ["The requirement says Mara must return the key."],
        "canonical_source_refs": ["canonical_source_0001"],
    }
    with pytest.raises(ValueError, match="exact excerpts from the current draft"):
        _validate_continuity_finding_contract([finding], execution)

    finding["evidence"] = ["Mara locks the east door and pockets the brass key."]
    _validate_continuity_finding_contract([finding], execution)


def test_v17_copied_recheck_assessment_is_advisory_but_evidence_stays_exact() -> None:
    original = {
        "id": "stalled_blocker",
        "severity": "blocking",
        "category": "fact",
        "summary": "The transition lacks a causal bridge.",
        "evidence": ["The original draft jumps directly to ambition."],
        "recommended_resolution": "Connect failure directly to the need for control.",
        "recheck_disposition": "still_blocking",
        "repair_assessment": "The writer changed the transition but left the gap unresolved.",
        "revised_evidence": ["The revised draft still jumps directly to ambition."],
    }
    prior_report: dict[str, object] = {"findings": [original]}
    copied_assessment = {
        **original,
        "revised_evidence": ["The revised draft now names the failed system."],
    }

    assert (
        _invalid_continuity_recheck_finding_ids(
            [copied_assessment],
            prior_report,
            revised_draft_prose="The revised draft now names the failed system.",
        )
        == ()
    )

    fresh_assessment = {
        **copied_assessment,
        "repair_assessment": (
            "The new system reference is present, but its effect on the decision is absent."
        ),
    }
    assert (
        _invalid_continuity_recheck_finding_ids(
            [fresh_assessment],
            prior_report,
            revised_draft_prose="The revised draft now names the failed system.",
        )
        == ()
    )
    assert _invalid_continuity_recheck_finding_ids(
        [fresh_assessment],
        prior_report,
        revised_draft_prose="This draft contains no quoted evidence.",
    ) == ("stalled_blocker",)


def test_v17_copied_recheck_assessment_emits_content_free_advisory_telemetry() -> None:
    finding_id = "stalled_blocker"
    prior = {
        "id": finding_id,
        "severity": "blocking",
        "category": "fact",
        "basis": "contradiction",
        "summary": "The transition lacks a causal bridge.",
        "evidence": ["The original transition."],
        "canonical_source_refs": ["canonical_source_0001"],
        "recommended_resolution": "Connect failure to the decision.",
        "blocks_approval": True,
        "recheck_disposition": "still_blocking",
        "repair_assessment": "The causal bridge remains absent.",
        "revised_evidence": ["The first revised transition."],
        "related_scene_ids": ["scene_1"],
    }
    execution = _v17_catalog_test_execution()
    execution = replace(
        execution,
        inputs=(
            *execution.inputs,
            {
                "artifact_kind": ArtifactKind.CONTINUITY_REPORT.value,
                "artifact_key": "continuity_scene_1",
                "artifact_version_id": str(uuid4()),
                "content": {"findings": [prior]},
            },
        ),
    )
    report = ContinuityReport(
        story_bible_version_id=uuid4(),
        scene_version_id=uuid4(),
        scene_plan_version_id=uuid4(),
        scene_id="scene_1",
        scene_number=1,
        checked_categories=tuple(ContinuityCategory),
        findings=(
            ContinuityFinding.model_validate(
                {
                    "id": finding_id,
                    "severity": "blocking",
                    "category": "fact",
                    "basis": "contradiction",
                    "summary": "The transition still lacks a causal bridge.",
                    "evidence": ["The second revised transition."],
                    "canonical_source_refs": ["canonical_source_0001"],
                    "recommended_resolution": "Connect failure to the decision.",
                    "blocks_approval": True,
                    "recheck_disposition": "still_blocking",
                    "repair_assessment": "The causal bridge remains absent.",
                    "revised_evidence": ["The second revised transition."],
                    "related_scene_ids": ["scene_1"],
                }
            ),
        ),
    )

    assert _continuity_recheck_observations(report, execution) == (
        {
            "finding_id": finding_id,
            "type": "copied_assessment_after_changed_evidence",
            "disposition": "advisory",
        },
    )


def test_unchanged_recheck_evidence_allows_an_accurate_repeated_assessment() -> None:
    prior_finding = {
        "id": "unchanged_blocker",
        "severity": "blocking",
        "category": "fact",
        "summary": "The key remains in the wrong location.",
        "evidence": ["Mara pockets the brass key."],
        "recommended_resolution": "Have Mara return the key.",
    }
    finding = {
        **prior_finding,
        "recheck_disposition": "still_blocking",
        "repair_assessment": "The conflict remains unresolved.",
        "revised_evidence": ["Mara pockets the brass key."],
    }
    assert (
        _invalid_continuity_recheck_finding_ids(
            [finding],
            {"findings": [prior_finding]},
            revised_draft_prose="Mara pockets the brass key.",
        )
        == ()
    )


def test_benchmark_constraint_text_is_deferred_until_final_scene() -> None:
    constraints: dict[str, object] = {
        "required_elements": ["Resolve the card's origin."],
        "forbidden_shortcuts": ["Do not explain the card as a prank."],
    }

    non_final = _benchmark_constraint_applicability(
        constraints,
        unit_number=1,
        unit_count=5,
    )

    assert non_final["is_final_scene"] is False
    assert non_final["due_now"] == []
    assert non_final["deferred_until_final_scene"] == [
        {"id": "required_element_1", "kind": "required_element"},
        {"id": "forbidden_shortcut_1", "kind": "forbidden_shortcut"},
    ]
    assert "Resolve the card's origin." not in json.dumps(non_final)
    assert "Do not explain the card as a prank." not in json.dumps(non_final)

    final = _benchmark_constraint_applicability(
        constraints,
        unit_number=5,
        unit_count=5,
    )

    assert final["is_final_scene"] is True
    assert final["deferred_until_final_scene"] == []
    assert final["due_now"] == [
        {
            "id": "required_element_1",
            "kind": "required_element",
            "text": "Resolve the card's origin.",
        },
        {
            "id": "forbidden_shortcut_1",
            "kind": "forbidden_shortcut",
            "text": "Do not explain the card as a prank.",
        },
    ]


def test_duplicate_story_requirement_stays_deferred_in_non_final_scene_plan() -> None:
    constraints: dict[str, object] = {
        "required_elements": ["The stroller remains central to the plot."],
    }
    scene_plan: dict[str, object] = {
        "required_elements": [
            "The stroller remains central to the plot.",
            "Elara begins a concrete facade survey.",
        ]
    }

    non_final = _scene_plan_requirement_applicability(
        constraints,
        scene_plan,
        unit_number=1,
        unit_count=5,
    )

    assert non_final["due_now"] == [
        {
            "id": "scene_plan_required_element_2",
            "kind": "required_element",
            "category": "constraint",
            "source_field": "required_elements",
            "text": "Elara begins a concrete facade survey.",
        }
    ]
    assert non_final["deferred_until_final_scene"] == [
        {
            "id": "scene_plan_required_element_1",
            "matched_benchmark_requirement_id": "required_element_1",
        }
    ]
    assert "stroller" not in json.dumps(non_final).lower()

    final = _scene_plan_requirement_applicability(
        constraints,
        scene_plan,
        unit_number=5,
        unit_count=5,
    )
    final_due_now = final["due_now"]
    assert isinstance(final_due_now, list)
    assert [item["text"] for item in final_due_now if isinstance(item, dict)] == scene_plan[
        "required_elements"
    ]


def test_deferred_duplicate_story_requirement_is_redacted_from_prompt_inputs() -> None:
    constraints: dict[str, object] = {
        "required_elements": ["The stroller remains central to the plot."],
    }
    scene_plan_content: dict[str, object] = {
        "required_elements": [
            "The stroller remains central to the plot.",
            "Elara begins a concrete facade survey.",
        ]
    }
    scene_plan_input: dict[str, object] = {
        "artifact_kind": ArtifactKind.SCENE_PLAN.value,
        "content": scene_plan_content,
    }
    other_input: dict[str, object] = {
        "artifact_kind": ArtifactKind.SCENE_DRAFT.value,
        "content": {"prose": "Current draft."},
    }
    applicability = _scene_plan_requirement_applicability(
        constraints,
        scene_plan_content,
        unit_number=1,
        unit_count=5,
    )

    prompt_inputs = _continuity_prompt_inputs(
        (scene_plan_input, other_input),
        applicability,
    )

    prompt_plan = next(
        item for item in prompt_inputs if item["artifact_kind"] == ArtifactKind.SCENE_PLAN.value
    )
    assert prompt_plan["content"]["required_elements"] == ["Elara begins a concrete facade survey."]
    assert scene_plan_content["required_elements"] == [
        "The stroller remains central to the plot.",
        "Elara begins a concrete facade survey.",
    ]


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

    assert "findings:ContinuityRecheckStagnationError" in diagnostic
    assert "stalled_blocker" in diagnostic
    assert private_response_content not in diagnostic


def test_plain_value_error_diagnostic_preserves_bounded_actionable_detail() -> None:
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
        ValueError(
            "initial continuity findings cannot contain re-check analysis: ['premature_recheck']"
        ),
        response,
    )

    assert "$:ValueError:initial continuity findings cannot contain re-check analysis" in diagnostic
    assert "premature_recheck" in diagnostic
    assert private_response_content not in diagnostic


@pytest.mark.parametrize(
    ("deployment", "error_code", "expects_guidance"),
    (
        (ModelDeployment.LOCAL, "schema_validation_failed", True),
        (ModelDeployment.LOCAL, "continuity_recheck_stagnated", True),
        (ModelDeployment.LOCAL, "provider_timeout", False),
        (ModelDeployment.CLOUD, "schema_validation_failed", False),
    ),
)
def test_schema_repair_guidance_is_limited_to_local_structured_failures(
    deployment: ModelDeployment,
    error_code: str,
    expects_guidance: bool,
) -> None:
    guidance = _local_schema_repair_guidance(
        operation=_Operation.CONTINUITY,
        deployment=deployment,
        previous_failure={
            "error_code": error_code,
            "validation_issues": [
                {
                    "location": "findings.0",
                    "type": "value_error",
                    "message": "repair assessment is required",
                }
            ],
        },
        continuity_schema_variant=_ContinuitySchemaVariant.INITIAL_CHECK,
    )

    assert (guidance is not None) is expects_guidance
    if guidance is not None:
        assert guidance["mode"] == "repair_only"
        assert guidance["schema_variant"] == "initial_check"
        assert guidance["focus_locations"] == ["findings.0"]
        assert "recheck_disposition" in str(guidance["operation_rules"])


def test_initial_continuity_schema_omits_every_recheck_only_field() -> None:
    context = _schema_test_continuity_context()
    schema = _output_schema(
        _Operation.CONTINUITY,
        continuity_schema_variant=_ContinuitySchemaVariant.INITIAL_CHECK,
        continuity_model_context=context,
    )
    definitions = schema["$defs"]
    blocking = definitions["InitialBlockingContinuityFinding"]
    advisory = definitions["InitialAdvisoryContinuityFinding"]
    blocking_properties = blocking["properties"]
    advisory_properties = advisory["properties"]
    basis_branches = blocking_properties["basis_details"]["anyOf"]
    contradiction = basis_branches[0]
    forbidden = basis_branches[1]
    category_branches = contradiction["properties"]["category_details"]["anyOf"]
    coverage = schema["properties"]["requirement_coverage"]
    coverage_entry = definitions["InitialRequirementCoverageEntry"]
    missing = coverage_entry["anyOf"][1]
    non_world = category_branches[0]
    world = category_branches[1]

    assert schema["title"] == "InitialContinuityReport"
    assert "ContinuityRecheckDisposition" not in definitions
    assert "ContinuityFinding" not in definitions
    assert schema["properties"]["findings"]["items"] == {
        "anyOf": [
            {"$ref": "#/$defs/InitialBlockingContinuityFinding"},
            {"$ref": "#/$defs/InitialAdvisoryContinuityFinding"},
        ]
    }
    assert blocking_properties["severity"]["enum"] == ["error", "blocking"]
    assert "recommended_resolution" in blocking["required"]
    assert blocking_properties["recommended_resolution"] == {
        "type": "string",
        "minLength": 1,
        "title": "Recommended Resolution",
    }
    assert advisory_properties["severity"]["enum"] == ["info", "warning"]
    assert "recommended_resolution" not in advisory["required"]
    assert {"draft_evidence_refs", "canonical_source_refs"} <= set(contradiction["required"])
    assert contradiction["properties"]["draft_evidence_refs"]["items"]["enum"] == [
        "draft_evidence_0001"
    ]
    assert contradiction["properties"]["canonical_source_refs"]["items"]["enum"] == [
        "canonical_source_0001"
    ]
    assert "evidence" not in missing["properties"]
    assert {"status", "coverage_assessment"} <= set(missing["required"])
    assert {"requirement_id", "draft_evidence_refs"} <= set(forbidden["required"])
    assert forbidden["properties"]["requirement_id"]["enum"] == ["forbidden_shortcut_1"]
    assert non_world["properties"]["category"]["enum"] == [
        category.value
        for category in ContinuityCategory
        if category not in {ContinuityCategory.WORLD_RULE, ContinuityCategory.CONSTRAINT}
    ]
    assert coverage["required"] == ["required_element_1"]
    assert set(coverage["properties"]) == {"required_element_1"}
    assert coverage["additionalProperties"] is False
    assert {
        "world_rule_ids",
        "companion_rule_assessment",
        "condition_explicitly_authorized",
    }.isdisjoint(blocking_properties)
    world_properties = world["properties"]
    assert world_properties["category"]["const"] == "world_rule"
    assert world_properties["world_rule_ids"]["items"]["enum"] == ["world_rule_1"]
    assert world_properties["world_rule_ids"]["minItems"] == 1
    assert world_properties["condition_explicitly_authorized"]["const"] is False
    assert {
        "world_rule_ids",
        "companion_rule_assessment",
        "condition_explicitly_authorized",
    } <= set(world["required"])
    assert "world_rule" not in non_world["properties"]["category"]["enum"]
    assert "constraint" not in non_world["properties"]["category"]["enum"]
    assert "category_details" not in blocking_properties
    assert "category_details" not in forbidden["properties"]
    assert "id" not in blocking_properties
    assert "id" not in advisory_properties
    assert "blocks_approval" not in blocking_properties
    assert "blocks_approval" not in advisory_properties
    assert {
        "recheck_disposition",
        "repair_assessment",
        "revised_evidence",
    }.isdisjoint(blocking_properties)
    assert {
        "recheck_disposition",
        "repair_assessment",
        "revised_evidence",
    }.isdisjoint(advisory_properties)
    assert "evidence" not in advisory_properties
    assert "draft_evidence_refs" not in advisory_properties
    assert {
        "story_bible_version_id",
        "scene_version_id",
        "scene_plan_version_id",
        "scene_id",
        "scene_number",
        "checked_categories",
    }.isdisjoint(schema["properties"])

    canonical_definitions = ContinuityReport.model_json_schema()["$defs"]
    canonical_properties = canonical_definitions["ContinuityFinding"]["properties"]
    assert "ContinuityRecheckDisposition" in canonical_definitions
    assert "recheck_disposition" in canonical_properties


def test_v16_critic_schema_makes_overall_score_application_owned() -> None:
    schema = _output_schema(
        _Operation.CRITIQUE,
        continuity_schema_variant=None,
    )

    assert "overall_score" not in schema["properties"]
    assert "overall_score" not in schema["required"]
    assert "overall_score" in Critique.model_json_schema()["required"]


def test_continuity_recheck_schema_exposes_recheck_analysis_fields() -> None:
    context = _schema_test_continuity_context(recheck=True)
    schema = _output_schema(
        _Operation.CONTINUITY,
        continuity_schema_variant=_ContinuitySchemaVariant.RECHECK,
        continuity_model_context=context,
    )
    definitions = schema["$defs"]
    blocking = definitions["RecheckBlockingContinuityFinding"]
    advisory = definitions["RecheckAdvisoryContinuityFinding"]
    blocking_properties = blocking["properties"]
    advisory_properties = advisory["properties"]
    basis_branches = blocking_properties["basis_details"]["anyOf"]
    contradiction = basis_branches[0]
    missing = definitions["RecheckRequirementCoverageEntry"]["anyOf"][1]
    world = contradiction["properties"]["category_details"]["anyOf"][1]

    assert schema["title"] == "RecheckContinuityReport"
    assert "ContinuityRecheckDisposition" not in definitions
    assert {
        "recommended_resolution",
        "repair_assessment",
    } <= set(blocking["required"])
    assert "prior_finding_id" in blocking_properties
    assert blocking_properties["prior_finding_id"]["enum"] == []
    assert contradiction["properties"]["revised_draft_evidence_refs"]["minItems"] == 1
    assert contradiction["properties"]["revised_draft_evidence_refs"]["items"]["enum"] == [
        "draft_evidence_0001"
    ]
    assert "recheck_evidence_state" not in contradiction["properties"]
    assert "revised_evidence" not in missing["properties"]
    assert "coverage_assessment" in missing["required"]
    assert "revised_draft_evidence_refs" not in missing["properties"]
    assert {
        "world_rule_ids",
        "companion_rule_assessment",
        "condition_explicitly_authorized",
    } <= set(world["required"])
    assert "recheck_disposition" not in blocking_properties
    assert {
        "recheck_disposition",
        "repair_assessment",
        "revised_evidence",
    }.isdisjoint(advisory_properties)
    assert "blocks_approval" not in blocking_properties
    assert "blocks_approval" not in advisory_properties


def test_v17_schema_uses_empty_keyed_coverage_when_nothing_is_due() -> None:
    context = replace(
        _schema_test_continuity_context(),
        requirement_catalog=(),
        forbidden_shortcut_catalog=(),
        requirement_kinds={},
        requirement_categories={},
    )
    schema = _output_schema(
        _Operation.CONTINUITY,
        continuity_schema_variant=_ContinuitySchemaVariant.INITIAL_CHECK,
        continuity_model_context=context,
    )
    definitions = schema["$defs"]

    blocking = definitions["InitialBlockingContinuityFinding"]
    basis_branches = blocking["properties"]["basis_details"]["anyOf"]
    assert [branch["properties"]["basis"]["const"] for branch in basis_branches] == [
        "contradiction",
    ]
    coverage = schema["properties"]["requirement_coverage"]
    assert coverage["properties"] == {}
    assert coverage["required"] == []
    assert coverage["additionalProperties"] is False
    assert schema["properties"]["findings"]["items"] == {
        "anyOf": [
            {"$ref": "#/$defs/InitialBlockingContinuityFinding"},
            {"$ref": "#/$defs/InitialAdvisoryContinuityFinding"},
        ]
    }


def test_v15_recheck_schema_stays_compact_without_unsupported_all_of() -> None:
    schema = _output_schema(
        _Operation.CONTINUITY,
        continuity_schema_variant=_ContinuitySchemaVariant.RECHECK,
        continuity_model_context=_schema_test_continuity_context(recheck=True),
    )
    serialized = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))

    assert len(serialized.encode("utf-8")) < 8_000
    assert '"allOf"' not in serialized


def test_terminal_workflow_cause_outranks_a_recovered_invocation_failure() -> None:
    assert (
        _preferred_production_failure_detail(
            workflow_detail="Scene revision limit reached after consolidated review.",
            invocation_detail="production specialist returned invalid structured output",
        )
        == "Scene revision limit reached after consolidated review."
    )
    assert (
        _preferred_production_failure_detail(
            workflow_detail="production specialist returned invalid structured output",
            invocation_detail="findings.0.basis_details was invalid",
        )
        == "findings.0.basis_details was invalid"
    )


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
async def test_hybrid_unchanged_continuity_blocker_routes_without_false_fallback(
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
    assert gateway.escalated_retry_payloads == []
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
        assert invocations
        assert all(invocation.model_identifier == "local-fixture" for invocation in invocations)
        assert all(not invocation.fallback_history for invocation in invocations)
        assert all(
            invocation.error_code != "continuity_recheck_stagnated" for invocation in invocations
        )


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
    with session_factory() as session:
        persisted_continuity_invocations = session.scalars(
            select(AgentInvocation).where(
                AgentInvocation.workflow_run_id == execution.workflow_run_id,
                AgentInvocation.specialist_role == "continuity_supervisor",
            )
        ).all()
    assert {
        invocation.request_settings["output_schema_variant"]
        for invocation in persisted_continuity_invocations
    } == {"initial_check", "recheck"}
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
    assert [report["findings"] for report in gateway.continuity_recheck_reports] == [
        report["findings"] for report in gateway.writer_revision_reports
    ]
    assert all(set(report) == {"findings"} for report in gateway.continuity_recheck_reports)
    for recheck_contract in gateway.continuity_recheck_contracts:
        assert "previous_report_version_id" in recheck_contract
        assert "audit every prior error or blocking finding" in str(
            recheck_contract["verification_contract"]
        )
        assert "contradictory guidance" in str(recheck_contract["verification_contract"])

    continuity_requests = [
        request
        for request in gateway.requests
        if request.invocation.specialist_role == "continuity_supervisor"
    ]
    initial_requests = [
        request
        for request in continuity_requests
        if json.loads(request.messages[-1].content)["assignment"]["revision_number"] == 0
    ]
    recheck_requests = [
        request
        for request in continuity_requests
        if json.loads(request.messages[-1].content)["assignment"]["revision_number"] > 0
    ]
    assert initial_requests
    assert recheck_requests
    for request in initial_requests:
        assert request.response_schema is not None
        payload = json.loads(request.messages[-1].content)
        schema = cast(dict[str, Any], request.response_schema)
        definitions = cast(dict[str, Any], schema["$defs"])
        blocking = cast(
            dict[str, Any],
            definitions["InitialBlockingContinuityFinding"],
        )
        advisory = cast(dict[str, Any], definitions["InitialAdvisoryContinuityFinding"])
        blocking_properties = cast(dict[str, Any], blocking["properties"])
        advisory_properties = cast(dict[str, Any], advisory["properties"])
        assert payload["output_schema_variant"] == "initial_check"
        assert payload["output_schema_delivery"] == "enforced_by_local_gateway"
        assert "output_schema" not in payload
        assert "input_artifacts" not in payload
        assert payload["candidate_draft"]["continuity_role"] == (
            "candidate_draft_and_only_valid_evidence_source"
        )
        assert "evidence_catalog" in payload["candidate_draft"]["content"]
        assert "prose" not in payload["candidate_draft"]["content"]
        assert "accepted_prior_drafts" in payload
        assert "canonical_source_catalog" in payload
        assert "requirement_coverage_catalog" in payload
        assert "forbidden_shortcut_catalog" in payload
        assert "benchmark_constraint_applicability" not in payload
        assert "scene_plan_requirement_applicability" not in payload
        assert all(
            item["continuity_role"] == "immediately_prior_accepted_scene_ending_not_valid_evidence"
            for item in payload["accepted_prior_drafts"]
        )
        assert len(payload["accepted_prior_drafts"]) <= 1
        assert all(
            "prose" not in item["content"] and "ending_excerpt" in item["content"]
            for item in payload["accepted_prior_drafts"]
        )
        source_catalog = payload["canonical_source_catalog"]
        assert source_catalog
        assert all(
            {
                "reference_id",
                "artifact_kind",
                "artifact_key",
                "artifact_version_id",
                "source_path",
                "claim",
            }
            <= set(entry)
            for entry in source_catalog
        )
        assert any(
            entry["artifact_kind"] == ArtifactKind.STORY_BLUEPRINT.value for entry in source_catalog
        )
        assert not any(
            entry["artifact_kind"] == ArtifactKind.SCENE_PLAN.value
            and entry["source_path"].split(".")[-1]
            in {
                "entry_state",
                "time_context",
                "purpose",
                "goal",
                "conflict",
                "turning_point",
                "outcome",
                "exit_state",
                "continuity_requirements",
                "required_elements",
            }
            for entry in source_catalog
        )
        contradiction_details = blocking_properties["basis_details"]["anyOf"][0]
        assert contradiction_details["properties"]["canonical_source_refs"]["items"]["enum"] == [
            entry["reference_id"] for entry in source_catalog
        ]
        assert "recheck_analysis" not in payload["output_requirements"]
        assert "continuity_recheck" not in payload
        assert "recommended_resolution" in blocking["required"]
        assert "blocks_approval" not in blocking_properties
        assert "blocks_approval" not in advisory_properties
        assert {
            "recheck_disposition",
            "repair_assessment",
            "revised_evidence",
        }.isdisjoint(blocking_properties)
    for request in recheck_requests:
        assert request.response_schema is not None
        payload = json.loads(request.messages[-1].content)
        schema = cast(dict[str, Any], request.response_schema)
        definitions = cast(dict[str, Any], schema["$defs"])
        blocking = cast(
            dict[str, Any],
            definitions["RecheckBlockingContinuityFinding"],
        )
        advisory = cast(dict[str, Any], definitions["RecheckAdvisoryContinuityFinding"])
        blocking_properties = cast(dict[str, Any], blocking["properties"])
        advisory_properties = cast(dict[str, Any], advisory["properties"])
        assert payload["output_schema_variant"] == "recheck"
        assert payload["output_schema_delivery"] == "enforced_by_local_gateway"
        assert "output_schema" not in payload
        assert "recheck_analysis" in payload["output_requirements"]
        assert {
            "recommended_resolution",
            "repair_assessment",
        } <= set(blocking["required"])
        assert "prior_finding_id" in blocking_properties
        contradiction_details = blocking_properties["basis_details"]["anyOf"][0]
        assert "revised_draft_evidence_refs" in contradiction_details["required"]
        assert "recheck_evidence_state" not in contradiction_details["properties"]
        assert "blocks_approval" not in blocking_properties
        assert {
            "recheck_disposition",
            "repair_assessment",
            "revised_evidence",
        }.isdisjoint(advisory_properties)

    recheck_payload = json.loads(gateway.continuity_recheck_prompts[0])
    output_requirements = recheck_payload["output_requirements"]
    assert "sole authorit" in output_requirements["requirement_scope"]
    assert "prior_finding_id" in output_requirements["recheck_analysis"]
    assert "application owns" in output_requirements["recheck_analysis"]
    assert "frozen_benchmark_constraints" not in recheck_payload
    assert "benchmark_constraint_applicability" not in recheck_payload
    assert "scene_plan_requirement_applicability" not in recheck_payload


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
    validation_issues = repair_context["validation_issues"]
    assert isinstance(validation_issues, list)
    assert validation_issues[0]["location"] == "findings.0"
    assert "requires a resolution" in str(validation_issues[0]["message"])
    assert len(gateway.local_schema_repairs) == 1
    local_schema_repair = gateway.local_schema_repairs[0]
    assert local_schema_repair["focus_locations"] == ["findings.0"]
    assert "recheck_disposition" in str(local_schema_repair["operation_rules"])
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
        persisted_issues = invocations[0].request_settings["structured_failure"]["issues"]
        assert persisted_issues[0]["location"] == "findings.0"
        assert "requires a resolution" in persisted_issues[0]["message"]

    case_executor = AgenticBenchmarkCaseExecutor(
        campaign_id=CAMPAIGN_ID,
        database_path=migrated_database_path,
        session_factory=session_factory,
        gateway=gateway,
    )
    with pytest.raises(BenchmarkCaseExecutionError) as failure:
        await case_executor.execute(case, prompt)
    assert "Scene production failed at continuity:" in str(failure.value)
    assert "findings.0" in str(failure.value)
    assert "requires a resolution" in str(failure.value)
    assert "production specialist returned invalid structured output" not in str(failure.value)
    assert "The persisted agentic scene-production run failed." not in str(failure.value)


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
    assert len(gateway.local_schema_repairs) == 1
    story_bible_rules = str(gateway.local_schema_repairs[0]["operation_rules"])
    assert "canonical IDs" in story_bible_rules
    assert "invented alias" in story_bible_rules
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
    non_final_applicabilities = [
        item for item in gateway.constraint_applicabilities if not item["is_final_scene"]
    ]
    final_applicabilities = [
        item for item in gateway.constraint_applicabilities if item["is_final_scene"]
    ]
    assert non_final_applicabilities
    assert all(
        all(
            entry.get("source") != "benchmark"
            for entry in cast(list[dict[str, object]], item["due_now"])
        )
        for item in non_final_applicabilities
    )
    assert len(final_applicabilities) == 1
    final_due_now = final_applicabilities[0]["due_now"]
    assert isinstance(final_due_now, list)
    assert all(isinstance(item, dict) for item in final_due_now)
    final_constraint_text = {
        item["text"]
        for item in final_due_now
        if isinstance(item, dict) and item.get("source") == "benchmark"
    }
    assert final_constraint_text == {
        *prompt.required_elements,
        *prompt.forbidden_shortcuts,
    }
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
    assert all(
        request.invocation.prompt_template_version == SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION
        for request in production_requests
    )
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

    with session_factory.begin() as session:
        story_version = session.get(ArtifactVersion, output.artifact_version_ids[-1])
        assert story_version is not None
        legacy_content = dict(story_version.content)
        legacy_content.pop("word_count_adherence")
        legacy_gates = dict(legacy_content["hard_gates"])
        legacy_gates[HardGate.COMPLETE.value] = False
        legacy_gates[HardGate.TARGET_FORMAT_VALID.value] = False
        legacy_content["hard_gates"] = legacy_gates
        # Simulate a historical immutable row created before advisory measurements existed.
        session.execute(
            update(ArtifactVersion)
            .where(ArtifactVersion.id == story_version.id)
            .values(
                content=legacy_content,
                content_sha256=canonical_sha256(legacy_content),
            )
        )
    legacy_artifact_replay = await case_executor.execute(case, prompt)

    assert output == output_replay
    assert output == legacy_artifact_replay
    assert output.workflow_run_id == execution.workflow_run_id
    assert len(output.invocation_ids) == 19
    assert len(output.artifact_version_ids) == 6
    assert output.content.count("\n\n") == 2
    assert output.word_count_adherence is not None
    assert output.word_count_adherence.status is WordCountStatus.UNDER_TARGET
    assert output.hard_gates[HardGate.COMPLETE] is True
    assert output.hard_gates[HardGate.TARGET_FORMAT_VALID] is None
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
