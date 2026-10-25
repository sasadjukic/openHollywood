# Evidence namespaces and relation-label regressions — 2026-10-25

Status: **local audit complete; no new inference or production change**. This
follows the [CV/CA results](../benchmark_reports/reviewer-components-v61-results-2026-10-25.md).
The original decision remains **retain limited evidence, no advancement**.
Live calls remain **PAUSED** and the full workflow canary stays **ON HOLD**.

## What the evidence establishes

The citation failures and relation failures need separate treatment. Eleven CA
responses violate the frozen evidence vocabulary. Three relation components in
valid CA responses are nevertheless false. Fixing reference delivery cannot, by
itself, fix those judgments; correct application aggregation cannot do so either.

The complete census covers **190 evidence arrays**: 48 CV whole-claim arrays and
142 CA component arrays. All 48 CV arrays use permitted references. In CA, **20
arrays contain 24 forbidden reference occurrences**:

| Component kind | All attempted arrays | Arrays with forbidden refs | Arrays in valid reports |
| --- | ---: | ---: | ---: |
| Constraint | 18 | 13 | 5 |
| Fact | 92 | 4 | 28 |
| Craft | 32 | 3 | 5 |
| Total | 142 | 20 | 38 |

These denominators include invalid reports; the 38 delivered components are not
the denominator for reference coverage. Other correctly formatted components in
an invalid report still receive no salvaged semantic credit.

The forbidden values are twelve context-artifact version UUID occurrences, six
task refs, four edit-unit IDs, one artifact-kind name and one packet-key name.
**Every value exists in the supplied input.** The audit records every matching
input path, including repeated copies, rather than guessing a reference from its
shape. All four affected fact fields cite the edit unit `U01`; the sixteen
affected constraint/craft fields use the other context-related namespaces.

Thus the captures establish namespace misuse, not fabricated identifiers. They
do not establish that the selected context proves the claim, or reveal the
model's internal reason for selecting it. The strong concentration in constraint
components is evidence supporting a citation-interface hypothesis, not a causal
experiment.

Both B/C03 unions also remain over the limit: **13 distinct refs in OR and 11 in
RO**, including ten and eight valid prose refs respectively. Dropping invalid
refs would still leave OR over eight and would silently repair both responses.
Neither operation is performed or credited.

## Ownership decision for a diagnostic candidate

The current contract exposes context but permits only O/R prose references. It
cannot directly cite the exact external assignment or voice passage. This is a
coverage limitation, not proof that the old contract is impossible to obey:
five constraint components were delivered validly using prose citations and
context in their explanations. Keep the old boundary and all its scores intact.

For a future candidate, **the application should own reference identity and
binding; the model should select references, not manufacture source identities**.
The local prototype implements that limited decision:

- Preserve O/R aliases with exact manuscript version, character offsets and text.
- Add a separate C namespace for exact text leaves in versioned context. Bind
  each to the complete input-packet hash, artifact kind/version, source pointer
  and literal text. A whole UUID, task ID, container name or edit-unit ID is not
  itself evidence.
- Enumerate scene-plan goal/discovery/decision/endpoint, blueprint voice, bible
  facts, mandatory requested-change/acceptance text and optional instruction.
  This is an explicit diagnostic allowlist, not general production retrieval.
  It includes all selected leaves, not only gold-supporting passages.
- Keep a **combined union of eight distinct references per whole claim**. Context
  references consume that same budget; there is no separate free allowance.
  Preserve the reason budget, exact component identities, duplicate rejection
  and complete-response validation. No existing response is converted to C refs.
- Require manuscript evidence for claims about what happens in a manuscript.
  Context can establish the assignment or desired voice; it cannot establish
  fulfillment, event occurrence or literary quality. This is a semantic review
  rule, not something the registry can prove.

The prototype resolves **81 context leaves across eight packets**, alongside 295
prose entries. All forty mirror checks pass: plan/assignment equality, endpoint
text/version agreement, and mandatory/optional assignment copies. P and Q reuse
one diagnostic-assignment version with identical content. This is not a content
collision, but it illustrates why an artifact UUID or short alias alone cannot
identify the complete evidence context. Packet binding remains required.

Do not automatically translate a rejected UUID to all its children or an edit
unit to its old/new spans. That would choose evidence the model did not supply,
possibly expand the union and obscure the original failure. Do not preselect a
requirement for each component as if the application already knew which premise
was true. The registry supplies addressable sources, not answers.

The earlier [reference audit](reviewer-reference-relation-audit-2026-10-24.md)
already tested a prose-only enum locally. The new difference is addressable,
typed context leaves, not merely repeating that enum idea. It has **no live
delivery evidence**. More aliases may increase selection or cardinality errors;
the B stress case must remain in a prospective test.

## Relation regressions and their limits

The local bundle preserves all **32 byte-identical raw captures**, all 21 valid
reports with their sealed source adjudications, and all eleven invalid reports.
Eleven focused failure fixtures cover the eight CV false-contradiction judgments
in H/K/N/U and three valid CA relation errors in **N/OR, U/OR and U/RO**. These are
existing observations, not eleven additional calls or independently new errors.

For example, N says that authorization has not arrived and then describes an
opening before authorization. Both facts can be true. The action does violate a
separate authorization-first requirement and the character's expressed resolve.
Replacing the stated status with that requirement or resolve changes the
relation being assessed.

N/OR's CA reason accurately repeats the two facts but does not support the
claimed contradiction. Its reason remains **supported but partial**, its relation
label remains wrong, and its citation support remains unsupported. Merely changing
the label would not make that explanation a complete assessment. U/OR explicitly
asserts the false contradiction; U/RO blends the distinct resolve and status.

The application conjunction faithfully returns supported when both component
labels are supported. It cannot recognize that one component's relation is false.
The replay still yields **35/38 correct delivered CA components**, with no new
semantic credit for the 104 components in invalid reports.

Eighteen explicitly authored local contrasts preserve:

- Compatible status facts versus genuine same-event or same-time contradiction.
- Actual external obligation, fulfilled obligation, and intention/action conflict.
- Intention as intention, without inventing an assignment or factual guarantee.
- Defensible impatience/characterization criticism versus criticism resting on
  a false factual premise.
- Different subjects, times and manuscript versions; unresolved time/referent
  uncertainty rather than forced certainty.
- Explaining versus deciding; exhaustive handling versus a narrow final-sequence
  assertion. B/C03 remains secondary; the historical Q/RO reading is unchanged.

These fixtures verify reproducible boundary and scoring behavior. They do not
teach a local truth classifier or prove a model understands the distinctions.
All relevant full source packets remain available; short authored examples are
regression contrasts, not replacements for full-scene inspection.

## Verification and preserved state

**100 offline tests pass: 80 new audit tests and twenty unchanged preceding
execution tests.** Ruff lint/format and strict mypy pass on the four new private
Python files. Real HTTP is blocked in tests. The audit verifies **2,427 historical
source fingerprints**, original frozen requests, unchanged result derivation,
exact captured bytes, source/quote/version binding, all rejected reference types,
registry tampering, mixed evidence cardinality, relation-fixture tampering and
supported craft controls. No production, API, worker, frontend or persistence
code changed; unrelated application builds were not rerun.

Private local artifacts, ignored by Git:

- [Audit bundle](../../data/diagnostics/reviewer-namespace-relation-audit-v61-2026-10-25/)
- [Readable fixture register](../../data/diagnostics/reviewer-namespace-relation-audit-v61-2026-10-25/fixture-register.md)
- [Namespace census](../../data/diagnostics/reviewer-namespace-relation-audit-v61-2026-10-25/namespace-census.json)
  and [registry audit](../../data/diagnostics/reviewer-namespace-relation-audit-v61-2026-10-25/registry-audit.json)
- [Captured relation fixtures](../../data/diagnostics/reviewer-namespace-relation-audit-v61-2026-10-25/relation-captures.json)
  and [authored contrasts](../../data/diagnostics/reviewer-namespace-relation-audit-v61-2026-10-25/authored-contrasts.json)
- [Verification](../../data/diagnostics/reviewer-namespace-relation-audit-v61-2026-10-25/verification-final.json)
  and [audit seal](../../data/diagnostics/reviewer-namespace-relation-audit-v61-2026-10-25/audit-manifest.json)

The [next proposal](reviewer-namespace-polarity-proposal-2026-10-25.md) separates
reference delivery from claim-polarity diagnosis: **two sixteen-call pilots,
32 calls total**, not prepared, frozen or approved. No new diagnostic prompt or
live request was authored here. This task used **zero inference and zero daemon
discovery calls**. Ollama 0.40.11 is the last sealed observation, not a fresh
availability check. Provider investigation remains deferred.

Production remains **prompt 61 / graph 9 / fulfillment policy 1**. All fourteen
issue bodies and user-posted GitHub links are preserved; no issue was closed or
externally edited. Step 19 remains **IN PROGRESS**, Step 20 **NOT STARTED**.
The nine human ties and the existing human checkpoint remain unchanged. Future
human review should concern feel, emotion, flow, character and story-breaking
details, with machine-prepared mechanics; strict report validity and lexical
preservation remain separate from story quality. **Canary ON HOLD.**
