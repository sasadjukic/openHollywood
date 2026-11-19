# ADR 0063: Registered read-only workspace association lookup

- Status: Accepted; bounded local qualification
- Date: 2026-11-19
- Extends: ADRs 0005, 0038 and 0062

## Decision

Qualify a separate application lookup over the six registered historical associations.
Accept a registered workspace name and one to twelve distinct explicit artifact
selections. Each selection includes role, project, logical artifact, immutable version
and canonical content hash. No caller database path, trust flag, source digest or
assessment completion is accepted. No HTTP route, UI or writer integration is added.

There is no persistent workspace-instance ID in the current schema. For this bounded
local qualification, register the configured database path and its filesystem device
and file identity in tracked code, alongside the existing association registration.
The configured path, physical file identity and historical archive registration must
agree. Refuse links/junctions and replaced, missing or unregistered files. A copied
database containing the same UUIDs does not inherit this registration.

This is a local source binding, not a portable installation identity or protection
against an adversary controlling the process/filesystem. Database replacement,
restore or relocation requires explicit requalification. Do not add a migration or
silently enroll the current configured file. The historical database digest remains
historical evidence; unrelated commits between lookups do not invalidate associations.

## Current-row revalidation

Authenticate the entire registered historical archive and independently validate its
six snapshots. Resolve candidate associations by exact selected version and role,
then require all selection keys to agree. No candidate, wrong keys or multiple exact
candidates yield explicit unavailable states. Do not substitute the latest version.

For each matching selection, read the current review invocation/run, output inventory,
complete input inventory, critique, target, corresponding plan and other original
inputs, draft creator and critique/draft lineage. Recompute canonical content hashes
and compare immutable identity, content and saved request context to the authenticated
snapshot. Preserve the raw SQL serialization digest as current evidence, but compare
canonical content rather than demanding an identical SQL JSON encoding.

Original lineage rows must remain intact. New valid heads may be present without
changing the original association. Keep historical lineage facts nested in the original
record and expose separate `review_lineage_at_lookup` and `draft_lineage_at_lookup`
facts. No current read rewrites the historical record's `current_database_revalidated`
flag. Current validation is a separate result, scoped to the selected source rows.

Use the existing `readonly_connection`: SQLite `mode=ro`, `query_only=ON` and an
explicit read transaction. Do not use the normal engine constructor, which creates
directories and configures WAL. Bind a SQLAlchemy connection and `WorkspaceStore`
sessions to the same transaction. Recheck the read-only flag, transaction continuity
and zero SQL changes. Call the existing exact-version read model and check selected
IDs, kind/key, schema, content/hash, version number and parent against the verified
source. Never use its active/latest version as a substitute.

Bound lineage to 64 rows, input links to 128 and critique outputs to 64. Bound selected
evaluations to 128 before invoking the existing detail loader. These are operator
resource limits, not story-length or semantic rules. A bound violation yields no
identity result for that selection.

Check main-database/WAL file identity, size and modification stamps before and after
the batch; refuse detected concurrent changes. Reauthenticate archive bytes/inventory
and implementation before returning. SQLite's WAL-aware read path includes committed
WAL content; do not use `immutable=1` and ignore it. Shared-memory read-lock coordination
is allowed under ADR 0038 and is distinguished from story/database mutation.

## Outcomes and limits

Successful results mean `identity_verified` for the explicit selection against the
registered local source in this read transaction. Missing or conflicting current
rows yield unavailable entries, never partially verified identities. Source/registration
drift and secret failures abort the whole batch. No inferred similarity, latest-head
fallback, source repair, SQL write, provider construction or inference occurs.

The captured v33 assessment contract remains unsupported, and native delivery remains
missing in that historical evidence. Current identity validation cannot grant assessment
attachment or writer permission. Semantic, evidence-adequacy, editorial, edit-necessity
and craft status remains unassessed. The seven diagnostic consumer associations remain
null. No new assessment artifact or mandatory human checkpoint is created.

Next implement a narrow read-only provenance view in the existing artifact inspector,
using this qualified lookup and explicit unavailable states. It should display source
identity separately from unsupported/missing assessment state. It must not attach the
diagnostic completions or convert identity verification into a quality verdict.

See the [qualification report](../handoffs/assessment-workspace-lookup-2026-11-19.md).
Production prompts remain unchanged, live calls paused and the canary on hold.
