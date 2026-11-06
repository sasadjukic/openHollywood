"""Scope-bound previews keep fulfillment, obligation and repair authority separate."""

from __future__ import annotations

import json
import socket
import sqlite3
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_claim_scope import ClaimScopeDeclarations
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceLocation,
    EvidenceRegistry,
    assessment_response_schema,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentContext,
    AssessmentReceipt,
    AssessmentWork,
    ContextDocument,
    ReportField,
    SelectedStatement,
    complete_work,
    partition_work,
)
from open_hollywood_engine.evaluations.assessment_work_brief import (
    AssessmentWorkBriefs,
    preview_work_briefs,
    render_work_briefs,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    EvidenceError,
    SavedMessage,
    text_hash,
)
from pydantic import ValidationError


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("No network or database access in brief previews")

    for owner, name in (
        (httpx.Client, "request"),
        (httpx.AsyncClient, "request"),
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "getaddrinfo"),
        (socket, "create_connection"),
        (sqlite3, "connect"),
    ):
        monkeypatch.setattr(owner, name, deny)


def document(identity: str, kind: Any, content: dict[str, Any]) -> ContextDocument:
    raw = json.dumps(content, ensure_ascii=False)
    return ContextDocument(
        identity=identity, version="v1", kind=kind, content_json=raw, content_sha256=text_hash(raw)
    )


@pytest.fixture
def work() -> AssessmentWork:
    source = document(
        "source",
        "source",
        {"assignment": "Nia must decide to compare the keys.", "prose": "Nia compares both keys."},
    )
    fields = (
        ReportField(field_id="F1", pointer="/claims/0", text="Nia must decide to compare keys."),
        ReportField(field_id="F2", pointer="/claims/1", text="Nia compares the keys."),
        ReportField(field_id="F3", pointer="/claims/2", text="Nia must compare again. ``` Ω"),
    )
    entries = tuple(
        EvidenceLocation(
            ref=ref,
            document_id=source.identity,
            document_version=source.version,
            document_sha256=source.content_sha256,
            field_pointer="/" + key,
            field_sha256=text_hash(value),
            start=0,
            end=len(value),
            quote=value,
        )
        for (key, value), ref in zip(
            json.loads(source.content_json).items(), ("A", "D"), strict=True
        )
    )
    docs = (
        source,
        document("report", "report", {"claims": [f.text for f in fields]}),
        document("registry", "registry", EvidenceRegistry(entries=entries).model_dump(mode="json")),
    )
    return partition_work(
        AssessmentContext(
            provenance="synthetic_fixture",
            origin_sha256="a" * 64,
            documents=docs,
            report_fields=fields,
            statements=tuple(
                SelectedStatement(
                    unit_id=f"Q{i}", field_id=f.field_id, start=0, end=len(f.text), quote=f.text
                )
                for i, f in enumerate(fields, 1)
            ),
            messages=(SavedMessage(role="user", content="Full fixture: " + str(docs)),),
        ),
        3,
    )


def declarations(work: AssessmentWork) -> ClaimScopeDeclarations:
    return ClaimScopeDeclarations.model_validate_json(
        json.dumps(
            {
                "work_sha256": work.fingerprint,
                "authored_by": "Synthetic fixture author",
                "declarations": [
                    {
                        "statement": s.model_dump(mode="json"),
                        "field_pointer": f.pointer,
                        "claim_predicates": [predicate],
                        "evidence_predicates": [predicate],
                        "material_components": [
                            {"description": s.quote, "addressed_by_evidence_contract": i != 2}
                        ],
                        "unresolved_qualifiers": ["Further repair necessity"] if i == 2 else [],
                        "source_scopes": [{"role": role, "evidence_refs": [ref]}],
                        "evidence_requirement": "Assess the whole selected question separately.",
                        "whole_claim_reviewed": True,
                        "observation_basis": "not_applicable",
                    }
                    for i, (s, f, predicate, role, ref) in enumerate(
                        zip(
                            work.context.statements,
                            work.context.report_fields,
                            ("assignment_obligation", "observed_choice", "editorial_effect"),
                            ("assignment", "draft", "draft"),
                            ("A", "D", "D"),
                            strict=True,
                        )
                    )
                ],
            }
        )
    )


def briefs(work: AssessmentWork, packet: ClaimScopeDeclarations) -> AssessmentWorkBriefs:
    return AssessmentWorkBriefs.model_validate_json(
        json.dumps(
            {
                "work_sha256": work.fingerprint,
                "declarations_sha256": canonical_sha256(packet.model_dump(mode="json")),
                "authored_by": "Synthetic fixture author",
                "briefs": [
                    {
                        "unit_id": s.unit_id,
                        "question": question,
                        "temporal_scope": "Current scene",
                        "source_authority": authority,
                        "evidence_obligation": "Do not substitute a different question.",
                    }
                    for s, question, authority in zip(
                        work.context.statements,
                        ("Is this required?", "Does this happen?", "Is another repair necessary?"),
                        ("Current assignment", "Current draft", "Unqualified editorial judgment"),
                        strict=True,
                    )
                ],
            }
        )
    )


def unpack(rendered: str) -> dict[str, Any]:
    fence = rendered.split("json\n")[0].splitlines()[-1]
    result: dict[str, Any] = json.loads(
        rendered.split(fence + "json\n")[1].rsplit("\n" + fence, 1)[0]
    )
    return result


def test_read_only_preview_preserves_context_and_unresolved_repair(work: AssessmentWork) -> None:
    packet = declarations(work)
    scope = scope_for_batch(work, "batch-001", "b" * 64)
    schema = assessment_response_schema(work, scope)
    before = work.model_dump_json()
    rendered = render_work_briefs(work, scope, packet, briefs(work, packet))
    payload = unpack(rendered)
    assert payload["full_work"] == work.model_dump(mode="json")
    preview = payload["work_brief_preview"]
    assert [u["status"] for u in preview["units"]] == [
        "declared_consistent",
        "declared_consistent",
        "needs_scope_review",
    ]
    assert preview["obligation_existence"] == preview["observed_fulfillment"] == "unassessed"
    assert preview["edit_necessity"] == "unassessed" and not preview["model_input"]
    assert not preview["writer_dispatch_authorized"] and not preview["brief_neutrality_verified"]
    assert "````json" in rendered and "Ω" in rendered
    assert schema == assessment_response_schema(work, scope) and work.model_dump_json() == before


@pytest.mark.parametrize("missing", ["brief", "declaration", "both"])
def test_missing_information_is_visible_not_completed(work: AssessmentWork, missing: str) -> None:
    packet = declarations(work)
    if missing != "brief":
        packet = packet.model_copy(update={"declarations": packet.declarations[1:]})
    authored = briefs(work, packet)
    if missing != "declaration":
        authored = authored.model_copy(update={"briefs": authored.briefs[1:]})
    result = preview_work_briefs(
        work, scope_for_batch(work, "batch-001", "b" * 64), packet, authored
    )
    assert len(result.units) == 3 and result.units[0].status == "needs_scope_review"
    assert ("missing_work_brief" in result.units[0].issues) == (missing != "declaration")
    assert ("missing_claim_declaration" in result.units[0].issues) == (missing != "brief")


@pytest.mark.parametrize(
    "mutation",
    ["work", "declarations", "duplicate", "unknown", "blank", "extra", "model_input", "writer"],
)
def test_bad_binding_and_unsupported_authority_rejected(
    work: AssessmentWork, mutation: str
) -> None:
    packet = declarations(work)
    value = briefs(work, packet).model_dump(mode="json")
    if mutation in ("work", "declarations"):
        value[mutation + "_sha256"] = "0" * 64
    elif mutation == "duplicate":
        value["briefs"].append(value["briefs"][0])
    elif mutation == "unknown":
        value["briefs"][-1]["unit_id"] = "foreign"
    elif mutation == "blank":
        value["briefs"][0]["temporal_scope"] = " "
    elif mutation == "extra":
        value["briefs"][0]["expected_support"] = "supported"
    else:
        value["model_input" if mutation == "model_input" else "writer_dispatch_authorized"] = True
    with pytest.raises((EvidenceError, ValidationError)):
        preview_work_briefs(
            work,
            scope_for_batch(work, "batch-001", "b" * 64),
            packet,
            AssessmentWorkBriefs.model_construct(**value),
        )


def test_declared_consistency_cannot_prove_free_text_interpretation(work: AssessmentWork) -> None:
    packet = declarations(work)
    value = briefs(work, packet).model_dump(mode="json")
    value["briefs"][0]["question"] = "Is further repair necessary?"
    authored = AssessmentWorkBriefs.model_validate_json(json.dumps(value))
    result = preview_work_briefs(
        work, scope_for_batch(work, "batch-001", "b" * 64), packet, authored
    )
    assert result.units[0].status == "declared_consistent"
    assert not result.semantic_interpretation_verified and not result.brief_neutrality_verified
    assert result.edit_necessity == "unassessed"


def test_scope_change_stales_brief_and_caller_aliases_are_detached(work: AssessmentWork) -> None:
    packet = declarations(work)
    authored = briefs(work, packet)
    scope = scope_for_batch(work, "batch-001", "b" * 64)
    with pytest.raises(EvidenceError, match="declarations_mismatch"):
        preview_work_briefs(
            work, scope, packet.model_copy(update={"authored_by": "Other"}), authored
        )
    mutable = list(authored.briefs)
    result = preview_work_briefs(
        work, scope, packet, authored.model_copy(update={"briefs": mutable})
    )
    mutable.clear()
    assert len(result.authored_briefs.briefs) == 3


@pytest.mark.parametrize("label", ["supported", "unsupported", "uncertain"])
def test_bound_model_labels_never_become_repair_or_writer_authority(
    work: AssessmentWork, label: str
) -> None:
    packet = declarations(work)
    scope = scope_for_batch(work, "batch-001", "b" * 64)
    raw = json.dumps(
        {
            "assessments": {
                u: {
                    "support": label,
                    "evidence": ["A", "D"],
                    "reason": "A synthetic fallible judgment.",
                }
                for u in scope.active_unit_ids
            }
        }
    )
    receipt = AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=scope.request_sha256,
        attempt_id="synthetic",
        status="valid",
        result_sha256=text_hash(raw),
        assessed_unit_ids=scope.active_unit_ids,
        active_seconds=1,
    )
    payload = unpack(
        render_work_briefs(
            work, scope, packet, briefs(work, packet), receipt=receipt, raw_final=raw
        )
    )
    assert payload["bound_result"]["raw_final"] == raw
    result = bind_assessment_result(work, scope, receipt, raw)
    completed = complete_work(work, (result.receipt,), {scope.batch_id: scope.request_sha256})
    assert completed.complete_delivery and completed.binding == "complete"
    assert completed.support == completed.edit_necessity == completed.craft == "unassessed"
    assert completed.unknown_usage_attempts == 1 and not completed.writer_dispatch_authorized
    assert payload["work_brief_preview"]["units"][2]["status"] == "needs_scope_review"


@pytest.mark.parametrize("bad", ["receipt_only", "raw_only", "failed", "scope", "stale_raw"])
def test_renderer_cannot_launder_bad_results(work: AssessmentWork, bad: str) -> None:
    scope = scope_for_batch(work, "batch-001", "b" * 64)
    packet = declarations(work)
    receipt = AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=scope.request_sha256,
        attempt_id="bad",
        status="transport_error",
        active_seconds=1,
    )
    kwargs: dict[str, Any] = {"receipt": receipt, "raw_final": "{}"}
    if bad == "receipt_only":
        kwargs.pop("raw_final")
    elif bad == "raw_only":
        kwargs.pop("receipt")
    elif bad == "scope":
        scope = scope.model_copy(update={"active_unit_ids": ("Q1",)})
    elif bad == "stale_raw":
        kwargs["receipt"] = receipt.model_copy(
            update={
                "status": "valid",
                "result_sha256": "0" * 64,
                "assessed_unit_ids": scope.active_unit_ids,
            }
        )
    with pytest.raises((EvidenceError, ValidationError)):
        render_work_briefs(work, scope, packet, briefs(work, packet), **kwargs)


def test_inactive_briefs_validated_and_missing_batch_keeps_completion_incomplete(
    work: AssessmentWork,
) -> None:
    work = partition_work(work.context, 2)
    packet = declarations(work)
    authored = briefs(work, packet)
    scope = scope_for_batch(work, "batch-001", "b" * 64)
    assert len(preview_work_briefs(work, scope, packet, authored).units) == 2
    value = authored.model_dump(mode="json")
    value["briefs"][-1]["unit_id"] = "foreign-inactive"
    with pytest.raises(EvidenceError, match="unknown_work_brief"):
        preview_work_briefs(
            work, scope, packet, AssessmentWorkBriefs.model_validate_json(json.dumps(value))
        )
    completion = complete_work(work, (), {b.batch_id: "b" * 64 for b in work.batches})
    assert not completion.complete_delivery and completion.expected_units == 3
