"""Registered local workspace lookup. No route, publication, inference or assessment admission."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from uuid import UUID

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import Digest, Identifier, Record, require
from open_hollywood_engine.secrets import SecretLeakError
from pydantic import Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from open_hollywood_api.persistence.database import database_path_from_environment
from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import production_association_export as archive
from open_hollywood_api.services import production_association_records as records
from open_hollywood_api.services import production_association_rows as rows
from open_hollywood_api.services.review_evidence_export import readonly_connection
from open_hollywood_api.services.workspace import WorkspaceStore


@dataclass(frozen=True)
class _Workspace:
    name: str
    path: Path
    device: int
    inode: int
    association: str


# Narrow local qualification, not a portable installation ID. Replacement/restore needs
# explicit requalification; neither a caller path nor a copied database is an authority.
REGISTERED = (
    _Workspace(
        "local-production-workspace-2026-11-19",
        archive.ROOT / "data/open_hollywood.db",
        2372488652078295932,
        7036874418153096,
        "production-association-2026-11-19",
    ),
)


class LookupRequest(Record):
    workspace: str = Field(min_length=1, max_length=100)
    selections: tuple[records.ArtifactSelection, ...] = Field(min_length=1, max_length=12)


class CurrentLineage(Record):
    latest_version_id: Identifier
    selected_is_latest: bool
    version_count: int = Field(ge=1, le=64)
    selected_parent_version_id: Identifier | None


def _current_lineage(value: records.LineageFacts) -> CurrentLineage:
    return CurrentLineage(
        latest_version_id=value.latest_version_id_at_capture,
        selected_is_latest=value.selected_is_latest_at_capture,
        version_count=value.version_count,
        selected_parent_version_id=value.selected_parent_version_id,
    )


class CurrentIdentity(Record):
    historical: records.AssociationRecord
    current_rows_sha256: Digest
    # These fields describe this read transaction; the nested historical fields stay at capture.
    review_lineage_at_lookup: CurrentLineage
    draft_lineage_at_lookup: CurrentLineage
    application_exact_version_read_verified: Literal[True] = True
    selected_rows_revalidated: Literal[True] = True
    assessment_attachment_eligible: Literal[False] = False
    semantic_support: Literal["unassessed"] = "unassessed"
    writer_dispatch_authorized: Literal[False] = False


class LookupEntry(Record):
    selection: records.ArtifactSelection
    status: Literal["identity_verified", "unavailable"]
    reason: Literal[
        "exact_registered_identity",
        "no_registered_association",
        "selection_mismatch",
        "ambiguous_association",
        "current_source_missing",
        "current_source_mismatch",
    ]
    identity: CurrentIdentity | None = None


class LookupResult(Record):
    contract: Literal["production-workspace-association-lookup-1"] = (
        "production-workspace-association-lookup-1"
    )
    workspace: str
    request_sha256: Digest
    workspace_source_basis: Literal["registered_local_file_identity_and_current_rows"] = (
        "registered_local_file_identity_and_current_rows"
    )
    portable_workspace_identity: Literal[False] = False
    archive_seal_bytes_sha256: Digest
    entries: tuple[LookupEntry, ...]
    current_read_transaction_verified: Literal[True] = True
    assessment_attachment_eligible: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False
    live_calls: Literal[0] = 0


def _source_stamp(workspace: _Workspace) -> tuple[tuple[str, int, int, int, int], ...]:
    path = storage._unlinked(workspace.path)
    require(path.is_file(), "lookup_workspace_missing")
    stat = path.stat()
    require(
        (stat.st_dev, stat.st_ino) == (workspace.device, workspace.inode),
        "lookup_workspace_replaced",
    )
    result = []
    # SHM read-lock coordination is not manuscript mutation. Main/WAL changes abort this
    # bounded lookup; changes between separate lookups are allowed if selected rows match.
    for member in (path, Path(str(path) + "-wal")):
        storage._unlinked(member)
        if member.exists():
            value = member.stat()
            result.append(
                (str(member), value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)
            )
    storage._unlinked(Path(str(path) + "-shm"))
    return tuple(result)


def _candidates(
    registration: archive._Registration, files: dict[str, bytes]
) -> tuple[tuple[records.AssociationSnapshot, records.AssociationRecord], ...]:
    result = []
    for case, expected in zip(
        archive.CASES, archive._expectations(files, registration), strict=True
    ):
        member = f"{case}.snapshot.json"
        snapshot = records.AssociationSnapshot.model_validate_json(
            encoded(archive._object(files[member]))
        )
        result.append(
            (
                snapshot,
                records.AssociationRecord(
                    source=records.SourceAuthentication(
                        registration=registration.name,
                        archive_seal_bytes_sha256=registration.seal_sha256,
                        snapshot_member=member,
                        snapshot_bytes_sha256=storage._sha(files[member]),
                    ),
                    evidence=records.validate_snapshot(snapshot, expected),
                ),
            )
        )
    return tuple(result)


def _implementation() -> dict[str, str]:
    from open_hollywood_api.services import review_evidence_export as reader
    from open_hollywood_api.services import workspace as workspace_module

    return {
        **archive._implementation(),
        **{
            name: storage._sha(path.read_bytes())
            for name, path in (
                ("lookup", Path(__file__)),
                ("current_rows", Path(rows.__file__)),
                ("workspace_read", Path(workspace_module.__file__)),
                ("read_only_sqlite", Path(reader.__file__)),
            )
        },
    }


def lookup(request: LookupRequest) -> LookupResult:
    """Return selected identity evidence only after whole-batch source checks succeed."""
    request = LookupRequest.model_validate_json(request.model_dump_json())
    keys = [s.model_dump_json() for s in request.selections]
    require(len(set(keys)) == len(keys), "lookup_duplicate_selection")
    matches = [w for w in REGISTERED if w.name == request.workspace]
    require(len(matches) == 1, "lookup_unregistered_workspace")
    workspace = matches[0]
    require(
        storage._unlinked(database_path_from_environment()) == storage._unlinked(workspace.path),
        "lookup_configured_workspace_mismatch",
    )
    registrations = [r for r in archive.REGISTERED if r.name == workspace.association]
    require(len(registrations) == 1, "lookup_unregistered_archive")
    registration = registrations[0]
    require(
        registration.database.absolute() == workspace.path.absolute(),
        "lookup_archive_workspace_mismatch",
    )
    before = _source_stamp(workspace)
    files = archive._collect(registration)
    candidates = _candidates(registration, files)
    implementation = _implementation()
    entries = []
    with readonly_connection(workspace.path) as raw:
        # Reuse the application's exact-version read model on this same read-only
        # connection. Avoid the normal engine factory (mkdir + WAL configuration).
        engine = create_engine("sqlite+pysqlite://", creator=lambda: raw, poolclass=StaticPool)
        try:
            with engine.connect() as connection, connection.begin():
                # Dialect initialization may roll back the initial DBAPI transaction.
                if not raw.in_transaction:
                    connection.exec_driver_sql("BEGIN")
                require(raw.execute("PRAGMA query_only").fetchone()[0] == 1, "lookup_not_readonly")
                store = WorkspaceStore(
                    sessionmaker(
                        bind=connection,
                        class_=Session,
                        autoflush=False,
                        join_transaction_mode="rollback_only",
                        expire_on_commit=False,
                    )
                )
                for selection in request.selections:
                    same_version = [
                        (s, r)
                        for s, r in candidates
                        if (
                            r.evidence.binding.critique_version_id
                            if selection.role == "original_review"
                            else r.evidence.binding.target_version_id
                        )
                        == selection.version_id
                    ]
                    matched = [
                        (s, r) for s, r in same_version if records.selection_matches(r, selection)
                    ]
                    reason: str | None = None
                    if not same_version:
                        reason = "no_registered_association"
                    elif not matched:
                        reason = "selection_mismatch"
                    elif len(matched) != 1:
                        reason = "ambiguous_association"
                    if reason is not None:
                        entries.append(
                            LookupEntry.model_validate(
                                {
                                    "selection": selection,
                                    "status": "unavailable",
                                    "reason": reason,
                                }
                            )
                        )
                        continue
                    original, record = matched[0]
                    try:
                        review_history, draft_history, digest = rows.revalidate(raw, original)
                        rows._rows(
                            raw,
                            "SELECT id FROM evaluations WHERE artifact_version_id=?",
                            selection.version_id,
                            128,
                        )
                        detail = store.get_artifact_version(UUID(selection.version_id))
                        require(raw.in_transaction, "lookup_read_transaction_lost")
                        old = (
                            original.review
                            if selection.role == "original_review"
                            else next(
                                row for row in original.inputs if row.id == selection.version_id
                            )
                        )
                        rows._require(
                            str(detail.selected_version.id) == selection.version_id
                            and str(detail.artifact.id) == selection.artifact_id
                            and detail.artifact.artifact_type == old.artifact_type
                            and detail.artifact.artifact_key == old.artifact_key
                            and detail.selected_version.schema_version == old.schema_version
                            and detail.content == old.content
                            and detail.content_sha256 == selection.content_sha256
                            and canonical_sha256(detail.content) == selection.content_sha256
                            and detail.selected_version.version_number == old.version_number
                            and (
                                str(detail.selected_version.parent_version_id)
                                if detail.selected_version.parent_version_id
                                else None
                            )
                            == old.parent_version_id
                        )
                        entries.append(
                            LookupEntry(
                                selection=selection,
                                status="identity_verified",
                                reason="exact_registered_identity",
                                identity=CurrentIdentity(
                                    historical=record,
                                    current_rows_sha256=digest,
                                    review_lineage_at_lookup=_current_lineage(review_history),
                                    draft_lineage_at_lookup=_current_lineage(draft_history),
                                ),
                            )
                        )
                    except SecretLeakError:
                        raise
                    except (rows.Unavailable, ValueError) as exc:
                        reason = (
                            "current_source_missing"
                            if str(exc) == "current_source_missing"
                            else "current_source_mismatch"
                        )
                        entries.append(
                            LookupEntry.model_validate(
                                {
                                    "selection": selection,
                                    "status": "unavailable",
                                    "reason": reason,
                                }
                            )
                        )
                require(
                    raw.in_transaction and raw.total_changes == 0, "lookup_readonly_transaction"
                )
        finally:
            engine.dispose()
    require(_source_stamp(workspace) == before, "lookup_workspace_changed_during_read")
    require(
        archive._collect(registration) == files and _implementation() == implementation,
        "lookup_source_or_code_drift",
    )
    result = LookupResult(
        workspace=workspace.name,
        request_sha256=canonical_sha256(request.model_dump(mode="json")),
        archive_seal_bytes_sha256=registration.seal_sha256,
        entries=tuple(entries),
    )
    active_secret_guard().ensure_safe(
        result.model_dump(mode="json"), destination="association lookup"
    )
    return result
