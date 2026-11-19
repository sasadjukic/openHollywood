# ADR 0064: Read-only artifact provenance inspector

- Status: Accepted; bounded local integration
- Date: 2026-11-19
- Extends: ADRs 0005, 0062 and 0063

## Decision

Expose the qualified registered-workspace lookup through a compact, read-only API
projection and the existing artifact inspector. The API accepts the explicit project,
logical artifact, immutable version, canonical content hash and review/draft role.
Its source path comes from the application-owned workspace database, never request
parameters. An injected workspace needs an explicitly injected provenance service;
the application does not guess the default database for it.

Keep the existing source authentication, physical file registration, current-row
closure and read-only transaction checks. No latest-version substitution, registration
repair, caller trust override or new source enrollment is introduced. Revalidate the
typed lookup result, request digest, workspace, selection and historical relationship
before projecting an allowlist of identity and status fields. Return no raw prose,
request text, hidden reasoning, filesystem path or physical device/file identifier.

`GET /api/v1/artifact-versions/{artifact_version_id}/provenance` returns
`artifact-provenance-view-1` with `Cache-Control: no-store`. Missing registration,
unavailable/changed source, missing/mismatched current records, wrong selection and
ambiguous association produce explicit unavailable states with no relationship.
Sanitize source and secret exceptions; never echo exception text into the view.

Generate the TypeScript endpoint and types from FastAPI OpenAPI. Bind the frontend
query, component lifetime and displayed response to all five selection fields. Abort
superseded requests, refuse mismatched artifact detail or response identity, and hide
cached success during revalidation or after an error. Recheck on mount without polling
or automatic retries; provide a local read-only retry for unavailable results.

## Meaning and boundaries

Display verified review/draft identity separately from assessment status. The six
registered historical reviews still have unsupported assessment contracts and no
captured native assessment delivery. Semantic support, evidence adequacy, editorial
effect, edit necessity and craft remain unassessed. Assessment attachment and writer
permission remain false. Diagnostic consumer completions are not attached.

Show the original relationship for an older selected version, with lookup-time head
labels separate from that immutable identity. Source details are optional literal text.
The view belongs to critique and scene-draft artifacts; it adds no manuscript editor,
workflow action or mandatory human checkpoint. Ensure the mobile drawer is opaque and
long identifiers wrap without horizontal overflow.

The registration remains local, archive-dependent and nonportable. A restore,
replacement or relocation needs requalification. This UI verifies the relationship
at the time of its local read; it is neither continuous source monitoring nor a
semantic/story-quality verdict. No persisted schema or production prompt changes.

See the [implementation and verification report](../handoffs/assessment-provenance-inspector-2026-11-19.md).
Live calls remain paused and the full workflow canary remains on hold.
