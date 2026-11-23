# Q011 Sol-high comparison of approach and arrival

**Ready for live approval.** Both cases use baseline B and `gpt-6.1-sol` at high reasoning. The single-use journal has four unused slots. Approval would authorize the full assessment packet at both OpenAI endpoints, with two input counts before at most two generations and zero retries. [Approval manifest](../../data/diagnostics/q011-arrival-comparison-2026-11-23/plan.json) · [Exact request bodies](../../data/diagnostics/q011-arrival-comparison-2026-11-23/requests/)

## What changes

Gemma wrote the following claim for critique v2 of *The Pristine Lure*.

> The achieved state matches the outcome ('drawn to the entrance') and exit state ('stands at the threshold') defined in the scene plan.

| Case and dispatch ID | Final draft evidence | Frozen whole-claim gold |
| --- | --- | --- |
| Original · `A-B` | The last sentence shows Elias stepping past the shoes and moving toward the threshold, drawn by its promise. His position at the cut remains open. | `uncertain` |
| Authored arrival · `B-B` | The complete original prose is followed in the same paragraph by one sentence, **“Elias stood at the threshold.”** Attraction and standing are both depicted. | `supported` |

The genuine draft is `b74efc96-dbe6-4147-8dd3-a1c24f295321`. The authored diagnostic draft has its own version, `4111438c-aff2-5041-8703-e1cbf6ce303b`. The arrival sentence occupies code points 3285 through 3313 in the authored draft. Both packets preserve the original association between critique v2 and the genuine draft. The authored version exists only for this comparison. [Prospective gold and source spans](../../data/diagnostics/q011-arrival-comparison-2026-11-23/gold.json) · [Original audit](q011-motion-endpoint-audit-2026-11-23.md)

Both cases use the rehearsed question, “How does the depicted ending compare with the outcome and exit state named in the claim?” Both carry the same complete Scene Plan v1, blueprint, story bible, normalized historical critique, native critic audit, claim, brief, B system message, response schema and model settings. Each packet contains its own complete assessed draft and a copy of its exact final paragraph. Only the current draft text, ending excerpt, version and dependent hashes vary across requests. Each case has the same messages and schema for count and generation. [Local rehearsal](q011-endpoint-rehearsal-2026-11-23.md)

The comparison uses four citation choices in both cases. `E0233` locates the assigned outcome, `E0229` the assigned exit state, `E0883` the complete assessed prose and `D01` its last paragraph. The historical critic’s own statements remain attributed to that critic. The scorer gold, labels for each case and adjudication rules stay outside both model-facing packets. This focused citation list makes comparison with the earlier 883-reference rehearsal indirect.

## Separate scores

1. **Evidence.** Inspect the registered citations and reason against the case’s frozen source witnesses. The evidence worksheet suppresses the returned label. Record and seal the evidence decision before joining it to the judgment. Require both plan obligations, the depicted attraction and a precise location for the decisive endpoint evidence. A precisely located full-draft citation is acceptable. For the original, the explanation must leave arrival and a stop short open. For the authored case, it must locate the final observation of standing. Merely citing the plan, naming a relevant document or returning the right label earns no evidence credit on its own.
2. **Judgment.** Compare the returned Q011 label directly with its frozen whole-claim gold. Report both scores for each eligible case. An eligible case requires a closed observed journal, a complete response within budget and a valid binding to Q011, its request and citation registry. A missing or ineligible case has two unscored axes. An incomplete pair is inconclusive.
3. **Interpretation.** Both cases must pass both scores to register sensitivity to the added destination fact on this passage. One observation per ending leaves repeatability and story quality unmeasured. [Scoring rules](../../data/diagnostics/q011-arrival-comparison-2026-11-23/scoring.json) · [Scoring implementation](../../scripts/q011_arrival/scoring.py)

## Dispatch and stops

| Slot | Stage | Case | Body bytes |
| --- | --- | --- | ---: |
| 1 | `POST /v1/responses/input_tokens` | Original | 39,138 |
| 2 | `POST /v1/responses/input_tokens` | Authored arrival | 39,198 |
| 3 | `POST /v1/responses` | Original | 39,284 |
| 4 | `POST /v1/responses` | Authored arrival | 39,344 |

Both endpoints are on `api.openai.com`. Each count must return HTTP 200 and a positive count within 16,384 tokens before generation starts. Each generation is capped at 16,384 input tokens and 4,096 output tokens including reasoning. The two-generation ceiling is 32,768 input and 8,192 output tokens. The frozen repository rates imply an uncached generation ceiling of **$0.08192 each, $0.16384 total**. Actual usage and billing require live evidence. Count timeout is 120 seconds, generation timeout is 300 seconds, and the serial run has an 840-second wall limit.

Verify the approved digest, source versions, all four bodies, scorer files, implementation pins and journal state before dispatch. Stop on the first technical failure, including HTTP errors, invalid counts, timeout, cancellation, model mismatch, refusal, truncation, malformed or duplicate JSON, invalid claim or citation, missing required input/output usage or exceeded limits. Record each intent before sending. An interrupted run consumes the journal and preserves unknown usage. A valid semantic miss is scored and the next scheduled slot proceeds. No retries, replacements, redirects or fallback are authorized. [Single-use runner](../../scripts/q011_arrival/run.py)

## Freeze record

| Record | SHA-256 |
| --- | --- |
| Approval manifest | `91a2d35d1519f0f42b72b7f6197c86cd60fb6c9e1f8fd2db6967e3941d5dde2c` |
| Gold | `a9b193697692cbed880ea35adce35556e8471915d32dd7570ad95a6eb2312182` |
| Independent scoring rules | `31382f3e4571d828d7c8496aad8ea867c58f81741f7fb151a8f9876220d66584` |

All **122 focused tests passed**, including 15 for this comparison. Disposable journals exercised count rejection before generation, malformed counts, HTTP errors at either generation, timeout, cancellation after intent, restart refusal, invalid claims and citations, length termination, missing usage and model drift. The scorer distinguished a grounded pair, a correct label supported only by a plan citation, and an incomplete pair. The fixtures exposed a model-mismatch reporting issue during preparation. The frozen runner preserves that specific stop reason. Repository-wide Ruff lint, formatting and strict mypy passed across 378 Python files. Independent readback matched every request body and gold witness to the issued manifest. All four live slots remain unused. [Test results](../../data/diagnostics/q011-arrival-verification-2026-11-23/verified.xml) · [Issued-file readback](../../data/diagnostics/q011-arrival-verification-2026-11-23/readback.json)

The offline audit can be replayed from the repository root with the repository Python.

```powershell
.\.venv\Scripts\python.exe -m scripts.q011_arrival.run audit --approved-plan-sha256 91a2d35d1519f0f42b72b7f6197c86cd60fb6c9e1f8fd2db6967e3941d5dde2c
```
