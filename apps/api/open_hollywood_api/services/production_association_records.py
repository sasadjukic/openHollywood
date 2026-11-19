"""Pure association records and structural validation, not source authentication.

Only the registered exporter authenticates these saved snapshots. Matching a selected
artifact is an identity comparison, never permission to attach an assessment or edit.
No database, filesystem, provider or workflow operations belong here.
"""

from __future__ import annotations

import json
import re
from typing import Literal
from uuid import UUID

from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    Identifier,
    JsonObject,
    Record,
    SavedMessage,
    messages_hash,
    object_value,
    require,
    strict_object,
    string_value,
    text_hash,
)
from pydantic import Field

NOTICE = (
    "READ-ONLY REGISTERED SOURCE ASSOCIATION. Identity at the captured database snapshot, "
    "not a current database lookup or provider attestation. Historical v33 review; current "
    "assessment contract unsupported and native assessment delivery absent. No assessment "
    "attachment, semantic qualification or writer permission."
)


class ArtifactRow(Record):
    id: Identifier
    artifact_id: Identifier
    parent_version_id: Identifier | None
    created_by_invocation_id: Identifier | None
    version_number: int = Field(ge=1)
    schema_version: str
    project_id: Identifier
    artifact_type: str
    artifact_key: str
    content: JsonObject
    content_sha256: Digest
    # Raw SQL JSON serialization was not retained. This is preserved source metadata;
    # canonical content hashes below are independently recomputed.
    stored_content_bytes_sha256: Digest


class InvocationRow(Record):
    id: Identifier
    workflow_run_id: Identifier
    project_id: Identifier
    specialist_role: str
    provider: str
    model_identifier: str
    status: str
    schema_validation_succeeded: int = Field(ge=0, le=1)
    request_settings: JsonObject
    prompt_sha256: Digest
    prompt_text: str = Field(min_length=1, max_length=2_000_000)
    workflow_name: str
    graph_version: str
    execution_kind: str
    run_prompt_version: str | None


class CreatorRow(Record):
    id: Identifier
    workflow_run_id: Identifier
    project_id: Identifier
    specialist_role: str
    status: str


class LineageRow(Record):
    id: Identifier
    artifact_id: Identifier
    parent_version_id: Identifier | None
    created_by_invocation_id: Identifier | None
    version_number: int = Field(ge=1)
    content_sha256: Digest


class AssociationSnapshot(Record):
    contract: Literal["private-production-association-snapshot-1"]
    origin: Literal["saved_production_review_identity_audit_not_assessment_delivery"]
    database_sha256: Digest
    invocation: InvocationRow
    review_outputs: tuple[Identifier, ...] = Field(min_length=1, max_length=64)
    review: ArtifactRow
    input_link_ids: tuple[Identifier, ...] = Field(min_length=1, max_length=128)
    inputs: tuple[ArtifactRow, ...] = Field(min_length=1, max_length=128)
    draft_creator: CreatorRow
    review_lineage: tuple[LineageRow, ...] = Field(min_length=1, max_length=64)
    draft_lineage: tuple[LineageRow, ...] = Field(min_length=1, max_length=64)
    existing_intake_reason: Literal["unsupported_contract"]


class ExpectedReview(Record):
    database_snapshot_sha256: Digest
    invocation_id: Identifier
    workflow_run_id: Identifier
    project_id: Identifier
    critique_artifact_id: Identifier
    critique_version_id: Identifier
    draft_version_id: Identifier


class AssociationBinding(Record):
    database_snapshot_sha256: Digest
    project_id: Identifier
    workflow_run_id: Identifier
    review_invocation_id: Identifier
    critique_artifact_id: Identifier
    critique_version_id: Identifier
    critique_content_sha256: Digest
    target_artifact_id: Identifier
    target_version_id: Identifier
    target_content_sha256: Digest
    plan_version_id: Identifier
    plan_content_sha256: Digest
    prompt_sha256: Digest
    visible_target_sha256: Digest


class LineageFacts(Record):
    latest_version_id_at_capture: Identifier
    selected_is_latest_at_capture: bool
    version_count: int = Field(ge=1, le=64)
    selected_parent_version_id: Identifier | None


class CatalogOccurrence(Record):
    ref: str = Field(min_length=1, max_length=1000)
    start: int = Field(ge=0)
    end: int = Field(ge=1)
    quote_sha256: Digest


class Eligibility(Record):
    source_contract: Literal["unsupported_contract"] = "unsupported_contract"
    prompt_version: Literal["33"] = "33"
    required_prompt_version: Literal["61"] = "61"
    required_scene_boundary_audit_present: Literal[False] = False
    required_run_prompt_marker_present: Literal[False] = False
    native_assessment_delivery: Literal["missing"] = "missing"
    assessment_attachment_eligible: Literal[False] = False


class AssociationEvidence(Record):
    """Structural evidence only; a parsed object does not authenticate its source."""

    binding: AssociationBinding
    binding_sha256: Digest
    review_lineage: LineageFacts
    draft_lineage: LineageFacts
    input_versions_verified: int = Field(ge=1, le=128)
    catalog_occurrences: tuple[CatalogOccurrence, ...] = Field(min_length=1, max_length=10000)
    repeated_excerpt_texts: int = Field(ge=0)
    visible_target_is_full_canonical_json: Literal[False] = False
    catalog_non_whitespace_prose_coverage: Literal[True] = True
    inter_excerpt_whitespace_is_separate: Literal[True] = True
    eligibility: Eligibility = Eligibility()


class SourceAuthentication(Record):
    registration: str
    archive_seal_bytes_sha256: Digest
    snapshot_member: str = Field(pattern=r"^R0[1-6]\.snapshot\.json$")
    snapshot_bytes_sha256: Digest
    basis: Literal["registered_audit_snapshot"] = "registered_audit_snapshot"
    current_database_revalidated: Literal[False] = False
    provider_signed: Literal[False] = False


class AssociationRecord(Record):
    contract: Literal["production-review-association-1"] = "production-review-association-1"
    notice: str = NOTICE
    source: SourceAuthentication
    evidence: AssociationEvidence
    identity_status: Literal["verified_in_registered_snapshot"] = "verified_in_registered_snapshot"
    semantic_support: Literal["unassessed"] = "unassessed"
    evidence_adequacy: Literal["unassessed"] = "unassessed"
    editorial_effect: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"
    craft: Literal["unassessed"] = "unassessed"
    writer_dispatch_authorized: Literal[False] = False
    whole_review_verdict: None = None
    actual_billed_cost: None = None
    live_calls: Literal[0] = 0


class ArtifactSelection(Record):
    role: Literal["original_review", "reviewed_draft"]
    project_id: Identifier
    artifact_id: Identifier
    version_id: Identifier
    content_sha256: Digest


def _messages(text: str, digest: str) -> tuple[SavedMessage, ...]:
    matches = []
    cursor, count = 0, 0
    while (cut := text.find("\n\n", cursor)) >= 0:
        count += 1
        require(count <= 512, "association_prompt_boundary_bound")
        pair = (
            SavedMessage(role="system", content=text[:cut]),
            SavedMessage(role="user", content=text[cut + 2 :]),
        )
        if messages_hash(pair) == digest:
            matches.append(pair)
        cursor = cut + 1
    require(len(matches) == 1, "association_prompt_binding")
    return matches[0]


def _lineage(rows: tuple[LineageRow, ...], item: ArtifactRow) -> LineageFacts:
    by_id = {r.id: r for r in rows}
    require(len(by_id) == len(rows) and item.id in by_id, "association_lineage_inventory")
    require(len({r.version_number for r in rows}) == len(rows), "association_version_ambiguity")
    for row in rows:
        require(row.artifact_id == item.artifact_id, "association_cross_artifact_lineage")
        if row.parent_version_id is not None:
            parent = by_id.get(row.parent_version_id)
            require(
                parent is not None and parent.version_number < row.version_number,
                "association_parent_missing_or_order",
            )
    selected = by_id[item.id]
    require(
        all(
            getattr(selected, key) == getattr(item, key)
            for key in (
                "parent_version_id",
                "content_sha256",
                "version_number",
                "created_by_invocation_id",
            )
        ),
        "association_lineage_mismatch",
    )
    latest = max(rows, key=lambda r: r.version_number)
    return LineageFacts(
        latest_version_id_at_capture=latest.id,
        selected_is_latest_at_capture=latest.id == item.id,
        version_count=len(rows),
        selected_parent_version_id=item.parent_version_id,
    )


def validate_snapshot(
    snapshot: AssociationSnapshot, expected: ExpectedReview
) -> AssociationEvidence:
    """Recompute identity evidence; caller must authenticate the archive independently."""
    s = AssociationSnapshot.model_validate_json(snapshot.model_dump_json())
    expected = ExpectedReview.model_validate_json(expected.model_dump_json())
    i, review = s.invocation, s.review
    require(
        (s.database_sha256, i.id, i.workflow_run_id, i.project_id, review.artifact_id, review.id)
        == (
            expected.database_snapshot_sha256,
            expected.invocation_id,
            expected.workflow_run_id,
            expected.project_id,
            expected.critique_artifact_id,
            expected.critique_version_id,
        ),
        "association_expected_identity",
    )
    settings = i.request_settings
    require(
        i.specialist_role == "scene_critic"
        and i.workflow_name == "scene_production"
        and i.status == "SUCCEEDED"
        and i.schema_validation_succeeded == 1
        and settings.get("operation") == "critique",
        "association_unsuccessful_review",
    )
    require(
        settings.get("prompt_template_version") == "33"
        and settings.get("graph_version") == i.graph_version == "9",
        "association_unsupported_identity_contract",
    )
    # This narrow historical registration cannot supply the current eligibility contract.
    audit = settings.get("scene_boundary_audit")
    require(
        (not isinstance(audit, dict) or audit.get("schema_version") != "7")
        and i.run_prompt_version != "61",
        "association_conflicting_contract_metadata",
    )
    require(
        review.artifact_type == "critique"
        and review.created_by_invocation_id == i.id
        and s.review_outputs == (review.id,),
        "association_review_creator_or_ambiguity",
    )
    by_id = {a.id: a for a in s.inputs}
    require(
        len(by_id) == len(s.inputs) == len(set(s.input_link_ids)) == len(s.input_link_ids)
        and set(by_id) == set(s.input_link_ids),
        "association_input_inventory",
    )
    for item in (review, *s.inputs):
        require(item.project_id == i.project_id, "association_cross_project")
        require(canonical_sha256(item.content) == item.content_sha256, "association_content_hash")
    target_id = str(UUID(string_value(review.content.get("target_artifact_version_id"))))
    require(target_id == expected.draft_version_id and target_id in by_id, "association_target")
    draft = by_id[target_id]
    require(draft.artifact_type == "scene_draft", "association_target_kind")
    require(
        (draft.created_by_invocation_id, i.project_id, i.workflow_run_id)
        == (s.draft_creator.id, s.draft_creator.project_id, s.draft_creator.workflow_run_id)
        and s.draft_creator.status == "SUCCEEDED"
        and s.draft_creator.specialist_role == "scene_writer",
        "association_draft_creator",
    )
    scene = string_value(draft.content.get("scene_id"))
    plans = [
        a for a in s.inputs if a.artifact_type == "scene_plan" and a.content.get("id") == scene
    ]
    require(len(plans) == 1, "association_plan_ambiguity")
    messages = _messages(i.prompt_text, i.prompt_sha256)
    payload = strict_object(messages[1].content)
    require(
        object_value(payload.get("assignment")).get("unit_id") == scene, "association_request_scene"
    )
    raw_views = payload.get("input_artifacts")
    require(
        isinstance(raw_views, list) and len(raw_views) == len(s.inputs),
        "association_visible_inventory",
    )
    assert isinstance(raw_views, list)
    views = [object_value(v) for v in raw_views]
    view_ids = [string_value(v.get("artifact_version_id")) for v in views]
    require(
        len(set(view_ids)) == len(view_ids) and set(view_ids) == set(by_id),
        "association_visible_ambiguity",
    )
    for view in views:
        item = by_id[string_value(view.get("artifact_version_id"))]
        require(
            (view.get("artifact_kind"), view.get("artifact_key"))
            == (item.artifact_type, item.artifact_key),
            "association_visible_identity",
        )
    visible = next(v for v in views if v.get("artifact_version_id") == target_id)
    content = object_value(visible.get("content"))
    prose = string_value(draft.content.get("prose"))
    require(
        "prose" not in content and "evidence_catalog" in content,
        "association_catalog_view_required",
    )
    require(
        all(
            key in draft.content and draft.content[key] == value
            for key, value in content.items()
            if key != "evidence_catalog"
        ),
        "association_visible_content",
    )
    raw_entries = content["evidence_catalog"]
    require(
        isinstance(raw_entries, list) and 1 <= len(raw_entries) <= 10000,
        "association_catalog_bound",
    )
    assert isinstance(raw_entries, list)
    entries = [object_value(e) for e in raw_entries]
    refs = [string_value(e.get("evidence_ref")) for e in entries]
    require(len(refs) == len(set(refs)), "association_catalog_duplicate_ref")
    occurrences = []
    cursor, repeated = 0, 0
    for entry in entries:
        text = string_value(entry.get("exact_excerpt"))
        require(bool(text), "association_empty_excerpt")
        start = prose.find(text, cursor)
        require(start >= 0 and not prose[cursor:start].strip(), "association_catalog_gap")
        repeated += int(prose.count(text) > 1)
        cursor = start + len(text)
        occurrences.append(
            CatalogOccurrence(
                ref=string_value(entry.get("evidence_ref")),
                start=start,
                end=cursor,
                quote_sha256=text_hash(text),
            )
        )
    require(not prose[cursor:].strip(), "association_catalog_gap")
    binding = AssociationBinding(
        database_snapshot_sha256=s.database_sha256,
        project_id=i.project_id,
        workflow_run_id=i.workflow_run_id,
        review_invocation_id=i.id,
        critique_artifact_id=review.artifact_id,
        critique_version_id=review.id,
        critique_content_sha256=review.content_sha256,
        target_artifact_id=draft.artifact_id,
        target_version_id=draft.id,
        target_content_sha256=draft.content_sha256,
        plan_version_id=plans[0].id,
        plan_content_sha256=plans[0].content_sha256,
        prompt_sha256=i.prompt_sha256,
        visible_target_sha256=canonical_sha256(visible),
    )
    return AssociationEvidence(
        binding=binding,
        binding_sha256=canonical_sha256(binding.model_dump(mode="json")),
        review_lineage=_lineage(s.review_lineage, review),
        draft_lineage=_lineage(s.draft_lineage, draft),
        input_versions_verified=len(s.inputs),
        catalog_occurrences=tuple(occurrences),
        repeated_excerpt_texts=repeated,
    )


def selection_matches(record: AssociationRecord, selection: ArtifactSelection) -> bool:
    """Compare explicit identity; grant no authentication or attachment authority."""
    record = AssociationRecord.model_validate_json(record.model_dump_json())
    selection = ArtifactSelection.model_validate_json(selection.model_dump_json())
    b = record.evidence.binding
    expected = (
        (b.critique_artifact_id, b.critique_version_id, b.critique_content_sha256)
        if (selection.role == "original_review")
        else (b.target_artifact_id, b.target_version_id, b.target_content_sha256)
    )
    return (
        selection.project_id == b.project_id
        and (selection.artifact_id, selection.version_id, selection.content_sha256) == expected
    )


def render_record(record: AssociationRecord) -> bytes:
    """All source strings remain literal; only fixed generated case links are active."""
    record = AssociationRecord.model_validate_json(record.model_dump_json())
    case = record.source.snapshot_member.removesuffix(".snapshot.json")
    text = json.dumps(record.model_dump(mode="json"), ensure_ascii=False, indent=2)
    fence = "`" * max(3, 1 + max((len(m.group()) for m in re.finditer(r"`+", text)), default=0))
    return (
        f"# {case}: historical production association\n\n{NOTICE}\n\n"
        f"[Complete source snapshot]({case}.snapshot.json) · "
        f"[Association record]({case}.association.json)\n\n"
        "Latest-version facts are as of the captured snapshot. Source identity remains "
        "separate from the unsupported contract and missing assessment delivery.\n\n"
        f"{fence}json\n{text}\n{fence}\n"
    ).encode()
