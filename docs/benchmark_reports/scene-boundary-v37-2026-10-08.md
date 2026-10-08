# Shared scene boundary: implementation and isolated probes

Date: 2026-10-08. Prompt v37 / graph v9.

**Implementation complete; overrun detection remains unqualified.** The writer
and critic now share a compact current endpoint and next-scene reservation.
Five authorized Cloud critic probes validated, but the critic still passed the
original scene-1 overrun. This is not a recovered story or a formal acceptance
result. Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Change and responsibilities

[ADR 0021](../adr/0021-shared-scene-boundary.md) records the decision.

The context compiler builds `scene_boundary` from the exact current Scene Plan
and approved Blueprint already bound to the invocation. It references the
current assignment's outcome and exit state, then exposes only the immediately
next scene's central turn and outcome. Selection uses scene number, not list
position. The final scene has no next reservation. Missing information does not
produce an invented reservation; ambiguous next-scene matches fail.

Both existing roles receive the same boundary, including on revisions. The
writer must stop at the endpoint. The critic must compare the achieved ending
with the boundary in its existing summary and report supported overruns through
the existing assignment gate, even when the current obligation is also achieved.
Setup, foreshadowing, guesses, incidental follow-through, and explicitly approved
overlap or repetition remain permitted. This is a semantic judgment, not a
keyword prohibition.

Their current-scene Blueprint projections omit the global `story_arc` and defer
`proposed_ending` until the final scene. Current plans/beats, applicable world
rules, character context, approved style and canonical Bible remain available.
No stored artifact is edited. Continuity, Bible maintenance and critic
adjudication keep their existing responsibilities and context projections.

There is no new agent, model call, output field, schema, migration or API/client
contract. Model profiles, budgets, retries, revision limits, exact evidence
validation, hard gates and Blueprint approval remain unchanged.

## Offline verification

Eleven new test cases cover Local/Cloud delivery, identical writer/critic
reservations, initial/revision scope, exact version identities, source
immutability, reordered plans, missing/ambiguous next assignments, final-scene
context, intentional overlap, and simulated review judgments. A persisted
workflow verifies that a reported overrun requests revision, carries the same
boundary and repair test forward, and replays without duplicate calls.

The simulated overrun remains blocking with a 5.0 craft mean. Simulated passing
judgments for stopping, foreshadowing and correctly assigned verification acquire
no automatic keyword blockers. These tests verify application behavior; they do
not establish model understanding.

All 19 measured historical request projections are shorter than v36 by 145–633
characters, with identical output schemas. The sample includes 18 critic inputs
covering initial, revision and final scenes, plus the exact original scene-1
writer inputs. For the source case:

| Request | v36 characters | v37 characters |
|---|---:|---:|
| Scene-1 writer | 16,500 | 16,170 |
| Scene-1 critic | 37,209 | 36,576 |

These are message-character measurements for this sample, not guaranteed token
savings across all stories or providers.

Final checks passed: Ruff lint and format (169 files), strict mypy (169 files),
pytest (665 tests), frontend format/lint/type checks, Vitest (11 tests), and the
production build. An initial full run exposed two old wording assertions, which
were updated to the equivalent condensed guidance, plus one worker-cancellation
failure during a premise call. The latter did not recur in the focused worker
run or the second full suite; no unrelated worker change was made.

## Approved probe design and provenance

The user explicitly approved five isolated critic probes, up to ten calls
including one structural retry per probe, and a maximum published-rate estimate
of USD 0.06560. No writer generation or full-story run was included.

Source database, opened read-only:
`data/benchmarks/v0.1/formal-cloud-v33-repeat-3-2026-10-02/private/completed-snapshot.db`.
Its SHA-256 remains
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

The two unmodified inputs come from OH-V01-002:

- Scene-1 critic invocation `d2758b4f-7a66-4587-b7c6-fc5386ff20b6`, reviewing
  draft `9deb29b1-bada-4c8b-9790-25a654f6c1d8`.
- Scene-2 initial critic invocation `cc71e86c-303f-48a5-a6f4-99f654c66e2c`.

The scene-1 boundary names current plan
`ebe18f4b-7da8-5bd0-a2d6-db11ae2ceb1a` and next reservation `scene_2` from approved
Blueprint `cb842774-1f37-4612-8cf3-ef71972f8092`. The current outcome is the decision
to verify; the next turn is verification of a private flourish and the next
outcome is acceptance of the card as a genuine warning.

Three synthetic, unapproved scene-1 drafts are kept only in local diagnostics:

1. **Proper stopping:** replace the early claim of an exact handwriting match
   with uncertain familiarity; replace the journal comparison and replication
   with a decision to investigate later.
2. **Permitted foreshadowing:** add speculation about discovering a private
   flourish, explicitly leaving the comparison unperformed.
3. **Missing-turn control:** change the properly stopping draft's future date
   to the current date and remove its ten-year realization.

Synthetic drafts receive distinct version identities and content hashes; source
versions remain immutable. These controls test specific distinctions, not a
complete scene rewrite or an estimate of literary quality.

Requests retain the source model settings and 24,000-input/8,000-output per-call
token limits. The existing Ollama 0.35.1 daemon routes `gemma4:31b-cloud` to
`https://ollama.com:443`, remote model `gemma4:31b`. Alias digest:
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
An alias digest does not guarantee immutable remote weights.

Prepared/live request hashes, source artifact hashes, response hashes, plan hash
and unchanged database hash all verified. Full model responses are preserved
separately from materialized critiques in local diagnostic files.

## Results

All five probes validated on the first call; no retries or further sampling ran.

| Probe | Verdict | Craft mean | Assignment finding | Expected distinction |
|---|---|---:|---|---|
| Original scene-1 overrun | PASS | 5.0 | None | **Missed premature verification** |
| Proper stopping | PASS | 5.0 | None | No overrun alleged |
| Permitted foreshadowing | PASS | 5.0 | None | No overrun alleged |
| Verification assigned to scene 2 | PASS | 5.0 | None | No overrun alleged |
| Missing-turn control | REVISE | 3.67 | Blocking `scene_assignment:turning_point` | Missing future-date realization detected |

The original overrun's summary claims the scene ends with the decision to verify.
Its dramatic-progress rationale explicitly praises comparison with a journal,
and its character-consistency rationale mentions the mathematical match. Thus
the model acknowledges the completed comparison while still treating the scene
as correctly stopping at the decision. It returns no assignment violations or
other issues. It does not explicitly reconcile this with the next reservation.

The other three passing probes contain no issues. The missing-turn control cites
the actual current-date statements and recommends restoring the ten-year
discrepancy. No hard gate was weakened to obtain these results.

Total usage: **53,809 input / 2,497 output tokens**. Applying the dated October 8
[published Gemma4 rates](https://ollama.com/library/gemma4:31b-cloud), assuming
uncached input at USD 0.14/M and output at USD 0.40/M, gives **USD 0.00853206**.
Actual charges are unknown. The gateway records `cost_basis: unknown`; its
numeric zero is not evidence of free billing. This estimate is separate from
historical costs and cannot close the cost-acceptance gate.

Local evidence: `data/diagnostics/scene-boundary-v37-2026-10-08/`, including the
preserved v36 executor, `compacted/` request comparisons, `prepared-v2/` exact
requests and plan, `live/` responses, and `assessment.json` hash/usage audit.

## Interpretation and next target

The implementation supplies the context that was previously missing and makes
responsibilities explicit. **Supplying that context plus a summary instruction
was insufficient on the original overrun.** This does not establish why the
model ignored or misapplied it. Broad current-scene wording about attempted
debunking and the presence of the correct current turn remain possible factors.
The results cannot isolate the effect of boundary visibility from removal of
global plot prose or the revised instructions.

The next focused candidate is a small, required, evidence-backed boundary
assessment inside the existing critic response: identify what the draft actually
establishes and compare it with the current endpoint and next reservation before
deciding whether an overrun occurred. That would make a missing comparison
observable and validate its evidence, while semantic correctness would still
need controls. It is not implemented or tested by this change.

Do not treat these calls as proof of writer improvement, repeatability,
multi-provider performance or full-story recovery. No additional probes or
formal reruns were launched to seek a better result. Technical stabilization and
Step 19 remain IN PROGRESS; creative-quality Step 20 has not started.
