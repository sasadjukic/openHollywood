# Frozen CV/MC material-claim comparison — 2026-10-24

Status: **prepared locally; awaiting separate live approval**. No inference or
daemon discovery occurred. Production remains **prompt 61 / graph 9 / fulfillment
policy 1**; the full workflow canary stays **ON HOLD**.

This implements the [36-call proposal](reviewer-material-claims-proposal-2026-10-24.md)
following the [whole-claim audit](reviewer-whole-claim-audit-2026-10-24.md). It tests
whether brief, visible premise assessments help the model judge the entire supplied
claim while retaining defensible literary interpretation. It does not test a writer,
qualify a production verifier or measure improved story quality.

## Frozen matrix and controls

**Nine families × two arms × two source orders = 36 attempts**, eighteen per arm,
with **zero retries**. Each response assesses three claims: 27 unique claims and
108 attempted judgments. There are no additional exact repetitions.

| Family | Scene | Frozen role |
| --- | --- | --- |
| H | Observatory | False status contradiction versus a genuine consultation-first violation and qualified voice criticism |
| B | Costume workroom | Explaining versus deciding, duplicate cleanup, real endpoint failure and a secondary ambiguous critique |
| G | Ferry terminal | Endpoint and continuity controls, with the earlier-choice claim retained as secondary |
| K | Concert hall | Compatible approval status, an approval-first violation and defensible impulsiveness |
| L | Pottery workshop | Successful prior discrimination of invented prerequisites while retaining urgency and endpoint criticism |
| M | Railway shed | Version ownership, cabinet endpoint and grounded movement interpretation |
| N | Floodgate inspection — fresh | Compatible authorization status, a real authorization-first condition and impatience as a reading |
| P | Bookbinding workshop — fresh | Before-explaining wording, an already made decision, intact stitches and a qualified consultation-related impression |
| Q | Seed archive — fresh | Explicit within-revision chronology versus original/revision comparison, drawer endpoint and impending movement |

All six existing cases, eighteen claims and their historical gold are unchanged.
The twelve historical CV wire payloads exactly match the first repetition of the
preceding fixed-claim run. The three new pairs contain complete scenes of 238–252
words, complete assignment/context artifacts, deterministic version identities,
catalog offsets and explicit material-scope annotations withheld from model input.
Each new family has one explicit unsupported factual claim and two supported
controls; unsupported claim position varies across the three families.

Both arms receive full original/revision prose, context, mechanical appendix and
the same three claims in fixed claim order. OR presents original first; RO presents
revision first. O/R evidence namespaces always refer to version, not display order.
No gold, prior judgments, material-scope annotations or demonstrations enter requests.

CV retains the exact existing system instruction, claim contract and schema. MC
adds only the following user-role instruction immediately before the unchanged
output contract. The serialized request differs only by this message; administrative
execution identifiers and budget records use the new experiment identity.

```text
MATERIAL-CLAIM ASSESSMENT
For each supplied claim, use the existing reason field for a brief source-based
assessment of its material factual assertions. Identify the assertions being checked
and state whether each is supported, contradicted, not established as claimed, or
genuinely unresolved. Cover material assertions rather than selecting only the easy
or defensible parts. Where the claim includes literary interpretation, distinguish
that interpretation from its factual premises and assess whether the reading is
defensible from the complete sources; it need not be the only reasonable response.
Then state why the judgment applies to the entire supplied claim as worded. A
material factual assertion that the sources contradict or do not establish prevents
a supported judgment, even when other clauses or the claim's general concern are
defensible. Do not replace a false assertion with a plausible core, extend a condition
to a different action, or import an original-only event into revision chronology.
Preserve genuine uncertainty without using disagreement about taste to excuse a
false factual assertion. Keep the explanation bounded by what the sources support.
Provide only this concise evidence summary, not an internal reasoning trace. Retain
the exact output fields, short-reference rules and reason-length limit; do not add
fields, copy the input, or treat this instruction as evidence about any claim.
```

This requests an observable evidence summary, not an internal reasoning trace or
proof of a particular internal process. The schema, 2,000-character reason limit,
eight-reference maximum and strict rejection of duplicates remain unchanged. No
provider `format` field, catalog enum, correction pass or new production role is
introduced. Structural validity does not establish factual correctness.

## Fixed model and allowance

Use **`deepseek-v4.1-flash:cloud` through the local Ollama daemon**, with the archived
last-verified **Ollama 0.40.10** baseline. Selected model digest:
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
The saved tag/show capabilities are pinned. Temperature is **0.2**, top-p **0.95**,
seed **20261022**, thinking=false and stream=false, with a 32,000-token context.
Approved preflight must match; no silent baseline or model refresh is permitted.

| Resource | Frozen ceiling |
| --- | ---: |
| Total attempts / per arm | **36 / 18** |
| Retries, resampling or correction calls | **0** |
| Input / output per call | 24,000 / 8,000 tokens |
| Aggregate input / output | 864,000 / 288,000 tokens |
| Active generation time per call / aggregate | 300 / 10,800 seconds |
| Archived-rate token reservation | **$0.60480** |
| Planning allowance | **$0.75** |

The price arithmetic uses archived input $0.30/output $1.20 per million tokens,
without discounts; it is not a new tariff lookup or provider-enforced cap. Actual
billing is unknown. Input estimates are 3,500–4,798 quarter-byte tokens; these are
estimates, not measured usage. Runtime enforces the frozen usage boundaries.

## Scoring, inspection and decision

Keep B/C03 and G/C03 as **secondary scope-sensitive probes**, preserving their exact
historical gold and reporting their answers separately. They cannot create recovery
opportunities, earn primary semantic recovery, or trigger a protected semantic loss.
An invalid response still counts as a delivery failure for the entire response.

Each arm has **50 primary claim opportunities** (32 supported, eighteen unsupported)
and four secondary opportunities. Report exact labels, abstentions, entire-reason
grounding, citation support and usability separately. Invalid or dispatched terminal
answers remain failed opportunities; unstarted calls are reported separately.
Uncertainty against a definite primary gold label is an abstention, not a recovery.

A usable primary claim needs a correct label and a supported entire reason and
citations. A correct label with an invented fact, an unjustified exhaustive count,
or a substituted proposition remains unusable. Representative citations are assessed
against complete sources; no new rule requires every incidental observation to
have a separate citation. A qualified, defensible craft reading need not be a unique
reader preference. Whole-response historical-gold usability is descriptive and does
not override the secondary-claim exclusions.

Record material-assertion coverage as complete, partial, unclear or not applicable
for both arms. Coverage is a separate descriptive measurement, not a new structural
validity rule or automatic semantic truth detector. Existing whole-reason support
still determines whether a judgment is grounded.

MC is retained as **promising diagnostic evidence only** when all conditions hold:

1. At least **17/18 valid responses**, including **5/6 fresh**, with no paired loss
   of a valid CV delivery.
2. At least **four paired primary claim recoveries across two families**, including
   one unchanged claim in both orders and at least one fresh-family recovery. Both
   deliveries must be valid; CV must be unusable and MC fully usable. Invalid-to-
   valid gains are separately reported delivery gains.
3. No paired loss of a usable primary CV claim, no rejected/abstained supported
   primary control that CV labels correctly, and no loss of grounded primary
   reason/citation support where CV's explanation was grounded. Uncertain support
   does not qualify as grounded support.

Recovery opportunity is evaluated from valid CV primary failures independently of
MC's success. If those failures cannot satisfy all recovery conditions, report
**insufficient opportunity** without adding calls. An independent delivery/protected
loss still produces **no advancement**. Incomplete runs cannot advance. Report by
arm, family, new/existing origin and order; repeated or related claims are not
independent samples and these thresholds do not establish generalization.

Export masked review IDs and complete sources, inspect all valid reasons and
evidence, and seal notes before decoding arm/order keys. Inspect invalid captures
separately without repairing or awarding credit. Reason style may reveal MC, so
this is assistant source adjudication with partial masking, not a blind human
preference test.

## Schedule and stops

The fixed sentinel sequence is:
`CV-H-OR`, `MC-H-OR`, `MC-N-OR`, `CV-N-OR`, `MC-N-RO`, `CV-N-RO`, `CV-H-RO`,
`MC-H-RO`. Then B/P, G/Q and K/L/M complete both arms and orders with balanced arm
order. The exact 36-row schedule is sealed in the bundle.

After eight completed calls, stop if either arm has zero valid responses, or the
same structural-failure signature occurs at least three times across both families,
counting both arms together. One normal-stop invalid response consumes its attempt
and is never retried. Semantic failures are outcomes, not resampling triggers.

Stop immediately on non-200 responses, transport failure, timeout, cancellation,
truncation/non-stop completion, unexpected thinking, missing/invalid/excess usage,
version/model drift, source/request/capture tampering or incomplete terminal
evidence. Every dispatched attempt counts, including unknown usage. Preserve the
gateway error chain and terminal capture; export remains available after a stop.
Initial/before/after version responses are durably captured before validation.
No terminal continuation, transferred allowance or extra retry is allowed. A clean
cell-boundary interruption may resume only the untouched frozen remainder within
the same ceiling. Exclusive operator locks and replay checks prevent duplicate work.

## Local verification and evidence

The private preparation bundle is
[`data/diagnostics/reviewer-material-claims-v61-2026-10-24/`](../../data/diagnostics/reviewer-material-claims-v61-2026-10-24/).
It contains the [complete casebook](../../data/diagnostics/reviewer-material-claims-v61-2026-10-24/casebook.md),
case/claim audits, 36 exact prepared requests and wire payloads, budgets, scoring,
stops, archived metadata, isolated operator, version capture, masked inspection,
paired scoring and offline tests. Full prose and raw historical captures remain
local and ignored by Git.

Verification checks exact historical CV equivalence, MC-only request differences,
withheld gold, source/claim/version/offset binding, full mock execution and clean
restart, ceilings, sentinel decisions, terminal error chains/unknown usage,
capture-before-validation, tamper rejection, sealed inspection and paired scoring.
Real HTTP is blocked in tests. The restricted Windows asyncio stall is retained in
verification records; the same mock-only suite runs outside that restriction.
**153 offline tests**, Ruff lint/format and strict mypy on all seven scripts pass.
The plan hash is recorded in the tracker and sealed verification artifacts.
No product code or production prompt changed; unrelated
frontend/API/worker builds are not applicable.

The plan seal binds local input/code files, **1,196 historical source fingerprints**
and this public document. The tracker records the exact plan hash. No approval file
or live directory exists at preparation closure. A later approval must bind that
plan, full unpublished prose/context/claims, Ollama Cloud via the local daemon, the
36-attempt ceiling and zero retries before any inference.

Provider investigation remains deferred. Preserve the nine human ties and future
reader focus on feel/emotion, flow, character and story-breaking problems. Even a
positive result requires separate full-review integration and story-quality work.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**
