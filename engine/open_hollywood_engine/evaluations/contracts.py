"""Typed, provider-neutral contracts for repeatable story benchmarks."""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Annotated, Any, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from open_hollywood_engine.models import (
    ModelDeployment,
    ModelProfileConfiguration,
    ModelProfileMode,
    ModelSelection,
)

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

BENCHMARK_SCHEMA_VERSION: Literal["1"] = "1"
HUMAN_REVIEW_SCHEMA_VERSION: Literal["2"] = "2"
CANONICAL_RUBRIC_NAME = "open-hollywood-story-quality"
CANONICAL_RUBRIC_VERSION = "1"


class EvaluationModel(BaseModel):
    """Strict immutable base for persisted benchmark values."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class BenchmarkCategory(StrEnum):
    """Capability family stressed by a corpus prompt."""

    SPARSE_PREMISE = "sparse_premise"
    CHARACTER_DIALOGUE = "character_dialogue"
    STRUCTURAL = "structural"
    CONSTRAINT = "constraint"


class FictionMaturity(StrEnum):
    """Product-level maturity mode attached to a benchmark premise."""

    STANDARD = "standard_fiction"
    MATURE = "mature_fiction"


class EvaluationDimension(StrEnum):
    """Canonical human-facing story-quality dimensions."""

    CAUSAL_COHERENCE = "causal_coherence_and_structure"
    CHARACTER_DEPTH = "character_depth_and_consistency"
    DIALOGUE = "dialogue"
    ORIGINALITY = "originality_and_specificity"
    VOICE = "voice_and_prose_quality"
    EMOTIONAL_IMPACT = "emotional_and_thematic_impact"
    PACING = "pacing_and_tension"
    CONTINUITY = "continuity_and_constraint_adherence"


EVALUATION_WEIGHTS: dict[EvaluationDimension, int] = {
    EvaluationDimension.CAUSAL_COHERENCE: 20,
    EvaluationDimension.CHARACTER_DEPTH: 15,
    EvaluationDimension.DIALOGUE: 15,
    EvaluationDimension.ORIGINALITY: 15,
    EvaluationDimension.VOICE: 10,
    EvaluationDimension.EMOTIONAL_IMPACT: 10,
    EvaluationDimension.PACING: 10,
    EvaluationDimension.CONTINUITY: 5,
}


class HardGate(StrEnum):
    """Failures that invalidate a story regardless of its rubric average."""

    COMPLETE = "complete"
    CENTRAL_FACTS_CONSISTENT = "central_facts_consistent"
    MANDATORY_REQUIREMENTS_PRESENT = "mandatory_requirements_present"
    NO_PLACEHOLDERS_OR_MODEL_COMMENTARY = "no_placeholders_or_model_commentary"
    TARGET_FORMAT_VALID = "target_format_valid"
    ENDING_NOT_TRUNCATED = "ending_not_truncated"
    NO_CRITIC_NOTES_IN_PROSE = "no_critic_notes_in_prose"


class TargetWordCount(EvaluationModel):
    """Advisory complete-story length target."""

    minimum: int = Field(ge=1)
    maximum: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.minimum > self.maximum:
            raise ValueError("minimum word count must not exceed maximum")
        return self


class WordCountStatus(StrEnum):
    """Observed position relative to an advisory word-count target."""

    UNDER_TARGET = "under_target"
    WITHIN_TARGET = "within_target"
    OVER_TARGET = "over_target"


class WordCountAdherence(EvaluationModel):
    """Non-gating measurement of one output against its advisory target."""

    policy: Literal["advisory"] = "advisory"
    target: TargetWordCount
    actual: int = Field(ge=1)
    status: WordCountStatus
    deviation_words: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_measurement(self) -> Self:
        expected_status, expected_deviation = self._expected()
        if self.status is not expected_status or self.deviation_words != expected_deviation:
            raise ValueError("word-count adherence does not match its target and actual count")
        return self

    @classmethod
    def measure(cls, *, target: TargetWordCount, actual: int) -> WordCountAdherence:
        """Measure an actual count without turning the preference into a hard gate."""
        if actual < target.minimum:
            status = WordCountStatus.UNDER_TARGET
            deviation = target.minimum - actual
        elif actual > target.maximum:
            status = WordCountStatus.OVER_TARGET
            deviation = actual - target.maximum
        else:
            status = WordCountStatus.WITHIN_TARGET
            deviation = 0
        return cls(
            target=target,
            actual=actual,
            status=status,
            deviation_words=deviation,
        )

    def _expected(self) -> tuple[WordCountStatus, int]:
        if self.actual < self.target.minimum:
            return WordCountStatus.UNDER_TARGET, self.target.minimum - self.actual
        if self.actual > self.target.maximum:
            return WordCountStatus.OVER_TARGET, self.actual - self.target.maximum
        return WordCountStatus.WITHIN_TARGET, 0


class BenchmarkPrompt(EvaluationModel):
    """One immutable prompt version and its evaluation metadata."""

    prompt_id: NonEmptyText
    version: NonEmptyText
    category: BenchmarkCategory
    prompt: NonEmptyText
    why_it_exists: NonEmptyText
    genres: tuple[NonEmptyText, ...] = Field(min_length=1)
    intended_maturity: FictionMaturity
    target_word_count: TargetWordCount
    required_elements: tuple[NonEmptyText, ...] = Field(min_length=1)
    forbidden_shortcuts: tuple[NonEmptyText, ...] = Field(min_length=1)
    likely_failure_modes: tuple[NonEmptyText, ...] = Field(min_length=1)
    stressed_dimensions: tuple[EvaluationDimension, ...] = Field(min_length=1)
    factual_research_allowed: bool
    random_seed: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_metadata(self) -> Self:
        if len(set(self.stressed_dimensions)) != len(self.stressed_dimensions):
            raise ValueError("stressed_dimensions must be unique")
        return self


class BenchmarkCorpus(EvaluationModel):
    """A frozen, versioned prompt collection."""

    schema_version: str
    corpus_id: NonEmptyText
    corpus_version: NonEmptyText
    prompts: tuple[BenchmarkPrompt, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_corpus(self) -> Self:
        if self.schema_version != BENCHMARK_SCHEMA_VERSION:
            raise ValueError(f"unsupported benchmark schema version {self.schema_version!r}")
        prompt_versions = {(prompt.prompt_id, prompt.version) for prompt in self.prompts}
        if len(prompt_versions) != len(self.prompts):
            raise ValueError("prompt ID/version pairs must be unique")
        seeds = [prompt.random_seed for prompt in self.prompts]
        if len(set(seeds)) != len(seeds):
            raise ValueError("benchmark random seeds must be unique")
        return self

    @property
    def content_sha256(self) -> str:
        """Return the canonical digest pinned by every campaign plan."""
        return canonical_sha256(self.model_dump(mode="json"))


class BenchmarkSystem(StrEnum):
    """Generation strategy represented by one benchmark case."""

    SINGLE_MODEL_BASELINE = "single_model_baseline"
    AGENTIC = "agentic"


class BenchmarkModelTarget(EvaluationModel):
    """Exact model used by a direct single-model baseline."""

    provider: NonEmptyText
    model_identifier: NonEmptyText
    deployment: ModelDeployment

    @classmethod
    def from_selection(cls, selection: ModelSelection) -> Self:
        return cls(
            provider=selection.provider,
            model_identifier=selection.model_identifier,
            deployment=selection.deployment,
        )

    def to_selection(self) -> ModelSelection:
        return ModelSelection(
            provider=self.provider,
            model_identifier=self.model_identifier,
            deployment=self.deployment,
        )


class BenchmarkProfileSnapshot(EvaluationModel):
    """Exact secret-free model profile frozen into a campaign."""

    profile_id: UUID
    mode: ModelProfileMode
    configuration: dict[str, Any]
    configuration_sha256: Sha256

    @model_validator(mode="after")
    def validate_snapshot(self) -> Self:
        configuration = ModelProfileConfiguration.from_data(self.configuration)
        if configuration.mode is not self.mode:
            raise ValueError("profile mode does not match configuration")
        if not configuration.is_complete:
            raise ValueError("benchmark profiles must be complete")
        if canonical_sha256(self.configuration) != self.configuration_sha256:
            raise ValueError("profile configuration digest does not match")
        return self

    @classmethod
    def from_configuration(
        cls,
        *,
        profile_id: UUID,
        configuration: ModelProfileConfiguration,
    ) -> Self:
        data = configuration.to_data()
        return cls(
            profile_id=profile_id,
            mode=configuration.mode,
            configuration=data,
            configuration_sha256=canonical_sha256(data),
        )


class BenchmarkCase(EvaluationModel):
    """One independently executable prompt/strategy combination."""

    case_id: UUID
    prompt_id: NonEmptyText
    prompt_version: NonEmptyText
    system: BenchmarkSystem
    run_seed: int = Field(ge=0)
    baseline_model: BenchmarkModelTarget | None = None
    profile: BenchmarkProfileSnapshot | None = None

    @model_validator(mode="after")
    def validate_target(self) -> Self:
        if self.system is BenchmarkSystem.SINGLE_MODEL_BASELINE:
            if self.baseline_model is None or self.profile is not None:
                raise ValueError("a baseline case requires only baseline_model")
        elif self.profile is None or self.baseline_model is not None:
            raise ValueError("an agentic case requires only a profile snapshot")
        return self

    @property
    def target_key(self) -> str:
        """Return the stable comparison key without exposing model credentials."""
        if self.system is BenchmarkSystem.SINGLE_MODEL_BASELINE:
            return "baseline"
        if self.profile is None:
            raise RuntimeError("agentic benchmark case has no profile")
        return self.profile.mode.value


class BenchmarkPlan(EvaluationModel):
    """Fully expanded, reproducible campaign input."""

    schema_version: str
    campaign_id: UUID
    corpus_id: NonEmptyText
    corpus_version: NonEmptyText
    corpus_sha256: Sha256
    workflow_versions: dict[NonEmptyText, NonEmptyText]
    cases: tuple[BenchmarkCase, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_plan(self) -> Self:
        if self.schema_version != BENCHMARK_SCHEMA_VERSION:
            raise ValueError(f"unsupported benchmark schema version {self.schema_version!r}")
        case_ids = [case.case_id for case in self.cases]
        if len(set(case_ids)) != len(case_ids):
            raise ValueError("benchmark case IDs must be unique")
        return self

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(self.model_dump(mode="json"))


class BenchmarkCaseStatus(StrEnum):
    """Terminal harness disposition for one planned case."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"


class BenchmarkFailureAttempt(EvaluationModel):
    """One safe persisted model-attempt failure in terminal execution order."""

    invocation_id: UUID
    workflow_node: NonEmptyText | None = None
    specialist_role: NonEmptyText
    operation: NonEmptyText | None = None
    schema_variant: NonEmptyText | None = None
    attempt_number: int = Field(ge=1)
    error_code: NonEmptyText
    error_message: NonEmptyText
    provider_finish_reason: NonEmptyText | None = None


class BenchmarkOutput(EvaluationModel):
    """Complete candidate document plus exact durable lineage."""

    title: NonEmptyText
    content: NonEmptyText
    content_sha256: Sha256
    word_count: int = Field(ge=1)
    word_count_adherence: WordCountAdherence | None = None
    workflow_run_id: UUID
    artifact_version_ids: tuple[UUID, ...] = Field(min_length=1)
    invocation_ids: tuple[UUID, ...] = Field(min_length=1)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    latency_ms: int = Field(ge=0)
    estimated_cost_usd: Annotated[str, StringConstraints(pattern=r"^\d+(\.\d+)?$")]
    hard_gates: dict[HardGate, bool | None]

    @model_validator(mode="after")
    def validate_output(self) -> Self:
        if hashlib.sha256(self.content.encode("utf-8")).hexdigest() != self.content_sha256:
            raise ValueError("benchmark output content digest does not match")
        if len(self.content.split()) != self.word_count:
            raise ValueError("benchmark output word count does not match its content")
        if (
            self.word_count_adherence is not None
            and self.word_count_adherence.actual != self.word_count
        ):
            raise ValueError("benchmark word-count adherence does not match its output")
        if len(set(self.artifact_version_ids)) != len(self.artifact_version_ids):
            raise ValueError("benchmark artifact version IDs must be unique")
        if len(set(self.invocation_ids)) != len(self.invocation_ids):
            raise ValueError("benchmark invocation IDs must be unique")
        if set(self.hard_gates) != set(HardGate):
            raise ValueError("benchmark output must report every hard gate")
        return self


class BenchmarkCaseResult(EvaluationModel):
    """One terminal result safe to resume and aggregate."""

    case_id: UUID
    status: BenchmarkCaseStatus
    output: BenchmarkOutput | None = None
    error_code: NonEmptyText | None = None
    error_message: NonEmptyText | None = None
    failure_history: tuple[BenchmarkFailureAttempt, ...] = ()

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.status is BenchmarkCaseStatus.SUCCEEDED:
            if (
                self.output is None
                or self.error_code is not None
                or self.error_message is not None
                or self.failure_history
            ):
                raise ValueError("successful cases require only an output")
        elif self.output is not None or self.error_code is None:
            raise ValueError("failed cases require an error code and no output")
        return self


class BenchmarkRunReport(EvaluationModel):
    """Resumable terminal and partial results pinned to one exact plan."""

    schema_version: Literal["1"]
    campaign_id: UUID
    plan_sha256: Sha256
    results: tuple[BenchmarkCaseResult, ...]

    @model_validator(mode="after")
    def validate_report(self) -> Self:
        if self.schema_version != BENCHMARK_SCHEMA_VERSION:
            raise ValueError(f"unsupported benchmark schema version {self.schema_version!r}")
        result_ids = [result.case_id for result in self.results]
        if len(set(result_ids)) != len(result_ids):
            raise ValueError("benchmark report case IDs must be unique")
        return self


class CanonicalStoryScore(EvaluationModel):
    """One reviewer's canonical rubric and hard-gate assessment."""

    rubric_name: str = CANONICAL_RUBRIC_NAME
    rubric_version: str = CANONICAL_RUBRIC_VERSION
    dimension_scores: dict[EvaluationDimension, int]
    hard_gates: dict[HardGate, bool]
    notes: NonEmptyText | None = None

    @model_validator(mode="after")
    def validate_score(self) -> Self:
        if self.rubric_name != CANONICAL_RUBRIC_NAME:
            raise ValueError("unsupported canonical rubric name")
        if self.rubric_version != CANONICAL_RUBRIC_VERSION:
            raise ValueError("unsupported canonical rubric version")
        if set(self.dimension_scores) != set(EvaluationDimension):
            raise ValueError("a score is required for every evaluation dimension")
        if any(not 1 <= score <= 5 for score in self.dimension_scores.values()):
            raise ValueError("dimension scores must be between 1 and 5")
        if set(self.hard_gates) != set(HardGate):
            raise ValueError("a result is required for every hard gate")
        return self

    @property
    def weighted_score(self) -> float:
        """Return the canonical 1–5 weighted human score."""
        return (
            sum(
                self.dimension_scores[dimension] * weight
                for dimension, weight in EVALUATION_WEIGHTS.items()
            )
            / 100
        )

    @property
    def passes_hard_gates(self) -> bool:
        return all(self.hard_gates.values())


class BlindDocument(EvaluationModel):
    """One sanitized candidate shown to a human reviewer."""

    label: Literal["A", "B"]
    title: NonEmptyText
    content: NonEmptyText
    content_sha256: Sha256


class BlindComparison(EvaluationModel):
    """Public two-candidate packet with no provider or profile provenance."""

    comparison_id: NonEmptyText
    prompt_id: NonEmptyText
    prompt_version: NonEmptyText
    prompt: NonEmptyText
    candidate_a: BlindDocument
    candidate_b: BlindDocument


class BlindPublicBundle(EvaluationModel):
    """Reviewer-safe comparison set."""

    schema_version: Literal["1"]
    campaign_id: UUID
    comparisons: tuple[BlindComparison, ...]


class BlindAnswer(EvaluationModel):
    """Private mapping from public aliases to benchmark cases."""

    comparison_id: NonEmptyText
    candidate_a_case_id: UUID
    candidate_b_case_id: UUID


class BlindAnswerKey(EvaluationModel):
    """Private key stored separately from reviewer packets."""

    schema_version: Literal["1"]
    campaign_id: UUID
    public_bundle_sha256: Sha256
    answers: tuple[BlindAnswer, ...]


class BlindPreference(StrEnum):
    """Human preference expressed without knowledge of system identity."""

    A = "a"
    B = "b"
    TIE = "tie"


class HumanComparisonReview(EvaluationModel):
    """One blind comparison review with a full score for each candidate."""

    comparison_id: NonEmptyText
    reviewer_id: NonEmptyText
    preference: BlindPreference
    candidate_a_score: CanonicalStoryScore
    candidate_b_score: CanonicalStoryScore
    notes: NonEmptyText | None = None


class HumanReviewBundle(EvaluationModel):
    """Validated reviewer submissions for one exact benchmark campaign."""

    schema_version: Literal["2"]
    campaign_id: UUID
    public_bundle_sha256: Sha256
    reviews: tuple[HumanComparisonReview, ...]

    @model_validator(mode="after")
    def validate_reviews(self) -> Self:
        review_keys = {(review.comparison_id, review.reviewer_id) for review in self.reviews}
        if len(review_keys) != len(self.reviews):
            raise ValueError("a reviewer may score each comparison only once")
        return self


class BenchmarkTargetMetrics(EvaluationModel):
    """Technical completion and cost metrics for one benchmark target."""

    target: NonEmptyText
    planned_cases: int = Field(ge=0)
    succeeded_cases: int = Field(ge=0)
    technical_success_rate: float = Field(ge=0, le=1)
    median_cost_usd: float | None = Field(default=None, ge=0)


class BenchmarkSuccessCriteria(EvaluationModel):
    """Formal v0.1 thresholds; None means insufficient human data."""

    technical_completion_at_least_95_percent: bool
    severe_continuity_free_at_least_80_percent: bool | None
    weighted_human_score_at_least_3_5: bool | None
    no_dimension_average_below_2_5: bool | None
    agentic_preference_at_least_60_percent: bool | None
    median_cloud_cost_within_budget: bool | None


class BenchmarkSummary(EvaluationModel):
    """Aggregated campaign evidence without candidate story bodies."""

    schema_version: Literal["1"]
    campaign_id: UUID
    target_metrics: tuple[BenchmarkTargetMetrics, ...]
    human_review_count: int = Field(ge=0)
    mean_agentic_weighted_score: float | None = Field(default=None, ge=1, le=5)
    lowest_agentic_dimension_mean: float | None = Field(default=None, ge=1, le=5)
    severe_continuity_free_rate: float | None = Field(default=None, ge=0, le=1)
    agentic_baseline_preference_rate: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    criteria: BenchmarkSuccessCriteria


def canonical_sha256(value: object) -> str:
    """Hash one JSON-compatible value using the repository's stable encoding."""
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
