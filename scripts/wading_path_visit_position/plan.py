"""Freeze six one-claim B requests with inherited gold and independent evidence criteria."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource
from open_hollywood_engine.evaluations.assessment_result import _registry
from open_hollywood_engine.evaluations.review_evidence import require, text_hash
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
from scripts.wading_path_three_claims import plan as previous_plan
from scripts.wading_path_three_claims import regression, visit_position

ROOT = base.ROOT.parent / "wading-path-sol-high-visit-position-2026-11-25"
CASES = {
    "S1": ("stop", "reached"),
    "X2": ("exclusion", "at_cut"),
    "A1": ("arrival", "reached"),
    "S2": ("stop", "at_cut"),
    "X1": ("exclusion", "reached"),
    "A2": ("arrival", "at_cut"),
}
ORDER = tuple(case + "-B" for case in CASES)
WALL_SECONDS = len(ORDER) * (COUNT_SECONDS + GENERATION_SECONDS)
FILES = (
    *previous_plan.FILES,
    "scripts/wading_path_three_claims/regression.py",
    "scripts/wading_path_three_claims/visit_position.py",
    "scripts/wading_path_visit_position/plan.py",
    "scripts/wading_path_visit_position/run.py",
    "scripts/wading_path_visit_position/scoring.py",
)
STOPS = (
    base.STOPS[0],
    "All six serial input counts must return HTTP 200 and a positive in-budget count before "
    "any generation. No retries, replacements, redirects, polling or fallback.",
    *base.STOPS[2:],
)
SCORING = {
    "eligibility": base.SCORING["eligibility"],
    "judgment": base.SCORING["judgment"],
    "evidence": base.SCORING["evidence"] + " For the exclusion visit, require the explanation "
    "to locate the observation covering the whole scene. Citing E1420 and describing only "
    "the endpoint gap earns zero evidence even with the correct label.",
    "decision": "Report both axes for every cell. A missing eligible generation makes the "
    "comparison inconclusive. A miss on either axis of either explicit-arrival control holds "
    "that control. Any other miss holds the claim scope. Six joint passes establish the "
    "measured-stop versus exclusion distinction on these drafts only.",
}


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    capture = regression.verified(regression.ARCHIVE)
    key = json.loads(_read(REPO / "tests/fixtures/wading_path_visit_position_gold.json"))
    prose = visit_position.drafts(regression.ARCHIVE, key)
    source = IntakeSource.model_validate_json(_read(capture / "source/intake.json"))
    previous = json.loads(_read(capture / "run/plan.json"))
    versions = tuple(UUID(v) for v in previous["historical_source_versions"])
    selected = {}
    for ending in ("stop", "exclusion", "arrival"):
        info = key["endings"][ending]
        draft = observations.selected_work(source, "Q008", prose[ending], info["version"], True)
        registry = _registry(draft).entries
        location = next(r for r in registry if r.ref == "E1420")
        require(
            location.quote == prose[ending]
            and location.document_version == info["version"]
            and location.field_sha256 == info["prose_sha256"] == text_hash(prose[ending]),
            "selected_draft_binding",
        )
        selected[ending] = draft

    cells = []
    rows: dict[str, dict[str, Any]] = {}
    for case, (ending, predicate) in CASES.items():
        info = key["endings"][ending]
        invoked = (*versions, UUID(info["version"]))
        claim = key["claims"][predicate]
        cell = previous_plan.authored_cell(selected[ending], claim, invoked)
        name = case + "-B"
        cells.append(Cell(name, cell.work, cell.wire))
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
                contract="wading-path-visit-position-b-1",
                live_directory=ROOT.relative_to(REPO).as_posix(),
                model=MODEL,
                reasoning="high",
                model_spec=spec.model_dump(mode="json"),
                historical_source_versions=previous["historical_source_versions"],
                historical_source_binding=previous["historical_source_binding"],
                assessment_draft_versions={k: r["draft_version"] for k, r in rows.items()},
                archive_sha256=regression.SEAL,
                exclusion_parent_version=key["endings"]["exclusion"]["parent_version"],
                rehearsal_gold_sha256=visit_position.GOLD_SHA,
                gold_sha256=digest(assets["gold.json"]),
                ordered_cells=ORDER,
                slots=slots,
                stops=STOPS,
                budget=dict(
                    input_counts=len(ORDER),
                    max_generations=len(ORDER),
                    retries=0,
                    input_per_generation=base.INPUT,
                    output_per_generation=base.OUTPUT,
                    aggregate_generation_input=len(ORDER) * base.INPUT,
                    aggregate_generation_output=len(ORDER) * base.OUTPUT,
                    max_usd_per_generation=str(cost),
                    aggregate_generation_usd=str(len(ORDER) * cost),
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
