# ADR 0020 Inactive review advice projection

- Status: Accepted
- Date: 2026-10-08
- Qualification: Offline checks pass; live assessment does not establish semantic recovery

## Evidence and hypothesis

[ADR 0019](0019-inactive-continuity-recurrence-and-counterevidence.md) records a
repeated-verification blocker in OH-V01-002 despite an empty current recheck set.
The approved scene assignment requires handwriting verification as its turning
point. An older continuity report asks the writer to remove that sequence.

The continuity request projects every older blocking finding with its summary,
source references, repair recommendation and historical recheck disposition.
That projection does not distinguish inactive findings from current obligations.
The latest report and active IDs are separately correct. The older repair is
not canon, but remains visible beside the current assignment.

This establishes a context path for obsolete advice. It does not establish that
the path causes the model's judgment. The allegation summary itself, other
context, or the model's treatment of repeated events could also matter.

## Decision

Use production prompt v36 / graph v9 on `codex/continuity-history-v36`.
Change only the continuity supervisor's projection of older reports:

- Determine activity from all blocking IDs in the latest report, including
  requirement findings. Advisory appearances do not count as active blockers.
- For an inactive finding, omit `recommended_resolution` and the historical
  `recheck_disposition`; mark `active_in_latest_report: false`.
- Preserve its ID, allegation summary, category, basis, requirement/World Rule
  references, source references and original report version.
- Keep active historical entries, the complete latest report and the original
  allegation ledger unchanged. Active repair guidance remains available.

An inactive finding is not automatically resolved, invalidated or correct. The
application still retains complete immutable reports and performs identity,
recurrence, changed-evidence and hard-gate validation with that complete context.
Only the model-facing projection changes. Genuine reintroduced assertions remain
eligible to block under the existing rules.

System instructions, output schema, model settings, retry policy, budgets,
revision limits, writer/critic prompts and adjudication context are unchanged.
No new model call, workflow node, schema migration or dependency is introduced.
The projection is opt-in at the continuity request builder; adjudication keeps
its existing unfiltered history projection.

## Offline verification

Eleven new regression cases cover mixed active/inactive history, advisory latest
findings, missing-requirement blockers, Local and Cloud message delivery,
unchanged canonical/evidence context, and preservation of original advice in
persisted artifacts after a complete simulated production workflow. The v35
recurrence and bounded repair tests remain in the suite.

All 654 Python tests and 11 frontend tests pass. Ruff lint/format, strict mypy
on 168 files, frontend formatting/lint/type checks, production build, and
`git diff --check` pass.

Read-only reconstruction reproduces all four saved v35 request hashes. The v36
comparison proves equal output schemas and system messages; the only payload
differences are the prompt contract version and inactive history projection.
The same synthetic controls retain exactly their v35 fixture IDs and hashes.

| Frozen request | v35 characters | v36 characters |
| --- | ---: | ---: |
| 002 | 39,958 | 39,683 |
| 002 contradiction control | 40,107 | 39,832 |
| 010 | 40,479 | 40,479 |
| 010 contradiction control | 40,666 | 40,666 |

002's system message stays at 9,398 characters; 010's stays at 7,155. These are
complete message character measurements on the four cases, not token estimates
or a universal size guarantee. The 010 pair has no older history, so its message
content changes only in the version label and provides a comparison for ordinary
remote-model variation.

Local reconstruction code, baseline source and packets are stored under
`data/diagnostics/v36-continuity-history-2026-10-08/`. The immutable source snapshot
remains SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

## Bounded live assessment

The assessment reuses the four exact frozen inputs/controls described
in ADR 0019, existing Ollama Cloud Gemma4 deployment, settings and seeds, with at
most two attempts per probe and eight total calls. At the dated October 8 rates
and existing token allocations, the maximum published-rate estimate is
USD 0.05248, assuming uncached input. Actual charges remain unknown.

Automatic approval review rejected the first launch because it treats the v36
review context as a new private payload requiring explicit permission. No
inference occurred in that rejected launch. The user then explicitly approved
the v36 payloads, destination and limits. The probes ran at approximately
15:48 Europe/Belgrade on October 8, using Ollama 0.35.1 and the same alias digest
as v35. Structured model output is saved separately from validated reports to
preserve the model's selected-claim explanation for assessment; it is unvalidated
source data, not an additional accepted artifact.

All four probes validated on their first attempt: four calls, no structural
retries, 39,300 input tokens and 3,838 output tokens. Live request hashes match
the offline packets; saved model-output hashes match the corresponding result
records. The source database hash is unchanged.

| Probe | Input / output tokens | Estimate, USD | Retained findings |
| --- | ---: | ---: | --- |
| 002 frozen draft | 9,590 / 1,043 | 0.00175980 | One repeated-verification blocker |
| 002 contradiction control | 9,630 / 1,032 | 0.00176100 | One blocker for the injected denial |
| 010 frozen draft | 10,016 / 789 | 0.00171784 | Two advisories; no blocker |
| 010 contradiction control | 10,064 / 974 | 0.00179856 | One blocker for the injected assertion; one advisory |

Total published-rate estimate: **USD 0.00703720**, assuming uncached input at
the same dated rates as ADR 0019. Actual charges remain unknown. Inherited
numeric-zero cost fields are unknown-cost placeholders, not billing evidence.

## Interpretation and next boundary

Removing the old repair instruction did **not** clear 002's false-positive
concern. The model generated a similar recommendation without seeing the old
one. Its explicit explanation infers that repeating verification means Elena
has forgotten her earlier discovery. The cited established fact proves prior
verification; it does not prohibit repetition. Its current evidence does not
establish the inferred forgetting, and its explanation does not reconcile the
approved scene's verification turning point. Narrative redundancy may warrant
craft advice, but it is not itself a pair of incompatible facts.

The old allegation summary remains in context, so this experiment does not rule
out influence from historical framing. It tests removal of repair advice and
stale disposition, together with an inactivity marker. No single component's
causal effect is isolated. In the 002 control, the model correctly focuses on
the affirmative denial and no longer emits the repeated-verification complaint.

010 clears on this call, although its review content changed only in the version
label and it had no history for this fix to alter. This is not evidence that
removing historical advice repaired 010. The differing result cautions against
attributing single-call changes to this intervention. Its positive control
still blocks the injected claim, but the model's explanation again conflates
the code back-door with the physical manual override. It truncates the denial's
scope when comparing them. Correct blocker detection does not establish a
correct explanation or repair prescription.

The projection change provides a clearer boundary between historical advice and
current obligations. Its implementation is tested; improved semantic accuracy
is **not demonstrated**. Preserve this experiment without rerolling it or
expanding to full-story runs. The next focused question is whether inactive
allegation summaries anchor the current review, versus the model independently
treating repeated actions as incompatible facts. That requires a separately
scoped comparison preserving canon, scene assignment, active rechecks and the
application's full recurrence history. Do not solve it by accepting every plan
action or dismissing every recurring finding automatically.

No sealed benchmark, canonical story, historical cost or acceptance gate is
changed.

Step 19 remains IN PROGRESS. Step 20 and the creative-quality sequence have not
started. Full-story testing remains deferred on this evidence.
