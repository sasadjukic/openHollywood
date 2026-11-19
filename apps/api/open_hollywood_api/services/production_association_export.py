"""Registered historical association export. No SQLite, transport or assessment admission."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal
from uuid import UUID

from open_hollywood_engine.evaluations import contracts, review_evidence
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import (
    JsonObject,
    object_value,
    require,
    strict_object,
)

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import production_association_records as records

ROOT = Path(__file__).resolve().parents[4]
CASES = tuple(f"R{n:02d}" for n in range(1, 7))


@dataclass(frozen=True)
class _Registration:
    name: str
    archive: Path
    seal_sha256: str
    database: Path


REGISTERED = (
    _Registration(
        "production-association-2026-11-19",
        ROOT / "data/diagnostics/assessment-production-association-2026-11-19",
        "4b07e7b673922b5620909ceb28721349cadede88859f4f4c2deecc1e37804578",
        ROOT / "data/open_hollywood.db",
    ),
)


def _object(raw: bytes) -> JsonObject:
    return strict_object(raw.decode("utf-8-sig"))


def _implementation() -> dict[str, str]:
    return {
        name: storage._sha(path.read_bytes())
        for name, path in (
            ("adapter", Path(__file__)),
            ("records", Path(records.__file__)),
            ("storage", Path(storage.__file__)),
            ("native_records", Path(review_evidence.__file__)),
            ("canonical_hash", Path(contracts.__file__)),
            ("cli", ROOT / "scripts/production_association.py"),
        )
    }


def _collect(registration: _Registration) -> dict[str, bytes]:
    root = storage._unlinked(registration.archive)
    seal = storage._read(root / "acceptance-seal.json")
    require(storage._sha(seal) == registration.seal_sha256, "association_registered_seal_changed")
    body = _object(seal)
    require(
        body.get("contract") == "production-association-acceptance-seal-1",
        "association_seal_contract",
    )
    members = object_value(body.get("members_sha256"))
    require(1 <= len(members) <= 128, "association_archive_bound")
    directories = {"."}
    for name in members:
        member_path = PurePosixPath(name)
        require(
            not member_path.is_absolute()
            and member_path.as_posix() == name
            and all(
                part not in (".", "..", "__pycache__")
                and all(c.isascii() and (c.isalnum() or c in "-_.") for c in part)
                for part in member_path.parts
            )
            and name != "acceptance-seal.json",
            "association_archive_member_path",
        )
        directories.update(p.as_posix() for p in member_path.parents)
    pending = [root]
    found: set[str] = set()
    while pending:
        directory = storage._unlinked(pending.pop())
        relative = directory.relative_to(root).as_posix()
        if directory.name == "__pycache__":
            continue  # Never loaded or executed; omitted by the original archive seal.
        require(relative in directories, "association_archive_directory_changed")
        for path in directory.iterdir():
            path = storage._unlinked(path)
            if path.is_dir():
                pending.append(path)
            else:
                require(path.is_file(), "association_archive_not_file")
                found.add(path.relative_to(root).as_posix())
                require(len(found) <= 129, "association_archive_bound")
    require(found == {*members, "acceptance-seal.json"}, "association_archive_inventory_changed")
    files = {}
    total = len(seal)
    for name, digest in members.items():
        data = storage._read(root / name)
        total += len(data)
        require(total <= storage.MAX_OUTPUT_BYTES, "association_archive_size")
        require(storage._sha(data) == digest, "association_archive_member_changed")
        files[name] = data
    files["acceptance-seal.json"] = seal
    return files


def _expectations(
    files: dict[str, bytes], registration: _Registration
) -> tuple[records.ExpectedReview, ...]:
    selection = _object(files["selection.json"])
    rows = selection.get("reviews")
    require(
        selection.get("maximum_reviews") == 6 and isinstance(rows, list) and len(rows) == 6,
        "association_selection_coverage",
    )
    assert isinstance(rows, list)
    # The path is a locator in the registered capture, not permission to open a database.
    pins = _object(files["database-before.json"])
    pin = object_value(pins.get(str(registration.database)))
    results = []
    for row in rows:
        value = object_value(row)
        selected = {
            key: str(UUID(str(value[key])))
            for key in (
                "invocation_id",
                "workflow_run_id",
                "project_id",
                "critique_artifact_id",
                "critique_version_id",
                "draft_version_id",
            )
        }
        results.append(
            records.ExpectedReview.model_validate_json(
                encoded(
                    {
                        **selected,
                        "database_snapshot_sha256": pin["sha256"],
                    }
                )
            )
        )
    require(
        len({r.invocation_id for r in results})
        == len({r.critique_version_id for r in results})
        == 6,
        "association_duplicate_selection",
    )
    return tuple(results)


def export_associations(source: str, destination: Path) -> Literal["created", "reused"]:
    """Authenticate one complete fixed archive; accept no caller records, hashes or DB paths."""
    matches = [r for r in REGISTERED if r.name == source]
    require(len(matches) == 1, "association_unregistered_source")
    registration = matches[0]
    protected = (
        registration.archive,
        registration.database,
        Path(str(registration.database) + "-wal"),
        Path(str(registration.database) + "-shm"),
    )
    storage._destination(destination, protected)
    originals = _collect(registration)
    expected = _expectations(originals, registration)
    implementation = _implementation()

    def recheck() -> None:
        require(
            _collect(registration) == originals and _implementation() == implementation,
            "association_source_or_implementation_drift",
        )

    files = {
        "source-seal.json": originals["acceptance-seal.json"],
        "source-selection.json": originals["selection.json"],
        "source-database-pins.json": originals["database-before.json"],
    }
    evidence = []
    for case, expectation in zip(CASES, expected, strict=True):
        member = f"{case}.snapshot.json"
        raw = originals[member]
        snapshot = records.AssociationSnapshot.model_validate_json(encoded(_object(raw)))
        proof = records.validate_snapshot(snapshot, expectation)
        record = records.AssociationRecord(
            source=records.SourceAuthentication(
                registration=source,
                archive_seal_bytes_sha256=registration.seal_sha256,
                snapshot_member=member,
                snapshot_bytes_sha256=storage._sha(raw),
            ),
            evidence=proof,
        )
        evidence.append(proof)
        files[member] = raw
        files[f"{case}.association.json"] = encoded(record.model_dump(mode="json"))
        files[f"{case}.md"] = records.render_record(record)
    files["README.md"] = (
        "# Historical production associations\n\n" + records.NOTICE + "\n\n"
        "Six complete registered source records. The original snapshots, selection, "
        "database pins and archive seal are retained byte-exact. The complete audit archive "
        "was verified; this export contains only the nine source evidence members needed "
        "to inspect these records, not the archive's logs or private scripts.\n\n"
        + "\n".join(f"- [{case}: association and source]({case}.md)" for case in CASES)
        + "\n\nThe database hash identifies the historical capture, not a permanent workspace "
        "identity. No live database was opened or revalidated. Older versions remain fixed; "
        "head information is as of capture. Current assessment admission remains unsupported "
        "and native assessment delivery missing.\n"
    ).encode("utf-8")
    files["manifest.json"] = encoded(
        {
            "contract": "production-association-export-1",
            "notice": records.NOTICE,
            "registration": source,
            "source_archive": str(registration.archive),
            "source_seal_bytes_sha256": registration.seal_sha256,
            "cases": list(CASES),
            "source_members_verified": len(originals),
            "copied_source_members": 9,
            "source_basis": "registered_audit_snapshot",
            "current_database_revalidated": False,
            "implementation_sha256": implementation,
            "files_sha256": {name: storage._sha(raw) for name, raw in files.items()},
            "binding_sha256": {
                case: proof.binding_sha256 for case, proof in zip(CASES, evidence, strict=True)
            },
            "identity_status": "verified_in_registered_snapshot",
            "eligibility": records.Eligibility().model_dump(mode="json"),
            "semantic_support": "unassessed",
            "evidence_adequacy": "unassessed",
            "editorial_effect": "unassessed",
            "edit_necessity": "unassessed",
            "craft": "unassessed",
            "writer_dispatch_authorized": False,
            "whole_review_verdict": None,
            "actual_billed_cost": None,
            "live_calls": 0,
        }
    )
    return storage._publish(destination, files, protected, recheck)
