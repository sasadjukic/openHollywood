# Independent mandatory scene checks v49: 2026-10-11

Implementation, all required local checks and twelve approved matching private
probes are complete. The four previous false passes persist as explicit `met`
judgments. Independent coverage and blocker routing work, but missing-turn
detection has not improved in this sample. Step 19 remains IN PROGRESS;
Step 20 is NOT STARTED.

## Problem and change

The [v48 investigation](decision-vs-attempt-v48-2026-10-10.md) found four missing-turn
false passes after explicit decision sentences were added, plus one questionable
extra outcome complaint. The review could recognize a wrong date in its prose
without emitting the corresponding blocker. Instructions alone did not provide
inspectable, independent coverage of the two mandatory scene obligations.

Prompt v49 / graph v9 adds required `assignment_checks` inside the existing critic
response. Each populated turning point and outcome receives its own met/unmet
status, bounded comparison and exact current-draft evidence. Met checks have no
repair recommendation; unmet checks require one. Each valid unmet check becomes
the existing blocking assignment issue and forces revision independently of
scores, the boundary check and historical repair status.

The application does not infer missing events from review wording or decide
literary equivalence. The critic still supplies the semantic judgment. Instructions
explicitly allow intentional actions and inconclusive tests to establish a
decision, without a required decision sentence or further commitment. Missing-turn
evidence alone does not establish an outcome failure.

The two mandatory anchors leave `assignment_violations`; duplicate legacy routes
fail validation. Current reference names and original repair lineage remain
unchanged. Existing boundary consolidation and generic craft comparison rules
apply to the new findings. Missing or invalid checks cause a bounded review retry,
never an invented manuscript defect. Critic retry policy is 16; other specialists
remain at 10. No extra call allowance, writer change, database migration or new
specialist is introduced. [ADR 0033](../adr/0033-independent-mandatory-scene-checks.md)
records the contract.

## Local evidence

Thirty-four new cases cover applicable key selection for local/cloud profiles,
independent hard routing with met/unmet historical repairs, malformed coverage and
field shapes, wrong-version evidence, duplicate routes, precise retry instructions,
redaction and persisted workflow behavior. An unmet turn reaches both writer and
critic as the same repair test. A missing review field retries the critic without
adding a writer call. Previously tested consolidation, classification retention
and craft-link scenarios use explicitly migrated synthetic fixtures.

All required checks pass: **926 Python tests**, **11 frontend tests**, Ruff lint
and formatting, strict mypy across **189 files**, frontend formatting/lint/type
checks and the production build. Frozen request/code/source hashes and the
read-only source database hash also verify.

The twelve saved raw v48 responses are rejected under the new wire contract;
they lack required checks or use the retired mandatory-anchor route. This is
expected format incompatibility, not evidence that the old stories fail.

Four separately labeled offline counterfactuals add human-authored turn-unmet and
outcome-met checks to the four prior false passes. Each yields exactly one blocking
turning-point issue. This tests routing only and is not a new model judgment or
evidence of improved narrative interpretation.

Validated audit schema 4 records both checks and the exact candidate/current-plan
identities. Failed capture remains bounded, redacted and explicitly unvalidated.
Canonical critiques contain only the resulting ordinary issues.

## Controlled live comparison

Reused all twelve date-presence by decision-wording cases at seeds 19103 and 19104,
in the same order as v48. The saved input artifacts, original repair, model settings,
seed, budget and every user-context field except `output_schema` compare identically.
There is no historical response reconstruction or annotation in model input.

Measure turning-point and outcome judgments separately, the resulting blocker,
boundary status, original no-match repair status and independent craft findings.
Report first-attempt validity separately from final results after structural retry.
The six present-day controls should retain a turn blocker across all wording
conditions; the six future-date cases test specificity. Inspect assessments and
source evidence rather than relying only on verdicts. Schema compliance cannot
establish that met/unmet judgments are correct.

Each first request grows by 1,033 system characters and 1,941 user characters.
This is a measured sample delta, not a universal token estimate. Limits remain
24,000 input / 8,000 output tokens per call, twelve probes, at most 24 calls.
The maximum estimate is **USD 0.15744**, using recorded October 8 rates of USD 0.14/M
input and USD 0.40/M output. Actual provider charges remain unknown.

Private files remain under
`data/diagnostics/mandatory-assignment-checks-v49-2026-10-11/`:
`experiment.py`, `plan.json`, `prepared/*.json`, `offline-verification.json`,
`approval.json`, `live/`, `assess.py`, `assessment.json`, `postcheck.json`,
`record_semantics.py`, `semantic-assessment.json` and `closure.json` (77 evidence
file hashes). The direct user approval is
bound to the plan hash. All fifteen request messages and response hashes replay
exactly; canonical materialization, audits and original repair lineage verify.
Code, frozen sources and source database remain unchanged. No writer calls,
canonical mutations, valid-judgment reruns or full-story runs occurred.

## Results

All twelve probes ultimately validate, using **15 calls**. **9/12** validate on
their first attempt, versus 12/12 in v48. Three use their one allowed structural
retry; there are no exhausted probes.

| Date / decision wording | v48 final result, two seeds | v49 final result, two seeds |
| --- | --- | --- |
| Future date / implicit action | 2 correct passes | 2 correct passes |
| Future date / explicit decision before | 2 correct passes | 2 correct passes |
| Future date / decision to continue afterward | 2 correct passes | 2 correct passes |
| Today / implicit action | 2 revisions; one adds a questionable outcome complaint | 2 turn-only revisions, both after retry |
| Today / explicit decision before | 2 incorrect passes | 2 incorrect passes |
| Today / decision to continue afterward | 2 incorrect passes | 2 incorrect passes, one after retry |

All final outcomes are `met`, boundary checks are `no_overrun`, and the original
no-match repair remains `met`. No extra outcome demand recurs. Both final unmet
turn checks yield exactly one blocking `scene_assignment:turning_point` issue.
One includes a repeated generic complaint that is correctly consolidated. These
results support the deterministic routing and independent outcome handling in
this sample; they do not demonstrate improved missing-turn detection.

The four false passes all cite the actual present-day date. Their stated
justifications reveal a narrower interpretation problem:

- Seed 19103, prior decision: a present-day date plus the broader premise is
  treated as establishing a temporal anomaly.
- Seed 19103, later decision: the warning about the next decade is treated as
  establishing a future origin, although the assignment requires the date itself
  to be ten years ahead.
- Seed 19104, prior decision: the assessment explicitly acknowledges the wrong
  date, but considers the general realization action fulfilled.
- Seed 19104, later decision: the retry treats present-day realization as a
  catalyst for shock and investigation despite the ten-years-ahead requirement.

The schema now exposes a judgment for every obligation. It cannot establish
whether that judgment faithfully compares the full assigned proposition with the
draft. A different fact serving a similar dramatic purpose is being accepted as
satisfaction. These are observed explanations, not proof of the model's internal
reasoning or of a general causal mechanism.

### Structural retries

The two implicit controls finish correctly after retry, but their first responses
are not counted as accepted detections:

- Seed 19103 reports turn `met` with a non-null date repair; the status/repair
  inconsistency is rejected. The retry reports `unmet`, retains outcome `met` and
  produces one turn blocker.
- Seed 19104 correctly reports turn `unmet`, but returns its repeated generic
  issue's comparison as text. Existing classification retention preserves its
  valid assignment reference; the retry supplies the object and consolidation
  leaves one turn blocker.

The seed-19104 later-decision control initially exceeds the 600-character
assessment limit. It also reports `met` with a date repair and a malformed generic
comparison. Its prose recognizes the date discrepancy, but its structured status
already says `met`. The retry removes the allegation and returns a false pass.
There was no valid original unmet check or eligible hard classification to
preserve; this is not a change from an accepted blocker to an accepted pass.

Usage is **199,327 input / 19,501 output tokens**, estimated **USD 0.03570618** at
the recorded October 8 rates, below the approved USD 0.15744 maximum. Provider
numeric zero costs have an unknown basis; actual charges remain unknown.

## Remaining qualification

The next focused candidate is a stricter definition of `met`: fulfillment of the
complete assigned fact/state, including its explicit conditions. Require the
comparison to distinguish the actual required fact from the fact observed in the
draft; a similar dramatic function or broad premise cannot replace a missing
condition. Preserve action-based and indirect realization: this must not become
a demand for literal wording or explicit decision sentences. Test the same
positive and negative cases before claiming improvement. No additional production
change or model call is made by this analysis.

This design uses one scene/model and two seeds per cell, with synthetic decisions
and an explicit endpoint. It lacks a missing-decision negative control. The
disappearance of one outcome allegation is promising but does not establish
general reliability, writer improvement, repeatable full-story acceptance, human
preference or cost acceptance. Step 19 remains open.
