# The Wading Path · Three claims about arrival

**Frozen for approval on November 24, 2026.** This diagnostic asks whether Sol on B can distinguish what the ending narrates, what happened at any time in scene four, and where Elias and Maya are when the scene cuts. The retreat draft makes the distinction observable. Both people arrive and then leave. The original places the housing at the end of the passage and leaves the pair’s final position open. [Local rehearsal and source passages](wading-path-three-claims-rehearsal-2026-11-24.md)

## Claims and dispatch order

Each request uses `gpt-6.1-sol` with high reasoning and one active claim. The six authored cases use the same B brief. Each row below has a reserved count and generation slot. All seven counts must succeed before the first generation. The last column is operator-only gold.

| Count | Generation | Case | Selected draft | Claim | Gold |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 8 | N1-B | Original | Ending explicitly narrates arrival | Unsupported |
| 2 | 9 | R2-B | Retreat | Both reach the housing at some time during the scene | Supported |
| 3 | 10 | P1-B | Original | Both are at the housing at the final narrated instant | Uncertain |
| 4 | 11 | Q008-B | Original | Saved critic’s whole field about the assigned outcome, plenum entry and narrated arrival | Unsupported |
| 5 | 12 | N2-B | Retreat | Ending explicitly narrates arrival | Supported |
| 6 | 13 | R1-B | Original | Both reach the housing at some time during the scene | Uncertain |
| 7 | 14 | P2-B | Retreat | Both are at the housing at the final narrated instant | Unsupported |

The original is draft v1, `38e82829-604f-40df-b5a0-1c968718573e`. The retreat is the diagnostic draft `ae1fb3f6-5e23-597a-a61f-020b9cc8e254`. It preserves the original’s full 4,804 characters, adds the pair’s explicit arrival, then puts them three strides back and keeps them there. In both versions, `E1420` resolves to the complete selected draft. All three claims on a given draft share its exact prose, historical critic messages, whole review, prior story context, and evidence registry. Each authored claim occupies its own field. The other two claims and the operator’s scoring materials stay outside that request. [Exact claims and draft hashes](../../tests/fixtures/wading_path_three_claims_gold.json) · [Frozen request bodies](../../data/diagnostics/wading-path-three-claims-sol-high-2026-11-24/requests)

Q008 is the original ordinary critic field. Its count and generation bodies each reproduce the previously used body byte for byte. Its assessment requires both the scene-four plan outcome (`E0258`) and the reviewed draft (`E1420`). Its historical score was 1 for judgment and 1 for evidence. Any new delivery receives a fresh score. [Q008 regression](wading-path-three-claims-rehearsal-2026-11-24.md) · [Manifest and exact source versions](../../data/diagnostics/wading-path-three-claims-sol-high-2026-11-24/plan.json)

## Judgment and evidence

**Judgment earns one point** for an exact match to the frozen whole-claim label. **Evidence earns one independent point** for a cited, version-bound explanation meeting the case criterion. The reader inspects the citations and reason with returned labels and dispatch order hidden, records the passages and basis, then seals the evidence decisions before joining the labels. Equivalent precise passages qualify. Only a complete, eligible delivery in a closed observed journal can score. Each other generation is recorded as unscored on both axes. [Evidence criteria without returned labels or gold](../../data/diagnostics/wading-path-three-claims-sol-high-2026-11-24/evidence-criteria.json) · [Scoring rules](../../data/diagnostics/wading-path-three-claims-sol-high-2026-11-24/scoring.json)

On the original, an adequate narration judgment must account for the move to the wall, entry into the plenum, the look deeper and the final description of the housing. For the other two claims, the reason must explain what those passages leave open about an earlier visit or the pair’s position at the cut. On the retreat draft, the arrival establishes both narration and a visit. Final position depends on the subsequent departure and persistent gap. For Q008, also identify the assigned outcome and account for the asserted entry and arrival in the published field. [Frozen gold and case-specific obligations](../../data/diagnostics/wading-path-three-claims-sol-high-2026-11-24/gold.json)

Report three pairs of scores for the original, three for the retreat and Q008 separately. Any missing eligible result makes the overall diagnostic inconclusive. A miss on either Q008 score holds the control. With a passing control, an authored miss identifies the claim scope and scoring axis to investigate. Seven joint passes establish discrimination on these two drafts. The pair contains neither a scene that rules out every earlier visit nor a final instant where both remain at the housing. Transfer and story quality require different evidence.

## Budget and stops

Approval would authorize full unpublished prose and context at both OpenAI endpoints. The seven serial counts use `POST https://api.openai.com/v1/responses/input_tokens`. Up to seven serial generations use `POST https://api.openai.com/v1/responses`, with `store=false`. The count and generation for each case use the same input, model, reasoning and response schema. No retries, replacements or fallback.

| Resource | Frozen limit |
| --- | --- |
| Per generation | 160,000 input tokens and 4,096 output tokens including reasoning |
| Aggregate generation | 1,120,000 input and 28,672 output tokens |
| Generation cost under the frozen repository catalog | $0.44096 per request and $3.08672 total |
| Time | 120 seconds per count, 300 seconds per generation, 49 minutes overall |

Every count must return HTTP 200 and a positive count within budget. The first technical failure stops the run. Stops include transport errors, timeouts, non-200 responses, malformed or duplicate-key JSON, model mismatch, refusal, truncation, an invalid claim or citation, missing required usage and budget overruns. A valid response with a semantic miss stays in the comparison and the schedule continues. The single-use journal commits intent before send. An interruption consumes the registration and leaves unknown usage and untouched slots visible. [Runner](../../scripts/wading_path_three_claims/run.py)

## Verification and approval

The approval SHA-256 is `91285c0d71c0e48e92ba22abf6d83e93b97b2bfc21be015e64cb7b739c45c137`. Independent readback rebuilt the 14 request bodies, checked 18 frozen members and 41 implementation files, and found the journal ready with all 14 slots unattempted. The read-only check is `python -m scripts.wading_path_three_claims.run verify --approved-plan-sha256 91285c0d71c0e48e92ba22abf6d83e93b97b2bfc21be015e64cb7b739c45c137`. [Registered readback](../../data/diagnostics/wading-path-three-claims-freeze-verification-2026-11-24/registered-readback.json)

All 48 focused tests passed. The tests exercised independent judgment and evidence failures, missing results, a control miss, an over-budget seventh count, a wrong claim, an invalid citation and an interrupted dispatch followed by a rejected restart. Requests were exercised through injected transport only. Repository-wide Ruff lint, formatting and strict mypy passed across 442 Python files. B remains the default, production prompts are unchanged, and the full workflow canary remains on hold. Live execution awaits approval. [Claim and scoring tests](../../data/diagnostics/wading-path-three-claims-freeze-verification-2026-11-24/claims-and-scoring.xml) · [Injected transport tests](../../data/diagnostics/wading-path-three-claims-freeze-verification-2026-11-24/injected-transport.xml)
