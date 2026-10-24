# Frozen DeepSeek C2/D1/D2 delivery comparison

Date: **2026-10-23**. **PREPARED LOCALLY; AWAITING NEW LIVE APPROVAL.**
No inference or daemon discovery was performed. Production remains **prompt 61 /
graph 9 / fulfillment policy 1** and the full workflow canary remains **ON HOLD**.

This implements the [delivery proposal](reviewer-delivery-repeat-proposal-2026-10-23.md)
following the [local delivery/aggregation audit](reviewer-delivery-aggregation-audit-2026-10-23.md).
The user reports that Ollama updated between sessions to **0.40.9**. This new
freeze therefore expects **0.40.9**, replacing the proposal's 0.40.8 expectation.
It is a user-reported baseline, not a local discovery result. Earlier 0.40.8
requests, results, stops and seals remain unchanged.

## Frozen question and arms

Can consistent schema presentation improve delivery without losing supported
complete reports? Does placing the group identity first add value beyond D1?
All three arms use `deepseek-v4.1-flash:cloud` with the same cases and settings.

| Arm | Frozen intervention | Calls |
| --- | --- | ---: |
| C2 | Unchanged archived C2 renderer, system text and contract | 16 |
| D1 | Exact archived D1 renderer: aligned property/required order | 16 |
| D2 | D1 with record identity first in both lists; the effective extra change is moving `group_id` from fourth to first | 16 |

Names, enums, evidence cardinality, required membership and validation stay
unchanged. There is no M1 ownership card, temporal cue, vocabulary change,
provider-enforced response schema, structural repair or extra judge. D1 request
messages are checked against the archived renderer byte-for-byte; C2 controls
retain their original message content. D2 differs only in the declared schema
field presentation. Production prompt templates are not edited.

Every valid response also gets a **separate application-owned mandatory-aggregate
view**. It retains the original flag and explanation, explicit task membership,
uncertainty and craft findings. It supplies no writer instruction and never
changes the primary scores. Invalid whole reports receive no aggregate. This
calculation makes no model calls and is not a production acceptance gate.

## Cases, identities and schedule

Eight cases × three arms × two presentation orders = **48 attempts maximum**.
OR and RO swap display order, retaining original/revision identities. Four
historical case records—including packets, versions, labels and inspection
anchors—are copied unchanged from C2/M1. Four new cases span two fresh families.

| Case | Frozen contrast | Groups | Original/revision words |
| --- | --- | ---: | ---: |
| A00, community radio | Recognition lost; forbidden broadcast; independent optional departure | 3 | 270 / 275 |
| B10, costume workroom | Discovery retained; prohibited alteration; optional duplicate cleanup | 2 | 275 / 273 |
| CN, conservatory | Real contradiction outside narrow mandatory retention | 1 | 274 / 296 |
| DB, sound archive | Real contradiction expressly included in mandatory scope | 1 | 278 / 295 |
| E-clean, flooded footbridge | Split discovery, carpenter appointment and closed endpoint retained; adjacent duplicate removed | 1 | 296 / 288 |
| E-compound, same family | Split discovery lost, bridge opened, appointment retained; same independent duplicate cleanup | 3 | 296 / 293 |
| F-narrow, bakery order | Handwriting recognition, driver question and unstarted order retained; same-time crate-count contradiction outside retention task | 1 | 313 / 327 |
| F-broad, same family | Identical F prose; consistency now explicitly mandatory | 1 | 313 / 327 |

E preserves an independent reason for the carpenter appointment: the routine
post-flood inspection. The appointment itself does not prohibit intervening
actions; the explicit endpoint prohibits leaving the bridge open. Optional
cleanup is a separate complete paragraph group. F's reliable narration gives
incompatible exact counts for the same single crate at the same noon bell;
this is not dialogue or a successive state. Other existing loaves do not mean
the new order has started. No literary preference is prescribed.

Complete prose, context artifacts, exact source catalogs, changed units,
paragraph groups, withheld labels and source-bound local inspection are in the
[private casebook](../../data/diagnostics/reviewer-layout-v61-2026-10-23/casebook.md)
and `cases.json` / `local-case-audit.json`. They remain local and ignored by Git.
These are **six family clusters**, not 48 independent stories.

Case order is **A00, E-clean, CN, F-broad, B10, E-compound, DB, F-narrow**.
Display-order precedence alternates by case. The arm schedule rotates all six
permutations; each arm appears in each within-triplet position five or six times.
The exact order and all 48 rendered requests are frozen in `schedule.json` and
`prepared/`. No output-dependent case selection or group boundary changes.

## Budget and identity

| Limit | Frozen value |
| --- | --- |
| Attempts | **48 total; 16 per arm; one per cell** |
| Retries, replacements, repair/judge calls | **0** |
| Input / output / context per call | 24,000 / 8,000 / 32,000 tokens |
| Per-call active time | 300 seconds |
| Aggregate input / output reservation | 1,152,000 / 384,000 tokens |
| Aggregate active-time reservation | 14,400 seconds |
| Temperature / top-p / seed | 0.2 / 0.95 / 20261022 |
| Thinking / streaming | false / false |
| Expected daemon | **0.40.9**, user reported; must match at approved preflight |
| Reference-rate reservation / planning allowance | $0.80640 / $1.00 |

The cost estimate uses previously archived rates of $0.30 input and $1.20 output
per million tokens, without discounts. It is not a fresh price check, actual
billing or an enforceable billing cap. The largest prompt-size estimate is
6,222 tokens using UTF-8 bytes divided by four; this is not tokenizer measurement.
Actual returned usage must satisfy the frozen limits.

Archived model digest:
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
The existing capability snapshot is retained, not rediscovered. Approved
preflight must match this digest, the capability fields and thinking support;
a mismatch stops rather than refreshing the frozen baseline. Version is checked
at preflight, before and after each inference, and across clean restarts.

Dispatch would send **full unpublished fictional prose and context to Ollama
Cloud through the local Ollama daemon**. This preparation is not that approval.
Earlier budgets remain closed: the three-pilot total stays 41 with D stopped and
seven unused slots unavailable; the completed C2/M1 run stays at 48. No rollover.

## Stops, accounting and restart

The first **12 calls** are A00 and E-clean, both orders in all arms: four responses
per arm across two families. Stop the entire comparison if any arm has zero valid
responses, or one structural signature occurs in at least three of its four
responses across both families. The archived classifier preserves duplicate-key
paths, normalizes array positions and distinguishes malformed JSON, invalid
evidence and schema errors. No failed arm's unused allowance transfers elsewhere.

Normal-stop malformed answers remain failed cells. Any non-200/transport/timeout
or cancellation, length/incomplete finish, missing or excessive usage, unexpected
thinking, model/version drift, source/request tampering, unresolved reservation
or ledger inconsistency blocks further dispatch. An automatic daemon update
during execution stops the run; it is not permission to resume on a new version.

The harness reserves before dispatch and records exact wire data, raw captures,
metadata, version checks, receipts and per-cell seals. A reserved uncertain or
failed attempt is not reclaimed. A clean restart resumes only completed cell
boundaries under the same plan and version, without duplicate calls. A terminal
stop cannot resume; its gateway error chain and unknown usage remain available
through the supported audit/export path. A single-operator lock prevents
concurrent dispatch. Completion at 48 prevents further discovery or inference.

## Frozen scoring and decision

Strict unique-key JSON, whole-report schema and evidence/source validation come
first. Invalid responses get no semantic credit. Valid responses are exported
with arm/order hidden and shuffled, then inspected against the complete source.
Each assessment field requires an exact bound claim, support judgment and
source/version/offset evidence. Notes are sealed before key decoding. Wording can
reveal condition; this is factual operator inspection, not blind human literary
preference. Unsupported and uncertain claims remain distinct and neither counts
as supported.

Score delivery, supported task/fact/endpoint/aggregate judgments, group labels,
optional-edit success and actual contradiction detection separately. Complete
usability additionally requires supported claims in **every assessment field**,
including craft and overall comparison. Contradiction inspection needs both
incompatible source assertions, not merely a negative craft rating. The model's
original aggregate remains scored even when the separate application view differs.

For each candidate against concurrent C2, require all of:

- **15/16 valid**, including **7/8 fresh cells**.
- **Four paired recoveries** where C2 is invalid and the candidate is valid and
  fully usable, spanning **two families**, including **one case in both orders**.
- **No loss** of a valid C2 report, usable report, supported target judgment,
  detected genuine contradiction or successful supported optional edit.
- All **48 scheduled cells complete**. Incomplete/stopped runs cannot advance.

Delivery-only validity gains without complete usability do not qualify. If C2
has too few failures to demonstrate recovery, report that limit without expanding
the run. No label repair, one-order gain or aggregate substitution changes the
primary decision.

Screen D1 and D2 separately. If only one passes, retain that candidate as promising
diagnostic evidence. If both pass, prefer D1 unless D2 has **two additional paired
fully usable reports over D1 and no losses on any protected dimension**. For this
tie-break, a D1 report may be invalid or valid-but-unusable; the main C2 recovery
threshold still requires C2-invalid cells. This makes the comparison of complete
reports explicit rather than equating validity with usability.

Passing is `retain_promising_diagnostic_only`; a completed failed screen is
`retain_limited_evidence_no_advancement`; a stopped run is
`incomplete_no_advancement`. No outcome qualifies production, proves a causal
mechanism or demonstrates better story quality.

## Local verification and next action

**138 offline tests pass: 116 preparation/harness checks plus 22 unchanged
gateway/contract checks.** Ruff lint/format and strict mypy pass on five private
scripts. Tests exercise all 48 exact adapter requests via HTTP mocks, clean
restart, per-arm and total ceilings, all-arm sentinels, sixteen non-200 fixtures,
terminal audit/export, source/assessment binding, complete field coverage,
independent losses and the D1/D2 preference rule. No mock answer is model evidence.

The first restricted-process attempt stopped at Windows asyncio's local socket
pair initialization; an empty-loop probe reproduced it before HTTP dispatch.
The completed mock tests ran outside that process sandbox with real HTTP
transports blocked. This was local verification, not daemon discovery. Production
and frontend source did not change, so unrelated application suites and the
production build were not repeated.

The immutable plan hash is recorded in the tracker and private preparation
bundle. The seal binds exact cases, requests, executable scoring/stops,
source/runtime fingerprints, verification and this public plan's hash. No
approval record or live run directory exists at preparation closure.

Offline verification from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-layout-v61-2026-10-23/layout_experiment.py verify
.venv/Scripts/python.exe -X utf8 -m pytest data/diagnostics/reviewer-layout-v61-2026-10-23/test_layout.py tests/models/test_ollama_gateway.py tests/models/test_contracts.py -q
```

The next action is review of this frozen plan, followed by new approval explicitly
covering its full-prose/context destination and 48-call ceiling. Do not start a
live preflight or inference until then. Retain the nine human ties and future
human emphasis on feel/emotion, flow, character and story-breaking details, with
mechanical evidence supplied by machines. **Step 19 remains IN PROGRESS; Step 20
NOT STARTED; the canary remains ON HOLD.**
