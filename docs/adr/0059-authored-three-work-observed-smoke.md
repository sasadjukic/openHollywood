# ADR 0059: Authored three-work smoke and observed-delivery audit

- Status: Accepted for local implementation; live execution awaits plan approval
- Date: 2026-11-15
- Extends: ADRs 0055, 0057 and 0058

## Decision

Add a separate application service and operator CLI for the three registered authored
works. Preserve the existing authored mapping, source renderer, injected journal,
saved-review paths and production prompts. Reuse the qualified protocol serializer,
response mapping, native binding/completion and evidence renderer.

Freeze exact preparation, source identity, settings, implementation, operator gold,
metadata and a single prospective journal path in a new plan. Gold is authenticated
from the existing admission archive and is never included in either endpoint payload.
The original source scopes remain local identities; request-bound authority is derived
only for rendering. Do not manufacture saved-review provenance for authored controls.

The only live sequence is F01/F02/F03 input counts followed by F01/F02/F03 generations.
There are three count slots, three generation slots and no retry or resume. Every
count must pass before generation. Exact approval hash and explicit confirmation of
full prose/context at both endpoints are required before the CLI resolves the existing
approved application credential. Authenticate sources/gold first. Credentials exist
only in memory and the outbound authorization header, never in retained artifacts.

Use TLS verification, no environment proxy, no redirect following and zero transport
retries. Bound response reads to the shared response limit. Apply async deadlines
of 120 seconds per count, 600 seconds per generation and 2,700 seconds for dispatch.
Recheck source/request/gold/metadata/implementation before and after durable intent.
The request is consumed once intent is flushed. Cancellation or a write/validation
failure leaves an inspectable prefix and forbids recovery. No trimming or substitution.

## Origins and terminal audit

New headers keep `source_origin=authored_diagnostic` separate from
`delivery_origin=injected_transport_fixture|observed_openai_transport`. The injected
entry point cannot occupy or overlap the fixed live journal. The observed path is
reachable only through the approved real-transport entry point; tests replace its
transport constructor explicitly. Such tests remain local protocol evidence.

Audit validates the complete hash chain, all six fixed slots and every terminal
mapping again. Retain HTTP status, available raw-body digest, mapped error chain,
nullable usage, elapsed time and allowlisted request ID. Unknown usage is not zero;
known excessive usage is a separate accounting hold. Billing remains unknown.
Do not carry fixture-only terminal discriminators into the observed wrapper.

Completion eligibility requires a closed complete journal, all three native works
complete and bound, no pending slot and no accounting hold. Every work gets that
same overall eligibility; a successful subset cannot qualify the smoke. Delivery
eligibility is not semantic approval. Full sources and failed/pending results remain
inspectable. The manifest-last read-only export has seventeen members, including
gold, metadata and separate evidence views. Neither qualification nor audit may
occupy the prospective live journal or overwrite source/preparation evidence.

## Limits

Local tests use injected transport, synthetic credentials and blocked external network
access. They do not verify account availability or provider behavior. A local journal
is application-owned evidence, not provider-signed attestation. Authored controls and
gold are not independent human judgments or natural critic-performance samples.

This is a factual-assessment smoke, with manual whole-claim and evidence inspection
after delivery. It changes no production prompt, graph, persistence schema, dependency,
UI, writer permission or human checkpoint. Live calls stay paused pending approval;
the canary stays on hold.
