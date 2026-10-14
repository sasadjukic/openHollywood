# Fixed-v59 writer repair experiment — 2026-10-14

Status: **APPROVED EXPERIMENT COMPLETE; REPAIR DELIVERY WORKS ON THESE CASES,
BUT ENDPOINT PRESERVATION IS NOT QUALIFIED.**

The user merged v59 to main at `72bed6f` after the previous comparison.
This diagnostic branch, `codex/writer-repair-v59`, starts there and changes no
production code, prompt, schema, obligation semantics, routing or retry policy.
Prompt version 59 / graph version 9 remain fixed. Earlier reports describe main
as v55 at the time of those experiments; they remain unchanged historical evidence.
Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Question and design

The [v59 comparison](shared-repair-conditions-v59-2026-10-13.md) established usable
shared repair conditions on its critic matrix. It did not test the resulting
writer revisions. This experiment uses the accepted canonical reviews without
editing their claims, evidence or rendered recommendations, through the existing
writer and critic context builders.

Six independent writer/critic pairs cover three cases at seeds 19101 and 19103:

| Case | Requested repair | What must be preserved or distinguished |
|---|---|---|
| Reversed events, order-only plan | Put stroller contact before the psychic pull | Both facts and the action-based decision already hold. Ordering does not require contact to cause the pull or the protagonist to finish entering. |
| Missing touch and decision, separately stated facts | Supply touch and a decision to enter | The psychic pull already holds. No assigned order, causation, immediacy or completed entry. A decision can be expressed through action or indirect narration. |
| Ordered but delayed pull, immediate-cause plan | Establish contact as the immediate cause of the first pull | This plan explicitly requires cause and timing. Simultaneous events alone do not establish causation; the existing action-based decision should survive. |

The exact source trials are `s{seed}-reversed-order_only`,
`s{seed}-both_missing-unconstrained_facts`, and
`s{seed}-ordered_delayed-immediate_cause_control` in the sealed v59 bundle.
The second seed reverses case order. Each writer receives only its own saved
review. Each follow-up critic receives its actual validated revision and the
same immutable original repair tests. There is no second prose revision.

Three critic controls run first:

1. The unchanged order defect, now reviewed as revision 1 with its original repair.
   Expected: turning point unmet, decision outcome met; original repair remains.
2. The unchanged missing-touch/decision draft with its two original repairs.
   Expected: both checks unmet; both repairs remain.
3. A synthetic valid ordered draft ending in an indirect commitment to enter,
   with both boots explicitly still outside. It uses the original order repair.
   Expected: both checks met and the original repair satisfied, without demanding
   explicit decision exposition or completed entry.

The positive control retains the existing delayed, ordered touch/pull passage.
Only its ending changes: the protagonist prepares her torch, braces herself to
go through, and the narration commits the next step to following once its strap
is secure, while both boots remain outside. This is a declared interpretation
control, not a canonical story edit or automatic proof of semantic fulfillment.
Its exact prose is frozen in the private request snapshot. Expected labels and
experimental case names are not placed in model messages.

## Existing production path

Both roles receive the same scene boundary, assignment contract and original
repair tests. The writer gets the complete prior draft and the existing
`bounded_scene_revision` contract, which calls for preserving unrelated successful
prose and beats. The canonical critique is projected to identity and verdict;
mandatory claims, evidence and rendered recommendations travel through the shared
repair tests. Score rationales and raw comparison/support audits are not passed
to the writer. No experiment-specific correction hint is added.

This matters because some previous critic explanations conflated order and cause.
The experiment tests the actual production projection, rather than inserting
those excluded explanations or supplying new advice on top of the saved review.
Bounded revision instructions are not a deterministic semantic-preservation gate:
the current application does not certify that unchanged facts retain their meaning.

Model settings remain writer temperature 0.85, critic temperature 0.2, top-p 0.95,
thinking disabled, with the original frozen profile and per-call token limits.
Writer output identities are materialized through the existing application path.
Each dependent critic request is saved with its exact new draft version, prompt,
evidence catalog and schema before sending it.

## Local verification

- Verify all 142 sealed v59 evidence files, its historical report, source database
  and unchanged implementation hashes. Replay all 21 raw v59 responses, preserving
  the original successful results and the one original validation failure.
- Build six writer requests, three control requests and six provisional dependent
  critic requests. Check identical repair tests, compaction, version-bound evidence,
  assignment and boundary inputs. Only real valid writer output can supply a live
  dependent request; provisional drafts are local builder checks.
- Run six fake writer cases through the real isolated runner and replay their
  receipts. One deliberately malformed first response recovers on the existing
  retry. A separate permanently malformed fixture exhausts exactly two attempts.
  Nine fake responses, zero model/network calls; unchanged fixture prose is not
  counted as a successful repair.
- All **34** relevant tests pass: `test_production_probe.py`,
  `test_production_v31.py` and `test_production_v59.py`. Diagnostic scripts pass
  Ruff formatting and syntax/undefined-name checks. No production or frontend
  implementation changed, so the full application suite/build was not repeated.

## Bounds and evidence

Private bundle: `data/diagnostics/writer-repairs-v59-2026-10-14/`.
Plan SHA-256: `be9f8df499d9479e2b08f72031734951760e19924e05a7e525c1fc78d76c8b3a`.
Frozen database SHA-256:
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

- Maximum **15 probes / 30 calls**: six writer/critic pairs and three critic
  controls; at most one existing structural retry per probe.
- Per-call maximum: 24,000 input / 8,000 output tokens.
- Maximum recorded-rate estimate: **USD 0.19680**, using October 8 rates of
  USD 0.14/M input and USD 0.40/M output tokens. Actual charges remain unknown.
- Existing local Ollama daemon forwarding to Cloud `gemma4:31b-cloud`; model
  digest must match the earlier experiment before generation.
- No valid-response rerolls, second prose revisions, extra adjudication,
  continuity calls, full-story runs, canonical writes or sealed benchmark changes.
- Skip a dependent critic if its writer exhausts validation. Record failures;
  do not alter the implementation or matrix in response to outcomes.
- Replay every raw response and reconstruct every request afterward. Preserve
  first and final responses separately, including retry drift and token usage.

The operator explicitly approved this exact new payload set. The approval record
is bound to the plan hash. The approved launch completed without changing code,
inputs, settings or call order; no extra calls or response edits were needed.

## Inspection criteria

Read every complete revision and original-to-revision diff, not only the critic
verdict. Record whether the requested fact, order or causal relationship is
actually repaired; whether fulfilled facts, intentional action-based decisions,
character identity, setting and unrelated successful prose survive; and whether
the scene gains future-scene material or an unrequested mechanism.

Inspect assignment checks, original repair checks, current finding links,
conditions, explanatory prose and final verdict separately. An unchanged defect
should not disappear merely because it was reviewed before. A satisfied repair
should not be reopened to demand explicit decision wording, immediate causality
or completed entry unsupported by its assignment or applicable canon.

Extra causation or completed entry in writer prose is recorded as a possible
unnecessary expansion; it is not automatically a violation when the assignment
permits it, and does not by itself prove the critic required it. Conversely, the
explicit-causation control must establish cause, not merely chronological proximity.
Lexical flags and similarity measurements are inspection aids, not semantic tests.

This experiment covers one scene and provider, two writer seeds, and one positive
indirect-outside control. It does not establish full-story quality, blind human
preference, cross-provider reliability, cost acceptance or completion of Step 19.

## Results

All **15 probes completed in 15 calls**, with no structural retries: six valid
writer outputs and nine valid critic reviews. All six revised drafts receive
`pass`, both native assignment checks are `met`, and their eight original repair
tests are `met` without links to new findings. No revised draft receives a new
mandatory repair or generic craft issue.

The unchanged order control retains one original blocker, and the unchanged
missing-facts control retains two. All three original repairs remain `unmet`
and link to the appropriate current native finding. One generic order complaint
reuses its native conditions and does not create a duplicate repair. The positive
outside control passes: the decision is recognized through purposeful action and
indirect narration while both boots remain outside, and the original order repair
is satisfied. All three control check pairs match their declared expectations.

These model judgments are recorded separately from inspection of the prose:

| Writer cases | Preserved / repaired on inspection | Limitation |
|---|---|---|
| Order-only, both seeds | Contact now precedes the pull. The entire existing pull paragraph and action-based ending remain byte-identical. | Contact is moved directly before the retained “At once” passage, inviting an immediate/causal reading. The original noncausal clause disappears along with the contradictory order sentence. |
| Missing touch/decision, both seeds | Both add touch and a definite decision; the entire original pull paragraph remains byte-identical. | Both also intensify the pull, add motivation and complete entry into the building. The critic accepts this despite the threshold exit state. |
| Required immediate causation, both seeds | Both remove the minute-long delay and narrate a snap/tether arising at skin contact, presenting contact as the immediate trigger. Both preserve the original action-based ending byte for byte. | The causal reading is indirect. This matrix contains no matched coincidence-only negative control, so it does not independently establish the critic's ability to distinguish cause from simultaneity. |

All six revisions preserve the first eight paragraphs exactly, including character,
setting and the NICU background, and preserve the approach-to-threshold paragraph.
The four already-fulfilled action-based decisions remain unchanged. In the two
missing-decision cases there was no fulfilled decision to preserve: the writer
supplies one, but chooses to express it with completed entry. This distinction
matters when judging preservation rather than merely counting critic passes.

No new mandatory causation, immediacy, explicit-decision exposition or completed-
entry demand appears in accepted repair advice. The outside positive control also
retains a full-minute delay before the pull and passes, so this run does not show
immediate causation being required for an order-only assignment. Nevertheless,
the first order-only follow-up describes “At once” as establishing causation,
and summaries/score rationales continue to use causal language. The writer's
order-only revisions do not demonstrate preservation of causal independence.

### Endpoint concern: satisfying the decision also advances the scene

Both missing-decision writers go beyond the minimum repair:

- Seed 19101 ends with “crossing the sill and entering the windowless dark.”
- Seed 19103 ends with “crossing the threshold and leaving the daylight behind.”

Both decisions are fulfilled. The concern is their final position compared with
the existing exit state, **“Elara stands at the threshold of the monolith.”** The
critic marks `no_overrun` in all nine reviews, including these two completed-entry
revisions. Its seed-19101 comparison explicitly acknowledges “extending slightly
to the act of entering” and permits it as “the logical completion of the decision.”
The other comparison treats having just entered as matching standing at the
threshold. Both also note that the later meeting with Thorne has not occurred.

This is evidence of permissive endpoint interpretation, not evidence that the
critic demanded completed entry. Under a strict end-state reading, the two endings
advance beyond the assigned position. The wording “at the threshold” can also be
read as a broad transitional moment, and the existing policy permits incidental
follow-through that stays within the endpoint. A matched control should separate
those interpretations before changing the implementation.

The relevant information is already present. `_scene_boundary_contract` identifies
both outcome and exit state as the current endpoint and says a decision, attempt
and established result differ. `_targeted_revision_contract` includes preservation
of the planned exit state. Both roles received those contracts unchanged. The
failure is therefore not an omitted exit-state field in these requests; it is how
the writer and critic interpret the supplied boundary. A met decision can remain
met while a separate boundary defect is reported through the existing critic path.

The seven passing reviews give all three craft dimensions 5/5. This experiment
preserves much of the original prose, including its stylistic tics, and does not
validate those scores or establish literary improvement.

## Verification, usage and recommendation

Every request was reconstructed and all fifteen raw responses replayed unchanged
through production materialization and validation. Dependent critic inputs match
the exact writer outputs, with the same original repair tests. Production/source
hashes, the frozen database and previous sealed evidence were reverified. Full
prose, diffs, inspection notes and receipts are retained in the private bundle;
`closure.json` indexes its sealed evidence and this report.

Usage: **214,224 input / 18,607 output tokens**, estimated **USD 0.03743416** at
the recorded October 8 rates, below the approved USD 0.19680 ceiling. Provider
receipts report an unknown cost basis and a zero placeholder; these do not show
actual billing. Actual charges remain unknown. No second prose revisions,
continuity/full-story calls, canonical writes or implementation changes occurred.

Keep v59 fixed. The next focused comparison should isolate **decision fulfillment
from preservation of the final position**: use the same repaired prose ending in
a valid indirect decision outside versus completed entry, under the original
threshold wording, an explicit outside-at-scene-end requirement, and explicit
permission to enter. Check whether outcome remains met while boundary judgments
respond to the exact permitted end state. This would distinguish ambiguous
wording from permission to advance beyond a clear endpoint. It requires a new
prepared plan and cloud approval; no such calls have been made here.

The tested repair path is usable and preserves several fulfilled facts, but the
six critic passes do not establish complete scope preservation. This is a narrow
single-scene result; the two seeds also receive their respective saved feedback,
so they are not a pure seed-only comparison. Keep Step 19 IN PROGRESS and Step 20
NOT STARTED. Main and production remain v59.
