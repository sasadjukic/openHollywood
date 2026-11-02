# Baseline-only MA repeatability diagnostic — results, 2026-11-02

**COMPLETE: 12/12 calls, 12 valid reports, no retries or terminal stops.** The
frozen outcome is **`known_failure_recurrence_observed`**. Source inspection finds
**60/72 fully grounded judgments**, six citation-only failures and six semantic
failures. Correct support labels alone score **67/72**; substantive semantic
correctness scores **66/72**. All fixed slots are available.

The earlier successful MA controls did not establish stable performance. This
repeat reproduces one historical citation-target failure and five historical
semantic-label failures, and exposes five other citation failures plus one
incorrect explanation with the correct label. These are observations on two
familiar scene families, not a population reliability estimate or evidence of
provider causation.

Production remains **prompt 61 / graph 9 / fulfillment policy 1**. No production
prompt, writer route, canonical prose or human checkpoint changed. **Step 19 is
IN PROGRESS; Step 20 is NOT STARTED; further live calls are PAUSED; the full
workflow canary is ON HOLD.** No issue is closed by this result.

## Authorization and execution

The user approved the [frozen twelve-call plan](../handoffs/reviewer-baseline-repeatability-frozen-plan-2026-11-02.md),
including full unpublished prose, context, reports and saved selections sent to
**Ollama Cloud through the local Ollama daemon**. The approval binds plan SHA-256
`de0f3fc5674e1d3c99d62f764ed729558703c0c6543a5429c9e6cc76635751f7`.

The run used four unchanged historical MA wire requests, each repeated three
times in the frozen interleaved order. The same wires were previously used by
VA/MA and the [MA/PE comparison](reviewer-paragraph-excerpts-v61-results-2026-11-01.md).
Repeat identifiers stayed outside model messages. There was no PE treatment,
selector, writer, request repair, retry, replacement or budget reallocation.

All twelve dispatched requests exactly match their frozen controls. Twenty-five
version observations match **Ollama 0.40.13**, and thirteen model checks preserve
the frozen DeepSeek metadata. The requested model was
`deepseek-v4.1-flash:cloud`, digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
Settings stayed at high thinking, temperature 0.2, top-p 0.95, seed 20261022,
40,000 requested context and 16,000 maximum combined generated tokens. Every
attempt returned HTTP 200, a nonempty valid final report and `done_reason: stop`.
No frozen stop condition fired, and all twelve approved slots are consumed.

## Source inspection and results

Every returned claim was inspected against its full source and exact selected
meaning. Notes bind the source, final result, reason and evidence references.
The repeat/trial key and resources were decoded only after notes were sealed.
This is **partial assistant masking, not blind human literary review**; familiar
content can reveal family and presentation order. Thinking is excluded from
semantic evidence. Citation adequacy measures relevant content coverage, not an
exact reference whitelist. No partial or absent answer receives credit.

| Unchanged wire | Valid reports | Grounded judgments | Citation-only failures | Semantic failures | Historical citation / label recurrences |
| --- | ---: | ---: | ---: | ---: | ---: |
| H1/PC | 3/3 | 14/21 | 5 | 2 | 0 / 2 |
| H1/CP | 3/3 | 17/21 | 1 | 3 | 1 / 3 |
| H2/PC | 3/3 | 15/15 | 0 | 0 | 0 / 0 |
| H2/CP | 3/3 | 14/15 | 0 | 1 | 0 / 0 |
| **Total** | **12/12** | **60/72** | **6** | **6** | **1 / 5** |

The frozen historical citation targets recur **1/21 times**: H1/CP Q005 in R1.
The four historical semantic-label targets recur **5/12 times**: H1/PC Q006 in
R1 and R3, and H1/CP Q007 in all three repeats. The other five citation failures
occur on H1/PC selections outside the seven original citation targets. H2/CP R3
Q005 retains the correct label but fails explanation grounding; it is not counted
as a historical label recurrence.

The original protection sets retain **35/39 grounded occurrences** and **60/60
semantically correct occurrences**, with four observed grounding losses and no
unavailable slots. These sets refer to the older VA/MA baseline; they are not a
claim that all 72 recently successful control occurrences stayed protected.
Relative to the most recent MA/PE historical controls, which grounded 24/24,
twelve of the 72 corresponding new occurrences fail full grounding. Historical
results remain separate from the current denominators.

### Citation failures: accurate descriptions attached to insufficient passages

**H1/PC R2, Q003–Q007** contains five citation-only failures. The model generally
describes the correct source content, but its submitted references do not cover it:

- Q003, Q004 and Q005 use **S310** for purposeful checking or the definitive
  match. Those events occur in **S309**. S310 is the final paragraph about the
  date, suspicion and dread; it does not contain the journal comparison.
- Q006 correctly distinguishes a general match from the specific future flourish
  test, but cites **S215 + S310**, omitting the actual comparison in S309.
- Q007 describes both dates and the ten-year realization, but cites
  **S305 + S306 + S299**: the warning reaction, card date and assignment turning
  point. The observed clock date and realization in **S307 + S308** are missing.
  An assigned realization cannot substitute for its observed occurrence.

**H1/CP R1 Q005** cites S305, S306 and S307. Both dates are covered, but the explicit
realization in **S308**, described by the reason, is not. Calculating the date gap
does not itself provide cited evidence of the character realizing it.

These are valid reference IDs with inadequate content, not malformed output or
unknown-reference failures. The saved model finals contain the submitted IDs,
and the frozen wires retain the source registry; this run does not identify an
application remapping defect. It demonstrates why reference existence and correct
explanation text are insufficient evidence-binding checks. It does not establish
why the model chose the neighboring or incomplete references.

### Semantic failures: the specific future test remains distinct

Five responses again infer that a general handwriting match consumes Scene 2's
specific **verification of an idiosyncratic flourish only Elena knows**. S215 names
that private test; S309 establishes a general match. Neither supplies the missing
equivalence. The current no-match obligation in S290 establishes a separate valid
endpoint violation, not completion of the future test.

H1/CP returns the wrong supported label in all three repeats. H1/PC changes labels:
R1 and R3 make the same false-positive inference; R2 correctly rejects it, but
mis-cites the comparison. Thus only **one of six** flourish judgments is
semantically correct, and **none of six** is fully grounded. A correct recovery
on one axis does not establish a usable complete judgment.

H2's unsupported claim that the next scene starts already inside is rejected in
all six repeats. **H2/CP R3 Q005**, however, says the next scene is only a plan,
demands an observed next scene, and accuses the claim of treating an obligation
as an observed event. The selected field is `/scene_boundary_check/next_scene_comparison`:
it makes a claim about the plan's timing. The plan can establish or fail to
establish that timing without a future draft. Darkness/interior location does not
prove an already-inside start, and the summary places entry in Scene 2; those are
valid independent grounds for rejection. The correct unsupported label and these
useful citations do not remove the explanation's material reference-type error.

### Whole-relation coverage is still a separate question

Only **one of six contextual flags** receives explicit, grounded whole-relation
credit: **H2/CP R2**. Its decision explanation expressly states that entry also
overruns the separate exit-state boundary, while the report's other selected
judgments supply the observed entry and governing prohibition. This is an actual
relational assertion, not an automatic inference from correct component labels.
The decision claim's own citation score concerns its reasoning and preparation;
the additional boundary observation and its source support are recorded in the
separate relation inspection.

The other five CP responses assess components without explicitly judging the
complete current endpoint violation. H1/CP R2 mentions the no-match prohibition
while arguing for future-flourish preemption; that does not explicitly decide the
current endpoint relation. PC selections that contain the whole relation make
that judgment directly, although H1/PC R2 mis-cites its observed side. Successful
component classification does not establish complete review coverage.

## Repeat variation and resources

| Wire | R1 grounded | R2 grounded | R3 grounded | Input tokens | Generated tokens | Active seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| H1/PC | 6/7 | 2/7 | 6/7 | 43,458 | 31,780 | 111.92 |
| H1/CP | 5/7 | 6/7 | 6/7 | 43,383 | 21,878 | 80.41 |
| H2/PC | 5/5 | 5/5 | 5/5 | 46,374 | 25,291 | 97.02 |
| H2/CP | 5/5 | 5/5 | 4/5 | 46,344 | 33,514 | 109.68 |
| **Total** | **21/24** | **18/24** | **21/24** | **179,559** | **112,463** | **399.03** |

All four wires produce three distinct final outputs. All **24 unit positions**
vary in reason wording, **12/24** vary in citation sets and ordered citation lists,
and **1/24** varies in support label. Stable labels can still be wrong: H1/CP's
flourish label is wrong three times. H1/PC R2 and R3 report identical cached-input
counts of 14,464 while changing citations, labels and grounding. Across the run,
120,576 input tokens are reported cached. These observations neither establish a
cache cause nor make the seed a deterministic guarantee. There is no comparison
provider, model intervention or evidence identifying an unseen backend change.

Every attempt has verified usage. Totals are below the frozen 288,000 input /
192,000 generated / 7,200-second reservations; every attempt remains below
24,000 input / 16,000 generated / 600 seconds. H2/CP R3 is the largest generation
and latency observation at **15,094 generated tokens and 49.31 seconds**, despite
returning only five selected judgments. This is a delivery-resource observation,
not an explanation of its semantic error. Reasoning and final token counts remain
**unknown separately**; character counts are not used to estimate that split.

The archived-rate reference is **$0.1888233**, below the plan's $0.35 allowance.
This is not actual billing or a current-price claim. Actual billing remains unknown.
Two family clusters, three repeats and incomplete position counterbalancing do
not support broad reliability, presentation-order causation or story-quality claims.

## Verification and evidence

The **51 frozen files and 2,283 historical/runtime fingerprints** remain unchanged.
Replay verifies the approval, call ceiling, schedule, exact dispatched wires,
response/receipt seals, source-bound annotations, usage, metadata and frozen score.
The original fourteen issue bodies and posted GitHub URLs are preserved.

**252 post-run offline tests pass:** 79 diagnostic tests, 22 gateway/contracts,
67 prior repeatability regressions and 84 delivery/usage regressions. The one
preparation-only test asserting that approval is absent is deselected; real
approval binding is checked separately. Ruff lint/format and strict mypy pass on
ten frozen and three analysis scripts. Annotation reconstruction and score replay
pass with real HTTP and database access blocked. No product code changed; client
builds and full workflow tests are outside this diagnostic-only verification.

Private evidence is under
`data/diagnostics/reviewer-baseline-repeatability-v61-2026-11-02/` and its `-live`,
`-inspection` and `-analysis` siblings. It includes approval, exact per-call
captures, sealed inspection notes, `execution-summary.json`, `results.json`,
`delivery-inspection.json`, `interpretation-summary.json`, offline verification
and `publication-closure.json`. Raw thinking is excluded from judgment evidence.

## Recommended next local work

1. Preserve these repeated controls as regressions, including the H1/PC
   correct-label/bad-citation response, its wrong-label neighbors, the recovered
   H2 judgments and the H2/CP reference-type failure. Retain the full same-wire
   triples so later changes cannot claim gains by selecting a favorable control.
2. Audit citation binding independently of semantic judgment. Compare the model's
   described source facts with its submitted references in all six citation-only
   failures. Assess locally whether an application-owned check can identify a
   demonstrated mismatch without inventing a citation repair, discarding relevant
   context or rejecting legitimate paraphrases. Do not rerun the resource-heavy
   PE intervention on the strength of these results alone.
3. Audit the specific-test versus general-match inference and plan-timing reference
   type as distinct semantic contracts. Preserve the valid current overrun while
   rejecting unsupported claims about a future beat. Require local counterexamples
   and a materially different, testable hypothesis before proposing another live
   treatment. This report grants no further call budget or prompt change.

Mechanical evidence grounding, literary merit and edit necessity remain separate.
An unsupported allegation should not acquire authority to rewrite a story merely
because it is fluent, repeated or accompanied by valid reference IDs. Future
story-quality work still needs overall feel, flow, character and story-breaking
detail assessment, alongside machine-owned mechanical checks and preservation
evidence. This reviewer-only repeat does not qualify a writer repair or a canary.
