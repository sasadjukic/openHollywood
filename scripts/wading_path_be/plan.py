"""Freeze the three ordinary Wading Path selections for an isolated Sol-high comparison."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_api.services.saved_review_openai_fixture import _request
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_compact_presentation import (
    NOTICE,
    PROVENANCE_ID,
    SYSTEM,
    compact,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    _registry,
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentWork, partition_work
from open_hollywood_engine.evaluations.review_evidence import require
from open_hollywood_engine.models.assessment_openai import (
    WireMapping,
    _prepare_wire,
    check_outgoing,
)
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
from scripts.q011_arrival.plan import IMPLEMENTATION as COMMON_FILES
from scripts.q011_arrival.sources import DATA
from scripts.q011_transfer import wading_path_selection as selection

ROOT = DATA / "wading-path-sol-high-be-2026-11-24"
PREVIEWS = DATA / "wading-path-selection-rehearsal-2026-11-24/previews.json"
PREVIEW_SHA = "9da0764cb50769cf52bd9bba438d1e9f88abe969d6884d2e094bb0690b29bae8"
INPUT, OUTPUT = 160_000, 4096
WALL_SECONDS = len(selection.PREVIEWS) * (COUNT_SECONDS + GENERATION_SECONDS)
REF_PATTERN = "^E(000[1-9]|00[1-9][0-9]|0[1-9][0-9]{2}|1[0-3][0-9]{2}|14[01][0-9]|1420)$"
STOPS = (
    "Verify frozen sources, gold, code, exact wires, budgets and unused single-use journal.",
    "All five serial counts must return HTTP 200 and positive counts within the input, context "
    "and cost limits before generation. No retries, replacements, redirects, polling or fallback.",
    "Stop globally on the first transport or capture error, non-200, timeout, deadline, ambiguous "
    "or duplicate JSON, model drift, refusal, truncation, invalid output, wrong claim or citation, "
    "missing input/output usage or a budget overrun. Preserve unknown usage and untouched slots.",
    "Commit intent before send. An interruption consumes the run. Record semantic misses and "
    "continue the fixed schedule when delivery is eligible.",
)
SCORING = {
    "eligibility": "Score only a complete in-budget generation bound in a closed observed journal. "
    "Report every other generation as unscored on each axis.",
    "judgment": "One point for the exact frozen whole-field label; otherwise zero.",
    "evidence": "Mask arm, dispatch order and returned label. Resolve citations to their exact "
    "sources, inspect the reason, and award one point only when all field-specific evidence "
    "requirements in gold.json are met. Record the passages, locators and basis for each "
    "decision. Accept equivalent source-bound evidence. Seal decisions before joining labels.",
    "comparison": "Report both axes for each eligible response. Compare Q010 and Q011 separately "
    "on each axis, report baseline joint passes and show Q008 B on its own.",
    "decision": "Any missing eligible response is inconclusive. A control miss or paired axis "
    "loss holds advancement. Otherwise a paired axis gain is a within-review signal. If both "
    "baselines already jointly passed, report no headroom. Remaining ties show no gain.",
}
FILES = (
    *COMMON_FILES,
    "scripts/q011_transfer/wading_path_selection.py",
    "scripts/q011_arrival/scope_rehearsal.py",
    "scripts/q011_evidence_check/plan.py",
    "scripts/wading_path_be/plan.py",
    "scripts/wading_path_be/run.py",
    "scripts/wading_path_be/scoring.py",
    "apps/api/open_hollywood_api/services/assessment_intake.py",
    "engine/open_hollywood_engine/evaluations/assessment_intake.py",
    "engine/open_hollywood_engine/evaluations/assessment_claim_scope.py",
    "engine/open_hollywood_engine/evaluations/assessment_work_brief.py",
    "engine/open_hollywood_engine/models/openai_schema.py",
)


def compact_registry_schema(wire: WireMapping, unit: str) -> WireMapping:
    """Represent the native enumeration exactly within the strict API enum limit."""
    refs = [f"E{i:04d}" for i in range(10_000) if re.fullmatch(REF_PATTERN, f"E{i:04d}")]
    ends = []
    for end in wire.endpoints:
        body = json.loads(end.body_utf8)
        schema = body["text"]["format"]["schema"]
        fields = schema["properties"]["assessments"]["properties"][unit]["properties"]
        require(fields["evidence"]["items"] == {"type": "string", "enum": refs}, "wading_ref_set")
        fields["evidence"]["items"] = dict(
            type="string", minLength=5, maxLength=5, pattern=REF_PATTERN
        )
        raw = encoded(body)
        endpoint = end.model_copy(
            update=dict(
                body_utf8=raw.decode(),
                body_bytes_sha256=digest(raw),
                body_canonical_sha256=canonical_sha256(body),
            )
        )
        check_outgoing(endpoint, _request(endpoint))
        ends.append(endpoint)
    effective = wire.effective | {
        "schema_sha256": digest(json.dumps(body["text"], sort_keys=True).encode())
    }
    return wire.model_copy(
        update=dict(
            endpoints=tuple(ends),
            effective=effective,
            schema_canonical_sha256=canonical_sha256(schema),
        )
    )


def native_view(work: AssessmentWork) -> dict[str, Any]:
    native = work.model_dump(mode="json")
    for doc in native["context"]["documents"]:
        content = json.loads(doc.pop("content_json"))
        if doc["kind"] == "scope":
            require(doc["identity"] == PROVENANCE_ID, "unknown_operator_document")
            doc["local_only"] = True
        elif doc["kind"] == "registry":
            refs = _registry(work).entries
            require(
                all(r.paragraph is None and r.start == 0 and r.end == len(r.quote) for r in refs),
                "whole_field_registry",
            )
            doc["columns"] = ["ref", "document_id", "field_pointer"]
            doc["whole_field_locations"] = [[r.ref, r.document_id, r.field_pointer] for r in refs]
        else:
            doc["structured_content"] = content
    return native


def render(work: AssessmentWork, row: dict[str, Any], versions: tuple[UUID, ...]) -> Cell:
    unit = row["unit"]
    require(work.fingerprint == row["work_sha256"], "wading_work_binding")
    (batch,) = work.batches
    user = compact(
        dict(
            contract="wading-path-saved-review-assessment-1",
            active_unit_ids=[unit],
            native_work_view=native_view(work),
            claim_scope=row["declaration"],
            work_brief=row["brief"],
            availability_notice=NOTICE,
            field_dispositions={
                f.field_id: "pending_assessment" if f.field_id == unit else "not_selected"
                for f in work.context.report_fields
            },
        )
    )
    spec = builtin_model_specs()[MODEL]
    request_id = digest(
        encoded([work.fingerprint, SYSTEM, user, MODEL, "high", INPUT, OUTPUT, REF_PATTERN])
    )
    scope = scope_for_batch(work, batch.batch_id, request_id)
    request = ModelRequest(
        provider="openai",
        deployment=ModelDeployment.CLOUD,
        model_identifier=MODEL,
        invocation=InvocationContext(
            "endpoint_fact_assessment", "wading-path-saved-review-assessment-1", versions
        ),
        messages=(ModelMessage(MessageRole.SYSTEM, SYSTEM), ModelMessage(MessageRole.USER, user)),
        settings=ModelSettings(thinking="high"),
        budget=ModelCallBudget(INPUT, OUTPUT, _cost(spec, INPUT, OUTPUT)),
        response_schema=assessment_response_schema(work, scope),
    )
    wire = compact_registry_schema(_prepare_wire(work, scope, request, spec, guard=None), unit)
    return Cell(unit + "-" + row["arm"], work, wire)


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    source = selection.load_source()
    previews = _read(PREVIEWS)
    rows = json.loads(previews)
    require(
        digest(previews) == PREVIEW_SHA
        and [(r["unit"], r["arm"]) for r in rows] == list(selection.PREVIEWS),
        "wading_preview_drift",
    )
    ctx = source.inventory_work.context
    snap = json.loads(next(d.content_json for d in ctx.documents if d.kind == "scope"))["snapshot"]
    versions = tuple(UUID(s["version_id"]) for s in [snap["critique"], *snap["sources"]])
    cells = []
    for row in rows:
        stmt = next(s for s in ctx.statements if s.unit_id == row["unit"])
        work = partition_work(ctx.model_copy(update={"statements": (stmt,)}), 1)
        cells.append(render(work, row, versions))
    # The operator's answer key is read after both endpoint bodies have been built.
    verification = selection.verify_gold(source, rows)
    assets = {
        "gold.json": _read(selection.GOLD),
        "selections.json": previews,
        "scoring.json": encoded(SCORING),
        "evidence-form-schema.json": encoded(Decisions.model_json_schema()),
    }
    require(digest(assets["gold.json"]) == selection.GOLD_SHA, "wading_gold_drift")
    slots = []
    for i, (cell, end) in enumerate(schedule(cells), 1):
        path = "requests/" + filename(cell, end)
        raw = end.body_utf8.encode()
        assets[path] = raw
        slots.append(
            dict(
                slot=i,
                cell=cell.name,
                filename=path,
                http_body_bytes=len(raw),
                work_sha256=cell.work.fingerprint,
                native_request_sha256=cell.wire.native_request_sha256,
                **end.model_dump(mode="json", exclude={"body_utf8"}),
            )
        )
    spec = cells[0].wire.model_spec
    cost = _cost(spec, INPUT, OUTPUT)
    manifest = encoded(
        dict(
            contract="wading-path-sol-high-be-1",
            live_directory=ROOT.relative_to(REPO).as_posix(),
            model=MODEL,
            reasoning="high",
            model_spec=spec.model_dump(mode="json"),
            database_sha256=selection.DB_SHA,
            intake_sha256=source.source_sha256,
            source_binding=verification["binding"],
            source_version_ids=list(map(str, versions)),
            gold_sha256=selection.GOLD_SHA,
            ordered_cells=[c.name for c in cells],
            slots=slots,
            citation_representation=dict(original_ids=1420, pattern=REF_PATTERN),
            stops=STOPS,
            budget=dict(
                input_counts=5,
                max_generations=5,
                retries=0,
                input_per_generation=INPUT,
                output_per_generation=OUTPUT,
                max_usd_per_generation=str(cost),
                aggregate_generation_input=5 * INPUT,
                aggregate_generation_output=5 * OUTPUT,
                aggregate_generation_usd=str(5 * cost),
                count_seconds=COUNT_SECONDS,
                generation_seconds=GENERATION_SECONDS,
                wall_seconds=WALL_SECONDS,
            ),
            implementation={p: ledger.file_hash(REPO / p) for p in FILES},
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
    require(all(_read(root / k) == v for k, v in assets.items()), "frozen_member_drift")
    require(
        {p.name for p in (root / "requests").iterdir()}
        == {filename(c, e) for c, e in schedule(cells)},
        "request_inventory",
    )
    ledger.ledger_state(root, approval)
    return cells
