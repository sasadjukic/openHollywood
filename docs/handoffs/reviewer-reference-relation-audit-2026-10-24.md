# Reviewer reference and relation audit — 2026-10-24

Status: **local follow-up complete; no new model evidence or production change**.
This follows the [amended D2/PC results](../benchmark_reports/reviewer-premise-amendment-v61-results-2026-10-24.md).
Further inference remains paused and the full workflow canary stays **ON HOLD**.

## Findings and decisions

The rejected reference, incorrect explanations and incorrect group labels are
different failures. The existing boundary catches the first; neither valid
references nor mostly correct event verdicts establish that an explanation is
true. This audit preserves the original **D2 9/16 usable and PC 6/16 usable**
results and the decision `retain_limited_evidence_no_advancement`.

1. Keep strict rejection of edit-unit IDs in prose evidence. A local enum
   prototype makes the existing allowed vocabulary explicit in the displayed
   schema. It has not been sent to a model and establishes no delivery gain.
2. Preserve both sides of the semantic contrasts: genuine violations and defects
   remain failures; false explanations do not become acceptable merely because
   the final verdict happens to be right. Reasonable literary interpretations
   remain allowed.
3. Keep fulfillment, permission and dependency distinct. Do not relabel the
   historical reports or replace their frozen gold with subject relevance.
4. Propose an isolated [claim-verification diagnostic](reviewer-claim-verification-proposal-2026-10-24.md)
   before another general reviewer comparison. Merely renaming the relation
   field has already been tested.

At the user's request, provider attribution is recorded but investigation is
**deferred**. No controlled evidence currently attributes these semantic errors
to Ollama. That does not exonerate the provider or erase the previously recorded
delivery limitations and interruptions. This task made **zero inference and
zero daemon-discovery calls** and did not investigate the provider further.

## Reference-type regression and schema audit

The exact rejected `P-B10-PC-OR` capture cites
`["O016", "R015", "U02", "U03"]`. U02/U03 identify edit operations in the input;
they are not prose-catalog references. The original schema describes evidence
items as strings. The separate boundary already checks catalog membership and
rejects this response. The original raw capture and invalid receipt remain intact.

The local prototype adds the packet's exact O/R catalog refs as an item enum in
the eight evidence-schema locations. It changes no other field, label,
cardinality rule or validation exception. Replaying all 32 captured responses:

| Check | Accepted | Rejected |
| --- | ---: | ---: |
| Original structural schema alone | 32 | 0 |
| Prototype schema with catalog enum | 31 | 1 |
| Existing complete boundary | 31 | 1 |

This is **earlier detection of an existing violation**, not a repaired response
or an observed improvement in model generation. The prototype repeats the enum
across eight locations, adding **2,256–2,592 serialized schema characters** per
packet. A live test would need to account for that presentation change. Current
wire payloads have no `format` field; the prototype makes no provider-enforcement
claim and is not applied to production or to any frozen request.

Seventy-two authored response mutations cover nine report-row locations and
eight variants: valid O/R pairs, edit-unit contamination, group IDs, unknown refs,
wrong case, duplicates, emptiness and overflow. Separate controls retain the
allowed empty-evidence uncertain craft judgment. The enum alone does not reject
duplicates or all impermissible empty lists; the existing boundary still does.
A real but irrelevant catalog ref passes both membership checks, demonstrating
that neither establishes support for the associated claim.

## Source-bound explanation fixtures

The new bundle binds **42 captured claim fixtures** to the complete source
packets, reports, sealed inspection notes, artifact versions, offsets and exact
quotes: all **25 unsupported fields**, both **uncertain fields**, and **15
supported controls** from the preceding run. Seven unsupported fields across
four H-before reports contain the false contradiction. These are retained
assistant adjudications, not new human preferences or newly generated answers.

Twelve additional, explicitly authored response contrasts exercise the scorer
with eight supported and four unsupported explanations. They retain the source
report's event and group labels. They are not model receipts, contain no invented
usage/raw-capture provenance and cannot qualify an incomplete experiment.

| Contrast | What remains supported | What must not be inferred |
| --- | --- | --- |
| Consultation and action | Rotating before consultation violates the explicit consultation-first condition; a reversal of intention may feel jarring. | Acting before consultation contradicts the statement that consultation has not happened yet. Those two facts agree. |
| Explanation versus action | The coat alteration violates the explicit intact-seam endpoint. | Wanting another pair of eyes before explaining creates a prohibition on deciding or acting before consultation. |
| Version ownership | The revised gate admission violates the required locked endpoint; its surrounding sequence can invite qualified craft criticism. | The original, replaced locked-gate sentence describes an earlier action within the revision, or a planned question independently forbids admission. |
| Real contradiction versus invented repetition | The same crate has incompatible exact counts at the same noon; the narrow assignment still excludes that defect from its mandatory test. | The revision contains an identical duplicated sentence when it does not. |

The positive inventory also retains genuine duplicate cleanup, a surviving
independent motivation, loss of the only stated cause, permitted optional
departure, retained decisions and grounded voice/naturalness readings.

These tests verify provenance, rejection and consumption of fixed adjudications.
They **do not implement an automatic truth detector** and do not demonstrate that
the model now recognizes these distinctions. A supported replacement explanation
also leaves an incorrect group label incorrect; no unrelated failure is silently
fixed by a fixture.

## Group-relation semantics

The frozen contract defines `direct` as doing what the requested task asks,
`adjacent` as supporting another change, and `unrelated` as not carrying out the
task. Separately, `edit_support` concerns permission under the task and binding
constraints. `dependency` concerns dependence on another supported or unsupported
change. These are different questions from whether an edit touches the subject
of a requirement.

The census covers **54 groups in 31 valid reports**. Eight groups, in eight
reports, disagree with their frozen allowed labels:

| Failure | Captures | Local reading |
| --- | ---: | --- |
| H-before labeled direct | 4 | The edit reverses the consultation-first condition. Correctly identifying that violation does not make it fulfillment. |
| G-voice labeled direct | 2 | Reversing the required locked endpoint touches that requirement but does not carry it out. |
| I-cause labeled direct | 1 | Removing the required discovery does not fulfill its retention. |
| B10 dependency on unsupported change | 1 | The report describes trailing wording inside the same complete replacement as a dependent cleanup. The frozen group is not a separate child edit. |

Thus **seven mismatches concern request relation and one concerns dependency**;
there is no `edit_support` mismatch in this set. Several explanations already
state that the edit defeats the assignment while selecting `direct`. That is
observable label/definition disagreement. The captures cannot establish the
model's internal reason for making it.

Do not resolve this by treating all nonminimal edits as bad. Requested optional
cleanup can be direct and supported without being mandatory. A whole replacement
can combine a real repair and unrelated changes; the existing contract permits
an explanation of both and uncertainty when one category is unfair. Dependency
must respect the frozen group boundaries. No new taxonomy is adopted here.

A diagnostic projection removes only the group-label gate while retaining all
other actual labels, supported-claim checks, uncertainty, contradictions and
invalid delivery. It would leave **D2 at 9/16 and move PC from 6/16 to 8/16**, solely
through G-voice RO and I-cause RO. This is not a new score or a proposed gate
relaxation. It shows that group semantics alone cannot remove the other recorded
failures, including the false contradiction and unsupported dependency explanation.

The earlier R1 pilot already renamed `request_relation` to `request_fulfillment`
and `direct` to `fulfills`, with matching alternatives. It corrected the h03
fulfillment distinction in both orders but C2 and R1 both remained **5/8 usable**;
the endpoint failures persisted. See the [T/R continuation results](../benchmark_reports/reviewer-tr-continuation-v61-results-2026-10-22.md).
Repeating that rename is not a new mechanism.

## Verification, provenance and next step

**158 offline tests pass: 144 new audit cases and the 14 unchanged preceding
execution tests.** Ruff lint/format and strict mypy pass on the three new private
scripts. Tests block real HTTP and cover exact capture replay, all reference
variants, source/quote/oracle tampering, all authored contrasts, preservation of
uncertainty and legitimate craft judgments, independent group dimensions and the
limited gate projection. The audit fingerprints **715 historical source files**.

Initial and final static/test records are retained. Local setup exposed a helper
module-name collision, long literal formatting and an inferred dictionary type;
these were corrected in the new audit scripts only. No production, API, worker
or frontend code changed, so unrelated application builds and broad product
suites were not rerun.

Private local evidence, ignored by Git:

- [Audit bundle](../../data/diagnostics/reviewer-reference-relation-audit-v61-2026-10-24/)
- [Readable fixture register](../../data/diagnostics/reviewer-reference-relation-audit-v61-2026-10-24/fixture-register.md)
- [Reference audit](../../data/diagnostics/reviewer-reference-relation-audit-v61-2026-10-24/reference-audit.json)
  and [group census](../../data/diagnostics/reviewer-reference-relation-audit-v61-2026-10-24/relation-audit.json)
- [Captured fixtures](../../data/diagnostics/reviewer-reference-relation-audit-v61-2026-10-24/premise-fixtures.json)
  and [authored contrasts](../../data/diagnostics/reviewer-reference-relation-audit-v61-2026-10-24/authored-contrasts.json)
- [Final verification](../../data/diagnostics/reviewer-reference-relation-audit-v61-2026-10-24/verification-final.json)
  and [audit seal](../../data/diagnostics/reviewer-reference-relation-audit-v61-2026-10-24/audit-manifest.json)

The historical analysis seal remains
`ff387312984aee7e5e7bbfa491ee155e2c94897479ad3fc1b0edac7fb3ee2e8d`.
The new audit seal binds its own artifacts and these public recommendations; a
separate documentation closure binds the updated tracker and issue index.
All fourteen issue bodies and user-posted GitHub links are preserved. No issue
was closed or edited externally.

The next proposal is **24 claim-verification calls**, not frozen, approved or
executed. Production remains **prompt 61 / graph 9 / fulfillment policy 1**;
Step 19 remains **IN PROGRESS**, Step 20 **NOT STARTED**. The human review remains
nine overall ties. Future story-quality work should measure feel, emotion, flow,
character and story-breaking concerns; exact wording preservation and strict
report usability are not reader-preference measures. No new human checkpoint is
introduced. **Live calls PAUSED; full workflow canary ON HOLD.**
