# Four-work assessment payload and resource audit

Date: 2026-11-13

Status: bounded local audit and reversible representation study **COMPLETE**.
No live calls, credential access, prompt changes or new executable request plan.
Production prompts unchanged; live calls **PAUSED**; full workflow canary **ON HOLD**.

## Finding

The [stopped smoke](assessment-openai-four-work-smoke-results-2026-11-13.md) exposed
a concrete application presentation problem: the diagnostic renderer sends a large
operator archive and an expanded citation registry alongside the source material.
Together those two document bodies account for **85.4–90.9% of the user-message
bytes** in the four frozen packets. This is separate from the known model semantic
failures. It explains the packet's size; it does not assign a measured token cost
to each section or establish how a different layout affects assessment quality.

The local study preserves the exact original sources and reconstructs all four
packets, including **3,658 citation bindings**, byte for byte. A prospective view
that retains provenance locally and uses compact source locators measures
**208,265–220,934 bytes**, versus **1,076,455–1,800,180 bytes** for the original user
messages. Those are **80.45–87.73% byte reductions**, not measured token savings.
The views are private study artifacts, not provider requests or a qualified renderer.

## Scope and measurement method

Audit only N06/N07/N10/N11 from the immutable approved plan, SHA-256
`97f479ce20069c57649bf981a92c3b2724a9cd9a9ba811b2e9b419f0b7ae9eed`.
Read the exact count/generation bodies, presentation, native intake/source bindings,
response schema, scope declarations, briefs and the existing stopped journal.
Keep all six active claims, 51 fields, four holds and 41 unselected fields.

All byte counts are UTF-8. A document's user-message contribution is the exact
decrease obtained by replacing only its `content_json` string with an empty string
in an in-memory copy, using the original serializer. It includes that string's
embedded escaping, but excludes its retained identity/version wrapper. This is
measurement, not a proposal to delete that document. The document contributions
are disjoint. Wire bytes include the outer HTTP JSON serialization and are not
the same quantity as decoded message bytes or model tokens.

| Work | Count body bytes | Generation body bytes | User-message bytes | Registry contribution | Operator-provenance contribution |
| --- | ---: | ---: | ---: | ---: | ---: |
| N06 | 1,314,463 | 1,314,610 | 1,076,455 | 419,339 (38.96%) | 504,082 (46.83%) |
| N07 | 1,352,941 | 1,353,088 | 1,083,642 | 419,004 (38.67%) | 506,324 (46.72%) |
| N10 | 1,467,344 | 1,467,491 | 1,182,995 | 420,495 (35.54%) | 599,462 (50.67%) |
| N11 | 2,198,122 | 2,198,269 | 1,800,180 | 437,795 (24.32%) | 1,198,736 (66.59%) |

The new assessment system instruction is 1,709 bytes in each work. Compact JSON
sizes of the output schemas are 7,750 / 15,323 / 15,371 / 8,062 bytes. The schemas
repeat the evidence-ID enum for each active claim; they are not the main byte
contributor. No schema, enum, evidence cardinality or generation setting changed.

## Where the duplication comes from

### Operator archive included in model-visible context

`render_presentation` serializes `full_original_work`, including every context
document. The document named `operator-provenance-not-visible-authority` contains
both a projection and a saved snapshot. The snapshot carries captured attempts,
dependencies, manifests, proof records and a summary. N11 additionally contains a
parent snapshot: its compact JSON value alone is **399,396 bytes**. This is useful
local audit evidence, but copying the entire archive into the assessment message
is a separate choice from preserving it locally.

The operator document's raw source strings are **440,928 / 443,144 / 529,109 /
1,058,077 bytes**. Serialization into the message expands them further. None of
the current registry entries points to that document: all resolve to the original
visible request or catalog-complete current draft. The declarations retain
assignment/draft scope, plan availability for N07/N10 and historical-critic-assertion
scope for N11. A provenance label must not promote an archive record into visible
historical authority, and local retention must not hide any genuinely required
authority in a future implementation.

### Registry repeats mechanically recoverable source data

The intake builder walks **every nonempty string field** in the two source
documents. It creates **904 / 904 / 907 / 943 entries**. All entries in this audited
set designate a complete field: start zero, end equal to its character length,
paragraph null. Each repeats document ID/version/hash, field pointer/hash, full
quote and offsets. There are no paragraph-only entries in these four packets.

| Work | Old output-schema fields | Repair-source-catalog fields | Current-draft field | Total registered fields |
| --- | ---: | ---: | ---: | ---: |
| N06 | 311 | 205 | 1 | 904 |
| N07 | 311 | 205 | 1 | 904 |
| N10 | 312 | 205 | 1 | 907 |
| N11 | 344 | 205 | 1 | 943 |

These counts describe citation locations, not assessment targets or judgments of
relevance. The historical request's output schema is itself source context; this
audit does **not** filter its locations or change which references are admissible.
The repeated document-hash and field-hash JSON values alone occupy **119,328–124,476
bytes** per registry before their keys and surrounding/nested JSON escaping.
For complete-field citations, these values and quotes can be derived exactly from
the bound original document and pointer. Equal wording at two locations must still
remain two distinct bindings.

### Multiple serializations, not just indentation

Each context document embeds JSON as a string inside a larger packet. That packet
is then a string inside the endpoint body. Operator snapshots also embed their own
captured JSON text. Outer wire escaping of the user message adds **204,715 / 205,127 /
219,979 / 363,362 bytes**. This is transport overhead; it must not be described as
an equal number of model input bytes or tokens after decoding.

Simply compacting the existing top-level user JSON saves only **4,108–6,377 bytes**
(less than 0.6%). It leaves most embedded serialization untouched. The original
critic user message and `visible-request` document are also **equal as parsed JSON
in all four cases**, though their exact serialized strings differ. The original
messages remain untouched in both studies; eliminating that second representation
would need an explicit message-role/visibility reconstruction contract.

## Reversible local studies

Both studies use parsed document objects instead of JSON-in-JSON strings. The
registry becomes a source-binding table and ordered rows of unchanged reference
ID, source index and field pointer. The source table retains original identity,
version and content hash. Reconstruction derives exact full-field quote, hash,
offsets and paragraph null, then compares the complete original registry digest.
No story text, original message, whole-review field, claim, declaration, brief,
hold, unselected field or allowed evidence ID is dropped.

| Work | Original user bytes | All context retained, compact view | Provenance retained locally, compact view |
| --- | ---: | ---: | ---: |
| N06 | 1,076,455 | 647,999 | 208,265 |
| N07 | 1,083,642 | 653,694 | 211,896 |
| N10 | 1,182,995 | 743,907 | 216,184 |
| N11 | 1,800,180 | 1,277,475 | 220,934 |

The first study retains all operator contents in the view and reduces bytes by
**29.04–39.80%**. The second replaces only that provenance document body with a
bound local reference and retains its **exact original bytes** in the local study
bundle. Reconstructing the original packet requires that bundle. The model would
not automatically have access to locally retained provenance.

The second study's pretty-printed views are 325,452 / 330,496 / 336,034 / 344,226
bytes; the compact figures therefore include a formatting choice for the new
structured tables. No new system instruction or endpoint body is frozen. Any
eventual source-locator explanation will add to the final presentation size.

All eight study variants reconstruct the original packet bytes and pass native
work/scope/registry validation after reconstruction. Original source, version,
work, declaration, brief and citation identities remain the authority. The study
view itself is **not** an `AssessmentWork` or an existing request: native identity
must remain separate from a new presentation identity.

This proves **lossless local reconstruction and source binding**, not semantic
equivalence, human readability, model usability, lower latency, lower charges or
successful generation. Locators are not complete evidence by themselves. A future
renderer must expose the entire bound source text and an unambiguous route from
each ID to that text, without asking a model to retrieve private local files.

## Resource accounting and limits

Only N06 has an observed provider count: **350,749 tokens**, above the unchanged
272,000-input cap. N07/N10/N11 and both studies have **unknown token counts**.
Do not estimate them by applying N06's token/byte ratio to different structures.
The 32,000-output cap, prior $1-per-work conservative generation reservation and
stops are unchanged historical plan settings, not a new authorization. There are
still **one prior count, zero generation attempts and zero retries** in the closed
smoke. This audit adds zero calls. Actual billed cost remains unknown.

The six preparation files per work occupy **13,866,512 / 14,148,230 / 15,350,309 /
23,331,954 bytes** locally. These include full native intake, request-set snapshots
and literal Markdown views. They are not additional model payload or billed input.
This audit preserves them rather than optimizing or deleting historical evidence.

A single instrumented local parse/factor/reconstruct pass took **1.98–2.22 seconds**
per work with **17.52–28.82 MB** of peak traced Python allocations. This is a narrow
helper profile with tracing enabled, not process RSS, native source-authentication
latency, a production benchmark or an API measurement. No generation latency or
reasoning-token result exists from the smoke.

## Verification and preservation

Private root: `data/diagnostics/assessment-payload-audit-2026-11-13/`.

- `measurements.json`: exact body/message/document measurements, source pins,
  registry groups, byte contributions and all eight study outcomes.
- `studies/`: eight non-dispatchable local bundles. `provider_request` is false;
  semantic equivalence is explicitly unassessed.
- `audit_payloads.py`: repeatable local audit, exact reconstruction and native scope
  validation. Outputs refuse changed reuse; original inputs are never rewritten.
- `test_audit_payloads.py`: **30 passing local tests**. Eight actual-work round trips;
  sixteen source/version/digest/location/ID/provenance/scope/brief/disposition/message
  tampering checks; five refusal cases for unqualified registry/serialization forms;
  Unicode, escaped pointers and identical text at distinct locations. Network sockets
  and SQLite access are blocked in these tests.
- `resource-profile.json`: bounded local timing/allocation profile and full intake
  disposition counts; network/database access blocked.

The supported smoke `verify` command passed for all four original preparations
with **zero calls**. The audit repeated with identical outputs. Ruff and formatting
pass; strict mypy passes on **269 files** (267 repository files plus two private
helpers). Runtime code, production tests, prompts, schemas, source declarations and
frozen endpoint bodies are unchanged. The earlier runtime test results remain
historical evidence; this audit does not claim a fresh full production test run.

Preserve **1,346 earlier sealed members**, **636 selected archive source pins**,
the original live journal, **764 of 767 baseline files** outside three declared
documentation updates, all fourteen issue bodies and posted URLs. Private snapshots,
verification records and the new audit seal preserve this handoff. No old delivery
is relabeled and no claim receives a semantic rescore.

## Recommended next step

Implement and qualify a **separately versioned source-bound diagnostic presentation**
in the tracked read-only assessment component, using the locally retained provenance
variant as the candidate. Extend the accepted full-context presentation contract
explicitly; do not overwrite ADR 0051, existing packets or native work identities.

1. Keep the complete source/request/review texts and original messages visible,
   with all original field dispositions, scope and briefs. Keep the entire operator
   archive locally, referenced by exact source identity/hash. Audit historical
   visibility explicitly, especially N11; do not move required story authority out
   of the model view merely because it appears in a provenance container.
2. Render all original citation IDs as readable source locations and derive their
   exact quotes/hashes/offsets application-side. Qualify whole-field behavior first;
   refuse unsupported paragraph layouts rather than silently converting them.
   Prove exact round trips, complete native binding and failure behavior for all
   four works. Do not alter evidence limits, claims, gold or production prompts.
3. After local qualification, freeze a new count-gated smoke for approval:
   provisionally four counts and four generation attempts, no retries, Sol/high,
   unchanged 272,000-input/32,000-output ceilings and the same strict stop policy.
   Freeze the actual new instruction/schema/body sizes and reviewed resource policy.
   Only actual approved counts can establish fit; any over-cap count stops generation.
   The old closed plan and its unused slots stay closed.

No live plan is prepared or authorized by this audit. First establish reliable,
bounded factual assessment delivery. Editorial judgment, edit necessity and story
quality remain separate: preserve the prose and context needed for later human
feel/flow/character review rather than shortening a story to fit serialization
overhead. CW-007/CW-013 remain open; CW-014 unqualified. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**
