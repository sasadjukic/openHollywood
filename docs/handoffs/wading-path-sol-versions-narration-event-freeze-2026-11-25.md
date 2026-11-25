# The Wading Path · Sol 6.1 and 6.2 narration/event comparison

**Frozen for approval.** Each model gets the same six one-claim B assessments on high reasoning. The budget is six input counts and up to six generations **per model**, 24 endpoint attempts across the comparison, with zero retries. The approval SHA-256 is `6eaadeb7d5290667d3e63a47eb9974a0d1d9f89ba9f5bda2f5a5d45934a40a93`. [Approval manifest](../../data/diagnostics/wading-path-sol-versions-narration-event-2026-11-25/plan.json) · [Exact request bodies](../../data/diagnostics/wading-path-sol-versions-narration-event-2026-11-25/requests)

## Cases and presentation order

The narration claim asks whether the scene-four draft explicitly recounts Elias and Maya reaching the master breaker panel housing together during that scene. The event claim asks whether both reached it at some time during scene four. All versions preserve the same 4,945-character approach and final stop three strides short. Only the excluded and confirmed histories add a retrospective. The selected versions, exact claims and passage criteria come from the gold frozen before the local rehearsal. [Rehearsal and source versions](wading-path-narration-event-rehearsal-2026-11-25.md) · [Six-case gold](../../data/diagnostics/wading-path-sol-versions-narration-event-2026-11-25/gold.json)

| Order within each stage | Case | History | Claim | Gold | First model |
| --- | --- | --- | --- | --- | --- |
| 1–2 | SN | Measured stop alone | Explicit narration | unsupported | 6.1 |
| 3–4 | XE | Earlier visit excluded | Event during scene | unsupported | 6.2 |
| 5–6 | VN | Earlier visit confirmed | Explicit narration | supported | 6.1 |
| 7–8 | SE | Measured stop alone | Event during scene | uncertain | 6.2 |
| 9–10 | XN | Earlier visit excluded | Explicit narration | unsupported | 6.1 |
| 11–12 | VE | Earlier visit confirmed | Event during scene | supported | 6.2 |

**SE is the primary comparison.** Sol 6.1 previously rejected an earlier visit on this draft. Both models get a fresh attempt. If both pass SE, that is a tie on this run. SN checks whether the same model can reject explicit narration on the same draft while leaving the event uncertain. The four retrospective controls test whether the answer follows the history when the final gap is identical. The earlier S2 endpoint delivery remains an offline control. [Original S1 and S2 results](wading-path-measured-stop-visit-audit-2026-11-25.md)

## Requests, resources and stops

1. Verify the manifest, exact draft and historical source bindings, frozen implementation, request hashes and unused single-use journal.
2. Send all 12 counts serially to `POST https://api.openai.com/v1/responses/input_tokens`. Every count must pass before the first generation. Both endpoints receive the full selected prose, saved review and original story context. Each request selects only A001. The grading key and criteria stay local.
3. Send up to 12 serial generations to `POST https://api.openai.com/v1/responses` in the same paired order. Within each pair, the only wire difference is the top-level model ID. Both use high reasoning, the ordinary B brief, identical schema, standard service tier and `store: false`.
4. Record intent before sending. Stop globally on the first transport failure, non-200, deadline, malformed or incomplete output, wrong model, invalid claim or citation, missing required usage, or budget breach. A consumed or interrupted registration cannot restart. An eligible semantic miss is scored and the schedule continues. Preserve every unattempted slot.

| Resource | Frozen limit |
| --- | --- |
| Generation input / output per attempt | 160,000 / 4,096 tokens, including reasoning in the output limit |
| Generation input / output per model | 960,000 / 24,576 tokens |
| Total generation input / output | 1,920,000 / 49,152 tokens |
| Estimated generation cost | $0.44096 per attempt, $2.64576 per model, **$5.29152 combined** |
| Timeout | 120 seconds per count, 300 seconds per generation, 84 minutes overall |

Both published standard rates are $2 per million input tokens and $10 per million output tokens. The ceiling allows $2.50 per million on every input token for a default 30-minute cache write. It is a conservative generation estimate. The 6.2 specification is scoped to this diagnostic. Account access and provider acceptance will first be exercised by the approved schedule. [Sol 6.1 model](https://developers.openai.com/api/docs/models/gpt-6.1-sol) · [Sol 6.2 model](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [Cache pricing and default lifetime](https://developers.openai.com/api/docs/guides/prompt-caching#cache-lifetime-gpt-5-6-and-later)

## Separate scores and interpretation

**Judgment** earns one point for the exact whole-claim label. **Evidence** earns one point for a reason grounded in the selected version and covering the relevant people, place and time. Grade the evidence with model, returned label and dispatch order hidden. Seal those decisions before joining labels to gold. Citing only the last gap earns zero evidence points on all six cases. A correct label can therefore score 1/0, and a wrong label with adequate evidence can score 0/1. [Case-specific criteria](../../data/diagnostics/wading-path-sol-versions-narration-event-2026-11-25/evidence-criteria.json) · [Scoring rules](../../data/diagnostics/wading-path-sol-versions-narration-event-2026-11-25/scoring.json)

Inspect all 24 fixed slots. For every eligible assessment, report both scores, the reason and cited evidence. Show paired gains, losses and ties on each axis. Report a 6.2 recovery on SE only when 6.1 misses at least one axis and 6.2 passes both. Show SN and each retrospective control separately. Report tokens, elapsed time and estimated generation cost by model. Any missing eligible generation makes the overall comparison inconclusive. One observation per model and claim on one scene family supports a case-level comparison.

## Local verification

All 32 targeted checks passed, including nine injected-transport tests. Repository-wide Ruff lint, formatting and strict mypy passed across 462 Python files.

Verified matching count and generation inputs, byte-level pair parity, exact versions and exclusion of the grading criteria. Injected-transport tests cover the all-count barrier, rejection of either sibling model and missing model identity, invalid responses, interrupted dispatch and refusal to reuse the journal. Scoring fixtures exercise independent judgment and evidence changes and incomplete pairs. The live journal is ready with all 24 slots unattempted. Zero story-bearing endpoint requests were sent. B remains the default and the full workflow canary stays on hold. [Request and scoring checks](../../data/diagnostics/wading-path-sol-versions-verification-2026-11-25/requests-and-scoring.xml) · [Injected transport checks](../../data/diagnostics/wading-path-sol-versions-verification-2026-11-25/injected-transport.xml) · [Unused journal readback](../../data/diagnostics/wading-path-sol-versions-verification-2026-11-25/unused-journal.json)
