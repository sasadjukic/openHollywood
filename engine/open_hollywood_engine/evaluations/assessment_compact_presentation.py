"""Version-two diagnostic view with exact native reconstruction; no provider or I/O."""

from __future__ import annotations

import json
from typing import Literal

from pydantic import Field, JsonValue

from open_hollywood_engine.evaluations.assessment_completion import (
    CompletionContext,
    SourcePin,
    encoded,
)
from open_hollywood_engine.evaluations.assessment_presentation import (
    SYSTEM as ORIGINAL_SYSTEM,
)
from open_hollywood_engine.evaluations.assessment_presentation import (
    AssessmentPresentation,
    render_presentation,
)
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceRegistry,
    _field,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentWork,
    ContextDocument,
    Name,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    SavedMessage,
    object_value,
    require,
    strict_object,
    string_value,
    text_hash,
)

MAX_BYTES = 16 * 1024 * 1024
PROVENANCE_ID = "operator-provenance-not-visible-authority"
NOTICE = (
    "Complete source documents, original messages, whole review, scope, briefs and all field "
    "dispositions are visible. Only the operator-provenance document body is retained locally, "
    "bound by its original identity/version/hash. It is unavailable to this assessment and is "
    "not story authority. Historical model_input labels describe earlier roles, not current "
    "visibility. Do not infer local archive contents or historical visibility from metadata."
)
SYSTEM = ORIGINAL_SYSTEM + (
    " This is diagnostic presentation version 2. native_work_view is a presentation of the "
    "unchanged native work, not a new native work. Each structured_content object is a complete "
    "source or review document. The registry's whole_field_locations rows have columns ref, "
    "document_id, field_pointer. Match document_id to the visible document identity and follow "
    "the JSON Pointer: ~1 means /, ~0 means ~, and array indices start at zero. Read the entire "
    "referenced string field and its surrounding document; the application derives its exact "
    "quote, hash and full-field offsets. Distinct IDs remain distinct locations even when text "
    "matches. A location is not a support judgment or a substitute for complete evidence. "
    "The local_only operator-provenance body is not included; do not request it or treat its "
    "hash as evidence. Assess only the declared active claims using supplied visible authority."
)


class LocalProvenance(Record):
    contract: Literal["assessment-local-provenance-2"]
    source: SourcePin
    document: ContextDocument
    original_availability_notice: str
    model_input: Literal[False]


class CompactPresentation(Record):
    contract: Literal["assessment-intake-presentation-2"]
    source: SourcePin
    batch_id: Name
    active_unit_ids: tuple[Name, ...] = Field(min_length=1, max_length=12)
    messages: tuple[SavedMessage, SavedMessage]
    messages_canonical_sha256: Digest
    response_schema: JsonObject
    schema_canonical_sha256: Digest
    original_packet_bytes_sha256: Digest
    local_provenance_canonical_sha256: Digest
    production_prompt_changed: Literal[False]
    live_authorized: Literal[False]


class CompactBundle(Record):
    contract: Literal["assessment-compact-bundle-2"]
    presentation: CompactPresentation
    local_provenance: LocalProvenance


def compact(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def _source_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def _array(value: JsonValue) -> list[JsonValue]:
    require(isinstance(value, list), "compact_array")
    assert isinstance(value, list)
    return value


def _documents(packet: JsonObject) -> list[JsonValue]:
    return _array(object_value(object_value(packet["native_work_view"])["context"])["documents"])


def parse_bundle(data: bytes) -> CompactBundle:
    require(len(data) <= MAX_BYTES, "compact_bundle_size")
    return CompactBundle.model_validate_json(encoded(strict_object(data.decode("utf-8"))))


def reconstruct(bundle: CompactBundle) -> AssessmentPresentation:
    """Prove local consistency; callers must validate against an authenticated context too."""
    bundle = parse_bundle(encoded(bundle.model_dump(mode="json")))
    p, local = bundle.presentation, bundle.local_provenance
    require(p.source == local.source, "compact_source_pin")
    require(
        canonical_sha256(local.model_dump(mode="json")) == p.local_provenance_canonical_sha256,
        "compact_local_digest",
    )
    require(
        local.document.identity == PROVENANCE_ID and local.document.kind == "scope",
        "compact_provenance_kind",
    )
    require(tuple(m.role for m in p.messages) == ("system", "user"), "compact_message_roles")
    require(p.messages[0].content == SYSTEM, "compact_system")
    require(
        canonical_sha256([m.model_dump(mode="json") for m in p.messages])
        == p.messages_canonical_sha256,
        "compact_message_digest",
    )
    require(
        canonical_sha256(p.response_schema) == p.schema_canonical_sha256, "compact_schema_digest"
    )
    packet = strict_object(p.messages[1].content)
    require(
        packet["contract"] == "assessment-intake-packet-2"
        and packet["availability_notice"] == NOTICE,
        "compact_packet_contract",
    )
    require(
        packet["source"] == p.source.model_dump(mode="json")
        and packet["batch_id"] == p.batch_id
        and packet["active_unit_ids"] == list(p.active_unit_ids),
        "compact_packet_scope",
    )
    documents = [object_value(d) for d in _documents(packet)]
    require(
        len({string_value(d["identity"]) for d in documents}) == len(documents),
        "compact_duplicate_document",
    )
    sources: dict[str, ContextDocument] = {}
    registry_view: JsonObject | None = None
    local_count = 0
    for document in documents:
        kind = document["kind"]
        if kind in ("source", "report"):
            content = document.pop("structured_content")
            require(isinstance(content, dict), "compact_document_object")
            document["content_json"] = _source_text(content)
            restored = ContextDocument.model_validate_json(encoded(document))
            if kind == "source":
                sources[restored.identity] = restored
        elif kind == "registry":
            require(registry_view is None, "compact_multiple_registries")
            registry_view = document
        else:
            require(
                kind == "scope" and document["identity"] == PROVENANCE_ID,
                "compact_unqualified_document",
            )
            require(document.pop("local_only") is True, "compact_local_visibility")
            document["content_json"] = local.document.content_json
            require(document == local.document.model_dump(mode="json"), "compact_local_binding")
            local_count += 1
    require(local_count == 1 and registry_view is not None, "compact_document_coverage")
    assert registry_view is not None
    require(
        registry_view.pop("columns") == ["ref", "document_id", "field_pointer"],
        "compact_location_columns",
    )
    entries: list[JsonObject] = []
    parsed = {key: strict_object(d.content_json) for key, d in sources.items()}
    for value in _array(registry_view.pop("whole_field_locations")):
        row = _array(value)
        require(len(row) == 3, "compact_location_width")
        ref, identity, pointer = (string_value(v) for v in row)
        require(identity in sources, "compact_unavailable_source")
        source_document = sources[identity]
        quote = _field(parsed[identity], pointer)
        entries.append(
            {
                "ref": ref,
                "document_id": identity,
                "document_version": source_document.version,
                "document_sha256": source_document.content_sha256,
                "field_pointer": pointer,
                "field_sha256": text_hash(quote),
                "start": 0,
                "end": len(quote),
                "quote": quote,
                "paragraph": None,
            }
        )
    registry = EvidenceRegistry.model_validate_json(
        encoded({"contract": "assessment-evidence-registry-1", "entries": entries})
    )
    registry_view["content_json"] = _source_text(registry.model_dump(mode="json"))
    ContextDocument.model_validate_json(encoded(registry_view))
    view = object_value(packet.pop("native_work_view"))
    object_value(view["context"])["documents"] = [dict(d) for d in documents]
    work = AssessmentWork.model_validate_json(encoded(view))
    require(work.fingerprint == p.source.work_canonical_sha256, "compact_native_work")
    scope = scope_for_batch(work, p.batch_id, "0" * 64)
    require(scope.active_unit_ids == p.active_unit_ids, "compact_active_units")
    packet["full_original_work"] = view
    packet["contract"] = "assessment-intake-packet-1"
    packet["availability_notice"] = local.original_availability_notice
    original_user = encoded(packet).decode()
    require(
        text_hash(original_user) == p.original_packet_bytes_sha256, "compact_packet_reconstruction"
    )
    messages = (
        SavedMessage(role="system", content=ORIGINAL_SYSTEM),
        SavedMessage(role="user", content=original_user),
    )
    return AssessmentPresentation(
        contract="assessment-intake-presentation-1",
        source=p.source,
        batch_id=p.batch_id,
        active_unit_ids=p.active_unit_ids,
        messages=messages,
        messages_canonical_sha256=canonical_sha256([m.model_dump(mode="json") for m in messages]),
        response_schema=p.response_schema,
        schema_canonical_sha256=p.schema_canonical_sha256,
        production_prompt_changed=False,
    )


def render_compact(context: CompletionContext, batch_id: str) -> CompactBundle:
    original = render_presentation(context, batch_id)
    packet = strict_object(original.messages[1].content)
    packet["native_work_view"] = packet.pop("full_original_work")
    packet["contract"] = "assessment-intake-packet-2"
    old_notice = string_value(packet["availability_notice"])
    packet["availability_notice"] = NOTICE
    local: LocalProvenance | None = None
    for item in _documents(packet):
        value = object_value(item)
        document = ContextDocument.model_validate_json(encoded(value))
        content = strict_object(document.content_json)
        require(_source_text(content) == document.content_json, "compact_document_serialization")
        value.pop("content_json")
        if document.kind == "registry":
            registry = EvidenceRegistry.model_validate_json(document.content_json)
            require(
                all(
                    e.start == 0 and e.end == len(e.quote) and e.paragraph is None
                    for e in registry.entries
                ),
                "compact_whole_fields_only",
            )
            value["columns"] = ["ref", "document_id", "field_pointer"]
            value["whole_field_locations"] = [
                [e.ref, e.document_id, e.field_pointer] for e in registry.entries
            ]
        elif document.kind == "scope":
            require(
                document.identity == PROVENANCE_ID and local is None,
                "compact_unqualified_provenance",
            )
            local = LocalProvenance(
                contract="assessment-local-provenance-2",
                source=context.pin,
                document=document,
                original_availability_notice=old_notice,
                model_input=False,
            )
            value["local_only"] = True
        else:
            value["structured_content"] = content
    require(local is not None, "compact_missing_provenance")
    assert local is not None
    messages = (
        SavedMessage(role="system", content=SYSTEM),
        SavedMessage(role="user", content=compact(packet)),
    )
    p = CompactPresentation(
        contract="assessment-intake-presentation-2",
        source=context.pin,
        batch_id=batch_id,
        active_unit_ids=original.active_unit_ids,
        messages=messages,
        messages_canonical_sha256=canonical_sha256([m.model_dump(mode="json") for m in messages]),
        response_schema=original.response_schema,
        schema_canonical_sha256=original.schema_canonical_sha256,
        original_packet_bytes_sha256=text_hash(original.messages[1].content),
        local_provenance_canonical_sha256=canonical_sha256(local.model_dump(mode="json")),
        production_prompt_changed=False,
        live_authorized=False,
    )
    result = CompactBundle(
        contract="assessment-compact-bundle-2", presentation=p, local_provenance=local
    )
    require(reconstruct(result) == original, "compact_reconstruction_changed")
    return result


def validate_compact(context: CompletionContext, candidate: CompactBundle) -> CompactBundle:
    candidate = parse_bundle(encoded(candidate.model_dump(mode="json")))
    reconstruct(candidate)
    expected = render_compact(context, candidate.presentation.batch_id)
    require(candidate == expected, "compact_authenticated_context_mismatch")
    return candidate
