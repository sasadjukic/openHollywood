# Frozen D2/premise-check reviewer comparison

Date: 2026-10-24. **PREPARED LOCALLY; AWAITING LIVE APPROVAL.**
No inference, model discovery or daemon preflight occurred during preparation.
Production remains **prompt 61 / graph 9 / fulfillment policy 1**. Live calls
remain **PAUSED** and the full workflow canary remains **ON HOLD**.

This freezes the [selected proposal](reviewer-premise-comparison-proposal-2026-10-24.md)
after the [extra-field and premise audit](reviewer-field-premise-audit-2026-10-24.md).
The preceding [C2/D1/D2 results](../benchmark_reports/reviewer-layout-v61-results-2026-10-23.md)
remain unchanged. D2 is an **unqualified diagnostic baseline**, not a production
candidate established as better than C2. This comparison contains no concurrent
C2 arm, writer calls, structural correction or workflow canary.

## Question and arms

Can one general premise-check card improve factual support throughout a review
without losing delivery, supported judgments, legitimate criticism or optional
repair recognition?

| Arm | Frozen difference | Attempts |
| --- | --- | ---: |
| D2 | Archived identity-first D2 renderer, instructions and closed schema | 16 |
| PC | Same D2 request with the fixed card below, immediately before the unchanged output schema | 16 |

The complete source/context, version IDs, evidence catalogs, paragraph edit
groups, schema, model and sampling settings are identical within each pair.
The card has no case IDs, answer quotes, gold labels, selected passages or
outcome-dependent hints. No M1 ownership card, output field, reasoning trace,
judge call, schema relaxation or temperature change is introduced. This tests
the instruction package; it does not isolate the wording from added length or
attention. The new card exists only in this private diagnostic preparation.

Exact card, including its substantive instructions:

```text
PREMISE CHECK
Before returning the required JSON, check the factual premises of each assessment
against the complete original, revision and assignment. Distinguish an event
present in the prose from an assignment restriction: a forbidden event may still
happen in the revision. Apply temporal conditions to the action they actually
qualify; do not extend a condition about one action to every intervening action.
Check whether an independent motivation remains before calling a decision
unmotivated; also recognize when the text explicitly makes one cause necessary
or sole and that cause has been removed. Distinguish identical assertions from
incompatible assertions about the same entity and time, and recognize supported
removal of an accidental exact duplicate. Neither these distinctions nor a
small edit prescribe a literary winner. Allow qualified literary interpretations
and honest uncertainty; do not present an unestablished premise as a textual
fact. Keep the existing output fields and evidence rules. Return only the
required assessment JSON, without an additional reasoning trace or new fields.
```

## Cases and execution order

**Eight pairs × two arms × two presentation orders = 32 attempts.** Each case
belongs to a different scene family. These are eight family clusters, not 32
independent stories. All prose is synthetic diagnostic fiction, 270–327
whitespace-delimited words per version. The four fresh scenes are conceptual
counterexamples, not minimal causal pairs with the historical scenes.

| Case | Family and withheld inspection contrast |
| --- | --- |
| A00, unchanged | Community radio: recognition is removed; an unidentified voice is not established; broadcast violates the separate endpoint. A deferred question is not itself a general prohibition. |
| B10, unchanged | Costume workroom: consultation before **explaining** does not mean consultation before every action; seam alteration violates the independent physical endpoint. Duplicate cleanup succeeds. |
| E-compound, unchanged | Flood footbridge: the split is removed, but routine inspection independently motivates the carpenter appointment. The chain endpoint fails; duplicate cleanup succeeds. |
| F-narrow, unchanged | Bakery: two incompatible counts describe the same crate at the same instant. They are not identical assertions. The genuine craft contradiction falls outside the narrow retention task. |
| G-voice, new | Ferry terminal: an unidentified voice really is heard and the question is retained; admitting a passenger violates the locked-gate endpoint. Event fulfillment and boundary failure must coexist. |
| H-before, new | Hilltop observatory: consultation explicitly must precede telescope rotation, and the revision rotates before consultation. Discovery, decision and closed roof survive; the separate mandatory consultation rule fails. |
| I-cause, new | Plant nursery: the original explicitly makes a cracked pane the sole reason for a glazier visit. The revision removes that cause and supplies no independent motivation, while keeping the decision. Criticism of that causal gap is supported; duplicate cleanup independently succeeds. |
| J-duplicate, new | Map archive: an accidental adjacent exact duplicate is correctly removed. Recognition, decision and physical endpoint survive. No incompatible state is introduced. |

Historical packets and both D2 wire requests per historical case are
**byte-for-byte unchanged**. Fresh packets retain the same source/version/offset
catalog and paragraph-group construction. Task acceptance, event retention,
endpoint, mandatory scope, allowed group labels and inspection anchors are
frozen separately from model inputs. The casebook contains complete original
and revision prose; withheld expectations are not sent to the model.

Case order is **B10, H-before, A00, G-voice, E-compound, I-cause, F-narrow,
J-duplicate**. Each case has both OR and RO presentation. Starting presentation
order alternates by case; arm order reverses between the two presentations and
alternates by case. Each arm goes first eight times. Execute the saved schedule
serially; do not reorder based on outputs.

The first **eight calls**, B10 and H-before, are the delivery sentinel: four per
arm across two families and both orders. No semantic inspection or favorable
early result changes the remaining schedule.

## Model and budget

| Setting | Frozen value |
| --- | --- |
| Model | `deepseek-v4.1-flash:cloud` |
| Destination, only after approval | Ollama Cloud through local daemon `http://127.0.0.1:11434` |
| Payload | Full unpublished original/revision prose, assignment and diagnostic context |
| Expected daemon | **0.40.9**, last verified in the completed October 23 comparison; not rediscovered today |
| Model digest | `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8` |
| Sampling | Temperature 0.2; top-p 0.95; seed 20261022 |
| Thinking / streaming | Both false |
| Per call | At most 24,000 input tokens, 8,000 output tokens, 32,000 context tokens, 300 active seconds |
| Total / per arm | **32 / 16 attempts**, one attempt per cell, **zero retries** |
| Aggregate reservations | 768,000 input tokens; 256,000 output tokens; 9,600 active seconds |
| Reference cost reservation | **$0.53760**, within a **$0.75 planning allowance** |

Cost uses the archived reference rates of $0.30 input / $1.20 output per million,
without discounts. It is not a current price assertion or a verified bill;
actual billed cost remains unknown and a dollar billing cap is not enforceable
through this adapter. Call, token and active-time ceilings remain enforced.
The frozen UTF-8-byte/4 input estimates range from **5,380 to 6,500**; they are
planning estimates, not tokenizer measurements or substitutes for recorded usage.

The selected model's archived capabilities, digest and thinking settings, runtime
versions and source fingerprints are pinned. A changed daemon/model/capability
baseline requires stopping and reviewing the plan, not silently refreshing it.

## Stops, accounting and recovery

The first-eight sentinel stops the whole comparison if either arm has **zero
valid reports**, or if the same normalized structural failure signature occurs
in **at least three of that arm's four cells across both sentinel families**.
The archived path-normalizing signature classifier is unchanged.

A complete HTTP-200 normal-stop response with invalid JSON, duplicate keys,
extra fields, wrong records or invalid evidence is an `invalid_stop`: count the
attempt, retain it rejected, and proceed only if no sentinel/terminal stop applies.
There is no repair, replacement, retry or transfer of unused budget between arms.

Stop the entire run on non-200 status, transport failure, timeout, cancellation,
length or incomplete finish, missing/excessive usage, unexpected thinking,
identity/version drift, source/request tampering, unresolved reservation or
accounting inconsistency. Preserve the gateway error chain, partial capture,
reserved/dispatched counts and **unknown usage**; never replace unknown usage
with zero. A terminal stop cannot resume under this plan.

The operator checks approval and seals before discovery, acquires an exclusive
lock, reserves each attempt before dispatch, checks the exact wire payload and
seals each complete cell. A clean stop at a completed cell boundary can restart
without repeating cells or exceeding the ceiling. A completed or sentinel-stopped
ledger makes no further discovery or inference calls. No old experiment's
approval or spare calls authorize this comparison.

## Frozen scoring and decision

Strict validation is unchanged: unique-key closed JSON, exact ordered records,
all required assessments and supported evidence references bound by the
application to exact source versions/offsets. Extra `effect_note` fields remain
invalid. A structurally valid report is not necessarily a true or usable report.

Export all complete reports into a shuffled inspection packet hiding arm/order
metadata. Wording may reveal condition; this is a masked operator factual audit,
not a new blind human literary rating. Inspect **every assessment field** against
the complete source and assignment, record exact source/version/offset quotes,
and seal notes before decoding the key. The code checks supplied adjudications
and their bindings; it is not an automatic semantic truth detector.

Score delivery, supported task/fact/endpoint/mandatory judgments, group labels,
supported optional-edit success and actual contradiction detection separately.
For F-narrow, contradiction recognition must be supported by both incompatible
assertions. A negative craft rating alone is insufficient. The application-owned
mandatory aggregate stays a separate diagnostic view; it cannot repair the
model's flag, a false task judgment or an unsupported explanation.

Full usability additionally requires correct scored labels and supported claims
in **every** assessment field, including craft and the overall comparison.
Unsupported and uncertain claims stay distinct; neither counts as supported.
Qualified literary interpretations remain legitimate when grounded. There is no
gold literary winner or reward for the fewest changed words.

Each unsupported field also receives a secondary classification:

- `decision_relevant_invented_constraint_or_event`: a fabricated restriction,
  event, causal premise or factual relationship materially used to justify a judgment.
- `narrow_wording_inaccuracy`: a local factual wording error without that broader
  decision premise. If a field contains both, use the decision-relevant category.

Both classes still fail primary full-support scoring. Supported/uncertain fields
have no unsupported classification. This breakdown does not rescore history.
Fresh counterexample inspection also flags a blanket false rejection, such as
denying a genuinely stated condition or condemning the supported duplicate
cleanup; it must bind to an unsupported field.

Retain PC as promising diagnostic evidence only if all of the following hold:

1. All **32** planned cells complete, with PC delivering **at least 15/16 valid**
   reports, including **at least 7/8 fresh reports**.
2. At least **three paired semantic recoveries**, across at least **two families**,
   including **one historical case recovered in both presentation orders**.
   A semantic recovery requires a **valid D2 report with an unsupported explanatory
   field** and a paired **valid, fully usable PC report**. An uncertain-only D2
   report is not an eligible premise failure. An invalid D2 report recovered by PC
   is recorded separately as a delivery-only gain and earns no semantic credit.
3. No paired loss of any valid D2 report, fully usable report, supported target,
   detected genuine contradiction or supported optional repair. No new blanket
   false rejection on a fresh counterexample relative to D2.

The opportunity check uses the concurrent D2 failures, not historical outcomes.
If their count, family coverage or historical both-order coverage cannot support
the required recoveries, report **`insufficient_recovery_opportunity`** with the
absolute metrics and regressions. Do not lower thresholds, add calls or call a
ceiling-effect repeat proof of benefit or proof of no benefit.

Decision precedence is explicit: an incomplete run is
`incomplete_no_advancement`; an independent delivery-floor failure or regression
is `retain_limited_evidence_no_advancement` even with insufficient opportunity
(retain that opportunity limit separately). Otherwise insufficient opportunity
takes precedence over the recovery screen. A completed, adequately exposed run
passes only as `retain_promising_diagnostic_only`; a failed screen remains
`retain_limited_evidence_no_advancement`.

## Local verification and next action

**132 offline tests pass: 110 preparation/harness tests plus 22 unchanged gateway
and contract tests.** Ruff lint/format and strict mypy pass on the five private
scripts. Verification covers all 32 exact requests through mocked HTTP,
unchanged historical controls, card-only treatment differences, withheld labels,
both-arm sentinels, ceilings/restart, sixteen non-200 fixtures, terminal export,
complete source-bound inspection, secondary classifications, insufficient
opportunity, delivery-only gains and independent regression failures.

The restricted-process test attempt reproduced Windows asyncio's socket-pair
initialization hang before HTTP. The completed mocks ran outside that restriction
with real HTTP transports blocked. Type checking required the private dependency
paths and repository engine path; the initial path-resolution failure and final
successful verification are retained. No test answer is new model evidence.
Production/frontend code did not change; unrelated application suites and the
production build were not repeated.

Private bundle: `data/diagnostics/reviewer-premise-v61-2026-10-24/`.
It contains eight frozen cases, the full casebook, 32 prepared requests, schedule,
card, executable scoring/stops, model/runtime/source fingerprints, budget and
verification evidence. Its immutable `plan.json` seals these artifacts and this
document; the tracker records the plan hash. Tracker/index hashes are bound by a
separate documentation closure. No approval record or live directory exists.

Offline commands from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-premise-v61-2026-10-24/premise_experiment.py verify
.venv/Scripts/python.exe -X utf8 -m pytest data/diagnostics/reviewer-premise-v61-2026-10-24/test_premise.py tests/models/test_ollama_gateway.py tests/models/test_contracts.py -q
```

Review this frozen plan before authorizing its **32-call ceiling and full
prose/context destination**. Live preflight and inference remain paused until
that approval. No outcome here qualifies production, proves a hidden generation
mechanism or demonstrates better whole-story experience. Long-form robustness,
writer behavior, no-op generalization and story-quality gains are untested here.
Preserve the nine human ties and future human emphasis on feel/emotion, flow,
character and story-breaking concerns, with mechanics prepared by machines.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**
