# Full-context assessment workload: DeepSeek and Luna approval plan

Date: **2026-11-02**. **FROZEN AND VERIFIED LOCALLY; LIVE APPROVAL PENDING.**
Two independent comparisons, **30 attempts each / 60 maximum combined**.
No generation or story-bearing token-count request has been sent during preparation.
Production **prompt 61 / graph 9 / fulfillment policy 1** remains unchanged.
The full workflow canary remains **ON HOLD**.

The [tracked integration record](assessment-work-integration-2026-11-02.md) and
[ADR 0041](../adr/0041-read-only-assessment-work.md) describe the read-only component.
This plan follows the [headroom audit](reviewer-workload-headroom-audit-2026-11-02.md)
and extends its proposed comparison to the user's newly added OpenAI provider.

## Approval scope

| Independent comparison | Model and effective reasoning | Destination | Maximum attempts |
| --- | --- | --- | ---: |
| D: Ollama/DeepSeek | `deepseek-v4.1-flash:cloud`, `think: "high"` | Ollama Cloud through local `http://127.0.0.1:11434/api/chat` | 30 |
| L: OpenAI/Luna | `gpt-5.6-luna`, `reasoning.effort: "high"` | `https://api.openai.com/v1/responses`, preceded by `/v1/responses/input_tokens` | 30 |

Approval would authorize the **full unpublished fictional prose and planning
context, full saved critic reports, complete source registry, all original selected
statements and the active assessment selections** to the selected destination.
The OpenAI token-count endpoint receives the same model/input/schema/reasoning
payload before generation; it is not used on story data before approval.

Each provider requires its own plan-bound approval record. The user may approve
both together or either separately. There is no cross-provider fallback, extra
connectivity generation, retry, replacement model or transfer of unused slots.
The twenty retired MA/WB slots and all other historical budgets remain closed.

Private freeze:
`data/diagnostics/reviewer-assessment-workload-v61-2026-11-02/plan.json`.
Plan SHA-256:
`2b38d6547dd5304ef2bc12e9b9fe2209fbdb915ba953cad660d29473137c2702`.
The freeze binds **24 preparation files and 3,153 current source fingerprints**,
with the sixteen historical runtime changes recorded separately.
Exact requests, schedules, cases/work records, selected statements, gold, adequate
evidence criteria, settings, budgets, stop policies, implementation and runtime
fingerprints are bound by this freeze. Approval is deliberately absent.

## Question and intervention

Does assessing **at most three whole selected statements per response**, while
retaining the full context, improve complete-case delivery or resource use without
losing grounded judgments?

**MA control:** assess all originally selected statements in one response.
The eight DeepSeek MA wire requests are byte-for-byte equivalent as JSON values
to the saved controls, including the two previously unrun fresh families.
Luna uses the same control messages through its own native provider adapter.

**NA treatment:** keep the original system instructions, every complete source,
the full report and field inventory, source registry and output contract. In the
existing selection message, `admitted_spans` contains only the active whole
statements; `original_admitted_spans_context_only` retains the entire original
selection list. The unchanged system instruction already says to assess exactly
the supplied admitted pairs. No gold, inspected evidence or expected label is added.

Existing authored links keep H1/CP Q003–Q004 and H2/CP Q003–Q004 together. Whole
compound selected statements remain intact. No semantic group is discovered by
the application, and component labels cannot substitute for an explicit assessment
of the original relation.

The per-call token/time limits stay the same, but NA uses two or three calls per
case, repeating the context and increasing its aggregate possible reservation.
This is a **workload strategy comparison**, not equal total reasoning allowance
per case or proof that decomposition alone causes a gain. Smaller responses can
cost more in total. Evaluate resources across every batch needed for a case.

## Frozen cases and order

| Family | Source | Statements per order | NA batches per order | Purpose |
| --- | --- | ---: | ---: | --- |
| H1 | Elena embedded match | 7 | 3 | Decision/endpoint separation, date-realization evidence, private-flourish inference |
| H2 | Elara entry | 5 | 2 | Earlier fulfillment versus entry overrun, planned versus observed scene timing |
| W1 | The Unfired Plate | 8 | 3 | Fresh transfer of decision, boundary, later-test and source-availability contrasts |
| W2 | The Last Cable Ledger | 8 | 3 | Fresh transfer with distinct scene material and the same protected semantic distinctions |

PC and CP retain the two original source presentation orders. W1/W2 were prepared
previously but received no inference in the stopped MA/WB comparison. They are
fresh to live testing here, not unseen by the preparer or independent of their
authored diagnostic design.

Both providers use this exact case/order sequence:

1. W1/PC — MA first, then all NA batches.
2. H1/CP — all NA batches first, then MA.
3. W2/CP — MA first, then all NA batches.
4. H2/PC — all NA batches first, then MA.
5. H1/PC — MA first, then all NA batches.
6. W1/CP — all NA batches first, then MA.
7. H2/CP — MA first, then all NA batches.
8. W2/PC — all NA batches first, then MA.

Thus each provider has **eight MA controls and 22 NA batches**, covering **56
selected judgments per condition**: 38 supported, fourteen unsupported and four
uncertain under the frozen source contract. Thirty-two judgments per condition
are in the fresh families. Across both providers there are **224 fixed judgment
slots**. Unavailable results remain in those denominators. Reordered presentations
are not independent scene families; there is no repeatability qualification here.

## Provider controls and readiness

Metadata preflight confirms **Ollama 0.40.13**, unchanged selected DeepSeek metadata
and account-visible **`gpt-5.6-luna`**. The existing Windows User `OPENAI_OH_KEY` is
approved for reuse and stays outside project files. No active model profile changes.

DeepSeek retains temperature 0.2, top-p 0.95, seed 20261022, 40,000 requested context,
high thinking, non-streaming and the historical prompt-only schema. Luna uses high
reasoning, the native strict JSON schema, standard service tier, `store=false`,
`background=false`, `stream=false` and disabled input truncation. Its adapter omits
seed, temperature and top-p for this reasoning mode and records those omissions.
Requested seed provenance does not imply an effective OpenAI seed.

OpenAI's reviewed Luna page documents high reasoning, Responses/structured-output
support and the rates used below. Native schema enforcement can still leave
semantic mistakes, refusals and incomplete responses. This is why local domain
validation and the terminal tests remain necessary.
[Luna model record](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses),
[input-token counting](https://developers.openai.com/api/docs/guides/token-counting).

The comparison within each provider uses matched settings and the same schema
mechanism. Cross-provider differences also include the model, service, schema
enforcement, effective sampling and reasoning implementation. Report them
descriptively; do not claim a pure model ranking or provider-cause finding.
Account listing and an alias/model digest do not prove unchanged remote weights
or guarantee billing/permission availability on a future generation.

## Budgets and accounting

| Limit | Per attempt, either provider | Per provider | Combined ceiling |
| --- | ---: | ---: | ---: |
| Reserved input tokens | 24,000 | 720,000 | 1,440,000 |
| Reserved generated tokens, including reasoning | 16,000 | 480,000 | 960,000 |
| Active generation/count time | 600 seconds | 18,000 seconds | 36,000 seconds |
| Attempts, reserved before transport | 1 per scheduled cell | 30 | 60 |
| Planning dollar allowance | $0.03 | $0.90 | $1.80 |

The DeepSeek uncached reference reservation is **$0.792** at the archived
$0.30 input / $1.20 output per million rates. It is a historical planning reference,
not a verified current Ollama invoice. Luna's conservative reservation is
**$0.756**, using $0.20 input × 1.25 cache-write allowance and $1.20 output per
million. The $0.02 cached-input rate is recorded in its provider metadata; the
common comparison reference does not assume a cache discount. Actual billed cost
is unknown and is never labeled verified by a published-rate calculation.

The OpenAI adapter counts input before generation and refuses an over-budget
request. A failed count or pre-generation check consumes that scheduled attempt;
it does not create a replacement slot. DeepSeek validates reported usage against
the envelope, so a provider's already-incurred overage cannot be undone. The
dollar allowance is application planning/reservation, not a guaranteed provider
billing cap.

Non-generating HTTP operations are separate from the 60-attempt ceiling: at most
30 story-bearing OpenAI count requests, up to 30 OpenAI catalog checks, and up to
120 local Ollama metadata requests for full execution. They have no generation
allowance. Preparation used only model discovery/metadata; no count request with
story data ran. The first actual scheduled request is the inference readiness
check, so there are no hidden smoke calls.

Retain reported input, total generated, cached and reasoning counters when
available, plus active time and conservative estimates. Unknown counters remain
unknown. Never infer a reasoning/final split from character counts or add reasoning
again to total generation. Raw OpenAI reasoning is not retained; final messages,
usage, safe metadata and response fingerprints are preserved. DeepSeek's captured
thinking stays opaque and is excluded from scoring.

## Validation and scoring

Each returned assessment must identify an exact active field/quote pair once,
use an allowed support label and valid distinct source references, and satisfy
the unchanged reason/quotation/evidence bounds. Missing/extra selections,
duplicate keys, forbidden fields, blank reasons and invalid references fail
delivery. Invalid or partial finals earn no semantic credit and are not repaired.

The frozen gold preserves each unit's original whole-field scope, support label,
rationale and adequate-evidence criterion. Example references illustrate sufficient
evidence; other genuinely adequate source evidence is allowed. The application
checks binding. Source inspection judges support of the whole proposition and its
reason, with separate **grounded / citation-only / semantic / unavailable** outcomes.
Correct labels cannot rescue unsupported reasons, and exact quotation identity
cannot establish an inference. Keep the private-flourish factual claim distinct
from a defensible editorial judgment about suspense. Plans can support claims
about planned events without being observed future prose.

Inspect shuffled final reports with provider/arm identifiers withheld where
practical, then seal notes before decoding. Familiar content and output shape can
reveal the treatment, so this remains a partially masked assistant factual audit,
not blind human preference review. Do not use thinking text as evidence.

The tracked component reports complete delivery only after every expected batch
arrives validly against the same work/request scope. Keep all individual observations,
but do not label a partial case successful. Assess the two cross-selection relation
contexts separately in each condition/provider; their members' labels cannot earn
whole-relation credit automatically.

Frozen interpretation:

- **Workload feasibility:** all eight NA cases complete, no paired grounded,
  semantic or contextual-relation loss, and all 32 fresh NA judgments grounded.
  Incomplete paired coverage cannot establish the no-loss condition.
- **Observed delivery recovery:** a failed full control may be contrasted only
  with an already completed NA case. If the terminal stop prevents that pair,
  report unavailable. Any terminal stop still makes the overall comparison
  incomplete and prevents qualification.
- **Resource improvement:** require all eight paired cases complete, at least
  20% median reduction in total generated tokens per complete NA case, no increase
  in aggregate active time or uncached reference estimate, and no grounded/semantic
  loss. Publish all input/output totals and per-case costs, including every batch.
- **No demonstrated gain:** complete delivery without a control failure or the
  resource screen supports feasibility only. Do not call it a recovery. Semantic
  improvement, if observed, is recorded separately from the workload hypothesis.

None of these screens qualifies ordinary production extraction, edit necessity,
writer preservation or better stories. The tracked completion component always
leaves those authorities unassigned.

## Stops, approval and verification

The first invalid, empty, truncated, refused or failed transport response stops
**both arms of that provider's comparison** and retires its remaining attempts.
There are no semantic early stops, retries, patched outputs or larger limits.
The other provider can run within its own separately approved budget. Shared
source/request/implementation drift or a secret-boundary failure stops both.

Metadata drift, quota/authentication errors, input-count failures and unsupported
settings stop before another attempt. A reservation without a sealed receipt is
an unresolved consumed attempt, never a free retry. Resume only at a fully sealed
valid cell and completed post-delivery metadata boundary; a terminal stop cannot
be resumed through the same approval. A process lock prevents concurrent runners.

The verification checks actual adapter wires for all sixty requests using mocks,
full-context and claim preservation, the native OpenAI schema, terminal accounting,
approval binding and saved-regression replay. The tracked component has **38 tests**;
the private harness adds **105 offline tests**, including all sixty request wires
and sixteen historical captures. Repository Ruff/format
and strict mypy pass across **222 files**, and the full repository suite passes
**1,278 tests**. Final focused verification passes **143 tests**; the 38 tracked
tests overlap the full suite, yielding **1,383 unique tests overall**. Verification
and the freeze fingerprint are recorded
in the private preparation and authoritative tracker.

**No live approval is inferred from key reuse, metadata access, preparation or
this document.** The user can now approve D, L or both with the stated payload,
destinations and limits. Full workflow canary remains **ON HOLD**.
