"""Data-only evidence projection for explicitly supported diagnostic probe archives."""

from __future__ import annotations

import json
from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import Field, JsonValue, model_validator

from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Anchor,
    ArtifactView,
    Digest,
    Identifier,
    JsonObject,
    NativeAssignmentCheck,
    Record,
    SavedMessage,
    catalog_v61,
    messages_hash,
    object_value,
    require,
    strict_object,
    string_value,
    text_hash,
)

Trial = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9-]{0,119}$")]
FileRole = Literal["request", "sent", "receipt", "capture", "reservation", "outcome"]


def objects(value: JsonValue) -> tuple[JsonObject, ...]:
    require(isinstance(value, list), "malformed_probe")
    assert isinstance(value, list)
    return tuple(object_value(item) for item in value)


def relative_path(value: str) -> str:
    path = PurePosixPath(value)
    require(
        bool(value)
        and path.as_posix() == value
        and not path.is_absolute()
        and all(part not in {".", ".."} for part in path.parts)
        and not any(c in value for c in "\\:\r\n\x00"),
        "unsafe_archive_path",
    )
    return value


class ProbeArchiveContract(Record):
    experiment: Trial
    plan_sha256: Digest
    preparation_closure_sha256: Digest
    live_closure_sha256: Digest


class ProbeFile(Record):
    area: Literal["prepared", "live"]
    path: str
    sha256: Digest
    text: str

    @model_validator(mode="after")
    def valid_file(self) -> ProbeFile:
        relative_path(self.path)
        require(text_hash(self.text) == self.sha256, "probe_file_hash_mismatch")
        strict_object(self.text)
        return self

    def document(self) -> JsonObject:
        return strict_object(self.text)


class ProbeProof(Record):
    contract: ProbeArchiveContract
    plan: ProbeFile
    preparation_closure: ProbeFile
    live_closure: ProbeFile

    def verify(self, contract: ProbeArchiveContract) -> None:
        require(self.contract == contract, "unsupported_probe_archive")
        for file, area, name, digest in (
            (self.plan, "prepared", "plan.json", contract.plan_sha256),
            (
                self.preparation_closure,
                "prepared",
                "preparation-closure.json",
                contract.preparation_closure_sha256,
            ),
            (self.live_closure, "live", "closure.json", contract.live_closure_sha256),
        ):
            require(
                (file.area, file.path, file.sha256) == (area, name, digest),
                "unsupported_probe_archive",
            )
            require(text_hash(file.text) == digest, "probe_file_hash_mismatch")
        live = self.live_closure.document()
        require(
            live.get("plan_sha256") == self.plan.sha256
            and live.get("preparation_closure_sha256") == self.preparation_closure.sha256,
            "probe_seal_mismatch",
        )
        require(
            self.plan.document().get("experiment") == contract.experiment,
            "unsupported_probe_archive",
        )

    def verify_member(self, file: ProbeFile) -> None:
        require(text_hash(file.text) == file.sha256, "probe_file_hash_mismatch")
        if file.area == "live":
            members = object_value(self.live_closure.document().get("evidence_sha256"))
        else:
            members = object_value(self.preparation_closure.document().get("evidence_sha256"))
        require(members.get(file.path) == file.sha256, "unsealed_probe_file")


class ProbeManifest(Record):
    experiment: Trial
    trial: Trial
    stage: Literal["initial", "post", "writer"]
    arm: Literal["none", "current", "evidence"]
    kind: Trial
    case_id: str
    seed: int
    candidate_version_id: Identifier
    prompt_version: Literal["61"]
    graph_version: Literal["9"]
    critic_semantics: Literal["ordinary_production"]
    source_commit: str
    synthetic_unapproved_context: Literal[True]
    input_artifact_sha256: dict[Identifier, Digest]
    source_trial: Trial | None
    evidence_type: Literal["isolated_comparison_not_full_workflow_or_story_acceptance"]


class ProbeInvocation(Record):
    specialist_role: Literal["scene_critic", "scene_writer"]
    prompt_template_version: Literal["61"]
    input_artifact_version_ids: tuple[Identifier, ...]
    model_profile_id: Identifier


class ProbeRequest(Record):
    budget: JsonObject
    inputs: tuple[ArtifactView, ...]
    invocation: ProbeInvocation
    manifest: ProbeManifest
    messages: tuple[SavedMessage, ...]
    model_identifier: Literal["gemma4:31b-cloud"]
    prompt_sha256: Digest
    response_schema: None
    settings: JsonObject


class ProbeAttempt(Record):
    number: int = Field(ge=1, le=2)
    files: dict[FileRole, ProbeFile]

    def document(self, role: FileRole) -> JsonObject:
        return self.files[role].document()


class ProbeSnapshot(Record):
    proof: ProbeProof
    manifest: ProbeFile
    summary: ProbeFile
    attempts: tuple[ProbeAttempt, ...] = Field(min_length=1, max_length=2)
    dependencies: tuple[ProbeFile, ...] = ()


class ProbeSpan(Record):
    namespace: str
    version_id: Identifier
    field_pointer: Literal["/turning_point", "/outcome", "/prose"]
    source_sha256: Digest
    view_sha256: Digest
    field_sha256: Digest
    evidence_ref: str | None
    catalog_sha256: Digest | None
    start: int = Field(ge=0)
    end: int = Field(ge=1)
    quote: str
    visibility: Literal["shown_in_assignment_contract", "shown_in_catalog"]


class ProbeComparison(Record):
    assigned: ProbeSpan
    selected: ProbeSpan
    status: Literal["exact", "different"]
    rule: Literal["exact Unicode code points; selected spans only; no normalization"] = (
        "exact Unicode code points; selected spans only; no normalization"
    )


class ProbeCheck(Record):
    anchor: Anchor
    raw_check: JsonObject
    saved_check: NativeAssignmentCheck
    advice_origin: Literal["application_rendered_shared_conditions", "none"]
    comparisons: tuple[ProbeComparison, ...]
    semantic_judgment: Literal["unchanged_not_reassessed"] = "unchanged_not_reassessed"
    aggregate_equality: None = None


class ProbeSource(Record):
    version_id: Identifier
    artifact_kind: str
    artifact_key: str
    content_sha256: Digest
    rendered_view_sha256: Digest
    rendered_view: JsonObject
    full_body_available_locally: Literal[True] = True
    old_prose_recovered_after_review: bool
    visible_repair_quotations: tuple[str, ...]


class ProbeProjection(Record):
    origin: Literal["diagnostic_probe"] = "diagnostic_probe"
    manifest: ProbeManifest
    successful_attempt: int
    raw_model_content: str
    normalized_review: JsonObject
    saved_native_audit: JsonObject
    saved_revision_audit: JsonValue
    sources: tuple[ProbeSource, ...]
    checks: tuple[ProbeCheck, ...]
    failed_predecessors: tuple[JsonObject, ...]
    assignment_contract_sha256: Digest
    validation_origin: Literal["sealed_saved_validated_receipt"] = "sealed_saved_validated_receipt"
    production_invocation_id: None = None
    canonical_critique_version_id: None = None
    original_revision_alignment: Literal["unresolved_not_selected"] = "unresolved_not_selected"
    writer_dispatch_authorized: Literal[False] = False


def parse_model_json(content: str) -> JsonObject:
    """Pinned single-fence JSON handling; original content remains in the export."""
    document = content.strip()
    if document.startswith("```"):
        lines = document.splitlines()
        require(
            len(lines) >= 3
            and lines[0].casefold() in {"```", "```json"}
            and lines[-1].strip() == "```",
            "malformed_probe_response",
        )
        document = "\n".join(lines[1:-1]).strip()
    else:
        require("```" not in document, "malformed_probe_response")
    return strict_object(document)


def validate_attempt(
    attempt: ProbeAttempt, manifest: ProbeManifest, proof: ProbeProof
) -> ProbeRequest:
    require(
        set(attempt.files) == {"request", "sent", "receipt", "capture", "reservation", "outcome"},
        "incomplete_probe_attempt",
    )
    slot = f"{manifest.trial}-attempt-{attempt.number}.json"
    paths = {
        "request": "requests/" + slot,
        "reservation": "reservations/" + slot,
        "outcome": "outcomes/" + slot,
        "sent": f"probes/{manifest.trial}/attempt-{attempt.number}-request.json",
        "receipt": f"probes/{manifest.trial}/attempt-{attempt.number}-result.json",
        "capture": f"probes/{manifest.trial}/attempt-{attempt.number}-model-output.json",
    }
    for role, file in attempt.files.items():
        require(file.area == "live" and file.path == paths[role], "probe_attempt_identity_mismatch")
        proof.verify_member(file)
    request = ProbeRequest.model_validate_json(attempt.files["request"].text)
    require(request.manifest == manifest, "probe_manifest_mismatch")
    require(
        tuple(m.role for m in request.messages) == ("system", "user"),
        "probe_message_roles_mismatch",
    )
    require(messages_hash(request.messages) == request.prompt_sha256, "probe_prompt_hash_mismatch")
    roles: tuple[FileRole, ...] = ("sent", "receipt", "capture", "reservation", "outcome")
    sent, receipt, capture, reservation, outcome = (attempt.document(k) for k in roles)
    require(
        sent.get("attempt")
        == receipt.get("attempt")
        == reservation.get("attempt")
        == attempt.number,
        "probe_attempt_identity_mismatch",
    )
    require(
        reservation.get("trial") == manifest.trial
        and reservation.get("plan_sha256") == proof.plan.sha256
        and reservation.get("request_sha256") == attempt.files["request"].sha256,
        "probe_reservation_mismatch",
    )
    require(
        all(r.get("prompt_sha256") == request.prompt_sha256 for r in (sent, receipt, reservation)),
        "probe_prompt_hash_mismatch",
    )
    require(
        sent.get("messages") == [m.model_dump(mode="json") for m in request.messages]
        and sent.get("response_schema") == request.response_schema,
        "probe_sent_request_mismatch",
    )
    response = string_value(capture.get("content"))
    require(
        text_hash(response)
        == capture.get("response_sha256")
        == receipt.get("response_sha256")
        == outcome.get("response_sha256"),
        "probe_response_hash_mismatch",
    )
    require(
        receipt.get("response_length") == len(response) and outcome.get("status") == "returned",
        "probe_incomplete_response",
    )
    require(
        capture.get("provider") == "ollama"
        and capture.get("deployment") == "cloud"
        and capture.get("model_identifier") == request.model_identifier,
        "probe_model_mismatch",
    )
    require(
        capture.get("finish_reason") == receipt.get("finish_reason") == "stop",
        "probe_incomplete_response",
    )
    usage = object_value(capture.get("usage"))
    require(
        all(
            usage.get(k) == receipt.get(k) == outcome.get(k)
            for k in ("input_tokens", "output_tokens")
        ),
        "probe_usage_mismatch",
    )
    return request


def project_probe(snapshot: ProbeSnapshot, contract: ProbeArchiveContract) -> ProbeProjection:
    snapshot.proof.verify(contract)
    for file in (snapshot.manifest, snapshot.summary, *snapshot.dependencies):
        snapshot.proof.verify_member(file)
    manifest = ProbeManifest.model_validate_json(snapshot.manifest.text)
    require(
        manifest.experiment == contract.experiment and manifest.stage in {"initial", "post"},
        "unsupported_probe_review",
    )
    require(
        snapshot.manifest.area == snapshot.summary.area == "live"
        and snapshot.manifest.path == f"probes/{manifest.trial}/manifest.json"
        and snapshot.summary.path == f"probes/{manifest.trial}/summary.json",
        "probe_summary_mismatch",
    )
    summary = snapshot.summary.document()
    require(
        summary.get("status") == "validated" and summary.get("attempts") == len(snapshot.attempts),
        "probe_not_validated",
    )
    require(
        tuple(a.number for a in snapshot.attempts) == tuple(range(1, len(snapshot.attempts) + 1)),
        "probe_attempt_identity_mismatch",
    )
    failed: list[JsonObject] = []
    for attempt in snapshot.attempts:
        request = validate_attempt(attempt, manifest, snapshot.proof)
        require(request.invocation.specialist_role == "scene_critic", "unsupported_probe_review")
        receipt = attempt.document("receipt")
        if attempt.number < len(snapshot.attempts):
            require(
                receipt.get("status") == "failed"
                and bool(receipt.get("validation_issues"))
                and "result" not in receipt,
                "probe_invalid_retry_chain",
            )
            failed.append(
                {
                    "attempt": attempt.number,
                    "receipt_path": attempt.files["receipt"].path,
                    "receipt_sha256": attempt.files["receipt"].sha256,
                    "response_sha256": receipt["response_sha256"],
                    "validation_issues": receipt["validation_issues"],
                    "source_for_comparisons": False,
                }
            )
    require(receipt.get("status") == "validated", "probe_not_validated")
    content = string_value(snapshot.attempts[-1].document("capture").get("content"))
    raw = parse_model_json(content)
    audit = object_value(receipt.get("scene_boundary_audit"))
    review = object_value(receipt.get("result"))
    require(
        audit.get("schema_version") == "7"
        and audit.get("repair_advice_origin") == "shared_finding_conditions",
        "unsupported_probe_audit",
    )
    payload = strict_object(request.messages[-1].content)
    views = tuple(
        ArtifactView.model_validate_json(json.dumps(v))
        for v in objects(payload.get("input_artifacts"))
    )
    by_view = {v.artifact_version_id: v for v in views}
    sources = {s.artifact_version_id: s for s in request.inputs}
    require(
        len(by_view) == len(views) and len(sources) == len(request.inputs), "probe_duplicate_input"
    )
    require(
        set(sources) == set(by_view) == set(manifest.input_artifact_sha256)
        and tuple(sources) == request.invocation.input_artifact_version_ids,
        "probe_missing_input",
    )
    for version, source in sources.items():
        require(
            canonical_sha256(source.content) == manifest.input_artifact_sha256[version],
            "probe_source_hash_mismatch",
        )
        require(
            (source.artifact_kind, source.artifact_key)
            == (by_view[version].artifact_kind, by_view[version].artifact_key),
            "probe_view_identity_mismatch",
        )
    candidate = sources[manifest.candidate_version_id]
    plan = sources[string_value(audit.get("current_plan_version_id"))]
    require(
        candidate.artifact_kind == "scene_draft"
        and plan.artifact_kind == "scene_plan"
        and plan.artifact_key == "scene_plan",
        "probe_source_kind_mismatch",
    )
    require(
        audit.get("candidate_version_id")
        == review.get("target_artifact_version_id")
        == candidate.artifact_version_id
        and review.get("target_artifact_kind") == candidate.artifact_kind
        and review.get("target_artifact_key") == candidate.artifact_key,
        "probe_target_mismatch",
    )
    assignment = object_value(payload.get("scene_assignment_contract"))
    require(
        plan.content.get("id") == candidate.content.get("scene_id") == assignment.get("scene_id")
        and plan.content == by_view[plan.artifact_version_id].content,
        "probe_plan_mismatch",
    )
    prose = string_value(candidate.content.get("prose"))
    catalog = catalog_v61(prose, candidate.artifact_version_id)
    serialized = [r.model_dump(mode="json") for r in catalog]
    require(
        by_view[candidate.artifact_version_id].content.get("evidence_catalog") == serialized,
        "probe_catalog_mismatch",
    )
    spans: dict[str, tuple[int, int, str]] = {}
    cursor = 0
    for row in catalog:
        start = prose.find(row.exact_excerpt, cursor)
        require(
            start >= cursor and not prose[cursor:start].strip(), "probe_catalog_coverage_mismatch"
        )
        cursor = start + len(row.exact_excerpt)
        spans[row.evidence_ref] = (start, cursor, row.exact_excerpt)
    require(not prose[cursor:].strip(), "probe_catalog_coverage_mismatch")
    raw_checks, saved_checks = (
        object_value(raw.get("assignment_checks")),
        object_value(audit.get("assignment_checks")),
    )
    require(
        set(raw_checks) == set(saved_checks) == {"turning_point", "outcome"},
        "probe_native_coverage_mismatch",
    )
    namespace = manifest.experiment + ":" + manifest.case_id
    checks = []
    for anchor in ("turning_point", "outcome"):
        typed_anchor: Anchor = "turning_point" if anchor == "turning_point" else "outcome"
        raw_check = object_value(raw_checks[anchor])
        check = NativeAssignmentCheck.model_validate_json(json.dumps(saved_checks[anchor]))
        require(
            all(
                raw_check.get(k) == object_value(saved_checks[anchor]).get(k)
                for k in ("status", "assessment", "draft_evidence_refs")
            ),
            "probe_native_judgment_mismatch",
        )
        require(raw_check.get("recommended_resolution") is None, "unsupported_probe_advice")
        if check.status == "unmet":
            conditions = [
                c
                for c in objects(raw.get("assignment_repair_conditions"))
                if c.get("repair_ref") == "assignment:" + anchor
            ]
            require(len(conditions) == 1, "probe_advice_mismatch")
            rendered = " ".join(
                string_value(c.get("condition")) for c in objects(conditions[0].get("conditions"))
            )
            require(rendered == check.recommended_resolution, "probe_advice_mismatch")
        assigned = string_value(plan.content.get(anchor))
        require(assignment.get(anchor) == assigned, "probe_assignment_mismatch")
        left = ProbeSpan(
            namespace=namespace,
            version_id=plan.artifact_version_id,
            field_pointer="/turning_point" if anchor == "turning_point" else "/outcome",
            source_sha256=manifest.input_artifact_sha256[plan.artifact_version_id],
            view_sha256=canonical_sha256(
                by_view[plan.artifact_version_id].model_dump(mode="json", exclude_unset=True)
            ),
            field_sha256=text_hash(assigned),
            evidence_ref=None,
            catalog_sha256=None,
            start=0,
            end=len(assigned),
            quote=assigned,
            visibility="shown_in_assignment_contract",
        )
        comparisons = []
        for ref in check.draft_evidence_refs:
            require(ref in spans, "probe_unbound_handle")
            start, end, quote = spans[ref]
            right = ProbeSpan(
                namespace=namespace,
                version_id=candidate.artifact_version_id,
                field_pointer="/prose",
                source_sha256=manifest.input_artifact_sha256[candidate.artifact_version_id],
                view_sha256=canonical_sha256(
                    by_view[candidate.artifact_version_id].model_dump(
                        mode="json", exclude_unset=True
                    )
                ),
                field_sha256=text_hash(prose),
                evidence_ref=ref,
                catalog_sha256=canonical_sha256(serialized),
                start=start,
                end=end,
                quote=quote,
                visibility="shown_in_catalog",
            )
            comparisons.append(
                ProbeComparison(
                    assigned=left,
                    selected=right,
                    status="exact" if assigned == quote else "different",
                )
            )
        checks.append(
            ProbeCheck(
                anchor=typed_anchor,
                raw_check=raw_check,
                saved_check=check,
                advice_origin="application_rendered_shared_conditions"
                if check.status == "unmet"
                else "none",
                comparisons=tuple(comparisons),
            )
        )
    source_rows = []
    for version, source in sources.items():
        view = by_view[version]
        old = source.artifact_kind == "scene_draft" and version != candidate.artifact_version_id
        if old:
            require(
                source.content.get("scene_id") == candidate.content.get("scene_id")
                and "prose" not in view.content
                and "evidence_catalog" not in view.content,
                "probe_old_source_mismatch",
            )
        quotes: list[str] = []
        for repair in objects(payload.get("repair_acceptance_tests", [])):
            if repair.get("source_draft_version_id") == version:
                evidence = repair.get("original_evidence")
                require(isinstance(evidence, list), "malformed_probe")
                assert isinstance(evidence, list)
                for item in evidence:
                    quote = string_value(item)
                    require(
                        quote in string_value(source.content.get("prose")),
                        "probe_repair_quote_mismatch",
                    )
                    quotes.append(quote)
        source_rows.append(
            ProbeSource(
                version_id=version,
                artifact_kind=source.artifact_kind,
                artifact_key=source.artifact_key,
                content_sha256=manifest.input_artifact_sha256[version],
                rendered_view_sha256=canonical_sha256(
                    view.model_dump(mode="json", exclude_unset=True)
                ),
                rendered_view=view.model_dump(mode="json", exclude_unset=True),
                old_prose_recovered_after_review=old,
                visible_repair_quotations=tuple(quotes),
            )
        )
    return ProbeProjection(
        manifest=manifest,
        successful_attempt=len(snapshot.attempts),
        raw_model_content=content,
        normalized_review=review,
        saved_native_audit=audit,
        saved_revision_audit=receipt.get("revision_acceptance_audit"),
        sources=tuple(source_rows),
        checks=tuple(checks),
        failed_predecessors=tuple(failed),
        assignment_contract_sha256=canonical_sha256(assignment),
    )
