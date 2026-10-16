# Ordinary-critic fulfillment comparison: results

Date: 2026-10-16. Status: **EXPERIMENT COMPLETE; LIMITED ELIGIBILITY; NO POSITIVE
PRESERVATION QUALIFICATION.**

The approved comparison finished in **27 calls**, below its 72-call ceiling.
Twenty-four probes finished; twelve dependent probes were skipped by the frozen
gates. Only **one of four paired comparisons** was eligible. In that pair the
current-context writer restored the clean text exactly, while the evidence-assisted
writer added an unnecessary explicit decision. All four genuinely unmet controls
were repaired. All six revised drafts passed ordinary post-critics, and direct prose
inspection supports their bounded factual repairs.

This completes execution and inspection, not the full planned behavioral
qualification. It provides no preservation benefit to support a broader rollout or
story-quality claim. **The full workflow canary was not started.**

## Frozen scope and authorization

The user explicitly approved the [frozen plan](production-fulfillment-v61-plan-2026-10-16.md)
and its 72-call ceiling, while excluding the full workflow canary. Approval is bound
to plan SHA-256
`03da1a013fc86a4a1a142d561d11fc001ab219ee252c55b64c72b4c0ed60bf18`.

Implementation stayed at `c1bacab638e91dadfd69016ac9226b4885e0f10f`, prompt **61**,
graph **9**, handoff policy **1**. The designated `gemma4:31b-cloud` model's recorded
digest matched before execution and at both live phases. All original case inputs,
ordinary critic semantics, request builders, seeds **19101 / 19103**, sampling
settings, repair advice, output validators and dependency gates remained fixed.
No failed-clause diagnostic, advice replacement or semantic reroll was used.

The execution operator implements the plan's declared ledger around the existing
probe runner. It saves each complete request and reserves a unique attempt plus its
token/time allowance before dispatch. Calls are sequential. Failed and unknown
outcomes consume reservations; duplicate slots and cap breaches stop dispatch.
The operator's hash and fake-gateway verification are recorded with approval.
It changes no production code or frozen request-construction code.

Live evidence is in the separate local directory
`data/diagnostics/production-fulfillment-v61-2026-10-16-live/`. The existing probe
runner protects the parent of its source path, so a sibling output directory is
used instead of writing beneath the prepared bundle's synthetic source path.
This affects storage location only. Preparation, operator and approval records remain
in `data/diagnostics/production-fulfillment-v61-2026-10-16/`.

## Coverage and failures

| Initial case | Seed 19101 | Seed 19103 | Dependent stages completed |
| --- | --- | --- | ---: |
| Elara clean | Pass; both anchors met | Pass; both anchors met | 0 |
| Elara separate entry defect | Eligible after structural retry | Invalid after both attempts | 2 writers + 2 post-critics |
| Elena clean | Pass; both anchors met | Pass; both anchors met | 0 |
| Elena embedded match defect | Decision classified unmet; gate fails | Decision classified unmet after retry; gate fails | 0 |
| Elena missing decision | Eligible | Eligible | 2 writers + 2 post-critics |
| Elena missing date and realization | Eligible | Eligible | 2 writers + 2 post-critics |

All twelve initial probes ran. Eleven produced validated reviews; nine met their
expected classification gates. All four clean baselines and all four controls met
their gates. The three failed paired-case gates skipped **twelve** dependent probes;
their unused allowance was not spent elsewhere. Paired coverage is **1/4**, unmet
control coverage **4/4**, and embedded same-excerpt writer coverage **0/2**.

There were **three structural retries and four failed attempts**:

- Elara separate defect, seed 19101: the first response supplied a model-authored
  `boundary` repair condition where the ordinary contract requires application
  boundary advice. The allowed retry validated. Only that successful review became
  the writer source.
- Elara separate defect, seed 19103: the first response invented `exit_state` as an
  assignment-violation anchor. The retry retained that invalid route and omitted the
  corresponding repair conditions. Both responses failed validation. Their native-met
  assessments are retained as failed evidence, never salvaged into a writer packet.
- Elena embedded defect, seed 19103: the first outcome assessment exceeded the
  600-character limit. The allowed retry validated but still classified the decision
  unmet, so the eligibility gate failed.

Thus **23 of 24 finished probes validated**. All six writers and six post-critics
validated on their first attempts. No transport failure, budget overage, interrupted
call, extra revision or replacement case occurred.

## Why the embedded cases were ineligible

Both ordinary critics cited the complete compound sentence for the outcome and the
boundary violation. Citation availability was not the problem. Both nevertheless
marked the decision unmet, even though the same journal-fetching action was accepted
as a decision in their matched clean baselines.

Seed 19101 reasons that the scene proceeds beyond deciding to verify and establishes
the forbidden result. Seed 19103 says the draft bypasses a specific decision-making
process and, more critically, violates the no-match exit state. In this inspection,
those rationales conflate an already performed event with a separate endpoint defect:
the frozen outcome says Elena decides to verify **during the scene**, and the exit
state separately prohibits establishing a match. The compound sentence still contains
the journal-fetching action and its verification purpose.

The forbidden match is a real defect. Its presence does not make the pre-existing
decision disappear under the frozen expected interpretation. The experiment retained
these valid but unexpected judgments, recorded their rationales, and skipped the
dependent pairs. It neither forced a met status nor substituted diagnostic reviews.
The production necessary-edit exception therefore remains untested by this run.

## Full-prose inspection

| Executed writer condition | Required repair | Fulfilled facts retained | Exact clean prose | Ordinary post-pass |
| --- | ---: | ---: | ---: | ---: |
| Elara current context, seed 19101 | 1/1 | 1/1 | **1/1** | 1/1 |
| Elara evidence, seed 19101 | 1/1 | 1/1 | **0/1** | 1/1 |
| Elena missing-decision controls, evidence | 2/2 | 2/2 | Not a preservation comparison | 2/2 |
| Elena missing-date controls, evidence | 2/2 | 2/2 | Not a preservation comparison | 2/2 |

The current-context Elara revision removes only the forbidden entry sentence and
its paragraph separator. The 729-word source becomes the exact 720-word clean
baseline, preserving the entire indirect decision and original ending.

The evidence-assisted revision also removes entry, but replaces the last clean
sentence with:

> Both boots remained outside in the daylight, but her resolve was fixed; she would enter.

That sentence adds an explicit restatement of the already fulfilled decision. The
result is 715 words. Touch, psychic pull, the decision and the outside position all
survive, but the original expression does not. No independent craft finding asked
for that change. All **five cited excerpts** remain verbatim: the changed sentence
was outside those excerpts. Quote retention alone would have concealed this
preservation loss. The paired result is **zero evidence wins, zero ties, one loss**
on the declared preservation diagnostic, not a general literary-quality verdict.

Both missing-decision controls remove explicit indecision and add a real decision
with action toward the journals. They preserve the 2034/2024 dates and the existing
“Ten years” realization, and neither establishes a handwriting match. Both replace
the original final sentence and add verification motivation in a new ending. Their
word counts are 489 and 502, from 483. These are needed-decision repairs with broader
ending edits; there is no current-context control from which to attribute the edits
to fulfillment evidence. Speculation about a prank does not resolve the card as a
prank or establish the reserved match.

Both missing-date controls restore the card date to 2034 against the current 2024
date and explicitly restore Elena's realization of the ten-year gap. Both preserve
the action-based decision sentence verbatim and establish no match. They update the
ending's date reference consistently, producing 461 and 458 words from 454.
Seed 19101's initial advice requested the future date without expressly repeating
the realization obligation; that writer still repaired both. This is a successful
repair of the complete frozen assignment, not evidence that incomplete advice is safe.

Across the five evidence-treated writers, all **13 supplied excerpt instances**
remain verbatim. Titles, scene identities and completion fields are unchanged in
all six revisions; each has the required revision number. The full originals,
revisions and diffs are retained under `inspection/`.

## Critic and quality interpretation

The six post-critics all return raw and normalized pass, with **twelve native-met
checks and six historical-repair-met checks**, no new issues and no overrun. Direct
inspection agrees with these bounded factual repairs. The current-context post-critic
credits the original reasoning and preparatory actions for the decision; the evidence
post-critic cites the newly explicit resolve sentence. Acceptance alone would hide
the difference in preservation.

Across all seventeen validated reviews, there are 28 native-met and six native-unmet
checks. Failed captures are excluded from those counts. Five valid initial reviews
have raw `reject` normalized to `revise` by unchanged production logic; both views
are retained. No independent craft findings were reported in validated reviews.
Consequently, live editing of a fulfilled passage for an independent craft reason
was not exercised; the preparation's craft fixture remains only a transmission check.

The evidence arm did not obstruct the four genuinely unmet repairs, but it also did
not improve preservation in the one eligible pair. The run cannot meet the declared
qualification requirement of four evaluable pairs and four controls. One pair and
stochastic hosted inference cannot establish a general negative effect either.

Keep this result as a fixed reference for further investigation. The evidence points
to two unresolved problems: ordinary critic separation of fulfilled events from
endpoint defects, and writer restatement despite a positive-evidence handoff.
Structural review-contract failures also reduce eligibility. Those findings should
inform a separately scoped follow-up before broader qualification; no prompt or
validator tuning is performed here.

Later story-quality work still needs blind human comparisons and the accepted
rubric. Preserve independent craft feedback and the necessary-edit exception;
neither exact quotation overlap, reduced word count nor critic pass is a literary
quality score. **No full workflow canary or story-quality campaign was started.**

## Usage, verification and closure

- **27 / 72 calls:** 15 initial-review attempts, six writer calls, six post-critic calls.
- **428,797 input / 30,845 output tokens.** Largest individual usage: 21,564 input
  and 1,531 output tokens, within the frozen 24,000/8,000 allowances.
- **USD 0.07236958** at recorded October 8 rates, below the USD 0.47232 recorded-rate
  ceiling. Provider dollar fields remain unknown-cost placeholders; actual charges
  remain unknown. Summed measured dispatch time was approximately 146.27 seconds.
- Every actual request was reconstructed and compared with its frozen builder;
  every raw response, failed validation, canonical result and audit replayed.
  Reservations, captures, outcomes and requests match exactly across all 27 slots.
- Reverified all frozen implementation hashes, twelve prepared requests, preparation
  closure, 483 sealed source files and both source reports. No canonical artifact or
  historical evidence was edited.
- The operator passed **39 fake calls** covering the full matrix, one structural
  retry and a permanent failure; completed replay added zero calls. Attempt 73 and
  unknown-outcome continuation were blocked before reaching the fake gateway.
  An initial offline replay check compared a tuple with its JSON-list form; the
  comparison was corrected before operator attestation and before live calls.
- Operator/inspection scripts pass formatting and syntax/undefined-name checks.
  The 91 production/probe regressions, repository Ruff and strict mypy checks from
  preparation remain the applicable baseline. Production code and dependencies
  are unchanged; no fresh full-suite or build result is claimed.

`assessment.json` contains mechanical results and complete review records;
`semantic-inspection.json` records the separate prose/advice inspection.
`closure.json` seals the completed live bundle, this report, the approval and
operator records, and the frozen preparation identity. The original plan document
retains its preparation-time status and hash; this report records its execution.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.** The bounded experiment is
complete; ordinary-critic behavioral qualification remains incomplete.
