# Inactive allegation summary experiment — 2026-10-08

Status: completed diagnostic; no production-context change adopted.
Branch: `codex/continuity-summary-experiment`.
Production remains prompt v36 / graph v9 at source commit
`28b97e6b0171406b7982267525c5adcc6a8ca8a2`.

**Result:** all three conditions block the original draft at all three seeds.
All three positive controls correctly block the injected denial. The model can
reconstruct the repeated-verification objection without inactive review history;
removing that history does not improve the observed verdict in this case.

## Question

Does inactive review history induce the repeated-verification blocker in
OH-V01-002, or can the model reach that conclusion without seeing the earlier
allegation? [ADR 0020](../adr/0020-inactive-review-advice-projection.md) found that
removing the old repair instruction did not remove that blocker, but the old
allegation summary remained visible.

This is a diagnostic comparison, not a proposed production change. No prompt
instructions, output schemas, validation gates, runtime limits, canonical
artifacts or workflow routing are changed.

## Predeclared design

Use the exact frozen 002 scene-2 revision-2 input and the same synthetic positive
control as v35/v36. The control appends an explicit claim that the handwriting
never matched Elena's private script, contradicting the established match.
Its diagnostic artifact ID/content hash remain unchanged from the earlier probes.

| Condition | Model-visible history | Original request characters | Control request characters |
| --- | --- | ---: | ---: |
| A: current | Complete v36 history projection, including the inactive summary | 39,683 | 39,832 |
| B: no summary | Remove only `summary` from inactive historical findings | 39,590 | 39,739 |
| C: no inactive findings | Omit inactive historical entries; this case has none remaining, so omit `continuity_history` | 39,304 | 39,453 |

Keep the complete history in application memory for identity, recurrence and
changed-evidence validation in every condition. A historical ID assigned after
the response does not imply the model saw that history. Preserve active findings
and repair instructions in all transformations. In this frozen case the latest
report and original-allegation ledger are empty, and the required active recheck
list is empty. The canon still states that verification happened earlier; it
must remain visible in every condition.

Use three matched seeds for the original draft and one seed for each positive
control: 12 probes, each with the existing maximum of one structural retry.
All conditions retain the v36 version label, system text, schema, model/profile
and all other request settings. Rotate order to reduce order confounding:

| Trial numbers | Stimulus | Seed | Condition order |
| --- | --- | ---: | --- |
| 1–3 | Original | 19204 | A, B, C |
| 4–6 | Original | 19205 | B, C, A |
| 7–9 | Original | 19206 | C, A, B |
| 10–12 | Contradiction control | 19204 | C, B, A |

Run this fixed set once. Do not reroll a condition until it passes or expand the
sample based on favorable results. Seeds and a stable alias do not guarantee
identical remote inference. Three paired observations are a within-case
diagnostic, not a statistical estimate across stories, models or providers.

## Verification before inference

The offline harness reconstructs both exact saved v36 message hashes. Every
condition has the same system message (9,398 characters), and all non-history
payload fields are equal, including the unchanged version label. Request settings,
budgets, schema delivery and exact input lineage remain equal within each seed.
The original source inputs are not mutated. Synthetic transformation checks
verify that active repair guidance survives and unrelated canon is unchanged.

Checks also establish that B and C contain no copy of the removed allegation
sentence elsewhere in the packet, and C contains neither that old finding ID nor
the history field. The full Story Bible claim, current scene assignment, accepted
prior prose and candidate evidence remain present.

Prepared packets and the fixed trial manifest are under
`data/diagnostics/continuity-summary-experiment-2026-10-08/`, with the completed
packets in `offline-verified/` and the predeclared sequence in `plan.json`.
The source database is read-only, SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

## Budget and approval

Destination: the existing Ollama Cloud `gemma4:31b-cloud` deployment through the
local daemon. The payload contains the private frozen 002 inputs and its existing
contradiction control, with the model-facing omissions above.

Maximum: 24 calls at the existing 24,000 input / 8,000 output token allocations.
Using the October 8 Gemma rates recorded in ADR 0019, with uncached input, the
maximum published-rate estimate is **USD 0.15744**. Actual charges remain unknown.
Estimate fields will be calculated from recorded token usage separately from
the runner's unknown-cost placeholders. Historical cost evidence is unchanged.

The previous automatic approval review required explicit permission for modified
private payloads. The user explicitly approved this 12-probe set, its destination
and limits before execution. No additional approval rejection occurred for this
experiment. All 12 calls then ran in the predeclared order.

## Assessment criteria

Assess both the validated result and the separately captured model-authored
structured explanation. Record, for every trial:

1. Whether validation succeeded, on which attempt, and any terminal review error.
2. Whether the original draft is blocked specifically for repeating verification,
   including whether the explanation infers forgetting without contradictory text.
3. Any other blocker, so disappearance of one allegation is not mistaken for a
   completely accepted scene.
4. For controls, whether the injected denial itself is detected using the relevant
   canonical assertion and exact candidate evidence, rather than merely counting
   any blocking verdict as success.
5. Token usage, latency, request/response hashes and the separate rate estimate.

Compare paired outcomes by seed, rather than selecting the best condition's
single result. Repeated objections in C show that prior allegation text is not
necessary for that judgment in this context; they do not rule out an additional
influence from history in A. Consistent improvement in B versus A supports a
summary influence within this case, subject to sampling variability. Improvement
only in C suggests that residual historical metadata may matter. Loss of control
detection prevents treating a quieter review as an improvement.

## Results

| Condition | Repeated-verification blocker on original | Injected contradiction detected | Other blockers |
| --- | ---: | ---: | ---: |
| A: current history | 3/3 | 1/1 | 0 |
| B: inactive summaries omitted | 3/3 | 1/1 | 0 |
| C: inactive findings omitted | 3/3 | 1/1 | 0 |

At seeds 19204, 19205 and 19206, every A/B/C original-draft response produced
exactly one blocker for the repeated verification. There were no other findings.
The explanations compare the current investigation with the established earlier
match and infer that the character treats it as a first discovery. C makes this
inference without receiving the earlier allegation, its ID or its metadata.

All three controls produced exactly one blocker for the injected denial, citing
`draft_evidence_0055` and the established handwriting-match claim
(`canonical_source_0067` after materialization). Their explanations correctly
contrast an established match with an assertion that it never matched. The
repetition allegation did not also appear in these controls. This changes which
defect the model selects, but does not make the original repetition a supported
factual contradiction.

All 12 responses validated on attempt 1: **12 calls, zero structural retries**.
Total usage was **114,632 input / 12,758 output tokens**. The published-rate
estimate is **USD 0.02115168** with uncached input, below the predeclared
USD 0.15744 allocation estimate. Actual charges remain unknown; the runner's
numeric-zero cost fields remain unknown-cost placeholders.

Runtime was Ollama 0.35.1 through the same `gemma4:31b-cloud` alias and remote
`gemma4:31b` deployment, with digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Every live request hash matches its prepared packet, every captured structured
response hash matches its result record, and the frozen database hash remains
unchanged. The predeclared `plan.json` hash remains
`b706f750babe50771b2d9a6ccd739377d28f7871830c05edcc36574d95c19362`.
`assessment.json` records all inspected classifications, per-trial counts,
latencies, estimates and hashes. Classifications come from inspection of the
captured reports and exact evidence, not a further model call.

## What the comparison answers

Prior allegation text is **not necessary** for the objection in this frozen
context. No paired verdict improves when summaries or inactive findings are
removed. There is therefore no demonstrated semantic benefit from further
history removal here. This does not prove history can never influence the model,
that every repeated action is misclassified, or that other stories/providers
would behave the same way. It also does not identify which combination of the
remaining story evidence and instructions produces the judgment.

The model is independently identifying a real repetition concern and assigning
it a disputed factual-contradiction label. Its explanations infer first discovery
or lost knowledge; the cited candidate assertions do not explicitly deny the
earlier investigation. An earlier match and a later recheck can both be true.
The approved scene assignment itself requires the later verification. The
repetition can remain poor writing without establishing incompatible story facts.

## Additional read-only finding: scene boundaries

Inspection after completing the fixed experiment located a concrete upstream
overlap in the exact approved Blueprint
`cb842774-1f37-4612-8cf3-ef71972f8092`:

| Stage | Approved plan | Observed accepted/current prose |
| --- | --- | --- |
| Scene 1 | Turning point: the future date. Outcome: Elena decides to verify the handwriting. | Its accepted ending already compares the card with a five-year-old journal, attempts to replicate the script, and concludes it matches. |
| Scene 2 | Turning point: verification of a private flourish. Outcome: accepting the warning. | It performs the comparison and authenticity discovery again. |

Two complete sentences in scene 2 (`draft_evidence_0014` and
`draft_evidence_0015`) occur verbatim in the immediately prior accepted ending,
artifact `9deb29b1-bada-4c8b-9790-25a654f6c1d8`. The surrounding investigative
actions also overlap. Thus the system is not inventing the repetition from
historical review prose: actual story material supplies it. This observation
does not establish why the earlier draft was accepted or why the next writer
repeated the wording; those require tracing the relevant production decisions.

The next focused technical investigation should examine the checks that accepted
scene 1 after it performed work assigned to scene 2. The writer and scene critic
own compliance with the scene's intended endpoint and narrative progression.
The continuity supervisor should distinguish a repeated dramatic action from
an incompatible assertion. Existing future-scene-material and planned-outcome
checks should be inspected before adding new roles, longer prompts or retries.
Do not delete established canon, make all repetition acceptable, or automatically
downgrade every recurring continuity finding to force these probes to pass.

## Disposition

Keep production at v36. The summary omissions were applied only by the diagnostic
request wrapper; they are not application changes. No full-story or formal
campaign rerun followed. No canonical or sealed artifact changed.

The matched-request preflight, synthetic projection checks, response/source hash
verification and document whitespace checks passed. Application code was not
changed, so the existing v36 lint/type/unit/integration/build verification was
not rerun for this diagnostic-only change.

The specified investigation is complete. **Step 19 remains IN PROGRESS**:
full-story completion, repeatability, preference and cost acceptance are not
established by these probes. The story-quality implementation sequence has not
started.
