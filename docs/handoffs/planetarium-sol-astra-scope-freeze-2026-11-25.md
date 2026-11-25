# Planetarium repeat for Sol 6.2 and Astra 6.2

**Prepared locally for approval on November 25, 2026.** The Wading Path comparison produced one grounded answer to its open event in four attempts, from Astra with explicit scope. This repeat asks whether that recovery transfers from a visit to a projection in a different story. B remains the default. Live calls are paused and the workflow canary is on hold. [Previous result and rationale](wading-path-sol-astra-open-event-audit-2026-11-25.md)

**Approval SHA-256** `8ee223cb4b4bd7251a6ec0c7bfbe764a12383e5aef90ff8dd1a8a0f75da26cd4`. Approval would cover the full prose and context at both OpenAI endpoints for this single-use schedule. [Frozen manifest](../../data/diagnostics/planetarium-sol-astra-scope-2026-11-25/plan.json)

## Sources and gold

Kit and Ada rehearse a commemorative show at Bellweather Planetarium. The plan lists a blue comet cue and the draft places its mounted slide on the console. The fictional review concerns the opening handoff of the cue key. Only the selected draft establishes events during rehearsal. The open draft passes over the middle cues. The two other versions each insert one paragraph immediately before the same closing paragraph. In all three the dome is blank from the closing cue through the end bell. The complete sources were authored for this diagnostic. [All three drafts, original request, plan and review](../../tests/fixtures/planetarium_scope_sources.json)

The narration claim asks whether the draft **explicitly recounts** the projection. The event claim asks whether the comet **was projected at any time** during rehearsal. Each request assesses one whole claim, A001, with E1420 pointing to the complete selected draft. The local gold fixes the exact claim, draft version, text hash, evidence criterion and quoted character spans for each case. [Gold and passage locators](../../tests/fixtures/planetarium_scope_gold.json)

| History | Narration judgment and evidence | Event judgment and evidence |
| --- | --- | --- |
| Open | **ON · unsupported.** The text describes the physical slide and skips over the middle cues. It never depicts the projection. | **OE · uncertain.** The available slide establishes preparation. The middle cues leave an earlier showing possible. The closing observation covers only the ending. |
| Explicit exclusion | **DN · unsupported.** The full account explicitly excludes the projection and gives no affirmative narration of it. | **DE · unsupported.** The exclusion covers the opening bell through the closing cue. The blank dome through the end bell covers the remaining interval. |
| Explicit confirmation | **PN · supported.** The narrator describes the projector casting the comet across the dome and the image going out. | **PE · supported.** That earlier projection establishes occurrence. Its extinction before Kit returns explains the later blank dome. |

## Matched requests

Sol (`gpt-6.2-sol`) and Astra (`gpt-6.2-astra`) both use high reasoning, standard service, structured output and `store=false`. B uses the Wading Path system message and work brief verbatim. X adds exactly one field, `claim_scope.assessment_target`, with the previous wording for each claim type.

- **Narration** — “Assess what the complete selected draft explicitly recounts during scene four. Limit any further conclusion about physical occurrence to what the cited account establishes.”
- **Event** — “Assess whether the event occurred at any time during scene four. Identify the interval covered by the cited observation and explain its bearing on that claim.”

Within each case and presentation, the only difference between the two models' requests is the model ID. Both endpoints would receive the complete selected prose, plan, authored review and original review request. The count uses the generation's model, messages, schema and reasoning settings. The grading key and alternative drafts stay local. Generation bodies are 11,923–12,398 bytes, compared with 375,852–376,453 bytes in the earlier saved-review family. This repeat tests transfer on a shorter, fully authored packet. Differences between families cannot isolate the effect of context length. [Renderer](../../scripts/planetarium_scope/presentation.py) · [48 exact request files](../../data/diagnostics/planetarium-sol-astra-scope-2026-11-25/requests)

| Case order | Arm order within case, identical for both stages |
| --- | --- |
| ON | Astra B, Sol X, Astra X, Sol B |
| DE | Sol B, Astra X, Sol X, Astra B |
| PN | Astra X, Sol B, Astra B, Sol X |
| OE | Sol X, Astra B, Sol B, Astra X |
| DN | Sol X, Astra X, Sol B, Astra B |
| PE | Astra B, Sol B, Astra X, Sol X |

Every pair of arms occurs in each relative order three times. The within-case order reverses the analogous Wading Path quartet. There is one observation per case and arm. [Manifest, request hashes and source versions](../../data/diagnostics/planetarium-sol-astra-scope-2026-11-25/plan.json)

## Independent scores and decision

Award one **judgment** point for the exact frozen whole-claim label. Award one **evidence** point for a cited explanation meeting the relevant case criterion on its exact draft. Equivalent passage references qualify. The blank dome at closing, used alone, earns zero evidence points on all six scene-wide claims. Grade evidence with model, presentation, returned label and dispatch order masked. Record the decisive passage and basis, then seal every eligible evidence decision before joining labels. An eligible wrong judgment can earn its evidence point. [Scoring rules](../../data/diagnostics/planetarium-sol-astra-scope-2026-11-25/scoring.json) · [Scorer and evidence seal](../../scripts/planetarium_scope/scoring.py)

The local OE rehearsal awards **1/1** for identifying the slide, the skipped interval and the limited closing observation and returning uncertain. Inferring “never” from the endpoint scores **0/0**. Inferring “must have happened” from the cue sheet also scores **0/0**. Returning unsupported alongside the grounded uncertainty explanation scores **0/1**. The negative control separately checks a correct exclusion judgment justified only by the closing image, which scores **1/0**. These are authored grading controls. [Rehearsal tests](../../tests/api/test_planetarium_scope.py)

An Astra-X-only transfer requires **both points on all six cases** for Astra X and an open-event miss on at least one axis in each of the other three arms. If Sol B passes OE, record baseline recovery. If Sol X passes OE, report that the less expensive explicit arm also recovered it. If Astra B passes OE, explicit scope was unnecessary for that observed recovery. An Astra X miss on either axis of any case holds escalation. An ineligible or missing cell leaves the overall comparison inconclusive. Inspect every slot and report each eligible score, the four paired contrasts on each axis, usage, reasoning tokens when supplied, elapsed time and estimated generation cost. Even a unique recovery supports only a further test of selective second opinions. [Decision rule](../../scripts/planetarium_scope/plan.py)

## Budget and stops

| Limit | Frozen allowance |
| --- | --- |
| Slots 1–24 | 24 serial counts at `POST https://api.openai.com/v1/responses/input_tokens`. All must pass before the first generation. |
| Slots 25–48 | Up to 24 serial generations at `POST https://api.openai.com/v1/responses`. Six per arm, twelve per model, zero retries. |
| Generation tokens | 160,000 input and 4,096 output per request, including reasoning within output. Aggregate maximum of 3,840,000 input and 98,304 output tokens. |
| Estimated generation cost | Sol up to $5.29152 and Astra up to $21.16608, or **$26.45760** combined. |
| Timeouts | 120 seconds per count, 300 seconds per generation, 168 minutes overall. |

The generation estimate uses the standard 30-minute cache-write rate for every input token, $2.50 per million for Sol and $10 for Astra, plus $10 and $40 per million output tokens respectively. The cost figures are ceilings. The actual count and service availability remain unknown before dispatch. [Sol rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [Astra rates](https://developers.openai.com/api/docs/models/gpt-6.2-astra)

Verify the manifest, source versions, exact request bytes, implementation hashes and unused journal before dispatch. Stop globally on the first failed count, transport or capture failure, HTTP error, timeout, deadline, malformed or duplicate JSON, unexpected model, refusal, truncation, invalid response or claim/citation binding, missing required usage or budget overrun. Record intent before sending. An interruption consumes the journal. Preserve unknown usage and unattempted slots. An eligible semantic miss receives its scores and the schedule continues. Retries, replacements, redirects, polling and fallback calls have zero allowance. [Single-use runner and auditor](../../scripts/planetarium_scope/run.py)

## Local verification

All **126 focused offline tests passed**. The 117 source, rendering, scoring, regression and response-mapping checks include the exact B brief and system message, X as a one-field change, full selected context at both endpoints, gold exclusion, masked grading, separate-axis outcomes, shared recovery, loss of a control and missing delivery. Nine injected-transport checks exercised a complete schedule, the last count failing by budget or HTTP status, sibling-model substitution in both directions, incorrect claim or citation, an output budget breach, and interruption. Every injected run rejected a second dispatch. Repository-wide Ruff lint and formatting and strict mypy passed across 484 Python files. [Sources, scoring and mapping](../../data/diagnostics/planetarium-sol-astra-verification-2026-11-25/sources-and-scoring.xml) · [Mock transport checks](../../data/diagnostics/planetarium-sol-astra-verification-2026-11-25/injected-transport.xml)

An independent disk readback checked the manifest SHA-256, 52 frozen members, 63 implementation hashes and the shared assessment input in every count/generation pair. The registered journal is ready, with **0 of 48 slots attempted** and no output directory. [Verified journal and inventory](../../data/diagnostics/planetarium-sol-astra-verification-2026-11-25/unused-journal.json)
