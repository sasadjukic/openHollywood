# Q010 Sol-high smoke approval plan

**Executed November 22, 2026. Both slots are spent.** [Observed results and independent scores](q010-sol-high-smoke-results-2026-11-22.md)

**Frozen for approval on November 22, 2026.** This smoke asks whether Sol can recognize what the final sentence of *The Pristine Lure* establishes about Elias’s movement and explain what it leaves open. Approval covers one input count and at most one generation with `gpt-6.1-sol` at `high` reasoning effort. Both OpenAI endpoints would receive the full unpublished prose and story context.

**Approval SHA-256** `792d7f4b809bdbd5064f29c497bd15414bed606f297519a694badeaf7d2e1e45`

## Case and exact requests

Q010 is the entire achieved-state field from Gemma’s ordinary v61 critique v2 (`2268e6e8-b82b-4cca-932f-55cc418a58b5`). It refers to draft v1 (`b74efc96-dbe6-4147-8dd3-a1c24f295321`). Scene Plan v1 (`b5179ac9-5585-5e5b-9555-20ca70b68f6a`) supplies the assignment context. The original critic invocation was `a2893a10-cc21-4844-9393-65f56f044f4d`.

> Elias has moved past the circle of shoes and is entering the threshold of the monolith.

The approval binds both request bodies in this order.

| Slot | OpenAI destination | Body bytes | Body SHA-256 |
| --- | --- | ---: | --- |
| 1. Count | `POST https://api.openai.com/v1/responses/input_tokens` | 263,928 | `2ee4c9e4617f6b8c7cc203af1d4491c9ec85c916ea3b9c68c2fa3971f16dcb46` |
| 2. Generate after an admitted count | `POST https://api.openai.com/v1/responses` | 264,075 | `b30c0697f7aca46f7ae7075ad17a2c15cfc13c4a6c0fd8458d7425a743a35bb5` |

Both bodies carry identical assessment messages and response schema. They include the complete draft, plan, original critic context, the twelve review-field dispositions, the Q010 brief and the registry of 883 evidence references. The schema asks for Q010 alone. Sol can see the critic’s own citation and a reference to the full draft, so this measures assessment with those clues available. The operator gold and scoring rules stay outside both payloads. Q016 remains held for editorial interpretation. [Local intake and request qualification](q010-intake-rehearsal-2026-11-22.md)

The source verifier reconstructs Q010’s intake from the sealed critic capture. The Q010 work fingerprint is `6f4c8be5bdfab5ca4d33befe1b6545a0784bd2da6e91e4fa7ef0d9d134fb5021` and the request manifest SHA-256 is `c4a5eabad2f89a9082291f8283f79a23a7014e5e9d5b5baf2e710167498ef116`. Q008’s earlier assessment of this same critique has a separate work identity, request and receipt. [Source binding](../../scripts/q010_assessment.py)

## Dispatch budget and stops

1. Recheck the approval, registered source, exact artifact versions, work, frozen bodies, implementation and scorer-gold digest before dispatch. A mismatch stops the run. The runner claims the pre-issued SQLite row once and writes a durable intent before each POST.
2. Admit generation only after a valid HTTP 200 input count of **1–96,000 tokens**, within the model context window and the frozen cost ceiling. Reserve up to **32,000 output tokens including reasoning**. The frozen rate card gives a conservative maximum of **$0.56** under the **$0.60** ceiling. Actual usage and billing are unmeasured.
3. Allow **120 seconds** for the count, **600 seconds** for generation and **900 seconds** for the dispatch sequence. The client uses verified TLS, zero retries and no redirects. The generation body specifies strict structured output, disabled truncation and `store: false`.
4. Stop on cancellation, deadline, transport error, HTTP failure, refusal, truncation, malformed output, wrong model, missing or extra claim, or an unknown citation. Missing input/output totals or usage over budget disqualify the generation. The audit preserves known values and leaves unknown usage null.
5. An interruption consumes the run, including one between the admitted count and generation. An intent without an outcome is reported as `possibly_sent`. Restart, replacement and fallback are excluded. After an approved run, inspect both slots, including any undispatched slot.

## Independent claim and evidence scores

Score only a closed, observed, complete response bound to Q010, both exact versions and this request, with eligible usage. Otherwise record both scores as **unscored**, alongside the stop reason. Preserve the returned label, explanation, citations, slot dispositions, latency and available usage. The pre-existing operator gold SHA-256 is `b1b616529e3f4040c28c165093201c7bc1299bf6b42295f4e587d9e3f57cd92a`. [Gold and source audit](q008-q013-ending-claim-audit-2026-11-22.md)

| Score | Pass condition |
| --- | --- |
| Whole-claim correctness | The returned label is `uncertain` for the complete 87-character field. Either other permitted label fails. |
| Evidence coverage | The cited draft passage and explanation establish that Elias passed the shoes and moved toward the threshold. The explanation recognizes that his exact position at the cut remains open. Accept the final excerpt `E0321`, the complete draft `E0883` with a precise passage locator, or equivalent version-bound draft evidence. |

A definite crossing or stop outside overreads the ending. A plan-only citation, an unlocated whole-draft reference, material misattribution, missing coverage or a claim that the supplied draft is missing fails evidence. A correct label can fail evidence, and a wrong label can accompany adequate evidence. The outcome concerns one guided factual claim. Story quality and the desirability of an edit remain editorial judgments.

## Local verification

The renderer reproduced both frozen bodies with access to scorer files blocked. The separate payload inspection resolved all 883 evidence references and caught four injected gold leaks. Six authored responses exercised the scoring rules. The final excerpt and a precisely located full draft each earned both passes. Definite entry and a definite stop outside each failed both scores. The plan-only and mismatched-label controls earned opposite scores on the two axes. Q016 produced zero requests.

All **24 exact-request journal rehearsals** used disposable ledgers and injected HTTP responses. The 96,000-token boundary admitted generation. Zero, missing and 96,001-token counts, an HTTP 500 and a redirect each ended after the count. Generation controls covered truncated, refused, malformed and wrong-model responses, a missing claim, a Q008 substitution, an unknown citation, timeout and unknown or excessive usage.

Fresh-process restarts sent **zero additional requests in all 24 cases**. Two competing launches produced one count and one generation in total. Four forced exits immediately before or after mock receipt of a POST retained the pending intent as `possibly_sent` with unknown usage. Three more exits after the journal header, count outcome and generation outcome preserved the recorded progress. None of those open journals produced a score.

A disposable mirror of the live entry point rejected missing consent, a wrong approval digest, altered request bytes and altered gold before credential access. The correctly approved mirror used a synthetic credential and mock HTTP transport. It sent one count and one generation and refused a second launch. The fixed live journal stayed `ready` with both slots undispatched and no output directory.

All 2,681 distinct Python tests passed, including seven portable Q010 journal regressions. Ruff lint, formatting and strict mypy passed across 361 Python files. The local evidence is under `data/diagnostics/q010-sol-smoke-verification-2026-11-22/`. The request and scoring check is in `wire-and-scoring.json`, the dispatch and interruption reports are in `qualified/verification.json` and `interruption-gaps/verification.json`, and the entry-point report is in `observed-entry-fixture/qualification-only.json`. [Portable journal regressions](../../tests/api/test_q008_sol_smoke.py)

## Operator access

The private bundle is `data/diagnostics/q010-sol-high-smoke-2026-11-22/`. It contains the two exact bodies, source receipt, request manifest, `plan.json` and `dispatch.sqlite3`. Use the following read-only command to inspect both slots. [Single-use runner](../../scripts/q010_sol_smoke.py)

```powershell
uv run --extra api python -m scripts.q010_sol_smoke audit
```

The following command is reserved for explicit approval of this plan and its full prose/context at both destinations.

```powershell
uv run --extra api python -m scripts.q010_sol_smoke run --approved-plan-sha256 792d7f4b809bdbd5064f29c497bd15414bed606f297519a694badeaf7d2e1e45 --confirm-full-prose-openai-both-endpoints
```
