"""Read-only completion publication of the registered observed deliveries over authored sources.

No caller receipts, trust overrides, credentials, transport or partial-work selection.
Authentication replays the existing audit; native completion and accounting admission
are separate. The local journal is not a provider signature or semantic qualification.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from open_hollywood_engine.evaluations import assessment_authority as authority_domain
from open_hollywood_engine.evaluations.assessment_authority import (
    AssessmentAuthority,
    render_assessment_authority,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import BoundAssessmentResult
from open_hollywood_engine.evaluations.assessment_work import complete_work
from open_hollywood_engine.evaluations.review_evidence import JsonObject, require, strict_object
from open_hollywood_engine.models.assessment_openai_authored import RequestManifest, derive_terminal

from open_hollywood_api.services import assessment_authored_source as sources
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_observed_completion as observed_storage
from open_hollywood_api.services import assessment_openai_authored_smoke as smoke

NOTICE = (
    "READ-ONLY OBSERVED COMPLETION. Authored diagnostic source; observed OpenAI "
    "assessment delivery. Application-owned local journal, not provider-signed attestation. "
    "Binding and accounting clearance do not establish semantic support, evidence adequacy, "
    "editorial effect, edit necessity or craft. No writer permission. Actual billed cost unknown."
)
ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class _Registration:
    name: str
    plan: Path
    audit: Path
    plan_sha256: str
    audit_manifest_sha256: str


REGISTERED = (
    _Registration(
        "authored-smoke-2026-11-15",
        ROOT / "data/diagnostics/assessment-authored-three-work-smoke-2026-11-15/plan.json",
        ROOT / "data/diagnostics/assessment-authored-three-work-smoke-results-2026-11-15/audit",
        "f474bfc29bee448116993fc6845faccbee3cf60b48e1b1cbf8afc5ac3e93b779",
        "3cd78a547a82832decf5625ec2256f53c09620fd5fdb98fc367e249966c696e9",
    ),
)


def _object(data: bytes) -> JsonObject:
    return strict_object(data.decode("utf-8"))


def _implementation() -> JsonObject:
    return {
        "authenticated_smoke": smoke.implementation(),
        "observed_publisher": storage._sha(Path(__file__).read_bytes()),
        "shared_observed_storage": storage._sha(Path(observed_storage.__file__).read_bytes()),
        "evidence_renderer": storage._sha(Path(authority_domain.__file__).read_bytes()),
        "operator_cli": storage._sha(
            (ROOT / "scripts/assessment_authored_observed_completion.py").read_bytes()
        ),
    }


def _admit_audit(value: JsonObject, plan: smoke.Plan, plan_sha256: str) -> None:
    require(
        value.get("contract") == "assessment-openai-authored-smoke-audit-1"
        and value.get("delivery_origin") == "observed_openai_transport"
        and value.get("source_origin") == "authored_diagnostic"
        and value.get("plan_sha256") == plan_sha256
        and value.get("transport_observation") is True
        and value.get("model_observation") is True,
        "observed_audit_origin_or_binding",
    )
    require(
        value.get("completion_eligible") is True
        and value.get("journal_closed") is True
        and value.get("stop_reason") == "complete"
        and value.get("count_intents") == value.get("generation_intents") == 3
        and value.get("unknown_elapsed_endpoints") == 0,
        "observed_incomplete_run",
    )
    require(
        value.get("generations_with_unknown_usage") == 0
        and value.get("generations_with_accounting_hold") == 0,
        "observed_accounting_hold",
    )
    require(
        value.get("actual_billed_cost") is None
        and value.get("semantic_support") == value.get("evidence_adequacy") == "unassessed"
        and value.get("writer_dispatch_authorized") is False,
        "observed_credit_forbidden",
    )
    rows, slots = value.get("works"), value.get("slots")
    require(isinstance(rows, list) and isinstance(slots, list), "observed_audit_shape")
    assert isinstance(rows, list) and isinstance(slots, list)
    require(
        [r.get("work") for r in rows if isinstance(r, dict)] == list(smoke.NAMES)
        and len(rows) == 3,
        "observed_work_coverage",
    )
    require(
        [(s.get("work"), s.get("stage"), s.get("state")) for s in slots if isinstance(s, dict)]
        == [
            (family, stage, "observed_terminal")
            for stage in ("input_count", "generation")
            for family in smoke.NAMES
        ]
        and len(slots) == 6,
        "observed_slot_coverage",
    )


def _work_files(
    collected: sources.Collected,
    manifest: RequestManifest,
    row: JsonObject,
    audit: JsonObject,
    binding: JsonObject,
) -> dict[str, bytes]:
    source = collected.source
    family, work = source.source.family, source.work
    require(
        row.get("work") == family and row.get("source") == source.model_dump(mode="json"),
        "observed_source_changed",
    )
    slots = audit["slots"]
    require(isinstance(slots, list), "observed_slots_shape")
    assert isinstance(slots, list)
    selected = [s for s in slots if isinstance(s, dict) and s.get("work") == family]
    require(
        [(s.get("stage"), s.get("state")) for s in selected]
        == [(stage, "observed_terminal") for stage in ("input_count", "generation")],
        "observed_work_slot_coverage",
    )
    outcomes = [smoke.Outcome.model_validate_json(encoded(s["outcome"])) for s in selected]
    terminal = derive_terminal(
        source,
        manifest,
        tuple(o.exchange for o in outcomes),
        sum(o.elapsed_seconds for o in outcomes),
    )
    # Shared reducer labels describe injected fixtures. Observation is authenticated
    # by the registered smoke audit, not by relabeling a caller-supplied terminal.
    terminal_value = terminal.model_dump(
        mode="json", exclude={"contract", "source_origin", "delivery_origin", "model_evidence"}
    )
    require(row.get("terminal") == terminal_value, "observed_terminal_changed")
    require(
        not terminal.accounting_hold
        and not terminal.budget_violations
        and all(v is not None for v in terminal.usage.model_dump().values())
        and terminal.unknown_elapsed_endpoints == 0,
        "observed_work_accounting_hold",
    )
    require(
        terminal.state == "bound_unassessed"
        and terminal.native_receipt is not None
        and terminal.bound_result is not None,
        "observed_delivery_incomplete",
    )
    assert terminal.native_receipt is not None and terminal.bound_result is not None
    completion = complete_work(
        work,
        (terminal.native_receipt,),
        {manifest.payload.presentation.batch_id: manifest.payload_canonical_sha256},
    )
    require(
        completion.complete_delivery
        and completion.binding == "complete"
        and row.get("completion") == completion.model_dump(mode="json")
        and row.get("completion_eligible") is True,
        "observed_whole_work_incomplete",
    )
    bound = BoundAssessmentResult.model_validate_json(encoded(terminal.bound_result))
    # Local source construction identity is immutable. Only this separately retained
    # rendering authority is rebound to the actual observed request.
    authority = AssessmentAuthority.model_validate_json(
        encoded(
            {
                **source.authority.model_dump(mode="json"),
                "request_sha256": manifest.payload_canonical_sha256,
            }
        )
    )
    evidence = render_assessment_authority(
        work,
        bound.scope,
        source.declarations,
        source.briefs,
        authority,
        receipt=terminal.native_receipt,
        raw_final=bound.raw_final,
    )
    files = {f"{family}.input.{name}": raw for name, raw in collected.safe_members.items()}
    files.update(
        {
            f"{family}.source.json": encoded(source.model_dump(mode="json")),
            f"{family}.source-receipt.json": collected.source_receipt,
            f"{family}.request.json": encoded(manifest.model_dump(mode="json")),
            f"{family}.presentation.json": encoded(
                manifest.payload.presentation.model_dump(mode="json")
            ),
            f"{family}.request-bound-authority.json": encoded(authority.model_dump(mode="json")),
        }
    )
    envelope = {
        "contract": "assessment-authored-observed-completion-1",
        "source_origin": "authored_diagnostic",
        "delivery_origin": "observed_openai_transport",
        "state": "bound_unassessed",
        "notice": NOTICE,
        "work": family,
        "source_binding": source.source.model_dump(mode="json"),
        "observation_binding": binding,
        "input_members_sha256": {n: storage._sha(v) for n, v in files.items()},
        "source": source.model_dump(mode="json"),
        "request_bound_authority": authority.model_dump(mode="json"),
        "terminal": terminal_value,
        "endpoint_slots": selected,
        "completion": completion.model_dump(mode="json"),
        "journal_closed": audit["journal_closed"],
        "stop_reason": audit["stop_reason"],
        "accounting_clear": True,
        "actual_billed_cost": None,
        "semantic_support": "unassessed",
        "evidence_adequacy": "unassessed",
        "editorial_effect": "unassessed",
        "edit_necessity": "unassessed",
        "craft": "unassessed",
        "live_calls": 0,
        "writer_dispatch_authorized": False,
    }
    files[f"{family}.completion.json"] = encoded(envelope)
    files[f"{family}.view.md"] = (
        f"{NOTICE}\n\n"
        f"Full source, original scope, unselected fields, terminal accounting and provenance: "
        f"[{family}.completion.json]({family}.completion.json). "
        "The evidence view below uses separately request-bound authority; it is a projection, "
        "not the complete delivery envelope.\n\n" + evidence
    ).encode()
    return files


def publish_observed(source: str, destination: Path) -> Literal["created", "reused"]:
    """Publish all three complete registered works, or nothing; never dispatch inference."""
    matches = [r for r in REGISTERED if r.name == source]
    require(len(matches) == 1, "observed_unregistered_source")
    registration = matches[0]
    require(
        storage._sha(storage._read(registration.plan)) == registration.plan_sha256,
        "observed_registered_plan_changed",
    )
    manifest_bytes = storage._read(registration.audit / "manifest.json")
    require(
        storage._sha(manifest_bytes) == registration.audit_manifest_sha256,
        "observed_registered_audit_changed",
    )
    audit_manifest = _object(manifest_bytes)
    names = (
        "audit.json",
        "view.md",
        "plan.json",
        "request-set.json",
        "scoring.json",
        "metadata.json",
        "journal.json",
        *(
            f"{f}-{suffix}"
            for f in smoke.NAMES
            for suffix in ("source.json", "source-receipt.json", "evidence.md")
        ),
    )
    require(
        {p.name for p in storage._unlinked(registration.audit).iterdir()}
        == {*names, "manifest.json"},
        "observed_audit_members_changed",
    )
    audit_files = {n: storage._read(registration.audit / n) for n in names}
    require(
        audit_manifest.get("contract") == "assessment-openai-authored-smoke-export-1"
        and audit_manifest.get("files_sha256")
        == {n: storage._sha(v) for n, v in audit_files.items()},
        "observed_audit_members_changed",
    )
    audit_files["manifest.json"] = manifest_bytes
    plan = smoke.load_plan(registration.plan)
    prepared = smoke._prepared(plan)
    protected = (
        registration.plan,
        registration.audit,
        Path(plan.live_journal),
        *(p for item in prepared.collected for p in item.protected),
        Path(plan.preparation),
        Path(plan.scoring_path),
        Path(plan.metadata_path),
    )
    storage._destination(destination, protected)
    before, implementation = observed_storage._snapshot(protected), _implementation()
    # Existing audit must already exist and match its registered bytes. The supported
    # audit recompiles sources, authenticates the closed observed journal and derives
    # every terminal. Exact reuse performs no write to the reference export.
    require(
        smoke.audit(registration.plan, Path(plan.live_journal), registration.audit) == "reused",
        "observed_audit_must_reuse",
    )

    def recheck() -> None:
        require(
            observed_storage._snapshot(protected) == before and _implementation() == implementation,
            "observed_source_or_implementation_drift",
        )

    recheck()
    value = _object(audit_files["audit.json"])
    _admit_audit(value, plan, registration.plan_sha256)
    binding: JsonObject = {
        "registration": registration.name,
        "plan_path": str(registration.plan),
        "plan_bytes_sha256": registration.plan_sha256,
        "audit_path": str(registration.audit),
        "audit_manifest_bytes_sha256": registration.audit_manifest_sha256,
        "audit_bytes_sha256": storage._sha(audit_files["audit.json"]),
        "journal_path": plan.live_journal,
        "journal_sha256": audit_manifest["journal_sha256"],
        "provenance_limit": value["provenance_limit"],
        "raw_http_response_bytes_retained": False,
    }
    files = {
        "source-audit.json": audit_files["audit.json"],
        "source-audit-manifest.json": audit_files["manifest.json"],
    }
    rows = value["works"]
    assert isinstance(rows, list)
    files["request-set.json"] = prepared.files["request-set.json"]
    for collected, manifest, row in zip(
        prepared.collected, prepared.request_set.payload.requests, rows, strict=True
    ):
        assert isinstance(row, dict)
        files.update(_work_files(collected, manifest, row, value, binding))
    files["manifest.json"] = encoded(
        {
            "contract": "assessment-authored-observed-publication-1",
            "delivery_origin": "observed_openai_transport",
            "source_origin": "authored_diagnostic",
            "notice": NOTICE,
            "state": "bound_unassessed",
            "works": list(smoke.NAMES),
            "editorial_effect": "unassessed",
            "edit_necessity": "unassessed",
            "craft": "unassessed",
            "observation_binding": binding,
            "implementation_sha256": implementation,
            "source_members_sha256": before,
            "files_sha256": {n: storage._sha(v) for n, v in files.items()},
            "semantic_support": "unassessed",
            "evidence_adequacy": "unassessed",
            "accounting_clear": True,
            "actual_billed_cost": None,
            "live_calls": 0,
            "writer_dispatch_authorized": False,
        }
    )
    return storage._publish(destination, files, protected, recheck)
