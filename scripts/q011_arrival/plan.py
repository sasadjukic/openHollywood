"""Prepare a fixed B comparison with one currently assessed draft per request."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_authored_source import _document
from open_hollywood_engine.evaluations.assessment_compact_presentation import SYSTEM, compact
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceLocation,
    EvidenceRegistry,
    _field,
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentContext,
    ReportField,
    SelectedStatement,
    partition_work,
)
from open_hollywood_engine.evaluations.review_evidence import (
    SavedMessage,
    require,
    strict_object,
    text_hash,
)
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

from . import sources

ROOT = sources.ROOT
INPUT, OUTPUT, WALL_SECONDS = 16384, 4096, 840
STOPS = (
    "Verify frozen sources, exact requests, implementation, limits and unused single-use journal.",
    "Complete both positive, within-budget counts before generation. Stop globally on the first "
    "technical failure, non-200, invalid or duplicate JSON, invalid count, model drift, refusal, "
    "length, invalid claim or citation, missing required input/output usage, budget or time limit.",
    "A semantically incorrect but eligible answer consumes its slot and the schedule continues.",
    "Persist intent before send. Cancellation or interruption consumes this run. No retries, "
    "fallback, replacements, polling or reissue of the live registration. Preserve unknown usage.",
)
IMPLEMENTATION = (
    "scripts/q011_arrival/sources.py",
    "scripts/q011_arrival/plan.py",
    "scripts/q011_arrival/run.py",
    "scripts/q011_arrival/scoring.py",
    "scripts/ordinary_v61_capture.py",
    "scripts/q008_sol_smoke.py",
    "scripts/q010_uncertainty_plan.py",
    "scripts/q010_uncertainty_run.py",
    "scripts/fresh_endpoint_repeat/scoring.py",
    "scripts/assessment_openai_authored_smoke.py",
    "apps/api/open_hollywood_api/services/assessment_delivery.py",
    "apps/api/open_hollywood_api/services/assessment_completion.py",
    "apps/api/open_hollywood_api/services/saved_review_openai_fixture.py",
    "engine/open_hollywood_engine/evaluations/assessment_result.py",
    "engine/open_hollywood_engine/evaluations/assessment_work.py",
    "engine/open_hollywood_engine/evaluations/assessment_compact_presentation.py",
    "engine/open_hollywood_engine/evaluations/assessment_presentation.py",
    "engine/open_hollywood_engine/models/assessment_openai.py",
    "engine/open_hollywood_engine/models/openai.py",
    "engine/open_hollywood_engine/models/openai_catalog.py",
)


def render(case: str, packet: dict[str, Any]) -> Cell:
    require(
        text_hash(SYSTEM) == "9b95b4fda41557bcc730fa821b7ba96cda2ab711cebd79d011730cd35686549b",
        "baseline_drift",
    )
    versions = []
    docs = []
    refs = []
    for role, source in {
        **packet["context"],
        "assessment_draft": packet["assessment_draft"],
    }.items():
        version = source["version"]
        versions.append(UUID(version))
        value = dict(source["content"])
        pointers = {}
        if role == "scene_plan":
            pointers = {"E0233": "/outcome", "E0229": "/exit_state"}
        elif role == "assessment_draft":
            value["ending_excerpt"] = value["prose"].rsplit("\n\n", 1)[-1]
            pointers = {"E0883": "/prose", "D01": "/ending_excerpt"}
        doc = _document(role, "source", value).model_copy(update={"version": version})
        docs.append(doc)
        for ref, ptr in pointers.items():
            quote = _field(strict_object(doc.content_json), ptr)
            refs.append(
                EvidenceLocation(
                    ref=ref,
                    document_id=role,
                    document_version=version,
                    document_sha256=doc.content_sha256,
                    field_pointer=ptr,
                    field_sha256=text_hash(quote),
                    start=0,
                    end=len(quote),
                    quote=quote,
                )
            )
    history = packet["historical_review"]
    versions.append(UUID(history["version"]))
    docs.append(
        _document("historical-review", "report", history).model_copy(
            update={"version": history["version"]}
        )
    )
    docs.append(
        _document(
            "registry", "registry", EvidenceRegistry(entries=tuple(refs)).model_dump(mode="json")
        )
    )
    field = ReportField(
        field_id="Q011",
        pointer="/saved_native_audit/check/current_endpoint_comparison",
        text=packet["claim"],
    )
    stmt = SelectedStatement(
        unit_id="Q011", field_id="Q011", start=0, end=len(field.text), quote=field.text
    )
    visible_docs = []
    for doc in docs:
        view = doc.model_dump(mode="json", exclude={"content_json"})
        if doc.kind == "registry":
            view.update(
                columns=["ref", "document_id", "field_pointer"],
                whole_field_locations=[[e.ref, e.document_id, e.field_pointer] for e in refs],
            )
        else:
            view["structured_content"] = json.loads(doc.content_json)
        visible_docs.append(view)
    user = compact(
        {
            "active_unit_ids": ["Q011"],
            "claim": field.model_dump(mode="json"),
            "work_brief": packet["work_brief"],
            "source_authority": packet["authority"],
            "native_work_view": {"context": {"documents": visible_docs}},
        }
    )
    work = partition_work(
        AssessmentContext(
            provenance="synthetic_fixture" if case == "B" else "diagnostic_capture",
            origin_sha256=digest(encoded(packet)),
            documents=tuple(docs),
            report_fields=(field,),
            statements=(stmt,),
            messages=(SavedMessage(role="user", content=user),),
        ),
        1,
    )
    (batch,) = work.batches
    spec = builtin_model_specs()[MODEL]
    scope = scope_for_batch(
        work, batch.batch_id, digest(encoded([work.fingerprint, MODEL, "high", SYSTEM, user]))
    )
    request = ModelRequest(
        provider="openai",
        deployment=ModelDeployment.CLOUD,
        model_identifier=MODEL,
        invocation=InvocationContext(
            "endpoint_fact_assessment", "q011-destination-1", tuple(versions)
        ),
        messages=(ModelMessage(MessageRole.SYSTEM, SYSTEM), ModelMessage(MessageRole.USER, user)),
        response_schema=assessment_response_schema(work, scope),
        settings=ModelSettings(thinking="high"),
        budget=ModelCallBudget(INPUT, OUTPUT, _cost(spec, INPUT, OUTPUT)),
    )
    return Cell(case + "-B", work, _prepare_wire(work, scope, request, spec, guard=None))


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    packets = sources.packets()
    gold = encoded(sources.scorer(packets))
    cases = [render(key, packets[key]) for key in sources.CASES]
    assets = {"gold.json": gold, "scoring.json": encoded(sources.SCORING)}
    slots = []
    for cell, end in schedule(cases):
        path = "requests/" + filename(cell, end)
        assets[path] = end.body_utf8.encode()
        slots.append(
            dict(
                cell=cell.name,
                filename=path,
                work_sha256=cell.work.fingerprint,
                native_request_sha256=cell.wire.native_request_sha256,
                **end.model_dump(mode="json", exclude={"body_utf8"}),
            )
        )
    spec = cases[0].wire.model_spec
    manifest = encoded(
        dict(
            contract="q011-sol-high-destination-1",
            model=MODEL,
            reasoning="high",
            baseline_sha256=text_hash(SYSTEM),
            origin_snapshot=sources.SNAPSHOT,
            original_gold_sha256=sources.GOLD,
            rehearsal_generation_sha256=sources.REHEARSED,
            model_spec=spec.model_dump(mode="json"),
            implementation={p: ledger.file_hash(sources.REPO / p) for p in IMPLEMENTATION},
            members={k: digest(v) for k, v in assets.items()},
            slots=slots,
            stops=STOPS,
            budget=dict(
                input_counts=2,
                max_generations=2,
                retries=0,
                input_per_generation=INPUT,
                output_per_generation=OUTPUT,
                max_usd_per_generation=str(_cost(spec, INPUT, OUTPUT)),
                aggregate_generation_usd=str(2 * _cost(spec, INPUT, OUTPUT)),
                count_seconds=COUNT_SECONDS,
                generation_seconds=GENERATION_SECONDS,
                wall_seconds=WALL_SECONDS,
            ),
        )
    )
    return cases, assets, manifest


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
