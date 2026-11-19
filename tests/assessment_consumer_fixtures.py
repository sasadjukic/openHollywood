"""Synthetic records for consumer boundaries, never real observation registrations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_consumer as service
from open_hollywood_api.services import assessment_consumer_projection as projection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import compile_intake
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceRegistry,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentReceipt, complete_work
from open_hollywood_engine.evaluations.review_evidence import text_hash

from tests.assessment_intake_fixtures import authored_source, choice_for, plan_for


def envelope(*, support: str = "uncertain", cite: bool = False) -> dict[str, Any]:
    source = authored_source()
    intake = compile_intake(
        source,
        plan_for(
            source,
            choice_for(source, "Q001"),
            choice_for(source, "Q002", "literal_procedure"),
            choice_for(source, "Q003", "editorial_effect"),
            choice_for(source, "Q004", "ambiguous"),
        ),
    )
    work = intake.pending_work
    assert work is not None
    scope = scope_for_batch(work, work.batches[0].batch_id, "a" * 64)
    registry = EvidenceRegistry.model_validate_json(
        next(d.content_json for d in work.context.documents if d.kind == "registry")
    )
    location = next(
        e
        for e in registry.entries
        if e.document_id == "catalog-complete-current-draft" and e.paragraph is None
    )
    raw = encoded(
        {
            "assessments": {
                u: {
                    "support": support,
                    "evidence": [location.ref] if cite else [],
                    "reason": "Unrelated claim about a dragon. Authored test ``` Ω </script> "
                    "[link](https://invalid.example).",
                }
                for u in scope.active_unit_ids
            }
        }
    ).decode()
    receipt = AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=scope.request_sha256,
        attempt_id="fixture-only",
        status="valid",
        result_sha256=text_hash(raw),
        assessed_unit_ids=scope.active_unit_ids,
        input_tokens=100,
        output_tokens=80,
        reasoning_tokens=60,
        active_seconds=1.0,
    )
    bound = bind_assessment_result(work, scope, receipt, raw)
    completion = complete_work(work, (bound.receipt,), {scope.batch_id: scope.request_sha256})
    return {
        "contract": "assessment-observed-completion-1",
        "origin": "observed_openai_transport",
        "source_origin": "registered_diagnostic_probe",
        "work": "N06",
        "state": "bound_unassessed",
        "observation_binding": {"fixture_only": True},
        "intake": intake.model_dump(mode="json"),
        "terminal": {
            "state": "bound_unassessed",
            "bound_result": bound.model_dump(mode="json"),
            "native_receipt": bound.receipt.model_dump(mode="json"),
            "usage": {
                "input_tokens": 100,
                "output_tokens": 80,
                "reasoning_tokens": 60,
                "cached_input_tokens": 10,
            },
            "accounting_hold": False,
            "budget_violations": [],
            "unknown_elapsed_endpoints": 0,
        },
        "completion": completion.model_dump(mode="json"),
        "journal_closed": True,
        "stop_reason": "complete",
        "accounting_clear": True,
        "actual_billed_cost": None,
        "endpoint_slots": [
            {"work": "N06", "stage": stage, "state": "observed_terminal"}
            for stage in ("input_count", "generation")
        ],
        **projection.Holds().model_dump(mode="json"),
        "live_calls": 0,
    }


def publication(root: Path) -> service._Registration:
    original = root / "source"
    original.mkdir()
    pin = root / "upstream.json"
    pin.write_bytes(b'{"fixture_only":true}')
    files = {"N06.completion.json": encoded(envelope()), "N06.view.md": b"original fixture"}
    manifest = {
        "contract": "assessment-observed-publication-1",
        "origin": "observed_openai_transport",
        "source_origin": "registered_diagnostic_probe",
        "state": "bound_unassessed",
        "works": ["N06"],
        "observation_binding": {"fixture_only": True},
        "source_members_sha256": {str(pin): storage._sha(pin.read_bytes())},
        "files_sha256": {n: storage._sha(v) for n, v in files.items()},
        "accounting_clear": True,
        "actual_billed_cost": None,
        **projection.Holds().model_dump(mode="json"),
        "live_calls": 0,
    }
    files["manifest.json"] = encoded(manifest)
    for name, data in files.items():
        (original / name).write_bytes(data)
    return service._Registration(
        "test-only",
        original,
        storage._sha(files["manifest.json"]),
        "registered_diagnostic_probe",
        ("N06",),
        3,
    )
