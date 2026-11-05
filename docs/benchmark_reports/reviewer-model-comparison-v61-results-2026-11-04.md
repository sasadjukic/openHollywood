# Terra/Sol/Astra reviewer comparison results — 2026-11-04

The approved comparison completed once: **24/24 valid attempts, zero retries**.
All **186 fixed judgments** and **385 evidence witnesses** were inspected.
At high reasoning, **Terra grounded 62/62 judgments; Sol and Astra each grounded
60/62**. All three eliminated the citation failures seen in the saved Luna-high
comparison. Sol and Astra's remaining disagreements concern the same H1 claim's
specific-event versus editorial-payoff interpretation, in both presentations.

All three pass the **frozen historical replication screen**. That screen permits
an existing semantic disagreement to remain; it is not a requirement for perfect
scores or a production qualification. Terra is the strongest narrow assessment
candidate in this run, with the highest frozen score, lowest observed latency and
lowest reference cost among the three contemporary models. This is not evidence
that it is the best writer or universally the best reviewer.

Production prompt **61**, graph **9**, fulfillment policy **1**, model profiles
and writer routing remain unchanged. No story was revised. Live calls are
**PAUSED**; the sixteen-call interpretation diagnostic and full workflow canary
remain **ON HOLD**. All fourteen tracked issues remain open.

## Execution and immutable scope

The user approved the [frozen plan](../handoffs/reviewer-model-comparison-frozen-plan-2026-11-04.md)
with full prose/context. Its plan SHA-256 remains
`2b38b3c1dc0ac9c3440ed97475dbe6adf260d15a3746f74f59ba481f2328bedc`.
All **37 frozen preparation files / 4,635 historical source fingerprints** remain
unchanged. The exact approved runner was invoked once, from
**22:18:33 to 22:39:04 UTC on November 4**. There were:

- **24 generation dispatches**, eight per model, and **24 story-bearing input
  counts** at the two approved OpenAI endpoints;
- **24 catalog preflights**, no extra smoke generation and no fallback;
- **48 authenticated count/generation request bodies**, all matching the freeze,
  and **48 HTTP 200 responses**;
- no terminal stop, retry, truncated final, invalid structured output, unknown
  usage, unstarted slot or remaining allowance.

Requests used `gpt-6.1-terra`, `gpt-6.1-sol` and `gpt-6-astra`, all at **high**.
Only `/model` differed between their count/generation bodies. The source context,
selected claims, instructions, native U section-locator schema and resource limits
were identical to the saved Luna-high controls: **24,000 input tokens, 32,000
generated tokens including reasoning, and 600 active seconds per attempt**.
The account and adapter successfully delivered this exact native output shape
for all three models; this does not certify other workloads or configurations.

Four existing families, H1/F3/F7/F8, supplied eight presentation blocks and
**62 fixed judgments per model**. F7/F8 are reused controls, not new generalization
evidence. H1-PC and H1-CP select different claims, so their contrast cannot isolate
a pure presentation-order effect.

## Frozen scores

“Grounded” requires a correct whole-claim judgment and materially accurate reason,
complete citation binding, and adequate selected evidence. A valid response alone
does not earn credit. Categories retain the frozen precedence: unavailable,
semantic, citation-only, grounded.

| Condition | Grounded / 62 | Citation-only | Semantic | Unavailable | Fully grounded responses / 8 | F7/F8 grounded / 32 |
|---|---:|---:|---:|---:|---:|---:|
| Terra high | **62** | 0 | 0 | 0 | **8** | **32** |
| Sol high | **60** | 0 | 2 | 0 | **6** | **32** |
| Astra high | **60** | 0 | 2 | 0 | **6** | **32** |
| Saved Luna high — historical | 53 | 7 | 2 | 0 | 3 | 29 |

The three current models agree on **60/62 matched slots**. All F3/F7/F8 judgments
are grounded for every model, in both presentations. H1 is **14/14 for Terra** and
**12/14 for Sol and Astra**. All three H1-CP contextual relations pass separate
source inspection: the actual match and no-match obligation are both located,
with their original relation retained. This is not automatic support aggregation
from the two member labels.

Against saved Luna high, every model recovers all **seven citation-failure slots**
across **six distinct family/whole-claim identities**, with no grounded, new
semantic or contextual loss. Terra additionally recovers the two H1 private-event
slots, one distinct claim. Thus Terra has **seven distinct recoveries**; Sol and
Astra each have **six**. All also ground all 32 reused F7/F8 slots, satisfying the
remaining frozen screen condition.

The contemporary screens must be read separately. Sol-versus-Terra and
Astra-versus-Terra fail: each has the same two semantic losses and no recovery.
Astra-versus-Sol also fails the improvement screen because there is **no recovery
at all**, not because Astra is worse on the scored judgments. Their classifications
are identical. No model-tier hierarchy is established.

## What changed, and what remains unresolved

### Citation binding and coverage recovered together

Every returned witness locates: **136/136 Terra, 119/119 Sol, 130/130 Astra**.
There are **zero unavailable-field, missing or ambiguous witnesses**. No locator
was repaired, discarded or replaced after the run. Source inspection separately
found adequate coverage for all 186 judgments, including the four interpretation
disagreements; their category is semantic, not citation-only.

This addresses several concrete earlier problems within these captures:

- H1's decision and exit-state statements now cite the operative assignment
  fields. The present comparison cites the actual draft rather than a similarly
  named plan field. Dates and explicit realization are covered together.
- F7's absent private calibration is evaluated with both its planned defining
  steps and the current general identity check. Successful location no longer
  hides missing coverage of that current check. Reasons stay within the complete
  draft's depiction; they do not invent an explicit refusal or off-page event.
- F8's speaker attribution uses a valid locator for the paragraph containing
  Tomas's proposal and Eda's refusal. The previous compressed, noncontiguous
  quotation failure does not recur.
- F3's actual private procedure is recognized through paraphrase. All three
  models also preserve its outside opening in the next plan, correct attribution,
  purposeful decision and independent current boundary violation.

A quote remains a **locator for a complete immutable field or one prose
paragraph**, not necessarily a self-contained proof. For example, F3's S051
already contains both dates; S051 plus the realization paragraph is adequate.
Extra valid context citations do not automatically fail a judgment, and authored
example references are not an exhaustive whitelist. These results therefore do
not establish that the models could satisfy a different quote-as-complete-evidence
contract.

### The remaining H1 disagreement is explicit interpretation

The complete claim is:

> The draft consumes the turning point of Scene 2 ('The verification of an idiosyncratic flourish') by establishing the match in Scene 1.

Frozen gold treats this as a **specific-event claim**. The draft establishes a
general handwriting match, but does not depict the particular private-flourish
procedure specified for Scene 2. Accordingly, the frozen answer is unsupported.

| Exact slot | Terra | Sol | Astra |
|---|---|---|---|
| H1-PC / Q006 | Unsupported; grounded | Supported; semantic | Supported; semantic |
| H1-CP / Q007 | Unsupported; grounded | Supported; semantic | Supported; semantic |

Terra explicitly separates the general match from the particular flourish. In
CP it also allows that an early match may encroach on later verification without
establishing that specific event. Sol and Astra explicitly interpret “consumes”
as **structural payoff or pacing preemption**, and say that this reading does not
require literal depiction of the private test. They locate both the private plan
and the actual general match correctly.

These are four failures against the original frozen criterion. They are **not
evidence that those responses falsely reported seeing the flourish test**, nor
that the models cannot distinguish a general check from a particular procedure:
all three correctly distinguish F3's performance, F7's absence and F8's explicit
nonperformance. Their final answers instead show a different interpretation of
this mixed factual/editorial claim. Hidden reasoning was not inspected and no
internal mechanism is inferred.

There is a real design question here: a factual gate should not turn a plausible
editorial concern into a false assertion about an event, but it should not erase
useful pacing criticism either. The original score is retained. Under a separate
editorial reading the alleged error needs a different assessment; no alternative
score or automatic edit permission is substituted after seeing results. Excluding
the two interpretation-sensitive slots descriptively leaves **60/60 for every
model**. This sensitivity observation is not the primary score or a new screen.

All three models also preserve the no-match obligation without the unsupported
reversible-match exception observed previously at Luna max. This does not resolve
the broader production question of how free-form exit states should represent
event-history prohibitions versus closing beliefs.

One frozen annotation dictionary has a clerical index mismatch: it calls
H1-PC/Q007 the private-event contrast, whereas **Q006 is the private-event claim
and Q007 is the date claim**. This was recorded before new-response inspection.
The exact claim text, gold, evidence criteria and scorer use the correct identities
and were unchanged. The report and notes follow those identities.

## Latency, tokens and reference cost

| Condition | Input tokens | Generated tokens | Included reasoning | Median active seconds | Maximum generated / 32,000 | Reference cost, USD |
|---|---:|---:|---:|---:|---:|---:|
| Terra high | 68,565 | 18,753 | 6,860 | **26.74** | 3,118 | **0.17947125** |
| Sol high | 68,565 | 24,639 | 10,154 | 44.03 | 3,733 | 0.41780250 |
| Astra high | 68,565 | 27,180 | 12,069 | 57.87 | 4,569 | 2.21606250 |
| Saved Luna high — historical | 68,565 | 37,290 | 24,719 | 36.69 | 6,024 | 0.027215625 |

Current totals are **205,695 input / 70,572 generated / 29,083 included reasoning
tokens**, **1,058.92 active seconds** and **20.53 minutes runner wall time**.
Reasoning is a subset of generated tokens and is not charged twice in the
calculation. Usage counters were known and internally consistent for every
attempt. The provider reported **22,737 cached input tokens** across the run.
The conservative frozen cost calculation does not subtract cache discounts.

The total **$2.81333625 reference cost** is within the **$19.76 max-token reference
reservation / $31.20 planning allowance**. It uses the frozen model rates and
1.25 input-charge multiplier; it is not an invoice. **Actual billed cost remains
unknown.** No new pricing assumption is needed to score this completed experiment.

For the eight contemporary matched blocks, median per-block ratios versus Terra
are **1.40× latency / 1.24× generated tokens / 2.29× reference cost for Sol**, and
**2.08× / 1.38× / 12.34× for Astra**. Astra versus Sol is **1.38× latency / 1.10×
generated tokens / 5.28× reference cost**, with identical scored outcomes.
Per fully grounded response, the reference costs are approximately **$0.02243
Terra, $0.06963 Sol and $0.36934 Astra**; these divide all eight attempts' cost by
the usable-response count and are not promised future prices.

Historical matched latency ratios versus Luna high are **0.71× Terra, 1.00× Sol
and 1.45× Astra**; generated-token ratios are **0.50×, 0.64× and 0.69×**. Reference
cost ratios are **6.27×, 14.92× and 78.00×**. Thus fewer generated tokens did not
mean lower dollar cost than Luna. These historical ratios are descriptive:
service conditions, caches and model deployments were not controlled across runs.
Equal `high` labels also do not promise equal internal compute across models.

The largest current response used only **4,569/32,000 generated tokens**, and the
longest active attempt was **94.92/600 seconds**. Delivery headroom does not explain
the remaining disagreements. This run does not justify shrinking production
limits, because longer contexts and other tasks were not tested.

## Evidence, verification and limits

Private evidence remains under:

- `data/diagnostics/reviewer-model-comparison-v61-2026-11-04/` — frozen requests,
  cases, gold, scoring, source pins and exact approval;
- its `-M-live/` sibling — ledger, exact dispatch hashes, sanitized HTTP captures,
  final responses, usage, receipts and immutable seals;
- its `-analysis/` sibling — all 24 source packets, 186 explicit claim notes,
  three relation inspections, readable `inspection-ledger.md`, original scoring,
  pairwise results, witness inventory and verification records;
- `reviewer-model-comparison-v61-2026-11-04-operator-execution.json` — one runner
  invocation, approval scope and exact start/end times.

Packets were inspected in the predeclared SHA order, with model/resource fields
omitted from the views, and every note was saved before model/resource decoding.
This is **assistant source inspection, not fully blind human review**: the operator
could see the execution schedule/status, and familiarity could reveal conditions.
No model grader or hidden-reasoning inspection was used.

**354 applicable offline tests pass**: 323 frozen/tracked checks and 31 result
checks. Only the unchanged preparation-only assertion that no live run exists is
deselected; all preparation checks passed before execution. Repository Ruff,
format and strict mypy pass for **224 Python files**, as do separate checks for
**eleven frozen and seven analysis scripts**. No frontend code changed, so frontend
build/tests are not applicable to this capture-and-documentation task.

The checks authenticate fixed-slot coverage, each saved request and response,
approval, witness replay, exact frozen scores, contextual inspection, resource
totals, zero retries and immutable inspection order. The initial result-verification
record retains one lint finding: an overlong explanatory string in the new verifier.
Wrapping that string resolved it; corrected static checks pass. The already-passing
tests were retained without unnecessary repetition. No score, observation, request
or capture changed. Both verification records remain in the analysis directory.

The [saved Luna reasoning results](reviewer-reasoning-effort-v61-results-2026-11-04.md)
are an exact-request **historical** comparator, not a concurrent efficient-model
arm. DeepSeek's earlier tests used different designs, provider/schema conditions
and workloads; this run supplies no matched numerical Terra/Sol/Astra-versus-
DeepSeek estimate. Four reused families, one sample per model/block, and one
interpretation-sensitive claim do not establish broad model superiority,
repeatability, fresh-family generalization, literary judgment or writer preservation.
Successful source assessment does not authorize a rewrite.

## Recommended next steps

1. **Preserve the paired evidence locally.** Turn the complete recovered citation
   controls, Terra's H1 pair and Sol/Astra's four interpretation disagreements
   into regression fixtures, retaining the full context, original reasons and
   original scores. Keep successful controls as well as failures.
2. **Audit factual and editorial assessment scope explicitly.** Separate “the
   particular procedure occurred” from “the earlier general revelation may reduce
   the later scene's payoff,” retaining both observations and the independent
   endpoint violation. Keep pacing impact and edit necessity open to story-quality
   evaluation. Do not hard-code an interpretation from model identity or a word
   such as “consumes.”
3. **Then revisit the held interpretation diagnostic.** Terra high is the leading
   candidate for a narrow, read-only factual-assessment component; Sol supplies a
   useful contrasting editorial reading. Before any further inference, locally
   justify the revised contrast and freeze its cases, exact claims, full-context
   requests, scoring and budget for approval. Include fresh families and unchanged
   controls before making a production-routing decision. Re-running the same three
   models merely to obtain a cleaner ranking is not warranted by these results.

This advances model selection for a bounded assessment task; it does not yet
qualify an autonomous critic/writer loop. No production change or additional live
allowance is authorized by this report. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; interpretation diagnostic ON HOLD; canary ON HOLD.**
