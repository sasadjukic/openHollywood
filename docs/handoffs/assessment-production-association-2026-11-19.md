# Exact production review/artifact association audit — 2026-11-19

## Outcome

**All six selected saved production reviews have verifiable exact links to their
original draft versions. None is eligible for the current assessment consumer.**
The blocker in these records is contract compatibility and missing assessment
delivery, not a missing review-to-artifact identity.

The [consumer export](assessment-consumer-export-2026-11-19.md) remains unchanged.
No production association was attached to its seven diagnostic works. No provider,
daemon, metadata, input-count or generation request occurred. Production prompts,
workflow gates, writer behavior and database content remain unchanged; live calls
are paused and the full workflow canary is on hold.

## Scope and selection

Read only the configured `data/open_hollywood.db`, with a metadata inventory before
selecting **six** detailed reviews. There are **147** ordinary-critic invocation rows:
144 succeeded and three failed. Prompt versions range from 29 to 33; none is v61,
and none has the required schema-7 scene-boundary audit. This agrees with the
[earlier inventory](reviewer-copy-export-results-2026-10-30.md), which covered 54
workspace databases. That larger inventory was not repeated. This audit makes no
claim about other databases or newly available records outside its stated scope.

Select the latest three v33 projects by critic completion time. Within each,
prefer the two latest versions of the most recent repeated critique artifact;
otherwise select the earliest/latest distinct critiques. Freeze the six invocation
IDs before detailed inspection. This gives three projects and two actual review/
draft revision pairs without exceeding six reviews. They are saved successful
Ollama/Gemma production invocations, not test-database fixtures. They remain
**historical v33/graph-9 records**, not retagged v61 examples.

| Case | Critique artifact-version UUID | Reviewed draft-version UUID | Current head in each logical lineage? |
| --- | --- | --- | --- |
| R01 | `326c231a-72e8-4576-833b-d3ecece1b500` | `d4b89be6-7b91-46de-9177-efe73a019c32` | Both yes |
| R02 | `4544cc4f-1db5-4ab2-8654-8f313319a791` | `96c78214-5f99-4aed-ab84-257de80b5d4b` | Both yes |
| R03 | `f0906627-fc83-4d52-9ac9-1f66d84b505c` | `f50dfddb-397a-48d0-b75c-7673d015dd05` | Both no; R04 is newer |
| R04 | `38d5cd29-ffb1-4597-a5c8-10585099a88c` | `f74a7008-8cad-438e-a24e-4d3d71c4df13` | Both yes |
| R05 | `56fb9046-4877-4689-91e2-781c57d8d00e` | `5abd5d7d-d1f0-49b3-94b4-3cccae79a3ac` | Both no; R06 is newer |
| R06 | `60d91b77-5091-460e-ba88-732dd1a4e08d` | `a66a06d2-bc87-42d8-ad28-de26e52aea6c` | Both yes |

R01/R02 belong to one project, R03/R04 to a second, and R05/R06 to a third. Full
invocation, run, project, logical artifact and version identities, content hashes,
parent links and prompt hashes are in the six private association records.
“Current head” describes this frozen database snapshot, not story approval or a
promise about future versions.

## What was verified

For each selected review:

1. Resolve the exact successful `scene_critic` invocation and production run; require
   exactly one saved critique output created by that invocation, in the same project.
2. Check the immutable critique version and its canonical JSON hash. Resolve its
   exact `target_artifact_version_id`, require that version in the invocation input
   relation, and verify the target's canonical content hash, artifact kind and project.
3. Verify every recorded input version and hash—**41 input occurrences** across the
   six reviews. Locate one matching standalone Scene Plan by its recorded scene ID.
   Verify the target draft's creator/run and both critique/draft parent lineages.
4. Recover the unique system/user serialization that matches the saved prompt hash.
   This is a mechanical check of these v33 records, not adoption of a new supported
   v33 intake contract. Match the actual request's input-version inventory, artifact
   identities, assignment scene and target view to the selected canonical draft.
5. Preserve the historical version even when it is no longer the head. R03 and R05
   remain valid associations to their old drafts; substituting R04/R06's newer draft
   versions fails exact association.

All six target views use an `evidence_catalog` instead of the canonical `prose`
field. **327 saved excerpt occurrences** align in order with the canonical target
prose and cover all non-whitespace characters. Inter-excerpt whitespace and the
catalog structure differ from canonical artifact JSON. Therefore each record keeps
both the canonical content digest and the separate actual visible-view digest.
Neither digest substitutes for the other.

R03 and R04 each contain three excerpt entries whose text occurs more than once.
Their ordered complete catalog resolves those occurrences against the selected
version. A standalone quotation search would not supply the same binding. This is
literal coverage evidence only; it does not establish that a critic's inference,
explanation, suggested edit or story-quality judgment is correct.

## What remains ineligible

The unchanged supported `load_entry` path returns **`unsupported_contract` for all
six**. They have prompt version 33, no schema-7 scene-boundary audit, and no saved
v61 run-prompt marker. Missing native assignment checks are not reconstructed from
the critique or catalog. No old contract is promoted merely to populate a sample.

These are production critique records, not native assessment deliveries. Their
stored provider-response hashes do not supply the missing complete raw delivery
and authenticated assessment receipt. The saved normalized critique must not be
relabeled as the exact raw provider response. No model-assessment judgment, cost,
semantic qualification or writer permission is fabricated.

The existing native `AssessmentContext.canonical_review_id` and consumer
`ProductionBinding` deliberately permit null association only. Even the saved-review
intake currently carries its source proof in operator provenance while constructing
a diagnostic context. Filling an ID into either immutable record would change its
contract and fingerprints. The audit made no such change.

The seven F/N consumer exports remain explicitly unassociated. Matching scene labels,
field IDs, filenames or prose is insufficient to connect them to any production
review. This audit does not create an assessment corresponding to the six R cases.

## Proposed association boundary

Use a separately versioned, application-owned association record rather than
mutating existing diagnostic work/completion records. Keep two independent decisions:

- **Exact source identity:** evidence binds a saved review invocation to its critique
  artifact version and reviewed draft version, within the same project/run, with
  matching canonical hashes, input links, parent lineage and actual request identity.
- **Assessment attachment:** a supported source contract and an authenticated native
  assessment completion bind to that exact review/work/request. Passing source
  identity alone does not satisfy this second decision.

Distinguish review invocation ID, critique logical artifact ID, critique version ID,
target logical artifact ID and target version ID. The existing saved intake's
`review_id` is the invocation UUID; it is not the critique version UUID. Retain both
explicitly. Include the registered source/snapshot identity, project/run, source
content hashes, prompt digest and visible-target digest in the association proof.

The physical database hash identifies this audit snapshot; it is not a permanent
workspace identity. Unrelated future writes change it, and copied databases can
contain the same UUIDs. A future adapter must authenticate its registered source
and recheck the relevant immutable rows. Neither an absolute path nor a caller's
UUID/hash assertion is sufficient source authority.

When matching an inspector selection, require exact project, logical artifact,
version and canonical content hash, with an explicit role of original critique or
reviewed draft. Never follow “latest” on behalf of an old review. Missing, foreign,
ambiguous or mismatched associations remain unavailable; a verified historical
association is not automatically corrupt just because a newer version exists.

## Verification and preservation

**195 local checks pass:** six saved-record replays, 108 authored fault refusals,
74 exact/missing/mismatched inspector-selection controls and seven unassociated
diagnostic controls. Faults include wrong database snapshot, invocation, run,
project, logical/version identity, creator, duplicate outputs/inputs, missing input
links, content drift, stale target references, wrong prompt hash, missing parents,
duplicate visible target IDs and changed excerpts. Two controls use the actual
newer draft versions and confirm refusal to rebind an older review.

**156 existing tests pass**, covering review evidence export, native review evidence,
intake, consumer boundaries, persistence immutability and workspace inspection.
No tracked runtime or test implementation changed. Ruff, formatting and strict mypy
pass on **309 Python files**, including the three private helpers. No frontend/API/schema
change requires a production build or migration; full-repository pytest was not run.

The database was opened with `mode=ro&immutable=1`, `query_only=ON` and an explicit
read transaction. Its WAL was confirmed empty before opening. A nonempty WAL or
changed source pin is refused by this audit helper; immutable mode must not be used
to silently omit pending WAL content. Main database, WAL and SHM hashes/mtimes are
checked before and after. No complete database copy, provider configuration/key
export, migration, worker or application startup was used.

Selected snapshots pass the existing secret guard. Replay disables SQLite and
network access; source collection disables network and reads only the pinned local
database. Synthetic mutations remain software controls, not observed model failures.
Preservation verifies the database and both sidecars byte-for-byte and by mtime,
**3,438** earlier sealed members, the separate **64-member** authored-control seal,
**636** archive pins, **1,602** prior source/preparation/result files and mtimes, all
three closed smoke journals, all **88** existing consumer export members and
**842 of 845** baseline files outside the three intended documentation updates.
All fourteen issue bodies and posted URLs remain unchanged. **727** local document
links and `git diff --check` pass. Earlier diagnostic evidence is not resealed or edited.

Private root: `data/diagnostics/assessment-production-association-2026-11-19/`.
`selection.json` freezes the six reviews; `metadata-inventory.json`/`inventory.sql`
record the metadata-only selection population. `R01`–`R06` snapshot/association files,
`audit.json`, `verification.json`, test/quality logs and preservation results retain
the evidence. A separate acceptance seal covers the final local bundle.

## Recommended next step

Implement the **narrow read-only production-association record, validator and operator
export path**, qualified against these six saved identity snapshots and the existing
negative controls. Keep this separate from the fixed diagnostic consumer exports
and from v61 assessment admission. Show exact historical review/target provenance
and explicit `unsupported_contract`/missing-assessment status; do not infer native
checks or create a production assessment attachment.

This provides a tested association boundary before any inspector integration. It
requires no live calls and no expansion of old-model review semantics. Actual
assessment attachment should wait for a supported production review source and its
separately authenticated assessment completion. Do not restart the canary or run
inference solely to manufacture a compatible record.

Story-quality work remains separate: identity and literal coverage checks do not
measure feel, flow, character or story-breaking effects. No additional human
checkpoint is introduced. CW-007/CW-013 remain open; CW-014 unqualified.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; prompts unchanged; live calls PAUSED;
full workflow canary ON HOLD.**
