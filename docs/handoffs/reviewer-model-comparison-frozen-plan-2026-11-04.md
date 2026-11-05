# Terra / Sol / Astra: model comparison approval plan

Date: **2026-11-04**. **FROZEN AND VERIFIED LOCALLY; LIVE APPROVAL PENDING.**
Maximum **24 attempts, zero retries**, eight attempts per model. All models use
**`reasoning.effort: "high"`**. Production prompt 61, graph 9, fulfillment policy 1,
profiles and writer routing remain unchanged. The sixteen-call interpretation
diagnostic and full workflow canary remain **ON HOLD**.

This follows the completed [reasoning-effort comparison](../benchmark_reports/reviewer-reasoning-effort-v61-results-2026-11-04.md)
and [paired-regression, coverage and obligation audit](reviewer-effort-coverage-audit-2026-11-04.md).
The question is whether these three requested models handle the same reviewer
problems differently, and at what latency, token and reference-cost tradeoff.
No story is rewritten and no improvement in literary quality is inferred.

## Models and isolated change

| Arm | Exact model ID | Reasoning | Attempts |
| --- | --- | --- | ---: |
| Terra | `gpt-6.1-terra` | high | 8 |
| Sol | `gpt-6.1-sol` | high | 8 |
| Astra | `gpt-6-astra` | high | 8 |

Within every case/order block, **only `/model` changes in both the generation
body and input-count body**. Each also differs from the saved Luna-high body
only at `/model`. Full prose and planning context, critic report, admitted whole
claims, evidence contract, schemas, order, instructions and output cap remain
identical. Internal request/ledger identities and model-specific price records
change appropriately; those are not extra model instructions.

All three exact IDs document high reasoning, Responses and structured output.
These are reviewed, diagnostic-only model specifications; no production catalog
or profile is changed. Actual account availability and acceptance of the frozen
native schema remain unverified until approved execution.
[Terra documentation](https://developers.openai.com/api/docs/models/gpt-6.1-terra),
[Sol documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[Astra documentation](https://developers.openai.com/api/docs/models/gpt-6-astra).

Keep the U **section-locator** contract: an exact quotation locates one complete
immutable registry field or prose paragraph. The selected sections together must
cover every material premise of the claim and explanation. Location alone does
not establish coverage or truth; uncited neighbors are not silently included.
No source repair, softened claim, new interpretation instruction or simpler
schema is permitted.

Keep native strict output, default service tier, disabled truncation and
`store/background/stream: false`. No tools, previous-response state, pro mode,
model-specific prompting or requested extended cache retention. The adapter
omits temperature, top-p and seed identically. Equal `high` settings do not imply
equal internal compute or generated-token counts; those are measured outcomes.

## Comparisons and limits

The primary comparison is **contemporary Terra versus Sol versus Astra** on
identical inputs. Report all three matched pairs, including losses in either
direction; Terra is a reference for reporting, not a presumed quality floor.
Marketing tiers are not treated as a measured outcome.

Separately compare each model against **the saved Luna-high results**: 53/62
grounded, seven citation-only failures and two semantic failures. Those requests
match apart from model identity, but were executed earlier. The comparison is
historical and descriptive, with no fresh Luna repeat or concurrent efficient
control. It cannot by itself establish a causal or general frontier-versus-
efficient advantage. Saved Luna xhigh/max results may appear as labeled context,
not substituted for the high baseline.

DeepSeek's earlier experiments differ in requests, provider, schemas and other
conditions. They supply failure history, **not a matched numerical comparator**
in this run. A direct DeepSeek-versus-OpenAI claim is outside this design.

## Cases and schedule

Reuse all cases and exact claims from the 24-attempt reasoning test:

| Family | Claims per order block | Protected contrasts |
| --- | ---: | --- |
| H1 | 7 | General authentication versus specific private procedure; assignment obligation versus observed overrun; no-match qualification; multisection evidence |
| F3: The Bell Without a Boat | 8 | Procedure fulfilled through paraphrase; plan-opening reference type; touch/vibration and date coverage |
| F7: The Public Gauge | 8 | General identity check versus a specific calibration not depicted; missing current-check coverage; attribution and actual overrun |
| F8: Seeds for the Empty Plot | 8 | Explicit denial of private verification; incorrect attribution; compressed quotation; inside opening and actual overrun |

Four families × two source-order blocks × three models = **eight matched
triples / 24 attempts / 186 fixed judgments**, **62 per model**. F7/F8 account
for 32 judgments per model. They were fresh in the earlier experiment and are
**reused controls here**; this run adds no held-out scene families.

PC presents prose before planning/context; CP reverses those groups. Both contain
all sources. H1's historical PC/CP claims differ and remain unchanged: compare
models within those blocks, not their difference as a pure order effect.
F3/F7/F8 use identical claims across orders. Claims and reordered presentations
are not independent stories.

| Block | Within-block sequence |
| --- | --- |
| F7-PC | Terra → Sol → Astra |
| H1-CP | Sol → Astra → Terra |
| F3-CP | Astra → Terra → Sol |
| F8-PC | Terra → Astra → Sol |
| H1-PC | Astra → Sol → Terra |
| F7-CP | Sol → Terra → Astra |
| F8-CP | Terra → Sol → Astra |
| F3-PC | Astra → Sol → Terra |

This maps the previous schedule onto model arms and uses all six permutations.
Eight blocks cannot perfectly balance first position. Calls are sequential with
no adaptive reordering, extra repeat or replacement. Cache and service-load
variation limit latency attribution.

## Frozen scoring and inspection

Preserve the original per-claim gold and adequate-evidence criteria. Classify
all **186 fixed slots**, including invalid and unstarted deliveries, in order:
**unavailable → semantic → citation-only → grounded**. Invalid output receives
no partial credit. Wrong labels or materially unsupported explanations are
semantic failures; correct judgments with unresolved, irrelevant or incomplete
evidence are citation-only. Grounded requires both semantic correctness and
adequate, precisely located evidence.

Record binding, section coverage, whole-claim label and material explanation
separately. Authored example witnesses illustrate adequate evidence without
excluding other valid choices. Inspect H1's contextual relation independently;
correct components do not automatically earn relation credit.

Keep interpretation-sensitive observations visible without rewriting scores:

- H1's private-procedure claim retains its specific-event gold. Record separately
  whether a reason instead judges broader editorial overlap. A plausible pacing
  concern has no factual story-quality gold and grants no rewrite authority.
- H1's no-match condition retains the frozen obligation judgment. Report any
  closing-belief/reversal exception separately. The audit's hypothetical temporal
  contrasts are not new scene facts or permission to reinterpret the score.
- F3 protects fulfillment through paraphrase. F7's missing depiction differs
  from F8's explicit denial. Purposeful action may fulfill a decision without a
  literal decision sentence. No invented off-page events.

Report absolute per-model delivery, semantic, binding, coverage, grounded and
fully grounded report totals; matched disagreements; distinct recoveries and
protected losses. Deduplicate recovery by **family plus exact whole claim**, not
by order or repeated claim fragments. A higher aggregate cannot erase a loss.

For continuity, apply the prior bounded replication screen to each model versus
saved Luna-high, explicitly labeled **historical**:

1. All 24 deliveries valid, with all eight complete triples.
2. At least two distinct semantic/citation failures recovered to grounded.
3. No grounded loss, new semantic loss or contextual-relation loss.
4. All 32 reused F7/F8 judgments grounded.

Report the same paired checks for Sol/Terra, Astra/Terra and Astra/Sol, alongside
the raw disagreements. Identical successes yield no recovery claim. Passing
supports only a candidate for bounded replication; it does not qualify production
adoption, autonomous edits, a model hierarchy or general efficient-model inferiority.
Failure remains informative about which error classes persist.

Inspect final-response packets in SHA-256 trial-ID order, hiding model and usage
where practical until notes are saved. This is assistant source inspection, not
a fully blind human study. No hidden reasoning is inspected or retained, and no
model grader or extra live call is allowed. Human story review remains about feel,
flow, character and story-breaking details.

## Resources and monetary allowance

Every attempt has the same **24,000 input-token / 32,000 generated-token /
600 active-second** limits as the reasoning test. Reasoning tokens are included
within generated output, never added again. The earlier max F3-CP response used
31,460 generated tokens; preserve that near-cap control without assuming how
these models will use the allowance. No cap increase after seeing output.

| Model | Standard input / output per million tokens | Reference maximum per attempt | Eight-attempt reference reservation | Planning allowance |
| --- | --- | ---: | ---: | ---: |
| Terra | $1 / $5 | $0.19 | $1.52 | $2.40 |
| Sol | $2 / $10 | $0.38 | $3.04 | $4.80 |
| Astra | $10 / $50 | $1.90 | $15.20 | $24.00 |
| **Total** | | | **$19.76** | **$31.20** |

Reference accounting charges all input at **1.25× standard input**, reserving
short-retention cache-write rates without assuming cache savings. No extended
cache retention, fast/ultrafast service, regional surcharge or pro execution is
requested. Published model rates are linked above. Actual account charges remain
unknown; these are conservative reference estimates and application allowances,
not an invoice or guaranteed account-level billing cap.

Total ceilings: **24 attempts/generation dispatches**, **576,000 input tokens**,
**768,000 generated tokens** and **14,400 active seconds**. Each model receives
eight attempts; there is no transfer of retired allowance. Unknown usage stays
unknown. Failed counts and interrupted generation reservations consume attempts.

Record input/cached-input, generated/reasoning tokens, output minus reasoning,
active count-plus-generation latency, wall time, finish status and reference cost.
Report sums, medians, maxima and resources per grounded judgment/fully grounded
report, including failed attempts and missing usage. Separate median paired
ratios from ratios of totals, and historical Luna ratios from contemporary pairs.
Output minus reasoning is not guaranteed to equal visible final-text tokens.

## Approval and terminal stops

Approval must explicitly cover full unpublished fictional prose, complete
planning/context, critic reports, registries and exact admitted claims at both:

- `https://api.openai.com/v1/responses`
- `https://api.openai.com/v1/responses/input_tokens`

At most **24 preceding story-bearing counts and 24 catalog preflights**, in
addition to at most 24 generations. A count and generation share one attempt;
this is not permission for 48 generations. No smoke generation, retry, model
substitution, simplified schema, fallback or replacement. Prior live approvals
and retired budgets do not authorize this run.

Reuse the already authorized application key only through its existing secret
store. Preparation checks presence without displaying or loading the key for
inference; it makes **zero catalog, count or generation calls**. Public official
documentation was consulted without sending story material. At execution,
recheck the selected model before each reserved attempt; reject unexpected
response identity. No immutable snapshot is selected, so alias drift remains a
limitation. Requested model IDs are never silently substituted.

Stop **all three models** on the first malformed/empty/duplicate/missing/extra/
changed-claim delivery, malformed evidence, refusal, truncation, unsupported
schema/effort, transport/auth/quota failure, unknown/inconsistent usage, resource
overflow, secret-boundary failure or frozen request/source/runtime/model drift.
Preserve final data, error chain, terminal status and unknown usage; invalid
answers earn no partial credit. Schema-valid unresolved citations are measured
outcomes, not delivery stops. Semantic errors alone do not terminate the run.

The runner holds an exclusive lock, captures exact outgoing body hashes,
reserves before transport, detects interrupted preflights/reservations and retires
unstarted slots without terminal resume. Successful completion also exhausts the
allowance; rerunning cannot generate another set.

## Local verification and freeze

Private bundle: `data/diagnostics/reviewer-model-comparison-v61-2026-11-04/`.
Plan SHA-256:
`2b38b3c1dc0ac9c3440ed97475dbe6adf260d15a3746f74f59ba481f2328bedc`.
The freeze binds **37 preparation files and 4,635 source fingerprints**, including
all exact requests, case/work versions, gold, schedule, budget/stops, model specs,
scoring, runtime, regression provenance and verification. No approval file or
live directory exists.

**324 offline tests pass:** 162 diagnostic, 123 tracked assessment work/result
tests and 39 provider/routing/execution tests, with no deselections. Repository
Ruff, formatting and strict mypy pass for **224 Python files**; all **eleven
private scripts** pass their checks. Preparation, fixed inspection slots and the
source/contrast audit reproduce byte for byte. Exact commands and output hashes
are retained in `verification-corrected.json`.

The initial complete pass had 315 passing tests but one missing local Counter
type annotation. That annotation was corrected and nine model-specific mocked
catalog checks were added before the final 324-test pass. Initial verification
and logs remain preserved. The initial Windows sandbox asyncio startup hang was
interrupted without provider calls; offline checks completed outside that sandbox
with guarded transports and synthetic credentials. No frontend changed, so
frontend checks are inapplicable; the full repository test suite is not claimed.

The checks cover all actual model/count adapter wires, model-specific price bounds,
full-context/schema identity, exact source and claim binding, all 24 historical
capture replays and their 400 unchanged witness outcomes, output/schema/usage
failures, model substitution, shared ledger/terminal behavior, fixed scoring and
deduplicated recoveries/losses. Tests use mocked transports and synthetic keys;
temporary databases are confined to tracked integration fixtures.

No production application, prompt, profile, schema, dependency or frontend change.
All fourteen issues remain open; issue bodies and posted URLs are preserved.
Step 19 remains **IN PROGRESS**, Step 20 **NOT STARTED**. Next is approval of this
exact freeze and both story-bearing endpoints, followed by one execution and
inspection of every fixed slot. Live calls **PAUSED**; interpretation diagnostic
and canary **ON HOLD**.
