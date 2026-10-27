# DeepSeek non-thinking/high-thinking comparison results — 2026-10-26

**Completed: 48/48 calls, 24 per mode, zero retries. High thinking recovers all
eight contemporary factual-relation failures across four families and both
presentation orders. The frozen overall decision remains
`retain_limited_evidence_no_advancement`.** Uncertainty labels and protected
explanation/citation losses prevent qualification despite the substantial gain.

Retain high thinking as useful diagnostic evidence for difficult relation review.
This does not justify enabling it throughout production, promoting this reviewer,
or claiming better stories. Production **prompt 61 / graph 9 / fulfillment policy
1** remains unchanged. Further inference is **PAUSED**; the canary stays **ON HOLD**.

## Execution and scope

The user approved the [frozen 48-call plan](../handoffs/reviewer-thinking-mode-frozen-plan-2026-10-26.md),
including its full unpublished fictional prose/context payload to Ollama Cloud
through the local daemon. Plan SHA-256:
`8720cb520255a098e6f700b4fb9168c7421b89162d606e84a361932876d9b24a`.
No cases, claims, components, requests, gold labels, budgets, scoring or stops
changed after approval.

Both modes used `deepseek-v4.1-flash:cloud`: NC requested `think: false`; TH requested
`think: "high"`. Matched wire requests differed only in `think`. The twelve full-scene
families included seven known families and five fresh families, each in both source
presentation orders. Mode-first order was balanced across pairs. Shared caps were
24,000 input tokens, 16,000 total generated tokens and 600 active seconds per call.
The control messages were unchanged; the larger shared caps mean historical
non-thinking runs are not exact whole-wire performance controls.

All 48 calls returned HTTP 200 with a normal stop. The first-eight delivery sentinel
passed at 4/4 valid per mode. There were no terminal failures, truncations, retries,
extra probes, replacement calls or unspent cells. All 97 daemon-version observations
matched **0.40.11**; model metadata matched the freeze. All 24 TH responses contained
nonempty thinking output; all 24 NC responses had none. This verifies the observed
output distinction, not the provider's internal effort allocation. Requested
sampling settings matched; effective mode-dependent sampling remains unverified.

## Results under the frozen rules

| Measure | NC: thinking off | TH: high thinking |
| --- | ---: | ---: |
| Calls | 24/24 | 24/24 |
| Structurally valid reports | 23/24 | 24/24 |
| Usable target judgments | 8/24 | 16/24 |
| Correct whole-claim labels | 48/72 | 64/72 |
| Usable whole claims | 48/72 | 62/72 |
| Usable material components | 137/166 | 156/166 |
| Usable non-target components | 129/142 | 140/142 |
| Completely usable reports | 5/24 | 14/24 |
| H/U/G1/G2 false-acceptance recoveries | Eight opportunities | **8/8 recovered** |

Usability requires correct labels and complete, source-grounded final reasons and
citations. Invalid delivery stays in the denominator and earns no partial semantic
credit. Thinking text never rescues the final answer. The two TH whole claims
with correct labels but unusable explanations are H/C01 in the two orders.

| Family | NC usable targets | TH usable targets | NC usable whole claims | TH usable whole claims |
| --- | ---: | ---: | ---: | ---: |
| H: observatory, factual status versus early action | 0/2 | 2/2 | 3/6 | 4/6 |
| U: greenhouse, factual status versus early action | 0/2 | 2/2 | 4/6 | 6/6 |
| X: same-instant door contradiction | 2/2 | 2/2 | 5/6 | 6/6 |
| Y: unresolved photograph timing | 0/2 | 0/2 | 4/6 | 4/6 |
| F1: compatible sequential dark/light states | 1/2 | 2/2 | 3/6 | 6/6 |
| F2: same-instant pane contradiction | 2/2 | 2/2 | 5/6 | 6/6 |
| F3: unresolved inspection-card timing | 1/2 | 0/2 | 4/6 | 4/6 |
| G1: fresh letterpress, factual status versus early action | 0/2 | 2/2 | 4/6 | 6/6 |
| G2: fresh boathouse, factual status versus early action | 0/2 | 2/2 | 3/6 | 6/6 |
| G3: fresh same-instant hatch contradiction | 2/2 | 2/2 | 6/6 | 6/6 |
| G4: fresh explicitly unresolved photograph timing | 0/2 | 0/2 | 4/6 | 4/6 |
| G5: fresh measurements with no timing established | 0/2 | 0/2 | 3/6 | 4/6 |

Across known cases, usable targets rise from **6/14 to 10/14**, and usable whole
claims from **28/42 to 36/42**. Across fresh cases, these rise from **2/10 to 6/10**
and **20/30 to 26/30**. Both modes deliver all ten fresh reports validly. Repeated
orders are not independent families; this remains a small constructed diagnostic.

TH passes the delivery and eight-recovery screens. It passes eight of the sixteen
required target controls: X/F1/F2/G3 in both orders. It fails all eight uncertainty
controls in Y/F3/G4/G5 and incurs protected losses. Higher aggregate accuracy does
not override these frozen conditions.

## What changed with thinking

### The persistent factual-relation error recovers in every tested pair

NC falsely accepts the designated contradiction in all eight H/U/G1/G2 cells.
TH correctly rejects it in all eight while recognizing the separate real rule
violation and intention/action conflict. For example, in H it distinguishes
“not yet consulted” from rotating before consultation: those facts coexist; the
action instead conflicts with the earlier resolve to wait and the explicit rule.
The same distinction transfers to consultation before printing and authorization
before operating the winch in the two fresh families.

These recoveries satisfy the predeclared breadth requirement across all four
families and both orders. They are contemporary paired recoveries, not comparisons
with a selected historical result. The evidence supports a material operating-mode
effect on this relation task. It does not establish an internal mechanism, a
general model ranking, or a provider cause.

NC's erroneous labels conceal different explanation defects. H in both orders
and U/RO explicitly make a false contradiction inference. U/OR and G1/G2 in both
orders merely restate the compatible facts without establishing the requested
contradiction. The latter premises are true; their relation coverage is incomplete.
TH's target explanations correctly address the actual factual pair in all eight.

### Endpoint labels and craft judgments also improve, with limitations

Five valid NC endpoint components describe an actual assignment violation
accurately but label the violation proposition `unsupported`: X/RO, F2/OR,
F3/OR, G2/OR and G5/OR. TH correctly labels all five. This is a label/reason
alignment gain, not newly discovered evidence. It does not authorize the
application to repair future labels by interpreting free-text reasons.

NC abstains on H's mechanical/contrived reading in both orders and its voice-strain
reading in OR. TH accepts those qualified craft readings. The frozen criterion is
defensibility, not unique entailment; the NC explanations' observations that craft
is interpretive need not themselves be false.

Fifteen usable whole-claim gains and one loss produce the net gain of fourteen:
six U/G1/G2 relation claims, five endpoint claims, three claims from the F1/OR
delivery gain and H/OR's craft claim, minus F3/OR's uncertainty claim. H's two
recovered target components do not make C01 usable because of the explanation
defects described below.

### Uncertainty remains a separate failure class

Both modes return `unsupported` on every Y/G4/G5 target while accurately explaining
that common timing is not established. This preserves the disclosed historical
unsupported-as-unestablished interpretation. Under the frozen primary contract,
the correct label is `uncertain`; accurate explanations do not earn label credit.
These are not six TH assertions that the events definitely occurred at different
times. G4 expressly leaves alternatives unresolved; G5 simply lacks measurement
timing. The reasons generally preserve that difference.

F3 shows a further problem. NC/OR correctly returns `uncertain`; TH/OR changes it
to `unsupported` despite accurately describing unresolved timing, creating a
paired target and whole-claim loss. TH/RO returns `supported`: its reason acknowledges
that common timing is unresolved, then says the opposite states would be
incompatible at the same instant. That conditional truth does not establish that
these records actually contradict at one instant. Inspection records true
premises but incomplete target-relation coverage, alongside the wrong label.
NC/RO also has the wrong `unsupported` label, but its explanation addresses the
evidential limit completely.

The primary scores are not retrospectively changed. Even treating
unsupported-as-unestablished more permissively would leave TH/RO's unsupported
same-instant acceptance to resolve; the application must not equate all rejected
claims with disproved claims.

### Two protected craft explanations remain imperfect

In **M-TH-H-OR/C01.A03**, the craft reading is defensible, but the reason states that
R015 “directly follows” R012's vow. R013 and R014 intervene. The frozen source-truth
screen preserves that inaccurate adjacency statement as an explanation defect.
It is not evidence that a human would dislike the story.

In **M-TH-H-RO/C01.A03**, the reason invokes an unexplained reversal but cites only
R014/R015, the compatible status/action pair. R012 supplies the earlier resolve
needed to support that reversal and is missing from this component's citations.
It already appears elsewhere in C01, so adding it here would not increase the
whole-claim reference union. This is incomplete evidence, not an unavoidable budget
conflict. The audit does not assume that the ambiguous phrase “contrary rotation”
necessarily asserts consultation occurred.

There are **six overlapping protected-loss flags in four paired cells**: H/OR,
H/RO, F3/OR and F3/RO. They are not six independent failed calls. The H losses
concern explanation grounding; the corresponding NC craft labels were already
uncertain. A local sensitivity check forgiving both H annotations still produces
the same no-advancement decision because the uncertainty controls and F3 losses
remain. These precision judgments do not drive the overall conclusion alone.

### One normal-stop delivery is invalid

**M-NC-F1-OR** repeats `claim_id` twice in each of its three claim objects, with
identical repeated values. Strict parsing rejects the complete report. It is one
failed delivery containing three duplicate members. Its TH counterpart is valid.
The capture is preserved intact; no repair, trimming, partial semantic credit or
retry was used. One delivery gain is insufficient to establish reliability.

## Latency, tokens and cost interpretation

| Observed measure | NC | TH |
| --- | ---: | ---: |
| Median active call latency | 2.441 s | 10.323 s |
| Mean active call latency | 3.121 s | 10.997 s |
| Maximum active call latency | 9.618 s | 35.848 s |
| Total active call time | 74.901 s | 263.925 s |
| Reported input tokens | 199,748 | 200,348 |
| Reported generated tokens | 9,411 | 49,925 |
| Median generated tokens per call | 383.5 | 1,978.5 |
| Maximum generated tokens per call | 528 | 4,399 |
| Active seconds per completely usable report | 14.980 | 18.852 |
| Generated tokens per completely usable report | 1,882.2 | 3,566.1 |
| Input + generated tokens per completely usable report | 41,831.8 | 17,876.6 |

The median **paired TH/NC ratio** is **3.83× latency** and **4.81× generated tokens**.
The ratio of aggregate generated totals is **5.30×**. Ratios of medians, paired
ratios and ratios of totals are different statistics and must not be conflated.
The higher success count reduces the per-usable-report penalty: about **1.26×**
active time and **1.89×** generated tokens. Input-inclusive tokens per usable report
fall because 14 TH reports are fully usable versus five NC reports. These
denominators include all completed costs, including NC's invalid delivery.

Total usage is **400,096 input tokens, 59,336 generated tokens and 338.825 active
seconds**. Maximum single-call input is 8,884 tokens. All observed usage remains
within the frozen reservations. Active call time excludes metadata capture,
ledger verification and offline inspection; it is not total operator wall time.

Reasoning/final token breakdowns are **unknown for all 48 calls**. Do not call the
49,925 TH generated tokens “reasoning tokens,” infer a split from character counts,
or treat missing values as zero. Provider total-duration counters sum to 70.112
seconds for NC and 258.526 seconds for TH; separate prompt/load/generation timings
are absent. Reported cached-input counts total 4,480 and 5,632 respectively.
Cache/load differences and mode-dependent effective settings are not independently
controlled, so these resource measurements are descriptive of this run.

Archived-rate arithmetic gives **$0.191232** before cache discounts, below the
frozen $1.50 planning allowance. This is not confirmed billing or a current tariff.
There is no predeclared latency qualification threshold, and no automatic claim
that the accuracy gain is worth its cost in every workflow role.

## Inspection and verification

All **47 valid reports, 141 whole reasons and 326 component reasons** were inspected
against full original/revision/context. Notes bind exact assessment, source,
claim, component-map and registry hashes and exact source quotes. They were sealed
before the trial key was decoded. The export excludes thinking, arm/order/trial
identifiers and timing/usage. Scenes and answer style can still reveal conditions;
this is partially masked assistant source adjudication, not independent human
preference. The raw thinking remains in private captures and was not used to score
or repair any final answer.

**67 post-run offline tests pass**, including all 48 exact raw replays and frozen
wire comparisons, mode observations, budget/version accounting, invalid-delivery
rejection, complete sealed inspection, source tampering, eight recoveries,
uncertainty/conditional substitution, protected losses, score sensitivity and
resource denominators. Ruff lint/format and strict mypy pass on four analysis
scripts. Real HTTP is blocked in tests. The earlier 381-test preparation and all
3,678 historical source fingerprints remain intact. Production code is unchanged;
frontend/build checks are not applicable to this diagnostic/documentation change.

Private ignored artifacts:

- [Frozen bundle and approval](../../data/diagnostics/reviewer-thinking-mode-v61-2026-10-26/).
- [Raw execution and durable ledger](../../data/diagnostics/reviewer-thinking-mode-v61-2026-10-26-live/).
- [Sealed inspection, scores, resources and verification](../../data/diagnostics/reviewer-thinking-mode-v61-2026-10-26-analysis/).

The execution manifest, inspection export/notes, report, tracker and issue index
are hash-bound in the analysis closure. All fourteen issue bodies and posted GitHub
links remain unchanged; no external issue is edited or closed.

## Recommended next work

1. Preserve these captures as local regressions: eight paired recoveries with their
   real rule/intention controls; the duplicate-ID delivery; five endpoint
   label/reason disagreements; F3's conditional substitution; uncertainty-label
   outcomes; and the two H craft explanation defects. Keep successful genuine
   contradictions and sequential-state controls beside the failures.
2. Audit the epistemic contract and conditional-versus-observed claim locally.
   Clarify when a claim is disproved versus merely unestablished, and make the
   compared assertions and required timing explicit in evaluation records.
   Historical gold stays frozen. Application checks may expose mismatches or
   incomplete witnesses; they must not invent facts or silently rewrite labels.
3. Consider high thinking selectively for difficult claim/relation verification
   only after that audit. A later, separately frozen test should target the
   remaining uncertainty/conditional failure with unchanged high-thinking
   controls and fresh full-scene families. Lower thinking could be a separate
   resource hypothesis; do not combine new contracts, effort levels and writer
   changes in one unexplained treatment. No additional live budget is approved
   or frozen by this report.

There is no evidence here for enabling thinking in every role: no drafting,
planning, writer revision, full workflow or story preference was tested. The nine
prior human ties remain unchanged. Future human review should assess feel/emotion,
flow, character and story-breaking details with mechanics prepared by machines.
Provider attribution remains deferred. Step 19 stays **IN PROGRESS**, Step 20
**NOT STARTED**, live calls **PAUSED**, and the canary **ON HOLD**.
