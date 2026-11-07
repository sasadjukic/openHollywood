# ADR 0045: Read-only historical authority and claim evidence obligations

- Status: Accepted
- Date: 2026-11-07
- Extends: ADRs 0041–0044; preserves their diagnostic-only provenance boundaries.

## Context

The historical-authority audit verified five saved quotations against their old
drafts but distinguished this from critic interpretation, historical violation
and requested repair. R1 still has an unresolved event/violation versus reported
allegation reading. R3 Q003's date correction was scored against an additional
realization requirement, although realization belongs to other selected claims.
The user authorized a read-only integration of these distinctions and per-claim
evidence obligations. Live calls and production promotion remain paused.

## Decision

Add the pure `evaluations.assessment_authority` component beside the existing
work, result, scope and brief modules. Its preview consumes those existing
contracts directly. It has no provider, filesystem, database, workflow, prompt,
CLI or production dispatch operation. Existing renderers and callers are unchanged.

Extend the authored scope vocabulary additively with historical attribution,
event, violation and requested-repair predicates, and historical critic assertion,
excerpt, assignment and requested-repair source roles. Existing serialized fields
and defaults do not change. Centralize the same required-role checks for both
scope declarations and component obligations. Historical violation requires
historical excerpt and historical assignment; a current assignment or requested
repair does not substitute for that role. Roles are still authored classifications.

`assessment-authority-1` binds to the exact work, active request fingerprint and
complete scope-declaration fingerprint. It records author and upstream origin
fingerprint, optional historical bodies, exact-copy bindings, and authored
claim-specific evidence obligations. It remains `model_input: false` and cannot
grant writer permission. No expected answer or semantic-result fields are accepted.

Each obligation identifies an existing selected unit and a zero-based material
component index in its exact bound declaration. It supplies a requirement,
declared predicates, required source roles and illustrative evidence references.
Reject duplicate/foreign units, components, predicates, roles and references,
including inactive units. Missing component obligations remain findings; do not
fill them in. The aggregate obligation predicates must match the declared claim
predicates, and each obligation must use the roles required by its predicates.
References must locate declared sources for those roles. They are examples, not
a whitelist for later model citations or a semantic coverage score.

Historical proof bodies are supplied separately from the unchanged work/context.
Each binding joins an existing registry section to a specified historical
document/version/JSON-text hash, JSON pointer, field hash, Unicode code-point
offsets and exact quotation. Recompute field lookup and copying; reject changed
hashes, versions, pointers, text, offsets or conflicting document identities.
Repeated text is resolved by its explicit occurrence, not a first-match search.
An absent historical body yields `unverified_missing_source`, not invented proof.
Every supplied body and binding is validated, even if not used by an active unit.

The binding's `exact_copy` means **verified against the supplied body**. It does
not prove the body is authentic, the chronology is correct, the critic's target
link is valid, the passage entails an event, or an edit is necessary. The supplying
adapter authenticates archive membership, source/critique lineage and visibility;
hashes are not signatures. The preview explicitly keeps external provenance
authentication and model visibility verification false. An origin fingerprint
records the caller's provenance claim without certifying it.

Excerpt and full-body visibility are separate, request-bound adapter declarations
(`shown`, `not_shown`, `unknown`) with a stated basis. A locally recovered body
does not become historically visible context. Missing/unknown visibility of a
declared historical excerpt remains a scope-review finding. The component does
not guess visibility from substring searches in serialized messages.

`preview_assessment_authority` recomputes the existing work-brief preview and all
new checks. It propagates unresolved scope, missing declarations/briefs and missing
evidence obligations. It never repairs or rewrites a selected field. A structurally
consistent author can still assign the wrong meaning, predicate, role or free-text
requirement; semantic interpretation and evidence adequacy remain unverified.

`render_assessment_authority` shows the full unchanged work, complete scope/brief
preview, separate proof bodies, computed bindings and per-claim obligations as
literal JSON in dynamic fences. An optional native result must pass the unchanged
receipt/result boundary. Historical quote-witness results are not converted into
native receipts. Returned records are revalidated snapshots, detached from caller
containers and unchecked Pydantic construction.

Copying, declared consistency and completion leave factual support, obligation
existence, fulfillment, edit necessity and craft unassessed. Whole-relation credit
and writer authorization remain false. Exporting callers retain responsibility
for credential guards. No new mandatory human checkpoint is introduced.

## Qualification and limits

Tracked authored tests distinguish date relation from realization, requested
repair from assignment authority, and source occurrence from historical violation.
They exercise missing proof, unresolved visibility, inactive obligations, stale
identities, malformed/extra fields, literal full-context rendering and native
completion without semantic promotion. A deliberately wrong free-text requirement
can pass structural checks while remaining explicitly unverified.

The private bridge authenticates the preceding sealed audit and renders all 32
saved works. It authors only five unique whole fields: R1 Q003, R3 Q002/Q003/Q004,
and R4 Q003. The 40 repeated declarations produce 32 structurally consistent
findings and eight unresolved R1 findings. The remaining 88 units stay visibly
undeclared. All 40 repeated historical bindings (five unique quotations) match.
This is integration evidence, not model rescoring or natural-error qualification.

Original gold, scores, requests and receipts are unchanged. No persistence,
migration, dependency, API/client schema, exporter eligibility, production
prompt/profile/graph/gate or writer route changes. See the
[implementation record](../handoffs/assessment-authority-integration-2026-11-07.md).
