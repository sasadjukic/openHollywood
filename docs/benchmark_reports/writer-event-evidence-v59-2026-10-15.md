# Gated writer evidence with explicit event scope — 2026-10-15

Status: **DIAGNOSTIC COMPLETE — DELETION-ONLY PRESERVATION AND BOTH REPAIRS SUCCEEDED.**

All sixteen approved probes completed in sixteen calls, with no retries or skipped
stages. Both evidence-assisted overrun repairs restore the accepted prose by deleting
only the forbidden-match sentence. Both current-context writers also retain the
original indirect decision and remove the overrun, but add new verification language.
Both missing-date controls restore the complete date-plus-realization requirement;
both missing-decision controls establish a real decision. All eight post critics
pass the revisions. Production and the diagnostic remain unchanged.

This resumes the writer-evidence transfer test using accepted event reviews from the
[event-versus-terminal diagnostic](critic-event-terminal-v59-2026-10-15.md).
Check whether fulfillment evidence helps the writer preserve an existing indirect
decision while removing a separate forbidden match. Retain both missing-date and
missing-decision controls, and inspect complete prose repairs independently of the
critic's verdict.

Source commit: `47966236156280a3ea49d6c77a5e610e0eec8bd3`.
Branch: `codex/writer-event-evidence-v59`.
Production remains **prompt v59 / graph v9**. The failed-clause critic diagnostic,
writer evidence policy and projection remain fixed. Step 19 remains IN PROGRESS;
Step 20 is NOT STARTED.

## Assignment and saved gates

Use the exact saved OH-V01-002 drafts and synthetic event plans:

- Turning point: “The realization that the date is exactly ten years in the future.”
- Outcome: “During this scene, Elena decides to verify the handwriting.”
- Separate exit restriction: “No handwriting match is established by the end of this scene.”

At each of seeds **19101 and 19103**, replay the saved baseline and three initial
reviews, including their structural retries. Both baselines must pass with both
native requirements met and no overrun. Each remaining review must have the expected
native statuses, boundary finding and verdict before it can supply writer feedback.
All eight saved reviews pass these gates; ten historical response attempts replay
exactly. These are reused reviews, not fresh critic calls or new evidence of model
repeatability. No review is rerolled or edited to improve its advice.

| Saved draft | Turning point | Outcome | Boundary | Eligible writer arms per seed |
| --- | --- | --- | --- | --- |
| Accepted inconclusive investigation | Met | Met | No overrun | Baseline gate only |
| Same prose plus separate definitive match | Met | Met | Overrun | Current, fulfillment evidence |
| Today-date contradiction plus definitive match | Unmet | Met | Overrun | Fulfillment evidence |
| Future date, genuinely unresolved decision | Met | Unmet | No overrun | Fulfillment evidence |

The preservation pair receives identical drafts, source feedback, assignments,
settings and seeds. Counterbalance current/evidence writer order across seeds.
Keep the existing evidence packet unchanged: it includes the latest critic's met
assessments and exact cited passages, bound to the current assignment, draft and
critique versions. The packet certifies both anchors for the main pair, only the
outcome for the date control, and only the turning point for the decision control.
Every actual mandatory repair remains in the writer's context.

The compatibility adapter routes saved diagnostic response validation through the
fixed failed-clause validator before the unchanged packet builder extracts met
checks. It does not change the packet policy, repair advice, native classifications
or production functions. Post critics use the same sealed diagnostic request/schema
builder and adapter, with complete actual repair history and no writer evidence
packet. Their artifact references update for the new writer output.

## Approved run and inspection criteria

**Eight writers and eight dependent post critics: at most 16 probes / 32 calls.**
Allow one existing structural retry per probe and one prose revision per case.
Freeze each post request before sending it; skip it if the writer has no validated
output. No new initial critics, semantic rerolls, replacement cases, second prose
revisions, full-story runs or canonical writes.

At the recorded October 8 rates of USD 0.14/M input and USD 0.40/M output, with
24,000 input / 8,000 output tokens budgeted per call, the maximum estimate is
**USD 0.20992**. Actual charges remain unknown. These are historical rates, not a
claim about current published prices or the user's balance.

Inspect every full revision and diff, not only critic acceptance:

1. **Preservation pair:** remove the definitive match while retaining the existing
   indirect decision and date realization. Record exact deletion-only restoration,
   unchanged verification passage, added decision restatements and other edits
   separately from semantic fulfillment.
2. **Missing-date control:** restore both the future date and Elena's realization
   of the ten-year gap, remove the match, and preserve the existing indirect decision.
3. **Missing-decision control:** repair the genuinely unresolved choice through
   actions or narration while preserving the future-date realization and no-match
   endpoint. Preservation must not prevent a necessary repair.
4. **Critic response:** inspect first/final native checks, failed clauses, historical
   repair checks and links, remaining independent criticism, advice and verdicts.
   Source traceability does not establish semantic support.

The saved date advice differs by seed: 19101 explicitly asks for Elena's realization;
19103 asks for the future date without explicitly requiring realization. Keep this
known qualification visible. Complete prose repair is required in both cases even
if the shorter advice or historical repair check is satisfied.

## Local validation

- Twenty-four no-network mock calls exercise the sixteen-stage matrix, writer JSON
  retry, critic clause retry, critic repair-link retry, permanent failures and an
  unchanged missing-date/overrun control.
- Ten malformed evidence packets are rejected. Saved-gate failures and writer
  failures skip dependent stages. Neither unmet control anchor enters its packet.
- All current repair feedback is preserved; post requests match the fixed critic
  diagnostic and receive no added writer packet.
- Ten saved event response attempts replay exactly; 2,398 sealed source files and
  fixed implementation hashes verify.
- Forty-five focused regressions pass in 13.18 seconds. Ruff, formatting and strict
  mypy pass for 198 source files. Diagnostic formatting and error lint pass.
- Frontend/build checks are inapplicable: no frontend, public API or production
  code changes. No live model result is established by these local fixtures.

## Results

| Measure | Current writer | Writer with fulfillment evidence |
| --- | --- | --- |
| Main pair: original indirect decision passage stays verbatim | 2/2 | 2/2 |
| Main pair: forbidden match removed | 2/2 | 2/2 |
| Main pair: exact deletion-only restoration | 0/2 | 2/2 |
| Main pair: added verification reinforcement | 2/2 | 0/2 |
| Missing-date control: future date and Elena's realization restored | Not run | 2/2 |
| Missing-date control: original decision preserved, overrun removed | Not run | 2/2 |
| Missing-decision control: genuine decision repaired, date realization preserved | Not run | 2/2 |
| Post critic accepts the revision | 2/2 | 6/6 |

The main-pair result is **greater editing restraint**, not prevention of a lost
decision. All four main revisions preserve the original action-based decision and
satisfy the assignment. The current writers' extra language is unnecessary for this
repair but does not itself violate the assignment or prove worse reader preference.
This is not a blind story-quality comparison.

At seed 19101, the current writer adds a sentence ending in “a more rigorous method
of verification.” At seed 19103, it adds two sentences about not being fooled and
needing “definitive proof.” The evidence-assisted writer at each seed deletes only
the separate forbidden-match sentence, leaving every other character of the prose
unchanged. Both evidence outputs are identical to the accepted baseline prose.

Both date repairs change the card from 2024 to 2034, retain the current date of 2024,
replace “Today.” with “Ten years.”, and adjust the later birthday reference to “a
decade removed.” They preserve the existing journal comparison and handwriting
replication verbatim, and delete the definitive match. Seed 19103 also removes a
trailing space. Its complete realization repair succeeds despite the abbreviated
saved advice; this does not establish that omitting realization from advice is safe.

Both missing-decision repairs remove the explicit unresolved-choice language and
open the desk drawer to investigate. Seed 19101 ends with “She would verify the
handwriting.” Seed 19103 opens the drawer “determined to find her old journals and
verify the handwriting.” Both preserve the date discovery and realization and stop
without establishing a match. The preservation packet therefore did not prevent
the genuinely necessary repair in these controls.

Across all eight revisions, the complete future-date realization and decision are
fulfilled and no handwriting match is established. All six input overruns are
removed. All six already-present indirect verification passages are preserved
verbatim; the two missing-decision drafts require new decision material instead.

## Critic replay and evidence inspection

Every first response validates: eight writers and eight critics, **16/16**, with no
structural retries, rerolls or skips. All eight raw and canonical critic verdicts
are `pass`. All sixteen native checks and all ten historical repair checks are
`met`, all eight boundary checks report `no_overrun`, and no independent issue,
assignment violation or mandatory repair condition remains. Met checks use null
failed clauses; satisfied historical checks use no current-finding links.

Replay reproduces every request, raw response hash, source binding, diagnostic
clause audit, canonical result, boundary audit and historical repair audit. Full
prose/diff inspection supports the substantive classifications. Native date checks
cite the card date, current date and “Ten years.”; decision checks cite the retained
verification actions or the new decision in the missing-decision controls.

The seed-19103 historical date check cites the two dates, while its independent
native turning-point check also cites the character's realization. Complete
fulfillment is supported by the prose and native check, not inferred from the
narrower recommendation alone. These post critics use the fixed failed-clause
diagnostic; this run does not establish the same performance for ordinary production
v59 criticism. The critic's favorable craft scores are not independent evidence of
story quality.

Usage: **212,392 input tokens / 19,190 output tokens**. The recorded-rate estimate is
**USD 0.03741088**, below the USD 0.20992 cap. Actual charges remain unknown. The
eight saved source gates and their two historical retries incur no new model calls.

## Interpretation and next focused check

Together with the earlier successful OH-V01-001 comparison, this supports the
writer-evidence mechanism on a second scene when the critic correctly distinguishes
fulfilled requirements from independent defects. It also demonstrates complete
repair of genuinely unmet requirements alongside preservation. Keep production v59
and the diagnostic fixed; no production integration was performed.

The next useful check is the existing policy's preservation exception: a passage
cited as evidence of fulfillment also contains the defect that must be repaired.
Test whether the writer edits that passage enough to remove the defect while
retaining the fulfilled fact. The present experiment puts the forbidden match in a
separate sentence, so it cannot establish this behavior. Retain a genuinely unmet
control; do not add another instruction before testing the current exception. No
additional cloud run is authorized by this completed experiment.

## Limits and evidence

This is a two-seed, one-scene, one-provider diagnostic with synthetic event/exit
wording and saved initial reviews. The evidence treatment combines status,
assessment, passages and preservation policy. The negative controls are evidence
arms, not current-versus-evidence comparisons. The result qualifies this bounded
repair task, not general reliability or production integration.

Ignored private bundle: `data/diagnostics/writer-event-evidence-v59-2026-10-15/`.
It contains the runner, replay and local checks, eight frozen writer requests,
source gates, baseline drafts, exact artifact versions, code hashes and protocol,
explicit approval, sixteen live receipts, exact replay and separate semantic
inspection. All eight dependent critic requests were frozen before sending them.

Plan SHA-256:
`bad4430d7563f95056842b940afb5508db995cf0e331f2476cb4025351dece03`.
Source closure SHA-256:
`b16efaad39d9943b436d4e5ab48d19ab9bea9d426bddc16ad73896a9a8528099`.

Explicit approval is recorded against the frozen plan. The closure hashes the
report and private evidence. Production remains v59; canonical stories and sealed
benchmark results are unchanged.
