# The Wading Path · one ordinary v61 Gemma capture

**Approved and executed once on November 24, 2026.** The operator slot is spent. The approved run sent the frozen story context to Ollama Cloud through the local daemon for one generation with `gemma4:31b-cloud`. The sections below preserve the plan as frozen. [Capture result and frozen gold](wading-path-ordinary-v61-capture-results-2026-11-24.md) · [Approval manifest](../../data/diagnostics/wading-path-v61-capture-2026-11-24/plan.json) · [Exact request](../../data/diagnostics/wading-path-v61-capture-2026-11-24/request.json)

## 1. Select the scene

*The Wading Path* is scene four of OH-V01-010, a family outside the three previously screened ordinary v61 reviews. The question for the later local screen is **where the draft places Elias and Maya relative to the master breaker-panel housing at the cut**. The plan says “They reach the breaker panel housing” and “They are standing before the final barrier.” The closing paragraphs describe the pair reaching the eastern wall, entering the service plenum and looking deeper into it. The final paragraph locates the housing at the end of the passage. These passages let a reviewer distinguish the characters’ position, the object’s position and what the plan calls for. [Earlier family inventory](price-of-life-approach-controls-and-v61-screen-2026-11-24.md)

I also considered *Unwelcome Guests* (004), whose ending keeps three people in the cellar, and *The Shared Void* (005), which distinguishes leaving the viewing room from leaving the morgue. I selected *The Wading Path* because its plan names both reaching the housing and standing before the barrier, and its draft gives separate spatial details for the people and the equipment. Selection used the drafts and plans. The question above is for the operator. Gemma receives the ordinary v61 critic prompt and the ordinary scene assignment.

## 2. Use the seven exact source versions

The original scene-four critic invocation `7e0eb43f-d9ee-4a0c-b224-189dbe6ae449` supplies all seven input links. Its target was the initial scene-four writer draft. The scene-four Story Bible identifies the three accepted drafts in this order. The new isolated run is `661be23f-9180-445d-9970-465309adacac`. All seven content hashes are frozen in the manifest. [Source and request verification](../../data/diagnostics/wading-path-v61-verification-2026-11-24/inspection.json)

| Input | Version | Exact artifact version |
| --- | --- | --- |
| Target draft · *The Wading Path* | v1 | `38e82829-604f-40df-b5a0-1c968718573e` |
| Scene-four plan | v1 | `152e58e1-57ee-5c48-8bb2-bf4f7e8e104e` |
| Accepted scene one · *The Gilded Cage* | v1 | `e5502349-d94f-44c8-a4f4-68b35eed8bdf` |
| Accepted scene two · *Logic’s Failure* | v2 | `3e00c55f-397f-4476-9156-20aafeb89b72` |
| Accepted scene three · *The Structural Flaw* | v1 | `62bc472b-3eda-4f58-b285-6179a8cb6eca` |
| Story Bible after scene three | v4 | `a5f49af4-90c9-4cc2-8f1b-44f4a6c3b843` |
| Approved Story Blueprint | v1 | `5a8e06cf-9d6f-4c9c-9e61-a075269290c0` |

The ordinary renderer carries the complete current draft in 69 ordered evidence excerpts, the full three earlier drafts, scene-four plan, updated Bible, current-scene Blueprint view, rubric, and scene five’s reserved turning point and outcome. The system message matches the previous ordinary v61 capture byte for byte. The three Price of Life approach controls stay local.

## 3. Spend one slot only after approval

| Setting | Frozen value |
| --- | --- |
| Transport | One `POST http://127.0.0.1:11434/api/chat` through the local Ollama daemon to Ollama Cloud |
| Role and model | Initial scene critic, production prompt 61, graph 9, `gemma4:31b-cloud` |
| Call ceiling | **One generation attempt, zero count calls, zero retries or fallbacks** |
| Resource ceilings | 40,000 input tokens, 8,000 output tokens, 48,000-token context, 300 seconds, USD 0.20 application reservation |
| Sampling | Temperature 0.2, top-p 0.95, seed 19410, thinking and streaming off |
| Request size and SHA-256 | 112,471 bytes · `e7694a69180226289e6215d7fdefd7d01d3da10b825777edec5d4642225418d1` |
| Messages SHA-256 | `a61b35dcd4a3ad0cb5119bfbe6cc4053568185390a10c8e573b70b0120f62e2a` |
| **Approval manifest SHA-256** | `c4126ff5134dcd505164ff75ab21d4073ec87b2eb2dd267b74df4bc5f75da3c2` |

The latest ordinary Gemma capture used 26,025 input tokens for an 86,804-byte request. Scaling that observed ratio to this request gives approximately 33,720 input tokens. The 40,000-token allowance leaves about 6,280 tokens above that estimate. Actual usage is available only after dispatch. [Previous usage receipt](../../data/diagnostics/price-of-life-v61-budget-capture-2026-11-24/output/terminal.json)

The harness verifies source, task, request, implementation and approval hashes, then records the dispatch intent before sending. A consumed slot stays spent through restart. Stop on interruption, timeout, HTTP error, identity mismatch, incomplete or invalid output, budget overrun or incompatible saved-review export or intake. A revision verdict also ends the capture. The writer, assessor, repair loop and workflow canary have zero allocated calls. [Single-use registration](../../scripts/wading_path_v61_capture.py)

## 4. Inspect what Gemma actually claims

After an eligible delivery, check the saved critique, schema-7 native audit, target and plan binding. Inspect every whole explanatory field. Admit a field only if judging its factual wording requires locating a person or object relative to a landmark at an identifiable story instant. For each qualifying field, freeze the verbatim whole field and pointer, exact source versions, whole-claim judgment gold and a separate passage-specific evidence criterion before viewing any assessor output. Use the draft for depicted positions and the plan for obligations. Keep a claim about locating the panel distinct from a claim that the characters reached it. A material position may remain unresolved.

If no field qualifies, record the coverage gap and stop. B remains the default factual brief. This is a purposively selected scene and one critic generation. Its result can supply an independent example but cannot establish how frequently position claims occur or measure story quality.

## Local verification

The production executor generated the frozen request through injected transport. Independent inspection verified all seven input links, all 69 excerpts against the complete draft, the full accepted history in order, and the exact boundary with scene five. Successful mock deliveries produced one schema-validated critique with compatible export and intake. The 14 scenarios covered concurrent starts, crashes before and after mock receipt, input and output budget stops, wrong approval, altered request bytes, and provider or delivery failures. At 40,000 reported input tokens the mock capture succeeded. At 40,001 it stopped. Two concurrent starts produced one mock POST. Restart after either crash added zero. [Injected scenario receipts](../../data/diagnostics/wading-path-v61-verification-2026-11-24/probes/verification.json)

At freeze, the operator bundle matched the verified fixture byte for byte for the manifest, seed database, task and request. Its separate journal reported `ready` via `python -m scripts.wading_path_v61_capture verify`. All 38 focused tests passed, including exchanged history and target versions, missing history and wrong source invocation. Repository-wide Ruff lint, formatting and strict mypy passed across 417 Python files. [Version-binding regressions](../../tests/api/test_wading_path_v61_capture.py) · [Focused test results](../../data/diagnostics/wading-path-v61-verification-2026-11-24/focused.xml)
