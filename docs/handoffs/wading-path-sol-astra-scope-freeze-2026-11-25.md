# The Wading Path · Sol 6.2 and Astra 6.2 on narration and event scope

**Frozen for approval on November 25, 2026.** Six cases each go to `gpt-6.2-sol` and `gpt-6.2-astra` on high reasoning, once with the ordinary B brief and once with explicit scope (X). All 24 input counts must pass before the first of up to 24 generations. The run is single-use, with zero retries. Approval SHA-256 is `01513dd73de11e779413b554a9bb04703e8706d2c6ca4620e254cbb84890c7dd`. [Approval manifest](../../data/diagnostics/wading-path-sol-astra-scope-2026-11-25/plan.json) · [48 exact request bodies](../../data/diagnostics/wading-path-sol-astra-scope-2026-11-25/requests)

The earlier Sol 6.2 B run earned 0/0 on the open event (SE), 1/0 on its narration counterpart (SN) and 1/1 on each of four controls. The new comparison asks whether a model change, a statement of what the claim covers, or both help on those two misses while preserving the controls. A fresh Sol B observation measures whether the baseline itself recovers. [Earlier paired scores](wading-path-sol-versions-narration-event-results-2026-11-25.md) · [Local evidence-coverage rehearsal](wading-path-evidence-coverage-rehearsal-2026-11-25.md)

## Cases, gold and order

Every draft ends the depicted approach with Elias and Maya standing three strides short of the master breaker panel housing. The three histories vary what else the narrator tells us about that scene. Each request assesses one of two claims, either that the draft explicitly recounts a joint arrival or that a joint visit occurred at some time during scene four. The registered draft versions, source roles, claim wording, gold and passage criteria come from the sealed six-case rehearsal. [Exact claims and versions](../../data/diagnostics/wading-path-sol-astra-scope-2026-11-25/gold.json) · [Case evidence criteria](../../data/diagnostics/wading-path-sol-astra-scope-2026-11-25/evidence-criteria.json)

| Case | History and claim | Gold | What earns the evidence point | Order in each stage |
| --- | --- | --- | --- | --- |
| SN | Stop alone · narrated arrival | unsupported | Use the complete draft to distinguish entering the plenum, seeing the housing and stopping short from a narrated joint arrival. A scene-wide denial of a visit overreaches. | SB, AX, SX, AB |
| XE | Whole-scene exclusion · visit occurred | unsupported | Locate the minimum-distance account covering both people from the opening huddle through the cut. | AB, SX, AX, SB |
| VN | Earlier visit confirmed · narrated arrival | supported | Locate the retrospective that explicitly recounts both people reaching the housing together. | SX, AB, SB, AX |
| SE | Stop alone · visit occurred | uncertain | Locate the approach and final gap. Explain why the earlier interval leaves a joint visit open. | AX, SB, AB, SX |
| XN | Whole-scene exclusion · narrated arrival | unsupported | Account for the complete draft, including the retrospective minimum distance and the absence of a narrated joint arrival. | AB, SB, AX, SX |
| VE | Earlier visit confirmed · visit occurred | supported | Locate the joint arrival after plenum entry and the subsequent return up the passage that precedes the final stop. | SX, AX, SB, AB |

The first letter of each arm is the model (S = Sol, A = Astra). The second is the presentation (B = ordinary, X = explicit scope). Every pair of arms appears in each relative order three times. The same order governs counts and generations. The previously scored S2 endpoint is an offline reference and consumes zero slots. [Source-bound S2 control](wading-path-evidence-coverage-rehearsal-2026-11-25.md)

## Exact presentation change

The 12 Sol B request bodies, including both endpoints, match the archived Sol 6.2 bodies byte for byte. Within either presentation, Sol and Astra bodies differ only in the top-level model ID. X keeps the system message, claim, B work brief, complete source context, schema and reasoning effort. It adds one field, `claim_scope.assessment_target`, whose value depends only on the claim type.

- **Narration** — “Assess what the complete selected draft explicitly recounts during scene four. Limit any further conclusion about physical occurrence to what the cited account establishes.”
- **Event** — “Assess whether the event occurred at any time during scene four. Identify the interval covered by the cited observation and explain its bearing on that claim.”

Both endpoints receive the full selected prose, saved review and original story context. The selected unit is A001 and the complete selected draft resolves to E1420 on its exact version. Gold, evidence criteria and previous scores stay local. Both models use structured output, `reasoning.effort=high`, standard service and `store=false`. [Renderer and source checks](../../scripts/wading_path_sol_astra/plan.py)

## Scoring and decision

Award **one judgment point** for the exact frozen whole-claim label. Independently award **one evidence point** for a reason and valid citations that cover the relevant people, location and time on the selected draft. Equivalent passage locators qualify. The final gap alone earns zero evidence points on all six scene-wide claims. Grade reasons with model, presentation, returned label and dispatch order masked, record the cited passages and the basis for each grade, then seal those decisions before joining labels to gold. This permits both 1/0 and 0/1. [Frozen scoring](../../data/diagnostics/wading-path-sol-astra-scope-2026-11-25/scoring.json) · [Evidence form](../../data/diagnostics/wading-path-sol-astra-scope-2026-11-25/evidence-form-schema.json)

Inspect every fixed slot. Report both scores for each eligible generation, SE and SN individually, and all four controls. Compare Astra with Sol under each presentation and X with B under each model. Record gains, losses and ties on each axis. Report a fresh Sol B recovery separately from a paired gain. Credit an improvement to a condition only when its matched comparator misses that axis. An arm qualifies as a within-scene candidate only if it earns both points on all six cases. Any missing eligible generation makes the overall comparison inconclusive. Report model usage, reasoning tokens when supplied, elapsed time and estimated generation cost. These 24 observations concern one family and one attempt per condition. [Scorer](../../scripts/wading_path_sol_astra/scoring.py)

## Budget and stops

| Limit | Frozen allowance |
| --- | --- |
| Counts | Slots 1–24, serial, to `POST https://api.openai.com/v1/responses/input_tokens` |
| Generations | Slots 25–48, serial, to `POST https://api.openai.com/v1/responses`, after all counts pass |
| Per arm | Six counts and up to six generations |
| Generation tokens | Up to 160,000 input and 4,096 output per attempt, including reasoning within output. Combined ceiling of 3,840,000 input and 98,304 output tokens |
| Estimated generation cost | Sol up to $5.29152, Astra up to $21.16608, combined **$26.45760** |
| Time | 120 seconds per count, 300 seconds per generation, 168 minutes for the schedule |

The estimate allows the standard 30-minute cache-write price for every input token. Sol is bounded at $0.44096 per generation and Astra at $1.76384. The count limit stays below both models’ long-context price threshold. Account access and provider acceptance remain untested by this local freeze. [OpenAI Sol 6.2 rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [OpenAI Astra 6.2 rates](https://developers.openai.com/api/docs/models/gpt-6.2-astra)

Verify the manifest, exact requests, source versions, code and unused ledger before dispatch. Require a positive in-budget count at every slot. Stop globally at the first transport or capture failure, non-200 response, timeout, deadline, malformed or duplicate JSON, model mismatch, refusal, truncation, invalid claim or citation, missing required usage, or budget breach. Record intent before sending. An interruption consumes the registration. Preserve unknown usage and untouched slots. An eligible semantic error receives its scores and the fixed schedule continues. There are zero retries, replacements, redirects or fallbacks. [Single-use runner and auditor](../../scripts/wading_path_sol_astra/run.py)

## Local verification

All **139 offline tests passed**. The 39 request, source, scoring and regression checks covered archive parity, all four comparison directions, masked grading, a failed control, tied arms and missing cells. Nine injected-transport tests exercised the full 48-slot schedule, failure on the last count with zero generations, wrong or missing model identity, wrong claim or citation, interruption and blocked reuse. Another 91 checks covered the shared OpenAI request and response mapping. Repository-wide Ruff lint and formatting passed, and strict mypy passed across 476 Python files. [Request, gold and scoring checks](../../data/diagnostics/wading-path-sol-astra-verification-2026-11-25/requests-and-scoring.xml) · [Injected-transport checks](../../data/diagnostics/wading-path-sol-astra-verification-2026-11-25/injected-transport.xml) · [Mapping checks](../../data/diagnostics/wading-path-sol-astra-verification-2026-11-25/response-mapping.xml)

The independent disk readback verified the approval digest, all 52 frozen members and 56 implementation hashes. The live ledger is ready with all 48 slots unattempted. B remains the default and the full workflow canary stays on hold pending a separate decision. [Unused journal readback](../../data/diagnostics/wading-path-sol-astra-verification-2026-11-25/unused-journal.json)
