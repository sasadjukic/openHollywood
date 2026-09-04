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
from difflib import SequenceMatcher
from enum import StrEnum
from math import ceil
from typing import Any, cast
from uuid import UUID, uuid4

from open_hollywood_engine.artifacts import (
    ArtifactKind,
    ContinuityCategory,
    ContinuityFindingBasis,
    ContinuityRecheckDisposition,
    ContinuityReport,
    Critique,
    CritiqueSeverity,
    CritiqueVerdict,
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
    ModelUsage,
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
_CONTINUITY_MODEL_DETAIL_FIELDS = frozenset({"basis_details", "category_details"})
_CONTINUITY_MODEL_REQUIREMENT_AUDIT_FIELDS = frozenset({"requirement_coverage"})
_CONTINUITY_MODEL_RECHECK_REPORT_FIELDS = frozenset({"prior_finding_rechecks", "new_findings"})
_CONTINUITY_MODEL_CERTIFICATION_FIELDS = frozenset(
    {
        "canonical_claim_ids",
        "conflict_kind",
        "conflict_disposition",
        "conflict_explanation",
        "draft_assertion",
        "repair_action",
        "violation_kind",
        "rule_conflict_assessment",
        "_prior_finding_recheck",
    }
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
_MAX_CANONICAL_CLAIMS_PER_FINDING = 1
_ADVISORY_SCENE_PLAN_REQUIREMENTS = frozenset(
    {"entry_state", "time_context", "purpose", "goal", "conflict", "exit_state"}
)
_COVERAGE_STATUSES = frozenset({"met", "partial", "absent"})
_NON_WORLD_CONFLICT_KIND_BY_CATEGORY: Mapping[str, str] = {
    ContinuityCategory.FACT.value: "fact",
    ContinuityCategory.TIMELINE.value: "timeline",
    ContinuityCategory.CHARACTER.value: "character_state",
    ContinuityCategory.CHARACTER_KNOWLEDGE.value: "character_knowledge",
    ContinuityCategory.RELATIONSHIP.value: "relationship_state",
    ContinuityCategory.LOCATION.value: "location_state",
    ContinuityCategory.SETUP_PAYOFF.value: "setup_payoff",
}
_NON_WORLD_REPAIR_ACTIONS = (
    "remove",
    "replace",
    "correct_state",
    "correct_sequence",
)
_DIRECT_CONFLICT_DISPOSITION = "directly_incompatible"
_TARGETED_REVISION_MINIMUM_SIMILARITY = 0.35
_STORY_LENGTH_ISSUE_PATTERN = re.compile(
    r"\b(?:word[ -]?count|words?|length)\b",
    re.IGNORECASE,
)
_STORY_LENGTH_TARGET_PATTERN = re.compile(
    r"\b(?:minimum|maximum|target|range|limit|under|below|short|over|above|exceed)\w*\b",
    re.IGNORECASE,
)
_STRUCTURAL_CRITIQUE_PATTERN = re.compile(
    r"\b(?:causal|continuity|contradict|character|dialogue|ending|logic|plot|"
    r"required element|scene plan|turning point)\w*\b",
    re.IGNORECASE,
)
_SCENE_ASSIGNMENT_CRITIQUE_PATTERN = re.compile(
    r"\b(?:point[ -]of[ -]view|pov|viewpoint|scene assignment|assigned (?:character|"
    r"protagonist)|future scene|next scene|wrong (?:character|scene))\b",
    re.IGNORECASE,
)
_SCENE_PLAN_DRIFT_PATTERN = re.compile(
    r"\b(?:miss(?:es|ing)?|omit(?:s|ted)?|abandon(?:s|ed)?|replace(?:s|d)?|"
    r"wrong|instead|does not|doesn't|fails? to)\b",
    re.IGNORECASE,
)
_SCENE_PLAN_ANCHOR_PATTERN = re.compile(
    r"\b(?:goal|conflict|turning point|outcome|exit state|scene plan)\b",
    re.IGNORECASE,
)
_QUALITATIVE_CONTRADICTION_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        (
            r"\b(?:does not|doesn't|fails? to)\s+(?:explicitly\s+)?"
            r"(?:establish|show|demonstrate|explain|connect|develop|earn|clarify|"
            r"emphasize|dramatize)\b"
        ),
        r"\b(?:too|purely|merely|insufficiently)\s+(?:abstract|intellectual|implicit|subtle|abrupt|weak|dismissive)\b",
        r"\b(?:feel|feels|seem|seems)\s+(?:too\s+)?(?:abrupt|unearned|weak|unclear)\b",
        r"\b(?:make|makes|making)\b.{0,40}\bearned\b",
        r"\b(?:pacing|atmosphere variation|emotional resonance|dramatic framing|sensory impact)\b",
    )
)
_ADDITIVE_REPAIR_PATTERN = re.compile(
    r"^\s*(?:add|insert|introduce|expand|deepen|strengthen)\b",
    re.IGNORECASE,
)
_CONTINUITY_APPLICATION_OWNED_FINDING_FIELDS = frozenset(
    {
        "category",
        "canonical_source_refs",
        "related_character_ids",
        "related_location_ids",
        "related_beat_ids",
        "related_scene_ids",
    }
)
_SCENE_PLAN_OBLIGATION_FIELDS = frozenset(
    {
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
)
_CONTINUITY_FINDING_RESOLUTION_REQUIREMENT = (
    "The blocking-finding schema requires every finding with severity 'error' or "
    "'blocking' to include a non-empty, concrete recommended_resolution. The application "
    "derives blocks_approval=true for both severities; never add that application-owned "
    "field. Advisory 'info' or 'warning' findings may omit recommended_resolution only "
    "when no repair is needed."
)
_CONTINUITY_FINDING_BASIS_REQUIREMENT = (
    "Every error or blocking finding must use exactly one basis_details branch. A "
    "contradiction must "
    "select draft_evidence_refs from candidate_draft.content.evidence_catalog. A non-world "
    "contradiction selects exactly one self-describing canonical_claim_id from "
    "contradiction_claim_catalog, one or more exact draft evidence handles, a "
    "directly_incompatible disposition, and a corrective repair_action. A short human-readable "
    "conflict_explanation is optional and never lexically gated; the application derives the "
    "category, conflict kind, source, lineage, and exact draft assertion. "
    "Scene Plan obligations are unavailable in this branch and can only be assessed through "
    "requirement_coverage. A World Rule contradiction "
    "selects only exact world_rule_ids; the application derives their canonical source "
    "references. Contradiction means an "
    "affirmative current-draft statement or action that conflicts with canon. The selected "
    "repair_action must correct, replace, or remove the "
    "existing incompatible assertion rather than add context. Never use contradiction "
    "for absent, weak, implicit, or incomplete requirement coverage. A "
    "forbidden_shortcut_violation must cite one exact due-now forbidden "
    "requirement_id and select the exact violating candidate-draft evidence reference. If the "
    "forbidden shortcut is absent, report no violation. The application resolves selected "
    "evidence references into exact persisted excerpts."
)
_CONTINUITY_REQUIREMENT_AUDIT_REQUIREMENT = (
    "Audit every entry in requirement_coverage_catalog exactly once by completing the "
    "schema-required property with that exact ID under requirement_coverage. Use 'met' when "
    "exact evidence performs the obligation, 'partial' when exact closest evidence performs "
    "part of it, and 'absent' only after checking the whole candidate draft. Met and partial "
    "results cite exact candidate-draft evidence references. An absent result either cites the "
    "closest relevant passages or explicitly declares that no related passage exists. Partial "
    "coverage is advisory craft feedback; only complete absence of an application-designated "
    "hard requirement can block. The application owns severity. Partial and absent results "
    "supply summary, coverage_assessment, and recommended_resolution. "
    "Evaluate companion_requirement_ids together before deciding. A Scene Plan goal with "
    "satisfaction_mode='pursue' is positive when the character meaningfully pursues or attempts "
    "it; achievement is required only by an outcome, turning point, exit state, or other entry "
    "whose own satisfaction_mode requires that result. "
    "Entry-state, time-context, purpose, goal, conflict, and exit-state coverage is advisory; "
    "qualitative adequacy belongs to the critic. "
    "The application derives each finding ID, category, lineage, and blocking state."
)
_CONTINUITY_WORLD_RULE_REQUIREMENT = (
    "For every world_rule contradiction, use the world-rule category_details branch nested "
    "inside basis_details, "
    "copy every involved canonical World Rule ID into world_rule_ids and omit redundant "
    "canonical_source_refs because the application derives exact rule provenance. Evaluate "
    "companion rules and exceptions in "
    "companion_rule_assessment, and set condition_explicitly_authorized=false only after that "
    "evaluation proves the condition is not authorized. A condition explicitly authorized by "
    "any companion rule, exception, Scene Plan turning point, outcome, or exit state cannot be "
    "reported as blocking. Select violation_kind only when the exact draft action breaches an "
    "explicit prohibition or fails an explicitly required condition, and explain in "
    "rule_conflict_assessment why the draft proposition and cited rule proposition cannot both "
    "be true. Pacing, abruptness, emphasis, atmosphere variation, emotional effectiveness, and "
    "dramatic framing belong to critique and cannot be continuity blockers by themselves. For "
    "every non-world "
    "blocker, use the non-world category branch and omit all world-rule analysis fields."
)
_CONTINUITY_REQUIREMENT_SCOPE = (
    "Use requirement_coverage_catalog and forbidden_shortcut_catalog as the sole "
    "authorities for requirement gates in this continuity call. The application has already "
    "deduplicated overlapping benchmark and Scene Plan obligations. Every required entry "
    "must be handled only by requirement_coverage. Scene Plan and benchmark requirement text "
    "is never a selectable contradiction claim. A contradiction must be logically independent "
    "of requirement coverage and must oppose stable canon rather than complain that a planned "
    "beat is absent, implicit, weak, or insufficiently explicit. "
    "A contradiction category can never be 'constraint'. Deferred story-wide requirements are "
    "intentionally "
    "absent and must not block the current scene. A character may temporarily consider a "
    "forbidden final "
    "explanation; it becomes a violation only if the completed story adopts it as the "
    "actual resolution. Never rewrite a planned intermediate scene to perform the ending's "
    "work early."
)
_CONTINUITY_RECHECK_REQUIREMENT = (
    "When a previous Continuity Report is supplied, audit every prior error or blocking "
    "finding against the revised draft before reporting anything new. Complete every exact "
    "schema-required key in prior_finding_rechecks once. Mark it resolved with a concrete "
    "resolution_assessment, or mark it still_blocking with repair_assessment. Both statuses "
    "select exact revised_draft_evidence_refs. The application rehydrates the prior finding's "
    "identity, basis, category, provenance, and repair; never repeat the complete finding. Put "
    "only genuinely new defects or advisories in new_findings. Consult continuity_history before "
    "calling a defect new. A defect matching any historical canonical claim, World Rule, or "
    "requirement keeps its stable application identity and prior repair direction; semantic "
    "duplicates are application-consolidated. A new non-world blocker must cite at "
    "least one exact assertion introduced or changed by the revision. Prior IDs are "
    "application-owned and "
    "are unavailable there. The application owns canonical finding IDs and derives "
    "recheck_disposition. A new blocking defect must explain in repair_assessment why it was "
    "not actionable before. Do not "
    "downgrade an unresolved prior blocker to an advisory finding. Every revised_evidence "
    "reference is resolved by the application to an exact excerpt from the supplied revised "
    "draft. A re-checked "
    "missing requirement instead uses met, partial, or absent in requirement_coverage with a "
    "current coverage_assessment and auditable closest evidence. "
    "An unchanged blocker may retain the same accurate assessment. A copied assessment after "
    "changed evidence is recorded as diagnostic telemetry and does not invalidate otherwise "
    "valid structured output. Do not replace prior guidance "
    "with contradictory guidance unless exact Scene Plan or Story Bible evidence proves "
    "the prior repair invalid."
)
_SCHEMA_REPAIR_COMMON_RULES = (
    "Return the complete replacement JSON object, not a patch or explanation.",
    "Correct every validation issue at its exact focus location before changing any "
    "unrelated creative content.",
    "Use exact enum literals and select evidence, canonical-claim, requirement, and world-rule "
    "IDs only from the catalogs and enums supplied for their specific fields; never turn "
    "labels, prose descriptions, null-like text, or newly invented names into IDs.",
    "When an optional field is not applicable, use the schema default shape (null, an "
    "empty array, or omission as permitted by the supplied schema) instead of placeholder text.",
)
_SCHEMA_REPAIR_OPERATION_RULES: Mapping[_Operation, tuple[str, ...]] = {
    _Operation.WRITE: (
        "Keep prose and title as non-empty strings, is_complete=true, and preserve the "
        "assigned scene and revision identity.",
    ),
    _Operation.CRITIQUE: (
        "Keep rubric score values numeric, use only declared verdict and severity literals, "
        "and never combine a passing verdict with a blocking issue. The application derives "
        "overall_score; do not add it.",
    ),
    _Operation.CONTINUITY: (
        "Every error or blocking finding needs a concrete recommended_resolution. Return "
        "an empty findings array when no defect remains.",
        "Match every blocking finding's basis_details object to its basis-specific evidence "
        "contract. Select draft "
        "evidence handles from candidate_draft.content.evidence_catalog. Non-world "
        "contradictions select exactly one typed claim ID from contradiction_claim_catalog, "
        "one or more draft evidence handles, conflict_disposition=directly_incompatible, and "
        "one corrective repair_action; the application derives the exact assertion, category, "
        "conflict kind, provenance, and lineage. "
        "World Rule contradictions select world_rule_ids and omit canonical_source_refs. "
        "Scene Plan requirements exist only in requirement_coverage. Never copy prose or "
        "requirement text into an ID field.",
        "World-rule branches require exact "
        "world_rule_ids, violation_kind, rule_conflict_assessment, a non-empty "
        "companion_rule_assessment, and "
        "condition_explicitly_authorized=false; the application derives their exact canonical "
        "source references. Non-world branches must omit those World Rule fields.",
        "Complete every schema-required requirement_coverage property with met, partial, or "
        "absent. Cite closest exact evidence for met and partial, and for absent whenever a "
        "related passage exists. Do not use a contradiction for an omitted requirement.",
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

    def __init__(
        self,
        location: str,
        message: str,
        *,
        issue_type: str | None = None,
        issues: tuple[dict[str, str], ...] = (),
        expected_value: str | None = None,
        received_value: str | None = None,
    ) -> None:
        super().__init__(message)
        self.location = location
        self.issue_type = issue_type or type(self).__name__
        self.issues = issues
        self.expected_value = expected_value
        self.received_value = received_value


class ContinuityRecheckStagnationError(_StructuredOutputContractError):
    """A continuity re-check violated exact evidence or disposition guarantees."""

    def __init__(
        self,
        message: str,
        *,
        issues: tuple[dict[str, str], ...] = (),
    ) -> None:
        super().__init__("findings", message, issues=issues)


@dataclass(frozen=True)
class _ContinuityModelContext:
    """Exact, bounded continuity context shared by the prompt and Local grammar."""

    candidate_draft: dict[str, Any]
    accepted_prior_drafts: tuple[dict[str, Any], ...]
    previous_continuity_report: dict[str, Any] | None
    canonical_source_catalog: tuple[dict[str, Any], ...]
    requirement_catalog: tuple[dict[str, Any], ...]
    forbidden_shortcut_catalog: tuple[dict[str, Any], ...]
    requirement_kinds: Mapping[str, str]
    requirement_categories: Mapping[str, str]
    requirement_satisfaction_modes: Mapping[str, str]
    requirement_enforcement: Mapping[str, str]
    world_rule_ids: tuple[str, ...]
    previous_candidate_draft: dict[str, Any] | None = None
    continuity_history: tuple[dict[str, Any], ...] = ()

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

    @property
    def canonical_claim_ids(self) -> tuple[str, ...]:
        return tuple(
            entry["claim_id"]
            for entry in self.canonical_source_catalog
            if isinstance(entry.get("claim_id"), str)
        )

    @property
    def canonical_claim_source_refs(self) -> Mapping[str, str]:
        return {
            cast(str, entry["claim_id"]): cast(str, entry["reference_id"])
            for entry in self.canonical_source_catalog
            if isinstance(entry.get("claim_id"), str) and isinstance(entry.get("reference_id"), str)
        }

    @property
    def contradiction_claim_catalog(self) -> tuple[dict[str, object], ...]:
        """Expose only the semantic selector and claim text needed by the model."""
        return tuple(
            {
                "canonical_claim_id": entry["claim_id"],
                "category": cast(list[str], entry["categories"])[0],
                "canonical_id": entry.get("canonical_id"),
                "claim": entry["claim"],
            }
            for entry in self.canonical_source_catalog
            if isinstance(entry.get("claim_id"), str)
            and isinstance(entry.get("categories"), list)
            and bool(entry["categories"])
        )

    @property
    def world_rule_catalog(self) -> tuple[dict[str, object], ...]:
        """Expose exact rule IDs and propositions without internal provenance handles."""
        return tuple(
            {
                "world_rule_id": entry["canonical_id"],
                "claim": entry["claim"],
            }
            for entry in self.canonical_source_catalog
            if entry.get("artifact_kind") == ArtifactKind.WORLD_RULE.value
            or (
                isinstance(entry.get("source_path"), str)
                and ".world_rules[" in cast(str, entry["source_path"])
            )
            if isinstance(entry.get("canonical_id"), str)
        )

    @property
    def canonical_source_claim_ids(self) -> Mapping[str, str]:
        return {
            source_ref: claim_id
            for claim_id, source_ref in self.canonical_claim_source_refs.items()
        }

    @property
    def canonical_claim_categories(self) -> Mapping[str, tuple[str, ...]]:
        return {
            cast(str, entry["claim_id"]): tuple(
                value for value in entry.get("categories", []) if isinstance(value, str)
            )
            for entry in self.canonical_source_catalog
            if isinstance(entry.get("claim_id"), str)
        }

    @property
    def canonical_claim_requirement_ids(self) -> Mapping[str, str]:
        return {
            cast(str, entry["claim_id"]): cast(str, entry["requirement_id"])
            for entry in self.canonical_source_catalog
            if isinstance(entry.get("claim_id"), str)
            and isinstance(entry.get("requirement_id"), str)
        }

    @property
    def canonical_claim_related_ids(self) -> Mapping[str, tuple[str, ...]]:
        return {
            cast(str, entry["claim_id"]): tuple(
                value for value in entry.get("related_ids", []) if isinstance(value, str)
            )
            for entry in self.canonical_source_catalog
            if isinstance(entry.get("claim_id"), str)
        }

    @property
    def world_rule_source_refs(self) -> Mapping[str, str]:
        """Map each exact World Rule ID to one deterministic canonical source handle."""
        references: dict[str, str] = {}
        for entry in self.canonical_source_catalog:
            canonical_id = entry.get("canonical_id")
            reference_id = entry.get("reference_id")
            source_path = entry.get("source_path")
            is_world_rule = entry.get("artifact_kind") == ArtifactKind.WORLD_RULE.value or (
                isinstance(source_path, str) and ".world_rules[" in source_path
            )
            if is_world_rule and isinstance(canonical_id, str) and isinstance(reference_id, str):
                references.setdefault(canonical_id, reference_id)
        return references

    @property
    def prior_blocking_finding_ids(self) -> tuple[str, ...]:
        report = self.previous_continuity_report
        content = report.get("content") if isinstance(report, dict) else None
        findings = content.get("findings") if isinstance(content, dict) else None
        if not isinstance(findings, list):
            return ()
        return tuple(
            finding["id"]
            for finding in findings
            if isinstance(finding, dict)
            and finding.get("severity") in {"error", "blocking"}
            and isinstance(finding.get("id"), str)
        )

    @property
    def prior_model_finding_ids(self) -> tuple[str, ...]:
        report = self.previous_continuity_report
        content = report.get("content") if isinstance(report, dict) else None
        findings = content.get("findings") if isinstance(content, dict) else None
        if not isinstance(findings, list):
            return ()
        return tuple(
            finding["id"]
            for finding in findings
            if isinstance(finding, dict)
            and finding.get("severity") in {"error", "blocking"}
            and finding.get("basis") != ContinuityFindingBasis.MISSING_REQUIREMENT.value
            and isinstance(finding.get("id"), str)
        )

    @property
    def historical_blocking_finding_ids(self) -> tuple[str, ...]:
        """Return stable blocker IDs from every earlier report in this scene."""
        reports = self.continuity_history or (
            (self.previous_continuity_report,)
            if self.previous_continuity_report is not None
            else ()
        )
        return tuple(
            dict.fromkeys(
                finding["id"]
                for report in reports
                for finding in _continuity_report_findings(report)
                if finding.get("severity") in {"error", "blocking"}
                and isinstance(finding.get("id"), str)
            )
        )

    @property
    def historical_semantic_finding_ids(self) -> Mapping[str, str]:
        """Map every known semantic issue to its first stable application ID."""
        identities: dict[str, str] = {}
        reports = self.continuity_history or (
            (self.previous_continuity_report,)
            if self.previous_continuity_report is not None
            else ()
        )
        for report in reports:
            for finding in _continuity_report_findings(report):
                finding_id = finding.get("id")
                key = _continuity_finding_semantic_key(finding, self)
                if isinstance(finding_id, str) and key is not None:
                    identities.setdefault(key, finding_id)
        return identities


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
        "changing scene identity. Keep revisions minimally invasive: preserve unrelated prose, "
        "the assigned viewpoint, characters, scene purpose, and scene outcome while repairing "
        "only the supplied defects. Never draft material assigned to a later scene. Treat "
        "length_guidance as a story-wide advisory allocation, "
        "not a hard per-scene quota."
    ),
    _Operation.CRITIQUE: (
        "Independently evaluate the exact scene draft against its Scene Plan, the "
        "approved Blueprint, prose quality, dramatic progress, and prompt constraints. A wrong "
        "viewpoint or assigned character, or replacement of the planned goal, turning point, "
        "outcome, or exit state with later-scene material, is blocking and cannot receive PASS. "
        "The target word-count range is story-wide and advisory. Use length_guidance for "
        "context, but never revise or reject a scene solely because that scene is under or "
        "over a proportional word allocation."
    ),
    _Operation.CONTINUITY: (
        "Check the exact scene draft against the exact canonical Story Bible and Scene "
        "Plan. Cover every continuity category in canonical enum order. "
        f"{_CONTINUITY_FINDING_RESOLUTION_REQUIREMENT} "
        f"{_CONTINUITY_FINDING_BASIS_REQUIREMENT} "
        f"{_CONTINUITY_REQUIREMENT_AUDIT_REQUIREMENT} "
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
            output_schema,
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
                usage=error.usage,
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
            resolved_input_references = input_references
            inputs = _load_inputs(session, resolved_input_references)
            if operation is _Operation.CONTINUITY:
                resolved_input_references = _continuity_recheck_input_references(
                    session,
                    resolved_input_references,
                    inputs,
                    project_id=run.project_id,
                )
                inputs = _load_inputs(session, resolved_input_references)
            run_seed = _integer_input(run.input_state, "run_seed")
            fingerprint = canonical_sha256(
                {
                    "workflow_run_id": str(run.id),
                    "operation": operation.value,
                    "specialist_role": specialist_role,
                    "unit_id": _unit_id(task),
                    "revision_number": _revision_number(task),
                    "input_artifact_version_ids": [
                        str(reference.version_id) for reference in resolved_input_references
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
                input_version_ids=tuple(
                    reference.version_id for reference in resolved_input_references
                ),
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
        output_schema: Mapping[str, Any],
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
                    "request_composition": _request_composition_metrics(
                        messages,
                        gateway_schema=(
                            output_schema
                            if execution.selection.deployment is ModelDeployment.LOCAL
                            else None
                        ),
                    ),
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
            if operation is _Operation.CONTINUITY and isinstance(output, ContinuityReport):
                observations = _continuity_recheck_observations(output, execution)
                if observations:
                    invocation.request_settings = {
                        **invocation.request_settings,
                        "continuity_recheck_observations": list(observations),
                    }
            if operation is _Operation.WRITE and isinstance(output, SceneDraft):
                similarity = _targeted_revision_similarity(
                    output.model_dump(mode="json"), execution
                )
                if similarity is not None:
                    invocation.request_settings = {
                        **invocation.request_settings,
                        "revision_scope_observation": {
                            "mode": "targeted_continuity_repair",
                            "prior_draft_similarity": round(similarity, 4),
                            "minimum_similarity": _TARGETED_REVISION_MINIMUM_SIMILARITY,
                            "within_change_budget": (
                                similarity >= _TARGETED_REVISION_MINIMUM_SIMILARITY
                            ),
                        },
                    }
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
        usage: ModelUsage | None = None,
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
            elif usage is not None:
                invocation.input_tokens = usage.input_tokens
                invocation.output_tokens = usage.output_tokens
                invocation.request_settings = {
                    **invocation.request_settings,
                    "provider_reported_usage": {
                        "input_tokens": usage.input_tokens,
                        "output_tokens": usage.output_tokens,
                    },
                }
            invocation.completed_at = datetime.now(UTC)
            invocation.error_code = code
            invocation.error_message = safe_message
            if safe_validation_issues:
                invocation.request_settings = {
                    **invocation.request_settings,
                    "structured_failure": {
                        "schema_version": "2",
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

    if isinstance(error, _StructuredOutputContractError) and error.issues:
        return tuple(
            {
                key: value
                for key, raw_value in issue.items()
                if key
                in {
                    "location",
                    "type",
                    "message",
                    "expected_value",
                    "received_value",
                }
                and (value := _safe_structured_failure_detail(raw_value)) is not None
            }
            for issue in error.issues[:_MAX_SAFE_STRUCTURED_FAILURE_ISSUES]
        )

    detail = _safe_structured_failure_detail(str(error))
    issue = {
        "location": (error.location if isinstance(error, _StructuredOutputContractError) else "$"),
        "type": (
            error.issue_type
            if isinstance(error, _StructuredOutputContractError)
            else type(error).__name__
        ),
    }
    if detail is not None:
        issue["message"] = detail
    if isinstance(error, _StructuredOutputContractError):
        for key, raw_value in (
            ("expected_value", error.expected_value),
            ("received_value", error.received_value),
        ):
            if (
                raw_value is not None
                and (value := _safe_structured_failure_detail(raw_value)) is not None
            ):
                issue[key] = value
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
        if operation is _Operation.CRITIQUE:
            properties = schema.get("properties")
            required = schema.get("required")
            if not isinstance(properties, dict) or not isinstance(required, list):
                raise SceneProductionError("critique schema is invalid")
            properties.pop("overall_score", None)
            schema["required"] = [field for field in required if field != "overall_score"]
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
    is_recheck = continuity_schema_variant is _ContinuitySchemaVariant.RECHECK
    phase_name = "Recheck" if is_recheck else "Initial"
    blocking_name = f"{phase_name}BlockingContinuityFinding"
    advisory_name = f"{phase_name}AdvisoryContinuityFinding"
    evidence_reference_name = "DraftEvidenceReference"
    definitions[evidence_reference_name] = {
        "type": "string",
        "enum": list(continuity_model_context.evidence_refs),
        "title": "Draft Evidence Reference",
    }
    required_requirement_ids = tuple(
        entry["id"] for entry in continuity_model_context.requirement_catalog
    )
    forbidden_requirement_ids = tuple(
        requirement_id
        for requirement_id, kind in continuity_model_context.requirement_kinds.items()
        if kind == "forbidden_shortcut"
    )
    basis_detail_schemas: list[dict[str, Any]] = []
    if continuity_model_context.canonical_claim_ids:
        non_world_contradiction = _continuity_basis_detail_schema(
            basis=ContinuityFindingBasis.CONTRADICTION,
            is_recheck=is_recheck,
            model_context=continuity_model_context,
            requirement_ids=(),
            include_canonical_claim_ids=True,
        )
        non_world_contradiction["title"] = "Non World Contradiction Details"
        basis_detail_schemas.append(non_world_contradiction)
    if continuity_model_context.world_rule_ids:
        world_rule_contradiction = _continuity_basis_detail_schema(
            basis=ContinuityFindingBasis.CONTRADICTION,
            is_recheck=is_recheck,
            model_context=continuity_model_context,
            requirement_ids=(),
            include_canonical_claim_ids=False,
        )
        world_rule_contradiction["properties"]["category_details"] = (
            _continuity_world_category_detail_schema(continuity_model_context)
        )
        world_rule_contradiction["required"].append("category_details")
        world_rule_contradiction["title"] = "World Rule Contradiction Details"
        basis_detail_schemas.append(world_rule_contradiction)
    if forbidden_requirement_ids:
        basis_detail_schemas.append(
            _continuity_basis_detail_schema(
                basis=ContinuityFindingBasis.FORBIDDEN_SHORTCUT_VIOLATION,
                is_recheck=is_recheck,
                model_context=continuity_model_context,
                requirement_ids=forbidden_requirement_ids,
                include_canonical_claim_ids=False,
            )
        )
    definitions[blocking_name] = _continuity_blocking_finding_schema(
        finding_schema,
        title=blocking_name,
        basis_detail_schemas=basis_detail_schemas,
        require_recheck_analysis=is_recheck,
    )
    definitions[advisory_name] = _continuity_advisory_finding_schema(
        finding_schema,
        title=advisory_name,
    )
    model_finding_items = {
        "anyOf": [
            {"$ref": f"#/$defs/{blocking_name}"},
            {"$ref": f"#/$defs/{advisory_name}"},
        ]
    }
    if is_recheck:
        report_properties.pop("findings", None)
        schema["required"] = [field for field in schema["required"] if field != "findings"]
        prior_definition_name = "PriorFindingRecheckEntry"
        definitions[prior_definition_name] = _continuity_prior_recheck_entry_schema(
            model_context=continuity_model_context
        )
        prior_ids = continuity_model_context.prior_model_finding_ids
        report_properties["prior_finding_rechecks"] = {
            "type": "object",
            "properties": {
                finding_id: {"$ref": f"#/$defs/{prior_definition_name}"} for finding_id in prior_ids
            },
            "required": list(prior_ids),
            "additionalProperties": False,
            "title": "Prior Finding Rechecks",
        }
        report_properties["new_findings"] = {
            "type": "array",
            "items": model_finding_items,
            "maxItems": _MAX_CONTINUITY_FINDINGS,
            "title": "New Findings",
        }
        schema["required"].extend(("prior_finding_rechecks", "new_findings"))
    else:
        findings_schema["maxItems"] = _MAX_CONTINUITY_FINDINGS
        findings_schema["items"] = model_finding_items
    coverage_definition_name = "RequirementCoverageEntry"
    definitions[coverage_definition_name] = _continuity_requirement_coverage_entry_schema(
        evidence_reference_name=evidence_reference_name,
    )
    coverage_properties = {
        cast(str, entry["id"]): {"$ref": f"#/$defs/{coverage_definition_name}"}
        for entry in continuity_model_context.requirement_catalog
    }
    report_properties["requirement_coverage"] = {
        "type": "object",
        "properties": coverage_properties,
        "required": list(required_requirement_ids),
        "additionalProperties": False,
        "title": "Requirement Coverage",
    }
    schema["required"].append("requirement_coverage")
    definitions.pop("ContinuityFinding", None)
    definitions.pop("ContinuityFindingBasis", None)
    definitions.pop("ContinuitySeverity", None)
    definitions.pop("ContinuityRecheckDisposition", None)
    schema["title"] = f"{phase_name}ContinuityReport"
    return schema


def _continuity_requirement_coverage_entry_schema(
    *,
    evidence_reference_name: str,
) -> dict[str, Any]:
    """Create one compact coverage grammar shared by every due requirement."""
    evidence = {
        "type": "array",
        "items": {"$ref": f"#/$defs/{evidence_reference_name}"},
        "maxItems": _MAX_EVIDENCE_REFS_PER_FINDING,
    }
    met = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "const": "met"},
            "coverage_assessment": {
                "type": "string",
                "minLength": 1,
            },
            "evidence_refs": {**evidence, "minItems": 1},
        },
        "required": ["status", "coverage_assessment", "evidence_refs"],
        "additionalProperties": False,
    }
    gap_properties: dict[str, Any] = {
        "summary": {"type": "string", "minLength": 1},
        "coverage_assessment": {"type": "string", "minLength": 1},
        "recommended_resolution": {"type": "string", "minLength": 1},
    }
    partial = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "const": "partial"},
            **gap_properties,
            "evidence_refs": {**evidence, "minItems": 1},
        },
        "required": ["status", *gap_properties, "evidence_refs"],
        "additionalProperties": False,
    }
    absent = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "const": "absent"},
            **gap_properties,
            "evidence_refs": evidence,
            "evidence_search_result": {
                "type": "string",
                "enum": ["closest_passages_selected", "no_related_passage"],
            },
        },
        "required": [
            "status",
            *gap_properties,
            "evidence_refs",
            "evidence_search_result",
        ],
        "additionalProperties": False,
    }
    return {"anyOf": [met, partial, absent]}


def _continuity_blocking_finding_schema(
    canonical_schema: Mapping[str, Any],
    *,
    title: str,
    basis_detail_schemas: list[dict[str, Any]],
    require_recheck_analysis: bool,
) -> dict[str, Any]:
    """Compose basis and category dimensions without duplicating the finding object."""
    branch = deepcopy(dict(canonical_schema))
    properties = branch.get("properties")
    required = branch.get("required")
    if not isinstance(properties, dict) or not isinstance(required, list):
        raise SceneProductionError("continuity finding branch schema is invalid")

    properties["severity"] = {
        "type": "string",
        "enum": ["error", "blocking"],
        "title": "Severity",
    }
    removed_fields = (
        _CONTINUITY_RECHECK_ONLY_FIELDS
        | _CONTINUITY_MODEL_EVIDENCE_FIELDS
        | _CONTINUITY_MODEL_DETAIL_FIELDS
        | _CONTINUITY_APPLICATION_OWNED_FINDING_FIELDS
        | {
            "id",
            "basis",
            "blocks_approval",
            "condition_explicitly_authorized",
            "coverage_assessment",
            "coverage_evidence",
            "coverage_status",
            "evidence",
            "requirement_id",
            "world_rule_ids",
            "companion_rule_assessment",
        }
    )
    for field_name in removed_fields:
        properties.pop(field_name, None)
    branch["required"] = [field_name for field_name in required if field_name not in removed_fields]
    properties["recommended_resolution"] = {
        "type": "string",
        "minLength": 1,
        "title": "Recommended Resolution",
    }
    properties["basis_details"] = {
        "anyOf": basis_detail_schemas,
        "title": "Basis Details",
    }
    branch["required"].extend(
        (
            "recommended_resolution",
            "basis_details",
        )
    )
    if require_recheck_analysis:
        properties["repair_assessment"] = {
            "type": "string",
            "minLength": 1,
            "title": "Repair Assessment",
        }
        branch["required"].append("repair_assessment")
    branch["title"] = title
    return branch


def _continuity_prior_recheck_entry_schema(
    *,
    model_context: _ContinuityModelContext,
) -> dict[str, Any]:
    """Require one compact decision while the application rehydrates prior finding data."""
    evidence = {
        "type": "array",
        "items": {"$ref": "#/$defs/DraftEvidenceReference"},
        "minItems": 1,
        "maxItems": _MAX_EVIDENCE_REFS_PER_FINDING,
    }
    resolved = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "const": "resolved", "title": "Status"},
            "resolution_assessment": {
                "type": "string",
                "minLength": 1,
            },
            "revised_draft_evidence_refs": evidence,
        },
        "required": ["status", "resolution_assessment", "revised_draft_evidence_refs"],
        "additionalProperties": False,
    }
    still_blocking = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "const": "still_blocking",
                "title": "Status",
            },
            "repair_assessment": {
                "type": "string",
                "minLength": 1,
            },
            "revised_draft_evidence_refs": evidence,
        },
        "required": ["status", "repair_assessment", "revised_draft_evidence_refs"],
        "additionalProperties": False,
    }
    return {"anyOf": [resolved, still_blocking]}


def _continuity_advisory_finding_schema(
    canonical_schema: Mapping[str, Any],
    *,
    title: str,
) -> dict[str, Any]:
    """Create the smaller non-blocking finding branch."""
    branch = deepcopy(dict(canonical_schema))
    properties = branch.get("properties")
    required = branch.get("required")
    if not isinstance(properties, dict) or not isinstance(required, list):
        raise SceneProductionError("continuity advisory branch schema is invalid")
    properties["severity"] = {
        "type": "string",
        "enum": ["info", "warning"],
        "title": "Severity",
    }
    removed_fields = (
        _CONTINUITY_RECHECK_ONLY_FIELDS
        | _CONTINUITY_MODEL_EVIDENCE_FIELDS
        | _CONTINUITY_MODEL_DETAIL_FIELDS
        | {
            "id",
            "basis",
            "blocks_approval",
            "canonical_source_refs",
            "condition_explicitly_authorized",
            "coverage_assessment",
            "coverage_evidence",
            "coverage_status",
            "evidence",
            "requirement_id",
            "world_rule_ids",
            "companion_rule_assessment",
        }
    )
    for field_name in removed_fields:
        properties.pop(field_name, None)
    branch["required"] = [field_name for field_name in required if field_name not in removed_fields]
    branch["title"] = title
    return branch


def _continuity_basis_detail_schema(
    *,
    basis: ContinuityFindingBasis,
    is_recheck: bool,
    model_context: _ContinuityModelContext,
    requirement_ids: tuple[str, ...],
    include_canonical_claim_ids: bool,
) -> dict[str, Any]:
    """Create one compact, mutually exclusive blocking-basis detail object."""
    properties: dict[str, Any] = {
        "basis": {
            "type": "string",
            "const": basis.value,
            "title": "Basis",
        }
    }
    required = ["basis"]
    evidence_field = "revised_draft_evidence_refs" if is_recheck else "draft_evidence_refs"
    properties[evidence_field] = {
        "type": "array",
        "items": {"$ref": "#/$defs/DraftEvidenceReference"},
        "minItems": 1,
        "maxItems": _MAX_EVIDENCE_REFS_PER_FINDING,
        "title": ("Revised Draft Evidence Refs" if is_recheck else "Draft Evidence Refs"),
    }
    required.append(evidence_field)
    if basis is ContinuityFindingBasis.CONTRADICTION and include_canonical_claim_ids:
        properties["canonical_claim_ids"] = {
            "type": "array",
            "items": {
                "type": "string",
                "enum": list(model_context.canonical_claim_ids),
            },
            "minItems": 1,
            "maxItems": _MAX_CANONICAL_CLAIMS_PER_FINDING,
            "title": "Canonical Claim Ids",
        }
        properties["conflict_disposition"] = {
            "type": "string",
            "const": _DIRECT_CONFLICT_DISPOSITION,
        }
        properties["conflict_explanation"] = {
            "type": "string",
            "minLength": 1,
        }
        properties["repair_action"] = {
            "type": "string",
            "enum": list(_NON_WORLD_REPAIR_ACTIONS),
        }
        required.extend(
            (
                "canonical_claim_ids",
                "conflict_disposition",
                "repair_action",
            )
        )
    elif basis is ContinuityFindingBasis.FORBIDDEN_SHORTCUT_VIOLATION:
        properties["requirement_id"] = {
            "type": "string",
            "enum": list(requirement_ids),
            "title": "Requirement Id",
        }
        required.append("requirement_id")
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
        "title": f"{basis.value.replace('_', ' ').title()} Details",
    }


def _continuity_world_category_detail_schema(
    model_context: _ContinuityModelContext,
) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "world_rule_ids": {
                "type": "array",
                "items": {"type": "string", "enum": list(model_context.world_rule_ids)},
                "minItems": 1,
            },
            "violation_kind": {
                "type": "string",
                "enum": ["explicit_prohibition_breach", "required_condition_breach"],
            },
            "rule_conflict_assessment": {
                "type": "string",
                "minLength": 1,
            },
            "companion_rule_assessment": {
                "type": "string",
                "minLength": 1,
            },
            "condition_explicitly_authorized": {
                "type": "boolean",
                "const": False,
            },
        },
        "required": [
            "world_rule_ids",
            "violation_kind",
            "rule_conflict_assessment",
            "companion_rule_assessment",
            "condition_explicitly_authorized",
        ],
        "additionalProperties": False,
    }


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


def _schema_repair_guidance(
    *,
    operation: _Operation,
    deployment: ModelDeployment,
    previous_failure: Mapping[str, object] | None,
    continuity_schema_variant: _ContinuitySchemaVariant | None = None,
    continuity_model_context: _ContinuityModelContext | None = None,
) -> dict[str, object] | None:
    """Build one provider-neutral repair packet without replaying global catalogs."""
    if previous_failure is None or previous_failure.get("error_code") not in {
        "schema_validation_failed",
        _CONTINUITY_RECHECK_STAGNATION_ERROR_CODE,
    }:
        return None
    del deployment

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

    operation_rules = list(_SCHEMA_REPAIR_OPERATION_RULES[operation])
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
                "This is a re-check. Complete every exact key in prior_finding_rechecks with "
                "status resolved or still_blocking, and put only semantically new issues in "
                "new_findings. Requirement gaps remain exclusively in requirement_coverage.",
            )
        else:
            raise ValueError("continuity repair guidance requires a schema variant")

    directives: list[dict[str, object]] = []
    if isinstance(validation_issues, list):
        for issue in validation_issues:
            if not isinstance(issue, dict):
                continue
            location = issue.get("location")
            issue_type = issue.get("type")
            if not isinstance(location, str) or not isinstance(issue_type, str):
                continue
            directive: dict[str, object] = {
                "location": location,
                "issue_type": issue_type,
                "action": "replace the value at this exact location with the schema-valid form",
            }
            for diagnostic_key in ("expected_value", "received_value"):
                diagnostic_value = issue.get(diagnostic_key)
                if isinstance(diagnostic_value, str):
                    directive[diagnostic_key] = diagnostic_value
            if issue_type == "scene_revision_scope_exceeded":
                directive["action"] = (
                    "restore the previous draft and apply only the repair-ledger changes; "
                    "preserve unrelated prose, viewpoint, assigned characters, and scene outcome"
                )
            elif issue_type == "missing_requirement_used_as_contradiction":
                directive["action"] = (
                    "remove the redundant contradiction and represent an omitted obligation "
                    "only in its keyed requirement_coverage entry"
                )
            elif issue_type == "requirement_partition_mismatch":
                directive["action"] = (
                    "return every exact requirement_coverage key once and no other keys"
                )
                if continuity_model_context is not None:
                    directive["required_requirement_ids"] = list(
                        continuity_model_context.requirement_categories
                    )
            elif issue_type == "prior_finding_partition_mismatch":
                directive["action"] = (
                    "return every exact prior_finding_rechecks key once and no other keys"
                )
                if continuity_model_context is not None:
                    directive["required_prior_finding_ids"] = list(
                        continuity_model_context.prior_model_finding_ids
                    )
            elif issue_type in {
                "invalid_world_rule_id",
                "world_rule_source_mismatch",
                "world_rule_source_provenance_invalid",
            }:
                directive["action"] = (
                    "select only world_rule_ids from the supplied enum and omit "
                    "canonical_source_refs because the application derives them"
                )
                if continuity_model_context is not None:
                    directive["valid_world_rule_ids"] = list(
                        continuity_model_context.world_rule_ids
                    )
            elif issue_type in {
                "non_world_claim_provenance_invalid",
                "non_world_claim_category_mismatch",
                "non_world_claim_lineage_mismatch",
            }:
                directive["action"] = (
                    "select exactly one self-describing canonical_claim_id from the field enum, "
                    "or remove the finding when no exact affirmative conflict exists; never "
                    "convert a Scene Plan coverage gap into a contradiction"
                )
            elif issue_type == "non_world_conflict_certificate_invalid":
                directive["action"] = (
                    "select conflict_disposition=directly_incompatible and a repair_action "
                    "that corrects or removes the selected draft evidence; "
                    "otherwise remove the blocker or return it as advisory craft feedback"
                )
            elif issue_type == "new_contradiction_not_new_to_revision":
                directive["action"] = (
                    "remove the newly exposed blocker because all of its cited assertions were "
                    "already present in the previous candidate; only a still-blocking prior ID "
                    "or evidence introduced or changed by this revision may block"
                )
            elif issue_type == "requirement_coverage_evidence_invalid":
                directive["action"] = (
                    "use met with exact proving evidence, partial with exact closest evidence, "
                    "or absent with closest passages or an explicit no_related_passage result"
                )
            directives.append(directive)

    guidance: dict[str, object] = {
        "policy_version": "6",
        "mode": "repair_only",
        "focus_locations": focus_locations,
        "directives": directives,
        "common_rules": list(_SCHEMA_REPAIR_COMMON_RULES),
        "operation_rules": operation_rules,
    }
    if continuity_schema_variant is not None:
        guidance["schema_variant"] = continuity_schema_variant.value
    return guidance


def _story_length_guidance(execution: _Execution) -> dict[str, object] | None:
    """Derive a soft scene allocation from the story-wide advisory word range."""
    target = execution.constraints.get("target_word_count")
    if not isinstance(target, dict):
        return None
    minimum = target.get("minimum")
    maximum = target.get("maximum")
    if (
        not isinstance(minimum, int)
        or isinstance(minimum, bool)
        or not isinstance(maximum, int)
        or isinstance(maximum, bool)
        or minimum < 0
        or maximum < minimum
    ):
        return None

    accepted_words = 0
    current_candidate_words: int | None = None
    for artifact in execution.inputs:
        if artifact.get("artifact_kind") != ArtifactKind.SCENE_DRAFT.value:
            continue
        content = artifact.get("content")
        if not isinstance(content, dict):
            continue
        prose = content.get("prose")
        scene_id = content.get("scene_id")
        if not isinstance(prose, str):
            continue
        words = len(prose.split())
        if scene_id == execution.unit_id:
            current_candidate_words = words
        else:
            accepted_words += words

    remaining_scenes = execution.unit_count - execution.unit_number + 1
    if remaining_scenes < 1:
        raise SceneProductionError("length guidance requires valid remaining scene bounds")
    remaining_minimum = max(0, minimum - accepted_words)
    remaining_maximum = max(0, maximum - accepted_words)
    guidance: dict[str, object] = {
        "policy": "story_wide_advisory",
        "story_target_words": {"minimum": minimum, "maximum": maximum},
        "accepted_scene_words_so_far": accepted_words,
        "remaining_story_target_words": {
            "minimum": remaining_minimum,
            "maximum": remaining_maximum,
        },
        "remaining_scenes_including_current": remaining_scenes,
        "current_scene_soft_allocation_words": {
            "minimum": ceil(remaining_minimum / remaining_scenes),
            "maximum": ceil(remaining_maximum / remaining_scenes),
        },
        "enforcement": (
            "advisory_only; never revise, reject, or block solely for scene word count"
        ),
    }
    if current_candidate_words is not None:
        guidance["current_candidate_words"] = current_candidate_words
    return guidance


def _messages(
    operation: _Operation,
    execution: _Execution,
    schema: dict[str, Any],
    *,
    continuity_schema_variant: _ContinuitySchemaVariant | None,
    continuity_model_context: _ContinuityModelContext | None,
) -> tuple[ModelMessage, ...]:
    schema_repair = _schema_repair_guidance(
        operation=operation,
        deployment=execution.selection.deployment,
        previous_failure=execution.previous_failure,
        continuity_schema_variant=continuity_schema_variant,
        continuity_model_context=continuity_model_context,
    )
    system = (
        "You are a registered Open Hollywood scene-production specialist. "
        f"{_INSTRUCTIONS[operation]} Return only one JSON value conforming exactly "
        "to the supplied schema. Do not include Markdown, commentary, hidden reasoning, "
        "or undeclared fields. If retry_context is present, correct every reported "
        "structural error without changing the assignment or inventing new lineage."
        + (
            " This is a structured-output repair attempt. Follow schema_repair exactly, "
            "prioritize its focus locations, and return the "
            "entire corrected object once."
            if schema_repair is not None
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
    }
    if execution.selection.deployment is ModelDeployment.LOCAL:
        payload["output_schema_delivery"] = "enforced_by_local_gateway"
    else:
        payload["output_schema"] = schema
    if operation is _Operation.CONTINUITY:
        if continuity_schema_variant is None:
            raise ValueError("continuity messages require a schema variant")
        if continuity_model_context is None:
            raise ValueError("continuity messages require their exact model context")
        payload.pop("input_artifacts", None)
        payload["candidate_draft"] = continuity_model_context.candidate_draft
        payload["accepted_prior_drafts"] = continuity_model_context.accepted_prior_drafts
        if continuity_model_context.previous_continuity_report is not None:
            payload["previous_continuity_report"] = (
                continuity_model_context.previous_continuity_report
            )
        if len(continuity_model_context.continuity_history) > 1:
            payload["continuity_history"] = [
                _bounded_continuity_history_entry(report)
                for report in continuity_model_context.continuity_history[:-1]
            ]
        payload["output_schema_variant"] = continuity_schema_variant.value
        payload["requirement_coverage_catalog"] = continuity_model_context.requirement_catalog
        payload["forbidden_shortcut_catalog"] = continuity_model_context.forbidden_shortcut_catalog
        payload["contradiction_claim_catalog"] = (
            continuity_model_context.contradiction_claim_catalog
        )
        payload["world_rule_catalog"] = continuity_model_context.world_rule_catalog
        payload["continuity_contract"] = {
            "version": SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
            "coverage_statuses": ["met", "partial", "absent"],
            "application_owns": [
                "finding_id",
                "category",
                "conflict_kind",
                "draft_assertion",
                "source",
                "lineage",
                "severity",
            ],
        }
        if continuity_model_context.previous_continuity_report is not None:
            payload["continuity_recheck"] = {
                "previous_report_version_id": continuity_model_context.previous_continuity_report[
                    "artifact_version_id"
                ],
                "historical_blocking_finding_ids": list(
                    continuity_model_context.historical_blocking_finding_ids
                ),
                "recurrence_policy": (
                    "A defect matching any historical finding keeps that stable finding ID and "
                    "is still_blocking; do not alternate repair guidance for the same canonical "
                    "claim, World Rule, or requirement."
                ),
            }
    else:
        payload["frozen_benchmark_constraints"] = execution.constraints
        if operation in {_Operation.WRITE, _Operation.CRITIQUE}:
            payload["input_artifacts"] = _scene_scoped_prompt_inputs(execution)
            payload["scene_assignment_contract"] = _scene_assignment_contract(execution)
            length_guidance = _story_length_guidance(execution)
            if length_guidance is not None:
                payload["length_guidance"] = length_guidance
        if operation is _Operation.WRITE:
            revision_contract = _targeted_revision_contract(execution)
            if revision_contract is not None:
                payload["revision_contract"] = revision_contract
    if execution.previous_failure is not None:
        retry_context = dict(execution.previous_failure)
        payload["retry_context"] = retry_context
    if schema_repair is not None:
        payload["schema_repair"] = schema_repair
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


def _scene_scoped_prompt_inputs(execution: _Execution) -> tuple[dict[str, Any], ...]:
    """Hide future scene assignments while retaining exact persisted input lineage."""
    plan = _continuity_scene_plan(execution)
    scene_id = plan.get("id")
    character_ids = {value for value in plan.get("character_ids", []) if isinstance(value, str)}
    beat_ids = {value for value in plan.get("beat_ids", []) if isinstance(value, str)}
    location_id = plan.get("location_id")

    def selected(content: Mapping[str, object], name: str, predicate: Any) -> list[object]:
        values = content.get(name)
        if not isinstance(values, list):
            return []
        return [deepcopy(value) for value in values if isinstance(value, dict) and predicate(value)]

    scoped: list[dict[str, Any]] = []
    for item in execution.inputs:
        if item.get("artifact_kind") != ArtifactKind.STORY_BLUEPRINT.value:
            scoped.append(deepcopy(item))
            continue
        content = item.get("content")
        if not isinstance(content, dict):
            raise SceneProductionError("approved Blueprint prompt input is invalid")
        bounded = {key: deepcopy(value) for key, value in item.items() if key != "content"}
        bounded["context_scope"] = "current_scene_only"
        bounded["content"] = {
            key: deepcopy(value)
            for key, value in content.items()
            if key
            not in {
                "characters",
                "relationships",
                "locations",
                "world_rules",
                "beats",
                "scene_plans",
            }
        }
        bounded_content = cast(dict[str, Any], bounded["content"])
        bounded_content.update(
            characters=selected(
                content,
                "characters",
                lambda value: value.get("id") in character_ids,
            ),
            relationships=selected(
                content,
                "relationships",
                lambda value: (
                    value.get("source_character_id") in character_ids
                    or value.get("target_character_id") in character_ids
                ),
            ),
            locations=selected(content, "locations", lambda value: value.get("id") == location_id),
            world_rules=selected(
                content,
                "world_rules",
                lambda value: (
                    (
                        not value.get("relevant_character_ids")
                        and not value.get("relevant_location_ids")
                    )
                    or bool(character_ids.intersection(value.get("relevant_character_ids", [])))
                    or location_id in value.get("relevant_location_ids", [])
                ),
            ),
            beats=selected(content, "beats", lambda value: value.get("id") in beat_ids),
            scene_plans=selected(content, "scene_plans", lambda value: value.get("id") == scene_id),
        )
        scoped.append(bounded)
    return tuple(scoped)


def _scene_assignment_contract(execution: _Execution) -> dict[str, object]:
    """Expose one exact current-scene assignment independently of prose guidance."""
    plan = _continuity_scene_plan(execution)
    character_ids = [value for value in plan.get("character_ids", []) if isinstance(value, str)]
    point_of_view = plan.get("point_of_view_character_id")
    return {
        "policy_version": "1",
        "scene_id": execution.unit_id,
        "scene_number": execution.unit_number,
        "assigned_character_ids": character_ids,
        "point_of_view_character_id": (
            point_of_view
            if isinstance(point_of_view, str)
            else (character_ids[0] if len(character_ids) == 1 else None)
        ),
        "goal": plan.get("goal"),
        "conflict": plan.get("conflict"),
        "turning_point": plan.get("turning_point"),
        "outcome": plan.get("outcome"),
        "exit_state": plan.get("exit_state"),
        "assigned_beat_ids": [
            value for value in plan.get("beat_ids", []) if isinstance(value, str)
        ],
        "hard_failures": [
            "wrong_point_of_view_or_primary_character",
            "current_scene_replaced_by_future_scene_material",
            "planned_turning_point_or_outcome_replaced",
        ],
    }


def _targeted_revision_contract(execution: _Execution) -> dict[str, object] | None:
    """Build a concrete repair ledger for a revision without expanding model authority."""
    if execution.revision_number <= 0:
        return None
    critique = _prior_critique(execution)
    report = _prior_continuity_report(execution)
    blockers = (
        [
            {
                key: deepcopy(finding.get(key))
                for key in (
                    "id",
                    "category",
                    "basis",
                    "requirement_id",
                    "world_rule_ids",
                    "recommended_resolution",
                )
                if finding.get(key) is not None
            }
            for finding in report.get("findings", [])
            if isinstance(finding, dict) and finding.get("severity") in {"error", "blocking"}
        ]
        if report is not None
        else []
    )
    critique_verdict = critique.get("verdict") if critique is not None else None
    targeted = critique_verdict == CritiqueVerdict.PASS.value and bool(blockers)
    contract: dict[str, object] = {
        "policy_version": "1",
        "mode": "targeted_continuity_repair" if targeted else "bounded_scene_revision",
        "prior_critique_verdict": critique_verdict,
        "repair_ledger": blockers,
        "preserve": [
            "scene_identity",
            "assigned_point_of_view_and_characters",
            "planned_goal_turning_point_outcome_and_exit_state",
            "all_unrelated_prose_and_successful beats",
        ],
        "prohibited": [
            "full_rewrite_for_a_localized_repair",
            "material_assigned_to_a_future_scene",
            "new_unrequested_story_mechanics",
        ],
    }
    if targeted:
        contract["minimum_prior_draft_similarity"] = _TARGETED_REVISION_MINIMUM_SIMILARITY
        contract["enforcement"] = "application_validated"
    return contract


def _prior_critique(execution: _Execution) -> dict[str, Any] | None:
    critiques = tuple(
        item.get("content")
        for item in execution.inputs
        if item.get("artifact_kind") == ArtifactKind.CRITIQUE.value
    )
    if not critiques:
        return None
    critique = critiques[-1]
    if not isinstance(critique, dict):
        raise SceneProductionError("prior critique content is invalid")
    return critique


def _prior_scene_draft(execution: _Execution) -> dict[str, Any] | None:
    drafts = tuple(
        item.get("content")
        for item in execution.inputs
        if item.get("artifact_kind") == ArtifactKind.SCENE_DRAFT.value
        and isinstance(item.get("content"), dict)
        and item["content"].get("scene_id") == execution.unit_id
        and item["content"].get("revision_number") == execution.revision_number - 1
    )
    if len(drafts) > 1:
        raise SceneProductionError("scene revision has ambiguous prior drafts")
    return cast(dict[str, Any], drafts[0]) if drafts else None


def _targeted_revision_similarity(
    output_data: Mapping[str, object],
    execution: _Execution,
) -> float | None:
    contract = _targeted_revision_contract(execution)
    if contract is None or contract.get("mode") != "targeted_continuity_repair":
        return None
    prior = _prior_scene_draft(execution)
    prior_prose = prior.get("prose") if prior is not None else None
    revised_prose = output_data.get("prose")
    if not isinstance(prior_prose, str) or not isinstance(revised_prose, str):
        return None
    prior_words = re.findall(r"\w+|[^\w\s]", prior_prose.casefold())
    revised_words = re.findall(r"\w+|[^\w\s]", revised_prose.casefold())
    return SequenceMatcher(None, prior_words, revised_words, autojunk=False).ratio()


def _validate_targeted_scene_revision(
    output_data: Mapping[str, object],
    execution: _Execution,
) -> None:
    """Reject a continuity-only revision that replaces rather than repairs the scene."""
    similarity = _targeted_revision_similarity(output_data, execution)
    if similarity is None or similarity >= _TARGETED_REVISION_MINIMUM_SIMILARITY:
        return
    raise _StructuredOutputContractError(
        "prose",
        "continuity-only revision replaced too much unrelated scene prose",
        issue_type="scene_revision_scope_exceeded",
        expected_value=f">={_TARGETED_REVISION_MINIMUM_SIMILARITY:.2f}",
        received_value=f"{similarity:.3f}",
    )


def _bounded_continuity_history_entry(report: Mapping[str, object]) -> dict[str, object]:
    """Expose historical semantic identity and repair direction without story excerpts."""
    findings = _continuity_report_findings(report)
    return {
        "artifact_version_id": report.get("artifact_version_id"),
        "findings": [
            {
                key: deepcopy(finding.get(key))
                for key in (
                    "id",
                    "category",
                    "basis",
                    "requirement_id",
                    "world_rule_ids",
                    "canonical_source_refs",
                    "recommended_resolution",
                    "recheck_disposition",
                )
                if finding.get(key) is not None
            }
            for finding in findings
            if finding.get("severity") in {"error", "blocking"}
        ],
    }


def _continuity_report_findings(report: Mapping[str, object]) -> tuple[dict[str, Any], ...]:
    content = report.get("content")
    findings = content.get("findings") if isinstance(content, dict) else report.get("findings")
    if not isinstance(findings, list):
        return ()
    return tuple(finding for finding in findings if isinstance(finding, dict))


def _benchmark_constraint_applicability(
    constraints: Mapping[str, object],
    *,
    unit_number: int,
    unit_count: int,
) -> dict[str, object]:
    """Expose story-wide benchmark text only when the final scene is evaluated."""
    if unit_number < 1 or unit_count < 1 or unit_number > unit_count:
        raise SceneProductionError("continuity assignment has invalid scene bounds")

    entries: list[dict[str, object]] = []
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
                "satisfaction_mode": (
                    "include" if kind == "required_element" else "reject_as_final_resolution"
                ),
                "companion_requirement_ids": [],
            }
            for index, value in enumerate(values, start=1)
        )

    is_final_scene = unit_number == unit_count
    return {
        "policy_version": "3",
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
    """Assign stable IDs to every due Scene Plan obligation."""
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
    scalar_obligations = (
        ("entry_state", "fact", "establish"),
        ("time_context", "timeline", "establish"),
        ("purpose", "constraint", "advance"),
        ("goal", "character", "pursue"),
        ("conflict", "fact", "dramatize"),
        ("turning_point", "setup_payoff", "occur"),
        ("outcome", "fact", "achieve"),
        ("exit_state", "fact", "establish"),
    )
    present_scalar_fields = {
        field_name
        for field_name, _, _ in scalar_obligations
        if isinstance(scene_plan.get(field_name), str) and cast(str, scene_plan[field_name]).strip()
    }
    companion_fields = {
        "entry_state": ("goal", "conflict"),
        "time_context": (),
        "purpose": ("goal", "conflict", "turning_point", "outcome"),
        "goal": ("conflict", "turning_point", "outcome", "exit_state"),
        "conflict": ("goal", "turning_point", "outcome", "exit_state"),
        "turning_point": ("goal", "conflict", "outcome", "exit_state"),
        "outcome": ("goal", "conflict", "turning_point", "exit_state"),
        "exit_state": ("goal", "turning_point", "outcome"),
    }
    for field_name, category, satisfaction_mode in scalar_obligations:
        text = scene_plan.get(field_name)
        if isinstance(text, str) and text.strip():
            due_now.append(
                {
                    "id": f"scene_plan_{field_name}",
                    "kind": "scene_plan_requirement",
                    "category": category,
                    "source_field": field_name,
                    "text": text,
                    "satisfaction_mode": satisfaction_mode,
                    "enforcement": (
                        "advisory"
                        if field_name in _ADVISORY_SCENE_PLAN_REQUIREMENTS
                        else "blocking"
                    ),
                    "companion_requirement_ids": [
                        f"scene_plan_{companion}"
                        for companion in companion_fields[field_name]
                        if companion in present_scalar_fields
                    ],
                }
            )
    continuity_requirements = scene_plan.get("continuity_requirements", [])
    if not isinstance(continuity_requirements, list) or any(
        not isinstance(value, str) for value in continuity_requirements
    ):
        raise SceneProductionError(
            "Scene Plan continuity_requirements must be a list of text values"
        )
    due_now.extend(
        {
            "id": f"scene_plan_continuity_requirement_{index}",
            "kind": "scene_plan_requirement",
            "category": "fact",
            "source_field": "continuity_requirements",
            "text": text,
            "satisfaction_mode": "satisfy",
            "enforcement": "blocking",
            "companion_requirement_ids": [],
        }
        for index, text in enumerate(continuity_requirements, start=1)
    )
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
            due_now.append(
                {
                    "id": entry_id,
                    "kind": "required_element",
                    "category": "constraint",
                    "source_field": "required_elements",
                    "text": text,
                    "satisfaction_mode": "include",
                    "enforcement": "blocking",
                    "companion_requirement_ids": [],
                }
            )
    return {
        "policy_version": "3",
        "current_scene_number": unit_number,
        "final_scene_number": unit_count,
        "is_final_scene": is_final_scene,
        "due_now": due_now,
        "deferred_until_final_scene": deferred,
        "deferred_text_intentionally_omitted": bool(deferred),
    }


def _continuity_requirement_catalogs(
    execution: _Execution,
) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    """Build one deduplicated due-required catalog plus a separate forbidden catalog."""
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
    benchmark_due = benchmark.get("due_now")
    scene_plan_due = scene_plan.get("due_now")
    if not isinstance(benchmark_due, list) or not isinstance(scene_plan_due, list):
        raise SceneProductionError("continuity requirement applicability is invalid")

    required: list[dict[str, Any]] = []
    forbidden: list[dict[str, Any]] = []
    required_by_text: dict[str, dict[str, Any]] = {}
    for raw in benchmark_due:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
            continue
        entry = deepcopy(raw)
        entry["source"] = "benchmark"
        if entry.get("kind") == "forbidden_shortcut":
            forbidden.append(entry)
            continue
        entry["category"] = ContinuityCategory.CONSTRAINT.value
        entry["enforcement"] = "blocking"
        entry["source_fields"] = ["benchmark.required_elements"]
        required.append(entry)
        text = entry.get("text")
        if isinstance(text, str):
            required_by_text[text.strip()] = entry

    for raw in scene_plan_due:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
            continue
        text = raw.get("text")
        duplicate = required_by_text.get(text.strip()) if isinstance(text, str) else None
        source_field = raw.get("source_field")
        if duplicate is not None:
            sources = duplicate.setdefault("source_fields", [])
            if isinstance(sources, list) and isinstance(source_field, str):
                sources.append(f"scene_plan.{source_field}")
            continue
        entry = deepcopy(raw)
        entry["source"] = "scene_plan"
        entry["source_fields"] = (
            [f"scene_plan.{source_field}"] if isinstance(source_field, str) else []
        )
        entry.setdefault("enforcement", "blocking")
        entry.pop("source_field", None)
        required.append(entry)
        if isinstance(text, str):
            required_by_text[text.strip()] = entry
    return tuple(required), tuple(forbidden)


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
    prior_drafts = _bounded_accepted_prior_drafts(prompt_inputs, candidate)
    prior_reports = tuple(
        _bounded_previous_continuity_report(item)
        for item in prompt_inputs
        if item.get("artifact_kind") == ArtifactKind.CONTINUITY_REPORT.value
    )
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
    requirement_catalog, forbidden_catalog = _continuity_requirement_catalogs(execution)
    requirement_kinds = {
        cast(str, entry["id"]): cast(str, entry.get("kind", "scene_plan_requirement"))
        for entry in (*requirement_catalog, *forbidden_catalog)
    }
    requirement_categories = {
        cast(str, entry["id"]): cast(str, entry.get("category", ContinuityCategory.FACT.value))
        for entry in requirement_catalog
    }
    requirement_satisfaction_modes = {
        cast(str, entry["id"]): cast(str, entry["satisfaction_mode"])
        for entry in requirement_catalog
    }
    requirement_enforcement = {
        cast(str, entry["id"]): cast(str, entry.get("enforcement", "blocking"))
        for entry in requirement_catalog
    }
    return _ContinuityModelContext(
        candidate_draft=candidate,
        accepted_prior_drafts=prior_drafts,
        previous_continuity_report=prior_reports[-1] if prior_reports else None,
        canonical_source_catalog=_continuity_canonical_source_catalog(
            canonical_inputs,
        ),
        requirement_catalog=requirement_catalog,
        forbidden_shortcut_catalog=forbidden_catalog,
        requirement_kinds=requirement_kinds,
        requirement_categories=requirement_categories,
        requirement_satisfaction_modes=requirement_satisfaction_modes,
        requirement_enforcement=requirement_enforcement,
        world_rule_ids=tuple(sorted(_continuity_world_rule_ids(execution.inputs))),
        previous_candidate_draft=_continuity_previous_candidate_draft(
            prompt_inputs,
            candidate,
        ),
        continuity_history=prior_reports,
    )


def _bounded_previous_continuity_report(item: dict[str, Any]) -> dict[str, Any]:
    """Keep only prior blockers needed to verify a continuity re-check."""
    content = item.get("content")
    if not isinstance(content, dict):
        raise SceneProductionError("prior Continuity Report prompt input is invalid")
    findings = content.get("findings")
    if not isinstance(findings, list):
        raise SceneProductionError("prior Continuity Report findings are invalid")
    bounded = {key: deepcopy(value) for key, value in item.items() if key != "content"}
    bounded["content"] = {
        "findings": [
            deepcopy(finding)
            for finding in findings
            if isinstance(finding, dict) and finding.get("severity") in {"error", "blocking"}
        ]
    }
    return bounded


def _bounded_accepted_prior_drafts(
    prompt_inputs: tuple[dict[str, Any], ...],
    candidate: Mapping[str, object],
) -> tuple[dict[str, Any], ...]:
    """Expose only the immediately prior accepted scene ending as non-evidence context."""
    candidate_content = candidate.get("content")
    current_scene_number = (
        candidate_content.get("scene_number") if isinstance(candidate_content, dict) else None
    )
    prior: list[tuple[int, dict[str, Any]]] = []
    for item in prompt_inputs:
        if item.get("artifact_kind") != ArtifactKind.SCENE_DRAFT.value or item.get(
            "artifact_version_id"
        ) == candidate.get("artifact_version_id"):
            continue
        content = item.get("content")
        if not isinstance(content, dict) or not isinstance(content.get("prose"), str):
            continue
        scene_number = content.get("scene_number")
        if not isinstance(scene_number, int):
            continue
        if isinstance(current_scene_number, int) and scene_number >= current_scene_number:
            continue
        prior.append((scene_number, item))
    if not prior:
        return ()
    _, item = max(prior, key=lambda entry: entry[0])
    bounded = {key: deepcopy(value) for key, value in item.items() if key != "content"}
    content = cast(dict[str, Any], item["content"])
    prose = cast(str, content["prose"]).strip()
    bounded["content"] = {key: deepcopy(value) for key, value in content.items() if key != "prose"}
    cast(dict[str, Any], bounded["content"])["ending_excerpt"] = prose[-1200:]
    bounded["continuity_role"] = "immediately_prior_accepted_scene_ending_not_valid_evidence"
    return (bounded,)


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


def _continuity_previous_candidate_draft(
    prompt_inputs: tuple[dict[str, Any], ...],
    candidate: Mapping[str, object],
) -> dict[str, Any] | None:
    """Return the immediately preceding draft revision for application-only re-check validation."""
    candidate_content = candidate.get("content")
    if not isinstance(candidate_content, dict):
        return None
    scene_id = candidate_content.get("scene_id")
    revision_number = candidate_content.get("revision_number")
    if (
        not isinstance(scene_id, str)
        or not isinstance(revision_number, int)
        or revision_number <= 0
    ):
        return None
    prior = tuple(
        item
        for item in prompt_inputs
        if item.get("artifact_kind") == ArtifactKind.SCENE_DRAFT.value
        and item.get("artifact_version_id") != candidate.get("artifact_version_id")
        and isinstance(item.get("content"), dict)
        and item["content"].get("scene_id") == scene_id
        and item["content"].get("revision_number") == revision_number - 1
    )
    if len(prior) > 1:
        raise SceneProductionError("continuity re-check has ambiguous prior candidate drafts")
    return deepcopy(prior[0]) if prior else None


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
    if item.get("artifact_kind") == ArtifactKind.SCENE_PLAN.value:
        content = item.get("content")
        if not isinstance(content, dict):
            raise SceneProductionError("Scene Plan continuity input is invalid")
        bounded = deepcopy(item)
        bounded["content"] = {
            key: value for key, value in content.items() if key not in _SCENE_PLAN_OBLIGATION_FIELDS
        }
        return bounded
    if item.get("artifact_kind") == ArtifactKind.STORY_BIBLE.value:
        content = item.get("content")
        if not isinstance(content, dict):
            raise SceneProductionError("Story Bible continuity input is invalid")
        story_bible_content = cast(dict[str, Any], content)
        plan = _continuity_scene_plan(execution)
        character_ids = {value for value in plan.get("character_ids", []) if isinstance(value, str)}
        location_id = plan.get("location_id")
        relationship_ids: set[str] = set()
        for source in execution.inputs:
            if source.get("artifact_kind") != ArtifactKind.STORY_BLUEPRINT.value:
                continue
            blueprint = source.get("content")
            relationships = blueprint.get("relationships") if isinstance(blueprint, dict) else None
            if isinstance(relationships, list):
                relationship_ids.update(
                    cast(str, relationship["id"])
                    for relationship in relationships
                    if isinstance(relationship, dict)
                    and isinstance(relationship.get("id"), str)
                    and (
                        relationship.get("source_character_id") in character_ids
                        or relationship.get("target_character_id") in character_ids
                    )
                )

        def selected(name: str, predicate: Any) -> list[object]:
            values = story_bible_content.get(name)
            if not isinstance(values, list):
                return []
            return [value for value in values if isinstance(value, dict) and predicate(value)]

        bounded = deepcopy(item)
        bounded["content"] = {
            "timeline": selected(
                "timeline",
                lambda event: (
                    not event.get("character_ids")
                    and event.get("location_id") is None
                    or bool(character_ids.intersection(event.get("character_ids", [])))
                    or event.get("location_id") == location_id
                ),
            ),
            "established_facts": selected(
                "established_facts",
                lambda fact: (
                    not fact.get("character_ids")
                    and not fact.get("location_ids")
                    or bool(character_ids.intersection(fact.get("character_ids", [])))
                    or location_id in fact.get("location_ids", [])
                ),
            ),
            "character_states": selected(
                "character_states", lambda state: state.get("character_id") in character_ids
            ),
            "relationship_states": selected(
                "relationship_states",
                lambda state: state.get("relationship_id") in relationship_ids,
            ),
            "location_states": selected(
                "location_states", lambda state: state.get("location_id") == location_id
            ),
            "threads": deepcopy(story_bible_content.get("threads", [])),
            "prohibited_contradictions": deepcopy(
                story_bible_content.get("prohibited_contradictions", [])
            ),
        }
        return bounded
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


def _continuity_claim_categories(
    artifact_kind: str,
    source_path: str,
) -> tuple[str, ...]:
    """Classify selectable canonical claims without asking the model to infer provenance."""
    if artifact_kind == ArtifactKind.SCENE_PLAN.value:
        return ()
    if artifact_kind == ArtifactKind.WORLD_RULE.value or ".world_rules[" in source_path:
        return (ContinuityCategory.WORLD_RULE.value,)
    if artifact_kind == ArtifactKind.BEAT.value or ".beats[" in source_path:
        # A current Blueprint beat is a planned obligation, not stable story history.
        # The Scene Plan requirement catalog is its exclusive continuity route.
        return ()
    field_name = source_path.rsplit(".", 1)[-1]
    is_blueprint_character = ".characters[" in source_path
    if artifact_kind == ArtifactKind.CHARACTER.value or is_blueprint_character:
        if field_name == "name":
            return (ContinuityCategory.CHARACTER.value,)
        if field_name in {"secrets", "initial_knowledge"}:
            return (ContinuityCategory.CHARACTER_KNOWLEDGE.value,)
        # Goals, traits, voice, arc, and descriptive phrasing are open creative
        # guidance. They become stable continuity facts only after Story Bible
        # materialization.
        return ()
    is_blueprint_relationship = ".relationships[" in source_path
    if artifact_kind == ArtifactKind.RELATIONSHIP.value or is_blueprint_relationship:
        if field_name == "label" or (
            field_name == "history" and artifact_kind == ArtifactKind.RELATIONSHIP.value
        ):
            return (ContinuityCategory.RELATIONSHIP.value,)
        return ()
    is_blueprint_location = ".locations[" in source_path
    if artifact_kind == ArtifactKind.LOCATION.value or is_blueprint_location:
        if field_name in {"name", "constraints"}:
            return (ContinuityCategory.LOCATION.value,)
        # Description, atmosphere, function, and sensory details are explicitly
        # non-exhaustive and cannot make additive prose contradictory.
        return ()
    path_categories = (
        (".timeline", (ContinuityCategory.TIMELINE.value,)),
        (".established_facts", (ContinuityCategory.FACT.value,)),
        (
            ".character_states",
            (
                ContinuityCategory.CHARACTER.value,
                ContinuityCategory.CHARACTER_KNOWLEDGE.value,
            ),
        ),
        (".relationship_states", (ContinuityCategory.RELATIONSHIP.value,)),
        (".location_states", (ContinuityCategory.LOCATION.value,)),
        (".threads", (ContinuityCategory.SETUP_PAYOFF.value,)),
        (".prohibited_contradictions", (ContinuityCategory.FACT.value,)),
        (
            ".characters",
            (
                ContinuityCategory.CHARACTER.value,
                ContinuityCategory.CHARACTER_KNOWLEDGE.value,
            ),
        ),
        (".relationships", (ContinuityCategory.RELATIONSHIP.value,)),
        (".locations", (ContinuityCategory.LOCATION.value,)),
        (
            ".beats",
            (
                ContinuityCategory.FACT.value,
                ContinuityCategory.TIMELINE.value,
                ContinuityCategory.SETUP_PAYOFF.value,
            ),
        ),
    )
    for marker, categories in path_categories:
        if marker in source_path:
            return categories
    artifact_categories = {
        ArtifactKind.CHARACTER.value: (
            ContinuityCategory.CHARACTER.value,
            ContinuityCategory.CHARACTER_KNOWLEDGE.value,
        ),
        ArtifactKind.RELATIONSHIP.value: (ContinuityCategory.RELATIONSHIP.value,),
        ArtifactKind.LOCATION.value: (ContinuityCategory.LOCATION.value,),
        ArtifactKind.BEAT.value: (
            ContinuityCategory.FACT.value,
            ContinuityCategory.TIMELINE.value,
            ContinuityCategory.SETUP_PAYOFF.value,
        ),
    }
    return artifact_categories.get(artifact_kind, ())


def _continuity_canonical_source_catalog(
    inputs: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], ...]:
    """Build stable, self-describing contradiction claims from non-requirement canon."""
    claims: list[dict[str, Any]] = []

    def add_claim(
        value: object,
        *,
        artifact: dict[str, Any],
        source_path: str,
        canonical_id: str | None,
        related_ids: tuple[str, ...],
        categories: tuple[str, ...] | None = None,
    ) -> None:
        claim_text = (
            value.strip()
            if isinstance(value, str)
            else json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        )
        if not claim_text:
            return
        claim: dict[str, Any] = {
            "reference_id": f"canonical_source_{len(claims) + 1:04d}",
            "artifact_kind": artifact["artifact_kind"],
            "artifact_key": artifact["artifact_key"],
            "artifact_version_id": artifact["artifact_version_id"],
            "source_path": source_path,
            "claim": claim_text,
        }
        claim_categories = categories or _continuity_claim_categories(
            cast(str, artifact["artifact_kind"]),
            source_path,
        )
        if claim_categories:
            claim["categories"] = list(claim_categories)
        if claim_categories and ContinuityCategory.WORLD_RULE.value not in claim_categories:
            source_label = re.sub(
                r"[^a-z0-9]+",
                "_",
                re.sub(r"\[\d+\]", "", source_path).casefold(),
            ).strip("_")
            identity_label = canonical_id or cast(str, artifact["artifact_key"])
            base = re.sub(
                r"[^a-z0-9]+",
                "_",
                f"{artifact['artifact_kind']}_{identity_label}_{source_label}".casefold(),
            ).strip("_")[:90]
            existing_ids = {
                cast(str, existing["claim_id"])
                for existing in claims
                if isinstance(existing.get("claim_id"), str)
            }
            claim_id = base
            if claim_id in existing_ids:
                suffix = hashlib.sha256(
                    f"{artifact['artifact_key']}:{source_path}".encode()
                ).hexdigest()[:8]
                claim_id = f"{base[:90]}_{suffix}"
            claim["claim_id"] = claim_id
        if canonical_id is not None:
            claim["canonical_id"] = canonical_id
        if related_ids:
            claim["related_ids"] = list(related_ids)
        claims.append(claim)

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
            claim_categories = _continuity_claim_categories(
                cast(str, artifact["artifact_kind"]),
                source_path,
            )
            if source_path != "content" and local_id is not None and claim_categories:
                add_claim(
                    value,
                    artifact=artifact,
                    source_path=source_path,
                    canonical_id=local_id,
                    related_ids=local_related,
                    categories=claim_categories,
                )
                return
            for key, nested in value.items():
                if (
                    artifact.get("artifact_kind") == ArtifactKind.SCENE_PLAN.value
                    and key in _SCENE_PLAN_OBLIGATION_FIELDS
                ):
                    continue
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
            if value and all(not isinstance(nested, (dict, list)) for nested in value):
                if field_name is not None and not field_name.endswith(("_id", "_ids")):
                    add_claim(
                        value,
                        artifact=artifact,
                        source_path=source_path,
                        canonical_id=canonical_id,
                        related_ids=related_ids,
                    )
                return
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
        add_claim(
            value,
            artifact=artifact,
            source_path=source_path,
            canonical_id=canonical_id,
            related_ids=related_ids,
        )

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
    return tuple(
        claim
        for claim in claims
        if "claim_id" in claim or ContinuityCategory.WORLD_RULE.value in claim.get("categories", [])
    )


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
        _validate_targeted_scene_revision(materialized, execution)
        return materialized
    if operation is _Operation.CRITIQUE:
        critique_task = cast(SceneCritiqueTask, task)
        materialized = _normalize_story_length_critique(materialized, execution)
        materialized = _normalize_scene_assignment_critique(materialized)
        scores = materialized.get("scores")
        if (
            not isinstance(scores, list)
            or not scores
            or any(
                not isinstance(score, dict)
                or not isinstance(score.get("score"), int)
                or isinstance(score.get("score"), bool)
                for score in scores
            )
        ):
            raise _StructuredOutputContractError(
                "scores",
                "critic scores must contain numeric rubric scores before overall score derivation",
                issue_type="invalid_rubric_scores",
            )
        materialized["overall_score"] = float(
            round(
                sum(cast(int, score["score"]) for score in cast(list[dict[str, Any]], scores))
                / len(scores),
                2,
            )
        )
        materialized.update(
            target_artifact_kind=ArtifactKind.SCENE_DRAFT.value,
            target_artifact_key=critique_task.draft.artifact_key,
            target_artifact_version_id=str(critique_task.draft.version_id),
        )
        return materialized
    if operation is _Operation.CONTINUITY:
        continuity_task = cast(ContinuityCheckTask, task)
        scene_id = continuity_task.unit.unit_id
        model_context = _continuity_model_context(execution)
        missing_requirement_findings = _materialize_requirement_coverage(
            materialized,
            model_context,
        )
        for field_name in _CONTINUITY_MODEL_REQUIREMENT_AUDIT_FIELDS:
            materialized.pop(field_name, None)
        materialized.update(
            story_bible_version_id=str(continuity_task.story_bible.version_id),
            scene_version_id=str(continuity_task.draft.version_id),
            scene_plan_version_id=str(continuity_task.unit.plan.version_id),
            scene_id=scene_id,
            scene_number=continuity_task.unit.unit_number,
            checked_categories=[category.value for category in ContinuityCategory],
        )
        findings = _continuity_model_findings(materialized, model_context)
        for field_name in _CONTINUITY_MODEL_RECHECK_REPORT_FIELDS:
            materialized.pop(field_name, None)
        if isinstance(findings, list):
            prior_resolutions = _prior_continuity_resolutions(execution)
            evidence_findings = [
                _materialize_continuity_evidence(finding, model_context) for finding in findings
            ]
            evidence_findings = [
                _downgrade_qualitative_non_world_contradiction(finding)
                for finding in evidence_findings
            ]
            identified_findings = [
                _materialize_continuity_identity(
                    finding,
                    model_context,
                    index=index,
                    revision_number=execution.revision_number,
                )
                for index, finding in enumerate(evidence_findings)
            ]
            all_findings = _consolidate_requirement_basis(
                [*identified_findings, *missing_requirement_findings],
                model_context,
            )
            all_findings = _consolidate_continuity_semantic_duplicates(
                all_findings,
                model_context,
            )
            _validate_unique_continuity_finding_ids(all_findings)
            materialized_findings = [
                _materialize_continuity_finding(
                    finding,
                    scene_id,
                    prior_resolutions=prior_resolutions,
                )
                for finding in all_findings
            ]
            _validate_continuity_finding_contract(materialized_findings, execution)
            _validate_new_recheck_contradiction_evidence(
                materialized_findings,
                model_context,
            )
            _validate_continuity_recheck_analysis(materialized_findings, execution)
            materialized["findings"] = [
                _strip_continuity_certification_fields(finding) for finding in materialized_findings
            ]
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


def _normalize_story_length_critique(
    critique: dict[str, Any],
    execution: _Execution,
) -> dict[str, Any]:
    """Keep the story-wide advisory range from becoming a per-scene revision gate."""
    issues = critique.get("issues")
    if not isinstance(issues, list) or not issues:
        return critique
    if _has_explicit_hard_scene_length_constraint(execution.constraints):
        return critique

    normalized = dict(critique)
    normalized_issues: list[object] = []
    length_issue_count = 0
    for issue in issues:
        if not isinstance(issue, dict) or not _is_story_length_only_critique_issue(issue):
            normalized_issues.append(issue)
            continue
        length_issue_count += 1
        normalized_issues.append({**issue, "severity": CritiqueSeverity.NOTE.value})
    if not length_issue_count:
        return critique
    normalized["issues"] = normalized_issues
    if length_issue_count == len(issues):
        normalized["verdict"] = CritiqueVerdict.PASS.value
    return normalized


def _normalize_scene_assignment_critique(
    critique: dict[str, Any],
) -> dict[str, Any]:
    """Prevent explicit scene-assignment drift from surviving as a minor PASS issue."""
    issues = critique.get("issues")
    if not isinstance(issues, list) or not issues:
        return critique
    normalized_issues: list[object] = []
    promoted = False
    for issue in issues:
        if not isinstance(issue, dict):
            normalized_issues.append(issue)
            continue
        category = issue.get("category")
        description = issue.get("description")
        if not isinstance(category, str) or not isinstance(description, str):
            normalized_issues.append(issue)
            continue
        diagnostic = f"{category} {description}"
        exact_assignment_failure = _SCENE_ASSIGNMENT_CRITIQUE_PATTERN.search(diagnostic) is not None
        planned_anchor_failure = (
            _SCENE_PLAN_ANCHOR_PATTERN.search(diagnostic) is not None
            and _SCENE_PLAN_DRIFT_PATTERN.search(description) is not None
        )
        if not exact_assignment_failure and not planned_anchor_failure:
            normalized_issues.append(issue)
            continue
        promoted = True
        normalized_issues.append({**issue, "severity": CritiqueSeverity.BLOCKING.value})
    if not promoted:
        return critique
    return {
        **critique,
        "issues": normalized_issues,
        "verdict": CritiqueVerdict.REVISE.value,
    }


def _is_story_length_only_critique_issue(issue: Mapping[str, object]) -> bool:
    """Recognize an issue whose asserted defect is only scene-level word count."""
    description = issue.get("description")
    category = issue.get("category")
    if not isinstance(description, str) or not isinstance(category, str):
        return False
    primary = f"{category} {description}"
    if (
        _STORY_LENGTH_ISSUE_PATTERN.search(primary) is None
        or _STORY_LENGTH_TARGET_PATTERN.search(primary) is None
        or _STRUCTURAL_CRITIQUE_PATTERN.search(description) is not None
    ):
        return False
    recommendation = issue.get("recommendation")
    if not isinstance(recommendation, str):
        return False
    return (
        _STORY_LENGTH_ISSUE_PATTERN.search(recommendation) is not None
        or re.search(r"\b(?:expand|lengthen|trim|shorten|cut)\b", recommendation, re.IGNORECASE)
        is not None
    )


def _has_explicit_hard_scene_length_constraint(constraints: Mapping[str, object]) -> bool:
    """Preserve an expressly hard scene-length request outside the advisory benchmark range."""
    if any(
        key in constraints
        for key in ("hard_scene_word_count", "strict_scene_word_count", "scene_word_limit")
    ):
        return True
    required = constraints.get("required_elements")
    if not isinstance(required, list):
        return False
    hard_length = re.compile(
        r"\b(?:must|exactly|at least|at most|no (?:more|fewer) than)\b.{0,40}\bwords?\b",
        re.IGNORECASE,
    )
    return any(isinstance(item, str) and hard_length.search(item) is not None for item in required)


def _materialize_requirement_coverage(
    output_data: Mapping[str, object],
    model_context: _ContinuityModelContext,
) -> list[dict[str, object]]:
    """Validate exact keyed coverage and materialize one auditable finding per gap."""
    expected_ids = tuple(model_context.requirement_categories)
    coverage = output_data.get("requirement_coverage")
    if not isinstance(coverage, dict):
        raise _StructuredOutputContractError(
            "requirement_coverage",
            "requirement_coverage must be an object keyed by every exact due requirement ID",
            issue_type="requirement_partition_mismatch",
        )
    selected_ids = set(coverage)
    if selected_ids != set(expected_ids):
        omitted = sorted(set(expected_ids) - selected_ids)
        unexpected = sorted(selected_ids - set(expected_ids))
        raise _StructuredOutputContractError(
            "requirement_coverage",
            "requirement coverage must include every exact due requirement key; "
            f"omitted={omitted}, unexpected={unexpected}",
            issue_type="requirement_partition_mismatch",
        )
    materialized: list[dict[str, object]] = []
    prior_ids = set(model_context.historical_blocking_finding_ids)
    for requirement_id in expected_ids:
        raw = coverage[requirement_id]
        if not isinstance(raw, dict) or raw.get("status") not in _COVERAGE_STATUSES:
            raise _StructuredOutputContractError(
                f"requirement_coverage.{requirement_id}",
                "coverage entry must use met, partial, or absent",
                issue_type="requirement_partition_mismatch",
            )
        status = cast(str, raw["status"])
        raw_evidence_refs = raw.get("evidence_refs")
        if not isinstance(raw_evidence_refs, list) or any(
            not isinstance(reference, str) for reference in raw_evidence_refs
        ):
            raise _StructuredOutputContractError(
                f"requirement_coverage.{requirement_id}.evidence_refs",
                "coverage evidence must use exact candidate-draft evidence references",
                issue_type="requirement_coverage_evidence_invalid",
            )
        evidence_refs = _normalize_continuity_evidence_refs(
            raw_evidence_refs,
            model_context,
            location=f"requirement_coverage.{requirement_id}.evidence_refs",
            issue_type="requirement_coverage_evidence_invalid",
        )
        if status in {"met", "partial"} and not evidence_refs:
            raise _StructuredOutputContractError(
                f"requirement_coverage.{requirement_id}.evidence_refs",
                f"{status} coverage requires exact candidate-draft evidence references",
                issue_type="requirement_coverage_evidence_invalid",
            )
        if status == "absent":
            search_result = raw.get("evidence_search_result")
            if search_result == "no_related_passage" and evidence_refs:
                raise _StructuredOutputContractError(
                    f"requirement_coverage.{requirement_id}.evidence_search_result",
                    "no_related_passage requires an empty evidence_refs array",
                    issue_type="requirement_coverage_evidence_invalid",
                )
            if search_result == "closest_passages_selected" and not evidence_refs:
                raise _StructuredOutputContractError(
                    f"requirement_coverage.{requirement_id}.evidence_search_result",
                    "closest_passages_selected requires at least one exact evidence reference",
                    issue_type="requirement_coverage_evidence_invalid",
                )
        if status == "met":
            continue
        exact_coverage_evidence = _resolve_continuity_evidence_refs(
            evidence_refs,
            model_context,
            location=f"requirement_coverage.{requirement_id}.evidence_refs",
            allow_empty=status == "absent",
            issue_type="requirement_coverage_evidence_invalid",
        )
        enforcement = model_context.requirement_enforcement[requirement_id]
        finding = {
            key: value
            for key, value in raw.items()
            if key not in {"status", "evidence_refs", "evidence_search_result"}
        }
        is_advisory = status == "partial" or enforcement == "advisory"
        finding_id = (
            f"advisory_{status}_{requirement_id}" if is_advisory else f"missing_{requirement_id}"
        )
        finding.update(
            id=finding_id,
            requirement_id=requirement_id,
            category=model_context.requirement_categories[requirement_id],
            severity="warning" if is_advisory else "error",
            basis=(None if is_advisory else ContinuityFindingBasis.MISSING_REQUIREMENT.value),
            evidence=[],
            coverage_status=status,
            coverage_evidence=exact_coverage_evidence,
            canonical_source_refs=[],
            world_rule_ids=[],
            related_character_ids=[],
            related_location_ids=[],
            related_beat_ids=[],
            related_scene_ids=[],
        )
        if is_advisory:
            finding.pop("repair_assessment", None)
        elif model_context.previous_continuity_report is not None:
            finding["recheck_disposition"] = (
                ContinuityRecheckDisposition.STILL_BLOCKING.value
                if finding_id in prior_ids
                else ContinuityRecheckDisposition.NEWLY_EXPOSED.value
            )
            finding["repair_assessment"] = finding["coverage_assessment"]
        materialized.append(finding)
    return materialized


# Compatibility alias retained for internal callers while v17 migrations settle.
_materialize_requirement_audit = _materialize_requirement_coverage


def _continuity_model_findings(
    output_data: Mapping[str, object],
    model_context: _ContinuityModelContext,
) -> list[object] | object:
    """Convert the compact model-only re-check partition into canonical findings."""
    if model_context.previous_continuity_report is None:
        return output_data.get("findings")
    prior = output_data.get("prior_finding_rechecks")
    new = output_data.get("new_findings")
    expected_ids = model_context.prior_model_finding_ids
    actual_ids = set(prior) if isinstance(prior, dict) else set()
    if not isinstance(prior, dict) or actual_ids != set(expected_ids):
        omitted = sorted(set(expected_ids) - actual_ids)
        unexpected = sorted(actual_ids - set(expected_ids))
        raise _StructuredOutputContractError(
            "prior_finding_rechecks",
            "prior finding audit must include every exact prior model finding key; "
            f"omitted={omitted}, unexpected={unexpected}",
            issue_type="prior_finding_partition_mismatch",
        )
    if not isinstance(new, list):
        raise _StructuredOutputContractError(
            "new_findings",
            "new_findings must be an array",
            issue_type="prior_finding_partition_mismatch",
        )
    previous_content = model_context.previous_continuity_report.get("content")
    previous_findings = (
        previous_content.get("findings") if isinstance(previous_content, dict) else None
    )
    if not isinstance(previous_findings, list):
        raise _StructuredOutputContractError(
            "prior_finding_rechecks",
            "prior continuity report is missing its blocking findings",
            issue_type="prior_finding_partition_mismatch",
        )
    previous_by_id = {
        finding["id"]: finding
        for finding in previous_findings
        if isinstance(finding, dict) and isinstance(finding.get("id"), str)
    }
    materialized: list[object] = []
    for finding_id in expected_ids:
        entry = prior[finding_id]
        if not isinstance(entry, dict) or entry.get("status") not in {
            "resolved",
            "still_blocking",
        }:
            raise _StructuredOutputContractError(
                f"prior_finding_rechecks.{finding_id}",
                "prior finding must declare status resolved or still_blocking",
                issue_type="prior_finding_partition_mismatch",
            )
        if entry["status"] == "resolved":
            continue
        retained_finding = previous_by_id.get(finding_id)
        repair_assessment = entry.get("repair_assessment")
        revised_refs = entry.get("revised_draft_evidence_refs")
        if not isinstance(retained_finding, dict):
            raise _StructuredOutputContractError(
                f"prior_finding_rechecks.{finding_id}",
                "a still-blocking prior entry must resolve to one persisted prior finding",
                issue_type="prior_finding_partition_mismatch",
            )
        if not isinstance(repair_assessment, str) or not isinstance(revised_refs, list):
            raise _StructuredOutputContractError(
                f"prior_finding_rechecks.{finding_id}",
                "a still-blocking prior entry requires repair assessment and revised evidence",
                issue_type="prior_finding_partition_mismatch",
            )
        retained = {
            key: deepcopy(value)
            for key, value in retained_finding.items()
            if key not in {"id", "blocks_approval", *_CONTINUITY_RECHECK_ONLY_FIELDS}
        }
        retained.update(
            prior_finding_id=finding_id,
            repair_assessment=repair_assessment,
            revised_draft_evidence_refs=revised_refs,
            _prior_finding_recheck=True,
        )
        if (
            retained.get("basis") == ContinuityFindingBasis.CONTRADICTION.value
            and retained.get("category") != ContinuityCategory.WORLD_RULE.value
        ):
            source_refs = retained.get("canonical_source_refs")
            claim_ids = [
                model_context.canonical_source_claim_ids[source_ref]
                for source_ref in source_refs or []
                if isinstance(source_ref, str)
                and source_ref in model_context.canonical_source_claim_ids
            ]
            if not claim_ids:
                raise _StructuredOutputContractError(
                    f"prior_finding_rechecks.{finding_id}",
                    "prior contradiction provenance is unavailable in the current claim catalog",
                    issue_type="non_world_claim_provenance_invalid",
                )
            retained["canonical_claim_ids"] = claim_ids
        materialized.append(retained)
    materialized.extend(new)
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
    """Return the latest exact repair text for every historical continuity blocker."""
    resolutions: dict[str, str] = {}
    for report in _prior_continuity_reports(execution):
        findings = report.get("findings")
        if not isinstance(findings, list):
            raise ValueError("prior continuity report findings are invalid")
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


def _downgrade_qualitative_non_world_contradiction(finding: object) -> object:
    """Route qualitative craft feedback away from the blocking contradiction branch."""
    if (
        not isinstance(finding, dict)
        or finding.get("basis") != ContinuityFindingBasis.CONTRADICTION.value
        or finding.get("category") == ContinuityCategory.WORLD_RULE.value
        or finding.get("severity") not in {"error", "blocking"}
        or finding.get("_prior_finding_recheck") is True
    ):
        return finding
    assessment_text = " ".join(
        value
        for field_name in ("summary", "conflict_explanation", "repair_assessment")
        if isinstance((value := finding.get(field_name)), str)
    )
    resolution = finding.get("recommended_resolution")
    is_qualitative = any(
        pattern.search(assessment_text) for pattern in _QUALITATIVE_CONTRADICTION_PATTERNS
    ) or (isinstance(resolution, str) and _ADDITIVE_REPAIR_PATTERN.search(resolution) is not None)
    if not is_qualitative:
        return finding
    materialized = dict(finding)
    materialized.update(
        severity="warning",
        basis=None,
        evidence=[],
        blocks_approval=False,
    )
    for field_name in (
        "requirement_id",
        "coverage_assessment",
        "coverage_status",
        "coverage_evidence",
        "recheck_disposition",
        "repair_assessment",
        "revised_evidence",
    ):
        materialized.pop(field_name, None)
    return materialized


def _validate_new_recheck_contradiction_evidence(
    findings: list[object],
    model_context: _ContinuityModelContext,
) -> None:
    """Require a newly exposed non-world blocker to cite evidence changed by the revision."""
    previous = model_context.previous_candidate_draft
    previous_content = previous.get("content") if isinstance(previous, dict) else None
    previous_prose = previous_content.get("prose") if isinstance(previous_content, dict) else None
    if not isinstance(previous_prose, str):
        return
    for index, finding in enumerate(findings):
        if (
            not isinstance(finding, dict)
            or finding.get("basis") != ContinuityFindingBasis.CONTRADICTION.value
            or finding.get("category") == ContinuityCategory.WORLD_RULE.value
            or finding.get("recheck_disposition")
            != ContinuityRecheckDisposition.NEWLY_EXPOSED.value
        ):
            continue
        evidence = finding.get("revised_evidence") or finding.get("evidence")
        if (
            isinstance(evidence, list)
            and evidence
            and all(isinstance(excerpt, str) and excerpt in previous_prose for excerpt in evidence)
        ):
            raise _StructuredOutputContractError(
                f"findings.{index}.revised_evidence",
                "a newly exposed non-world contradiction must cite an assertion introduced "
                "or changed by the revision",
                issue_type="new_contradiction_not_new_to_revision",
            )


def _validate_continuity_finding_contract(
    findings: list[object],
    execution: _Execution,
) -> None:
    """Enforce canonical evidence, source, requirement, and world-rule guarantees."""
    draft_prose = _current_scene_draft_prose(execution)
    model_context = _continuity_model_context(execution)
    source_refs = set(model_context.canonical_source_refs)
    requirement_kinds = model_context.requirement_kinds
    world_rule_ids = _continuity_world_rule_ids(execution.inputs)
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue
        severity = finding.get("severity")
        basis = finding.get("basis")
        location = f"findings.{index}"
        coverage_status = finding.get("coverage_status")
        coverage_evidence = finding.get("coverage_evidence")
        if coverage_status is not None:
            if coverage_status not in {"partial", "absent"} or not isinstance(
                coverage_evidence, list
            ):
                raise _StructuredOutputContractError(
                    f"{location}.coverage_status",
                    "requirement gap must use partial or absent with coverage evidence",
                )
            if coverage_status == "partial" and not coverage_evidence:
                raise _StructuredOutputContractError(
                    f"{location}.coverage_evidence",
                    "partial requirement coverage requires exact closest evidence",
                )
            if any(
                not isinstance(excerpt, str) or excerpt not in draft_prose
                for excerpt in coverage_evidence
            ):
                raise _StructuredOutputContractError(
                    f"{location}.coverage_evidence",
                    "coverage evidence must contain exact excerpts from the current draft",
                    issue_type="requirement_coverage_evidence_invalid",
                )
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
                issue_type="evidence_not_in_current_draft",
            )

        if basis == ContinuityFindingBasis.CONTRADICTION.value:
            if finding.get("category") == ContinuityCategory.CONSTRAINT.value:
                raise _StructuredOutputContractError(
                    f"{location}.category",
                    "required omissions must use requirement_coverage, not a constraint "
                    "contradiction",
                    issue_type="missing_requirement_used_as_contradiction",
                )
            references = finding.get("canonical_source_refs")
            if (
                not isinstance(references, list)
                or not references
                or any(reference not in source_refs for reference in references)
            ):
                raise _StructuredOutputContractError(
                    f"{location}.canonical_source_refs",
                    "contradiction sources must be copied from canonical_source_catalog",
                    issue_type="missing_requirement_used_as_contradiction",
                )
            if finding.get("category") != ContinuityCategory.WORLD_RULE.value:
                claim_ids = finding.get("canonical_claim_ids")
                if (
                    not isinstance(claim_ids, list)
                    or len(claim_ids) != 1
                    or any(
                        not isinstance(claim_id, str)
                        or claim_id not in model_context.canonical_claim_source_refs
                        for claim_id in claim_ids
                    )
                ):
                    raise _StructuredOutputContractError(
                        f"{location}.canonical_claim_ids",
                        "non-world contradictions require exact typed canonical claim IDs",
                        issue_type="non_world_claim_provenance_invalid",
                    )
                expected_refs = list(
                    dict.fromkeys(
                        model_context.canonical_claim_source_refs[claim_id]
                        for claim_id in claim_ids
                    )
                )
                if references != expected_refs:
                    raise _StructuredOutputContractError(
                        f"{location}.canonical_source_refs",
                        "application-derived non-world provenance is incomplete",
                        issue_type="non_world_claim_provenance_invalid",
                        expected_value=json.dumps(expected_refs, separators=(",", ":")),
                        received_value=json.dumps(references, separators=(",", ":")),
                    )
                expected_category = model_context.canonical_claim_categories[
                    cast(str, claim_ids[0])
                ][0]
                if finding.get("category") != expected_category:
                    raise _StructuredOutputContractError(
                        f"{location}.category",
                        "application-derived contradiction category is inconsistent",
                        issue_type="non_world_claim_provenance_invalid",
                        expected_value=expected_category,
                        received_value=str(finding.get("category")),
                    )
                if finding.get("_prior_finding_recheck") is not True:
                    expected_conflict_kind = _NON_WORLD_CONFLICT_KIND_BY_CATEGORY.get(
                        expected_category
                    )
                    if finding.get("conflict_kind") != expected_conflict_kind:
                        raise _StructuredOutputContractError(
                            f"{location}.conflict_kind",
                            "the application-derived contradiction kind is inconsistent",
                            issue_type="non_world_conflict_certificate_invalid",
                            expected_value=str(expected_conflict_kind),
                            received_value=str(finding.get("conflict_kind")),
                        )
                    if finding.get("conflict_disposition") != _DIRECT_CONFLICT_DISPOSITION:
                        raise _StructuredOutputContractError(
                            f"{location}.conflict_disposition",
                            "a non-world contradiction must select the direct-conflict disposition",
                            issue_type="non_world_conflict_certificate_invalid",
                            expected_value=_DIRECT_CONFLICT_DISPOSITION,
                            received_value=str(finding.get("conflict_disposition")),
                        )
                    if finding.get("repair_action") not in _NON_WORLD_REPAIR_ACTIONS:
                        raise _StructuredOutputContractError(
                            f"{location}.repair_action",
                            "a contradiction repair must remove, replace, or correct the "
                            "existing incompatible assertion",
                            issue_type="non_world_conflict_certificate_invalid",
                            expected_value=json.dumps(
                                _NON_WORLD_REPAIR_ACTIONS,
                                separators=(",", ":"),
                            ),
                            received_value=str(finding.get("repair_action")),
                        )
        else:
            requirement_id = finding.get("requirement_id")
            is_valid_requirement = (
                isinstance(requirement_id, str)
                and requirement_id in model_context.requirement_categories
                if basis == ContinuityFindingBasis.MISSING_REQUIREMENT.value
                else isinstance(requirement_id, str)
                and requirement_kinds.get(requirement_id) == "forbidden_shortcut"
            )
            if not is_valid_requirement:
                expected_kind = (
                    "due required"
                    if basis == ContinuityFindingBasis.MISSING_REQUIREMENT.value
                    else "forbidden_shortcut"
                )
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
            expected_references = [
                model_context.world_rule_source_refs[rule_id]
                for rule_id in cited_rule_ids
                if rule_id in model_context.world_rule_source_refs
            ]
            if finding.get("canonical_source_refs") != list(dict.fromkeys(expected_references)):
                raise _StructuredOutputContractError(
                    f"{location}.canonical_source_refs",
                    "application-derived World Rule provenance is incomplete",
                    issue_type="world_rule_source_provenance_invalid",
                )
            if finding.get("violation_kind") not in {
                "explicit_prohibition_breach",
                "required_condition_breach",
            }:
                raise _StructuredOutputContractError(
                    f"{location}.violation_kind",
                    "world-rule blockers require an explicit rule-violation kind",
                )
            if (
                not isinstance(finding.get("rule_conflict_assessment"), str)
                or not cast(str, finding["rule_conflict_assessment"]).strip()
            ):
                raise _StructuredOutputContractError(
                    f"{location}.rule_conflict_assessment",
                    "world-rule blockers must explain the direct logical conflict",
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


def _consolidate_requirement_basis(
    findings: list[object],
    model_context: _ContinuityModelContext | None = None,
) -> list[object]:
    """Keep keyed requirement coverage as the exclusive route for an obligation."""

    def normalized(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        result = " ".join(value.casefold().split()).strip(" .")
        return result or None

    requirement_pairs: set[tuple[str, str]] = set()
    covered_requirement_ids: set[str] = set()
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        requirement_id = finding.get("requirement_id")
        if isinstance(requirement_id, str):
            covered_requirement_ids.add(requirement_id)
        summary = normalized(finding.get("summary"))
        resolution = normalized(finding.get("recommended_resolution"))
        if (
            (
                isinstance(requirement_id, str)
                or finding.get("basis") == ContinuityFindingBasis.MISSING_REQUIREMENT.value
            )
            and summary is not None
            and resolution is not None
        ):
            requirement_pairs.add((summary, resolution))
    if not requirement_pairs and not covered_requirement_ids:
        return findings
    consolidated: list[object] = []
    for finding in findings:
        if isinstance(finding, dict) and finding.get("basis") == (
            ContinuityFindingBasis.CONTRADICTION.value
        ):
            claim_ids = finding.get("canonical_claim_ids")
            claim_requirement_ids = {
                model_context.canonical_claim_requirement_ids[claim_id]
                for claim_id in claim_ids or []
                if model_context is not None
                and isinstance(claim_id, str)
                and claim_id in model_context.canonical_claim_requirement_ids
            }
            if claim_requirement_ids & covered_requirement_ids:
                continue
            pair = (
                normalized(finding.get("summary")),
                normalized(finding.get("recommended_resolution")),
            )
            if pair in requirement_pairs:
                continue
        consolidated.append(finding)
    return consolidated


def _continuity_finding_semantic_key(
    finding: Mapping[str, object],
    model_context: _ContinuityModelContext,
) -> str | None:
    """Return an application-owned identity for one canonical continuity issue."""
    requirement_id = finding.get("requirement_id")
    if isinstance(requirement_id, str):
        return f"requirement:{requirement_id}"
    if finding.get("basis") != ContinuityFindingBasis.CONTRADICTION.value:
        return None
    world_rule_ids = finding.get("world_rule_ids")
    if isinstance(world_rule_ids, list) and world_rule_ids:
        selected = sorted(value for value in world_rule_ids if isinstance(value, str))
        return f"world_rule:{'|'.join(selected)}" if selected else None
    claim_ids = finding.get("canonical_claim_ids")
    selected_claims = (
        [value for value in claim_ids if isinstance(value, str)]
        if isinstance(claim_ids, list)
        else []
    )
    if not selected_claims:
        source_refs = finding.get("canonical_source_refs")
        if isinstance(source_refs, (list, tuple)):
            selected_claims = [
                model_context.canonical_source_claim_ids[source_ref]
                for source_ref in source_refs
                if isinstance(source_ref, str)
                and source_ref in model_context.canonical_source_claim_ids
            ]
    return f"canonical_claim:{'|'.join(sorted(selected_claims))}" if selected_claims else None


def _semantic_continuity_finding_id(semantic_key: str) -> str:
    digest = hashlib.sha256(semantic_key.encode("utf-8")).hexdigest()[:16]
    return f"continuity_issue_{digest}"


def _consolidate_continuity_semantic_duplicates(
    findings: list[object],
    model_context: _ContinuityModelContext,
) -> list[object]:
    """Keep one finding for each requirement, canonical claim, rule, or shortcut."""
    seen: set[str] = set()
    consolidated: list[object] = []
    for finding in findings:
        if not isinstance(finding, dict):
            consolidated.append(finding)
            continue
        key = _continuity_finding_semantic_key(finding, model_context)
        if key is None:
            consolidated.append(finding)
            continue
        if key in seen:
            continue
        seen.add(key)
        consolidated.append(finding)
    return consolidated


def _continuity_due_requirement_kinds(execution: _Execution) -> dict[str, str]:
    required, forbidden = _continuity_requirement_catalogs(execution)
    return {
        cast(str, entry["id"]): cast(str, entry.get("kind", "scene_plan_requirement"))
        for entry in (*required, *forbidden)
    }


def _continuity_due_requirement_categories(execution: _Execution) -> dict[str, str]:
    """Return application-owned categories for every auditable required ID."""
    required, _ = _continuity_requirement_catalogs(execution)
    return {
        cast(str, entry["id"]): cast(str, entry.get("category", ContinuityCategory.FACT.value))
        for entry in required
    }


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
    issues = _continuity_recheck_issues(
        findings,
        prior_report,
        revised_draft_prose=_current_scene_draft_prose(execution),
        historical_blocking_finding_ids=set(
            _continuity_model_context(execution).historical_blocking_finding_ids
        ),
    )
    if issues:
        raise ContinuityRecheckStagnationError(
            "continuity re-check findings violate the exact current-draft analysis contract",
            issues=issues,
        )


def _prior_continuity_report(execution: _Execution) -> dict[str, Any] | None:
    reports = _prior_continuity_reports(execution)
    if not reports:
        return None
    return reports[-1]


def _prior_continuity_reports(execution: _Execution) -> tuple[dict[str, Any], ...]:
    reports: list[dict[str, Any]] = []
    for item in execution.inputs:
        if item.get("artifact_kind") != ArtifactKind.CONTINUITY_REPORT.value:
            continue
        report = item.get("content")
        if not isinstance(report, dict):
            raise ValueError("prior continuity report content is invalid")
        reports.append(report)
    return tuple(reports)


def _invalid_continuity_recheck_finding_ids(
    findings: list[object],
    prior_report: Mapping[str, object],
    *,
    revised_draft_prose: str | None = None,
) -> tuple[str, ...]:
    """Compatibility view over granular v16 continuity re-check diagnostics."""
    return tuple(
        dict.fromkeys(
            issue["location"].split(".", 1)[0]
            for issue in _continuity_recheck_issues(
                findings,
                prior_report,
                revised_draft_prose=revised_draft_prose,
            )
        )
    )


def _continuity_recheck_issues(
    findings: list[object],
    prior_report: Mapping[str, object],
    *,
    revised_draft_prose: str | None = None,
    historical_blocking_finding_ids: set[str] | None = None,
) -> tuple[dict[str, str], ...]:
    """Validate application-owned re-check state and exact current-draft evidence."""
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
    historical_ids = historical_blocking_finding_ids or set(prior_by_id)
    issues: list[dict[str, str]] = []

    def issue(finding_id: str, code: str, message: str) -> None:
        issues.append(
            {
                "location": f"{finding_id}.{code}",
                "type": code,
                "message": message,
            }
        )

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
            if finding_id in historical_ids
            else ContinuityRecheckDisposition.NEWLY_EXPOSED.value
        )
        revised_evidence = finding.get("revised_evidence")
        repair_assessment = finding.get("repair_assessment")
        is_missing_requirement = (
            finding.get("basis") == ContinuityFindingBasis.MISSING_REQUIREMENT.value
        )
        if finding.get("recheck_disposition") != expected_disposition:
            issue(
                finding_id,
                "invalid_recheck_disposition",
                f"expected {expected_disposition} for this finding ID",
            )
            continue
        if not isinstance(repair_assessment, str) or not repair_assessment.strip():
            issue(
                finding_id,
                "invalid_recheck_disposition",
                "a re-check blocker requires a non-empty repair_assessment",
            )
            continue
        if is_missing_requirement:
            if (
                revised_evidence not in (None, [])
                or not isinstance(finding.get("coverage_assessment"), str)
                or not cast(str, finding["coverage_assessment"]).strip()
            ):
                issue(
                    finding_id,
                    "missing_requirement_used_as_contradiction",
                    "a missing requirement needs coverage assessment and cannot cite evidence",
                )
            continue
        if (
            not isinstance(revised_evidence, list)
            or not revised_evidence
            or any(not isinstance(item, str) or not item.strip() for item in revised_evidence)
        ):
            issue(
                finding_id,
                "evidence_not_in_current_draft",
                "a contradiction or forbidden-shortcut re-check requires exact revised evidence",
            )
            continue
        exact_evidence = cast(list[str], revised_evidence)
        if revised_draft_prose is not None and any(
            excerpt not in revised_draft_prose for excerpt in exact_evidence
        ):
            issue(
                finding_id,
                "evidence_not_in_current_draft",
                "one or more revised evidence excerpts are absent from the current draft",
            )
            continue

        # A repeated assessment after changed evidence is useful telemetry, but it is not
        # a structured-output contract violation. Exact evidence remains mandatory above.
    return tuple(issues)


def _continuity_recheck_observations(
    report: ContinuityReport,
    execution: _Execution,
) -> tuple[dict[str, str], ...]:
    """Record content-free advisory telemetry without rejecting a valid re-check."""
    prior_report = _prior_continuity_report(execution)
    if prior_report is None:
        return ()
    prior_findings = prior_report.get("findings")
    if not isinstance(prior_findings, list):
        return ()
    prior_by_id = {
        finding["id"]: finding
        for finding in prior_findings
        if isinstance(finding, dict) and isinstance(finding.get("id"), str)
    }
    historical_ids = set(_continuity_model_context(execution).historical_blocking_finding_ids)
    observations: list[dict[str, str]] = []
    for finding in report.findings:
        prior = prior_by_id.get(finding.id)
        if (
            prior is None
            and finding.id in historical_ids
            and finding.recheck_disposition is ContinuityRecheckDisposition.STILL_BLOCKING
        ):
            observations.append(
                {
                    "finding_id": finding.id,
                    "type": "historical_blocker_recurred",
                    "disposition": "blocking",
                }
            )
            continue
        if prior is None or not finding.repair_assessment:
            continue
        prior_evidence = prior.get("revised_evidence") or prior.get("evidence")
        current_evidence = list(finding.revised_evidence or finding.evidence)
        prior_assessment = prior.get("repair_assessment")
        if (
            isinstance(prior_evidence, list)
            and current_evidence != prior_evidence
            and isinstance(prior_assessment, str)
            and finding.repair_assessment.strip() == prior_assessment.strip()
        ):
            observations.append(
                {
                    "finding_id": finding.id,
                    "type": "copied_assessment_after_changed_evidence",
                    "disposition": "advisory",
                }
            )
    return tuple(observations)


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


def _resolve_continuity_evidence_refs(
    references: list[str],
    model_context: _ContinuityModelContext,
    *,
    location: str,
    allow_empty: bool = False,
    issue_type: str | None = None,
) -> list[str]:
    """Resolve bounded evidence handles into immutable current-draft excerpts."""
    if not references and not allow_empty:
        raise _StructuredOutputContractError(location, "evidence references must not be empty")
    content = model_context.candidate_draft.get("content")
    catalog = content.get("evidence_catalog") if isinstance(content, dict) else None
    by_reference = {
        entry["evidence_ref"]: entry["exact_excerpt"]
        for entry in catalog or []
        if isinstance(entry, dict)
        and isinstance(entry.get("evidence_ref"), str)
        and isinstance(entry.get("exact_excerpt"), str)
    }
    normalized = _normalize_continuity_evidence_refs(
        references,
        model_context,
        location=location,
        issue_type=issue_type,
    )
    return list(dict.fromkeys(by_reference[reference] for reference in normalized))


def _normalize_continuity_evidence_refs(
    references: list[str],
    model_context: _ContinuityModelContext,
    *,
    location: str,
    issue_type: str | None,
) -> list[str]:
    """Accept canonical handles, unambiguous padding aliases, or exact excerpts."""
    content = model_context.candidate_draft.get("content")
    catalog = content.get("evidence_catalog") if isinstance(content, dict) else None
    by_reference = {
        entry["evidence_ref"]: entry["exact_excerpt"]
        for entry in catalog or []
        if isinstance(entry, dict)
        and isinstance(entry.get("evidence_ref"), str)
        and isinstance(entry.get("exact_excerpt"), str)
    }
    by_excerpt: dict[str, list[str]] = {}
    for reference, excerpt in by_reference.items():
        by_excerpt.setdefault(excerpt, []).append(reference)
    normalized: list[str] = []
    invalid: list[str] = []
    for reference in references:
        if reference in by_reference:
            normalized.append(reference)
            continue
        handle_match = re.fullmatch(r"draft_evidence_(\d{1,4})", reference)
        if handle_match is not None:
            canonical_reference = f"draft_evidence_{int(handle_match.group(1)):04d}"
            if canonical_reference in by_reference:
                normalized.append(canonical_reference)
                continue
        excerpt_matches = by_excerpt.get(reference, [])
        if len(excerpt_matches) == 1:
            normalized.append(excerpt_matches[0])
            continue
        invalid.append(reference)
    if invalid:
        safe_invalid = [
            active_secret_guard().redact_text(value).replace("\n", " ")[:120]
            for value in invalid[:5]
        ]
        raise _StructuredOutputContractError(
            location,
            "evidence references must be selected from "
            "candidate_draft.content.evidence_catalog; "
            f"rejected_values={safe_invalid}",
            issue_type=issue_type,
        )
    return list(dict.fromkeys(normalized))


def _materialize_continuity_evidence(
    finding: object,
    model_context: _ContinuityModelContext,
) -> object:
    """Resolve model-selected evidence handles into exact canonical artifact excerpts."""
    if not isinstance(finding, dict):
        return finding
    finding = _flatten_continuity_model_finding(finding)
    finding = _materialize_non_world_source_refs(finding, model_context)
    finding = _materialize_world_rule_source_refs(finding, model_context)
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
    excerpts = _resolve_continuity_evidence_refs(
        cast(list[str], references),
        model_context,
        location=ref_field,
    )
    materialized["evidence"] = excerpts
    if (
        basis == ContinuityFindingBasis.CONTRADICTION.value
        and materialized.get("category") != ContinuityCategory.WORLD_RULE.value
    ):
        category = materialized.get("category")
        materialized["draft_assertion"] = excerpts[0]
        materialized["conflict_kind"] = (
            _NON_WORLD_CONFLICT_KIND_BY_CATEGORY.get(category)
            if isinstance(category, str)
            else None
        )
    if model_context.previous_continuity_report is not None:
        materialized["revised_evidence"] = excerpts
    return materialized


def _materialize_non_world_source_refs(
    finding: dict[str, object],
    model_context: _ContinuityModelContext,
) -> dict[str, object]:
    """Derive non-World-Rule provenance from model-selected typed canonical claims."""
    claim_ids = finding.get("canonical_claim_ids")
    if finding.get("basis") != ContinuityFindingBasis.CONTRADICTION.value or not isinstance(
        claim_ids, list
    ):
        return finding
    if len(claim_ids) != 1 or any(
        not isinstance(claim_id, str) or claim_id not in model_context.canonical_claim_source_refs
        for claim_id in claim_ids
    ):
        raise _StructuredOutputContractError(
            "canonical_claim_ids",
            "non-world contradictions require exactly one typed claim with deterministic "
            "provenance",
            issue_type="non_world_claim_provenance_invalid",
        )
    claim_id = cast(str, claim_ids[0])
    categories = model_context.canonical_claim_categories[claim_id]
    if not categories or categories[0] == ContinuityCategory.WORLD_RULE.value:
        raise _StructuredOutputContractError(
            "canonical_claim_ids",
            "non-world contradiction selector does not resolve to non-world canon",
            issue_type="non_world_claim_provenance_invalid",
        )
    materialized = dict(finding)
    materialized["category"] = categories[0]
    materialized["canonical_source_refs"] = [model_context.canonical_claim_source_refs[claim_id]]
    for field_name in (
        "related_character_ids",
        "related_location_ids",
        "related_beat_ids",
        "related_scene_ids",
    ):
        materialized[field_name] = []
    return materialized


def _materialize_world_rule_source_refs(
    finding: dict[str, object],
    model_context: _ContinuityModelContext,
) -> dict[str, object]:
    """Derive exact World Rule provenance from model-selected canonical rule IDs."""
    if not (
        finding.get("basis") == ContinuityFindingBasis.CONTRADICTION.value
        and finding.get("category") == ContinuityCategory.WORLD_RULE.value
    ):
        return finding
    rule_ids = finding.get("world_rule_ids")
    if (
        not isinstance(rule_ids, list)
        or not rule_ids
        or any(
            not isinstance(rule_id, str) or rule_id not in model_context.world_rule_source_refs
            for rule_id in rule_ids
        )
    ):
        raise _StructuredOutputContractError(
            "world_rule_ids",
            "World Rule contradictions require IDs with deterministic canonical provenance",
            issue_type="invalid_world_rule_id",
        )
    materialized = dict(finding)
    materialized["category"] = ContinuityCategory.WORLD_RULE.value
    materialized["canonical_source_refs"] = list(
        dict.fromkeys(model_context.world_rule_source_refs[rule_id] for rule_id in rule_ids)
    )
    for field_name in (
        "related_character_ids",
        "related_location_ids",
        "related_beat_ids",
        "related_scene_ids",
    ):
        materialized[field_name] = []
    return materialized


def _flatten_continuity_model_finding(finding: Mapping[str, object]) -> dict[str, object]:
    """Flatten compact model-only basis/category detail objects for canonical validation."""
    basis_details = finding.get("basis_details")
    category_details = finding.get("category_details")
    if basis_details is None:
        return dict(finding)
    if not isinstance(basis_details, dict):
        raise _StructuredOutputContractError(
            "findings",
            "blocking findings require a basis_details object",
        )
    basis_details = dict(basis_details)
    nested_category = basis_details.pop("category_details", None)
    if category_details is not None and nested_category is not None:
        raise _StructuredOutputContractError(
            "findings",
            "blocking finding supplied category_details twice",
        )
    category_details = nested_category if nested_category is not None else category_details
    if category_details is not None and not isinstance(category_details, dict):
        raise _StructuredOutputContractError("findings", "category_details must be an object")
    root = {
        key: value for key, value in finding.items() if key not in _CONTINUITY_MODEL_DETAIL_FIELDS
    }
    category_fields = set(category_details) if isinstance(category_details, dict) else set()
    duplicate_fields = (set(root) & set(basis_details)) | (set(root) & category_fields)
    duplicate_fields |= set(basis_details) & category_fields
    if duplicate_fields:
        raise _StructuredOutputContractError(
            "findings",
            f"compact continuity details duplicate fields: {sorted(duplicate_fields)}",
        )
    flattened = {**root, **basis_details}
    basis = flattened.get("basis")
    if basis == ContinuityFindingBasis.FORBIDDEN_SHORTCUT_VIOLATION.value:
        flattened["category"] = ContinuityCategory.CONSTRAINT.value
    elif isinstance(category_details, dict):
        flattened.update(category_details)
        if basis == ContinuityFindingBasis.CONTRADICTION.value:
            flattened["category"] = ContinuityCategory.WORLD_RULE.value
    elif basis == ContinuityFindingBasis.CONTRADICTION.value and isinstance(
        flattened.get("canonical_claim_ids"), list
    ):
        pass
    else:
        raise _StructuredOutputContractError(
            "findings", "contradiction finding does not select canonical claim or World Rule"
        )
    return flattened


def _materialize_continuity_identity(
    finding: object,
    model_context: _ContinuityModelContext,
    *,
    index: int,
    revision_number: int = 0,
) -> object:
    """Derive canonical finding identity and re-check disposition in application code."""
    if not isinstance(finding, dict):
        return finding
    materialized = {
        key: value for key, value in finding.items() if key not in {"id", "prior_finding_id"}
    }
    severity = finding.get("severity")
    is_blocking = severity in {"error", "blocking"}
    semantic_key = _continuity_finding_semantic_key(finding, model_context)
    if model_context.previous_continuity_report is None:
        materialized["id"] = (
            _semantic_continuity_finding_id(semantic_key)
            if semantic_key is not None
            else f"continuity_finding_{index + 1:03d}"
        )
        return materialized
    prior_id = finding.get("prior_finding_id")
    if is_blocking and isinstance(prior_id, str):
        if prior_id not in model_context.prior_model_finding_ids:
            raise _StructuredOutputContractError(
                f"findings.{index}.prior_finding_id",
                "prior_finding_id must reference an exact prior blocking finding",
            )
        materialized["id"] = prior_id
        materialized["recheck_disposition"] = ContinuityRecheckDisposition.STILL_BLOCKING.value
    else:
        prefix = "continuity_new" if is_blocking else "continuity_advisory"
        historical_id = (
            model_context.historical_semantic_finding_ids.get(semantic_key)
            if semantic_key is not None
            else None
        )
        materialized["id"] = historical_id or (
            _semantic_continuity_finding_id(semantic_key)
            if semantic_key is not None
            else f"{prefix}_r{revision_number:02d}_{index + 1:03d}"
        )
        if is_blocking:
            materialized["recheck_disposition"] = (
                ContinuityRecheckDisposition.STILL_BLOCKING.value
                if historical_id is not None
                else ContinuityRecheckDisposition.NEWLY_EXPOSED.value
            )
    return materialized


def _strip_continuity_certification_fields(finding: object) -> object:
    """Remove model-only certification fields before canonical artifact validation."""
    if not isinstance(finding, dict):
        return finding
    return {
        key: value
        for key, value in finding.items()
        if key not in _CONTINUITY_MODEL_CERTIFICATION_FIELDS
    }


def _validate_unique_continuity_finding_ids(findings: list[object]) -> None:
    ids = [
        finding.get("id")
        for finding in findings
        if isinstance(finding, dict) and isinstance(finding.get("id"), str)
    ]
    if len(ids) != len(set(ids)):
        raise _StructuredOutputContractError(
            "findings.prior_finding_id",
            "each prior blocking finding may be referenced at most once",
            issue_type="duplicate_prior_finding_reference",
        )


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
        historical_resolution = (
            prior_resolutions.get(finding_id)
            if isinstance(finding_id, str) and prior_resolutions is not None
            else None
        )
        if historical_resolution is not None and (
            finding.get("recheck_disposition") == ContinuityRecheckDisposition.STILL_BLOCKING.value
            or not isinstance(resolution, str)
            or not resolution.strip()
        ):
            materialized["recommended_resolution"] = historical_resolution
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
            *task.continuity_history,
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


def _continuity_recheck_input_references(
    session: Session,
    references: tuple[ArtifactReference, ...],
    inputs: tuple[dict[str, Any], ...],
    *,
    project_id: UUID,
) -> tuple[ArtifactReference, ...]:
    """Attach the prior candidate draft named by a re-check report to exact invocation lineage."""
    reports = tuple(
        item for item in inputs if item.get("artifact_kind") == ArtifactKind.CONTINUITY_REPORT.value
    )
    if not reports:
        return references
    resolved = references
    for report in reports:
        content = report.get("content")
        prior_version_value = content.get("scene_version_id") if isinstance(content, dict) else None
        try:
            prior_version_id = UUID(str(prior_version_value))
        except (TypeError, ValueError) as error:
            raise SceneProductionError(
                "prior Continuity Report has no valid candidate-draft lineage"
            ) from error
        if any(reference.version_id == prior_version_id for reference in resolved):
            continue
        version = session.scalar(
            select(ArtifactVersion)
            .where(ArtifactVersion.id == prior_version_id)
            .options(joinedload(ArtifactVersion.artifact))
        )
        if (
            version is None
            or version.artifact.project_id != project_id
            or version.artifact.artifact_type != ArtifactKind.SCENE_DRAFT.value
        ):
            raise SceneProductionError(
                "prior Continuity Report candidate-draft lineage cannot be resolved"
            )
        resolved = _unique_references((*resolved, _reference(version)))
    return resolved


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


def _request_composition_metrics(
    messages: tuple[ModelMessage, ...],
    *,
    gateway_schema: Mapping[str, Any] | None,
) -> dict[str, object]:
    """Record content-free size diagnostics for each provider-input contribution."""
    user_message = next(
        (message.content for message in messages if message.role is MessageRole.USER),
        None,
    )
    if user_message is None:
        raise SceneProductionError("production request has no user message")
    user_payload = json.loads(user_message)
    if not isinstance(user_payload, dict):
        raise SceneProductionError("production user message must contain a JSON object")

    artifact_keys = {
        "accepted_prior_drafts",
        "candidate_draft",
        "contradiction_claim_catalog",
        "input_artifacts",
        "previous_continuity_report",
        "world_rule_catalog",
    }
    retry_keys = {"schema_repair", "retry_context"}
    inline_schema = user_payload.pop("output_schema", None)
    artifact_context = {
        key: user_payload.pop(key) for key in tuple(user_payload) if key in artifact_keys
    }
    retry_context = {key: user_payload.pop(key) for key in tuple(user_payload) if key in retry_keys}
    system_instructions = "\n".join(
        message.content for message in messages if message.role is MessageRole.SYSTEM
    )
    components = {
        "system_instructions": _content_metric(system_instructions),
        "artifact_context": _content_metric(artifact_context),
        "control_context": _content_metric(user_payload),
        "retry_repair_context": _content_metric(retry_context),
        "inline_schema": _content_metric(inline_schema),
        "gateway_schema": _content_metric(gateway_schema),
        "serialized_messages": _content_metric(
            [{"role": message.role.value, "content": message.content} for message in messages]
        ),
    }
    estimated_provider_bytes = sum(
        cast(int, component["utf8_bytes"])
        for name, component in components.items()
        if name
        in {
            "system_instructions",
            "artifact_context",
            "control_context",
            "retry_repair_context",
            "inline_schema",
            "gateway_schema",
        }
    )
    return {
        "schema_version": "1",
        "token_estimate_method": "ceil(utf8_bytes/4); diagnostic only",
        "estimated_provider_input_tokens": ceil(estimated_provider_bytes / 4),
        "components": components,
    }


def _content_metric(value: object) -> dict[str, object]:
    serialized = (
        ""
        if value is None
        else value
        if isinstance(value, str)
        else json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    )
    encoded = serialized.encode("utf-8")
    return {
        "characters": len(serialized),
        "utf8_bytes": len(encoded),
        "estimated_tokens": ceil(len(encoded) / 4),
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }


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
