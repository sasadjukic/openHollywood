"""Authored intake examples, never live observations or semantic ground truth."""

from __future__ import annotations

import json

from open_hollywood_engine.evaluations.assessment_claim_scope import (
    ClaimScopeDeclaration,
    DeclaredSourceScope,
    MaterialComponent,
    Predicate,
)
from open_hollywood_engine.evaluations.assessment_intake import (
    IntakeChoice,
    IntakePlan,
    IntakeSource,
    Reading,
    build_intake_source,
    empty_intake_plan,
)
from open_hollywood_engine.evaluations.assessment_result import EvidenceRegistry
from open_hollywood_engine.evaluations.assessment_work_brief import AuthoredWorkBrief
from open_hollywood_engine.evaluations.review_evidence import SavedMessage


def authored_source() -> IntakeSource:
    return build_intake_source(
        origin="diagnostic_probe",
        review_id="authored-only",
        report_origin="raw_model",
        messages=(
            SavedMessage(role="system", content="Authored fixture."),
            SavedMessage(
                role="user",
                content=json.dumps(
                    {
                        "assignment": {"definition": "The proof requires reading both signatures."},
                        "next_scene": {"outcome": "The witness answers."},
                    }
                ),
            ),
        ),
        current_prose="Mira 🔑 opens the ledger.\r\n\r\nShe reads only the first signature.",
        current_version="authored-draft",
        report={
            "issues": [
                {"assessment": "Mira opens the ledger."},
                {"assessment": "Mira completes the two-signature proof."},
                {"assessment": "The reveal steals the next scene's dramatic work."},
                {"assessment": "The generic match achieves the named proof too early."},
                {"assessment": "The next scene starts with a confession."},
            ],
            "summary": "Full context ``` </script> stays literal.",
        },
        operator_provenance={"fixture": "authored-only", "hidden_start": "confession"},
    )


def choice_for(source: IntakeSource, field_id: str, reading: Reading = "factual") -> IntakeChoice:
    work = source.inventory_work
    statement = next(s for s in work.context.statements if s.field_id == field_id)
    field = next(f for f in work.context.report_fields if f.field_id == field_id)
    registry = EvidenceRegistry.model_validate_json(
        next(d.content_json for d in work.context.documents if d.kind == "registry")
    )
    draft_ref = next(
        e.ref for e in registry.entries if e.document_id == "catalog-complete-current-draft"
    )
    predicates: tuple[Predicate, ...] = (
        ("observed_procedure",) if reading == "literal_procedure" else ("observed_event",)
    )
    scopes: tuple[DeclaredSourceScope, ...] = (
        DeclaredSourceScope(role="draft", evidence_refs=(draft_ref,), coverage="complete_fields"),
    )
    if reading == "literal_procedure":
        definition = next(
            e.ref for e in registry.entries if e.field_pointer == "/assignment/definition"
        )
        scopes += (DeclaredSourceScope(role="definition", evidence_refs=(definition,)),)
    declaration = ClaimScopeDeclaration(
        statement=statement,
        field_pointer=field.pointer,
        claim_predicates=predicates,
        evidence_predicates=predicates,
        source_scopes=scopes,
        material_components=(
            MaterialComponent(
                description="Assess every clause of the unchanged field.",
                addressed_by_evidence_contract=True,
            ),
        ),
        evidence_requirement="Use the declared source roles and complete current prose.",
        whole_claim_reviewed=True,
        observation_basis="positive_depiction",
    )
    return IntakeChoice(
        field_id=field_id,
        reading=reading,
        interpretation="Authored literal whole-field reading.",
        declaration=declaration,
        brief=AuthoredWorkBrief(
            unit_id=statement.unit_id,
            question="Is the entire claim established?",
            temporal_scope="Current scene; future assertions need separate authority.",
            source_authority="Actual visible context and complete current draft.",
            evidence_obligation="Address all material clauses; a locator is not complete proof.",
        ),
    )


def plan_for(source: IntakeSource, *choices: IntakeChoice) -> IntakePlan:
    return empty_intake_plan(source).model_copy(
        update={"authored_by": "Authored test operator", "choices": tuple(choices)}
    )
