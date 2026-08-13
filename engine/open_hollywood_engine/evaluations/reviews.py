"""Reviewer-friendly CSV forms bound to exact blind comparison packets."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from io import StringIO

from open_hollywood_engine.evaluations.contracts import (
    CANONICAL_RUBRIC_NAME,
    CANONICAL_RUBRIC_VERSION,
    EVALUATION_WEIGHTS,
    HUMAN_REVIEW_SCHEMA_VERSION,
    BlindComparison,
    BlindPreference,
    BlindPublicBundle,
    CanonicalStoryScore,
    EvaluationDimension,
    HardGate,
    HumanComparisonReview,
    HumanReviewBundle,
    canonical_sha256,
)

_IDENTITY_COLUMNS = (
    "campaign_id",
    "public_bundle_sha256",
    "comparison_id",
    "prompt_id",
    "prompt_version",
    "reviewer_id",
    "preference",
)
_CANDIDATE_A_SCORE_COLUMNS = tuple(
    f"candidate_a_score__{dimension.value}" for dimension in EvaluationDimension
)
_CANDIDATE_A_GATE_COLUMNS = tuple(f"candidate_a_gate__{gate.value}" for gate in HardGate)
_CANDIDATE_B_SCORE_COLUMNS = tuple(
    f"candidate_b_score__{dimension.value}" for dimension in EvaluationDimension
)
_CANDIDATE_B_GATE_COLUMNS = tuple(f"candidate_b_gate__{gate.value}" for gate in HardGate)
REVIEW_CSV_COLUMNS = (
    *_IDENTITY_COLUMNS,
    *_CANDIDATE_A_SCORE_COLUMNS,
    *_CANDIDATE_A_GATE_COLUMNS,
    *_CANDIDATE_B_SCORE_COLUMNS,
    *_CANDIDATE_B_GATE_COLUMNS,
    "notes",
)
_DIMENSION_QUESTIONS = {
    EvaluationDimension.CAUSAL_COHERENCE: (
        "Do events follow convincingly, build, and reach a complete ending?"
    ),
    EvaluationDimension.CHARACTER_DEPTH: (
        "Do characters have distinct motives, contradictions, and believable behavior?"
    ),
    EvaluationDimension.DIALOGUE: (
        "Is the dialogue distinctive, subtextual, natural, and non-expository?"
    ),
    EvaluationDimension.ORIGINALITY: (
        "Does the story avoid generic AI patterns and obvious clichés?"
    ),
    EvaluationDimension.VOICE: ("Is the writing controlled, vivid, and stylistically consistent?"),
    EvaluationDimension.EMOTIONAL_IMPACT: (
        "Does the story produce a meaningful emotional or thematic effect?"
    ),
    EvaluationDimension.PACING: (
        "Does each section earn its place and move at an appropriate pace?"
    ),
    EvaluationDimension.CONTINUITY: (
        "Does it honor the prompt, established facts, constraints, and format?"
    ),
}
_HARD_GATE_DESCRIPTIONS = {
    HardGate.COMPLETE: "The story is complete.",
    HardGate.CENTRAL_FACTS_CONSISTENT: "No central established fact is contradicted.",
    HardGate.MANDATORY_REQUIREMENTS_PRESENT: "Every mandatory prompt requirement is present.",
    HardGate.NO_PLACEHOLDERS_OR_MODEL_COMMENTARY: (
        "There are no placeholders or model commentary."
    ),
    HardGate.TARGET_FORMAT_VALID: "The requested short-prose format is respected.",
    HardGate.ENDING_NOT_TRUNCATED: "The ending is not cut off by a token limit.",
    HardGate.NO_CRITIC_NOTES_IN_PROSE: "Critic notes are not incorporated as story prose.",
}


def render_review_csv(
    public_bundle: BlindPublicBundle,
    *,
    reviewer_id: str,
) -> str:
    """Create one blank scoring row per blinded comparison."""
    normalized_reviewer_id = reviewer_id.strip()
    if not normalized_reviewer_id:
        raise ValueError("reviewer_id must not be empty")
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=REVIEW_CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    public_digest = canonical_sha256(public_bundle.model_dump(mode="json"))
    for comparison in public_bundle.comparisons:
        row = {column: "" for column in REVIEW_CSV_COLUMNS}
        row.update(
            {
                "campaign_id": str(public_bundle.campaign_id),
                "public_bundle_sha256": public_digest,
                "comparison_id": comparison.comparison_id,
                "prompt_id": comparison.prompt_id,
                "prompt_version": comparison.prompt_version,
                "reviewer_id": normalized_reviewer_id,
            }
        )
        writer.writerow(row)
    return output.getvalue()


def render_review_guide(
    public_bundle: BlindPublicBundle,
    *,
    reviewer_id: str,
) -> str:
    """Render a provenance-free guide for applying the canonical rubric."""
    normalized_reviewer_id = reviewer_id.strip()
    if not normalized_reviewer_id:
        raise ValueError("reviewer_id must not be empty")
    public_digest = canonical_sha256(public_bundle.model_dump(mode="json"))
    lines = [
        "# Open Hollywood blind review guide",
        "",
        f"- Campaign: `{public_bundle.campaign_id}`",
        f"- Public packet SHA-256: `{public_digest}`",
        f"- Reviewer: `{normalized_reviewer_id.replace('`', '')}`",
        f"- Rubric: `{CANONICAL_RUBRIC_NAME}` version `{CANONICAL_RUBRIC_VERSION}`",
        "",
        "Review only the public packet and CSV form. Do not access the private answer key "
        "or try to identify the model/profile behind either candidate.",
        "",
        "For each comparison, read A and B in the public packet, choose `a`, `b`, or `tie`, "
        "then score both candidates on every dimension.",
        "",
        "Score anchors: `1` = seriously broken; `3` = competent but ordinary or noticeably "
        "flawed; `5` = memorable, highly controlled, and close to publishable with minor "
        "editing.",
        "",
        "## Scoring dimensions",
        "",
        "| CSV suffix | Weight | Question |",
        "|---|---:|---|",
    ]
    lines.extend(
        f"| `{dimension.value}` | {EVALUATION_WEIGHTS[dimension]}% | "
        f"{_DIMENSION_QUESTIONS[dimension]} |"
        for dimension in EvaluationDimension
    )
    lines.extend(
        [
            "",
            "## Hard gates",
            "",
            "Enter `true` only when the statement holds; otherwise enter `false`.",
            "The prompt's word-count range is advisory, not a hard gate. Judge excess or "
            "insufficient development through pacing, structure, and prose quality; mark a hard "
            "gate false only for the defect named by that gate.",
            "",
        ]
    )
    lines.extend(f"- `{gate.value}`: {_HARD_GATE_DESCRIPTIONS[gate]}" for gate in HardGate)
    lines.extend(
        [
            "",
            "Complete every non-notes cell for each submitted row. Rows may be divided among "
            "reviewers, but a reviewer must not score the same comparison more than once.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_review_csvs(
    public_bundle: BlindPublicBundle,
    sources: Iterable[str],
) -> HumanReviewBundle:
    """Validate and merge completed CSV forms into immutable review evidence."""
    source_values = tuple(sources)
    if not source_values:
        raise ValueError("at least one completed review CSV is required")
    public_digest = canonical_sha256(public_bundle.model_dump(mode="json"))
    comparisons = {comparison.comparison_id: comparison for comparison in public_bundle.comparisons}
    if len(comparisons) != len(public_bundle.comparisons):
        raise ValueError("public review packet comparison IDs must be unique")
    reviews: list[HumanComparisonReview] = []
    for source_number, source in enumerate(source_values, start=1):
        reader = csv.DictReader(StringIO(source, newline=""))
        if tuple(reader.fieldnames or ()) != REVIEW_CSV_COLUMNS:
            raise ValueError(f"review CSV {source_number} has an unexpected header")
        for row_number, row in enumerate(reader, start=2):
            reviews.append(
                _parse_review_row(
                    row,
                    row_number=row_number,
                    source_number=source_number,
                    public_bundle=public_bundle,
                    public_digest=public_digest,
                    comparisons=comparisons,
                )
            )
    if not reviews:
        raise ValueError("completed review CSV files contain no review rows")
    return HumanReviewBundle(
        schema_version=HUMAN_REVIEW_SCHEMA_VERSION,
        campaign_id=public_bundle.campaign_id,
        public_bundle_sha256=public_digest,
        reviews=tuple(reviews),
    )


def _parse_review_row(
    row: dict[str, str | None],
    *,
    row_number: int,
    source_number: int,
    public_bundle: BlindPublicBundle,
    public_digest: str,
    comparisons: dict[str, BlindComparison],
) -> HumanComparisonReview:
    location = f"review CSV {source_number} row {row_number}"
    campaign_id = _required(row, "campaign_id", location)
    if campaign_id != str(public_bundle.campaign_id):
        raise ValueError(f"{location} belongs to a different campaign")
    if _required(row, "public_bundle_sha256", location) != public_digest:
        raise ValueError(f"{location} belongs to a different public review packet")
    comparison_id = _required(row, "comparison_id", location)
    comparison = comparisons.get(comparison_id)
    if comparison is None:
        raise ValueError(f"{location} references an unknown comparison")
    prompt_id = _required(row, "prompt_id", location)
    prompt_version = _required(row, "prompt_version", location)
    if prompt_id != comparison.prompt_id or prompt_version != comparison.prompt_version:
        raise ValueError(f"{location} prompt identity does not match its comparison")
    try:
        preference = BlindPreference(_required(row, "preference", location).lower())
    except ValueError as error:
        raise ValueError(f"{location} preference must be a, b, or tie") from error
    return HumanComparisonReview(
        comparison_id=comparison_id,
        reviewer_id=_required(row, "reviewer_id", location),
        preference=preference,
        candidate_a_score=_score(row, "candidate_a", location),
        candidate_b_score=_score(row, "candidate_b", location),
        notes=_optional(row, "notes"),
    )


def _score(
    row: dict[str, str | None],
    candidate: str,
    location: str,
) -> CanonicalStoryScore:
    return CanonicalStoryScore(
        dimension_scores={
            dimension: _integer_score(
                row,
                f"{candidate}_score__{dimension.value}",
                location,
            )
            for dimension in EvaluationDimension
        },
        hard_gates={
            gate: _boolean(
                row,
                f"{candidate}_gate__{gate.value}",
                location,
            )
            for gate in HardGate
        },
    )


def _integer_score(
    row: dict[str, str | None],
    column: str,
    location: str,
) -> int:
    value = _required(row, column, location)
    try:
        score = int(value)
    except ValueError as error:
        raise ValueError(f"{location} column {column!r} must be an integer from 1 to 5") from error
    if not 1 <= score <= 5:
        raise ValueError(f"{location} column {column!r} must be from 1 to 5")
    return score


def _boolean(
    row: dict[str, str | None],
    column: str,
    location: str,
) -> bool:
    value = _required(row, column, location).lower()
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError(f"{location} column {column!r} must be true or false")


def _required(
    row: dict[str, str | None],
    column: str,
    location: str,
) -> str:
    value = row.get(column)
    normalized = value.strip() if value is not None else ""
    if not normalized:
        raise ValueError(f"{location} column {column!r} must not be empty")
    return normalized


def _optional(row: dict[str, str | None], column: str) -> str | None:
    value = row.get(column)
    normalized = value.strip() if value is not None else ""
    return normalized or None
