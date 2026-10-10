# Decision versus inconclusive attempt: 2026-10-10

Historical inspection and twelve approved critic probes are complete. All twelve
responses validated on their first calls, but four missed the required date
revelation and one added a questionable outcome complaint. Production remains
v48 / graph v9, unchanged. Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## What the saved evidence establishes

The v45 `repair-19103` and `missing-turn` inputs share every noncandidate artifact,
generation setting and original repair test. Their handwriting-comparison and
replication passage is byte-identical. The control changes only three date-related
passages: the printed future date becomes today's date, the ten-year realization
becomes recognition of today, and the ending's future-date reference changes.

The actual outcome is a decision to verify handwriting, with no match established
by scene end. It does not require a second decision, a new verification method or
an explicit future commitment in the last paragraph. The critic's instructions
say actions and indirect realization count, prohibit demanding unassigned actions,
and permit inconclusive tests. The historical repair explicitly asks to preserve
inconclusive tests and restore unsettled suspicion rather than certainty.

The accepted response recognizes the comparison and replication as satisfying the
outcome. The control response acknowledges the inconclusive attempt but demands
a forward-looking decision to verify further. It correctly identifies the missing
future-date revelation, yet also uses that omission in its endpoint comparison.
This makes contextual spillover a plausible explanation, not an established cause.
Another possibility is a stricter reading of decision timing or explicit intent.

The prior campaigns show variation under different critic contracts, not repeated
independent measurements of one unchanged prompt:

| Campaign | Repaired draft | Missing-turn draft's assignment findings |
| --- | --- | --- |
| v41 | PASS | Outcome: alleges the wording establishes a handwriting match |
| v42 | PASS | Turning point only |
| v43 | PASS | Turning point only; overall REJECT |
| v44 | PASS | Turning point only |
| v45 | PASS | Turning point plus a demand for a future decision to verify |

All ten saved responses validated on their first calls. The v41 outcome complaint
differs from v45's: the former alleges premature confirmation, the latter missing
future intent. This is not one stable, recurring allegation. Overall verdict alone
cannot identify the problem; the missing-turn version should already require work
because its date revelation is absent.

## Experiment

Keep the current production critic and all useful story context. Cross two date
conditions with three decision wordings, at paired seeds 19103 and 19104:

| Wording | Future-date revelation present | Future-date revelation absent |
| --- | --- | --- |
| Existing actions; no added decision sentence | 2 probes | 2 probes |
| Explicit decision immediately before the unchanged comparison | 2 probes | 2 probes |
| Explicit decision to continue after the inconclusive attempt, at scene end | 2 probes | 2 probes |

The first wording preserves the exact saved drafts. The second adds one sentence
stating her decision to verify whether the handwriting is hers, immediately before
the unchanged comparison passage. The third instead adds one sentence committing
to continue verification before trusting the card, after the original ending.
These synthetic additions are diagnostic variations, not proposed canonical prose.

Each pair retains the same plan, Blueprint, bible, original draft and critique,
repair test, generation settings, system message and production policies. Only
the candidate prose and its derived version/evidence metadata change. All twelve
retain the exact verification passage. The second seed reverses the first seed's
six-condition call order. Calls are isolated; no earlier response enters a later
case's context. Seeds do not guarantee provider determinism.

Interpret results separately:

- More outcome complaints when the date is absent, at the same wording and seed,
  would support context-sensitive spillover as a behavior worth investigating.
- Acceptance after an explicit decision before the attempt would suggest that
  stating intent directly stabilizes interpretation of the existing action.
- Acceptance only after the final future commitment would suggest that the
  critic expects a future task, beyond merely deciding and attempting verification.
- If the original pair does not diverge again, record non-reproduction. Do not
  describe the sentence variations as fixing an unreproduced failure.

Inspect the actual allegations and cited passages. Record premature-match claims,
missing-decision claims and missing-future-commitment claims separately. Check that
the date defect remains detected, the original no-match repair stays met, and no
unrelated obligation is introduced. Separate first-attempt judgments from any
permitted structural retry; a formatting failure is not a manuscript defect.

This is one scene/model and two seeds per cell. Sentence placement, wording and
derived evidence handles necessarily differ. The absent date can legitimately
weaken motivation, so a narrower outcome complaint needs its own evidence. There
is no next-scene-reservation ablation or live missing-decision negative control.
This experiment cannot establish the model's internal reasoning or general
reviewer accuracy.

## Local verification and budget

Preparation verifies all twelve immutable requests, reversible single-sentence
edits, byte-identical verification prose, shared noncandidate context/settings and
the same original repair test. Four baseline replays (two cases at both seeds)
reproduce the saved v45 canonical results without modifying responses. Historical
response hashes and request/source hashes are retained. There are no application
code changes requiring a new full application test run.

- Destination: existing Ollama Cloud `gemma4:31b-cloud` through the local daemon.
- Maximum: **12 probes / 24 calls**, at most one structural retry per probe.
- Per call: up to 24,000 input / 8,000 output tokens.
- Recorded October 8 rates: USD 0.14/M input and USD 0.40/M output.
- Maximum recorded-rate estimate: **USD 0.15744**; actual charges unknown.
- No writer calls, full-story runs, semantic rerolls or canonical changes.

Private evidence and runnable harness are under
`data/diagnostics/decision-vs-attempt-v48-2026-10-10/` (ignored by Git).
The source database remains read-only with SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
Canonical stories and sealed benchmarks remain unchanged.

## Live results

The user approved the twelve-probe campaign. Exactly **12 calls** ran; every
response validated on its first attempt, so no structural retries occurred.
Exact requests, raw response hashes, canonical results and audits were replayed
and verified without edits. Original repair identity and source database hashes
remain unchanged.

| Decision wording | Future date present, two seeds | Future date absent, two seeds |
| --- | --- | --- |
| Existing actions | 2 PASS | 2 REVISE: one date finding only; one date plus outcome finding |
| Explicit decision before comparison | 2 PASS | **2 incorrect PASS**: date finding omitted |
| Explicit decision to continue afterward | 2 PASS | **2 incorrect PASS**: date finding omitted |

All twelve report `no_overrun` and mark the original premature-match repair met.
That is consistent with an inconclusive comparison and does not by itself prove
all current scene obligations were met. All generic issue arrays are empty. The
two reported date blockers create new repair targets; the extra outcome complaint
creates another distinct target. No original repair is reopened.

### What happened to the extra decision demand

At seed 19103, both unmodified drafts treat the existing verification actions as
satisfying the outcome; the control reports only the missing date. Thus the exact
v45 demand for a separately stated forward-looking decision does not repeat at
the original seed under current v48.

At seed 19104, the control adds an outcome complaint again. Its explanation shifts:
it acknowledges attempted verification, calls the comparison ambiguous, and says
the unsettled/suspicious exit state is not clearly achieved **because the future
date is absent**. Its recommendation asks for a decision to investigate further.
The final paragraph already describes suspicion and dread, unchanged from the
accepted counterpart except for its date reference. This is a recurrence of the
broader extra-demand pattern, with a different stated rationale, not a stable
requirement for future commitment established by these probes.

Both positions for an explicit decision pass, but the existing actions also pass
in every future-date case. The sample therefore does not justify requiring writers
to state decisions literally or end every scene with an explicit future task.

### A more concrete failure: an acknowledged defect is not routed

All four date-absent drafts with an added decision sentence pass with
`assignment_violations=[]`. Their achieved-state descriptions all recognize that
the card is dated today. Two additionally state that the plan expected a date ten
years ahead. Nonetheless, neither produces the required turning-point finding.
The original verification passage and missing-date edits remain unchanged.

These are missed mandatory turning points, not an ambiguity in handwriting
interpretation. The synthetic decision sentences do not restore the future date.
Their addition coincides with loss of date-defect reporting in both paired seeds.
This supports investigating interaction between obligation judgments; it does not
prove an internal attention mechanism or exclude effects of derived evidence
handles and small-sample model variation.

### Architectural explanation and practical conclusion

The critic receives separate planned obligations, but its response currently has
an endpoint comparison plus a list of violations it chooses to report. It is not
required to give a separate evidence-backed met/unmet assessment for every planned
turning point and outcome. Runtime validation checks declared findings, references
and original repairs; an empty violation list can still be structurally valid.
The application correctly avoids deriving semantic violations from free text.

The instructions already say that missing turning points require their own finding
and that mentions in boundary/repair assessments are not findings. The four false
passes demonstrate that this instruction alone does not reliably connect recognized
state to the separate blocking obligation. The questionable extra outcome finding
shows the opposite risk: one failed obligation supplies the rationale for another.

The strongest supported explanation is unstable separation of scene obligations,
with contextual spillover as a plausible mechanism. We cannot establish why the
particular v45 sample demanded a future decision. We can reject treating that demand
as a dependable creative requirement and identify a concrete coverage/routing gap
to address next. This investigation establishes neither a production fix nor
overall critic reliability.

Usage: **148,812 input / 11,062 output tokens**, estimated **USD 0.02525848** at the
recorded October 8 rates, below the approved USD 0.15744 maximum. Provider numeric
zero cost has an unknown basis; actual charges remain unknown. No writer calls,
canonical changes, full-story runs or production edits occurred. The private
`assessment.json`, `postcheck.json` and separately labeled `semantic-assessment.json`
preserve structural and manual assessments independently.

## Recommended next step

The next focused production candidate is separate evidence-backed assessment of
the assigned turning point and outcome within the existing critic response.
Require a judgment for each applicable obligation and route an unmet mandatory
one into a blocker consistently. Passing the outcome or satisfying an old repair
must not substitute for checking the turning point. A turning-point breach likewise
cannot prove a distinct outcome breach without evidence for that outcome.

This should remain one critic call, preserve action-based evidence of intent and
keep original repair tests distinct. It should not mandate explicit decision
sentences in stories or infer violations from keywords in reviewer prose. New
structured checks would make coverage and routing inspectable; their semantic
accuracy would still need qualification. Reuse these missing-turn cases as controls
when evaluating that change. No production change is made by this investigation.

Broader reviewer sensitivity, full-story recovery, preference and cost acceptance
remain open.
