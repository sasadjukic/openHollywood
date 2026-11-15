# ADR 0057: Explicit authored assessment sources

- Status: Accepted; bounded read-only local implementation
- Date: 2026-11-15
- Extends: ADRs 0049 and 0053–0056

## Decision

Add a separate authored-source domain, registered application adapter and local
operator CLI. Do not broaden saved-review intake, probe source pins, the existing
authored-response publisher or the November 14 observed registration. Source
origin and assessment-delivery origin describe different events.

Initially register only `fresh-claims-2026-11-15`, its exact admission manifest
digest and three families F01/F02/F03. Reauthenticate all 31 admission members and
the two construction-file digests. Construction files are read, never executed.
Gold members are authenticated as bytes but never parsed into assessment input.
Caller-supplied hashes cannot register a replacement archive.

Preserve six exact input members per family: work, original local scope,
declarations, briefs, authority and source packet. Recompute their bindings,
whole-field selection, full context, original messages, scope/brief checks and
historical copying checks. Native work retains `synthetic_fixture`; the enclosing
source pin explicitly declares `authored_diagnostic`. Neither implies that a
model produced the review or that an independent human validated its gold.

## Presentation and completion

Use the existing diagnostic `assessment_presentation.SYSTEM` verbatim. A separately
versioned data presentation supplies the complete native work, original declarations,
briefs, authored authority and all field dispositions. Retain three active whole
claims and one unselected editorial summary per family. Clarify that archived
`model_input=false` and local scope identities describe construction, not provider
requests or historical model visibility. No gold labels, rationales or witness
spans are added to model input. Authority examples remain illustrative, not a
citation whitelist. Production prompts do not change.

The preparation is not a provider request or live authorization. The existing
compact presentation has a different registered-intake/provenance contract; do
not coerce these packets into it. Qualify any later provider mapping separately.

Local completion accepts only an explicitly authored fixture submission bound to
the exact source pin and presentation. The application constructs its fixture
receipt and distinct fixture-input identity; it accepts no caller receipt, usage,
observed-origin label, result override or writer approval. Reuse the native binder,
whole-work completion and authority renderer. Rebind authority to the derived
fixture identity in a separate copy, retaining the original authority and local
scope unchanged. Require every original active unit; do not salvage a subset.

An outer envelope identifies `source_origin=authored_diagnostic` separately from
`delivery_origin=authored_fixture`. Raw finals and all evidence locations remain
visible. Native `model_assessment` field names do not authenticate model origin.
Unknown/null native usage is explicitly **not applicable: no inference**; preserve
all four token counters and actual billing as null. Native null-usage counts and
zero fixture elapsed time are not provider telemetry. Binding leaves semantic
support, evidence adequacy, editing and craft unassessed, and writer permission false.

## Publication

Reuse existing bounded reads, secret checks, link/junction/traversal refusal,
bidirectional source/output protection, exclusive writes, manifest-last finalization
and exact byte reuse. Protect the entire admission archive and the fixture submission.
Reauthenticate the registered source, submission and implementation after rendering,
before writes, before the final manifest and during reuse. Preserve partial failed
outputs without repair or deletion. No database, route, provider SDK, migration,
credential setup, network call or writer dispatch is added.

Prepare exports contain 12 files per family; fixture-completion exports contain
13. Both include all six exact original inputs, explicit source/source receipt,
presentation, a native view and a final manifest. Preparation adds a deliberately
incomplete submission template; completion adds exact submission bytes and a full
completion envelope. No CLI trust or origin override exists.

The [qualification report](../handoffs/assessment-authored-source-integration-2026-11-15.md)
records actual-packet inspection and the next local transport boundary. This
decision qualifies controlled source integration, not natural critic precision,
editorial judgment, revision necessity, preservation or story quality.
