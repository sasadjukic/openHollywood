"""Read-only registered-source compact presentation export; no inference or database."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from open_hollywood_engine.evaluations import assessment_compact_presentation as domain
from open_hollywood_engine.evaluations import assessment_presentation as original
from open_hollywood_engine.evaluations.assessment_completion import CompletionContext, encoded
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import require

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_delivery as shared

NOTICE = (
    "READ-ONLY DIAGNOSTIC PRESENTATION V2; NO MODEL REQUEST OR DELIVERY. "
    "Local provenance remains in its separate bound file. Native source identity and all "
    "field dispositions remain unchanged. Binding is not semantic or story-quality approval."
)


def _implementation() -> str:
    return canonical_sha256(
        {
            "shared_source_io": shared._implementation(),
            "original_presentation": storage._sha(Path(original.__file__).read_bytes()),
            "compact_presentation": storage._sha(Path(domain.__file__).read_bytes()),
            "application": storage._sha(Path(__file__).read_bytes()),
        }
    )


def _files(context: CompletionContext) -> dict[str, bytes]:
    work = context.intake.pending_work
    require(work is not None, "compact_no_pending_work")
    assert work is not None
    require(len(work.batches) <= 12, "compact_batch_bound")
    bundles = [domain.render_compact(context, b.batch_id) for b in work.batches]
    local = bundles[0].local_provenance
    require(all(b.local_provenance == local for b in bundles), "compact_mixed_local_provenance")
    files = {
        "intake.json": context.exact_intake,
        "source-receipt.json": encoded(context.adapter_receipt),
        "local-provenance.json": encoded(local.model_dump(mode="json")),
    }
    for index, bundle in enumerate(bundles, 1):
        files[f"presentation-{index:02d}.json"] = encoded(
            bundle.presentation.model_dump(mode="json")
        )
    files["view.md"] = shared._literal(
        "Compact diagnostic presentations",
        {
            "notice": NOTICE,
            "presentations": [b.presentation.model_dump(mode="json") for b in bundles],
            "local_provenance_file": "local-provenance.json",
            "writer_dispatch_authorized": False,
        },
    ).replace(shared.NOTICE.encode(), NOTICE.encode(), 1)
    files["manifest.json"] = encoded(
        {
            "contract": "assessment-compact-publication-2",
            "state": "diagnostic_inputs_only",
            "source": context.pin.model_dump(mode="json"),
            "batch_ids": [b.presentation.batch_id for b in bundles],
            "files_sha256": {n: storage._sha(v) for n, v in files.items()},
            "implementation_sha256": _implementation(),
            "live_calls": 0,
            "model_evidence": False,
            "writer_dispatch_authorized": False,
        }
    )
    require(all(len(raw) <= storage.MAX_FILE_BYTES for raw in files.values()), "compact_file_size")
    return files


def prepare(intake: Path, destination: Path) -> Literal["created", "reused"]:
    collected = storage._collect(intake)
    files = _files(collected.context)

    def recheck() -> None:
        require(storage._collect(intake) == collected, "compact_source_drift")

    return storage._publish(destination, files, collected.protected, recheck)


def verify(intake: Path, destination: Path) -> Literal["verified_zero_calls"]:
    collected = storage._collect(intake)
    files = _files(collected.context)
    storage._destination(destination, collected.protected)
    storage._verify_output(destination, files, manifest=True)
    require(storage._collect(intake) == collected, "compact_source_drift")
    storage._verify_output(destination, files, manifest=True)
    return "verified_zero_calls"
