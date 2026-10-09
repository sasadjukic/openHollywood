# Consolidated overrun reporting and live writer repair

Date: 2026-10-09. Production contract v40 / graph v9.

**The original duplicate-reporting route is consolidated, and two of three live
writer revisions clearly leave the handwriting match unresolved and pass review.**
The third substitutes apparent identity and doubts about forgery; its critic
keeps the repair open. The unchanged-prose control also correctly requires
revision. This is evidence of useful targeted repair in this scene, with an
important remaining ambiguity, not full-story recovery or general reliability.

## Implementation

The preceding [explicit-endpoint comparison](explicit-endpoint-comparison-2026-10-09.md)
found the same overrun reported through both the boundary check and assignment
violations. The v40 normalizer combines these current-review routes only when
the assignment anchor and exact evidence-handle set agree. It retains both
explanations and repair instructions in one blocking issue. Different anchors,
different handle sets and independent craft/POV findings remain separate.

Every route is validated before a critique can be accepted. Bad evidence or a
malformed assignment cannot disappear through consolidation. No model-written
claim is silently dropped just because its evidence overlaps. The existing
writer/critic repair packet receives one test for the consolidated issue.

The version changes because canonical critique materialization and downstream
repair packets change. No semantic instruction, model schema, role, call budget,
retry/revision limit, migration or API/client contract is added. This is
provider-neutral application behavior. See [ADR 0024](../adr/0024-consolidated-scene-overrun-reporting.md).

Offline replay covers all twelve previous responses. Each of the three positive
reviews changes from two outcome blockers to one, preserving all other feedback
and the revision verdict. The other nine canonical results remain exactly equal.

## Live experiment

The user explicitly approved three isolated writer/critic pairs and one
unchanged-draft critic control on the existing Ollama Cloud Gemma4 deployment.
The fixed allocation was seven probes, at most fourteen calls and a USD 0.09184
estimate using recorded October 8 rates. Each probe permits one structural
retry; there is no second manuscript revision or outcome-dependent expansion.

Each pair starts from the same original OH-V01-002 scene and the synthetic
explicit outcome: **"Elena decides to verify the handwriting. No handwriting
match is established by the end of this scene."** Full standard story context
and the next-scene reservation remain present throughout. The synthetic plan
does not replace the real approved Blueprint or become canonical story content.

The three source critiques are the three positive responses from the previous
experiment, rematerialized offline under v40. All feedback is retained: seed
19102 has a major tension repair plus the consolidated outcome repair; 19103
has only the outcome repair; 19104 also has minor pacing advice. Each writer
uses the corresponding seed. These are three related trials with different
feedback and seeds, not repeated identical feedback or a controlled ablation of
the advice. No new initial critic call is needed.

Writer requests use the existing scene-writer instructions, temperature 0.85,
top-p 0.95 and thinking disabled. Model, profile, per-call budget and original
draft provenance are retained. Each validated revision receives a new synthetic
draft version. Its critic receives that exact version and the same original
repair tests the writer received, through the normal production message builder.
Dependent critic requests are frozen before transmission, without manual edits
or additional review hints.

The unchanged-draft control uses seed 19102 and its repair packet, with original
prose unchanged under a new revision-1 identity. It runs first. Its purpose is
to check that a new revision number does not itself cause acceptance.

## Results

| Trial | Writer attempts | Critic attempts | Final review | Outcome repair |
|---|---:|---:|---|---|
| Unchanged draft, 19102 | Not run | 1 | REVISE / overrun | Unmet |
| Repair pair, 19102 | 1 | 2 | PASS / no-overrun | Met; tension test also met |
| Repair pair, 19103 | 1 | 2 | PASS / no-overrun | Met |
| Repair pair, 19104 | 1 | 1 | REVISE / overrun | Unmet |

All three writers produce valid complete draft objects on their first calls.
The two successful critic trials initially use malformed evidence identifiers
such as `draft_evidence_035_...` instead of the supplied `draft_evidence_0035_...`.
Validation rejects those reviews; the existing single structural retry corrects
the handles. The writer drafts do not change during these retries. Rejected
reviews already propose PASS but are not counted as accepted critiques.

All seven probes eventually validate, using **nine calls**. The 19104 trial is
not rerolled or repaired a second time. A valid review requiring revision is an
observed semantic result, not an execution failure.

## Reading the actual revisions

The following assessment comes from inspecting the complete original and revised
prose, separately from the critic's verdict. All three revisions alter the same
four paragraphs (6, 11, 12 and 13) and preserve the other nine exactly. The warning
message, birthday, apartment setup and October 2024/2034 realization remain
unchanged. Verification attempts and suspicion remain part of the scene.

| Seed | What changes in the comparison | Assessment |
|---|---|---|
| 19102 | Elena cannot bridge the gap between similar and identical; the ending says the evidence is not yet proof and she needs something more | Clear repair of the explicit no-match endpoint |
| 19103 | The comparison remains inconclusive, with pressure/confidence differences; the closing assertion of her own hand becomes suspicion | Clear repair of the explicit no-match endpoint |
| 19104 | The samples "seemed identical," and "the very perfection of the match" raises doubts about forgery or authorship | Do not count as a clean repair; apparent matching and unresolved authenticity remain entangled |

The first two revisions also soften the earlier recognition paragraph, not just
the two sentences originally cited by the critic. They replace the initial
assertion of an exact mirror and change the later closing certainty. This is
useful evidence that the writer can revise related assertions across the scene
while preserving unrelated paragraphs.

The third revision removes "mathematical match" and adds qualifiers. However,
its journal comparison still calls the match perfect, then asks whether it is
a forgery. That questions the writing's origin rather than clearly leaving the
match itself unestablished. Its later phrase "terrifying, ambiguous authenticity"
continues the ambiguity. The critic's concern is understandable, but its claim
that the draft simply declares identity is stronger than the qualified prose.
This trial exposes a distinction worth testing, not an infallible judgment about
every use of "seemed" or "similar."

The original is 651 whitespace-separated words; revisions are 698, 684 and 673.
These counts and exact paragraph preservation describe edit scope, not literary
quality. No style-tic improvement, broad quality score or continuity acceptance
is claimed. The app's critic craft scores are not blind human review.

## Remaining duplicate route

The new current-review consolidation works in both live blocked reviews: their
boundary and assignment findings collapse into one current outcome issue. But
`_normalize_repair_checks` subsequently restores the unmet historical obligation
with current evidence, producing a second outcome issue. This occurs in the
unchanged control and the 19104 review; their current and historical evidence
sets differ. The unchanged control also repeats its major tension allegation
through current feedback and the unmet historical repair.

This historical-repair route is absent from the initial critiques used to
prepare the writers. Duplicate obligations therefore remain possible in a
revision loop. These new reviews were not sent to another writer. A future fix must
preserve source-test identity and independent findings instead of suppressing
all issues with the same category or guessing equivalence from similar wording.

## Interpretation and next work

An explicit unresolved endpoint plus the existing repair packet can produce
a substantive local correction: two trials do so, and the unchanged control is
not accepted. The third shows why adding suspicion is not always enough. This
is not a comparison with duplicate feedback left in place, so the experiment
does not establish that consolidation caused better writing.

The next technical target is the overlap between a current finding and an unmet
historical repair, with explicit provenance preserved. The next semantic target
is a focused match-versus-authorship comparison: distinguish an inconclusive
comparison from a confirmed likeness whose origin remains doubtful. That can
inform shared writer/critic repair criteria without removing story context or
forbidding inconclusive investigation. Neither follow-up is implemented here.

Automatic generation of explicit scene endpoints remains a separate planning
change owned by the existing Blueprint integrator and checked by the Blueprint
critic. No fresh Blueprint generation, continuity review, dialogue pass, second
scene, adjudication, canonical acceptance or full-story execution occurred here.
Three trials on one scene/model do not establish a success rate across stories,
immutable remote weights or deterministic remote seed handling.

## Verification, provenance and cost

Base commit: `aed7d7cfd3c2f33c819cf97da7edf3aefdd11d83`; branch:
`codex/consolidated-overrun-repair`. All diagnostics freeze exact source and
implementation hashes. The completed benchmark snapshot remains read-only with
SHA-256 `71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
Historical raw responses and results remain unchanged.

The seven probes consumed **85,693 input / 8,987 output tokens** across nine calls.
At recorded October 8 rates of USD 0.14/M uncached input and USD 0.40/M output,
the estimate is **USD 0.01559182**, below the approved USD 0.09184 maximum.
Actual charges remain unknown; this is not a newly verified tariff or bill.
The existing `gemma4:31b-cloud` alias retains digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.

All prepared/dependent requests reconstruct exactly, response hashes verify,
and validated outputs rematerialize exactly. Shared repair targets and new draft
evidence identities verify. The source snapshot hash is unchanged after inference.
The fixed run stops after the planned probes.

Verification passed Ruff, strict mypy (172 files), 710 Python tests, frontend
format/lint/type checks, 11 frontend tests and production build. There are 13 new
consolidation tests, including persisted revision/replay. The first full Python
run had 709 passes and one SQLite-lock failure in a worker cancellation test.
The five worker tests and a second full 710-test run passed without code changes;
the transient remains recorded rather than being hidden by the successful rerun.

Local evidence is under `data/diagnostics/consolidated-overrun-v40-2026-10-09/`:
`experiment.py`, `plan.json`, `prepared/`, `offline-replay.json`, complete `live/`
requests/responses, `assess.py`, `assessment.json` and `draft-diffs/`.
**This implementation and bounded experiment are complete. Step 19 remains
IN PROGRESS; Step 20 is NOT STARTED.**
