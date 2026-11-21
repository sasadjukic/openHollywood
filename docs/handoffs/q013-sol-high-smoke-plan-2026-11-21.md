# Q013 one-claim Sol-high smoke approval plan

**Executed November 21, 2026. Both slots are spent.** [Results and independent scores](q013-sol-high-smoke-results-2026-11-21.md)

**Frozen for approval, November 21, 2026.** This smoke asks whether `gpt-6.1-sol`, at high reasoning effort, can assess one factual explanation in Gemma’s v61 critique of *The Impossible Card* and cite the draft passages that establish it. Only critique v3 is selected. The budget is one input count followed by at most one generation, with zero retries. [Source qualification](assessment-saved-review-q013-qualification-2026-11-21.md)

**Approval SHA-256** `ca0314f557dc4a8b4e23085cc974dfd4d7c51abbc30c510d6f1e6f9149342ee3`

## Case and exact requests

The whole 185-character claim is reproduced from critique v3.

> The draft explicitly establishes that Elara notices the date on the card is October 14th, 2034, while today is October 14th, 2024, concluding that it is exactly ten years in the future.

The selected critique version is `ca5915a5-5b82-4bad-82ce-e5c31a519dc0`. The reviewed draft is v1, `c3689bce-e108-4761-bafe-390f6e7ea1b3`. The request manifest is `59ad7cd95b4d22e3541e3d7f190d30c37ea8132b02e4e6c76a7d5dec5fce170f`.

Approval would send **full unpublished prose and story context to OpenAI at both endpoints**, including the original critic messages, the draft, critique, work brief and evidence registry. The two endpoints receive identical assessment input and strict schema. All 17 review-field dispositions are visible. Q013 alone is active. The frozen bytes match the local qualification, which resolved all 920 evidence locations. The independent gold and scoring instructions are held outside both bodies.

| Order | Destination | Request bytes | Body SHA-256 |
| --- | --- | ---: | --- |
| 1. Count input | `POST https://api.openai.com/v1/responses/input_tokens` | 281,286 | `a7ed9399c181e48833013be88ac02e1880ef50e47aede640c1b5b645119541a6` |
| 2. Assess after an admitted count | `POST https://api.openai.com/v1/responses` | 281,433 | `527d4d168af04fb7d7ec1d21d0f3ee66221fdc168ba0d829bdc25e41cb6b7778` |

## Budget and stops

1. Verify the approval digest, source registration, exact versions, gold digest, implementation and request bytes. Claim the pre-issued SQLite row once. The runner durably records each intent and rechecks the source and journal before the POST.
2. Admit generation only on a valid HTTP 200 count greater than zero and at most **96,000 input tokens** that fits both the model context and the cost limit. Generation allows **32,000 output tokens**, including reasoning. The frozen local rate card reserves at most **$0.56** at those token limits under the **$0.60 ceiling**. Actual usage, latency and billing have not been measured.
3. The time limits are 120 seconds for the count, 600 seconds for generation and 900 seconds for the dispatch sequence. Generation uses strict structured output, disabled truncation and `store: false`. The client uses verified TLS, zero transport retries and no redirects.
4. Stop on drift, cancellation, timeout, transport or HTTP failure, refusal, length limit, wrong model, malformed response, unknown citation, or missing or extra claim. Missing input/output totals or usage above the limits holds the result out of scoring. An interruption spends the run, including one between the count and generation. No resume, replacement, or model fallback is authorized.

## Two independent scores

Score only an observed, closed, version-bound Q013 delivery with eligible usage. Record the returned label, rationale, exact cited locations and dispositions of both slots. If the delivery is ineligible, record both scores as **unscored** and retain the stop reason and known usage. The existing independent gold SHA-256 is `0e9747397ead04c270566f6e27173a859a5eb50338ab235ced2758d3dc9b40d0`. [Gold freeze](second-family-ordinary-v61-capture-results-2026-11-21.md)

| Score | Pass condition |
| --- | --- |
| Claim correctness | Sol returns `supported` for the complete turning-point claim. Either other valid label fails this score. |
| Evidence coverage | The cited draft passages establish the 2034 date belongs to the card, the 2024 date is the scene’s present, Elara attends to the numbers, and the text establishes the ten-year interval. Record a location for each obligation. Missing coverage or material misattribution fails this score. |

The frozen draft witnesses are `E0282`, `E0284`, `E0286`, `E0288` and `E0290`. Equivalent version-bound passages qualify. A complete-draft citation (`E0920`) qualifies when the explanation locates the relevant passage precisely. The plan (`E0237`) describes the intended turning point and cannot establish what the draft depicts on its own. A correct label with inadequate citations receives a claim pass and an evidence fail. Evidence is also scored when a valid label is wrong. Full credit requires both passes. Editorial quality and edit necessity are outside this smoke.

## Single-use journal verification

All **21 full-case rehearsals** used the frozen Q013 request bytes in disposable journals. Eighteen checked successful delivery, stops, send boundaries and races. Three more interrupted a process immediately after a durable journal write. Fresh-process relaunches sent **zero additional requests** in all 21. The actual approval ledger stayed `ready`, both slots were undispatched and the live output directory was absent.

| Injected interruption or race | Count POSTs received by mock | Generation POSTs received by mock | Restart POSTs |
| --- | ---: | ---: | ---: |
| Exit after claiming the run and writing its header | 0 | 0 | 0 |
| Exit immediately before / after the count POST | 0 / 1 | 0 | 0 |
| Exit after recording the admitted count and before generation intent | 1 | 0 | 0 |
| Exit immediately before / after the generation POST | 1 | 0 / 1 | 0 |
| Exit after recording the generation response and before closure | 1 | 1 | 0 |
| Two processes launch the same journal concurrently | 1 total | 1 total | 0 |

The last unclosed generation had a terminal record and remained unscored. Open intents with missing terminals retained unknown usage. A 96,000-token count admitted generation. A 96,001-token count, HTTP 500 and redirect each stopped after the count. Generation rehearsals covered timeout, refusal, truncation, wrong model, malformed output, omitted Q013, unknown citation and missing or excessive usage.

A separate disposable copy exercised the live entry point with a synthetic credential and mock transport. Missing consent, a wrong approval digest, changed request bytes and changed gold were each rejected before credential access. One valid launch reached both mock endpoints. Reissue and restart were refused. No rehearsal contacted OpenAI. The local evidence is under `data/diagnostics/q013-sol-smoke-verification-2026-11-21/` in `qualified/verification.json`, `interruption-gaps/verification.json`, `observed-entry-fixture/qualification-only.json` and `wire-and-scoring.json`.

All 2,651 distinct Python tests passed, including the seven portable journal regressions for each of Q008 and Q013. Ruff lint, formatting and strict mypy passed across 349 Python files. [Journal regression tests](../../tests/api/test_q008_sol_smoke.py)

## Journal and operator access

The private bundle is `data/diagnostics/q013-sol-high-smoke-2026-11-21/`. It contains the hashed `plan.json`, exact requests, request manifest, source receipt and the single-use `dispatch.sqlite3`. Only the fixed live path may produce an observed Q013 delivery. The runner’s `verify` and `audit` commands are read-only. [Runner](../../scripts/q013_sol_smoke.py)

```powershell
uv run --extra api python -m scripts.q013_sol_smoke verify
```

The following command is reserved for explicit approval of full prose at both endpoints.

```powershell
uv run --extra api python -m scripts.q013_sol_smoke run --approved-plan-sha256 ca0314f557dc4a8b4e23085cc974dfd4d7c51abbc30c510d6f1e6f9149342ee3 --confirm-full-prose-openai-both-endpoints
```

After an authorized run, inspect both slots and score any eligible delivery against the two frozen rules. Production prompts are unchanged and the full workflow canary remains on hold.
