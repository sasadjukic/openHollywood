# ADR 0056: Registered observed assessment completion publication

- Status: Accepted; bounded read-only implementation
- Date: 2026-11-14
- Extends: ADRs 0049 and 0053–0055

## Decision

Add the separate `assessment_observed_completion` service and operator CLI as the
observed branch of the read-only completion publisher. Preserve the authored
publisher, registered B exporter, compact transport and all frozen implementation
hashes. Reuse their source authentication, terminal reducer, native binder,
whole-work completion, work-brief renderer and exclusive publication primitives.
There is no new provider adapter, database schema, route, prompt or writer gate.

Initially register only `compact-smoke-2026-11-14`, with fixed local plan/audit
locations and their reviewed byte digests. The original plan fixes the journal,
intakes, compact presentations, local provenance and exact request sets. The CLI
accepts this source identifier and an output directory; it cannot accept a caller
receipt, origin flag, trust pin, response replacement or subset of claims/works.
Adding another source requires a separately reviewed registration/qualification.

Recollect each original intake and compact preparation, then require exact reuse
of the existing supported smoke audit. This independently replays the closed
application-owned observed journal, its eight endpoint slots and source bindings.
The previously exported audit is not trusted merely because it contains hashes.
Its fixed registration and current source/journal replay must agree. Refuse a
fixture, open/halted run, missing/reordered work or incomplete endpoint coverage.

Regenerate each terminal from the authenticated endpoint outcomes and original
request. Compare the complete derived terminal and original intake with the audit.
Require all four original works to complete and bind without salvage. Independently
require known input/output/reasoning/**cached-input** counters, known elapsed time,
no reservation violation and no accounting hold. `completion_eligible` is not an
accounting clearance flag. A failed run remains inspectable through its original
audit; this success publisher does not publish a successful subset of that run.

## Export and integrity

Use explicit `assessment-observed-completion-1` and
`assessment-observed-publication-1` discriminators and observed-origin notices.
The bundle contains 27 fixed members:

- The original full `source-audit.json` and its `source-audit-manifest.json`.
- For each N06/N07/N10/N11: exact `intake.json`, `request-set.json`,
  `local-provenance.json`, `source-receipt.json`, a derived `completion.json`, and
  a native `view.md`, all prefixed by the work name.
- A final `manifest.json` with every output digest, source membership/digests,
  implementation identity and observation binding.

Each completion envelope retains the full pending intake, declarations, briefs,
held/unselected dispositions, terminal metadata/raw final/all usage, endpoint slots,
closed-run status and recomputed whole-work completion. The intake's original
result/receipt placeholders remain null. The evidence view links to its envelope
and explicitly identifies itself as a projection. Shared reducer fixture labels
are excluded from the observed terminal; preparation/source receipts retain their
original meanings and do not themselves authenticate assessment delivery.

After full source authentication, snapshot bounded protected-tree membership and
bytes, including empty directories. Recheck those pins and implementation identity
after audit/rendering, before writes, before the final manifest and during exact
reuse. This avoids repeated source compilation during individual writes without
accepting source drift. Keep existing secret checks, file/aggregate bounds,
symlink/junction/traversal and bidirectional overlap refusal. Create exclusively;
write the manifest last; retain partial failures without repair or deletion. Exact
reuse verifies all bytes without rewriting them. No key or database is accessed
for inference, and no provider/count/metadata request is made.

## Interpretation limits

Observed origin means an application-owned local transport journal, **not** a
provider-signed attestation. Original raw HTTP bytes were not retained; mapped
responses, final text, IDs and digests were. Preserve that absence and null actual
billing. Publication `live_calls: 0` describes this local operation; the original
four count/four generation observations remain visible in the source audit.

State remains `bound_unassessed`. Factual support, evidence adequacy, editorial
effect, edit necessity and craft remain unassessed; writer permission is false.
Neither mechanical binding nor accounting clearance approves a model's reason or
an edit. Human review still covers feel, flow, character and story-breaking effects.
Production prompts stay unchanged, live calls paused and the canary on hold.

See the [implementation and verification report](../handoffs/assessment-observed-completion-2026-11-14.md).
