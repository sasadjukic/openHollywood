# Compact version-two four-work OpenAI smoke plan

Date: 2026-11-14

Status: frozen and verified locally. **Awaiting live approval.**
No provider API calls have been made for this plan.
Production prompts unchanged; full workflow canary **ON HOLD**.

## Purpose and unchanged controls

Test whether the exact version-two compact presentation fits the resource
reservation and delivers bound assessments for N06/N07/N10/N11. This is a delivery
smoke with claim inspection, not a model comparison or story-quality test.

The [qualified version-two mapping](assessment-openai-compact-qualification-2026-11-14.md)
and its diagnostic messages/schema remain unchanged. All eight endpoint bodies
must match that qualification byte for byte. New prospective request and plan
identities bind the reviewed metadata and a new fixed journal. The old November 13
smoke remains closed: its one count, zero generations and unused slots stay intact.

| Work | Original active claims | Distinction retained | Count bytes | Generation bytes |
| --- | --- | --- | ---: | ---: |
| N06 | Q001 | Assignment attribution and depicted crossing | 274,545 | 274,692 |
| N07 | Q004, Q005 | Current endpoint versus future starting state | 309,299 | 309,446 |
| N10 | Q003, Q007 | Exit obligation versus next-scene claim | 314,049 | 314,196 |
| N11 | Q003 | Historical allegation versus current correction | 290,079 | 290,226 |

Preserve all six active claims, 51 original fields, four holds and 41 unselected
fields. Full visible source prose, original messages, whole reviews, scope
declarations, work briefs and all 3,658 source locators are retained. Held and
unselected fields remain context, not new targets. Only the already qualified
operator provenance body stays in the exact hash-bound local file; its contents
are not sent to either endpoint or promoted into story authority. N11's visible
historical allegation and repair evidence remain available.

Private root: `data/diagnostics/assessment-openai-compact-smoke-2026-11-14/`.

- `plan.json`: order, exact work/preparation/presentation bindings, budgets, scoring,
  stops, implementation identity and fixed `live-journal` path.
- `requests/N06`, `N07`, `N10`, `N11`: immutable source-bound preparations with
  local provenance and exact endpoint bodies.
- `selection.json`: verbatim claims, source/request identity and endpoint hashes.
- `settings.json`, `public-docs-review.json`: model metadata and resource review.
- `inspection-template.json`: eight fixed endpoint slots and six claim inspections;
  all live-result fields remain empty.

**Plan bytes SHA-256:** `fa814d8c09b897ad8c6c9b902ef99a9eec7b24a49a8923ec4f2643253d8181f5`.

## Payload, endpoints and budget for approval

The future run sends full unpublished fictional prose and diagnostic context to
both OpenAI endpoints:

- `https://api.openai.com/v1/responses/input_tokens`
- `https://api.openai.com/v1/responses`

Use the existing approved application credential `OPENAI_OH_KEY` in memory. No
credential is written to source, requests, traces or exports. No Ollama, model-list,
catalog, synthetic preflight, response polling or recovery request is included.

| Reservation | Frozen ceiling |
| --- | --- |
| Model / reasoning | `gpt-6.1-sol` / `high` |
| Input-count attempts | 4 total, one per work |
| Generation attempts | 4 total, one per work |
| Retries, resumes, substitutions | 0 |
| Input tokens | 272,000 per generation; 1,088,000 total reserved |
| Output tokens including reasoning | 32,000 per generation; 128,000 total reserved |
| Conservative generation estimate | $1.00 per work; $4.00 total |
| Count / generation network deadlines | 120 / 600 seconds per attempt |
| Run dispatch window | 3,600 seconds after initial authentication/journal creation |
| Concurrency | 1 request |
| Response-body bound | 1 MiB per endpoint |

Official documentation reviewed November 14 supports Sol/high, structured output
and the retained model limits. The 272,000 input cap is our conservative pricing
boundary, not the model's full context limit. Standard rates are $2/M input,
$2.50/M cache writes and $10/M output; using the cache-write allowance yields
$0.68 + $0.32 = $1.00 per reserved generation. This is a published-rate estimate,
not a guarantee of actual billing; input-count calls are not assumed free.
[Model and rate documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol).

No current account/model access or balance was queried, and no real token count
was measured. Byte sizes and authored count 100 are not token-fit evidence. Count
uses the same messages, model, reasoning and structured response format as
generation. [Token-count documentation](https://developers.openai.com/api/docs/guides/token-counting).

Keep `store=false`, disabled truncation, explicit default service tier, no tools,
no background execution and no added conversation state. The same original messages
remain embedded as source context. Reasoning consumes the output cap; reasoning
text is not retained as assessment output. Metadata review changes no endpoint body.

## Order and stops

1. Validate the approved plan hash, implementation, registered sources, compact
   exports, request preparations and fixed empty live-journal location locally.
   Refuse every existing journal, including an interrupted or partial one.
2. Count N06, N07, N10, N11 in order. **Every count must pass before any generation.**
   A failed, malformed, unknown, non-200 or over-budget count halts all remaining
   slots. An unused slot stays unused; no retry or replacement count.
3. Generate N06, N07, N10, N11 in the same order, at most once each. Stop on failed,
   empty, refused, truncated, ambiguous, malformed or wrong-model delivery; failed
   native binding; missing usage; or any reservation violation. A successful subset
   cannot qualify the original whole work.
4. Stop on source/presentation/request/code drift, secret refusal, cancellation,
   deadline, journal/fsync failure or other uncertainty. Recheck the remaining
   deadline after durable intent and before sending. Every consumed intent counts,
   including an interrupted request whose remote processing or usage is unknown.
   Do not infer that cancellation or timeout prevented provider processing.
5. Audit all eight fixed slots and every returned claim. Export interrupted
   evidence without another call. Missing closure prevents completion eligibility.
   No input trimming, prompt/schema repair, budget increase, model/work substitution,
   automatic retry, polling or resumption is authorized.

Transport verifies TLS and disables redirects, environment proxies and connection
retries. Exact outgoing bytes are checked and the intent is fsynced before sending.
The async deadline covers send plus body read, bounded by the remaining run window.
Initial source authentication and final local audit are outside that window;
synchronous validation can finish after it, but cannot authorize a later send.

## Scoring and inspection

Report separately: source/request integrity, count admission, complete terminal
delivery, strict native binding for every active claim and whole-work completion.
Retain requested/returned model, available request/response IDs, safe error chain,
final digest, elapsed interval and nullable usage. List every undispatched slot.
Show known generation-token subtotals and unknown-usage generations; do not treat
an input count as generation usage. Distinguish known over-budget usage from missing
usage. Actual billed cost stays unknown.

Inspect all six delivered claim assessments against their unchanged declarations,
source scope and work briefs: whole-claim support, every material clause, exact
source/version/reference binding, endpoint coverage, historical authority,
future-state availability and explanation materiality. Record unresolved
interpretation explicitly. The earlier four authored batch responses are binding
fixtures, not semantic gold. No pooled model-quality score or new gold is frozen.

The smoke cannot establish editorial merit, justified writer edits, generalization
to fresh stories or story quality. Humans retain feel/flow/character/story-breaking
review. No writer dispatch or full-workflow qualification follows from completion.

## Local qualification and execution boundary

- **407 relevant tests pass**: 48 new version-two transport tests (188.50 seconds)
  and 359 shared mapping, compact-presentation, source/terminal, native-binding and
  original-smoke regressions (499.10 seconds). No test failures or warnings.
- Ruff, formatting and strict mypy pass on **282 files** (281 repository files
  plus the private preparation/rehearsal helper). Both new schemas match runtime.
- The actual four registered works pass preparation, exact freeze reuse, read-only
  CLI verification and all **eight injected endpoint slots**. The same four authored
  batch responses cover six assessments with complete native binding and whole-work
  completion. Terminal audit publication and exact reuse pass. Network, real provider
  transport and SQLite are blocked in the actual helper; tests use isolated fixtures.
  Windows event-loop/file checks run outside the sandbox, with transport still mocked.
- All eight request bodies match the previously qualified compact controls byte for
  byte. The original intakes and compact exports are unchanged. **1,583 earlier sealed
  members**, **636 archive pins**, **785 baseline files** outside four documentation
  updates, the closed original live journal, all fourteen issue bodies and posted
  URLs are preserved. No previously observed delivery is relabeled.
- Documentation links, UTF-8/LF and `git diff --check` pass. No client/build check
  applies: no client code, API route or persisted schema changed.

Private `prepare_verify.py`, `qualification.json`, `verified/journal`,
`verified/audit`, CLI/test logs, final source snapshots, preservation records and
the acceptance seal retain the local evidence. Authored count 100 and fixture
usage do not measure token fit or billing. The fixed `live-journal` is absent.

The new [service](../../apps/api/open_hollywood_api/services/assessment_openai_compact_smoke.py)
and [CLI](../../scripts/assessment_openai_compact_smoke.py) use the verified compact
preparation, shared mapper and native completion. Separate version-two
[plan](../contracts/assessment-openai-compact-four-work-smoke-2.schema.json) and
[event](../contracts/assessment-openai-compact-smoke-event-2.schema.json) contracts
refuse version-one records. [ADR 0055](../adr/0055-compact-four-work-assessment-smoke.md)
documents the boundary.

```powershell
uv run --extra api python scripts/assessment_openai_compact_smoke.py verify `
  --plan data/diagnostics/assessment-openai-compact-smoke-2026-11-14/plan.json
```

Only after explicit approval, `run` also requires the exact approved hash,
`--confirm-full-prose-openai-both-endpoints` and the frozen `live-journal` path.
`verify` and `audit` never resolve the application key or dispatch a call. The
fixture journal lives separately under `verified/journal` and cannot be resumed
or relabeled as a live observation.

CW-007/CW-013 remain open; CW-014 unqualified. Step 19 **IN PROGRESS**, Step 20
**NOT STARTED**. Approval of this exact plan is the next boundary; no live approval
or canary authorization is implied by local preparation.
