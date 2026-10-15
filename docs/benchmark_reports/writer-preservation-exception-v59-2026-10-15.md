# Writer preservation exception, fixed v59 diagnostic — 2026-10-15

Status: **DIAGNOSTIC COMPLETE — PRESERVATION EXCEPTION SUCCEEDED; MINIMAL EDITING NOT ESTABLISHED.**

All eighteen approved probes completed in nineteen calls, including one structural
retry. Both evidence-assisted writers edited the passage containing the fulfilled
decision and forbidden match, removed the match, and retained the decision through
actions. Both current-context writers also repaired it. Both genuinely missing
decisions were repaired, and all six revisions preserved the date realization.
All six post critics passed. Production v59 and the diagnostic remain unchanged.

Test whether the writer can repair a defect inside a passage cited as evidence of
a fulfilled requirement while retaining that fulfilled fact. The
[previous writer-evidence experiment](writer-event-evidence-v59-2026-10-15.md)
produced deletion-only repairs in both evidence arms, but the forbidden match was
in a separate sentence. It did not test the existing preservation exception.

Source commit: `12f8663d5d14c32fd3dd7457c48dd65c2e31e498`.
Branch: `codex/writer-preservation-exception-v59`.
Production remains **prompt v59 / graph v9**. Reuse the sealed failed-clause critic
diagnostic, writer evidence policy, packet builder, provenance binding and request
projection unchanged. No new instruction, schema, production code or canonical
artifact is introduced. Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Controlled draft change

Retain the exact OH-V01-002 context and synthetic event-scoped assignment:

- Elena realizes the date is exactly ten years in the future.
- During the scene, Elena decides to verify the handwriting.
- No handwriting match is established by the end of the scene.

Start from the saved unresolved-decision draft, whose other prose establishes the
future date and Elena's realization without establishing a handwriting match.
Replace only its unresolved-choice passage to create two matched variants:

**Clean baseline:**

> She pulled her old journal from the desk drawer and laid it beside the card to
> check whether the handwriting was her own.

**Fulfilled decision with an embedded defect:**

> She pulled her old journal from the desk drawer and laid it beside the card to
> check whether the handwriting was her own; after comparing them, she established
> beyond doubt that the handwriting on the card matched her own.

The semicolon keeps the action-based decision and forbidden match inside one exact
evidence-catalog excerpt. The clean variant differs only by removal of the added
clause and restoration of the period. There is no other verification-action passage
to substitute for it. Deleting the whole sentence would remove the fulfilled
decision as well as the defect.

The negative control retains the original unresolved-choice prose unchanged. It
still lacks a genuine decision, retains the future-date realization and establishes
no match. Its writer packet may certify only the already fulfilled turning point.

## Frozen matrix and gates

At each of seeds **19101 and 19103**, run:

| Draft | Initial critic requirement | Dependent writer arms |
| --- | --- | --- |
| Matched clean baseline | Both native checks met; no overrun; pass | None |
| Embedded forbidden match | Both native checks met; overrun; revise; shared citation | Current and fulfillment evidence |
| Genuinely unresolved decision | Turning point met; outcome unmet; no overrun; revise | Fulfillment evidence |

The main writer pair requires both an accepted matched baseline and an eligible
initial overrun review. The initial critic must cite the **same compound excerpt**
as evidence of outcome fulfillment and of the boundary defect. The unchanged packet
builder must carry that complete excerpt, including the defect, into the evidence
arm. Do not invent, substitute or selectively sanitize a citation to make the gate
pass. If the critic does not supply the required classifications and shared citation,
skip and report that writer pair; the exception was not tested at that seed.

All six initial critics run even if an earlier gate fails. The negative-control
writer depends on its own eligible review and can proceed independently of a failed
matched baseline. An invalid writer output skips its post critic. Counterbalance
the main current/evidence writer order across the two seeds.

Both writer arms receive the same source draft, actual initial feedback, assignment,
settings and seed. The evidence arm adds only the existing fulfillment packet and
its unchanged policy, including:

> If a cited passage itself needs change to repair another supplied defect, make
> that necessary repair.

All original repair feedback remains. Post critics receive complete actual repair
history and the same fixed failed-clause diagnostic, with no added writer packet.
Exact new draft versions and references are bound before each dependent call.

## Budget and stopping rule

Maximum **18 probes: six initial critics, six writers and six post critics**.
Allow at most one existing structural retry per probe: **36 calls / USD 0.23616**
at recorded October 8 rates of USD 0.14/M input and USD 0.40/M output, with
24,000 input / 8,000 output tokens budgeted per call. Actual charges remain unknown.
These are historical rates, not a current price or balance claim.

Freeze every dependent request before sending it. One prose revision per case;
no semantic rerolls, replacement cases, second revisions, full-story runs or
canonical writes. Gate failures reduce the number of calls; they do not authorize
another attempt with different prose or instructions.

## Inspection criteria

Inspect every full revision and diff independently of the critic verdict:

1. The embedded match is removed and no equivalent definitive match appears elsewhere.
2. The valid action-based decision survives the repair. Record exact clause-only
   restoration separately from valid paraphrase or unnecessary explicit reinforcement.
3. The shared evidence excerpt actually changes. Keeping the defect is not successful
   preservation; deleting the sole decision is not a complete repair.
4. The future-date realization and other fulfilled facts remain intact.
5. The genuinely missing decision is repaired in the negative control while the
   fulfilled date realization and no-match endpoint remain intact.
6. First/final native checks, failed clauses, historical repair links, advice,
   incidental craft findings and verdicts agree with the resulting prose. Valid
   source references establish traceability, not semantic support.

## Local validation

- Twenty-seven no-network mock calls exercise the eighteen-stage matrix, writer
  JSON retry, critic clause retry, repair-link retry and permanent failures.
- Both unchanged defective controls still produce blockers. Baseline, initial,
  shared-citation and writer failures correctly skip dependent calls; all six
  initial reviews remain scheduled.
- Five malformed or selectively sanitized evidence packets are rejected. The
  genuinely unmet outcome never enters its control's fulfillment packet.
- The matched drafts differ only in the embedded clause and punctuation. The
  unchanged negative control retains identical model messages, schema, settings
  and budget; its invocation provenance is rebuilt for this experiment.
- All sixteen immediately preceding live response attempts replay exactly. Verify
  2,651 sealed source files and unchanged production/diagnostic hashes.
- Forty-five focused regressions pass in 14.10 seconds. Ruff, formatting and strict
  mypy pass for 198 source files; diagnostic formatting and error lint pass.
- Frontend/build checks are inapplicable: no frontend, public API or production
  changes. Local fixtures establish no new live model result.

## Results

Both matched baselines pass. Both overrun reviews keep the decision met and cite
the same complete compound excerpt for fulfillment and the boundary defect. Both
negative controls identify the genuinely unresolved decision as unmet. All gates
pass; no pair is skipped, and no citation is fabricated or selectively sanitized.

| Measure | Current writer | Writer with fulfillment evidence |
| --- | --- | --- |
| Shared passage changed, match removed, action-based decision retained | 2/2 | 2/2 |
| Date and Elena's realization preserved in main pairs | 2/2 | 2/2 |
| Exact clause-only restoration of the matched baseline | 0/2 | 0/2 |
| Original ending preserved in main pairs | 0/2 | 2/2 |
| Genuinely missing decision repaired, date realization preserved | Not run | 2/2 |
| Post critic accepts the revision | 2/2 | 4/4 |

The preservation exception works in this bounded case: evidence does not freeze a
defective sentence or prevent its necessary repair. This does not establish higher
assignment success than the current writer, since both arms succeed, or guarantee
minimal editing, since neither evidence arm simply deletes the offending clause.

At both seeds, the evidence-assisted writer replaces the shared sentence with a
paragraph showing Elena retrieve a journal and compare its handwriting with the
card. Seed 19101 explicitly withholds acceptance of the resemblance as proof. Seed
19103 ends the comparison with “She couldn't be sure. Not yet.” These are still
action-based decisions; neither requires an additional declaration of the decision.
The original closing paragraph stays unchanged in both evidence arms.

The current writer also turns the comparison into an inconclusive investigation.
It adds verification reinforcement to the ending in both cases: the need for
certainty at 19101, and a resolve to prove fraud or authorship at 19103. Those
additions are unnecessary for the assigned minimum but do not invalidate the repair.
The evidence-assisted rewrites also add description and interpretation within the
shared passage. The observed ending preservation is not a blind preference result.

Both negative-control writers remove the unresolved-choice language and commit to
checking the journals. Seed 19101 reaches for the drawer and intends to compare
the script to expose a possible fraud. Seed 19103 states that she will compare the
card to the journals and verify the handwriting. These are intentions, not completed
proof or a handwriting match. Both retain the dates and “Ten years.” realization;
their endings are rewritten to supply the genuinely missing decision.

Across the six revisions, every date realization remains fulfilled, every decision
is fulfilled and no match is established. All four embedded overruns are removed.

## Response replay and remaining qualifications

Seventeen of eighteen probes validate on their first call; all eighteen validate
finally. The sole retry is the seed-19103 overrun initial critic. Its generic boundary
restatement supplied separate recommendation text, which v59 rejects because the
consolidated finding owns the advice. The structural retry sets that field to null
while retaining both met native statuses, their citations and the overrun judgment.
There is no semantic reroll or writer retry.

All six post reviews have raw and canonical `pass` verdicts, twelve met native
checks, six met historical repair checks and six `no_overrun` boundary checks.
No independent issue, assignment violation or mandatory repair condition remains.
Full prose/diff inspection supports these classifications. Native decision evidence
uses the comparison actions or the new control decision; date checks cite the
future date, current date and the character's realization.

Every request, response hash, source binding, diagnostic clause audit, canonical
result, boundary audit and historical repair audit replays exactly. The writer
evidence packets contain the complete defective excerpt, unchanged policy and
correct draft/assignment/critique provenance. No packet certifies the negative
control's unmet outcome.

The initial overrun critics overstate that establishing the handwriting match also
establishes acceptance of the card as a genuine warning. The draft establishes the
match; acceptance is not separately established. The explicit no-match exit rule
independently supports the blocker, and the subsequent repairs are supported by
the prose without that extra inference. This limits the supporting explanation;
the run does not qualify all critic reasoning or ordinary production-v59 criticism.

Usage: **284,316 input / 21,980 output tokens**. The recorded-rate estimate is
**USD 0.04859624**, below the USD 0.23616 cap. Actual charges remain unknown.
The run uses six writer calls and thirteen critic calls, with no skips, full stories
or canonical changes.

## Interpretation and next focused step

Close this focused preservation-exception question as successful within the tested
matrix. The existing policy permits necessary changes inside cited fulfillment
evidence while retaining the fulfilled fact, and still allows repair of a genuinely
unmet requirement. No new writer instruction is justified by this result.

The next focused task should examine the smallest production integration of the
tested fulfillment-evidence handoff: use the latest validated critic assessment
bound to the exact current draft and assignment, retain all mandatory repairs, and
carry the existing necessary-edit exception unchanged. Identify the available audit
storage and provenance checks before choosing the implementation. Keep the critic
diagnostic separate; this result does not authorize promoting it or changing the
meaning of “met.” No production integration or additional cloud run was performed
or authorized by this completion.

## Limits and private evidence

This is a two-seed, one-provider, one-scene test with synthetic localized prose and
event/no-match wording. It combines fulfillment status, assessment, cited passages
and the existing preservation policy. The negative control has an evidence arm only.
It does not compare ordinary production-v59 criticism, establish general reliability
or authorize production integration.

Ignored private bundle:
`data/diagnostics/writer-preservation-exception-v59-2026-10-15/`.
It contains the runner, replay and local checks, six frozen initial requests,
baseline drafts, exact artifact identities, code hashes and protocol, explicit
approval, nineteen live response receipts, exact replay and independent semantic
inspection. Every dependent writer and post-critic request was frozen before sending.

Plan SHA-256:
`0c56d71a7d6c4ca12d2ba4166b6c0e4aab1cadd9812a2f8d550d3479cc277c7f`.
Source closure SHA-256:
`3f34490418c44f56ff3019c79b43fe0ea466b9f9716c76f9356e53e3813d6a2a`.

Explicit approval is recorded against the frozen plan. The closure hashes the
report and private evidence. Production remains v59; canonical stories and sealed
benchmark results are unchanged.
