# Writer preservation during minimal repair, v60 — 2026-10-14

Status: **EXPERIMENT COMPLETE — NO PRESERVATION IMPROVEMENT; NOT PROMOTED.**

The previous [fixed-v59 experiment](indirect-decision-preservation-v59-2026-10-14.md)
found that both writers repaired the boundary but also rewrote an already valid
indirect ending. Both deletion-only controls passed. This change tests whether a
compact writer clarification reduces that unnecessary editing without preventing
repair of a genuinely missing decision.

Start from `a01c33270125fc2a0c8abdc0ff6f1a58d8f272a9` on
`codex/writer-minimal-repair-v60`. Main remains v59. Step 19 is IN PROGRESS;
Step 20 is NOT STARTED.

## Implementation scope

Add only this paragraph to the existing writer instructions:

> If deletion alone repairs an independent defect, delete it and preserve the existing wording that fulfills other requirements, including actions and indirect decisions. Change that wording only when needed to repair a remaining defect; do not add explicit restatement merely to emphasize fulfillment.

The addition is 292 characters; writer instructions grow from 638 to 930
characters. The existing instruction-size test allows a bounded 320-character
addition. Shared production prompt metadata advances to **60** for reproducibility;
graph version stays **9**. Three runtime version expectations update accordingly.

The critic's instructions, schema, meaning of met, source validation, consolidation,
repair tests, evidence and verdict gates remain unchanged. Six exact historical
critic message/schema pairs compare identically, and their raw responses replay
to identical canonical results and audits. The two saved writer requests differ
only by the new system-text paragraph; prose, feedback, user payload, schema,
settings and budgets are identical. Shared version metadata changes do not imply
a critic-guidance change.

No new role, field, call, retry, revision allowance, dependency, migration or public
API/client contract is introduced. Existing bounded repair and canonical authority
rules still apply. This is guidance, not an automatic exact-wording acceptance gate.

## Frozen comparison

Use private OH-V01-001 scene 1 context and seeds **19101 / 19103**. Keep the plan
requiring touch and psychic pull without an assigned relationship, a decision to
enter, and an explicit outside-at-scene-end boundary. Retain the source Story Bible,
broader context and next-scene reservation. These plans remain synthetic diagnostic
controls, not canonical approvals.

| Case per seed | Input and feedback | Calls before structural retries |
|---|---|---|
| Preservation | Exact v59 overrun draft, saved canonical boundary review and seed | Writer, then critic: 2 |
| Missing decision | Same accepted source, with its final paragraph replaced by explicit indecision | Initial critic, unchanged control critic, writer, post critic: 4 |

Total: **12 probes, at most 24 calls**. Four writer revisions are planned.

The preservation case has an independently valid indirect decision followed by a
separate forbidden entry sentence. Reuse its exact saved feedback; do not obtain
fresh first reviews that would change the comparison. Compare generated prose with
both the accepted deletion-only baseline and the sealed v59 writer outputs.

The missing-decision case keeps all preceding paragraphs, including touch, psychic
pull and an outside position. Replace only its final paragraph with:

> She looked from the passage to the path back to the road. She stayed behind the sill, unable to settle whether to go inside or walk away. Both boots remained in the daylight.

This removes the preparatory actions and positive decision reasoning and explicitly
retains indecision. Its initial critic should keep the turning point met and find
the outcome unmet without an overrun. Run dependent stages only after a validated
revise review marking that outcome unmet. Retain all actual canonical feedback
unedited, including unexpected additional criticism. Otherwise record the failure
and skipped branch; no replacement case or reroll.

The unchanged control repeats the missing-decision prose as revision 2 under the
fresh feedback history and should still require revision. Its result does not gate
the writer. The writer must actually supply the decision, through actions or direct
narration, while remaining outside. Post-review runs only for valid writer output.
Freeze every dependent request before sending it. Writer and critic retain the
same assignment, boundary and historical repair tests through normal compaction.

## Assessment declared before generation

- Primary preservation measure: exact deletion of the appended overrun restores
  the accepted baseline. Separately inspect indirect expression, fulfilled facts,
  motivation, unnecessary restatement, unrelated prose and final position.
- Missing-decision repairs must establish a decision; preserving indecision is a
  failure. Do not require any particular form of decision wording or completed entry.
- Read full prose and diffs independently of critic verdicts. Compare native checks,
  each historical/current repair and boundary separately. Keep duplicate reporting,
  unsupported demands, failures, retries and skipped cases visible.
- Inspect first/final structural responses and actual advice. Valid citations and
  high text similarity are not proof of semantic support or artistic quality.

The v59 comparator is historical, not a simultaneous rerun. This covers one scene,
one provider and two seeds. It cannot establish a general style-preservation gain,
full-story acceptance or the cause of the earlier extra edits.

## Local verification

- Verify **725 sealed files** across five predecessor bundles, their reports and
  the frozen database. Verify all prior implementation hashes except the two
  deliberately changed production files; compare those files against main to
  enforce exactly the paragraph and version edits.
- Replay all eight previous responses unchanged. Confirm identical critic messages,
  schemas and results, and only the declared writer-text difference.
- Seventeen mock calls cover all twelve planned stages, one structural retry
  recovery, permanent initial/writer failure, shared contracts, missing-decision
  rejection and repaired-fixture acceptance. No network or model calls. These
  fixtures test execution and validation, not creative success.
- Full Python run: **1,022 passed; four failed** on three stale v59 expectations
  and the old writer-length cap. Update those expectations, then rerun all four
  affected modules: **85 passed in 26.29 seconds**. The initial full run took
  325.73 seconds. No production behavior was changed to bypass those tests.
- Ruff lint/format checks pass for all 198 Python files. Strict mypy passes all
  198 files. The sandboxed uv checks could not write their interpreter cache;
  installed-environment tools and the outside-sandbox type/test runs completed.
- Diagnostic scripts pass formatting and syntax/undefined-name checks. The first
  preparation check compared an in-memory empty tuple with JSON's empty list;
  normalization fixed that local comparison without changing model settings.
- Frontend format, lint, type checks, all 11 Vitest tests and the production build
  pass. Initial sandboxed commands could not fetch pnpm through Corepack; the
  documented checks completed outside the sandbox without application edits.

## Bounds and provenance

Private bundle: `data/diagnostics/writer-minimal-repair-v60-2026-10-14/`.
Plan SHA-256: `d1fcf98cbf31bba6682cf1c6137b12a143e4e766f5c1747b67a8529508f46e76`.
Source database SHA-256:
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

- Existing Ollama Cloud `gemma4:31b-cloud` deployment through the local daemon;
  verify its recorded digest before generation.
- Maximum **24 calls / USD 0.15744** using recorded October 8 rates of
  USD 0.14/M input and USD 0.40/M output. Actual charges remain unknown.
- Per call: 24,000 input / 8,000 output tokens; writer temperature 0.85,
  critic temperature 0.2, top-p 0.95, thinking disabled.
- At most one existing structural retry per probe and one prose revision per
  case. No second prose revision, valid-response rerolls, outcome-dependent additions,
  full-story/continuity/adjudication calls or canonical writes.

The user explicitly approved this frozen matrix on October 14: “Yes, run the twelve
v60 probes.” `approval.json` records the authorization and exact plan hash. The
bounded run completed with twelve calls. Every request was reconstructed and every
raw response replayed; source hashes were reverified. Full prose, diffs and advice
were inspected before recording the following conclusions.

## Results

All **12 probes validated on their first attempt**: four writer and eight critic
calls. No structural retries, failures, skipped branches, second prose revisions
or additional model calls were needed.

| Measure | v60 result | Historical v59 comparison |
|---|---|---|
| Deletion alone restores accepted prose | **0/2** | **0/2** |
| Forbidden entry removed | 2/2 | 2/2 |
| Preservation revisions pass the unchanged critic | 2/2 | 2/2 |
| Genuinely missing decision repaired while outside | 2/2 | New negative control |
| Initial and unchanged missing-decision reviews reject indecision | 4/4 | New negative control |

Both preservation revisions keep the first **4,021 characters** verbatim, through
the torch preparation, fastening the wrist strap and bracing against the jamb.
They preserve touch, psychic pull, motivation and a semantic decision to enter.
Both remove the separate entry sentence. However, both also replace this accepted
last sentence:

> The first step would follow as soon as the strap was secure; both boots were still outside in the daylight.

Seed 19101 replaces it with:

> She decided she would go inside; she would find whatever had left the stroller there, even if it meant stepping into the dark.

Seed 19103 replaces it with:

> She had to know. She decided she would go inside.

These are successful assignment repairs but unsuccessful preservation tests. The
preparatory actions remain; the final indirect expression is still unnecessarily
replaced with explicit decision narration. A passing critic verdict does not
establish deletion-only preservation, nor was that a new critic requirement.

Both missing-decision writers change only the final paragraph and retain all
preceding prose. Seed 19101 supplies “She would go inside” and explicitly leaves
both boots in daylight; its mind-crossing metaphor is not physical entry. Seed
19103 supplies a decision and then leaves her boots on the concrete outside the
sill. Neither preserves the defective indecision. Other draft fields remain
unchanged except the expected revision number in all four writer outputs.

The unchanged critic correctly marks both native checks and every historical
repair met in all four post-reviews, with no overrun or current issues. Both initial
missing-decision reviews and both unchanged controls keep the fulfilled turning
point met, mark the outcome unmet, and require revision without alleging entry.

## Advice and validation inspection

The four negative reviews author four condition records, each citing the exact
Scene Plan outcome, “Elara decides to enter the windowless building,” from version
`f31c7da6-3a6a-5891-9eae-3b1e3193ddfc`, path `/content/outcome`. Inspection finds no
added requirement for causation, timing, completed entry or direct narration. One
raw condition calls for a definitive decision; it does not mandate particular
wording. The original canonical advice remains a decision to enter.

Three raw generic complaints restate the unmet assignment and consolidate into
its single outcome blocker. Each negative review retains the two existing repair
tests (touch and decision); repeating the known decision complaint does not create
a third identity. All four post-reviews contain no mandatory conditions or issues.
All first responses validate, so there is no retry-related classification drift.

`assessment.json` records mechanical comparisons, `inspection/` retains prose and
diffs, and `semantic-inspection.json` records the separate full-prose and advice
judgments. `postcheck.json` confirms replay and provenance. `closure.json` seals
the private bundle and this report after final verification. The initial automated
assessment's manual-inspection flag is resolved by the separate semantic record.

## Usage and decision

Usage is **194,332 input / 15,807 output tokens** across twelve calls. At the recorded
October 8 rates, the estimate is **USD 0.03352928**, within the approved maximum of
24 calls / USD 0.15744. Provider cost fields are zero placeholders with unknown cost
basis; **actual charges remain unknown**.

**Keep v59 on main.** The writer-only v60 candidate has not demonstrated its intended
preservation benefit. It does not prevent necessary repair in these two controls,
but that is insufficient reason to add the paragraph to production. The code stays
on `codex/writer-minimal-repair-v60`; no main update, canonical story change or sealed
benchmark change is made. Step 19 remains IN PROGRESS and Step 20 NOT STARTED.

The next focused diagnostic should compare the same writer request with and without
the already satisfied historical missing-decision complaint. Keep the current
boundary and genuinely unmet requirements, and retain full critic review history.
This would test whether stale decision criticism encourages explicit restatement;
the present experiment does not establish that cause. Do not remove production
history or add another general instruction based on that hypothesis alone.
