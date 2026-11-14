# Version-two diagnostic assessment presentation

Date: 2026-11-14

Status: tracked read-only implementation and local qualification **COMPLETE**.
Production prompts unchanged; live calls **PAUSED**; full workflow canary **ON HOLD**.
No live plan or provider request frozen by this change.

## Result

The [payload audit](assessment-payload-resource-audit-2026-11-13.md) is now implemented
as a separate provider-neutral presentation, application exporter and CLI. It keeps
complete visible sources, original messages, whole reviews, declarations, briefs
and field dispositions. The operator archive remains local and hash-bound; source
locators replace repeated registry quotes, hashes and offsets in the model view.

All four registered works pass local preparation, read-only verification and exact
reuse. Reconstructed version-one presentations match the original frozen records,
including unchanged response schemas and **3,658 evidence bindings**. Replaying the
same **six authored finals** yields complete native binding and whole-work completion
for all four works. These remain authored fixtures, not live model results or gold.

| Work | Active claims | Registry locations | Original user bytes | Version-two user bytes |
| --- | --- | ---: | ---: | ---: |
| N06 | Q001 | 904 | 1,076,455 | 222,480 |
| N07 | Q004, Q005 | 904 | 1,083,642 | 226,111 |
| N10 | Q003, Q007 | 907 | 1,182,995 | 230,447 |
| N11 | Q003 | 943 | 1,800,180 | 235,773 |

These are UTF-8 user-message bytes, not wire bytes or token measurements. The new
diagnostic system instruction is **2,595 bytes** versus 1,709 in version one. It
explains source locators, JSON Pointer escaping, full-field evidence and local-only
provenance. Unlike the smaller audit study's numeric source indices, each row names
its original document directly. This makes the tracked views somewhat larger than
the study. No token count, generation latency, billing or model-quality gain is
established. Only the prior N06 count of 350,749 tokens is known; it belongs to the
old request and cannot be reassigned to this presentation.

## Implementation and source contract

[ADR 0053](../adr/0053-versioned-compact-diagnostic-presentation.md) explicitly extends
the earlier contract. The existing version-one renderer, provider mapper, request
manifests, durable journals and smoke executor are unchanged. No default route
switch, old request repair, schema migration, new dependency or UI change.

- The [domain component](../../engine/open_hollywood_engine/evaluations/assessment_compact_presentation.py)
  defines strict `assessment-intake-presentation-2`, `assessment-local-provenance-2`
  and `assessment-compact-bundle-2` records. It renders, parses, reconstructs and
  validates against the authenticated original intake. The
  [bundle schema](../contracts/assessment-compact-bundle-2.schema.json) and
  [presentation schema](../contracts/assessment-intake-presentation-2.schema.json)
  match their runtime models.
- The [application service](../../apps/api/open_hollywood_api/services/assessment_compact_presentation.py)
  uses the existing registered probe collector and immutable publisher. It retains
  exact source receipts, rechecks source state around publication, enforces size
  and secret guards, and rejects unsafe paths or partial/changed/extra exports.
- The [operator CLI](../../scripts/assessment_compact_presentation.py) exposes only
  `prepare` and `verify`. It has no live, count, provider, credential, model-origin,
  trust-override, writer or repair option. Errors are summary-only.

Every current source/review document is visible in full as a structured object,
with original identity/version/content hash. Original messages remain byte-identical
strings. All six targets, 51 fields, four holds and 41 unselected fields retain
their original identities and dispositions; no source filtering or new claim
interpretation is introduced.

The registry view contains all original IDs in order, with explicit columns
`ref`, `document_id`, `field_pointer`. Its locations resolve into complete visible
source fields. Native reconstruction derives the original quote, Unicode character
offsets, field hash and document/version binding. Matching text at different
locations remains distinct. Paragraph/partial-field layouts and alternative source
serialization are refused rather than silently normalized or promoted.

Only the recognized `operator-provenance-not-visible-authority` scope document
body becomes local-only. Its original wrapper stays visible, and the full exact
body remains in `local-provenance.json`. Other scope documents are not silently
removed. Original registry validation already rejects evidence references into
that operator document. A new explicit availability notice makes clear that a
model cannot access the local archive or infer its contents from a hash.

The model view is named `native_work_view`: it is not a new native work. Reconstruction
must match the original work fingerprint and original version-one packet digest.
Acceptance additionally regenerates the entire candidate from the authenticated
intake. A self-consistent caller hash is not a root of trust. In particular, changing
and rehashing an output schema can pass local consistency but fails authenticated
context validation; that distinction has a regression test.

## Historical authority and N11

N11's five original authored fixture citations remain bound to visible authority:

| Reference | Original document | Original field |
| --- | --- | --- |
| E0943 | catalog-complete-current-draft | `/prose` |
| E0908 | visible-request | `/scene_assignment_contract/exit_state` |
| E0693 | visible-request | `/repair_acceptance_tests/0/claim` |
| E0694 | visible-request | `/repair_acceptance_tests/0/original_evidence/0` |
| E0695 | visible-request | `/repair_acceptance_tests/0/requested_change` |

The full visible historical allegation, recorded evidence and requested change are
therefore retained. Removing the separate operator archive from the model view
does not remove these fields. This is a location/visibility check; it does not
resolve whether every clause of the reviewer claim is true or adequately supported.
The scope and brief still distinguish historical assertion, requested change and
current fulfillment. No private archive statement is newly admitted as authority.

## Supported use and immutable output

```powershell
uv run --extra api python scripts/assessment_compact_presentation.py prepare `
  --intake PATH_TO_INTAKE_BUNDLE/review-01.json `
  --output data/exports/compact-presentation-001

uv run --extra api python scripts/assessment_compact_presentation.py verify `
  --intake PATH_TO_INTAKE_BUNDLE/review-01.json `
  --output data/exports/compact-presentation-001
```

The six-file, one-batch export contains exact `intake.json`, `source-receipt.json`,
`local-provenance.json`, `presentation-01.json`, a literal `view.md` and `manifest.json`.
Multi-batch work adds a presentation file for each original batch. The manifest
binds source, file digests, batch coverage and implementation identity, with state
`diagnostic_inputs_only`, zero live calls and writer permission false.

The archive and intake remain untouched. Exact prepare repeats verify and reuse
bytes without changing mtimes; verify regenerates expected files and does not
write them. Outputs must be outside source/intake trees. Changed sources, secrets,
linked/protected destinations, malformed or altered records and partial/extra
exports are refused. A failure before the final manifest can leave a partial
directory; it is retained and cannot be silently repaired or resumed.

## Verification

The two new test files cover source/context authentication, exact reconstruction,
unchanged schema and whole-work binding; rehashed source/version/ID/pointer/scope/
brief/message/schema tampering; missing provenance, duplicate keys, invalid roles,
oversized inputs, unsupported location/serialization layouts, secret refusal,
source drift, safe paths and immutable reuse. Existing native validation retains
Unicode, pointer and exact-offset rules. Tests and actual-work replay block provider
transport, network connections and SQLite; they never use the user database.

The combined relevant suite passes **488 tests** (**47 new**, 441 existing) in
325.16 seconds, with 56 existing mutation-fixture serializer warnings. It includes
the native source/scope/binding/completion contracts and existing OpenAI rehearsal
and smoke regressions. Existing asynchronous fixtures run outside the Windows
sandbox for event-loop support; provider transport stays mocked or blocked.
Ruff, formatting and strict mypy pass on **273 Python
files** (272 repository files plus one private actual-work helper). Both new schema
artifacts match runtime. No client/build check is required for this Python-only
read-only slice; no client or API route changed.

Private root: `data/diagnostics/assessment-compact-presentation-2026-11-14/`.
`verified/N06`, `N07`, `N10`, `N11` contain supported exports. `N*-qualification.json`
records the unchanged authored-final hashes, fresh presentation identities, native
bindings and completion. `actual-summary.json` records all four successes.
`verify_actual.py` uses the supported CLI with real registered source authentication;
no test registry override is used for these four works.

The native authored receipt fields retain null usage and zero synthetic elapsed
time. The qualification explicitly labels usage `not_applicable_no_inference`:
native unknown-usage counters are not observations of missing provider telemetry.
No live inference, new token count or semantic rescore occurred.

Preserve **1,372 earlier sealed members**, **636 selected archive source pins**,
the original smoke journal, all fourteen issue bodies and posted URLs, and all
**764 baseline files** outside four declared documentation updates. The old smoke
still has one count, zero generations and zero retries; its unused slots stay closed.
Final code/document snapshots, verification records and an acceptance seal preserve
this change. No previous fixture or delivery is relabeled.

## Next step

Qualify a **separate version-two OpenAI mapping/manifest path locally** using these
four exports and injected transport. Bind the exact new messages/schema to both
endpoint bodies and the original native work; preserve local provenance separately
and retain durable intent, terminal evidence, null usage and existing stop rules.
Do not make the version-one mapper accept arbitrary replacement presentations or
silently invalidate the old smoke's implementation pins.

Once that adapter is qualified, prepare a new smoke freeze for approval:
provisionally four counts and four generation attempts, no retries, Sol/high and
the same 272,000-input/32,000-output ceilings unless separately reviewed. Actual
counts must establish fit before generation. No live plan is frozen now, and byte
size is not permission to skip counting or raise the reservation.

Generation delivery, model use of the locator layout, factual support, evidence
adequacy, editorial judgment, edit necessity and story quality remain unqualified.
Preserving full prose and context keeps later human feel/flow/character review
possible. CW-007/CW-013 remain open; CW-014 unqualified. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; production prompts unchanged; live calls PAUSED; canary ON HOLD.**
