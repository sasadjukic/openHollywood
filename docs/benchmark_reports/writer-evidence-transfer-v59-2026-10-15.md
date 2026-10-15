# Writer fulfilled-evidence transfer, fixed v59 — 2026-10-15

Status: **DIAGNOSTIC COMPLETE — INITIAL-REVIEW GATES STOPPED THE WRITER COMPARISON.**

The approved protocol completed after **six first-attempt-valid critic calls**.
Both deletion-only baselines passed. All four overrun reviews correctly detected the
forbidden match, and both missing-date controls correctly detected the absent future
date. However, all four also marked the already expressed decision to investigate
as **unmet because the later endpoint was exceeded**. The protocol therefore skipped
all twelve dependent probes: no writer or post-critic calls were made.

This does **not** establish success or failure of the evidence treatment on this
scene. It identifies an earlier obstacle: the current review does not certify the
fulfilled decision that this transfer test intended to preserve.

This repeats the [fulfilled-evidence comparison](writer-fulfilled-evidence-v59-2026-10-15.md)
on OH-V01-002 scene 1. The earlier OH-V01-001 result was 2/2 exact deletion-only
repairs with evidence versus 0/2 with current context; both missing-decision controls
still repaired their defects. That result does not establish transfer to other scenes.

Source commit: `cdcc54889b0694953fcc1824a10f3c77da540fcd`.
Branch: `codex/writer-evidence-transfer-v59`.
Production and critic stay **prompt v59 / graph v9**. Main is unchanged.
Six authorized cloud calls were made; no production or canonical artifacts changed.
Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Different scene and a genuinely unmet fact

Elena examines a birthday card dated exactly ten years in the future. The saved
`repair-19103` draft expresses her decision to investigate through deliberate
handwriting comparison and replication. The comparison remains inconclusive.

The primary draft appends one separate sentence:

> After one final comparison, she established beyond doubt that the handwriting on the card matched her own.

Deleting that sentence restores the previously accepted prose exactly. A fresh v59
baseline review must first accept the deletion-only version, including its indirect
decision, before dependent probes at that seed proceed.

The negative control uses the earlier `missing-turn` draft. Its three date passages
describe today's date rather than a ten-year difference; its handwriting actions
are identical. Append the same forbidden match sentence. A successful repair must
restore the required future-date realization and remove the match while preserving
the valid action-based decision. This is a missing turning-point control, rather
than repeating the first scene's missing-decision control.

The older synthetic plan bundled the decision and no-match endpoint in one outcome.
For this experiment, move the exact existing sentence “No handwriting match is
established by the end of this scene.” from `outcome` to `exit_state`. Keep the
decision as the outcome. Both obligations remain mandatory; separating their plan
fields allows the existing native outcome check and boundary check to assess them
independently. Apply the same change to both Scene Plan views and update synthetic
Blueprint/Bible identities. Every other plan/Blueprint/Bible field stays intact.

Use fresh revision-zero diagnostic drafts and current initial reviews. Do not feed
legacy critiques into the writer or reconstruct old responses as fresh evidence.
This intentionally excludes historical-repair context from this transfer. All
changes are private synthetic artifacts; no canonical story is modified.

## Unchanged treatment and bounded matrix

Import the prior packet builder, provenance binder and request projection unchanged.
Only treated writers receive `revision_contract.latest_fulfilled_requirements`, with
the same policy, current review/draft/source versions, met assessments and exact
cited passages. Keep all actual repair advice, artifact context, role instructions,
schemas and settings. Critics receive no added packet.

At each seed, 19101 and 19103:

| Stage | Probes | Purpose |
| --- | ---: | --- |
| Deletion-only baseline critic | 1 | Confirm both requirements met and no overrun under v59 |
| Overrun initial critic | 1 | Confirm both requirements met, but boundary overrun |
| Current/evidence writer and post-critic pairs | 4 | Same initial review and draft; only evidence field differs |
| Missing-date plus overrun initial critic | 1 | Confirm unmet turning point, met outcome and overrun |
| Evidence writer and post-critic control | 2 | Repair necessary defects without needless decision restatement |

Total: **18 probes**, comprising six initial critics, six writers and six post-critics.
Counterbalance current/evidence writer order across seeds. The two primary writers
at each seed receive the same actual initial review; extra valid criticism remains
visible and is assessed as a potential confound. The missing-date control receives
evidence for the outcome only, with no new current-context control arm.

Require the declared baseline verdict/checks before dependent reviews. Require each
initial review to identify the expected native checks and overrun with `revise`
before writers. Skip and report unsuitable chains; never reroll a valid judgment or
fabricate favorable feedback. Post-review only validated writer output. Allow one
structural retry per probe and one prose revision per writer case. Freeze every
dependent request before sending it. No replacement cases or full-story runs.

Maximum: **36 calls / USD 0.23616** using the recorded October 8 rates of USD 0.14/M
input and USD 0.40/M output, at 24,000 input / 8,000 output tokens per call. Actual
charges remain unknown. Use the existing `gemma4:31b-cloud` deployment and frozen
model digest; writer temperature 0.85, critic 0.2, top-p 0.95, thinking disabled.

## Local verification and assessment

- 24 no-network mock calls cover the complete 18-probe matrix, a writer structural
  retry retaining its evidence, permanent writer/post-critic failures and an unchanged
  negative control that still fails both repairs.
- Four scheduler checks exercise baseline failure, initial failure, unexpected
  classification and writer failure. Dependent stages are skipped as specified.
- Ten invalid evidence/provenance mutations are rejected. All original repair tests
  survive the writer projection, and post-critic requests remain ordinary v59.
- 45 focused regressions pass in 26.17 seconds. Repository Ruff, formatting and
  strict mypy pass for 198 source files; diagnostic formatting/error checks pass.
- Verify 1,569 previously sealed files and their reports, the historical source
  database, both imported scene drafts and current production hashes.

The frozen assessment protocol was to replay all sent requests and raw outputs,
and inspect full prose and
diffs as well as judgments. Primary observations are exact deletion-only restoration,
retention of the original verification passage, preserved date facts/motivation, and
any unnecessary explicit decision restatement. The control must acquire the missing
ten-year realization and lose the match without losing its valid decision. Record
first/final validity, native/historical checks, advice, verdicts and skips separately.

This is a second-scene test with two seeds and one provider, a synthetic endpoint
and fresh review context. Status, assessment, evidence and preservation policy remain
a combined treatment. Traceability alone does not establish semantic correctness.
It does not test an excerpt that fulfills one requirement while containing another
defect, and does not authorize production integration or claim general story quality.

## Live findings

| Draft condition | Native turning point | Native decision outcome | Boundary | Canonical verdict | Count |
| --- | --- | --- | --- | --- | ---: |
| Accepted inconclusive investigation | Met | Met | No overrun | Pass | 2/2 |
| Same prose plus definitive match | Met | Unmet | Overrun | Revise | 2/2 |
| Missing future date plus definitive match | Unmet | Unmet | Overrun | Revise | 2/2 |

Both baselines identify retrieving the journal, comparing flourishes and replicating
the script as valid evidence of deciding to investigate. Those actions remain
unchanged in both overrun conditions. All four defective-draft reviews acknowledge
that Elena performs verification, but use the forbidden later match to mark the
decision outcome unmet. This classification is present in the **raw model response**;
the application did not turn a met outcome into an unmet one.

Under this protocol's independently scoped checks, the decision is fulfilled and
the no-match exit requirement is violated. The scene should still require revision.
The observed interpretation appears to treat the outcome status as compliance with
the combined outcome/exit state, even though the synthetic plan separates them.
That is an inference from the explicit assessments, not a claim about hidden reasoning.

The missing-date control works as a detection control: both critics cite the two
2024 dates and require the ten-year gap. **Necessary writer repair remains untested**,
because the control's valid decision was also marked unmet and its writer gate failed.

All four raw defective-draft verdicts were `reject`; existing v59 materialization
normalizes these repairable cases to `revise`. They failed the declared gate on
outcome status, not on verdict normalization. All six calls were structurally valid
on the first attempt; there were no retries, transport failures or rerolls.

One secondary observation is retained: `s19103-preserve-initial` yields two canonical
blocking outcome-category issues about the same match, one from the native outcome
plus generic restatement and one from the boundary check. The other overrun reviews
consolidate that allegation. This is not a demonstrated independent craft defect.

Every sent request, raw response and resulting audit was reconstructed and replayed.
Sources and frozen code remain unchanged. Usage: **115,472 input / 8,364 output tokens**,
for a **USD 0.01951168** estimate at the recorded rates. Actual charges remain unknown.
Only six of the permitted 36 calls were used; twelve of the planned 18 probes were
skipped by the declared eligibility rules.

## Next focused recommendation

Keep production v59 and the evidence projection unchanged. Test whether explicitly
scoping native fulfillment to its own assigned requirement prevents a separate
boundary violation from erasing a fulfilled decision. The boundary must remain a
blocker, and genuinely missing facts or decisions must remain unmet. This would
qualify the evidence source before repeating dependent writer comparisons.

Do not force met statuses in application code or carry the baseline's certification
forward to a changed draft. The current-draft evidence packet must represent the
actual latest validated review. No further cloud experiment is authorized here.

## Private evidence

Bundle: `data/diagnostics/writer-evidence-transfer-v59-2026-10-15/` (ignored locally).
The bundle contains the runner, replay/assessment script, no-network fixtures, six
frozen initial requests, baselines, check receipts, dependent-stage protocol,
explicit approval, all six live receipts, replay assessment and semantic inspection.

Frozen plan SHA-256:
`25b2d6bc8bd2f4baf099992224f41e5012e5ef8d116da60e050b355a02948c91`.

Prior fulfilled-evidence closure SHA-256:
`7e0fef0d5426be9790b7ed8487ab066dbbbbb1128dac2248a96beed9e6dbdae2`.

The user's explicit approval is recorded against the frozen plan. The final closure
hashes the report and the private evidence bundle; prior sealed evidence remains intact.
