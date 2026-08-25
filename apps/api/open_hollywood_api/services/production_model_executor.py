"""Profile-routed, replay-safe model execution for scene production."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, cast
from uuid import UUID, uuid4

from open_hollywood_engine.artifacts import (
    ArtifactKind,
    ContinuityCategory,
    ContinuityFindingBasis,
    ContinuityRecheckDisposition,
    ContinuityReport,
    Critique,
    SceneDraft,
    StoryBible,
    StoryBibleInvariantError,
    StoryBibleThread,
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
    ModelProfileMode,
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
from pydantic import BaseModel, ValidationError
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
from open_hollywood_api.services.structured_output import normalize_json_document


class _Operation(StrEnum):
    WRITE = "write"
    CRITIQUE = "critique"
    CONTINUITY = "continuity"
    STORY_BIBLE_UPDATE = "story_bible_update"


class _ContinuitySchemaVariant(StrEnum):
    INITIAL_CHECK = "initial_check"
    RECHECK = "recheck"


_MAX_SAFE_STRUCTURED_FAILURE_DETAIL_CHARS = 500
_MAX_SAFE_STRUCTURED_FAILURE_ISSUES = 12
_CONTINUITY_RECHECK_STAGNATION_ERROR_CODE = "continuity_recheck_stagnated"
_CONTINUITY_RECHECK_ONLY_FIELDS = frozenset(
    {"recheck_disposition", "repair_assessment", "revised_evidence"}
)
_CONTINUITY_MODEL_EVIDENCE_FIELDS = frozenset(
    {"draft_evidence_refs", "revised_draft_evidence_refs"}
)
_CONTINUITY_APPLICATION_OWNED_REPORT_FIELDS = frozenset(
    {
        "story_bible_version_id",
        "scene_version_id",
        "scene_plan_version_id",
        "scene_id",
        "scene_number",
        "checked_categories",
    }
)
_MAX_CONTINUITY_FINDINGS = 8
_MAX_EVIDENCE_REFS_PER_FINDING = 3
_MAX_CANONICAL_SOURCE_REFS_PER_FINDING = 3
_CONTINUITY_FINDING_RESOLUTION_REQUIREMENT = (
    "The blocking-finding schema requires every finding with severity 'error' or "
    "'blocking' to include a non-empty, concrete recommended_resolution. The application "
    "derives blocks_approval=true for both severities; never add that application-owned "
    "field. Advisory 'info' or 'warning' findings may omit recommended_resolution only "
    "when no repair is needed."
)
_CONTINUITY_FINDING_BASIS_REQUIREMENT = (
    "Every error or blocking finding must use exactly one basis. A contradiction must "
    "select draft_evidence_refs from candidate_draft.content.evidence_catalog and cite "
    "canonical_source_refs selected from canonical_source_catalog. A missing_requirement "
    "must cite one exact due-now "
    "requirement_id and provide a coverage_assessment; it must not invent or quote evidence "
    "for absent content. A forbidden_shortcut_violation must cite one exact due-now forbidden "
    "requirement_id and select the exact violating candidate-draft evidence reference. If the "
    "forbidden shortcut is absent, report no violation. The application resolves selected "
    "evidence references into exact persisted excerpts."
)
_CONTINUITY_WORLD_RULE_REQUIREMENT = (
    "Choose the schema branch matching both the finding basis and category. For every "
    "world_rule blocker, use its world-rule branch, copy every involved canonical World Rule "
    "ID into world_rule_ids, evaluate companion rules and exceptions in "
    "companion_rule_assessment, and set condition_explicitly_authorized=false only after that "
    "evaluation proves the condition is not authorized. A condition explicitly authorized by "
    "any companion rule or exception cannot be reported as blocking. For every non-world "
    "blocker, use its non-world branch and omit all world-rule analysis fields."
)
_CONTINUITY_REQUIREMENT_SCOPE = (
    "Use benchmark_constraint_applicability and scene_plan_requirement_applicability as "
    "the sole authorities for requirement gates in this continuity call. Only their "
    "due_now entries may produce an error or blocking finding. Deferred story-wide "
    "requirements, including exact duplicates removed from a non-final Scene Plan view, "
    "must not block the current scene. Treat the Scene Plan's continuity_requirements, "
    "purpose, turning_point, outcome, exit_state, and non-deferred required_elements as "
    "current-scene obligations. A character may temporarily consider a forbidden final "
    "explanation; it becomes a violation only if the completed story adopts it as the "
    "actual resolution. Never rewrite a planned intermediate scene to perform the ending's "
    "work early."
)
_CONTINUITY_RECHECK_REQUIREMENT = (
    "When a previous Continuity Report is supplied, audit every prior error or blocking "
    "finding against the revised draft before reporting anything new. Omit a prior finding "
    "when resolved. For an unresolved prior finding, preserve its ID, set "
    "recheck_disposition='still_blocking', and supply repair_assessment plus "
    "revised_draft_evidence_refs selected from the candidate draft. The same evidence "
    "reference is allowed when the writer left "
    "the offending passage unchanged, but repair_assessment must explain that fact. For a new "
    "blocking defect caused or exposed by the revision, set "
    "recheck_disposition='newly_exposed' and explain why it was not actionable before. Do not "
    "downgrade an unresolved prior blocker to an advisory finding. Every revised_evidence "
    "reference is resolved by the application to an exact excerpt from the supplied revised "
    "draft. A re-checked "
    "missing_requirement instead supplies a fresh coverage_assessment and must omit "
    "revised_evidence because absent content has no excerpt. "
    "When the cited evidence changes, write a fresh repair_assessment instead of copying "
    "the previous judgment. Reuse unchanged evidence only when repair_assessment explicitly "
    "explains that the offending passage was left unchanged. Do not replace prior guidance "
    "with contradictory guidance unless exact Scene Plan or Story Bible evidence proves "
    "the prior repair invalid."
)
_LOCAL_SCHEMA_REPAIR_COMMON_RULES = (
    "Return the complete replacement JSON object, not a patch or explanation.",
    "Correct every validation issue at its exact focus location before changing any "
    "unrelated creative content.",
    "Use exact enum literals and select evidence, canonical-source, requirement, and world-rule "
    "IDs only from the catalogs and enums supplied for their specific fields; never turn "
    "labels, prose descriptions, null-like text, or newly invented names into IDs.",
    "When an optional field is not applicable, use the schema default shape (null, an "
    "empty array, or omission as permitted by the supplied schema) instead of placeholder text.",
)
_LOCAL_SCHEMA_REPAIR_OPERATION_RULES: Mapping[_Operation, tuple[str, ...]] = {
    _Operation.WRITE: (
        "Keep prose and title as non-empty strings, is_complete=true, and preserve the "
        "assigned scene and revision identity.",
    ),
    _Operation.CRITIQUE: (
        "Keep score values numeric, use only declared verdict and severity literals, and "
        "never combine a passing verdict with a blocking issue.",
    ),
    _Operation.CONTINUITY: (
        "Every error or blocking finding needs a concrete recommended_resolution. Return "
        "an empty findings array when no defect remains.",
        "Match every blocking finding to its basis-specific evidence contract. Select draft "
        "evidence handles from candidate_draft.content.evidence_catalog and canonical source "
        "handles from canonical_source_catalog; never copy prose or requirement text into an "
        "ID field.",
        "Choose the branch matching the finding category. World-rule branches require exact "
        "world_rule_ids, a non-empty companion_rule_assessment, and "
        "condition_explicitly_authorized=false. Non-world branches must omit those fields.",
    ),
    _Operation.STORY_BIBLE_UPDATE: (
        "Character, relationship, location, scene, fact, and thread references must use "
        "only canonical IDs present in input_artifacts or valid new IDs declared in this "
        "same update where the schema permits them.",
        "Omit an entity-state update when no matching canonical entity ID exists; never "
        "substitute a display name, location description, or invented alias.",
        "knowledge_fact_ids may reference only facts in the source Story Bible or facts "
        "declared in established_facts in this same response.",
    ),
}


class _StructuredOutputContractError(ValueError):
    """Application validation failure with an explicit output-field location."""

    def __init__(self, location: str, message: str) -> None:
        super().__init__(message)
        self.location = location


class ContinuityRecheckStagnationError(_StructuredOutputContractError):
    """A continuity re-check copied an unresolved judgment without new analysis."""

    def __init__(self, message: str) -> None:
        super().__init__("findings", message)


@dataclass(frozen=True)
class _ContinuityModelContext:
    """Exact, bounded continuity context shared by the prompt and Local grammar."""

    candidate_draft: dict[str, Any]
    accepted_prior_drafts: tuple[dict[str, Any], ...]
    previous_continuity_report: dict[str, Any] | None
    canonical_source_catalog: tuple[dict[str, Any], ...]
    requirement_kinds: Mapping[str, str]
    world_rule_ids: tuple[str, ...]

    @property
    def evidence_refs(self) -> tuple[str, ...]:
        content = self.candidate_draft.get("content")
        if not isinstance(content, dict):
            return ()
        catalog = content.get("evidence_catalog")
        if not isinstance(catalog, list):
            return ()
        return tuple(
            entry["evidence_ref"]
            for entry in catalog
            if isinstance(entry, dict) and isinstance(entry.get("evidence_ref"), str)
        )

    @property
    def canonical_source_refs(self) -> tuple[str, ...]:
        return tuple(
            entry["reference_id"]
            for entry in self.canonical_source_catalog
            if isinstance(entry.get("reference_id"), str)
        )


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
        "On revision, address the supplied critique and, when present, the exact blocking "
        "Continuity Report including each finding's recommended_resolution, without "
        "changing scene identity."
    ),
    _Operation.CRITIQUE: (
        "Independently evaluate the exact scene draft against its Scene Plan, the "
        "approved Blueprint, prose quality, dramatic progress, and prompt constraints."
    ),
    _Operation.CONTINUITY: (
        "Check the exact scene draft against the exact canonical Story Bible and Scene "
        "Plan. Cover every continuity category in canonical enum order. "
        f"{_CONTINUITY_FINDING_RESOLUTION_REQUIREMENT} "
        f"{_CONTINUITY_FINDING_BASIS_REQUIREMENT} "
        f"{_CONTINUITY_WORLD_RULE_REQUIREMENT} "
        f"{_CONTINUITY_REQUIREMENT_SCOPE}"
    ),
    _Operation.STORY_BIBLE_UPDATE: (
        "Return only the typed delta established by the accepted scene. Preserve the "
        "source version IDs and continue timeline numbering from the supplied Story Bible."
    ),
}


class ProfileRoutedProductionExecutor(SceneProductionExecutor):
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
        continuity_schema_variant = (
            _continuity_schema_variant(execution) if operation is _Operation.CONTINUITY else None
        )
        continuity_model_context = (
            _continuity_model_context(execution) if operation is _Operation.CONTINUITY else None
        )
        output_schema = _output_schema(
            operation,
            continuity_schema_variant=continuity_schema_variant,
            continuity_model_context=continuity_model_context,
        )
        messages = _messages(
            operation,
            execution,
            output_schema,
            continuity_schema_variant=continuity_schema_variant,
            continuity_model_context=continuity_model_context,
        )
        invocation_id = await asyncio.to_thread(
            self._start_invocation,
            operation,
            execution,
            messages,
            continuity_schema_variant,
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
                output_schema if execution.selection.deployment is ModelDeployment.LOCAL else None
            ),
        )
        try:
            response = await self._gateway.generate(request)
            _require_matching_response(response, execution)
            output_data = json.loads(normalize_json_document(response.content))
            output = output_model.model_validate(
                _materialize_output_data(operation, task, execution, output_data)
            )
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
        except asyncio.CancelledError:
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                "cancelled_execution",
                "The production specialist call was cancelled before completion.",
                None,
            )
            raise
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
                response,
            )
            raise
        except (ValueError, json.JSONDecodeError, StoryBibleInvariantError) as error:
            diagnostic = _structured_failure_message(error, response)
            validation_issues = _structured_failure_issues(error)
            error_code = (
                _CONTINUITY_RECHECK_STAGNATION_ERROR_CODE
                if isinstance(error, ContinuityRecheckStagnationError)
                else "schema_validation_failed"
            )
            await asyncio.to_thread(
                self._fail_invocation,
                invocation_id,
                error_code,
                diagnostic,
                False,
                response,
                validation_issues,
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
            attempt_number, previous_failure = _retry_context(
                session,
                workflow_run_id=run.id,
                specialist_role=specialist_role,
                task_fingerprint=fingerprint,
            )
            selection, fallback_history = _select_production_model(
                operation=operation,
                specialist_role=specialist_role,
                configuration=configuration,
                attempt_number=attempt_number,
                previous_failure=previous_failure,
            )
            if selection.provider != self._gateway.provider:
                raise SceneProductionError(
                    f"no runtime gateway is configured for provider {selection.provider!r}"
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
                unit_number=_unit_number(task),
                unit_count=len(production.units),
                revision_number=_revision_number(task),
                attempt_number=attempt_number,
                previous_failure=previous_failure,
                fallback_history=fallback_history,
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
        continuity_schema_variant: _ContinuitySchemaVariant | None,
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
                retry_count=execution.attempt_number - 1,
                fallback_history=[dict(item) for item in execution.fallback_history],
                request_settings={
                    "deployment": execution.selection.deployment.value,
                    "graph_version": SCENE_PRODUCTION_GRAPH_VERSION,
                    "model_profile_configuration_sha256": (execution.configuration_sha256),
                    "operation": operation.value,
                    "output_schema_variant": (
                        continuity_schema_variant.value
                        if continuity_schema_variant is not None
                        else "canonical"
                    ),
                    "prompt_template_version": (SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION),
                    "run_seed": execution.seed,
                    "schema_enforced": (execution.selection.deployment is ModelDeployment.LOCAL),
                    "task_fingerprint": execution.task_fingerprint,
                    "attempt_number": execution.attempt_number,
                    "fallback_applied": bool(execution.fallback_history),
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
            _apply_response_metadata(invocation, response)
            invocation.schema_validation_succeeded = True
            invocation.completed_at = datetime.now(UTC)
            return tuple(references)

    def _fail_invocation(
        self,
        invocation_id: UUID,
        code: str,
        message: str,
        schema_valid: bool | None,
        response: ModelResponse | None = None,
        validation_issues: tuple[dict[str, str], ...] = (),
    ) -> None:
        guard = active_secret_guard()
        safe_message = guard.redact_text(message)[:2_000]
        safe_validation_issues = tuple(
            {
                key: guard.redact_text(value)[:_MAX_SAFE_STRUCTURED_FAILURE_DETAIL_CHARS]
                for key, value in issue.items()
            }
            for issue in validation_issues[:_MAX_SAFE_STRUCTURED_FAILURE_ISSUES]
        )
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
            if safe_validation_issues:
                invocation.request_settings = {
                    **invocation.request_settings,
                    "structured_failure": {
                        "schema_version": "1",
                        "issues": list(safe_validation_issues),
                    },
                }

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
        == SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION
    )
    if not failures:
        return 1, None
    latest = failures[-1]
    context: dict[str, object] = {
        "error_code": latest.error_code or "unknown",
        "message": latest.error_message or "No structural diagnostic was recorded.",
        "provider_finish_reason": latest.request_settings.get("provider_finish_reason"),
        "provider_response_length": latest.request_settings.get("provider_response_content_length"),
    }
    structured_failure = latest.request_settings.get("structured_failure")
    if isinstance(structured_failure, dict):
        issues = structured_failure.get("issues")
        if isinstance(issues, list) and all(isinstance(issue, dict) for issue in issues):
            context["validation_issues"] = [dict(issue) for issue in issues]
    return len(failures) + 1, context


def _structured_failure_message(
    error: ValueError | StoryBibleInvariantError,
    response: ModelResponse,
) -> str:
    locations = [
        ":".join(
            value
            for value in (
                issue["location"],
                issue["type"],
                issue.get("message", ""),
            )
            if value
        )
        for issue in _structured_failure_issues(error)
    ]
    return (
        "Structured output validation failed "
        f"(provider_finish_reason={response.finish_reason}): {', '.join(locations)}."
    )


def _structured_failure_issues(
    error: ValueError | StoryBibleInvariantError,
) -> tuple[dict[str, str], ...]:
    """Return bounded diagnostics without retaining model response content or inputs."""
    if isinstance(error, ValidationError):
        issues: list[dict[str, str]] = []
        for item in error.errors(
            include_url=False,
            include_context=False,
            include_input=False,
        )[:_MAX_SAFE_STRUCTURED_FAILURE_ISSUES]:
            location = ".".join(str(value) for value in item["loc"]) or "$"
            issue = {
                "location": location,
                "type": str(item["type"]),
            }
            detail = _safe_structured_failure_detail(str(item["msg"]))
            if detail is not None:
                issue["message"] = detail
            issues.append(issue)
        return tuple(issues)

    detail = _safe_structured_failure_detail(str(error))
    issue = {
        "location": (error.location if isinstance(error, _StructuredOutputContractError) else "$"),
        "type": type(error).__name__,
    }
    if detail is not None:
        issue["message"] = detail
    return (issue,)


def _safe_structured_failure_detail(message: str) -> str | None:
    """Bound deterministic validation detail before persistence and model retry."""
    normalized = " ".join(message.split())
    if not normalized:
        return None
    if len(normalized) <= _MAX_SAFE_STRUCTURED_FAILURE_DETAIL_CHARS:
        return normalized
    return f"{normalized[: _MAX_SAFE_STRUCTURED_FAILURE_DETAIL_CHARS - 3]}..."


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
    unit_number: int
    unit_count: int
    revision_number: int
    attempt_number: int
    previous_failure: dict[str, object] | None
    fallback_history: tuple[dict[str, object], ...]


def _continuity_schema_variant(execution: _Execution) -> _ContinuitySchemaVariant:
    return (
        _ContinuitySchemaVariant.RECHECK
        if _prior_continuity_report(execution) is not None
        else _ContinuitySchemaVariant.INITIAL_CHECK
    )


def _output_schema(
    operation: _Operation,
    *,
    continuity_schema_variant: _ContinuitySchemaVariant | None,
    continuity_model_context: _ContinuityModelContext | None = None,
) -> dict[str, Any]:
    """Build the exact model-facing schema without changing canonical artifacts."""
    schema = deepcopy(_OUTPUT_MODELS[operation].model_json_schema())
    if operation is not _Operation.CONTINUITY:
        if continuity_schema_variant is not None:
            raise ValueError("non-continuity output cannot use a continuity schema variant")
        return schema
    if continuity_schema_variant is None:
        raise ValueError("continuity output requires a schema variant")
    if continuity_model_context is None:
        raise ValueError("continuity output requires its exact model context")

    definitions = schema.get("$defs")
    if not isinstance(definitions, dict):
        raise SceneProductionError("continuity schema is missing definitions")
    finding_schema = definitions.get("ContinuityFinding")
    if not isinstance(finding_schema, dict):
        raise SceneProductionError("continuity schema is missing its finding definition")
    properties = finding_schema.get("properties")
    if not isinstance(properties, dict):
        raise SceneProductionError("continuity finding schema is missing properties")
    report_properties = schema.get("properties")
    if not isinstance(report_properties, dict):
        raise SceneProductionError("continuity report schema is missing properties")
    findings_schema = report_properties.get("findings")
    if not isinstance(findings_schema, dict):
        raise SceneProductionError("continuity report schema is missing findings")
    report_required = schema.get("required")
    if not isinstance(report_required, list):
        raise SceneProductionError("continuity report schema is missing required fields")
    for field_name in _CONTINUITY_APPLICATION_OWNED_REPORT_FIELDS:
        report_properties.pop(field_name, None)
    schema["required"] = [
        field_name
        for field_name in report_required
        if field_name not in _CONTINUITY_APPLICATION_OWNED_REPORT_FIELDS
    ]
    findings_schema["maxItems"] = _MAX_CONTINUITY_FINDINGS

    is_recheck = continuity_schema_variant is _ContinuitySchemaVariant.RECHECK
    phase_name = "Recheck" if is_recheck else "Initial"
    advisory_name = f"{phase_name}AdvisoryContinuityFinding"
    required_requirement_ids = tuple(
        requirement_id
        for requirement_id, kind in continuity_model_context.requirement_kinds.items()
        if kind == "required_element"
    )
    forbidden_requirement_ids = tuple(
        requirement_id
        for requirement_id, kind in continuity_model_context.requirement_kinds.items()
        if kind == "forbidden_shortcut"
    )
    basis_branches = (
        ("Contradiction", ContinuityFindingBasis.CONTRADICTION, ()),
        (
            "MissingRequirement",
            ContinuityFindingBasis.MISSING_REQUIREMENT,
            required_requirement_ids,
        ),
        (
            "ForbiddenShortcut",
            ContinuityFindingBasis.FORBIDDEN_SHORTCUT_VIOLATION,
            forbidden_requirement_ids,
        ),
    )
    branch_names: list[str] = []
    for basis_name, basis, requirement_ids in basis_branches:
        if basis is not ContinuityFindingBasis.CONTRADICTION and not requirement_ids:
            continue
        for category_scope, is_world_rule in (
            ("NonWorld", False),
            ("WorldRule", True),
        ):
            if is_world_rule and not continuity_model_context.world_rule_ids:
                continue
            branch_name = f"{phase_name}{basis_name}{category_scope}ContinuityFinding"
            definitions[branch_name] = _continuity_finding_branch_schema(
                finding_schema,
                title=branch_name,
                severities=("error", "blocking"),
                basis=basis,
                require_resolution=True,
                require_recheck_analysis=is_recheck,
                model_context=continuity_model_context,
                requirement_ids=requirement_ids,
                is_world_rule=is_world_rule,
            )
            branch_names.append(branch_name)
    definitions[advisory_name] = _continuity_finding_branch_schema(
        finding_schema,
        title=advisory_name,
        severities=("info", "warning"),
        basis=None,
        require_resolution=False,
        require_recheck_analysis=False,
        model_context=continuity_model_context,
    )
    branch_names.append(advisory_name)
    findings_schema["items"] = {
        "anyOf": [{"$ref": f"#/$defs/{branch_name}"} for branch_name in branch_names]
    }
    definitions.pop("ContinuityFinding", None)
    definitions.pop("ContinuityFindingBasis", None)
    definitions.pop("ContinuitySeverity", None)
    if not is_recheck:
        definitions.pop("ContinuityRecheckDisposition", None)
    schema["title"] = f"{phase_name}ContinuityReport"
    return schema


def _continuity_finding_branch_schema(
    canonical_schema: Mapping[str, Any],
    *,
    title: str,
    severities: tuple[str, str],
    basis: ContinuityFindingBasis | None,
    require_resolution: bool,
    require_recheck_analysis: bool,
    model_context: _ContinuityModelContext,
    requirement_ids: tuple[str, ...] = (),
    is_world_rule: bool | None = None,
) -> dict[str, Any]:
    """Create one unambiguous model-facing continuity-finding branch."""
    branch = deepcopy(dict(canonical_schema))
    properties = branch.get("properties")
    required = branch.get("required")
    if not isinstance(properties, dict) or not isinstance(required, list):
        raise SceneProductionError("continuity finding branch schema is invalid")

    properties.pop("blocks_approval", None)
    properties["severity"] = {
        "type": "string",
        "enum": list(severities),
        "title": "Severity",
    }
    basis_fields = {
        "basis",
        "canonical_source_refs",
        "requirement_id",
        "coverage_assessment",
    }
    for field_name in (
        _CONTINUITY_RECHECK_ONLY_FIELDS
        | _CONTINUITY_MODEL_EVIDENCE_FIELDS
        | basis_fields
        | {"evidence"}
    ):
        properties.pop(field_name, None)
    branch["required"] = [
        field_name
        for field_name in required
        if field_name != "blocks_approval"
        and field_name not in _CONTINUITY_RECHECK_ONLY_FIELDS
        and field_name not in _CONTINUITY_MODEL_EVIDENCE_FIELDS
        and field_name not in basis_fields
        and field_name != "evidence"
    ]

    if basis is None:
        if is_world_rule is not None:
            raise SceneProductionError("advisory continuity branch cannot select a category scope")
        for field_name in (
            "world_rule_ids",
            "companion_rule_assessment",
            "condition_explicitly_authorized",
        ):
            properties.pop(field_name, None)
    else:
        properties["basis"] = {
            "type": "string",
            "const": basis.value,
            "title": "Basis",
        }
        branch["required"].append("basis")
        if is_world_rule is None:
            raise SceneProductionError("blocking continuity branch requires a category scope")
        if is_world_rule:
            properties["category"] = {
                "type": "string",
                "const": ContinuityCategory.WORLD_RULE.value,
                "title": "Category",
            }
            properties["world_rule_ids"] = {
                "type": "array",
                "items": {"type": "string", "enum": list(model_context.world_rule_ids)},
                "minItems": 1,
                "title": "World Rule Ids",
            }
            properties["companion_rule_assessment"] = {
                "type": "string",
                "minLength": 1,
                "title": "Companion Rule Assessment",
            }
            properties["condition_explicitly_authorized"] = {
                "type": "boolean",
                "const": False,
                "title": "Condition Explicitly Authorized",
            }
            branch["required"].extend(
                (
                    "world_rule_ids",
                    "companion_rule_assessment",
                    "condition_explicitly_authorized",
                )
            )
        else:
            properties["category"] = {
                "type": "string",
                "enum": [
                    category.value
                    for category in ContinuityCategory
                    if category is not ContinuityCategory.WORLD_RULE
                ],
                "title": "Category",
            }
            for field_name in (
                "world_rule_ids",
                "companion_rule_assessment",
                "condition_explicitly_authorized",
            ):
                properties.pop(field_name, None)
        if basis is ContinuityFindingBasis.CONTRADICTION:
            evidence_field = (
                "revised_draft_evidence_refs" if require_recheck_analysis else "draft_evidence_refs"
            )
            properties[evidence_field] = {
                "type": "array",
                "items": {"type": "string", "enum": list(model_context.evidence_refs)},
                "minItems": 1,
                "maxItems": _MAX_EVIDENCE_REFS_PER_FINDING,
                "title": (
                    "Revised Draft Evidence Refs"
                    if require_recheck_analysis
                    else "Draft Evidence Refs"
                ),
            }
            properties["canonical_source_refs"] = {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": list(model_context.canonical_source_refs),
                },
                "minItems": 1,
                "maxItems": _MAX_CANONICAL_SOURCE_REFS_PER_FINDING,
                "title": "Canonical Source Refs",
            }
            branch["required"].extend((evidence_field, "canonical_source_refs"))
        elif basis is ContinuityFindingBasis.MISSING_REQUIREMENT:
            properties["requirement_id"] = {
                "type": "string",
                "enum": list(requirement_ids),
                "title": "Requirement Id",
            }
            properties["coverage_assessment"] = {
                "type": "string",
                "minLength": 1,
                "title": "Coverage Assessment",
            }
            branch["required"].extend(("requirement_id", "coverage_assessment"))
        else:
            evidence_field = (
                "revised_draft_evidence_refs" if require_recheck_analysis else "draft_evidence_refs"
            )
            properties[evidence_field] = {
                "type": "array",
                "items": {"type": "string", "enum": list(model_context.evidence_refs)},
                "minItems": 1,
                "maxItems": _MAX_EVIDENCE_REFS_PER_FINDING,
                "title": (
                    "Revised Draft Evidence Refs"
                    if require_recheck_analysis
                    else "Draft Evidence Refs"
                ),
            }
            properties["requirement_id"] = {
                "type": "string",
                "enum": list(requirement_ids),
                "title": "Requirement Id",
            }
            branch["required"].extend((evidence_field, "requirement_id"))

    if require_resolution:
        properties["recommended_resolution"] = {
            "type": "string",
            "minLength": 1,
            "title": "Recommended Resolution",
        }
        branch["required"].append("recommended_resolution")
    if require_recheck_analysis:
        properties["recheck_disposition"] = {"$ref": "#/$defs/ContinuityRecheckDisposition"}
        properties["repair_assessment"] = {
            "type": "string",
            "minLength": 1,
            "title": "Repair Assessment",
        }
        branch["required"].extend(("recheck_disposition", "repair_assessment"))
    branch["title"] = title
    return branch


def _select_production_model(
    *,
    operation: _Operation,
    specialist_role: str,
    configuration: ModelProfileConfiguration,
    attempt_number: int,
    previous_failure: Mapping[str, object] | None,
) -> tuple[ModelSelection, tuple[dict[str, object], ...]]:
    """Escalate only a persisted Hybrid continuity-stagnation retry to cloud."""
    primary = configuration.selection_for(specialist_role)
    should_escalate = (
        operation is _Operation.CONTINUITY
        and specialist_role == "continuity_supervisor"
        and configuration.mode is ModelProfileMode.HYBRID
        and primary.deployment is ModelDeployment.LOCAL
        and previous_failure is not None
        and previous_failure.get("error_code") == _CONTINUITY_RECHECK_STAGNATION_ERROR_CODE
    )
    if not should_escalate:
        return primary, ()

    cloud = configuration.models[ModelDeployment.CLOUD]
    if cloud is None:
        raise SceneProductionError(
            "Hybrid continuity escalation requires the frozen cloud model selection"
        )
    fallback = {
        "reason": _CONTINUITY_RECHECK_STAGNATION_ERROR_CODE,
        "attempt_number": attempt_number,
        "from_provider": primary.provider,
        "from_model_identifier": primary.model_identifier,
        "from_deployment": primary.deployment.value,
        "to_provider": cloud.provider,
        "to_model_identifier": cloud.model_identifier,
        "to_deployment": cloud.deployment.value,
    }
    return cloud, (fallback,)


def _local_schema_repair_guidance(
    *,
    operation: _Operation,
    deployment: ModelDeployment,
    previous_failure: Mapping[str, object] | None,
    continuity_schema_variant: _ContinuitySchemaVariant | None = None,
) -> dict[str, object] | None:
    """Build a concise repair-only packet for a failed Local structured call."""
    if (
        deployment is not ModelDeployment.LOCAL
        or previous_failure is None
        or previous_failure.get("error_code")
        not in {"schema_validation_failed", _CONTINUITY_RECHECK_STAGNATION_ERROR_CODE}
    ):
        return None

    focus_locations: list[str] = []
    validation_issues = previous_failure.get("validation_issues")
    if isinstance(validation_issues, list):
        for issue in validation_issues:
            if not isinstance(issue, dict):
                continue
            location = issue.get("location")
            if isinstance(location, str) and location not in focus_locations:
                focus_locations.append(location)
    if not focus_locations:
        focus_locations.append("$")

    operation_rules = list(_LOCAL_SCHEMA_REPAIR_OPERATION_RULES[operation])
    if operation is _Operation.CONTINUITY:
        if continuity_schema_variant is _ContinuitySchemaVariant.INITIAL_CHECK:
            operation_rules.insert(
                0,
                "This is an initial check. The supplied schema has no re-check fields; "
                "do not add undeclared recheck_disposition, repair_assessment, or "
                "revised_evidence fields.",
            )
        elif continuity_schema_variant is _ContinuitySchemaVariant.RECHECK:
            operation_rules.insert(
                0,
                "This is a re-check. An unresolved prior or newly exposed error/blocking "
                "finding must supply recheck_disposition and repair_assessment. Contradiction "
                "and forbidden-shortcut bases also require non-empty "
                "revised_draft_evidence_refs selected from the candidate draft; a "
                "missing-requirement basis requires fresh coverage_assessment and must omit "
                "draft evidence references. Info and warning findings must not use re-check "
                "fields.",
            )
        else:
            raise ValueError("continuity repair guidance requires a schema variant")

    guidance: dict[str, object] = {
        "policy_version": "1",
        "mode": "repair_only",
        "focus_locations": focus_locations,
        "common_rules": list(_LOCAL_SCHEMA_REPAIR_COMMON_RULES),
        "operation_rules": operation_rules,
    }
    if continuity_schema_variant is not None:
        guidance["schema_variant"] = continuity_schema_variant.value
    return guidance


def _messages(
    operation: _Operation,
    execution: _Execution,
    schema: dict[str, Any],
    *,
    continuity_schema_variant: _ContinuitySchemaVariant | None,
    continuity_model_context: _ContinuityModelContext | None,
) -> tuple[ModelMessage, ...]:
    local_schema_repair = _local_schema_repair_guidance(
        operation=operation,
        deployment=execution.selection.deployment,
        previous_failure=execution.previous_failure,
        continuity_schema_variant=continuity_schema_variant,
    )
    system = (
        "You are a registered Open Hollywood scene-production specialist. "
        f"{_INSTRUCTIONS[operation]} Return only one JSON value conforming exactly "
        "to the supplied schema. Do not include Markdown, commentary, hidden reasoning, "
        "or undeclared fields. If retry_context is present, correct every reported "
        "structural error without changing the assignment or inventing new lineage."
        + (
            " This is a Local structured-output repair attempt. Follow "
            "local_schema_repair exactly, prioritize its focus locations, and return the "
            "entire corrected object once."
            if local_schema_repair is not None
            else ""
        )
    )
    payload: dict[str, object] = {
        "assignment": {
            "operation": operation.value,
            "specialist_role": execution.specialist_role,
            "unit_id": execution.unit_id,
            "unit_number": execution.unit_number,
            "unit_count": execution.unit_count,
            "revision_number": execution.revision_number,
        },
        "input_artifacts": execution.inputs,
        "output_schema": schema,
    }
    if operation is _Operation.CONTINUITY:
        if continuity_schema_variant is None:
            raise ValueError("continuity messages require a schema variant")
        if continuity_model_context is None:
            raise ValueError("continuity messages require their exact model context")
        scene_plan = _continuity_scene_plan(execution)
        scene_plan_applicability = _scene_plan_requirement_applicability(
            execution.constraints,
            scene_plan,
            unit_number=execution.unit_number,
            unit_count=execution.unit_count,
        )
        benchmark_applicability = _benchmark_constraint_applicability(
            execution.constraints,
            unit_number=execution.unit_number,
            unit_count=execution.unit_count,
        )
        payload.pop("input_artifacts", None)
        payload["candidate_draft"] = continuity_model_context.candidate_draft
        payload["accepted_prior_drafts"] = continuity_model_context.accepted_prior_drafts
        if continuity_model_context.previous_continuity_report is not None:
            payload["previous_continuity_report"] = (
                continuity_model_context.previous_continuity_report
            )
        payload["output_schema_variant"] = continuity_schema_variant.value
        payload["benchmark_constraint_applicability"] = benchmark_applicability
        payload["scene_plan_requirement_applicability"] = scene_plan_applicability
        payload["canonical_source_catalog"] = continuity_model_context.canonical_source_catalog
        output_requirements = {
            "continuity_finding_resolution": (_CONTINUITY_FINDING_RESOLUTION_REQUIREMENT),
            "continuity_finding_basis": _CONTINUITY_FINDING_BASIS_REQUIREMENT,
            "world_rule_blockers": _CONTINUITY_WORLD_RULE_REQUIREMENT,
            "requirement_scope": _CONTINUITY_REQUIREMENT_SCOPE,
        }
        if continuity_model_context.previous_continuity_report is not None:
            output_requirements["recheck_analysis"] = _CONTINUITY_RECHECK_REQUIREMENT
            payload["continuity_recheck"] = {
                "previous_report_version_id": continuity_model_context.previous_continuity_report[
                    "artifact_version_id"
                ],
                "verification_contract": _CONTINUITY_RECHECK_REQUIREMENT,
            }
        payload["output_requirements"] = output_requirements
    else:
        payload["frozen_benchmark_constraints"] = execution.constraints
    if execution.previous_failure is not None:
        retry_context = dict(execution.previous_failure)
        if operation is _Operation.CONTINUITY:
            if continuity_model_context is None:
                raise ValueError("continuity retry requires its exact model context")
            requirements = [
                _CONTINUITY_FINDING_RESOLUTION_REQUIREMENT,
                _CONTINUITY_FINDING_BASIS_REQUIREMENT,
                _CONTINUITY_WORLD_RULE_REQUIREMENT,
            ]
            if continuity_model_context.previous_continuity_report is not None:
                requirements.append(_CONTINUITY_RECHECK_REQUIREMENT)
            retry_context["required_correction"] = " ".join(requirements)
        payload["retry_context"] = retry_context
    if local_schema_repair is not None:
        payload["local_schema_repair"] = local_schema_repair
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


def _benchmark_constraint_applicability(
    constraints: Mapping[str, object],
    *,
    unit_number: int,
    unit_count: int,
) -> dict[str, object]:
    """Expose story-wide benchmark text only when the final scene is evaluated."""
    if unit_number < 1 or unit_count < 1 or unit_number > unit_count:
        raise SceneProductionError("continuity assignment has invalid scene bounds")

    entries: list[dict[str, str]] = []
    for kind, key in (
        ("required_element", "required_elements"),
        ("forbidden_shortcut", "forbidden_shortcuts"),
    ):
        values = constraints.get(key)
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise SceneProductionError(f"benchmark {key} must be a list of text values")
        entries.extend(
            {
                "id": f"{kind}_{index}",
                "kind": kind,
                "text": value,
            }
            for index, value in enumerate(values, start=1)
        )

    is_final_scene = unit_number == unit_count
    return {
        "policy_version": "1",
        "current_scene_number": unit_number,
        "final_scene_number": unit_count,
        "is_final_scene": is_final_scene,
        "due_now": entries if is_final_scene else [],
        "deferred_until_final_scene": (
            []
            if is_final_scene
            else [{"id": entry["id"], "kind": entry["kind"]} for entry in entries]
        ),
        "deferred_text_intentionally_omitted": not is_final_scene,
        "forbidden_shortcut_semantics": (
            "A forbidden shortcut is violated only when the completed story adopts it as "
            "the actual explanation or resolution, not when a character temporarily "
            "considers and later rejects it."
        ),
    }


def _scene_plan_requirement_applicability(
    constraints: Mapping[str, object],
    scene_plan: Mapping[str, object],
    *,
    unit_number: int,
    unit_count: int,
) -> dict[str, object]:
    """Keep duplicated story-wide requirements deferred in non-final Scene Plans."""
    if unit_number < 1 or unit_count < 1 or unit_number > unit_count:
        raise SceneProductionError("continuity assignment has invalid scene bounds")
    required_elements = scene_plan.get("required_elements")
    if not isinstance(required_elements, list) or any(
        not isinstance(value, str) for value in required_elements
    ):
        raise SceneProductionError("Scene Plan required_elements must be a list of text values")
    benchmark_required = constraints.get("required_elements")
    if not isinstance(benchmark_required, list) or any(
        not isinstance(value, str) for value in benchmark_required
    ):
        raise SceneProductionError("benchmark required_elements must be a list of text values")

    benchmark_ids = {
        text: f"required_element_{index}" for index, text in enumerate(benchmark_required, start=1)
    }
    is_final_scene = unit_number == unit_count
    due_now: list[dict[str, object]] = []
    deferred: list[dict[str, object]] = []
    for index, text in enumerate(required_elements, start=1):
        entry_id = f"scene_plan_required_element_{index}"
        benchmark_id = benchmark_ids.get(text)
        if not is_final_scene and benchmark_id is not None:
            deferred.append(
                {
                    "id": entry_id,
                    "matched_benchmark_requirement_id": benchmark_id,
                }
            )
        else:
            due_now.append({"id": entry_id, "text": text})
    return {
        "policy_version": "1",
        "current_scene_number": unit_number,
        "final_scene_number": unit_count,
        "is_final_scene": is_final_scene,
        "due_now": due_now,
        "deferred_until_final_scene": deferred,
        "deferred_text_intentionally_omitted": bool(deferred),
    }


def _continuity_scene_plan(execution: _Execution) -> dict[str, Any]:
    plans = tuple(
        item.get("content")
        for item in execution.inputs
        if item.get("artifact_kind") == ArtifactKind.SCENE_PLAN.value
    )
    if len(plans) != 1 or not isinstance(plans[0], dict):
        raise SceneProductionError("continuity call requires one valid Scene Plan input")
    return plans[0]


def _continuity_prompt_inputs(
    inputs: tuple[dict[str, Any], ...],
    scene_plan_applicability: Mapping[str, object],
) -> tuple[dict[str, Any], ...]:
    """Compile a prompt view that cannot expose deferred Scene Plan requirement text."""
    due_now = scene_plan_applicability.get("due_now")
    if not isinstance(due_now, list):
        raise SceneProductionError("Scene Plan requirement applicability is invalid")
    due_text = {
        entry["text"]
        for entry in due_now
        if isinstance(entry, dict) and isinstance(entry.get("text"), str)
    }
    prompt_inputs = deepcopy(inputs)
    for item in prompt_inputs:
        if item.get("artifact_kind") != ArtifactKind.SCENE_PLAN.value:
            continue
        content = item.get("content")
        if not isinstance(content, dict):
            raise SceneProductionError("continuity Scene Plan prompt input is invalid")
        required_elements = content.get("required_elements")
        if not isinstance(required_elements, list):
            raise SceneProductionError("continuity Scene Plan requirements are invalid")
        content["required_elements"] = [value for value in required_elements if value in due_text]
    return prompt_inputs


def _continuity_model_context(execution: _Execution) -> _ContinuityModelContext:
    """Compile one unambiguous, bounded prompt view for a continuity call."""
    scene_plan_applicability = _scene_plan_requirement_applicability(
        execution.constraints,
        _continuity_scene_plan(execution),
        unit_number=execution.unit_number,
        unit_count=execution.unit_count,
    )
    prompt_inputs = _continuity_prompt_inputs(execution.inputs, scene_plan_applicability)
    candidate = _continuity_candidate_draft(execution, prompt_inputs)
    prior_drafts = tuple(
        {
            **item,
            "continuity_role": "accepted_prior_draft_context_not_valid_evidence",
        }
        for item in prompt_inputs
        if item.get("artifact_kind") == ArtifactKind.SCENE_DRAFT.value
        and item.get("artifact_version_id") != candidate.get("artifact_version_id")
    )
    prior_reports = tuple(
        item
        for item in prompt_inputs
        if item.get("artifact_kind") == ArtifactKind.CONTINUITY_REPORT.value
    )
    if len(prior_reports) > 1:
        raise SceneProductionError("continuity re-check requires at most one prior report")
    canonical_inputs = tuple(
        _bounded_continuity_canonical_input(item, execution)
        for item in prompt_inputs
        if item.get("artifact_kind")
        not in {
            ArtifactKind.SCENE_DRAFT.value,
            ArtifactKind.CRITIQUE.value,
            ArtifactKind.CONTINUITY_REPORT.value,
        }
    )
    return _ContinuityModelContext(
        candidate_draft=candidate,
        accepted_prior_drafts=prior_drafts,
        previous_continuity_report=prior_reports[0] if prior_reports else None,
        canonical_source_catalog=_continuity_canonical_source_catalog(canonical_inputs),
        requirement_kinds=_continuity_due_requirement_kinds(execution),
        world_rule_ids=tuple(sorted(_continuity_world_rule_ids(execution.inputs))),
    )


def _continuity_candidate_draft(
    execution: _Execution,
    prompt_inputs: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    candidates = tuple(
        item
        for item in prompt_inputs
        if item.get("artifact_kind") == ArtifactKind.SCENE_DRAFT.value
        and isinstance(item.get("content"), dict)
        and item["content"].get("scene_id") == execution.unit_id
        and item["content"].get("revision_number") == execution.revision_number
    )
    if len(candidates) != 1:
        raise SceneProductionError("continuity call requires one exact candidate draft")
    candidate = deepcopy(candidates[0])
    content = candidate.get("content")
    if not isinstance(content, dict) or not isinstance(content.get("prose"), str):
        raise SceneProductionError("continuity candidate draft prose is invalid")
    prose = cast(str, content.pop("prose"))
    content["evidence_catalog"] = list(_draft_evidence_catalog(prose))
    candidate["continuity_role"] = "candidate_draft_and_only_valid_evidence_source"
    return candidate


def _draft_evidence_catalog(prose: str) -> tuple[dict[str, str], ...]:
    """Split prose into exact deterministic excerpts that a model selects by ID."""
    excerpts: list[str] = []
    for paragraph in re.split(r"\n\s*\n", prose):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        matches = tuple(
            match.group(0).strip()
            for match in re.finditer(
                r".+?(?:[.!?…]+[\"'’”\)\]]*(?=\s+|$)|$)",
                paragraph,
                flags=re.DOTALL,
            )
            if match.group(0).strip()
        )
        excerpts.extend(matches or (paragraph,))
    if not excerpts:
        raise SceneProductionError("continuity candidate draft has no evidence excerpts")
    return tuple(
        {
            "evidence_ref": f"draft_evidence_{index:04d}",
            "exact_excerpt": excerpt,
        }
        for index, excerpt in enumerate(excerpts, start=1)
    )


def _bounded_continuity_canonical_input(
    item: dict[str, Any],
    execution: _Execution,
) -> dict[str, Any]:
    """Keep only the approved-Blueprint sections relevant to the candidate scene."""
    if item.get("artifact_kind") != ArtifactKind.STORY_BLUEPRINT.value:
        return item
    content = item.get("content")
    if not isinstance(content, dict):
        raise SceneProductionError("approved Blueprint continuity input is invalid")
    plan = _continuity_scene_plan(execution)
    character_ids = {value for value in plan.get("character_ids", []) if isinstance(value, str)}
    location_id = plan.get("location_id")
    beat_ids = {value for value in plan.get("beat_ids", []) if isinstance(value, str)}

    def matching(collection_name: str, predicate: Any) -> list[object]:
        collection = content.get(collection_name)
        if not isinstance(collection, list):
            return []
        return [entry for entry in collection if isinstance(entry, dict) and predicate(entry)]

    bounded = deepcopy(item)
    bounded["content"] = {
        "characters": matching("characters", lambda entry: entry.get("id") in character_ids),
        "relationships": matching(
            "relationships",
            lambda entry: (
                entry.get("source_character_id") in character_ids
                or entry.get("target_character_id") in character_ids
            ),
        ),
        "locations": matching("locations", lambda entry: entry.get("id") == location_id),
        # Every rule remains visible so a narrowly tagged companion rule or exception
        # can authorize a condition and prevent a false blocker.
        "world_rules": matching("world_rules", lambda entry: True),
        "beats": matching("beats", lambda entry: entry.get("id") in beat_ids),
    }
    return bounded


def _continuity_canonical_source_catalog(
    inputs: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], ...]:
    """Flatten semantic canonical claims into exact, provenance-bearing choices."""
    claims: list[dict[str, Any]] = []

    def walk(
        value: object,
        *,
        artifact: dict[str, Any],
        source_path: str,
        canonical_id: str | None,
        related_ids: tuple[str, ...],
        field_name: str | None = None,
    ) -> None:
        if isinstance(value, dict):
            local_id = next(
                (
                    candidate
                    for key in ("id", "character_id", "relationship_id", "location_id")
                    if isinstance((candidate := value.get(key)), str)
                    and _is_reference_id(candidate)
                ),
                canonical_id,
            )
            local_related = tuple(
                dict.fromkeys(
                    (
                        *related_ids,
                        *(
                            nested
                            for key, nested in value.items()
                            if key.endswith("_id")
                            and isinstance(nested, str)
                            and _is_reference_id(nested)
                        ),
                        *(
                            nested
                            for key, values in value.items()
                            if key.endswith("_ids") and isinstance(values, list)
                            for nested in values
                            if isinstance(nested, str) and _is_reference_id(nested)
                        ),
                    )
                )
            )
            for key, nested in value.items():
                walk(
                    nested,
                    artifact=artifact,
                    source_path=f"{source_path}.{key}",
                    canonical_id=local_id,
                    related_ids=local_related,
                    field_name=key,
                )
            return
        if isinstance(value, list):
            for index, nested in enumerate(value):
                walk(
                    nested,
                    artifact=artifact,
                    source_path=f"{source_path}[{index}]",
                    canonical_id=canonical_id,
                    related_ids=related_ids,
                    field_name=field_name,
                )
            return
        if (
            not isinstance(value, str)
            or not value.strip()
            or field_name is None
            or field_name == "id"
            or field_name.endswith("_id")
            or field_name.endswith("_ids")
        ):
            return
        reference_id = f"canonical_source_{len(claims) + 1:04d}"
        claim: dict[str, Any] = {
            "reference_id": reference_id,
            "artifact_kind": artifact["artifact_kind"],
            "artifact_key": artifact["artifact_key"],
            "artifact_version_id": artifact["artifact_version_id"],
            "source_path": source_path,
            "claim": value,
        }
        if canonical_id is not None:
            claim["canonical_id"] = canonical_id
        if related_ids:
            claim["related_ids"] = list(related_ids)
        claims.append(claim)

    for item in inputs:
        if not all(
            isinstance(item.get(field), str)
            for field in ("artifact_kind", "artifact_key", "artifact_version_id")
        ):
            raise SceneProductionError("continuity canonical input lineage is invalid")
        walk(
            item.get("content"),
            artifact=item,
            source_path="content",
            canonical_id=None,
            related_ids=(),
        )
    if not claims:
        raise SceneProductionError("continuity canonical source catalog is empty")
    return tuple(claims)


def _is_reference_id(value: str) -> bool:
    return (
        1 <= len(value) <= 100
        and "a" <= value[0] <= "z"
        and all(
            character.isdigit() or "a" <= character <= "z" or character in "_-"
            for character in value
        )
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


def _materialize_output_data(
    operation: _Operation,
    task: object,
    execution: _Execution,
    output_data: object,
) -> dict[str, Any]:
    """Attach application-owned identity and lineage to model-authored output."""
    if not isinstance(output_data, dict):
        raise ValueError("production specialist output must be a JSON object")
    materialized = dict(output_data)
    if operation is _Operation.WRITE:
        writing = cast(SceneWritingTask, task)
        materialized.update(
            scene_id=writing.unit.unit_id,
            scene_number=writing.unit.unit_number,
            revision_number=writing.revision_number,
        )
        return materialized
    if operation is _Operation.CRITIQUE:
        critique_task = cast(SceneCritiqueTask, task)
        materialized.update(
            target_artifact_kind=ArtifactKind.SCENE_DRAFT.value,
            target_artifact_key=critique_task.draft.artifact_key,
            target_artifact_version_id=str(critique_task.draft.version_id),
        )
        return materialized
    if operation is _Operation.CONTINUITY:
        continuity_task = cast(ContinuityCheckTask, task)
        scene_id = continuity_task.unit.unit_id
        materialized.update(
            story_bible_version_id=str(continuity_task.story_bible.version_id),
            scene_version_id=str(continuity_task.draft.version_id),
            scene_plan_version_id=str(continuity_task.unit.plan.version_id),
            scene_id=scene_id,
            scene_number=continuity_task.unit.unit_number,
            checked_categories=[category.value for category in ContinuityCategory],
        )
        findings = materialized.get("findings")
        if isinstance(findings, list):
            prior_resolutions = _prior_continuity_resolutions(execution)
            model_context = _continuity_model_context(execution)
            materialized_findings = [
                _materialize_continuity_finding(
                    _materialize_continuity_evidence(finding, model_context),
                    scene_id,
                    prior_resolutions=prior_resolutions,
                )
                for finding in findings
            ]
            _validate_continuity_finding_contract(materialized_findings, execution)
            _validate_continuity_recheck_analysis(materialized_findings, execution)
            materialized["findings"] = materialized_findings
        return materialized

    update_task = cast(StoryBibleUpdateTask, task)
    scene_id = update_task.unit.unit_id
    materialized.update(
        source_story_bible_version_id=str(update_task.source_story_bible.version_id),
        continuity_report_version_id=str(update_task.continuity_report.version_id),
    )
    accepted_scene = materialized.get("accepted_scene")
    if not isinstance(accepted_scene, dict):
        raise ValueError("story-bible update must contain accepted_scene")
    materialized["accepted_scene"] = {
        **accepted_scene,
        "scene_id": scene_id,
        "scene_number": update_task.unit.unit_number,
        "artifact_version_id": str(update_task.accepted_draft.version_id),
    }
    _materialize_scene_origin(materialized, "timeline_events", "scene_id", scene_id)
    source_story_bible = _source_story_bible(execution)
    timeline_events = materialized.get("timeline_events")
    if isinstance(timeline_events, list):
        materialized["timeline_events"] = [
            (
                {
                    **event,
                    "id": f"{scene_id}_timeline_event_{index}",
                    "sequence": len(source_story_bible.timeline) + index,
                }
                if isinstance(event, dict)
                else event
            )
            for index, event in enumerate(timeline_events, start=1)
        ]
    _materialize_scene_origin(
        materialized,
        "established_facts",
        "established_scene_id",
        scene_id,
    )
    established_facts = materialized.get("established_facts")
    fact_id_map: dict[str, str] = {}
    if isinstance(established_facts, list):
        for index, fact in enumerate(established_facts, start=1):
            if isinstance(fact, dict) and isinstance(fact.get("id"), str):
                fact_id_map[cast(str, fact["id"])] = f"{scene_id}_established_fact_{index}"
        materialized["established_facts"] = [
            (
                {**fact, "id": f"{scene_id}_established_fact_{index}"}
                if isinstance(fact, dict)
                else fact
            )
            for index, fact in enumerate(established_facts, start=1)
        ]
    for field_name in (
        "character_states",
        "relationship_states",
        "location_states",
    ):
        _materialize_scene_origin(
            materialized,
            field_name,
            "last_updated_scene_id",
            scene_id,
        )
    character_states = materialized.get("character_states")
    if isinstance(character_states, list):
        materialized["character_states"] = [
            _materialize_character_state(state, fact_id_map) for state in character_states
        ]
    thread_changes = materialized.get("thread_changes")
    if isinstance(thread_changes, list):
        current_threads = {thread.id: thread for thread in source_story_bible.threads}
        materialized["thread_changes"] = [
            _materialize_thread_change(change, scene_id, current_threads)
            for change in thread_changes
        ]
    contradictions = materialized.get("prohibited_contradictions")
    if isinstance(contradictions, list):
        materialized["prohibited_contradictions"] = _new_prohibitions(
            contradictions,
            source_story_bible.prohibited_contradictions,
        )
    return materialized


def _source_story_bible(execution: _Execution) -> StoryBible:
    story_bibles = [
        item.get("content")
        for item in execution.inputs
        if item.get("artifact_kind") == ArtifactKind.STORY_BIBLE.value
    ]
    if len(story_bibles) != 1:
        raise ValueError("story-bible update requires one exact source story bible")
    return StoryBible.model_validate(story_bibles[0])


def _materialize_character_state(
    state: object,
    fact_id_map: Mapping[str, str],
) -> object:
    if not isinstance(state, dict):
        return state
    knowledge_fact_ids = state.get("knowledge_fact_ids")
    if not isinstance(knowledge_fact_ids, list):
        return state
    return {
        **state,
        "knowledge_fact_ids": [
            fact_id_map.get(fact_id, fact_id) if isinstance(fact_id, str) else fact_id
            for fact_id in knowledge_fact_ids
        ],
    }


def _materialize_thread_change(
    change: object,
    scene_id: str,
    current_threads: Mapping[str, StoryBibleThread],
) -> object:
    if not isinstance(change, dict):
        return change
    materialized = dict(change)
    thread_id = change.get("id")
    existing = current_threads.get(thread_id) if isinstance(thread_id, str) else None
    if existing is None:
        materialized["introduced_scene_id"] = scene_id
    else:
        existing_data = existing.model_dump(mode="json")
        materialized.update(
            kind=existing_data["kind"],
            statement=existing_data["statement"],
            introduced_scene_id=existing_data["introduced_scene_id"],
        )
    if change.get("resolved_scene_id") is not None:
        materialized["resolved_scene_id"] = scene_id
    return materialized


def _new_prohibitions(
    proposed: list[object],
    existing: tuple[str, ...],
) -> list[object]:
    seen = set(existing)
    materialized: list[object] = []
    for contradiction in proposed:
        if not isinstance(contradiction, str):
            materialized.append(contradiction)
        elif contradiction not in seen:
            seen.add(contradiction)
            materialized.append(contradiction)
    return materialized


def _prior_continuity_resolutions(execution: _Execution) -> dict[str, str]:
    """Return exact repair text from the single prior continuity report, if any."""
    report = _prior_continuity_report(execution)
    if report is None:
        return {}
    findings = report.get("findings")
    if not isinstance(findings, list):
        raise ValueError("prior continuity report findings are invalid")
    resolutions: dict[str, str] = {}
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        finding_id = finding.get("id")
        resolution = finding.get("recommended_resolution")
        if (
            finding.get("severity") in {"error", "blocking"}
            and isinstance(finding_id, str)
            and isinstance(resolution, str)
            and resolution.strip()
        ):
            resolutions[finding_id] = resolution
    return resolutions


def _validate_continuity_finding_contract(
    findings: list[object],
    execution: _Execution,
) -> None:
    """Enforce canonical evidence, source, requirement, and world-rule guarantees."""
    draft_prose = _current_scene_draft_prose(execution)
    source_refs = set(_continuity_model_context(execution).canonical_source_refs)
    requirement_kinds = _continuity_due_requirement_kinds(execution)
    world_rule_ids = _continuity_world_rule_ids(execution.inputs)
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        severity = finding.get("severity")
        basis = finding.get("basis")
        location = f"findings.{index}"
        if severity not in {"error", "blocking"}:
            if basis is not None:
                raise _StructuredOutputContractError(
                    f"{location}.basis",
                    "advisory continuity findings cannot use a blocking basis",
                )
            if finding.get("evidence") not in (None, []):
                raise _StructuredOutputContractError(
                    f"{location}.evidence",
                    "advisory continuity findings cannot emit draft evidence",
                )
            continue
        if basis not in {item.value for item in ContinuityFindingBasis}:
            raise _StructuredOutputContractError(
                f"{location}.basis",
                "error or blocking continuity findings require one declared basis",
            )

        evidence = finding.get("evidence")
        if basis == ContinuityFindingBasis.MISSING_REQUIREMENT.value:
            if evidence not in (None, []):
                raise _StructuredOutputContractError(
                    f"{location}.evidence",
                    "a missing requirement cannot cite or fabricate a draft excerpt",
                )
        elif (
            not isinstance(evidence, list)
            or not evidence
            or any(
                not isinstance(excerpt, str) or excerpt not in draft_prose for excerpt in evidence
            )
        ):
            raise _StructuredOutputContractError(
                f"{location}.evidence",
                "finding evidence must contain exact excerpts from the current draft",
            )

        if basis == ContinuityFindingBasis.CONTRADICTION.value:
            references = finding.get("canonical_source_refs")
            if (
                not isinstance(references, list)
                or not references
                or any(reference not in source_refs for reference in references)
            ):
                raise _StructuredOutputContractError(
                    f"{location}.canonical_source_refs",
                    "contradiction sources must be copied from canonical_source_catalog",
                )
        else:
            requirement_id = finding.get("requirement_id")
            expected_kind = (
                "required_element"
                if basis == ContinuityFindingBasis.MISSING_REQUIREMENT.value
                else "forbidden_shortcut"
            )
            if (
                not isinstance(requirement_id, str)
                or requirement_kinds.get(requirement_id) != expected_kind
            ):
                raise _StructuredOutputContractError(
                    f"{location}.requirement_id",
                    f"finding requires an exact due-now {expected_kind} ID",
                )
            if basis == ContinuityFindingBasis.MISSING_REQUIREMENT.value and not isinstance(
                finding.get("coverage_assessment"), str
            ):
                raise _StructuredOutputContractError(
                    f"{location}.coverage_assessment",
                    "a missing requirement requires a coverage assessment",
                )

        if finding.get("category") == ContinuityCategory.WORLD_RULE.value:
            cited_rule_ids = finding.get("world_rule_ids")
            if (
                not isinstance(cited_rule_ids, list)
                or not cited_rule_ids
                or any(rule_id not in world_rule_ids for rule_id in cited_rule_ids)
            ):
                raise _StructuredOutputContractError(
                    f"{location}.world_rule_ids",
                    "world-rule findings require exact canonical World Rule IDs",
                )
            if not isinstance(finding.get("companion_rule_assessment"), str):
                raise _StructuredOutputContractError(
                    f"{location}.companion_rule_assessment",
                    "world-rule findings must assess companion rules and exceptions",
                )
            if finding.get("condition_explicitly_authorized") is not False:
                raise _StructuredOutputContractError(
                    f"{location}.condition_explicitly_authorized",
                    "an explicitly authorized or unevaluated world condition cannot block",
                )


def _continuity_due_requirement_kinds(execution: _Execution) -> dict[str, str]:
    benchmark = _benchmark_constraint_applicability(
        execution.constraints,
        unit_number=execution.unit_number,
        unit_count=execution.unit_count,
    )
    scene_plan = _scene_plan_requirement_applicability(
        execution.constraints,
        _continuity_scene_plan(execution),
        unit_number=execution.unit_number,
        unit_count=execution.unit_count,
    )
    kinds: dict[str, str] = {}
    benchmark_due = benchmark.get("due_now")
    scene_plan_due = scene_plan.get("due_now")
    if not isinstance(benchmark_due, list) or not isinstance(scene_plan_due, list):
        raise SceneProductionError("continuity requirement applicability is invalid")
    for entry in benchmark_due:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            kinds[entry["id"]] = cast(str, entry["kind"])
    for entry in scene_plan_due:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            kinds[entry["id"]] = "required_element"
    return kinds


def _continuity_world_rule_ids(inputs: tuple[dict[str, Any], ...]) -> set[str]:
    rule_ids: set[str] = set()
    for item in inputs:
        content = item.get("content")
        if not isinstance(content, dict):
            continue
        if item.get("artifact_kind") == ArtifactKind.WORLD_RULE.value:
            rule_id = content.get("id")
            if isinstance(rule_id, str):
                rule_ids.add(rule_id)
        if item.get("artifact_kind") == ArtifactKind.STORY_BLUEPRINT.value:
            rules = content.get("world_rules")
            if isinstance(rules, list):
                rule_ids.update(
                    rule["id"]
                    for rule in rules
                    if isinstance(rule, dict) and isinstance(rule.get("id"), str)
                )
    return rule_ids


def _validate_continuity_recheck_analysis(
    findings: list[object],
    execution: _Execution,
) -> None:
    prior_report = _prior_continuity_report(execution)
    if prior_report is None:
        unexpected_ids = tuple(
            finding["id"]
            for finding in findings
            if isinstance(finding, dict)
            and isinstance(finding.get("id"), str)
            and any(
                (
                    finding.get("recheck_disposition") is not None,
                    finding.get("repair_assessment") is not None,
                    bool(finding.get("revised_evidence")),
                )
            )
        )
        if unexpected_ids:
            raise _StructuredOutputContractError(
                "findings",
                "initial continuity findings cannot contain re-check analysis: "
                f"{list(unexpected_ids)}",
            )
        return
    invalid_ids = _invalid_continuity_recheck_finding_ids(
        findings,
        prior_report,
        revised_draft_prose=_current_scene_draft_prose(execution),
    )
    if invalid_ids:
        raise ContinuityRecheckStagnationError(
            "continuity re-check findings lack fresh, exact revised-draft analysis: "
            f"{list(invalid_ids)}; set recheck_disposition to still_blocking for preserved "
            "IDs or newly_exposed for new IDs, and supply repair_assessment plus exact "
            "revised_evidence excerpts; when evidence changes, reassess it instead of "
            "copying the prior judgment"
        )


def _prior_continuity_report(execution: _Execution) -> dict[str, Any] | None:
    reports = tuple(
        item.get("content")
        for item in execution.inputs
        if item.get("artifact_kind") == ArtifactKind.CONTINUITY_REPORT.value
    )
    if len(reports) > 1:
        raise ValueError("continuity re-check requires at most one prior report")
    if not reports:
        return None
    report = reports[0]
    if not isinstance(report, dict):
        raise ValueError("prior continuity report content is invalid")
    return report


def _invalid_continuity_recheck_finding_ids(
    findings: list[object],
    prior_report: Mapping[str, object],
    *,
    revised_draft_prose: str | None = None,
) -> tuple[str, ...]:
    prior_findings = prior_report.get("findings")
    if not isinstance(prior_findings, list):
        raise ValueError("prior continuity report findings are invalid")
    prior_by_id = {
        finding["id"]: finding
        for finding in prior_findings
        if isinstance(finding, dict)
        and isinstance(finding.get("id"), str)
        and finding.get("severity") in {"error", "blocking"}
    }
    invalid: list[str] = []
    for finding in findings:
        if (
            not isinstance(finding, dict)
            or finding.get("severity") not in {"error", "blocking"}
            or not isinstance(finding.get("id"), str)
        ):
            continue
        finding_id = cast(str, finding["id"])
        expected_disposition = (
            ContinuityRecheckDisposition.STILL_BLOCKING.value
            if finding_id in prior_by_id
            else ContinuityRecheckDisposition.NEWLY_EXPOSED.value
        )
        revised_evidence = finding.get("revised_evidence")
        repair_assessment = finding.get("repair_assessment")
        is_missing_requirement = (
            finding.get("basis") == ContinuityFindingBasis.MISSING_REQUIREMENT.value
        )
        structurally_invalid = (
            finding.get("recheck_disposition") != expected_disposition
            or not isinstance(repair_assessment, str)
            or not repair_assessment.strip()
            or (
                is_missing_requirement
                and (
                    revised_evidence not in (None, [])
                    or not isinstance(finding.get("coverage_assessment"), str)
                    or not cast(str, finding["coverage_assessment"]).strip()
                )
            )
            or (
                not is_missing_requirement
                and (
                    not isinstance(revised_evidence, list)
                    or not revised_evidence
                    or any(
                        not isinstance(item, str) or not item.strip() for item in revised_evidence
                    )
                )
            )
        )
        if structurally_invalid:
            invalid.append(finding_id)
            continue
        if is_missing_requirement:
            prior_finding = prior_by_id.get(finding_id)
            if prior_finding is not None and (
                finding.get("coverage_assessment") == prior_finding.get("coverage_assessment")
                and finding.get("repair_assessment") == prior_finding.get("repair_assessment")
            ):
                invalid.append(finding_id)
            continue
        exact_evidence = cast(list[str], revised_evidence)
        if revised_draft_prose is not None and any(
            excerpt not in revised_draft_prose for excerpt in exact_evidence
        ):
            invalid.append(finding_id)
            continue

        prior_finding = prior_by_id.get(finding_id)
        if prior_finding is None:
            continue
        prior_revised_evidence = prior_finding.get("revised_evidence")
        comparison_evidence = (
            prior_revised_evidence
            if isinstance(prior_revised_evidence, list) and prior_revised_evidence
            else prior_finding.get("evidence")
        )
        prior_assessment = prior_finding.get("repair_assessment")
        if exact_evidence == comparison_evidence:
            if not _assessment_explains_unchanged(cast(str, repair_assessment)):
                invalid.append(finding_id)
        elif (
            isinstance(prior_assessment, str)
            and cast(str, repair_assessment).strip() == prior_assessment.strip()
        ):
            invalid.append(finding_id)
    return tuple(invalid)


def _current_scene_draft_prose(execution: _Execution) -> str:
    drafts = tuple(
        content
        for item in execution.inputs
        if item.get("artifact_kind") == ArtifactKind.SCENE_DRAFT.value
        and isinstance((content := item.get("content")), dict)
        and content.get("scene_id") == execution.unit_id
        and content.get("revision_number") == execution.revision_number
    )
    if len(drafts) != 1 or not isinstance(drafts[0].get("prose"), str):
        raise SceneProductionError("continuity call requires one exact current scene draft")
    return cast(str, drafts[0]["prose"])


def _assessment_explains_unchanged(assessment: str) -> bool:
    normalized = " ".join(assessment.casefold().split())
    return any(
        marker in normalized
        for marker in (
            "unchanged",
            "not changed",
            "did not change",
            "still contains",
            "still says",
        )
    ) or (("left" in normalized or "leaves" in normalized) and "in place" in normalized)


def _materialize_continuity_evidence(
    finding: object,
    model_context: _ContinuityModelContext,
) -> object:
    """Resolve model-selected evidence handles into exact canonical artifact excerpts."""
    if not isinstance(finding, dict):
        return finding
    materialized = {
        key: value for key, value in finding.items() if key not in _CONTINUITY_MODEL_EVIDENCE_FIELDS
    }
    severity = finding.get("severity")
    basis = finding.get("basis")
    if severity not in {"error", "blocking"}:
        return materialized
    if basis == ContinuityFindingBasis.MISSING_REQUIREMENT.value:
        return materialized
    ref_field = (
        "revised_draft_evidence_refs"
        if model_context.previous_continuity_report is not None
        else "draft_evidence_refs"
    )
    references = finding.get(ref_field)
    if not isinstance(references, list) or not references:
        raise _StructuredOutputContractError(
            ref_field,
            f"blocking finding requires non-empty {ref_field}",
        )
    content = model_context.candidate_draft.get("content")
    catalog = content.get("evidence_catalog") if isinstance(content, dict) else None
    by_reference = {
        entry["evidence_ref"]: entry["exact_excerpt"]
        for entry in catalog or []
        if isinstance(entry, dict)
        and isinstance(entry.get("evidence_ref"), str)
        and isinstance(entry.get("exact_excerpt"), str)
    }
    invalid = [reference for reference in references if reference not in by_reference]
    if invalid:
        raise _StructuredOutputContractError(
            ref_field,
            "evidence references must be selected from candidate_draft.content.evidence_catalog",
        )
    excerpts = list(dict.fromkeys(by_reference[reference] for reference in references))
    materialized["evidence"] = excerpts
    if model_context.previous_continuity_report is not None:
        materialized["revised_evidence"] = excerpts
    return materialized


def _materialize_continuity_finding(
    finding: object,
    scene_id: str,
    *,
    prior_resolutions: Mapping[str, str] | None = None,
) -> object:
    if not isinstance(finding, dict):
        return finding
    related_scene_ids = finding.get("related_scene_ids")
    model_scene_ids = related_scene_ids if isinstance(related_scene_ids, list) else []
    materialized = {
        **{key: value for key, value in finding.items() if key != "blocks_approval"},
        "related_scene_ids": list(dict.fromkeys((*model_scene_ids, scene_id))),
    }
    if finding.get("severity") in {"error", "blocking"}:
        materialized["blocks_approval"] = True
        resolution = finding.get("recommended_resolution")
        finding_id = finding.get("id")
        if (
            (not isinstance(resolution, str) or not resolution.strip())
            and isinstance(finding_id, str)
            and prior_resolutions is not None
            and finding_id in prior_resolutions
        ):
            materialized["recommended_resolution"] = prior_resolutions[finding_id]
    return materialized


def _materialize_scene_origin(
    output_data: dict[str, Any],
    collection_name: str,
    origin_field: str,
    scene_id: str,
) -> None:
    collection = output_data.get(collection_name)
    if not isinstance(collection, list):
        return
    output_data[collection_name] = [
        {**item, origin_field: scene_id} if isinstance(item, dict) else item for item in collection
    ]


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
            *((task.previous_continuity,) if task.previous_continuity is not None else ()),
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
            task.production.approved_blueprint,
            task.unit.plan,
            task.story_bible,
            task.draft,
            *task.accepted_units,
            *((task.previous_continuity,) if task.previous_continuity is not None else ()),
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


# Preserve the public name used by the frozen evaluation harness.
BenchmarkProductionExecutor = ProfileRoutedProductionExecutor
