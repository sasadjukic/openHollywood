# Sol-high B/H authority comparison — frozen local plan

Date: 2026-11-07. **Local preparation complete; awaiting separate live approval.**
Production prompts/profiles unchanged; full workflow canary **ON HOLD**.
No generation, input-count, catalog or daemon calls were made during preparation.

The question is whether a case-level **provenance and exact-copy receipt** improves
Sol-high's ability to distinguish reviewer allegations and repair requests from
actual events and version-specific assignment authority. This tests an application
presentation mechanism on clear authored controls. It does not measure natural-error
precision, necessary edits, prose preservation or literary quality.

## Frozen comparison

| Item | Frozen value |
| --- | --- |
| Model | `gpt-6.1-sol`, reasoning `high`, OpenAI Responses |
| B | Complete sources, manifest, unchanged whole claims and explicit work briefs |
| H | Identical B content plus the derived provenance/visibility and exact-copy receipt |
| Families | A seed-house sluice; B observatory booking; C cinema reel |
| Claims | Six per family: two supported, two contradicted (`unsupported`), two unavailable (`uncertain`) |
| Design | Three families × two conditions × two presentation orders × two exact repeats |
| Ceiling | **24 attempts**, at most 24 generations |
| Assessment denominator | **144 fixed slots**: 72 per condition, 24 per support class per condition |

The [authored-control handoff](reviewer-authored-authority-controls-2026-11-07.md)
records all eighteen whole claims, admission rationales and explicit counterevidence.
The full earlier/current scenes, assignments, reviewer allegations, requests and
availability records are preserved in the private bundle. No claim or gold was
reworded for this freeze. The saved natural controls remain separate calibration;
they do not consume additional calls or become authored-negative evidence.

H adds **6,211–6,252 UTF-8 bytes**. Every underlying source, role, version and
availability fact is already visible to B. The receipt is an organized repetition
and derived binding, with no per-claim verdict, label or gold rationale. Any benefit
therefore concerns this combined presentation; it does not isolate which receipt
element helped. Token counts are not inferred from byte sizes.

`SC` presents sources before claims; `CS` presents claims before sources. Claim
order Q1–Q6 stays fixed, and H's receipt stays last. Each six-pair block uses
A-SC, B-CS, C-SC, A-CS, B-SC, C-CS. Within those pairs, the first repeat alternates
B/H then H/B; the second repeat reverses those arm orders. Corresponding repeats
have byte-identical generation and count bodies. This varies presentation and
execution position without treating repeats as new independent families.

## Requests and native boundary

The frozen request includes the full prose/context, six active claims, diagnostic
artifact identities and the closed native assessment schema. Both conditions use
the same diagnostic system instructions. The response is exactly one assessment
per active claim, with support, up to eight distinct registered references and a
nonblank reason of at most 1,200 characters. The application resolves references
to complete source fields and validates exact IDs, versions, hashes and scope.
Binding does not establish semantic support or authorize a writer.

This uses the existing native reference schema in both arms, rather than a quote-
witness response. B is unchanged between the paired conditions; this experiment
is **not** an exact replay of an older ordinary-review request. Earlier absolute
scores must not be used as if they were an additional matched control.

The actual OpenAI adapter renders and replays the frozen wire: strict structured
output, `high`, standard service tier, 32,000 maximum output tokens, storage off,
background off, streaming off and truncation disabled. Portable seed, temperature
and top-p settings are omitted by this reasoning adapter; they are not effective
sampling controls. There are no tools, conversations or prior-response pointers.

Current official documentation confirms Sol supports high reasoning, Responses and
structured output, with a 1,050,000-token context and 128,000-token maximum output.
The diagnostic deliberately retains its smaller existing limits. Standard published
rates remain $2/M input, $0.10/M cached input, $2.50/M cache writes and $10/M output.
[OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol)

The retained specification's pricing-version label records its original review
date; the values were rechecked on 2026-11-07 and are unchanged. Account access,
server acceptance of this exact schema and actual input counts remain unverified
remotely. Model-list and returned-model checks after approval will enforce the
selected alias; they cannot prove immutable backend weights.

## Budget and destinations

| Resource | Per attempt | Maximum across 24 attempts |
| --- | ---: | ---: |
| Input tokens | 24,000 | 576,000 |
| Generated tokens, including reasoning | 32,000 | 768,000 |
| Active count-plus-generation time | 600 seconds | 4 hours |
| Catalog check timeout | 25 seconds | 10 minutes |
| Planning allowance | $0.60 | **$14.40** |
| Conservative published-rate bound | $0.38 | **$9.12** |

The reference bound uses the existing 1.25 input multiplier to cover the published
cache-write rate and assumes the full output reservation. Actual billing remains
unknown; this is a planning bound at the reviewed rates, not a bill or price guarantee.
Latency, input, output, reasoning and cached tokens will be reported separately,
including H's overhead and any unknown usage.

**24 attempts is not a 24-HTTP-request ceiling.** Each reserved attempt permits
one full-context input-count POST and, only if that succeeds within budget, one
generation POST. The ceilings are **24 count POSTs + 24 generation POSTs**, plus
at most 24 non-story catalog GETs. Count requests supply the same model, input,
schema and reasoning configuration; the official endpoint is
[`POST /responses/input_tokens`](https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count).

Separate approval must cover full unpublished fictional prose, assignments, reviewer
assertions, repair requests and diagnostic context at **both**:

- `https://api.openai.com/v1/responses/input_tokens`
- `https://api.openai.com/v1/responses`

The runner uses the previously authorized application credential without persisting
it. Preparation did not send it to a provider. No story text is sent in catalog GETs.
There are **zero retries, repairs, continuations, fallback models or budget transfers**.
An input-count failure consumes the reserved attempt. An early catalog failure
consumes no story attempt but still ends the diagnostic. Unknown usage stays unknown.

## Prospective scoring and decision

All 144 slots remain in the denominator. Delivery, binding and label correctness
are recorded separately. A **grounded whole-claim success** requires valid delivery
and binding, the correct whole-claim support label, adequate cited evidence for
every material component, coverage of all material qualifiers, and an explanation
faithful to the supplied evidence without unsupported assertions.

Every valid output receives an explicit inspection bound to the request hash and
exact raw final hash. The scorer does not infer semantic success from a label or
matching words. Invalid and unrun slots receive no grounded credit and are reported
as unavailable, rather than silently counted as semantic errors. Inspect their
delivery/stop status as part of accounting for all fixed slots.

- Supported requires all material parts. A decisive contradiction can determine
  an unsupported compound label, while its true attribution still needs explanation
  and evidence for whole-claim credit.
- Uncertain requires the actual unavailable source to remain unknown; grounded
  credit requires its availability record. A similarly worded available assignment
  cannot establish a missing document's contents.
- C Q1's scale quotation alone does not prove non-opening. The earlier prose's
  explicit non-opening evidence is necessary.
- B Q2 concerns the date relation; B Q3 concerns recognition. Historical fulfillment,
  current obligations and current realization remain distinct.
- The admitted example reference sets are not a whitelist. Equivalent complete
  evidence is allowed with an explicit, source-grounded inspection rationale.

Report support-class/family confusion, material coverage, evidence adequacy,
explanation fidelity, both orders and repeats, and all **72 B/H slot pairs**.
Compare tokens, latency, delivery and reference cost alongside accuracy.

The prospective **promising-receipt** criterion is H **72/72 grounded**, no
B-pass/H-fail pair, and at least one family/claim recovery repeated in all four
order/repeat cells. A perfect tie supplies no demonstrated accuracy benefit for H;
inspect its overhead. Other outcomes remain diagnostic evidence for local audit.
These are decision rules on three authored families, not population estimates or
statistical independence claims. No result automatically changes production.

## Stops and verification

Stop before transport for absent/mismatched approval, source/request/runtime drift,
an exclusive lock, an unresolved reservation or failed model-catalog check. After
reservation, the **first** transport/provider/HTTP error, timeout, cancellation,
empty/refusal/length result, schema/active-ID/binding failure, unknown required
usage, model mismatch or resource overrun retires every remaining attempt.
Interrupted catalog/request reservations also stop; never resend an unknown call.
Secret-boundary failure blocks further dispatch. There is no automatic recovery.

A schema-valid wrong label, inadequate known reference or unsupported explanation
continues the fixed comparison; those are evaluation outcomes, not delivery retries.
The runner retains sanitized terminal evidence, error chains and available usage,
without storing credentials or raw/encrypted reasoning. Every final binds to its
native assessment work and completion receipt.

**338 tests pass: 85 private harness tests and 253 existing assessment/provider
tests.** All ten recorded checks pass, including repository Ruff/formatting/strict
mypy for 230 Python files, the same checks for ten private helpers, and deterministic
request/rule/slot generation. The 56 warnings come from existing deliberately
unchecked Pydantic test fixtures. Full-suite/frontend/build checks were not repeated
because no tracked implementation, schema or dependency changed.

The immutable plan seals **48 preparation/log files and 296 source pins**: the
64 authored-control members, their seal, the retained runner source and 230 tracked
Python files. Plan SHA-256:
`53638172ce2ead7f42810934478ce59dac69630eacea0d73f8d6775691d60d90`.
The private tests exercise actual adapter wires against mocks,
the complete 24-attempt schedule, all terminal classes, approval/hash drift,
exclusive locks, interrupted reservations, usage accounting, raw-final-bound
inspection, whole-claim scoring and source/gold invariants. They also replace all
gold labels/rationales and confirm that no provider request changes.

The initial mock run caught serialization ordering drift in the native schema's
`required` arrays. The local preparation now constructs wire bodies from the
canonical saved representation; replay matches exactly. Superseded unapproved
drafts are archived and excluded from execution. No source gold or production
adapter was changed. Windows asyncio checks run outside the restricted sandbox
with credential variables removed; private tests block real HTTP, sockets, DNS
and SQLite. Existing integration tests use temporary test databases.

## Local artifacts and next step

Private root: `data/diagnostics/reviewer-authority-bh-v61-2026-11-07/`.

- [Full bundle and operator sequence](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07/README.md)
- [Exact requests](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07/requests.json), [schedule](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07/schedules.json), [gold](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07/gold.json)
- [Fixed slots](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07/fixed-slots.json), [scoring](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07/scoring.json), [budget](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07/budget-M.json), [stops](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07/stops.json)
- [Verification](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07/verification.json), [immutable plan](../../data/diagnostics/reviewer-authority-bh-v61-2026-11-07/plan.json)

**Next: obtain approval of this frozen plan before either story-bearing endpoint.**
After approval, execute once, inspect every fixed slot, document results and update
the tracker. Keep the natural-negative admission gap explicit. Human craft review
continues to address feel, flow, character and story-breaking details; this diagnostic
aims to improve factual assessment that may prevent unjustified editing.

CW-007/CW-013 remain open; CW-014 remains unqualified. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; full workflow canary ON HOLD.**
