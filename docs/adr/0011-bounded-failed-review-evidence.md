# ADR 0011: Bounded evidence for rejected production reviews

- Status: Accepted
- Date: 2026-09-12

## Context

The v29 Cloud canary preserved failure layers, safe validation diagnostics,
response hashes and lengths, but not the rejected critic finding. Investigation
could not recover the subject, evidence handles or explanation for failed
OH-V01-009 reviews. The shared viewpoint error was also misinterpreted:
it covers both an unassigned viewpoint and a finding about the assigned character.

The user authorized improving failure evidence first, without increasing prompt
length, retries or limits, or implementing the other proposed production changes.

## Decision

On a failed structured production review, retain an additive, versioned
AgentInvocation.request_settings.review_failure_evidence envelope. This applies
to critique, continuity and continuity adjudication, not writer prose or transport
failures without a response.

The envelope is explicitly unvalidated_review_response, with
manuscript_defect_established set to false. It records:

- Exact input artifact-version IDs and the current candidate version.
- Scene/POV assignment, assignment origin where available, and revision number.
- Allowlisted attempted POV, assignment, craft, continuity, requirement-coverage,
  recheck and adjudication fields: selected subject, assessment, proposed repair
  and evidence/claim handles.
- Bounded selected evidence resolved only against the exact request catalogs.
  Unknown or stale handles remain unresolved. A catalog match is not validation
  of the finding's semantic correctness.
- Redacted excerpt SHA-256, full redacted character count and truncation marker,
  bound to the exact draft version.
- A diagnostic-only distinction between no_assigned_viewpoint and
  subject_is_assigned_character for the existing shared validation error.

Keep the existing failure layer, validation issues, error code/message and
response hash/length unchanged. The new envelope is never copied into retry
context, prompts, accepted artifacts, graph checkpoints or story canon.
It does not change rejection, recovery, adjudication eligibility or acceptance.

Capture is best effort. Malformed JSON, non-object output, excessive response
size and capture errors have explicit availability statuses; the original
production failure remains authoritative. Raw response bodies, arbitrary unknown
fields, top-level prose and general reviewer commentary are not stored.

## Bounds and secret handling

Redact complete strings before truncation. Capture at most eight entries per
section, eight references per field, 24 resolved-reference observations, 1,000
characters per text value, and a shared 16,000-character text budget. Serialized
JSON also includes bounded structural metadata and reference copies; the text
budget is not a serialized-byte limit. Parse at most 262,144 response characters.
Record truncation explicitly. Existing ORM and database-export secret guards
remain active. This is an allowlisted diagnostic exception, not raw-response
logging; errors and checkpoints still do not expose provider response bodies.

## Compatibility

No SQL migration is needed: this is an optional, schema-versioned observation
inside the existing JSON request-settings column, as with prior invocation
audits. No API/domain artifact schema or generated client contract changes.
Older invocations remain valid and are not backfilled. Missing failed responses
from the v29 canary cannot be reconstructed by this change.

Prompt v29, graph v7, provider requests, response schemas, model settings, budgets,
retry counts, revision limits and manuscript decisions remain unchanged.
Future evidence should identify the new runtime commit even though the model
contract versions are unchanged. Source canary archives stay immutable.

## Verification

Offline boundary tests exercise both POV causes, valid and unresolved evidence
references, continuity/recheck fields, malformed/non-object/oversized responses,
redaction before truncation, and capture fallback. Real migrated SQLite workflow
tests cover failed critic and continuity calls, automatic recovery versus terminal
failure at the existing limit, artifact isolation, identical retry context,
secret-safe persistence/export and successful replay.

These are observability checks, not evidence of improved model judgment or
production completion. Assignment-aware schemas, repair acceptance criteria,
critic adjudication and continuity policy changes remain separate future work.
