# Gemma and DeepSeek C2 reviewer repeat

Date: 2026-10-21. Status: **FROZEN, LOCALLY VERIFIED, NOT RUN**.
Live inference is not authorized. The full workflow canary remains **ON HOLD**.

This plan follows the [local interface audit](reviewer-interface-audit-2026-10-21.md).
It prepares **64 calls maximum**: eight original/revision pairs, two deployments,
two seeds and both presentation orders. There is one experimental interface, C2,
one attempt per cell, no retries, no writer calls and no fallback model. Production
prompt **61**, graph **9**, fulfillment policy **1**, schemas and routing stay unchanged.

## What the repeat can establish

Test whether C2 produces valid, source-supported assessments across repeated draws
and display orders on known failures and fresh controls. Score event retention
separately from endpoint compliance, and inspect false premises even when all labels
are correct. C2 combines several audited changes; this is not an ablation study.
There is no concurrent C1 arm, so historical scores are context rather than a causal
control or directly comparable improvement rate.

The 64-call design is eight cases × two models × two seeds × two orders. Reducing
that to one order per seed would confound order with seed. No old unused allowance
is reused. This ceiling is proposed for future explicit execution approval.

## Frozen interface and models

C2 keeps complete prose and source context, application-owned exact binding and
short catalog selections. It separates request relation, authorization and conditional
dependency, groups complete changed paragraph blocks for explanation, preserves the
token diff appendix, and adds an explicit endpoint judgment. Evidence arrays contain
at most eight distinct known references. No output is silently trimmed or repaired.
The audit specifies neutral/uncertain evidence handling and category examples.

The source context appears first, followed by both complete labeled versions, the
mechanical appendix and the final schema. **OR** displays original then revision;
**RO** displays revision then original. Labels, O/R references, assignments and the
direction of the edit do not swap. Only the two prose messages exchange positions.

| Deployment through local Ollama | Archived manifest digest |
| --- | --- |
| `gemma4:31b-cloud` | `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e` |
| `deepseek-v4.1-flash:cloud` | `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8` |

Both use temperature **0.2**, top-p **0.95**, explicit **thinking disabled**, and
seeds **20261021 / 20261022**. Each seed crosses both orders for both models on every
case. Case order reverses for the second seed; model/order combinations rotate
within each case, balancing their dispatch positions. Seeds are request settings,
not guarantees about cloud randomness. Two seeds do not estimate general reliability.

Metadata is inherited from the sealed October 20 preparation, not freshly queried.
Before every future dispatch, model tag/digest and recorded capability/thinking
metadata must match. Drift stops the run. Local manifest identity cannot prove
unchanging remote weights behind a cloud tag.

## Cases and exact expectations

The private [casebook](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21/casebook.md)
contains complete texts, exact groups, token operations and withheld expectations.
The four historical packets are unchanged except for added mechanical groups; their
prior packet hashes, prose, source identities, tasks and context are verified.

| ID | Source / case | Expected distinction |
| --- | --- | --- |
| h01 | Historical r01, Elara optional-duplicate no-op | Optional task unmet; both facts and endpoint retained; no comparative deterioration. |
| h02 | Historical r04, actual saved duplicate repair | Optional task met; direct supported edit; required facts and endpoint retained. |
| h03 | Historical r05, Elena date deletion and callback | Required realization lost; decision and endpoint retained. Core deletion unsupported; callback cleanup conditionally dependent on an unsupported edit. |
| h04 | Historical r08, safehouse departure | Earlier discovery and truce retained; departure violates endpoint. Do not erase the agreement. |
| n01 | New museum wording/grammar control | Requested optional `a rehearsal` → `an exercise` is direct and supported as a complete phrase; required facts and endpoint survive. |
| n02 | New harbor preparation then completed match | Decision to compare already occurred; added match violates endpoint. Earlier reflection was before completion, not after an invented comparison. |
| n03 | New seed-store cooperation replaced by refusal | Discovery retained, agreement lost, endpoint retained. Judge the whole replacement with its nine exact token operations. |
| n04 | New museum clean no-op | Optional task permits unchanged prose. Purposeful warnings serve separate actions; no invented obligation or comparative change. |

These are **six scene families**, not eight independent stories or 64 independent
story examples. The museum pair is reused for two controls. Fresh scenes and their
contexts are coordinator-authored synthetic fixtures, not model-generated stories,
approved Blueprints or human literary-quality evidence. Historical h02 is the only
saved actual writer revision; no new writer performance is measured.

The new explicit categories replace the ambiguous historical necessity labels only
for this experiment. Historical scores and uncertainty notes are never rewritten.
The category key, cases, full requests and scoring instructions are frozen before
any live response. No expected answer enters a model request.

## Scoring and decision rules

Keep delivery, task completion, each retained fact, endpoint compliance, mandatory
failure, group relation/authorization/dependency, no-op invariance and explanation
support separate. Literary comparison is descriptive: changed prose has no prescribed
winner. Supported ties, mixed judgments and uncertainty remain acceptable.

A **usable supported assessment** requires valid delivery, all frozen mechanical
label checks correct and source-supported consequential explanations after inspection.
Unresolved semantic support does not count as success. A correctly bound but irrelevant
quotation is not proof. A correct verdict with invented chronology still fails support.

Export shuffled normalized assessments without model, seed or display-order labels.
Inspect against full sources and diffs before consulting the separately stored key.
Record counterevidence, unresolved interpretations and materiality separately. Invalid
raw answers may be diagnosed in a separate column but cannot become primary successes.
This is coordinator inspection, not an independent blinded human quality assessment.

For each model, report **32 scheduled cells**, four per case, eight per seed/order
stratum, sixteen historical and sixteen fresh. Compare orders within each case/model/
seed and compare seeds within each case/model/order. Keep every attempted invalid or
length cell in its denominator. A terminal stop leaves remaining cells unobserved;
do not score unstarted cells as failures or successes.

Predeclared screening rule for a model: at least **28/32 valid** and **24/32 usable
supported** assessments, at least **3/4 usable for every case**, invariant valid no-op
reports, and no invented mandatory failure on any valid permissible control. Failing
any component means the candidate has not cleared this diagnostic screen. Report
the failure classes and order/seed variation without post-hoc rerolls. Passing permits
consideration of further evaluation; it does not qualify a production gate, select
a general model winner or prove better stories. The thresholds are diagnostic choices,
not replacements for the product's accepted whole-story benchmark.

## Budget and stop rules

| Limit | Ceiling |
| --- | ---: |
| Inference calls | 64 total; 32 per model |
| Attempts | One per fixed cell; zero retries or replacements |
| Input per call | 24,000 tokens |
| Output per call | 8,000 tokens |
| Requested context | 32,000 tokens |
| Active timeout per call | 300 seconds |
| Aggregate input reservation | 1,536,000 tokens |
| Aggregate output reservation | 512,000 tokens |
| Aggregate active request time | 19,200 seconds, at most 5 hours 20 minutes |

Using **historical October 20 reference rates**, reserved tokens imply $0.74752:
Gemma $0.20992 and DeepSeek $0.53760, without cache/off-peak discounts. Set an **$0.80
planning allowance**. This preparation performs no current-price lookup. These are
estimates, not verified charges or an enforceable billed-dollar limit; actual charges
remain unknown under ADR 0017. Exact calls, tokens and active time have explicit bounds.
Request byte-quarter estimates range from **4,712 to 14,914 tokens**; these are
UTF-8 bytes divided by four, rounded up, not tokenizer guarantees. Provider counts
govern actual token-limit checks, and no source is trimmed to fit.

Continue after a valid response, a captured invalid response or an identified,
in-budget `length` completion. A length response fails its cell and is never parsed,
retried, salvaged or given a higher cap.

Stop all dispatch on transport/auth/rate-limit failure, timeout, cancellation,
unknown outcome, missing capture/usage, excessive usage/time, model or thinking drift,
unexpected nonempty thinking, another finish reason, source/request/code mismatch,
incomplete previous cell, concurrent operator or approval mismatch. Invalid provider
envelopes and unclassified runtime failures also stop. A persisted reservation consumes
the cell even if its provider outcome is unknown. Completed cells replay without calls;
terminal or incomplete cells cannot become automatic retries. Unused cells cannot
transfer to another experiment, a writer or a workflow canary.

## Local verification and execution boundary

The private preparation directory is
`data/diagnostics/reviewer-interface-repeat-v61-2026-10-21/`.
It contains the protocol, construction code, complete requests, schedule, scoring,
stop rules, archived model metadata, offline cardinality audit and executable runner.
The runner uses the existing Ollama adapter with exact wire-payload verification,
durable reservation/capture/receipt files, replay checks and a single fixed live path.

Local verification passed **80 tests**: 58 diagnostic harness tests and 22 existing
gateway/contract regressions. Tests use the actual Ollama adapter over in-memory
HTTP, with real network transports disabled. They exercise the full 64-cell schedule,
partial resume and completed replay, invalid and truncated responses, cancellation,
provider/metadata drift, usage limits, evidence boundaries, tampering and approval
gates. All requests reconstruct; historical packets, exact group/token coverage,
catalog spans and sixteen prose exports verify. The five archived cardinality
failures replay exactly as reported in the audit.

Ruff lint/format and strict mypy pass across six private scripts. No frontend build
or application-wide test run is needed for unchanged production/frontend code.
Windows asyncio required execution outside the sandbox's internal-socket restriction;
provider networking remained disabled. Initial local checks exposed a reserved
`authorization` field name and an inherited 48-call resume assertion. The field is
now `edit_support`, the assertion uses the 64-call ceiling, and the complete suite
passes. Earlier local failure evidence is retained; no live result was altered.

The [verification record](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21/verification.json)
and [preparation seal](../../data/diagnostics/reviewer-interface-repeat-v61-2026-10-21/plan.json)
bind the requests, code, sources, scoring, limits and this plan. The executable
refuses to construct a live transport without a matching
future approval for the seal, **64-call ceiling**, exact models, **full unpublished
fiction and context**, and **Ollama Cloud through the local daemon**. No such approval
is created by preparation. No provider discovery or live inference is part of this task.

The earlier sealed preparation and live evidence remain unchanged. No production
application or frontend code is edited. The user-posted issue links remain intact;
local preparation progress does not close a GitHub issue.

Step 19 remains **IN PROGRESS**; Step 20 **NOT STARTED**. The full workflow canary is
**ON HOLD**. The separate writer-selection experiment is not prepared by this plan.
