"""Read-only authored completion publication over registered probe intake sources."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from open_hollywood_engine.evaluations import assessment_completion as domain
from open_hollywood_engine.evaluations.assessment_completion import (
    NOTICE,
    CompletionContext,
    derive,
    encoded,
    expected_pin,
    fixture_input,
    parse_submission,
    render_completion,
)
from open_hollywood_engine.evaluations.assessment_intake import IntakeResult, compile_intake
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    require,
    strict_object,
)
from pydantic import Field

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services.assessment_intake import IntakeBatchPlan, collect_intakes
from open_hollywood_api.services.probe_review_export import archive_contract, protected_archives

MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_SUBMISSION_BYTES = 4 * 1024 * 1024
MAX_BUNDLE_BYTES = 64 * 1024 * 1024
MAX_OUTPUT_BYTES = 64 * 1024 * 1024


class _IntakeManifest(Record):
    contract: Literal["ordinary-review-intake-manifest-1"]
    origin: Literal["diagnostic_probe"]
    source_path: str = Field(min_length=1, max_length=4096)
    review_ids: tuple[str, ...] = Field(min_length=1, max_length=12)
    source_sha256: Digest
    plan_sha256: Digest
    implementation_sha256: dict[str, Digest]
    files_sha256: dict[str, Digest]
    live_calls: Literal[0]


@dataclass(frozen=True)
class _Collected:
    context: CompletionContext
    protected: tuple[Path, ...]
    bundle_members: dict[str, bytes]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unlinked(path: Path) -> Path:
    require(".." not in path.parts, "completion_path_traversal")
    path = path.absolute()
    for part in (path, *path.parents):
        require(not part.is_symlink() and not part.is_junction(), "completion_linked_path")
    return path.resolve()


def _read(path: Path, limit: int = MAX_FILE_BYTES) -> bytes:
    path = _unlinked(path)
    require(path.is_file(), "completion_input_not_file")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "completion_input_too_large")
    # This also rejects invalid UTF-8 in Markdown members without normalizing bytes.
    active_secret_guard().ensure_safe(data.decode("utf-8"), destination="completion input")
    return data


def _collect(intake_path: Path) -> _Collected:
    """No caller contract override: trust is selected only from the registered archive."""
    intake_path = _unlinked(intake_path)
    folder = intake_path.parent
    manifest_bytes = _read(folder / "manifest.json", MAX_SUBMISSION_BYTES)
    manifest = _IntakeManifest.model_validate_json(
        encoded(strict_object(manifest_bytes.decode("utf-8")))
    )
    require(len(set(manifest.review_ids)) == len(manifest.review_ids), "completion_review_ids")
    names = {"index.json", "index.md", "plan.json"}
    for n in range(1, len(manifest.review_ids) + 1):
        names.update((f"review-{n:02d}.json", f"review-{n:02d}.md"))
    require(set(manifest.files_sha256) == names, "completion_bundle_members")
    require(
        {p.name for p in folder.iterdir()} == names | {"manifest.json"},
        "completion_bundle_members",
    )
    require(
        intake_path.name
        in {f"review-{n:02d}.json" for n in range(1, len(manifest.review_ids) + 1)},
        "completion_intake_member",
    )
    members = {"manifest.json": manifest_bytes}
    size = len(manifest_bytes)
    for name in sorted(names):
        data = _read(folder / name, min(MAX_FILE_BYTES, MAX_BUNDLE_BYTES - size))
        size += len(data)
        require(size <= MAX_BUNDLE_BYTES, "completion_bundle_too_large")
        require(_sha(data) == manifest.files_sha256[name], "completion_bundle_changed")
        members[name] = data
    path = Path(manifest.source_path)
    require(path.is_absolute(), "completion_relative_source")
    path = _unlinked(path)
    contract = archive_contract(path)
    protected = tuple(_unlinked(p) for p in protected_archives(path, contract))
    collection = collect_intakes("diagnostic_probe", path, manifest.review_ids)
    require(
        canonical_sha256(collection.model_dump(mode="json")) == manifest.source_sha256,
        "completion_source_changed",
    )
    require(len(members["plan.json"]) <= MAX_SUBMISSION_BYTES, "completion_plan_too_large")
    plans = IntakeBatchPlan.model_validate_json(
        encoded(strict_object(members["plan.json"].decode("utf-8")))
    )
    require(
        canonical_sha256(plans.model_dump(mode="json")) == manifest.plan_sha256,
        "completion_plan_changed",
    )
    require(set(plans.plans) == set(manifest.review_ids), "completion_plan_coverage")
    original = members[intake_path.name]
    intake = IntakeResult.model_validate_json(encoded(strict_object(original.decode("utf-8"))))
    index = int(intake_path.stem.removeprefix("review-")) - 1
    require(intake.source.review_id == manifest.review_ids[index], "completion_review_mismatch")
    source = collection.entries[index].source
    require(source is not None, "completion_incompatible_source")
    assert source is not None
    require(
        intake == compile_intake(source, plans.plans[source.review_id]), "completion_intake_changed"
    )
    pin = expected_pin(intake, manifest_bytes, original)
    receipt: JsonObject = {
        "contract": "assessment-completion-source-receipt-1",
        "origin": "registered_diagnostic_probe",
        "intake_path": str(intake_path),
        "source_path_locator": str(path),
        "archive_contract": contract.model_dump(mode="json"),
        "collection_canonical_sha256": manifest.source_sha256,
        "plan_canonical_sha256": manifest.plan_sha256,
        "recollected_review_ids": list(manifest.review_ids),
        "source_binding": pin.model_dump(mode="json"),
        "assessment_delivery_authenticated": False,
        "live_calls": 0,
    }
    return _Collected(
        CompletionContext(intake, pin, original, manifest_bytes, receipt),
        (*protected, folder),
        members,
    )


def _destination(path: Path, protected: tuple[Path, ...]) -> Path:
    path = _unlinked(path)
    for source in protected:
        source = _unlinked(source)
        require(
            not path.is_relative_to(source) and not source.is_relative_to(path),
            "completion_protected_path",
        )
    return path


def _manifest(files: dict[str, bytes], context: CompletionContext, *, prepared: bool) -> bytes:
    return encoded(
        {
            "contract": "assessment-authored-preparation-1"
            if prepared
            else "assessment-authored-publication-1",
            "origin": "authored_fixture",
            "notice": NOTICE,
            "source_binding": context.pin.model_dump(mode="json"),
            "files_sha256": {name: _sha(data) for name, data in files.items()},
            "envelope_canonical_sha256": None
            if prepared
            else canonical_sha256(strict_object(files["envelope.json"].decode("utf-8"))),
            "implementation_sha256": {
                "domain": _sha(Path(domain.__file__).read_bytes()),
                "adapter": _sha(Path(__file__).read_bytes()),
            },
            "publication_state": "authored_inputs_only" if prepared else "bound_unassessed",
            "model_evidence": False,
            "live_calls": 0,
            "writer_dispatch_authorized": False,
        }
    )


def _verify_output(destination: Path, files: dict[str, bytes], *, manifest: bool) -> None:
    _unlinked(destination)
    expected = files if manifest else {n: d for n, d in files.items() if n != "manifest.json"}
    require(
        destination.is_dir() and {p.name for p in destination.iterdir()} == set(expected),
        "completion_output_conflict",
    )
    for name, data in expected.items():
        target = _unlinked(destination / name)
        require(
            target.is_file() and target.stat().st_size == len(data), "completion_output_conflict"
        )
        require(_read(target, len(data)) == data, "completion_output_conflict")


def _write_new(target: Path, data: bytes) -> None:
    target = _unlinked(target)
    with target.open("xb") as stream:
        stream.write(data)


def _publish(
    destination: Path,
    files: dict[str, bytes],
    protected: tuple[Path, ...],
    recheck: Callable[[], None],
) -> Literal["created", "reused"]:
    require(list(files)[-1] == "manifest.json", "completion_manifest_order")
    require(sum(map(len, files.values())) <= MAX_OUTPUT_BYTES, "completion_output_too_large")
    guard = active_secret_guard()
    for data in files.values():
        guard.ensure_safe(data.decode("utf-8"), destination="authored completion publication")
    destination = _destination(destination, protected)
    recheck()  # Original sources and submission again after all rendering, before any writes.
    _destination(destination, protected)
    if destination.exists():
        _verify_output(destination, files, manifest=True)
        recheck()
        _verify_output(destination, files, manifest=True)
        return "reused"
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        if name == "manifest.json":
            recheck()  # A partial directory is retained without a manifest on failure.
            _destination(destination, protected)
            _verify_output(destination, files, manifest=False)
        _destination(destination, protected)
        _write_new(destination / name, data)
    return "created"


def prepare_inputs(intake_path: Path, destination: Path) -> Literal["created", "reused"]:
    """Export exact authored fixture inputs and a non-submittable authoring template."""
    collected = _collect(intake_path)
    context = collected.context
    work = context.intake.pending_work
    assert work is not None
    require(
        1 <= len(work.context.statements) <= 12 and len(work.batches) <= 12, "publisher_work_bound"
    )
    files = {}
    attempts = []
    for n, batch in enumerate(work.batches, 1):
        data = fixture_input(context, batch.batch_id)
        require(len(data) <= MAX_FILE_BYTES, "completion_input_too_large")
        files[f"input-{n:02d}.json"] = data
        attempts.append(
            {
                "fixture_id": f"authored-{n:02d}",
                "batch_id": batch.batch_id,
                "local_input_bytes_sha256": _sha(data),
                "raw_final": "",
            }
        )
    # Blank author/finals deliberately fail submission validation until explicitly authored.
    files["submission.template.json"] = encoded(
        {
            "contract": "assessment-authored-submission-1",
            "origin": "authored_fixture",
            "authored_by": "",
            "source": context.pin.model_dump(mode="json"),
            "attempts": attempts,
        }
    )
    files["manifest.json"] = _manifest(files, context, prepared=True)

    def recheck() -> None:
        require(_collect(intake_path) == collected, "completion_source_drift")

    return _publish(destination, files, collected.protected, recheck)


def publish_completion(
    intake_path: Path, submission_path: Path, destination: Path
) -> Literal["created", "reused"]:
    """Authenticate from paths and recompute every result; accept no supplied envelope."""
    submission_path = _unlinked(submission_path)
    raw_submission = _read(submission_path, MAX_SUBMISSION_BYTES)
    submission = parse_submission(raw_submission)
    collected = _collect(intake_path)
    context = collected.context
    envelope = derive(context, submission)
    files = {
        "intake.json": context.exact_intake,
        "submission.json": encoded(submission.model_dump(mode="json")),
        "source-receipt.json": encoded(context.adapter_receipt),
        "envelope.json": encoded(envelope),
        "view.md": render_completion(envelope).encode("utf-8"),
    }
    files["manifest.json"] = _manifest(files, context, prepared=False)

    def recheck() -> None:
        require(
            _read(submission_path, MAX_SUBMISSION_BYTES) == raw_submission,
            "completion_submission_drift",
        )
        require(_collect(intake_path) == collected, "completion_source_drift")

    return _publish(destination, files, (*collected.protected, submission_path), recheck)
