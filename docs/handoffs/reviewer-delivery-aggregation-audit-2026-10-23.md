# Local reviewer delivery and mandatory-aggregation audit

Date: **2026-10-23**. **COMPLETE LOCALLY: zero inference and zero daemon discovery.**
Production remains **prompt 61 / graph 9 / fulfillment policy 1**. Live calls are
paused and the full workflow canary remains **ON HOLD**.

The delivery evidence justifies a small schema-presentation comparison. The
application can own the arithmetic of an explicitly scoped mandatory aggregate,
but that arithmetic cannot establish whether the critic's underlying judgments
are true. Retain the implementation as a diagnostic sidecar; do not substitute
it for a production acceptance gate or issue a writer instruction from it.

## Evidence and delivery findings

This audit binds all 48 raw [C2/M1 captures](../benchmark_reports/reviewer-ownership-v61-results-2026-10-23.md),
their requests, packets, receipts, source versions and original scores. It also
replays all 64 captures from the earlier C2 repeat, including all 32 Gemma
duplicate-key failures. Historical seals, inspection and decisions are unchanged.

| Latest C2/M1 delivery | Local finding |
| --- | --- |
| 35 valid, 13 invalid | Exactly reproduced; no captured answer becomes valid |
| 11 reports with duplicate `group_id` | All 27 affected group objects emit `group_id`, then the entire schema `required` sequence, including `group_id` again |
| One malformed JSON report | Premature root closure and trailing/misplaced fields remain invalid |
| One unknown evidence reference | `R020` is absent from the source catalog; the field's seven references are within the eight-reference bound |
| All 48 normal-stop responses | No length finish or transport error explains these failures |

The displayed C2 schema has two competing field orders. For group objects,
`properties` lists fields alphabetically, whereas `required` lists:

```text
assessment, evidence, preservation, group_id,
request_relation, edit_support, dependency
```

Every duplicated group starts with its natural identity field and then follows
that second list exactly. This is consistent with a conflict between starting
with an identity and following the displayed checklist. It is a hypothesis about
generation, not proof of the model's internal process or a demonstrated fix.

The earlier Gemma failures repeated root `endpoint_check` rather than a group ID.
The schema's competing traversals are a shared plausible mechanism, but different
models and response shapes need separate evidence. Gemma's stopped D pilot stays
stopped: D1's four successful answers there do not qualify it for DeepSeek.

Delivery also varies with edit-group count: **23/24** reports with one group,
**11/16** with two and **1/8** with three are valid. Cases, content, complexity and
group count covary; these counts do not isolate group count as a cause.

## Two local presentation candidates

| Layout | Exact local change | What remains fixed |
| --- | --- | --- |
| C2 | Archived control | All existing behavior |
| D1 | Archived root order; each object's `properties` follows its `required` order | Names, enums, required membership, cardinalities, evidence rules and contract prose |
| D2 | D1 plus `task_ref`, `fact_id` or `group_id` first in both lists of their respective record objects | Every other D1 field order and validation rule |

D1 already puts task and fact identities first; D2's effective new change in
these schemas is moving `group_id` from fourth to first. D2 therefore tests the
specific remaining conflict without adding a new ownership card or semantic rule.
Neither candidate invokes provider-enforced structured output.

Across 480 object-schema instances in the latest requests, C2's two lists differ;
D1 and D2 align them. Semantic schema comparison confirms unchanged validation
rules. Every raw capture receives the same strict validation result under all
three layouts. The earlier controls remain **32 rejected Gemma / 32 accepted
DeepSeek**. No duplicate is collapsed, brace spliced, reference remapped or
partial report accepted. Identical duplicate values remain invalid.

The new artifacts contain request-layout prototypes, not a frozen next run. Tests
check that the D1 final message exactly reproduces the archived D1 renderer and
that non-schema content stays unchanged, including any existing M1 card in a
historical request. A future comparison should use C2-based requests throughout,
without that card.

## Application-owned mandatory aggregation

The private prototype validates the **whole report** and exact source/response
binding before deriving a separate view. Mandatory membership comes from the
packet's declared tests and acceptance conditions. Optional membership is also
explicit; missing, duplicate, overlapping or undeclared identities are rejected.
It does not infer mandatory status from prose keywords, a craft score or the
critic's aggregate explanation.

| Valid mandatory task statuses | Derived result |
| --- | --- |
| Any `unmet` | Failure; retain any other uncertain members |
| No `unmet`, at least one `uncertain` | Unresolved (`null`), never a pass |
| All `met` | No declared mandatory-task failure |
| No mandatory tests | Explicit `no_mandatory_tests` state; not whole-story acceptance |
| Invalid whole report or source binding | No aggregate from fragments; binding mismatch is rejected |

On the **35 valid archived reports**, the derived flag matches the withheld
aggregate **35/35**, compared with **33/35** model-authored flags. The only
differences are the two C2 CN reports: their mandatory task says `met`, but their
aggregate says failure because of a real contradiction outside that narrow task.
The derived view retains the contradiction in craft/group fields. CB's broader
test still fails because it expressly requires consistency.

This is a conditional consistency result on existing judgments, not two repaired
model successes. All **eight historically unusable valid reports remain
unusable**, all thirteen invalid reports remain withheld, and C2/M1's frozen
decision remains `retain_limited_evidence_no_advancement`.

Eleven authored offline controls test optional failures, uncertainty, mixed
unmet/uncertain tasks, narrow/broad scope and absent mandatory tasks. Two are
deliberately false semantic inputs: changing a genuinely failed task to `met`
makes the arithmetic return false even while retained fact/endpoint fields show
loss; changing a successful task to `unmet` makes it return true. These synthetic
controls are labeled separately from model observations. They demonstrate the
boundary: deterministic aggregation cannot correct a false task verdict.

The sidecar keeps the original flag and explanation, member evidence, optional
checks, fact/endpoint/group findings, craft and literary comparison. Its
`production_eligible` and `writer_dispatch_authorized` fields are always false.
It neither overwrites a report nor resolves an aggregate disagreement by hiding
the original assessment.

**Decision:** retain this separate diagnostic view and use it to measure
consistency in future comparisons. Production adoption would require an explicit
mapping to the independent acceptance checks in [ADR 0013](../adr/0013-revision-acceptance-tests.md)
and [ADR 0033](../adr/0033-independent-mandatory-scene-checks.md), including their
separate mandatory blockers and unresolved outcomes. A narrow diagnostic task
aggregate must not replace those broader gates. Removing model-authored aggregate
fields, changing the persisted production report or dispatching writer repairs
would be separate changes with their own validation; none is implemented here.

## Verification and next step

**104 offline tests pass: 81 new audit checks plus 23 unchanged execution checks.**
HTTP is blocked in the audit tests. They cover all 48 captures, both candidate
layouts, older duplicate/valid controls, exact D1 rendering, source tampering,
invalid report rejection, declared membership, uncertainty and the semantic
counterexamples. Ruff lint/format and strict mypy pass on four new private scripts.

An initial run failed all 48 exact-D1-rendering checks: parsing the alphabetized
C2 schema before reordering retained a different schema-keyword order. The
prototype now uses the archived schema constructor. Initial prototypes and the
failed verification record remain available alongside the corrected artifacts;
the sealed historical harness was not edited. Application/frontend source did
not change, so unrelated application suites and the production build were not
repeated for this local diagnostic/documentation work.

The [next proposal](reviewer-delivery-repeat-proposal-2026-10-23.md) is a
**provisional 48-call DeepSeek C2/D1/D2 comparison**. It includes unchanged
historical packets, two fresh scene families and both presentation orders.
Aggregation runs locally as a separate observation in every arm. No next cases,
requests, scoring or budget are frozen or approved by this audit.

Private evidence: [delivery/aggregation bundle](../../data/diagnostics/reviewer-delivery-aggregation-v61-2026-10-23/).
It contains four scripts, 48 pinned fixtures, layout prototypes, both audits,
eleven authored controls, verification records and an audit manifest. Complete
prose/raw responses remain local and ignored by Git. The tracker and issue index
are updated; all fourteen GitHub links and issue bodies are preserved. No issue
was closed or externally edited.

Offline replay from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-delivery-aggregation-v61-2026-10-23/audit_delivery.py verify
.venv/Scripts/python.exe -X utf8 -m pytest data/diagnostics/reviewer-delivery-aggregation-v61-2026-10-23/test_audit.py data/diagnostics/reviewer-ownership-v61-2026-10-23-analysis/test_execution.py -q
```

The nine human ties remain unchanged. Reliable delivery and task accounting are
prerequisites for learning from reviewer-driven edits, not measures of story
quality. Future human assessment should still focus on feel/emotion, flow,
character and story-breaking details, with mechanical evidence prepared by
machines. **Step 19 remains IN PROGRESS; Step 20 NOT STARTED.**
