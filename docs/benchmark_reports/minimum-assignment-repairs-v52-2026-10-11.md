# Minimum assignment repairs v52: 2026-10-11

Implementation, local checks and all twelve approved probes are complete. **The
minimum-repair instruction is not qualified as a fix.** Both matched missing-touch
repairs still prescribe causality, and one consolidated complaint still demands
completed entry. Both new pull-before-touch positives also receive unsupported
causal blockers. The decision-versus-completed-entry controls behave correctly.
Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Evidence and focused change

The [v51 comparison](first-review-comparison-v51-2026-10-11.md) eliminated observed
comparison-object retries while retaining the correct native check statuses. It
also retained stronger-than-assigned advice. Missing-touch repairs prescribed
contact before the psychic pull or as its immediate/direct cause, although the
plan required touch and a pull without specifying that mechanism. One repeated
complaint demanded the action of entering to satisfy a decision-to-enter outcome.
Consolidation retained these prescriptions in writer-facing recommendations.

Prompt v52 adds one shared critic instruction:

- Limit current assignment repairs, including generic restatements, to the missing
  assigned fact. Preserve fulfilled facts and the current scene endpoint.
- Do not infer order, immediacy or causality from "and", or require completed action
  when only a decision or attempt is assigned, unless an explicit applicable
  assignment or canonical rule requires it.
- Apply the same limit to assessments and comparisons, so an invented condition
  cannot enter through the explanation before it reaches the repair.
- State the minimum sufficient repair without prescribing an unassigned mechanism.
  Keep optional staging, motivation and craft suggestions out of mandatory repair
  text; label them optional and never use them as acceptance conditions.

The exact v50/v51 `OBLIGATION_RULE` remains unchanged, including complete-fact
fulfillment, independent checks, action/indirect evidence and blocker routing.
The v51 comparison-object clarification remains intact. The new instruction
reaches original reviews, revision reviews and the system message during structural
retries in local/cloud profiles. The targeted retry packet and policy 17 are
unchanged. Graph v9, output schemas, validation, consolidation, classification
retention, fixed historical repair tests, writer instructions and call allowances
are unchanged. No migration, dependency, API field or new specialist is added.

This is a prompt refinement within the existing critic contract. The application
does not decide whether a suggested mechanism is logically necessary, remove
recommendation text by keyword, or retroactively change valid reviews. Model
evidence is needed to evaluate whether the instruction improves advice.

## Local verification and preserved baseline

Eight new regressions cover first-review delivery and structural-retry delivery
under local/cloud profiles, including repeated and independent craft claims.
They check unchanged payloads, source inputs, classification metadata and canonical
materialization. The existing prompt-size test separately bounds the new rule at
675 characters, preserving the prior allowances. The delivered addition, including
its separating space, is **670 characters**.

All **29 focused regressions** pass. The full **946 Python tests**, Ruff
lint/formatting, strict mypy across **192 files**, frontend formatting/lint/type
checks, **11 frontend tests**, the production build and `git diff --check` pass.

All **twelve saved v51 responses** replay unmodified to identical canonical results
and evidence audits, including their stronger repair advice. Removing only the new
instruction reproduces all prior first messages and schemas exactly. The unchanged
met-definition string is verified against a saved v51 source copy. Previous v50/v51
evidence and the sealed source database retain their hashes.

This work continues the uncommitted v51 changes on the existing branch. Before
editing, the thirteen relevant baseline files were copied into the private
diagnostic directory and hashed. No previous report or sealed diagnostic output
is overwritten.

## Frozen diagnostic design

The experiment uses the same OH-V01-001 scene 1 source: formal Cloud v33 repeat 3's
sealed database, critic invocation `fdbc1392-549a-4ee6-9398-e1fb593e1c36`.
The database SHA-256 remains
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
The original plan requires touching the stroller and feeling a psychic pull,
followed by deciding to enter, with an exit at the threshold. Blueprint world rules
make the stroller a lure and anchor without requiring an immediate touch trigger.

Six cases ran at seeds **19101 and 19103**, in forward and reversed orders:

| Case | Draft and plan | Expected turn / outcome |
| --- | --- | --- |
| Complete baseline | Exact v51 touch-present, action-based decision draft and original plan | met / met |
| Both-missing baseline | Exact v51 absent-touch, unresolved-choice draft and original plan | unmet / unmet |
| Pull before touch | Same original plan; the pull begins before contact and does not change on contact; action-based entry decision retained | met / met |
| Decision while outside | Same original plan and touch/pull passage; choice to enter is settled, but both boots remain outside during a brief preparation | met / met |
| Explicit causality | Exact pull-before-touch draft; synthetic plan expressly requires the contact to immediately cause the first pull | unmet / met |
| Explicit entry | Exact decision-while-outside draft; synthetic plan expressly requires crossing with both feet and stopping just inside at the threshold | met / unmet |

The four requests across the two baseline conditions match saved v51 inputs,
settings and user messages exactly. Only the system instruction differs. The other
eight are new controls; no historical live v51 result is claimed for them.

Alternative drafts preserve the opening and all unrelated prose. One replaces only
the touch/pull sequence; the other replaces only the final decision paragraph.
The strict controls each change exactly one obligation field in both the Scene
Plan and embedded Blueprint plan, preserving the paired draft byte-for-byte. New
opaque artifact identities and a coherent initial Bible-to-Blueprint reference
mark their synthetic lineage. These plans are unapproved diagnostic contexts and
are never persisted to canon. No broader story context is removed.

Local preparation checks the exact paragraph substitutions, paired single-field
plan changes, artifact schemas, unchanged non-draft context in the ordinary-plan
cases, baseline request equality, source hashes, advisory length range, budgets
and call order. Condition labels and expected judgments are not model inputs.

## Inspection method

The primary advice check is the both-missing baseline. Its two legitimate blockers
should request the missing contact and settled entry choice while preserving the
already present pull and the scene endpoint. Inspection covered both native repairs
and the complete recommendations after consolidation; clean native wording is
insufficient if a repeated complaint reintroduces an extra requirement.

The alternative positive cases check that an unassigned order or completed movement
is not silently imposed during fulfillment assessment. The strict controls check
the converse: an expressly assigned cause or completed entry cannot be waived as
optional. Every unmet mandatory check still produces a blocker. Evidence, boundary
findings, independent craft and additional repair targets require separate review.

All 24 native checks, eight generic issues, consolidated repairs, cited passages,
paired drafts, original/synthetic plans and relevant Blueprint rules were read.
Semantic inspection compared assigned facts with the whole draft, rather than
grading by keyword. Bookkeeping code checks counts and replays; it does not assign
the semantic judgments.

## Observed results

All **12 first responses validated in 12 calls**, with **zero structural retries**.
All eight generic complaints supplied valid comparison objects and consolidated
into their native assignment findings. There were no independent craft findings,
separate assignment violations or boundary overruns. No live retry occurred, so
this run does not newly qualify retry behavior.

Both seeds produced the same native status pair for each condition:

| Condition | Observed turn / outcome | Assessment |
| --- | --- | --- |
| Complete baseline | met / met | Correct; no repair |
| Both-missing baseline | unmet / unmet | Correct missing-fact detection; repair advice still exceeds the assignment |
| Pull before touch | unmet / met | Incorrect; adds an unassigned causal requirement |
| Decision while outside | met / met | Correct; a settled decision does not require completed entry |
| Explicit causality | unmet / met | Correct; the expressly required causal relationship is absent |
| Explicit entry | met / unmet | Correct; the expressly required completed entry is absent |

Thus **10/12 native check pairs** match the inspected assignments, but this does
not establish successful repair advice. **Neither of the two matched both-missing
reviews keeps its complete repair recommendations within the assigned minimum.**

### The original repair-advice problem persists

At seed 19101, the native touch repair requires physical contact **"before the
psychic pull is triggered."** At seed 19103, it requires contact **"triggering the
psychic pull."** Neither relationship is assigned. The pull already exists in
both drafts; the required missing fact is contact.

Both native outcome repairs stay within the required decision: a definitive choice
or action committing Elara to entry is sufficient. However, the repeated generic
complaint at seed 19101 says to have her touch the stroller and then **"cross the
threshold."** It links to the turning-point finding while discussing both missing
facts, so that extra completed-entry requirement survives in the consolidated
turning-point repair. Inspecting only the native outcome repair would miss it.

The matched v51 reviews already exhibited causal over-prescription in 2/2 cases
and a generic completed-entry demand in 1/2. Native check pairs remain unchanged
in all four matched baseline requests. This provides **no demonstrated improvement
on the primary advice target**.

### Causality is added during assessment, before repair wording

The original turning point is "Elara touches the stroller and feels a psychic
pull." The new positive explicitly includes both facts but places the pull first
and states that contact does not change it. Neither the assignment nor the
Blueprint's lure/anchor rules requires contact to cause the pull.

Nevertheless, seed 19101 describes the conjunction as **"implying the touch is the
trigger"**. Seed 19103 rewrites it as **"and [consequently] feels a psychic pull"**.
Both mark the turn unmet and require a causal repair. The same drafts correctly
fail when the synthetic plan expressly requires contact to immediately cause the
first pull. The critic therefore fails to distinguish the ordinary conjunction
from that explicit causal assignment at both seeds.

These two extra blockers originate in native assignment interpretation. They are
not duplicate complaints introduced by consolidation: **10 repair targets** are
reported where **8** are supported by the inspected assignments.

### The entry distinction holds in the controlled drafts

Both outside-decision drafts pass under the original decision-only outcome. Both
fail under the synthetic outcome requiring both feet inside. Completed-entry
repairs are appropriate in those strict controls. This supports that distinction
in v52 while the both-missing baseline still contains the generic overreach above.

Two other explanations overstate context without creating additional blockers:
one boundary explanation says standing at the threshold must result from the
decision; one strict-causality repair appeals to anchor world logic as if that
alone established touch causation. The explicit synthetic assignment supports
causality in the latter case; the world rule alone does not.

## Interpretation and next focused step

The added instruction is present, but the critic still promotes an inferred
relationship to a mandatory fact. The observed assessments locate this problem
before repair generation; another reminder about polite or minimal repair wording
would not directly address it.

The next focused recommendation is to require support in the exact assignment or
an applicable canonical rule for any mandatory temporal, causal or completion
relationship. Inside the existing critic's assignment comparison, separate explicit
facts from inferred relationships before deciding that a fact is unmet or writing
its repair. Preserve actions and indirect narration as valid fulfillment evidence.
This is a proposed experiment, not an implemented or qualified remedy. No extra
agent, keyword filter, automatic semantic correction or additional call was added.

This is one scene and model, six cases and two seeds. It can test targeted advice
and fulfillment distinctions, but not the writer's response, other providers,
full-story quality or general reliability. Only the four baseline requests offer a
matched historical v51 comparison. Results on the eight new requests cannot
establish either improvement or regression caused by v52.

## Budget, billing and closure

Destination: the existing Ollama Cloud `gemma4:31b-cloud` deployment through the
local Ollama daemon, with the recorded model digest verified before inference.
Approved maximum: **12 probes / 24 calls**, with at most one existing structural
retry per probe and no rerun of a valid judgment. No writer calls, full-story runs
or canonical writes are included.

The per-call ceilings remain 24,000 input / 8,000 output tokens. The maximum estimate
is **USD 0.15744**, using the recorded October 8 rates of USD 0.14/M input and
USD 0.40/M output. Actual usage was **153,616 input / 13,206 output tokens**, giving
a reference estimate of **USD 0.02678864**. Actual charges remain unknown.

On October 11, the user reported that observed charges for the v50/v51 calls appear
somewhat below these estimates and will continue monitoring before concluding.
This is useful qualitative billing evidence, not an exact reconciled charge or a
new rate schedule. Keep the reference estimates and actual billing separate; no
historical cost values or budget ceilings are revised on this observation alone.

The user explicitly approved "Yes, run the twelve v52 probes" before inference.
The approval is bound to plan SHA-256
`9b802d344db47c21b43a1e9b96cfca2249f858893ec13ece26c68e3a73372622`.
All twelve raw responses replay unmodified to the saved results and audits, and
their requests reconstruct exactly. Frozen code, source database and prior sealed
evidence hashes still match. No writer calls, full-story runs or canonical changes
occurred; no additional live calls were made during analysis.

Private evidence is under
`data/diagnostics/minimum-assignment-repairs-v52-2026-10-11/`: `baseline-v51/`,
`baseline.json`, `experiment.py`, `prepared/*.json`, `offline-verification.json`
and `plan.json`; `approval.json`; `live/` requests, responses, results and runtime;
`assess.py`, `assessment.json`, `postcheck.json`; `record_semantics.py` and
`semantic-assessment.json`; and `closure.json` with evidence/report hashes.
Implementation and the bounded experiment are complete; the repair-scope defect
remains open. Step 19 is not complete.
