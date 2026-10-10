# ADR 0028: Constrain original repair links and consolidate declared assignment restatements

- Status: Accepted
- Date: 2026-10-10
- Amends: ADR 0025's eligible links and ADR 0024's current finding consolidation.

## Context

The v42 unchanged-draft probe failed both attempts by linking a blocking outcome
finding to a major tension repair, as well as to the original outcome repair.
Application validation correctly rejected this, but the response schema offered
every repair the same broad link syntax. An unmet repair needs no link when no
compatible current finding repeats it.

The missing-turn control kept its original outcome repair met and reported the
independent turn failure. It also repeated that failure as a generic blocking
plot issue. These two reports created two new repair IDs because neither the
boundary/assignment consolidation nor the historical-repair link declared their
equivalence. Category or shared evidence alone cannot safely establish it.

## Decision

New executions use production contract v43 / graph v9. Before inference, the
critic's repair-check schema is bound to each original category and severity and
the populated current scene assignment:

- Blocking assignment repairs can link only to applicable assignment/viewpoint
  routes with their exact category. `boundary` is eligible only for the category
  to which the current boundary maps: outcome, or its turning-point fallback.
- Other assignment severities or unavailable anchors allow only empty links.
- Craft repairs can use only `issue:<index>`. Their current categories, severities
  and existence cannot be known before generation and remain application checks.
- Met checks still require empty links. Unmet checks may also use empty links;
  their original repair remains actionable.

Definitions are shared by original category/severity group. Existing exact test
keys, evidence requirements, same-claim instructions, single ownership and
complete consolidated-route validation remain. Eligibility does not prove that
two allegations mean the same thing, and separate historical repair IDs are
never merged.

Every generic critic issue now includes `assignment_finding_ref`: either `null`
for an independent craft issue, or an explicit applicable current assignment
route that it repeats. The schema prefers reporting assignment defects only
through their dedicated routes. If the model repeats one in generic reporting,
the explicit reference permits consolidation after all issues, evidence and the
target finding validate. Both source and target must be blocking.

The consolidated assignment finding retains both descriptions, all distinct
resolved evidence and both repair recommendations. Only the declared generic
restatement leaves the canonical issue array. Unlinked issues survive, even if
their category or evidence overlaps. Missing, unreported or invalid references,
malformed issues and incompatible severity cause structural rejection; the
application does not guess links or silently clear them.

The removed generic issue is not an `issue:<index>` alias for historical linking.
An original assignment repair must claim the native assignment routes; a craft
repair cannot claim the assignment through its removed restatement. An original
unmet repair still retains its original identity and requested change; linked
current wording remains inspectable in its existing revision audit.

The scene-boundary invocation audit uses version 2 when declared restatements
exist, recording their count and up to 16 source reports with exact evidence
references and redacted, bounded text. This also covers initial critiques without
historical repairs. Rejected-response evidence retains the new reference field.
Audit version 1 remains unchanged when no restatement exists.

No specialist, model call, retry allowance, dependency, canonical artifact field,
API contract or migration is added. Writer and critic system instructions,
approved story context and historical artifacts are unchanged. Local and cloud
deployments retain their existing schema delivery paths.

## Qualification

Local regressions cover eligible route groups, inactive targets, invalid links,
evidence retention, independent same-evidence findings, audit redaction and
persisted propagation of one new turn repair to the next writer and critic with
the original repair either met or unmet.

Old raw responses with generic issues lack the new required wire field. They are
not silently upgraded in production. Explicitly labeled offline annotations test
consolidation mechanics; they do not establish model compliance. Saved canonical
artifacts remain readable without migration. The five prepared probes preserve
exact v42 inputs and settings to test the revised protocol before any broader
story campaign.

The approved five probes use six calls. The missing-turn control reports only
the dedicated turn finding, retaining one new repair target instead of two; it
does not exercise non-null consolidation live. The three saved revisions pass.
The unchanged control no longer links tension to outcome, but both attempts
fail on an invalid generic assignment reference. Manual offline annotations
also expose incompatible restatement severity, omitted consolidated routes and
category spelling drift on the retry. All real failures remain failures.
Reviewer reliability and Step 19 acceptance remain open.

See the [implementation and diagnostic report](../benchmark_reports/eligible-repair-links-v43-2026-10-10.md).
