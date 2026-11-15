"""Small authored source fixtures, independent of the private admitted scene archive."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from open_hollywood_api.services import assessment_authored_source as service
from open_hollywood_api.services.assessment_completion import _sha
from open_hollywood_engine.evaluations.assessment_authored_source import (
    ORIGIN,
    AuthoredSource,
    _document,
    fixture_template,
)
from open_hollywood_engine.evaluations.assessment_authority import AssessmentAuthority
from open_hollywood_engine.evaluations.assessment_claim_scope import ClaimScopeDeclarations
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceLocation,
    EvidenceRegistry,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentContext,
    ReportField,
    SelectedStatement,
    partition_work,
)
from open_hollywood_engine.evaluations.assessment_work_brief import AssessmentWorkBriefs
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import SavedMessage, text_hash


def members(family: str) -> dict[str, bytes]:
    body = f"{family}: Mara returned the key. The door remained shut. ``` Ω"
    document = _document(family + "-draft", "source", {"text": body})
    ledger = {
        "origin": ORIGIN,
        "family": family,
        "source_authentication": "authored_local_construction_only",
        "historical_model_visibility": "not_applicable_no_model_review",
    }
    registry = EvidenceRegistry(
        entries=(
            EvidenceLocation(
                ref="S001",
                document_id=document.identity,
                document_version=document.version,
                document_sha256=document.content_sha256,
                field_pointer="/text",
                field_sha256=text_hash(body),
                start=0,
                end=len(body),
                quote=body,
            ),
        )
    )
    texts = (
        "Mara returned the key.",
        "Mara opened the door.",
        "Mara returned the key and the door stayed shut.",
    )
    report: dict[str, Any] = {"claims": list(texts), "summary": "The atmosphere feels restrained."}
    packet = {
        "source_manifest": ledger,
        "sources": [document.model_dump(mode="json")],
        "whole_authored_review": report,
        "evidence_registry": registry.model_dump(mode="json"),
    }
    identity = canonical_sha256(packet)
    fields = tuple(
        ReportField(field_id=f"Q{i:03d}", pointer=f"/claims/{i - 1}", text=t)
        for i, t in enumerate(texts, 1)
    )
    work = partition_work(
        AssessmentContext(
            provenance="synthetic_fixture",
            origin_sha256=identity,
            documents=(
                document,
                _document(family + "-manifest", "source", ledger),
                _document(family + "-report", "report", report),
                _document(family + "-registry", "registry", registry.model_dump(mode="json")),
            ),
            report_fields=(
                *fields,
                ReportField(field_id="Q004", pointer="/summary", text=report["summary"]),
            ),
            statements=tuple(
                SelectedStatement(
                    unit_id=f.field_id, field_id=f.field_id, start=0, end=len(f.text), quote=f.text
                )
                for f in fields
            ),
            messages=(SavedMessage(role="user", content=encoded(packet).decode()),),
        ),
        maximum_units=3,
    )
    declarations = ClaimScopeDeclarations.model_validate_json(
        encoded(
            {
                "work_sha256": work.fingerprint,
                "authored_by": ORIGIN,
                "declarations": [
                    {
                        "statement": s.model_dump(mode="json"),
                        "field_pointer": f.pointer,
                        "claim_predicates": ["observed_event"],
                        "evidence_predicates": ["observed_event"],
                        "material_components": [
                            {
                                "description": "Is the entire claim established?",
                                "addressed_by_evidence_contract": True,
                            }
                        ],
                        "source_scopes": [
                            {
                                "coverage": "complete_fields",
                                "role": "draft",
                                "evidence_refs": ["S001"],
                            }
                        ],
                        "observation_basis": "not_applicable",
                        "unresolved_qualifiers": [],
                        "whole_claim_reviewed": True,
                        "evidence_requirement": "All clauses, using the complete draft.",
                    }
                    for s, f in zip(work.context.statements, fields, strict=True)
                ],
            }
        )
    )
    declaration_sha = canonical_sha256(declarations.model_dump(mode="json"))
    briefs = AssessmentWorkBriefs.model_validate_json(
        encoded(
            {
                "work_sha256": work.fingerprint,
                "declarations_sha256": declaration_sha,
                "authored_by": ORIGIN,
                "briefs": [
                    {
                        "unit_id": s.unit_id,
                        "question": "Is the entire claim established?",
                        "temporal_scope": "Current scene.",
                        "source_authority": "The complete draft.",
                        "evidence_obligation": "All clauses, not merely a matching quote.",
                    }
                    for s in work.context.statements
                ],
            }
        )
    )
    authority = AssessmentAuthority.model_validate_json(
        encoded(
            {
                "work_sha256": work.fingerprint,
                "request_sha256": identity,
                "declarations_sha256": declaration_sha,
                "authored_by": ORIGIN,
                "origin_sha256": identity,
                "claims": [
                    {
                        "unit_id": s.unit_id,
                        "obligations": [
                            {
                                "component_index": 0,
                                "requirement": "Is the entire claim established?",
                                "predicates": ["observed_event"],
                                "source_roles": ["draft"],
                                "example_refs": ["S001"],
                            }
                        ],
                    }
                    for s in work.context.statements
                ],
            }
        )
    )
    return {
        name: encoded(value)
        for name, value in {
            "work.json": work.model_dump(mode="json"),
            "scope.json": scope_for_batch(work, work.batches[0].batch_id, identity).model_dump(
                mode="json"
            ),
            "declarations.json": declarations.model_dump(mode="json"),
            "briefs.json": briefs.model_dump(mode="json"),
            "authority.json": authority.model_dump(mode="json"),
            "source-packet.json": packet,
        }.items()
    }


def make_archive(root: Path) -> service.Registration:
    folder = root / "admitted"
    folder.mkdir(parents=True)
    for family in ("F01", "F02", "F03"):
        child = folder / family
        child.mkdir()
        for name, raw in members(family).items():
            (child / name).write_bytes(raw)
        for name in ("admission.json", "preview.json", "view.md"):
            (child / name).write_text("OPERATOR_ONLY_GOLD_SENTINEL", encoding="utf-8")
    for name in ("admission-decisions.json", "cases-and-gold.md", "readiness.json"):
        (folder / name).write_text("OPERATOR_ONLY_GOLD_SENTINEL", encoding="utf-8")
    for name in ("material.py", "admit.py"):
        (root / name).write_text(
            "raise AssertionError('archive code must never execute')\n", encoding="utf-8"
        )
    return reseal(root)


def reseal(root: Path) -> service.Registration:
    folder = root / "admitted"
    manifest = {
        "contract": "assessment-authored-admission-bundle-1",
        "origin": ORIGIN,
        "helper_sha256": _sha((root / "admit.py").read_bytes()),
        "material_sha256": _sha((root / "material.py").read_bytes()),
        "members_sha256": {
            p.relative_to(folder).as_posix(): _sha(p.read_bytes())
            for p in folder.rglob("*")
            if p.is_file() and p.name != "manifest.json"
        },
        "live_calls": 0,
        "model_evidence": False,
        "writer_dispatch_authorized": False,
    }
    raw = encoded(manifest)
    (folder / "manifest.json").write_bytes(raw)
    return service.Registration(service.SOURCE_ID, root, _sha(raw))


def submission(source: AuthoredSource) -> dict[str, Any]:
    value: dict[str, Any] = dict(fixture_template(source))
    value["authored_by"] = "Test fixture author; no semantic validation"
    value["raw_final"] = encoded(
        {
            "assessments": {
                u.unit_id: {
                    "support": label,
                    "evidence": ["S001"],
                    "reason": "Authored transport fixture only.",
                }
                for u, label in zip(
                    source.work.context.statements,
                    ("supported", "unsupported", "uncertain"),
                    strict=True,
                )
            }
        }
    ).decode()
    return value
