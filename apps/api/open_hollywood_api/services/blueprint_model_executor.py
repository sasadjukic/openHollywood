"""Profile-routed model execution and immutable outputs for Blueprint specialists."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID, uuid4

from open_hollywood_engine.artifacts import (
    ArtifactKind,
    Character,
    CreativeBrief,
    Critique,
    Location,
    Premise,
    Relationship,
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
from pydantic import BaseModel, ConfigDict, Field
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

BLUEPRINT_MODEL_PROMPT_VERSION = "1"


class _StructuredOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class _WorldOutput(_StructuredOutput):
    locations: tuple[Location, ...] = Field(min_length=1)
    world_rules: tuple[WorldRule, ...] = Field(min_length=1)


class _CharacterOutput(_StructuredOutput):
    characters: tuple[Character, ...] = Field(min_length=2, max_length=5)
    relationships: tuple[Relationship, ...] = Field(min_length=1)


type _BlueprintOutput = (
    CreativeBrief | Premise | _WorldOutput | _CharacterOutput | StoryBlueprint | Critique
)

_OUTPUT_MODELS: Mapping[BlueprintNode, type[BaseModel]] = {
    BlueprintNode.BRIEF: CreativeBrief,
    BlueprintNode.PREMISE: Premise,
    BlueprintNode.WORLD_SPECIALIST: _WorldOutput,
    BlueprintNode.CHARACTER_SPECIALIST: _CharacterOutput,
    BlueprintNode.INTEGRATION: StoryBlueprint,
    BlueprintNode.EVALUATION: Critique,
}

_NODE_INSTRUCTIONS: Mapping[BlueprintNode, str] = {
    BlueprintNode.BRIEF: (
        "Convert the frozen user premise and constraints into an authoritative "
        "short-prose Creative Brief. Infer missing creative choices explicitly."
    ),
    BlueprintNode.PREMISE: (
        "Develop the Creative Brief into a causally specific premise, thematic "
        "thesis, complete arc, deliberate ending, and controlled voice guide."
    ),
    BlueprintNode.WORLD_SPECIALIST: (
        "Design the smallest dramatically sufficient set of locations and world "
        "rules. Every identifier must be stable snake_case and references must resolve."
    ),
    BlueprintNode.CHARACTER_SPECIALIST: (
        "Create exactly the significant-character count required by the brief and "
        "at least one valid relationship. Give every character a distinct motive, "
        "contradiction, arc, and dialogue voice."
    ),
    BlueprintNode.INTEGRATION: (
        "Integrate the exact specialist artifacts into one complete Story Blueprint. "
        "Preserve their identifiers and content, create a causal beat sequence and "
        "the exact requested number of contiguous scene plans, and reach the declared ending."
    ),
    BlueprintNode.EVALUATION: (
        "Evaluate the exact Story Blueprint against causal structure, character depth, "
        "dialogue potential, originality, voice, emotional impact, pacing, continuity, "
        "prompt constraints, completeness, and format. Target the supplied blueprint version."
    ),
}


class BenchmarkBlueprintNodeExecutor(BlueprintNodeExecutor):
    """Execute benchmark Blueprint roles through one provider-neutral gateway."""

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
        messages = _messages(
            task=task,
            instruction=_NODE_INSTRUCTIONS[task.node],
            premise=execution.premise,
            inputs=execution.inputs,
            revision_instruction=execution.revision_instruction,
            constraints=execution.constraints,
            schema=output_model.model_json_schema(),
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
                output_model.model_json_schema()
                if execution.selection.deployment is ModelDeployment.LOCAL
                else None
            ),
        )
        try:
            response = await self._gateway.generate(request)
            _require_matching_response(response, execution)
            output = cast(_BlueprintOutput, output_model.model_validate_json(response.content))
            _validate_output(task, output, execution)
            references = await asyncio.to_thread(
                self._complete_invocation,
                invocation_id=invocation_id,
                task=task,
                execution=execution,
                response=response,
                outputs=_artifact_outputs(task.node, output),
            )
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
            )
            raise
        except (ValueError, json.JSONDecodeError) as error:
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                code="schema_validation_failed",
                message="The specialist returned invalid structured output.",
                schema_valid=False,
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
                request_settings={
                    "deployment": execution.selection.deployment.value,
                    "graph_version": STORY_BLUEPRINT_GRAPH_VERSION,
                    "model_profile_configuration_sha256": (execution.configuration_sha256),
                    "node": task.node.value,
                    "prompt_template_version": BLUEPRINT_MODEL_PROMPT_VERSION,
                    "run_seed": execution.run_seed,
                    "schema_enforced": schema_enforced,
                    "task_fingerprint": execution.task_fingerprint,
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
            invocation.request_settings = {
                **invocation.request_settings,
                "provider_response_model_identifier": (
                    response.provider_model_identifier or response.model_identifier
                ),
            }
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
    ) -> None:
        safe_message = active_secret_guard().redact_text(message)[:2_000]
        with self._session_factory.begin() as session:
            invocation = session.get(AgentInvocation, invocation_id)
            if invocation is None:
                return
            invocation.status = InvocationStatus.FAILED
            invocation.schema_validation_succeeded = schema_valid
            invocation.completed_at = datetime.now(UTC)
            invocation.error_code = code
            invocation.error_message = safe_message


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


def _messages(
    *,
    task: BlueprintNodeTask,
    instruction: str,
    premise: str,
    inputs: tuple[dict[str, Any], ...],
    revision_instruction: str | None,
    constraints: dict[str, object],
    schema: dict[str, Any],
) -> tuple[ModelMessage, ...]:
    system = (
        "You are a registered Open Hollywood Story Blueprint specialist. "
        f"{instruction} Return only one JSON value conforming exactly to the supplied "
        "schema. Do not include Markdown, commentary, hidden reasoning, or undeclared fields."
    )
    user = json.dumps(
        {
            "assignment": {
                "node": task.node.value,
                "specialist_role": task.specialist_role,
                "human_revision_instruction": revision_instruction,
            },
            "frozen_user_premise": premise,
            "frozen_benchmark_constraints": constraints,
            "input_artifacts": inputs,
            "output_schema": schema,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return (
        ModelMessage(role=MessageRole.SYSTEM, content=system),
        ModelMessage(role=MessageRole.USER, content=user),
    )


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
            raise ValueError("Creative Brief changed the frozen user premise")
        constraints = execution.constraints
        target = constraints.get("target_word_count")
        if not isinstance(target, Mapping):
            raise ValueError("benchmark target word count is missing")
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
            raise ValueError("Creative Brief does not preserve benchmark constraints")
        return
    if isinstance(output, _CharacterOutput):
        brief_data = _single_input(execution.inputs, ArtifactKind.CREATIVE_BRIEF)
        expected_count = CreativeBrief.model_validate(brief_data).target_significant_character_count
        if len(output.characters) != expected_count:
            raise ValueError("character count does not match the Creative Brief")
        character_ids = {character.id for character in output.characters}
        if any(
            relationship.source_character_id not in character_ids
            or relationship.target_character_id not in character_ids
            for relationship in output.relationships
        ):
            raise ValueError("relationship references an unknown character")
        return
    if isinstance(output, StoryBlueprint):
        authoritative_brief = CreativeBrief.model_validate(
            _single_input(execution.inputs, ArtifactKind.CREATIVE_BRIEF)
        )
        premise = Premise.model_validate(_single_input(execution.inputs, ArtifactKind.PREMISE))
        if output.creative_brief != authoritative_brief:
            raise ValueError("Story Blueprint changed the authoritative Creative Brief")
        if (
            output.logline != premise.logline
            or output.thematic_thesis != premise.thematic_thesis
            or output.central_conflict != premise.central_conflict
            or output.story_arc != premise.story_arc
            or output.proposed_ending != premise.proposed_ending
            or output.voice_and_style_guide != premise.voice_and_style_guide
        ):
            raise ValueError("Story Blueprint changed authoritative premise fields")
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
            raise ValueError("Blueprint critique target does not match its exact input")


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
        raise ValueError(f"expected one {kind.value} input")
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
        raise ValueError(f"Story Blueprint changed {kind.value} specialist artifacts")


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
