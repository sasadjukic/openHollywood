# Fresh-family B/C repeat for uncertain scene endings

**Approval requested for 16 input counts and up to 16 generations.** Each of eight fresh cases has one B request and one C request. Each case in each arm gets one count and at most one generation, with zero retries. Both OpenAI endpoints receive the full admitted packet and brief. The model is `gpt-6.1-sol` with high reasoning. The issued journal is ready with all 32 slots unused. [Approval manifest](../../data/diagnostics/q010-fresh-repeat-2026-11-23/plan.json) · [All exact requests](../../data/diagnostics/q010-fresh-repeat-2026-11-23/requests/)

The earlier clarification recovered one known case involving motion toward a threshold. Both arms already passed the open moth scene. This repeat asks whether the clarification helps on a **fresh destination claim** and whether it transfers to a **fresh identity claim**. Report those outcomes separately. These are authored factual controls with one observation per arm per case. [Preceding results](q010-paired-uncertainty-results-2026-11-23.md)

## Cases, gold and order

In *The Vermilion Pouch*, the two-part claim says Lale has stamped the routing slip and the pouch is in the receiving pan when the closing bell rings. In *The Nicked Composing Stick*, the claim says Orsa has broken the blue seal and Neri holds the nicked stick when the skylight shutters meet. An earlier witness establishes the first clause even when the scene draft is unavailable.

| Evidence state and whole-claim gold | The Vermilion Pouch | The Nicked Composing Stick |
| --- | --- | --- |
| Confirmed · `supported` | **R01, B then C.** At the bell the pouch is visible in the pan. | **R07, C then B.** At shutter closure Neri is holding the stick in the clear doorway. |
| Contradicted · `unsupported` | **R08, B then C.** The pouch is caught upstream above the empty pan at the bell. | **R04, C then B.** Sabin alone holds the stick. Neri shows both empty hands. |
| Unresolved in a complete draft · `uncertain` | **R06, C then B.** The pouch moves toward the pan and disappears behind a hood. At the bell Lale sees only her reflection. Arrival and a delay behind the hood are both possible. | **R02, B then C.** A chip in the partition reveals the nick and four fingertips. Either setter could be holding the stick. |
| Missing draft · `uncertain` | **R03, C then B.** The witness saw the stamping and left. The source inventory records the absent draft. | **R05, B then C.** The witness saw the seal broken and went downstairs. The inventory records the absent draft. |

Run R01 through R08 in numeric order, using the indicated arm order. Repeat the same sequence for generation only after all counts pass. B and C each run first four times, twice per family and once per evidence state. Within each family the claim, question, observation time, earlier witness and authority are fixed. The three supplied drafts share their entire opening and differ only in the last paragraph. The missing cases supply the earlier witness and inventory only. [Source packets](../../data/diagnostics/q010-fresh-controls-2026-11-23/frozen/packets/) · [Gold with exact witnesses and alternative readings](../../data/diagnostics/q010-fresh-controls-2026-11-23/frozen/gold.json)

## Single intervention

B uses the prior diagnostic system message. Its uncertainty definition reads “Uncertain means material evidence is unavailable and no supplied evidence decisively contradicts the claim.” C inserts the same sentence as in the preceding comparison:

> Material evidence can be unavailable even when the relevant source is complete but leaves the material fact undetermined.

For every case at each endpoint, that insertion is the entire byte-level difference. Both arms see the same source versions, whole claim, authored brief, evidence references, schema, model settings and limits. Gold, witness spans, case-state labels, scoring rules and previous answers are scorer-only. [R06 baseline generation](../../data/diagnostics/q010-fresh-repeat-2026-11-23/requests/R06-B-generation.json) · [R06 clarified generation](../../data/diagnostics/q010-fresh-repeat-2026-11-23/requests/R06-C-generation.json)

## Independent scoring

1. **Evidence adequacy.** Read the registered citations and verbatim reason against the sealed witnesses. The worksheet uses opaque IDs and withholds the arm, dispatch order and returned label field. A reason can disclose the model’s conclusion. Record pass or fail with a passage-specific basis for every eligible ID and seal those decisions before joining labels.
2. **Whole-claim correctness.** Compare the actual returned label to gold. Each response receives both scores. Joint success requires both passes. Unattempted, invalid or incomplete generations remain unscored. Preserve their dispositions and any known usage.
3. **Coverage.** For complete drafts, credit the first clause from S01 or a located S02 passage. The endpoint requires a precise S02 locator and an accurate interpretation at the specified instant. For an open ending, explain what was observed and what remains undetermined. For a missing draft, cite S01 and S03 and explain why the earlier witness cannot resolve the endpoint. Accurate paraphrases qualify. A bare draft reference, wrong attribution, wrong availability explanation or material overread fails evidence.

The scorer binds decisions to the exact approval, worksheet digest, response IDs and cases. Sealing uses exclusive creation. The score command requires that sealed file. A correct label can pass alongside an inadequate explanation, and a wrong label can fail alongside adequate evidence. [Frozen scoring rules](../../data/diagnostics/q010-fresh-controls-2026-11-23/frozen/scoring.json) · [Scoring commands and decision logic](../../scripts/fresh_endpoint_repeat/scoring.py)

**Decision rule.** A fresh recovery requires a joint miss in B and a joint pass in C on an open case, regardless of which arm ran first. A retained baseline pass is a tie. A transfer signal requires 16 eligible generations, joint passes in C on both open cases, at least one fresh recovery, and joint passes on all six C controls with zero control-axis losses. Report R06 separately. An R02-only recovery supports the identity contrast while leaving the earlier movement recovery unreplicated. A C miss or control loss holds the change. If both arms pass both open cases, record the absence of recovery headroom. An incomplete comparison is inconclusive. A signal supports a bounded check on ordinary-review claims. Story-quality effects remain outside this test.

## Budget and stops

| Resource | Frozen limit |
| --- | --- |
| Effective destinations | 16 POSTs to `https://api.openai.com/v1/responses/input_tokens`, then at most 16 POSTs to `https://api.openai.com/v1/responses` |
| Attempts | 32 total, serial, zero retries, polling, replacements or fallback |
| Tokens | 8,192 input and 4,096 output including reasoning per generation. Aggregate generation ceilings are 131,072 input and 65,536 output tokens. |
| Estimated generation cost | $0.06144 per generation and $0.98304 total using the frozen repository rates and uncached input. Actual billing is unknown. |
| Time | 120 seconds per count, 300 per generation, 1,800 seconds for serial dispatch |

Verify the source seal, implementation, exact bodies, approval digest and unused journal before dispatch. Every count must return HTTP 200 and a positive admitted count within the frozen limits. Stop globally on the first failed count or technical failure, including non-200, timeout, cancellation, refusal, truncation, malformed or duplicate-key output, model mismatch, invalid claim or citation, missing required usage or exceeded budget. An interruption after intent consumes the single-use journal. A valid semantic error is scored and the schedule continues. Report all fixed slots. [Single-use runner](../../scripts/fresh_endpoint_repeat/run.py)

## Freeze record

Gold and the scorer-only rules were sealed together at **08:23:44 UTC on November 23, 2026**, before previews, mock responses or issuance of the request manifest. All 22 witness spans resolve to the designated versions and fields. The two titles, claims, story text and source version identifiers differ from the preceding study. Arm comparisons at both endpoints reproduced the single insertion across all eight pairs. All 32 bodies matched their hashes and complete source-to-citation bindings. The prior B/C journal still verifies as closed and spent. [Source and scoring seal](../../data/diagnostics/q010-fresh-controls-2026-11-23/frozen/seal.json) · [Local source readback](../../data/diagnostics/q010-fresh-controls-2026-11-23/readback.json)

| Record | SHA-256 |
| --- | --- |
| Approval manifest | `983b8beb98385a8034c8429c92ae2b7bfc5f47bc18079fc6a1568df892284414` |
| Source and scoring seal | `3d8fbde2a94e340d2c46a938b53d27b3d3ca06e44f110f577e99a44b23c9d3bc` |
| Gold | `b43db608a0d7ff65b89bb9fa7957eee085d563cf6d0d6fe9279f97888263a145` |
| Scoring rules | `07c768bbd9448c2fd323c2f3ce25670aa35ff5037bc02e3cffbf0a02420cbfa0` |

All **229 focused tests passed**, including the original and fresh registrations. Injected transports exercised the full 16-count gate and 16-generation schedule. An excessive final count prevented all generation; cancellation at the first generation preserved the intent and blocked restart. Invalid citations, missing usage, duplicate keys, model drift and damaged receipts triggered the expected stops. Scoring checks covered mismatched worksheet IDs, control losses, incomplete pairs, ties and recovery on the identity case alone. Repository-wide Ruff lint, formatting and strict mypy passed across 372 Python files. Nine existing Pydantic serialization warnings came from work-brief tests. [Local test results](../../data/diagnostics/q010-fresh-controls-2026-11-23/regressions.xml)

The offline CLI is `python -m scripts.fresh_endpoint_repeat.run verify --approved-plan-sha256 983b8beb98385a8034c8429c92ae2b7bfc5f47bc18079fc6a1568df892284414`. Its `audit` command lists all 32 fixed slots. Live dispatch awaits separate approval. Production prompts retain their current text and the full workflow canary remains on hold.
