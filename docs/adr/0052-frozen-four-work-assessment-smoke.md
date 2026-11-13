# ADR 0052: Frozen four-work assessment smoke transport

- Status: Accepted for local qualification; live plan awaits approval
- Date: 2026-11-13
- Extends: ADRs 0049–0051

## Decision

Add a separate, explicit four-work smoke service and operator CLI. Keep existing
rehearsal contracts fixture-only and production execution unchanged. Freeze original
intake work, exact prepared requests and implementation identity in a prospective
plan. Plan bytes, source authentication and a fixed one-shot journal govern dispatch.

Admit only N06/N07/N10/N11 in their frozen order, one original batch each. First count
all four; generate only after every count fits. At most four count and four generation
attempts, no retries or resume. A failed count stops the remainder. Freeze 272,000
input/32,000 output tokens and $1 conservative generation estimate per work, without
changing the previous diagnostic prompt, schema or endpoint bodies. The input limit
is application policy; actual resource fit is unknown until an approved count.

Use a single asynchronous HTTP client, TLS verification, disabled redirects,
environment proxy use and transport retries. Resolve the existing application key
only on explicit live execution with the exact approved plan hash and payload/destination
confirmation. No catalog/preflight endpoint, default live action, alternative
destination, caller-supplied live transport or hidden recovery is exposed.

Write/fsync intent before transport; consume uncertain interrupted slots. Freeze
per-endpoint network deadlines and a run dispatch window. Cancel local awaiting
without asserting remote cancellation or zero usage. Stop on unsafe/failed/invalid
delivery, failed binding, missing usage, budget overrun or source/journal drift.

Derive read-only terminal exports with every fixed slot, original work completion,
nullable usage and explicit origin. The audit shares pure native binding/completion
with the rehearsal; it does not copy or promote old fixture receipts. Local transport
qualification uses mock responses and a separate journal location. Live origin is
assigned only by the dedicated application execution path. Journal integrity is not
a provider signature. Keep model output, transport evidence, semantic correctness
and writer permission separate; actual billed cost remains unknown.

## Verification and approval boundary

Qualify the real HTTP client configuration and request/response path with injected
fixtures, then verify the exact four saved works. Block real provider transport and
external network access during qualification. No database, workflow checkpoint,
production prompt/profile/gate, archive eligibility or writer permission changes.

The [frozen plan](../handoffs/assessment-openai-four-work-smoke-plan-2026-11-13.md)
records exact approval identity, payload, destinations, scoring, limitations and stops.
Preparation is not authorization to execute that plan.
