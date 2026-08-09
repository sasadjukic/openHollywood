"""Digest-bound human review artifacts for benchmark Story Blueprints."""

from __future__ import annotations

import csv
import io
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import Field, StringConstraints, model_validator

from open_hollywood_engine.artifacts import Critique, StoryBlueprint
from open_hollywood_engine.evaluations.contracts import (
    BenchmarkPrompt,
    EvaluationModel,
    Sha256,
    canonical_sha256,
)

BLUEPRINT_REVIEW_SCHEMA_VERSION: Literal["1"] = "1"
BLUEPRINT_REVIEW_CSV_COLUMNS = (
    "campaign_id",
    "plan_sha256",
    "packet_sha256",
    "reviewer_id",
    "case_id",
    "prompt_id",
    "target_key",
    "workflow_run_id",
    "blueprint_version_id",
    "blueprint_content_sha256",
    "approved",
    "notes",
)

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class BlueprintReviewCase(EvaluationModel):
    """One exact paused Blueprint and its human-review context."""

    case_id: UUID
    prompt: BenchmarkPrompt
    target_key: NonEmptyText
    workflow_run_id: UUID
    interrupt_id: NonEmptyText
    blueprint_version_id: UUID
    blueprint_content_sha256: Sha256
    blueprint: StoryBlueprint
    critique_version_id: UUID
    critique_content_sha256: Sha256
    critique: Critique

    @model_validator(mode="after")
    def validate_lineage(self) -> Self:
        if (
            canonical_sha256(self.blueprint.model_dump(mode="json"))
            != self.blueprint_content_sha256
        ):
            raise ValueError("Blueprint content digest does not match")
        if canonical_sha256(self.critique.model_dump(mode="json")) != self.critique_content_sha256:
            raise ValueError("Blueprint critique content digest does not match")
        if self.critique.target_artifact_version_id != self.blueprint_version_id:
            raise ValueError("Blueprint critique targets a different artifact version")
        return self


class BlueprintReviewPacket(EvaluationModel):
    """Deterministic set of surviving Blueprints presented to one reviewer."""

    schema_version: str
    campaign_id: UUID
    corpus_sha256: Sha256
    plan_sha256: Sha256
    cases: tuple[BlueprintReviewCase, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_packet(self) -> Self:
        if self.schema_version != BLUEPRINT_REVIEW_SCHEMA_VERSION:
            raise ValueError(f"unsupported Blueprint review schema version {self.schema_version!r}")
        case_ids = [case.case_id for case in self.cases]
        if len(set(case_ids)) != len(case_ids):
            raise ValueError("Blueprint review case IDs must be unique")
        return self

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(self.model_dump(mode="json"))


class BlueprintApprovalRecord(EvaluationModel):
    """One affirmative human decision bound to an exact Blueprint version."""

    case_id: UUID
    workflow_run_id: UUID
    blueprint_version_id: UUID
    blueprint_content_sha256: Sha256
    notes: str = ""


class BlueprintApprovalBundle(EvaluationModel):
    """Complete reviewer submission for one exact Blueprint review packet."""

    schema_version: str
    campaign_id: UUID
    plan_sha256: Sha256
    packet_sha256: Sha256
    reviewer_id: NonEmptyText
    approvals: tuple[BlueprintApprovalRecord, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_bundle(self) -> Self:
        if self.schema_version != BLUEPRINT_REVIEW_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported Blueprint approval schema version {self.schema_version!r}"
            )
        case_ids = [approval.case_id for approval in self.approvals]
        if len(set(case_ids)) != len(case_ids):
            raise ValueError("Blueprint approval case IDs must be unique")
        return self


def render_blueprint_review_csv(packet: BlueprintReviewPacket, *, reviewer_id: str) -> str:
    """Create a spreadsheet-friendly approval form with immutable lineage prefilled."""
    normalized_reviewer = reviewer_id.strip()
    if not normalized_reviewer:
        raise ValueError("reviewer_id must not be empty")
    target = io.StringIO(newline="")
    writer = csv.DictWriter(target, fieldnames=BLUEPRINT_REVIEW_CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for case in packet.cases:
        writer.writerow(
            {
                "campaign_id": str(packet.campaign_id),
                "plan_sha256": packet.plan_sha256,
                "packet_sha256": packet.content_sha256,
                "reviewer_id": normalized_reviewer,
                "case_id": str(case.case_id),
                "prompt_id": case.prompt.prompt_id,
                "target_key": case.target_key,
                "workflow_run_id": str(case.workflow_run_id),
                "blueprint_version_id": str(case.blueprint_version_id),
                "blueprint_content_sha256": case.blueprint_content_sha256,
                "approved": "",
                "notes": "",
            }
        )
    return target.getvalue()


def parse_blueprint_review_csv(
    packet: BlueprintReviewPacket,
    source: str,
) -> BlueprintApprovalBundle:
    """Validate a completed form and require affirmative review of every packet case."""
    reader = csv.DictReader(io.StringIO(source))
    if tuple(reader.fieldnames or ()) != BLUEPRINT_REVIEW_CSV_COLUMNS:
        raise ValueError("Blueprint review CSV columns do not match the canonical form")
    rows = list(reader)
    if len(rows) != len(packet.cases):
        raise ValueError("Blueprint review form must contain every packet case exactly once")
    packet_cases = {str(case.case_id): case for case in packet.cases}
    seen: set[str] = set()
    reviewer_ids: set[str] = set()
    approvals: list[BlueprintApprovalRecord] = []
    for row_number, row in enumerate(rows, start=2):
        _require_form_value(row, "campaign_id", str(packet.campaign_id), row_number)
        _require_form_value(row, "plan_sha256", packet.plan_sha256, row_number)
        _require_form_value(row, "packet_sha256", packet.content_sha256, row_number)
        reviewer_id = row["reviewer_id"].strip()
        if not reviewer_id:
            raise ValueError(f"Blueprint review row {row_number} has no reviewer_id")
        reviewer_ids.add(reviewer_id)
        case_id = row["case_id"].strip()
        if case_id in seen:
            raise ValueError(f"Blueprint review case {case_id} appears more than once")
        seen.add(case_id)
        case = packet_cases.get(case_id)
        if case is None:
            raise ValueError(f"Blueprint review row {row_number} has an unknown case_id")
        _require_form_value(row, "prompt_id", case.prompt.prompt_id, row_number)
        _require_form_value(row, "target_key", case.target_key, row_number)
        _require_form_value(row, "workflow_run_id", str(case.workflow_run_id), row_number)
        _require_form_value(
            row,
            "blueprint_version_id",
            str(case.blueprint_version_id),
            row_number,
        )
        _require_form_value(
            row,
            "blueprint_content_sha256",
            case.blueprint_content_sha256,
            row_number,
        )
        if row["approved"].strip().casefold() != "yes":
            raise ValueError(f"Blueprint review row {row_number} must contain 'yes' in approved")
        approvals.append(
            BlueprintApprovalRecord(
                case_id=case.case_id,
                workflow_run_id=case.workflow_run_id,
                blueprint_version_id=case.blueprint_version_id,
                blueprint_content_sha256=case.blueprint_content_sha256,
                notes=row["notes"].strip(),
            )
        )
    if len(reviewer_ids) != 1:
        raise ValueError("Blueprint review form must identify exactly one reviewer")
    if seen != set(packet_cases):
        raise ValueError("Blueprint review form does not cover every packet case")
    return BlueprintApprovalBundle(
        schema_version=BLUEPRINT_REVIEW_SCHEMA_VERSION,
        campaign_id=packet.campaign_id,
        plan_sha256=packet.plan_sha256,
        packet_sha256=packet.content_sha256,
        reviewer_id=reviewer_ids.pop(),
        approvals=tuple(approvals),
    )


def render_blueprint_review_guide(packet: BlueprintReviewPacket, *, reviewer_id: str) -> str:
    """Render all review context and Blueprints as a readable Markdown dossier."""
    normalized_reviewer = reviewer_id.strip()
    if not normalized_reviewer:
        raise ValueError("reviewer_id must not be empty")
    lines = [
        "# Open Hollywood Story Blueprint review",
        "",
        f"- Campaign: `{packet.campaign_id}`",
        f"- Reviewer: `{normalized_reviewer}`",
        f"- Plan SHA-256: `{packet.plan_sha256}`",
        f"- Review packet SHA-256: `{packet.content_sha256}`",
        f"- Surviving Blueprints: {len(packet.cases)}",
        "",
        "## Approval standard",
        "",
        "Approve a Blueprint only after confirming that it:",
        "",
        "- faithfully retains the frozen premise and every required element;",
        "- avoids every forbidden shortcut;",
        "- presents a complete, causally coherent short-story arc and ending;",
        "- gives each scene a concrete dramatic purpose, conflict, turn, and outcome;",
        "- keeps characters, locations, beats, and scene references internally consistent;",
        "- contains no unresolved decision that prevents autonomous drafting; and",
        "- is suitable for autonomous production without adding another human checkpoint.",
        "",
        "This checkpoint is not a blind quality comparison and does not rank profiles. "
        "Review the exact content below, then enter `yes` in the matching CSV row only "
        "when you approve that exact Blueprint version. Do not edit any prefilled lineage field.",
        "",
    ]
    for index, case in enumerate(packet.cases, start=1):
        lines.extend(_render_case(index, case))
    return "\n".join(lines).rstrip() + "\n"


def _render_case(index: int, case: BlueprintReviewCase) -> list[str]:
    blueprint = case.blueprint
    brief = blueprint.creative_brief
    lines = [
        f"## {index}. {case.prompt.prompt_id} / {case.target_key}",
        "",
        f"- Case ID: `{case.case_id}`",
        f"- Workflow run: `{case.workflow_run_id}`",
        f"- Blueprint version: `{case.blueprint_version_id}`",
        f"- Blueprint SHA-256: `{case.blueprint_content_sha256}`",
        f"- Critique version: `{case.critique_version_id}`",
        "",
        "### Frozen prompt",
        "",
        _quote(case.prompt.prompt),
        "",
        "**Required elements**",
        "",
        *_bullets(case.prompt.required_elements),
        "",
        "**Forbidden shortcuts**",
        "",
        *_bullets(case.prompt.forbidden_shortcuts),
        "",
        "### Creative brief",
        "",
        f"- Original premise: {_inline(brief.original_premise)}",
        f"- Interpretation: {_inline(brief.interpretation)}",
        f"- Format: `{brief.story_format.value}`",
        f"- Genres: {', '.join(brief.genres)}",
        f"- Tone: {', '.join(brief.tone)}",
        f"- Maturity: `{brief.maturity.value}`",
        f"- Intended effect: {_inline(brief.intended_effect)}",
        f"- Target audience: {_inline(brief.target_audience)}",
        f"- Target: {brief.target_word_count} words, {brief.target_scene_count} scenes, "
        f"{brief.target_significant_character_count} significant characters",
        f"- Central dramatic question: {_inline(brief.central_dramatic_question)}",
        f"- Themes: {', '.join(brief.themes)}",
        "",
        "**Assumptions**",
        "",
        *_bullets(brief.assumptions),
        "",
        "**Brief-required elements**",
        "",
        *_bullets(brief.required_elements),
        "",
        "**Brief-forbidden elements**",
        "",
        *_bullets(brief.forbidden_elements),
        "",
        "**Style constraints**",
        "",
        *_bullets(brief.style_constraints),
        "",
        "**Authorized ambiguities**",
        "",
        *_bullets(brief.authorized_ambiguities),
        "",
        "### Story architecture",
        "",
        f"**Logline:** {_inline(blueprint.logline)}",
        "",
        f"**Thematic thesis:** {_inline(blueprint.thematic_thesis)}",
        "",
        f"**World:** {_inline(blueprint.world_summary)}",
        "",
        f"**Central conflict:** {_inline(blueprint.central_conflict)}",
        "",
        f"**Story arc:** {_inline(blueprint.story_arc)}",
        "",
        f"**Proposed ending:** {_inline(blueprint.proposed_ending)}",
        "",
        f"**Voice and style:** {_inline(blueprint.voice_and_style_guide)}",
        "",
        "### Characters",
        "",
    ]
    for character in blueprint.characters:
        lines.extend(
            [
                f"#### {character.name} (`{character.id}`)",
                "",
                f"- Role: {_inline(character.story_role)}",
                f"- Description: {_inline(character.description)}",
                (
                    f"- Goal / need: {_inline(character.external_goal)} / "
                    f"{_inline(character.internal_need)}"
                ),
                (
                    f"- Motivation / stakes: {_inline(character.motivation)} / "
                    f"{_inline(character.stakes)}"
                ),
                f"- Conflict: {_inline(character.primary_conflict)}",
                f"- Arc: {_inline(character.arc)}",
                f"- Traits: {'; '.join(_inline(item) for item in character.traits)}",
                f"- Voice: {_inline(character.voice)}",
                (
                    "- Contradictions: "
                    + "; ".join(_inline(item) for item in character.contradictions)
                ),
                f"- Secrets: {'; '.join(_inline(item) for item in character.secrets) or 'None.'}",
                (
                    "- Initial knowledge: "
                    + ("; ".join(_inline(item) for item in character.initial_knowledge) or "None.")
                ),
                "",
            ]
        )
    lines.extend(["### Relationships", ""])
    for relationship in blueprint.relationships:
        lines.extend(
            [
                (
                    f"#### {relationship.label} (`{relationship.id}`; "
                    f"`{relationship.source_character_id}` -> "
                    f"`{relationship.target_character_id}`)"
                ),
                "",
                f"- Dynamic: {_inline(relationship.dynamic)}",
                f"- History: {_inline(relationship.history)}",
                f"- Tension: {_inline(relationship.tension)}",
                f"- Arc: {_inline(relationship.arc)}",
                f"- Mutual: {'yes' if relationship.is_mutual else 'no'}",
                "",
            ]
        )
    lines.extend(["### Locations", ""])
    for location in blueprint.locations:
        lines.extend(
            [
                f"#### {location.name} (`{location.id}`)",
                "",
                f"- Description: {_inline(location.description)}",
                f"- Atmosphere: {_inline(location.atmosphere)}",
                f"- Story function: {_inline(location.story_function)}",
                (
                    "- Sensory details: "
                    + "; ".join(_inline(item) for item in location.sensory_details)
                ),
                (
                    "- Constraints: "
                    + ("; ".join(_inline(item) for item in location.constraints) or "None.")
                ),
                (
                    "- Associated characters: "
                    + (", ".join(location.associated_character_ids) or "None.")
                ),
                "",
            ]
        )
    lines.extend(["### World rules", ""])
    for rule in blueprint.world_rules:
        lines.extend(
            [
                f"#### Rule `{rule.id}`",
                "",
                f"- Statement: {_inline(rule.statement)}",
                f"- Rationale: {_inline(rule.rationale)}",
                f"- Story consequence: {_inline(rule.story_consequence)}",
                f"- Exceptions: {'; '.join(_inline(item) for item in rule.exceptions) or 'None.'}",
                ("- Relevant locations: " + (", ".join(rule.relevant_location_ids) or "None.")),
                ("- Relevant characters: " + (", ".join(rule.relevant_character_ids) or "None.")),
                "",
            ]
        )
    lines.extend(["", "### Ordered beats", ""])
    for beat in blueprint.beats:
        lines.extend(
            [
                f"#### {beat.sequence}. {beat.title} (`{beat.id}`)",
                "",
                f"- Summary: {_inline(beat.summary)}",
                f"- Purpose: {_inline(beat.purpose)}",
                f"- Cause: {_inline(beat.cause)}",
                f"- Effect: {_inline(beat.effect)}",
                f"- Characters: {', '.join(beat.character_ids)}",
                f"- Location: `{beat.location_id}`" if beat.location_id else "- Location: None.",
                ("- Depends on beats: " + (", ".join(beat.depends_on_beat_ids) or "None.")),
                ("- Pays off beats: " + (", ".join(beat.pays_off_beat_ids) or "None.")),
                "",
            ]
        )
    lines.extend(["", "### Scene plan", ""])
    for scene in blueprint.scene_plans:
        lines.extend(
            [
                f"#### Scene {scene.scene_number}: {scene.title} (`{scene.id}`)",
                "",
                f"- Summary: {_inline(scene.summary)}",
                f"- Purpose: {_inline(scene.purpose)}",
                f"- Goal / conflict: {_inline(scene.goal)} / {_inline(scene.conflict)}",
                f"- Turning point: {_inline(scene.turning_point)}",
                f"- Outcome: {_inline(scene.outcome)}",
                f"- Entry / exit: {_inline(scene.entry_state)} / {_inline(scene.exit_state)}",
                f"- Characters: {', '.join(scene.character_ids)}",
                (
                    f"- Point of view: `{scene.point_of_view_character_id}`"
                    if scene.point_of_view_character_id
                    else "- Point of view: None specified."
                ),
                f"- Location / time: `{scene.location_id}` / {_inline(scene.time_context)}",
                f"- Beats: {', '.join(scene.beat_ids)}",
                f"- Estimated words: {scene.estimated_word_count}",
                (
                    "- Required elements: "
                    + ("; ".join(_inline(item) for item in scene.required_elements) or "None.")
                ),
                (
                    "- Continuity requirements: "
                    + (
                        "; ".join(_inline(item) for item in scene.continuity_requirements)
                        or "None."
                    )
                ),
                "",
            ]
        )
    lines.extend(
        [
            "### Risks and unresolved decisions",
            "",
            "**Potential risks**",
            "",
            *_bullets(blueprint.potential_risks),
            "",
            "**Unresolved decisions**",
            "",
            *_bullets(blueprint.unresolved_decisions),
            "",
            "### Automated Blueprint critique (advisory)",
            "",
            f"- Verdict: `{case.critique.verdict.value}`",
            f"- Overall score: {case.critique.overall_score:g}/5",
            f"- Summary: {_inline(case.critique.summary)}",
            "",
            "**Strengths**",
            "",
            *_bullets(case.critique.strengths),
            "",
            "**Issues**",
            "",
        ]
    )
    if case.critique.issues:
        for issue in case.critique.issues:
            lines.extend(
                [
                    f"- **{issue.severity.value} / {issue.category}:** "
                    f"{_inline(issue.description)}",
                    f"  - Evidence: {'; '.join(_inline(item) for item in issue.evidence)}",
                    f"  - Recommendation: {_inline(issue.recommendation)}",
                ]
            )
    else:
        lines.append("- None reported.")
    lines.extend(["", "**Rubric scores**", ""])
    for score in case.critique.scores:
        lines.append(f"- **{score.dimension}: {score.score}/5.** {_inline(score.rationale)}")
    lines.extend(["", "---", ""])
    return lines


def _require_form_value(
    row: dict[str, str],
    field: str,
    expected: str,
    row_number: int,
) -> None:
    if row[field].strip() != expected:
        raise ValueError(f"Blueprint review row {row_number} changed {field}")


def _bullets(values: tuple[str, ...]) -> list[str]:
    return [f"- {_inline(value)}" for value in values] or ["- None."]


def _inline(value: str) -> str:
    return " ".join(value.split())


def _quote(value: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in value.splitlines())
