"""Authored history/materiality fixtures; exact copying never grants semantic authority."""

from __future__ import annotations

import json
import socket
import sqlite3
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_authority import (
    AssessmentAuthority,
    preview_assessment_authority,
    render_assessment_authority,
)
from open_hollywood_engine.evaluations.assessment_claim_scope import ClaimScopeDeclarations
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceLocation,
    EvidenceRegistry,
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
from open_hollywood_engine.evaluations.assessment_work_brief import AssessmentWorkBriefs
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, SavedMessage, text_hash
from open_hollywood_engine.secrets import EnvironmentSecretStore
from pydantic import ValidationError


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Authority preview forbids external I/O")

    for owner, name in (
        (httpx.Client, "request"),
        (httpx.AsyncClient, "request"),
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "getaddrinfo"),
        (socket, "create_connection"),
        (sqlite3, "connect"),
        (EnvironmentSecretStore, "get"),
        (EnvironmentSecretStore, "configured_values"),
    ):
        monkeypatch.setattr(owner, name, deny)


def document(identity: str, kind: Any, value: dict[str, Any]) -> ContextDocument:
    raw = json.dumps(value, ensure_ascii=False)
    return ContextDocument(
        identity=identity,
        version=identity + "-v1",
        kind=kind,
        content_json=raw,
        content_sha256=text_hash(raw),
    )


@pytest.fixture
def fixture() -> tuple[
    AssessmentWork, ClaimScopeDeclarations, AssessmentWorkBriefs, AssessmentAuthority
]:
    values = {
        "H": "The critic said the card was dated today.",
        "E": "She crossed.",
        "R": "Show realization again.",
        "A": "The card must be exactly ten years ahead.",
        "T": "Nia must realize the ten-year gap.",
        "D": "Card: October 14, 2034. Clock: October 14, 2024.",
        "N": "Nia recognized the ten-year gap.",
        "O": "Nia remained outside.",
    }
    source = document("packet", "source", values)
    fields = tuple(
        ReportField(field_id=f"F{i}", pointer=f"/claims/{i - 1}", text=text)
        for i, text in enumerate(
            (
                "The previous claim named today; the current dates establish the required gap.",
                "The required realization is depicted.",
                "The previous crossing violation is corrected; Nia stays outside.",
                "The critic requested another realization. ``` Ω",
            ),
            1,
        )
    )
    entries = tuple(
        EvidenceLocation(
            ref=ref,
            document_id=source.identity,
            document_version=source.version,
            document_sha256=source.content_sha256,
            field_pointer="/" + ref,
            field_sha256=text_hash(text),
            start=0,
            end=len(text),
            quote=text,
        )
        for ref, text in values.items()
    )
    docs = (
        source,
        document("report", "report", {"claims": [f.text for f in fields]}),
        document("registry", "registry", EvidenceRegistry(entries=entries).model_dump(mode="json")),
    )
    work = partition_work(
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
            messages=(SavedMessage(role="user", content="Full visible fixture: " + str(docs)),),
        ),
        3,
    )
    # Component-to-predicate mapping is authored. No text parser supplies it.
    specifications = [
        [
            (
                "Historical attribution",
                "historical_attribution",
                "historical_critic_assertion",
                "H",
            ),
            ("Current dates", "observed_event", "draft", "D"),
            ("Required gap", "assignment_obligation", "assignment", "A"),
        ],
        [
            ("Realization requirement", "assignment_obligation", "assignment", "T"),
            ("Depicted realization", "observed_event", "draft", "N"),
        ],
        [
            ("Historical violation", "historical_violation", "historical_excerpt", "E"),
            ("Current outside state", "observed_event", "draft", "O"),
        ],
        [("Requested repair", "requested_repair", "requested_repair", "R")],
    ]
    declared, claims = [], []
    for index, (statement, field, specs) in enumerate(
        zip(work.context.statements, fields, specifications, strict=True)
    ):
        predicates = list(dict.fromkeys(s[1] for s in specs))
        declared.append(
            {
                "statement": statement.model_dump(mode="json"),
                "field_pointer": field.pointer,
                "claim_predicates": predicates,
                "evidence_predicates": predicates,
                "material_components": [
                    {"description": s[0], "addressed_by_evidence_contract": True} for s in specs
                ],
                "source_scopes": [{"role": s[2], "evidence_refs": [s[3]]} for s in specs],
                "unresolved_qualifiers": ["Earlier assignment authority and violation meaning"]
                if index == 2
                else [],
                "evidence_requirement": (
                    "Keep each whole proposition and its evidence obligations separate."
                ),
                "whole_claim_reviewed": True,
                "observation_basis": "not_applicable",
            }
        )
        claims.append(
            {
                "unit_id": statement.unit_id,
                "obligations": [
                    {
                        "component_index": n,
                        "requirement": s[0],
                        "predicates": [s[1]],
                        "source_roles": [s[2]],
                        "example_refs": [s[3]],
                    }
                    for n, s in enumerate(specs)
                ],
            }
        )
    declarations = ClaimScopeDeclarations.model_validate_json(
        json.dumps(
            {
                "work_sha256": work.fingerprint,
                "authored_by": "Test author",
                "declarations": declared,
            }
        )
    )
    declaration_hash = canonical_sha256(declarations.model_dump(mode="json"))
    briefs = AssessmentWorkBriefs.model_validate_json(
        json.dumps(
            {
                "work_sha256": work.fingerprint,
                "declarations_sha256": declaration_hash,
                "authored_by": "Test author",
                "briefs": [
                    {
                        "unit_id": s.unit_id,
                        "question": "Is the whole selected field established?",
                        "temporal_scope": "Explicit current and recorded historical clauses",
                        "source_authority": (
                            "Keep assignment, assertion and requested repair separate."
                        ),
                        "evidence_obligation": (
                            "Use only the material predicates of this selected claim."
                        ),
                    }
                    for s in work.context.statements
                ],
            }
        )
    )
    old = "Ω She crossed.\n\nShe crossed. ```"
    historical = document("old", "source", {"nested/field": {"~prose": [old]}})
    start = old.rindex(values["E"])
    authority = AssessmentAuthority.model_validate_json(
        json.dumps(
            {
                "work_sha256": work.fingerprint,
                "request_sha256": "b" * 64,
                "declarations_sha256": declaration_hash,
                "authored_by": "Test author",
                "origin_sha256": "c" * 64,
                "historical_sources": [historical.model_dump(mode="json")],
                "claims": claims,
                "bindings": [
                    {
                        "evidence_ref": "E",
                        "historical_span": {
                            "document_id": historical.identity,
                            "document_version": historical.version,
                            "document_sha256": historical.content_sha256,
                            "field_pointer": "/nested~1field/~0prose/0",
                            "field_sha256": text_hash(old),
                            "start": start,
                            "end": start + len(values["E"]),
                            "quote": values["E"],
                        },
                        "excerpt_visibility": "shown",
                        "historical_body_visibility": "not_shown",
                        "visibility_basis": (
                            "Authored fixture; only the excerpt occurs in the recorded context."
                        ),
                    }
                ],
            }
        )
    )
    return work, declarations, briefs, authority


def preview(fixture: tuple[Any, ...], value: dict[str, Any] | None = None) -> Any:
    work, declarations, briefs, authority = fixture
    return preview_assessment_authority(
        work,
        scope_for_batch(work, "batch-001", "b" * 64),
        declarations,
        briefs,
        AssessmentAuthority.model_construct(**value) if value is not None else authority,
    )


def unpack(text: str) -> dict[str, Any]:
    fence = text.split("json\n", 1)[0].splitlines()[-1]
    return dict(json.loads(text.split(fence + "json\n", 1)[1].rsplit("\n" + fence, 1)[0]))


def test_exact_copy_and_materiality_do_not_promote_truth(fixture: tuple[Any, ...]) -> None:
    work, declarations, briefs, authority = fixture
    before = work.model_dump_json()
    result = preview(fixture)
    assert [u.status for u in result.units] == [
        "declared_consistent",
        "declared_consistent",
        "needs_scope_review",
    ]
    binding = result.historical_bindings[0]
    assert binding.status == "exact_copy" and binding.verified_against_supplied_body
    assert binding.binding.historical_span.start > 0  # exact second occurrence
    assert not binding.external_provenance_authenticated and not binding.model_visibility_verified
    assert binding.event_truth == binding.historical_violation == "unassessed"
    assert "missing_source_role:historical_assignment" in result.units[2].issues
    assert not result.writer_dispatch_authorized and not result.model_input
    rendered = render_assessment_authority(
        work, scope_for_batch(work, "batch-001", "b" * 64), declarations, briefs, authority
    )
    payload = unpack(rendered)
    assert payload["full_work"] == work.model_dump(mode="json") and work.model_dump_json() == before
    assert "````json" in rendered and "Ω" in rendered
    assert all(d.identity != "old" for d in work.context.documents)
    assert payload["authority_preview"]["authored_authority"]["historical_sources"]


@pytest.mark.parametrize(
    "mutation",
    [
        "work",
        "request",
        "declarations",
        "duplicate_claim",
        "unknown_claim",
        "duplicate_component",
        "extra_component",
        "duplicate_role",
        "duplicate_ref",
        "unknown_ref",
        "duplicate_predicate",
        "model_input",
        "writer",
        "answer",
        "inactive",
    ],
)
def test_structural_and_inactive_obligations_rejected(
    fixture: tuple[Any, ...], mutation: str
) -> None:
    value = fixture[3].model_dump(mode="json")
    if mutation in ("work", "request", "declarations"):
        value[mutation + "_sha256"] = "0" * 64
    elif mutation == "duplicate_claim":
        value["claims"].append(value["claims"][0])
    elif mutation == "unknown_claim":
        value["claims"][-1]["unit_id"] = "foreign"
    elif mutation in ("extra_component", "inactive"):
        value["claims"][-1 if mutation == "inactive" else 0]["obligations"][0][
            "component_index"
        ] = 99
    elif mutation == "duplicate_component":
        value["claims"][0]["obligations"].append(value["claims"][0]["obligations"][0])
    elif mutation in ("duplicate_role", "duplicate_ref", "duplicate_predicate"):
        field = {
            "duplicate_role": "source_roles",
            "duplicate_ref": "example_refs",
            "duplicate_predicate": "predicates",
        }[mutation]
        value["claims"][0]["obligations"][0][field] *= 2
    elif mutation == "unknown_ref":
        value["claims"][0]["obligations"][0]["example_refs"] = ["foreign"]
    elif mutation == "answer":
        value["claims"][0]["expected_support"] = "supported"
    else:
        value["model_input" if mutation == "model_input" else "writer_dispatch_authorized"] = True
    with pytest.raises((EvidenceError, ValidationError)):
        preview(fixture, value)


@pytest.mark.parametrize(
    "mutation",
    [
        "source_hash",
        "version",
        "field",
        "field_hash",
        "offset",
        "quote",
        "unknown_evidence",
        "duplicate_binding",
        "duplicate_body",
        "body_kind",
        "identity",
    ],
)
def test_historical_proof_mutations_rejected(fixture: tuple[Any, ...], mutation: str) -> None:
    value = fixture[3].model_dump(mode="json")
    binding = value["bindings"][0]
    span = binding["historical_span"]
    if mutation == "source_hash":
        span["document_sha256"] = "0" * 64
    elif mutation == "version":
        span["document_version"] = "other"
    elif mutation == "field":
        span["field_pointer"] = "/nested~2field"
    elif mutation == "field_hash":
        span["field_sha256"] = "0" * 64
    elif mutation == "offset":
        span["start"] += 1
        span["end"] += 1
    elif mutation == "quote":
        span["quote"] = "She did not cross."
    elif mutation == "unknown_evidence":
        binding["evidence_ref"] = "foreign"
    elif mutation == "duplicate_binding":
        value["bindings"] *= 2
    elif mutation == "duplicate_body":
        value["historical_sources"] *= 2
    elif mutation == "body_kind":
        value["historical_sources"][0]["kind"] = "scope"
    else:
        value["historical_sources"][0]["identity"] = "packet"
    with pytest.raises((EvidenceError, ValidationError)):
        preview(fixture, value)


@pytest.mark.parametrize("missing", ["body", "binding", "visibility", "claims", "component"])
def test_missing_information_is_visible(fixture: tuple[Any, ...], missing: str) -> None:
    value = fixture[3].model_dump(mode="json")
    if missing == "body":
        value["historical_sources"] = []
    elif missing == "binding":
        value["bindings"] = []
    elif missing == "visibility":
        value["bindings"][0]["excerpt_visibility"] = "unknown"
    elif missing == "claims":
        value["claims"] = []
    else:
        value["claims"][1]["obligations"].pop()
    result = preview(fixture, value)
    if missing == "body":
        assert result.historical_bindings[0].status == "unverified_missing_source"
    if missing in ("body", "binding"):
        assert "unverified_historical_excerpt:E" in result.units[2].issues
    if missing == "visibility":
        assert "historical_excerpt_visibility_unresolved:E" in result.units[2].issues
    if missing == "claims":
        assert all(u.status == "needs_scope_review" for u in result.units)
    if missing == "component":
        assert result.units[0].status == "declared_consistent"
        assert "missing_component_obligation:1" in result.units[1].issues


def test_repair_request_cannot_fill_assignment_obligation(fixture: tuple[Any, ...]) -> None:
    value = fixture[3].model_dump(mode="json")
    value["claims"][0]["obligations"][2].update(
        source_roles=["requested_repair"], example_refs=["R"]
    )
    result = preview(fixture, value)
    assert "obligation_missing_required_role:2:assignment" in result.units[0].issues
    assert result.units[1].status == "declared_consistent"


def test_wrong_free_text_is_not_semantically_certified(fixture: tuple[Any, ...]) -> None:
    value = fixture[3].model_dump(mode="json")
    value["claims"][0]["obligations"][1]["requirement"] = "Demand a further realization rewrite."
    result = preview(fixture, value)
    assert result.units[0].status == "declared_consistent"
    assert not result.semantic_interpretation_verified and result.edit_necessity == "unassessed"


def test_requested_repair_is_supported_as_a_role_not_current_canon(
    fixture: tuple[Any, ...],
) -> None:
    work, declarations, briefs, authority = fixture
    result = preview_assessment_authority(
        work, scope_for_batch(work, "batch-002", "b" * 64), declarations, briefs, authority
    )
    assert result.units[0].unit_id == "Q4" and result.units[0].status == "declared_consistent"
    assert result.obligation_existence == "unassessed"


def test_unchanged_completion_and_optional_native_result(fixture: tuple[Any, ...]) -> None:
    work, declarations, briefs, authority = fixture
    scope = scope_for_batch(work, "batch-001", "b" * 64)
    raw = json.dumps(
        {
            "assessments": {
                unit: {"support": "uncertain", "reason": "Unqualified test.", "evidence": []}
                for unit in scope.active_unit_ids
            }
        }
    )
    receipt = AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id="batch-001",
        request_sha256="b" * 64,
        attempt_id="test-1",
        status="valid",
        assessed_unit_ids=scope.active_unit_ids,
        result_sha256=text_hash(raw),
        binding="unresolved",
        input_tokens=None,
        output_tokens=None,
        reasoning_tokens=None,
        active_seconds=1,
    )
    output = unpack(
        render_assessment_authority(
            work, scope, declarations, briefs, authority, receipt=receipt, raw_final=raw
        )
    )
    bound = AssessmentReceipt.model_validate_json(json.dumps(output["bound_result"]["receipt"]))
    completion = complete_work(work, (bound,), {b.batch_id: "b" * 64 for b in work.batches})
    assert not completion.writer_dispatch_authorized
    assert completion.support == "unassessed"
    for kwargs in ({"receipt": receipt}, {"receipt": receipt, "raw_final": raw + " "}):
        with pytest.raises(EvidenceError):
            render_assessment_authority(work, scope, declarations, briefs, authority, **kwargs)


def test_caller_aliases_do_not_mutate_preview(fixture: tuple[Any, ...]) -> None:
    value = fixture[3].model_dump(mode="json")
    result = preview(fixture, value)
    value["claims"][0]["obligations"].clear()
    assert result.units[0].authored is not None and len(result.units[0].authored.obligations) == 3
