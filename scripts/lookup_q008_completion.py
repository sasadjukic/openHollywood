"""Look up Q008 by exact artifact selection in the registered read-only publication."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from typing import Literal

from open_hollywood_api.services.assessment_consumer_projection import Usage
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_result import BoundAssessmentResult
from open_hollywood_engine.evaluations.review_evidence import Record, require

from scripts import lookup_saved_review_completion as shared
from scripts.lookup_saved_review_completion import Accounting as Accounting
from scripts.lookup_saved_review_completion import Assessment as Assessment
from scripts.lookup_saved_review_completion import Available as Available
from scripts.lookup_saved_review_completion import Unavailable as Unavailable

PUBLICATION = shared.Q008.directory
MANIFEST_SHA = shared.Q008.manifest_sha256


class Inventory(Record):
    contract: Literal["q008-consumer-lookup-1"] = "q008-consumer-lookup-1"
    lookups: tuple[Available | Unavailable, ...]
    assessments: tuple[Assessment, ...] = ()
    accounting_records: tuple[Accounting, ...] = ()
    generation_totals: Usage | None = None


def _project(
    files: dict[str, bytes], bound: BoundAssessmentResult
) -> tuple[Assessment, Accounting]:
    """Projection used by the archived Q008/Q013 rehearsal."""
    return shared._project(shared.Q008, files, bound)


def lookup(selections: Sequence[ArtifactSelection]) -> Inventory:
    """Keep the original Q008-only result and publication-failure behavior."""
    selected = tuple(ArtifactSelection.model_validate_json(s.model_dump_json()) for s in selections)
    require(bool(selected), "q008_selection_required")
    registration = replace(shared.Q008, directory=PUBLICATION, manifest_sha256=MANIFEST_SHA)
    result = shared._lookup_publication(registration, selected)
    return Inventory(
        lookups=result.lookups,
        assessments=result.assessments,
        accounting_records=result.accounting_records,
        generation_totals=result.generation_totals,
    )


def main(argv: list[str] | None = None) -> int:
    return shared._run_cli(argv, __doc__, lookup)


if __name__ == "__main__":
    raise SystemExit(main())
