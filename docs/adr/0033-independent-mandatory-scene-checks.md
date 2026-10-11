# ADR 0033: Independent evidence-backed mandatory scene checks

- Status: Accepted
- Date: 2026-10-11
- Amends: ADR 0022's optional assignment reporting and ADR 0024's input routes.

## Context

The twelve v48 decision-versus-attempt probes produced four incorrect passes on
the missing-turn control after an explicit decision sentence was added. Each
review described the present-day date; two also mentioned the required future
date. None reported a turning-point blocker. Another review used the absent
future date to support an extra outcome allegation despite an intentional,
inconclusive handwriting test. The existing instructions did not reliably keep
the two obligations separate or connect acknowledged missing work to revision.

## Decision

Production prompt v49 / graph v9 requires `assignment_checks`, an object with
exactly the populated `turning_point` and `outcome` keys from the immutable current
scene plan. With neither assigned, it must be `{}`. Each applicable check requires:

- `status`: `met` or `unmet`.
- `assessment`: a nonblank comparison of that obligation with the current draft,
  at most 600 characters.
- `draft_evidence_refs`: one to three distinct exact current-draft handles.
- `recommended_resolution`: null when met, otherwise a nonblank targeted repair
  of at most 600 characters.

Both statuses require evidence. For missing work, the critic cites the closest
relevant passage and explains the absence. An intentional attempt may establish a
decision through action; neither an explicit decision sentence nor a promise of
future investigation is required unless assigned. The critic must assess each
obligation independently. A failed turn does not prove a failed outcome, and a met
outcome or satisfied historical repair does not clear a missing turn.

Validated unmet checks become the existing blocking `scene_assignment:<anchor>`
findings, preserving `assignment:<anchor>` references. They force REVISE regardless
of model verdict, craft scores, no-overrun status or another satisfied check.
Turning-point/outcome entries in `assignment_violations` are rejected; other
assignment anchors retain that route. Boundary and viewpoint checks remain.
Boundary comparison does not replace fulfillment checking: the critic still
assesses the complete assigned outcome, including an explicit terminal-state
restriction. Existing exact-anchor/evidence consolidation retains both assessments
and repairs when a boundary finding overlaps an unmet check. Different anchors
remain separate even with identical evidence.

Generic assignment-versus-craft comparisons and original repair links see the
same current references as before. Satisfied original repairs stay distinct from
newly reported defects. No semantic claim matching, keyword inference, automatic
decision prose or additional critic call is introduced.

Malformed, missing, inapplicable or stale-evidence checks are review errors. They
use the existing bounded structural retry and cannot create a canonical critique
or writer repair. Critic retry policy 16 supplies the exact applicable keys and
required fields; other specialists retain policy 10. Existing classification
retention and link validation remain in force.

## Observability and compatibility

Scene boundary audit schema 4 also retains both validated checks, bounded and
redacted, with the existing exact candidate and plan identities. Failed-response
capture allowlists the new object under its existing item/text bounds and marks
it unvalidated. These diagnostics are never story canon or rejected-prose retry
input. The probe runner exports the same audit.

Canonical critique, database, API/client and writer contracts are unchanged;
no migration or dependency is needed. Old canonical artifacts remain inputs to
repair history. Old raw critic responses lack the new mandatory coverage and
cannot be accepted as new v49 responses. Historical evidence remains sealed.

## Qualification

Local regressions cover applicability, independent blockers, satisfied and unmet
historical repairs, exact evidence, malformed coverage, duplicate routes, audit
redaction and durable writer-versus-review retry routing. Existing synthetic
fixtures are ported explicitly to the new wire contract; production has no
legacy-response autofill. The same twelve private v48 cases were run with explicit
approval: 9/12 first-attempt valid, all twelve valid after three bounded retries.
Both final unmet turn checks become blockers; all final outcome checks and the
original no-match repair remain met. The extra outcome allegation does not recur.

All four prior missing-turn false passes persist as explicit met judgments. Their
assessments accept general date-realization or a similar dramatic function in
place of the assigned future-date fact. Thus coverage and routing are qualified
on these cases, but missing-turn detection is not improved. Complete-proposition
fulfillment, rather than broad functional similarity, is the next focused
candidate. No semantic reliability or full-story qualification is claimed.

See the [implementation and diagnostic report](../benchmark_reports/mandatory-assignment-checks-v49-2026-10-11.md).
Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.
