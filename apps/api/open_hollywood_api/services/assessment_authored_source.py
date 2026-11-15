"""Registered local authored-source exports; no saved-review or observed-delivery coercion."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from open_hollywood_engine.evaluations import assessment_authored_source as domain
from open_hollywood_engine.evaluations.assessment_authored_source import (
    NOTICE,
    ORIGIN,
    AuthoredSource,
    AuthoredSourceSubmission,
    complete_fixture,
    fixture_template,
    render_presentation,
    validate_source,
)
from open_hollywood_engine.evaluations.assessment_authority import render_assessment_authority
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import Digest, Record, require, strict_object

from open_hollywood_api.services import assessment_completion as publication
from open_hollywood_api.services.assessment_completion import (
    MAX_BUNDLE_BYTES,
    MAX_SUBMISSION_BYTES,
    _destination,
    _publish,
    _read,
    _sha,
    _unlinked,
)

SOURCE_ID = "fresh-claims-2026-11-15"
ROOT = Path(__file__).resolve().parents[4]
SAFE_MEMBERS = (
    "work.json",
    "scope.json",
    "declarations.json",
    "briefs.json",
    "authority.json",
    "source-packet.json",
)


@dataclass(frozen=True)
class Registration:
    source_id: str
    root: Path
    manifest_sha256: str


REGISTERED = (
    Registration(
        SOURCE_ID,
        ROOT / "data/diagnostics/assessment-fresh-claim-admission-2026-11-15",
        "2578f9b350175768d208773484ddde4fc459e78b9d77354db94fdec4d61fcfef",
    ),
)


class AdmissionManifest(Record):
    contract: Literal["assessment-authored-admission-bundle-1"]
    helper_sha256: Digest
    material_sha256: Digest
    members_sha256: dict[str, Digest]
    origin: str
    live_calls: Literal[0]
    model_evidence: Literal[False]
    writer_dispatch_authorized: Literal[False]


@dataclass(frozen=True)
class Collected:
    source: AuthoredSource
    protected: tuple[Path, ...]
    safe_members: dict[str, bytes]
    authenticated_members: dict[str, bytes]
    source_receipt: bytes
    implementation_sha256: dict[str, str]


def _implementation() -> dict[str, str]:
    # Include reused native validators/renderers and publication primitives.
    modules = (domain, publication)
    paths = {Path(m.__file__).resolve() for m in modules if m.__file__ is not None}
    paths.add(Path(__file__).resolve())
    paths.update(Path(domain.__file__).parent.glob("assessment_*.py"))
    paths.update(
        Path(domain.__file__).parent / name for name in ("review_evidence.py", "contracts.py")
    )
    return {p.relative_to(ROOT).as_posix(): _sha(_read(p)) for p in sorted(paths)}


def collect(source_id: str, family: str) -> Collected:
    """Only a fixed registry may authenticate authored bytes; never execute archive helpers."""
    registrations = [r for r in REGISTERED if r.source_id == source_id]
    require(len(registrations) == 1, "authored_unregistered_source")
    require(family in ("F01", "F02", "F03"), "authored_unknown_family")
    registration = registrations[0]
    root = _unlinked(registration.root)
    folder = _unlinked(root / "admitted")
    manifest_raw = _read(folder / "manifest.json", MAX_SUBMISSION_BYTES)
    require(_sha(manifest_raw) == registration.manifest_sha256, "authored_registration_changed")
    manifest = AdmissionManifest.model_validate_json(encoded(strict_object(manifest_raw.decode())))
    require(manifest.origin == ORIGIN, "authored_manifest_origin")
    names = {"admission-decisions.json", "cases-and-gold.md", "readiness.json"}
    names.update(
        f"{f}/{n}"
        for f in ("F01", "F02", "F03")
        for n in (*SAFE_MEMBERS, "admission.json", "preview.json", "view.md")
    )
    require(set(manifest.members_sha256) == names, "authored_manifest_members")
    require(
        {p.name for p in folder.iterdir()}
        == {
            "F01",
            "F02",
            "F03",
            "manifest.json",
            "admission-decisions.json",
            "cases-and-gold.md",
            "readiness.json",
        },
        "authored_source_members",
    )
    for f in ("F01", "F02", "F03"):
        child = _unlinked(folder / f)
        require(
            child.is_dir()
            and {p.name for p in child.iterdir()}
            == {
                *SAFE_MEMBERS,
                "admission.json",
                "preview.json",
                "view.md",
            },
            "authored_source_members",
        )
    members = {"manifest.json": manifest_raw}
    size = len(manifest_raw)
    for name in sorted(names):
        raw = _read(folder / name, min(publication.MAX_FILE_BYTES, MAX_BUNDLE_BYTES - size))
        size += len(raw)
        require(size <= MAX_BUNDLE_BYTES, "authored_archive_too_large")
        require(_sha(raw) == manifest.members_sha256[name], "authored_source_changed")
        members[name] = raw
    for name, digest in (
        ("admit.py", manifest.helper_sha256),
        ("material.py", manifest.material_sha256),
    ):
        raw = _read(root / name)
        require(_sha(raw) == digest, "authored_construction_changed")
        members["../" + name] = raw
    # Gold members are authenticated bytes only, never parsed into an input or result.
    safe = {n: members[f"{family}/{n}"] for n in SAFE_MEMBERS}
    source = AuthoredSource.model_validate_json(
        encoded(
            {
                "contract": "assessment-authored-source-1",
                "source": {
                    "source_origin": "authored_diagnostic",
                    "source_id": source_id,
                    "family": family,
                    "manifest_bytes_sha256": _sha(manifest_raw),
                    "input_members_sha256": {n: _sha(raw) for n, raw in safe.items()},
                },
                **{
                    key: strict_object(safe[name].decode())
                    for key, name in (
                        ("work", "work.json"),
                        ("original_scope", "scope.json"),
                        ("declarations", "declarations.json"),
                        ("briefs", "briefs.json"),
                        ("authority", "authority.json"),
                        ("source_packet", "source-packet.json"),
                    )
                },
            }
        )
    )
    source = validate_source(source)
    receipt = encoded(
        {
            "contract": "assessment-authored-source-receipt-1",
            "source": source.source.model_dump(mode="json"),
            "source_origin": "authored_diagnostic",
            "authentication": "fixed_registered_local_authored_archive",
            "authenticated_admission_members": len(names) + 1,
            "construction_files_authenticated_not_executed": ["admit.py", "material.py"],
            "gold_in_model_input": False,
            "independent_human_gold": False,
            "historical_model_visibility": "not_applicable_no_model_review",
            "assessment_delivery_authenticated": False,
            "live_calls": 0,
        }
    )
    return Collected(source, (root,), safe, members, receipt, _implementation())


def _manifest(files: dict[str, bytes], collected: Collected, mode: str) -> bytes:
    return encoded(
        {
            "contract": "assessment-authored-source-export-1",
            "mode": mode,
            "source_origin": "authored_diagnostic",
            "delivery_origin": "authored_fixture" if mode == "fixture" else None,
            "source": collected.source.source.model_dump(mode="json"),
            "implementation_sha256": collected.implementation_sha256,
            "files_sha256": {n: _sha(raw) for n, raw in files.items()},
            "notice": NOTICE,
            "model_evidence": False,
            "live_calls": 0,
            "writer_dispatch_authorized": False,
        }
    )


def prepare(source_id: str, family: str, destination: Path) -> Literal["created", "reused"]:
    collected = collect(source_id, family)
    source = collected.source
    files = {
        **collected.safe_members,
        "source.json": encoded(source.model_dump(mode="json")),
        "source-receipt.json": collected.source_receipt,
        "presentation.json": encoded(render_presentation(source).model_dump(mode="json")),
        "submission.template.json": encoded(fixture_template(source)),
        "view.md": (
            NOTICE
            + "\n\n"
            + render_assessment_authority(
                source.work,
                source.original_scope,
                source.declarations,
                source.briefs,
                source.authority,
            )
        ).encode(),
    }
    files["manifest.json"] = _manifest(files, collected, "preparation")

    def recheck() -> None:
        require(collect(source_id, family) == collected, "authored_source_drift")

    return _publish(destination, files, collected.protected, recheck)


def publish_fixture(
    source_id: str, family: str, submission_path: Path, destination: Path
) -> Literal["created", "reused"]:
    collected = collect(source_id, family)
    submission_path = _destination(submission_path, collected.protected)
    raw = _read(submission_path, MAX_SUBMISSION_BYTES)
    submission = AuthoredSourceSubmission.model_validate_json(encoded(strict_object(raw.decode())))
    envelope, view = complete_fixture(collected.source, submission)
    files = {
        **collected.safe_members,
        "source.json": encoded(collected.source.model_dump(mode="json")),
        "source-receipt.json": collected.source_receipt,
        "presentation.json": encoded(render_presentation(collected.source).model_dump(mode="json")),
        "submission.json": raw,
        "envelope.json": encoded(envelope),
        "view.md": view.encode(),
    }
    files["manifest.json"] = _manifest(files, collected, "fixture")

    def recheck() -> None:
        require(_read(submission_path, MAX_SUBMISSION_BYTES) == raw, "authored_submission_drift")
        require(collect(source_id, family) == collected, "authored_source_drift")

    return _publish(destination, files, (*collected.protected, submission_path), recheck)
