# ADR 0051: Intake-bound OpenAI assessment rehearsal

- Status: Accepted for local preparation, injected capture and read-only audit
- Date: 2026-11-13
- Extends: ADRs 0049 and 0050

## Context

The OpenAI wire mapper is qualified locally against six saved deliveries and
authored failures. Current intake works have different identities, scopes and
batches. Their original critic messages are source context, not a suitable new
assessment instruction. A real-format rehearsal must preserve those identities
without relabeling historical or authored output as a new model delivery.

## Decision

Add a separately versioned OpenAI preparation/capture/audit path. Preserve the
existing synthetic fixture contracts and native assessment identity.

1. Render an explicit diagnostic presentation for each original batch. Include
   the full original work, source documents, original messages, evidence registry,
   scope declarations, work briefs and all intake dispositions. Unselected and held
   material remains context. Historical `model_input` flags describe original
   visibility; they do not hide fields in this new presentation. Operator provenance
   does not become story authority. The instruction targets the current active
   whole claims, not the historical fixed six-claim control.
2. Keep the original mapper entry point's original-message check. A separate
   intake entry point regenerates the new presentation while retaining the original
   native work and batch. No original message or scope is replaced in that work.
3. Freeze source pins, presentation, explicit settings, exact count/generation
   endpoints and bodies, implementation identity, unique attempts and ordered
   whole-work coverage. Allow one count and one generation callback per batch,
   zero retries, and `live_authorized: false`. Hash the request payload without its
   wrapper; derive the wire mapping's native request identity afterward to avoid
   circular hashes.
4. Check actual request bytes and write/fsync a chained intent before each mock
   callback. Revalidate the source and preparation at every dispatch boundary.
   Preserve observed HTTP status, safe mapped response, original response digest,
   nullable usage and explicit interrupted/failed outcomes. Raw response bytes
   are not retained merely because their digest is recorded.
5. Reconstruct native binding and whole-work completion from the journal. Refuse
   capture into any existing journal, automatic retries, repaired journal prefixes,
   caller origin promotion and successful-subset publication. Audit interrupted
   prefixes without dispatch; missing final stop prevents completion eligibility.
6. Require known input, output, reasoning and cached token counts before another
   batch. A final batch can bind while retaining an accounting hold. Count estimates
   are not generation usage; authored usage is not billing. Actual billed cost stays
   unknown. The local time ceiling covers cumulative observed transport intervals,
   not source validation or preemption of a callback already in progress.

Reuse registered source collection, strict native binding, completion and immutable
publication. Admit only injected mock transport and fixture origin. Do not add a
live client, credential access, model-origin receipt, API/database route, writer
permission or human workflow checkpoint.

## Consequences

Four current works can exercise actual OpenAI-format requests and failure accounting
locally. Exact preparation/audit repeats reuse existing bytes; evidence remains
authored, and semantic correctness remains unassessed. Production prompts, profiles,
graph, gates and the old fixture path remain unchanged.

The complete packets are large. Authored fixture input counts do not demonstrate
context fit. A future smoke plan must review the exact presentation and resource
ceilings, qualify the real transport/observed-origin boundary locally, and obtain
approval before any story-bearing endpoint call. A failed or over-budget count
must stop generation; do not silently trim input or increase the frozen budget.

See the [implementation report](../handoffs/assessment-openai-integration-2026-11-13.md).
