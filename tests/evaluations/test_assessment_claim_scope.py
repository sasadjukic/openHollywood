"""Read-only scope integration: authored semantics never become verified story truth."""

from __future__ import annotations

import json
import socket
import sqlite3
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_claim_scope import (
    ClaimScopeDeclaration,
    ClaimScopeDeclarations,
    audit_claim_scope,
    render_claim_scope,
)
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceLocation,
    EvidenceRegistry,
    assessment_response_schema,
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
from open_hollywood_engine.evaluations.review_evidence import (
    EvidenceError,
    SavedMessage,
    text_hash,
)
from pydantic import ValidationError


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("No provider or database access in the scope component")

    for owner, name in (
        (httpx.Client, "request"),
        (httpx.AsyncClient, "request"),
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "create_connection"),
        (socket, "getaddrinfo"),
        (sqlite3, "connect"),
    ):
        monkeypatch.setattr(owner, name, deny)


def doc(identity: str, kind: Any, content: dict[str, Any]) -> ContextDocument:
    raw = json.dumps(content, ensure_ascii=False, sort_keys=True)
    return ContextDocument(
        identity=identity, version="v1", kind=kind, content_json=raw, content_sha256=text_hash(raw)
    )


@pytest.fixture
def work() -> AssessmentWork:
    prose = "Nia 🔑 turns the key.\r\n\r\nThe drawer opens before she counts.\r\n\r\nNia leaves."
    draft = doc("draft", "source", {"prose": prose})
    assignment = doc("assignment", "source", {"outcome": "Nia may investigate; it is optional."})
    locations = []
    start = 0
    for i, paragraph in enumerate(prose.split("\r\n\r\n"), 1):
        locations.append(
            EvidenceLocation(
                ref=f"D{i}",
                document_id=draft.identity,
                document_version=draft.version,
                document_sha256=draft.content_sha256,
                field_pointer="/prose",
                field_sha256=text_hash(prose),
                start=start,
                end=start + len(paragraph),
                quote=paragraph,
                paragraph=i,
            )
        )
        start += len(paragraph) + 4
    text = json.loads(assignment.content_json)["outcome"]
    locations.append(
        EvidenceLocation(
            ref="A1",
            document_id=assignment.identity,
            document_version=assignment.version,
            document_sha256=assignment.content_sha256,
            field_pointer="/outcome",
            field_sha256=text_hash(text),
            start=0,
            end=len(text),
            quote=text,
        )
    )
    claims = [
        "The assignment requires Nia to investigate.",
        "Nia opens the drawer by counting.",
        "A continuation resolves the conflict.",
    ]
    full = "Context before. " + claims[1] + " Context after. ``` <script>data</script>"
    report = doc("report", "report", {"claims": [claims[0], full, claims[2]]})
    fields = tuple(
        ReportField(field_id=f"F{i}", pointer=f"/claims/{i}", text=text)
        for i, text in enumerate((claims[0], full, claims[2]))
    )
    registry = doc(
        "registry", "registry", EvidenceRegistry(entries=tuple(locations)).model_dump(mode="json")
    )
    documents = (draft, assignment, report, registry)
    return partition_work(
        AssessmentContext(
            provenance="synthetic_fixture",
            origin_sha256="a" * 64,
            documents=documents,
            report_fields=fields,
            statements=tuple(
                SelectedStatement(
                    unit_id=f"U{i}",
                    field_id=f"F{i}",
                    start=fields[i].text.index(claim),
                    end=fields[i].text.index(claim) + len(claim),
                    quote=claim,
                )
                for i, claim in enumerate(claims)
            ),
            messages=(
                SavedMessage(role="user", content=json.dumps([d.model_dump() for d in documents])),
            ),
        ),
        2,
    )


def declarations(work: AssessmentWork) -> ClaimScopeDeclarations:
    predicates = (
        "assignment_obligation",
        "observed_means_relation",
        "unavailable_document_content",
    )
    rows = []
    for i, statement in enumerate(work.context.statements):
        rows.append(
            {
                "statement": statement.model_dump(mode="json"),
                "field_pointer": f"/claims/{i}",
                "claim_predicates": [predicates[i]],
                "evidence_predicates": [predicates[i]],
                "material_components": [
                    {
                        "description": "Entire selected claim, including means and scope",
                        "addressed_by_evidence_contract": True,
                    }
                ],
                "source_scopes": (
                    [{"role": "assignment", "evidence_refs": ["A1"]}]
                    if i == 0
                    else [{"role": "draft", "evidence_refs": ["D1", "D2"]}]
                    if i == 1
                    else []
                ),
                "evidence_requirement": (
                    "Cover the entire proposition, not just the resulting event."
                ),
                "whole_claim_reviewed": True,
                "observation_basis": "unavailable_scope" if i == 2 else "not_applicable",
            }
        )
    return ClaimScopeDeclarations.model_validate_json(
        json.dumps(
            {
                "work_sha256": work.fingerprint,
                "authored_by": "Authored test declarations",
                "declarations": rows,
            }
        )
    )


def changed(work: AssessmentWork, **changes: Any) -> ClaimScopeDeclarations:
    packet = declarations(work).model_dump(mode="json")
    packet["declarations"][0].update(changes)
    return ClaimScopeDeclarations.model_validate_json(json.dumps(packet))


def findings(work: AssessmentWork, packet: ClaimScopeDeclarations) -> tuple[str, ...]:
    return (
        audit_claim_scope(work, scope_for_batch(work, "batch-001", "b" * 64), packet)
        .units[0]
        .issues
    )


def test_declared_consistency_does_not_grade_even_a_false_means_claim(work: AssessmentWork) -> None:
    scope = scope_for_batch(work, "batch-001", "b" * 64)
    before = work.model_dump_json()
    result = audit_claim_scope(work, scope, declarations(work))
    assert all(u.status == "declared_consistent" for u in result.units)
    assert (
        result.factual_support == result.evidence_adequacy == result.edit_necessity == "unassessed"
    )
    assert not result.semantic_interpretation_verified and not result.writer_dispatch_authorized
    assert not result.whole_relation_credit and result.source_roles_are_authored
    assert result.units[1].full_report_field != result.units[1].statement.quote
    assert work.model_dump_json() == before


@pytest.mark.parametrize(
    ("change", "issue"),
    [
        ({"claim_predicates": []}, "missing_predicate_declaration"),
        ({"evidence_predicates": ["observed_event"]}, "claim_evidence_predicate_mismatch"),
        ({"material_components": []}, "whole_claim_not_reviewed"),
        ({"whole_claim_reviewed": False}, "whole_claim_not_reviewed"),
        (
            {"unresolved_qualifiers": ["Does 'by counting' assert a mechanism?"]},
            "unresolved_material_qualifier",
        ),
        (
            {
                "material_components": [
                    {"description": "Asserted mechanism", "addressed_by_evidence_contract": False}
                ]
            },
            "unresolved_material_qualifier",
        ),
        (
            {"claim_predicates": ["editorial_effect"]},
            "editorial_effect_requires_separate_assessment",
        ),
        ({"source_scopes": []}, "missing_source_role:assignment"),
        ({"observation_basis": "unavailable_scope"}, "unavailable_scope_mismatch"),
    ],
)
def test_scope_conflicts_are_visible(
    work: AssessmentWork, change: dict[str, Any], issue: str
) -> None:
    assert issue in findings(work, changed(work, **change))


def test_absence_and_explicit_nonperformance_have_different_coverage(work: AssessmentWork) -> None:
    changes: dict[str, Any] = {
        "claim_predicates": ["observed_event"],
        "evidence_predicates": ["observed_event"],
        "observation_basis": "absence_in_complete_scope",
        "source_scopes": [{"role": "draft", "evidence_refs": ["D1", "D2"]}],
    }
    assert "absence_requires_complete_draft_scope" in findings(work, changed(work, **changes))
    changes["source_scopes"][0]["coverage"] = "complete_fields"
    assert "incomplete_declared_field_coverage:draft" in findings(work, changed(work, **changes))
    changes["source_scopes"][0]["evidence_refs"] = ["D1", "D2", "D3"]
    assert findings(work, changed(work, **changes)) == ()
    changes["observation_basis"] = "explicit_nonperformance"
    changes["source_scopes"] = [{"role": "draft", "evidence_refs": ["D1"]}]
    assert findings(work, changed(work, **changes)) == ()  # Not semantic proof of nonperformance.


def test_missing_declarations_visible_unavailable_claim_needs_no_invented_citation(
    work: AssessmentWork,
) -> None:
    packet = declarations(work)
    missing = packet.model_copy(update={"declarations": ()})
    assert findings(work, missing) == ("missing_claim_declaration",)
    result = audit_claim_scope(work, scope_for_batch(work, "batch-002", "c" * 64), packet)
    assert len(result.units) == 1 and result.units[0].issues == ()
    assert not result.units[0].source_locations


@pytest.mark.parametrize(
    "mutation",
    [
        "work",
        "unit",
        "quote",
        "pointer",
        "offset",
        "ref",
        "duplicate",
        "duplicate_ref",
        "duplicate_role",
        "duplicate_predicate",
        "inactive_ref",
        "authority",
    ],
)
def test_identity_errors_rejected_including_unchecked_and_inactive_records(
    work: AssessmentWork, mutation: str
) -> None:
    packet = declarations(work).model_dump(mode="json")
    row = packet["declarations"][0]
    if mutation == "work":
        packet["work_sha256"] = "0" * 64
    elif mutation == "unit":
        row["statement"]["unit_id"] = "unknown"
    elif mutation == "quote":
        row["statement"]["quote"] += " altered"
    elif mutation == "pointer":
        row["field_pointer"] = "/claims/1"
    elif mutation == "offset":
        row["statement"]["start"] = 1
    elif mutation == "ref":
        row["source_scopes"][0]["evidence_refs"] = ["unknown"]
    elif mutation == "duplicate":
        packet["declarations"].append(row)
    elif mutation == "duplicate_ref":
        row["source_scopes"][0]["evidence_refs"] *= 2
    elif mutation == "duplicate_role":
        row["source_scopes"] *= 2
    elif mutation == "duplicate_predicate":
        row["claim_predicates"] *= 2
    elif mutation == "inactive_ref":
        packet["declarations"][2]["source_scopes"] = [
            {"role": "availability", "evidence_refs": ["missing"]}
        ]
    else:
        packet["writer_dispatch_authorized"] = True
    with pytest.raises((EvidenceError, ValidationError)):
        unchecked = ClaimScopeDeclarations.model_construct(**packet)
        findings(work, unchecked)


def test_native_result_and_full_context_render_without_prompt_or_completion_change(
    work: AssessmentWork,
) -> None:
    scope = scope_for_batch(work, "batch-001", "b" * 64)
    schema = assessment_response_schema(work, scope)
    raw = json.dumps(
        {
            "assessments": {
                unit: {
                    "support": "supported",
                    "evidence": ["D1"],
                    "reason": "An intentionally fallible model judgment.",
                }
                for unit in scope.active_unit_ids
            }
        }
    )
    receipt = AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=scope.request_sha256,
        attempt_id="one",
        status="valid",
        result_sha256=text_hash(raw),
        assessed_unit_ids=scope.active_unit_ids,
        active_seconds=1.0,
    )
    rendered = render_claim_scope(work, scope, declarations(work), receipt=receipt, raw_final=raw)
    fence = rendered.split("json\n")[0].splitlines()[-1]
    payload = json.loads(rendered.split(fence + "json\n", 1)[1].rsplit("\n" + fence, 1)[0])
    assert payload["full_work"] == work.model_dump(mode="json")
    assert payload["bound_result"]["raw_final"] == raw
    assert payload["bound_result"]["evidence_adequacy"] == "unassessed"
    assert payload["claim_scope_audit"]["factual_support"] == "unassessed"
    assert len(fence) > 3 and "<script>data</script>" in rendered
    assert assessment_response_schema(work, scope) == schema
    completed = complete_work(
        work, (receipt,), {b.batch_id: scope.request_sha256 for b in work.batches}
    )
    assert not completed.complete_delivery


@pytest.mark.parametrize("bad", ["receipt_only", "raw_only", "failed", "raw_hash", "scope"])
def test_render_revalidates_delivery_and_scope(work: AssessmentWork, bad: str) -> None:
    scope = scope_for_batch(work, "batch-001", "b" * 64)
    receipt = AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=scope.request_sha256,
        attempt_id="one",
        status="transport_error",
        active_seconds=1,
    )
    kwargs: dict[str, Any] = {}
    if bad == "receipt_only":
        kwargs["receipt"] = receipt
    elif bad == "raw_only":
        kwargs["raw_final"] = "{}"
    elif bad == "scope":
        scope = scope.model_copy(update={"active_unit_ids": ("U2",)})
    else:
        kwargs = {"receipt": receipt, "raw_final": "{}"}
        if bad == "raw_hash":
            kwargs["receipt"] = receipt.model_copy(
                update={
                    "status": "valid",
                    "result_sha256": "0" * 64,
                    "assessed_unit_ids": scope.active_unit_ids,
                }
            )
    with pytest.raises((EvidenceError, ValidationError)):
        render_claim_scope(work, scope, declarations(work), **kwargs)


def test_caller_mutation_cannot_rewrite_returned_snapshot(work: AssessmentWork) -> None:
    packet = declarations(work)
    mutable = list(packet.declarations)
    unchecked = packet.model_copy(update={"declarations": mutable})
    result = audit_claim_scope(work, scope_for_batch(work, "batch-001", "b" * 64), unchecked)
    mutable.clear()
    assert len(result.declarations.declarations) == 3
    assert isinstance(result.declarations.declarations[0], ClaimScopeDeclaration)
