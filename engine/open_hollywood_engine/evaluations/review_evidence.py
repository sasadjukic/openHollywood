"""Deterministic review evidence. No database, provider or workflow dependencies."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Annotated, Literal, TypedDict, cast
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from open_hollywood_engine.evaluations.contracts import canonical_sha256

Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Identifier = Annotated[str, Field(pattern=r"^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$")]
Anchor = Literal["turning_point", "outcome"]
JsonObject = dict[str, JsonValue]
CATALOG_CONTRACT: Literal["v61-draft-excerpts-1"] = "v61-draft-excerpts-1"
COMPARISON_RULE: Literal["exact Unicode code points; selected spans only; no normalization"] = (
    "exact Unicode code points; selected spans only; no normalization"
)
ANCHORS: tuple[Anchor, ...] = ("turning_point", "outcome")


class _SpanBinding(TypedDict):
    version_id: str
    project_id: str
    scene_id: str
    artifact_key: str
    field_pointer: Literal["/turning_point", "/outcome", "/prose"]
    evidence_ref: str | None
    canonical_content_sha256: str
    rendered_view_sha256: str
    context_scope: str | None


class EvidenceError(ValueError):
    """A bounded diagnostic reason, never a manuscript finding."""


def require(condition: bool, reason: str = "invalid_provenance") -> None:
    if not condition:
        raise EvidenceError(reason)


def object_value(value: JsonValue) -> JsonObject:
    require(isinstance(value, dict), "malformed_source")
    return cast(JsonObject, value)


def string_value(value: JsonValue) -> str:
    require(isinstance(value, str), "malformed_source")
    return cast(str, value)


def strict_object(text: str) -> JsonObject:
    def pairs(items: list[tuple[str, JsonValue]]) -> JsonObject:
        result: JsonObject = {}
        for key, value in items:
            require(key not in result, "malformed_source")
            result[key] = value
        return result

    def invalid_constant(_value: str) -> None:
        raise EvidenceError("malformed_source")

    return object_value(json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant))


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class SavedMessage(Record):
    role: Literal["system", "user"]
    content: str


def messages_hash(messages: tuple[SavedMessage, ...]) -> str:
    ordered = [{"role": m.role, "content": m.content} for m in messages]
    return text_hash(json.dumps(ordered, ensure_ascii=False, separators=(",", ":")))


def recover_messages(text: str | None, digest: str) -> tuple[SavedMessage, ...]:
    """Caller must establish the supported v61 two-message contract first."""
    require(text is not None and len(text) <= 2_000_000, "unavailable_view")
    assert text is not None
    matches: list[tuple[SavedMessage, ...]] = []
    cursor, count = 0, 0
    while (cut := text.find("\n\n", cursor)) >= 0:
        count += 1
        require(count <= 512, "unavailable_view")
        pair = (
            SavedMessage(role="system", content=text[:cut]),
            SavedMessage(role="user", content=text[cut + 2 :]),
        )
        if messages_hash(pair) == digest:
            matches.append(pair)
        cursor = cut + 1
    require(len(matches) == 1, "unavailable_view")
    return matches[0]


class ArtifactSource(Record):
    version_id: Identifier
    project_id: Identifier
    artifact_kind: str
    artifact_key: str
    content_sha256: Digest
    content: JsonObject | None

    @model_validator(mode="after")
    def valid_content(self) -> ArtifactSource:
        require(self.content is None or canonical_sha256(self.content) == self.content_sha256)
        return self


class ArtifactView(Record):
    artifact_version_id: Identifier
    artifact_kind: str
    artifact_key: str
    content: JsonObject
    context_scope: str | None = None


class InvocationIdentity(Record):
    invocation_id: Identifier
    workflow_run_id: Identifier
    project_id: Identifier
    attempt: int = Field(ge=1)
    task_fingerprint: Digest
    prompt_sha256: Digest
    response_sha256: Digest
    prompt_version: Literal["61"] = "61"
    graph_version: Literal["9"] = "9"


class NativeAssignmentCheck(Record):
    status: Literal["met", "unmet"]
    assessment: str = Field(min_length=1, max_length=600)
    draft_evidence_refs: tuple[str, ...] = Field(min_length=1, max_length=3)
    recommended_resolution: str | None = Field(max_length=600)

    @model_validator(mode="after")
    def valid_check(self) -> NativeAssignmentCheck:
        require(bool(self.assessment.strip()), "malformed_source")
        require(
            len(set(self.draft_evidence_refs)) == len(self.draft_evidence_refs), "malformed_source"
        )
        require(
            (self.status == "met" and self.recommended_resolution is None)
            or (
                self.status == "unmet"
                and bool(self.recommended_resolution and self.recommended_resolution.strip())
            ),
            "malformed_source",
        )
        return self


class ReviewSnapshot(Record):
    schema_version: Literal["1"] = "1"
    invocation: InvocationIdentity
    critique: ArtifactSource
    draft_version_id: Identifier
    plan_version_id: Identifier
    scene_id: str
    sources: tuple[ArtifactSource, ...]
    messages: tuple[SavedMessage, ...]
    native_audit: JsonObject
    catalog_contract: Literal["v61-draft-excerpts-1"] = CATALOG_CONTRACT


class CatalogExcerpt(Record):
    evidence_ref: str
    exact_excerpt: str = Field(min_length=1)


def catalog_v61(prose: str, version_id: str) -> tuple[CatalogExcerpt, ...]:
    """Pinned v61 algorithm, checked against production by parity tests."""
    excerpts: list[str] = []
    for paragraph in re.split(r"\n\s*\n", prose):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        matches = tuple(
            m.group(0).strip()
            for m in re.finditer(
                r".+?(?:[.!?…]+[\"'’”\)\]]*(?=\s+|$)|$)", paragraph, flags=re.DOTALL
            )
            if m.group(0).strip()
        )
        excerpts.extend(matches or (paragraph,))
    require(bool(excerpts), "malformed_source")
    return tuple(
        CatalogExcerpt(
            evidence_ref=f"draft_evidence_{i:04d}_{UUID(version_id).hex}", exact_excerpt=quote
        )
        for i, quote in enumerate(excerpts, 1)
    )


class SourceSpan(Record):
    version_id: Identifier
    project_id: Identifier
    scene_id: str
    artifact_key: str
    field_pointer: Literal["/turning_point", "/outcome", "/prose"]
    evidence_ref: str | None
    canonical_content_sha256: Digest
    rendered_view_sha256: Digest
    field_sha256: Digest | None
    catalog_sha256: Digest | None
    context_scope: str | None
    visibility: Literal[
        "shown_in_assignment_contract",
        "shown_in_catalog",
        "shown_in_full_prose",
        "recovered_after_review",
        "unavailable",
    ]
    start: int | None = Field(ge=0)
    end: int | None = Field(ge=0)
    quote: str | None

    @model_validator(mode="after")
    def valid_span(self) -> SourceSpan:
        if self.visibility == "unavailable":
            require(self.start is None and self.end is None and self.quote is None)
        else:
            require(self.start is not None and self.end is not None and self.quote is not None)
            assert self.start is not None and self.end is not None and self.quote is not None
            require(self.end - self.start == len(self.quote) and self.end > self.start)
        return self


def resolve_span(
    source: ArtifactSource,
    view: ArtifactView,
    *,
    scene_id: str,
    current_revision: int,
    field: Literal["/turning_point", "/outcome", "/prose"],
    evidence_ref: str | None,
    current: bool,
) -> SourceSpan:
    require(
        (source.version_id, source.artifact_key, source.artifact_kind)
        == (view.artifact_version_id, view.artifact_key, view.artifact_kind)
    )
    # Revalidate on every use; frozen models do not make nested JSON dictionaries immutable.
    require(source.content is None or canonical_sha256(source.content) == source.content_sha256)
    base = _SpanBinding(
        version_id=source.version_id,
        project_id=source.project_id,
        scene_id=scene_id,
        artifact_key=source.artifact_key,
        field_pointer=field,
        evidence_ref=evidence_ref,
        canonical_content_sha256=source.content_sha256,
        rendered_view_sha256=canonical_sha256(view.model_dump(mode="json", exclude_unset=True)),
        context_scope=view.context_scope,
    )
    if field == "/prose":
        revision = view.content.get("revision_number")
        require(
            source.artifact_kind == "scene_draft"
            and source.artifact_key == "scene_draft_" + scene_id
            and view.content.get("scene_id") == scene_id
            and type(revision) is int
        )
        assert isinstance(revision, int)
        require(revision == current_revision if current else revision < current_revision)
        require(
            isinstance(evidence_ref, str)
            and re.fullmatch(
                r"draft_evidence_[0-9]{4,}_" + UUID(source.version_id).hex, evidence_ref
            )
            is not None
        )
    else:
        require(
            current
            and source.artifact_kind == "scene_plan"
            and source.artifact_key == "scene_plan_" + scene_id
            and evidence_ref is None
        )
    if source.content is None:
        return SourceSpan(
            **base,
            field_sha256=None,
            catalog_sha256=None,
            visibility="unavailable",
            start=None,
            end=None,
            quote=None,
        )
    if field != "/prose":
        require(source.content.get("id") == scene_id)
        text = string_value(source.content.get(field[1:]))
        return SourceSpan(
            **base,
            field_sha256=text_hash(text),
            catalog_sha256=None,
            visibility="shown_in_assignment_contract",
            start=0,
            end=len(text),
            quote=text,
        )
    require(
        source.content.get("scene_id") == scene_id
        and source.content.get("revision_number") == view.content.get("revision_number")
    )
    prose = string_value(source.content.get("prose"))
    catalog = catalog_v61(prose, source.version_id)
    serialized = [r.model_dump(mode="json") for r in catalog]
    shown = view.content.get("evidence_catalog")
    require(shown is None or shown == serialized)
    shown_prose = view.content.get("prose")
    require(shown_prose is None or shown_prose == prose)
    cursor = 0
    selected: tuple[int, int, str] | None = None
    for row in catalog:
        start = prose.find(row.exact_excerpt, cursor)
        require(start >= cursor and not prose[cursor:start].strip())
        end = start + len(row.exact_excerpt)
        if row.evidence_ref == evidence_ref:
            selected = start, end, row.exact_excerpt
        cursor = end
    require(not prose[cursor:].strip() and selected is not None)
    assert selected is not None
    visibility: Literal["shown_in_catalog", "shown_in_full_prose", "recovered_after_review"] = (
        "shown_in_catalog"
        if shown is not None
        else "shown_in_full_prose"
        if shown_prose is not None
        else "recovered_after_review"
    )
    return SourceSpan(
        **base,
        field_sha256=text_hash(prose),
        catalog_sha256=canonical_sha256(serialized),
        visibility=visibility,
        start=selected[0],
        end=selected[1],
        quote=selected[2],
    )


class LiteralComparison(Record):
    left: SourceSpan
    right: SourceSpan
    status: Literal["exact", "different", "unavailable"]
    statement: str


def compare_spans(left: SourceSpan, right: SourceSpan) -> LiteralComparison:
    require(left.project_id == right.project_id and left.scene_id == right.scene_id)
    status: Literal["exact", "different", "unavailable"] = (
        "unavailable"
        if left.quote is None or right.quote is None
        else "exact"
        if left.quote == right.quote
        else "different"
    )
    label = (
        "Assigned requirement → selected current-draft excerpt"
        if left.field_pointer != "/prose"
        else "Original draft excerpt → selected revision excerpt"
    )
    finding = {
        "exact": "The selected text spans are identical character for character.",
        "different": "The selected text spans differ.",
        "unavailable": "A selected source is unavailable; text identity is not determined.",
    }[status]
    return LiteralComparison(
        left=left, right=right, status=status, statement=label + ": " + finding
    )


class RequirementEvidence(Record):
    anchor: Anchor
    assignment_contract_sha256: Digest
    original_check: NativeAssignmentCheck
    comparisons: tuple[LiteralComparison, ...]
    selection_origin: Literal["saved_native_handles"] = "saved_native_handles"
    semantic_judgment: Literal["unchanged_not_reassessed"] = "unchanged_not_reassessed"
    aggregate_equality: None = None


def project_review(snapshot: ReviewSnapshot) -> tuple[RequirementEvidence, ...]:
    """All-or-nothing provenance validation; no partial salvage of a malformed review."""
    require(tuple(m.role for m in snapshot.messages) == ("system", "user"))
    require(
        messages_hash(snapshot.messages) == snapshot.invocation.prompt_sha256, "unavailable_view"
    )
    payload = strict_object(snapshot.messages[1].content)
    raw_views = payload.get("input_artifacts")
    require(isinstance(raw_views, list), "malformed_source")
    assert isinstance(raw_views, list)
    views = tuple(ArtifactView.model_validate_json(json.dumps(v)) for v in raw_views)
    by_view = {v.artifact_version_id: v for v in views}
    sources = {s.version_id: s for s in snapshot.sources}
    require(len(by_view) == len(views) and len(sources) == len(snapshot.sources))
    require(set(by_view) == set(sources), "missing_source")
    for source in (*snapshot.sources, snapshot.critique):
        require(source.project_id == snapshot.invocation.project_id)
        require(source.content is None or canonical_sha256(source.content) == source.content_sha256)
    for source in snapshot.sources:
        view = by_view[source.version_id]
        require(
            (view.artifact_kind, view.artifact_key) == (source.artifact_kind, source.artifact_key)
        )
    draft = sources.get(snapshot.draft_version_id)
    plan = sources.get(snapshot.plan_version_id)
    require(draft is not None and plan is not None, "missing_source")
    assert draft is not None and plan is not None
    require(
        draft.content is not None
        and plan.content is not None
        and snapshot.critique.content is not None,
        "missing_source",
    )
    assert (
        draft.content is not None
        and plan.content is not None
        and snapshot.critique.content is not None
    )
    require(
        draft.artifact_kind == "scene_draft"
        and draft.artifact_key == "scene_draft_" + snapshot.scene_id
        and draft.content.get("scene_id") == snapshot.scene_id
        and plan.artifact_kind == "scene_plan"
        and plan.artifact_key == "scene_plan_" + snapshot.scene_id
        and plan.content.get("id") == snapshot.scene_id
    )
    require(
        snapshot.critique.artifact_kind == "critique"
        and snapshot.critique.artifact_key == "critique_" + snapshot.scene_id
    )
    require(
        snapshot.critique.content.get("target_artifact_version_id") == draft.version_id
        and snapshot.critique.content.get("target_artifact_key") == draft.artifact_key
        and snapshot.critique.content.get("target_artifact_kind") == "scene_draft"
    )
    audit = snapshot.native_audit
    require(audit.get("schema_version") == "7", "unsupported_contract")
    require(
        audit.get("candidate_version_id") == draft.version_id
        and audit.get("current_plan_version_id") == plan.version_id
    )
    require(
        audit.get("repair_advice_origin") == "shared_finding_conditions"
        and isinstance(audit.get("assignment_repair_conditions"), list)
    )
    assignment = object_value(payload.get("scene_assignment_contract"))
    require(assignment.get("scene_id") == snapshot.scene_id)
    raw_checks = object_value(audit.get("assignment_checks"))
    anchors: tuple[Anchor, ...] = tuple(a for a in ANCHORS if plan.content.get(a))
    require(set(raw_checks) == set(anchors))
    revision = draft.content.get("revision_number")
    require(type(revision) is int)
    assert isinstance(revision, int)
    require(
        by_view[draft.version_id].content.get("evidence_catalog")
        == [
            r.model_dump(mode="json")
            for r in catalog_v61(string_value(draft.content.get("prose")), draft.version_id)
        ]
    )
    result = []
    for anchor in anchors:
        require(assignment.get(anchor) == plan.content.get(anchor))
        check = NativeAssignmentCheck.model_validate_json(json.dumps(raw_checks[anchor]))
        field: Literal["/turning_point", "/outcome"] = (
            "/turning_point" if anchor == "turning_point" else "/outcome"
        )
        left = resolve_span(
            plan,
            by_view[plan.version_id],
            scene_id=snapshot.scene_id,
            current_revision=revision,
            field=field,
            evidence_ref=None,
            current=True,
        )
        comparisons = tuple(
            compare_spans(
                left,
                resolve_span(
                    draft,
                    by_view[draft.version_id],
                    scene_id=snapshot.scene_id,
                    current_revision=revision,
                    field="/prose",
                    evidence_ref=ref,
                    current=True,
                ),
            )
            for ref in check.draft_evidence_refs
        )
        result.append(
            RequirementEvidence(
                anchor=anchor,
                assignment_contract_sha256=canonical_sha256(assignment),
                original_check=check,
                comparisons=comparisons,
            )
        )
    return tuple(result)


Reason = Literal[
    "compatible",
    "not_found",
    "not_successful_ordinary_critic",
    "unsupported_contract",
    "missing_source",
    "invalid_provenance",
    "unavailable_view",
    "malformed_source",
]


class ReviewExportEntry(Record):
    invocation_id: Identifier
    reason: Reason
    original_critique: ArtifactSource | None = None
    original_native_audit: JsonValue = None
    snapshot: ReviewSnapshot | None = None
    snapshot_sha256: Digest | None = None
    evidence: tuple[RequirementEvidence, ...] = ()
    original_revision_alignment: Literal["unresolved_not_selected"] = "unresolved_not_selected"
    writer_dispatch_authorized: Literal[False] = False


class ReviewEvidenceExport(Record):
    schema_version: Literal["1"] = "1"
    origin: Literal["application_computed_literal_evidence"] = (
        "application_computed_literal_evidence"
    )
    database_path: str
    invocation_ids: tuple[Identifier, ...] = Field(min_length=1, max_length=12)
    entries: tuple[ReviewExportEntry, ...]
    replayer_sha256: Digest
    comparison_rule: Literal["exact Unicode code points; selected spans only; no normalization"] = (
        COMPARISON_RULE
    )
    live_calls: Literal[0] = 0

    @model_validator(mode="after")
    def valid_selection(self) -> ReviewEvidenceExport:
        require(len(set(self.invocation_ids)) == len(self.invocation_ids))
        require(self.invocation_ids == tuple(e.invocation_id for e in self.entries))
        return self
