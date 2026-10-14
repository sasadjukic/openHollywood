# Fixed-v59 indirect-decision preservation — 2026-10-14

Status: **COMPLETED — BOUNDARY REPAIRED; DELETION-ONLY PRESERVATION 0/2.**

Both writers remove the forbidden entry and preserve the decision's meaning, but
also rewrite the accepted final sentence into more explicit entering intention.
Both deletion-only controls pass, showing that this extra rewrite was unnecessary
for critic acceptance. Eight probes complete in eight calls without retries.

Keep production at prompt version 59 / graph version 9. Start from
`50fabff62eaa13e332434f9520dba7b969c9b786`, which merged the
[outside-boundary repair results](outside-boundary-repairs-v59-2026-10-14.md),
on `codex/indirect-decision-preservation-v59`. No production instructions,
meaning of met, schema, rendering, compaction or retry policy change.
Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Question and source

Can the writer remove a separate forbidden entry while retaining an already
valid indirect decision, without replacing it with explicit decision narration?
The previous experiment could not isolate this: the original entry action partly
expressed the decision and itself required replacement.

Use the accepted family-19103 outside variant from the endpoint-wording experiment,
case `f19103-s19101-outside-outside_required`. Its last paragraph establishes the
decision through preparing a torch, securing its strap and bracing to enter, while
explicitly leaving both boots outside. The earlier motivation and all remaining
prose are retained verbatim. This indirect variant passed under the explicit
outside endpoint at both tested critic seeds; the subsequent boundary experiment
also accepted it with the added repair history.

Append only this separate paragraph:

> She stepped across the sill and entered the building.

The plan still requires touch and psychic pull without an assigned order or
causal relationship, and the outcome is **Elara decides to enter the windowless
building.** The exit state explicitly requires her to remain outside at scene end
without crossing the sill. Keep the exact source Story Bible, broader context and
next-scene reservation. Synthetic diagnostic plans remain unapproved controls;
canonical story artifacts do not change.

## Frozen matrix and dependency rules

Eight probes at most: **two critic/writer/critic chains plus two matched
deletion-only critic controls**, using seeds 19101 and 19103. The initial prose,
context and schema are identical across seeds.

| Stage per seed | Current candidate | Purpose |
|---|---|---|
| Initial critic | Accepted indirect prose plus separate entry | Identify overrun while keeping fulfilled facts/decision met |
| Control critic | Original accepted prose, revision 2 | Check deletion-only repair under the new feedback history |
| Writer | Overrun draft plus exact fresh canonical feedback | One bounded revision using existing production instructions |
| Post-repair critic | Unedited validated writer output | Assess boundary, decision, facts and original repairs separately |

Run in that order for each seed. Run dependent stages only if the initial review
validates, requests revision and identifies a boundary overrun. Otherwise record
the detection failure and skipped stages, without replacing the case or rerolling.
A failed writer has no post-repair critic. Control results do not gate the writer.

Retain **all actual canonical feedback unchanged**, including any unexpected
additional criticism; do not select only reviews that already agree with expected
labels. Preserve the earlier two repair tests and add every repair from the new
review. Writer, post critic and matched control share exact assignment, boundary,
history and repair-test content through normal production compaction. Freeze each
dependent request before generation. No hand-authored preservation instruction or
expected experimental verdict is inserted into model messages.

## Assessment declared before generation

1. Primary preservation measure: revised prose equals the accepted baseline
   exactly. This is a deletion-only repair of the appended paragraph.
2. Separately inspect retention of the full indirect passage, earlier motivation,
   touch/pull facts, unrelated prose and other draft fields. Distinguish harmless
   extra edits, explicit restatement, lost decision and retained/reintroduced entry.
3. Inspect whether initial criticism demanded any decision rewrite before
   attributing a writer change to the writer alone. The unchanged control tests
   critic acceptance; the generated revision tests actual preservation.
4. Inspect both native checks, earlier and new repair statuses, boundary and final
   verdict. Retain independent defects, duplicate-reporting evidence and all
   mandatory advice. Valid source citations establish traceability, not entailment.
5. Reconstruct every request and replay raw responses unchanged, including failed
   structural attempts. Compare first/final judgment statuses separately from
   wording changes. Keep failures and skipped stages in the denominator.

Full prose and exact diffs require manual inspection; similarity scores and critic
pass verdicts alone do not prove semantic or artistic success. This tests one
synthetic extension of one scene on one provider at two seeds. Feedback and writer
seed vary together. It is not full-story or Step 19 acceptance evidence.

## Local verification

- Verify **591 sealed files** across four predecessor bundles, their reports,
  source code hashes and the frozen database.
- Reconstruct and replay all thirteen prior boundary-experiment responses,
  including its rejected repair-ID attempt, through unchanged production.
- Verify the initial draft differs only by the appended paragraph and both seeds
  receive identical initial messages/schema.
- Thirteen mock gateway calls exercise both complete chains, shared contracts,
  one allowed retry recovery and permanent initial/writer failure. Local fixtures
  establish execution/validation behavior, not model judgment or creative success.
  An initial fixture used the wrong boundary field name; the failed local run is
  retained separately and the corrected fixture passes. Production was unchanged.
- **45 relevant regression tests pass in 12.74 seconds**, covering isolated probes,
  v31 repair acceptance, v39 boundaries and v59 consolidation. No cloud calls.
- Diagnostic scripts pass Ruff formatting and syntax/undefined-name checks.
  No application code changed, so the full application suite and frontend build
  were not repeated for this diagnostic/documentation change.

## Bounds and provenance

Private bundle: `data/diagnostics/indirect-decision-preservation-v59-2026-10-14/`.
Plan SHA-256: `e55275cd74cdb8eba15da1fa573efee9f59386144943c27ad7a25d4c2b4983d9`.
Source database SHA-256:
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

- Maximum **8 probes / 16 calls**, including at most one existing structural retry
  per probe; one prose revision per seed.
- Existing `gemma4:31b-cloud` deployment through the local Ollama daemon forwarding
  to Ollama Cloud; verify its recorded digest before generation.
- Per-call limits: 24,000 input / 8,000 output tokens. Existing writer temperature
  0.85, critic temperature 0.2, top-p 0.95 and thinking disabled.
- Maximum recorded-rate estimate: **USD 0.10496**, using October 8 rates of
  USD 0.14/M input and USD 0.40/M output tokens. Actual charges remain unknown.
- No second prose revision, valid-response rerolls, outcome-dependent additions,
  adjudication, continuity/full-story calls or canonical writes.

The user explicitly approved this frozen matrix on October 14: “Yes, run the v59
indirect-decision preservation experiment.” `approval.json` records the exact
authorization and plan hash. The approved run completed in eight calls: two writers
and six critics. No further generation ran.

## Results and exact prose changes

| Seed | Initial critic | Deletion-only control | Writer preservation | Post-repair critic |
|---|---|---|---|---|
| 19101 | Both native checks/old repairs met; one boundary blocker | Pass; three repairs met | Removes entry, rewrites accepted final sentence and adds outside description | Pass; three repairs met |
| 19103 | Both native checks/old repairs met; one boundary blocker | Pass; three repairs met | Removes entry and rewrites accepted final sentence | Pass; three repairs met |

All eight probes validate on their first attempt. No branch is skipped. The two
initial reviews identify precisely the appended entry sentence as the boundary
evidence, leave both native requirements and earlier repairs met, and generate
one canonical blocking issue apiece. Neither requires explicit decision narration.
The boundary advice uses the existing application-rendered template. No generic
duplicate complaint, assignment violation or model-authored condition set is added.

Both writers preserve the first **4,021 characters** exactly, through the torch
preparation and “She braced her free hand on the jamb to carry herself through.”
Thus the existing action-based decision, motivation, touch, psychic pull and
unrelated prose survive. All other draft fields remain unchanged apart from the
revision number. No new causation requirement or later encounter is introduced.

Both remove the separate entry paragraph, but also replace this already accepted
sentence:

> The first step would follow as soon as the strap was secure; both boots were still outside in the daylight.

Seed 19101 substitutes:

> She would go inside; she had to know.
>
> She stood at the threshold, the light of the overcast afternoon still warming her heels, her eyes fixed on the dark void ahead.

Seed 19103 substitutes:

> She had to know. She had to enter.

The first revision states the intention directly and supplies a new outside
description. The second states the need to enter more directly while relying on
unchanged earlier text to keep her outside. Neither narrates a crossing. The
decision remains fulfilled in context, including the preserved preparatory actions.
The input has 729 words, the accepted baseline 720, and the revisions 731/708.

The primary deletion-only measure therefore succeeds **0/2**, while boundary and
semantic decision preservation succeed **2/2** in manual inspection. These are
localized unnecessary edits, not wholesale removal of the indirect evidence or
proof that explicit phrasing is always artistically worse.

All four control/post reviews pass with both native checks and all three original
repairs met, no overrun, empty links for satisfied repairs and no issues. Both
controls retain the exact accepted indirect ending. This demonstrates that the
critic accepts the simpler deletion-only repair under the same feedback history.
One post-review explanation reverses the narrated order of bracing and internal
realization; the actual draft still establishes the decision, and no requirement
assigns an order to those acts. Record that rationale imprecision without treating
it as a false acceptance or invented mandatory order.

## Interpretation, verification and next focused step

This experiment isolates unnecessary rewriting more clearly than the preceding
one: the valid decision expression exists independently of the removable defect.
The critics do not ask for its replacement and accept the original form. It does
not isolate why the writer changes it. The actual writer contract retains the
historical acceptance tests, including the earlier missing-decision claim, along
with generic preservation guidance. The latest met audit is not projected into
an explicit fulfilled-passage preservation directive. That is a possible influence,
not demonstrated causation; ordinary generation preferences may also contribute.

The next focused change should concern the **existing writer's revision guidance**:
when deleting an independent defect is sufficient, preserve the wording that
already fulfills the scene, including indirect decisions. A deletion can be the
complete repair; extra restatement is unnecessary. Test that compact clarification
against these frozen writer inputs, retaining a genuinely missing-decision control
so preservation does not obstruct necessary repair. Keep the critic and meaning
of met unchanged. Do not introduce a universal exact-text gate or classify all
small paraphrases as blockers. No such implementation or further calls occurred here.

All eight exact requests and raw responses were reconstructed and replayed through
unchanged production validation. Dependent inputs match the actual canonical
feedback and unedited writer outputs. Source code, the database, reports and
591 prior sealed files were reverified. Complete prose, diffs, semantic inspection,
local tests and receipts are retained; `closure.json` indexes the evidence/report.

Usage: **143,523 input / 11,215 output tokens**, estimated **USD 0.02457922** at
the recorded October 8 rates, below the approved USD 0.10496 ceiling. Provider
receipts retain an unknown cost basis and zero placeholder; actual charges remain
unknown. Production and main stay v59; canonical stories and sealed benchmarks
are unchanged. This one-scene, two-seed result does not establish general style
preservation, preference or cost acceptance, and does not close Step 19.
