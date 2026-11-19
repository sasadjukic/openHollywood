# ADR 0061: Registered read-only assessment consumer

- Status: Accepted; bounded local implementation
- Date: 2026-11-19
- Extends: ADRs 0056 and 0060

## Decision

Add an application consumer exporter and operator CLI for exactly two complete
publications: `authored-smoke-2026-11-15` and `compact-smoke-2026-11-14`. Accept a
registration name and destination only. Pin each original publication manifest,
member inventory and work inventory. Require its supported publisher to reauthenticate
the upstream sources, requests, closed journal and audit through exact reuse.
Do not accept arbitrary source paths, caller receipts, trust overrides or work subsets.

Refuse the entire export on any missing, changed, failed, incomplete or accounting-held
input. Do not repair the reference publication. The earlier private rehearsal's fault
projections are test evidence, not an alternative admission API. A future display of
failed deliveries would require a separately qualified source contract.

Derive typed consumer records using existing native source, scope, result and completion
records. Rebind the raw result and verify whole-work delivery and all endpoint slots.
Retain every original field, including held and unselected fields. Distinguish a
delivered uncertain judgment from no judgment. Namespaced field identity includes the
registration, publication digest, work digest, request digest, field pointer and unit.

Keep original claims, selection findings, authored interpretations, material components,
source roles, work briefs, model judgments and literal citations separate. An exact
complete-field citation is not proof of material coverage. Original authored authority
and separately request-bound authority remain available; probe sources get no fabricated
authority record. All semantic, evidence-adequacy, editorial, edit-necessity and craft
status stays unassessed. Writer permission is false; no whole-review verdict is derived.

## Publication

Copy every original publication member byte-exact, preserving its filename except
`manifest.json`, retained as `source-manifest.json`. This keeps native relative links
working. Add a JSON record and literal Markdown view per work, an index and a final
consumer manifest. Exports contain 51 authored or 37 probe files. Full envelopes,
requests, context, source receipts and endpoint accounting remain inspectable.

Use the existing bounded reads, secret guard, link/junction checks, bidirectional
destination protection, exclusive writes, final-manifest marker and exact-byte reuse.
Protect all pinned upstream source members as well as the original publication.
Recheck source membership/content and implementation after authentication/rendering,
before writes/finalization and on reuse. Retain partial/conflicting output without
repair or overwrite. There is no new fsync/durability claim beyond existing storage.

Generated navigation uses fixed work names. Model text, field names, reasons and
quotes appear as literal JSON within adequately long fences. The original native
views are preserved unchanged. This is an operator file export, not an HTML/UI route.

## Limits and next boundary

Source origin remains authored diagnostic or registered diagnostic probe; delivery
origin remains observed transport. Local journal binding is not provider-signed
attestation. All four token counters are retained and actual billed cost stays unknown.
`live_calls=0` describes export, not the historical requests in retained evidence.

Canonical review and production artifact-version IDs remain null and association is
explicitly unqualified. No database is opened to guess one. Before production-inspector
integration, separately qualify exact immutable review/artifact-version association
with content hashes and mismatch/missing/ambiguous controls.

No new transport, route, dependency, database schema, migration, prompt, workflow gate,
writer behavior or mandatory human checkpoint is introduced. Existing engine evaluation
modules and frozen publisher implementations remain unchanged. Quality work must still
evaluate feel, flow, character and story-breaking effects separately from factual
delivery and literal citation checks.

See the [implementation and verification report](../handoffs/assessment-consumer-export-2026-11-19.md).
Live calls remain paused and the full workflow canary remains on hold.
