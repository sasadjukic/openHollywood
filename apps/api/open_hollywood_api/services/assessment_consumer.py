"""Export complete, authenticated fixed diagnostic publications for read-only consumption."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import JsonObject, require, strict_object

from open_hollywood_api.services import assessment_authored_observed_completion as authored
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_consumer_projection as projection
from open_hollywood_api.services import assessment_observed_completion as probe

ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class _Registration:
    name: str
    publication: Path
    manifest_sha256: str
    source_origin: projection.SourceOrigin
    works: tuple[str, ...]
    member_count: int


REGISTERED = (
    _Registration(
        "authored-smoke-2026-11-15",
        ROOT
        / "data/diagnostics/assessment-authored-observed-completion-2026-11-15"
        / "verified-publication",
        "dae565b39755dbc58c252f98bfb6267e5a632fdfb5ff886e61640efe3005fca0",
        "authored_diagnostic",
        ("F01", "F02", "F03"),
        43,
    ),
    _Registration(
        "compact-smoke-2026-11-14",
        ROOT
        / "data/diagnostics/assessment-observed-completion-2026-11-14"
        / "verified-publication",
        "465786a0d70d1ae5997d02bbc023a59f55b1f9aa300114f05c684b430746c283",
        "registered_diagnostic_probe",
        ("N06", "N07", "N10", "N11"),
        27,
    ),
)


def _object(data: bytes) -> JsonObject:
    return strict_object(data.decode("utf-8"))


def _implementation() -> JsonObject:
    return {
        "adapter": storage._sha(Path(__file__).read_bytes()),
        "projection": storage._sha(Path(projection.__file__).read_bytes()),
        "storage": storage._sha(Path(storage.__file__).read_bytes()),
        "cli": storage._sha((ROOT / "scripts/assessment_consumer.py").read_bytes()),
        "authored_publisher": authored._implementation(),
        "probe_publisher": probe._implementation(),
    }


def _collect(registration: _Registration) -> tuple[dict[str, bytes], JsonObject]:
    directory = storage._unlinked(registration.publication)
    raw_manifest = storage._read(directory / "manifest.json")
    require(
        storage._sha(raw_manifest) == registration.manifest_sha256,
        "consumer_registered_manifest_changed",
    )
    manifest = _object(raw_manifest)
    expected = manifest.get("files_sha256")
    require(isinstance(expected, dict), "consumer_source_members")
    assert isinstance(expected, dict)
    require(len(expected) + 1 == registration.member_count <= 64, "consumer_source_member_bound")
    reserved = {"manifest.json", "source-manifest.json", "README.md"}
    require(
        all(
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", n)
            and n not in reserved
            and not n.startswith("consumer.")
            for n in expected
        ),
        "consumer_source_filename",
    )
    require(
        {p.name for p in directory.iterdir()} == {*expected, "manifest.json"},
        "consumer_source_inventory_changed",
    )
    files = {name: storage._read(directory / name) for name in expected}
    require(sum(map(len, files.values())) <= storage.MAX_OUTPUT_BYTES, "consumer_source_size_bound")
    require(
        expected == {name: storage._sha(data) for name, data in files.items()},
        "consumer_source_bytes_changed",
    )
    files["manifest.json"] = raw_manifest
    is_authored = registration.source_origin == "authored_diagnostic"
    require(
        manifest.get("contract")
        == (
            "assessment-authored-observed-publication-1"
            if is_authored
            else "assessment-observed-publication-1"
        )
        and manifest.get("source_origin") == registration.source_origin
        and manifest.get("delivery_origin" if is_authored else "origin")
        == "observed_openai_transport"
        and manifest.get("works") == list(registration.works)
        and manifest.get("state") == "bound_unassessed"
        and manifest.get("accounting_clear") is True
        and manifest.get("actual_billed_cost") is None
        and manifest.get("semantic_support") == manifest.get("evidence_adequacy") == "unassessed"
        and manifest.get("live_calls") == 0
        and manifest.get("writer_dispatch_authorized") is False,
        "consumer_publication_ineligible",
    )
    return files, manifest


def export_consumer(source: str, destination: Path) -> Literal["created", "reused"]:
    """Only fixed names and a new output directory; no caller assertions or partial exports."""
    matches = [r for r in REGISTERED if r.name == source]
    require(len(matches) == 1, "consumer_unregistered_source")
    registration = matches[0]
    original, manifest = _collect(registration)
    pins = manifest.get("source_members_sha256")
    require(isinstance(pins, dict) and 0 < len(pins) <= 4096, "consumer_source_pins")
    assert isinstance(pins, dict)
    # Paths become authoritative only after the entire registered manifest is pinned.
    roots = tuple(Path(name) for name in pins)
    protected = (registration.publication, *roots)
    storage._destination(destination, protected)
    implementation = _implementation()

    def recheck() -> None:
        require(
            _collect(registration) == (original, manifest)
            and probe._snapshot(roots) == pins
            and _implementation() == implementation,
            "consumer_source_or_implementation_drift",
        )

    recheck()
    publisher = authored if registration.source_origin == "authored_diagnostic" else probe
    # No missing publication is created or repaired: _collect above requires its exact
    # pinned bytes. The supported publisher reauthenticates its upstream audit/journal.
    require(
        publisher.publish_observed(source, registration.publication) == "reused",
        "consumer_original_publication_must_reuse",
    )
    recheck()
    binding = manifest.get("observation_binding")
    require(isinstance(binding, dict), "consumer_observation_binding")
    assert isinstance(binding, dict)
    views = tuple(
        projection._project(
            _object(original[f"{name}.completion.json"]),
            registration=source,
            publication_sha256=registration.manifest_sha256,
            work_name=name,
            source_origin=registration.source_origin,
            observation_binding=binding,
        )
        for name in registration.works
    )
    files = {name: data for name, data in original.items() if name != "manifest.json"}
    files["source-manifest.json"] = original["manifest.json"]
    for view in views:
        files[f"consumer.{view.work}.json"] = encoded(view.model_dump(mode="json"))
        files[f"consumer.{view.work}.md"] = projection._render(view)
    files["README.md"] = (
        "# Read-only diagnostic assessment export\n\n" + projection.NOTICE + "\n\n"
        "Complete registered delivery inventory; no whole-review verdict. Every original "
        "publication member is retained byte-exact. Its manifest is retained as "
        "[source-manifest.json](source-manifest.json); native relative links remain intact. "
        "Missing, failed, altered or accounting-held input refuses the entire export.\n\n"
        + "\n".join(f"- [{v.work}](consumer.{v.work}.md)" for v in views)
        + "\n\nNo canonical review or artifact-version association is qualified. "
        "This export makes no provider calls and gives no writer permission.\n"
    ).encode("utf-8")
    files["manifest.json"] = encoded(
        {
            "contract": "assessment-consumer-publication-1",
            "notice": projection.NOTICE,
            "registration": source,
            "source_origin": registration.source_origin,
            "delivery_origin": "observed_openai_transport",
            "state": "observed_bound_unassessed",
            "works": list(registration.works),
            "source_publication_path": str(registration.publication),
            "source_manifest_bytes_sha256": registration.manifest_sha256,
            "observation_binding": binding,
            "implementation_sha256": implementation,
            "source_members_sha256": pins,
            "files_sha256": {name: storage._sha(data) for name, data in files.items()},
            "original_member_mapping": {
                n: "source-manifest.json" if n == "manifest.json" else n for n in original
            },
            "production_binding": projection.ProductionBinding().model_dump(mode="json"),
            "whole_review_verdict": None,
            "accounting_clear": True,
            "actual_billed_cost": None,
            **projection.Holds().model_dump(mode="json"),
            "live_calls": 0,
        }
    )
    return storage._publish(destination, files, protected, recheck)
