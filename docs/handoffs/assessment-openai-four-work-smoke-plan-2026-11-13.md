# Four-work OpenAI assessment smoke plan

Date: 2026-11-13

Status: frozen and verified locally. **Awaiting live approval.**
Production prompts unchanged; live calls **PAUSED**; full workflow canary **ON HOLD**.

## Purpose and limits

Test whether the verified intake-bound path can deliver and bind assessments for
the four current works using actual OpenAI transport. This is a delivery smoke test,
not a new model comparison, story-quality evaluation or permission to rewrite prose.

The [previous integration](assessment-openai-integration-2026-11-13.md) remains
fixture-only. A separate prospective plan and journal qualify real transport without
relabeling old captures. The production gateway, prompt profiles, graph, gates,
existing fixture contracts, original sources, declarations and briefs are unchanged.

## Frozen work and exact requests

Use `gpt-6.1-sol`, explicit `high`, one original batch per work, in this fixed order:

| Work | Active original claims | Main distinction retained | Count body bytes | Generation body bytes |
| --- | --- | --- | ---: | ---: |
| N06 | Q001 | Assignment attribution and depicted crossing | 1,314,463 | 1,314,610 |
| N07 | Q004, Q005 | Current endpoint versus claimed future starting state | 1,352,941 | 1,353,088 |
| N10 | Q003, Q007 | Explicit exit obligation versus next-scene claim | 1,467,344 | 1,467,491 |
| N11 | Q003 | Historical allegation versus current correction | 2,198,122 | 2,198,269 |

All **six active claims**, **51 original fields**, **four holds** and **41 unselected
fields** remain present under their existing identities. Full source prose, original
messages, whole reviews, registry, provenance, scope declarations and work briefs
are retained. Held/unselected material is context, not an added assessment target.

The diagnostic presentation, schema and **all eight endpoint bodies are byte-identical**
to the verified rehearsal. Resource settings and the prospective request/plan identities
are new. No prompts, claims, evidence selection, schema cardinality or source ordering
change for this smoke run. The generic batch instruction is the already verified
diagnostic presentation, not the old historical six-claim B control.

Private root: `data/diagnostics/assessment-openai-smoke-2026-11-13/`.

- `plan.json`: exact work references, budgets, order, scoring, stops, implementation
  identity and fixed live journal path.
- `requests/N06`, `N07`, `N10`, `N11`: complete immutable intake-bound preparations;
  each manifest binds source/presentation/schema/settings and actual endpoint bytes.
- `selection.json`: six verbatim claims, source/request hashes and eight body hashes.
- `settings.json`: reviewed model metadata and explicit local resource ceilings.

**Plan bytes SHA-256:**
`97f479ce20069c57649bf981a92c3b2724a9cd9a9ba811b2e9b419f0b7ae9eed`.

## Payload, destination and budget for approval

The proposed run sends the full unpublished fictional prose and diagnostic context
to **both** `https://api.openai.com/v1/responses/input_tokens` and
`https://api.openai.com/v1/responses`. Use the existing approved application credential
`OPENAI_OH_KEY` in memory. No credential is written to source, requests, journals or
exports. No Ollama, catalog, model-list, synthetic preflight or extra recovery call
is included.

| Reservation | Frozen ceiling |
| --- | --- |
| Input-count requests | 4 total, at most one per work |
| Generation attempts | 4 total, at most one per work |
| Retries, resumes, replacements | 0 |
| Input tokens | 272,000 per generation; 1,088,000 total reserved |
| Output tokens, including reasoning | 32,000 per generation; 128,000 total reserved |
| Conservative generation estimate | $1.00 per work; $4.00 total |
| Count network deadline | 120 seconds per attempt |
| Generation network deadline | 600 seconds per attempt |
| Run dispatch window | 3,600 seconds after initial local authentication/journal creation |
| Parallel requests | 1 |
| Response-body retention bound | 1 MiB per endpoint |

The 272,000-input cap is the application's conservative pricing boundary, **not a
claim about the model's full context limit**. It explicitly replaces the previous
24,000-token/$0.60 fixture reservation before any approval or live request. At reviewed
standard rates, the reservation uses $2/M input with a 1.25 cache-write allowance and
$10/M output: $0.68 + $0.32 = $1.00. These are published-rate estimates, not actual
billing; no claim is made that token-count requests are free. Current model access
and actual provider input counts have not been queried. [Model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[pricing](https://developers.openai.com/api/docs/pricing).

The bodies are large. Resource fit is explicitly **unknown**; authored count 100
from local fixtures is not a measurement. The input-count endpoint sees the same
full input/schema/reasoning configuration before generation. [Token-count documentation](https://developers.openai.com/api/docs/guides/token-counting).

Retain `store=false`, disabled truncation, no tools, no conversation history,
no background job and the serializer's explicit standard/default service settings.
No caching discount is assumed in the reservation. Generation output includes
reasoning within the cap; reasoning text is not retained in the audit.

## Order and terminal stops

1. Validate the exact approved plan hash, implementation, all four registered
   sources, preparations and fixed live-journal location locally. No extra endpoint
   preflight. Refuse every existing live journal, including partial/interrupted ones.
2. Count N06, N07, N10, N11 in that order. **All four counts must pass before any
   generation.** Any HTTP/nonterminal/malformed/unknown/over-budget count stops the
   entire remainder immediately; unused count and generation slots stay unused.
3. Generate N06, N07, N10, N11 in the same order, one attempt each. Stop after any
   failed/refused/truncated/empty/ambiguous/malformed/wrong-model delivery, failed native
   binding, missing usage counter, input/output usage above reservation or elapsed
   deadline. Do not salvage valid slots from an invalid work.
4. Stop on source/request/code drift, unsafe content, cancellation, interruption,
   journal/fsync failure or other uncertainty. A flushed intent consumes that endpoint
   slot even when receipt/usage is unknown. Never infer that a timeout prevented
   provider processing. No retry, polling, response retrieval, fallback, budget raise,
   prompt repair, input trimming or substitute work is authorized by this plan.
5. Audit every fixed slot, including undispatched ones, and every returned claim.
   Export an interrupted journal without dispatching anything else. Missing final
   stop prevents completion eligibility. Keep actual billed cost unknown.

The transport disables redirects, environment proxies and connection retries and
uses TLS verification. Exact method/URL/body are checked before sending; durable
intent precedes transport. A cancellable async deadline covers send plus body read.
The remaining run window bounds each next network attempt. Synchronous source
validation may finish after the window, but no later request is allowed; initial
authentication and final local audit are outside this window. Cancellation does not
prove remote cancellation or zero cost.

## Frozen scoring and inspection

Primary software outcome per work: authenticated source/request identity, admitted
count, complete HTTP/model/final delivery, strict parsing and exact native binding
for **every original active claim**, followed by whole-work completion. Report each
dimension separately. A successful subset is not a successful whole work. A native
binding does not establish semantic support or adequate evidence.

For all eight fixed slots record: dispatched/not dispatched, consumed intent,
observed HTTP status, safe error chain, returned model and available response/request
IDs, final-text digest, terminal status, elapsed interval and nullable usage. Show
known generation-token subtotals with the number of unknown-usage generations.
Never substitute input counts for generation usage or assume omitted cached/reasoning
tokens are zero. Native receipts remain attached to original work and new request hashes.

Manually inspect all six returned claim judgments against their **unchanged original
declarations and work briefs**: whole-claim support, coverage of each material clause,
source/version/reference binding, adequate endpoint evidence, historical authority,
future-state availability, and explanation materiality. Use supported/contradicted/
unavailable distinctions from that scope, and record unresolved interpretation openly.
No new automated semantic gold or pooled model-quality score is introduced. The earlier
authored finals are binding fixtures, **not semantic ground truth**.

Promising deliveries may become local regressions after inspection. The smoke cannot
qualify editorial judgment, story quality, writer edits, a broader archive adapter or
the full workflow. Humans retain the feel/flow/character/story-breaking review role.

## Local qualification and commands

The separate [service](../../apps/api/open_hollywood_api/services/assessment_openai_smoke.py)
uses the existing source collector, renderer, mapper, native binder/completion and
immutable publisher. The [CLI](../../scripts/assessment_openai_smoke.py) exposes
`verify`, `audit` and explicit `run`; only `run` resolves the key or constructs real
HTTP transport. Strict [plan](../contracts/assessment-openai-four-work-smoke-1.schema.json)
and [event](../contracts/assessment-openai-smoke-event-1.schema.json) contracts are new.
Old fixture journals cannot be passed as new smoke journals. Injected qualification
cannot occupy the fixed live location or acquire a model-origin label.

Local verification (no endpoint calls):

```powershell
uv run --extra api python scripts/assessment_openai_smoke.py verify `
  --plan data/diagnostics/assessment-openai-smoke-2026-11-13/plan.json
```

**After separate approval only**, execute once:

```powershell
uv run --extra api python scripts/assessment_openai_smoke.py run `
  --plan data/diagnostics/assessment-openai-smoke-2026-11-13/plan.json `
  --journal data/diagnostics/assessment-openai-smoke-2026-11-13/live-journal `
  --approved-plan-sha256 97f479ce20069c57649bf981a92c3b2724a9cd9a9ba811b2e9b419f0b7ae9eed `
  --confirm-full-prose-openai-both-endpoints
```

Regardless of success or interruption, use read-only `audit --plan ... --journal ...
--output PATH` to derive the three-file export. Exact audit repeats reuse bytes;
partial/changed/extra exports are refused. Journal provenance is application-owned
local integrity, not a provider signature. No source artifact or user database is
written. Model observation, native completion, accounting and semantic qualification
remain distinct.

Local qualification is complete:

- **420 tests pass** in the combined relevant suite (337.03s). After the final
  audit-label correction, **all 38 smoke tests pass** (65.15s); these overlap the
  combined suite and must not be added as distinct tests. The added case verifies
  that a count-only HTTP failure is transport evidence without observed model output.
- Ruff, formatting and strict mypy pass on **268 Python files** (267 repository
  files plus one private helper). Both new runtime schemas match their typed models.
- All four actual registered works pass the final client-path rehearsal: **eight
  injected callbacks**, six unchanged authored finals, complete native binding and
  all eight fixed slots. Full intake/scope/briefs and retained fields remain intact.
  Accepted artifacts are under `verified/`; no registry/source trust override is used.
- Tests cover exact outgoing bytes/headers, fsync before send, redirect refusal,
  zero retries, approval hash/fixed path, count and delivery failures, missing usage,
  cancellation/deadline, source/plan/journal drift, missing stop, and immutable exports.
  Real HTTP transport, external sockets and SQLite are blocked in the actual-work
  rehearsal. Windows asyncio's local wakeup pipe needs execution outside the sandbox;
  regression databases are isolated fixtures, never the user database.
- Preserve **1,217 earlier sealed members**, **636 selected archive source pins**,
  **755 baseline files** outside four declared documentation edits, all fourteen
  issue bodies and posted URLs. Earlier captures and fixture contracts stay unchanged.

The preliminary local freeze/replay is retained separately after correcting the
audit label; only the plan hash above and `verified/` qualify for this approval.
`inspection-template.json` freezes the eight-slot/six-claim review form for a future
run. Private snapshots and the acceptance seal preserve final implementation and
preparation evidence. `live-journal` is absent: **zero count requests and zero
generation attempts have been used**. Only public documentation was fetched;
account access and actual input fit remain untested.

CW-007/CW-013 remain open; CW-014 unqualified. Step 19 **IN PROGRESS**, Step 20
**NOT STARTED**. No new human checkpoint, writer permission or canary run.
