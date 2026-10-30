# Exact-copy display and production source-alignment audit

Date: **2026-10-30**. **COMPLETE — local audit and regression preservation.**
Inference and daemon calls: **zero**. Production **prompt 61 / graph 9 /
fulfillment policy 1** unchanged; live calls **PAUSED**, canary **ON HOLD**.

**The application can render an unambiguous statement about two explicitly
selected text spans without another model call. It cannot infer semantic
fulfillment or the appropriate comparison pair from equality.** The local
prototype establishes the first capability and preserves the second boundary.
It is an offline shadow implementation, not a production integration.

The production audit also identifies an occurrence-identity distinction:
versioned evidence handles distinguish repeated sentences, but resolving a
handle to quotation text alone does not retain that distinction. The full,
version-bound catalog and canonical prose can recover exact offsets locally.
A quote-only search must retain all matching occurrences instead of choosing
the first and claiming semantic alignment.

## Preserved evidence

Source: [PO/EX results](../benchmark_reports/reviewer-exactness-v61-results-2026-10-30.md).
Private bundle: `data/diagnostics/reviewer-copy-rendering-audit-v61-2026-10-30/`.
As with earlier diagnostics, `data/` is Git-ignored and remains local.

| Material | Count / bundle artifact |
| --- | --- |
| Byte-identical raw responses, original envelopes and opaque thinking | 32; `captures/<trial>/raw-response.json` |
| Raw and bound component assessments, source bindings, sealed notes and historical metrics | 224; `captured-regressions.json` |
| All PO/EX pairs with every component | 16; `po-ex-pairs.json` |
| N8 pairs in both orders, including the affected OR pair | 2; `n8-pairs.json` |
| Six fresh families in both orders and both arms | 12 pairs / 168 component regressions; `fresh-contrast-pairs.json` |
| Source-premise assessments retained inside target records | 96 |
| Ambiguous EX-N8-OR assertions | 2; `precision-regressions.json` |
| Unchanged complete scoring decision | `historical-decision.json` |
| Deterministic displays for all unique frozen text comparisons | 32; `rendered-comparisons.json`, `copy-display-samples.md` |
| Existing production rendering probes plus two new authored probes | 5; `production-rendering-probes.json`, `production-alignment-audit.json` |

The source documentation closure is
`6911157b16a79432b4227bb77f11f06ffa6972e67eecf70541ceb66f8ba657fb`.
Exact requests, full source packets, response bytes, sealed annotations and
production files are bound through **8,904 fingerprints** in `sources.json`.
Raw thinking is preserved opaquely and is not semantic evidence.

The historical outcome remains **retain limited evidence, no advancement**:
both arms have **112/112 semantically usable components, 48/48 grounded premises
and 16/16 source/event projection pairs**. Strict grounding remains **PO 112/112,
EX 110/112**, with two ambiguous assertions in **C-EX-N8-OR, C01.A01/A02**, no
definite literal errors, no matched precision recovery and no protected semantic
loss. These regressions do not turn ambiguity into a definite falsehood or erase
the model's original explanation.

## Application-rendered comparison statements

The prototype recomputes the receipt from its bound inventory and selections,
then requires the supplied receipt to match that recomputation exactly. A model
cannot supply the displayed equality status or free-form comparison wording.
The display retains both source roles, source IDs, artifact versions, field
pointers, full-text hashes, selected offsets/quotes and the receipt hash.

For each of N8's discovery and decision passages, the fixed statements are:

| Explicit pair | Deterministic statement |
| --- | --- |
| Original draft → revision | The selected text spans are identical character for character. |
| Assigned requirement → revision | The selected text spans differ. |

An unavailable source produces **“text identity is not determined,”** never a
negative equality result. Comparisons use exact Unicode code points without
normalizing whitespace, line endings, case, punctuation or Unicode composition.
The scope is always the selected spans, not the whole scene.

This resolves comparison scope in the **new application statement**. It does
not resolve what the historical model intended by “verbatim,” repair its raw
response, or change its strict score. The renderer emits no fulfillment verdict,
prose-repair recommendation or writer authorization.

The successful fresh contrasts remain important constraints:

- X1/X2 retain the assigned meaning through paraphrase or intentional action,
  despite different selected text.
- X3 copies the assignment sentence exactly into a fictional quotation; the
  actual protagonist does not make the decision.
- X4 places the decision with another person of the same name; X5 negates it.
- X6 narrates the actual decision and later reverses it. The decision event
  remains true while the sale separately violates the endpoint.

Neither exact copying nor differing text settles these semantic questions.
Selecting a pair remains an explicit input, not a capability supplied by the
renderer. Hashes detect inconsistent bindings under the trusted local-source
model; they do not establish truth or resist replacement of all source data and
all corresponding hashes.

## Production alignment findings

The first three probes replay the
[previous production-scope audit](reviewer-production-scope-audit-2026-10-28.md)
exactly: initial scene, final scene and a revision containing old/other-scene
drafts and prior critique. Two new authored fixtures exercise duplicate sentences
and whitespace/Unicode differences through the actual production renderer.
These are application tests, not new model observations or sampled live workflows.

| Surface | Observed behavior | Implication |
| --- | --- | --- |
| Current Scene Plan | Ten turning-point/outcome field projections across five probes match their canonical source values. | Exact obligation provenance is available; these values remain assignments, not observed story events. No assignment-to-draft semantic mapping is derived. |
| Current draft evidence | Eleven catalog excerpts across five probes replay against canonical prose and bind to exact code-point spans. Handles contain ordinal and draft-version identity. | A complete catalog replay can locate the selected occurrence; keep the generating code/version and source hashes with that operation. |
| Duplicate sentences | Two handles identify “The hatch closed.” at `[0,17)` and `[31,48)`. Each quote-only search returns both occurrences. Production resolution returns identical quotation strings for the two distinct handles. | Quote text alone is insufficient for occurrence identity. Preserve handles and offsets where a comparison needs a particular occurrence. This does not show that existing production critics misresolved these probes. |
| Whitespace and Unicode | Joining catalog excerpts does not reproduce the full canonical prose. Precomposed and decomposed accented text remain distinct. | Compare canonical text at explicit offsets; do not reconstruct a manuscript or normalize strings silently before an exact-copy claim. |
| Prior and other-scene drafts | The revision probe retains their version identities but omits their prose, with `repair_source_identity` and `identity_only_canon_in_story_bible` scope tags. | Available local canonical data and material visible to the reviewer are separate inventories. A later application comparison must not imply that the reviewer saw omitted prose. |
| Scoped Blueprint and prior critique | Rendered content differs while source-version identity persists. | Retain both canonical-content and rendered-view hashes; version identity alone does not prove view completeness or semantic authority. |

Relevant production boundaries are
[`_critic_evidence_catalog` and `_resolve_critic_evidence_refs`](../../apps/api/open_hollywood_api/services/production_model_executor.py),
[`compact_repair_inputs`](../../apps/api/open_hollywood_api/services/production_revision_acceptance.py),
and the [fulfillment projection](../../apps/api/open_hollywood_api/services/production_fulfillment.py).
The saved native audit/fulfillment handoff already preserves versioned handles
and assigned text. The quote-only resolver finding must not be generalized into
a claim that all production evidence loses its handles.

The new offset adapter requires the **entire** supplied catalog to match a fresh
replay from the exact canonical prose/version. It then follows catalog order and
checks that skipped gaps contain only whitespace. Reordered, omitted, duplicated,
changed or stale entries fail. A partial catalog does not acquire a guessed
offset. This is mechanical location recovery; it does not decide attribution,
negation, event truth, claim scope, necessary repair or literary value.

## Decisions and verification

Keep exact-copy display application-owned and explicitly separate from fallible
reviewer judgments. Preserve original model explanations and their diagnostics.
Do not add the EX receipt block to production prompts, infer fulfillment from a
match, or demand literal assignment wording from the writer. A differing receipt
is not itself a manuscript defect. Necessary craft edits remain possible inside
an already fulfilled passage, consistent with [ADR 0037](../adr/0037-durable-writer-fulfillment-handoff.md).

**143 offline tests pass: 78 audit checks plus the unchanged 65 execution checks.**
Ruff lint/format and strict mypy pass on seven local scripts. Tests block real
HTTP, replay historical scoring, preserve every capture and both orders, reject
receipt/catalog tampering, and exercise duplicate occurrence, unavailable-source,
Unicode, whitespace and semantic-versus-copying boundaries. All **8,904 historical
and production fingerprints** verify. No production/frontend code changed, so
unrelated application/build suites were not rerun.

The initial test run started before fixture construction had completed and found
37 missing-artifact failures. Construction also exposed tuple/list differences
after JSON serialization of occurrence offsets. The local representation was
corrected to JSON-native lists, the complete bundle was rebuilt, and verification
then passed. Both verification records remain preserved; no historical output,
score or production code was changed to obtain the pass.

The [next-step proposal](reviewer-copy-rendering-next-steps-2026-10-30.md) recommends
a bounded **local, zero-inference integration-design pass**, not another PO/EX
repeat. There is no remaining uncertainty requiring a model merely to determine
the literal comparisons or occurrence offsets demonstrated here.

Human review continues to assess feel, flow, character and story-breaking details
with machine-prepared mechanical evidence. These tests do not qualify story
quality, automatic claim extraction, general semantic alignment or a production
writer route. All fourteen issue bodies and posted links remain intact; no
external issue edited or closed. Blueprint approval and nine prior human ties
remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**
