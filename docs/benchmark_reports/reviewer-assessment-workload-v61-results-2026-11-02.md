# Full-context assessment workload: DeepSeek and Luna results

Date: **2026-11-02**. **EXECUTION AND INSPECTION COMPLETE: 35/60 calls used,
zero retries. DeepSeek stopped at 5/30; Luna completed 30/30.**

**Do not adopt the narrower workload in production from this comparison.**
DeepSeek returned all seven context-only selections when asked to assess two,
triggering the frozen stop. Luna delivered every scheduled response, but narrowing
introduced seven grounded-judgment losses against four recoveries. Its median
complete-case generated-token reduction was **18.4%**, below the frozen 20% screen;
repeated input increased the uncached reference cost. Neither comparison qualifies
the workload treatment, an editing policy, or better story quality.

The tracked read-only component worked as intended: it rejected the extra
selections, retained the failed attempt and usage, and withheld completion from
unfinished work. Valid delivery and exact identity binding did not establish
adequate citations or correct reasoning.

The [approved frozen plan](../handoffs/reviewer-assessment-workload-frozen-plan-2026-11-02.md)
remains unchanged, with SHA-256
`2b38d6547dd5304ef2bc12e9b9fe2209fbdb915ba953cad660d29473137c2702`.
The user authorized both destinations and full unpublished prose/context, reports
and selections. **Production prompt 61 / graph 9 / fulfillment policy 1 remain
unchanged. Further inference is PAUSED; the full workflow canary is ON HOLD.**

## Execution and terminal evidence

| Provider | Attempts / ceiling | Valid deliveries | Complete MA / NA cases | Unused calls retired |
| --- | ---: | ---: | ---: | ---: |
| Ollama / `deepseek-v4.1-flash:cloud` | 5 / 30 | 4 | 1 / 1 of 8 each | 25 |
| OpenAI / `gpt-5.6-luna` | 30 / 30 | 30 | 8 / 8 of 8 each | 0 |

Each complete NA case needs all two or three narrow batches, not merely one valid
response. The first scheduled requests served as inference readiness checks; no
extra smoke generation occurred. All **35 generation dispatches** match frozen
wire bodies. OpenAI additionally made **30 approved story-bearing input-count
requests** and thirty model-catalog checks. DeepSeek made nineteen local metadata
requests around the five attempts. No failed count, transport retry, provider
fallback, unresolved reservation, larger limit or historical budget reuse occurred.

Ollama remained **0.40.13**, with matching selected DeepSeek metadata. OpenAI's
catalog and reviewed specification matched, and generated responses identified
`gpt-5.6-luna`. The existing Windows User credential was loaded into process memory;
no secret file, stored credential or active application profile changed. These
checks do not prove unchanged remote weights or independently verify billing.

DeepSeek's fifth request, **`D-NA-H1-CP-batch-001`**, asked for Q001 and Q002.
It returned **Q001–Q007**, exactly the original selections retained under
`original_admitted_spans_context_only`. The unchanged system instruction explicitly
requires assessing each active `admitted_spans` pair once and only those pairs.
The application rejected the first extra selection with
`changed or unrequested selection` and stopped both DeepSeek arms.

This was **HTTP 200, `done_reason=stop`, complete JSON, 8,219 generated tokens**,
with **7,781 tokens below the cap**. It was neither truncation nor a captured
service outage. The five extra judgments are a scope failure, not usable extra
coverage; no portion of the invalid final receives semantic credit. The original
final, wire fingerprints, usage, validation error and terminal record are retained.
The observation is consistent with confusing context-only selections with active
work, but does not establish the model's internal cause or a provider cause.

Luna completed the same narrow H1/CP request within scope. Its successful native
schema delivery is useful evidence that the new integration can execute these
requests. It does not isolate schema enforcement as the cause: model, provider,
reasoning and effective sampling also differ. Cross-provider results remain
descriptive, with very unequal coverage.

## Source-bound inspection

All **128 judgments in 34 valid responses** were inspected against the frozen
whole-claim contract, full fields and source evidence. Five shuffled, partially
masked packets were inspected and sealed before decoding their provider/arm keys.
Familiar cases, output shape and progress observations limit masking; the first
DeepSeek full W1/PC final and its terminal response had already been seen.
Contextual relations received a separate unmasked source audit. This is an
assistant factual audit, not blind human preference review. Reasoning text was
excluded throughout; OpenAI raw reasoning was not retained.

| Provider / arm | Grounded | Citation-only | Semantic | Unavailable | Fixed slots | Fresh grounded / 32 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek MA | 8 | 0 | 0 | 48 | 56 | 8 |
| DeepSeek NA | 8 | 0 | 0 | 48 | 56 | 8 |
| Luna MA | 48 | 5 | 3 | 0 | 56 | 27 |
| Luna NA | 45 | 7 | 4 | 0 | 56 | 31 |
| Total | **109** | **12** | **7** | **96** | **224** | — |

Unavailable slots are not observed semantic mistakes: two were active in the
invalid DeepSeek response and 94 belong to unstarted requests. Its only complete
pair is W1/PC, with all eight judgments grounded in both arms. There is no paired
full-control delivery failure, so no delivery recovery is demonstrated.

Luna has **56 complete paired judgments**. Its MA labels/material explanations are
correct in **53/56**, versus **52/56** for NA; correct wording does not repair a
wrong evidence handle. The paired changes are:

- **Four citation recoveries, W2/PC Q001/Q002/Q004/Q005:** MA gives substantively
  correct explanations but cites the private-test paragraph for the decision,
  contact without the vibration, preparation without the crossing, and vibration
  instead of nonperformance of the private test. NA supplies the needed evidence.
- **Six citation losses:** H1/CP Q003/Q005/Q006 and H1/PC Q004/Q005/Q007. NA
  substitutes the date or “Ten years” paragraphs for the handwriting comparison,
  or omits the observed current date/explicit realization. MA cites adequate
  evidence for these claims. Valid registry IDs are not sufficient coverage.
- **One semantic loss, H2/PC Q005:** MA correctly separates the next-scene entry
  summary from the current prohibition. NA infers that the next scene starts
  already inside from its interior location and frightened/dark entry state.
  Those fields do not establish the alleged timing.

Two important failures remain shared:

- **Private flourish, H1/CP Q007 and H1/PC Q006:** Luna supports the allegation
  that the current general handwriting match consumes the later specific private-
  flourish verification in both arms. “Structural overlap” does not establish
  that factual proposition. NA additionally misbinds the observed-match citation.
  This score does not reject a possible literary concern about suspense; craft
  opinion and factual occurrence remain different contracts.
- **Next-scene timing, H2/CP Q005:** both arms infer already-inside timing from
  location/darkness. NA additionally cites current-scene location/entry fields
  for its explanation of the next scene. These are semantic failures even though
  the separate current outside obligation is correct.

Fresh cases are informative without qualifying the treatment. All W1/W2
private-test, next-plan, attribution, negation and unavailable-annex **labels and
material explanations** are correct in both Luna arms. W1 explicitly performs
the planned test; W2 explicitly leaves it undone. W1's next plan begins outside;
W2's begins inside. The more explicit contrasts are handled, but this does not
establish why the older claims fail. Citation adequacy still falls short:
**W1/CP Q005 fails in both arms**—MA cites the wrong planned turning point,
NA cites entry preparation instead of the performed tracing test. With the four
additional MA W2/PC citation failures, fresh grounding is **27/32 MA, 31/32 NA**.

One adjudication is explicitly retained in the notes: NA W2/PC Q001 compresses
the blueprint's “decides to enter” into “entering” in an extra clause. Its main
reason and actual evidence correctly establish a decision while outside. This
was treated as imprecise shorthand, not a material claim that the blueprint
requires a completed crossing. No gold or scoring rule was changed.

## Whole relations and application completion

The four Luna H1/CP and H2/CP contextual relation slots retain the original full
fields and linked members. Independent source inspection establishes the match
versus no-match contradiction and crossing versus outside-boundary violation.
The H1/CP NA member citations lose the observed-match evidence; the corresponding
MA citations and both H2/CP sets cover their relation's premises.

However, these returned answers judge the shortened selected propositions, not
the complete original relation explicitly. **No model whole-relation credit is
manufactured from their supported labels.** The four corresponding DeepSeek
slots are unavailable. The tracked completion records leave support, edit
necessity and craft unassessed and writer permission false. This distinction
prevents mechanically complete work from silently becoming an editing decision.

## Complete-case resources

Input and generated counts below are provider-reported. Generated counts include
reasoning; it is not added again. Active seconds cover count/generation, excluding
metadata, local hashing, orchestration and inspection. They are not end-to-end
workflow wall time. Reference dollars use the frozen uncached planning rates,
including Luna's conservative input allowance; **actual billed cost is unknown**.

| DeepSeek observation | Calls | Input | Generated | Active seconds | Reference USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| W1/PC MA, complete | 1 | 4,258 | 6,424 | 16.28 | 0.0089862 |
| W1/PC NA, complete | 3 | 13,011 | 5,170 | 17.13 | 0.0101073 |
| H1/CP NA, invalid first batch | 1 | 14,515 | 8,219 | 24.67 | 0.0142173 |
| Total | **5** | **31,784** | **19,813** | **58.08** | **0.0333108** |

Its single complete pair reduces generation **19.5%**, while repeating roughly
three times the input and increasing active time and reference cost. The terminal
stop makes this an incomplete comparison regardless of that single observation.
Reasoning/cache splits are unreported, not zero.

Every Luna table cell is **MA / NA**, with NA summed across all its batches:

| Case | Input tokens | Generated tokens | Active seconds | Reference USD |
| --- | ---: | ---: | ---: | ---: |
| W1/PC | 4,353 / 13,295 | 2,156 / 2,048 | 28.99 / 29.00 | 0.00367545 / 0.00578135 |
| H1/CP | 14,411 / 43,461 | 4,678 / 2,908 | 50.25 / 33.22 | 0.00921635 / 0.01435485 |
| W2/CP | 4,329 / 13,220 | 1,676 / 1,828 | 24.07 / 27.51 | 0.00309345 / 0.00549860 |
| H2/PC | 15,384 / 30,969 | 2,592 / 2,474 | 22.64 / 23.42 | 0.00695640 / 0.01071105 |
| H1/PC | 14,436 / 43,561 | 3,704 / 3,122 | 38.70 / 36.69 | 0.00805380 / 0.01463665 |
| W1/CP | 4,353 / 13,295 | 2,872 / 1,991 | 35.34 / 28.00 | 0.00453465 / 0.00571295 |
| H2/CP | 15,375 / 30,942 | 1,888 / 1,490 | 17.28 / 15.22 | 0.00610935 / 0.00952350 |
| W2/PC | 4,329 / 13,220 | 2,970 / 2,021 | 33.81 / 26.75 | 0.00464625 / 0.00573020 |
| Total | **76,970 / 201,963** | **22,536 / 17,882** | **251.09 / 219.79** | **0.04628570 / 0.07194915** |

Luna NA reduces aggregate generation **20.7%** and active time **12.5%**, but the
prespecified **median per-case reduction is 18.4%**. Input increases **162.4%**;
uncached reference cost increases **55.4%**. Do not replace the failed median
screen with the favorable aggregate number. Reported reasoning totals are
**17,741 MA / 12,583 NA**; cached input is **6,590 / 13,099**, already included
within input counts. No cache discount is applied to the frozen reference.

All attempts stay within their frozen per-call token/time envelopes and both
provider reservations. Total observed reference cost is **$0.15154565**, not an
invoice. All 35 attempts have known input/output counts; no unknown usage is
silently treated as free.

## Frozen interpretation

- **DeepSeek: incomplete delivery.** Twenty-five calls retired. One grounded
  fresh pair, no demonstrated delivery recovery, no workload qualification.
- **Luna: complete execution; treatment not qualified.** All eight pairs complete,
  but seven grounded losses, one semantic loss, only 31/32 grounded fresh NA
  judgments, and incomplete explicit whole-relation assessment. No control
  delivery failure was observed. The efficiency screen also fails its median,
  cost and no-loss conditions.
- **Integration evidence:** the OpenAI count/Responses route and tracked work
  completion operate on real approved diagnostic payloads. This does not qualify
  ordinary critic extraction, writer preservation, edit necessity or story quality.

Four families in two presentation orders are not eight independent stories. There
is one attempt per scheduled cell and no repeatability estimate. The workload
intervention also increases aggregate possible allowance and repeats context;
it is not an equal-total-reasoning-budget experiment. These results do not justify
a pure model ranking, a provider-cause finding, a production profile switch or
a new prompt by themselves.

## Verification and retained evidence

The original freeze and all **3,153 source pins** reverify. Every live cell seal,
exact outgoing wire, strict final validation and completion receipt replays.
The final reconciliation accounts for all **224 fixed judgment slots** and every
valid judgment exactly once. Approval, terminal/completed records, five inspection
packet/notes seals, separate contextual inspection, detailed case resources and
all failed-delivery evidence are retained under:

- `data/diagnostics/reviewer-assessment-workload-v61-2026-11-02/`
- Its `-D-live`, `-L-live` and `-analysis` siblings.

These private bundles contain unpublished prose. The public report contains the
findings and bounded excerpts, not a new public story archive.

Post-approval checks pass **142 tests**, repository Ruff/format/strict mypy across
**222 Python files**, and the same checks for all six frozen private scripts.
The two new read-only analysis scripts pass Ruff/format. The earlier preparation
passed 143 focused tests and the full 1,278-test repository suite; the full suite
was not repeated because no production or frozen harness code changed here.

Verification history is retained honestly: the sandboxed pytest subprocess
stalled before results and was interrupted. The same verification outside the
sandbox returned **142 passes and one failure**: the preparation-only test that
asserts no approval files exist. Both approvals now legitimately exist. Its
original code remains frozen; the post-approval rerun excludes only that phase
assertion and passes **142 tests, one deselected**. No live runner was interrupted
or budget reset by these local checks.

## Recommended next local work

1. Preserve the DeepSeek two-requested/seven-returned failure, Luna citation
   recoveries/losses, shared semantic failures and grounded fresh contrasts as
   regressions. Keep invalid finals uncredited and whole-relation authority unset.
2. Audit **active work scope and evidence selection separately**. Locally test an
   application-owned response boundary against the exact active pairs while
   retaining full context. Audit the adjacent/wrong-section citation substitutions
   against the already frozen registry and renderer; do not silently remap IDs or
   treat a plausible explanation as proof that its cited text supports it.
3. Keep full MA controls and the explicit fresh event/plan contrasts as diagnostic
   references. Require a materially different, locally justified hypothesis before
   another inference proposal. Narrowing alone has not earned another unchanged
   repeat. Any stronger schema, evidence-witness interface or changed claim wording
   would need its own local verification and separately approved freeze.

The production direction remains application-owned provenance, completion and
read-only evidence presentation, with factual support separate from editorial
necessity. Human evaluation should continue to focus on feel, flow, character and
story-breaking details when actual repairs are ready for quality qualification.
No additional human checkpoint, writer dispatch or general manuscript editor is
introduced. All fourteen tracked issues remain open; Step 19 is **IN PROGRESS**,
Step 20 **NOT STARTED**, live calls **PAUSED**, and the canary **ON HOLD**.
