"""Shared physical workspace and display boundaries for saved assessment inspectors."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Literal
from uuid import UUID

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

Reader = Callable[[Sequence[ArtifactSelection]], BaseModel]
LocalFailure = Literal[
    "unregistered_workspace",
    "workspace_unavailable",
    "exact_selection_unavailable",
    "publication_unavailable",
]
LookupReason = Literal[
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


@dataclass(frozen=True)
class WorkspacePin:
    path: Path
    device: int
    inode: int
    sha256: str
    database_limit: int = storage.MAX_FILE_BYTES


class InspectorStatus(Record):
    semantic_support: Literal["unassessed"]
    evidence_adequacy: Literal["unassessed"]
    edit_necessity: Literal["unassessed"]
    craft: Literal["unassessed"]
    production_attachment_eligible: Literal[False]
    writer_dispatch_authorized: Literal[False]


class InspectorAccounting(Record):
    delivery_id: str
    request_selection: ArtifactSelection
    preflight_input_count: NonNegativeInt
    generation_usage: Usage
    actual_billed_cost: None


def display_fields(
    source: BaseModel,
    selected: ArtifactSelection,
    review: ArtifactSelection,
    *,
    contract: str,
    claim_id: str,
    score: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    data = source.model_dump(mode="json")
    require(data.pop("contract") == contract, "wrong_consumer_contract")
    (row,) = data["lookups"]
    require(row["selection"] == selected.model_dump(mode="json"), "wrong_consumer_selection")
    if row["status"] == "unavailable":
        require(
            row["reason"] is not None
            and row["claim_id"] is None
            and row["delivery_id"] is None
            and not data["assessments"]
            and not data["accounting_records"]
            and data["generation_totals"] is None,
            "unavailable_with_delivery",
        )
    else:
        (claim,), (account,) = data["assessments"], data["accounting_records"]
        require(
            row["status"] == "available"
            and row["reason"] is None
            and row["claim_id"] == claim["claim_id"] == claim_id
            and bool(row["delivery_id"])
            and row["delivery_id"] == claim["delivery_id"] == account["delivery_id"]
            and account["request_selection"] == review.model_dump(mode="json")
            and data["generation_totals"] == account["generation_usage"],
            "wrong_consumer_delivery",
        )
        claim["operator_score"] = score(claim["operator_score"])
        account.pop("request_manifest_sha256")
    return data


def _stamp(path: Path, pin: WorkspacePin) -> tuple[int, int, int, int]:
    stat = storage._unlinked(path).stat()
    require((stat.st_dev, stat.st_ino) == (pin.device, pin.inode), "workspace_replaced")
    require(
        not any(
            storage._unlinked(Path(str(path) + suffix)).exists()
            for suffix in ("-wal", "-shm", "-journal")
        ),
        "workspace_has_sidecars",
    )
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def registered_image(path: Path, pin: WorkspacePin) -> bytes:
    """Return the sealed database bytes without opening the original in SQLite."""
    require(path == pin.path, "unregistered_workspace")
    before = _stamp(path, pin)
    require(0 < before[2] <= pin.database_limit, "workspace_size")
    with path.open("rb") as stream:
        stat = os.fstat(stream.fileno())
        require(
            (stat.st_dev, stat.st_ino) == (pin.device, pin.inode),
            "workspace_replaced",
        )
        image = stream.read(pin.database_limit + 1)
    require(len(image) == before[2] and storage._sha(image) == pin.sha256, "workspace_changed")
    require(before == _stamp(path, pin), "workspace_changed_during_read")
    return image


def _matches_workspace(path: Path, pin: WorkspacePin, selected: ArtifactSelection) -> bool:
    image = registered_image(path, pin)
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


def read_view[T](
    database: Path,
    pin: WorkspacePin,
    selected: ArtifactSelection,
    pair: Callable[[], tuple[ArtifactSelection, ArtifactSelection]],
    reader: Reader,
    project: Callable[[BaseModel, ArtifactSelection, ArtifactSelection], T],
    unavailable: Callable[[ArtifactSelection, LocalFailure], T],
) -> T:
    try:
        path = storage._unlinked(database)
        if path != pin.path:
            return unavailable(selected, "unregistered_workspace")
        before = _stamp(path, pin)
        review, draft = pair()
        if selected not in (review, draft) or not _matches_workspace(path, pin, selected):
            return unavailable(selected, "exact_selection_unavailable")
        try:
            view = project(reader((selected,)), selected, review)
        except (ValueError, OSError, LookupError, TypeError, sqlite3.Error, SecretLeakError):
            return unavailable(selected, "publication_unavailable")
        require(before == _stamp(path, pin), "workspace_changed_during_lookup")
        return view
    except (ValueError, OSError, LookupError, sqlite3.Error, SQLAlchemyError, SecretLeakError):
        return unavailable(selected, "workspace_unavailable")
