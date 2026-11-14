"""Read-only completion publication of the registered, observed compact smoke.

No caller receipts, trust overrides, credentials, transport or partial-work selection.
Authentication replays the existing audit; native completion and accounting admission
are separate. The local journal is not a provider signature or semantic qualification.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from open_hollywood_engine.evaluations import assessment_work_brief as brief_domain
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import BoundAssessmentResult
from open_hollywood_engine.evaluations.assessment_work import complete_work
from open_hollywood_engine.evaluations.assessment_work_brief import render_work_briefs
from open_hollywood_engine.evaluations.review_evidence import JsonObject, require, strict_object
from open_hollywood_engine.models.assessment_openai_compact_manifest import derive_terminal

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_openai_compact_delivery as preparation
from open_hollywood_api.services import assessment_openai_compact_smoke as smoke

NOTICE = (
    "READ-ONLY OBSERVED COMPLETION. Registered diagnostic-probe source; observed OpenAI "
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
        "compact-smoke-2026-11-14",
        ROOT / "data/diagnostics/assessment-openai-compact-smoke-2026-11-14/plan.json",
        ROOT / "data/diagnostics/assessment-openai-compact-smoke-results-2026-11-14/audit",
        "fa814d8c09b897ad8c6c9b902ef99a9eec7b24a49a8923ec4f2643253d8181f5",
        "2406c7a70db5eb133c45c550945666546654c9da09efb9ccb6cfbdac93d1b8fb",
    ),
)


def _object(data: bytes) -> JsonObject:
    return strict_object(data.decode("utf-8"))


def _implementation() -> JsonObject:
    return {
        "authenticated_smoke": smoke.implementation(),
        "observed_publisher": storage._sha(Path(__file__).read_bytes()),
        "evidence_renderer": storage._sha(Path(brief_domain.__file__).read_bytes()),
        "operator_cli": storage._sha(
            (ROOT / "scripts/assessment_observed_completion.py").read_bytes()
        ),
    }


def _snapshot(roots: tuple[Path, ...]) -> dict[str, str]:
    """Bounded byte/membership guard after supported source authentication.

    Walk without following links, including empty directories in membership. Rechecks
    avoid repeating expensive source compilation while refusing every source change.
    Content secret checks remain in the existing authenticated readers and publisher.
    """
    pending = list(roots)
    result: dict[str, str] = {}
    total = 0
    while pending:
        path = storage._unlinked(pending.pop())
        key = str(path)
        if key in result:
            continue
        require(len(result) < 4096, "observed_source_member_bound")
        if path.is_dir():
            result[key] = "directory"
            pending.extend(path.iterdir())
            continue
        require(path.is_file(), "observed_source_missing")
        size = path.stat().st_size
        require(size <= storage.MAX_FILE_BYTES, "observed_source_size")
        total += size
        require(total <= 512 * 1024 * 1024, "observed_source_total_size")
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        require(path.stat().st_size == size, "observed_source_size_drift")
        result[key] = digest
    return result


def _admit_audit(value: JsonObject, plan: smoke.Plan, plan_sha256: str) -> None:
    require(
        value.get("contract") == "assessment-openai-compact-smoke-audit-2"
        and value.get("origin") == "observed_openai_transport"
        and value.get("plan_sha256") == plan_sha256
        and value.get("transport_observation") is True
        and value.get("model_observation") is True,
        "observed_audit_origin_or_binding",
    )
    require(
        value.get("journal_closed") is True
        and value.get("stop_reason") == "complete"
        and value.get("count_intents") == value.get("generation_intents") == 4
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
        [r.get("work") for r in rows if isinstance(r, dict)] == [w.name for w in plan.works]
        and len(rows) == 4,
        "observed_work_coverage",
    )
    require(
        [(s.get("work"), s.get("stage"), s.get("state")) for s in slots if isinstance(s, dict)]
        == [
            (w.name, stage, "observed_terminal")
            for stage in ("input_count", "generation")
            for w in plan.works
        ]
        and len(slots) == 8,
        "observed_slot_coverage",
    )


def _work_files(
    ref: smoke.Work,
    prepared: preparation._Prepared,
    row: JsonObject,
    audit: JsonObject,
    binding: JsonObject,
) -> dict[str, bytes]:
    context = prepared.collected.context
    intake, requests = context.intake, prepared.request_set
    work = intake.pending_work
    require(work is not None and len(requests.payload.requests) == 1, "observed_original_work")
    assert work is not None
    require(intake.declarations is not None and intake.briefs is not None, "observed_scope_missing")
    assert intake.declarations is not None and intake.briefs is not None
    manifest = requests.payload.requests[0]
    require(row.get("intake") == intake.model_dump(mode="json"), "observed_intake_changed")
    slots = audit["slots"]
    assert isinstance(slots, list)
    selected = [s for s in slots if isinstance(s, dict) and s.get("work") == ref.name]
    outcomes = [smoke.Outcome.model_validate_json(encoded(s["outcome"])) for s in selected]
    terminal = derive_terminal(
        context,
        manifest,
        tuple(o.exchange for o in outcomes),
        sum(o.elapsed_seconds for o in outcomes),
    )
    terminal_value = terminal.model_dump(
        mode="json", exclude={"contract", "origin", "model_evidence"}
    )
    require(row.get("terminal") == terminal_value, "observed_terminal_changed")
    # Never use completion_eligible as accounting authorization: cached usage isn't
    # represented by native AssessmentReceipt or complete_work's unknown counter.
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
    evidence = render_work_briefs(
        work,
        bound.scope,
        intake.declarations,
        intake.briefs,
        receipt=bound.delivery_receipt,
        raw_final=bound.raw_final,
    ).encode("utf-8")
    files = {
        f"{ref.name}.{name}": prepared.files[name]
        for name in (
            "intake.json",
            "request-set.json",
            "local-provenance.json",
            "source-receipt.json",
        )
    }
    require(files[f"{ref.name}.intake.json"] == context.exact_intake, "observed_exact_intake")
    envelope = {
        "contract": "assessment-observed-completion-1",
        "origin": "observed_openai_transport",
        "source_origin": "registered_diagnostic_probe",
        "state": "bound_unassessed",
        "notice": NOTICE,
        "work": ref.name,
        "source_binding": context.pin.model_dump(mode="json"),
        "observation_binding": binding,
        "input_members_sha256": {n: storage._sha(v) for n, v in files.items()},
        "intake": intake.model_dump(mode="json"),
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
    files[f"{ref.name}.completion.json"] = encoded(envelope)
    files[f"{ref.name}.view.md"] = (
        f"{NOTICE}\n\n"
        "Full intake, held/unselected fields, terminal accounting and delivery provenance: "
        f"[{ref.name}.completion.json]({ref.name}.completion.json). "
        "The native evidence view below is a projection, not the delivery envelope.\n\n"
    ).encode() + evidence
    return files


def publish_observed(source: str, destination: Path) -> Literal["created", "reused"]:
    """Publish all four complete registered works, or nothing; never dispatch inference."""
    matches = [r for r in REGISTERED if r.name == source]
    require(len(matches) == 1, "observed_unregistered_source")
    registration = matches[0]
    require(
        storage._sha(storage._read(registration.plan)) == registration.plan_sha256,
        "observed_registered_plan_changed",
    )
    audit_files = {
        n: storage._read(registration.audit / n) for n in ("audit.json", "view.md", "manifest.json")
    }
    require(
        storage._sha(audit_files["manifest.json"]) == registration.audit_manifest_sha256,
        "observed_registered_audit_changed",
    )
    audit_manifest = _object(audit_files["manifest.json"])
    require(
        audit_manifest.get("files_sha256")
        == {n: storage._sha(v) for n, v in audit_files.items() if n != "manifest.json"},
        "observed_audit_members_changed",
    )
    plan = smoke.load_plan(registration.plan)
    prepared = {w.name: smoke._work(w) for w in plan.works}
    protected = (
        registration.plan,
        registration.audit,
        Path(plan.live_journal),
        *(p for item in prepared.values() for p in item.collected.protected),
        *(Path(w.preparation) for w in plan.works),
        *(Path(w.presentation) for w in plan.works),
    )
    storage._destination(destination, protected)
    before, implementation = _snapshot(protected), _implementation()
    # Existing audit must already exist and match its registered bytes. The supported
    # audit recompiles sources, authenticates the closed observed journal and derives
    # every terminal. Exact reuse performs no write to the reference export.
    require(
        smoke.audit(registration.plan, Path(plan.live_journal), registration.audit) == "reused",
        "observed_audit_must_reuse",
    )

    def recheck() -> None:
        require(
            _snapshot(protected) == before and _implementation() == implementation,
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
    for ref, row in zip(plan.works, rows, strict=True):
        assert isinstance(row, dict)
        files.update(_work_files(ref, prepared[ref.name], row, value, binding))
    files["manifest.json"] = encoded(
        {
            "contract": "assessment-observed-publication-1",
            "origin": "observed_openai_transport",
            "source_origin": "registered_diagnostic_probe",
            "notice": NOTICE,
            "state": "bound_unassessed",
            "works": [w.name for w in plan.works],
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
