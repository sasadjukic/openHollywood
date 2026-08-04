"""Profile-routed model execution and immutable outputs for Blueprint specialists."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Mapping
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Self, cast
from uuid import UUID, uuid4

from open_hollywood_engine.artifacts import (
    ArtifactKind,
    Beat,
    Character,
    CreativeBrief,
    Critique,
    Location,
    MaturityMode,
    Premise,
    Relationship,
    ScenePlan,
    StoryBlueprint,
    StoryFormat,
    WorldRule,
)
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.models import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelDeployment,
    ModelGateway,
    ModelGatewayError,
    ModelMessage,
    ModelProfileConfiguration,
    ModelRequest,
    ModelResponse,
    ModelSelection,
    ModelSettings,
)
from open_hollywood_engine.workflows import (
    DEFAULT_MAX_GRAPH_STEPS,
    STORY_BLUEPRINT_GRAPH_VERSION,
    ArtifactReference,
    BlueprintNode,
    BlueprintNodeExecutor,
    BlueprintNodeResult,
    BlueprintNodeTask,
    BlueprintWorkflowError,
    RetryableSpecialistError,
    RunBudget,
)
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from sqlalchemy import insert, select
from sqlalchemy.orm import Session, joinedload, sessionmaker

from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    HumanDecision,
    InvocationStatus,
    Message,
    WorkflowRun,
    agent_invocation_inputs,
)
from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services.structured_output import normalize_json_document

BLUEPRINT_MODEL_PROMPT_VERSION = "9"


class _SpecialistContractError(ValueError):
    """A schema-valid specialist result changed authoritative inputs."""


class _StructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class _BriefOutput(_StructuredOutput):
    interpretation: str = Field(min_length=1)
    assumptions: tuple[str, ...] = ()
    tone: tuple[str, ...] = Field(min_length=1)
    intended_effect: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    target_word_count: int = Field(ge=2500, le=5000)
    target_scene_count: int = Field(ge=3, le=8)
    target_significant_character_count: int = Field(ge=2, le=5)
    central_dramatic_question: str = Field(min_length=1)
    themes: tuple[str, ...] = Field(min_length=1)
    style_constraints: tuple[str, ...] = ()
    authorized_ambiguities: tuple[str, ...] = ()


class _WorldOutput(_StructuredOutput):
    locations: tuple[Location, ...] = Field(min_length=1)
    world_rules: tuple[WorldRule, ...] = Field(min_length=1)


class _CharacterOutput(_StructuredOutput):
    characters: tuple[Character, ...] = Field(min_length=2, max_length=5)
    relationships: tuple[Relationship, ...] = Field(min_length=1)


class _IntegrationOutput(_StructuredOutput):
    world_summary: str = Field(
        min_length=1,
        description="A compact world synthesis of at most 250 words.",
    )
    beats: tuple[Beat, ...] = Field(
        min_length=1,
        max_length=16,
        description="A compact causal sequence with no more than two beats per scene.",
    )
    scene_plans: tuple[ScenePlan, ...] = Field(
        min_length=3,
        max_length=8,
        description="The exact requested scene count using concise narrative text fields.",
    )

    @model_validator(mode="after")
    def keep_plan_bounded(self) -> Self:
        if len(self.beats) > len(self.scene_plans) * 2:
            raise ValueError("integration cannot create more than two beats per scene")
        if len(self.world_summary.split()) > 250:
            raise ValueError("integration world summary cannot exceed 250 words")
        return self


type _BlueprintOutput = (
    CreativeBrief | Premise | _WorldOutput | _CharacterOutput | StoryBlueprint | Critique
)

_OUTPUT_MODELS: Mapping[BlueprintNode, type[BaseModel]] = {
    BlueprintNode.BRIEF: _BriefOutput,
    BlueprintNode.PREMISE: Premise,
    BlueprintNode.WORLD_SPECIALIST: _WorldOutput,
    BlueprintNode.CHARACTER_SPECIALIST: _CharacterOutput,
    BlueprintNode.INTEGRATION: _IntegrationOutput,
    BlueprintNode.EVALUATION: Critique,
}

_NODE_INSTRUCTIONS: Mapping[BlueprintNode, str] = {
    BlueprintNode.BRIEF: (
        "Generate only the creative choices needed to complete a short-prose Creative "
        "Brief. Infer missing choices explicitly. The application deterministically "
        "attaches every authoritative value identified by output_invariants."
    ),
    BlueprintNode.PREMISE: (
        "Develop the Creative Brief into a causally specific premise, thematic "
        "thesis, complete arc, deliberate ending, and controlled voice guide."
    ),
    BlueprintNode.WORLD_SPECIALIST: (
        "Design the smallest dramatically sufficient set of locations and world "
        "rules. Every identifier must be stable snake_case. Because this role runs "
        "in parallel with Character, leave all character-reference arrays empty."
    ),
    BlueprintNode.CHARACTER_SPECIALIST: (
        "Create exactly the significant-character count required by the brief and "
        "at least one valid relationship. Give every character a distinct motive, "
        "contradiction, arc, and dialogue voice."
    ),
    BlueprintNode.INTEGRATION: (
        "Generate only a world summary, causal beat sequence, and the exact requested "
        "number of contiguous scene plans. Reference the supplied character, location, "
        "world-rule, and premise identifiers without repeating or rewriting those artifacts. "
        "Reach the declared ending. Be compact: keep the world summary under 250 words, "
        "create no more than two beats per scene, and use one concise sentence in each "
        "narrative text field."
    ),
    BlueprintNode.EVALUATION: (
        "Evaluate the exact Story Blueprint against causal structure, character depth, "
        "dialogue potential, originality, voice, emotional impact, pacing, continuity, "
        "prompt constraints, completeness, and format. Target the supplied blueprint version."
    ),
}


class ProfileRoutedBlueprintNodeExecutor(BlueprintNodeExecutor):
    """Execute profile-routed Blueprint roles through one provider-neutral gateway."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        gateway: ModelGateway,
    ) -> None:
        self._session_factory = session_factory
        self._gateway = gateway

    async def execute(self, task: BlueprintNodeTask) -> BlueprintNodeResult:
        """Run, validate, and persist one idempotent specialist task."""
        try:
            output_model = _OUTPUT_MODELS[task.node]
        except KeyError as error:
            raise BlueprintWorkflowError(
                f"node {task.node.value} is not a model-backed Blueprint specialist"
            ) from error

        execution = await asyncio.to_thread(self._load_execution, task)
        existing = await asyncio.to_thread(
            self._replay,
            execution.task_fingerprint,
        )
        if existing is not None:
            return existing
        response_schema = _response_schema(
            node=task.node,
            output_model=output_model,
            execution=execution,
        )
        messages = _messages(
            task=task,
            instruction=_NODE_INSTRUCTIONS[task.node],
            premise=execution.premise,
            inputs=execution.inputs,
            revision_instruction=execution.revision_instruction,
            constraints=execution.constraints,
            schema=response_schema,
            retry_context=(
                {
                    "attempt_number": execution.attempt_number,
                    "previous_failure": execution.previous_failure,
                }
                if execution.previous_failure is not None
                else None
            ),
        )
        invocation_id = await asyncio.to_thread(
            self._start_invocation,
            task=task,
            execution=execution,
            messages=messages,
            schema_enforced=execution.selection.deployment is ModelDeployment.LOCAL,
        )
        request = ModelRequest(
            model_identifier=execution.selection.model_identifier,
            messages=messages,
            budget=execution.call_budget,
            invocation=InvocationContext(
                specialist_role=task.specialist_role,
                prompt_template_version=BLUEPRINT_MODEL_PROMPT_VERSION,
                input_artifact_version_ids=execution.input_version_ids,
                model_profile_id=execution.profile_id,
            ),
            settings=ModelSettings(
                temperature=_temperature(task.node),
                top_p=0.95,
                seed=execution.run_seed,
                thinking=False,
            ),
            response_schema=(
                response_schema if execution.selection.deployment is ModelDeployment.LOCAL else None
            ),
        )
        try:
            response = await self._gateway.generate(request)
            _require_matching_response(response, execution)
            parsed_output = output_model.model_validate_json(
                normalize_json_document(response.content)
            )
            output = _materialize_output(task.node, parsed_output, execution)
            _validate_output(task, output, execution)
            references = await asyncio.to_thread(
                self._complete_invocation,
                invocation_id=invocation_id,
                task=task,
                execution=execution,
                response=response,
                outputs=_artifact_outputs(task.node, output),
            )
        except asyncio.CancelledError:
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                code="cancelled_execution",
                message="The Blueprint specialist call was cancelled before completion.",
                schema_valid=None,
            )
            raise
        except ModelGatewayError as error:
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                code=error.code.value,
                message=str(error),
                schema_valid=None,
            )
            if error.retryable:
                raise RetryableSpecialistError(str(error)) from error
            raise BlueprintWorkflowError(str(error)) from error
        except BlueprintWorkflowError as error:
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                code="specialist_contract_failed",
                message=str(error),
                schema_valid=False,
                response=response,
            )
            raise
        except _SpecialistContractError as error:
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                code="artifact_contract_failed",
                message=str(error),
                schema_valid=True,
                response=response,
            )
            raise RetryableSpecialistError(
                "specialist output changed authoritative artifact inputs"
            ) from error
        except (ValueError, json.JSONDecodeError) as error:
            failure_message = _structured_failure_message(error, response)
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                code="schema_validation_failed",
                message=failure_message,
                schema_valid=False,
                response=response,
            )
            raise RetryableSpecialistError(
                "specialist returned invalid structured output"
            ) from error
        return BlueprintNodeResult(artifacts=references)

    def _load_execution(self, task: BlueprintNodeTask) -> _Execution:
        with self._session_factory() as session:
            run = session.get(WorkflowRun, task.workflow_run_id)
            if run is None:
                raise BlueprintWorkflowError("Blueprint workflow run does not exist")
            profile_id = _uuid_input(run.input_state, "model_profile_id")
            configuration = ModelProfileConfiguration.from_data(
                _mapping_input(run.input_state, "model_profile_configuration")
            )
            configuration_sha256 = canonical_sha256(configuration.to_data())
            if configuration_sha256 != _text_input(
                run.input_state,
                "model_profile_configuration_sha256",
            ):
                raise BlueprintWorkflowError(
                    "frozen model-profile configuration digest does not match"
                )
            if not configuration.is_complete:
                raise BlueprintWorkflowError("Blueprint model profile is incomplete")
            selection = configuration.selection_for(task.specialist_role)
            if selection.provider != self._gateway.provider:
                raise BlueprintWorkflowError(
                    f"no runtime gateway is configured for provider {selection.provider!r}"
                )
            budget = RunBudget.from_data(
                run.budget,
                default_max_graph_steps=DEFAULT_MAX_GRAPH_STEPS,
            )
            input_ids = tuple(reference.version_id for reference in task.input_artifacts)
            prompt_version_id = _optional_uuid_input(
                run.input_state,
                "benchmark_prompt_version_id",
            )
            invocation_input_ids = (
                *((prompt_version_id,) if prompt_version_id is not None else ()),
                *input_ids,
            )
            inputs = _load_artifact_inputs(session, task.input_artifacts)
            premise = _premise_for_run(session, run)
            run_seed = _integer_input(run.input_state, "run_seed", default=0)
            constraints = dict(
                _optional_mapping_input(
                    run.input_state,
                    "benchmark_constraints",
                )
            )
            revision_instruction = None
            if task.human_decision_id is not None:
                decision = session.get(HumanDecision, task.human_decision_id)
                if decision is None:
                    raise BlueprintWorkflowError("Blueprint human decision does not exist")
                revision_instruction = decision.instruction
            fingerprint = canonical_sha256(
                {
                    "workflow_run_id": str(task.workflow_run_id),
                    "node": task.node.value,
                    "specialist_role": task.specialist_role,
                    "input_artifact_version_ids": [str(value) for value in invocation_input_ids],
                    "human_decision_id": (
                        str(task.human_decision_id) if task.human_decision_id is not None else None
                    ),
                    "run_control_id": (
                        str(task.run_control_id) if task.run_control_id is not None else None
                    ),
                    "reviewed_artifact_version_ids": [
                        str(reference.version_id) for reference in task.reviewed_artifacts
                    ],
                    "prompt_template_version": BLUEPRINT_MODEL_PROMPT_VERSION,
                    "model_profile_configuration": configuration.to_data(),
                    "run_seed": run_seed,
                }
            )
            attempt_number, previous_failure = _retry_context(
                session,
                workflow_run_id=run.id,
                specialist_role=task.specialist_role,
                task_fingerprint=fingerprint,
            )
            return _Execution(
                workflow_run_id=run.id,
                project_id=run.project_id,
                profile_id=profile_id,
                configuration=configuration,
                configuration_sha256=configuration_sha256,
                selection=selection,
                premise=premise,
                inputs=inputs,
                revision_instruction=revision_instruction,
                constraints=constraints,
                input_version_ids=invocation_input_ids,
                call_budget=ModelCallBudget(
                    max_input_tokens=budget.per_call_input_tokens,
                    max_output_tokens=budget.per_call_output_tokens,
                    max_cost_usd=budget.per_call_cost_usd,
                ),
                run_seed=run_seed,
                task_fingerprint=fingerprint,
                attempt_number=attempt_number,
                previous_failure=previous_failure,
            )

    def _replay(self, task_fingerprint: str) -> BlueprintNodeResult | None:
        with self._session_factory() as session:
            invocations = session.scalars(
                select(AgentInvocation)
                .where(AgentInvocation.status == InvocationStatus.SUCCEEDED)
                .options(
                    joinedload(AgentInvocation.output_versions).joinedload(ArtifactVersion.artifact)
                )
            ).unique()
            invocation = next(
                (
                    candidate
                    for candidate in invocations
                    if candidate.request_settings.get("task_fingerprint") == task_fingerprint
                ),
                None,
            )
            if invocation is None:
                return None
            references = tuple(
                _reference(version)
                for version in sorted(
                    invocation.output_versions,
                    key=lambda item: (item.artifact.artifact_key, item.version_number),
                )
            )
            if not references:
                raise BlueprintWorkflowError(
                    "succeeded specialist invocation has no artifact outputs"
                )
            return BlueprintNodeResult(artifacts=references)

    def _start_invocation(
        self,
        *,
        task: BlueprintNodeTask,
        execution: _Execution,
        messages: tuple[ModelMessage, ...],
        schema_enforced: bool,
    ) -> UUID:
        invocation_id = uuid4()
        with self._session_factory.begin() as session:
            invocation = AgentInvocation(
                id=invocation_id,
                workflow_run_id=execution.workflow_run_id,
                model_profile_id=execution.profile_id,
                specialist_role=task.specialist_role,
                provider=execution.selection.provider,
                model_identifier=execution.selection.model_identifier,
                status=InvocationStatus.RUNNING,
                retry_count=execution.attempt_number - 1,
                request_settings={
                    "deployment": execution.selection.deployment.value,
                    "graph_version": STORY_BLUEPRINT_GRAPH_VERSION,
                    "model_profile_configuration_sha256": (execution.configuration_sha256),
                    "node": task.node.value,
                    "prompt_template_version": BLUEPRINT_MODEL_PROMPT_VERSION,
                    "run_seed": execution.run_seed,
                    "schema_enforced": schema_enforced,
                    "task_fingerprint": execution.task_fingerprint,
                    "attempt_number": execution.attempt_number,
                    "temperature": _temperature(task.node),
                    "top_p": 0.95,
                    "thinking": False,
                    "budget": {
                        "max_input_tokens": execution.call_budget.max_input_tokens,
                        "max_output_tokens": execution.call_budget.max_output_tokens,
                        "max_cost_usd": format(
                            execution.call_budget.max_cost_usd,
                            "f",
                        ),
                    },
                },
                prompt_sha256=_messages_sha256(messages),
                prompt_text="\n\n".join(message.content for message in messages),
            )
            session.add(invocation)
            session.flush()
            if execution.input_version_ids:
                session.execute(
                    insert(agent_invocation_inputs),
                    [
                        {
                            "agent_invocation_id": invocation_id,
                            "artifact_version_id": version_id,
                        }
                        for version_id in execution.input_version_ids
                    ],
                )
        return invocation_id

    def _complete_invocation(
        self,
        *,
        invocation_id: UUID,
        task: BlueprintNodeTask,
        execution: _Execution,
        response: ModelResponse,
        outputs: tuple[tuple[ArtifactKind, BaseModel], ...],
    ) -> tuple[ArtifactReference, ...]:
        with self._session_factory.begin() as session:
            invocation = session.get(AgentInvocation, invocation_id)
            if invocation is None:
                raise BlueprintWorkflowError("specialist invocation disappeared")
            references = tuple(
                _persist_output(
                    session=session,
                    invocation=invocation,
                    project_id=execution.project_id,
                    task=task,
                    kind=kind,
                    output=output,
                )
                for kind, output in outputs
            )
            invocation.status = InvocationStatus.SUCCEEDED
            invocation.input_tokens = response.usage.input_tokens
            invocation.output_tokens = response.usage.output_tokens
            invocation.estimated_cost_usd = response.estimated_cost_usd
            invocation.latency_ms = response.timing.total_ms
            _apply_response_metadata(invocation, response)
            invocation.schema_validation_succeeded = True
            invocation.completed_at = datetime.now(UTC)
            return references

    def _fail_invocation(
        self,
        invocation_id: UUID,
        *,
        code: str,
        message: str,
        schema_valid: bool | None,
        response: ModelResponse | None = None,
    ) -> None:
        safe_message = active_secret_guard().redact_text(message)[:2_000]
        with self._session_factory.begin() as session:
            invocation = session.get(AgentInvocation, invocation_id)
            if invocation is None:
                return
            invocation.status = InvocationStatus.FAILED
            invocation.schema_validation_succeeded = schema_valid
            if response is not None:
                invocation.input_tokens = response.usage.input_tokens
                invocation.output_tokens = response.usage.output_tokens
                invocation.estimated_cost_usd = response.estimated_cost_usd
                invocation.latency_ms = response.timing.total_ms
                _apply_response_metadata(invocation, response)
            invocation.completed_at = datetime.now(UTC)
            invocation.error_code = code
            invocation.error_message = safe_message


def _apply_response_metadata(
    invocation: AgentInvocation,
    response: ModelResponse,
) -> None:
    invocation.request_settings = {
        **invocation.request_settings,
        "provider_response_model_identifier": (
            response.provider_model_identifier or response.model_identifier
        ),
        "provider_finish_reason": response.finish_reason,
        "provider_response_content_sha256": hashlib.sha256(
            response.content.encode("utf-8")
        ).hexdigest(),
        "provider_response_content_length": len(response.content),
    }


def _retry_context(
    session: Session,
    *,
    workflow_run_id: UUID,
    specialist_role: str,
    task_fingerprint: str,
) -> tuple[int, dict[str, object] | None]:
    candidates = session.scalars(
        select(AgentInvocation)
        .where(
            AgentInvocation.workflow_run_id == workflow_run_id,
            AgentInvocation.specialist_role == specialist_role,
            AgentInvocation.status == InvocationStatus.FAILED,
        )
        .order_by(AgentInvocation.started_at, AgentInvocation.id)
    ).all()
    failures = tuple(
        invocation
        for invocation in candidates
        if invocation.request_settings.get("task_fingerprint") == task_fingerprint
        and invocation.request_settings.get("prompt_template_version")
        == BLUEPRINT_MODEL_PROMPT_VERSION
    )
    if not failures:
        return 1, None
    latest = failures[-1]
    return len(failures) + 1, {
        "error_code": latest.error_code or "unknown",
        "message": latest.error_message or "No structural diagnostic was recorded.",
        "provider_finish_reason": latest.request_settings.get("provider_finish_reason"),
        "provider_response_length": latest.request_settings.get("provider_response_content_length"),
    }


def _structured_failure_message(
    error: ValueError,
    response: ModelResponse,
) -> str:
    locations: list[str] = []
    if isinstance(error, ValidationError):
        for item in error.errors(
            include_url=False,
            include_context=False,
            include_input=False,
        )[:12]:
            location = ".".join(str(value) for value in item["loc"]) or "$"
            locations.append(f"{location}:{item['type']}:{item['msg']}")
    else:
        locations.append(f"$:{type(error).__name__}")
    joined = ", ".join(locations)
    return (
        "Structured output validation failed "
        f"(provider_finish_reason={response.finish_reason}): {joined}."
    )


class _Execution:
    def __init__(
        self,
        *,
        workflow_run_id: UUID,
        project_id: UUID,
        profile_id: UUID,
        configuration: ModelProfileConfiguration,
        configuration_sha256: str,
        selection: ModelSelection,
        premise: str,
        inputs: tuple[dict[str, Any], ...],
        revision_instruction: str | None,
        constraints: dict[str, object],
        input_version_ids: tuple[UUID, ...],
        call_budget: ModelCallBudget,
        run_seed: int,
        task_fingerprint: str,
        attempt_number: int,
        previous_failure: dict[str, object] | None,
    ) -> None:
        self.workflow_run_id = workflow_run_id
        self.project_id = project_id
        self.profile_id = profile_id
        self.configuration = configuration
        self.configuration_sha256 = configuration_sha256
        self.selection = selection
        self.premise = premise
        self.inputs = inputs
        self.revision_instruction = revision_instruction
        self.constraints = constraints
        self.input_version_ids = input_version_ids
        self.call_budget = call_budget
        self.run_seed = run_seed
        self.task_fingerprint = task_fingerprint
        self.attempt_number = attempt_number
        self.previous_failure = previous_failure


def _response_schema(
    *,
    node: BlueprintNode,
    output_model: type[BaseModel],
    execution: _Execution,
) -> dict[str, Any]:
    schema = deepcopy(output_model.model_json_schema())
    if node is not BlueprintNode.INTEGRATION:
        return schema
    brief = CreativeBrief.model_validate(
        _single_input(execution.inputs, ArtifactKind.CREATIVE_BRIEF)
    )
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise BlueprintWorkflowError("integration schema properties are missing")
    scene_plans = properties.get("scene_plans")
    beats = properties.get("beats")
    if not isinstance(scene_plans, dict) or not isinstance(beats, dict):
        raise BlueprintWorkflowError("integration collection schemas are missing")
    scene_plans["minItems"] = brief.target_scene_count
    scene_plans["maxItems"] = brief.target_scene_count
    beats["maxItems"] = brief.target_scene_count * 2
    return schema


def _messages(
    *,
    task: BlueprintNodeTask,
    instruction: str,
    premise: str,
    inputs: tuple[dict[str, Any], ...],
    revision_instruction: str | None,
    constraints: dict[str, object],
    schema: dict[str, Any],
    retry_context: dict[str, object] | None,
) -> tuple[ModelMessage, ...]:
    system = (
        "You are a registered Open Hollywood Story Blueprint specialist. "
        f"{instruction} Return only one JSON value conforming exactly to the supplied "
        "schema. Do not include Markdown, commentary, hidden reasoning, or undeclared fields. "
        "If retry_context is present, correct every reported structural error and make the "
        "replacement more concise rather than expanding it."
    )
    payload: dict[str, object] = {
        "assignment": {
            "node": task.node.value,
            "specialist_role": task.specialist_role,
            "human_revision_instruction": revision_instruction,
        },
        "frozen_user_premise": premise,
        "frozen_benchmark_constraints": constraints,
        "input_artifacts": inputs,
        "output_invariants": _output_invariants(
            node=task.node,
            premise=premise,
            constraints=constraints,
            inputs=inputs,
        ),
        "output_schema": schema,
    }
    if retry_context is not None:
        payload["retry_context"] = retry_context
    user = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return (
        ModelMessage(role=MessageRole.SYSTEM, content=system),
        ModelMessage(role=MessageRole.USER, content=user),
    )


def _output_invariants(
    *,
    node: BlueprintNode,
    premise: str,
    constraints: dict[str, object],
    inputs: tuple[dict[str, Any], ...],
) -> dict[str, object]:
    if node is BlueprintNode.BRIEF:
        return {
            "application_assembles_authoritative_fields": [
                "original_premise",
                "story_format",
                "genres",
                "maturity",
                "required_elements",
                "forbidden_elements",
            ],
            "generate_only": list(_BriefOutput.model_fields),
            "target_word_count_range": constraints.get("target_word_count"),
        }
    if node is BlueprintNode.CHARACTER_SPECIALIST:
        return {
            "creative_brief_target_significant_character_count": (
                _single_input(inputs, ArtifactKind.CREATIVE_BRIEF).get(
                    "target_significant_character_count"
                )
            ),
            "relationship_character_ids_must_resolve": True,
        }
    if node is BlueprintNode.WORLD_SPECIALIST:
        return {
            "location_associated_character_ids_must_be_empty": True,
            "world_rule_relevant_character_ids_must_be_empty": True,
        }
    if node is BlueprintNode.INTEGRATION:
        brief = _single_input(inputs, ArtifactKind.CREATIVE_BRIEF)
        return {
            "application_assembles_authoritative_input_artifacts": True,
            "generate_only": ["world_summary", "beats", "scene_plans"],
            "allowed_character_ids": _input_identifiers(
                inputs,
                ArtifactKind.CHARACTER,
            ),
            "allowed_location_ids": _input_identifiers(
                inputs,
                ArtifactKind.LOCATION,
            ),
            "required_scene_count": brief.get("target_scene_count"),
            "maximum_beat_count": (
                brief["target_scene_count"] * 2
                if isinstance(brief.get("target_scene_count"), int)
                else None
            ),
            "maximum_world_summary_words": 250,
            "every_beat_id_must_appear_in_a_scene_plan": True,
        }
    if node is BlueprintNode.EVALUATION:
        blueprint = next(
            (
                value
                for value in inputs
                if value["artifact_kind"] == ArtifactKind.STORY_BLUEPRINT.value
            ),
            None,
        )
        return {
            "target_artifact_kind": ArtifactKind.STORY_BLUEPRINT.value,
            "target_artifact_key": (blueprint["artifact_key"] if blueprint is not None else None),
            "target_artifact_version_id": (
                blueprint["artifact_version_id"] if blueprint is not None else None
            ),
        }
    return {}


def _materialize_output(
    node: BlueprintNode,
    output: BaseModel,
    execution: _Execution,
) -> _BlueprintOutput:
    if node is BlueprintNode.BRIEF:
        if not isinstance(output, _BriefOutput):
            raise BlueprintWorkflowError("brief returned an incompatible output")
        maturity_value = execution.constraints.get("intended_maturity")
        if not isinstance(maturity_value, str):
            raise BlueprintWorkflowError("benchmark maturity constraint is missing or invalid")
        try:
            maturity = MaturityMode(maturity_value)
        except ValueError as error:
            raise BlueprintWorkflowError(
                "benchmark maturity constraint is missing or invalid"
            ) from error
        try:
            return CreativeBrief(
                original_premise=execution.premise,
                story_format=StoryFormat.SHORT_PROSE,
                genres=_constraint_texts(execution.constraints, "genres"),
                maturity=maturity,
                required_elements=_constraint_texts(
                    execution.constraints,
                    "required_elements",
                    allow_empty=True,
                ),
                forbidden_elements=_constraint_texts(
                    execution.constraints,
                    "forbidden_shortcuts",
                    allow_empty=True,
                ),
                **output.model_dump(),
            )
        except ValidationError as error:
            first = error.errors(include_url=False)[0]
            location = ".".join(str(value) for value in first["loc"]) or "creative_brief"
            raise _SpecialistContractError(
                f"Materialized Creative Brief violates {location}: {first['msg']}"
            ) from error
    if node is not BlueprintNode.INTEGRATION:
        return cast(_BlueprintOutput, output)
    if not isinstance(output, _IntegrationOutput):
        raise BlueprintWorkflowError("integration returned an incompatible output")
    brief = CreativeBrief.model_validate(
        _single_input(execution.inputs, ArtifactKind.CREATIVE_BRIEF)
    )
    premise = Premise.model_validate(_single_input(execution.inputs, ArtifactKind.PREMISE))
    try:
        return StoryBlueprint(
            creative_brief=brief,
            logline=premise.logline,
            thematic_thesis=premise.thematic_thesis,
            world_summary=output.world_summary,
            characters=tuple(
                Character.model_validate(value["content"])
                for value in execution.inputs
                if value["artifact_kind"] == ArtifactKind.CHARACTER.value
            ),
            relationships=tuple(
                Relationship.model_validate(value["content"])
                for value in execution.inputs
                if value["artifact_kind"] == ArtifactKind.RELATIONSHIP.value
            ),
            locations=tuple(
                Location.model_validate(value["content"])
                for value in execution.inputs
                if value["artifact_kind"] == ArtifactKind.LOCATION.value
            ),
            world_rules=tuple(
                WorldRule.model_validate(value["content"])
                for value in execution.inputs
                if value["artifact_kind"] == ArtifactKind.WORLD_RULE.value
            ),
            central_conflict=premise.central_conflict,
            story_arc=premise.story_arc,
            beats=output.beats,
            scene_plans=output.scene_plans,
            proposed_ending=premise.proposed_ending,
            voice_and_style_guide=premise.voice_and_style_guide,
            potential_risks=premise.potential_risks,
            unresolved_decisions=premise.unresolved_decisions,
        )
    except ValidationError as error:
        first = error.errors(include_url=False)[0]
        location = ".".join(str(value) for value in first["loc"]) or "story_blueprint"
        raise _SpecialistContractError(
            f"Integrated Story Blueprint violates {location}: {first['msg']}"
        ) from error


def _input_identifiers(
    inputs: tuple[dict[str, Any], ...],
    kind: ArtifactKind,
) -> list[str]:
    return sorted(
        str(value["content"]["id"]) for value in inputs if value["artifact_kind"] == kind.value
    )


def _constraint_texts(
    constraints: Mapping[str, object],
    key: str,
    *,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    value = constraints.get(key)
    if (
        not isinstance(value, (list, tuple))
        or (not allow_empty and not value)
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise BlueprintWorkflowError(f"benchmark {key} constraint is missing or invalid")
    return tuple(value)


def _artifact_outputs(
    node: BlueprintNode,
    output: _BlueprintOutput,
) -> tuple[tuple[ArtifactKind, BaseModel], ...]:
    if node is BlueprintNode.BRIEF and isinstance(output, CreativeBrief):
        return ((ArtifactKind.CREATIVE_BRIEF, output),)
    if node is BlueprintNode.PREMISE and isinstance(output, Premise):
        return ((ArtifactKind.PREMISE, output),)
    if node is BlueprintNode.WORLD_SPECIALIST and isinstance(output, _WorldOutput):
        return (
            *((ArtifactKind.LOCATION, value) for value in output.locations),
            *((ArtifactKind.WORLD_RULE, value) for value in output.world_rules),
        )
    if node is BlueprintNode.CHARACTER_SPECIALIST and isinstance(
        output,
        _CharacterOutput,
    ):
        return (
            *((ArtifactKind.CHARACTER, value) for value in output.characters),
            *((ArtifactKind.RELATIONSHIP, value) for value in output.relationships),
        )
    if node is BlueprintNode.INTEGRATION and isinstance(output, StoryBlueprint):
        return ((ArtifactKind.STORY_BLUEPRINT, output),)
    if node is BlueprintNode.EVALUATION and isinstance(output, Critique):
        return ((ArtifactKind.CRITIQUE, output),)
    raise BlueprintWorkflowError(f"node {node.value} returned an incompatible output")


def _validate_output(
    task: BlueprintNodeTask,
    output: _BlueprintOutput,
    execution: _Execution,
) -> None:
    if isinstance(output, CreativeBrief):
        if output.original_premise != execution.premise:
            raise _SpecialistContractError("Creative Brief changed the frozen user premise")
        constraints = execution.constraints
        target = constraints.get("target_word_count")
        if not isinstance(target, Mapping):
            raise BlueprintWorkflowError("benchmark target word count is missing")
        minimum = target.get("minimum")
        maximum = target.get("maximum")
        if (
            output.story_format is not StoryFormat.SHORT_PROSE
            or not isinstance(minimum, int)
            or not isinstance(maximum, int)
            or not minimum <= output.target_word_count <= maximum
            or output.maturity.value != constraints.get("intended_maturity")
            or not set(cast(list[str], constraints.get("required_elements", []))).issubset(
                output.required_elements
            )
            or not set(cast(list[str], constraints.get("forbidden_shortcuts", []))).issubset(
                output.forbidden_elements
            )
        ):
            raise _SpecialistContractError("Creative Brief does not preserve benchmark constraints")
        return
    if isinstance(output, _CharacterOutput):
        brief_data = _single_input(execution.inputs, ArtifactKind.CREATIVE_BRIEF)
        expected_count = CreativeBrief.model_validate(brief_data).target_significant_character_count
        if len(output.characters) != expected_count:
            raise _SpecialistContractError("character count does not match the Creative Brief")
        character_ids = {character.id for character in output.characters}
        if any(
            relationship.source_character_id not in character_ids
            or relationship.target_character_id not in character_ids
            for relationship in output.relationships
        ):
            raise _SpecialistContractError("relationship references an unknown character")
        return
    if isinstance(output, _WorldOutput):
        if any(location.associated_character_ids for location in output.locations):
            raise _SpecialistContractError(
                "parallel World output referenced unknown Blueprint characters"
            )
        if any(rule.relevant_character_ids for rule in output.world_rules):
            raise _SpecialistContractError(
                "parallel World rules referenced unknown Blueprint characters"
            )
        return
    if isinstance(output, StoryBlueprint):
        authoritative_brief = CreativeBrief.model_validate(
            _single_input(execution.inputs, ArtifactKind.CREATIVE_BRIEF)
        )
        premise = Premise.model_validate(_single_input(execution.inputs, ArtifactKind.PREMISE))
        if output.creative_brief != authoritative_brief:
            raise _SpecialistContractError(
                "Story Blueprint changed the authoritative Creative Brief"
            )
        if (
            output.logline != premise.logline
            or output.thematic_thesis != premise.thematic_thesis
            or output.central_conflict != premise.central_conflict
            or output.story_arc != premise.story_arc
            or output.proposed_ending != premise.proposed_ending
            or output.voice_and_style_guide != premise.voice_and_style_guide
        ):
            raise _SpecialistContractError("Story Blueprint changed authoritative premise fields")
        _require_same_identified_inputs(
            output.characters,
            execution.inputs,
            ArtifactKind.CHARACTER,
        )
        _require_same_identified_inputs(
            output.relationships,
            execution.inputs,
            ArtifactKind.RELATIONSHIP,
        )
        _require_same_identified_inputs(
            output.locations,
            execution.inputs,
            ArtifactKind.LOCATION,
        )
        _require_same_identified_inputs(
            output.world_rules,
            execution.inputs,
            ArtifactKind.WORLD_RULE,
        )
        return
    if isinstance(output, Critique):
        blueprint = next(
            (
                reference
                for reference in task.input_artifacts
                if reference.kind is ArtifactKind.STORY_BLUEPRINT
            ),
            None,
        )
        if (
            blueprint is None
            or output.target_artifact_kind is not ArtifactKind.STORY_BLUEPRINT
            or output.target_artifact_key != blueprint.artifact_key
            or output.target_artifact_version_id != blueprint.version_id
        ):
            raise _SpecialistContractError(
                "Blueprint critique target does not match its exact input"
            )


def _single_input(
    inputs: tuple[dict[str, Any], ...],
    kind: ArtifactKind,
) -> dict[str, Any]:
    values = [
        cast(dict[str, Any], value["content"])
        for value in inputs
        if value["artifact_kind"] == kind.value
    ]
    if len(values) != 1:
        raise BlueprintWorkflowError(f"expected one {kind.value} input")
    return values[0]


def _require_same_identified_inputs(
    outputs: tuple[BaseModel, ...],
    inputs: tuple[dict[str, Any], ...],
    kind: ArtifactKind,
) -> None:
    expected = {
        str(value["content"]["id"]): value["content"]
        for value in inputs
        if value["artifact_kind"] == kind.value
    }
    actual = {str(cast(Any, output).id): output.model_dump(mode="json") for output in outputs}
    if actual != expected:
        raise _SpecialistContractError(f"Story Blueprint changed {kind.value} specialist artifacts")


def _persist_output(
    *,
    session: Session,
    invocation: AgentInvocation,
    project_id: UUID,
    task: BlueprintNodeTask,
    kind: ArtifactKind,
    output: BaseModel,
) -> ArtifactReference:
    artifact_key = _artifact_key(task.node, kind, output)
    artifact = session.scalar(
        select(Artifact)
        .where(
            Artifact.project_id == project_id,
            Artifact.artifact_key == artifact_key,
        )
        .options(joinedload(Artifact.versions))
    )
    if artifact is None:
        artifact = Artifact(
            project_id=project_id,
            artifact_key=artifact_key,
            artifact_type=kind.value,
            title=_artifact_title(kind, output),
            status=ArtifactStatus.DRAFT,
        )
        version_number = 1
        parent_version_id = None
    else:
        version_number = len(artifact.versions) + 1
        parent_version_id = artifact.versions[-1].id
    content = output.model_dump(mode="json")
    version = ArtifactVersion(
        artifact=artifact,
        parent_version_id=parent_version_id,
        created_by_invocation=invocation,
        version_number=version_number,
        schema_version="1",
        content=content,
        content_sha256=canonical_sha256(content),
        change_summary=f"Created by {task.specialist_role}.",
    )
    session.add_all((artifact, version))
    session.flush()
    return _reference(version)


def _artifact_key(
    node: BlueprintNode,
    kind: ArtifactKind,
    output: BaseModel,
) -> str:
    identifier = getattr(output, "id", None)
    if isinstance(identifier, str):
        return f"{kind.value}_{identifier}"
    return f"{node.value}_{kind.value}"


def _artifact_title(kind: ArtifactKind, output: BaseModel) -> str:
    title = getattr(output, "title", None)
    if isinstance(title, str):
        return title[:200]
    name = getattr(output, "name", None)
    if isinstance(name, str):
        return name[:200]
    return kind.value.replace("_", " ").title()


def _reference(version: ArtifactVersion) -> ArtifactReference:
    return ArtifactReference(
        kind=ArtifactKind(version.artifact.artifact_type),
        artifact_key=version.artifact.artifact_key,
        version_id=version.id,
        schema_version=version.schema_version,
    )


def _load_artifact_inputs(
    session: Session,
    references: tuple[ArtifactReference, ...],
) -> tuple[dict[str, Any], ...]:
    inputs: list[dict[str, Any]] = []
    for reference in references:
        version = session.scalar(
            select(ArtifactVersion)
            .where(ArtifactVersion.id == reference.version_id)
            .options(joinedload(ArtifactVersion.artifact))
        )
        if (
            version is None
            or version.artifact.artifact_key != reference.artifact_key
            or version.artifact.artifact_type != reference.kind.value
            or version.schema_version != reference.schema_version
        ):
            raise BlueprintWorkflowError("Blueprint input artifact lineage is invalid")
        inputs.append(
            {
                "artifact_key": reference.artifact_key,
                "artifact_kind": reference.kind.value,
                "artifact_version_id": str(reference.version_id),
                "content": dict(version.content),
            }
        )
    return tuple(inputs)


def _require_matching_response(response: ModelResponse, execution: _Execution) -> None:
    if (
        response.provider != execution.selection.provider
        or response.model_identifier != execution.selection.model_identifier
        or response.deployment is not execution.selection.deployment
    ):
        raise BlueprintWorkflowError(
            "provider response does not match the frozen profile selection"
        )
    if (
        response.usage.input_tokens > execution.call_budget.max_input_tokens
        or response.usage.output_tokens > execution.call_budget.max_output_tokens
        or response.estimated_cost_usd > execution.call_budget.max_cost_usd
    ):
        raise BlueprintWorkflowError("provider response exceeded the reserved call budget")


def _temperature(node: BlueprintNode) -> float:
    return {
        BlueprintNode.BRIEF: 0.3,
        BlueprintNode.PREMISE: 0.8,
        BlueprintNode.WORLD_SPECIALIST: 0.8,
        BlueprintNode.CHARACTER_SPECIALIST: 0.8,
        BlueprintNode.INTEGRATION: 0.5,
        BlueprintNode.EVALUATION: 0.2,
    }[node]


def _messages_sha256(messages: tuple[ModelMessage, ...]) -> str:
    value = "\n".join(f"{message.role.value}\0{message.content}" for message in messages)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _mapping_input(value: Mapping[str, Any], key: str) -> Mapping[str, object]:
    result = value.get(key)
    if not isinstance(result, Mapping):
        raise BlueprintWorkflowError(f"workflow input {key!r} must be an object")
    return cast(Mapping[str, object], result)


def _optional_mapping_input(
    value: Mapping[str, Any],
    key: str,
) -> Mapping[str, object]:
    result = value.get(key)
    if result is None:
        return {}
    if not isinstance(result, Mapping):
        raise BlueprintWorkflowError(f"workflow input {key!r} must be an object")
    return cast(Mapping[str, object], result)


def _text_input(value: Mapping[str, Any], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result.strip():
        raise BlueprintWorkflowError(f"workflow input {key!r} must be non-empty text")
    return result


def _premise_for_run(session: Session, run: WorkflowRun) -> str:
    direct = run.input_state.get("premise")
    if isinstance(direct, str) and direct.strip():
        return direct
    sequence = run.input_state.get("premise_message_sequence")
    if (
        run.conversation_id is not None
        and isinstance(sequence, int)
        and not isinstance(sequence, bool)
    ):
        message = session.scalar(
            select(Message).where(
                Message.conversation_id == run.conversation_id,
                Message.sequence_number == sequence,
            )
        )
        if message is not None and message.content.strip():
            return message.content
    raise BlueprintWorkflowError("workflow premise input is missing")


def _uuid_input(value: Mapping[str, Any], key: str) -> UUID:
    result = _optional_uuid_input(value, key)
    if result is None:
        raise BlueprintWorkflowError(f"workflow input {key!r} must be a UUID")
    return result


def _optional_uuid_input(value: Mapping[str, Any], key: str) -> UUID | None:
    result = value.get(key)
    if result is None:
        return None
    try:
        return UUID(str(result))
    except ValueError as error:
        raise BlueprintWorkflowError(f"workflow input {key!r} must be a UUID") from error


def _integer_input(
    value: Mapping[str, Any],
    key: str,
    *,
    default: int,
) -> int:
    result = value.get(key, default)
    if not isinstance(result, int) or isinstance(result, bool):
        raise BlueprintWorkflowError(f"workflow input {key!r} must be an integer")
    return result


# Preserve the public name used by the frozen evaluation harness.
BenchmarkBlueprintNodeExecutor = ProfileRoutedBlueprintNodeExecutor
