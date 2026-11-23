"""Freeze six rehearsed works, their independent scoring and twelve exact HTTP bodies."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentWork
from open_hollywood_engine.evaluations.review_evidence import require
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
from open_hollywood_engine.models.openai_catalog import builtin_model_specs

from scripts import ordinary_v61_capture as ledger
from scripts.q010_uncertainty_plan import (
    COUNT_SECONDS,
    GENERATION_SECONDS,
    MODEL,
    Cell,
    digest,
    filename,
    schedule,
)
from scripts.q011_arrival import plan as parent
from scripts.q011_arrival import scope_rehearsal as rehearsal
from scripts.q011_arrival import sources

ROOT = sources.DATA / "q011-scope-comparison-2026-11-23"
# The existing worksheet uses the prefix before the arm suffix as the case identifier.
CASES = {
    "AP": "approach-position",
    "AD": "approach-depiction",
    "RD": "arrival-depiction",
    "RP": "arrival-position",
    "SP": "stop-position",
    "SD": "stop-depiction",
}
WALL_SECONDS = len(CASES) * (COUNT_SECONDS + GENERATION_SECONDS)
STOPS = (
    "Verify approval, immutable sources, gold, scoring, implementation, all request bytes "
    "and an unused registered journal before dispatch.",
    "All six counts must return HTTP 200 and a positive, in-budget token count before generation.",
    "Stop globally on the first failed count or technical failure, HTTP error, invalid or "
    "duplicate JSON, model mismatch, refusal, incomplete output, bad unit or citation, missing "
    "required generation usage, or exceeded token, cost or time limit.",
    "Record intent before send. A timeout, cancellation or interruption consumes the run. "
    "Retain unknown usage. No retries, replacements, fallback, polling or redirects.",
    "Continue after a complete, validly bound semantic miss. Score every eligible generation.",
)
IMPLEMENTATION = (
    *parent.IMPLEMENTATION,
    "scripts/q011_arrival/regression.py",
    "scripts/q011_arrival/scope_rehearsal.py",
    "scripts/verify_q010_endpoint_controls.py",
    "scripts/q011_scope/plan.py",
    "scripts/q011_scope/run.py",
    "scripts/q011_scope/scoring.py",
    "engine/open_hollywood_engine/evaluations/assessment_completion.py",
    "engine/open_hollywood_engine/evaluations/assessment_authored_source.py",
    "engine/open_hollywood_engine/evaluations/review_evidence.py",
    "engine/open_hollywood_engine/models/contracts.py",
)


def render(works: dict[str, AssessmentWork]) -> list[Cell]:
    require(set(works) == set(CASES.values()), "q011_scope_case_inventory")
    spec = builtin_model_specs()[MODEL]
    budget = ModelCallBudget(parent.INPUT, parent.OUTPUT, _cost(spec, parent.INPUT, parent.OUTPUT))
    result = []
    for key, case in CASES.items():
        work = works[case]
        (batch,) = work.batches
        messages = tuple(
            ModelMessage(MessageRole(m.role), m.content) for m in work.context.messages
        )
        require(
            batch.unit_ids == (rehearsal.UNIT,)
            and [m.role for m in messages] == [MessageRole.SYSTEM, MessageRole.USER],
            "q011_scope_wire_scope",
        )
        versions = tuple(UUID(d.version) for d in work.context.documents if d.kind == "source")
        request_id = digest(encoded([work.fingerprint, MODEL, "high", parent.INPUT, parent.OUTPUT]))
        scope = scope_for_batch(work, batch.batch_id, request_id)
        request = ModelRequest(
            provider="openai",
            deployment=ModelDeployment.CLOUD,
            model_identifier=MODEL,
            invocation=InvocationContext("endpoint_fact_assessment", "q011-scope-b-1", versions),
            messages=messages,
            settings=ModelSettings(thinking="high"),
            budget=budget,
            response_schema=assessment_response_schema(work, scope),
        )
        result.append(Cell(key + "-B", work, _prepare_wire(work, scope, request, spec, guard=None)))
    return result


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    packets = rehearsal.packets()
    works = {
        k: w for ending, p in packets.items() for k, w in rehearsal.work_pair(ending, p).items()
    }
    cells = render(works)
    gold = _read(rehearsal.ROOT / "gold.json")
    require(
        digest(gold) == rehearsal.GOLD and gold == encoded(rehearsal.gold(packets)),
        "q011_scope_gold_drift",
    )
    sealed = json.loads(gold)
    rules = sealed["rules"] | {
        "eligibility": "Score a complete, budgeted and source-bound generation in a closed "
        "observed journal. Ineligible or unused slots are unscored on both axes.",
        "evidence_join": "Read the cited version, paragraph, plan fields and reason with the "
        "returned label withheld. Seal a pass/fail decision and passage-specific basis for "
        "every eligible scoring ID before joining exact labels to gold.",
        "decision": "Report the original two cases and the four controls separately. All six "
        "eligible cases must pass both axes for grounded_scope_split. Any missing case makes "
        "the result inconclusive. Any axis failure in a complete run yields hold.",
    }
    witnesses = {
        key: {field: value for field, value in sealed["cases"][case].items() if field != "gold"}
        for key, case in CASES.items()
    }
    assets = {
        "gold.json": gold,
        "scoring.json": encoded(rules),
        "witnesses.json": encoded(witnesses),
    }
    slots = []
    for i, (cell, end) in enumerate(schedule(cells), 1):
        key = cell.name.removesuffix("-B")
        path = "requests/" + filename(cell, end)
        body = end.body_utf8.encode()
        assets[path] = body
        slots.append(
            dict(
                slot=i,
                cell=cell.name,
                case=CASES[key],
                filename=path,
                work_sha256=cell.work.fingerprint,
                native_request_sha256=cell.wire.native_request_sha256,
                http_body_bytes=len(body),
                **end.model_dump(mode="json", exclude={"body_utf8"}),
            )
        )
    spec = cells[0].wire.model_spec
    ceiling = _cost(spec, parent.INPUT, parent.OUTPUT)
    manifest = encoded(
        dict(
            contract="q011-sol-high-position-depiction-1",
            live_directory=ROOT.relative_to(sources.REPO).as_posix(),
            cases=CASES,
            slots=slots,
            gold_sha256=rehearsal.GOLD,
            model=MODEL,
            reasoning="high",
            baseline_sha256=digest(cells[0].work.context.messages[0].content.encode()),
            model_spec=spec.model_dump(mode="json"),
            stops=STOPS,
            budget=dict(
                input_counts=6,
                max_generations=6,
                retries=0,
                input_per_generation=parent.INPUT,
                output_per_generation=parent.OUTPUT,
                aggregate_generation_input=6 * parent.INPUT,
                aggregate_generation_output=6 * parent.OUTPUT,
                max_usd_per_generation=str(ceiling),
                aggregate_generation_usd=str(6 * ceiling),
                count_seconds=COUNT_SECONDS,
                generation_seconds=GENERATION_SECONDS,
                wall_seconds=WALL_SECONDS,
            ),
            implementation={p: ledger.file_hash(sources.REPO / p) for p in IMPLEMENTATION},
            members={k: digest(v) for k, v in assets.items()},
        )
    )
    return cells, assets, manifest


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
    require(all(_read(root / k) == raw for k, raw in assets.items()), "frozen_member_drift")
    require(
        {p.name for p in (root / "requests").iterdir()}
        == {filename(c, e) for c, e in schedule(cells)},
        "request_inventory",
    )
    ledger.ledger_state(root, approval)
    return cells
