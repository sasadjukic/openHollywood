# ADR 0032: Independent craft findings own original repair links

- Status: Accepted
- Date: 2026-10-10
- Amends: ADR 0025's model-selected craft routes and ADR 0028's link eligibility.

## Context

All three v46 retries retained their generic complaint's assignment-repetition
classification. They then linked an original craft repair to `issue:0`, even
though consolidation had removed that complaint's separate identity. Runtime
validation rejected the links. The schema still offered an unrestricted craft
index pattern, while its prose instructed the critic not to use consolidated
complaints. Structural prevention required placing the choice beside the
classification it depends on.

## Decision

Production contract v47 / graph v9 moves craft-link ownership onto the independent
generic issue. Its optional wire-only `repair_test_id` defaults to null. A non-null
value is permitted only alongside `assignment_finding_ref=null`, the exact original
craft category and severity, and an exact eligible original repair ID. JSON Schema
alternatives express those conditions together on the same object. Each alternative
groups compatible original IDs without merging their obligations. Without eligible
original craft repairs, only omission or null is allowed.

Every historical craft check now requires `current_finding_refs=[]`, whether met
or unmet. Native assignment checks retain their bounded boundary/viewpoint/anchor
choices. No historical check offers a model-selected `issue:N` route. A repeated
assignment complaint cannot own a craft link, even if its labels match the original.
Independent new defects use null/omission and survive separately.

The application rejects legacy index links rather than clearing them. It validates
the declared ownership, exact category/severity and original check's unmet status,
then translates that explicit declaration into an internal current-issue route.
This is a deterministic representation change, not inferred claim matching.
Existing core-field, evidence, comparison, ownership and original-lineage validation
still runs before a current finding can be replaced with its original obligation.
Multiple independent reports may refer to one original; each report selects at
most one owner. Issue reordering does not change ownership.

The original check remains responsible for assessing the original claim. It may
remain unmet without any current finding linked to it; the original obligation
still produces revision work. The application does not rename categories, change
severity, reclassify complaints, merge original IDs or remove an obligation to
make a link valid. Current comparison and original-equivalence judgments remain
the critic's responsibility.

Critic retry policy 14 adds the ownership rule and bounded, candidate-bound eligible
ID hints for malformed direct links. Craft-check link diagnostics offer only an
empty array. Classification retention accepts the new wire field while continuing
to preserve valid classification choices independently of link errors. Other
specialists retain retry policy 10; inference and revision allowances are unchanged.

Revision acceptance audit schema 3 applies when a direct craft link is declared.
It records wire checks separately from effective internal checks, plus up to 16
declared issue-index/test-ID pairs and their total count. Existing bounded prose
redaction remains. Failure evidence can retain the redacted wire ID for inspection.
No field is added to canonical critiques, database schemas, API/client contracts
or writer inputs. Persisted successful canonical artifacts remain replayable.

## Qualification

Local tests cover positive independent ownership, forbidden repetition links,
incompatible labels, met and unknown targets, malformed issue/evidence rejection,
legacy-route rejection, order independence, evidence retention, audits and durable
propagation of the same original tests to writer and critic.

Three saved v46 failures remain rejected. Their labeled one-field offline
corrections materialize identically to the previous counterfactual results. Three
approved matching saved-failure retries all exclude separate links for the
consolidated complaint while retaining classification and original checks. Two
fully validate with exactly the two original repair tests. One returns its
comparison as text and remains failed; a labeled local correction of that field
alone recovers the same two tests. No additional model attempts were granted.
The same source inputs, settings and valid classification choices were retained.

The schema constrains which links can exist; it cannot prove narrative equivalence
or independent craft quality. No live independent-craft sensitivity or broader
story improvement is established by local fixtures. Step 19 remains IN PROGRESS.
See the [v47 report](../benchmark_reports/independent-repair-links-v47-2026-10-10.md).
