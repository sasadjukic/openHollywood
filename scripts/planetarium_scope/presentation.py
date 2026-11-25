"""Build one complete authored source packet and its matched reviewer requests."""

from __future__ import annotations

from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from open_hollywood_engine.evaluations.assessment_claim_scope import (
    ClaimScopeDeclaration,
    DeclaredSourceScope,
    MaterialComponent,
)
from open_hollywood_engine.evaluations.assessment_compact_presentation import (
    NOTICE,
    SYSTEM,
    compact,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import _document
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceLocation,
    EvidenceRegistry,
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentContext,
    AssessmentWork,
    ReportField,
    SelectedStatement,
    partition_work,
)
from open_hollywood_engine.evaluations.assessment_work_brief import AuthoredWorkBrief
from open_hollywood_engine.evaluations.review_evidence import SavedMessage, text_hash
from open_hollywood_engine.models.assessment_openai import _prepare_wire
from open_hollywood_engine.models.contracts import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelDeployment,
    ModelMessage,
    ModelRequest,
    ModelSettings,
)
from open_hollywood_engine.models.openai import _cost
from open_hollywood_engine.models.openai_catalog import OpenAIModelSpec

from scripts.q010_uncertainty_plan import Cell, digest
from scripts.wading_path_be.plan import INPUT, OUTPUT, native_view
from scripts.wading_path_sol_astra.plan import TARGET

BRIEF = AuthoredWorkBrief(
    unit_id="A001",
    question="Does the selected scene-four draft establish the whole active claim?",
    temporal_scope="Use the interval or instant specified by the claim.",
    source_authority="Use E1420, the complete selected scene-four draft. The saved review "
    "and its original request supply historical context.",
    evidence_obligation="Cite the selected draft and explain what it establishes "
    "for the whole claim.",
)


def version(role: str, content_hash: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"openhollywood/planetarium/{role}/{content_hash}"))


def work_for(source: dict[str, Any], history: str, kind: str) -> AssessmentWork:
    claim = source["claims"][kind]
    prose = source["drafts"][history]
    docs = []
    refs = []
    for role, value, ref, field in (
        ("scene_plan", source["scene_plan"], "E0001", "assignment"),
        ("review_request", source["review_request"], "E0002", "excerpt"),
        ("saved_review", source["saved_review"], "E0003", "observation"),
        ("draft", {"prose": prose}, "E1420", "prose"),
    ):
        pin = text_hash(prose) if role == "draft" else digest(encoded(value))
        doc = _document(role, "source", value, version(role, pin))
        docs.append(doc)
        quote = value[field]
        refs.append(
            EvidenceLocation(
                ref=ref,
                document_id=role,
                document_version=doc.version,
                document_sha256=doc.content_sha256,
                field_pointer="/" + field,
                field_sha256=text_hash(quote),
                start=0,
                end=len(quote),
                quote=quote,
            )
        )
    docs.append(
        _document(
            "authored-diagnostic-claim",
            "report",
            {"authored_claim": claim},
            version("claim", text_hash(claim)),
        )
    )
    registry = EvidenceRegistry(entries=tuple(refs)).model_dump(mode="json")
    docs.append(
        _document("registry", "registry", registry, version("registry", digest(encoded(registry))))
    )
    field_record = ReportField(field_id="A001", pointer="/authored_claim", text=claim)
    statement = SelectedStatement(
        unit_id="A001", field_id="A001", start=0, end=len(claim), quote=claim
    )
    return partition_work(
        AssessmentContext(
            provenance="synthetic_fixture",
            origin_sha256=digest(encoded([d.content_sha256 for d in docs])),
            documents=tuple(docs),
            report_fields=(field_record,),
            statements=(statement,),
            messages=(SavedMessage(role="user", content=compact(source["review_request"])),),
        ),
        1,
    )


def render(name: str, work: AssessmentWork, kind: str, spec: OpenAIModelSpec) -> Cell:
    statement = work.context.statements[0]
    declaration = ClaimScopeDeclaration(
        statement=statement,
        field_pointer="/authored_claim",
        whole_claim_reviewed=True,
        claim_predicates=("observed_event",),
        evidence_predicates=("observed_event",),
        observation_basis="not_applicable",
        source_scopes=(
            DeclaredSourceScope(role="draft", coverage="complete_fields", evidence_refs=("E1420",)),
        ),
        material_components=(
            MaterialComponent(description=statement.quote, addressed_by_evidence_contract=True),
        ),
        evidence_requirement=BRIEF.evidence_obligation,
    ).model_dump(mode="json")
    if name.endswith("X"):
        declaration["assessment_target"] = TARGET["narrated" if kind == "narration" else "reached"]
    user = compact(
        dict(
            contract="planetarium-authored-assessment-1",
            active_unit_ids=["A001"],
            native_work_view=native_view(work),
            claim_scope=declaration,
            work_brief=BRIEF.model_dump(mode="json"),
            availability_notice=NOTICE,
            field_dispositions={"A001": "pending_assessment"},
        )
    )
    model = spec.model_identifier
    native_id = digest(encoded([work.fingerprint, SYSTEM, user, model, "high", INPUT, OUTPUT]))
    scope = scope_for_batch(work, work.batches[0].batch_id, native_id)
    versions = tuple(UUID(d.version) for d in work.context.documents if d.kind != "registry")
    request = ModelRequest(
        provider="openai",
        deployment=ModelDeployment.CLOUD,
        model_identifier=model,
        invocation=InvocationContext(
            "endpoint_fact_assessment", "planetarium-authored-assessment-1", versions
        ),
        messages=(ModelMessage(MessageRole.SYSTEM, SYSTEM), ModelMessage(MessageRole.USER, user)),
        response_schema=assessment_response_schema(work, scope),
        settings=ModelSettings(thinking="high"),
        budget=ModelCallBudget(INPUT, OUTPUT, _cost(spec, INPUT, OUTPUT)),
    )
    return Cell(name, work, _prepare_wire(work, scope, request, spec, guard=None))
