# Exact-version workspace lookup qualification — 2026-11-19

## Outcome

Qualified a tracked read-only lookup against the six registered historical production
associations and the current configured database. All **12 exact selections** pass:
the critique and reviewed draft for each association. The application's existing
exact-version read model returns the same selected identity, content and lineage.
R03/R05 remain attached to their original older versions; R04/R06 are independently
valid newer selections, not substitutions for those old reviews.

All six retain **unsupported assessment contract** and **missing native delivery in
the captured evidence**. Current-row verification supplies no assessment attachment,
semantic qualification or writer authority. All seven diagnostic consumer works retain
null production associations. No live inference, metadata, input-count, daemon or
provider calls occurred. Production prompts are unchanged; the canary is **ON HOLD**.

## Implementation and source authority

Added [the lookup service](../../apps/api/open_hollywood_api/services/production_association_lookup.py)
and [bounded row revalidation](../../apps/api/open_hollywood_api/services/production_association_rows.py),
with [authored SQLite fixtures](../../tests/production_lookup_fixtures.py) and
[boundary tests](../../tests/api/test_production_association_lookup.py).
[ADR 0063](../adr/0063-registered-read-only-workspace-association-lookup.md) records
the source/transaction contract. Existing exporters, workspace read model, production
routes, prompts, engine evaluation modules and native assessment admission are unchanged.

The supported local registration is `local-production-workspace-2026-11-19`, associated
with the existing `production-association-2026-11-19` archive. The lookup accepts one to
twelve distinct explicit selections, each containing role, project, logical artifact,
version and canonical content hash. It accepts neither caller database paths nor trust
overrides. The complete 51-member historical archive is authenticated on each batch.

The schema has no durable workspace-instance ID. This qualification therefore pins
the configured path plus the local filesystem device/file identity in tracked code.
The archive's database locator must agree. This rejects copied or replaced files even
when they contain the same UUIDs; current row checks reject changed content/provenance
within the same file. A path or matching UUID alone is insufficient.

This source registration is intentionally local. It is not a portable workspace ID,
provider attestation or defense against a hostile process/filesystem owner. A restore,
replacement or relocation needs explicit requalification. No database identity row or
migration was added. The old full-database hash remains historical capture evidence;
it is not used to reject otherwise valid rows after unrelated commits.

## Revalidation and result states

The current-row check covers the review invocation/run, creator/output links, complete
input inventory, critique, target, plan and remaining original inputs, saved request
settings/text/hash, draft creator and original critique/draft lineage. Canonical content
hashes are recomputed. Current SQL serialization hashes are retained in the row-closure
digest; a different JSON serialization alone does not change canonical identity.

The application `WorkspaceStore.get_artifact_version` is called for the **explicit
selected version** on the same read transaction. Its selected IDs, content/hash,
artifact kind/key, schema, version number and parent must match. New valid heads may
exist while the old selected version remains valid. Historical facts stay in the
nested historical record; separate lookup-time lineage facts describe current heads.

| State | Meaning | Assessment attachment |
| --- | --- | --- |
| `identity_verified` | Exact registered selection and current source closure agree | False |
| `no_registered_association` | This version/role has no registered association | Unavailable |
| `selection_mismatch` | A candidate exists, but project/artifact/hash keys disagree | Unavailable |
| `ambiguous_association` | More than one candidate matches exactly | Unavailable |
| `current_source_missing` | Required current rows are missing | Unavailable |
| `current_source_mismatch` | Content, provenance, lineage, bounds or read-model checks fail | Unavailable |

Unavailable entries contain no identity record. Failed archive/source registration,
detected source or implementation drift, and secret failures abort the batch. There
is no latest-version fallback, fuzzy matching, repair or partial identity certification.

## Read-only behavior

Use the existing SQLite `mode=ro`, `query_only=ON` reader and one explicit transaction
for the batch. The normal database factory is avoided because it creates directories
and configures WAL. SQLAlchemy sessions for the workspace read model share the same
connection/transaction; transaction continuity and zero SQL changes are checked.

This path reads committed WAL data. It does not use `immutable=1` or ignore a nonempty
WAL. Changes to main/WAL file identity, size or modification stamp during a batch cause
refusal. An unrelated commit **between** separate lookups is allowed if the selected
source closure still matches. Archive bytes/inventory and implementation are rechecked
before results are returned.

The actual production database and both sidecars remain **byte-identical**. Main
database and WAL modification times are unchanged. SQLite refreshed the SHM timestamp
during read-lock coordination, while its bytes remained identical. This expected
ADR-0038 behavior is recorded in `database-before.json` and `database-after.json`;
the original timestamp was not restored or represented as unchanged. No SQL state,
artifact, invocation, workflow, schema or setting was written.

Resource bounds cover at most 12 selections across the six registered associations,
64 lineage rows, 128 input links, 64 critique outputs and 128 selected evaluations.
They are local read limits, not story-length constraints or quality rules.

## Verification and preservation

**43 new tests and 235 existing tests pass: 278 distinct tests.** Existing coverage
includes historical association/export behavior, native review evidence, ordinary
intake, diagnostic consumers and the workspace API/read model. The new tests use
disposable authored SQLite databases with sockets and HTTP clients disabled; they
do not depend on private production prose.

New tests cover exact and historical selections, project/artifact/version/hash/role
mismatches, missing/replaced/copied/configured-source conflicts, changed source rows,
provenance and old lineage, ambiguous associations, wrong application read results
and metadata, forbidden SQL writes, secret failure propagation, archive/code drift,
resource bounds and rejected caller trust fields. An unrelated commit remains valid,
a newly appended head leaves the old selection intact, WAL changes are visible, and
a concurrent WAL commit aborts the batch.

**69 saved-workspace controls pass** with network disabled:

- Twelve exact version selections, all with the supported application detail read.
- Forty-eight project/logical-artifact/version/hash selection faults, all unavailable.
- Two substitutions of actual newer draft IDs into the old selections, both refused.
  Complete explicit selections for those newer drafts succeed in their own right.
- Seven existing diagnostic works retain null production associations.

All twelve saved results reproduce exactly on repeat lookup. All six selected reviews,
their 41 input-version occurrences and 327 historical catalog occurrences remain bound
to the same authenticated context. These are structural identity checks, not new
semantic labels or evidence-adequacy judgments.

Ruff, formatting and strict mypy pass on **317 Python files**, including the two private
verification helpers. Existing async API tests used the approved local runtime outside
the Windows sandbox for loopback initialization; all data/transport remained fixtures.
No frontend, API contract or persisted schema changed, so frontend builds and migrations
are not applicable. Full-repository pytest was not run.

Preservation checks cover **3,540** earlier sealed members, separate **64** authored
controls, **636** archive pins, **1,706** source files/mtimes, three closed journals,
**88** diagnostic consumer files, **23** historical association export files and
**851 of 854** baseline files outside the three intended documentation updates.
All fourteen issue bodies and posted URLs remain unchanged. Document links and diff
cleanliness are verified. Earlier evidence roots are neither edited nor resealed.

Private evidence root: `data/diagnostics/assessment-workspace-lookup-2026-11-19/`.
`workspace-registration.json` records the local physical-file binding; `request.json`
freezes all twelve selections; `lookup-result.json` and `verification.json` preserve
results and controls. Before/after database pins, preservation/test/quality logs and
a new acceptance seal complete the local record. The service has no transport or
publication command and adds no artifact-inspector attachment yet.

## Recommended next step

Implement a **narrow read-only provenance view in the existing artifact inspector**
using this lookup. Bind the response and display to the explicit selected version,
show the historical critique/target relationship and separate assessment status,
and test version switching plus unavailable, ambiguous and unregistered-source states.
Do not substitute the active head or let a stale response populate a different selection.

Keep identity verification visually distinct from assessment support or story quality.
Show unsupported contract and missing captured delivery without attaching any diagnostic
completion or adding writer controls. Actual assessment attachment still requires a
supported production source and separately authenticated completion. No new live test
is needed for this read-only presentation work.

Feel, flow, character and story-breaking effects remain separate evaluation targets.
No additional human checkpoint is introduced. CW-007/CW-013 remain open; CW-014 remains
unqualified. **Step 19 IN PROGRESS; Step 20 NOT STARTED; production prompts unchanged;
live calls PAUSED; full workflow canary ON HOLD.**
