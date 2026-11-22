"""Read one Q013 delivery for a version in the physically registered, sealed workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import ModelAssessment
from open_hollywood_engine.evaluations.review_evidence import Record, require
from pydantic import BaseModel

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_inspector_workspace as workspace
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services.assessment_consumer_projection import Usage
from open_hollywood_api.services.assessment_inspector_workspace import WorkspacePin as WorkspacePin
from open_hollywood_api.services.production_association_records import ArtifactSelection

Q013Reader = workspace.Reader

SOURCE = (
    Path(__file__).resolve().parents[4]
    / "data/diagnostics/q013-downstream-2026-11-21/registration/source"
)
REGISTERED = WorkspacePin(
    SOURCE / "database/open_hollywood.db",
    2372488652078295932,
    2533274792150197,
    "0d8a12fca395380072e72030d18700328e3855893143d7e98d28c376b49d6c99",
    24_580_096,
)


class Q013LookupRow(Record):
    selection: ArtifactSelection
    status: Literal["available", "unavailable"]
    reason: workspace.LookupReason | None
    delivery_id: str | None
    claim_id: Literal["Q013"] | None


class Q013OperatorScore(Record):
    claim_correctness: Literal["pass", "fail"]
    evidence_coverage: Literal["pass", "fail"]


class Q013AssessmentView(Record):
    delivery_id: str
    claim_id: Literal["Q013"]
    claim: str
    model: str
    model_assessment: ModelAssessment
    operator_score: Q013OperatorScore
    application_status: workspace.InspectorStatus


class Q013InspectorView(Record):
    contract: Literal["q013-inspector-view-1"]
    lookups: tuple[Q013LookupRow, ...]
    assessments: tuple[Q013AssessmentView, ...]
    accounting_records: tuple[workspace.InspectorAccounting, ...]
    generation_totals: Usage | None


def unavailable(
    selection: ArtifactSelection,
    reason: workspace.LocalFailure,
) -> Q013InspectorView:
    return Q013InspectorView(
        contract="q013-inspector-view-1",
        lookups=(
            Q013LookupRow(
                selection=selection,
                status="unavailable",
                reason=reason,
                claim_id=None,
                delivery_id=None,
            ),
        ),
        assessments=(),
        accounting_records=(),
        generation_totals=None,
    )


def _registered_pair() -> tuple[ArtifactSelection, ArtifactSelection]:
    raw = storage._read(SOURCE / "source-fixture/source-manifest.json")
    require(
        storage._sha(raw) == "910f7e50035a6449bdfe426005d8b7a0823d4ec9235f01ed503fd08e338259c4",
        "changed_source_manifest",
    )
    manifest = saved._CaptureManifest.model_validate_json(raw)
    review, draft = manifest.selection
    require(
        review.role == "original_review" and draft.role == "reviewed_draft", "wrong_source_pair"
    )
    return review, draft


def _project(
    source: BaseModel, selected: ArtifactSelection, review: ArtifactSelection
) -> Q013InspectorView:
    data = workspace.display_fields(
        source,
        selected,
        review,
        contract="saved-review-consumer-lookup-1",
        claim_id="Q013",
        score=lambda value: {name: value[name]["score"] for name in Q013OperatorScore.model_fields},
    )
    return Q013InspectorView.model_validate_json(
        encoded({**data, "contract": "q013-inspector-view-1"})
    )


class Q013InspectorService:
    def __init__(self, database: Path, reader: Q013Reader) -> None:
        self.database = database.absolute()
        self.reader = reader

    def view(self, selected: ArtifactSelection) -> Q013InspectorView:
        return workspace.read_view(
            self.database,
            REGISTERED,
            selected,
            _registered_pair,
            self.reader,
            _project,
            unavailable,
        )
