# Assignment transfer with unchanged v50: 2026-10-11

Twelve approved isolated probes are complete for a different story: OH-V01-001,
scene 1, "The Pristine Lure." All twelve final obligation judgments match the
inspected facts, including valid indirect fulfillment and genuinely missing
decisions. Nine negative reviews require a structural retry even though their
mandatory check statuses are already correct. Production remains prompt v50 /
graph v9 / critic retry policy 17. Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Question and source

The [previous v50 comparison](complete-assigned-fact-v50-2026-10-11.md) corrected
four final false passes in the Elena handwriting scene while preserving acceptance
of action-based decisions. Two rejected first responses still selected met despite
acknowledging a wrong date. Those results do not establish transfer to other facts,
characters or contexts.

The new scene's existing approved obligations are:

- Turning point: "Elara touches the stroller and feels a psychic pull."
- Outcome: "Elara decides to enter the windowless building."
- Exit state: Elara stands at the threshold.

These supply a conjunctive fact and a separate decision without changing the plan.
The original Blueprint, Scene Plan, initial Story Bible and benchmark constraints
remain exact source versions. The Blueprint's stroller rule describes an anchor
and lure; it does not independently require touch to activate the lure. This
reduces a potential confound in the non-contact control.

Source: formal Cloud v33 repeat 3's sealed `completed-snapshot.db`, critic invocation
`fdbc1392-549a-4ee6-9398-e1fb593e1c36`, draft
`a36b508f-4e43-45ea-b3e2-2fae249cf727`, plan
`a13ccc8a-951b-59f9-ba4f-4ae36a5e8104`. The database SHA-256 is
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
The source commit is `9782a90`, containing merged v50.

## Four controlled drafts

All four diagnostic drafts preserve the original opening through Elara's approach
to the stroller. A shared replacement passage conveys an involuntary inward pull
toward the building through perception and bodily reaction, without the literal
phrase "psychic pull." A shared approach brings her to the doorway to inspect it,
without yet selecting whether to enter. Two independent paragraphs then vary:

1. She grips and releases the stroller handle, or lowers her hand without touching
   it. The supernatural pull and dramatic attraction stay identical.
2. She prepares her torch and clothing and shifts her weight onto one boot at the
   inner edge of the sill, or remains outside explicitly unable to settle whether
   to enter or leave. The positive uses purposeful action, without a declaration
   that she has decided; the negative leaves the choice genuinely unresolved.

| Touch condition | Decision condition | Expected turning-point check | Expected outcome check |
| --- | --- | --- | --- |
| Touch present | Entry shown through action | met | met |
| Touch absent, same pull | Entry shown through action | unmet | met |
| Touch present | Choice unresolved | met | unmet |
| Touch absent, same pull | Choice unresolved | unmet | unmet |

The final cell checks whether the critic reports both missing obligations
independently. A missing touch should not manufacture a missing decision, and a
fulfilled decision should not clear an incomplete turning point.

These are manually edited diagnostic drafts, not new writer outputs or approved
story versions. They are 661-670 words, within the unchanged 500-1,000 word advisory
allocation. The narrator does not use either assigned sentence verbatim. They end
at the threshold without Thorne's encounter or disclosure. The expected boundary
judgment is no overrun; any contrary finding must be inspected separately rather
than counted automatically as a failed mandatory check.

Each cell runs at seeds 19101, 19102 and 19103: twelve probes, with predeclared
forward, reversed and rotated orders. The design uses opaque draft identifiers;
condition names and expected judgments appear only in private diagnostic metadata,
never in the model-facing messages. Assessments and cited passages determine the
semantic analysis. An overall craft verdict alone is insufficient, and independent
craft findings remain reportable.

## Local verification and limits

Preparation and a separate verification pass reconstruct every request from its
exact artifacts. They check unchanged system instructions, non-draft artifacts,
settings other than the paired seed, budgets and current-scene obligations. The
only model-facing differences are the candidate draft, its derived evidence/schema
handles and measured length. Replacing the two varied paragraphs restores exactly
the same positive draft in every cell. No historical review or synthetic repair
test is added.

All eight existing v50 delivery/retry tests pass. Production code, API/client
contracts and application tests are unchanged; the full application suite/build
was not repeated for this diagnostic and documentation work. Request reconstruction,
artifact schemas, factor isolation, budget arithmetic, source/code hashes and
`git diff --check` are the applicable additional checks. None proves model accuracy.

This is one new scene, one model and four authored variants repeated at three seeds,
not twelve independent stories. It uses a first review without repair history,
whereas the prior Elena cases were revision reviews. There is no v49 comparison
arm, no general accuracy estimate, no cross-provider qualification and no claim
about writer or full-story quality. A disputed interpretation should be recorded,
not repaired by changing a frozen case during the experiment.

## Bounded execution and evidence

Destination: the existing Ollama Cloud `gemma4:31b-cloud` deployment through the
local Ollama daemon. The user approved the frozen plan: "Yes, run the twelve v50
transfer probes". Approval is tied to the plan hash; the model digest verified
before inference. The earlier automatic approval review's requirement for this
new private payload set was satisfied before transmission.

Maximum: **12 probes / 24 calls**, with at most one existing structural retry per
probe. Never rerun a valid judgment. Record first-attempt validity, rejected
responses, final mandatory checks, evidence, generic complaints and boundary
judgments separately. Failed review formatting must remain distinct from manuscript
defects. No writer calls, full-story generation, canonical changes or production
prompt changes are included.

Each call retains the 24,000 input / 8,000 output token ceilings. The maximum
recorded-rate estimate is **USD 0.15744**, using the October 8 reference rates of
USD 0.14/M input and USD 0.40/M output. These are recorded comparison rates, not a
new assertion about current pricing or actual billing. Actual charges remain unknown.

Private artifacts are under `data/diagnostics/assignment-transfer-v50-2026-10-11/`:
`experiment.py`, `source.json`, four `draft-*.txt` files, twelve `prepared/*.json`
requests, `offline-verification.json`, `plan.json`, `approval.json`, `live/`,
`assess.py`, `assessment.json`, `postcheck.json`, `record_semantics.py`,
`semantic-assessment.json`, `delivery-inspection.json` and `closure.json`.
All 21 saved responses replay without edits, with exact request reconstruction
and matching canonical results or structural errors. Source artifacts, frozen
requests, production code and the sealed database retain their recorded hashes.

## Results

The twelve probes use **21 calls**: three valid first responses and nine successful
bounded structural retries. No retry is exhausted and no valid judgment is rerun.

| Draft condition | Final checks across three seeds | Canonical blockers per probe | Valid first responses |
| --- | --- | --- | --- |
| Touch present, action-based decision | Both met, 3/3 | 0 | 3/3 |
| Touch absent, action-based decision | Turn unmet; outcome met, 3/3 | 1 turning-point blocker | 0/3 |
| Touch present, decision unresolved | Turn met; outcome unmet, 3/3 | 1 outcome blocker | 0/3 |
| Touch absent, decision unresolved | Both unmet, 3/3 | 2 separate blockers | 0/3 |

All three complete positive drafts pass. The nine negative drafts require revision.
No extra boundary finding, independent craft defect or duplicate repair target
appears. All twelve boundary checks say no overrun. The two missing obligations
remain separate in every both-missing case.

The evidence supports the intended distinctions:

- All six touch-present cases accept the hand closing around the handle and the
  inward directional compulsion as the assigned turn, without demanding the words
  "psychic pull."
- All six touch-absent cases cite the explicitly avoided contact. The same lure
  and supernatural experience do not substitute for the complete assigned fact.
- All six action-based decisions are accepted using the braced hand, boot on the
  inner sill and forward weight shift. No explicit decision sentence is required.
- All six unresolved-choice cases cite the final inability to settle whether to
  enter or leave. The critic distinguishes physical arrival at the threshold from
  the required decision.

The first responses already select the correct pair of mandatory statuses in
**12/12 cases**, including the nine otherwise invalid reviews. This is an inspected
statement about those fields, not acceptance of the complete responses. Every
negative response adds one repeated generic complaint whose `assignment_comparison`
is a string rather than the required object. The supplied first-review schema
already contains the object with `finding_refs` and `assessment`; this is not an
omitted schema field. The system instruction does not explicitly name that object.

All nine retries produce the correct object and retain the linked assignment,
category, severity and evidence references. Consolidation produces exactly one
repair target for each unmet obligation. The eight blocking generic repetitions
and one major repetition do not become additional craft repairs. No mandatory
status is lost or gained during retry. Thus the diagnostic supports semantic
transfer on these cases while exposing a repeated formatting cost.

Usage totals **275,139 input / 24,356 output tokens**. The estimate at recorded
October 8 rates is **USD 0.04826186**, below the USD 0.15744 cap. Actual charges
remain unknown; provider receipts' unknown-basis zero estimates are not evidence
of free billing. No writer calls, full-story runs, production edits or canonical
changes occurred.

## Interpretation and next focused step

Keep the v50 definition of met. This experiment supports complete-fact checking
and action-based fulfillment on a second scene, with the stated sample limits.
It does not establish reliable first-response formatting: only 3/12 complete
responses validate initially. That rate should not be treated as a causal decline
from the Elena test because the story, variants and review context differ.

The next focused candidate is to bring the successful retry clarification into
the **first-review instructions**: any generic issue's comparison must be the
existing object containing `finding_refs` and `assessment`. Preserve the schema,
met semantics, classification retention and duplicate consolidation. A matched
rerun of these frozen cases would measure whether that reduces retries without
changing the judgments. This is a proposal, not an implemented or tested remedy;
no additional calls are authorized or made here.

Correct detection does not yet qualify repair advice. Some responses treat touch
as a necessarily immediate causal trigger, although the assigned sentence requires
touch and a pull without separately stating that timing/mechanism. One final
outcome repair asks for crossing the threshold to satisfy the outcome and exit
state, although the plan only requires a decision and standing at the threshold.
These stronger prescriptions did not create extra blockers here, but should not
be promoted into new mandatory obligations. This design does not test alternative
causal ordering, a missing psychic pull, or the writer's response to such advice.
