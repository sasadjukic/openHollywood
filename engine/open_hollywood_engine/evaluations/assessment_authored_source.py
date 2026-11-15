"""Explicit authored sources and fixture completion, separate from saved model reviews."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from open_hollywood_engine.evaluations.assessment_authority import (
    AssessmentAuthority,
    preview_assessment_authority,
    render_assessment_authority,
)
from open_hollywood_engine.evaluations.assessment_claim_scope import ClaimScopeDeclarations
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_presentation import SYSTEM
from open_hollywood_engine.evaluations.assessment_result import (
    AssessmentScope,
    assessment_response_schema,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentReceipt,
    AssessmentWork,
    ContextDocument,
    Name,
    complete_work,
)
from open_hollywood_engine.evaluations.assessment_work_brief import AssessmentWorkBriefs
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    SavedMessage,
    require,
    strict_object,
    text_hash,
)

ORIGIN = "assistant_authored_fictional_control_not_model_output_or_independent_human_gold"
Family = Literal["F01", "F02", "F03"]
NOTICE = (
    "Source origin: registered authored diagnostic controls. Delivery origin: authored fixture "
    "only when a fixture is supplied. No model delivery, independent human gold or billing. "
    "Mechanical binding does not verify support, evidence adequacy, edit necessity or craft. "
    "Live calls paused; writer permission false; canary on hold."
)


class AuthoredSourcePin(Record):
    source_origin: Literal["authored_diagnostic"]
    source_id: Name
    family: Family
    manifest_bytes_sha256: Digest
    # Safe input members only; operator gold remains outside this domain object.
    input_members_sha256: dict[str, Digest]


class AuthoredSource(Record):
    contract: Literal["assessment-authored-source-1"]
    source: AuthoredSourcePin
    work: AssessmentWork
    original_scope: AssessmentScope
    declarations: ClaimScopeDeclarations
    briefs: AssessmentWorkBriefs
    authority: AssessmentAuthority
    source_packet: JsonObject
    result: None = None
    receipt: None = None
    support: Literal["unassessed"] = "unassessed"
    writer_dispatch_authorized: Literal[False] = False


class AuthoredPresentation(Record):
    contract: Literal["assessment-authored-source-presentation-1"]
    source: AuthoredSourcePin
    batch_id: Name
    active_unit_ids: tuple[Name, ...]
    messages: tuple[SavedMessage, SavedMessage]
    messages_canonical_sha256: Digest
    response_schema: JsonObject
    schema_canonical_sha256: Digest
    production_prompt_changed: Literal[False] = False
    live_execution_authorized: Literal[False] = False


class AuthoredSourceSubmission(Record):
    contract: Literal["assessment-authored-source-fixture-1"]
    source: AuthoredSourcePin
    delivery_origin: Literal["authored_fixture"]
    authored_by: str = Field(min_length=1, max_length=1000, pattern=r"\S")
    fixture_id: Name
    presentation_canonical_sha256: Digest
    raw_final: str = Field(min_length=1, max_length=64_000)


def _document(
    identity: str, kind: Literal["source", "report", "registry"], value: object
) -> ContextDocument:
    raw = encoded(value).decode()
    return ContextDocument(
        identity=identity, version="v1", kind=kind, content_json=raw, content_sha256=text_hash(raw)
    )


def validate_source(source: AuthoredSource) -> AuthoredSource:
    """Recompute native bindings; archive authentication belongs to the registered adapter."""
    source = AuthoredSource.model_validate_json(source.model_dump_json())
    bound_members = {
        "work.json": source.work.model_dump(mode="json"),
        "scope.json": source.original_scope.model_dump(mode="json"),
        "declarations.json": source.declarations.model_dump(mode="json"),
        "briefs.json": source.briefs.model_dump(mode="json"),
        "authority.json": source.authority.model_dump(mode="json"),
        "source-packet.json": source.source_packet,
    }
    require(
        source.source.input_members_sha256
        == {name: text_hash(encoded(value).decode()) for name, value in bound_members.items()},
        "authored_input_binding",
    )
    work, packet, family = source.work, source.source_packet, source.source.family
    require(
        set(packet) == {"source_manifest", "sources", "whole_authored_review", "evidence_registry"},
        "authored_packet_shape",
    )
    ledger = strict_object(encoded(packet["source_manifest"]).decode())
    require(ledger.get("origin") == ORIGIN and ledger.get("family") == family, "authored_origin")
    require(
        ledger.get("source_authentication") == "authored_local_construction_only"
        and ledger.get("historical_model_visibility") == "not_applicable_no_model_review",
        "authored_visibility",
    )
    sources = packet["sources"]
    require(isinstance(sources, list), "authored_sources")
    assert isinstance(sources, list)
    documents = tuple(ContextDocument.model_validate_json(encoded(d)) for d in sources)
    expected = (
        *documents,
        _document(family + "-manifest", "source", ledger),
        _document(family + "-report", "report", packet["whole_authored_review"]),
        _document(family + "-registry", "registry", packet["evidence_registry"]),
    )
    require(work.context.provenance == "synthetic_fixture", "authored_work_origin")
    require(work.context.documents == expected, "authored_full_context")
    require(
        work.context.messages == (SavedMessage(role="user", content=encoded(packet).decode()),),
        "authored_original_messages",
    )
    identity = canonical_sha256(packet)
    require(work.context.origin_sha256 == identity, "authored_packet_binding")
    require(len(work.batches) == 1 and len(work.context.statements) == 3, "authored_work_bound")
    fields = {f.field_id: f for f in work.context.report_fields}
    require(len(fields) == 4, "authored_field_coverage")
    for statement in work.context.statements:
        field = fields[statement.field_id]
        require(
            statement.unit_id == field.field_id
            and statement.start == 0
            and statement.end == len(field.text)
            and statement.quote == field.text,
            "authored_whole_field",
        )
    scope = scope_for_batch(work, work.batches[0].batch_id, identity)
    require(source.original_scope == scope, "authored_original_scope")
    require(source.authority.origin_sha256 == identity, "authored_authority_origin")
    preview = preview_assessment_authority(
        work, scope, source.declarations, source.briefs, source.authority
    )
    require(all(u.status == "declared_consistent" for u in preview.units), "authored_scope")
    require(all(b.status == "exact_copy" for b in preview.historical_bindings), "authored_history")
    return source


def dispositions(source: AuthoredSource) -> list[JsonObject]:
    active = {s.field_id for s in source.work.context.statements}
    return [
        {
            "field_id": f.field_id,
            "pointer": f.pointer,
            "text": f.text,
            "disposition": "active_whole_factual_claim"
            if f.field_id in active
            else "unselected_context",
        }
        for f in source.work.context.report_fields
    ]


def render_presentation(source: AuthoredSource) -> AuthoredPresentation:
    source = validate_source(source)
    scope = source.original_scope
    packet = {
        "contract": "assessment-authored-source-packet-1",
        "source": source.source.model_dump(mode="json"),
        "batch_id": scope.batch_id,
        "active_unit_ids": list(scope.active_unit_ids),
        "full_original_work": source.work.model_dump(mode="json"),
        "original_scope_declarations": source.declarations.model_dump(mode="json"),
        "original_work_briefs": source.briefs.model_dump(mode="json"),
        "original_authored_authority": source.authority.model_dump(mode="json"),
        "whole_field_dispositions": dispositions(source),
        "availability_notice": (
            "This new diagnostic presentation explicitly supplies all of these authored records. "
            "Original model_input=false labels and local scope hashes describe prior local "
            "construction, not provider requests or historical critic visibility. No gold is "
            "supplied. Missing bodies remain missing. Source origin remains authored_diagnostic."
        ),
    }
    messages = (
        SavedMessage(role="system", content=SYSTEM),
        SavedMessage(role="user", content=encoded(packet).decode()),
    )
    schema = strict_object(encoded(assessment_response_schema(source.work, scope)).decode())
    return AuthoredPresentation(
        contract="assessment-authored-source-presentation-1",
        source=source.source,
        batch_id=scope.batch_id,
        active_unit_ids=scope.active_unit_ids,
        messages=messages,
        messages_canonical_sha256=canonical_sha256([m.model_dump(mode="json") for m in messages]),
        response_schema=schema,
        schema_canonical_sha256=canonical_sha256(schema),
    )


def fixture_template(source: AuthoredSource) -> JsonObject:
    presentation = render_presentation(source)
    return {
        "contract": "assessment-authored-source-fixture-1",
        "source": source.source.model_dump(mode="json"),
        "delivery_origin": "authored_fixture",
        "authored_by": "",
        "fixture_id": "local-fixture-001",
        "presentation_canonical_sha256": canonical_sha256(presentation.model_dump(mode="json")),
        "raw_final": "",
    }


def complete_fixture(
    source: AuthoredSource, submission: AuthoredSourceSubmission
) -> tuple[JsonObject, str]:
    source = validate_source(source)
    submission = AuthoredSourceSubmission.model_validate_json(submission.model_dump_json())
    presentation = render_presentation(source)
    presentation_sha = canonical_sha256(presentation.model_dump(mode="json"))
    require(submission.source == source.source, "authored_submission_source")
    require(submission.presentation_canonical_sha256 == presentation_sha, "authored_presentation")
    fixture_identity = canonical_sha256(
        {
            "contract": "assessment-authored-source-fixture-input-1",
            "source": source.source.model_dump(mode="json"),
            "presentation_canonical_sha256": presentation_sha,
        }
    )
    scope = scope_for_batch(source.work, presentation.batch_id, fixture_identity)
    receipt = AssessmentReceipt(
        work_sha256=source.work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=fixture_identity,
        attempt_id=submission.fixture_id,
        status="valid",
        result_sha256=text_hash(submission.raw_final),
        assessed_unit_ids=scope.active_unit_ids,
        active_seconds=0.0,
    )
    bound = bind_assessment_result(source.work, scope, receipt, submission.raw_final)
    completion = complete_work(source.work, (bound.receipt,), {scope.batch_id: fixture_identity})
    derived_authority = AssessmentAuthority.model_validate_json(
        encoded(
            {
                **source.authority.model_dump(mode="json"),
                "request_sha256": fixture_identity,
            }
        )
    )
    envelope: JsonObject = {
        "contract": "assessment-authored-source-completion-1",
        "source_origin": "authored_diagnostic",
        "delivery_origin": "authored_fixture",
        "notice": NOTICE,
        "source": source.model_dump(mode="json"),
        "submission": submission.model_dump(mode="json"),
        "presentation": presentation.model_dump(mode="json"),
        "fixture_input_identity_sha256": fixture_identity,
        "derived_fixture_authority": derived_authority.model_dump(mode="json"),
        "bound_result": bound.model_dump(mode="json"),
        "completion": completion.model_dump(mode="json"),
        "usage": {
            "provenance": "not_applicable_no_inference",
            "input_tokens": None,
            "output_tokens": None,
            "reasoning_tokens": None,
            "cached_input_tokens": None,
            "actual_billing": None,
            "native_null_usage_count_is_not_missing_provider_telemetry": True,
        },
        "publication_state": "bound_unassessed",
        "model_evidence": False,
        "live_calls": 0,
        "writer_dispatch_authorized": False,
    }
    view = render_assessment_authority(
        source.work,
        scope,
        source.declarations,
        source.briefs,
        derived_authority,
        receipt=receipt,
        raw_final=submission.raw_final,
    )
    return envelope, NOTICE + "\n\nProjection of `envelope.json`.\n\n" + view
