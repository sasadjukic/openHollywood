"""Freeze seven full-context Sol-high requests and the independent operator materials."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_claim_scope import (
    ClaimScopeDeclaration,
    DeclaredSourceScope,
    MaterialComponent,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource, _document
from open_hollywood_engine.evaluations.assessment_result import _registry
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentContext,
    AssessmentWork,
    ReportField,
    SelectedStatement,
    partition_work,
)
from open_hollywood_engine.evaluations.assessment_work_brief import AuthoredWorkBrief
from open_hollywood_engine.evaluations.review_evidence import require, strict_object, text_hash
from open_hollywood_engine.models.openai import _cost

from scripts import ordinary_v61_capture as ledger
from scripts.fresh_endpoint_repeat.scoring import Decisions
from scripts.q010_uncertainty_plan import (
    COUNT_SECONDS,
    GENERATION_SECONDS,
    MODEL,
    REPO,
    Cell,
    digest,
    filename,
    schedule,
)
from scripts.wading_path_be import plan as base
from scripts.wading_path_observations import plan as observations
from scripts.wading_path_observations import regression, three_claims

ROOT = base.ROOT.parent / "wading-path-three-claims-sol-high-2026-11-24"
CASES = {
    "N1": ("original", "narrated"),
    "R2": ("retreat", "reached"),
    "P1": ("original", "at_cut"),
    "N2": ("retreat", "narrated"),
    "R1": ("original", "reached"),
    "P2": ("retreat", "at_cut"),
}
ORDER = ("N1-B", "R2-B", "P1-B", "Q008-B", "N2-B", "R1-B", "P2-B")
WALL_SECONDS = len(ORDER) * (COUNT_SECONDS + GENERATION_SECONDS)
FILES = (
    *observations.FILES,
    "scripts/wading_path_observations/regression.py",
    "scripts/wading_path_observations/three_claims.py",
    "scripts/wading_path_three_claims/plan.py",
    "scripts/wading_path_three_claims/run.py",
    "scripts/wading_path_three_claims/scoring.py",
)
STOPS = (
    base.STOPS[0],
    "All seven serial input counts must return HTTP 200 and a positive in-budget count before "
    "any generation. No retries, replacements, redirects, polling or fallback.",
    *base.STOPS[2:],
)
SCORING = {
    "eligibility": base.SCORING["eligibility"],
    "judgment": base.SCORING["judgment"],
    "evidence": base.SCORING["evidence"],
    "decision": "Report judgment and evidence for each cell, grouped by ending, with Q008 "
    "separate. A missing eligible cell makes the diagnostic inconclusive. A Q008 miss holds "
    "the control. A miss on either axis of any authored cell holds that claim scope. All "
    "seven joint passes demonstrate discrimination on these two drafts only.",
}


def authored_cell(draft: AssessmentWork, claim: str, versions: tuple[UUID, ...]) -> Cell:
    """Bind one authored statement and preserve the historical review as a complete source."""
    ctx = draft.context
    historical = next(d for d in ctx.documents if d.kind == "report")
    unit, pointer = "A001", "/authored_claim"
    field = ReportField(field_id=unit, pointer=pointer, text=claim)
    statement = SelectedStatement(unit_id=unit, field_id=unit, start=0, end=len(claim), quote=claim)
    report = _document(
        "authored-diagnostic-claim", "report", {"authored_claim": claim}, text_hash(claim)
    )
    docs = tuple(
        historical.model_copy(update={"kind": "source"}) if d == historical else d
        for d in ctx.documents
    )
    context = AssessmentContext.model_validate(
        ctx.model_dump()
        | dict(
            origin_sha256=canonical_sha256([ctx.fingerprint, report.content_sha256]),
            provenance="synthetic_fixture",
            documents=(*docs, report),
            report_fields=(field,),
            statements=(statement,),
            declared_links=(),
        )
    )
    work = partition_work(context, 1)
    brief = AuthoredWorkBrief(
        unit_id=unit,
        question="Does the selected scene-four draft establish the whole active claim?",
        temporal_scope="Use the interval or instant specified by the claim.",
        source_authority="Use E1420, the complete selected scene-four draft. The saved review "
        "and its original request supply historical context.",
        evidence_obligation="Cite the selected draft and explain what it establishes for "
        "the whole claim.",
    )
    declaration = ClaimScopeDeclaration(
        statement=statement,
        field_pointer=pointer,
        whole_claim_reviewed=True,
        claim_predicates=("observed_event",),
        evidence_predicates=("observed_event",),
        observation_basis="not_applicable",
        source_scopes=(
            DeclaredSourceScope(role="draft", coverage="complete_fields", evidence_refs=("E1420",)),
        ),
        material_components=(
            MaterialComponent(description=claim, addressed_by_evidence_contract=True),
        ),
        evidence_requirement=brief.evidence_obligation,
    )
    return base.render(
        work,
        dict(
            unit=unit,
            arm="B",
            work_sha256=work.fingerprint,
            declaration=declaration.model_dump(mode="json"),
            brief=brief.model_dump(mode="json"),
        ),
        versions,
    )


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    capture = regression.verified(regression.ARCHIVE)
    key = json.loads(_read(REPO / "tests/fixtures/wading_path_three_claims_gold.json"))
    prose = three_claims.drafts(regression.ARCHIVE, key)
    source = IntakeSource.model_validate_json(_read(capture / "source/intake.json"))
    previous = json.loads(_read(capture / "run/plan.json"))
    versions = tuple(UUID(v) for v in previous["historical_source_versions"])
    selected = {}
    for ending in ("original", "retreat"):
        info = key["endings"][ending]
        draft = observations.selected_work(
            source, "Q008", prose[ending], info["version"], ending == "retreat"
        )
        registry = _registry(draft).entries
        location = next(r for r in registry if r.ref == "E1420")
        require(
            location.quote == prose[ending]
            and location.document_version == info["version"]
            and location.field_sha256 == info["prose_sha256"],
            "selected_draft_binding",
        )
        selected[ending] = draft

    rendered = {}
    rows: dict[str, dict[str, Any]] = {}
    for case, (ending, predicate) in CASES.items():
        info = key["endings"][ending]
        invoked = versions if ending == "original" else (*versions, UUID(info["version"]))
        claim = key["claims"][predicate]
        cell = authored_cell(selected[ending], claim, invoked)
        name = case + "-B"
        rendered[name] = Cell(name, cell.work, cell.wire)
        label, criterion = info["cells"][predicate]
        rows[case] = dict(
            unit="A001",
            claim=claim,
            predicate=predicate,
            ending=ending,
            draft_version=info["version"],
            prose_sha256=info["prose_sha256"],
            gold=label,
            evidence_requirements=[criterion, key["scoring"]["evidence"]],
        )

    native = json.loads(_read(capture / "run/requests/Q008-B-generation.json"))
    packet = strict_object(native["input"][1]["content"])
    control = selected["original"]
    cell = base.render(
        control,
        dict(
            unit="Q008",
            arm="B",
            work_sha256=control.fingerprint,
            declaration=packet["claim_scope"],
            brief=packet["work_brief"],
        ),
        versions,
    )
    for end in cell.wire.endpoints:
        require(
            end.body_utf8.encode() == _read(capture / "run/requests" / filename(cell, end)),
            "q008_control_drift",
        )
    rendered[cell.name] = cell
    rows["Q008"] = json.loads(_read(capture / "run/gold.json"))["Q008"]
    cells = [rendered[name] for name in ORDER]
    assets = {
        "gold.json": encoded(rows),
        "evidence-criteria.json": encoded(
            {case: {k: v for k, v in row.items() if k != "gold"} for case, row in rows.items()}
        ),
        "scoring.json": encoded(SCORING),
        "evidence-form-schema.json": encoded(Decisions.model_json_schema()),
    }
    slots = []
    for i, (cell, end) in enumerate(schedule(cells), 1):
        path = "requests/" + filename(cell, end)
        assets[path] = end.body_utf8.encode()
        slots.append(
            dict(
                slot=i,
                cell=cell.name,
                filename=path,
                http_body_bytes=len(assets[path]),
                native_request_sha256=cell.wire.native_request_sha256,
                work_sha256=cell.work.fingerprint,
                **end.model_dump(mode="json", exclude={"body_utf8"}),
            )
        )
    spec = cells[0].wire.model_spec
    cost = _cost(spec, base.INPUT, base.OUTPUT)
    return (
        cells,
        assets,
        encoded(
            dict(
                contract="wading-path-three-claim-b-1",
                live_directory=ROOT.relative_to(REPO).as_posix(),
                model=MODEL,
                reasoning="high",
                model_spec=spec.model_dump(mode="json"),
                historical_source_versions=previous["historical_source_versions"],
                historical_source_binding=previous["historical_source_binding"],
                assessment_draft_versions={k: r["draft_version"] for k, r in rows.items()},
                archive_sha256=regression.SEAL,
                rehearsal_gold_sha256=three_claims.GOLD_SHA,
                gold_sha256=digest(assets["gold.json"]),
                ordered_cells=ORDER,
                slots=slots,
                stops=STOPS,
                budget=dict(
                    input_counts=7,
                    max_generations=7,
                    retries=0,
                    input_per_generation=base.INPUT,
                    output_per_generation=base.OUTPUT,
                    aggregate_generation_input=7 * base.INPUT,
                    aggregate_generation_output=7 * base.OUTPUT,
                    max_usd_per_generation=str(cost),
                    aggregate_generation_usd=str(7 * cost),
                    count_seconds=COUNT_SECONDS,
                    generation_seconds=GENERATION_SECONDS,
                    wall_seconds=WALL_SECONDS,
                ),
                implementation={p: ledger.file_hash(REPO / p) for p in FILES},
                members={k: digest(v) for k, v in assets.items()},
            )
        ),
    )


def issue(root: Path) -> str:
    _, assets, manifest = materials()
    _unlinked(root).mkdir(exist_ok=False)
    (root / "requests").mkdir()
    for name, raw in assets.items():
        _durable_write(root / name, raw)
    _durable_write(root / "plan.json", manifest)
    approval = digest(manifest)
    ledger.initialize_ledger(root, approval)
    return approval


def verify(root: Path, approval: str) -> list[Cell]:
    cells, assets, manifest = materials()
    require(
        digest(manifest) == approval and _read(root / "plan.json") == manifest,
        "approval_or_source_drift",
    )
    require(all(_read(root / k) == v for k, v in assets.items()), "frozen_member_drift")
    require(
        {p.name for p in (root / "requests").iterdir()}
        == {filename(c, e) for c, e in schedule(cells)},
        "request_inventory",
    )
    ledger.ledger_state(root, approval)
    return cells
