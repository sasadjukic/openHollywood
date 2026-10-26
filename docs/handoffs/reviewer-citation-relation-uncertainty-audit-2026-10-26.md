# Local citation-budget, relation and uncertainty audit — 2026-10-26

**Completed locally: zero inference calls, zero daemon/metadata calls, unchanged
prompts.** The [32-call pilot results](../benchmark_reports/reviewer-namespace-polarity-v61-results-2026-10-25.md)
remain sealed and unchanged. This follow-up preserves the failures, verifies
application-owned accounting/projection prototypes, and clarifies a prospective
diagnostic contract. It does not qualify a reviewer or alter production policy.

The findings support a [provisional 28-call semantic comparison](reviewer-epistemic-status-proposal-2026-10-26.md).
A separate live citation-budget comparison is not yet justified. Further live
calls remain paused and the full workflow canary remains **ON HOLD**.

## Citation budgets: fourteen valid refs are still too many

Both NC costume-workroom captures, `N-NC-B-OR` and `N-NC-B-RO`, fail the same
historical eight-reference whole-claim limit. Each B/C03 contains **fourteen
distinct valid references: eight prose and six context**. No component uses
more than four refs. Counting per-component sizes therefore misses the actual
failure: the boundary limits the union across the complete claim.

The audit traces every ref to its exact packet, version, text/path and component
uses. Its findings do not depend on malformed output, truncation or nonexistent
identifiers. The raw captures remain rejected in their entirety.

| Reference group | Purpose in the captured claim | Local assessment |
| --- | --- | --- |
| O011, O012, R011 | Original duplicate and revised single sentence | Distinct source occurrences; equal wording does not merge their identities |
| R005, R012 | Discovery and decision in the revision | Prose establishes actual events; comparison with the full original establishes retention |
| O016, R015 | Original no-alteration action versus revised unpicking | Both sides matter to this change claim |
| R013 | Deferred consultation language | Supports a qualified craft reading; it does not say consultation must precede deciding |
| C002, C003 | Assigned discovery and decision | Redundant for the narrated-event witness basis; context alone cannot establish occurrence |
| C004 | Required unaltered endpoint | Specific source of the assignment obligation |
| C008, C009 | Requested change and mandatory acceptance | Identical text in this artifact, at distinct pointers; the authored plan selects C009 for acceptance |
| C010 | Optional duplicate-cleanup instruction | Source of the claim that cleanup was requested |

Removing the three context refs C002, C003 and C008 from an **authored alternative
witness plan** leaves **eleven**, not eight. This is an accounting exercise, not
an edited model response. The original captures and scores are untouched.

The local prototype records two complete component plans:

| Authored plan | Distinct refs | Eight-ref status | Limitation |
| --- | ---: | --- | --- |
| Historical prose-only convention | 8 | Fits | Assignment and optional-instruction context is read without explicit context citations |
| Explicit contextual witness basis | 11 | Over budget | C004, C009 and C010 make those obligations explicitly citable |

**Eleven is the size of this manually reviewed witness basis, not a proved global
minimum.** Other representations could differ. Conversely, an eight-ref plan
does not establish that every contextual premise has an explicit citation.
The earlier eight-ref example and current fourteen-ref failures are compatible
observations under the historical convention; neither is retroactively invalidated.

The application-owned prototype binds a plan to the full source packet, claims,
component map and registry, requires every material component, and counts the
union without silently dropping witnesses. It rejects missing/duplicate components,
unknown aliases, namespace substitution and source/version/text drift. All plans
have dispatch disabled. It does **not** automatically select sufficient evidence
or determine literary truth; witness choices and their sufficiency are authored
diagnostic annotations. Hashes provide consistency checks, not protection against
an actor rewriting every trusted source and seal.

**Decision:** preserve the eight-ref historical boundary and keep the eleven-ref
explicit plan over budget. Do not increase the allowance, alias several source
occurrences into one counted ref, trim outputs or accept partial reports here.
Before a citation treatment is proposed, decide explicitly whether all contextual
premises must be cited and how a complex claim gets its allowance. Local plan
coverage is the next step; another live call cannot make an eleven-ref plan fit
an unchanged eight-ref union.

## Relation and negation regressions

The bundle preserves all **32 raw captures** and derives **32 source-bound
regression records** from the prior sealed inspection: 22 failure/ambiguity
records and ten positive controls. These retain the exact claim, response,
reason, source hash, historical expected label and adjudication. No new model
judge or retrospective rescoring is used.

| Regression class | Records |
| --- | ---: |
| False status contradiction | 8 |
| Craft abstention despite a defensible reading | 4 |
| Whole-assertion negation narrowed to an event | 2 |
| Uncertainty-contract ambiguity | 4 |
| Wrong rejection of an endpoint violation | 1 |
| Reversed acceptance-test explanation | 1 |
| Incomplete contractual coverage | 1 |
| Missing structured relation citation | 1 |
| Actual contradiction, exhaustive handling, sequential state and qualified craft controls | 10 |

The distinctions remain explicit:

- Absence of authorization is compatible with an action performed **before**
  authorization. A binding prerequisite can still be violated, and a character
  can act against a prior resolve. These are different relations.
- A fully open and fully shut description of the same door at the same instant
  is an actual literal contradiction in the supplied reliable-narration context.
- An empty satchel can subsequently receive an object. Alternative manuscript
  versions are not automatically conflicting events within one version.
- “Before explaining” does not establish “before deciding.” A real endpoint
  violation does not make every explanation of that violation true.
- The complement of **A and R** concerns the complete conjunction. If the action
  A is established but relation R is refuted, the conjunction is false and its
  complement true. Negating only A produces a different claim.

Eighteen authored short contrasts cover these distinctions, unestablished motive,
explicitly unresolved time/referent, fulfilled and violated prerequisites, and
mixed-status conjunctions. They are local gold annotations and projection tests,
not fresh full-scene experiments or evidence that a model can classify them.

The prior inspection's limits stay visible. Y's unsupported-as-unestablished
explanations are not labeled invented timing facts. N/RO's missing contractual
conclusion remains a coverage judgment. X/RO's free-text R011 mention is not
silently added to its structured citation array. The false N/OR statement that
unauthorized opening satisfies authorization-first remains a separate, stronger
explanation failure.

## Prospective uncertainty contract

For a **future isolated diagnostic**, distinguish evidence status from the final
three-label projection:

| Evidence status for the complete proposition | Meaning | Projected label | Status of its complement |
| --- | --- | --- | --- |
| `established_true` | Supplied evidence establishes the proposition | Supported | Established false |
| `established_false` | Supplied evidence refutes the proposition | Unsupported | Established true |
| `unestablished` | The packet does not establish either side | Uncertain | Unestablished |
| `explicitly_unresolved` | The source itself leaves a material fact unresolved | Uncertain | Explicitly unresolved |

Here **unsupported means refuted**, not merely unproven. This is deliberately a
new diagnostic interpretation; it is **not** silently applied to historical CV,
CP, CA or NC outputs. Their existing prompts, labels, gold and reported scores
remain unchanged. An unknown result is not by itself a reason to rewrite a story.

For conjunctions, any established-false material part refutes the whole claim;
all established-true parts establish it. Otherwise the result remains unknown.
If both kinds of unknown occur, retain the explicit-unresolved marker while
preserving the per-component statuses. Negation flips only true/false; it cannot
turn absence of evidence into evidence of absence. Missing components or unknown
status values are rejected rather than filled with convenient defaults.

Craft uses a separate standard: a qualified reading can be **supported because
it is defensible**, without being the unique interpretation compelled by a scene.
Its factual premises still require grounding. A false factual premise is not
rescued by an attractive craft judgment; genuine uncertainty about the premise
remains uncertainty.

The application can own this projection once it receives trustworthy semantic
assessments. It **cannot** determine those assessments from hashes or enum values.
A regression deliberately supplies a falsely established relation and shows that
the application preserves that mistake. This is why deterministic aggregation
and complementary-label consistency have not solved the reviewer problem.

## Verification and preservation

**184 offline tests pass: 128 new tests plus all 56 prior execution regressions.**
Ruff lint/format and strict mypy pass on four new scripts. Tests replay all raw
responses, reproduce the 32 source-bound records, preserve both fourteen-ref
rejections, verify the eight/eleven-ref accounting, reject stale and incomplete
plans, exercise complete negation/conjunction and unknown states, and keep craft,
reason truth, citation support and material coverage separate. Real HTTP is
blocked during tests; no daemon discovery or live inference occurred.

All **3,061 historical source fingerprints** verify, including the prior plan,
requests, capture seals, inspection and report. Historical usable primary totals
remain **CA 9/22, NC 13/22, CV 17/24 and CP 16/24**. Both historical decisions
remain limited evidence with no advancement.

Private bundle:
`data/diagnostics/reviewer-citation-epistemic-audit-v61-2026-10-26/`.
It contains copied raw captures, the per-ref/component audit, both authored witness
plans, bound regressions, authored contrasts, the local epistemic contract,
verification, source fingerprints and a seal binding this report and the proposal.
The scripts are isolated diagnostics; no production/API/worker/frontend code or
dependency changes require an application build.

The tracker and issue index are updated; all fourteen issue bodies and user-posted
GitHub links are preserved, with no external edits or issue closures. Production
remains **prompt 61 / graph 9 / fulfillment policy 1**. Provider attribution stays
deferred. The nine prior human ties are unchanged; future human review continues
to focus on feel/emotion, flow, character and story-breaking details, supported
by machine-prepared mechanical evidence. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; canary ON HOLD.**
