"""Freeze the six authored planetarium claims across four counterbalanced conditions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require, text_hash
from open_hollywood_engine.models.openai import _cost

from scripts import ordinary_v61_capture as ledger
from scripts.fresh_endpoint_repeat.scoring import Decisions
from scripts.q010_uncertainty_plan import (
    COUNT_SECONDS,
    GENERATION_SECONDS,
    REPO,
    Cell,
    digest,
    filename,
    schedule,
)
from scripts.wading_path_be.plan import INPUT, OUTPUT
from scripts.wading_path_sol_astra import plan as prior

from .presentation import BRIEF, render, version, work_for

ROOT = REPO / "data/diagnostics/planetarium-sol-astra-scope-2026-11-25"
FIXTURES = REPO / "tests/fixtures"
SOURCE = FIXTURES / "planetarium_scope_sources.json"
GOLD = FIXTURES / "planetarium_scope_gold.json"
SOURCE_SHA = "bd69f504eb6019d42d838b665fcfd21778b683acae871460928bfc85d0ed7b0b"
GOLD_SHA = "0f01440bde2b2f5013312c027b66cea829519fd81a8f9dead98a20212d8b73e7"
ARMS = prior.ARMS
TARGETS = ("OE", "ON")
CONTROLS = ("DE", "DN", "PE", "PN")
CASES = {
    "ON": ("open", "narration"),
    "DE": ("excluded", "event"),
    "PN": ("confirmed", "narration"),
    "OE": ("open", "event"),
    "DN": ("excluded", "narration"),
    "PE": ("confirmed", "event"),
}
# Reverse each former quartet so each analogous case sees the opposite order on transfer.
ORDER = tuple(
    f"{case}-{arm}"
    for case, group in zip(CASES, prior.QUARTETS, strict=True)
    for arm in reversed(group.split())
)
WALL_SECONDS = len(ORDER) * (COUNT_SECONDS + GENERATION_SECONDS)
SCORING = {
    "eligibility": prior.SCORING["eligibility"],
    "judgment": "One point for the exact frozen whole-claim label. A wrong label scores zero.",
    "evidence": "Mask arm, model, order and returned label. Resolve the cited passages on the "
    "exact selected version. Award one point for a reason meeting the case criterion, including "
    "the claim's time span. Equivalent locators count. A blank dome at closing alone fails "
    "every scene-wide claim. Seal every eligible evidence decision before joining labels.",
    "decision": "Incomplete delivery is inconclusive. AX must pass both axes on all six cases. "
    "Only AX passing both axes on OE then gives unique transfer. Any other OE joint pass is "
    "shared recovery. An AX miss on any axis holds escalation. Report Sol B recovery, Sol X "
    "parity, Astra B parity and four paired contrasts per case and axis. One family, one "
    "observation per arm and case. No automatic writer or production decision.",
}
FILES = tuple(
    dict.fromkeys(
        (
            *prior.FILES,
            "engine/open_hollywood_engine/evaluations/assessment_completion.py",
            "engine/open_hollywood_engine/evaluations/review_evidence.py",
            "engine/open_hollywood_engine/models/contracts.py",
            "scripts/planetarium_scope/presentation.py",
            "scripts/planetarium_scope/plan.py",
            "scripts/planetarium_scope/run.py",
            "scripts/planetarium_scope/scoring.py",
        )
    )
)


def validate_gold(source: dict[str, Any], key: dict[str, Any]) -> None:
    require(set(key) == set(CASES), "planetarium_cases")
    for case, (history, kind) in CASES.items():
        prose = source["drafts"][history]
        row = key[case]
        require(
            row["claim"] == source["claims"][kind]
            and row["history"] == history
            and row["kind"] == kind
            and row["prose_sha256"] == text_hash(prose)
            and row["draft_version"] == version("draft", text_hash(prose)),
            "planetarium_gold_binding",
        )
        for witness in row["spans"].values():
            require(
                witness["quote"] == prose[witness["start"] : witness["end"]], "planetarium_witness"
            )


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    raw, key_raw = _read(SOURCE), _read(GOLD)
    require(
        digest(raw) == SOURCE_SHA and digest(key_raw) == GOLD_SHA,
        "planetarium_source_or_gold_drift",
    )
    source, key = json.loads(raw), json.loads(key_raw)
    validate_gold(source, key)
    specs = prior.specifications()
    works = {case: work_for(source, history, kind) for case, (history, kind) in CASES.items()}
    cells = []
    for name in ORDER:
        case, arm = name.split("-")
        cells.append(render(name, works[case], CASES[case][1], specs[arm[0]]))
    assets = {
        "sources.json": raw,
        "gold.json": key_raw,
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
                expected_model=cell.wire.model_spec.model_identifier,
                work_sha256=cell.work.fingerprint,
                native_request_sha256=cell.wire.native_request_sha256,
                http_body_bytes=len(assets[path]),
                **end.model_dump(mode="json", exclude={"body_utf8"}),
            )
        )
    costs = {k: _cost(s, INPUT, OUTPUT) for k, s in specs.items()}
    manifest = dict(
        contract="planetarium-sol-astra-scope-transfer-1",
        provenance="authored diagnostic",
        live_directory=ROOT.relative_to(REPO).as_posix(),
        source_sha256=SOURCE_SHA,
        gold_sha256=GOLD_SHA,
        model_specs={k: s.model_dump(mode="json") for k, s in specs.items()},
        reasoning="high",
        baseline=BRIEF.model_dump(mode="json"),
        explicit_scope={"narration": prior.TARGET["narrated"], "event": prior.TARGET["reached"]},
        paired_cases=CASES,
        source_versions={
            case: {d.identity: d.version for d in w.context.documents} for case, w in works.items()
        },
        ordered_cells=ORDER,
        slots=slots,
        stops=prior.STOPS,
        budget=dict(
            input_counts=24,
            max_generations=24,
            retries=0,
            counts_per_arm=6,
            max_generations_per_arm=6,
            input_per_generation=INPUT,
            output_per_generation=OUTPUT,
            aggregate_generation_input=24 * INPUT,
            aggregate_generation_output=24 * OUTPUT,
            max_usd_per_generation={k: str(v) for k, v in costs.items()},
            per_model_generation_usd={k: str(12 * v) for k, v in costs.items()},
            aggregate_generation_usd=str(12 * sum(costs.values())),
            count_seconds=COUNT_SECONDS,
            generation_seconds=GENERATION_SECONDS,
            wall_seconds=WALL_SECONDS,
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
    sha = digest(manifest)
    ledger.initialize_ledger(root, sha)
    return sha


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
