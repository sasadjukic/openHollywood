# MA/PE paragraph-excerpt comparison — 2026-11-01

**Completed under the frozen arm stop: 10/16 calls used, zero retries. PE is not
qualified.** MA grounded all **56/56** selected judgments. PE grounded **6/7**
judgments in its only valid report, then reached the generation limit on its
second request. Its six remaining requests were retired without dispatch.
The unchanged MA controls recovered every historical citation gap, leaving no
reproduced control failure on which to demonstrate a PE citation benefit.

The [frozen plan](../handoffs/reviewer-paragraph-excerpts-frozen-plan-2026-11-01.md)
and [preceding local audit](../handoffs/reviewer-citation-mapping-audit-2026-11-01.md)
remain unchanged. This report records diagnostic results, not production or
story-quality qualification. Production stays **prompt61 / graph9 / fulfillment
policy1**; further inference is **PAUSED** and the full workflow canary is **ON HOLD**.

## Scope, authorization and execution

The user approved full unpublished prose/context through **Ollama Cloud via the
local Ollama daemon**, within the sixteen-call ceiling. The stored approval binds
the exact plan hash:

`509d552c76faabc1ac1d31345c64b3956b34c8247e01c37c9e7d0f9848b896c8`.

MA is the existing full-context assessment of selected claims. PE adds only
`exact_paragraph_text` beside each prose registry reference. It retains the full
sources, fields, report and selections. Removing the additions restores the
paired MA wire exactly. The four historical MA wires are unchanged from VA/MA;
fresh C5/D6 families supply positive and negative semantic contrasts. Both PC
(prose first) and CP (context first) orders were frozen. No selector, writer,
repair or replacement call was made.

All dispatched requests used `deepseek-v4.1-flash:cloud`, `think: "high"`,
temperature 0.2, top-p 0.95, seed 20261022, 40,000 context and 16,000 combined
generated tokens. These are verified requested settings; provider-effective
sampling is not attested. All **21 version observations** matched **Ollama
0.40.13**; **11 model checks** matched the frozen model information, including
digest `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.

| Arm | Planned / dispatched | Valid | Length stop | Retired without dispatch |
| --- | ---: | ---: | ---: | ---: |
| MA | 8 / 8 | 8 | 0 | 0 |
| PE | 8 / 2 | 1 | 1 | 6 |
| Total | 16 / 10 | 9 | 1 | 6 |

The fourth overall attempt, **E-PE-H2-CP**, returned HTTP 200 with
`done_reason: length`, **16,438 input / 16,000 generated tokens**, and a
**1,433-character partial final response**. It also returned a nonempty thinking
field of **73,535 characters**. The provider counters are integrity-bound and
verified; the reasoning/final token split remains unknown. Character counts
cannot substitute for token counts. No judgment was salvaged from the partial
final. The gateway error chain is empty: this is a reported length termination,
not a captured HTTP or transport error.

The frozen rule immediately retired PE. MA continued only its original remaining
cells and completed normally. No global terminal stop, retry, budget transfer or
replacement occurred. The six unused calls are not permission to resume PE.

## Inspection and results

All **63 judgments** from the nine valid reports were inspected against complete
sources, exact selections, reasons, cited passages and frozen adequate-evidence
criteria. Partial masking withheld the trial key and resources until notes were
sealed. This was an assistant factual audit, **not blind human review**; recognizable
cases and selections limited masking. Thinking content was excluded from semantic
inspection. The sealed notes and exact source evidence remain replayable.

| Measure | MA | PE |
| --- | ---: | ---: |
| Returned valid judgments | 56 | 7 |
| Correct labels | 56/56 | 6/7 |
| Semantically correct judgments | 56/56 | 6/7 |
| Adequately cited, grounded judgments | 56/56 | 6/7 |
| Grounded / frozen denominator | 56/56 | 6/56 |
| Historical grounded | 24/24 | 6/24 |
| Fresh grounded | 32/32 | 0/32; all unstarted |
| Observed material semantic errors | 0 | 1 |
| Additional correct-label citation gaps | 0 | 0 |

Only **one complete valid request pair**, H1/PC, was available: seven paired
judgments, six retained successes and one PE regression. PE's five H2/CP slots
have no valid report; its remaining 44 slots were never attempted. The frozen
scorer therefore lists **50 paired grounded and semantic losses**, comprising
**one observed regression and 49 unobserved slots**. These are not fifty observed
semantic mistakes. Likewise, the seven historical grounded-protection misses and
fourteen historical semantic-protection misses are all unobserved. PE retains
six observed successes from each protected set; it does not demonstrate retention
of the remaining protected units.

### The observed PE failure is semantic, with correctly located citations

**E-PE-H1-PC / Q006 / U011** claims that establishing a handwriting match in the
current scene consumes the next scene's specified verification of a private,
idiosyncratic flourish. The frozen judgment is **unsupported**. PE returned
**supported** and cited S215, S290 and S309:

- S215 specifies the later verification of a flourish only the protagonist knows.
- S290 prohibits a handwriting match by the end of the current scene.
- S309 establishes a general handwriting match in the current prose, without
  performing the specified private-flourish verification.

PE's reason treats the valid current-scene boundary violation as proof that the
specific later test has already been consumed. The locations are correct; the
inference is not established by those sources. The paired MA judgment correctly
separates the general match from the specific verification. This repeats an
existing semantic failure pattern, rather than revealing an application mapping
error or a new failure class.

One observation per condition does not establish that excerpt presentation caused
the regression. It does show that correct paragraph presentation did not prevent
this error in the observed PE report.

### The unchanged MA controls recovered without the PE intervention

The four historical MA requests now ground **24/24** judgments, versus **13/24
grounded and 20/24 correct labels** in their previous captures. Their exact wire
payloads are unchanged. All seven old citation targets recover:

- H1/CP: Q002, Q003, Q005 and Q006.
- H2/CP: Q004.
- H2/PC: Q001 and Q002.

The four old semantic false positives also recover: both orders of the specific
flourish inference and both orders of the unsupported starting-inside inference.
Thus **0/7 historical citation failures reproduce** in the new MA controls and
**zero paired citation recoveries** can be credited to PE. None of those seven
targets has a valid PE counterpart in this stopped run.

This is observed repeat variability under the same visible request settings and
captured metadata. It does not prove stable reliability, a provider-side fix,
effective seed determinism or an unseen model change. MA's fresh **32/32** results
are useful bounded positives, with no PE fresh result available for comparison.

### Component success remains separate from a complete relation judgment

The two evaluable historical contextual flags, **MA H1/CP and MA H2/CP**, correctly
assess selected components but do not explicitly assess the complete current
endpoint relation. Rejecting a separate future-scene allegation does not itself
assert the current violation. No automatic whole-relation credit is awarded.
The corresponding PE flags are unavailable because of length retirement and an
unstarted request. The PC selections that expressly include the complete boundary
claim are grounded in MA. Selected-claim accuracy does not measure whether an
upstream selector admitted every necessary relation.

## Frozen decision and resources

The frozen outcome is **`gate_not_met`**, rather than a promising citation result:

1. Nine of sixteen reports are valid, with only seven of 56 paired units evaluable.
2. No historical citation-only failure reproduces in the new MA control; the
   required two paired recoveries are unavailable.
3. One observed paired semantic and grounded regression violates the zero-loss rule.
4. PE cannot demonstrate all historical protections or the 32 fresh successes.

Control nonreproduction alone would have been inconclusive if the other gates
passed. Here the delivery, observed regression and coverage gates also fail.
There is no production qualification or writer-dispatch authorization.

| Arm | Input tokens | Combined generated tokens | Active request seconds |
| --- | ---: | ---: | ---: |
| MA, eight attempts | 97,973 | 69,349 | 307.27 |
| PE, two attempts | 31,597 | 20,934 | 92.22 |
| Total | **129,570** | **90,283** | **399.48** |

All ten attempts have verified reported usage, including the length stop. Total
usage remains within 384,000 input / 256,000 generated / 9,600 seconds, and every
call stays within 24,000 input / 16,000 generated / 600 seconds. Generation at
exactly the cap still triggers the frozen length retirement. The largest input,
generation and elapsed values belong to PE H2/CP: 16,438 / 16,000 / 70.11 seconds.
MA C5/CP also approached the generation limit at 14,975 tokens while delivering
a valid report.

Using the plan's archived reference rates, total nominal cost is **$0.1472106**.
This is not actual billing or a current-price claim; billing remains unknown.
No reasoning/final token split is inferred. In the only complete valid pair,
PE used 673 more input tokens, with generated-token ratio 0.653 and elapsed-time
ratio 0.705 relative to MA. One pair plus a stopped arm does not support an
efficiency conclusion; the frozen aggregate resource screen is unavailable.

## Verification and preserved evidence

Post-run verification covers the approved ceiling, original schedule and stops,
exact dispatched wires, raw response/receipt bindings, known usage, metadata,
source-bound annotations and frozen score replay. The **63 frozen files and
1,751 historical/runtime source fingerprints** remain unchanged. All fourteen
original issue bodies and posted URLs are preserved.

**283 post-run offline tests pass:** 103 comparison tests, 22 gateway/contract
tests, 74 citation-mapping regressions and 84 delivery/usage regressions. Only the
preparation test asserting that approval is absent is deselected; actual approval
binding is verified separately. Ruff lint/format and strict mypy pass on eleven
frozen and three analysis scripts. Sealed annotation reconstruction and live
evidence/score replay pass with real HTTP and database access blocked. No product
code changed, so client build and end-to-end workflow checks are outside this
diagnostic-only verification.

The private records are under
`data/diagnostics/reviewer-paragraph-excerpts-v61-2026-11-01/` and its `-live`,
`-inspection` and `-analysis` siblings. Key records are `approval.json`, the sealed
per-cell captures, `notes.json` / `notes-seal.json`, `execution-summary.json`,
`results.json`, `delivery-inspection.json`, `interpretation-summary.json`, the
post-run verification record and `publication-closure.json`. Raw thinking remains
private and is excluded from judgment evidence.

## Recommended local follow-up

1. Preserve the partial-final length capture, the H1/PC MA/PE semantic pair and
   the recovered historical MA controls as regressions. Keep delivery, source
   location, semantic support and whole-relation coverage on separate axes.
2. Audit the saved delivery/resource evidence locally. PE adds duplicate source
   text and input overhead, but this run cannot establish why one request exhausted
   generation. Preserve unknown token splits; compare exact settings, final shape
   and resource observations without inferring a provider outage or converting
   internal thinking into factual evidence.
3. Audit baseline repeatability across the existing identical MA captures before
   proposing further inference. The intended citation failure did not reproduce.
   Any later experiment needs a locally justified question that distinguishes
   unstable baseline performance from treatment benefit, and must account for
   delivery risk. No new call budget or prompt change is proposed here.

Keep successful mechanical judgments as diagnostic evidence. They do not establish
edit necessity, prose preservation, overall feel, story flow or character quality.
Those remain separate from this reviewer experiment and from the eventual human
literary review. CW-007, CW-008 and CW-013 remain open; CW-014 is unqualified.
No issue is closed or edited externally. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
production prompts unchanged; live calls PAUSED; full workflow canary ON HOLD.**
