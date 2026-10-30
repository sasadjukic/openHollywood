"""Read-only sealed-file export. No historical code execution or model calls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal
from uuid import NAMESPACE_URL, uuid5

from open_hollywood_engine.evaluations import probe_review_evidence as domain
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.probe_review_evidence import (
    FileRole,
    ProbeArchiveContract,
    ProbeAttempt,
    ProbeFile,
    ProbeManifest,
    ProbeProjection,
    ProbeProof,
    ProbeSnapshot,
    Trial,
    project_probe,
    relative_path,
    validate_attempt,
)
from open_hollywood_engine.evaluations.review_evidence import (
    JsonObject,
    Record,
    object_value,
    require,
    string_value,
)
from pydantic import Field, TypeAdapter

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services.review_evidence_export import _quoted

SUPPORTED = ProbeArchiveContract(
    experiment="production-fulfillment-v61-2026-10-16",
    plan_sha256="03da1a013fc86a4a1a142d561d11fc001ab219ee252c55b64c72b4c0ed60bf18",
    preparation_closure_sha256="c9494ba2c56e95c07152bd25e213cffdb4c37cf8b58e122d6457341ffe2799c2",
    live_closure_sha256="74d282a77aac675e4d9c1104c236124caa0df87d937444ed028e37c88c68309b",
)
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_EXPORT_BYTES = 32 * 1024 * 1024


class ProbeExportEntry(Record):
    snapshot: ProbeSnapshot
    projection: ProbeProjection


class ProbeExport(Record):
    schema_version: Literal["1"] = "1"
    origin: Literal["diagnostic_probe"] = "diagnostic_probe"
    archive_path: str
    preparation_path: str
    trial_ids: tuple[Trial, ...] = Field(min_length=1, max_length=12)
    entries: tuple[ProbeExportEntry, ...]
    implementation_sha256: str
    live_calls: Literal[0] = 0


def _path(root: Path, name: str) -> Path:
    relative_path(name)
    candidate = root / name
    require(candidate.resolve().is_relative_to(root), "unsafe_archive_path")
    for part in (candidate, *candidate.parents):
        if part == root:
            break
        require(not part.is_symlink() and not part.is_junction(), "unsafe_archive_path")
    return candidate


class _Archive:
    """Cache exact authenticated bytes; every read is bounded and non-executable."""

    def __init__(self, live: Path, contract: ProbeArchiveContract) -> None:
        self.live = live.resolve(strict=True)
        self.prepared = (self.live.parent / contract.experiment).resolve(strict=True)
        require(
            self.live.is_dir() and self.prepared.is_dir() and self.live != self.prepared,
            "incomplete_probe_archive",
        )
        self.bytes: dict[tuple[str, str], bytes] = {}
        self.total = 0
        self.proof = ProbeProof(
            contract=contract,
            plan=self.file("prepared", "plan.json"),
            preparation_closure=self.file("prepared", "preparation-closure.json"),
            live_closure=self.file("live", "closure.json"),
        )
        self.proof.verify(contract)
        for area, closure in (
            ("prepared", self.proof.preparation_closure),
            ("live", self.proof.live_closure),
        ):
            self.verify_members(area, object_value(closure.document().get("evidence_sha256")))
        self.verify_members(
            "prepared",
            object_value(self.proof.live_closure.document().get("operator_evidence_sha256")),
        )
        plan = self.proof.plan.document()
        self.verify_bytes("prepared", "cases.json", string_value(plan.get("cases_sha256")))
        for name, digest in object_value(plan.get("prepared_sha256")).items():
            self.verify_bytes("prepared", "prepared/" + relative_path(name), string_value(digest))

    def data(self, area: str, name: str) -> bytes:
        key = (area, name)
        if key not in self.bytes:
            root = self.live if area == "live" else self.prepared
            path = _path(root, name)
            require(path.is_file(), "incomplete_probe_archive")
            with path.open("rb") as stream:
                data = stream.read(MAX_FILE_BYTES + 1)
            require(len(data) <= MAX_FILE_BYTES, "probe_archive_too_large")
            self.total += len(data)
            require(
                self.total <= MAX_ARCHIVE_BYTES and len(self.bytes) < 10000,
                "probe_archive_too_large",
            )
            self.bytes[key] = data
        return self.bytes[key]

    def verify_bytes(self, area: str, name: str, expected: str) -> None:
        require(
            hashlib.sha256(self.data(area, name)).hexdigest() == expected,
            "probe_archive_hash_mismatch",
        )

    def verify_members(self, area: str, members: JsonObject) -> None:
        for name, digest in members.items():
            self.verify_bytes(area, name, string_value(digest))

    def file(self, area: Literal["prepared", "live"], name: str) -> ProbeFile:
        data = self.data(area, name)
        return ProbeFile(
            area=area, path=name, sha256=hashlib.sha256(data).hexdigest(), text=data.decode("utf-8")
        )

    def sealed(self, area: Literal["prepared", "live"], name: str) -> ProbeFile:
        file = self.file(area, name)
        self.proof.verify_member(file)
        return file

    def attempt(self, trial: str, number: int) -> ProbeAttempt:
        slot = f"{trial}-attempt-{number}.json"
        paths: dict[FileRole, str] = {
            "request": "requests/" + slot,
            "reservation": "reservations/" + slot,
            "outcome": "outcomes/" + slot,
            "sent": f"probes/{trial}/attempt-{number}-request.json",
            "receipt": f"probes/{trial}/attempt-{number}-result.json",
            "capture": f"probes/{trial}/attempt-{number}-model-output.json",
        }
        return ProbeAttempt(
            number=number, files={role: self.sealed("live", path) for role, path in paths.items()}
        )

    def snapshot(self, trial: str) -> ProbeSnapshot:
        manifest = self.sealed("live", f"probes/{trial}/manifest.json")
        summary = self.sealed("live", f"probes/{trial}/summary.json")
        count = summary.document().get("attempts")
        require(type(count) is int and count in (1, 2), "probe_not_validated")
        assert isinstance(count, int)
        snapshot = ProbeSnapshot(
            proof=self.proof,
            manifest=manifest,
            summary=summary,
            attempts=tuple(self.attempt(trial, n) for n in range(1, count + 1)),
        )
        projection = project_probe(snapshot, self.proof.contract)
        dependencies = self.dependencies(snapshot, projection.manifest)
        return snapshot.model_copy(update={"dependencies": dependencies})

    def dependencies(
        self, snapshot: ProbeSnapshot, manifest: ProbeManifest
    ) -> tuple[ProbeFile, ...]:
        if manifest.stage == "initial":
            prepared = self.sealed("prepared", f"prepared/{manifest.trial}.json")
            require(
                prepared.document() == snapshot.attempts[0].document("request"),
                "probe_prepared_request_mismatch",
            )
            return (prepared,)
        require(manifest.source_trial is not None, "probe_missing_writer")
        assert manifest.source_trial is not None
        writer = manifest.source_trial
        writer_manifest_file = self.sealed("live", f"probes/{writer}/manifest.json")
        writer_summary = self.sealed("live", f"probes/{writer}/summary.json")
        wm = ProbeManifest.model_validate_json(writer_manifest_file.text)
        require(
            (wm.stage, wm.kind, wm.seed, wm.arm)
            == ("writer", manifest.kind, manifest.seed, manifest.arm),
            "probe_writer_identity_mismatch",
        )
        ws = writer_summary.document()
        count = ws.get("attempts")
        require(
            ws.get("status") == "validated" and type(count) is int and count in (1, 2),
            "probe_missing_writer",
        )
        assert isinstance(count, int)
        writer_attempt = self.attempt(writer, count)
        writer_request = validate_attempt(writer_attempt, wm, self.proof)
        require(
            writer_request.invocation.specialist_role == "scene_writer",
            "probe_writer_identity_mismatch",
        )
        receipt = writer_attempt.document("receipt")
        require(receipt.get("status") == "validated", "probe_missing_writer")
        draft = object_value(receipt.get("result"))
        expected_version = str(
            uuid5(
                NAMESPACE_URL,
                f"{manifest.experiment}:{manifest.case_id}:scene_draft:{canonical_sha256(draft)}",
            )
        )
        current = snapshot.attempts[-1].document("request")
        original_inputs = writer_attempt.document("request").get("inputs")
        require(isinstance(original_inputs, list), "malformed_probe")
        assert isinstance(original_inputs, list)
        expected_candidate: JsonObject = {
            "artifact_kind": "scene_draft",
            "artifact_key": "scene_draft_scene_1",
            "artifact_version_id": expected_version,
            "content": draft,
        }
        require(
            current.get("inputs") == [*original_inputs, expected_candidate]
            and manifest.candidate_version_id == expected_version,
            "probe_writer_lineage_mismatch",
        )
        require(wm.source_trial is not None, "probe_missing_parent_review")
        parent = wm.source_trial
        parent_summary = self.sealed("live", f"probes/{parent}/summary.json")
        ps = parent_summary.document()
        n = ps.get("attempts")
        require(
            ps.get("status") == "validated" and type(n) is int and n in (1, 2),
            "probe_missing_parent_review",
        )
        parent_receipt = self.sealed("live", f"probes/{parent}/attempt-{n}-result.json")
        review = object_value(parent_receipt.document().get("result"))
        version = str(
            uuid5(
                NAMESPACE_URL,
                f"{manifest.experiment}:{manifest.case_id}:critique:{canonical_sha256(review)}",
            )
        )
        require(
            {
                "artifact_kind": "critique",
                "artifact_key": "critique_scene_1",
                "artifact_version_id": version,
                "content": review,
            }
            in original_inputs,
            "probe_parent_lineage_mismatch",
        )
        return (
            writer_manifest_file,
            writer_summary,
            *writer_attempt.files.values(),
            parent_summary,
            parent_receipt,
        )


def collect_probe_export(
    archive: Path, trial_ids: tuple[str, ...], *, _contract: ProbeArchiveContract = SUPPORTED
) -> ProbeExport:
    """CLI uses only the registered contract; injection supports authored local tests."""
    require(
        1 <= len(trial_ids) <= 12 and len(set(trial_ids)) == len(trial_ids),
        "invalid_probe_selection",
    )
    for trial in trial_ids:
        TypeAdapter(Trial).validate_python(trial)
    reader = _Archive(archive, _contract)
    entries = []
    for trial in trial_ids:
        snapshot = reader.snapshot(trial)
        entries.append(
            ProbeExportEntry(snapshot=snapshot, projection=project_probe(snapshot, _contract))
        )
    export = ProbeExport(
        archive_path=str(reader.live),
        preparation_path=str(reader.prepared),
        trial_ids=trial_ids,
        entries=tuple(entries),
        implementation_sha256=hashlib.sha256(Path(domain.__file__).read_bytes()).hexdigest(),
    )
    active_secret_guard().ensure_safe(
        export.model_dump(mode="json"), destination="probe review export"
    )
    return export


def render_probe(entry: ProbeExportEntry) -> str:
    p = entry.projection
    lines = [
        "# Diagnostic probe review: " + p.manifest.trial,
        "",
        "Synthetic, unapproved diagnostic context. No persisted production creator "
        "or canonical critique identity. Saved judgments are unchanged; "
        "no writer action is authorized.",
        "",
        f"Successful attempt: {p.successful_attempt}. Validation origin: sealed saved receipt.",
        "",
        "## Raw model response",
        "",
        _quoted(p.raw_model_content),
        "",
        "## Saved normalized review",
        "",
        "Application normalization may change the raw verdict. This is the complete saved result.",
        "",
        _quoted(json.dumps(p.normalized_review, ensure_ascii=False, indent=2)),
        "",
        "## Saved native audit",
        "",
        "Repair advice is application-rendered from shared finding conditions; "
        "raw nulls remain in the model response above.",
        "",
        _quoted(json.dumps(p.saved_native_audit, ensure_ascii=False, indent=2)),
        "",
        "## Application text comparisons",
        "",
        "Exact Unicode comparison of selected spans only. Differing wording does not "
        "establish a defect; identical wording does not establish fulfillment or literary quality.",
        "",
    ]
    for check in p.checks:
        lines += [
            "### " + check.anchor,
            "",
            "Saved critic status: **" + check.saved_check.status + "**.",
            "",
            _quoted(check.saved_check.assessment),
            "",
        ]
        for comparison in check.comparisons:
            lines += [
                "Assigned requirement → selected draft excerpt: **" + comparison.status + "**.",
                "",
            ]
            for label, span in (
                ("Assigned field", comparison.assigned),
                ("Selected excerpt", comparison.selected),
            ):
                lines += [
                    label
                    + f": `{span.version_id}` `{span.field_pointer}` `[{span.start},{span.end})`.",
                    "",
                    "Visibility: " + span.visibility + ".",
                    "",
                    _quoted(span.quote),
                    "",
                ]
                if span.evidence_ref:
                    lines += ["Handle: `" + span.evidence_ref + "`.", ""]
    lines += [
        "## Source visibility",
        "",
        "Full local source packets and actual message views are retained in the JSON snapshot. "
        "Current prose is shown through its catalog. Old full prose is recovered after review; "
        "specific historical repair quotations may have been visible.",
        "",
    ]
    for source in p.sources:
        lines += [
            _quoted(json.dumps(source.model_dump(mode="json"), ensure_ascii=False, indent=2)),
            "",
        ]
    lines += [
        "## Failed predecessors",
        "",
        "Excluded from successful review evidence and comparisons.",
        "",
        _quoted(json.dumps(list(p.failed_predecessors), ensure_ascii=False, indent=2)),
        "",
        "Original/revision semantic alignment: unresolved; no pairing was selected.",
        "",
        "All byte hashes, source fields, raw files and the archive proof "
        "are in the adjacent JSON file.",
        "",
    ]
    return "\n".join(lines)


def write_probe_export(
    destination: Path, export: ProbeExport, *, _contract: ProbeArchiveContract = SUPPORTED
) -> Literal["created", "reused"]:
    body = export.model_dump(mode="json")
    guard = active_secret_guard()
    guard.ensure_safe(body, destination="probe review export")
    require(
        export.trial_ids == tuple(e.projection.manifest.trial for e in export.entries)
        and len(set(export.trial_ids)) == len(export.trial_ids),
        "invalid_probe_selection",
    )
    require(
        not any(
            destination.resolve().is_relative_to(Path(path).resolve())
            for path in (export.archive_path, export.preparation_path)
        ),
        "protected_probe_archive",
    )
    files: dict[str, bytes] = {}
    reader = _Archive(Path(export.archive_path), _contract)
    require(str(reader.prepared) == export.preparation_path, "probe_archive_identity_mismatch")
    require(
        export.implementation_sha256
        == hashlib.sha256(Path(domain.__file__).read_bytes()).hexdigest(),
        "probe_implementation_mismatch",
    )
    index = [
        "# Diagnostic probe review exports",
        "",
        "Twelve or fewer explicitly selected historical probes. Synthetic context; "
        "saved validation is not semantic or story-quality qualification. "
        "No model calls or writer actions.",
        "",
        "| Trial | Attempt | Saved turn / outcome | Excerpts |",
        "| --- | ---: | --- | ---: |",
    ]
    for entry in export.entries:
        require(
            reader.snapshot(entry.projection.manifest.trial) == entry.snapshot,
            "probe_snapshot_mismatch",
        )
        require(
            project_probe(entry.snapshot, _contract) == entry.projection,
            "probe_projection_mismatch",
        )
        p = entry.projection
        trial = p.manifest.trial
        files[trial + ".json"] = (
            json.dumps(entry.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, indent=2)
            + "\n"
        ).encode("utf-8")
        files[trial + ".md"] = render_probe(entry).encode("utf-8")
        states = {c.anchor: c.saved_check.status for c in p.checks}
        index.append(
            f"| [{trial}]({trial}.md) | {p.successful_attempt} | "
            f"{states['turning_point']} / {states['outcome']} | "
            f"{sum(len(c.comparisons) for c in p.checks)} |"
        )
    index += [
        "",
        "Each review has an adjacent JSON snapshot. The manifest binds every file "
        "and exact selected trial order. Raw responses, saved normalized reviews "
        "and application-rendered audit advice remain separate. "
        "Original/revision alignment is unresolved.",
        "",
    ]
    files["index.md"] = "\n".join(index).encode("utf-8")
    require(sum(len(data) for data in files.values()) <= MAX_EXPORT_BYTES, "probe_export_too_large")
    for data in files.values():
        guard.ensure_safe(data.decode("utf-8"), destination="probe review publication")
    manifest = {
        "schema_version": "1",
        "origin": "diagnostic_probe",
        "archive_path": export.archive_path,
        "preparation_path": export.preparation_path,
        "contract": _contract.model_dump(mode="json"),
        "trial_ids": list(export.trial_ids),
        "implementation_sha256": export.implementation_sha256,
        "export_sha256": canonical_sha256(body),
        "files_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
        "live_calls": 0,
    }
    files["manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if destination.exists():
        require(
            destination.is_dir() and not destination.is_symlink() and not destination.is_junction(),
            "probe_export_conflict",
        )
        require({p.name for p in destination.iterdir()} == set(files), "probe_export_conflict")
        require(
            all(
                (destination / name).is_file()
                and not (destination / name).is_symlink()
                and (destination / name).read_bytes() == data
                for name, data in files.items()
            ),
            "probe_export_conflict",
        )
        return "reused"
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        with (destination / name).open("xb") as stream:
            stream.write(data)
    return "created"
