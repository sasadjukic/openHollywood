# Ordinary-critic fulfillment comparison: frozen plan

Date: 2026-10-16. Status: **PREPARED AND LOCALLY VERIFIED; AWAITING LIVE APPROVAL.**

This prepares step 5 of the fulfillment handoff work. **Zero live model calls**
have been made. The authorized work is preparation, not execution. Implementation
baseline: `c1bacab638e91dadfd69016ac9226b4885e0f10f`, prompt **61**, graph **9**,
handoff policy **1**. See [ADR 0037](../adr/0037-durable-writer-fulfillment-handoff.md).

The question is whether ordinary production critics supply usable native evidence,
and whether carrying that evidence helps a writer preserve fulfilled facts and
their expression while repairing real defects. Earlier diagnostic-critic successes
are source material, not qualifying critic results for this experiment.

## Execution plan

1. Obtain approval for this exact frozen plan. Reverify implementation, sources,
   cases, requests and model digest. Record approval against the plan hash before
   constructing a live gateway. A changed implementation, case, model, budget or
   request rule requires a new plan; do not quietly substitute one.
2. Run all twelve initial reviews using unchanged ordinary production critics.
   Keep every structurally valid judgment, including unexpected findings and failed
   eligibility gates. Only the existing one structural retry is allowed.
3. Apply the gates below. For eligible paired cases, construct both writer requests
   from the same actual review and source draft. Check that the fulfillment field
   is their only model-visible difference. Save and hash each exact request before
   dispatch. Run the independently eligible unmet controls with evidence only.
4. Run one ordinary post-critic per validated revision. Retain the original review
   and every repair acceptance test. Critics receive neither treatment labels nor
   fulfillment packets. A writer failure skips its dependent review.
5. Replay all responses through the frozen production validators, inspect complete
   prose and diffs, account for every attempt and skipped dependency, reverify
   source integrity, and seal a results report. Decide whether a separate full
   workflow canary is justified. That canary is not included in this approval.

## Frozen cases and matrix

Seeds: **19101 and 19103**. Each row below runs at both seeds. Source fiction and
synthetic assignments come from the sealed
[OH-V01-001 comparison](writer-fulfilled-evidence-v59-2026-10-15.md) and
[OH-V01-002 exception test](writer-preservation-exception-v59-2026-10-15.md).
These remain diagnostic contexts, not newly approved canonical Story Blueprints.

| Case | Initial critic requirement | Dependent stages per seed | Total probes |
| --- | --- | --- | ---: |
| Elara clean baseline | Touch/pull and decision met; outside boundary retained; pass | None | 2 |
| Elara separate entry defect | Both anchors met; forbidden entry detected; revise | Current writer + post; evidence writer + post | 10 |
| Elena clean baseline | Future-date realization and verification decision met; no match; pass | None | 2 |
| Elena embedded match defect | Both anchors met; forbidden match detected; revise; shared citation | Current writer + post; evidence writer + post | 10 |
| Elena genuinely missing decision | Date realization met; decision unmet; no overrun; revise | Evidence writer + post | 6 |
| Elena genuinely missing date and realization | Turning point unmet; decision met; no overrun; revise | Evidence writer + post | 6 |
| **Maximum** | **12 initial critics** | **12 writers + 12 post-critics** | **36** |

The Elara defect is the separate sentence, “She stepped across the sill and entered
the building.” Removing it and its separator restores the frozen clean baseline.
The existing decision is expressed through motivation and preparing to enter while
both boots remain outside. Touch and psychic pull are both required; no new causal
or temporal relation is introduced.

The Elena assignment remains the earlier synthetic event-scoped wording: she
realizes the date is exactly ten years in the future; during the scene she decides
to verify the handwriting; no handwriting match is established by scene end.
The clean action sentence is:

> She pulled her old journal from the desk drawer and laid it beside the card to check whether the handwriting was her own.

The embedded case replaces its final period with a semicolon and the existing
forbidden-match clause. The entire resulting sentence is one evidence excerpt.
The actual initial review must cite that same complete excerpt for both the met
outcome and the boundary defect. Do not sanitize it, substitute a cleaner excerpt,
or fabricate a citation. Deleting the entire sentence also deletes the only decision.

The missing-decision control retains the earlier explicit unresolved-choice passage.
The new missing-date control starts from the same clean Elena draft and makes exactly
three declared substitutions: card date 2034 to 2024; “Ten years.” to “The same date.
Today.”; and the ending's ten-years-in-the-future phrase to “her own birthday”. It
retains the action-based decision and establishes no handwriting match. Both the
future date and its realization must be restored; restoring only a date is insufficient.

## Gates and comparison rules

- A paired case requires its own expected ordinary-critic classification and its
  matching clean baseline's pass at the same seed. The embedded case also requires
  the shared citation described above. A failure skips both paired writer arms
  and their post-critics. Report the failure as critic eligibility/coverage, not
  writer failure or handoff success.
- Each unmet control depends on its own expected classification and valid evidence,
  independently of clean-baseline results. Its packet may contain only the other,
  fulfilled anchor. A partially met compound requirement is never certified.
- Initial reviews all run first, in seed order and the table's case order. Then
  eligible cases run in the same order. Paired writers run current/evidence at
  seed 19101 and evidence/current at 19103; each writer is followed by its post-critic.
- Both arms use prompt 61 and identical ordinary repair advice, settings, assignment,
  prior draft and actual Critique. The current arm omits only
  `revision_contract.latest_fulfilled_requirements`; the evidence arm receives the
  production projection and exact policy. No diagnostic critic adapter is imported.
- Preserve all actual incidental craft findings and mandatory repairs. No advice
  rewriting, semantic rerolls, replacement seeds/cases, second prose revisions,
  extra critics, continuity/adjudication calls or full-story runs are allowed.
- Source-response replay, provenance mismatch, omitted/oversized packet, or request
  mismatch stops that dependent path. Record the reason; never patch the source
  judgment or truncate a quotation to make the path eligible.

All native evidence is fallible. Schema validation and a correct hash establish
traceability, not semantic truth. Full-prose inspection must still identify a
misclassified initial or post-review rather than treating it as a successful result.

## Request and source freeze

Local private bundle:
`data/diagnostics/production-fulfillment-v61-2026-10-16/`.

- `cases.json`: all six full input sets, exact artifact identities/content and
  benchmark constraints. Both seeds share identical case inputs.
- `prepared/`: **twelve complete initial requests**, including messages, schema
  delivery mode, model, settings, budgets, invocation context and source hashes.
- `experiment.py`: frozen ordinary request construction, output replay, eligibility
  gates, production fulfillment projection, paired writer construction and post-review
  construction. Its CLI has only `prepare` and `verify`; neither opens a gateway.
- `local_check.py` and `local-check.json`: reproducible offline checks with socket
  connection attempts blocked; these fixtures are not live model evidence.
- `plan.json`: limits, dependency rules, hashes of 109 implementation/configuration
  files, cases, all initial requests, local checks and the two source closures.

**Frozen plan SHA-256:**
`03da1a013fc86a4a1a142d561d11fc001ab219ee252c55b64c72b4c0ed60bf18`.

The exact writer and post-critic bodies cannot exist before their upstream outputs.
Their construction code, permitted inputs, gates and retry rules are frozen now.
Each actual body must be saved and hashed before sending, including any structural
retry. No mock response may become a live source review.

Preparation made three explicit context choices. First, it starts each case at
revision zero with new diagnostic identities and canonical-shaped artifact keys;
old current-scene review history is not imported. Second, it corrects inherited
OH-V01-001 metadata on the historical Elena snapshots to OH-V01-002. Third, it uses
the full respective corpus constraints for every case, including required elements
and forbidden shortcuts missing from the historical Elena initial-request metadata.
The prose and assignments are unchanged except for the declared case variants;
the Bible's Blueprint pointer is rebound to the new diagnostic identity. Both
Blueprint and standalone Scene Plan views agree. No canonical database is changed.

This isolates **production projection and writer-request behavior**. It does not
execute a durable production graph or establish new SQLite lifecycle evidence.
Step 4's real SQLite tests cover that implementation; step 6's proposed full workflow
canary remains separate. Do not describe these isolated requests as full workflow
qualification or evidence about a later revision with historical review loops.

## Model and budget

| Limit | Frozen value |
| --- | --- |
| Provider path | Existing local Ollama daemon forwarding to Ollama Cloud |
| Model | `gemma4:31b-cloud` |
| Expected recorded digest | `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e` |
| Sampling | Writer 0.85; critic 0.2; top-p 0.95; thinking disabled |
| Maximum probes / attempts | 36 / **72**, including one structural retry per probe |
| Per-call token allowance | 24,000 input; 8,000 output |
| Aggregate token reservation | 1,728,000 input; 576,000 output |
| Existing application per-call cost field | USD 0.20; unchanged, not evidence of a billed charge |
| Recorded-rate estimate | **USD 0.47232 maximum at October 8 rates**, assuming token allowances hold |
| Time bounds | 900 seconds per call; 64,800 active seconds total worst case |

The estimate uses the previously recorded USD 0.14/M input and USD 0.40/M output.
No current price or billed-spend ceiling is asserted. The adapter reports unknown
dollar costs, and input-token overages are detected after a response. Actual charges
remain unknown; an observed token overage stops further dispatch and is reported.
The model digest must be verified before generation; a recorded local digest and
matching seeds do not guarantee deterministic hosted inference.

Before each call, durably reserve a unique probe/attempt slot and its full token/time
allowance. Count failed, cancelled and unknown-outcome attempts against the ceiling.
Never reuse an occupied slot or convert skipped probes into extra calls. There are
no automatic transport retries. Stop on integrity, model, authentication, transport
or budget failure. A restart must inspect the ledger; only definitely unsent slots
can proceed. The preparation tool does not itself implement a live dispatcher;
execution must follow these frozen operator limits using the existing probe runner.

## Assessment and subsequent story-quality work

Report coverage first: twelve initial reviews, four possible paired comparisons
and four possible unmet controls. Report structural failures and each failed gate,
packet omission, retry and skipped dependency with the original denominator.
Partial coverage cannot qualify the entire planned matrix.

For every revision, inspect all prose and compare it with its starting draft. Record:

- Whether the supplied defect is actually repaired and every previously fulfilled
  fact survives. In the embedded case the defective excerpt must change while the
  decision survives. For controls, inspect the genuinely missing fact directly.
- Exact deletion-only/clause-only restoration, preservation of the indirect
  expression, added explicit restatement, ending changes and unrelated rewrites.
  Record repairs justified by actual craft feedback separately from unnecessary edits.
- Every native check, original repair test, current finding, recommendation,
  boundary judgment, raw and normalized verdict, including unsuccessful attempts.

For complete narrow behavioral qualification, all four paired cases and four
controls must be evaluable; all eight evidence-treated revisions must repair their
defect, retain fulfilled facts, meet the remaining supplied repairs, and pass their
ordinary post-review, with no independently observed false success. Report paired
preservation wins, ties and losses separately. A tie does not establish improvement;
a harmful preservation tradeoff prevents a positive handoff recommendation.

Preservation counts and small diffs are diagnostics, not literary-quality scores.
A met passage can still need better voice, characterization, dialogue or pacing.
The necessary-edit exception and independent craft feedback remain intact. The
offline craft fixture verifies feedback transmission only; if no live critic raises
such a finding, report that live craft-edit behavior was not exercised. Later story
quality work needs a stable baseline, the accepted rubric and blind human comparison.
This small, synthetic, one-provider experiment cannot establish general quality,
human preference, Local/Hybrid behavior or whole-story acceptance.

## Local verification

- Reverified **483 sealed source files** (195 + 288) and their report hashes.
- Reconstructed and verified all twelve frozen requests. Validated all six cases'
  artifact schemas, matching Blueprint/Scene Plan views and UTF-8 text.
- Passed **36 offline stage fixtures**, four paired request comparisons, twelve
  retry-request checks, unmet/baseline/shared-citation failure gates, and two
  independent-craft feedback checks. Identical revised prose yields identical
  post-critic requests across arms. The complete defective quotation survives.
- Passed **91 focused regressions** in 62.68 seconds: production handoff, ordinary
  v59 critic semantics and isolated probe tests. Tests used fake gateways outside
  the Windows sandbox so asyncio could create its local loopback sockets.
- Passed repository Ruff lint/format and strict mypy for 201 files; the two private
  preparation scripts pass Ruff formatting and syntax/undefined-name checks.
- Production, frontend, contracts and dependencies are unchanged. The full suite
  and production build passed in step 4; this preparation repeats the relevant
  Python checks rather than claiming a fresh full-suite/build run.

The offline fixture preparation initially assumed that ordinary critics lacked
`critic_requirement_scope`, attempted a model-authored boundary repair condition,
and omitted the boundary link from a simulated independent craft comparison. These
fixture assumptions were corrected against the production validator before freezing;
production semantics were not changed. The final preparation reconstructs exactly.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.** Preparation is complete;
live qualification, full workflow canary and story-quality evaluation remain pending.
