# ADR 0014: Bounded terminal adjudication of critic findings

- Status: Accepted
- Date: 2026-09-13

## Context

Production-improvement step 3 made revision acceptance tests inspectable. It did
not settle semantic disputes: the v31 probe of OH-V01-007 still overcredited a
qualifier already present in the original passage. Repeating review instructions
or allowing more prose revisions would not establish whether the allegation was
valid. Step 4 gives an unresolved critic allegation a separate, focused assessment.

## Decision

New runs use prompt v32 / graph v9. Add the registered critic_adjudication node,
routed through the existing scene_critic specialist and frozen Local, Cloud or
Hybrid model profile. This is a separate request, not a second model or a vote.
The same model can repeat the original mistake; structured validation establishes
provenance and valid decisions, not literary truth.

Reuse ADR 0007's existing terminal allowance: a scene may visit either critic
adjudication or continuity adjudication, once, with at most two model attempts.
Revision cycles, aggregate call/token/cost ceilings, per-call budgets, graph-step
envelope, timeout and cancellation policies do not increase. The new path does
not append instructions to ordinary writer, critic or continuity requests.

Critic adjudication is eligible only after at least one revision, at the existing
revision cap, when all remaining hard critic issues are typed scene-assignment
allegations and continuity is clear. Eligible anchors are POV, assigned
characters, location, scene identity, turning point and outcome. This includes
hard assignment repairs retained by step 3. No fuzzy matching is used to require
that the current wording exactly repeat an earlier allegation; newly expressed
terminal allegations are still assessed against the earlier repair history.

An unrelated hard critic issue prevents this path. If critic and continuity
blockers coexist, neither adjudication path runs: one available visit cannot
clear two independent gates. The diagnostic identifies competing_review_blockers.
Continuity-only adjudication retains its existing policy. World Rules,
requirements, forbidden shortcuts and other continuity gates cannot be released
by critic adjudication. Step 5's continuity-policy changes remain pending.

## Evidence and decisions

The application supplies the exact current critique version and its issue indexes,
the complete current scene as version-bound evidence handles, approved scene
assignment and narrative permission, canonical Bible, scoped requirements, and
step 3's frozen original repair tests. It resolves prior critiques' exact target
drafts into invocation lineage. Duplicate critique prose and craft scores are
omitted from the adjudicator's context; prior reports and repair advice remain
allegations, not authority. The current scene remains complete.

Each supplied issue requires exactly one decision: upheld, uncertain, unsupported,
or already_repaired; a nonempty assessment; and one to three distinct current
scene evidence handles. The assessment must consider approved permission or
obligation, contextual support and counterevidence, and the original repair
condition. Qualifiers alone establish neither violation nor repair.

Unknown or missing issues, stale or duplicate evidence, malformed assessments,
extra output fields and invalid dispositions fail review validation. They cannot
become manuscript defects. The existing structural retry is bounded; exhaustion
stops production. Upheld and uncertain decisions retain the original blocker.
Unsupported and already_repaired decisions become nonblocking notes in a new
immutable Critique artifact. Every other issue, target identity, score and rubric
verdict is copied unchanged. The new summary identifies released/retained counts
and preserves the prior summary. The original critique is preserved.

Adjudication does not declare a craft pass. When all hard issues are released,
the existing revision-limit policy may accept a nonblocking revise/reject rubric
recommendation. That acceptance remains labelled revision_limit_reached. The
writer is not called again and the manuscript does not change.

## Persistence and diagnostics

Inputs include the source critique, current clear continuity report, prior
critiques and their exact target drafts. Fingerprints include operation, version,
profile, seed and input versions. Successful replay reuses the persisted output.
Checkpoints retain only artifact references, counters and shared adjudication
completion state, reset for each scene. Terminal blocker errors identify the
adjudicated critique and remaining issue indexes.

Successful invocation diagnostics record source critique and candidate version
IDs, keyed dispositions, redacted assessments and current evidence handles.
Released notes also redact assessments before persistence. Invalid adjudication
responses use step 1's bounded unvalidated-review capture; they do not enter canon
or subsequent story prompts. There is no artifact-schema or SQL migration.
Original v29 canary evidence and prior runtime labels remain untouched.

## Verification and rollout

Offline verification covers each decision disposition, current evidence binding,
exhaustive issue coverage, preserved unrelated blockers/scores, fixed repair
history, shorter focused requests, terminal eligibility, the shared call/graph
allowance, real SQLite lineage, redaction, structural retries and replay. Existing
continuity and POV regression controls remain applicable. These simulated outcomes
are not live model-conformance results or new canary completions.

The user's three post-v31 manual stories were verified as successful with 74
production calls and no failed calls. They remain v31 observations. The shared
SammyAI premise for One Bad Year is comparison context, not quality evidence.
Continue the user's manual-test cadence; defer an aggregate manual diagnostic
review until requested after at least ten stories. Do not infer a v32 success
rate from v31 manual runs or offline fixtures.

Verification completed: 511 tests passed in the full Python suite; a final
35-test focused run passed after tightening retry isolation (26 step-4 cases plus
production graph controls). Ruff lint/format, strict mypy on 158 files and the
production build passed. Writer/critic instruction lengths remain 586/3,848
characters; the adjudication instruction is 1,298 characters. A matched fixture
request is smaller than the full critic request. No live v32 Cloud probe or
canary was run in this step.
