# OpenAI assessment request/response mapping qualification

Date: 2026-11-13. Local mapping qualification **COMPLETE**.
Production prompts unchanged; live calls **PAUSED**; full workflow canary **ON HOLD**.

The shared OpenAI request serializer reproduces all twelve logical endpoint bodies
from the six selected historical B deliveries. The new offline response mapper
preserves their exact finals, known usage and all 36 original native result bindings.
Authored provider-format fixtures qualify failure, cancellation, request-mismatch
and unknown-usage branches without contacting either OpenAI endpoint.

This qualifies mapping under the stated contract. It does not authenticate a new
model delivery, attach historical results to current intake, or establish improved
claim judgments or story quality.

## Implemented boundary

The tracked [OpenAI assessment mapping module](../../engine/open_hollywood_engine/models/assessment_openai.py)
provides `prepare_wire`, `check_outgoing`, `map_response`, `count_admitted` and a
one-shot `OfflineReplay`. It has no real HTTP client, credential resolver, catalog
lookup, database or live execution command. Its replay accepts only an injected
`httpx.MockTransport`; callbacks are trusted local test code, not a Python sandbox.
No provider SDK types enter the native assessment domain.

The existing gateway's request-body method now delegates to the pure
`render_responses_body` function in [openai.py](../../engine/open_hollywood_engine/models/openai.py).
The extracted function's executable AST is identical to the former method body.
No production parser, settings, prices, prompt, profile, workflow or retry behavior
changes. Existing provider/routing tests cover the delegation.

Preparation requires an already prepared assessment work, exact batch scope,
matching full messages and native schema, an explicit model specification and
bounded request. It does **not** turn ordinary critic messages or the synthetic
fixture presentation into an assessment prompt. It preserves the native request
identity separately from count/generation body identities. Authentication of that
work remains the source collector's responsibility.

The generation body reuses the established serializer: complete input messages,
strict response schema, explicit reasoning effort, disabled input truncation,
`store=false`, `background=false`, `stream=false`, default service tier and bounded
output. Seed and sampling omissions remain explicit. Count includes the identical
model/input/schema/reasoning fields, without generation-only settings. New local
UTF-8 serialization has separately named exact-byte and canonical-body hashes.

Before a fixture callback, checks require the exact POST URL, path, body bytes,
hashes and safe host/content-length/content-type headers. Authorization headers are
not used. A failed, missing or invalid count blocks generation; successful counts
must fit input, context, output reservation and historical cost limits. No estimate
fallback, retry, redirect, streaming, hosted tool or provider-side conversation is
added. The one-shot replay remembers consumed intent before calling the fixture;
interruptions leave that intent unresolved, and the same replay object cannot run
again. This is an **in-memory test runner**, not a replacement for the existing
durable manifest/journal service or a cross-process retry safeguard.

## Response and accounting contract

The mapper preserves safe response ID/model metadata when present, exact final
text and its UTF-8 hash, terminal status, recognized incomplete reason and nullable
usage. It excludes arbitrary headers, error messages, reasoning content and
encrypted reasoning. It uses bounded strict JSON parsing, rejecting duplicate keys
and nonfinite values. Secret checks reject unsafe payloads without rewriting a
bound final. Request and response bounds are 16 MiB and 1 MiB; native final bounds
remain 64,000 characters and 256,000 UTF-8 bytes.

| Observed condition | Local mapping decision |
| --- | --- |
| HTTP 200, completed status, allowed model, one completed assistant final text | Complete terminal envelope; native final validation still required |
| Multiple messages/text parts, commentary phase, unexpected tool/item, wrong model, missing final | Invalid; no concatenation or slot salvage |
| Output-token limit | Length; retain safe partial final and valid usage |
| Refusal or content filter | Refusal; no successful result credit |
| Non-200 HTTP, provider error, failed/cancelled status | Error; HTTP failure cannot be overridden by a completed body |
| Unknown/nonterminal status, malformed envelope or inconsistent usage | Invalid; preserve independently valid counters where available |
| Missing usage or optional counter details | Preserve null; never substitute count estimates or zero |
| Timeout/transport error or process interruption | Consumed fixture intent; no retry and no invented response/usage |

Known zero, missing counters and partial counters are distinct. Reasoning remains a
subset of output and cached input a subset of input; inconsistent subtotals cannot
be promoted to valid accounting. Actual billed cost remains unknown. The mapped
object explicitly says `mapping_only_not_delivery_authentication` and grants no
writer permission. A complete envelope can contain malformed assessment JSON,
missing/extra slots or unregistered citations; the native binder still rejects it.

This mapper is intentionally separate from the production gateway's existing
response parser. In particular, the current gateway concatenates output text parts
and defaults absent optional usage details to zero. This task preserves that
production behavior and tests the narrower assessment contract separately. The six
selected real responses do not exercise those differences, so they provide no new
evidence of historical failures caused by either behavior.

The official [token-counting guide](https://developers.openai.com/api/docs/guides/token-counting)
documents the separate input-count endpoint and that output counts include
non-visible output. The [Responses reference](https://developers.openai.com/api/reference/python/resources/responses/methods/create)
documents terminal status, incomplete details and usage. These were checked for
the boundary design; historical settings/prices were replayed from pinned records,
not presented as current account access, current prices or invoice evidence.

## Saved-capture qualification

Reuse the six deliveries selected by the
[November 12 admission audit](assessment-delivery-admission-2026-11-12.md):
`BH-1-{A,B,C}-B-{SC,CS}`. These cover all three registered families, both orders,
first repeat, using the original `gpt-6.1-sol` high-reasoning specification. No new
selection by outcome, gold change or semantic rescore occurs.

The current registered archive collector authenticates **636 source members**.
Historical programs remain inert; none is imported or executed. The new helper
reconstructs the recorded request settings, passes full original messages/schema
through the shared serializer, then injects saved sanitized response bodies into
the new mapper. All six native results equal their original bound results.

- **12/12 logical endpoint bodies and effective settings match.** Historical request
  capture proves logical JSON equality, not original HTTP serialization bytes.
- **6/6 exact finals, usage records and native bindings match; 36 slots retained.**
  Each count reconciles with its saved generation input usage.
- **6/6 response-level IDs remain null**, because the archive did not retain them.
- **6/6 repeated replay attempts are refused** by the one-shot fixture runner.
- All **636 source members retain their hashes and modification times**.

Original raw HTTP responses are absent. Their recorded raw digests are preserved
separately from the digest of the sanitized record and the newly serialized replay
body. Replaying those sanitized bytes is not reconstruction of the original HTTP
body or proof of a fresh provider response. The source archive supplies historical
local integrity, not provider signatures.

No failed real delivery was selected; failure qualification comes from explicitly
authored fixtures. The earlier **0/24** current-intake attachment result stands.
Old B work has six claims and a six-claim diagnostic instruction. It cannot become
N06/N07/N10/N11 work by relabeling units, changing receipts or passing its text to a
new renderer.

## Verification and evidence

The new authored tests exercise request/scope/model/schema drift, exact outgoing
bytes and URLs, metadata retention, aliases, failure states, usage bounds, missing
usage, secret rejection, native invalid-final refusal, count budgets, cancellation,
interruptions, oversized responses and one-shot behavior. Network, HTTP clients and
SQLite are blocked in these tests and in the actual saved-capture qualification.

**732 distinct tests pass across the broader and final mapper checks.** The combined
suite passed **730 tests** (641 existing and 89 new), with 56 existing deliberate
mutation warnings, in 281.99 seconds. Two additional mapper-only regressions then
covered invalid Unicode and excessive JSON nesting; all **91 final mapper tests**
passed in 2.32 seconds. Existing gateway/assessment code did not change between
those checks. The six actual saved deliveries also replayed again with the final code.

Ruff, formatting and strict mypy pass on **259 files** (258 repository files plus
one private audit helper). Existing async provider/SQLite tests used isolated
fixtures outside the sandbox after an initial in-sandbox stall; no real database or
live provider was accessed. No frontend/build check applies: no API route, OpenAPI
contract or client code changed.

Preservation checks verify **1,060 earlier sealed evidence members**, the **636
selected archive source members**, and **738 baseline files** outside five declared
existing-file edits. All fourteen issue bodies and posted GitHub URLs remain exact.
The five edits are the shared serializer and four documentation/tracker files;
new mapping/test/report files are separate. Existing fixture contracts, archived
requests/responses, model profiles, production prompts and the native publisher
remain unchanged.

Private evidence root: `data/diagnostics/assessment-openai-mapping-2026-11-13/`.
Accepted per-delivery records are in `accepted/deliveries/`.

- [Selection](../../data/diagnostics/assessment-openai-mapping-2026-11-13/selection.json),
  [six-delivery results](../../data/diagnostics/assessment-openai-mapping-2026-11-13/summary.json),
  [source pins](../../data/diagnostics/assessment-openai-mapping-2026-11-13/source-pins.json).
- [Serializer equivalence](../../data/diagnostics/assessment-openai-mapping-2026-11-13/serializer-equivalence.json)
  and [local replay helper](../../data/diagnostics/assessment-openai-mapping-2026-11-13/audit.py).
- [Verification](../../data/diagnostics/assessment-openai-mapping-2026-11-13/verification.json)
  and [preservation](../../data/diagnostics/assessment-openai-mapping-2026-11-13/preservation.json).

## Recommended next step

Integrate this qualified mapping into the **source-bound assessment manifest and
durable journal path**, keeping the real provider contract separate from authored
fixture contracts. Verify locally on the four current intake works, with their six
claims and unchanged holds/unselected context. The preparation must explicitly
bind a batch-appropriate assessment presentation, full source/brief context, exact
wire bodies, model settings, count/output/cost reservations and implementation
identity. Do not reuse the historical six-claim prompt indiscriminately or convert
synthetic fixture origins into authenticated delivery labels.

Once that integration and failure accounting pass, freeze a small smoke plan for
approval: provisionally **four generation attempts plus four input counts**, one
existing batch per N06/N07/N10/N11, zero retries, stop on failed count, delivery or
unresolved accounting. Fix exact requests, current reviewed model metadata and a
cost/time ceiling before requesting approval. This is a recommendation, **not a
frozen or approved live plan**. No broader model comparison is needed to qualify
these plumbing changes.

The resulting assessment still supplies read-only factual evidence, not permission
to rewrite. Evidence adequacy, editorial effect, edit necessity and human judgments
of feel, flow, character and story-breaking details remain separate. No additional
mandatory human checkpoint is introduced. CW-007/CW-013 remain open; CW-014
unqualified. Step 19 **IN PROGRESS**; Step 20 **NOT STARTED**.
