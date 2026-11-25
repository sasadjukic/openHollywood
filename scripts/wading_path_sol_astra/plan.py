"""Freeze six saved cases across two models and two diagnostic presentations."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require
from open_hollywood_engine.models.openai import _cost
from open_hollywood_engine.models.openai_catalog import OpenAIModelSpec

from scripts import ordinary_v61_capture as ledger
from scripts.q010_uncertainty_plan import (
    COUNT_SECONDS,
    GENERATION_SECONDS,
    REPO,
    Cell,
    digest,
    filename,
    schedule,
)
from scripts.wading_path_be import plan as base
from scripts.wading_path_sol_versions import plan as previous
from scripts.wading_path_sol_versions import regression
from scripts.wading_path_sol_versions.scoring import GOLD_SHA

ROOT = previous.ROOT.parent / "wading-path-sol-astra-scope-2026-11-25"
CASES = previous.CASES
MODELS = {"S": "gpt-6.2-sol", "A": "gpt-6.2-astra"}
ARMS = ("SB", "SX", "AB", "AX")
# Each quartet has its reverse. Every two arms precede one another three times each.
QUARTETS = (
    "SB AX SX AB",
    "AB SX AX SB",
    "SX AB SB AX",
    "AX SB AB SX",
    "AB SB AX SX",
    "SX AX SB AB",
)
ORDER = tuple(
    f"{case}-{arm}" for case, group in zip(CASES, QUARTETS, strict=True) for arm in group.split()
)
WALL_SECONDS = len(ORDER) * (COUNT_SECONDS + GENERATION_SECONDS)
TARGET = {
    "narrated": "Assess what the complete selected draft explicitly recounts during scene four. "
    "Limit any further conclusion about physical occurrence to what the cited account establishes.",
    "reached": "Assess whether the event occurred at any time during scene four. Identify "
    "the interval covered by the cited observation and explain its bearing on that claim.",
}
STOPS = (
    base.STOPS[0],
    "Admit all 24 serial counts globally before generation. Require a positive count within "
    "input, context and cost bounds. Stop at the first failed count. No retries, replacements, "
    "redirects, fallback or polling.",
    *base.STOPS[2:],
)
SCORING = {
    "eligibility": base.SCORING["eligibility"],
    "judgment": previous.SCORING["judgment"],
    "evidence": "Grade the reason and citations against the unchanged case criterion with "
    "model, presentation, order and returned label masked. Accept equivalent locators. "
    "A final gap alone is insufficient for all six scene-wide claims. Seal all eligible "
    "evidence grades before joining the returned labels.",
    "decision": "For each arm require both points on SE and SN and on each of XE, XN, VE, VN. "
    "Report baseline repeat recoveries separately. Compare models within B and X, and X "
    "against B within each model, for each axis and case. A candidate qualifies only as a "
    "within-scene signal. Missing cells make the comparison inconclusive. Ties are not gains.",
}
FILES = (
    *previous.FILES,
    "scripts/wading_path_sol_versions/regression.py",
    "scripts/wading_path_sol_astra/plan.py",
    "scripts/wading_path_sol_astra/run.py",
    "scripts/wading_path_sol_astra/scoring.py",
)


def specifications() -> dict[str, OpenAIModelSpec]:
    sol = previous.specifications()["62"]
    astra = OpenAIModelSpec.model_validate(
        sol.model_dump()
        | dict(
            model_identifier=MODELS["A"],
            response_model_identifiers=(MODELS["A"],),
            input_usd_per_million="8.00",
            cached_input_usd_per_million="0.40",
            output_usd_per_million="40.00",
        )
    )
    return {"S": sol, "A": astra}


def explicit_cell(baseline: Cell, predicate: str, versions: tuple[UUID, ...]) -> Cell:
    original = json.loads(baseline.wire.endpoints[1].body_utf8)
    user = json.loads(original["input"][1]["content"])
    require("assessment_target" not in user["claim_scope"], "scope_already_present")
    declaration = user["claim_scope"] | {"assessment_target": TARGET[predicate]}
    explicit = base.render(
        baseline.work,
        dict(
            unit="A001",
            arm="X",
            work_sha256=baseline.work.fingerprint,
            declaration=declaration,
            brief=user["work_brief"],
        ),
        versions,
    )
    changed = json.loads(explicit.wire.endpoints[1].body_utf8)
    require(
        json.loads(changed["input"][1]["content"]) == user | {"claim_scope": declaration},
        "scope_presentation_drift",
    )
    return explicit


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    capture = regression.verified(regression.ARCHIVE)
    run = capture / "run"
    history = json.loads(_read(run / "plan.json"))
    historical = tuple(UUID(v) for v in history["historical_source_versions"])
    specs = specifications()
    assets = {
        k: _read(run / k)
        for k in ("gold.json", "evidence-criteria.json", "evidence-form-schema.json")
    }
    require(digest(assets["gold.json"]) == GOLD_SHA, "wading_gold_changed")
    assets["scoring.json"] = encoded(SCORING)
    rendered = {}
    for baseline in regression.archived_cells(capture):
        case, arm = baseline.name.split("-")
        if arm != "62":
            continue
        for end in baseline.wire.endpoints:
            require(
                end.body_utf8.encode() == _read(run / "requests" / filename(baseline, end)),
                "historical_baseline_drift",
            )
        versions = (*historical, UUID(history["assessment_draft_versions"][case]))
        explicit = explicit_cell(baseline, CASES[case][1], versions)
        for presentation, cell in (("B", baseline), ("X", explicit)):
            for model, spec in specs.items():
                name = f"{case}-{model}{presentation}"
                rendered[name] = (
                    Cell(name, cell.work, cell.wire)
                    if presentation == "B" and model == "S"
                    else previous.paired_cell(cell, name, spec, versions)
                )
    cells = [rendered[k] for k in ORDER]
    slots = []
    for i, (cell, end) in enumerate(schedule(cells), 1):
        path = "requests/" + filename(cell, end)
        assets[path] = end.body_utf8.encode()
        slots.append(
            dict(
                slot=i,
                cell=cell.name,
                filename=path,
                expected_model=cell.wire.model_spec.model_identifier,
                http_body_bytes=len(assets[path]),
                work_sha256=cell.work.fingerprint,
                native_request_sha256=cell.wire.native_request_sha256,
                **end.model_dump(mode="json", exclude={"body_utf8"}),
            )
        )
    costs = {m: _cost(s, base.INPUT, base.OUTPUT) for m, s in specs.items()}
    manifest = dict(
        contract="wading-path-sol-astra-assessment-scope-1",
        live_directory=ROOT.relative_to(REPO).as_posix(),
        archive_sha256=regression.SEAL,
        historical_approval_sha256=regression.APPROVAL,
        models=MODELS,
        model_specs={m: s.model_dump(mode="json") for m, s in specs.items()},
        reasoning="high",
        explicit_scope=TARGET,
        paired_cases=CASES,
        ordered_cells=ORDER,
        slots=slots,
        stops=STOPS,
        gold_sha256=GOLD_SHA,
        **{
            k: history[k]
            for k in (
                "historical_source_versions",
                "historical_source_binding",
                "assessment_draft_versions",
                "fixed_stop",
                "rehearsal_gold_sha256",
            )
        },
        budget=dict(
            input_counts=24,
            max_generations=24,
            retries=0,
            counts_per_arm=6,
            max_generations_per_arm=6,
            input_per_generation=base.INPUT,
            output_per_generation=base.OUTPUT,
            aggregate_generation_input=24 * base.INPUT,
            aggregate_generation_output=24 * base.OUTPUT,
            count_seconds=COUNT_SECONDS,
            generation_seconds=GENERATION_SECONDS,
            wall_seconds=WALL_SECONDS,
            max_usd_per_generation={m: str(v) for m, v in costs.items()},
            per_model_generation_usd={m: str(12 * v) for m, v in costs.items()},
            aggregate_generation_usd=str(12 * sum(costs.values())),
        ),
        implementation={p: ledger.file_hash(REPO / p) for p in FILES},
        members={k: digest(v) for k, v in assets.items()},
    )
    return cells, assets, encoded(manifest)


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
