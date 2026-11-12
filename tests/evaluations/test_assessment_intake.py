"""Authored scope, retention and refusal tests; no semantics inferred by the harness."""

from __future__ import annotations

import json
import socket
import sqlite3
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations.assessment_claim_scope import DeclaredSourceScope
from open_hollywood_engine.evaluations.assessment_intake import (
    IntakeChoice,
    IntakePlan,
    IntakeResult,
    Reading,
    build_intake_source,
    compile_intake,
    empty_intake_plan,
    render_intake,
)
from open_hollywood_engine.evaluations.assessment_work import partition_work
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from pydantic import ValidationError

from tests.assessment_intake_fixtures import authored_source, choice_for, plan_for


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def denied(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("No network or database in intake domain")

    for owner, name in (
        (socket.socket, "connect"),
        (socket, "create_connection"),
        (httpx.Client, "send"),
        (httpx.AsyncClient, "send"),
        (sqlite3, "connect"),
    ):
        monkeypatch.setattr(owner, name, denied)


def test_inventory_does_not_admit_or_create_completion() -> None:
    source = authored_source()
    result = compile_intake(source, empty_intake_plan(source))
    assert all(f.status == "not_selected" for f in result.findings)
    assert result.pending_work is None
    assert result.declarations is None and result.briefs is None
    assert result.assessment_result is result.completion_receipt is None
    assert not result.writer_dispatch_authorized and not result.model_input


def test_factual_and_procedure_work_keep_complete_context_and_distinct_scope() -> None:
    source = authored_source()
    plan = plan_for(
        source, choice_for(source, "Q001"), choice_for(source, "Q002", "literal_procedure")
    )
    result = compile_intake(source, plan)
    pending = result.pending_work
    assert pending is not None and len(pending.context.statements) == 2
    assert pending.context.documents == source.inventory_work.context.documents
    assert pending.context.messages == source.inventory_work.context.messages
    assert pending.context.report_fields == source.inventory_work.context.report_fields
    assert result.declarations is not None
    assert result.declarations.declarations[1].claim_predicates == ("observed_procedure",)
    assert result.factual_support == result.evidence_adequacy == result.craft == "unassessed"
    assert not result.semantic_interpretation_verified


@pytest.mark.parametrize("reading", ["editorial_effect", "mixed", "ambiguous"])
def test_nonfactual_reading_is_held_even_with_consistent_declaration(reading: Reading) -> None:
    source = authored_source()
    result = compile_intake(source, plan_for(source, choice_for(source, "Q003", reading)))
    assert result.findings[2].status == "hold" and result.pending_work is None
    assert "nonfactual_or_ambiguous_reading" in result.findings[2].issues


@pytest.mark.parametrize("mutation", ["no_definition", "no_predicate", "factual_reading"])
def test_procedure_obligations_are_explicit(mutation: str) -> None:
    source = authored_source()
    choice = choice_for(source, "Q002", "literal_procedure")
    d = choice.declaration
    assert d is not None
    if mutation == "no_definition":
        choice = choice.model_copy(
            update={"declaration": d.model_copy(update={"source_scopes": d.source_scopes[:1]})}
        )
    elif mutation == "no_predicate":
        choice = choice_for(source, "Q002").model_copy(update={"reading": "literal_procedure"})
    else:
        choice = choice.model_copy(update={"reading": "factual"})
    result = compile_intake(source, plan_for(source, choice))
    assert result.findings[1].status == "hold" and result.pending_work is None


def test_ambiguous_procedure_not_silently_reinterpreted() -> None:
    source = authored_source()
    choice = IntakeChoice(
        field_id="Q004",
        reading="ambiguous",
        interpretation="Named procedure versus editorial preemption; unresolved.",
    )
    result = compile_intake(source, plan_for(source, choice))
    assert result.findings[3].field.text == source.inventory_work.context.report_fields[3].text
    assert result.findings[3].choice == choice and result.pending_work is None


@pytest.mark.parametrize(
    "mutation",
    ["source", "work", "duplicate", "unknown", "short_quote", "foreign_brief", "foreign_ref"],
)
def test_identity_failures_are_refused(mutation: str) -> None:
    source = authored_source()
    choice = choice_for(source, "Q001")
    plan = plan_for(source, choice)
    if mutation in ("source", "work"):
        key = "source_sha256" if mutation == "source" else "inventory_work_sha256"
        plan = plan.model_copy(update={key: "0" * 64})
    elif mutation == "duplicate":
        plan = plan.model_copy(update={"choices": (choice, choice)})
    elif mutation == "unknown":
        plan = plan_for(source, choice.model_copy(update={"field_id": "unknown"}))
    elif mutation == "foreign_brief":
        assert choice.brief is not None
        plan = plan_for(
            source,
            choice.model_copy(
                update={"brief": choice.brief.model_copy(update={"unit_id": "Q002"})}
            ),
        )
    else:
        d = choice.declaration
        assert d is not None
        if mutation == "short_quote":
            d = d.model_copy(
                update={"statement": d.statement.model_copy(update={"end": 4, "quote": "Mira"})}
            )
        else:
            d = d.model_copy(
                update={
                    "source_scopes": (
                        DeclaredSourceScope(role="draft", evidence_refs=("foreign",)),
                    )
                }
            )
        plan = plan_for(source, choice.model_copy(update={"declaration": d}))
    with pytest.raises(EvidenceError):
        compile_intake(source, plan)


@pytest.mark.parametrize("missing", ["declaration", "brief"])
def test_missing_sidecar_is_a_visible_hold(missing: str) -> None:
    source = authored_source()
    choice = choice_for(source, "Q001").model_copy(update={missing: None})
    result = compile_intake(source, plan_for(source, choice))
    assert result.findings[0].status == "hold" and result.pending_work is None


def test_unavailable_scope_is_not_falsehood_or_recovered_authority() -> None:
    source = authored_source()
    choice = choice_for(source, "Q005")
    d = choice.declaration
    assert d is not None
    d = d.model_copy(
        update={
            "claim_predicates": ("unavailable_document_content",),
            "evidence_predicates": ("unavailable_document_content",),
            "source_scopes": (),
            "observation_basis": "unavailable_scope",
        }
    )
    result = compile_intake(source, plan_for(source, choice.model_copy(update={"declaration": d})))
    assert result.findings[4].status == "pending_assessment"
    assert result.factual_support == "unassessed"
    registry = next(x for x in source.inventory_work.context.documents if x.kind == "registry")
    assert "hidden_start" not in registry.content_json


def test_authored_hold_and_unresolved_qualifier_cannot_dispatch() -> None:
    source = authored_source()
    choice = choice_for(source, "Q001").model_copy(
        update={"hold_reason": "Need interpretation review."}
    )
    result = compile_intake(source, plan_for(source, choice))
    assert result.pending_work is None and "authored_hold" in result.findings[0].issues


def test_literal_render_and_caller_mutation_rechecked() -> None:
    source = authored_source()
    result = compile_intake(source, plan_for(source, choice_for(source, "Q001")))
    markdown = render_intake(result)
    assert "````json" in markdown and "</script>" in markdown
    assert json.loads(
        markdown.split("````json\n", 1)[1].rsplit("\n````", 1)[0]
    ) == result.model_dump(mode="json")
    with pytest.raises(EvidenceError, match="intake_result_mismatch"):
        render_intake(result.model_copy(update={"pending_work": None}))


@pytest.mark.parametrize("field", ["gold", "model_input", "writer_dispatch_authorized"])
def test_gold_and_authority_escalation_rejected(field: str) -> None:
    source = authored_source()
    data = empty_intake_plan(source).model_dump(mode="json")
    data[field] = "supported" if field == "gold" else True
    with pytest.raises(ValidationError):
        IntakePlan.model_validate_json(json.dumps(data))


def test_structural_validity_does_not_certify_authored_interpretation() -> None:
    source = authored_source()
    choice = choice_for(source, "Q001").model_copy(
        update={"interpretation": "A deliberately wrong free-text reading."}
    )
    result: IntakeResult = compile_intake(source, plan_for(source, choice))
    assert result.pending_work is not None
    assert not result.semantic_interpretation_verified and not result.brief_neutrality_verified


def test_inventory_over_twelve_fields_preserves_every_field_in_bounded_batches() -> None:
    base = authored_source()
    source = build_intake_source(
        origin=base.origin,
        review_id="many-fields",
        report_origin=base.report_origin,
        messages=base.inventory_work.context.messages,
        current_prose="Full current prose.",
        current_version="authored",
        operator_provenance={"fixture": True},
        report={"issues": [{"assessment": f"Whole claim {i}."} for i in range(25)]},
    )
    result = compile_intake(source, plan_for(source, choice_for(source, "Q025")))
    assert len(result.findings) == 25 and len(source.inventory_work.batches) == 3
    assert all(len(b.unit_ids) <= 12 for b in source.inventory_work.batches)
    assert result.pending_work is not None
    assert len(result.pending_work.context.report_fields) == 25
    assert result.pending_work.context.statements[0].unit_id == "Q025"
    with pytest.raises(ValidationError):
        IntakePlan.model_validate_json(
            empty_intake_plan(source).model_copy(update={"maximum_units": 13}).model_dump_json()
        )


@pytest.mark.parametrize("mutation", ["source_hash", "report_origin", "provenance_role"])
def test_source_contract_cannot_promote_provenance_or_change_identity(mutation: str) -> None:
    source = authored_source()
    plan = empty_intake_plan(source)
    if mutation == "source_hash":
        source = source.model_copy(update={"source_sha256": "0" * 64})
    elif mutation == "report_origin":
        source = source.model_copy(update={"report_origin": "saved_normalized_and_audit"})
    else:
        work = source.inventory_work
        documents = tuple(
            d.model_copy(update={"kind": "source"}) if d.kind == "scope" else d
            for d in work.context.documents
        )
        changed = partition_work(work.context.model_copy(update={"documents": documents}), 12)
        source = source.model_copy(update={"inventory_work": changed})
    with pytest.raises(ValueError):
        compile_intake(source, plan)
