"""Exercise real neighboring versions and Q008's authenticated receipts against Q013 offline."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services.review_evidence_export import readonly_connection
from open_hollywood_engine.evaluations.assessment_result import (
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import complete_work
from open_hollywood_engine.evaluations.review_evidence import (
    EvidenceError,
    object_value,
    require,
    strict_object,
)

from scripts import publish_q008_completion, q008_sol_smoke, q013_assessment

# These are the four bodies inspected independently against the scorer-only gold.
# The regression can check future renders without opening that gold.
CHECKED_BODIES = {
    "original_review": {
        "input_count": "a7ed9399c181e48833013be88ac02e1880ef50e47aede640c1b5b645119541a6",
        "generation": "527d4d168af04fb7d7ec1d21d0f3ee66221fdc168ba0d829bdc25e41cb6b7778",
    },
    "reviewed_draft": {
        "input_count": "39417d728f67984ca568bfe3e5e6d131825a8098fe7e5a22016f593c7c513f1b",
        "generation": "d4903af69860201d2999913d0973f00c730ae3e7c93bd92271c96963e33c4d33",
    },
}


def rejected(operation: Callable[[], object], reason: str) -> str:
    try:
        operation()
    except EvidenceError as exc:
        require(str(exc) == reason, f"unexpected_rejection_{exc}")
        return reason
    raise AssertionError(f"Expected {reason}")


def verify() -> dict[str, object]:
    # Authenticate the historical control using its own source and observed delivery.
    old = q008_sol_smoke.source()
    _, observed = publish_q008_completion.collect_observed(old.source.pin.review)
    archive = q013_assessment._open()
    manifest = saved._CaptureManifest.model_validate_json(
        archive.read("source-fixture/source-manifest.json")
    )
    results: dict[str, object] = {}
    with TemporaryDirectory() as tmp:
        db = Path(tmp) / "captured.db"
        db.write_bytes(archive.read("database/open_hollywood.db", database=True))
        for selected in manifest.selection:
            plan = q013_assessment.prepare(selected)
            bodies = {
                e.stage: hashlib.sha256(e.body_utf8.encode()).hexdigest()
                for e in plan.wire.endpoints
            }
            require(bodies == CHECKED_BODIES[selected.role], "q013_checked_body_changed")
            scope = scope_for_batch(plan.work, plan.wire.batch_id, plan.digest)
            require(scope.active_unit_ids == ("Q013",), "wrong_positive_control")
            with readonly_connection(db) as conn:
                saved._verify_selection(conn, selected)
                row = conn.execute(
                    "SELECT id, content_sha256 FROM artifact_versions "
                    "WHERE artifact_id=? AND version_number=2",
                    (UUID(selected.artifact_id).hex,),
                ).fetchone()
                require(row is not None, "missing_neighbor")
                assert row is not None
                neighbor = selected.model_copy(
                    update={"version_id": str(UUID(row[0])), "content_sha256": row[1]}
                )
                saved._verify_selection(conn, neighbor)
                require(selected.version_id != neighbor.version_id, "not_a_neighbor")

            doc = next(d for d in plan.work.context.documents if d.kind == "scope")
            snapshot = object_value(strict_object(doc.content_json)["snapshot"])
            # Both claims use batch-001. The work and exact request must still match.
            require(
                observed.scope.batch_id == scope.batch_id
                and observed.scope.work_sha256 != scope.work_sha256
                and observed.scope.request_sha256 != scope.request_sha256,
                "weak_receipt_control",
            )
            results[selected.role] = {
                "exact_version": selected.version_id,
                "gold_checked_body_sha256": bodies,
                "neighbor": neighbor.model_dump(mode="json"),
                "wrong_version": rejected(
                    partial(q013_assessment.prepare, neighbor), "saved_review_wrong_selection"
                ),
                "q008_assessment_binding": rejected(
                    partial(
                        bind_assessment_result,
                        plan.work,
                        scope,
                        observed.delivery_receipt,
                        observed.raw_final,
                    ),
                    "mixed_work_scope",
                ),
                "q008_usage_accounting": rejected(
                    partial(
                        complete_work, plan.work, (observed.receipt,), {scope.batch_id: plan.digest}
                    ),
                    "mixed_work_scope",
                ),
                "q008_critic_source": rejected(
                    partial(saved._capture_receipt, old.archive, snapshot, plan.source.pin),
                    "saved_review_capture_receipt_binding",
                ),
            }
    return {
        "selections": results,
        "q008_observed_attempt": observed.receipt.attempt_id,
        "q008_work_sha256": observed.scope.work_sha256,
        "q008_request_sha256": observed.scope.request_sha256,
        "live_calls": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
