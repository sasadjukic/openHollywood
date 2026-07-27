"""Persisted direct-story execution for the benchmark's essential baseline."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid5

from open_hollywood_engine.evaluations import (
    BenchmarkCase,
    BenchmarkCaseExecutionError,
    BenchmarkOutput,
    BenchmarkPrompt,
    BenchmarkSystem,
    HardGate,
    canonical_sha256,
)
from open_hollywood_engine.models import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelDeployment,
    ModelGateway,
    ModelGatewayError,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ModelSettings,
)
from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session, sessionmaker

from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    InvocationStatus,
    Project,
    RunStatus,
    WorkflowEvent,
    WorkflowRun,
    agent_invocation_inputs,
)

DIRECT_STORY_WORKFLOW_NAME = "benchmark_direct_story"
DIRECT_STORY_GRAPH_VERSION = "1"
DIRECT_STORY_PROMPT_VERSION = "1"
DEFAULT_BASELINE_CALL_BUDGET = ModelCallBudget(
    max_input_tokens=8_192,
    max_output_tokens=7_000,
    max_cost_usd=Decimal("2.00"),
)


class DirectBaselineBenchmarkExecutor:
    """Run one direct-model story and persist exact prompt, call, and output lineage."""

    def __init__(
        self,
        *,
        campaign_id: UUID,
        session_factory: sessionmaker[Session],
        gateway: ModelGateway,
        call_budget: ModelCallBudget = DEFAULT_BASELINE_CALL_BUDGET,
    ) -> None:
        self._campaign_id = campaign_id
        self._session_factory = session_factory
        self._gateway = gateway
        self._call_budget = call_budget

    async def execute(
        self,
        case: BenchmarkCase,
        prompt: BenchmarkPrompt,
    ) -> BenchmarkOutput:
        """Execute one baseline case without representing it as an agentic graph."""
        if case.system is not BenchmarkSystem.SINGLE_MODEL_BASELINE:
            raise BenchmarkCaseExecutionError(
                "unsupported_benchmark_system",
                "The direct baseline executor cannot run agentic benchmark cases.",
            )
        target = case.baseline_model
        if target is None:
            raise RuntimeError("baseline benchmark case has no model target")
        if target.provider != self._gateway.provider:
            raise BenchmarkCaseExecutionError(
                "provider_not_configured",
                f"No runtime gateway is configured for provider {target.provider!r}.",
            )

        existing = self._load_succeeded_output(case)
        if existing is not None:
            return existing

        messages = _baseline_messages(prompt)
        run_id, invocation_id, prompt_version_id = self._start_attempt(
            case=case,
            prompt=prompt,
            messages=messages,
        )
        request = ModelRequest(
            model_identifier=target.model_identifier,
            messages=messages,
            budget=self._call_budget,
            invocation=InvocationContext(
                specialist_role="direct_story_baseline",
                prompt_template_version=DIRECT_STORY_PROMPT_VERSION,
                input_artifact_version_ids=(prompt_version_id,),
            ),
            settings=ModelSettings(
                temperature=0.8,
                top_p=0.95,
                seed=case.run_seed,
                thinking=False,
            ),
        )
        try:
            response = await self._gateway.generate(request)
            _validate_response(
                response=response,
                expected_provider=target.provider,
                expected_model=target.model_identifier,
                expected_deployment=target.deployment,
                budget=self._call_budget,
            )
            title, content = _parse_story(response.content, prompt)
            return self._complete_attempt(
                case=case,
                prompt=prompt,
                run_id=run_id,
                invocation_id=invocation_id,
                title=title,
                content=content,
                response=response,
            )
        except BenchmarkCaseExecutionError as error:
            self._fail_attempt(
                run_id=run_id,
                invocation_id=invocation_id,
                code=error.code,
                message=str(error),
            )
            raise
        except ModelGatewayError as error:
            self._fail_attempt(
                run_id=run_id,
                invocation_id=invocation_id,
                code=error.code.value,
                message=str(error),
            )
            raise BenchmarkCaseExecutionError(error.code.value, str(error)) from error
        except Exception:
            self._fail_attempt(
                run_id=run_id,
                invocation_id=invocation_id,
                code="unexpected_execution_failure",
                message="The direct baseline failed outside the provider boundary.",
            )
            raise

    def _start_attempt(
        self,
        *,
        case: BenchmarkCase,
        prompt: BenchmarkPrompt,
        messages: tuple[ModelMessage, ...],
    ) -> tuple[UUID, UUID, UUID]:
        run_id = uuid5(case.case_id, "benchmark-workflow")
        project_id = uuid5(case.case_id, "benchmark-project")
        with self._session_factory.begin() as session:
            project = session.get(Project, project_id)
            if project is None:
                project = Project(
                    id=project_id,
                    name=f"Benchmark {prompt.prompt_id} — baseline",
                    description="Synthetic frozen-corpus benchmark case.",
                    story_format="short_prose",
                    settings={
                        "benchmark_campaign_id": str(self._campaign_id),
                        "benchmark_case_id": str(case.case_id),
                        "benchmark_target": case.target_key,
                    },
                )
                session.add(project)
            run = session.get(WorkflowRun, run_id)
            if run is None:
                run = WorkflowRun(
                    id=run_id,
                    project=project,
                    workflow_name=DIRECT_STORY_WORKFLOW_NAME,
                    graph_version=DIRECT_STORY_GRAPH_VERSION,
                    input_state={
                        "benchmark_campaign_id": str(self._campaign_id),
                        "benchmark_case_id": str(case.case_id),
                        "prompt_id": prompt.prompt_id,
                        "prompt_version": prompt.version,
                        "run_seed": case.run_seed,
                    },
                    budget=_budget_data(self._call_budget),
                )
                session.add(run)
            _reconcile_interrupted_attempts(
                session=session,
                run=run,
                case_id=case.case_id,
            )
            run.status = RunStatus.RUNNING
            run.current_node = "generate"
            run.started_at = run.started_at or datetime.now(UTC)
            run.completed_at = None
            run.error_code = None
            run.error_message = None

            prompt_version = _get_or_create_prompt_version(
                session=session,
                project=project,
                case=case,
                prompt=prompt,
            )
            with session.no_autoflush:
                attempt_number = (
                    session.scalar(
                        select(func.count())
                        .select_from(AgentInvocation)
                        .where(AgentInvocation.workflow_run_id == run_id)
                    )
                    or 0
                ) + 1
            invocation_id = uuid5(case.case_id, f"baseline-invocation:{attempt_number}")
            target = case.baseline_model
            if target is None:
                raise RuntimeError("baseline benchmark case has no model target")
            invocation = AgentInvocation(
                id=invocation_id,
                workflow_run=run,
                specialist_role="direct_story_baseline",
                provider=target.provider,
                model_identifier=target.model_identifier,
                status=InvocationStatus.RUNNING,
                request_settings={
                    "deployment": target.deployment.value,
                    "prompt_template_version": DIRECT_STORY_PROMPT_VERSION,
                    "run_seed": case.run_seed,
                    "temperature": 0.8,
                    "top_p": 0.95,
                    "thinking": False,
                    "budget": _budget_data(self._call_budget),
                },
                prompt_sha256=_messages_sha256(messages),
                prompt_text="\n\n".join(message.content for message in messages),
            )
            session.add(invocation)
            session.add(
                WorkflowEvent(
                    workflow_run_id=run.id,
                    event_type="benchmark.case_started",
                    source="evaluation_harness",
                    payload={
                        "case_id": str(case.case_id),
                        "target": case.target_key,
                        "attempt": attempt_number,
                    },
                )
            )
            session.flush()
            session.execute(
                insert(agent_invocation_inputs),
                {
                    "agent_invocation_id": invocation.id,
                    "artifact_version_id": prompt_version.id,
                },
            )
            return run.id, invocation.id, prompt_version.id

    def _complete_attempt(
        self,
        *,
        case: BenchmarkCase,
        prompt: BenchmarkPrompt,
        run_id: UUID,
        invocation_id: UUID,
        title: str,
        content: str,
        response: ModelResponse,
    ) -> BenchmarkOutput:
        word_count = len(content.split())
        hard_gates = automatic_hard_gates(
            content=content,
            word_count=word_count,
            prompt=prompt,
            finish_reason=response.finish_reason,
        )
        content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        with self._session_factory.begin() as session:
            run = session.get(WorkflowRun, run_id)
            invocation = session.get(AgentInvocation, invocation_id)
            if run is None or invocation is None:
                raise RuntimeError("benchmark attempt disappeared before completion")
            invocation.status = InvocationStatus.SUCCEEDED
            invocation.input_tokens = response.usage.input_tokens
            invocation.output_tokens = response.usage.output_tokens
            invocation.estimated_cost_usd = response.estimated_cost_usd
            invocation.latency_ms = response.timing.total_ms
            invocation.request_settings = {
                **invocation.request_settings,
                "provider_response_model_identifier": (
                    response.provider_model_identifier or response.model_identifier
                ),
            }
            invocation.schema_validation_succeeded = True
            invocation.completed_at = datetime.now(UTC)

            story_artifact = session.scalar(
                select(Artifact).where(
                    Artifact.project_id == run.project_id,
                    Artifact.artifact_key == "benchmark-story",
                )
            )
            if story_artifact is None:
                story_artifact = Artifact(
                    id=uuid5(case.case_id, "benchmark-story-artifact"),
                    project_id=run.project_id,
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
                "hard_gates": {gate.value: value for gate, value in hard_gates.items()},
            }
            version = ArtifactVersion(
                id=uuid5(
                    case.case_id, f"benchmark-story-version:{len(story_artifact.versions) + 1}"
                ),
                artifact=story_artifact,
                created_by_invocation=invocation,
                version_number=len(story_artifact.versions) + 1,
                schema_version="benchmark-story-1",
                content=artifact_content,
                content_sha256=canonical_sha256(artifact_content),
                change_summary="Direct single-model baseline output.",
            )
            session.add(version)
            run.status = RunStatus.SUCCEEDED
            run.current_node = None
            run.completed_at = datetime.now(UTC)
            session.add(
                WorkflowEvent(
                    workflow_run_id=run.id,
                    event_type="benchmark.case_succeeded",
                    source="evaluation_harness",
                    payload={
                        "case_id": str(case.case_id),
                        "artifact_version_id": str(version.id),
                        "invocation_id": str(invocation.id),
                        "word_count": word_count,
                    },
                )
            )
            session.flush()
            return BenchmarkOutput(
                title=title,
                content=content,
                content_sha256=content_sha256,
                word_count=word_count,
                workflow_run_id=run.id,
                artifact_version_ids=(version.id,),
                invocation_ids=(invocation.id,),
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                latency_ms=response.timing.total_ms,
                estimated_cost_usd=format(response.estimated_cost_usd, ".6f"),
                hard_gates=hard_gates,
            )

    def _fail_attempt(
        self,
        *,
        run_id: UUID,
        invocation_id: UUID,
        code: str,
        message: str,
    ) -> None:
        safe_message = message.strip()[:2_000] or "Benchmark execution failed."
        with self._session_factory.begin() as session:
            run = session.get(WorkflowRun, run_id)
            invocation = session.get(AgentInvocation, invocation_id)
            if invocation is not None:
                invocation.status = InvocationStatus.FAILED
                invocation.completed_at = datetime.now(UTC)
                invocation.error_code = code
                invocation.error_message = safe_message
            if run is not None:
                run.status = RunStatus.FAILED
                run.current_node = None
                run.completed_at = datetime.now(UTC)
                run.error_code = code
                run.error_message = safe_message
                session.add(
                    WorkflowEvent(
                        workflow_run_id=run.id,
                        event_type="benchmark.case_failed",
                        source="evaluation_harness",
                        payload={"error_code": code},
                    )
                )

    def _load_succeeded_output(self, case: BenchmarkCase) -> BenchmarkOutput | None:
        run_id = uuid5(case.case_id, "benchmark-workflow")
        with self._session_factory() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None or run.status is not RunStatus.SUCCEEDED:
                return None
            version = session.scalar(
                select(ArtifactVersion)
                .join(Artifact)
                .where(
                    Artifact.project_id == run.project_id,
                    Artifact.artifact_key == "benchmark-story",
                )
                .order_by(ArtifactVersion.version_number.desc())
            )
            invocations = tuple(
                session.scalars(
                    select(AgentInvocation)
                    .where(
                        AgentInvocation.workflow_run_id == run.id,
                        AgentInvocation.status == InvocationStatus.SUCCEEDED,
                    )
                    .order_by(AgentInvocation.started_at, AgentInvocation.id)
                )
            )
            if version is None or not invocations:
                raise RuntimeError("succeeded benchmark run has incomplete persisted lineage")
            value = version.content
            gates = {HardGate(key): gate_value for key, gate_value in value["hard_gates"].items()}
            return BenchmarkOutput(
                title=str(value["title"]),
                content=str(value["content"]),
                content_sha256=str(value["content_sha256"]),
                word_count=int(value["word_count"]),
                workflow_run_id=run.id,
                artifact_version_ids=(version.id,),
                invocation_ids=tuple(invocation.id for invocation in invocations),
                input_tokens=sum(invocation.input_tokens for invocation in invocations),
                output_tokens=sum(invocation.output_tokens for invocation in invocations),
                latency_ms=sum(invocation.latency_ms or 0 for invocation in invocations),
                estimated_cost_usd=format(
                    sum(
                        (invocation.estimated_cost_usd for invocation in invocations),
                        start=Decimal("0"),
                    ),
                    "f",
                ),
                hard_gates=gates,
            )


def _get_or_create_prompt_version(
    *,
    session: Session,
    project: Project,
    case: BenchmarkCase,
    prompt: BenchmarkPrompt,
) -> ArtifactVersion:
    version_id = uuid5(case.case_id, "benchmark-prompt-version")
    existing = session.get(ArtifactVersion, version_id)
    if existing is not None:
        return existing
    artifact = Artifact(
        id=uuid5(case.case_id, "benchmark-prompt-artifact"),
        project=project,
        artifact_key="benchmark-prompt",
        artifact_type="benchmark_prompt",
        title=f"{prompt.prompt_id} v{prompt.version}",
        status=ArtifactStatus.APPROVED,
    )
    content = prompt.model_dump(mode="json")
    version = ArtifactVersion(
        id=version_id,
        artifact=artifact,
        version_number=1,
        schema_version="benchmark-prompt-1",
        content=content,
        content_sha256=canonical_sha256(content),
        change_summary="Frozen benchmark prompt input.",
    )
    session.add_all((artifact, version))
    return version


def _baseline_messages(prompt: BenchmarkPrompt) -> tuple[ModelMessage, ...]:
    required = "\n".join(f"- {value}" for value in prompt.required_elements)
    forbidden = "\n".join(f"- {value}" for value in prompt.forbidden_shortcuts)
    system = (
        "Write one complete, polished short prose story. Return only a title on "
        "the first line in the form 'Title: ...', followed by the story. Do not "
        "include planning notes, critique, explanations, placeholders, or Markdown "
        "code fences. End deliberately rather than at a token boundary."
    )
    user = (
        f"Premise:\n{prompt.prompt}\n\n"
        f"Length: {prompt.target_word_count.minimum}–{prompt.target_word_count.maximum} words.\n"
        f"Genre signals: {', '.join(prompt.genres)}.\n"
        f"Maturity: {prompt.intended_maturity.value}.\n\n"
        f"Required elements:\n{required}\n\n"
        f"Forbidden shortcuts:\n{forbidden}"
    )
    return (
        ModelMessage(role=MessageRole.SYSTEM, content=system),
        ModelMessage(role=MessageRole.USER, content=user),
    )


def _parse_story(response_content: str, prompt: BenchmarkPrompt) -> tuple[str, str]:
    normalized = response_content.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        raise BenchmarkCaseExecutionError(
            "empty_baseline_output",
            "The direct baseline returned an empty story.",
        )
    first_line, separator, remainder = normalized.partition("\n")
    candidate = first_line.strip().removeprefix("#").strip()
    if candidate.casefold().startswith("title:"):
        title = candidate.split(":", maxsplit=1)[1].strip()
        content = remainder.strip() if separator else ""
    elif candidate.startswith("**") and candidate.endswith("**"):
        title = candidate.strip("*").strip()
        content = remainder.strip() if separator else ""
    else:
        title = f"Benchmark Story {prompt.prompt_id}"
        content = normalized
    if not title or not content:
        raise BenchmarkCaseExecutionError(
            "invalid_baseline_document",
            "The direct baseline did not return both a title and story body.",
        )
    return title[:200], content


def automatic_hard_gates(
    *,
    content: str,
    word_count: int,
    prompt: BenchmarkPrompt,
    finish_reason: str | None,
) -> dict[HardGate, bool | None]:
    target_valid = (
        prompt.target_word_count.minimum <= word_count <= prompt.target_word_count.maximum
    )
    ending_not_truncated = finish_reason == "stop" and content.rstrip().endswith(
        (".", "!", "?", "”", '"', "'")
    )
    folded = content.casefold()
    no_placeholders = not any(
        marker in folded
        for marker in ("[todo", "<todo", "placeholder text", "as an ai language model")
    )
    no_critic_notes = not any(
        marker in folded for marker in ("critic note:", "revision note:", "editor note:")
    )
    return {
        HardGate.COMPLETE: target_valid and ending_not_truncated,
        HardGate.CENTRAL_FACTS_CONSISTENT: None,
        HardGate.MANDATORY_REQUIREMENTS_PRESENT: None,
        HardGate.NO_PLACEHOLDERS_OR_MODEL_COMMENTARY: no_placeholders,
        HardGate.TARGET_FORMAT_VALID: target_valid,
        HardGate.ENDING_NOT_TRUNCATED: ending_not_truncated,
        HardGate.NO_CRITIC_NOTES_IN_PROSE: no_critic_notes,
    }


def _messages_sha256(messages: tuple[ModelMessage, ...]) -> str:
    value = "\n".join(f"{message.role.value}\0{message.content}" for message in messages)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _validate_response(
    *,
    response: ModelResponse,
    expected_provider: str,
    expected_model: str,
    expected_deployment: ModelDeployment,
    budget: ModelCallBudget,
) -> None:
    if (
        response.provider != expected_provider
        or response.model_identifier != expected_model
        or response.deployment is not expected_deployment
    ):
        raise BenchmarkCaseExecutionError(
            "model_target_mismatch",
            "The provider response does not match the frozen campaign model target.",
        )
    if (
        response.usage.input_tokens > budget.max_input_tokens
        or response.usage.output_tokens > budget.max_output_tokens
        or response.estimated_cost_usd > budget.max_cost_usd
    ):
        raise BenchmarkCaseExecutionError(
            "budget_exceeded",
            "The provider response exceeded the frozen direct-story call budget.",
        )


def _reconcile_interrupted_attempts(
    *,
    session: Session,
    run: WorkflowRun,
    case_id: UUID,
) -> None:
    interrupted = tuple(
        session.scalars(
            select(AgentInvocation).where(
                AgentInvocation.workflow_run_id == run.id,
                AgentInvocation.status == InvocationStatus.RUNNING,
            )
        )
    )
    if not interrupted:
        return
    completed_at = datetime.now(UTC)
    for invocation in interrupted:
        invocation.status = InvocationStatus.FAILED
        invocation.completed_at = completed_at
        invocation.error_code = "interrupted_execution"
        invocation.error_message = (
            "A previous benchmark process ended before recording a terminal result."
        )
    run.status = RunStatus.FAILED
    run.current_node = None
    run.completed_at = completed_at
    run.error_code = "interrupted_execution"
    run.error_message = "A previous benchmark attempt was interrupted."
    session.add(
        WorkflowEvent(
            workflow_run_id=run.id,
            event_type="benchmark.case_interrupted",
            source="evaluation_harness",
            payload={
                "case_id": str(case_id),
                "invocation_count": len(interrupted),
            },
        )
    )


def _budget_data(budget: ModelCallBudget) -> dict[str, int | str]:
    return {
        "max_input_tokens": budget.max_input_tokens,
        "max_output_tokens": budget.max_output_tokens,
        "max_cost_usd": format(budget.max_cost_usd, "f"),
    }
