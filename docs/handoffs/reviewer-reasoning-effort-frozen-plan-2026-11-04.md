# Luna high/xhigh/max comparison: approval plan

Date: **2026-11-04**. **FROZEN AND VERIFIED LOCALLY; LIVE APPROVAL PENDING.**
Maximum **24 attempts, zero retries**. The proposed
sixteen-call interpretation diagnostic is **ON HOLD**, as the user requested.
Production prompt 61, graph 9, fulfillment policy 1, profiles and writer routing
remain unchanged. The full workflow canary is **ON HOLD**.

This follows the [section-receipt and private-event audit](reviewer-section-receipt-audit-2026-11-04.md)
and the user's decision to test reasoning effort before changing claim wording.
The question is whether additional Luna reasoning improves grounded assessments
under identical inputs and resource limits, and at what token, latency and cost
tradeoff. It does not test story rewriting or establish literary quality.

## Treatment and common resource amendment

Use **`gpt-6-luna`**, via the existing OpenAI Responses adapter, with three arms:

| Arm | Exact request setting | Role |
| --- | --- | --- |
| high | `reasoning.effort: "high"` | Contemporary control |
| xhigh | `reasoning.effort: "xhigh"` | First candidate |
| max | `reasoning.effort: "max"` | Second candidate |

Within each block, **the only generation/count body difference is
`/reasoning/effort`**. Full sources, order, critic report, whole selected claims,
instructions, evidence contract, domain/native schema and all other effective
settings are identical. No new interpretive instruction, source-bound C schema,
receipt-handle format, excerpt treatment, reduced workload or model substitution.
All efforts are documented for this exact model; their actual server acceptance
is not established by local mocks.
[Official model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna).

Every arm receives **32,000 generated tokens including reasoning**, increased
from the previous 16,000. This is a declared **common baseline amendment**, not
an effort-specific advantage. The four historical high request bodies differ
from their saved U bodies only at `/max_output_tokens`; their count bodies,
messages, schemas, sources and selections are unchanged. Historical outcomes
are provenance and regression evidence, not concurrent controls. This design
cannot separately measure the effect of increasing the cap.

The previous Luna run completed without truncation, with a maximum 6,461 generated
tokens. The larger shared cap gives higher efforts additional headroom; it does
not guarantee completion. OpenAI recommends initially reserving at least 25,000
tokens for reasoning plus final output. No cap increase or retry is allowed after
observing responses. Results describe performance within the frozen limits.
[Reasoning and output-budget documentation](https://developers.openai.com/api/docs/guides/reasoning).

All arms retain the **U section-locator evidence contract**: an exact quote
selects one complete immutable registry field or one prose paragraph. Its quote
need not contain every premise when the selected section does. Selected sections
together must cover the whole claim and material explanation; adjacent uncited
sections are not silently included. Legal location is distinct from relevance,
adequacy and truth. No witness repair or normalization is allowed.

Native strict output, default service tier, disabled truncation and
`store/background/stream: false` remain fixed. No tools or prior-response state.
The adapter omits portable temperature, top-p and seed for all three efforts,
matching the historical effective settings. It supports effort per request;
this preparation does not introduce a production escalation policy.

## Cases and exact schedule

| Family | Status | Claims per block | Main contrasts |
| --- | --- | ---: | --- |
| H1 | Unchanged saved historical scene/report/selections | 7 | General authentication versus private-flourish event; current obligation versus observed overrun; compound evidence and prior citation failures |
| F3: The Bell Without a Boat | Unchanged saved control | 8 | Private procedure performed through paraphrase; multisection touch/vibration evidence; plan-opening reference type |
| F7: The Public Gauge | Fresh 613-word scene and five-scene blueprint | 8 | General instrument identity; specific calibration not established; actual overrun; next plan opens outside; accurate proposal/rejection attribution |
| F8: Seeds for the Empty Plot | Fresh 637-word scene and five-scene blueprint | 8 | General stock origin with explicit denial of private verification; next plan opens inside; false protagonist attribution; current overrun |

Fresh families have different goals and stakes: a public flood warning and
community stewardship of planting stock. Both retain complete current prose,
blueprint, separate current assignment, source-scope record and report. Date,
purposeful-decision, persistent-vibration and unavailable-annex controls remain.
No gold rationale, expected label or authored answer enters the model messages.

Four families × two source-order blocks × three efforts = **eight matched
triples / 24 attempts**. There are **62 claims per effort, 186 fixed slots**,
including **32 fresh claims per effort**. PC places the draft before planning
context; CP reverses those groups. All full sources remain present.

H1's PC/CP selections differ historically and remain untouched. Compare efforts
within those blocks; do not infer a pure order effect from their difference.
F3/F7/F8 retain identical claims across orders. Reordered presentations and
multiple claims are not independent stories.

| Block order | Within-block attempt order |
| --- | --- |
| 1. F7-PC | high → xhigh → max |
| 2. H1-CP | xhigh → max → high |
| 3. F3-CP | max → high → xhigh |
| 4. F8-PC | high → max → xhigh |
| 5. H1-PC | max → xhigh → high |
| 6. F7-CP | xhigh → high → max |
| 7. F8-CP | high → xhigh → max |
| 8. F3-PC | max → xhigh → high |

The schedule uses all six permutations, with two repeats. Eight blocks cannot
perfectly balance first position across three arms. Calls are sequential; cache
and service-load effects remain limitations of latency comparisons. No adaptive
reordering, replacement story or additional repeat is permitted.

## Frozen judgment and continuation rules

Inspect **all 186 slots**, including failed and unstarted ones. Apply these
categories in order: **unavailable**, **semantic**, **citation-only**, **grounded**.
Unavailable deliveries earn no partial credit. Wrong labels or materially
unsupported reasons are semantic failures; correct judgments with unresolved,
irrelevant or incomplete selected evidence are citation-only failures. Grounded
requires correct judgment/reason and adequate precisely located evidence.

`gold.json` freezes every whole proposition, expected label and adequate-evidence
criteria. Authored example witnesses illustrate coverage without excluding other
adequate selections. Record binding, whole-claim label, material explanation,
coverage and source-inspection notes separately. Inspect H1's contextual relation
independently; correct component labels do not automatically establish it.

H1's mixed structural-consumption wording keeps its existing specific-event score.
In final-reason notes, distinguish a specific-event reading from a broader
editorial-overlap reading. The latter is not proof that the private procedure
occurred, and its actual pacing effect has no factual gold. Fresh F7 lacks
depiction of the specific method; F8 explicitly denies performing it. Those are
different conditions even though both particular performance claims are unsupported.
F3 protects actual performance through paraphrase. No invented off-page events.

Compare **xhigh versus contemporary high** and **max versus contemporary high**
separately. Each bounded continuation screen requires:

- All 24 complete valid deliveries and all eight triples.
- At least **two distinct family/full-claim recoveries** from high semantic or
  citation-only failure to candidate grounded. Deduplicate repeated order
  presentations; report semantic and citation recoveries separately.
- **No grounded loss, no new semantic loss and no contextual-relation loss.**
  A high citation-only answer becoming semantically wrong is a new semantic loss.
- **All 32 fresh candidate judgments grounded.**

The scorer cannot average away a protected loss. If high does not reproduce
failures, report feasibility/repeatability and resources, not demonstrated recovery
efficacy. A terminal run remains incomplete. Passing supports a bounded replication
candidate, not production qualification. Do not assume monotonic quality with
effort or select the highest setting automatically.

Inspect final-response packets in SHA-256 trial-ID order, hiding effort and usage
where practical until inspection notes are saved. This is assistant source
inspection, not fully blind human review; familiarity and response wording can
reveal conditions. No model grader, hidden-reasoning inspection or extra live call.

## Resource measurements and budget

Record input/cached-input, total generated and reasoning tokens, non-reasoning
output, count-plus-generation active latency, finish/delivery status and reference
cost per attempt. Reasoning is part of generated output, never an additional
allowance or a second charge in the calculations. Output minus reasoning is not
guaranteed to equal visible final-text tokens. Unknown usage remains unknown.

Report per-arm sums/medians/maxima, paired per-block ratios against high, and
resource consumption per grounded judgment and fully grounded report. Include
failed-attempt consumption; expose missing pairs and zero denominators. Distinguish
median paired ratios from ratios of totals. Report end-to-end wall time separately
from active count/generation time, which excludes preflight and inspection.
No latency/token multiplier for Luna is assumed from earlier DeepSeek results.

| Resource | Per attempt | Entire comparison |
| --- | ---: | ---: |
| Attempts / maximum generation dispatches | 1, zero retries | **24** |
| Input tokens | 24,000 | **576,000** |
| Generated tokens, including reasoning | 32,000 | **768,000** |
| Active count/generation time | 600 seconds | **14,400 seconds** |
| Application planning allowance | $0.03 | **$0.72** |
| Conservative token-max reference reservation | $0.019 | **$0.456** |

Reference accounting uses $0.125 per million for all input tokens and $0.50 per
million for generated tokens, without assuming cache savings. Published standard
input/cached-input/cache-write rates are $0.10/$0.01/$0.125 per million. Actual
account charges remain unknown; the allowance is not an invoice.
[Published rates](https://developers.openai.com/api/docs/models/gpt-6-luna).

Approval must cover full unpublished fictional prose, complete planning/context,
critic reports, registries and exact claims at **both story-bearing endpoints**:

- `https://api.openai.com/v1/responses`
- `https://api.openai.com/v1/responses/input_tokens`

At most **24 preceding story-bearing count requests** and **24 catalog preflights**
are permitted, with no extra smoke generation. Counts share their attempt's
reservation with generation; failed counts and interrupted reservations consume
that attempt. Old retired allowances are not reused.

Preparation uses saved successful 2026-11-04 visibility and current official
documentation, with **zero new catalog, count or generation requests**. Current
access and xhigh/max acceptance remain unverified. Recheck catalog availability
before each reserved attempt after approval; reject unexpected model identity.
The frozen alias has no selected immutable snapshot, so alias drift is a limitation.
Reuse the already authorized application credential only through the secret store.

## Terminal stops

Stop **all three arms** on the first invalid/empty/duplicate/missing/extra/changed
claim delivery, malformed evidence, refusal, truncation, unsupported schema/effort,
transport/auth/quota failure, unknown input/output/reasoning usage, inconsistent
usage, resource overflow, secret-boundary failure or frozen identity drift.
Schema-valid unresolved witness locations are measured citation outcomes, not
delivery failures. Semantic errors alone do not stop the run.

Preserve terminal status, error chain, raw final data and unknown usage without
crediting invalid output. Inconsistent reasoning usage remains in raw evidence;
the typed completion record leaves it unknown rather than inventing a consistent
number. The harness reserves before transport, checks exact destinations/bodies,
holds an exclusive lock, detects interrupted preflights/reservations, retires
unstarted slots and refuses terminal resume. No retries, model/schema fallback,
replacement generations, prompt revisions or allowance transfers.

## Freeze and verification

Private bundle: `data/diagnostics/reviewer-reasoning-effort-v61-2026-11-04/`.
Plan SHA-256:
`e81e12309fb400c587e3519065a1d410a9e3a4290c8d65e7b56472239f4d2f75`.
The freeze binds **39 preparation files and 3,769 source fingerprints**, including
exact native/count requests, complete work/context, per-claim gold, scoring,
inspection slots, schedule, budget/stops, model specification, runtime and
verification. No approval file or live directory exists.

**309 offline tests pass:** 147 diagnostic tests, 123 tracked assessment-work/result
tests and 39 provider/routing/execution tests, with no deselections. Coverage
includes all 24 actual adapter wires, treatment isolation, historical headroom-only
amendments, all sixteen saved U/C delivery replays, full-context rendering, schema
and witness failures, terminal error/usage preservation, all-three-arm ceiling,
no retry/resume, incomplete reservations, missing/inconsistent reasoning usage,
complete scoring denominators and deduplicated recovery/loss screens.

Repository Ruff/format/strict mypy pass for **224 Python files**; all **eleven
private scripts** pass their corresponding checks. Deterministic preparation,
inspection slots and the source/contrast audit reproduce their artifacts. The
audit authenticates all sixteen prior cell seals and preserves historical scores.

One deterministic check initially caught CRLF instead of LF in the generated
source manifest. The recorded correction changes no parsed value or source hash;
the subsequent byte-for-byte preparation passes. Original failed logs and the
successful correction observations remain in the bundle. Development lint/typing
findings were corrected. Verification history identifies these stages explicitly.

The offline harness uses mock HTTP and a synthetic credential, blocking real HTTP,
external sockets, DNS and SQLite; tracked integration tests use temporary test
databases. Async checks use the established Windows sandbox-startup workaround.
No provider call follows from those checks. No frontend changed, so frontend
checks are not applicable; the entire repository test suite is not claimed as
rerun. Original issue bodies and posted URLs remain unchanged.

No production application, frontend, schema, dependency, profile or prompt changes.
Human story review remains focused on feel, flow, character and story-breaking
details. No story is rewritten, and no literary-quality or automatic-edit authority
is inferred from this diagnostic. All fourteen issues remain open.

Next: approve the exact frozen 24-attempt plan, including full prose/context at
both endpoints, then execute once and inspect every fixed slot. **Step 19 IN
PROGRESS; Step 20 NOT STARTED; interpretation diagnostic ON HOLD; live calls
PAUSED; canary ON HOLD.**
