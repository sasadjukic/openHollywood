"""Durable agentic benchmark preparation through the real Blueprint graph."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid5

from open_hollywood_engine.artifacts import ArtifactKind
from open_hollywood_engine.evaluations import (
    BenchmarkCase,
    BenchmarkCaseExecutionError,
    BenchmarkOutput,
    BenchmarkPrompt,
    BenchmarkSystem,
    HardGate,
    canonical_sha256,
)
from open_hollywood_engine.models import ModelGateway
from open_hollywood_engine.workflows import (
    DEFAULT_MAX_GRAPH_STEPS,
    STORY_BLUEPRINT_GRAPH_VERSION,
    STORY_BLUEPRINT_WORKFLOW_NAME,
    ArtifactReference,
    RunBudget,
    SceneProductionResult,
)
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    Project,
    RunStatus,
    WorkflowEvent,
    WorkflowRun,
)
from open_hollywood_api.services.blueprint_model_executor import (
    BenchmarkBlueprintNodeExecutor,
)
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService
from open_hollywood_api.services.evaluation_execution import automatic_hard_gates
from open_hollywood_api.services.production_model_executor import (
    BenchmarkProductionExecutor,
)
from open_hollywood_api.services.production_workflow import (
    BenchmarkSceneProductionService,
)

AGENTIC_BENCHMARK_BLUEPRINT_BUDGET = RunBudget(
    max_graph_steps=DEFAULT_MAX_GRAPH_STEPS,
    max_model_calls=12,
    max_input_tokens=120_000,
    max_output_tokens=36_000,
    max_cost_usd=Decimal("0.50"),
    max_wall_clock_seconds=3_600,
    per_call_input_tokens=12_000,
    per_call_output_tokens=8_000,
    per_call_cost_usd=Decimal("0.08"),
)


@dataclass(frozen=True, slots=True)
class AgenticBlueprintPreparation:
    """One benchmark case paused at or completed past Blueprint governance."""

    case_id: UUID
    project_id: UUID
    workflow_run_id: UUID
    artifacts: tuple[ArtifactReference, ...]
    awaiting_approval: bool
    interrupt_id: str | None


class AgenticBenchmarkBlueprintService:
    """Prepare one exact agentic case through the mandatory approval interrupt."""

    def __init__(
        self,
        *,
        campaign_id: UUID,
        database_path: Path,
        session_factory: sessionmaker[Session],
        gateway: ModelGateway,
    ) -> None:
        self._campaign_id = campaign_id
        self._database_path = database_path
        self._session_factory = session_factory
        self._gateway = gateway

    async def prepare(
        self,
        case: BenchmarkCase,
        prompt: BenchmarkPrompt,
    ) -> AgenticBlueprintPreparation:
        """Create or resume one Blueprint run without bypassing human approval."""
        if case.system is not BenchmarkSystem.AGENTIC or case.profile is None:
            raise BenchmarkCaseExecutionError(
                "unsupported_benchmark_system",
                "Agentic Blueprint preparation requires a profile-backed agentic case.",
            )
        project_id, run_id = self._persist_case(case, prompt)
        executor = BenchmarkBlueprintNodeExecutor(
            session_factory=self._session_factory,
            gateway=self._gateway,
        )
        async with BlueprintWorkflowService(
            self._database_path,
            self._session_factory,
            executor,
        ) as workflow:
            status = self._run_status(run_id)
            execution = (
                await workflow.inspect(run_id)
                if status in {RunStatus.PAUSED, RunStatus.SUCCEEDED}
                else await workflow.execute(run_id)
            )
        return AgenticBlueprintPreparation(
            case_id=case.case_id,
            project_id=project_id,
            workflow_run_id=run_id,
            artifacts=execution.artifacts,
            awaiting_approval=execution.awaiting_approval,
            interrupt_id=execution.interrupt_id,
        )

    def _persist_case(
        self,
        case: BenchmarkCase,
        prompt: BenchmarkPrompt,
    ) -> tuple[UUID, UUID]:
        profile = case.profile
        if profile is None:
            raise RuntimeError("agentic benchmark case has no profile snapshot")
        project_id = uuid5(case.case_id, "agentic-benchmark-project")
        run_id = uuid5(case.case_id, "agentic-blueprint-workflow")
        prompt_version_id = uuid5(case.case_id, "agentic-benchmark-prompt-version")
        with self._session_factory.begin() as session:
            project = session.get(Project, project_id)
            if project is None:
                project = Project(
                    id=project_id,
                    name=f"Benchmark {prompt.prompt_id} — {case.target_key}",
                    description="Synthetic frozen-corpus agentic benchmark case.",
                    story_format="short_prose",
                    settings={
                        "benchmark_campaign_id": str(self._campaign_id),
                        "benchmark_case_id": str(case.case_id),
                        "benchmark_target": case.target_key,
                    },
                )
                session.add(project)
            else:
                _require_matching_project(project, self._campaign_id, case)

            prompt_version = session.get(ArtifactVersion, prompt_version_id)
            if prompt_version is None:
                prompt_artifact = Artifact(
                    id=uuid5(case.case_id, "agentic-benchmark-prompt-artifact"),
                    project=project,
                    artifact_key="benchmark-prompt",
                    artifact_type="benchmark_prompt",
                    title=f"{prompt.prompt_id} v{prompt.version}",
                    status=ArtifactStatus.APPROVED,
                )
                prompt_content = prompt.model_dump(mode="json")
                prompt_version = ArtifactVersion(
                    id=prompt_version_id,
                    artifact=prompt_artifact,
                    version_number=1,
                    schema_version="benchmark-prompt-1",
                    content=prompt_content,
                    content_sha256=canonical_sha256(prompt_content),
                    change_summary="Frozen agentic benchmark prompt input.",
                )
                session.add_all((prompt_artifact, prompt_version))

            run = session.get(WorkflowRun, run_id)
            expected_input = {
                "benchmark_campaign_id": str(self._campaign_id),
                "benchmark_case_id": str(case.case_id),
                "benchmark_prompt_version_id": str(prompt_version_id),
                "model_profile_id": str(profile.profile_id),
                "model_profile_configuration": profile.configuration,
                "model_profile_configuration_sha256": profile.configuration_sha256,
                "premise": prompt.prompt,
                "run_seed": case.run_seed,
                "benchmark_constraints": {
                    "category": prompt.category.value,
                    "genres": list(prompt.genres),
                    "intended_maturity": prompt.intended_maturity.value,
                    "target_word_count": prompt.target_word_count.model_dump(mode="json"),
                    "required_elements": list(prompt.required_elements),
                    "forbidden_shortcuts": list(prompt.forbidden_shortcuts),
                    "factual_research_allowed": prompt.factual_research_allowed,
                },
            }
            if run is None:
                run = WorkflowRun(
                    id=run_id,
                    project=project,
                    workflow_name=STORY_BLUEPRINT_WORKFLOW_NAME,
                    graph_version=STORY_BLUEPRINT_GRAPH_VERSION,
                    status=RunStatus.PENDING,
                    input_state=expected_input,
                    budget=AGENTIC_BENCHMARK_BLUEPRINT_BUDGET.to_data(),
                )
                session.add(run)
            else:
                if (
                    run.project_id != project_id
                    or run.workflow_name != STORY_BLUEPRINT_WORKFLOW_NAME
                    or run.graph_version != STORY_BLUEPRINT_GRAPH_VERSION
                    or run.input_state != expected_input
                ):
                    raise BenchmarkCaseExecutionError(
                        "benchmark_lineage_conflict",
                        "Persisted agentic Blueprint lineage does not match the campaign case.",
                    )
                expected_budget = AGENTIC_BENCHMARK_BLUEPRINT_BUDGET.to_data()
                if run.budget != expected_budget:
                    if run.status not in {RunStatus.PENDING, RunStatus.FAILED}:
                        raise BenchmarkCaseExecutionError(
                            "benchmark_budget_conflict",
                            "Prepared agentic Blueprint budget differs from the runtime contract.",
                        )
                    previous_budget = dict(run.budget)
                    run.budget = expected_budget
                    session.add(
                        WorkflowEvent(
                            workflow_run_id=run.id,
                            event_type="benchmark.budget_updated",
                            source="evaluation_harness",
                            payload={
                                "previous_budget": previous_budget,
                                "budget": expected_budget,
                            },
                        )
                    )
            session.flush()
            return project.id, run.id

    def _run_status(self, run_id: UUID) -> RunStatus:
        with self._session_factory() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None:
                raise RuntimeError("agentic Blueprint run disappeared")
            return run.status


class AgenticBenchmarkCaseExecutor:
    """Run one approved agentic case through production and document assembly."""

    def __init__(
        self,
        *,
        campaign_id: UUID,
        database_path: Path,
        session_factory: sessionmaker[Session],
        gateway: ModelGateway,
    ) -> None:
        self._session_factory = session_factory
        self._gateway = gateway
        self._blueprints = AgenticBenchmarkBlueprintService(
            campaign_id=campaign_id,
            database_path=database_path,
            session_factory=session_factory,
            gateway=gateway,
        )
        self._database_path = database_path
        self._campaign_id = campaign_id

    async def execute(
        self,
        case: BenchmarkCase,
        prompt: BenchmarkPrompt,
    ) -> BenchmarkOutput:
        """Resume an approved case and return its immutable complete story."""
        prepared = await self._blueprints.prepare(case, prompt)
        if prepared.awaiting_approval:
            raise BenchmarkCaseExecutionError(
                "blueprint_approval_required",
                "The agentic case is paused at the mandatory Story Blueprint approval.",
            )
        blueprint = next(
            (
                reference
                for reference in prepared.artifacts
                if reference.kind is ArtifactKind.STORY_BLUEPRINT
            ),
            None,
        )
        if blueprint is None:
            raise BenchmarkCaseExecutionError(
                "approved_blueprint_missing",
                "The approved agentic case has no Story Blueprint artifact.",
            )
        production_executor = BenchmarkProductionExecutor(
            session_factory=self._session_factory,
            gateway=self._gateway,
        )
        try:
            async with BenchmarkSceneProductionService(
                database_path=self._database_path,
                session_factory=self._session_factory,
                executor=production_executor,
            ) as production:
                execution = await production.execute(
                    prepared.workflow_run_id,
                    blueprint,
                )
        except BenchmarkCaseExecutionError:
            raise
        except Exception as error:
            raise BenchmarkCaseExecutionError(
                "agentic_production_failed",
                "The persisted agentic scene-production run failed.",
            ) from error
        if execution.result is None or execution.status is not RunStatus.SUCCEEDED:
            raise BenchmarkCaseExecutionError(
                "agentic_production_paused",
                "The agentic scene-production run is paused and has no complete output.",
            )
        return self._assemble_output(
            case,
            prompt,
            prepared.workflow_run_id,
            execution.result,
        )

    def _assemble_output(
        self,
        case: BenchmarkCase,
        prompt: BenchmarkPrompt,
        blueprint_run_id: UUID,
        production_result: SceneProductionResult,
    ) -> BenchmarkOutput:
        with self._session_factory.begin() as session:
            production_run = session.get(
                WorkflowRun,
                production_result.workflow_run_id,
            )
            if (
                production_run is None
                or production_run.parent_workflow_run_id != blueprint_run_id
                or production_run.status is not RunStatus.SUCCEEDED
            ):
                raise BenchmarkCaseExecutionError(
                    "agentic_lineage_incomplete",
                    "The completed production run has invalid Blueprint lineage.",
                )
            scene_versions = tuple(
                _load_accepted_scene(
                    session,
                    production_run.project_id,
                    unit.artifact,
                )
                for unit in production_result.accepted_units
            )
            content = "\n\n".join(
                str(version.content["prose"]).strip() for version in scene_versions
            )
            title = f"Benchmark Story {prompt.prompt_id}"[:200]
            word_count = len(content.split())
            gates = automatic_hard_gates(
                content=content,
                word_count=word_count,
                prompt=prompt,
                finish_reason="stop",
            )
            gates[HardGate.CENTRAL_FACTS_CONSISTENT] = True
            content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
            story_artifact = session.scalar(
                select(Artifact).where(
                    Artifact.project_id == production_run.project_id,
                    Artifact.artifact_key == "benchmark-story",
                )
            )
            if story_artifact is None:
                story_artifact = Artifact(
                    id=uuid5(case.case_id, "agentic-benchmark-story-artifact"),
                    project_id=production_run.project_id,
                    artifact_key="benchmark-story",
                    artifact_type="benchmark_story",
                    title=title,
                    status=ArtifactStatus.DRAFT,
                )
                session.add(story_artifact)
            artifact_content = {
                "schema_version": "1",
                "benchmark_campaign_id": str(self._campaign_id),
                "benchmark_case_id": str(case.case_id),
                "prompt_id": prompt.prompt_id,
                "prompt_version": prompt.version,
                "title": title,
                "content": content,
                "content_sha256": content_sha256,
                "word_count": word_count,
                "hard_gates": {gate.value: value for gate, value in gates.items()},
                "accepted_scene_version_ids": [str(version.id) for version in scene_versions],
                "final_story_bible_version_id": str(production_result.final_story_bible.version_id),
            }
            story_version_id = uuid5(
                case.case_id,
                f"agentic-benchmark-story:{content_sha256}",
            )
            story_version = session.get(ArtifactVersion, story_version_id)
            if story_version is None:
                story_version = ArtifactVersion(
                    id=story_version_id,
                    artifact=story_artifact,
                    version_number=len(story_artifact.versions) + 1,
                    schema_version="benchmark-story-1",
                    content=artifact_content,
                    content_sha256=canonical_sha256(artifact_content),
                    change_summary=("Deterministically assembled from accepted scene versions."),
                )
                session.add(story_version)
                session.flush()
            elif (
                story_version.artifact_id != story_artifact.id
                or story_version.content != artifact_content
            ):
                raise BenchmarkCaseExecutionError(
                    "agentic_lineage_conflict",
                    "Persisted agentic story assembly conflicts with the accepted scenes.",
                )
            blueprint_version_id = _approved_blueprint_version_id(
                session,
                blueprint_run_id,
            )
            invocation_rows = tuple(
                session.scalars(
                    select(AgentInvocation)
                    .where(
                        AgentInvocation.workflow_run_id.in_((blueprint_run_id, production_run.id))
                    )
                    .order_by(
                        AgentInvocation.started_at,
                        AgentInvocation.id,
                    )
                )
            )
            if not invocation_rows:
                raise BenchmarkCaseExecutionError(
                    "agentic_lineage_incomplete",
                    "The assembled story has no model invocation lineage.",
                )
            artifact_version_ids = tuple(
                dict.fromkeys(
                    (
                        blueprint_version_id,
                        *(version.id for version in scene_versions),
                        production_result.final_story_bible.version_id,
                        story_version.id,
                    )
                )
            )
            return BenchmarkOutput(
                title=title,
                content=content,
                content_sha256=content_sha256,
                word_count=word_count,
                workflow_run_id=production_run.id,
                artifact_version_ids=artifact_version_ids,
                invocation_ids=tuple(row.id for row in invocation_rows),
                input_tokens=sum(row.input_tokens for row in invocation_rows),
                output_tokens=sum(row.output_tokens for row in invocation_rows),
                latency_ms=sum(row.latency_ms or 0 for row in invocation_rows),
                estimated_cost_usd=format(
                    sum(
                        (row.estimated_cost_usd for row in invocation_rows),
                        start=Decimal("0"),
                    ),
                    "f",
                ),
                hard_gates=gates,
            )


def _require_matching_project(
    project: Project,
    campaign_id: UUID,
    case: BenchmarkCase,
) -> None:
    expected = {
        "benchmark_campaign_id": str(campaign_id),
        "benchmark_case_id": str(case.case_id),
        "benchmark_target": case.target_key,
    }
    if any(project.settings.get(key) != value for key, value in expected.items()):
        raise BenchmarkCaseExecutionError(
            "benchmark_lineage_conflict",
            "Persisted benchmark project does not match the campaign case.",
        )


def _load_accepted_scene(
    session: Session,
    project_id: UUID,
    reference: ArtifactReference,
) -> ArtifactVersion:
    version = session.get(ArtifactVersion, reference.version_id)
    if (
        version is None
        or version.artifact.project_id != project_id
        or version.artifact.artifact_type != ArtifactKind.SCENE_DRAFT.value
        or version.artifact.artifact_key != reference.artifact_key
        or version.schema_version != reference.schema_version
        or version.artifact.status is not ArtifactStatus.APPROVED
    ):
        raise BenchmarkCaseExecutionError(
            "agentic_lineage_incomplete",
            "An accepted scene has invalid immutable artifact lineage.",
        )
    return version


def _approved_blueprint_version_id(
    session: Session,
    blueprint_run_id: UUID,
) -> UUID:
    version = session.scalar(
        select(ArtifactVersion)
        .join(ArtifactVersion.created_by_invocation)
        .join(ArtifactVersion.artifact)
        .where(
            AgentInvocation.workflow_run_id == blueprint_run_id,
            Artifact.artifact_type == ArtifactKind.STORY_BLUEPRINT.value,
            Artifact.status == ArtifactStatus.APPROVED,
        )
        .order_by(ArtifactVersion.version_number.desc())
    )
    if version is None:
        raise BenchmarkCaseExecutionError(
            "agentic_lineage_incomplete",
            "The approved Blueprint version is missing from story lineage.",
        )
    return version.id
