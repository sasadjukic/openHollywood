# Read-only artifact provenance inspector — 2026-11-19

## Outcome

The artifact inspector now displays the exact registered review/draft relationship
for a selected critique or scene draft. Older selections retain their original
relationship. A separate assessment block explains unsupported contract and missing
captured delivery. Unregistered, unavailable, changed, mismatched and ambiguous sources
show an unavailable state without a relationship. No assessment or writer authority
is attached.

All **12 saved selections** pass through the new API, including **four older-version
selections**. Twelve identical repeats and twelve wrong-hash refusals also pass.
Desktop/mobile browser checks verify version switching, unavailable state and recheck.
Production prompts are unchanged, live calls remain **PAUSED**, and the canary remains
**ON HOLD**. No provider, metadata, input-count or inference call occurred.

## Implementation

- [API projection service](../../apps/api/open_hollywood_api/services/artifact_provenance.py)
  and [GET route](../../apps/api/open_hollywood_api/routes/artifact_provenance.py),
  wired to the same app-owned database as the workspace read model.
- [Inspector card](../../apps/web/src/components/ArtifactProvenance.tsx), using the
  generated API/types, with explicit selection binding and read-only unavailable states.
- [API tests](../../tests/api/test_artifact_provenance.py) and
  [frontend tests](../../apps/web/src/components/ArtifactProvenance.test.tsx).
- [ADR 0064](../adr/0064-read-only-artifact-provenance-inspector.md) records the contract.

The request includes project, logical artifact, immutable version, canonical content
hash and role. The service resolves only the app-owned database's existing fixed
registration. It then invokes the qualified lookup, authenticating its archive and
current source rows. The projection rechecks typed output, request digest, workspace,
selection and historical identity. Caller database paths or source registrations
cannot select a different source. A missing injected service stays unavailable.

The compact `artifact-provenance-view-1` response includes review/draft IDs and hashes,
review invocation/run, registered source, lookup-time head labels and assessment states.
It excludes source prose, prompts, physical file IDs and filesystem paths. It returns
`Cache-Control: no-store`; the browser fetch also disables HTTP caching. The existing
native lookup, archive exporter and diagnostic consumer contracts remain unchanged.

The frontend keys both requests and component lifetime by the explicit selection,
checks the returned selection and selected side of the relationship, and aborts
superseded fetches. A late response cannot populate another version. While revalidating,
or after an HTTP/source failure, the previous verified relationship is hidden. Stale
artifact detail is also withheld. Unavailable results have a local **Check again**
action; no inference or automatic polling/retries are added.

| State | Visible result |
| --- | --- |
| Exact registered identity | Review/draft versions and separate assessment unavailable block |
| Older exact selection | Original relationship plus older-version notice |
| No registration or association | Explicit unavailable reason; no relationship |
| Ambiguous or mismatched selection | Explicit refusal; no guessed candidate |
| Source unavailable/changed or current rows missing/mismatched | Unavailable; no cached success |
| Pending/refetching | Checking this exact version; previous relationship hidden |
| Invalid response or HTTP failure | Generic safe unavailable text; no raw exception |

Source details use literal React text with wrapped identifiers. The version selector
has an explicit accessible name. Visual inspection exposed text showing through the
existing translucent mobile inspector; the drawer now uses an opaque panel background.

## Verification

**214 distinct Python tests pass**, including 23 new projection/route/lifecycle tests
and 191 existing app, workspace, association lookup/export and consumer tests. The final
23-test module also passes after correcting a fixture's secret-error constructor.
Coverage includes all twelve selections, five selection-key faults, unavailable states,
missing/replaced/copied/unregistered sources, safe exceptions, altered lookup results,
no default-source guessing, GET-only behavior, compact output and same-database startup.

**34 frontend tests pass**, including 23 new inspector cases and 11 existing application
tests. New cases cover both review/draft roles, all unavailable reasons, five mismatched
response keys, relationship/permission faults, late and aborted responses, changed
project/hash, cached-success suppression, malformed output and literal source strings.
Unrelated artifact kinds do not request provenance.

**36 saved-source checks pass**: twelve exact selections, twelve identical repeats and
twelve wrong-hash refusals. They use the real registered source through in-process ASGI,
with socket connections blocked and without the production application lifespan.
Every response is below 3,000 bytes. All six reviews remain `unsupported_contract`,
with captured delivery `missing`; all semantic/editorial dimensions remain `unassessed`.

An isolated headless Chrome check exercises the real frontend/SDK with **authored API
fixtures**, not a production server: 16 intercepted GETs, including five provenance
reads. Desktop (1500 × 1100), mobile (390 × 844), old-version selection, unavailable
state and recheck pass, with no page errors, unexpected requests or horizontal overflow.
The three screenshots were visually inspected. This browser check demonstrates UI
behavior; the separate saved-source ASGI check establishes actual source binding.

Ruff, formatting and strict mypy pass on the **318** tracked Python source files in
the README's check directories. Frontend formatting, ESLint, strict TypeScript, Vitest
and production builds pass. OpenAPI and generated SDK/types are updated together.
Full-repository pytest was not run; the relevant API/source/export suites were run.

The pinned pnpm 11.12.0 was absent from the local Corepack cache; its registry attempt
failed without downloading packages. Checks used the bundled pnpm 11.25.0, within the
repository's declared major-version range, and existing installed dependencies. Thirteen
otherwise byte-identical generated helper files have refreshed modification times;
their bytes were verified separately. No dependency manifest or lockfile changed.
Windows asyncio/browser loopback checks used
the approved local runtime outside the sandbox; provider traffic remained absent.

## Preservation and limits

Production database and WAL/SHM bytes remain identical. Main database and WAL mtimes
are unchanged; SQLite refreshed only the SHM mtime during read-lock coordination.
No SQL story state, artifact, workflow, schema or setting was written. No real worker
or production application lifespan was started.

Preservation covers **3,568** earlier sealed members, **64** separate authored controls,
**636** archive pins, **1,735** source files/mtimes, three closed journals, **88** consumer
files, **23** association export files and **847/860** byte-identical baseline files outside the thirteen
intended existing-file changes. Fourteen issue bodies and posted URLs remain intact.
Document links and diff cleanliness are checked; earlier evidence is not edited or
resealed.

Private evidence: `data/diagnostics/assessment-provenance-inspector-2026-11-19/`.
Start with `saved-verification.json`, twelve `selection-*.json` projections,
`browser-verification.json` and the screenshots. Database pins, check records, source
snapshots, preservation results and a new acceptance seal retain the local evidence.

This is the bounded registration from ADR 0063, not general enrollment of any saved
review. Other workspaces/versions correctly remain unavailable. Database restore,
replacement or relocation needs requalification. The archive must remain present.
Identity verification says nothing about critic accuracy, evidence adequacy, necessary
edits, preservation or story quality. The seven diagnostic consumer works remain
unassociated. CW-007/CW-013 stay open; CW-014 remains unqualified.

## Recommended next step

Do a **bounded local qualification of supported production-review admission and exact
completion binding**. The visible remaining gap is no eligible assessment for these
historical reviews; more presentation work or another model comparison will not fill it.

1. Trace the current production review contract into the existing read-only intake and
   identify the exact source fields and terminal evidence it requires. Preserve the
   six historical v33 reviews as unsupported controls; do not retag or upgrade them.
2. Rehearse one supported review/draft pair in a disposable authored current-contract
   workspace, with missing-delivery and wrong-version controls. Mark authored origin
   explicitly. Require exact request/source/terminal binding before considering a
   completion eligible, and keep observed/model judgments distinct from verified facts.
3. Record whether the existing intake/completion contracts suffice or a narrow adapter
   is needed. Propose implementation or a separately frozen live smoke only after that
   local source-to-completion path passes. Do not attach the seven unrelated diagnostic
   completions or activate writer gates.

This next step needs no live calls. Feel, flow, character and story-breaking effects
remain separate quality targets, and no additional human checkpoint is introduced.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; prompts unchanged; live calls PAUSED;
full workflow canary ON HOLD.**
