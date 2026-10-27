# Frozen DeepSeek non-thinking versus high-thinking comparison

Date: 2026-10-26. **LOCAL PREPARATION; 0/48 INFERENCE CALLS USED. LIVE APPROVAL REQUIRED.**

This implements the agreed twelve-case, two-order, two-mode comparison following
the [relation-object audit](reviewer-relation-object-audit-2026-10-26.md) and
[model assessment](deepseek-model-attribution-assessment-2026-10-26.md).
It tests whether the selected DeepSeek operating mode affects grounded review
accuracy and resource use. Production **prompt 61 / graph 9 / fulfillment policy
1** are unchanged. There are no writer calls, production routing changes or full
workflow canary; the canary remains **ON HOLD**.

## Exact comparison

| Item | Frozen choice |
| --- | --- |
| Model | `deepseek-v4.1-flash:cloud`, both arms |
| Destination, after approval | Ollama Cloud through `http://127.0.0.1:11434` |
| NC control | `think: false` |
| TH treatment | `think: "high"` |
| Matrix | 12 full-scene families × original/revision or revision/original presentation × 2 modes = **48 attempts** |
| Allocation | 24 NC and 24 TH; one attempt per cell; **zero retries** |
| Shared requested settings | temperature 0.2; top-p 0.95; seed 20261022; non-streaming; no provider format override |
| Shared task | Existing NC instructions, three-label component assessments, application-owned whole-claim aggregation |
| Evidence limits | Eight distinct references per whole claim; 2,000 summed component-reason characters per whole claim |

For each matched pair, the wire payloads differ **only in `think`**. All messages,
source versions, claims, components, schema, reference registry, requested sampling
settings and resource limits match. The fourteen known-case message sequences
remain byte-identical to their previous NC counterparts. Both current arms share
a larger generation/context allowance than the earlier experiment: the old wire
payloads as a whole are therefore not identical. Historical results are context;
the new contemporary NC arm is the comparison baseline.

The schedule alternates which mode is called first: twelve pairs start with NC,
twelve with TH. It includes both presentation orders and keeps paired modes
adjacent. This reduces ordering confounds without proving identical server load,
caching or deterministic sampling. Repeated orders are not independent families.
The first eight scheduled cells cover H/U in both modes and both orders; they are
part of the 48-call ceiling, not additional probes.

## Frozen cases and claims

| Family | Source | Main relation being tested |
| --- | --- | --- |
| H | Existing observatory | Not yet consulted versus rotating before consultation; separate real intention/rule conflicts |
| U | Existing greenhouse | Not yet authorized versus starting before authorization; separate real intention/rule conflicts |
| X | Existing foundry | Incompatible states of the same door at the same instant |
| Y | Existing photographic archive | Explicitly unresolved timing of opposite lamp depictions |
| F1 | Existing pottery | Compatible dark/lit states at different specified times |
| F2 | Existing railway office | Intact/shattered descriptions of the same pane at the same instant |
| F3 | Existing reservoir records | Explicitly unresolved timing of opposite shutter records |
| G1 | **Fresh letterpress shop** | Unconsulted status versus early printing; distinct resolve and assignment breaches |
| G2 | **Fresh ferry boathouse** | Unauthorized status versus early winch operation; distinct resolve and assignment breaches |
| G3 | **Fresh aquarium chart room** | Shut/open descriptions of the same hatch at the same instant |
| G4 | **Fresh bakery photographs** | Explicitly unresolved timing of lit/dark sign photographs |
| G5 | **Fresh radio repair ledger** | Two meter readings with no established measurement timing; uncertainty from absent evidence |

The fresh originals contain **281–313 words each** and retain narrative setting,
character relationships, discovery, decision and an assigned endpoint. Revisions
are frozen authored changes, not new writer output. Every family includes
assignment and qualified-craft controls; G1/G2 separately expose the real rule
and intention conflicts. G5 distinguishes the order of ledger entries from the
unknown timing of measurements. It does not state that the measurements were
simultaneous or sequential.

The bundle freezes **36 whole claims and 83 material components**. Each arm has
**72 whole-claim, 166 component, 24 target and 142 non-target opportunities**.
Gold labels, source witnesses and relation-status annotations remain withheld
from every model request. Original/revision packets, version IDs, registries,
component maps, exact prepared requests, wire requests, schemas, schedule, authored
examples and a readable casebook are all included in the freeze.

## Budget and accounting

| Limit | Per call, both modes | Entire comparison |
| --- | ---: | ---: |
| Attempts | 1 | **48** |
| Input-token reservation | 24,000 | **1,152,000** |
| Generated-token reservation | **16,000 total** | **768,000** |
| Active call-time ceiling | **600 seconds** | **28,800 seconds / 8 hours** |
| Requested context capacity | 40,000 tokens | Per-call setting |

These are ceilings, not forecasts. Thinking and final output share the generated-
token allowance; there is no extra uncounted thinking allowance. The larger shared
limit gives high thinking more room than the earlier 8,000-token cap while keeping
the same budget in both arms. A truncated answer remains a delivery outcome; it
must not be silently retried or treated as an answered semantic question.

Budget enforcement uses the request's generation limit, reported `eval_count`,
input count and an active wall-clock timeout. It does not independently inspect
the remote server's internal token accounting. Missing or inconsistent reported
usage stops the experiment; unknown usage is preserved as unknown. Reservation
occurs before dispatch, so failed or ambiguous dispatched cells cannot be reused.

Archived October 22 reference rates produce a maximum reservation estimate of
**$1.26720** and a **$1.50 planning allowance**, without discounts. These are not a
current tariff, confirmed charge or enforceable billing cap. Actual billed cost
remains unknown. No free calibration, replacement calls, budget transfers or
automatic escalation to another model/mode are allowed.

## What is measured

**Quality:** valid final delivery; exact component and whole labels; source truth;
complete evidence for each material component; correct assertion-pair/relation
scope; paired recoveries and losses; and whole-report usability. Invalid delivery
stays in attempted denominators. Incomplete experiments disclose scheduled,
reserved, completed and unattempted counts separately.

**Resources:** active end-to-end call latency, provider total/prompt/generation/load
timings when present, input and cached-input counts, total generated tokens, and
explicitly supplied reasoning-token breakdowns. Missing breakdowns remain null,
not zero. Character lengths and hashes preserve observations but are not token
estimates. If a provider supplies a separate usage object, its totals must agree
with the primary counters before a reasoning/final split is accepted.

The analysis reports per-mode medians and maxima, paired latency/token ratios,
and total time/tokens per completely usable report, including completed invalid
answers in the resource numerator. Terminal elapsed time and reported/unknown
usage remain visible separately; ratios never silently substitute zero for them.
Known and fresh families are identifiable separately. There is no invented
acceptable-latency threshold or automatic production efficiency qualification.

The latest fourteen historical NC calls averaged about 1.53 active seconds and
378 reported output tokens. That is a descriptive reference only. This run must
measure its own contemporary baseline; no thinking-mode multiplier is assumed.

## Frozen quality screen

Retain a **promising operating-mode diagnostic signal only** if the complete run
satisfies all of the following:

1. At least **22/24 TH reports are valid**, including **all ten fresh-case TH
   reports**.
2. There are at least **six contemporary NC false-acceptance opportunities** across
   all four H/U/G1/G2 failure families, with both orders represented in at least
   two families. Otherwise causal recovery evidence is insufficient, even if TH
   scores well in isolation.
3. TH makes at least **six grounded paired recoveries**, spanning those same four
   families and both orders in at least two. An invalid NC report does not create
   a semantic recovery opportunity.
4. All **sixteen required TH target controls** in X/Y/F1/F2/F3/G3/G4/G5 are usable.
   This includes genuine contradictions, compatible sequential states and both
   sources of uncertainty.
5. There are **no protected paired losses** in valid delivery, previously usable
   targets, whole claims or non-target components, supported requirement/craft labels, or
   grounded complete explanations/citations. Overlapping flags must be reported
   as overlapping, not additional independent failures.

An incomplete run cannot advance. A completed run that violates a quality screen
retains limited evidence without advancement. With otherwise satisfactory screens
but insufficient contemporary opportunities, report insufficient opportunity;
do not manufacture a recovery comparison from historical calls. Resource results
remain a separate descriptive assessment for later role-selection decisions.

The unchanged NC contract uses supported/unsupported/uncertain in both arms.
Y/F3/G4/G5 require uncertain in primary scoring. The historical ambiguity of
unsupported-as-unestablished remains disclosed: an accurate explanation that
timing is not established is not automatically a false factual assertion, but
does not gain primary label credit. Distinguish explicitly unresolved alternatives
from information simply absent in G5 through source inspection; do not introduce
ES vocabulary into either model's response contract.

Qualified craft readings require defensibility, not unique entailment. A correct
label cannot rescue a false premise or missing witness. Nor can genuine intention
conflict substitute for the requested factual compatibility judgment. This screen
is a mechanism diagnostic on a small constructed matrix, not a general model
ranking or evidence of improved story preference.

## Inspection and thinking isolation

Store raw thinking and final content separately, retaining the exact raw response.
Only final content is parsed and scored. The masked inspection export excludes
thinking text, mode, trial/order identifiers and usage/timing measurements. Inspect
every valid report's whole and component reasons against full source/context;
seal the notes before decoding the trial key. Known scenes and answer style may
still reveal conditions, so masking is partial and adjudication remains assistant
source inspection, not a new human literary review.

Thinking text is not accepted as evidence that rescues the final report and is
not treated as a reliable account of internal computation. No thinking trace is
passed to a writer, added to story truth or carried into another request.

## Stops and mode checks

- NC requires absent/empty thinking output. TH requires a nonempty thinking
  field. A missing TH observation stops with an **unverified mode change**; it
  does not demonstrate that the model answered incorrectly without extra thought.
  The trace supports an output observation, not independent verification of the
  server's internal effort allocation.
- After the first eight planned calls, stop if either mode has zero valid reports
  in its four attempts, or TH repeats the same blocking delivery signature across
  both sentinel families. This delivery/accounting checkpoint uses no semantic
  early stopping and no replacement allocation.
- Any non-200, gateway/transport error, truncation, incomplete response, missing or
  excessive usage, invalid supplied timing/token breakdown, elapsed-time breach,
  mode-observation mismatch, daemon/model drift, tampering, cancellation or
  ambiguous dispatch is a global terminal stop.
- Preserve raw error bodies, the error chain, reservations, known or unknown usage
  and version observations. Terminal audit and export are supported. Never restart
  a terminal or ambiguous cell. Resume only from an intact clean cell boundary
  using unspent original allocations, under the same approved plan.

## Metadata and interpretation limits

Three metadata-only responses on October 26 confirm **Ollama 0.40.11**, the
unchanged selected cloud tag/show metadata, and digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
Supported thinking values are `[false, "low", "high", "max"]`, with default high.
We explicitly select false/high. The initial sandbox socket failure is preserved;
the successful metadata capture contains no fiction and no generation request.
Fresh preflight and per-cell checks must match this baseline after live approval.

Ollama documents model-specific thinking values and generated-token/timing
counters. DeepSeek documents mode-dependent sampling behavior, including ignored
temperature in thinking mode. Requested sampling settings remain equal, but
effective settings through Ollama are not independently verified. This is a
comparison of supported operating modes, not a pure isolation of extra internal
computation. [Thinking controls](https://docs.ollama.com/capabilities/thinking),
[Ollama usage](https://docs.ollama.com/api/usage),
[DeepSeek mode behavior](https://api-docs.deepseek.com/guides/thinking_mode/).

Provider attribution and a context-isolation experiment remain deferred. No low-
thinking third arm, second model or writer comparison has been added.

## Verification, artifacts and approval

**381 offline tests pass: 206 new preparation tests plus 120 preceding local-audit
regressions and 55 prior execution tests. Ruff lint/format and strict mypy pass
on eleven scripts.** Verification results are recorded in the private bundle before this plan is sealed.
The preparation verifies paired wire identity, unchanged known prompts, source/gold
separation, exact budgets, metadata, supported modes, token/timing boundaries,
source-bound inspection, protected losses, all 48 mocked dispatches, clean-boundary
resume, terminal export, tamper rejection and approval binding. Real HTTP is blocked
in tests. Production code and the earlier frozen evidence remain unchanged.

Private ignored bundle:
`data/diagnostics/reviewer-thinking-mode-v61-2026-10-26/`.
The [casebook](../../data/diagnostics/reviewer-thinking-mode-v61-2026-10-26/casebook.md)
contains every original/revision and claim. `plan.json` seals the public plan,
scripts, cases, requests, scoring, stops, metadata and **3,678 historical source
fingerprints**. The tracker and issue index record the preparation; all fourteen
issue bodies and posted GitHub links remain unchanged. No external issue is edited
or closed.

**Approval requested only after local verification:** run this exact 48-attempt
NC/TH comparison, sending the frozen full unpublished fictional prose/context to
Ollama Cloud through the local daemon. No live approval file exists at preparation.
There are **0/48 inference calls used**. Production prompts, human checkpoints and
the nine prior human ties remain unchanged. Humans continue to assess feel/emotion,
flow, character and story-breaking details with machine-prepared mechanics.

**Step 19 IN PROGRESS; Step 20 NOT STARTED; live inference PAUSED; canary ON HOLD.**
