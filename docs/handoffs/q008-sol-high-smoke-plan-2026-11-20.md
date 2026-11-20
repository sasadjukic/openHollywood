# Q008 one-claim Sol-high smoke approval plan

**Executed November 20, 2026. Both slots are spent.** [Results and frozen scores](q008-sol-high-smoke-results-2026-11-20.md)

This smoke asks whether Sol can assess the complete factual
outcome explanation from one genuine Gemma v61 critique and cite evidence for each
part. The original critique is the sole selection. The reviewed draft supplies
evidence. There is one case, one count slot, one conditional generation slot and
zero retries. [Source qualification](assessment-saved-review-q008-qualification-2026-11-20.md)

**Approval SHA-256** `f447f66fa27d9731244304fbebd1a99426e7ed4b8794c0aaa23a3ed6f227e58a`.
The private bundle is `data/diagnostics/q008-sol-high-smoke-2026-11-20/`.
Its `plan.json` binds both request files, the source receipt, independent gold,
implementation, budgets, scoring, stops and the fixed journal location.

## Exact requests and budget

Both requests would send **full unpublished prose and story context to OpenAI**.
They carry the 307-character Q008 claim, original critic messages, whole review,
scene plan, draft, work brief and version-bound evidence registry. All 12 review
field dispositions remain visible, with Q008 alone active. The model-facing data
is byte-identical to the local qualification. The scoring record stays with the
operator. [Admission and frozen gold](ordinary-v61-single-capture-results-2026-11-20.md)

| Slot | OpenAI endpoint | Body bytes | SHA-256 |
| --- | --- | ---: | --- |
| 1. Count | `POST https://api.openai.com/v1/responses/input_tokens` | 265,153 | `9c29c18a3e2c9f3322785f25ccc61e8889898ae770e3ab78669c359870cfce1a` |
| 2. Assess after an admitted count | `POST https://api.openai.com/v1/responses` | 265,300 | `6c05c8c449abb43de995b7f5bad490e9b30bb5c8428b3cc870c916d01dcc790e` |

The critique version is `2268e6e8-b82b-4cca-932f-55cc418a58b5` and the draft
version is `b74efc96-dbe6-4147-8dd3-a1c24f295321`. The generator uses
`gpt-6.1-sol`, reasoning effort `high`, strict structured output, disabled
truncation and `store: false`. The input ceiling is **96,000 tokens** and the
output ceiling is **32,000 tokens**, including reasoning. The **$0.60** generation
cost ceiling uses the repository’s frozen rate card. The maximum reservation at
those token limits is $0.56. Actual input tokens, latency, usage and billing are
unknown before inference. The count deadline is 120 seconds, the generation
deadline is 600 seconds, and the dispatch sequence has a 900-second wall budget.

## Frozen scoring

Score a closed, model-matched, version-bound Q008 delivery against the original
gold file, SHA-256 `5c22a997adb4b8a533c4e3442f4e779149fd0179dd79a20ab4aeac2580cafbb0`.
Record each judgment separately, with the cited source and reason.

| Judgment | Pass condition |
| --- | --- |
| Whole-claim label | Sol returns `supported` for the entire outcome explanation. |
| Plan evidence | The cited plan establishes the assigned outcome of Elias being drawn to the building’s entrance. `E0233` or an equivalent version-bound witness qualifies. |
| Draft-ending evidence | The cited prose establishes Elias passing the shoes, moving toward the threshold and the narrated motive. `E0321` or equivalent evidence qualifies. For a full-draft citation such as `E0883`, the explanation must locate the relevant ending. Claiming that he arrives, enters or makes contact fails this judgment. |

Inspect all cited locations for material misattribution. An attribution that fails
to establish the plan or draft obligation fails that evidence judgment. Full
credit requires three passes. A valid `uncertain` or `unsupported` judgment earns
a label failure and still proceeds to evidence scoring. An ineligible delivery is
recorded as unscored, with the stop reason and disposition of both slots. This
case measures a guided factual judgment. The separate achieved-state claim, edit
necessity and the story’s editorial quality are outside its scope.

## Single-use execution and stops

1. Verify the approved plan digest, fixed source registration, critique selection,
   both version identities, implementation, gold digest and endpoint bytes. Only
   the live entry point with explicit full-context approval resolves the existing
   application credential.
2. Claim the pre-issued SQLite row with a committed conditional update. A launch
   that loses the claim stops. Write and flush each endpoint intent, rebuild the
   source, and check the journal before sending. The client uses verified TLS,
   zero transport retries, and disables redirects and environment proxies.
3. Generate only after a positive HTTP 200 count fits the input, context and
   reserved-cost limits. A failed count ends the smoke. A timeout, cancellation,
   HTTP error, source drift, refusal, length limit, wrong model, malformed final,
   invalid citation or missing/extra claim ends the attempt. No alternate model,
   draft-selected run, payload reduction or replacement slot is authorized.
4. An interrupted intent remains spent even when its terminal is missing.
   Inspect both fixed slots and preserve available status, elapsed time, response
   identity, usage and evidence. Missing usage remains unknown. Missing input or
   output totals or an exceeded budget holds the result out of scoring. A fresh
   launch cannot resume an interrupted journal. The read-only audit binds the
   result to the request manifest and both versions before scoring.

## Local verification

All **18 full-case rehearsals** used the frozen Q008 approval and independent
fixture journals. Across those cases the mock received 29 POSTs. A fresh process
retried each spent journal and generated **zero additional POSTs**. All provider
calls remained at zero. The hard-exit controls bypassed cleanup.

| Injected event | Count POSTs received | Generation POSTs received | Restart POSTs |
| --- | ---: | ---: | ---: |
| Exit after count intent, immediately before POST | 0 | 0 | 0 |
| Exit after the mock received the count | 1 | 0 | 0 |
| Exit after generation intent, immediately before POST | 1 | 0 | 0 |
| Exit after the mock received generation | 1 | 1 | 0 |
| Two processes launch the same issued journal concurrently | 1 total | 1 total | 0 |

The successful boundary count was 96,000. A count of 96,001, an HTTP 500 and a
redirect each ended the run after one count POST. Generation controls covered
timeout, refusal, length limit, wrong model, malformed response, omitted Q008,
unknown citation and missing or excessive usage. Each produced its own audit with
both slots accounted for. Incomplete and over-budget deliveries received no score.

An isolated copy also exercised the live entry with a substituted transport and a
dummy credential. Missing disclosure confirmation, a wrong approval digest, changed
request bytes and changed gold were rejected before credential access. A valid
launch sent the two expected requests to the mock, and reissue and restart were
refused. The actual approval ledger remained `ready` and had no output directory.
The private receipts are `qualified/verification.json` and
`observed-entry-fixture/qualification-only.json` under the verification workspace.

All 2,606 existing Python tests passed. The [seven new journal regressions](../../tests/api/test_q008_sol_smoke.py)
passed on rerun after correcting a test setup that also blocked HTTPX’s in-memory transport.
The corrected setup blocks network sockets and construction of a real transport.
The runner and frozen request bytes were identical across both runs.
`suite-verified.json` reconciles all 2,613 distinct tests. The suite reported 56
Pydantic serializer warnings. Ruff, formatting and strict mypy passed across 330 Python files.

## Operator access

The [runner](../../scripts/q008_sol_smoke.py) supports a read-only status check
with `python -m scripts.q008_sol_smoke verify`. After a run, `audit` reconstructs
both slots without dispatching. The SQLite claim is in `dispatch.sqlite3` and
its bound receipts are written under `output/` in the private bundle. Fixture
evidence lives in `data/diagnostics/q008-sol-smoke-verification-2026-11-20/`.

The frozen operator command for the now-spent journal is recorded below.

```powershell
uv run --extra api python -m scripts.q008_sol_smoke run --approved-plan-sha256 f447f66fa27d9731244304fbebd1a99426e7ed4b8794c0aaa23a3ed6f227e58a --confirm-full-prose-openai-both-endpoints
```

Production prompts are unchanged and the full workflow canary is on hold.
