# ADR 0038: Read-only review evidence export

- Status: Accepted
- Date: 2026-10-30
- Extends: ADR 0005's immutable source versions, ADR 0008's review/prose
  separation, ADR 0033's native checks and ADR 0037's provenance discipline.

## Context

The PO/EX comparison and subsequent local audits support deterministic statements
about explicitly selected text. They do not establish automatic semantic
correspondence, critic correctness, writer preservation or story quality.
The [local integration design](../handoffs/reviewer-copy-integration-design-2026-10-30.md)
qualified a source-bound prototype using twelve authored cases and SQLite/fake
gateways. A tracked operator tool is now authorized, with inference paused.

## Decision

Add an offline `scripts/review_evidence_export.py` command with `inventory` and
`export` operations. There is no inference operation, provider construction,
worker startup, migration, prompt change, acceptance change or writer dispatch.
The export is application evidence for operator review, not story canon.

Keep typed, versioned source/selection/result records and the deterministic
comparison in the provider-neutral engine. The API service adapter reads saved
SQLite records; the CLI only selects a database, exact invocation IDs and a
destination. Support v61 ordinary successful schema-validated critics with native
audit schema 7 and graph 9. Require the frozen run to agree. Unsupported records
receive explicit non-results; never retag them or synthesize missing checks.

Read SQLite through `mode=ro`, `query_only=ON` and one explicit read transaction
per batch. Do not use the normal application engine, which creates directories
and configures WAL. A missing database stays missing. No invocation, artifact,
workflow state, settings, journal policy or schema is changed. Read locks and
SQLite's shared-memory coordination are not manuscript or database writes.

The full source contract binds the exact critique creator and target, project/run,
input versions, canonical hashes, standalone Scene Plan, current draft, native
checks and actual request. Recover the supported system/user messages from saved
prompt text only when exactly one role/content serialization matches the saved
prompt hash. Never rebuild a historical prompt from current instructions.
Recovery is bounded to two million characters and 512 candidate boundaries.
Missing/truncated/unsupported views remain unavailable.

Preserve both the complete safe original critique and saved native audit,
including original statuses, explanations and advice. Invalid source data yields
no partial comparison. Where the original critique itself cannot be verified,
do not present it as a verified original. Security failures abort the export;
do not silently redact exact quotations or swallow credential errors as ordinary
incompatibility. Errors printed by the CLI never include source bodies or
validation inputs.

For each populated assignment anchor, compare its exact canonical field with
**every** selected current-draft handle, retaining order and separate results.
Validate the assignment's rendered contract and retain its hash. Versioned
catalog replay resolves duplicate occurrences against canonical prose; quotation
search alone cannot choose a location. Pin the v61 catalog algorithm and test
parity against the unchanged production helper. Its local implementation hash
does not attest to a historical runtime binary.

Retain canonical/field/view/catalog hashes, field pointers, handles, code-point
offsets, selected quotations and visibility labels. Hash actual view field
presence, including omitted scope fields, without adding defaults. Compare exact
Unicode code points without normalization. Unavailable text is unknown, never
different. Copying does not establish fulfillment; differing text does not
authorize repair. The saved met/unmet judgment remains independent.

The command does not select an original-to-revision correspondence. It explicitly
reports that mapping as unresolved. Pure span primitives retain the tested
recovered/unavailable-source behavior for independently established locations;
no similarity selector or user-supplied assertion of semantic equivalence is
exposed by this command.

## Output and replay

Accept one to twelve distinct explicit invocation IDs. Inventory reads ordinary
critic metadata and identifies candidates; it does not certify full eligibility
or silently choose a sample. One export batch uses a consistent source snapshot.

Write `review-evidence.json`, a literal-source Markdown review packet, and a
manifest with hashes. Mark statements as application-computed selected-span
comparisons beside the unchanged original review. Story text and model output
are rendered as literal data, including embedded Markdown/HTML. A manifest is
written last; a partial output never counts as complete.

An existing destination is reusable only if its complete file set and every byte
match the newly computed export. Do not overwrite changed or partial exports,
follow export-member symlinks, or silently repair a manifest. Recompute displayed
comparisons before writing, so supplied equality fields cannot become evidence.
Guard all exported data against credentials before creating a destination.
Combined JSON/Markdown output is capped at 32 MiB; this local limit creates no
model call allowance or manuscript length rule.

The JSON/Markdown bundle is derived external output. No SQL migration, persisted
application schema, public API/client contract or graph checkpoint change is
needed. Any later API/UI or persisted evidence integration requires its own
versioned contract and migrations where applicable. Preserve the single Blueprint
checkpoint and the artifact-centered product without a manuscript editor.

## Qualification and limits

Tracked tests cover the twelve source/status cases, catalog parity, literal
identity and semantic independence, missing/conflicting provenance, exact view
hashes, SQLite read-only and concurrent snapshot behavior, successful retry
lineage, repeat export, drift/partial-output rejection and secret protection.
Local compatibility does not qualify model judgments or literary quality.

Inspect at most twelve compatible saved reviews after a metadata inventory. If
none exist, report zero coverage rather than generating or substituting samples.
The bounded inventory and checks are documented in the
[implementation report](../handoffs/reviewer-copy-export-results-2026-10-30.md).
Production prompt 61, graph 9 and fulfillment policy 1 remain unchanged.
**Step 19 remains IN PROGRESS; Step 20 remains NOT STARTED; inference PAUSED;
full workflow canary ON HOLD.**
