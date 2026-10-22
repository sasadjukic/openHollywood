# Gemma and DeepSeek C2 reviewer repeat: results

Date: **2026-10-21**. Status: **COMPLETED AND INSPECTED — 64/64 calls, no retries**.
Production remains **prompt 61 / graph 9 / fulfillment policy 1**. The full workflow
canary remains **ON HOLD**. Neither model clears the frozen diagnostic screen.

| Deployment | Calls | Valid | All frozen labels correct | Usable supported |
| --- | ---: | ---: | ---: | ---: |
| `gemma4:31b-cloud` | 32 | **0** | 0 valid assessments | **0** |
| `deepseek-v4.1-flash:cloud` | 32 | **32** | **24** | **22** |
| Total | **64** | **32** | **24** | **22** |

Gemma's zero is a delivery result, not evidence that every underlying judgment was
wrong. All 32 answers repeated a JSON key. DeepSeek delivered valid answers throughout,
but eight failed frozen labels and two more failed explanation support. Both completed
all scheduled cells normally; there were **zero truncated responses or terminal stops**.

## Scope, approval and inspection

The user approved the [frozen plan](../handoffs/reviewer-interface-repeat-frozen-plan-2026-10-21.md),
64-call ceiling and transmission of full unpublished prose/context to Ollama Cloud
through the local daemon. The preparation seal remains
`9246680ddc52832107f5e814a5cddb07c8b436932ab7f368ffb6a523b1a83142`.
The approval, discovery and subsequent execution are separate records; the frozen
plan's preparation-time “not run” status is preserved.

Eight pairs crossed two models, two seeds and two prose presentation orders. Four
historical packets were retained and four synthetic controls added three fresh settings:
**six scene families**, not 64 independent stories. Only h02 contains an actual saved
writer revision. There were no writer, correction, replacement, fallback or canary calls.

C2 combines application-owned binding, eight-reference evidence arrays, paragraph
groups, separate request relation/support/dependency labels and an endpoint judgment.
There is no simultaneous C1 arm. Neither historical rate comparisons nor this combined
change establish which individual interface choice caused a difference.

All 64 captures replayed. All 32 normalized answers were read in shuffled order with
model, seed and display order hidden. Per-review notes were persisted and hashed before
opening the identity key. All 32 invalid raw answers were then inspected separately,
retaining both duplicate-key occurrences. This was coordinator inspection with prior
source familiarity, not independent blind human quality review. No frozen score changed.

## Frozen screen and case coverage

The screen requires at least **28/32 valid**, **24/32 usable**, **3/4 usable on every
case**, invariant valid no-ops and no invented mandatory failure on valid permissible
controls. Passing would only permit consideration of further diagnostic evaluation.

DeepSeek passes delivery, all **8/8 valid no-op** invariance checks and all **16/16
valid permissible controls** without mandatory false alarms. It fails total usability
and coverage on h03, h04 and n03. Gemma fails delivery and usability; its valid-control
conditions are unobserved, not demonstrated passes.

| Case | Distinction | DeepSeek valid / label-correct / usable, out of four |
| --- | --- | ---: |
| h01 | Optional duplicate left in identical prose | 4 / 4 / **4** |
| h02 | Actual optional duplicate removal | 4 / 4 / **4** |
| h03 | Future date deleted; dependent callback cleanup | 4 / 0 / **0** |
| h04 | Truce retained; later departure violates endpoint | 4 / 4 / **2** |
| n01 | Requested optional phrase and article change | 4 / 4 / **4** |
| n02 | Decision retained; later completed match forbidden | 4 / 4 / **4** |
| n03 | Agreement replaced with refusal; physical endpoint retained | 4 / 0 / **0** |
| n04 | Clean unchanged prose with purposeful repeated warnings | 4 / 4 / **4** |

Gemma delivers **0/4 valid and usable on every case**. DeepSeek has **10/16 usable
historical** and **12/16 usable fresh** cells. These are conditional results on a small,
constructed corpus; neither subgroup estimates general reviewer reliability.

## Delivery: Gemma repeats the endpoint key

Every Gemma response contains two root `endpoint_check` keys. Strict parsing rejects
the response before semantic scoring. **29 pairs are identical; three differ in their
assessment wording**, although all three retain the same endpoint status and evidence.
Those three are h03/20261021/RO, h03/20261022/OR and h04/20261021/RO.

The supplied schema does not duplicate that property or its required-field name.
An offline audit parsed all 64 exact request schemas and checked **640 object schemas**:
required names are unique and match properties. The normal-stop captures show completed
answers, not truncation or a provider timeout. The observed failure is model-authored
duplicate-key delivery under this interface. The model's internal cause is unknown.
Reconciling schema property order, required-field order and a preferred answer sequence
is a plausible hypothesis to test; this run did not vary those factors.

Six Gemma cells also contain another independently visible structural defect:

- h01/20261021/OR corrupts the requested task reference.
- n04/20261021/OR, n04/20261021/RO and n04/20261022/RO omit required task evidence.
- h04/20261022/RO omits evidence for neutral voice on changed prose.
- n01/20261022/RO omits evidence for three neutral craft judgments on changed prose.

The relaxed empty-evidence rule applies only to uncertain craft or neutral craft on
identical prose; it does not apply to these fields. No duplicate key was dropped, no
answer was repaired and no invalid cell became a primary success. Reading raw answers
shows noticing worth preserving: Gemma generally identifies the optional edits, lost
agreement, retained earlier events and endpoint overruns. It also repeats the h03
endpoint attribution error below. Two n03 task explanations also blur which component
failed despite otherwise correct fact/endpoint fields: their compound wording could
mean the whole retention contract failed, rather than that each component was lost.
Raw noticing is not reliable report delivery.

**The evidence-cardinality failure did not recur here.** DeepSeek stayed within eight
references, reaching that bound; Gemma's raw arrays reached at most three. Neither model
returned excessive arrays, duplicate evidence references or unknown quotation references
in this run. That supports the bounded policy on these packets; it does not establish
an isolated causal improvement over C1 or validate every selected quotation's relevance.

## Judgment: what remains wrong, and what now works

**Missing event is still confused with final-state failure.** All four valid DeepSeek
h03 reports recognize the missing ten-year realization, retain Elena's handwriting-check
decision and acknowledge that she remains unsettled without a match. They nevertheless
mark the endpoint violated because the turning point is missing. The source endpoint
specifically references the outcome and exit state; deletion of the earlier event is
already a separate mandatory fact failure. Gemma's invalid h03 reports also make the
exit state's suspicion depend on that specific deleted cause. This is the converse of
the earlier error in which a bad ending supposedly erased a completed event.

**Request relation is still read as textual relevance.** All four DeepSeek n03 reports
and three h03 reports call an opposing edit `direct`. The frozen definition means
“does what the requested task asks.” Replacing a required agreement with refusal or
removing a required date does not carry out a retention task. Their explanations often
mean that the edit directly changes the relevant plot beat. Crucially, every one still
marks edit support **unsupported** and finds the real mandatory failure. These seven
label failures should not be described as seven endorsements of unnecessary rewrites.
The distinction is explicit now, but the word `direct` still invites another reading.

The conditional-cleanup distinction worked in all four valid h03 reports: G02 is
adjacent, unsupported and dependent on an unsupported change. Requested optional
duplicate and wording repairs are direct and supported without becoming mandatory.
The article/noun pair is assessed as one group. All four valid n03 reports identify
the missing agreement while preserving the physical endpoint. Whole groups avoided
the earlier isolated-token explanation on these cases; grouping does not itself prove
correct explanations or improved edit selection.

**Correct labels still acquire a false explanatory premise.** Both DeepSeek h04
reports shown revision-first (RO) call the added departure an internal factual
contradiction with the preceding statement that the characters remained in the room.
Remaining for a time and subsequently leaving are compatible events. The required
final state is violated, and abruptness or redundancy are defensible craft criticisms;
a direct internal contradiction is a stronger claim than the text warrants. Both
reports pass every frozen label and fail source-support inspection. The OR reports
do not make that claim and remain usable.

One n03 report has unresolved support for saying the replacement drops the original
bargain paragraph's “memory-weighing” texture: the memories are in the preceding,
unchanged paragraph. A broader aesthetic interpretation is possible, so this is
recorded as uncertain rather than a categorical literary error. It already fails
request relation, and resolving that uncertainty would not change the primary total.
Minor wording imprecisions and defensible aesthetic alternatives are retained in the
notes rather than automatically treated as consequential failures.

There are real strengths. DeepSeek preserves the truce in **4/4 h04** answers while
identifying the separate departure violation. It preserves the earlier decision in
**4/4 n02** answers without inventing a previously completed stamp comparison. All
valid no-ops remain ties with neutral craft effects. The clean museum control preserves
the two purposeful warnings, and the changed museum wording receives supported ties.

## Seed and presentation-order observations

| DeepSeek stratum | Valid / eight | All labels correct / eight | Usable / eight |
| --- | ---: | ---: | ---: |
| 20261021, OR | 8 | 6 | **6** |
| 20261021, RO | 8 | 6 | **5** |
| 20261022, OR | 8 | 6 | **6** |
| 20261022, RO | 8 | 6 | **5** |

Across 16 paired order contrasts, delivery is unchanged; one h03 relation label changes
without changing its failed overall label result. The two h04 contrasts change supported
usability, producing **12/16 OR versus 10/16 RO**. Across 16 paired seed contrasts,
one h03 relation label changes; no cell changes primary usability. Semantic-support
categories vary on one already-failed n03 cell as documented above.

Gemma is invalid in every seed/order stratum. Its valid semantic contrasts are therefore
unavailable; uniform rejection is not stable reasoning accuracy. Two seeds and one
affected historical scene cannot establish a general order effect. Cloud seeds are
request settings, and local manifest identity cannot prove fixed remote weights.

## Decision and recommended follow-up

Retain **DeepSeek/C2 as useful diagnostic evidence with a 22/32 limit**, not a screened
or production-qualified reviewer. Retain Gemma's captured delivery failures as local
fixtures, while preserving the earlier Gemma/C1 findings as their own historical result.
Do not choose a general model winner or promote a critic gate from this comparison.

Before proposing another live run:

1. Investigate delivery locally using all 32 duplicate-key captures. Exercise a single
   canonical response layout, exact-once fields, required evidence and task-ID binding.
   Examine constrained-output feasibility separately from prompt wording. Do not silently
   select a duplicate occurrence or present offline altered-contract handling as recovery.
2. Make the remaining semantic contrasts explicit in the evaluation design: an earlier
   fact versus the final state, carrying out a request versus merely touching its subject,
   and a forbidden transition versus logically contradictory events. Use counterexamples
   and both permissible and impermissible sequences, retaining original controls.
3. If those local checks justify more inference, propose a small isolated comparison
   with unchanged controls, fresh families and both presentation orders. Separate the
   delivery hypothesis from semantic changes, and predeclare a systemic-delivery stop
   rule to avoid spending a full matrix on one repeated malformed-output pattern.

These are recommendations, not prepared prompts or an approved new budget. The frozen
run correctly continued after captured invalid answers under its existing stop rules.
No further calls or production changes were made. Writer edit selection remains a
separate unprepared experiment.

Story quality still requires its own evidence. The user's nine human ties remain valid;
small edits are not demonstrated reader harm. Future human review should focus on
feel/emotion, flow, character and story-breaking details, with mechanics prepared by
machines. None of this scene-level diagnostic establishes better complete stories.

## Usage, verification and evidence

| Model | Calls | Input tokens | Output tokens | Historical-rate estimate |
| --- | ---: | ---: | ---: | ---: |
| Gemma | 32 | 309,044 | 28,200 | $0.05454616 |
| DeepSeek | 32 | 296,604 | 29,050 | $0.12384120 |
| Total | **64** | **605,648** | **57,250** | **$0.17838736** |

These estimates use the frozen October 20 reference rates without discounts, within
the $0.80 planning allowance. **Actual billed cost remains unknown.** Maximum input
was 15,006 tokens, output 1,244 tokens and active generation time 11.22 seconds per
call. Total active generation time was **252.79 seconds**; all explicit limits held.
Both manifests/capabilities matched at preflight and before every dispatch. The separate
initial preflight and per-cell metadata requests were discovery, not inference.

The preparation's **80 tests** remain its harness evidence. Post-run checks reverify
the frozen seal, all 64 requests/captures/receipts, masking-note integrity, complete
inspection coverage, aggregation, exact schema uniqueness and source bindings without
inference. Ruff lint/format and strict mypy cover the five new private helper scripts.
No production or frontend files changed; no application-wide build is claimed.

Local ignored evidence:

- [Approval](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21/approval.json)
  and [preflight](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21-live/preflight.json).
- [Aggregate results and paired contrasts](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21-live/analysis.json)
  and [per-cell index](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21-live/analysis-cells.json).
- [Masked inspection notes](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21-live/inspection/masked-notes.json),
  [notes seal](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21-live/inspection/masked-notes-seal.json),
  [all invalid occurrences](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21-live/inspection/invalid-raw-audit.json)
  and [additional raw observations](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21-live/inspection/invalid-raw-observations.json),
  with an [attribution caveat](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21-live/inspection/post-audit-clarifications.json)
  for the two ambiguous invalid n03 task explanations.
- [Verification and closure](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21-live/closure.json).

These local links expose no private bundle on GitHub. Public progress is recorded in
the [issue index](../../issues/README.md) and
[authoritative tracker](../../open_hollywood_bible/step_by_step_implementation.md).
No external issue was edited or closed. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**
