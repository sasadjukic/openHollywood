# Why OH-V01-002 scene 1 was accepted — 2026-10-08

Status: completed read-only investigation. Production remains v36 / graph v9.
Branch: `codex/scene-one-acceptance-trace`.

**Finding:** the original critic approved the overrun rather than identifying it
as an assignment violation. Continuity found no blocker, so the workflow accepted
the first draft normally. The application did not discard a reported blocker or
accept because retries were exhausted. Its existing assignment gate rejects the
same high-scoring review when a supported violation is supplied.

## Exact production path

The frozen Repeat 3 workflow is `c7e501ae-b942-50a1-a4f3-abe6a46b3b21`.
Its scene-1 calls used prompt v33. Four invocations succeeded, all at revision 0:

| Role | Invocation | Recorded result |
| --- | --- | --- |
| Scene writer | `155ca99d-7edc-408f-979d-16572821a9ad` | Draft `9deb29b1-bada-4c8b-9790-25a654f6c1d8` already completes the handwriting comparison. |
| Scene critic | `d2758b4f-7a66-4587-b7c6-fc5386ff20b6` | Critique `9cadaa15-18fa-424b-a40e-a77943acf8c8`: PASS, no issues, all three craft scores 5/5. |
| Continuity supervisor | `75e744c9-34c9-40ed-915e-f83cdd35d7d5` | Report `45f3d675-ab1d-47bf-8841-ca4c714d612f`: one informational location observation, no blocker. |
| Story Bible maintainer | `87989e2c-8899-4506-ae8b-2c255f5f1209` | Update `20f751e7-d4f8-4b5b-bdbb-80e2f210c3dd` records verification as an established fact. |

The `workflow.node.completed` event for `accept` references exactly this draft,
critique, continuity report, Bible update and successor Bible
`868b99e6-c85d-4b49-aa69-2ad5f5ba33a1`. There was no scene-1 revision or adjudication
invocation. With PASS and no continuity blocker, the graph's disposition is
`passed_rubric`; no revision-limit fallback is needed.

## What writer and critic could see

Both rendered requests explicitly contained the current outcome:
**Elena decides to verify the handwriting.** The writer was also instructed never
to draft material assigned to a later scene. The problem is not that the current
outcome was lost before reaching either agent.

Their Blueprint projections were labeled `current_scene_only`. They included
only scene 1 and beat 1; scene 2's plan and verification beat were omitted. The
complete original Blueprint remained in immutable input lineage, but that does
not mean its complete contents were shown to the model.

At the same time, both projections retained the entire `story_arc`, which
describes Elena verifying the handwriting by replicating flourishes from her
journals, then proceeds through the promotion decision and ending. The current
scene summary also says she attempts to debunk the card. Consequently, the
requests supplied the later action as general story direction without also
showing its explicit allocation to scene 2.

This is a context-design tension, not proof that the story arc caused the model's
choice. The current outcome alone offers a clue that the scene should stop
earlier. However, there is no dedicated current-endpoint/next-scene-reservation
comparison in the request. The model must infer that deciding is the stopping
point, rather than a step it may fulfill on the way to completing verification.

## The critic's recorded judgment

The critic did not merely overlook handwriting verification in a short report.
Its rationale explicitly praised it:

- **Character consistency, 5/5:** it considered the attempt to debunk the card
  through a mathematical match consistent with Elena's analytical traits.
- **Dramatic progress, 5/5:** it praised the movement from discovery through the
  date revelation and “finally to the verification process.”
- **Prose quality, 5/5:** it praised the tone and controlled prose.

Its summary stated that the turning point and outcome were both clearly realized.
This supports a specific interpretation: the reviewer treated the extra action
as successful progress within scene 1, rather than checking whether the final
achieved state exceeded scene 1's allotted work.

The instructions ask for an incompatible replacement or a missing planned
turn/outcome, and warn against demanding stronger or more explicit realization
of an achieved turn. The assignment contract lists replacement of the current
scene by future material and replacement of the planned outcome as hard failures.
Those are useful protections, but premature completion of a later scene's work
is less explicit. Scene 1 still contains its own turn and implicitly contains a
decision to investigate before performing it. That makes a presence-oriented
reading of the contract permissive here.

The response schema permits an empty `assignment_violations` array. It does not
require a positive, evidence-bound assessment of the scene's endpoint when no
violation is reported. Raw successful critic JSON was not retained in this
snapshot, so the exact original array cannot be quoted. The preserved canonical
critique has no issues; the normalizer would convert any valid reported
assignment violation into a blocking issue and a revise verdict. No per-outcome
alignment audit survives beyond the critic's general summary and rationales.

## Why continuity and memory did not stop it

Continuity received the current assignment and a blocking coverage requirement
for the outcome, with `satisfaction_mode: achieve`. Its coverage vocabulary tests
met/partial/absent; it does not explicitly classify an outcome as exceeded.
Completing verification can be read as including a prior decision to verify.
The scene also preserves the assigned unsettled/suspicious emotional state.

The resulting report contains only an informational observation about the
apartment's changing emotional meaning. The saved finding audit contains no
separate judgment about the endpoint. We cannot reconstruct unretained coverage
explanations or claim that the model explicitly reasoned about overshoot.

The Bible maintainer then records what the accepted prose actually established:
Elena verified the handwriting using a five-year-old journal. This is consistent
with its recording responsibility. Deleting that fact from memory would conceal
what happened in the accepted text; it would not repair the earlier sequencing
error. Scene 2 subsequently receives both that established fact and its own
unchanged verification assignment, setting up the later repetition dispute.

## Application gate versus model detection

The relevant code is in
[production_model_executor.py](../../apps/api/open_hollywood_api/services/production_model_executor.py)
and [production_graph.py](../../engine/open_hollywood_engine/workflows/production_graph.py):

- `_scene_scoped_prompt_inputs` filters future plans/beats while retaining the
  global story arc.
- `_scene_assignment_contract` exposes the current outcome and hard-failure labels.
- `_normalize_scene_assignment_critique` turns a valid anchored violation into a
  blocking issue and forces revise, independently of craft scores.
- `_review_disposition` schedules revision when a reviewer requests it or reports
  a blocker; PASS plus no blockers proceeds to Bible update and acceptance.

A synthetic offline control confirms the gate: starting from the saved 5/5
critique, supply an `outcome` violation citing the exact sentence “It was a
mathematical match.” Current full critique materialization and validation yield
**score 5.0, verdict revise, one blocking assignment issue**. This is a diagnostic
control, not an original model response or a newly approved story change.

Thus high scores did not override a hard failure. The hard failure was never
reported. Adding more retries alone would not help this acceptance path because
the initial reviews requested no revision.

## Current-version check and verification

The current v36 critic request reconstructed from the same frozen inputs has
exactly the original v33 message hash:
`5872b60420f1fc19879aa2adfa0f13a2a669a5fd2681c0248580c5721699da54`.
Invocation metadata carries the newer version; the critic's actual messages are
identical. This does not predict an identical new response from the remote model.

AST comparison also confirms unchanged implementations of the context projection,
critic input projection, assignment contract, assignment normalization and
assignment schema specialization between the preserved v33 executor and current
v36. The recent continuity changes therefore do not address this initial critic
request or its boundary representation.

All extracted artifact contents passed their stored hash checks. SQLite was
opened read-only with query-only enabled. The frozen database remains SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
Local evidence is under `data/diagnostics/scene-one-acceptance-2026-10-08/`:
four invocation traces, workflow events, provenance index, current-request parity
result and synthetic gate-control result.

No provider request ran, no inference cost was incurred, and no application code
or canonical artifact changed. Offline provenance/reconstruction/control checks
and document whitespace checks passed. The full application suite was not rerun
for this read-only diagnostic and documentation change.

## Focused next implementation proposal

Make **the intended scene endpoint** explicit within the existing writer/critic
calls, rather than expanding continuity's job or adding an agent:

1. **Context compiler:** expose the current scene's endpoint and the immediately
   following scene's reserved central turn/outcome, with exact approved-plan
   provenance. Replace less relevant global plot detail to stay within the
   existing request-size envelope; do not restore the entire future outline.
2. **Scene writer:** preserve that boundary. A decision to investigate is distinct
   from establishing the investigation's result; foreshadowing remains allowed.
3. **Scene critic:** compare the draft's achieved ending with that boundary and
   report a supported overrun through the existing assignment gate, even when
   the current turn also occurs and the prose scores well. Test this separately
   from missing-outcome detection. Do not make every incidental action after an
   outcome, or every mention of a future event, a hard violation.
4. **Continuity supervisor and Bible maintainer:** retain their existing duties
   of factual consistency and recording accepted events. Preserve the distinction
   between narrative repetition and incompatible assertions.

Before a full-story rerun, test the exact original overrun, a draft that stops
at the intended decision, permitted foreshadowing, and the same verification
action when it is correctly assigned to scene 2. Include current hard-failure
controls so reduced scope confusion cannot silently weaken real gates. These
are proposed next checks; no new implementation or live test is claimed here.

The investigation is complete. Step 19 remains IN PROGRESS, Step 20 is NOT STARTED,
and story-quality improvements remain a separate later sequence.
