# Required critic boundary comparison: implementation and probes

Date: 2026-10-08. Prompt v38 / graph v9.

**The required comparison is implemented and observable. The original overrun
still passes.** The new response identifies a more specific interpretation:
the critic acknowledges verification beyond the decision to verify, but treats
it as a general match that leaves a particular secret flourish for scene 2.

## Implementation

[ADR 0022](../adr/0022-required-critic-boundary-comparison.md) records the change.
The existing critic must return `scene_boundary_check` containing:

1. The state the draft establishes.
2. A comparison with the current endpoint.
3. A separate comparison with the next scene's reservation.
4. One to three distinct current-draft evidence handles.
5. `no_overrun` or `overrun`.

Each prose field is nonblank and capped at 600 characters. The application
validates structure, current evidence identity and applicability. A valid overrun
becomes a blocking assignment issue and forces revision even if the model returns
PASS with perfect craft scores. `no_overrun` cannot release another blocker or
certify that the current scene has achieved its assignment.

When there is no next reservation or no current endpoint to anchor it, the new
overrun route is unavailable in both the bound schema and validation. Other
assignment routes remain intact. Missing or malformed comparisons consume the
existing bounded response repair; they never generate a story-revision request
or canonical critique. Repair guidance is now version 10.

Successful production invocations and isolated probes retain a redacted
`scene_boundary_audit` tied to the exact draft, current plan and approved
Blueprint reservation. Failed reviews retain only allowlisted, bounded,
unvalidated comparison fields in diagnostic evidence. These records do not enter
story canon or retry context. The canonical Critique schema remains unchanged;
only a reported overrun becomes an ordinary canonical assignment issue.

Model-authored target artifact IDs are omitted from every critic output schema.
The application already binds those IDs to the task draft. This extends the
existing behavior for repair-bearing revisions and offsets most of the new
comparison schema. The five initial requests grow by 134 characters each;
seven measured revision requests grow by 134–912 characters. No call budget,
retry allowance, revision limit, role, graph route, provider choice, SQL schema
or API/client contract changes. Writer messages remain identical to v37.

## Verification

Twenty-three new test cases cover required fields, bounded text, exact evidence,
stale and duplicate handles, Local/Cloud schemas, inapplicable overruns, high-score
blocking, preservation of other hard failures, source identities and redaction.
Persisted workflow tests distinguish a genuine reported overrun causing prose
revision from a missing comparison causing only response repair, and verify
replay without duplicate calls. Probe tests verify the exported audit's exact
candidate identity. Simulated judgments do not establish model judgment quality.

Checks passed: 688 Python tests, Ruff lint/format and strict mypy (170 files),
frontend format/lint/type checks, 11 frontend tests and production build. Final
focused comparison/probe checks also passed after strengthening an audit
assertion. There were no new model calls after the five approved probes.

## Matched live probe scope

The user approved the same five input sets as the
[v37 experiment](scene-boundary-v37-2026-10-08.md), now under the v38 response
contract: the original scene-1 overrun, proper stopping, permitted foreshadowing,
verification correctly assigned to scene 2, and a missing-turn control.

The two original scenes and three synthetic draft variants retain exactly their
v37 identities and content hashes. Their input payloads, shared boundary,
current canon, seed and model settings are unchanged; the critic instructions
and output schema differ. All synthetic variants remain unapproved diagnostic
fixtures. Source provenance and their construction are recorded in the v37
report; the principal source critic invocation is
`d2758b4f-7a66-4587-b7c6-fc5386ff20b6`.

The approved bound was ten calls, including at most one structural repair per
probe, and a published-rate allocation estimate of USD 0.06560. All five
validated on the first call; no repairs, rerolls, writer calls or full-story
tests ran.

The existing Ollama 0.35.1 daemon routed `gemma4:31b-cloud` to Ollama Cloud's
`gemma4:31b`, retaining alias digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Per-call limits remained 24,000 input / 8,000 output tokens. The alias does not
guarantee immutable remote weights or deterministic reproduction.

Prepared/live request hashes, source artifact hashes, raw/materialized response
hashes, exported comparisons and the approved plan hash verified. The read-only
source snapshot remains SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
Canonical stories, sealed campaigns and historical results were not modified.

## Results and interpretation

| Probe | v37 verdict | v38 verdict | v38 boundary status |
|---|---|---|---|
| Original scene-1 overrun | PASS | PASS | `no_overrun` |
| Proper stopping | PASS | PASS | `no_overrun` |
| Permitted foreshadowing | PASS | PASS | `no_overrun` |
| Verification assigned to scene 2 | PASS | PASS | `no_overrun` |
| Missing-turn control | REVISE | REVISE | `no_overrun`; independent assignment blocker |

All passing cases still receive three 5/5 scores. The missing-turn control's
mean remains 3.67. There is no improved overrun-detection result in this set.

The original scene's required comparison is nevertheless informative:

- **Achieved state:** the model identifies journal comparison and a mathematical
  handwriting match, rather than claiming that no verification happened.
- **Current endpoint:** it explicitly says the draft reaches the decision to
  verify and exceeds it by performing initial verification.
- **Next reservation:** it calls the completed work a general match, while
  reserving a specific secret flourish for scene 2; it therefore chooses
  `no_overrun`.

Its selected evidence is the current draft's sentence stating the samples were
identical and the later sentence describing Elena's future trajectory as a trap.
The handles resolve correctly. They are relatively narrow support for the
compound achieved-state assessment, so validated references should not be read
as proof that every part of the explanation is sufficiently evidenced.

The distinction between specific letter details has a textual basis. Scene 1
describes her private script, idiosyncratic descenders, letter spacing and looped
L's before concluding an exact mathematical match. Scene 2 adds a private knot
in the tail of a lowercase g. That additional detail does not make scene 1 stop
at its approved decision to investigate. The unresolved judgment is whether
retaining a more specific later mechanism permits this material advance beyond
the current endpoint.

This shows the critic's documented interpretation, not its hidden internal
reasoning. It now compares the boundary explicitly, but regards the work as
distinct enough to permit. There is no deterministic check that can decide the
literary question merely by noticing a word such as "exceeds" in its prose.

The proper-stopping and foreshadowing controls correctly describe an unperformed
comparison. Scene 2 is correctly assessed as accomplishing its assigned
verification while preserving the later Marcus reveal. No extra issues occur in
those three passing probes.

The missing-turn control correctly reports a blocking assignment violation for
replacing the ten-year-future date with today's date. It also adds a questionable
blocking plot issue, claiming the present date makes a warning about the next
decade nonsensical. A present-day warning can refer to the next decade; the
approved date requirement already supplies the sound reason to revise. Preserve
this additional reasoning weakness instead of counting every reported blocker
as correct. Its `no_overrun` status does not clear either independent issue.

## Usage and next question

The five calls used **53,894 input / 3,484 output tokens**. At the dated October 8
[Gemma4 published rates](https://ollama.com/library/gemma4:31b-cloud), assuming
uncached input at USD 0.14/M and output at USD 0.40/M, the estimate is
**USD 0.00893876**. Actual charges remain unknown. The gateway's zero numeric
placeholder with `cost_basis: unknown` is not evidence of free billing and
cannot close the cost-acceptance gate.

Local evidence is under `data/diagnostics/critic-boundary-v38-2026-10-08/`:
the preserved v37 executor, `prepared/` requests and plan, `live/` complete model
responses and materialized audits, `revision-sizes.json`, and `assessment.json`.

The next question is **how binding the current endpoint should be when a later
scene retains a more specific detail of an already established result**. A
candidate rule would require explicit current-plan authorization for material
advancement beyond that endpoint; merely retaining a new later detail would not
authorize it. This needs controls separating preliminary investigation,
conclusive verification, incidental follow-through and approved overlap. That
additional policy change is not part of v38.

No broader semantic recovery, fresh writer improvement, repeatability or
multi-provider result is established. Step 19 remains IN PROGRESS; Step 20 and
the creative-quality implementation sequence have not started.
