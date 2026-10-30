# ADR 0039: Diagnostic-probe review export

- Status: Accepted
- Date: 2026-10-30
- Extends: ADR 0038's local mechanical review assistance.

## Context

The [provenance audit](../handoffs/reviewer-probe-provenance-audit-2026-10-30.md)
verified twelve ordinary-v61 captures in the sealed October 16 probe archive.
These captures retain exact source packets and native checks but have synthetic
context and no persisted production creator. Their plan keys also differ from
the production SQLite contract. A separate operator adapter is authorized.

## Decision

Add `scripts/probe_review_export.py`, a read-only file adapter and typed
`diagnostic_probe` evidence records. Keep the SQLite exporter and its checks
unchanged. The new command has no database, provider, model, worker or workflow
operation. It never executes archive Python files or regenerates requests.

Register the exact October 16 plan, preparation-closure and live-closure hashes.
Require an explicit live archive path, its sibling prepared archive and one to
twelve distinct trial IDs. Verify all preparation/live evidence members and the
operator evidence against those pinned closures. Reject unsupported, incomplete
or inconsistent archives as a whole before output; there is no partial salvage.
New archive support requires a separately qualified registered contract. The CLI
has no override for the trusted hashes. Authored tests inject their own contract
only through the Python test surface.

Read bounded bytes and preserve original UTF-8 JSON text, hashes and relative
source identities. Reject path traversal and member symlinks/junctions. These are
local integrity seals, not provider-signed attestations. Historical report and
implementation hashes remain in the original plan/closures; export does not need
or execute the current checkout's historical request builders. It does not repeat
the earlier validator replay or make a new model judgment.

Bind trial/stage/arm/seed, successful attempt, ordinary critic role, prompt 61,
graph 9 and native audit 7. Verify request reservations, actual saved role/content
hashes, response hashes, usage consistency and successful receipts. Retain failed
predecessors separately. Follow exact post-review writer results and parent-review
lineage. Computed diagnostic UUIDs verify existing identities; they never create
canonical records. Production invocation and canonical critique IDs stay null.

Keep three complete views: raw model response, saved normalized review and saved
native audit. Preserve status, assessment and selected handles. Label advice
rendered from shared finding conditions and raw-to-normalized verdict changes.
Do not reinterpret those transformations as model-authored wording.

Reuse the unchanged v61 catalog algorithm and exact Unicode comparison rules.
Use probe-specific spans rather than fabricating the project/creator fields of
production records. Preserve assignment/source/view/catalog hashes, ordinal
handles, offsets and quotes. Multiple excerpts stay separate. Full local bodies,
shown catalog excerpts, visible historical repair quotes and recovered old prose
retain distinct identities. Original/revision semantic alignment stays unresolved.

## Publication and verification

Publish one Markdown and one JSON file per trial, an index and a manifest.
The JSON retains original selected-attempt files and dependency snapshots;
Markdown renders story/model text as literal data. Guard all output against
credentials. Recompute projections and re-read authenticated archive snapshots
before publishing, rejecting changed sources or caller-supplied comparison claims.

Refuse destinations inside either archive. Write only a new destination; write
the manifest last. An identical repeat verifies every byte without writing;
changed or partial destinations are never overwritten. Limits are 8 MiB per
source file, 128 MiB of cached archive bytes and 32 MiB of JSON/Markdown output.
These are local tooling bounds, not model budgets or manuscript limits.
The manifest's implementation fingerprint identifies the local domain projection
module; it is not an attestation of the historical runtime binary.

No persistence migration, API/client change, dependency, prompt, acceptance gate,
writer route or additional human checkpoint is introduced. Exact copying remains
mechanical evidence, not semantic correctness or literary quality.

Authored regressions cover positive/retry/unmet/post-review records, invalid source
chains, altered hashes, advice, identity and handles, source changes before
publication, sample limits, protected paths, secret rejection and repeat/conflict
behavior. The same twelve real captures are exported and compared to the prior
audit separately. See the [implementation report](../handoffs/reviewer-probe-export-results-2026-10-30.md).

Step 19 remains IN PROGRESS; Step 20 remains NOT STARTED. Inference is PAUSED and
the full workflow canary remains ON HOLD.
