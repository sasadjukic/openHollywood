"""Profile-routed, replay-safe model execution for scene production."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, cast
from uuid import UUID, uuid4

from open_hollywood_engine.artifacts import (
    ArtifactKind,
    ContinuityReport,
    Critique,
    SceneDraft,
    StoryBible,
    StoryBibleInvariantError,
    StoryBibleUpdate,
    apply_story_bible_update,
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
    SCENE_PRODUCTION_GRAPH_VERSION,
    SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
    ArtifactReference,
    ContinuityCheckResult,
    ContinuityCheckTask,
    DialogueIntegrationTask,
    RetryableSceneProductionError,
    RunBudget,
    SceneCritiqueResult,
    SceneCritiqueTask,
    SceneDraftResult,
    SceneProductionError,
    SceneProductionExecutor,
    SceneWritingTask,
    StoryBibleUpdateResult,
    StoryBibleUpdateTask,
)
from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.orm import Session, joinedload, sessionmaker

from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    InvocationStatus,
    WorkflowRun,
    agent_invocation_inputs,
)
from open_hollywood_api.persistence.secret_policy import active_secret_guard


class _Operation(StrEnum):
    WRITE = "write"
    CRITIQUE = "critique"
    CONTINUITY = "continuity"
    STORY_BIBLE_UPDATE = "story_bible_update"


_OUTPUT_MODELS: Mapping[_Operation, type[BaseModel]] = {
    _Operation.WRITE: SceneDraft,
    _Operation.CRITIQUE: Critique,
    _Operation.CONTINUITY: ContinuityReport,
    _Operation.STORY_BIBLE_UPDATE: StoryBibleUpdate,
}

_INSTRUCTIONS: Mapping[_Operation, str] = {
    _Operation.WRITE: (
        "Write one complete short-prose scene that follows the exact Scene Plan, "
        "approved Blueprint, current canonical Story Bible, and prior accepted scenes. "
        "On revision, address the supplied critique without changing scene identity."
    ),
    _Operation.CRITIQUE: (
        "Independently evaluate the exact scene draft against its Scene Plan, the "
        "approved Blueprint, prose quality, dramatic progress, and prompt constraints."
    ),
    _Operation.CONTINUITY: (
        "Check the exact scene draft against the exact canonical Story Bible and Scene "
        "Plan. Cover every continuity category in canonical enum order."
    ),
    _Operation.STORY_BIBLE_UPDATE: (
        "Return only the typed delta established by the accepted scene. Preserve the "
        "source version IDs and continue timeline numbering from the supplied Story Bible."
    ),
}


class BenchmarkProductionExecutor(SceneProductionExecutor):
    """Execute production specialists with exact lineage and idempotent replay."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        gateway: ModelGateway,
    ) -> None:
        self._session_factory = session_factory
        self._gateway = gateway

    async def write(self, task: SceneWritingTask) -> SceneDraftResult:
        output, references = await self._execute(
            _Operation.WRITE,
            task,
            _writing_inputs(task),
        )
        if not isinstance(output, SceneDraft) or len(references) != 1:
            raise SceneProductionError("writer replay returned incompatible output")
        return SceneDraftResult(draft=output, artifact=references[0])

    async def integrate_dialogue(
        self,
        task: DialogueIntegrationTask,
    ) -> SceneDraftResult:
        del task
        raise SceneProductionError(
            "benchmark production does not enable the optional dialogue subgraph"
        )

    async def critique(self, task: SceneCritiqueTask) -> SceneCritiqueResult:
        output, references = await self._execute(
            _Operation.CRITIQUE,
            task,
            _critique_inputs(task),
        )
        if not isinstance(output, Critique) or len(references) != 1:
            raise SceneProductionError("critic replay returned incompatible output")
        return SceneCritiqueResult(critique=output, artifact=references[0])

    async def check_continuity(
        self,
        task: ContinuityCheckTask,
    ) -> ContinuityCheckResult:
        output, references = await self._execute(
            _Operation.CONTINUITY,
            task,
            _continuity_inputs(task),
        )
        if not isinstance(output, ContinuityReport) or len(references) != 1:
            raise SceneProductionError("continuity replay returned incompatible output")
        return ContinuityCheckResult(report=output, artifact=references[0])

    async def update_story_bible(
        self,
        task: StoryBibleUpdateTask,
    ) -> StoryBibleUpdateResult:
        output, references = await self._execute(
            _Operation.STORY_BIBLE_UPDATE,
            task,
            _story_bible_inputs(task),
        )
        if not isinstance(output, StoryBibleUpdate) or len(references) != 2:
            raise SceneProductionError("story-bible replay returned incompatible output")
        by_kind = {reference.kind: reference for reference in references}
        update_reference = by_kind.get(ArtifactKind.STORY_BIBLE_UPDATE)
        bible_reference = by_kind.get(ArtifactKind.STORY_BIBLE)
        if update_reference is None or bible_reference is None:
            raise SceneProductionError("story-bible replay is missing persisted outputs")
        source, successor = await asyncio.to_thread(
            self._load_story_bible_pair,
            task.source_story_bible,
            bible_reference,
        )
        return StoryBibleUpdateResult(
            source_story_bible=source,
            update=output,
            story_bible=successor,
            update_artifact=update_reference,
            story_bible_artifact=bible_reference,
        )

    async def _execute(
        self,
        operation: _Operation,
        task: object,
        input_references: tuple[ArtifactReference, ...],
    ) -> tuple[BaseModel, tuple[ArtifactReference, ...]]:
        execution = await asyncio.to_thread(
            self._load_execution,
            operation,
            task,
            input_references,
        )
        replay = await asyncio.to_thread(self._replay, operation, execution)
        if replay is not None:
            return replay
        output_model = _OUTPUT_MODELS[operation]
        messages = _messages(
            operation,
            execution,
            output_model.model_json_schema(),
        )
        invocation_id = await asyncio.to_thread(
            self._start_invocation,
            operation,
            execution,
            messages,
        )
        request = ModelRequest(
            model_identifier=execution.selection.model_identifier,
            messages=messages,
            budget=execution.call_budget,
            invocation=InvocationContext(
                specialist_role=execution.specialist_role,
                prompt_template_version=SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
                input_artifact_version_ids=execution.input_version_ids,
                model_profile_id=execution.profile_id,
            ),
            settings=ModelSettings(
                temperature=_temperature(operation),
                top_p=0.95,
                seed=execution.seed,
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
            output = output_model.model_validate_json(response.content)
            _validate_output(operation, task, output)
            references = await asyncio.to_thread(
                self._complete_invocation,
                invocation_id,
                operation,
                task,
                execution,
                output,
                response,
            )
        except ModelGatewayError as error:
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                error.code.value,
                str(error),
                None,
            )
            if error.retryable:
                raise RetryableSceneProductionError(str(error)) from error
            raise SceneProductionError(str(error)) from error
        except SceneProductionError as error:
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                "production_contract_failed",
                str(error),
                None,
            )
            raise
        except (ValueError, json.JSONDecodeError, StoryBibleInvariantError) as error:
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                "schema_validation_failed",
                "The production specialist returned invalid structured output.",
                False,
            )
            raise RetryableSceneProductionError(
                "production specialist returned invalid structured output"
            ) from error
        return output, references

    def _load_execution(
        self,
        operation: _Operation,
        task: object,
        input_references: tuple[ArtifactReference, ...],
    ) -> _Execution:
        production = _production(task)
        specialist_role = _specialist_role(task)
        with self._session_factory() as session:
            run = session.get(WorkflowRun, production.workflow_run_id)
            if run is None:
                raise SceneProductionError("scene-production workflow run does not exist")
            profile_id = _uuid_input(run.input_state, "model_profile_id")
            if profile_id != production.model_profile_id:
                raise SceneProductionError("production profile does not match its frozen run")
            configuration = ModelProfileConfiguration.from_data(
                _mapping_input(run.input_state, "model_profile_configuration")
            )
            configuration_sha256 = canonical_sha256(configuration.to_data())
            if configuration_sha256 != _text_input(
                run.input_state,
                "model_profile_configuration_sha256",
            ):
                raise SceneProductionError(
                    "frozen model-profile configuration digest does not match"
                )
            if not configuration.is_complete:
                raise SceneProductionError("scene-production model profile is incomplete")
            selection = configuration.selection_for(specialist_role)
            if selection.provider != self._gateway.provider:
                raise SceneProductionError(
                    f"no runtime gateway is configured for provider {selection.provider!r}"
                )
            budget = RunBudget.from_data(
                run.budget,
                default_max_graph_steps=production.max_graph_steps,
            )
            call_budget = production.call_budget
            if (
                call_budget.max_input_tokens != budget.per_call_input_tokens
                or call_budget.max_output_tokens != budget.per_call_output_tokens
                or call_budget.max_cost_usd != budget.per_call_cost_usd
            ):
                raise SceneProductionError("production call budget does not match its frozen run")
            inputs = _load_inputs(session, input_references)
            run_seed = _integer_input(run.input_state, "run_seed")
            fingerprint = canonical_sha256(
                {
                    "workflow_run_id": str(run.id),
                    "operation": operation.value,
                    "specialist_role": specialist_role,
                    "unit_id": _unit_id(task),
                    "revision_number": _revision_number(task),
                    "input_artifact_version_ids": [
                        str(reference.version_id) for reference in input_references
                    ],
                    "prompt_template_version": SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
                    "model_profile_configuration": configuration.to_data(),
                    "run_seed": run_seed,
                }
            )
            return _Execution(
                workflow_run_id=run.id,
                project_id=run.project_id,
                profile_id=profile_id,
                configuration_sha256=configuration_sha256,
                selection=selection,
                specialist_role=specialist_role,
                input_version_ids=tuple(reference.version_id for reference in input_references),
                inputs=inputs,
                constraints=dict(_mapping_input(run.input_state, "benchmark_constraints")),
                call_budget=call_budget,
                seed=run_seed + _unit_number(task) * 100 + _revision_number(task),
                task_fingerprint=fingerprint,
                unit_id=_unit_id(task),
                revision_number=_revision_number(task),
            )

    def _replay(
        self,
        operation: _Operation,
        execution: _Execution,
    ) -> tuple[BaseModel, tuple[ArtifactReference, ...]] | None:
        with self._session_factory() as session:
            invocations = session.scalars(
                select(AgentInvocation)
                .where(
                    AgentInvocation.workflow_run_id == execution.workflow_run_id,
                    AgentInvocation.status == InvocationStatus.SUCCEEDED,
                )
                .options(
                    joinedload(AgentInvocation.output_versions).joinedload(ArtifactVersion.artifact)
                )
            ).unique()
            invocation = next(
                (
                    candidate
                    for candidate in invocations
                    if candidate.request_settings.get("task_fingerprint")
                    == execution.task_fingerprint
                ),
                None,
            )
            if invocation is None:
                return None
            versions = tuple(
                sorted(
                    invocation.output_versions,
                    key=lambda version: (
                        version.artifact.artifact_type,
                        version.version_number,
                    ),
                )
            )
            primary_kind = _primary_kind(operation)
            primary = next(
                (
                    version
                    for version in versions
                    if version.artifact.artifact_type == primary_kind.value
                ),
                None,
            )
            if primary is None:
                raise SceneProductionError("succeeded production invocation has no primary output")
            output = _OUTPUT_MODELS[operation].model_validate(primary.content)
            return output, tuple(_reference(version) for version in versions)

    def _start_invocation(
        self,
        operation: _Operation,
        execution: _Execution,
        messages: tuple[ModelMessage, ...],
    ) -> UUID:
        invocation_id = uuid4()
        with self._session_factory.begin() as session:
            invocation = AgentInvocation(
                id=invocation_id,
                workflow_run_id=execution.workflow_run_id,
                model_profile_id=execution.profile_id,
                specialist_role=execution.specialist_role,
                provider=execution.selection.provider,
                model_identifier=execution.selection.model_identifier,
                status=InvocationStatus.RUNNING,
                request_settings={
                    "deployment": execution.selection.deployment.value,
                    "graph_version": SCENE_PRODUCTION_GRAPH_VERSION,
                    "model_profile_configuration_sha256": (execution.configuration_sha256),
                    "operation": operation.value,
                    "prompt_template_version": (SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION),
                    "run_seed": execution.seed,
                    "schema_enforced": (execution.selection.deployment is ModelDeployment.LOCAL),
                    "task_fingerprint": execution.task_fingerprint,
                    "temperature": _temperature(operation),
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
        invocation_id: UUID,
        operation: _Operation,
        task: object,
        execution: _Execution,
        output: BaseModel,
        response: ModelResponse,
    ) -> tuple[ArtifactReference, ...]:
        with self._session_factory.begin() as session:
            invocation = session.get(AgentInvocation, invocation_id)
            if invocation is None:
                raise SceneProductionError("production invocation disappeared")
            references: list[ArtifactReference] = [
                _persist_output(
                    session,
                    invocation,
                    execution.project_id,
                    operation,
                    execution.unit_id,
                    output,
                )
            ]
            if operation is _Operation.STORY_BIBLE_UPDATE:
                if not isinstance(output, StoryBibleUpdate):
                    raise SceneProductionError("story-bible output is incompatible")
                source_reference = cast(
                    StoryBibleUpdateTask,
                    task,
                ).source_story_bible
                source = _load_story_bible(session, source_reference)
                successor = apply_story_bible_update(source, output)
                references.append(
                    _persist_output(
                        session,
                        invocation,
                        execution.project_id,
                        operation,
                        execution.unit_id,
                        successor,
                    )
                )
            invocation.status = InvocationStatus.SUCCEEDED
            invocation.input_tokens = response.usage.input_tokens
            invocation.output_tokens = response.usage.output_tokens
            invocation.estimated_cost_usd = response.estimated_cost_usd
            invocation.latency_ms = response.timing.total_ms
            invocation.schema_validation_succeeded = True
            invocation.completed_at = datetime.now(UTC)
            return tuple(references)

    def _fail_invocation(
        self,
        invocation_id: UUID,
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

    def _load_story_bible_pair(
        self,
        source_reference: ArtifactReference,
        successor_reference: ArtifactReference,
    ) -> tuple[StoryBible, StoryBible]:
        with self._session_factory() as session:
            return (
                _load_story_bible(session, source_reference),
                _load_story_bible(session, successor_reference),
            )


@dataclass(frozen=True, slots=True)
class _Execution:
    workflow_run_id: UUID
    project_id: UUID
    profile_id: UUID
    configuration_sha256: str
    selection: ModelSelection
    specialist_role: str
    input_version_ids: tuple[UUID, ...]
    inputs: tuple[dict[str, Any], ...]
    constraints: dict[str, object]
    call_budget: ModelCallBudget
    seed: int
    task_fingerprint: str
    unit_id: str
    revision_number: int


def _messages(
    operation: _Operation,
    execution: _Execution,
    schema: dict[str, Any],
) -> tuple[ModelMessage, ...]:
    system = (
        "You are a registered Open Hollywood scene-production specialist. "
        f"{_INSTRUCTIONS[operation]} Return only one JSON value conforming exactly "
        "to the supplied schema. Do not include Markdown, commentary, hidden reasoning, "
        "or undeclared fields."
    )
    user = json.dumps(
        {
            "assignment": {
                "operation": operation.value,
                "specialist_role": execution.specialist_role,
                "unit_id": execution.unit_id,
                "revision_number": execution.revision_number,
            },
            "frozen_benchmark_constraints": execution.constraints,
            "input_artifacts": execution.inputs,
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


def _validate_output(
    operation: _Operation,
    task: object,
    output: BaseModel,
) -> None:
    if operation is _Operation.WRITE:
        writing = cast(SceneWritingTask, task)
        draft = cast(SceneDraft, output)
        if (
            draft.scene_id != writing.unit.unit_id
            or draft.scene_number != writing.unit.unit_number
            or draft.revision_number != writing.revision_number
            or not draft.is_complete
        ):
            raise ValueError("scene draft does not match its exact assignment")
        return
    if operation is _Operation.CRITIQUE:
        critique_task = cast(SceneCritiqueTask, task)
        critique = cast(Critique, output)
        if (
            critique.target_artifact_kind is not ArtifactKind.SCENE_DRAFT
            or critique.target_artifact_key != critique_task.draft.artifact_key
            or critique.target_artifact_version_id != critique_task.draft.version_id
        ):
            raise ValueError(
                "scene critique does not target its exact draft "
                f"({critique.target_artifact_version_id} != "
                f"{critique_task.draft.version_id})"
            )
        return
    if operation is _Operation.CONTINUITY:
        continuity_task = cast(ContinuityCheckTask, task)
        report = cast(ContinuityReport, output)
        if (
            report.story_bible_version_id != continuity_task.story_bible.version_id
            or report.scene_version_id != continuity_task.draft.version_id
            or report.scene_plan_version_id != continuity_task.unit.plan.version_id
            or report.scene_id != continuity_task.unit.unit_id
            or report.scene_number != continuity_task.unit.unit_number
        ):
            raise ValueError("continuity report does not match its exact inputs")
        return
    update_task = cast(StoryBibleUpdateTask, task)
    update = cast(StoryBibleUpdate, output)
    if (
        update.source_story_bible_version_id != update_task.source_story_bible.version_id
        or update.continuity_report_version_id != update_task.continuity_report.version_id
        or update.accepted_scene.scene_id != update_task.unit.unit_id
        or update.accepted_scene.scene_number != update_task.unit.unit_number
        or update.accepted_scene.artifact_version_id != update_task.accepted_draft.version_id
    ):
        raise ValueError("story-bible update does not match its exact inputs")


def _writing_inputs(task: SceneWritingTask) -> tuple[ArtifactReference, ...]:
    return _unique_references(
        (
            task.production.approved_blueprint,
            task.unit.plan,
            *(character.artifact for character in task.unit.characters),
            *task.unit.context_artifacts,
            task.story_bible,
            *task.accepted_units,
            *((task.previous_draft,) if task.previous_draft is not None else ()),
            *((task.previous_critique,) if task.previous_critique is not None else ()),
        )
    )


def _critique_inputs(task: SceneCritiqueTask) -> tuple[ArtifactReference, ...]:
    return _unique_references(
        (
            task.production.approved_blueprint,
            task.unit.plan,
            task.draft,
            task.story_bible,
            *task.accepted_units,
        )
    )


def _continuity_inputs(task: ContinuityCheckTask) -> tuple[ArtifactReference, ...]:
    return _unique_references(
        (
            task.unit.plan,
            task.story_bible,
            task.draft,
            *task.accepted_units,
        )
    )


def _story_bible_inputs(task: StoryBibleUpdateTask) -> tuple[ArtifactReference, ...]:
    return _unique_references(
        (
            task.unit.plan,
            task.source_story_bible,
            task.accepted_draft,
            task.continuity_report,
            *task.accepted_units,
        )
    )


def _unique_references(
    references: Iterable[ArtifactReference],
) -> tuple[ArtifactReference, ...]:
    by_version: dict[UUID, ArtifactReference] = {}
    for reference in references:
        by_version.setdefault(reference.version_id, reference)
    return tuple(by_version.values())


def _load_inputs(
    session: Session,
    references: tuple[ArtifactReference, ...],
) -> tuple[dict[str, Any], ...]:
    result: list[dict[str, Any]] = []
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
            raise SceneProductionError("production input artifact lineage is invalid")
        result.append(
            {
                "artifact_key": reference.artifact_key,
                "artifact_kind": reference.kind.value,
                "artifact_version_id": str(reference.version_id),
                "content": dict(version.content),
            }
        )
    return tuple(result)


def _persist_output(
    session: Session,
    invocation: AgentInvocation,
    project_id: UUID,
    operation: _Operation,
    unit_id: str,
    output: BaseModel,
) -> ArtifactReference:
    kind = _kind_for_output(output)
    artifact_key = _artifact_key(kind, unit_id)
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
            title=_artifact_title(output, kind, unit_id),
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
        change_summary=f"Created by {invocation.specialist_role} ({operation.value}).",
    )
    session.add_all((artifact, version))
    session.flush()
    return _reference(version)


def _artifact_key(kind: ArtifactKind, unit_id: str) -> str:
    if kind is ArtifactKind.STORY_BIBLE:
        return "canonical_story_bible"
    return f"{kind.value}_{unit_id}"


def _artifact_title(output: BaseModel, kind: ArtifactKind, unit_id: str) -> str:
    title = getattr(output, "title", None)
    if isinstance(title, str):
        return title[:200]
    return f"{kind.value.replace('_', ' ').title()} — {unit_id}"[:200]


def _kind_for_output(output: BaseModel) -> ArtifactKind:
    if isinstance(output, SceneDraft):
        return ArtifactKind.SCENE_DRAFT
    if isinstance(output, Critique):
        return ArtifactKind.CRITIQUE
    if isinstance(output, ContinuityReport):
        return ArtifactKind.CONTINUITY_REPORT
    if isinstance(output, StoryBibleUpdate):
        return ArtifactKind.STORY_BIBLE_UPDATE
    if isinstance(output, StoryBible):
        return ArtifactKind.STORY_BIBLE
    raise SceneProductionError("production output has no registered artifact kind")


def _primary_kind(operation: _Operation) -> ArtifactKind:
    return {
        _Operation.WRITE: ArtifactKind.SCENE_DRAFT,
        _Operation.CRITIQUE: ArtifactKind.CRITIQUE,
        _Operation.CONTINUITY: ArtifactKind.CONTINUITY_REPORT,
        _Operation.STORY_BIBLE_UPDATE: ArtifactKind.STORY_BIBLE_UPDATE,
    }[operation]


def _load_story_bible(
    session: Session,
    reference: ArtifactReference,
) -> StoryBible:
    version = session.get(ArtifactVersion, reference.version_id)
    if version is None:
        raise SceneProductionError("story-bible artifact version does not exist")
    return StoryBible.model_validate(version.content)


def _reference(version: ArtifactVersion) -> ArtifactReference:
    return ArtifactReference(
        kind=ArtifactKind(version.artifact.artifact_type),
        artifact_key=version.artifact.artifact_key,
        version_id=version.id,
        schema_version=version.schema_version,
    )


def _require_matching_response(
    response: ModelResponse,
    execution: _Execution,
) -> None:
    if (
        response.provider != execution.selection.provider
        or response.model_identifier != execution.selection.model_identifier
        or response.deployment is not execution.selection.deployment
    ):
        raise SceneProductionError("provider response does not match the frozen profile selection")
    if (
        response.usage.input_tokens > execution.call_budget.max_input_tokens
        or response.usage.output_tokens > execution.call_budget.max_output_tokens
        or response.estimated_cost_usd > execution.call_budget.max_cost_usd
    ):
        raise SceneProductionError("provider response exceeded the reserved call budget")


def _production(task: object) -> Any:
    production = getattr(task, "production", None)
    if production is None:
        raise SceneProductionError("production task is missing its run contract")
    return production


def _specialist_role(task: object) -> str:
    role = getattr(task, "specialist_role", None)
    if not isinstance(role, str) or not role:
        raise SceneProductionError("production task has no registered specialist role")
    return role


def _unit_id(task: object) -> str:
    unit = getattr(task, "unit", None)
    value = getattr(unit, "unit_id", None)
    if not isinstance(value, str) or not value:
        raise SceneProductionError("production task has no unit ID")
    return value


def _unit_number(task: object) -> int:
    unit = getattr(task, "unit", None)
    value = getattr(unit, "unit_number", None)
    if not isinstance(value, int) or isinstance(value, bool):
        raise SceneProductionError("production task has no unit number")
    return value


def _revision_number(task: object) -> int:
    value = getattr(task, "revision_number", 0)
    if not isinstance(value, int) or isinstance(value, bool):
        raise SceneProductionError("production task has no revision number")
    return value


def _temperature(operation: _Operation) -> float:
    return {
        _Operation.WRITE: 0.85,
        _Operation.CRITIQUE: 0.2,
        _Operation.CONTINUITY: 0.1,
        _Operation.STORY_BIBLE_UPDATE: 0.1,
    }[operation]


def _messages_sha256(messages: tuple[ModelMessage, ...]) -> str:
    value = [{"role": message.role.value, "content": message.content} for message in messages]
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _mapping_input(value: Mapping[str, Any], key: str) -> Mapping[str, object]:
    result = value.get(key)
    if not isinstance(result, Mapping):
        raise SceneProductionError(f"workflow input {key!r} must be an object")
    return cast(Mapping[str, object], result)


def _text_input(value: Mapping[str, Any], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise SceneProductionError(f"workflow input {key!r} must be text")
    return result


def _uuid_input(value: Mapping[str, Any], key: str) -> UUID:
    try:
        return UUID(_text_input(value, key))
    except ValueError as error:
        raise SceneProductionError(f"workflow input {key!r} must be a UUID") from error


def _integer_input(value: Mapping[str, Any], key: str) -> int:
    result = value.get(key)
    if not isinstance(result, int) or isinstance(result, bool):
        raise SceneProductionError(f"workflow input {key!r} must be an integer")
    return result
