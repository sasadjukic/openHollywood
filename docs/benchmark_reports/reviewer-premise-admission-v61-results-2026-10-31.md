# SA/VA premise-admission diagnostic results

Date: **2026-10-31**. **6/24 calls attempted; five completed reports; one terminal
truncation; eighteen calls unstarted; zero retries.** Production **prompt 61 /
graph 9 / fulfillment policy 1** unchanged. Further inference **PAUSED**; full
workflow canary **ON HOLD**.

**The comparison is incomplete and does not establish a premise-admission
benefit.** Call six, **A-SA-H1-CP**, reached the 16,000 generated-token ceiling
with thinking text and an empty final answer. The frozen terminal rule stopped
execution before the eight-call delivery checkpoint or any fresh-family calls.
The decision is **`incomplete_no_advancement`**. The unused eighteen slots are
not an automatic continuation or retry allowance.

The five completed reports selected all fifteen primary target opportunities and
gave the expected support labels. Grounded usability was **SA 6/6** and **VA
8/9** on completed reports. One VA explanation lacks evidence for the observed
psychic pull in its returned citation set. There are **zero observed admission
recoveries**, one paired loss of grounded usability, and no observed primary
support-label errors. These are partial historical-case observations, not a
completed comparison, fresh-case generalization or production qualification.

The [frozen plan](../handoffs/reviewer-premise-admission-frozen-plan-2026-10-31.md)
and [preceding local audit](../handoffs/cw013-admission-preparation-2026-10-31.md)
remain unchanged. Plan SHA-256:
`758e951f75410bb97b71ffabbb112779fedcbc87f54dc725a9fc615c6508ad0e`.

## Execution and the terminal event

The user approved full fictional prose/context, complete reports and admitted
spans sent to Ollama Cloud through the local daemon. Six scheduled requests were
reserved and dispatched in order, three per condition. No request, source,
sampling setting, scoring rule, resource limit or stop rule changed. No retries,
replacement calls, output repair or budget reallocation occurred.

| Scheduled call | Result | Generated tokens | Active seconds |
| --- | --- | ---: | ---: |
| A-SA-H1-PC | Valid final report | 15,335 | 39.09 |
| A-VA-H1-PC | Valid final report | 6,060 | 17.95 |
| A-SA-H2-CP | Valid final report | 11,729 | 31.37 |
| A-VA-H2-CP | Valid final report | 4,173 | 11.78 |
| A-VA-H1-CP | Valid final report | 2,954 | 9.10 |
| A-SA-H1-CP | Terminal: length, empty final | 16,000 | 52.79 |

Every raw response returned HTTP 200. The final response reports `done: true`,
`done_reason: length`, 14,256 input tokens and 16,000 generated tokens. Its final
`content` is empty; its `thinking` field contains 75,181 characters. Character
counts do not establish a reasoning/final token split. The supported observation
is that the generated-token limit was reached before a final answer was delivered.
There was no HTTP 500 or other observed service-unavailability response in this run.

The gateway rejected the empty final content before the runner could create a
normal receipt. Its preserved error chain is:

1. `ModelGatewayError`, code `invalid_response`: “Ollama response metadata is invalid”.
2. Caused by `ValueError`: “response content must not be empty”.

The outer message alone obscures the length finish; the sealed raw capture
preserves it. The terminal record conservatively retains **unknown usage**, no
normal receipt, `retry_allowed: false` and `resume_allowed: false`. An independent
local supplement records the raw counters without rewriting that terminal record
or treating the response as successful. Billing remains unknown.

All calls requested `deepseek-v4.1-flash:cloud`, high thinking, temperature 0.2,
top-p 0.95, seed 20261022, context 40,000, non-streaming and no format override.
All **twelve captured daemon-version observations** matched **Ollama 0.40.13**:
one initial, six before dispatch and five after successful gateway returns.
There is **no post-call version observation for the terminal response**, because
the gateway raised before that step. Initial and six per-call model checks
matched the frozen digest and capabilities. Effective sampling is unverified.

## Inspection and partial results

The supported terminal-audit exporter verified the ledger and shuffled the five
completed reports. All **21 returned assertions/reasons and fifteen primary
targets** were inspected against the complete two drafts, assignment context,
declared source scope and relevant next-scene records. Notes were validated and
sealed before opening the trial key. Trial, condition and presentation-order
labels were hidden during annotation; familiar wording and response shape can
reveal condition. This is a partially masked assistant source audit, not blind
human preference review. Thinking text was retained but not read as scoring
evidence.

| Measure | SA | VA |
| --- | ---: | ---: |
| Attempted calls | 3 | 3 |
| Valid completed reports | 2 | 3 |
| Terminal deliveries | 1 | 0 |
| Unstarted calls | 9 | 9 |
| Returned assertions inspected | 12 | 9 |
| Admitted primary targets, completed reports | 6/6 | 9/9 |
| Correct primary labels, completed reports | 6/6 | 9/9 |
| Grounded usable targets, completed reports | 6/6 | 8/9 |
| Usable protected supported targets, completed reports | 5/5 | 6/7 |
| Usable targets against all 36 frozen opportunities | 6/36 | 8/36 |
| Fresh-family calls | 0 | 0 |

Terminal and unstarted cells remain in the frozen denominators, without being
described as observed semantic mistakes. An empty final answer is a delivery
failure, not evidence that the model omitted a particular premise. No eight-call
sentinel decision was reached. The original admission screen required all 24
valid deliveries, 36 usable VA targets and recoveries across multiple families,
including a fresh family; none of those completion requirements is satisfied.

Both completed H1 conditions reject the unsupported allegation that Elena
bypasses the assigned decision. Her deliberate journal retrieval and comparison
establish that decision. Both preserve the independently valid no-match endpoint
violation and the ten-year date realization. The self-admission report selects
the missing-decision allegation itself, so its VA counterpart is not an admission
recovery. VA also gives the correct three H1 judgments in the other presentation
order, but its SA partner has no final answer.

For H2, both completed reports identify the genuine entry violation, the already
fulfilled decision and the touch/pull events. SA covers the protected entry
comparison using an equivalent occurrence in the issue assessment rather than the
authored target's boundary field. The inspection accepts that complete equivalent
proposition. Repeated formulations of one premise receive only one target credit.

### The citation gap

**A-VA-H2-CP**, masked as `premise-review-002`, correctly labels the combined
touch/pull claim supported. Its citations are:

- **S316:** the assignment requires touch and a psychic pull; this is an obligation.
- **S336:** Elara grips the stroller handle; this establishes the touch.

The observed fixed pull is in **S337**, and its magnetic description appears in
**S339**. Neither is in this assessment's citation list. Its reason additionally
places both events in paragraph 9, while the fixed pull occurs in paragraph 10.
The complete source supports the label, but the returned evidence does not cover
the second event. This fails grounded usability and produces the one paired
protected-target loss; the matched SA report cites the relevant passages.

This is an evidence-coverage/localization failure. It does not show that the
psychic pull was absent, invent a new story event, or justify prose repair. The
inspection records no material story-premise or support-label reversal. It keeps
correct labels, adequate evidence and materiality separate.

Two lesser precision observations remain explicit in the notes. The H1 SA
achieved-state reason assigns the claustrophobic shift to S310 instead of S309,
but cites both passages and supports the complete state. The H1 VA/CP date reason
quotes “Ten years” without citing its separate S308 paragraph; its cited date
comparison and reaction already support the realization, and the full source
confirms the quotation. These do not receive the same missing-event-evidence
classification as the H2 citation set. Authored example witnesses were never an
exhaustive mandatory citation list.

### Additional selected allegations

SA also inspects ordinary report statements outside the primary target set. It
separates assignment obligations from their fulfillment and preserves the actual
match/entry violations. Two additional rejections are supported under the literal
source-entailment reading used in the notes:

- H1's general handwriting match does not establish the specifically named
  verification of an idiosyncratic flourish in the next scene's turning point.
- H2's scene-2 entry-state affect does not establish that entry is already
  completed when that scene begins; its summary describes entering during it.

These are inspected extra allegations, not new frozen targets or counted
recoveries. In particular, the first does not settle whether an early general
match reduces the later scene's dramatic value. Source verification must not
convert a debatable pacing judgment into a mandatory story edit.

## Resources and interpretation

| Resource, including the terminal attempt's raw observations | SA, three attempts | VA, three attempts |
| --- | ---: | ---: |
| Raw reported input tokens | 43,777 | 44,149 |
| Raw reported generated tokens | 43,064 | 13,187 |
| Active request seconds | 123.25 | 38.82 |
| Completed reports | 2 | 3 |

The five validated receipts account for **73,670 input / 40,251 generated tokens**.
Adding the separately verified terminal raw counters gives **87,926 input /
56,251 generated tokens / 162.07 active seconds** across all six attempts.
The archived-rate reference is **$0.093879**, not actual billing or a verified
current tariff. The canonical terminal usage remains unknown; the supplement is
explicitly a raw-counter observation. Thinking/final token splits remain unknown,
and generated tokens are counted once. All per-call input/time and aggregate
reservations remain within the frozen limits; the sixth response reached the
output limit and triggered the truncation stop.

The two completed SA reports use more generated tokens and active time than their
paired VA reports. SA also selected eight and four assertions, versus three each
for VA. The third SA attempt consumed its allowance without a final report. This
is evidence that the tested combined selection-and-assessment task can exhaust
this budget. It is **not** evidence of a particular internal reasoning mechanism,
a stable cost ratio, a model-wide incapacity, a provider fault or a proven benefit
from lower thinking. Both conditions used high thinking; no thinking-mode contrast
was run. The complete historical input packets and their hundreds of reference
entries are another potential workload factor, not an isolated causal finding.

## Verification and next work

The post-run verifier replays the five receipts, all six frozen wire requests,
raw response hashes, terminal chain/seal, twelve version observations, seven
model checks, export/source bindings, all annotations, scoring and accounting.
It verifies that ordinary continuation is refused after the terminal stop. Real
HTTP is blocked during this replay. All **100 frozen bundle files and 397
historical/runtime fingerprints** remain unchanged, including the production
Python baseline and fourteen issue bodies. **252 offline regression tests pass
again:** 198 current/export/version tests in 52.51 seconds and 54 prior-admission
tests in 2.54 seconds. Ruff lint/format and strict mypy pass on the nine frozen
scripts and the separate result verifier. No production code changed; unrelated
application/frontend build suites were not rerun. Verification records remain
with the analysis.

Retain the completed historical judgments as limited diagnostic evidence. They
show that SA can select the known missing-decision premise in one presentation,
and that supplying spans does not guarantee complete citations. They do not
justify adopting either condition or closing CW-013.

Before another live run:

1. Preserve the empty-final, length-finished response as a local delivery fixture.
   Audit how the terminal exporter can expose trustworthy raw usage and finish
   metadata separately from receipt validity, while preserving unknown billing,
   the original error chain and the no-resume rule.
2. Preserve the H2 matched citation contrast. Audit coverage of each factual
   component without substituting an assignment obligation for an observed event
   or treating a correct label as a complete explanation.
3. Audit SA's workload locally: repeated premises, scope of obligations versus
   repair allegations, source-index size and the separation of premise selection
   from assessment. Only then propose a bounded amendment with an explicit
   resource hypothesis and unchanged controls. Do not simply increase limits or
   spend the eighteen unused slots under this stopped plan.

No additional inference is required to establish the captured length finish or
the citation gap. No production prompt, graph, schema, writer route, source truth
or story prose changed. Human review retains feel, flow, character and
story-breaking judgments; the Blueprint checkpoint and nine earlier human ties
remain unchanged. No external issue was edited or closed. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**

Private evidence:

- `data/diagnostics/reviewer-premise-admission-v61-2026-10-31/`: frozen plan and approval.
- `data/diagnostics/reviewer-premise-admission-v61-2026-10-31-live/`: six attempts, five receipts and terminal evidence.
- `data/diagnostics/reviewer-premise-admission-v61-2026-10-31-inspection/`: shuffled reports, key and sealed notes.
- `data/diagnostics/reviewer-premise-admission-v61-2026-10-31-analysis/`: dispositions, decoded notes, results, raw-counter supplement and verification.
