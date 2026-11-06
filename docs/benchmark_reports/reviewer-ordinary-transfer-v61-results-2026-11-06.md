# Sol-high ordinary-review transfer diagnostic results

Date: 2026-11-06. **Completed: 16/16 attempts; frozen screen not passed.**

Sol-high delivered all sixteen responses successfully. Inspection of all **96 fixed
slots** found **87 grounded, eight citation-only failures and one semantic scope
failure**, with zero unavailable slots. The saved ordinary-review cohort scored
**39/48 grounded**; the fresh authored controls scored **48/48**. This supports
limited factual transfer, but not reliable assessment of every admitted ordinary
explanation, automatic repair authorization or production promotion.

Execution followed the approved [frozen plan](../handoffs/reviewer-ordinary-transfer-frozen-plan-2026-11-05.md)
once, using `gpt-6.1-sol` at high reasoning. Full prose/context went to OpenAI
Responses and its input-count endpoint. There were **16 generation requests,
16 input-count requests and 16 catalog reads**, zero retries, replacements,
fallbacks or extra probes. No stop condition occurred. Production prompts,
profiles, graph and routing are unchanged; further live calls are **PAUSED** and
the full workflow canary remains **ON HOLD**.

## Results and limits

| Cohort / family | Grounded | Citation-only | Semantic scope | Unavailable |
| --- | ---: | ---: | ---: | ---: |
| Saved S1: Elara | 24/24 | 0 | 0 | 0 |
| Saved S2: Elena | 15/24 | 8 | 1 | 0 |
| **Saved ordinary total** | **39/48** | **8** | **1** | **0** |
| Fresh S3: Lina | 24/24 | 0 | 0 | 0 |
| Fresh S4: Orin / Bea | 24/24 | 0 | 0 | 0 |
| **Fresh authored total** | **48/48** | **0** | **0** | **0** |
| **All fixed slots** | **87/96** | **8** | **1** | **0** |

Support labels match frozen gold in **95/96** slots. All **214 submitted witnesses**
locate their exact immutable source sections. All 96 assessments have complete
mechanical binding, including four permitted empty evidence lists for unavailable
continuations. Mechanical binding does not establish evidence adequacy. The
all-96-grounded screen therefore fails despite successful delivery and high label
agreement.

The twelve unchanged saved fields all have **supported gold**. They come from two
ordinary-v61 Gemma diagnostic probes with synthetic unapproved context, not durable
production reviews. All surrounding report fields and original story-bearing
context remain available. Their forty-eight repeated slots do not test precision
on naturally false ordinary-review explanations. False compounds, attribution
errors and missing-source uncertainty occur in the fresh authored controls.
Different context lengths and provenance prevent a causal comparison of cohorts.

Gold, evidence criteria, exact requests and source scope were fixed before
inference. These results are assistant adjudications against primary sources,
not blind human ratings or independently certified semantic truth. No gold,
criterion, claim, source packet or denominator was changed after responses.

## The remaining failures

**One response changes the question from obligation to repair necessity.**
In `OT-1-S2-CP / Q002`, the unchanged selected field says:

> Elena must decide to verify the handwriting.

The current assignment explicitly requires this decision. The model recognizes
that fact and correctly observes that her purposeful journal comparison already
fulfills it. Nevertheless, it returns `unsupported` because the surrounding review
presents the condition as an outstanding mandatory repair. It has assessed whether
a further repair is justified, rather than whether the selected obligation exists.

The explanation's story facts are correct. The inspection therefore records
material explanation correctness as true, whole-claim scope as false, and the
support label as wrong. This is a semantic scope failure, not a fabricated event
or a citation-location failure. Its exact CP repeat returns `supported`, as do
both PC responses, while separately explaining that a supported obligation does
not establish a missing decision or justify another rewrite.

The current wire asks for exact propositions and distinguishes obligations from
observed events, but also frames the task around factual repair premises and keeps
the whole report as context. The admitted selection contains only `field_id` and
the unchanged quotation. The specific `assignment_obligation` declaration is in
offline gold, not that model-visible selection. This is a concrete interface
observation, not proof of a cause or of a particular fix. The recovered identical
request also prevents treating the first failure as a deterministic order effect.

**Eight correctly labeled endpoint judgments omit required ending evidence.**
All four Elena responses fail the frozen evidence criteria for Q005 and Q006.
They correctly identify the conclusive handwriting match and its conflict with
the current no-match endpoint. Their evidence locates the match paragraph (`S572`)
and assignment prohibition (`S527`), sometimes with outcome or boundary policy.
None cites the final paragraph (`S573`).

The pre-inference criteria require the established result **and ending context**:
the final paragraph leaves the sender/origin unknown but does not retract the
handwriting finding. A quote locating S572 credits that paragraph only, not its
neighbor. Two responses even discuss the remaining sender uncertainty while
leaving the paragraph containing it uncited. Thus all eight retain correct
semantics and complete location binding, but insufficient cited coverage under
the frozen rule. The missing paragraph was visible, and each affected assessment
used only two to four of eight allowed witnesses. There was no citation-budget,
output-limit or delivery failure preventing one more witness.

This is specifically a coverage failure against the published criterion, not
evidence that the model missed the match or misunderstood the ending. The scorer
does not require the illustrative reference set verbatim; alternative adequate
sections would pass. No alternative cited section supplies this missing ending
context. Correct incidental background or separation-of-scope qualifications are
not independently counted as new claim predicates; material explanations are
checked against the full source, while the frozen claim-specific adequacy criteria
determine the needed cited coverage. No unseen neighboring text is credited.

## What worked

Elara's four responses retain the distinction between a purposeful decision and
completed entry. They recognize touch followed by a fixed magnetic pull, without
inventing an assignment requiring that order or causation. They preserve the
valid current-endpoint criticism without erasing earlier fulfillment.

The fresh families consistently distinguish optional actions from obligations,
true clauses from false whole compounds, complete from partial procedures,
attributed statements from statements by another speaker, and unavailable drafts
from disproved events. They recognize actual boundary breaches and reject invented
ones. These are useful positive controls. They do not measure craft, emotional
effect, prose preservation or whether any particular rewrite would improve a story.

## Repeats, order and all attempts

All **48 exact-repeat pairs** and **48 source-order pairs** were inspected and
remain in the [full pair ledger](../../data/diagnostics/reviewer-ordinary-transfer-v61-2026-11-05-analysis/aggregate.json).

| Pair comparison | Label agreement | Category agreement | Both grounded |
| --- | ---: | ---: | ---: |
| Exact-body repeats | 47/48 | 47/48 | 43/48 |
| PC versus CP order | 47/48 | 47/48 | 43/48 |

The sole label/category disagreement in either comparison is S2 Q002: first CP
fails, second CP and both PC pass. The eight ending-coverage failures produce four
repeat pairs and four order pairs that agree while both fail. Agreement alone is
not success. These paired counts reuse the 96 slots; they are not additional
independent samples or estimates of a population effect.

G = grounded; C = citation-only; S = semantic scope. Every row delivered all six
claims validly. Generated tokens include reasoning; time includes count/generation.

| # | Trial | G | C | S | Input tokens | Generated tokens | Active seconds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | OT-1-S1-PC | 6 | 0 | 0 | 23,310 | 2,420 | 35.98 |
| 2 | OT-1-S2-CP | 3 | 2 | 1 | 22,714 | 3,959 | 60.93 |
| 3 | OT-1-S3-PC | 6 | 0 | 0 | 3,047 | 2,200 | 30.52 |
| 4 | OT-1-S4-CP | 6 | 0 | 0 | 3,091 | 2,304 | 30.56 |
| 5 | OT-1-S2-PC | 4 | 2 | 0 | 22,714 | 3,101 | 42.65 |
| 6 | OT-2-S1-PC | 6 | 0 | 0 | 23,310 | 2,521 | 35.32 |
| 7 | OT-1-S1-CP | 6 | 0 | 0 | 23,310 | 2,151 | 28.14 |
| 8 | OT-2-S2-CP | 4 | 2 | 0 | 22,714 | 3,452 | 49.59 |
| 9 | OT-1-S4-PC | 6 | 0 | 0 | 3,091 | 2,042 | 26.80 |
| 10 | OT-2-S3-PC | 6 | 0 | 0 | 3,047 | 1,892 | 23.77 |
| 11 | OT-1-S3-CP | 6 | 0 | 0 | 3,047 | 1,900 | 23.73 |
| 12 | OT-2-S4-CP | 6 | 0 | 0 | 3,091 | 2,248 | 29.85 |
| 13 | OT-2-S2-PC | 4 | 2 | 0 | 22,714 | 3,964 | 66.11 |
| 14 | OT-2-S1-CP | 6 | 0 | 0 | 23,310 | 2,311 | 30.13 |
| 15 | OT-2-S4-PC | 6 | 0 | 0 | 3,091 | 2,029 | 22.77 |
| 16 | OT-2-S3-CP | 6 | 0 | 0 | 3,047 | 2,113 | 28.07 |

## Resources and verification

Usage is known for every attempt: **208,648 input tokens / 40,607 generated tokens**,
including **15,213 reasoning tokens** and **110,177 cached input tokens**. Reasoning
content is not retained. Active time totals **564.92 seconds**, median **30.32s**,
maximum **66.11s**. Separate catalog/operator wall time was not independently timed.

The exact count endpoint and delivered usage agree for every request. Input sizes
are 23,310 / 22,714 / 3,047 / 3,091 for S1–S4, within the frozen 24,000 limit.
Maximum generated tokens are 3,964, below 32,000. Final responses are 5,572–7,589
characters, below 64,000. All responses identify the frozen Sol model. No limits
were expanded and no missing or unknown usage was converted to zero.

The frozen-rate uncached input/cache-write bound gives **$0.927690** in reference
cost, within the **$6.08 reference reservation / $9.60 planning allowance**.
Actual billing remains unknown; this is not an account charge or a cache-discounted
invoice calculation.

**361 offline tests pass**: 154 applicable frozen harness/design tests, 154 tracked
assessment tests, 39 provider/routing/execution tests and 14 result regressions.
Only the preparation-time assertion that approval/live directories do not exist is
deselected; actual approval, endpoint bodies, ceilings and all slots are checked
separately. The 13 warnings come from existing deliberately malformed Pydantic
fixtures. Repository Ruff/format/strict mypy pass for **226 files**; corresponding
private checks pass for **18 diagnostic/analysis scripts**. Literal full-context
views, seals, scoring, pair ledgers and resources replay exactly.

The first private type check exposed missing explicit module exports in the new
analysis helper. That typing-only defect was corrected; all private checks and
the 14 result tests pass afterward. The initial failed check and helper copies
remain preserved. Frozen code, captures, gold and result judgments did not change.
No application code, dependency, persistence, API or frontend changed, so frontend
and production-build checks were inapplicable.

Verification results are recorded in the [final local verification record](../../data/diagnostics/reviewer-ordinary-transfer-v61-2026-11-05-analysis/verification-final.json).
All **80 frozen files / 768 source fingerprints** remain unchanged. The plan hash is:

```text
488369a1af1ebe7f18a6d02aae50f67ecd8d5d5a28b39821cd6864d84cd3926d
```

The [inspection ledger](../../data/diagnostics/reviewer-ordinary-transfer-v61-2026-11-05-analysis/inspection.json)
binds every judgment to its exact sealed receipt and assessment; the
[analysis index](../../data/diagnostics/reviewer-ordinary-transfer-v61-2026-11-05-analysis/README.md)
links all sixteen full-context literal views, resource records and replay commands.
These private artifacts are local files, not GitHub attachments.

## Recommended next work

1. Preserve the obligation failure/recovery and all ending-coverage pairs as local
   regressions, alongside the successful controls. Keep the original scores intact.
2. Audit **selected-field truth versus the surrounding repair recommendation** in
   the read-only assessment contract. Check whether an explicitly rendered,
   answer-free predicate/authority declaration can preserve an unchanged whole
   ordinary statement while keeping fulfillment and edit necessity separate.
   Local declaration consistency alone must not become semantic certification.
3. Audit endpoint evidence coverage separately: when does a claim require the
   established event, the ending, or both, and how should that obligation be visible
   to an assessor? Preserve complete context and the distinction between locators
   and evidence. Do not silently append missing citations, infer adequacy from
   binding, or relax this run's frozen criterion. Require a locally justified
   hypothesis before preparing another live comparison.

No further comparison is frozen or approved here. These results favor continuing
the bounded read-only component, not granting writers authority from reviewer
support labels. Factual support does not establish an outstanding repair, and an
outstanding repair does not establish the best creative solution. Future human
review should continue to focus on feel, flow, character and story-breaking details,
with mechanics and source evidence prepared for review rather than re-searched.

CW-007/CW-013 remain open; CW-014 remains unqualified. All fourteen issue bodies and
posted URLs are unchanged; no external issue changed. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; production prompts unchanged; live calls PAUSED;
full workflow canary ON HOLD.**
