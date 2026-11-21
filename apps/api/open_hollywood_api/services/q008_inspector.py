"""Read one Q008 delivery for a version in the physically registered, sealed workspace."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal
from uuid import UUID

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import ModelAssessment
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import Record, require
from open_hollywood_engine.secrets import SecretLeakError
from pydantic import BaseModel, NonNegativeInt
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services.assessment_consumer_projection import Usage
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_api.services.workspace import WorkspaceStore

Q008Reader = Callable[[Sequence[ArtifactSelection]], BaseModel]


@dataclass(frozen=True)
class WorkspacePin:
    path: Path
    device: int
    inode: int
    sha256: str


REGISTERED = WorkspacePin(
    saved.CAPTURED_Q008.archive / "source/database/open_hollywood.db",
    2372488652078295932,
    3096224745196681,
    "2724fd7db1cbe2a0d400acebf5536f42f65b9f1eeabfa0dd86fd7f668f894b61",
)


class Q008LookupRow(Record):
    selection: ArtifactSelection
    status: Literal["available", "unavailable"]
    reason: (
        Literal[
            "unregistered_workspace",
            "workspace_unavailable",
            "exact_selection_unavailable",
            "publication_missing",
            "publication_incomplete",
            "publication_manifest_changed",
            "publication_unexpected_member",
            "publication_member_changed",
            "publication_unavailable",
        ]
        | None
    )
    delivery_id: str | None
    claim_id: Literal["Q008"] | None


class Q008OperatorScore(Record):
    possible_judgments: NonNegativeInt
    passed_judgments: NonNegativeInt


class Q008ApplicationStatus(Record):
    semantic_support: Literal["unassessed"]
    evidence_adequacy: Literal["unassessed"]
    edit_necessity: Literal["unassessed"]
    craft: Literal["unassessed"]
    production_attachment_eligible: Literal[False]
    writer_dispatch_authorized: Literal[False]


class Q008AssessmentView(Record):
    delivery_id: str
    claim_id: Literal["Q008"]
    claim: str
    model: str
    model_assessment: ModelAssessment
    operator_score: Q008OperatorScore
    application_status: Q008ApplicationStatus


class Q008AccountingView(Record):
    delivery_id: str
    request_selection: ArtifactSelection
    preflight_input_count: NonNegativeInt
    generation_usage: Usage
    actual_billed_cost: None


class Q008InspectorView(Record):
    contract: Literal["q008-inspector-view-1"]
    lookups: tuple[Q008LookupRow, ...]
    assessments: tuple[Q008AssessmentView, ...]
    accounting_records: tuple[Q008AccountingView, ...]
    generation_totals: Usage | None


def unavailable(
    selection: ArtifactSelection,
    reason: Literal[
        "unregistered_workspace",
        "workspace_unavailable",
        "exact_selection_unavailable",
        "publication_unavailable",
    ],
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
    data = source.model_dump(mode="json")
    require(data.pop("contract") == "q008-consumer-lookup-1", "wrong_consumer_contract")
    # Only return display fields. The operator's detailed gold and frozen request hash stay local.
    for assessment in data["assessments"]:
        score = assessment["operator_score"]
        assessment["operator_score"] = {
            name: score[name] for name in Q008OperatorScore.model_fields
        }
    for record in data["accounting_records"]:
        record.pop("request_manifest_sha256")
    view = Q008InspectorView.model_validate_json(
        encoded({**data, "contract": "q008-inspector-view-1"})
    )
    (row,) = view.lookups
    require(row.selection == selected, "wrong_consumer_selection")
    if row.status == "unavailable":
        require(
            row.reason is not None
            and row.delivery_id is None
            and row.claim_id is None
            and not view.assessments
            and not view.accounting_records
            and view.generation_totals is None,
            "unavailable_with_delivery",
        )
    else:
        (claim,), (account,) = view.assessments, view.accounting_records
        require(
            row.reason is None
            and row.claim_id == claim.claim_id
            and bool(row.delivery_id)
            and row.delivery_id == claim.delivery_id == account.delivery_id
            and account.request_selection == review
            and view.generation_totals == account.generation_usage,
            "wrong_consumer_delivery",
        )
    return view


def _stamp(path: Path) -> tuple[int, int, int, int]:
    stat = storage._unlinked(path).stat()
    require(
        (stat.st_dev, stat.st_ino) == (REGISTERED.device, REGISTERED.inode), "workspace_replaced"
    )
    require(
        not any(
            storage._unlinked(Path(str(path) + suffix)).exists()
            for suffix in ("-wal", "-shm", "-journal")
        ),
        "workspace_has_sidecars",
    )
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def registered_image(path: Path) -> bytes:
    """Return the sealed database bytes without opening the original in SQLite."""
    require(path == REGISTERED.path, "unregistered_workspace")
    before = _stamp(path)
    with path.open("rb") as stream:
        stat = os.fstat(stream.fileno())
        require(
            (stat.st_dev, stat.st_ino) == (REGISTERED.device, REGISTERED.inode),
            "workspace_replaced",
        )
        image = stream.read(saved.CAPTURED_Q008.database_limit + 1)
    require(storage._sha(image) == REGISTERED.sha256, "workspace_changed")
    require(before == _stamp(path), "workspace_changed_during_read")
    return image


def _matches_workspace(path: Path, selected: ArtifactSelection) -> bool:
    image = registered_image(path)
    # SQLite only sees the authenticated image in a private scratch directory.
    with TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "snapshot.db"
        scratch.write_bytes(image)
        uri = scratch.as_uri() + "?mode=ro&immutable=1"
        engine = create_engine("sqlite+pysqlite://", creator=lambda: sqlite3.connect(uri, uri=True))
        try:
            with engine.connect() as conn:
                raw = conn.connection.driver_connection
                assert isinstance(raw, sqlite3.Connection)
                try:
                    saved._verify_selection(raw, selected)
                except ValueError:
                    return False
                detail = WorkspaceStore(sessionmaker(bind=conn)).get_artifact_version(
                    UUID(selected.version_id)
                )
                return (
                    str(detail.selected_version.id) == selected.version_id
                    and str(detail.artifact.id) == selected.artifact_id
                    and detail.content_sha256
                    == canonical_sha256(detail.content)
                    == selected.content_sha256
                )
        finally:
            engine.dispose()


class Q008InspectorService:
    def __init__(self, database: Path, reader: Q008Reader) -> None:
        self.database = database.absolute()
        self.reader = reader

    def view(self, selected: ArtifactSelection) -> Q008InspectorView:
        try:
            path = storage._unlinked(self.database)
            if path != REGISTERED.path:
                return unavailable(selected, "unregistered_workspace")
            before = _stamp(path)
            review, draft = _registered_pair()
            if selected not in (review, draft) or not _matches_workspace(path, selected):
                return unavailable(selected, "exact_selection_unavailable")
            try:
                view = _project(self.reader((selected,)), selected, review)
            except (ValueError, OSError, LookupError, TypeError, sqlite3.Error, SecretLeakError):
                return unavailable(selected, "publication_unavailable")
            require(before == _stamp(path), "workspace_changed_during_lookup")
            return view
        except (ValueError, OSError, LookupError, sqlite3.Error, SQLAlchemyError, SecretLeakError):
            return unavailable(selected, "workspace_unavailable")
