"""Small authored archive; no private prose, model observation or provider dependency."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from open_hollywood_api.services.assessment_archive_export import AssessmentArchiveContract
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceLocation,
    EvidenceRegistry,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentContext,
    AssessmentReceipt,
    ContextDocument,
    ReportField,
    SelectedStatement,
    partition_work,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import SavedMessage, text_hash

PREP = "data/diagnostics/authored-native-assessment"
AUTHORED = "data/diagnostics/authored-native-controls"
TRIAL = "BH-1-A-B-SC"
CELL = PREP + "-M-live/cells/" + TRIAL


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


@dataclass
class ArchiveFixture:
    root: Path
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)

    def seal(self) -> AssessmentArchiveContract:
        # Only tests can inject this contract. No CLI accepts a caller-provided seal.
        self.documents[CELL + "/seal.json"] = {
            name.rsplit("/", 1)[1]: text_hash(encoded(value).decode("utf-8"))
            for name, value in self.documents.items()
            if name.startswith(CELL + "/") and not name.endswith("/seal.json")
        }
        hashes = {name: text_hash(encoded(v).decode("utf-8")) for name, v in self.documents.items()}
        seal = {
            "preparation_members_sha256": hashes,
            "source_pins_sha256": {},
            "capture_members_sha256": {},
            "results_members_sha256": {},
            "public_files_sha256": {},
            "plan_sha256": hashes[PREP + "/plan.json"],
            "approval_sha256": hashes[PREP + "/approval-M.json"],
        }
        for name, value in {**self.documents, PREP + "-results/results-seal.json": seal}.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded(value))
        return AssessmentArchiveContract(
            experiment="authored-native-assessment",
            authored_experiment="authored-native-controls",
            results_seal_sha256=text_hash(encoded(seal).decode("utf-8")),
            plan_sha256=hashes[PREP + "/plan.json"],
        )


def make_archive(root: Path) -> ArchiveFixture:
    f = ArchiveFixture(root)

    def document(identity: str, kind: Any, body: dict[str, Any]) -> ContextDocument:
        raw = json.dumps(body, ensure_ascii=False)
        return ContextDocument(
            identity=identity,
            version="v1",
            kind=kind,
            content_json=raw,
            content_sha256=text_hash(raw),
        )

    prose = "Mira closed the gate. Ω 🔑 ```"
    source = document("old-scene", "source", {"prose": prose})
    location = EvidenceLocation(
        ref="S001",
        document_id=source.identity,
        document_version=source.version,
        document_sha256=source.content_sha256,
        field_pointer="/prose",
        field_sha256=text_hash(prose),
        start=0,
        end=len(prose),
        quote=prose,
    )
    registry = document(
        "registry", "registry", EvidenceRegistry(entries=(location,)).model_dump(mode="json")
    )
    fields = tuple(
        ReportField(field_id=f"Q{i}", pointer=f"/Q{i}", text="Mira closed the gate.")
        for i in range(1, 7)
    )
    report = document("report", "report", {v.field_id: v.text for v in fields})
    manifest = document("A-manifest", "source", {"lineage": "Explicit authored test only"})
    context = AssessmentContext(
        provenance="synthetic_fixture",
        origin_sha256="a" * 64,
        documents=(source, manifest, registry, report),
        report_fields=fields,
        statements=tuple(
            SelectedStatement(
                unit_id=v.field_id, field_id=v.field_id, start=0, end=len(v.text), quote=v.text
            )
            for v in fields
        ),
        messages=(SavedMessage(role="user", content="Authored prototype context"),),
    )
    old = partition_work(context, 6)
    declarations = {
        "work_sha256": old.fingerprint,
        "authored_by": "Test author",
        "declarations": [
            {
                "statement": s.model_dump(mode="json"),
                "field_pointer": v.pointer,
                "claim_predicates": ["observed_event"],
                "evidence_predicates": ["observed_event"],
                "material_components": [
                    {"description": "The whole event", "addressed_by_evidence_contract": True}
                ],
                "source_scopes": [{"role": "draft", "evidence_refs": ["S001"]}],
                "unresolved_qualifiers": [],
                "evidence_requirement": "Use the whole supplied scene.",
                "whole_claim_reviewed": True,
                "observation_basis": "not_applicable",
            }
            for s, v in zip(context.statements, fields, strict=True)
        ],
    }
    # Hash validated defaults, exactly as the real authoring component does.
    from open_hollywood_engine.evaluations.assessment_claim_scope import ClaimScopeDeclarations

    declarations = ClaimScopeDeclarations.model_validate_json(json.dumps(declarations)).model_dump(
        mode="json"
    )
    briefs = {
        "work_sha256": old.fingerprint,
        "declarations_sha256": canonical_sha256(declarations),
        "authored_by": "Test author",
        "briefs": [
            {
                "unit_id": v.field_id,
                "question": "Is this whole event established?",
                "temporal_scope": "Earlier scene",
                "source_authority": "The complete earlier scene",
                "evidence_obligation": "Cite the supplied source; copying is not semantic proof.",
            }
            for v in fields
        ],
    }
    authority = {
        "work_sha256": old.fingerprint,
        "request_sha256": "b" * 64,
        "declarations_sha256": canonical_sha256(declarations),
        "authored_by": "Test author",
        "origin_sha256": "c" * 64,
        "historical_sources": [source.model_dump(mode="json")],
        "bindings": [
            {
                "evidence_ref": "S001",
                "historical_span": {
                    k: v
                    for k, v in location.model_dump(mode="json").items()
                    if k not in ("ref", "paragraph")
                },
                "excerpt_visibility": "shown",
                "historical_body_visibility": "shown",
                "visibility_basis": "Complete authored source in the request.",
            }
        ],
        "claims": [
            {
                "unit_id": v.field_id,
                "obligations": [
                    {
                        "component_index": 0,
                        "requirement": "The whole event",
                        "predicates": ["observed_event"],
                        "source_roles": ["draft"],
                        "example_refs": ["S001"],
                    }
                ],
            }
            for v in fields
        ],
    }
    base = {
        "sources": [source.model_dump(mode="json")],
        "manifest": json.loads(manifest.content_json),
        "registry": registry.model_dump(mode="json"),
        "whole_claims": {v.field_id: v.text for v in fields},
        "work_briefs": briefs["briefs"],
    }
    sections = [
        ("Sources", {k: v for k, v in base.items() if k not in ("whole_claims", "work_briefs")}),
        ("Claims and brief", {k: base[k] for k in ("whole_claims", "work_briefs")}),
    ]
    message = "\n".join(
        "## " + title + "\n\n````json\n" + json.dumps(value, ensure_ascii=False) + "\n````\n"
        for title, value in sections
    )
    context = context.model_copy(
        update={
            "messages": (
                SavedMessage(role="system", content="Authored read-only test"),
                SavedMessage(role="user", content=message),
            )
        }
    )
    work = partition_work(context, 6)
    messages = [m.model_dump(mode="json") for m in context.messages]
    wire = {"model": "authored-no-provider", "input": messages, "text": {}, "reasoning": {}}
    request: dict[str, Any] = {
        "trial": TRIAL,
        "family": "A",
        "condition": "B",
        "repeat": 1,
        "presentation_order": "SC",
        "work_sha256": work.fingerprint,
        "work_key": "A-B-SC",
        "batch_id": work.batches[0].batch_id,
        "unit_ids": [v.field_id for v in fields],
        "messages": messages,
        "wire": wire,
        "count_wire": wire,
    }
    request["request_sha256"] = canonical_sha256(request)
    scope = scope_for_batch(work, work.batches[0].batch_id, request["request_sha256"])
    final = json.dumps(
        {
            "assessments": {
                v.field_id: {
                    "support": "supported",
                    "evidence": ["S001"],
                    "reason": "The source describes closing; this is an authored test.",
                }
                for v in fields
            }
        }
    )
    receipt = AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=scope.request_sha256,
        attempt_id=TRIAL,
        status="valid",
        result_sha256=text_hash(final),
        assessed_unit_ids=scope.active_unit_ids,
        input_tokens=100,
        output_tokens=50,
        reasoning_tokens=10,
        active_seconds=1,
    )
    result = bind_assessment_result(work, scope, receipt, final)
    saved = {
        "trial": TRIAL,
        "request_sha256": scope.request_sha256,
        "work_key": request["work_key"],
        "status": "valid",
        "transport_requests": 2,
        "generation_dispatches": 1,
        "final": final,
        "completion_receipt": receipt.model_dump(mode="json"),
        "usage": {
            "input_tokens": 100,
            "output_tokens": 50,
            "reasoning_tokens": 10,
            "cached_input_tokens": 0,
        },
        "actual_billed_cost": None,
        "result": {"units": [u.model_dump(mode="json") for u in result.units]},
    }
    f.documents = {
        PREP + "/plan.json": {"authored": True},
        PREP + "/approval-M.json": {"authored": True},
        PREP + "/requests.json": {TRIAL: request},
        PREP + "/works.json": {request["work_key"]: work.model_dump(mode="json")},
        PREP + "/cases.json": {
            "A": {
                "base": base,
                "receipt": {"authored": "operator-only"},
                "source_work_sha256": old.fingerprint,
            }
        },
        CELL + "/request.json": request,
        CELL + "/receipt.json": saved,
        AUTHORED + "/packets/A-work.json": old.model_dump(mode="json"),
        AUTHORED + "/packets/A-declarations.json": declarations,
        AUTHORED + "/packets/A-briefs.json": briefs,
        AUTHORED + "/packets/A-authority.json": authority,
    }
    for i, body in enumerate(
        (
            {"input_tokens": 100},
            {
                "status": "completed",
                "incomplete_details": None,
                "output": [
                    {
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": final}],
                    }
                ],
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "output_tokens_details": {"reasoning_tokens": 10},
                    "input_tokens_details": {"cached_tokens": 0},
                },
            },
        ),
        1,
    ):
        path = "/v1/responses" + ("/input_tokens" if i == 1 else "")
        f.documents[CELL + f"/dispatch-{i}.json"] = {
            "path": path,
            "generation": i == 2,
            "body_sha256": canonical_sha256(wire),
        }
        f.documents[CELL + f"/response-{i}.json"] = {"path": path, "status": 200, "body": body}
    return f
