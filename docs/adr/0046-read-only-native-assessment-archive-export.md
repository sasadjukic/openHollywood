# ADR 0046: Read-only native assessment archive export

- Status: Accepted
- Date: 2026-11-12
- Extends: ADRs 0041–0045; ordinary-review and diagnostic-probe contracts stay separate.

## Context

The B/H audit preserved twelve successful pairs and verified full-context native B
authority views. The engine renderers existed, but neither the ordinary-review
database exporter nor the registered diagnostic-probe exporter admitted these
native assessment captures. The user authorized a read-only exporter and local
verification against the same twelve B captures, with inference paused.

## Decision

Add an application service and `scripts/assessment_archive_export.py` CLI. Keep
filesystem/archive authentication outside the provider-neutral assessment domain.
Reuse the existing work, result, scope, work-brief and authority contracts and
renderer without changing them. Add no provider, workflow, database, UI route,
prompt, model-profile or writer dispatch operation.

The CLI accepts one to twelve distinct, explicit B trial IDs from the November 7
authored-authority comparison. Its trust root is the registered results-seal hash
and plan hash. It reads the relocated, immutable repository-shaped `captures/`
snapshot from the prior audit, not the mutable working checkout. Authenticate all
636 historical members, including source pins and contemporaneous documentation;
never execute or import historical scripts. No CLI option can supply a different
trusted seal. Test-only contract injection admits small explicitly authored fixtures.

Bound reads by member count, member size and aggregate archive size. Reject path
escapes, symlinks/junctions, missing members, conflicting hashes and unregistered
archives. Compare frozen requests, work/context identity, cell receipts, actual
count/generation dispatches, completed response text, native completion and usage.
Reject partial/failed deliveries. Unknown usage, when present consistently, stays
unknown rather than becoming zero or an inferred bill. This exporter does not
relax any historical live-run stop rule.

Validate the original authored auxiliary identities before deriving new
work/declaration/request bindings for the actual saved B work. Preserve all
semantic text and sources; retain original and derived auxiliary records separately.
Parse the complete frozen message sections to establish what this assessment saw.
Do not certify a historical critic's visibility or change domain preview flags.

Export each capture as complete JSON, native literal Markdown and a separate
operator receipt, plus an index and manifest. Retain the request, full work, raw
final, saved delivery/usage and response envelopes. Gold and semantic inspection
annotations are not export inputs, although their historical bytes are authenticated
as part of the archive closure. The operator receipt was absent from B model input
and cannot add evidence retroactively.

Recompute caller-supplied exports from authenticated sources before publication;
recheck source bytes after rendering. Apply the existing secret guard before any
output. Record current implementation hashes and exact source/output hashes. Write
new destinations exclusively, with the manifest last. Exact repeats verify and
reuse all files without writes; partial, extra or changed output is refused. An
interrupted publication is an incomplete destination, never a completed export.

## Limits and consequences

This is a supported local operator capability for one registered diagnostic
archive. It does not admit production reviews, create canonical story provenance,
or activate autonomous assessment. Existing ordinary/probe exporters remain intact.

Scope holds and missing historical proof remain visible findings. Structural
consistency and exact copying do not prove semantics; incorrect authored free text
may pass structure while remaining unverified. Every export retains unassessed
factual support/evidence adequacy/craft and denies writer permission. Successful
delivery is not a story-quality or necessary-edit decision.

Tracked tests use authored data and block network/database operations. Local
acceptance additionally requires exact Markdown equality with all twelve audited
B views and unchanged original work/request/final/receipt evidence. See the
[implementation and verification report](../handoffs/native-assessment-export-2026-11-12.md).
