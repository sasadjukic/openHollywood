# First-review comparison-object clarification v51: 2026-10-11

The normal critic instructions now explicitly require each generic issue's
`assignment_comparison` to be the existing two-field JSON object. The v50 meaning
of met is unchanged. Local implementation and the twelve approved matched probes
are complete. All twelve reviews validate on the first response, compared with
3/12 under v50, and all native obligation check pairs and repair-target counts
remain unchanged. Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Reason and focused change

The [v50 transfer experiment](assignment-transfer-v50-2026-10-11.md) produced correct
mandatory check pairs in all twelve first responses, but only three complete
responses validated initially. All nine negative first reviews supplied a string
instead of the required comparison object. Each succeeded on its single structural
retry after explicit field/type guidance. The original first-review schema already
specified the object; this change addresses instruction delivery.

Prompt v51 adds the successful retry clarification to the existing critic's normal
instructions, introduced with "For every generic issues entry":

- `assignment_comparison` is an object with exactly two required fields.
- `finding_refs` is an array of distinct reported-reference strings.
- `assessment` is a nonblank string of at most 1,000 characters.
- A string, null, missing field or extra key is invalid.

The shape wording is shared with the targeted retry directive to prevent drift.
That directive's emitted text is identical to v50. The clarification reaches first
reviews of original drafts and revisions, in local and cloud profiles, and remains
in the system instruction during a structural retry. Graph v9 and critic retry
policy 17 remain unchanged because the targeted repair packet has not changed.

The complete-fact obligation module is byte-identical to v50: every assigned
condition must hold; similar dramatic purpose cannot replace a missing fact;
actions and indirect narration remain valid evidence. No literal plan wording or
explicit decision sentence is newly required. Existing schemas, validation,
classification retention, consolidation, repair links, writer instructions and
call/revision allowances are unchanged. This is a prompt refinement within the
existing critic contract, with no migration, dependency or API/client change.

## Local verification

Four new delivery regressions cover first reviews of original and revised drafts
under local/cloud profiles. They verify that removing just the added instruction
restores the prior system message, with unchanged user payloads and source inputs.
Existing retry regressions also check that first-review and targeted retry shape
wording match. All 54 focused v48-v51 regressions pass.

The existing critic-size guard initially rejects the intentional addition. Its
allowance is updated explicitly: the clarification is capped at 291 characters,
while the previous bound on all other guidance remains intact.

The full Python run reports **937 passed and that one obsolete size-bound failure**;
the corrected size-bound test then passes separately, covering all 938 collected
tests. No other failure remains. Ruff lint/formatting, strict mypy across 191 files,
frontend formatting/lint/type checks, all 11 frontend tests, the production build
and `git diff --check` pass. The full suite is not repeated after the test-only
allowance update; production code is unchanged from that run.

All **21 saved v50 responses** replay without edits: twelve identical canonical
results and nine identical structural rejections. Evidence and classification
audits match, as do the nine prior retry packets, including their directives.
All 116 previously sealed evidence files and the source database retain their
hashes. These checks establish compatibility, not model compliance with the new
instruction.

## Matched comparison

Reuse the exact twelve OH-V01-001 scene-1 cases from v50, with the same four draft
versions, source artifacts, seeds 19101-19103, order, settings and token ceilings.
Touch present/absent is crossed with an action-based entry decision or an explicitly
unresolved choice. The approved plan still requires touch plus a psychic pull,
and separately a decision to enter. No synthetic plan or repair history is added.

Every first user message, including the output schema, is identical to its saved
v50 counterpart. The only model-facing change is the **291-character addition** to
the system message. Request hashes, source hashes and current code are frozen.
The obligation module's byte identity is checked against the v50 plan.

The comparison measures first-response validity and malformed comparison objects
against v50's 3/12 first-valid responses. It separately inspects mandatory judgments,
assessments and cited evidence on every first and final response, including rejected
reviews, plus added boundary/craft findings, classification retention and duplicate
repair targets. It also records advice that demands more than the assigned minimum;
changing that advice is outside this patch.

This is a matched historical comparison on one scene/model, four authored drafts
and three seeds, not simultaneous experimental arms or twelve independent stories.
Even a clean result would not qualify general semantic accuracy, writer repairs,
cross-provider behavior, full-story repeatability, preference or cost acceptance.

## Execution boundary and evidence

The destination is the existing Ollama Cloud `gemma4:31b-cloud` deployment
through the local Ollama daemon, with the same recorded model digest. The maximum
is **12 probes / 24 calls**, allowing at most one existing structural retry per
probe. Never rerun a valid judgment. No writer calls, full-story runs or canonical
writes are included.

Each call retains 24,000 input / 8,000 output token ceilings. The maximum estimate
is **USD 0.15744**, using the recorded October 8 rates of USD 0.14/M input and
USD 0.40/M output. These are comparison rates, not a fresh current-price claim;
actual charges remain unknown.

Preparation made no model calls. The user then approved this exact v51 set:
"Yes, run the twelve v51 probes". Approval is bound to the frozen plan hash,
satisfying the earlier automatic approval review's requirement for revised private
payloads before transmission. The model digest verified before inference.

Private evidence is under
`data/diagnostics/first-review-comparison-v51-2026-10-11/`: `experiment.py`,
`prepared/*.json`, `offline-verification.json`, `plan.json`, `approval.json`,
`live/`, `assess.py`, `assessment.json`, `postcheck.json`, `record_semantics.py`,
`semantic-assessment.json` and `closure.json`. It references sealed v50 evidence
rather than overwriting it. All twelve new raw responses replay without edits,
with exact request reconstruction, canonical results and evidence audits.
Source artifacts, frozen requests, code and database hashes verify after execution.

## Results

| Measure | Saved v50 transfer | Matched v51 |
| --- | --- | --- |
| Valid first responses | 3/12 | 12/12 |
| Structural retries | 9 | 0 |
| Total calls | 21 | 12 |
| Final valid reviews | 12/12 | 12/12 |
| Native check pairs matching inspected facts, first and final | 12/12 | 12/12 |
| Extra repair targets | 0 | 0 |

All nine negative reviews still contain a generic assignment repetition. All nine
now supply the correct comparison object, with both fields and appropriate current
finding references, immediately. The improvement is not explained by omission of
the problematic generic issue. Consolidation leaves exactly one blocker for each
unmet obligation. No independent craft or extra boundary finding appears.

All six touch-present turns accept the physical grip and indirectly conveyed
directional compulsion. All six absent-touch cases recognize that the same pull
does not satisfy the missing conjunct. All six action-based entry decisions are
accepted using the preparation, braced hand, boot at the inner sill and forward
weight. All six unresolved-choice cases remain unmet; arrival at the threshold
does not replace a decision. The three both-missing cases retain two independent
blockers. Every boundary check remains no overrun. The three complete positive
drafts pass and the nine incomplete drafts require revision.

These are stable native statuses and repair-target counts, not identical review
prose or reasoning. The three both-missing cases change generic labels or selected
assignment links between fresh reviews. One moves from major to blocking severity;
all nine v51 generic repetitions are blocking. In seed 19103's both-missing case,
one generic complaint discusses both defects and lists both comparison refs while
selecting the turning-point link. Its text joins that target; the separate outcome
blocker remains. There is no third repair target, but that merged recommendation
mentions both repairs. No live v51 structural retry was needed, so this run does
not add fresh evidence about retention within retries.

Usage is **150,528 input / 13,881 output tokens**. The recorded-rate estimate is
**USD 0.02662632**, below the USD 0.15744 cap and compared with USD 0.04826186 for
the saved v50 run. Actual charges remain unknown. Unknown-basis zero estimates
in provider receipts are not evidence of free billing. No writer/full-story calls
or canonical changes occurred.

## Interpretation and next focused step

Keep v51's compact clarification and the existing meaning of met. On this matched
sample, the clarification eliminates all nine observed formatting retries while
preserving the required-fact distinctions and repair-target counts. The source,
schema, settings and case isolation support this narrow result. A historical
comparison on one model and four drafts does not establish general reliability.

Repair advice remains a separate concern. Every missing-touch review prescribes
contact before the pull or as its immediate/direct cause, although the plan assigns
touch and a pull without separately requiring that mechanism. The Blueprint calls
the stroller a lure and anchor; it does not establish an immediate touch trigger.
Seed 19101's both-missing generic repair explicitly asks for the action of entering
to satisfy an outcome that only requires deciding to enter, with the exit at the
threshold. These stronger prescriptions survive consolidation into writer-facing
repairs. Correct missing-fact detection does not qualify that extra specificity.

The next focused candidate is to keep repair recommendations tied to the minimum
assigned fact, distinguishing an optional implementation from a mandatory condition.
Controlled cases should test whether different valid timing/causality and a clear
entry decision without completed entry remain acceptable, alongside missing-fact
controls. This change and any additional calls are not implemented or authorized
here. No full-story, preference or cost-acceptance conclusion is drawn.
