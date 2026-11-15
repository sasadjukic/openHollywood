# Authored three-work smoke: frozen plan, 2026-11-15

The real-transport wrapper and observed-delivery audit are qualified locally with
injected responses. The three-work smoke is frozen and **awaiting approval**:
**three input counts before three generations, no retries**. No live provider calls
were made. Production prompts are unchanged; the full workflow canary is **ON HOLD**.

The purpose is to test the tracked factual-assessment path across the three fresh
families admitted on November 15. This is not a model comparison, writer test or
story-quality qualification.

## Frozen identity and inputs

Private root: `data/diagnostics/assessment-authored-three-work-smoke-2026-11-15/`.

| Item | SHA-256 |
| --- | --- |
| Approval target: `plan.json` exact bytes | `f474bfc29bee448116993fc6845faccbee3cf60b48e1b1cbf8afc5ac3e93b779` |
| Request-set canonical payload | `d9b60e80c404f270b6eb04b078d7ba4ee452119053f97d6b127140e61081ebf4` |
| Operator `scoring.json` exact bytes | `ff6b6f1ad7bc7e30fa19c6cc1b64f964123cae358a8539bfc9c9e54f292babca` |
| Reviewed `metadata.json` exact bytes | `fe9ff429785dcbb0552676530f2268bb64c02baebec91f3790a3e11e042fed2c` |

`prepared/request-set.json` contains all six exact endpoint bodies and their hashes.
They are byte-identical to the previous authored mapping qualification. Only the
local run identity and reviewed pricing-version metadata changed; no diagnostic
instruction, selection, source or schema changed. The new plan pins its implementation
as well. The nested preparation remains `live_authorized=false`; only separately
approved one-shot execution may dispatch it. No preparation is silently promoted.

Each endpoint receives the full original work, original selected claims and unselected
summary, complete source-bearing context, source scopes, explicit work briefs,
historical authority and claim-specific evidence obligations. Current scenes and the
relevant complete older draft remain intact. Gold stays in the operator-only scoring
file, outside model input. Sources are explicitly `authored_diagnostic`; they are not
saved ordinary model reviews or independent human controls.

## Cases and unchanged gold

The exact whole claims, sixteen material components, eighteen witness locations and
adequate-evidence rules are frozen from the existing admission records in `scoring.json`.
The following table is an index, not a replacement for those whole claims.

| Family / claim | Contrast | Expected label |
| --- | --- | --- |
| F01 ferry Q001 | Required boarding/delivery, return ashore, both ropes fastened and bell silent at endpoint | supported |
| F01 Q002 | Alleged throughout boarding prohibition and alleged obedience; assignment requires boarding and scene depicts it | unsupported |
| F01 Q003 | Contents of an unavailable next-scene draft | uncertain |
| F02 kiln Q001 | True uncovering action plus false violation of the older assignment; later restriction cannot govern v1 retroactively | unsupported |
| F02 Q002 | Contents of an unavailable conservator's report | uncertain |
| F02 Q003 | Earlier critic alleges breakage; complete older prose establishes intactness, re-covering and non-removal | supported |
| F03 printroom Q001 | Contents of an unavailable authorship certificate | uncertain |
| F03 Q002 | First signature checked, second covered/uninspected, stamp unused, and current assignment compliance | supported |
| F03 Q003 | Conditional promise incorrectly treated as completed paired proof and stamp use | unsupported |

There are nine active whole claims: three supported, three contradicted (`unsupported`)
and three unavailable (`uncertain`). Each family's fourth, editorial summary remains
visible but unselected. F02 retains both historical copy bindings. The gold is
assistant-authored and locally checked, not independently human-rated.

## Endpoint order and resources

| Slot | Family | Endpoint | Body bytes |
| --- | --- | --- | ---: |
| 1 | F01 | `https://api.openai.com/v1/responses/input_tokens` | 44,623 |
| 2 | F02 | same input-count endpoint | 63,287 |
| 3 | F03 | same input-count endpoint | 47,997 |
| 4 | F01 | `https://api.openai.com/v1/responses` | 44,770 |
| 5 | F02 | same generation endpoint | 63,434 |
| 6 | F03 | same generation endpoint | 48,144 |

Both endpoints receive full unpublished fictional prose and diagnostic context.
All three counts must pass before the first generation. There are **at most six
endpoint attempts: three counts and three generations**, with no retries, warmups,
model-list probes, replacement works or follow-up repairs.

Use **`gpt-6.1-sol`, reasoning `high`**, strict structured output, `store=false`,
`truncation=disabled` and the existing default service tier. Public documentation was
reviewed on November 15: the model supports high reasoning, structured output,
a 1,050,000-token context and 128,000 maximum output tokens. The plan uses the
documented unsuffixed alias; no immutable dated snapshot is claimed.
[Official model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol).

Per generation, cap admission at **272,000 input tokens**, reserve **32,000 output
tokens**, and cap the conservative local cost estimate at **$1.00** (**$3.00 total**).
Use standard rates of $2/M input and $10/M output with a conservative 1.25 input
multiplier for potential cache writes; assume no cache discount. Thus the maximum
reservation is $0.68 input plus $0.32 output per work. Actual usage and billing remain
unknown until observed; this estimate is not an invoice guarantee. Inputs beyond
the long-context threshold are refused by this plan.
[Official pricing](https://developers.openai.com/api/docs/pricing).

Allow 120 seconds per count, 600 seconds per generation, and a 2,700-second dispatch
window. Output reservation includes reasoning resources under the existing adapter.
Observe input, output, reasoning and cached-input usage separately. Record terminal
latency, counts and conservative cost estimates; do not replace missing counters
with zero. Local fixture counts and usage are invented protocol data and do not
predict real token demand or latency.

Account/model availability is unverified. Reuse of `OPENAI_OH_KEY` was already
authorized; the real key is resolved only after exact approval, fixed empty-journal
checks and source/gold validation. No provider authentication was used here.

## Scoring and stops

1. **Delivery and accounting:** retain all six fixed slots. Report count admission,
   terminal state, exact source/request/native binding and accounting independently.
   Completion eligibility requires all three works to bind completely, a closed
   complete journal, no pending slot and no accounting hold. Never qualify a subset.
2. **Whole-claim judgment:** inspect every delivered claim against frozen gold;
   report per-claim labels, correct/9 and results among delivered claims separately.
   Missing deliveries cannot count as correct. Unsupported mixed claims must retain
   the true clause in their explanation instead of denying the whole event.
3. **Evidence adequacy:** check the exact document, version, field and all material
   components. A truthful locator alone is insufficient evidence. Check historical
   assignment authority, endpoint versus throughout scope, attribution versus event
   truth, conditional versus observed action, and the unavailable-source obligation.
   Equivalent complete evidence is allowed; example references are not a whitelist.
4. **Explanation materiality:** identify invented facts, unsupported inferences or
   omitted qualifications that change the assessment. Record judgment correctness
   separately from citation/coverage correctness. Mechanical binding does not confer
   factual truth. Semantic scoring remains manual after all available fixed slots
   have been inspected; no gold-driven repair or second model adjudication.

Stop all later dispatch on any failed, unknown or over-budget count; transport/HTTP
failure; empty/refused/truncated/malformed/wrong-model response; invalid native binding;
missing usage; reservation violation; timeout/cancellation; drift in source, requests,
gold, metadata or code; or journal failure. No trimming, retries, budget increase,
slot replacement or resumed run. An intent flushed before interruption is consumed
even if provider receipt is unknown. Audit the surviving prefix and undispatched
slots. The prospective `live-journal` directory must not exist before execution.

## Local implementation and verification

The new service and CLI are `assessment_openai_authored_smoke.py`, under the API
services and `scripts/` respectively. See [ADR 0059](../adr/0059-authored-three-work-observed-smoke.md).
The qualified client uses TLS verification, no proxy environment, no redirects and
zero transport retries. Intent is durably flushed before send, with another full
validation immediately before transport. Response size and async time are bounded.

Source origin and delivery origin remain separate. Fixture capture cannot occupy
the live path. The observed path was exercised in tests by replacing the real
transport constructor with injected responses and synthetic credentials; this is
not an observed provider run. The audit preserves all sources and original scopes,
derives request-bound evidence rendering separately, and exports seventeen files.
Local hash chains are application evidence, not provider-signed attestation.

**52 new wrapper tests pass.** The full packets additionally pass uncached source
recollection through complete, missing-final-usage and interrupted-final-generation
rehearsals. The complete fixture binds all nine claims. The missing-usage fixture
also binds nine but denies completion for every work; interruption preserves six
bound claims and the final unknown consumed slot. All three audits reuse exactly,
with no mtime changes. No fixture becomes model-performance evidence.

**318 tests pass: 52 new wrapper tests and 266 existing mapping, source, native
receipt and compact-smoke regressions**, without warnings. Ruff, formatting and
strict mypy pass on **298 files**. Logs are `tests-wrapper.log`,
`tests-regression.log`, `ruff.log`, `format.log` and `mypy.log`; schema and local-link
checks also pass.

Preservation verifies **2,260 prior sealed members**, the separate **64-member**
authored-control seal, **636 archive pins**, **818 baseline files** outside three
documentation updates, both earlier closed smoke journals, **375** source-archive
files/mtimes and **104** new preparation/journal/audit members. All fourteen issue
bodies and posted URLs are unchanged. The private root retains source snapshots,
inspection records, preservation counts and the final acceptance seal.
The Windows sandbox blocked asyncio's loopback wakeup socket before transport;
offline suites were run outside that restriction with external-network guards.
No dependency, persistence schema, frontend or production behavior changed; no web
build or migration is applicable. Repository-wide pytest was not run.

## Approval and next step

Approve the exact plan above to allow **three counts before three generations,
no retries**, sending full prose/context to both stated OpenAI endpoints. Until
then, live calls remain paused. After approval, verify again, execute once into the
fixed journal, inspect all six slots and every available claim, document outcomes
and update the tracker. Any stop requires a new decision before further inference.

The smoke can establish end-to-end delivery and provide limited factual-assessment
evidence across these authored families. It cannot qualify natural critic precision,
editorial effect, edit necessity, writer preservation or overall story quality.
Human review remains focused on feel, flow, character and story-breaking effects.
CW-007/CW-013 remain open; CW-014 unqualified. Step 19 remains IN PROGRESS, Step 20
NOT STARTED. Production prompts stay unchanged and the canary stays ON HOLD.
