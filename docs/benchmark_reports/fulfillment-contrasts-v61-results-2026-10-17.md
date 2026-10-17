# Fulfillment contrasts and writer replication: results

Date: 2026-10-17. **BOUNDED COMPARISON COMPLETE; BROADER QUALIFICATION INCOMPLETE.**

The approved comparison finished in **35 of 64 allowed calls**, with all 32 probes
attempted and no skips. The evidence packet avoided explicit decision restatement
in all three writer pairs, whereas current context added it in all three. The
earlier evidence-only restatement did not recur. Ordinary critics still had both
structural routing failures and incorrect fulfillment attribution on Elena's
overrun cases. These results do not qualify literary quality or the full workflow.

Prompts, schemas, validators, runtime and frozen cases stayed unchanged. The full
workflow canary remains **ON HOLD; NOT STARTED**. Step 19 remains **IN PROGRESS**;
Step 20 is **NOT STARTED**.

## Approval, identity and execution

This executes the [immutable frozen plan](fulfillment-contrasts-v61-plan-2026-10-17.md)
following the [failure diagnosis](../handoffs/fulfillment-failure-diagnosis-next-experiment-2026-10-16.md).
The plan's preparation-time statement that live work was not authorized remains
historical; this report records the subsequent approval and execution.

- Approved `plan.json` SHA-256:
  `9d01888c27a0aa45eaa126cf47824540591ce3867aa5324c44dbc48fb8371b9e`.
- Preparation closure SHA-256:
  `8991649304da976309c4b10b2570fbbb0a51f94bc1f2d6931fc884c4adb8df0f`.
- Source checkout: `ce2d32ba03b68874c24ac1a8b3260d8fd10c3ae9`;
  production prompt **61**, graph **9**, fulfillment policy **1**.
- Model: `gemma4:31b-cloud`, through the local Ollama daemon forwarding to Cloud.
  Preflight and both execution phases verified digest
  `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
- Critic seeds **19201/19203**, writer seeds **19201/19203/19205**; critic
  temperature 0.2, writer temperature 0.85, top-p 0.95, thinking disabled.

The user approved this frozen comparison, its ceiling and canary exclusion. Local
automatic approval review blocked launches before dispatch over the unpublished
prose/context transfer to Ollama Cloud. The initial phase proceeded after checking
the disclosed plan and approval. Before the writer phase, the user additionally
answered **“Approve this payload and destination”** to the explicit transfer
question. Both approval records are retained. Rejected launches made no model calls
and consumed no reservations; the remaining phase then ran without changing requests.

The final writer/post phase completed at **06:46:14 UTC / 08:46:14 Europe/Belgrade**.
The three model-discovery checks were not inference calls. There were no transport
retries, semantic rerolls, replacement probes, additional prose revisions or canary
calls. Structural retries used only the frozen validation-feedback builder.

## Critic results

Initial reviews used **23 calls for 20 probes**: 17 validated on their first
attempt, one recovered on its second, and two remained structurally invalid.
**16/20** matched all frozen classification targets. Failed probes stay in the
denominator; unvalidated raw judgments never become successful checks or evidence.

In the table, M/U mean met/unmet, N/O mean no overrun/overrun. Each tuple is
**turning point / outcome / boundary / normalized verdict**. “Invalid” is a failed
review, not an assessment of the manuscript.

| Story and condition | Seed 19201 | Seed 19203 | Classification matches |
| --- | --- | --- | ---: |
| Elara clean | M/M/N/pass | M/M/N/pass | 2/2 |
| Elara separate entry | M/M/O/revise | M/M/O/revise | 2/2 |
| Elara embedded entry | M/M/O/revise | M/M/O/revise | 2/2 |
| Elara missing decision | M/U/N/revise | M/U/N/revise | 2/2 |
| Elara compound outcome | M/U/O/revise | M/U/O/revise | 2/2 |
| Elena clean | M/M/N/pass | M/M/N/pass | 2/2 |
| Elena separate match | M/**U**/O/revise | M/**U**/O/revise, retry | 0/2 |
| Elena embedded match | Invalid after two attempts | Invalid after two attempts | 0/2 |
| Elena missing decision | M/U/N/revise | M/U/N/revise | 2/2 |
| Elena compound outcome | M/U/O/revise | M/U/O/revise | 2/2 |

This yields **4/4 clean**, **4/8 event/overrun distinctions**, **4/4 missing
decisions**, and **4/4 compound-outcome classifications**. Turning points are met
in all 18 validated reviews, or 18/20 with invalid probes retained. Raw valid
verdicts are four pass, three revise and eleven reject; production normalization
produces four pass and fourteen revise. No validated defective case had a raw pass.

### Attribution and routing are separate failures

Both separate Elena reviews explicitly acknowledge the comparison action, then
mark the decision unmet because a match is established later. Their boundary
finding is correct, but the exit-state failure does not negate the earlier
decision. Splitting the match into another sentence did **not** fix attribution.

Both embedded Elena probes recognized the decision as met and the boundary as
overrun in their raw attempts, but could not encode the findings correctly:

| Probe | First attempt | Structural retry |
| --- | --- | --- |
| Elena embedded, 19201 | Repair conditions target `assignment:outcome` despite its met status | Invents the invalid `exit_state` violation anchor and associated repair route |
| Elena separate, 19203 | Duplicates `outcome` through the generic violation route | Valid shape, but now incorrectly calls the outcome unmet |
| Elena embedded, 19203 | Linked issue repeats a non-null recommendation; also contains incompatible outcome routes | Links the blocking issue to met/absent outcome rather than the available `boundary` finding |

All five failed attempts and their exact validation feedback remain saved. There
was no assessment-length failure in this run. The recovered separate review is
particularly informative: structural validity improved while its outcome judgment
became wrong. One trajectory does not establish why the model changed its judgment.

Elara distinguished the decision from entry in both groupings at both seeds. At
19201, the embedded outcome and boundary even cite the same composite excerpt;
at 19203, the outcome instead cites earlier preparation. Both are valid. Citation
overlap therefore was neither an eligibility gate nor sufficient to cause failure.
The results do not support a simple “semicolon causes conflation” explanation.
Elara also changes a paragraph boundary; the contrast remains specific to these
two contexts and seeds.

All four compound controls correctly fail the outcome's **own** no-entry/no-match
clause. This retains the distinction between a fulfilled event with a separate
boundary defect and a compound obligation that is not fully satisfied.

### Advice inspection is stricter than status matching

Full inspection conservatively counts **15/20 sound initial reviews**, compared
with 16/20 classification matches. The additional caution is Elena's compound
outcome at 19203. Its second repair condition says:

> The result of the handwriting comparison must remain inconclusive or negative.

The cited source requires only that no match be established. It also permits
deferring the comparison after deciding to check; it does not require a comparison
result or request a negative one. The condition is more specific than its source.
This is an assistant judgment about advice support, recorded separately from the
correct classification. A permissive interpretation of “inconclusive” could accept
pending verification; under that reading the sound-review count would be 16/20.
Neither interpretation changes the four clear classification/validity failures.

The other inspected repairs are supported by the assigned defects. Repeating the
decision condition in a compound obligation is recorded as repetition, not proof
that the decision itself was missing. Generic linked issues repeat assignment or
boundary findings; **no independent craft issue** appeared in any valid initial
or post-review. Positive craft scores and praise are not evidence of human quality.

## Writer comparison

All six writers used the exact saved successful ordinary review
`s19101-elara-separate-initial`, attempt 2. The original failed attempt contributed
no evidence. New critic results did not select, replace or gate these writers.
All six writers and six post-critics validated first attempt.

Assistant inspection covered the entire 729-word original, every complete revision
and every diff. All revisions remove the forbidden entry, retain touch, psychic
pull and the already established decision, and leave Elara outside. All post-critics
pass with **12 native-met checks and six historical repair checks met**. These
factual results qualify all three pairs for the frozen preservation comparison.

| Seed | Current context | Fulfillment evidence | Evidence versus current |
| --- | --- | --- | --- |
| 19201 | 719 words; adds “She decided then, with a desperate, shivering certainty, that she would go inside.” Also adds heart-hammering language. | 714 words; ends with boots outside, poised at the edge of the dark; no new decision declaration. | Win on avoidable restatement |
| 19203 | 713 words; adds “She stood there, poised at the edge of the dark, deciding to enter.” | 716 words; joins the braced-hand sentence to poised weight and boots outside; no new decision declaration. | Win on avoidable restatement |
| 19205 | 721 words; adds a heart-hammering ending “as she decided to enter.” | 714 words; ends with boots outside, poised at the edge of the threshold; no new decision declaration. | Win on avoidable restatement |

Under the frozen rubric: **three evidence wins, zero ties, losses or mixed
tradeoffs**. This is a narrow comparison of unnecessary restatement, not three
literary-quality wins. The evidence arms retain the decision through the same
bridge reasoning and preparatory actions already sufficient in the source.

The important limitation is shared: **all six unnecessarily rewrite the adequate
ending about the imminent first step and boots outside**. None restores the clean
720-word scene exactly. The change is confined to the final ending and deletion of
the entry sentence; the earlier prose remains unchanged. Evidence helps avoid an
explicit decision assertion here, but does not eliminate unnecessary ending edits.

Exact quote retention is 5/5 except current 19201 and evidence 19203, each 4/5.
In those two revisions the braced-hand sentence is extended with a comma, so the
exact excerpt including its period no longer matches; its meaning remains intact.
Quote retention, word count and exact restoration are descriptive measurements,
not factual or literary-quality acceptance gates.

The frozen recurrence threshold was at least two evidence-only restatements out
of three pairs. The observed count is **0/3**, with current-context restatement
**3/3** and evidence **0/3**. Thus the earlier evidence-only regression did not
reproduce under these seeds and this fixed saved review. It remains a real prior
observation. These three pairs neither prove universal benefit nor identify the
cause of either the earlier failure or the shared ending rewrite.

Three anonymous full-prose A/B pairs and originals were exported, with their key
stored separately. **Blind human review remains pending** for voice, tension,
agency and naturalness. Assistant inspection has not filled that human review sheet.

## Budget, verification and evidence

| Measurement | Actual | Frozen limit |
| --- | ---: | ---: |
| Inference attempts | **35**: 23 initial, 6 writer, 6 post | 64 |
| Probes | 32 attempted; 30 validated; 2 terminal failures | 32 planned |
| Structural retries | 3; five invalid attempts total | One per probe |
| Input tokens | **586,904** | 1,536,000 |
| Output tokens | **41,345** | 512,000 |
| Largest input / output call | 20,900 / 1,498 tokens | 24,000 / 8,000 |
| Summed active dispatch time | **176.48 seconds** | 57,600 seconds |
| Recorded October 8 rate estimate | **USD 0.09870456** | Historical estimate USD 0.41984 |

Actual billed charges are **unknown**. The estimate uses the frozen historical
USD 0.14/M input and USD 0.40/M output rates, not a current pricing claim. The
application's USD 0.20 per-call admission placeholder is not a measured charge.
The unused 29 call slots were not spent or reassigned.

Offline verification reconstructed all **35 exact dispatched requests** and
replayed all **32 probe receipts**, including failed validation and both terminal
failures. Request, response, usage, reservation and outcome records reconcile;
all slots have known returned outcomes. The actual schedule, per-call and aggregate
limits, approved hashes and three model identities were checked. Replay and
inspection made zero model calls.

The frozen 26 static requests, 115 code/dependency hashes, 42 preparation files,
691 fake-harness files and sealed historical sources still verify. This includes
the prior experiment's 27 attempts, 280 source closure checks and 483 historical
source files. Production prompts and the frozen plan were not edited.

The two new private offline inspection scripts pass Ruff and formatting checks.
The preparation's **91 passing focused regressions**, repository Ruff/format and
strict mypy for 201 files remain recorded verification of the unchanged code;
they are not claimed as newly rerun tests. No fresh full-suite, frontend or build
claim is made for this evidence-and-documentation change.

Private, Git-ignored evidence is stored under:

- `data/diagnostics/fulfillment-contrasts-v61-2026-10-17/`: frozen inputs,
  operator, scoring, preparation closure and subsequent approval record.
- `data/diagnostics/fulfillment-contrasts-v61-2026-10-17-live/`: exact requests,
  reservations, responses, raw failures, normalized audits and phase completions.
- Live `assessment.json`: replay-derived counts, complete reviews and revisions.
- Live `semantic-inspection.json`: completed assistant judgments, separate from
  the frozen exporter's unfilled inspection template and pending human review.
- Live `inspection/`: full originals/revisions/diffs, anonymous pairs and private key.
- Live `final-verification.json` and `closure.json`: final checks and file hashes
  binding live evidence, approvals, preparation, this report and the tracker snapshot.

## Decisions and later quality work

1. Close this bounded experiment at 35 calls. Keep the cases, requests, results and
   failed attempts fixed; do not use remaining allowance for tuning or rerolls.
2. Keep production unchanged. The next critic intervention, if authorized, should
   separately address legal output routing and event-versus-endpoint attribution.
   Structural success alone must not conceal a semantic regression. Retain clean,
   genuinely missing and compound-outcome controls in any proposed follow-up.
3. Retain the evidence packet's narrow positive result alongside the prior negative
   result. Shared unnecessary ending edits deserve separate investigation; this run
   does not justify changing prompts or declaring a stable preservation benefit.
4. Preserve meaningful craft feedback and permission to revise fulfilled passages
   when a real defect requires it. This run exercises no live craft repair inside
   a met passage and cannot qualify that exception. Do not freeze prose, require
   explicit decision sentences or optimize the system merely for smaller diffs.
5. Keep blind human scene review pending and complete-story evaluation under the
   accepted rubric and comparable single-model baseline separate. No story-quality
   campaign, Step 20 work or full workflow canary was started.
