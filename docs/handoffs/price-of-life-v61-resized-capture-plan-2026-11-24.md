# Fresh Gemma capture for *The Price of Life*

**Approved and executed November 24, 2026.** The single-use slot is spent. The approved plan below froze one isolated ordinary v61 critique with `gemma4:31b-cloud`. The first capture reported 26,025 input tokens and 1,092 output tokens, then stopped at its 24,000-token input limit. The fresh capture allowed **28,000 input tokens**, leaving 1,975 tokens of headroom (7.6%). The 8,000-token output allowance gave a 36,000-token context window. [Fresh capture result and admission decision](price-of-life-v61-resized-capture-results-2026-11-24.md) · [First capture receipt and outcome](price-of-life-ordinary-v61-capture-results-2026-11-24.md) · [Approval manifest](../../data/diagnostics/price-of-life-v61-budget-capture-2026-11-24/plan.json)

## What approval would send

The local daemon would send the frozen unpublished story context to Ollama Cloud in one `POST http://127.0.0.1:11434/api/chat`. The ordinary system and user messages are byte-identical to those from the first capture. The scene-two draft appears in 60 ordered evidence excerpts, with the complete accepted scene-one prose, the scene-two plan, the updated Story Bible, the current-scene Blueprint view, and the ordinary scene-three boundary. The request contains no added question about the extraction chair. [Exact request](../../data/diagnostics/price-of-life-v61-budget-capture-2026-11-24/request.json)

| Input | Exact version |
| --- | --- |
| Target draft · *The Price of Life* v1 | `a35894d5-6d87-400d-b48b-fa84b8069dfd` |
| Scene-two plan v1 | `aac632e7-27bb-5f71-a503-c97ab1cf0aa2` |
| Accepted draft · *The Hollow Home* v2 | `ad787886-83c5-483e-b46e-9a665309d4da` |
| Story Bible after scene one v2 | `8b2eaec7-c4e4-442b-afec-70f8f7182d4b` |
| Approved Story Blueprint v1 | `bada17ea-7429-4f55-8ccf-5cde1f16e3d6` |

| Execution setting | Frozen value |
| --- | --- |
| Generation | **One generation attempt, zero count calls, zero retries or fallbacks** |
| Limits | 28,000 input tokens, 8,000 output tokens, 36,000 context, 300 seconds, USD 0.20 application reservation |
| Sampling | Temperature 0.2, top-p 0.95, seed 19208, thinking off, streaming off |
| Run | `4b7f5aa4-a23b-411b-9bd3-df1b75d1894a`, with a separate database and ledger |
| Request body | 86,804 bytes. Only `options.num_ctx` changed, from 32,000 to 36,000. |
| Request SHA-256 | `cbc5c84f2c535fe4a8a9067ae05f7c8d3ee53cc7117cdd752ce06e228ec5be01` |
| Messages SHA-256 | `0dadf1e059ea936515cfbef229fbd7d6be13949862842f3857f885abd5730aee` |
| **Approval manifest SHA-256** | `03ccd59bda3288f584774d2629b3dad363b970b4666daa9b4dd4445dc0095fc1` |

## Stops and admission

1. Verify the approval, source versions, seed, task, implementation and request hashes. Commit the single dispatch intent before sending. A restart after a claim or dispatch cannot spend another attempt.
2. Stop on timeout, HTTP failure, wrong model, incomplete or malformed output, validation failure, or reported usage above either token limit. Save available usage and the terminal outcome. A revision verdict ends the capture.
3. On success, require one saved scene-two critique with compatible native export and intake. Inspect its whole explanatory fields. If a factual position claim qualifies, freeze its wording, input versions, whole-claim judgment gold and separate passage-specific evidence criterion before viewing assessor output. Otherwise record the gap. B remains the default. The writer, assessor and workflow canary have no calls in this plan.

## Verification

All 14 scenarios used injected transport with provider connections blocked. The ordinary executor emitted the frozen request on disposable copies. The checks used an authored fixture response with the first capture’s reported usage. They verified native export, all five source links and the correct target. [Independent request and budget checks](../../data/diagnostics/price-of-life-v61-budget-verification-2026-11-24/inspection.json) · [Scenario results](../../data/diagnostics/price-of-life-v61-budget-verification-2026-11-24/probes/verification.json)

| Injected input / output tokens | Result |
| --- | --- |
| 26,025 / 1,092 | One validated critique and compatible export |
| 28,000 / 1,092 | One validated critique at the input limit |
| 28,001 / 1,092 | Input-budget stop, zero critique versions |
| 26,025 / 8,001 | Output-budget stop, zero critique versions |

Two concurrent starts produced one mock POST. Restarts after crashes on either side of transport receipt added zero POSTs. The old and new registrations rejected each other’s approval, and the prior slot remained spent. The operator bundle matched the qualified fixture byte for byte. To inspect its status locally, run `python -m scripts.price_of_life_v61_budget_capture verify`. Preparation used zero provider calls. [Read-only verification and capture entry point](../../scripts/price_of_life_v61_budget_capture.py)

All 71 focused registration, restart, evidence and export tests passed. Repository-wide Ruff lint, formatting and strict mypy passed across 414 Python files. [Focused test results](../../data/diagnostics/price-of-life-v61-budget-verification-2026-11-24/focused.xml)
