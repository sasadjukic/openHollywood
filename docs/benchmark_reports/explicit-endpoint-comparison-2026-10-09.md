# Explicit unresolved scene endpoint comparison

Date: 2026-10-09. Production prompt v39 / graph v9 unchanged.

**An explicit unresolved endpoint recovered overrun detection in all three
tested seeds, with full story context retained.** The same original OH-V01-002
draft passes under the original decision-to-verify wording and under explicit
permission to verify. It requires revision when the outcome adds that no
handwriting match is established by scene end. The inconclusive-investigation
control still passes, and the missing-turn control still requires revision.

This demonstrates sensitivity to a stronger synthetic plan instruction in this
case. It does not fix enforcement of the original wording or demonstrate writer
repair. Each positive detection also produces two blocking findings for the same
overrun, exposing a separate normalization problem.

## Controlled comparison

The user approved twelve isolated critic probes on the existing Ollama Cloud
Gemma4 deployment, with at most twenty-four calls and a USD 0.15744 allocation
estimate. All conditions were run contemporaneously; historical responses are
not used as either side of the comparison.

The original draft is unchanged across these three current-plan outcomes:

| Condition | Exact outcome | Requested seeds |
|---|---|---|
| A: original decision | Elena decides to verify the handwriting. | 19102, 19103, 19104 |
| B: explicitly unverified | Elena decides to verify the handwriting. No handwriting match is established by the end of this scene. | 19102, 19103, 19104 |
| C: authorized verification | Elena verifies that the handwriting matches her private script but does not yet accept the future warning. | 19102, 19103, 19104 |

The three groups run in predeclared orders A/B/C, B/C/A and C/A/B. Three further
probes use seed 19102: the existing inconclusive-investigation draft under A and
B, and the existing missing-ten-year-future-turn draft under B. There are no
outcome-dependent additions or semantic rerolls.

Unlike the preceding
[broader-context comparison](broader-context-comparison-2026-10-09.md), every
request retains standard v39 broader Blueprint guidance and the next-scene
reservation. There are no context projection overrides. Current goal, summary,
conflict, turn, exit state, style, review policy, evidence catalog, schema and
model settings remain unchanged within each draft/seed comparison.

Condition B uses new synthetic ScenePlan, StoryBlueprint and StoryBible versions;
C reuses the existing synthetic authorized-verification fixture. The changed
outcome agrees across the standalone plan, embedded Blueprint plan, assignment
contract and due-now requirement scope. Bible content changes only its source
Blueprint version reference. Artifact lineage and hashes are consistent. These
are unapproved diagnostic plans, not revisions to the real approved Blueprint.

Whole-payload comparisons, after normalizing only the changed outcomes and
associated version references, verify that nothing else changes. A and C retain
the exact message content of their prepared v39 fixtures. B adds 248 request
characters and 50 reported input tokens relative to A; C adds 264 characters and
53 tokens. The experiment tests these wording packages, not individual words
independently of their length or repetition across the existing plan views.

## Results

| Draft | A: decision | B: explicitly unverified | C: authorized verification |
|---|---|---|---|
| Original conclusive verification | PASS / no-overrun, 3/3 | REVISE / overrun, 3/3 | PASS / no-overrun, 3/3 |
| Inconclusive investigation | PASS / no-overrun | PASS / no-overrun | Not run |
| Missing required future-date turn | Not run | REVISE / no-overrun | Not run |

All twelve responses validate on their first calls. There are no structural
repairs or discarded initial responses. REVISE is the application's normalized
verdict: the four affected raw model responses say `reject`. No production
workflow or writer revision was executed.

All three B reviews identify the same conclusive statements as exact evidence:
**"They were identical."** and **"It was a mathematical match."** They compare
those results against the explicit unresolved endpoint and find an overrun.
They no longer treat the next scene's more specific flourish as justification
for establishing the general match now.

The A reviews still accept completed comparison under a decision-to-verify
outcome. The C reviews accept the same evidence when verification is explicitly
permitted. Thus the positive result concerns the new explicit constraint; the
original implicit stopping-point failure persists.

The B inconclusive control selects the failed attempt itself as evidence:
**"She could not tell whether the strokes matched; this test proved nothing."**
It also selects the later decision to compare journals and the unresolved
question. This is useful discrimination: the stricter endpoint does not forbid
all investigation in this control. The missing-turn response identifies one
blocking `scene_assignment:turning_point` issue for today's date replacing the
required date ten years ahead, without inventing an overrun.

The original A/C reviews and inconclusive controls receive mean craft scores of
5.0; the three B original reviews receive 4.33; the missing-turn control receives
4.0. These scores are diagnostic observations, not evidence that prose improved.

## Duplicate findings and repair limits

Each of the three B overrun responses reports the same defect in both
`scene_boundary_check` and `assignment_violations`, despite instructions to put
overruns only in the boundary check. Both routes use the same two evidence
handles and the outcome anchor. Current normalization preserves both, creating
**two blocking `scene_assignment:outcome` issues for one overrun**. This is not
six independent detected defects.

The duplicate findings could create redundant repair obligations in a real
workflow. That consequence has not been tested here. A focused follow-up should
ensure that the same supported overrun is materialized once while retaining
independent assignment violations, including the missing-turn control. Avoid
merging unrelated findings merely because their categories match.

Two B reviews also offer nonblocking dramatic-tension or pacing advice involving
a match that seems too perfect or a suspected forgery. Doubt about who produced
the writing does not by itself undo a conclusive handwriting match. A future
writer test must verify the actual revised prose leaves the match unresolved;
acceptance of the critique alone is insufficient.

## Interpretation and next step

The evidence supports stating the permitted end state explicitly when scene
separation depends on an unresolved result. It is consistent with the original
decision wording being treated as a minimum achievement rather than a stopping
point. It does not reveal the model's internal reasoning or establish that this
is the only influence. Useful story context can remain in production.

The existing `blueprint_integrator` is the appropriate owner of clear scene
outcomes, including what must remain unresolved when relevant. The existing
`blueprint_critic` can check that these endpoints agree with the causal sequence.
The normal human Blueprint approval then establishes the plan consumed by both
`scene_writer` and `scene_critic`. This is a proposed model-agnostic responsibility
within the existing roles, not a new agent or an implemented planning change.
It should not impose a negative constraint on every scene or forbid authorized
overlap, exploratory action or incidental follow-through.

The next technical slice should consolidate duplicate overrun findings, then
test actual writer repair against an explicit approved endpoint. Before adopting
the planning change broadly, test whether the integrator can produce useful
boundaries on other premises and whether writers preserve scene progress while
honoring them. This single story, three requested seeds and one cloud model do
not establish general reliability, remote seed determinism or immutable weights.
Full-story recovery and Step 19 acceptance remain unproven.

## Verification and cost

Source commit: `956ad8719f8ab0a87c4e98ed3cb5f99fd5d17432`. Source critic invocation:
`d2758b4f-7a66-4587-b7c6-fc5386ff20b6`. The read-only completed benchmark snapshot
retains SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

Ollama 0.35.1 forwarded `gemma4:31b-cloud` to Ollama Cloud's `gemma4:31b`, retaining
alias digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Each call retained limits of 24,000 input / 8,000 output tokens.

The twelve calls used **126,270 input / 8,853 output tokens**. Using recorded
October 8 [Gemma4 rates](https://ollama.com/library/gemma4:31b-cloud), with uncached
input at USD 0.14/M and output at USD 0.40/M, the estimate is **USD 0.021219**,
within the approved USD 0.15744 maximum allocation estimate. Actual charges remain
unknown; these are recorded rates, not a newly verified tariff or billing receipt.

Offline checks verified typed synthetic artifacts, consistent outcome copies
and lineage, exact source fixtures and unchanged request fields. Prepared/live
request hashes, source/code hashes, captured response hashes and scene audits
verified. All twelve requests reconstructed and validated results rematerialized
exactly. The unchanged probe and endpoint suites passed **36 focused tests**:

```text
uv run --extra api pytest tests/evaluations/test_production_probe.py tests/api/test_production_v38.py tests/api/test_production_v39.py -q
```

Local evidence is in `data/diagnostics/explicit-endpoint-v39-2026-10-09/`:
`experiment.py`, `assess.py`, `plan.json`, `prepared/`, complete `live/` responses
and `assessment.json`. Full application gates were not repeated for this
documentation and isolated diagnostic change. Production remains v39 / graph v9;
canonical stories, sealed benchmarks and historical results are unchanged.
**This comparison is complete; Step 19 remains IN PROGRESS and Step 20 is NOT STARTED.**
