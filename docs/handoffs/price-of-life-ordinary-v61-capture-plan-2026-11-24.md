# Approval plan for one ordinary v61 critique of *The Price of Life*

**Frozen locally on November 24, 2026. Subsequently approved and dispatched once. The slot is spent.** This capture was designed to learn whether the ordinary critic independently makes a factual position claim about scene two of OH-V01-008. The ending shows Elias walking toward the extraction machine. The saved v33 critic discussed the memory sale. The frozen request contains the ordinary production v61 messages, with no added question about the chair or arrival. [Capture result and input-budget stop](price-of-life-ordinary-v61-capture-results-2026-11-24.md) · [Source-screen decision](q011-independent-position-screen-2026-11-24.md)

## 1. Use the five saved inputs

The v33 critic invocation `ff193b4e-3de7-4f88-bc9c-f113785f903d` provides the original input links. Its critique identifies the scene-two draft as the target. The approved Story Bible names the revised scene-one draft as already accepted. The isolated run `5234a721-a539-45bf-ab2a-c3252ebf3d7b` uses a private copy of the source database. [Frozen source, task and budget manifest](../../data/diagnostics/price-of-life-v61-capture-2026-11-24/plan.json)

| Role in the request | Exact artifact version | Canonical content SHA-256 |
| --- | --- | --- |
| Target draft · *The Price of Life*, v1 | `a35894d5-6d87-400d-b48b-fa84b8069dfd` | `c7e3052cac5ba68e6676254c668d17e690524b820716fa842fa4155345af7878` |
| Scene-two plan, v1 | `aac632e7-27bb-5f71-a503-c97ab1cf0aa2` | `86c40240b7c18d2a1e3c2ecce106b39d37cd1e5789907db593b116c8a7f87ee3` |
| Accepted prior draft · *The Hollow Home*, v2 | `ad787886-83c5-483e-b46e-9a665309d4da` | `4f7ab99c65bb8d4ae7cd02a2f70580509c632af9eee92895f1e23cf4ba055f83` |
| Story Bible after scene one, v2 | `8b2eaec7-c4e4-442b-afec-70f8f7182d4b` | `cbce97bb89480b5cbe3b6878233d4ce6f416c18901141b7f01d102e485baa318` |
| Approved Story Blueprint, v1 | `bada17ea-7429-4f55-8ccf-5cde1f16e3d6` | `9b6deb1d7544dc9e66d70ba7433fc71059ec391d8a0aa3e3907d2b7a846363b2` |

## 2. Send the exact request only after approval

| Item | Frozen value |
| --- | --- |
| Destination | One `POST http://127.0.0.1:11434/api/chat` through the local Ollama daemon to Ollama Cloud |
| Model and role | `gemma4:31b-cloud`, initial `scene_critic` operation, production prompt v61, graph 9 |
| Unpublished story payload | Full target draft in 60 ordered evidence excerpts, full accepted scene-one prose, exact scene-two plan and updated Bible, current-scene view of the Blueprint, ordinary assignment and rubric, and the scene-three turning point and outcome |
| Exact body | 86,804 UTF-8 bytes. System message 10,997 characters and user message 70,690 characters. |
| Sampling | Temperature 0.2, top-p 0.95, seed 19208, thinking off, streaming off |
| Budget | **One generation attempt, zero count calls, zero retries.** 24,000 input tokens, 8,000 output tokens, 32,000-token context. 300-second deadline. Application reservation USD 0.20. |
| Request SHA-256 | `a996098f8b671c7b86f9b9d2543c2809607159ad49e7fd8ffa6043d33b16b9f9` |
| Messages SHA-256 | `0dadf1e059ea936515cfbef229fbd7d6be13949862842f3857f885abd5730aee` |
| **Approval manifest SHA-256** | `71eaf9118ef23fb95c6e4b9357985f362b58b47ce5dc329afcbfb2642b286e16` |

The capture verifies the manifest, source hashes, task, seed, implementation and endpoint. The ledger consumes the slot before the transport can send bytes. A timeout, interruption, provider error, wrong model, incomplete or invalid delivery, or reported budget overrun ends the attempt. A revision verdict also ends the run. No fallback, writer, repair, assessor or graph continuation is budgeted. [Exact request](../../data/diagnostics/price-of-life-v61-capture-2026-11-24/request.json) · [Single-use registration](../../scripts/price_of_life_v61_capture.py)

## 3. Inspect the critic’s own claims

On successful delivery, require one saved critic invocation and one correctly targeted critique, a schema-7 native audit, and compatible export and intake. Inspect all whole explanatory fields. For each factual claim that places a person or object relative to a landmark at an identifiable instant, freeze the original wording and field pointer, source versions, whole-claim judgment gold and an independent passage-specific evidence criterion before viewing any assessor output. Preserve the distinction between moving toward the machine, arriving there and lying back. If the review makes no qualifying claim, record the coverage gap and stop. B remains the default factual brief.

## Local verification

The ordinary production executor rendered the exact request through an injected transport. The 60 catalog entries reproduced the complete target prose after whitespace normalization. The full accepted scene-one prose, scene-two plan and updated Bible matched their saved versions. The Blueprint supplied scene two’s plan and the exact reserved scene-three boundary. Both successful mock paths created one new invocation and one new critique, with all five input links and the expected target. [Request and source inspection](../../data/diagnostics/price-of-life-v61-verification-2026-11-24/inspection.json)

All 12 injected scenarios passed. Two processes starting together produced one mock POST. An interruption immediately after recording intent consumed the slot with zero mock POSTs. An interruption after receipt consumed it with one. Restart added zero in both cases. Wrong approval and changed request bytes stopped before claiming. HTTP 500, timeout, malformed and truncated output, wrong model and over-budget output all stopped after the single attempt. [Injected scenario results](../../data/diagnostics/price-of-life-v61-verification-2026-11-24/probes/verification.json)

All 69 focused registration, restart, evidence and native-export tests passed. The scene-two regression rejects exchanged target and history versions, missing history and the wrong source critic. Repository-wide Ruff lint, formatting and strict mypy passed across 412 Python files. [Focused test results](../../data/diagnostics/price-of-life-v61-verification-2026-11-24/focused.xml)

At freeze, the operator manifest, seed, task and request were byte-identical to the rehearsed bundle. Both older capture ledgers were spent. The read-only command `python -m scripts.price_of_life_v61_capture verify` reports the approval hash and current slot state. Preparation used zero provider calls. Production prompts are unchanged and the full workflow canary remains on hold.
