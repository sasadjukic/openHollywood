# ADR 0031: Preserve critic classification during structural repair

- Status: Accepted
- Date: 2026-10-10
- Amends: ADR 0029's retry projection and ADR 0030's comparison repair.

## Context

The v45 unchanged-draft control first selected `assignment:outcome` for its generic
tension complaint, correctly referencing a reported hard finding, but returned
its comparison as a string. Its retry selected null and claimed independent
craft. Supplying the missing comparison references alone would have allowed a
third repair target. A structural correction had become an untracked change of
classification. This observation does not establish that the first judgment was
semantically correct.

## Decision

Production contract v46 / graph v9 uses critic retry policy 13. After rejection,
the application may retain a structurally valid classification alongside the
existing precise comparison and historical-link diagnostics. Capture requires:

- A valid generic issue core and one to three exact current evidence handles.
- An explicit null choice, or an applicable reference to a currently validated
  hard assignment finding. Missing, malformed and unreported references do not
  qualify. A malformed comparison does not invalidate a separate reference choice.
- Bounded metadata with no detected secret in the category. Rejected allegation,
  recommendation and comparison prose are never replayed.

The compact record binds to both the exact candidate and the task fingerprint,
which includes input artifact versions, prompt version, model profile and seed.
The retry packet explains which choices to preserve and how to repair their
comparison structure. Preservation records are not error focus locations and do
not establish manuscript defects.

Runtime validation compares classification multisets grouped by exact category,
severity and evidence set. This handles reordered issues and evidence without
using array positions as identity. When multiple complaints share all three
fields, all their classification counts are retained together; they are not
semantically merged. A changed reference, missing complaint, duplicate count,
renamed category, changed severity or changed evidence fails the retry. The
application does not silently rewrite the response to restore a choice.

Normal current-finding, comparison and original-repair validation still applies.
For example, removing a retained reference's target does not make the reference
valid or cause the application to recreate that finding. A failed retry cannot
replace the retention contract with its rejected choice. A fresh review or a
different draft has no retention contract. Genuine reconsideration belongs in a
fresh assessment, not an untracked format-only retry.

The existing limits remain: at most 12 diagnostic records, each at most 500
serialized characters. Capture inspects at most 64 issues; categories are bounded
to 80 characters. An oversized group, invalid member, stale record or unsupported
hint is omitted rather than partially retained. Existing errors take priority
within the diagnostic limit. Thus bounded retention is conservative, not a claim
that every possible review is fully preserved.

Capture covers materialization errors and later domain/assignment validation
failures in production. Initial request messages and output schemas are unchanged.
No new wire field, canonical field, persistence migration, role, dependency,
writer instruction or inference allowance is introduced.

## Qualification

Metadata signatures are structural slots, not a semantic identity test. A model
could preserve metadata while changing the allegation's meaning; the application
does not claim to detect that. Retaining null likewise does not prove independence.

Local tests cover both classifications and delivery modes, drift rejection,
reordering, repeated metadata, invalid and bounded capture, stale inputs,
disappearing targets, original repair IDs and a durable retry after domain
validation fails. Saved v45 evidence is replayed locally. Three approved isolated
retries preserved classification and repaired the comparison and boundary links,
but all failed after introducing a historical link to the now-consolidated generic
issue. Labeled offline copies removing only that ineligible link recover the same
two original repairs without new targets; the actual responses remain failed.
No full-story improvement or reviewer reliability is established. Step 19 remains
IN PROGRESS. See the [v46 report](../benchmark_reports/retry-classification-v46-2026-10-10.md).
