# Frozen NC/ES evidence-status comparison — 2026-10-26

**PREPARED LOCALLY; AWAITING SEPARATE LIVE APPROVAL. 0/28 inference calls used.**
Production **prompt 61 / graph 9 / fulfillment policy 1** is unchanged. The full
workflow canary remains **ON HOLD**. This plan does not authorize inference.

This implements the [28-call proposal](reviewer-epistemic-status-proposal-2026-10-26.md)
following the [citation/relation/uncertainty audit](reviewer-citation-relation-uncertainty-audit-2026-10-26.md).
The question is whether explicit evidence-status categories improve judgments of
the complete relation proposition while preserving actual contradictions,
unresolved evidence, assignment checks and defensible craft readings.

## Frozen comparison and scope decision

**NC** retains the existing control instructions, three-label component judgments,
source-bound O/R/C evidence registry, complete component delivery, eight-reference
whole-claim union and 2,000-character summed whole-claim reason limit. Context
references share that eight-reference allowance with prose references.

**ES** changes only the designated factual relation component's judgment vocabulary
and adds its explanatory contract to the final diagnostic instruction. It must
return exactly one of:

| Raw target status | Meaning | Application projection |
| --- | --- | --- |
| `established_true` | The source establishes the complete proposition, including its relation | supported |
| `established_false` | The source establishes that the complete proposition is false | unsupported |
| `unestablished` | Neither proposition nor negation is established; no explicit unresolved alternative | uncertain |
| `explicitly_unresolved` | The source explicitly leaves the relevant alternatives unresolved | uncertain |

The relation proposition, other component propositions, source/context, registry,
model settings and limits match between arms. All other components retain NC's
three-label contract, including its qualified craft standard. ES changes the final
user instruction/schema only; it does not receive selected witnesses, expected
answers, gold statuses or a weaker relation proposition. This tests the status
vocabulary **plus its explanatory instructions**, not an enum in isolation.

**Preparation clarification:** only the designated component has four-status
semantics. Its status is projected before the existing three-label whole-claim
conjunction. We do not reinterpret legacy non-target `unsupported` as established
falsity or silently give the entire report four-status truth semantics. The
application derives the designated proposition's complement status locally;
unknown stays unknown. Whole-conjunction/whole-negation behavior is checked on
authored four-status fixtures offline, not claimed for mixed-contract live
reports. No complement is another observation or a test of model response to
negation. This resolves the proposal's scope ambiguity before inference.

## Cases, claims and schedule

**Seven full-scene families × two presentation orders × two arms = 28 attempts**,
fourteen per arm. OR presents original then revision; RO reverses presentation,
while O/R identities and artifact versions stay fixed.

| Family | Relation under test | Target component | Withheld expected ES status | Source status |
| --- | --- | --- | --- | --- |
| H: observatory, Sol | Acting before consultation versus not yet having consulted; separate real rule/resolve breach | C01.A04 | established_false | Packet, claims and map unchanged; both NC wire payloads exactly preserved |
| U: greenhouse, Maren | Unauthorized action versus authorization not yet received | C02.A02 | established_false | Packet, claims and prior map unchanged; new NC assembly |
| X: foundry, Ida | Same door open and shut at the same instant | C02.A01 | established_true | Packet/claims unchanged; newly authored component map |
| Y: negative archive, Lio | Lit/dark photographs whose common timing is explicitly unresolved | C02.A01 | explicitly_unresolved | Packet/claims unchanged; newly authored component map |
| F1: pottery, Tessa | Dark bench at six and lit bench fifteen minutes later | C02.A01 | established_false | New complete scene pair; 279-word original |
| F2: railway parcel office, Ruben | Same pane intact and shattered at the exact same instant | C02.A01 | established_true | New complete scene pair; 266-word original |
| F3: reservoir records, Mira | Open/closed shutter observations with explicitly unresolvable timing | C02.A01 | explicitly_unresolved | New complete scene pair; 275-word original |

These expected statuses are withheld from model messages. Each fresh family also
has a real assignment violation and a defensible, qualified craft control. F1
retains a breakfast question while moving the cup off its assigned bench. F2
retains an investigation decision while opening an envelope meant to stay sealed
in a locked drawer. F3 retains a family inquiry while breaking a survey packet's
required seal. Their authored purposes are distinct from human story preference.

Frozen totals: **21 unique whole claims and 49 unique material components**. Across
both orders, each arm has **42 whole-claim opportunities, 98 component
opportunities, 14 designated targets and 84 non-target components**. There are no
secondary exclusions. The previous B/C03 citation-budget case is not in this
semantic comparison; its rejection and unresolved allowance policy remain intact.

Exact fixed order, grouped into adjacent paired cells:

| Calls | Family/order | Arm sequence |
| --- | --- | --- |
| 1–2 | H/OR | NC, ES |
| 3–4 | U/OR | ES, NC |
| 5–6 | U/RO | ES, NC |
| 7–8 | H/RO | NC, ES |
| 9–10 | X/OR | NC, ES |
| 11–12 | Y/OR | ES, NC |
| 13–14 | F1/OR | NC, ES |
| 15–16 | F2/OR | ES, NC |
| 17–18 | F3/OR | NC, ES |
| 19–20 | F3/RO | ES, NC |
| 21–22 | F2/RO | NC, ES |
| 23–24 | F1/RO | ES, NC |
| 25–26 | Y/RO | NC, ES |
| 27–28 | X/RO | ES, NC |

Only H has historical NC request equivalence; reused source material in U/X/Y
does not make those newly assembled requests historical controls. Both arms
receive an authored decomposition, limiting inference about unconstrained review.

## Scoring and retention screen

Reject malformed, duplicate-key, extra-field, incomplete, misidentified,
wrong-namespace or over-budget reports in full. No repair, trimming, partial
salvage or replacement. Schema-valid evidence is not automatically relevant or
sufficient; all valid reports receive complete source inspection.

Report valid delivery, raw target status, projected target label, exact status
correctness, whole/component labels, reasoning truth, citation support, material
coverage and usability separately. A usable ES target requires valid full-report
delivery, the exact expected status, correct projection, correct proposition scope
and grounded complete reasons/citations. A correct whole label cannot conceal a
wrong material component. Whole-claim usability additionally requires all its
components to be correct and all material parts explained.

Retain an **evidence-status diagnostic signal only** if all conditions hold:

1. Complete all 28 attempts. ES delivers at least **12/14** valid reports,
   including **all six fresh responses**, without losing any paired valid NC
   delivery.
2. Valid contemporary NC falsely supports the H/U target in at least **three of
   four cells**, spanning both families and both orders in at least one family.
   ES supplies grounded correct targets in at least three such cells with the
   same spread. NC abstentions and invalid reports are not recovery opportunities.
3. ES correctly handles **both orders of X and Y and all six fresh targets**.
   Y/F3 require `explicitly_unresolved`; `unestablished` has the correct projected
   label but fails this exact-status control. Inventing either timing alternative
   also fails source grounding.
4. Preserve every paired usable non-target component and whole claim, supported
   requirement/craft label, and grounded complete reason/citation assessment.
   Record losses even when there are too few recovery opportunities.

Insufficient recovery opportunity is inconclusive without extra calls. Independent
losses still produce limited evidence/no advancement. Early stops cannot qualify.
NC's `unsupported` on Y/F3 retains a separate unestablished-versus-uncertain
interpretation annotation; it earns no primary credit but is not automatically a
false timing assertion. H/U, not this label ambiguity, determines recovery.

Shuffle complete source-inspection exports, mask trial/arm/order IDs and seal
notes before decoding the key. Response vocabulary and familiar cases may reveal
the arm, so disclose partial masking. This is assistant factual adjudication,
not blind human preference evidence. Citation exactness and accounting are
machine-checked; semantic support and completeness still require source review.

## Budget, model and stop rules

- **28 maximum attempts, 14 per arm, one attempt per scheduled cell, zero retries.**
  No extra probes, replacements, reallocation or expansion for inconclusive data.
- Per attempt: **24,000 input tokens, 8,000 output tokens, 300 active seconds**.
  Aggregate reservation: **672,000 input / 224,000 output / 8,400 active seconds**.
- Archived reference-rate arithmetic: **$0.01680 per attempt / $0.47040 total**;
  **$0.60 planning allowance**. These are not verified billing caps; actual billed
  cost remains unknown. No new pricing assertion is made.
- `deepseek-v4.1-flash:cloud` through `http://127.0.0.1:11434`, which routes the
  approved full fictional prose/context to Ollama Cloud after separate approval.
  Temperature **0.2**, top-p **0.95**, seed **20261022**, context **32,000**,
  thinking **false**, streaming **false**, no format override.
- At eight completed H/U calls, stop the entire comparison if either arm has
  **zero of four valid reports**, or ES repeats the same blocking structural
  signature in both families. There is no other pilot to receive unused calls.
- A non-200 response, provider error, truncation/non-stop finish, missing/excess
  usage, elapsed-time breach, daemon/model drift, tampering, cancellation or
  ambiguous dispatch is terminal. Preserve raw response/version observations,
  gateway error chain and unknown usage. No restart after a terminal stop.
- A clean, deliberately paused cell boundary may continue only the remaining
  original schedule. Completed cells are never replayed; pending/ambiguous cells
  do not qualify for automatic continuation. Exclusive operator lock and durable
  reservations prevent concurrent or duplicate dispatch.

Metadata-only capture on **2026-10-26** confirms daemon **0.40.11** and unchanged
selected model tag/show metadata, digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
Three successful metadata responses—version, tags and show—are preserved with
request/response hashes. An initial sandbox connection failure is also retained;
it is not provider or inference evidence. Execution must recapture matching
metadata before generation and preserve before/after version observations.
Current successful discovery does not guarantee future availability.

## Frozen artifacts and verification

Private ignored bundle:
[`data/diagnostics/reviewer-evidence-status-v61-2026-10-26/`](../../data/diagnostics/reviewer-evidence-status-v61-2026-10-26/).
It contains the complete casebook; immutable source/context versions; 21 claims;
49 component propositions; withheld gold; registries; 28 exact prepared and wire
requests; response schemas; schedule; scoring and stops; budget; current metadata;
offline examples and witness-budget audit; runner, inspection/scoring code and
tests. Gold and authored examples are excluded from model input.

All authored example unions fit the unchanged limit (maximum **six refs**); this
shows representability, not likely model compliance. Prompt-size estimates are
**6,808–8,882 quarter-byte tokens**, not tokenizer counts; actual usage is checked
against the reserved ceiling. The plan seals its files and this public document,
and verifies **3,110 historical source fingerprints** without changing old evidence.

Verification: **336 offline tests pass**—152 new harness checks plus 128 local
audit regressions and 56 prior execution regressions. Ruff lint/format and strict
mypy pass on ten new scripts. Tests exercise all 28 adapter requests via mocked
HTTP, status/projection scope, both unknown categories, citation/whole-claim
limits, protected losses, recovery spread, sentinels, clean-boundary continuation,
terminal audit/export, unknown usage, drift, evidence tampering and approval
binding. Real HTTP transports are blocked during tests. Windows event-loop
permissions were needed for mocked asynchronous execution. No production code,
API or frontend changed, so application builds are outside this change's scope.
UTF-8/LF, local links and `git diff --check` are verified. An optional Markdown
Prettier invocation was unavailable because Corepack could not download the
pinned pnpm package; no dependency or package-manager version was changed.

There is **no live approval file and no live run directory**. The operator notes
provide verification, future plan-bound execution, terminal export and source
inspection commands. Separate approval must cover this frozen plan, its 28-call
ceiling, full prose/context and Ollama Cloud via the local daemon.

## Story quality and next decision

This comparison tests evidence judgments, not improved fiction. Supported craft
controls remain protected; abstaining on a defensible emotional reading is not
credited as safer or better storytelling. Ambiguity intentionally left by a scene
must not be forced into an invented fact. The nine prior human ties remain
unchanged. Future human review should focus on feel/emotion, flow, character and
story-breaking details, supported by machine-prepared mechanics.

After a separately approved run, inspect every valid report, document invalid and
terminal evidence, apply these frozen screens and update the tracker. A positive
screen retains diagnostic evidence only; it does not promote ES, authorize writer
edits or start the canary. If the treatment repeats the relation failures, require
a materially different hypothesis before further inference. Provider attribution
remains deferred; the separate citation-allowance question remains local work.
