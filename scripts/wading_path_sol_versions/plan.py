"""Freeze six identical B tasks on each of two Sol models with one global count barrier."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource
from open_hollywood_engine.evaluations.assessment_result import (
    _registry,
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.review_evidence import require, text_hash
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
from open_hollywood_engine.models.openai_catalog import OpenAIModelSpec, builtin_model_specs

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
from scripts.wading_path_visit_position import narration_event as rehearsal
from scripts.wading_path_visit_position import plan as prior_plan
from scripts.wading_path_visit_position import regression

ROOT = base.ROOT.parent / "wading-path-sol-versions-narration-event-2026-11-25"
MODELS = {"61": MODEL, "62": "gpt-6.2-sol"}
# Alternate the first model within matched pairs in both stages.
CASES = {
    "SN": ("stop", "narrated"),
    "XE": ("exclusion", "reached"),
    "VN": ("visit", "narrated"),
    "SE": ("stop", "reached"),
    "XN": ("exclusion", "narrated"),
    "VE": ("visit", "reached"),
}
ORDER = tuple(
    f"{case}-{arm}"
    for i, case in enumerate(CASES)
    for arm in (("61", "62") if i % 2 == 0 else ("62", "61"))
)
WALL_SECONDS = len(ORDER) * (COUNT_SECONDS + GENERATION_SECONDS)
FILES = (
    *prior_plan.FILES,
    "scripts/wading_path_visit_position/regression.py",
    "scripts/wading_path_visit_position/narration_event.py",
    "tests/fixtures/wading_path_narration_event_gold.json",
    "scripts/wading_path_sol_versions/plan.py",
    "scripts/wading_path_sol_versions/run.py",
    "scripts/wading_path_sol_versions/scoring.py",
)
STOPS = (
    base.STOPS[0],
    "All twelve serial counts, six per exact model, must pass before any generation. "
    "Stop globally on the first failure. No retries, fallback, redirects, polling or replacement.",
    *base.STOPS[2:],
)
SCORING = dict(
    eligibility=base.SCORING["eligibility"],
    judgment="Exact whole-claim support label scores one.",
    evidence="Grade each reason and its cited draft against the frozen case criterion before "
    "revealing the model, order or returned label. A final gap alone fails every scene-wide claim.",
    decision="Report both axes and paired changes for all six cases. A missing eligible "
    "assessment makes the comparison inconclusive. Report SE recovery separately, SN and each "
    "retrospective control, including ties and losses. One observation per model and claim.",
)


def specifications() -> dict[str, OpenAIModelSpec]:
    legacy = builtin_model_specs()[MODEL]
    # Diagnostic-only spec with short-context prices and the default 30-minute cache-write bound.
    current = OpenAIModelSpec(
        model_identifier=MODELS["62"],
        response_model_identifiers=(MODELS["62"],),
        context_window=1_050_000,
        max_output_tokens=128_000,
        max_input_tokens=272_000,
        supports_structured_output=True,
        reasoning_efforts=("high",),
        default_reasoning_effort="high",
        input_usd_per_million="2.00",
        cached_input_usd_per_million="0.10",
        output_usd_per_million="10.00",
        input_charge_multiplier="1.25",
        pricing_version="openai-standard-2026-11-25",
    )
    return {"61": legacy, "62": current}


def paired_cell(cell: Cell, name: str, spec: OpenAIModelSpec, versions: tuple[UUID, ...]) -> Cell:
    body = json.loads(cell.wire.endpoints[1].body_utf8)
    system, user = (m["content"] for m in body["input"])
    work = cell.work
    request_id = digest(
        encoded(
            [
                work.fingerprint,
                system,
                user,
                spec.model_identifier,
                "high",
                base.INPUT,
                base.OUTPUT,
                base.REF_PATTERN,
            ]
        )
    )
    scope = scope_for_batch(work, cell.wire.batch_id, request_id)
    request = ModelRequest(
        provider="openai",
        deployment=ModelDeployment.CLOUD,
        model_identifier=spec.model_identifier,
        invocation=InvocationContext(
            "endpoint_fact_assessment", "wading-path-saved-review-assessment-1", versions
        ),
        messages=(ModelMessage(MessageRole.SYSTEM, system), ModelMessage(MessageRole.USER, user)),
        settings=ModelSettings(thinking="high"),
        budget=ModelCallBudget(base.INPUT, base.OUTPUT, _cost(spec, base.INPUT, base.OUTPUT)),
        response_schema=assessment_response_schema(work, scope),
    )
    wire = base.compact_registry_schema(
        _prepare_wire(work, scope, request, spec, guard=None), "A001"
    )
    for a, b in zip(cell.wire.endpoints, wire.endpoints, strict=True):
        require(
            json.loads(b.body_utf8) == json.loads(a.body_utf8) | {"model": spec.model_identifier},
            "unpaired_model_request",
        )
    return Cell(name, work, wire)


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    capture = regression.verified(regression.ARCHIVE)
    key = json.loads(_read(REPO / "tests/fixtures/wading_path_narration_event_gold.json"))
    prose = rehearsal.sources(regression.ARCHIVE, key)
    source = IntakeSource.model_validate_json(_read(capture / "source/intake.json"))
    previous = json.loads(_read(capture / "run/plan.json"))
    versions = tuple(UUID(v) for v in previous["historical_source_versions"])
    selected = {}
    for ending, draft in prose.items():
        info = key["endings"][ending]
        work = observations.selected_work(source, "Q008", draft, info["version"], True)
        location = next(r for r in _registry(work).entries if r.ref == "E1420")
        require(
            location.quote == draft
            and location.document_version == info["version"]
            and location.field_sha256 == info["prose_sha256"] == text_hash(draft),
            "selected_draft_binding",
        )
        selected[ending] = work
    specs = specifications()
    pairs = {}
    rows = {}
    for case, (ending, predicate) in CASES.items():
        info = key["endings"][ending]
        invoked = (*versions, UUID(info["version"]))
        claim = key["claims"][predicate]
        first = previous_plan.authored_cell(selected[ending], claim, invoked)
        pairs[case + "-61"] = Cell(case + "-61", first.work, first.wire)
        pairs[case + "-62"] = paired_cell(first, case + "-62", specs["62"], invoked)
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
    cells = [pairs[k] for k in ORDER]
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
                expected_model=cell.wire.model_spec.model_identifier,
                filename=path,
                http_body_bytes=len(assets[path]),
                native_request_sha256=cell.wire.native_request_sha256,
                work_sha256=cell.work.fingerprint,
                **end.model_dump(mode="json", exclude={"body_utf8"}),
            )
        )
    costs = {k: _cost(spec, base.INPUT, base.OUTPUT) for k, spec in specs.items()}
    return (
        cells,
        assets,
        encoded(
            dict(
                contract="wading-path-narration-event-sol-versions-b-1",
                live_directory=ROOT.relative_to(REPO).as_posix(),
                models=MODELS,
                reasoning="high",
                model_specs={k: v.model_dump(mode="json") for k, v in specs.items()},
                historical_source_versions=previous["historical_source_versions"],
                historical_source_binding=previous["historical_source_binding"],
                assessment_draft_versions={k: r["draft_version"] for k, r in rows.items()},
                archive_sha256=regression.SEAL,
                paired_cases=CASES,
                fixed_stop=key["fixed_stop"],
                rehearsal_gold_sha256=rehearsal.GOLD_SHA,
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
                    per_model_counts=6,
                    per_model_max_generations=6,
                    max_usd_per_generation={k: str(v) for k, v in costs.items()},
                    per_model_generation_usd={k: str(v * 6) for k, v in costs.items()},
                    aggregate_generation_usd=str(6 * sum(costs.values())),
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
