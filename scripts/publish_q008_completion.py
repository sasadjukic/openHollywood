"""Publish the registered Q008 assessment for either exact artifact selection, offline."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_result import BoundAssessmentResult

from scripts import publish_saved_review_completion as publication
from scripts import q008_sol_smoke as smoke

# Retain the read-only paths used by the original private Q008 replay.
SCORE = publication.REGISTRATIONS["q008"].score
ARCHIVE = publication.REGISTRATIONS["q008"].regression_root
__all__ = ["ARCHIVE", "SCORE", "collect_observed", "main", "publish", "saved", "smoke"]


def collect_observed(
    selection: ArtifactSelection,
) -> tuple[dict[str, bytes], BoundAssessmentResult]:
    return publication.collect_observed("q008", selection)


def _collect(selection: ArtifactSelection) -> dict[str, bytes]:
    return collect_observed(selection)[0]


def publish(
    selection: ArtifactSelection, destination: Path, *, journal: Path | None = None
) -> Literal["created", "reused"]:
    return publication.publish("q008", selection, destination, journal=journal)


def main(argv: list[str] | None = None) -> int:
    return publication._main(argv, q008_only=True)


if __name__ == "__main__":
    raise SystemExit(main())
