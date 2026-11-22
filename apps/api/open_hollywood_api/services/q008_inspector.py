"""Read one Q008 delivery for a version in the physically registered, sealed workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import ModelAssessment
from open_hollywood_engine.evaluations.review_evidence import Record, require
from pydantic import BaseModel, NonNegativeInt

from open_hollywood_api.services import assessment_inspector_workspace as workspace
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services.assessment_consumer_projection import Usage
from open_hollywood_api.services.assessment_inspector_workspace import WorkspacePin as WorkspacePin
from open_hollywood_api.services.production_association_records import ArtifactSelection

Q008Reader = workspace.Reader

REGISTERED = WorkspacePin(
    saved.CAPTURED_Q008.archive / "source/database/open_hollywood.db",
    2372488652078295932,
    3096224745196681,
    "2724fd7db1cbe2a0d400acebf5536f42f65b9f1eeabfa0dd86fd7f668f894b61",
    saved.CAPTURED_Q008.database_limit,
)


class Q008LookupRow(Record):
    selection: ArtifactSelection
    status: Literal["available", "unavailable"]
    reason: workspace.LookupReason | None
    delivery_id: str | None
    claim_id: Literal["Q008"] | None


class Q008OperatorScore(Record):
    possible_judgments: NonNegativeInt
    passed_judgments: NonNegativeInt


class Q008ApplicationStatus(workspace.InspectorStatus):
    pass


class Q008AssessmentView(Record):
    delivery_id: str
    claim_id: Literal["Q008"]
    claim: str
    model: str
    model_assessment: ModelAssessment
    operator_score: Q008OperatorScore
    application_status: Q008ApplicationStatus


class Q008AccountingView(workspace.InspectorAccounting):
    pass


class Q008InspectorView(Record):
    contract: Literal["q008-inspector-view-1"]
    lookups: tuple[Q008LookupRow, ...]
    assessments: tuple[Q008AssessmentView, ...]
    accounting_records: tuple[Q008AccountingView, ...]
    generation_totals: Usage | None


def unavailable(
    selection: ArtifactSelection,
    reason: workspace.LocalFailure,
) -> Q008InspectorView:
    return Q008InspectorView(
        contract="q008-inspector-view-1",
        lookups=(
            Q008LookupRow(
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
    archive = saved._open(saved.CAPTURED_Q008.name, allow_capture=True)
    manifest = saved._CaptureManifest.model_validate_json(
        archive.read("source-fixture/source-manifest.json")
    )
    review, draft = manifest.selection
    require(
        review.role == "original_review" and draft.role == "reviewed_draft", "wrong_source_pair"
    )
    return review, draft


def _project(
    source: BaseModel, selected: ArtifactSelection, review: ArtifactSelection
) -> Q008InspectorView:
    data = workspace.display_fields(
        source,
        selected,
        review,
        contract="q008-consumer-lookup-1",
        claim_id="Q008",
        score=lambda value: {name: value[name] for name in Q008OperatorScore.model_fields},
    )
    return Q008InspectorView.model_validate_json(
        encoded({**data, "contract": "q008-inspector-view-1"})
    )


def registered_image(path: Path) -> bytes:
    return workspace.registered_image(path, REGISTERED)


class Q008InspectorService:
    def __init__(self, database: Path, reader: Q008Reader) -> None:
        self.database = database.absolute()
        self.reader = reader

    def view(self, selected: ArtifactSelection) -> Q008InspectorView:
        return workspace.read_view(
            self.database,
            REGISTERED,
            selected,
            _registered_pair,
            self.reader,
            _project,
            unavailable,
        )
