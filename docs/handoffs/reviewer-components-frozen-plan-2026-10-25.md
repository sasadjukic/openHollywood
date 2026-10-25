# Frozen CV/CA component-assessment comparison — 2026-10-25

Status: **prepared locally; inference approval pending; 0/32 model calls used**.
The full workflow canary remains **ON HOLD**. This implements the
[component proposal](reviewer-component-assessment-proposal-2026-10-25.md) following
the [aggregation/cardinality audit](reviewer-aggregation-cardinality-audit-2026-10-25.md).
The new daemon baseline is verified **Ollama 0.40.11**. No model inference occurred
during preparation.

## Question and comparison

Can explicit assessments of supplied material components, followed by
application-owned aggregation, improve usable whole-claim judgments without
rejecting defensible literary interpretations or adding unsupported explanations?

| Arm | Frozen behavior |
| --- | --- |
| CV — control | Existing fixed-claim prompt, schema, sampling settings and whole-claim response contract |
| CA — candidate | Complete original claims plus authored component maps; keyed component judgments, evidence and brief reasons; application derives whole-claim labels |

CA is one diagnostic interface package: supplied decomposition, response shape
and application aggregation. This comparison cannot isolate their individual
contributions. It tests assessment of **supplied** components, not autonomous
decomposition of arbitrary reviews. The map author also supplies withheld gold;
this is a limitation of a selected diagnostic, not independent quality validation.

Production remains **prompt 61 / graph 9 / fulfillment policy 1**. No production
prompt, writer behavior, role, graph, schema or human checkpoint changes here.
CA's isolated diagnostic contract is frozen in this bundle.

## Frozen matrix and inputs

**Eight families × two arms × two source orders = 32 attempts**, sixteen per arm,
zero retries or extra repetitions. Each response assesses three complete claims:
**24 unique claims, 96 attempted whole-claim judgments**. CA has **71 unique
components**, giving 142 component opportunities across its sixteen attempts.

| Family | Source | Frozen contrast |
| --- | --- | --- |
| H — observatory | Unchanged | False status contradiction versus actual prohibition and qualified voice criticism |
| B — costume workroom | Unchanged | Invented before-deciding condition; duplicate cleanup; dense evidence delivery |
| K — concert hall | Unchanged | Condition violation versus status contradiction previously sensitive to source order |
| N — floodgate | Unchanged | False status contradiction accepted in all four recent responses |
| P — bookbinding | Unchanged | Already-made decision, actual intact-stitch requirement and legitimate craft interpretation |
| Q — seed archive | Unchanged | Original/revision ownership and unsupported exhaustive claims in explanations |
| U — greenhouse inspection | Fresh | Starting a heater before authorization violates a requirement without contradicting non-authorization status |
| V — instrument conservation | Fresh | A true no-locking observation combined with a false “only handling” assertion; earlier handling is explicit |

The six historical packets, original/revised prose, claims and gold are unchanged.
All **twelve historical CV wire payloads match their prior CV/MC equivalents
exactly**. Fresh CV requests use the unchanged control builder. G/L/M remain in
the local regression evidence; omission from this reduced live matrix does not
qualify their broader behavior.

U and V each supply one unsupported claim and two supported controls, with full
fictional scenes, assignment context and exact source catalogs. Their originals
contain 238 and 243 words; revisions contain 242 and 248. Both arms receive the
same full sources, mechanical appendix, claim order and source identities. Only
CA receives the component map and corresponding response contract. Original-first
(OR) and revision-first (RO) presentations are counterbalanced with arm order.

The first eight calls are **CV-H-OR, CA-H-OR, CA-U-OR, CV-U-OR, CA-U-RO, CV-U-RO,
CV-H-RO, CA-H-RO**. The remaining family blocks are B/P, Q/V and K/N, each with
both arms and orders. There is one observation per cell: order comparisons remain
descriptive, without an exact-repeat estimate of variability.

## Component meaning, evidence and boundaries

Maps preserve complete original claims, negation, quantifiers, version ownership,
timing, conditional language and relational assertions. False contradictions and
invented prerequisites remain assertions to assess; they are not silently replaced
by their correct alternatives. Components distinguish facts, explicit constraints
and craft interpretations. A defensible craft interpretation need not be the only
possible reader response. Whole claims remain visible alongside their maps.

The application derives a whole-claim label as follows:

1. Any **unsupported** component produces **unsupported**.
2. Otherwise, any **uncertain** component produces **uncertain**.
3. Otherwise, all components supported produces **supported**.

This arithmetic does not establish truth or completeness of the decomposition.
It cannot detect an invented assertion added in a reason. Those remain source
inspection responsibilities. The model cannot override the aggregate with a final
verdict; no whole-claim verdict or extra summary field is accepted in CA.

Each supplied claim and component must appear exactly once in its frozen order.
Missing, duplicate, reordered or unknown identities, duplicate JSON members,
unknown/incorrect-type evidence references and additional fields are rejected.
There is no normalization, trimming, salvaged-claim credit or repair call.

**Evidence cardinality remains eight distinct refs per whole claim.** CA counts
the union across components; cross-component reuse is allowed, duplicates within
a component are not. Definite judgments require evidence; uncertainty may use an
empty list with a reason. Total component reasons per claim are bounded at
**2,000 characters**. Full versions and exact quotes are bound by the application.
Representative citations are assessed against the entire source pair; there is
no new rule requiring a separate citation for every incidental detail.

Authored bound demonstrations cover all 24 claims and fit the limit, including
B/C03 at eight distinct refs. For its retained-events component, the demonstration
cites the revision discovery/decision while the full original is also available.
These examples and adjudications are **withheld from requests** and earn no model
or recovery credit. They establish local representability, not future delivery.

**B/C03 stays secondary and scope-sensitive.** “Undermines the deferred-consultation
logic” is retained as a defensible craft reading, without adding a formal
before-deciding prerequisite. Its unchanged historical whole-claim gold remains
unsupported; the frozen component interpretation can yield all-supported. Report
both descriptions explicitly. A component-correct CA answer can therefore miss
the historical secondary whole label. It cannot create or block primary recovery.
Structural validity still applies to the entire response.

Component gold, whole-claim gold, source adjudication rationales, chosen gold
citations and historical outcomes are absent from all live payloads.

## Scoring and decision rule

Per arm, freeze **46 primary judgments** (30 supported, sixteen unsupported) and
two secondary B/C03 judgments. CA's component denominators are 128 primary and
fourteen secondary. Invalid or dispatched terminal responses remain failed
attempted opportunities; unstarted cells are separate. Unsupported explanations
and uncertainty receive no usable-claim credit. Correct labels alone are not enough.

Report delivery, whole-claim labels, component labels, abstentions, complete-reason
grounding, citation support and usable claims separately, by arm/family/order and
fresh/historical origin. Missing components invalidate delivery. A CA claim is
usable only if its aggregate matches gold, **every material component matches
its frozen interpretation**, and all component and combined explanations/citations
are supported. A correct aggregate cannot hide a wrong component or an unjustified
rejection of craft. CV retains the complete-claim/full-reason standard. Material
coverage annotations remain descriptive; they do not excuse a false assertion.

CA is retained as **promising diagnostic evidence only** if all conditions hold:

1. At least **15/16 valid responses**, including **3/4 fresh**, with no paired loss
   of valid CV delivery.
2. At least **four paired usable primary recoveries across two families**,
   including one historical claim recovered in **both orders** and at least one
   fresh recovery. Both paired reports must be valid. Invalid-to-valid delivery
   gains are reported separately and earn no semantic recovery credit.
3. No paired loss of a usable primary CV claim, no supported primary control
   correctly labeled by CV becoming wrong/uncertain in CA, and no grounded
   primary CV reason/citation becoming unsupported/uncertain in CA.

Recovery opportunity is computed from valid CV primary failures independently of
CA success. Insufficient opportunity adds no calls and cannot hide an independent
delivery failure or protected loss. Incomplete runs never advance. All decisions
retain `production_qualified=false` and `writer_dispatch_authorized=false`.

Source inspection uses shuffled IDs and hides arm/order/trial labels. Inspect
whole reasons and every component reason against full versions, record exact
source quotes, and seal notes before decoding the key. The schema/map reveals
the arm, so masking is partial. This is assistant factual adjudication, **not
blind human preference** or a new rating of story quality.

## Model, metadata and budget

Selected model: **`deepseek-v4.1-flash:cloud`**, through the local Ollama daemon to
Ollama Cloud. Authorized read-only preparation captured `/api/version`, `/api/tags`
and `/api/show`: three successful responses with raw bodies, hashes and a seal.
Daemon version is **0.40.11**. The selected tag, digest, capabilities and thinking
metadata exactly match the previous selected-model snapshot. Digest:

`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`

An initial sandbox-blocked socket attempt is retained separately; it returned no
daemon response and dispatched no inference. Prior 0.40.10 evidence is preserved.
This is a new contemporary baseline for both arms, not a controlled daemon-version
or provider comparison. Provider investigation remains deferred.

Sampling: **temperature 0.2, top-p 0.95, seed 20261022, thinking=false,
stream=false, context 32,000**, with no provider `format` field. Identical sampling
settings and per-call limits apply to both arms.

| Resource | Frozen ceiling |
| --- | ---: |
| Total attempts / per arm | **32 / 16** |
| Retries, correction calls, resampling | **0** |
| Input / output tokens per attempt | **24,000 / 8,000** |
| Aggregate input / output reservations | **768,000 / 256,000** |
| Active generation seconds per attempt / total | **300 / 9,600** |
| Archived-rate reservation / planning allowance | **$0.53760 / $0.70** |

Cost arithmetic uses archived $0.30 input/$1.20 output per million tokens, without
discounts. It is not a current pricing lookup, actual bill or provider-enforced
dollar cap. Prompt byte estimates are planning estimates; usage returned by the
provider is checked against limits. Missing usage remains unknown, not zero.
The frozen payloads contain 14,806–21,047 UTF-8 message bytes; the largest
quarter-byte planning estimate is 5,262 input tokens, not a tokenizer measurement.

## Stops, execution and approval

After the first eight calls, stop if either arm has zero valid responses, or the
same structural failure signature occurs at least three times across both sentinel
families, pooling arms. A normal-stop invalid report consumes its attempt. Semantic
failure is an outcome, not a reason to resample.

Stop immediately on non-200/transport error, timeout, cancellation, truncation or
non-stop output, unexpected thinking, missing/invalid/excess usage, version/model
drift, tampered source/request/capture, incomplete evidence or exhausted budget.
Persist initial/before/after version observations before validation, gateway error
chains and unknown usage. All dispatched attempts count, including failures.
No terminal restart, retry, transferred allowance or automatic amendment is allowed.
Only a clean cell-boundary restart may run the untouched remainder.

Execution requires a separate approval bound to the sealed plan, full unpublished
fiction/context and claims/components payload, **Ollama Cloud through the local
daemon**, 32 attempts and zero retries. The runner validates seals, uses an exclusive
operator lock, reserves before dispatch, checks model metadata and version, sends
the exact prepared request, and preserves raw responses and receipts. A completed
run cannot dispatch further calls. No approval file or live execution directory
has been created during preparation.

## Local artifacts and verification

Private bundle: `data/diagnostics/reviewer-components-v61-2026-10-25/`.
It contains `cases.json`, `claims.json`, `components.json`, `component-gold.json`,
`casebook.md`, `case-audit.json`, authored evidence-bound examples, 32 `prepared/`
requests, wire payloads, settings/budget/stops/scoring/schemas, captured metadata,
source fingerprints, runner, strict boundary, version capture, masked inspection
and offline tests. Unpublished full prose remains in the ignored local bundle.

`plan.json` binds the frozen code, inputs, requests, metadata, this public plan and
historical source fingerprints. Verification outputs and the subsequent tracker
update have separate closure records to avoid a circular seal. The tracker records
the final plan hash. Exact commands and results are retained in local verification
records; all inference paths in tests use mocked transport with real HTTP blocked.

**Verification passed: 279 offline tests** (188 new harness tests plus 91 prior
aggregation regressions), Ruff lint/format and strict mypy on nine new private
Python files. The historical chain contains **1,851 verified source fingerprints**.
Mock transport tests used the existing Windows asyncio test accommodation; they
block real HTTP and make no inference calls. No application source or dependency
changed, so frontend/build and unrelated product suites are outside this change.

The test suite covers unchanged control wires, withheld gold, complete component
delivery, deterministic aggregation, evidence union/reason limits, source-bound
inspection, secondary scope, protected losses, insufficient opportunity, full
mock execution/restart/ceiling, sentinel stops, terminal error export, version
drift and approval/tamper guards. The prior aggregation regression suite retains
the broader historical fixtures. Verification commands and full results are saved
as `verification-static-final.json` and `verification-tests-final.json`; the
post-seal verification is recorded separately.

No issue is closed, reviewer promoted or better-story claim made. The nine human
ties remain unchanged. Future reader review still focuses on feel/emotion, flow,
character and story-breaking concerns, with machine-prepared mechanical evidence.
**Step 19 remains IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**
