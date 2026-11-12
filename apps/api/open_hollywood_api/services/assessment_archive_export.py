"""Read-only export of registered native assessment archives; no provider or DB calls."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Annotated, Literal

from open_hollywood_engine.evaluations import (
    assessment_authority,
    assessment_claim_scope,
    assessment_result,
    assessment_work,
    assessment_work_brief,
)
from open_hollywood_engine.evaluations.assessment_authority import (
    AssessmentAuthority,
    AssessmentAuthorityPreview,
    preview_assessment_authority,
    render_assessment_authority,
)
from open_hollywood_engine.evaluations.assessment_claim_scope import ClaimScopeDeclarations
from open_hollywood_engine.evaluations.assessment_result import (
    AssessmentScope,
    BoundAssessmentResult,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentReceipt,
    AssessmentWork,
    Completion,
    complete_work,
)
from open_hollywood_engine.evaluations.assessment_work_brief import AssessmentWorkBriefs
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.probe_review_evidence import objects, relative_path
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    JsonObject,
    Record,
    object_value,
    require,
    strict_object,
    string_value,
)
from pydantic import Field, TypeAdapter

from open_hollywood_api.persistence.secret_policy import active_secret_guard

Trial = Annotated[str, Field(pattern=r"^BH-[12]-[ABC]-B-(?:SC|CS)$")]
Experiment = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{0,119}$")]
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_MEMBERS = 2048
MAX_EXPORT_BYTES = 32 * 1024 * 1024


class AssessmentArchiveContract(Record):
    experiment: Experiment
    authored_experiment: Experiment
    results_seal_sha256: Digest
    plan_sha256: Digest


SUPPORTED = AssessmentArchiveContract(
    experiment="reviewer-authority-bh-v61-2026-11-07",
    authored_experiment="reviewer-authored-authority-v61-2026-11-07",
    results_seal_sha256="f21a1a62a28c8e193bbf08fa849930f95ff954a0c858ebc934123e90b3515bde",
    plan_sha256="53638172ce2ead7f42810934478ce59dac69630eacea0d73f8d6775691d60d90",
)


class OperatorReceipt(Record):
    request_sha256: Digest
    derived_from_frozen_case: JsonObject
    model_input: Literal[False] = False
    adds_historical_model_evidence: Literal[False] = False


class AssessmentArchiveEntry(Record):
    trial: Trial
    work: AssessmentWork
    scope: AssessmentScope
    result: BoundAssessmentResult
    completion: Completion
    request: JsonObject
    saved_receipt: JsonObject
    dispatches: tuple[JsonObject, ...]
    responses: tuple[JsonObject, ...]
    original_auxiliary: JsonObject
    declarations: ClaimScopeDeclarations
    briefs: AssessmentWorkBriefs
    authority: AssessmentAuthority
    preview: AssessmentAuthorityPreview
    operator_receipt: OperatorReceipt
    actual_assessment_context_verified: Literal[True] = True
    original_critic_visibility_certified: Literal[False] = False
    identity_rebinding_only: Literal[True] = True
    writer_dispatch_authorized: Literal[False] = False


class AssessmentArchiveExport(Record):
    schema_version: Literal["1"] = "1"
    origin: Literal["native_diagnostic_assessment"] = "native_diagnostic_assessment"
    archive_path: str
    contract: AssessmentArchiveContract
    trial_ids: tuple[Trial, ...] = Field(min_length=1, max_length=12)
    entries: tuple[AssessmentArchiveEntry, ...]
    source_members_sha256: dict[str, Digest]
    implementation_sha256: dict[str, Digest]
    live_calls: Literal[0] = 0
    writer_dispatch_authorized: Literal[False] = False


def _encoded(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unlinked(path: Path) -> None:
    for part in (path, *path.parents):
        require(not part.is_symlink() and not part.is_junction(), "linked_assessment_path")


def _path(root: Path, name: str) -> Path:
    relative_path(name)
    candidate = root / name
    require(candidate.resolve().is_relative_to(root), "unsafe_assessment_path")
    _unlinked(candidate)
    return candidate


def _implementation() -> dict[str, str]:
    modules = (
        assessment_work,
        assessment_result,
        assessment_claim_scope,
        assessment_work_brief,
        assessment_authority,
    )
    paths = [Path(__file__)]
    for module in modules:
        assert module.__file__ is not None
        paths.append(Path(module.__file__))
    return {p.name: _sha(p.read_bytes()) for p in paths}


class _Archive:
    """Authenticate a relocated immutable snapshot, never the current checkout."""

    def __init__(self, root: Path, contract: AssessmentArchiveContract) -> None:
        _unlinked(root.absolute())
        self.root = root.resolve(strict=True)
        require(self.root.is_dir(), "assessment_archive_unavailable")
        self.prep = "data/diagnostics/" + contract.experiment
        self.live = self.prep + "-M-live"
        self.authored = "data/diagnostics/" + contract.authored_experiment
        self.cache: dict[str, bytes] = {}
        self.total = 0
        seal_name = self.prep + "-results/results-seal.json"
        raw = self._read(seal_name)
        require(_sha(raw) == contract.results_seal_sha256, "unsupported_assessment_archive")
        seal = strict_object(raw.decode("utf-8"))
        require(seal.get("plan_sha256") == contract.plan_sha256, "assessment_plan_mismatch")
        self.members: dict[str, str] = {seal_name: contract.results_seal_sha256}
        for field in (
            "preparation_members_sha256",
            "source_pins_sha256",
            "capture_members_sha256",
            "results_members_sha256",
            "public_files_sha256",
        ):
            for name, digest in object_value(seal.get(field)).items():
                self._member(name, string_value(digest))
        self._member(self.prep + "/plan.json", contract.plan_sha256)
        self._member(self.prep + "/approval-M.json", string_value(seal.get("approval_sha256")))
        require(len(self.members) <= MAX_MEMBERS, "assessment_archive_too_large")
        for name, digest in self.members.items():
            require(_sha(self._read(name)) == digest, "assessment_archive_hash_mismatch")

    def _member(self, name: str, digest: str) -> None:
        relative_path(name)
        TypeAdapter(Digest).validate_python(digest)
        require(
            name not in self.members or self.members[name] == digest, "conflicting_archive_seal"
        )
        self.members[name] = digest

    def _read(self, name: str) -> bytes:
        if name not in self.cache:
            path = _path(self.root, name)
            require(path.is_file(), "incomplete_assessment_archive")
            with path.open("rb") as stream:
                data = stream.read(MAX_FILE_BYTES + 1)
            self.total += len(data)
            require(
                len(data) <= MAX_FILE_BYTES
                and self.total <= MAX_ARCHIVE_BYTES
                and len(self.cache) < MAX_MEMBERS,
                "assessment_archive_too_large",
            )
            self.cache[name] = data
        return self.cache[name]

    def document(self, name: str) -> JsonObject:
        require(name in self.members, "unsealed_assessment_member")
        return strict_object(self._read(name).decode("utf-8"))

    def recheck(self) -> None:
        # Re-read bounded bytes immediately before returning/publishing; never run archived code.
        for name, expected in self.cache.items():
            with _path(self.root, name).open("rb") as stream:
                require(stream.read(len(expected) + 1) == expected, "assessment_source_changed")


def _sections(text: str) -> dict[str, JsonObject]:
    pattern = re.compile(r"## ([^\n]+)\n\n(`{3,})json\n(.*?)\n\2\n(?:\n|\Z)", re.S)
    cursor = 0
    sections = {}
    for match in pattern.finditer(text):
        require(
            match.start() == cursor and match[1] not in sections, "invalid_assessment_presentation"
        )
        sections[match[1]] = strict_object(match[3])
        cursor = match.end()
    require(cursor == len(text) and bool(sections), "invalid_assessment_presentation")
    return sections


def _visible(request: JsonObject, work: AssessmentWork, case: JsonObject) -> None:
    require(len(work.context.messages) == 2, "assessment_message_mismatch")
    sections = _sections(work.context.messages[1].content)
    expected = ["Sources", "Claims and brief"]
    if request["presentation_order"] == "CS":
        expected.reverse()
    base = object_value(case.get("base"))
    require(list(sections) == expected, "assessment_section_mismatch")
    require(
        sections["Sources"]
        == {k: v for k, v in base.items() if k not in ("whole_claims", "work_briefs")}
        and sections["Claims and brief"] == {k: base[k] for k in ("whole_claims", "work_briefs")},
        "assessment_context_mismatch",
    )
    manifest_id = string_value(request["family"]) + "-manifest"
    docs = work.context.documents
    manifests = [d for d in docs if d.kind == "source" and d.identity == manifest_id]
    require(
        len(manifests) == 1 and strict_object(manifests[0].content_json) == base["manifest"],
        "assessment_manifest_mismatch",
    )
    require(
        [
            d.model_dump(mode="json")
            for d in docs
            if d.kind == "source" and d.identity != manifest_id
        ]
        == base["sources"],
        "assessment_source_mismatch",
    )
    require(
        [d.model_dump(mode="json") for d in docs if d.kind == "registry"] == [base["registry"]]
        and {f.field_id: f.text for f in work.context.report_fields} == base["whole_claims"],
        "assessment_claim_registry_mismatch",
    )
    require(
        [b["unit_id"] for b in objects(base["work_briefs"])] == request["unit_ids"],
        "assessment_brief_selection_mismatch",
    )


def _delivery(
    request: JsonObject,
    saved: JsonObject,
    dispatches: tuple[JsonObject, ...],
    responses: tuple[JsonObject, ...],
) -> None:
    wire, count = object_value(request["wire"]), object_value(request["count_wire"])
    require(
        wire.get("input") == request["messages"]
        and count
        == {k: v for k, v in wire.items() if k in ("model", "input", "text", "reasoning")},
        "assessment_wire_mismatch",
    )
    require(
        saved["trial"] == request["trial"]
        and saved["request_sha256"] == request["request_sha256"]
        and saved["work_key"] == request["work_key"],
        "assessment_receipt_mismatch",
    )
    require(
        saved["status"] == "valid"
        and saved["transport_requests"] == 2
        and saved["generation_dispatches"] == 1,
        "assessment_delivery_incomplete",
    )
    for index, body in enumerate((count, wire)):
        path = "/v1/responses" + ("/input_tokens" if index == 0 else "")
        require(
            dispatches[index]["body_sha256"] == canonical_sha256(body)
            and dispatches[index]["generation"] is (index == 1)
            and dispatches[index]["path"] == responses[index]["path"] == path
            and responses[index]["status"] == 200,
            "assessment_dispatch_mismatch",
        )
    generated = object_value(responses[1]["body"])
    require(
        generated["status"] == "completed" and generated.get("incomplete_details") is None,
        "assessment_delivery_incomplete",
    )
    texts = []
    for output in objects(generated["output"]):
        if output["type"] == "message":
            require(
                output.get("role") == "assistant" and output.get("status") == "completed",
                "assessment_delivery_incomplete",
            )
            for content in objects(output["content"]):
                require(content.get("type") == "output_text", "assessment_delivery_incomplete")
                texts.append(string_value(content["text"]))
    require(len(texts) == 1 and texts[0] == saved["final"], "assessment_final_mismatch")
    usage = object_value(saved["usage"])
    reported = object_value(generated["usage"])
    completion = object_value(saved["completion_receipt"])
    for field in ("input_tokens", "output_tokens", "reasoning_tokens"):
        native = (
            reported.get(field)
            if field != "reasoning_tokens"
            else object_value(reported.get("output_tokens_details", {})).get(field)
        )
        require(usage.get(field) == completion.get(field) == native, "assessment_usage_mismatch")
    require(
        usage.get("cached_input_tokens")
        == object_value(reported.get("input_tokens_details", {})).get("cached_tokens"),
        "assessment_usage_mismatch",
    )
    counted = object_value(responses[0]["body"]).get("input_tokens")
    require(
        counted is None or usage.get("input_tokens") is None or counted == usage["input_tokens"],
        "assessment_count_mismatch",
    )


def _entry(reader: _Archive, trial: str) -> AssessmentArchiveEntry:
    request = object_value(reader.document(reader.prep + "/requests.json")[trial])
    family = trial.split("-")[2]
    require(
        request["trial"] == trial
        and request["condition"] == "B"
        and request["family"] == family
        and request["presentation_order"] == trial.split("-")[4]
        and request["repeat"] == int(trial.split("-")[1]),
        "assessment_trial_mismatch",
    )
    require(
        request["request_sha256"]
        == canonical_sha256({k: v for k, v in request.items() if k != "request_sha256"}),
        "assessment_request_mismatch",
    )
    work_data = object_value(
        reader.document(reader.prep + "/works.json")[string_value(request["work_key"])]
    )
    work = AssessmentWork.model_validate_json(json.dumps(work_data))
    require(
        work.fingerprint == request["work_sha256"]
        and request["messages"] == [m.model_dump(mode="json") for m in work.context.messages],
        "assessment_work_mismatch",
    )
    case = object_value(reader.document(reader.prep + "/cases.json")[family])
    _visible(request, work, case)
    cell = reader.live + "/cells/" + trial
    cell_seal = reader.document(cell + "/seal.json")
    for name, digest in cell_seal.items():
        require(
            reader.members.get(cell + "/" + relative_path(name)) == digest,
            "assessment_cell_mismatch",
        )
    require(reader.document(cell + "/request.json") == request, "assessment_sent_request_mismatch")
    saved = reader.document(cell + "/receipt.json")
    dispatches = tuple(reader.document(cell + f"/dispatch-{i}.json") for i in (1, 2))
    responses = tuple(reader.document(cell + f"/response-{i}.json") for i in (1, 2))
    _delivery(request, saved, dispatches, responses)
    scope = scope_for_batch(
        work, string_value(request["batch_id"]), string_value(request["request_sha256"])
    )
    require(list(scope.active_unit_ids) == request["unit_ids"], "assessment_unit_mismatch")
    receipt = AssessmentReceipt.model_validate_json(json.dumps(saved["completion_receipt"]))
    result = bind_assessment_result(work, scope, receipt, string_value(saved["final"]))
    require(
        [u.model_dump(mode="json") for u in result.units] == object_value(saved["result"])["units"],
        "assessment_native_replay_mismatch",
    )
    completion = complete_work(work, (result.receipt,), {scope.batch_id: scope.request_sha256})
    require(completion.complete_delivery, "assessment_delivery_incomplete")
    prefix = reader.authored + "/packets/" + family
    old_work = AssessmentWork.model_validate_json(
        json.dumps(reader.document(prefix + "-work.json"))
    )
    actual_context, old_context = (
        work.context.model_dump(mode="json"),
        old_work.context.model_dump(mode="json"),
    )
    require(
        {k: v for k, v in actual_context.items() if k != "messages"}
        == {k: v for k, v in old_context.items() if k != "messages"},
        "assessment_authored_context_mismatch",
    )
    original = {
        name: reader.document(prefix + "-" + name + ".json")
        for name in ("declarations", "briefs", "authority")
    }
    require(case.get("source_work_sha256") == old_work.fingerprint, "assessment_origin_mismatch")
    old_declarations = ClaimScopeDeclarations.model_validate_json(
        json.dumps(original["declarations"])
    )
    old_briefs = AssessmentWorkBriefs.model_validate_json(json.dumps(original["briefs"]))
    old_authority = AssessmentAuthority.model_validate_json(json.dumps(original["authority"]))
    old_scope = scope_for_batch(old_work, scope.batch_id, old_authority.request_sha256)
    preview_assessment_authority(old_work, old_scope, old_declarations, old_briefs, old_authority)
    declarations = ClaimScopeDeclarations.model_validate_json(
        json.dumps({**original["declarations"], "work_sha256": work.fingerprint})
    )
    identity = {
        "work_sha256": work.fingerprint,
        "declarations_sha256": canonical_sha256(declarations.model_dump(mode="json")),
    }
    briefs = AssessmentWorkBriefs.model_validate_json(
        json.dumps({**original["briefs"], **identity})
    )
    authority = AssessmentAuthority.model_validate_json(
        json.dumps({**original["authority"], **identity, "request_sha256": scope.request_sha256})
    )
    preview = preview_assessment_authority(work, scope, declarations, briefs, authority)
    # Keep findings/holds; consistency is not an admission gate or a semantic verdict.
    return AssessmentArchiveEntry(
        trial=trial,
        work=work,
        scope=scope,
        result=result,
        completion=completion,
        request=request,
        saved_receipt=saved,
        dispatches=dispatches,
        responses=responses,
        original_auxiliary=dict(original),
        declarations=declarations,
        briefs=briefs,
        authority=authority,
        preview=preview,
        operator_receipt=OperatorReceipt(
            request_sha256=scope.request_sha256,
            derived_from_frozen_case=object_value(case["receipt"]),
        ),
    )


def collect_assessment_export(
    archive: Path, trial_ids: tuple[str, ...], *, _contract: AssessmentArchiveContract = SUPPORTED
) -> AssessmentArchiveExport:
    """Only the registered contract is available to the CLI; injection is for authored tests."""
    require(
        1 <= len(trial_ids) <= 12 and len(set(trial_ids)) == len(trial_ids),
        "invalid_assessment_selection",
    )
    for trial in trial_ids:
        TypeAdapter(Trial).validate_python(trial)
    reader = _Archive(archive, _contract)
    export = AssessmentArchiveExport(
        archive_path=str(reader.root),
        contract=_contract,
        trial_ids=trial_ids,
        entries=tuple(_entry(reader, t) for t in trial_ids),
        source_members_sha256=reader.members,
        implementation_sha256=_implementation(),
    )
    active_secret_guard().ensure_safe(
        export.model_dump(mode="json"), destination="assessment archive export"
    )
    reader.recheck()
    return export


def render_assessment_entry(entry: AssessmentArchiveEntry) -> str:
    return render_assessment_authority(
        entry.work,
        entry.scope,
        entry.declarations,
        entry.briefs,
        entry.authority,
        receipt=entry.result.delivery_receipt,
        raw_final=entry.result.raw_final,
    )


def write_assessment_export(
    destination: Path,
    export: AssessmentArchiveExport,
    *,
    _contract: AssessmentArchiveContract = SUPPORTED,
) -> Literal["created", "reused"]:
    """Recompute from authenticated sources; publish exclusively with manifest last."""
    _unlinked(destination.absolute())
    target, archive = destination.resolve(), Path(export.archive_path).resolve()
    require(
        not target.is_relative_to(archive) and not archive.is_relative_to(target),
        "protected_assessment_archive",
    )
    require(
        collect_assessment_export(archive, export.trial_ids, _contract=_contract) == export,
        "assessment_export_changed",
    )
    files = {}
    lines = [
        "# Native diagnostic assessment exports",
        "",
        "Saved diagnostic assessments; authored context, no production provenance. "
        "Structural completion is not semantic support, edit necessity or craft. "
        "No model calls or writer permission.",
        "",
        "| Capture | Delivered units | Unknown usage attempts |",
        "| --- | ---: | ---: |",
    ]
    for entry in export.entries:
        files[entry.trial + ".json"] = _encoded(entry.model_dump(mode="json"))
        files[entry.trial + ".md"] = render_assessment_entry(entry).encode("utf-8")
        files[entry.trial + "-operator-receipt.json"] = _encoded(
            entry.operator_receipt.model_dump(mode="json")
        )
        lines.append(
            f"| [{entry.trial}]({entry.trial}.md) | {entry.completion.delivered_units} | "
            f"{entry.completion.unknown_usage_attempts} |"
        )
    lines += [
        "",
        "Adjacent JSON retains the original request, full work, delivery and response evidence, "
        "plus separate identity-rebound operator declarations. The operator receipt was absent "
        "from B model input and adds no historical evidence. Gold and scoring are not exported.",
        "",
    ]
    files["index.md"] = "\n".join(lines).encode("utf-8")
    files["manifest.json"] = _encoded(
        {
            "schema_version": "1",
            "origin": export.origin,
            "archive_path": export.archive_path,
            "contract": export.contract.model_dump(mode="json"),
            "trial_ids": export.trial_ids,
            "source_members_sha256": export.source_members_sha256,
            "implementation_sha256": export.implementation_sha256,
            "export_sha256": canonical_sha256(export.model_dump(mode="json")),
            "files_sha256": {name: _sha(body) for name, body in files.items()},
            "live_calls": 0,
            "writer_dispatch_authorized": False,
        }
    )
    require(sum(len(v) for v in files.values()) <= MAX_EXPORT_BYTES, "assessment_export_too_large")
    guard = active_secret_guard()
    for body in files.values():
        guard.ensure_safe(body.decode("utf-8"), destination="assessment archive publication")
    # Revalidate after rendering and secret inspection, just before publication/reuse.
    reader = _Archive(archive, _contract)
    reader.recheck()
    require(export.implementation_sha256 == _implementation(), "assessment_implementation_changed")
    _unlinked(target)
    if target.exists():
        require(
            target.is_dir() and {p.name for p in target.iterdir()} == set(files),
            "assessment_export_conflict",
        )
        for name, body in files.items():
            path = _path(target, name)
            require(
                path.is_file() and path.stat().st_size == len(body) and path.read_bytes() == body,
                "assessment_export_conflict",
            )
        return "reused"
    target.mkdir(parents=True, exist_ok=False)
    for name, body in files.items():
        with _path(target, name).open("xb") as stream:
            stream.write(body)
    return "created"
