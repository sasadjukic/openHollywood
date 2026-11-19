# Read-only production association export — 2026-11-19

## Outcome

Implemented and locally qualified a tracked association record, validator and operator
exporter over the six saved production-review identity snapshots. All six historical
associations reproduce the previous audit. Identity verification does **not** make
any of these reviews eligible for a native assessment attachment: all remain
`unsupported_contract`, with `missing` native assessment delivery in the captured
evidence. The seven existing diagnostic consumer works remain unassociated.

No live inference, input counts, metadata/preflight requests or daemon calls occurred.
The exporter and saved-capture verification never open a database. Production prompts,
workflow, provider code and writer behavior are unchanged. Live calls are **PAUSED**;
the full workflow canary remains **ON HOLD**.

## Implementation and decisions

- [Typed records and validator](../../apps/api/open_hollywood_api/services/production_association_records.py)
  define the historical source, separate eligibility and exact artifact-selection
  contract. The validator recomputes identity evidence from snapshots; it does not
  trust the earlier audit's derived association records.
- [Registered exporter](../../apps/api/open_hollywood_api/services/production_association_export.py)
  authenticates the full frozen archive and exports all six records together.
- [Operator CLI](../../scripts/production_association.py) accepts only the fixed source
  name and output directory. There is no database path, caller receipt, trust override,
  selection subset, transport or model option.
- [ADR 0062](../adr/0062-read-only-production-review-associations.md) records the boundary;
  the [JSON schema](../contracts/production-review-association-1.schema.json) describes
  the record shape. Schema validation alone is not source authentication.

The binding distinguishes review invocation, critique logical artifact, critique
version, target logical artifact and target version. It includes the captured source,
project/run, canonical content hashes, corresponding Scene Plan, saved-message hash
and visible-target hash. Explicit selection matching checks project, logical artifact,
version and content hash in the requested original-review or reviewed-draft role.
It grants neither assessment eligibility nor writer authority.

All **41** saved input-version occurrences and **327** ordered catalog occurrences
revalidate. Catalog excerpts cover the target's non-whitespace prose; they are not
the full canonical draft JSON. Inter-excerpt whitespace and repeated occurrences stay
explicit. R03/R04 each contain three repeated excerpt entries. Exact literal coverage
is not evidence adequacy or proof that the critic's explanation is correct.

| Case | Input versions | Catalog occurrences | Review/draft selection at capture |
| --- | ---: | ---: | --- |
| R01 | 4 | 26 | Both latest |
| R02 | 9 | 61 | Both latest |
| R03 | 4 | 60 | Both older; original versions retained |
| R04 | 6 | 60 | Both latest |
| R05 | 8 | 60 | Both older; original versions retained |
| R06 | 10 | 60 | Both latest |

Lineage fields explicitly say **at capture**. A saved database digest identifies a
historical snapshot, not a permanent workspace. The exporter does not inspect the
current database or claim its heads are unchanged. The preserved raw SQL content-byte
digest cannot be independently recomputed because those serialization bytes were not
retained in the archive; canonical content hashes are independently recomputed.

Assessment state is separate from these verified identities. These are v33/graph-9
reviews, lacking the current v61/schema-7 source contract and required run marker.
Their stored response hashes and schema-success flags do not establish a native
assessment delivery. Semantic support, evidence adequacy, editorial effect, edit
necessity and craft stay unassessed; whole-review verdict and actual billed cost are
null, writer dispatch false. No native intake or old-contract compatibility was expanded.

## Export and inspection

```powershell
uv run --extra api python scripts/production_association.py `
  --source production-association-2026-11-19 `
  --output data/diagnostics/production-association-operator
```

The original archive's acceptance-seal SHA-256 is pinned in tracked code:
`4b07e7b673922b5620909ceb28721349cadede88859f4f4c2deecc1e37804578`.
All **51** source members are authenticated: 50 sealed files and the seal. The
original cache directories are excluded without loading or executing private scripts.
Wrong paths, extra/missing members, changed bytes or implementation drift refuse
publication. The archive must remain available at its registered local location.

The **23-file** output contains:

- Nine byte-exact evidence members: six complete snapshots and the source selection,
  database pins and acceptance seal.
- Six `Rxx.association.json` records and six literal `Rxx.md` views.
- `README.md` navigation and a manifest written last.

The manifest records the full archive verification and the smaller copied evidence
subset separately. The exported original seal still describes the complete archive;
the subset is not a replacement for that archive. Missing/changed source evidence
cannot be bypassed by presenting a previously exported JSON record.

The existing storage helper supplies bounded reads, secret screening, link/junction
checks, protected destinations, exclusive writes and exact byte/mtime reuse.
Partial or conflicting output is retained and refused, never repaired. Source
membership/bytes and implementation are rechecked before publication and completion.
There is no new transactional/fsync guarantee. No current database, WAL or SHM is
opened by this exporter; those paths are protected against output overlap.

The verified export is local at
`data/diagnostics/assessment-association-export-2026-11-19/verified-publication/`.
Start with its `README.md`; each R view links its complete source snapshot and
association record. All source text is displayed as literal JSON, with fixed generated
navigation. Private story content remains under ignored local diagnostic storage.

## Verification

**82 new offline tests pass**, using authored snapshots rather than private production
fixtures. They cover identity/creator/link/hash changes, historical heads, ambiguous
versions and inputs, rehashed wrong visible context, duplicate excerpt references,
prose gaps, unsupported-contract conflicts, selection mismatches, unchecked typed
model mutations, duplicate JSON keys and schema parity. Export tests cover complete
membership, nine exact source copies, missing current database, exact reuse,
selection cardinality, path/destination protection, source/implementation drift,
partial-output retention, cache exclusion and sanitized secret refusal.

**144 existing tests pass** for review export, native review evidence, ordinary intake
and consumer boundaries: **226 distinct tests** total. The initial sandboxed native
test run stalled during Windows async setup and was stopped; the same suite passed
with the local test runtime allowed outside the sandbox. No production database or
live provider transport was used by these tests.

**195 saved-capture checks pass** with SQLite, sockets and HTTP clients disabled:
six exact replays against the prior audit, 108 authored source-fault refusals,
74 exact/missing/mismatched artifact-selection controls, and seven unchanged null
diagnostic associations. The actual newer R03/R05 draft versions fail old-review
selection matching. All nine copied source files are byte-exact, all 23 output hashes
match the manifest, and a second export reuses the exact bytes and mtimes.

Ruff, formatting and strict mypy pass on **313 Python files**, including two private
verification helpers. This change adds no frontend, API route or persisted schema;
no frontend production build or migration is applicable. Full-repository pytest
was not run. Earlier engine evaluation modules and frozen publisher implementations
remain unchanged.

Preservation checks cover the database and two sidecars, **3,488** earlier sealed
members, separate **64** authored controls, **636** archive pins, **1,653** source
files/mtimes, three closed journals, **88** existing consumer files, **23** new output
files, and **843 of 846** baseline files outside the three intended documentation
updates. All fourteen issue bodies and posted URLs remain unchanged. Documentation
links and diff cleanliness are checked; the private result records the link count.
Earlier diagnostic roots are neither edited nor resealed.

Private evidence root: `data/diagnostics/assessment-association-export-2026-11-19/`.
`verification.json`, `publication-pins.json`, test/quality logs and `preservation.json`
retain the local results; a new acceptance seal covers this completed bundle.

## Recommended next step

Qualify a **narrow read-only workspace lookup for explicit immutable selections**,
using these six associations and missing/foreign/mismatched/ambiguous controls.
Bind the lookup to an authenticated workspace/source, revalidate the selected review
and target rows through the application's supported read path, and preserve historical
versions even when newer heads exist. Do not treat a path, matching UUID or the old
database digest as sufficient authority for the current workspace.

This is the next boundary before a production-inspector provenance display. It can
show exact historical review/target provenance with unsupported/missing assessment
status. It must not attach any of the seven diagnostic completions or manufacture
assessment eligibility. Actual assessment attachment still needs a supported production
review source plus its independently authenticated completion; neither is available
in these six captures. No live experiment is needed to qualify this lookup.

Mechanical identity checks support production reliability, but do not establish critic
accuracy, preservation or story quality. Feel, flow, character and story-breaking
effects remain separate evaluation targets; no additional human checkpoint is added.
CW-007/CW-013 remain open; CW-014 unqualified. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
production prompts unchanged; live calls PAUSED; full workflow canary ON HOLD.**
