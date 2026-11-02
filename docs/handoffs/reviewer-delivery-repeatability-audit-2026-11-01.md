# MA/PE delivery and baseline-repeatability audit — 2026-11-01

**Local audit complete. No model, daemon or database calls were made.** The PE
length termination, its semantic failure pair and the recovered MA controls are
preserved as replayable regressions. The evidence establishes answer variation
across identical visible MA requests. It does not identify the cause of that
variation or PE's generation demand. I recommend a **provisional twelve-call,
baseline-only repeatability diagnostic** before another presentation intervention.
Nothing is frozen or approved for that next diagnostic.

This follows the [MA/PE results](../benchmark_reports/reviewer-paragraph-excerpts-v61-results-2026-11-01.md).
All historical requests, results and scores remain unchanged. Production remains
**prompt61 / graph9 / fulfillment policy1**. Live calls are **PAUSED** and the full
workflow canary is **ON HOLD**.

## Preserved regressions

The local bundle is
`data/diagnostics/reviewer-delivery-repeatability-audit-v61-2026-11-01/`.
It preserves **258 exact capture/support files** from fourteen attempts:

- All ten MA/PE attempts, including the partial-final PE length stop and the
  H1/PC semantic pair. This retains all eight successful MA reports, including
  fresh C5/D6 positive and negative semantic controls in both presentation orders.
- The four original H1/H2 MA reports from VA/MA, paired with their recovered
  MA/PE controls. The historical failures are retained alongside the successes.
- Exact request/wire/raw/receipt/seal and metadata records, full source cases,
  frozen assessment units, original inspection notes, scores and stop rules.

The fixture register contains **87 source-bound judgments**: 75 grounded
successes, seven citation-only failures and five semantic failures. These are
saved inspection decisions, not new automatic entailment judgments. The five
semantic failures comprise four historical failures and the observed PE failure;
they do not represent five new independent failure classes. Four historical/current
contextual flags are retained separately. The length response has no valid
judgments and receives no semantic credit.

The export is byte- and modification-time-idempotent and rejects conflicting
existing files. The audit verifies **2,011 source fingerprints**, including all
**63 frozen MA/PE files and 1,751 prior source pins**. An independent source-map
replay checks **4,164 presented reference entries across the fourteen requests**,
with zero mapping errors. For the two dispatched PE requests it verifies all
**24 added paragraphs**, then removes only those additions and recovers the paired
MA wire exactly. The other 78 planned PE paragraph additions remain untested by
live inference; their original renderer verification is preserved.

## Delivery-resource findings

**E-PE-H2-CP** is a verified HTTP-200 generation-length termination. The final
response is 1,433 characters and cannot be parsed as complete JSON: it ends in
an unterminated string starting at character offset 1,410. The audit does not
repair the string, extract partial judgments or turn the provider counters into
a successful-delivery receipt.

| Saved observation | Value | Interpretation |
| --- | ---: | --- |
| Input tokens | 16,438 | Within the 24,000 reservation |
| Combined generated tokens | 16,000 | Exactly the limit; frozen arm retirement applies |
| Active elapsed seconds | 70.11 | Below the 600-second limit |
| Final characters | 1,433 | Partial JSON, no valid report |
| Thinking characters | 73,535 | Nonempty field; not a reasoning-token measurement |
| Cached input tokens | 13,696 | Provider-reported cache count, not a causal explanation |
| Input plus generated counts | 32,438 | Below requested context 40,000; not an attestation of internal context handling |
| Gateway error chain | Empty | No captured HTTP/transport exception |

The raw response and receipt agree on their counters and termination. Reasoning
and final-output token counts remain **unknown**, as does actual billing. Character
ratios cannot supply that split. Thinking text remains private and is excluded
from semantic evidence. The observation shows a generation limit was reached;
it does not show that the context window was exhausted, that the provider was
unavailable, or why the model spent that generation budget.

The paired MA H2/CP request delivered a valid report with 15,448 input / 7,318
generated tokens in 32.16 seconds. PE added 990 input tokens in that pair. In the
other attempted pair, H1/PC, PE added 673 input tokens while using fewer generated
tokens than MA (4,934 versus 7,561). That valid PE report nevertheless made a
semantic error. MA C5/CP used 14,975 generated tokens on a shorter 9,574-token
input and delivered successfully. Thus neither an excerpt-caused generation
increase nor a simple input-length explanation is established by these captures.

All ten current attempts retain known usage: **129,570 input / 90,283 generated
tokens / 399.48 active seconds**. The archived-rate nominal reference remains
**$0.1472106**, not an actual bill or current-price claim. No more inference was
used to investigate delivery. The six retired PE calls remain unused; this audit
does not release their reservation or authorize a retry, larger cap or new run.

## Baseline repeatability

For each historical H1/H2 source order, the old and new MA wire files are
**byte-identical**. Their source/version identities, selected quotations and
frozen per-claim support judgments also match. Saved before/after daemon versions
are 0.40.13; model checks are identical apart from their check timestamps. The
requested model, high thinking, temperature 0.2, top-p 0.95, seed 20261022,
40,000 context and 16,000 generation cap did not change.

| Identical MA request | Grounded judgments, old → new | Generated tokens, old → new | Cached input, old → new |
| --- | ---: | ---: | ---: |
| H1/PC | 6/7 → 7/7 | 8,229 → 7,561 | 13,056 → 0 |
| H2/CP | 3/5 → 5/5 | 12,970 → 7,318 | 512 → 512 |
| H1/CP | 2/7 → 7/7 | 7,861 → 11,812 | 512 → 512 |
| H2/PC | 2/5 → 5/5 | 11,641 → 8,698 | 512 → 512 |
| Total | **13/24 → 24/24** | **40,701 → 35,389** | Not a treatment assignment |

All four final answers changed. Across the 24 paired judgments, **four support
labels, all 24 reasons and sixteen citation lists changed**. The exact transitions
are thirteen retained grounded successes, seven citation-only recoveries and four
semantic recoveries. Correct labels therefore move from 20/24 to 24/24.

Three pairs recovered despite the same recorded cache count. One pair changed
cache count and also recovered. This record cannot establish a cache effect or
explain the variation solely by changed cache counts. A requested seed is not
proof of deterministic effective execution; no provider-effective sampling
attestation exists in these captures. There is no observed request, source or
captured-version change to explain the recovery, and no evidence here identifying
an unseen provider/model change as its cause.

These are **two observations of each of four exact requests, from two story
families**, collected in two sessions. Presentation orders, claims within one
report and repeated family material are not independent stories. The record
supports repeat variability, not a population reliability estimate or a durable
fix. Since no old citation failure recurred in the new MA controls, PE has no
demonstrated citation-recovery benefit.

## Semantic and whole-relation boundaries

The preserved **E-MA-H1-PC/Q006 versus E-PE-H1-PC/Q006** pair remains a semantic
contrast. The sources establish a general handwriting match and a valid breach
of the current no-match endpoint rule. They do not establish performance of the
next scene's specific private-flourish test. PE cites the correct source locations
but returns an unsupported positive judgment; MA correctly rejects that inference.
Exact location does not grant entailment. The historical starting-inside failures
and their recovered controls preserve the separate distinction between interior
location and a scene beginning after entry.

No historical score is repaired. The fixed MA/PE scoring still has one observed
paired regression and 49 absent PE slots counted as losses. The latter are five
slots from the length-stopped report and 44 unstarted slots, not 49 observed errors.

Both newer MA CP reports ground their selected components without explicitly
assessing the complete current endpoint relation. The older H2/CP report did
mention that relation, but with inadequate citations; the newer one does not
explicitly assess it. This is a change in coverage, not a lost previously grounded
relation. The older H1/CP report also lacked that complete comparison. Successful
selected claims do not authorize automatic whole-field aggregation, writer advice
or a claim that the complete reviewer is now reliable.

## Local verification

**271 offline tests pass:** 67 new saved-capture/boundary regressions, 46 existing
review-evidence tests, 84 delivery/usage regressions and 74 citation-mapping
regressions. Ruff lint/format and strict mypy pass on four local scripts.
The first verification recorded import-path/typing findings; those are corrected
and the successful verification is retained separately. Existing MA/PE result
replay and the new audit replay pass without changing sealed annotations or scores.

Tests reject corrupt or conflicting usage, terminal-result salvage, changed control
wires/source identities/gold, altered excerpts, ambiguous JSON, unsafe paths and
fixture overwrite. Real HTTP, sockets and database access are blocked in audit
and test execution. No production code changes, so no client build or live workflow
check is needed for this local diagnostic addition. All fourteen original issue
bodies and posted URLs remain unchanged.

Key bundle records: `fixtures-manifest.json`, `sources.json`, `regressions.json`,
`delivery-repeatability-audit.json`, `verification-attempt-002.json`,
`publication-checks.json` and `publication-closure.json`. Reproduce the read-only
audit from the repository root:

```powershell
$env:PYTHONPATH = 'engine;apps/api;apps/worker'
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-delivery-repeatability-audit-v61-2026-11-01/repeat_audit.py verify
```

## Proposed next step: baseline-only repeatability diagnostic

The next useful question is **whether the saved MA citation and semantic failures
recur within a deliberately replicated run at the current budget**. That question
differs from whether an excerpt intervention improves a single paired response.
The current evidence justifies measuring recurrence before selecting another
presentation treatment. Keep PE deferred; this proposal does not retry its stopped
cells or claim that additional thinking tokens would fix its delivery.

Provisional design, requiring separate local preparation and approval:

- **Twelve calls maximum:** the four exact historical MA wires, each repeated
  three times in fixed interleaved blocks. Both families and presentation orders
  remain. Freeze the order before execution; do not select repeats in response
  to results. No PE, selector, writer, fresh-family expansion or prompt change.
- Keep the original visible model/settings and per-call limits: 24,000 input,
  16,000 combined generated tokens and 600 seconds; requested context 40,000.
  Reserve at most **288,000 input / 192,000 generated / 7,200 seconds**.
  Fresh metadata capture belongs in preparation; any mismatch needs an explicit
  baseline amendment before inference. No new metadata request was made here.
- Freeze the same 24 per-block source judgments and evidence criteria: **72
  judgment slots**, including 21 occurrences of the seven historical citation
  targets and twelve occurrences of the four historical semantic targets.
  Retain all 39 occurrences of thirteen previously grounded units and separately
  all 60 occurrences of twenty previously label-correct units. Inspect the six
  contextual flags independently; labels do not imply relation coverage.
- Report each wire's valid-delivery count, failure recurrence, grounded result,
  reason/citation variation, tokens, cache counters and latency across its three
  new attempts. Distinguish citation-only failure from semantic error and from
  absence of a valid report. Keep historical observations separate from new-run
  counts and retain family clustering. No automatic reliability or promotion score.
- Continue across semantic failures to observe recurrence. Stop the diagnostic
  on the first invalid/empty/length final, transport or non-200 failure, unknown
  or conflicting usage, budget breach, metadata drift, missing required thinking,
  integrity mismatch or cancellation. Count the attempted call; keep unstarted
  slots in the denominator. **Zero retries or replacements.**
- If known failures recur, retain their per-wire frequency and co-occurrence as
  the baseline for a later, separately frozen intervention. If they do not recur,
  record bounded nonreproduction and defer another citation-presentation run.
  Neither outcome establishes production reliability or warrants a larger cap.

The fresh C5/D6 positives remain local regressions. A later generalization study
would need fresh families, but adding them now would reduce replication of the
specific unchanged requests whose behavior varied. Any next study is a new budget;
the retired six-call allowance stays closed. **No requests, budget or live approval
for this proposal have been created.**

Human literary review remains focused on feel, flow, character and story-breaking
details. Citation mechanics and factual support do not determine whether an edit
is necessary or emotionally effective, and the whole-relation coverage gap remains
open. CW-007/CW-008/CW-013 and all other issues remain open; no external issue was
edited. **Step 19 IN PROGRESS; Step 20 NOT STARTED; production prompts unchanged;
live calls PAUSED; full workflow canary ON HOLD.**
