"""Durable agentic benchmark preparation through the real Blueprint graph."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid5

from open_hollywood_engine.evaluations import (
    BenchmarkCase,
    BenchmarkCaseExecutionError,
    BenchmarkPrompt,
    BenchmarkSystem,
    canonical_sha256,
)
from open_hollywood_engine.models import ModelGateway
from open_hollywood_engine.workflows import (
    DEFAULT_MAX_GRAPH_STEPS,
    STORY_BLUEPRINT_GRAPH_VERSION,
    STORY_BLUEPRINT_WORKFLOW_NAME,
    ArtifactReference,
    RunBudget,
)
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import (
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    Project,
    RunStatus,
    WorkflowRun,
)
from open_hollywood_api.services.blueprint_model_executor import (
    BenchmarkBlueprintNodeExecutor,
)
from open_hollywood_api.services.blueprint_workflow import BlueprintWorkflowService

AGENTIC_BENCHMARK_BLUEPRINT_BUDGET = RunBudget(
    max_graph_steps=DEFAULT_MAX_GRAPH_STEPS,
    max_model_calls=12,
    max_input_tokens=120_000,
    max_output_tokens=36_000,
    max_cost_usd=Decimal("0.50"),
    max_wall_clock_seconds=3_600,
    per_call_input_tokens=12_000,
    per_call_output_tokens=4_000,
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
            elif (
                run.project_id != project_id
                or run.workflow_name != STORY_BLUEPRINT_WORKFLOW_NAME
                or run.graph_version != STORY_BLUEPRINT_GRAPH_VERSION
                or run.input_state != expected_input
            ):
                raise BenchmarkCaseExecutionError(
                    "benchmark_lineage_conflict",
                    "Persisted agentic Blueprint lineage does not match the campaign case.",
                )
            session.flush()
            return project.id, run.id

    def _run_status(self, run_id: UUID) -> RunStatus:
        with self._session_factory() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None:
                raise RuntimeError("agentic Blueprint run disappeared")
            return run.status


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
