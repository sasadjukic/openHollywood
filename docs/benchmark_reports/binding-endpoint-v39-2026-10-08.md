# Binding the current scene endpoint: implementation and probes

Date: 2026-10-08. Prompt v39 / graph v9.

**Retaining a more specific later detail does not authorize an earlier result
under the new shared policy. The live critic still misses the original overrun.**
It acknowledges a conclusive handwriting match but labels the comparison
preliminary, then passes the scene because the next scene retains a stronger
revelation. Clearer instructions alone did not change the verdict in this trial.

## Implementation

[ADR 0023](../adr/0023-binding-current-scene-endpoint.md) makes the current
outcome/exit state independently binding on substantive plot and knowledge
changes. The existing writer and critic receive the same compact policy:

- A decision, an attempt and an established result are distinct states.
- Later detail or stronger proof does not authorize an earlier result.
- Setup, foreshadowing, guesses, inconclusive tests and incidental follow-through
  are allowed when they do not establish a result beyond the current endpoint.
- Explicit current-plan instructions can authorize overlap; a broad goal or
  summary cannot override a specific endpoint.

The critic's existing current-endpoint comparison must identify any authorizing
plan field and instruction. Its five-field response contract remains unchanged.
The application now permits an `overrun` whenever the current outcome or turning
point supplies an anchor, including final scenes and missing next reservations.
Previously this route also required an explicit next reservation.

A valid reported overrun forces revision despite perfect craft scores. Repair
guidance asks for removal of unassigned material advancement, not merely one
later detail of an already established result, and includes the next reservation
only when one exists. No-overrun judgments cannot clear independent blockers;
malformed comparisons remain bounded response-repair errors.

The application validates structure, source identity and applicability. It does
not interpret free-text comparisons to override the model's status. This change
does not establish that the model follows the policy.

Graph v9, repair guidance v10, profiles, budgets, retry/revision limits, canonical
schemas and API/client contracts are unchanged. No new role, call, dependency or
migration is introduced. Against v38, the seven critic requests grow by 251
characters each, and corresponding writer requests by 254. For these populated
endpoint cases, the output schemas are identical; message differences are the
shared policy and critic instruction. These are sample size measurements.

## Verification

Eleven new cases cover Local/Cloud schemas with present, absent and final
reservations; high-score blocking and exact evidence; optional reservation
guidance; shared policy in initial/revision requests; permitted simulated
inconclusive tests and follow-through; explicit current authority over overlap;
and a persisted final-scene revision with replay. Existing v38 applicability
tests now check for a missing current anchor rather than a missing next scene.
These simulated judgments verify routing and contracts, not literary judgment.

Checks passed: **697 Python tests**, Ruff lint/format, strict mypy (171 files),
frontend format/lint/type checks, **11 frontend tests**, and production build.

## Approved live experiment

The first five cases preserve exactly the v38 input versions and content hashes:
the original OH-V01-002 scene-1 overrun, proper stopping, permitted foreshadowing,
verification correctly assigned to scene 2, and a missing-turn control.
See the [v38 report](critic-boundary-v38-2026-10-08.md) for their preceding results.

Two new, isolated controls distinguish legitimate progress:

1. **Preliminary investigation:** the proper-stopping draft gains an attempted
   comparison of one copied letter. Skipping ink and a smudge make it explicitly
   inconclusive. The draft still ends with the decision to compare journals
   tomorrow. Only the draft receives a new synthetic version and hash.
2. **Authorized overlap:** the original overrun prose is unchanged, but the
   current outcome explicitly assigns verification of the private script while
   withholding acceptance of the future warning. The standalone and Blueprint
   scene-1 plans agree; the initial Bible's Blueprint reference follows the
   synthetic Blueprint version. Those three artifacts receive new versions and
   hashes. The next reservation is unchanged.

These controls are unapproved diagnostic contexts, not changes to the real
approved plan or canonical story. Their source hashes remain recorded separately.
The second control tests this particular overlap; it does not establish that
every kind of intentional repetition will be handled correctly.

The user approved seven probes, at most fourteen calls including structural
repairs, with a maximum published-rate estimate of **USD 0.09184**. All seven
validated on their first calls. No structural repairs, semantic rerolls, writer
generation or full-story runs occurred.

The existing Ollama 0.35.1 daemon forwarded `gemma4:31b-cloud` to Ollama Cloud's
`gemma4:31b`, retaining alias digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Per-call limits were 24,000 input / 8,000 output tokens, with source seeds and
settings preserved. The alias does not guarantee immutable remote weights or
deterministic reproduction.

Prepared/live request hashes, artifact hashes, captured/raw response hashes,
exported comparisons and the approved plan hash all verified. The read-only
source snapshot remains SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
The principal source critic invocation is
`d2758b4f-7a66-4587-b7c6-fc5386ff20b6`. Canonical stories, sealed campaigns and
historical results were not modified.

## Results

| Probe | v38 | v39 | Assessment |
|---|---|---|---|
| Original scene-1 overrun | PASS | PASS | Missed overrun |
| Proper stopping | PASS | PASS | No boundary false positive |
| Permitted foreshadowing | PASS | PASS | No boundary false positive |
| Verification assigned to scene 2 | PASS | PASS | No boundary false positive |
| Missing-turn control | REVISE | REVISE | Correct independent assignment blocker; extra broad plot claim |
| Inconclusive preliminary test | Not run | PASS | No boundary false positive |
| Explicitly authorized overlap | Not run | PASS | No boundary false positive |

Every response returns `no_overrun`. The single positive overrun case is missed;
the five legitimate-progress controls have no boundary false positives. This
does not demonstrate a functioning distinction: an always-no-overrun judgment
would produce the same boundary results. All passes receive three 5/5 scores;
the missing-turn control retains a 3.67 mean.

The original scene's achieved-state assessment explicitly says the journal
comparison concludes that the handwriting is identical, while labeling the
comparison preliminary. Its current-endpoint assessment says that the decision
to verify and suspicious exit state are achieved. It does not examine the extra
established result or cite a current-plan instruction authorizing it. The
next-scene assessment again relies on the reserved private flourish and full
acceptance of the warning.

This differs from v38's explicit admission that the endpoint was exceeded; v39
instead describes the requirement as satisfied. Both versions retain the same
verdict. The evidence is consistent with the critic checking that an assigned
outcome happened while failing to enforce where the scene must stop. It does
not establish the model's internal causal mechanism.

The original selected evidence shows the journal comparison, the future becoming
a trap, and the evidence of Elena's own hand. These references resolve correctly,
but the explicit identical-match sentence is not selected in this response.
Reference validity therefore remains separate from completeness of support.

The authorized-overlap control selects that identical-match sentence and correctly
ties verification to the changed current outcome. Yet the same prose passes
without that authorization too. This pair does not establish sensitivity to
whether verification is permitted.

The preliminary-test control passes, but its summary and selected evidence focus
on the final decision to investigate tomorrow, not the inserted inconclusive
attempt. It shows absence of a false positive, not explicit recognition of the
attempt/result distinction.

The missing-turn control correctly blocks replacement of the ten-year-future
date with today's date. It also claims this removes the speculative element
and existential dread altogether. That is broader than the demonstrated
assignment violation and should not be counted as an independently established
defect. The current change does not address this criticism-quality weakness.

## Cost and next question

The seven calls used **74,937 input / 4,778 output tokens**. At the recorded
October 8 [Gemma4 rates](https://ollama.com/library/gemma4:31b-cloud), assuming
uncached input at USD 0.14/M and output at USD 0.40/M, the published-rate estimate
is **USD 0.01240238**. Actual charges remain unknown. The gateway's zero numeric
placeholder with `cost_basis: unknown` is not evidence of free billing.

Local evidence is under `data/diagnostics/binding-endpoint-v39-2026-10-08/`:
the v38 executor snapshot, fixture/preparation and run scripts, hash-frozen
`prepared/` requests and plan, complete `live/` responses, and `assessment.json`.

The next diagnostic question is whether the later reservation still anchors the
judgment, or whether the critic independently treats achieving the assigned
decision as sufficient even when a result follows. A bounded comparison with
only current-endpoint context would help separate those explanations before
adding more instructions. Another possible response-contract change is to
require separate judgments for achieving the assignment and exceeding it;
neither further change is implemented or tested here.

Fresh writer compliance, full-story recovery, repeatability and multi-provider
behavior remain unqualified. **Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**
