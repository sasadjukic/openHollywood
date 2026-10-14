# Fixed-v59 endpoint wording comparison — 2026-10-14

Status: **COMPLETED — EXPLICIT ENDPOINT WORDING CHANGES THE BOUNDARY JUDGMENT.**

All 24 reviews validated on the first attempt. All twenty predeclared boundary
controls matched. Both entered drafts passed under the original threshold wording
and explicit permission, but required revision under the explicit outside-at-end
requirement. Decision fulfillment and the original repairs remained met throughout.
This supports a permissive reading of the original wording in this case; it does
not establish general boundary reliability or writer compliance.

Start from `c6739976af358834752b56895c6fb380877730f4`, which merged the previous
writer-repair documentation. The branch `codex/endpoint-wording-v59` changes no
production code, instructions, output schema, definition of met, routing or retry
policy. Prompt version 59 / graph version 9 remain fixed. Step 19 is IN PROGRESS;
Step 20 is NOT STARTED.

## Question

The [writer-repair experiment](writer-repairs-v59-2026-10-14.md) found that both
missing-decision revisions took Elara inside, and both critics accepted this
despite the planned threshold ending. An independent control established that the
critic could accept an indirect decision while Elara remained outside. The open
question is whether the original wording permits a broad transitional reading or
the critic also permits advancement beyond an explicitly bounded final position.

Compare the same endings under three exit-state wordings. Keep the decision
outcome unchanged: **“Elara decides to enter the windowless building.”** Keep
the turning point, original repair tests, broader story context and next-scene
reservation unchanged. A fulfilled decision must remain met even when the final
position violates a separate endpoint requirement.

## Frozen matrix

Twenty-four critic probes: **two source revisions × two endings × three exit
states × two critic seeds** (19101 and 19103). No writer calls.

Both source revisions are the exact accepted writer outputs from
`s19101-both_missing-unconstrained_facts-writer` and
`s19103-both_missing-unconstrained_facts-writer` in the previous sealed bundle.
Each retains its own two original v59 repairs and corresponding earlier draft.
The already completed follow-up reviews are not added as new review history.

- **Entered:** preserve the entire saved writer output unchanged.
- **Outside:** replace only its final completed-entry sentence with the same
  purposeful-action ending accepted by the previous outside control. Elara readies
  her torch, braces herself to go through, and the narration commits the next
  step to following once the strap is secure; both boots are still outside.
  Everything before that final sentence is unchanged, including the repaired
  touch, psychic pull and motivation. The first source retains its explicit
  decision narration; the second retains indirect reasoning and action.

Within each source/ending pair, prose and draft identity remain identical across
all three exit states and both critic seeds. The exact wordings are:

| Condition | Exit state |
|---|---|
| Original | Elara stands at the threshold of the monolith. |
| Outside required | Elara stands at the threshold of the monolith. At scene end, she remains outside the building and has not crossed the sill. |
| Entry permitted | Elara stands at the threshold of the monolith. This scene may end either with her still outside or just inside after crossing the sill; entry is permitted, not required. |

Permission deliberately leaves both endings available. It does not replace the
decision with a requirement to complete entry. The second critic seed reverses
source-family, wording and ending order to reduce a fixed ordering effect.

## Interpretation declared before generation

All 24 native turning-point and outcome pairs should remain `met`, and both
original repairs should remain `met`. Record these independently of the boundary
check and the final revision verdict.

| Ending | Original threshold | Outside required | Entry permitted |
|---|---|---|---|
| Outside decision | No overrun | No overrun | No overrun; permission must not become an entry demand |
| Completed entry | Descriptive / ungraded: this wording's interpretation is the question | Overrun; a separate endpoint defect should require revision | No overrun |

Thus twenty cells have a declared boundary expectation; four original-wording
entry cells are descriptive. Expected pass/revise labels assume no independently
supported defect. Inspect any valid independent exit-state finding as well as the
dedicated boundary check, rather than silently treating a different reporting route
as equivalent. Structural failures remain failures even if raw judgments look right.

Inspect first and final responses separately: native checks, original repair
checks, boundary comparisons, generic repetitions, condition sources, mandatory
advice and final verdict. In particular, a completed-entry defect must not be
misreported as a missing decision, reopen a satisfied original repair, or demand
immediate causation unrelated to the unchanged turning point. An outside decision
must not acquire a completion requirement in the permission condition.

If only explicit outside-at-end wording rejects entry, that supports a wording-
sensitivity explanation. If even the explicit boundary is waived as natural
follow-through, the evidence points to a remaining boundary-reasoning problem.
If permission still rejects entry, inspect current-plan authorization versus the
unchanged next-scene reservation. Neither a valid source reference nor a correct
label alone establishes that the repair advice is semantically justified.

## Isolation and local verification

The Scene Plan is duplicated inside the Blueprint. Both copies receive the same
exit-state substitution; synthetic identities and the Story Bible's Blueprint
reference are regenerated. Bible rules and facts do not change. This preserves
the existing revision compaction, which omits the duplicate plan only when both
copies agree. It prevents an accidental conflicting-plan/context-size comparison.

Local comparisons establish that, after accounting for the endpoint text and its
derived version/source references, all wording requests are identical. System
instructions, other assignment fields, prose, original repair tests, next-scene
reservation and generation settings are retained. Expected labels and trial names
do not appear in model messages. The source catalogs retain identical entries and
content apart from the changed endpoint and necessary version references.

- Verify **299 sealed files** across the previous writer-repair and v59 critic
  bundles, both reports, the frozen database and unchanged implementation hashes.
- Reconstruct all fifteen previous writer/critic requests and replay their raw
  responses unchanged through current materialization and validation. The saved
  judgments remain identical.
- Build all 24 requests and validate four distinct drafts and three consistent
  plan/Blueprint variants. Two original-entry requests reproduce the earlier
  live messages, schema and settings exactly at their original seeds.
- An explicit local counterfactual changes a saved review's boundary check to
  overrun under the outside requirement. The existing application produces one
  blocker while both native checks and both original repair checks remain met.
  This proves the reporting route works locally; it is not new model evidence.
- **45 relevant tests pass:** isolated probes, v31 repair acceptance, v39 endpoint
  handling and v59 consolidation. Diagnostic scripts pass Ruff formatting and
  syntax/undefined-name checks. No production or frontend implementation changed,
  so the full application suite/build is not repeated.

## Bounds and evidence

Private bundle: `data/diagnostics/endpoint-wording-v59-2026-10-14/`.
Plan SHA-256: `e8933bba61ff8a289dd9489859c998da15e063328703d6ffca1a536c966de515`.
Source database SHA-256:
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

- Maximum **24 probes / 48 calls**, at most one existing structural retry each.
- Per-call limits: 24,000 input / 8,000 output tokens; critic temperature 0.2,
  top-p 0.95, thinking disabled; original frozen provider profile retained.
- Maximum recorded-rate estimate: **USD 0.31488**, using October 8 rates of
  USD 0.14/M input and USD 0.40/M output tokens. Actual charges remain unknown.
- Destination: existing local Ollama daemon forwarding to Cloud
  `gemma4:31b-cloud`, with the recorded model digest verified before generation.
- No valid-response rerolls, writer calls, further prose revisions, adjudication,
  outcome-dependent additions, continuity/full-story runs or canonical writes.
- Freeze exact requests and code before approval. Reconstruct every request,
  replay every response, inspect results and reverify source hashes afterward.

The user explicitly approved this frozen matrix on October 14: “Yes, run the 24
endpoint-wording probes.” `approval.json` records that approval and its exact
plan hash. All 24 approved probes completed in 24 calls with no structural retry,
reroll or additional generation.

## Results and inspection

Each table cell contains four reviews: two source revisions at two critic seeds.
The boundary check and final verdict agreed in every review.

| Exit-state wording | Outside decision ending | Completed-entry ending |
|---|---|---|
| Original threshold | 4/4 no overrun; pass | 4/4 no overrun; pass (descriptive, ungraded) |
| Explicitly remain outside at scene end | 4/4 no overrun; pass | 4/4 overrun; revise |
| Either outside or just inside permitted | 4/4 no overrun; pass | 4/4 no overrun; pass |

- **24/24** first reviews structurally valid; **20/20** graded boundary controls
  matched. The four original-wording entry reviews remain descriptive rather than
  being retroactively counted as correct.
- Both native checks, turning point and decision outcome, stayed **met in 24/24**
  reviews. Both original repair checks stayed **met in 24/24**, with empty current
  finding links. No satisfied repair was reopened.
- Both outside variants passed under all three wordings: **12/12**. The second
  source's purposeful action and indirect narration were accepted without a new
  explicit declaration or completed entry. Permission did not become obligation.
- Each of the four explicit-boundary violations produced exactly **one canonical
  blocking issue**, through the existing boundary normalization. All other
  reviews had no canonical issues. Raw and canonical verdicts agreed **24/24**.
- Native advice was null throughout; generic issues, assignment violations and
  authored condition sets were empty throughout. Thus there were no duplicate
  repair conditions or new model-authored causal/completion requirements. This
  matrix does not provide new coverage of condition citation entailment.

The boundary explanations show the distinction directly. Under the original
wording, `f19101-s19103-entered-original` describes stepping inside as the
“immediate result of the decision” and treats it as matching the threshold ending.
The other original-entry reviews also acknowledge crossing the threshold while
accepting the endpoint. Under the explicit outside requirement, all four reviews
say that the decision is achieved but crossing the sill violates the exit state.
Under permission, all four entry reviews cite the current plan's authorization;
they still reserve the later interaction with Thorne for scene 2.

This is a consistent, broad interpretation of the original threshold wording,
not proof that crossing the sill literally preserves the final position. One
original-wording explanation even says the draft does not advance into the
interior while acknowledging the crossing. The controlled result is narrower:
making the end position explicit reliably changes this judgment in the tested
cases without changing the implementation or the meaning of met.

For the four overruns, the canonical issue category remains the existing
`scene_assignment:outcome`, but the description identifies the **exit-state**
violation and the independent outcome check remains met. The application renders
the existing recommendation to restore the planned outcome/exit state, remove
unassigned advancement and reserve scene 2's distinct work. It neither demands
another decision nor invents causation. That recommendation is general; the
specific crossing is identified in the accompanying description and draft
evidence. Whether the writer can apply it while preserving the fulfilled decision
has not been tested here.

## Verification, usage and next step

Every live request was reconstructed and every raw response replayed unchanged
through production materialization and validation. Frozen code, source reports,
299 earlier sealed files, prepared requests and database hashes were reverified.
`assessment.json`, `postcheck.json` and `inspection.json` retain individual
judgments, evidence, advice and grouped results. `closure.json` indexes the private
bundle and this report. Production and canonical story artifacts are unchanged.

Usage: **508,700 input / 34,452 output tokens**, estimated **USD 0.08499880** at
the recorded October 8 rates, below the approved USD 0.31488 ceiling. All provider
receipts have an unknown cost basis and a zero placeholder; neither establishes
actual billing. Actual charges remain unknown. There were no writer, continuity
or full-story calls.

Keep v59 fixed. The next focused test should feed these four explicit-boundary
findings back through the existing writer/critic repair path, with one bounded
revision per case. Check that Elara ends outside while retaining the touch,
psychic pull, motivation and a fulfilled decision, including valid indirect
fulfillment. Inspect the prose changes as well as the critic verdict; removing
the entry sentence must not leave the decision unresolved. Use the saved accepted
outside variants as controls. Prepare and approve that distinct payload set before
generation; no such calls were made in this comparison.

These results favor stating a necessary final position clearly in the existing
Scene Plan's exit state. They do not justify making every decision a prohibition
on action, imposing stricter endpoints on all scenes, or changing critic guidance
again on this evidence alone. Any later planning change should preserve deliberate
permission to continue and follow the approved artifact/version workflow.

This is one scene/provider and two source revisions with their respective saved
feedback. Within each source, wording and critic seeds are paired; differences
between source families cannot be attributed to seed alone. This comparison tests
critic interpretation, not whether a writer will obey revised endpoint wording.
Synthetic assignments remain diagnostic controls, not approved canon. Full-story,
preference and cost acceptance remain open.
