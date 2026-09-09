# ADR 0010: One version-bound evidence interface for the scene critic

- Status: Accepted
- Date: 2026-09-09

## Context

The 31b candidate passed 24 novel viewpoint controls against provisional
assistant labels. Its unchanged v28 full-critic transfer made nine correct raw
POV decisions, but only six complete responses validated. All three Local-002
responses used an evidence ID in an assignment field requiring a quotation.
Ordinary craft findings also returned IDs that were not resolved. Two Local-005
responses said pass despite a real typed POV violation; existing normalization
correctly enforced revise.

Correct POV decisions do not certify the critic's other judgments. Local-002's
outcome criticism and Local-003's mathematical/literary quality remain disputed,
not approved manuscript revisions.

## Decision

New model requests use prompt contract v29 with unchanged production graph v7.
Develop these corrections on `codex/v29-production-contract`.

Every model-authored assignment, POV, and ordinary craft finding uses
`draft_evidence_refs`: one to three distinct references selected from one
current-draft catalog. A shared JSON Schema definition holds the call-specific
enum once. Application validation rejects unknown references, literal
quotations, duplicates, empty/oversized lists, and legacy unscoped handles.

Critic handles combine the sentence ordinal with the exact immutable draft
version UUID. Even an identical sentence at the same ordinal in a different
version has a different handle. The original canonical input versions remain
the source of truth; no text matching, fuzzy repair, or guessed reference
translation occurs. Continuity's independent evidence protocol is unchanged.

The application resolves references to exact excerpts before canonical
validation and persistence. Craft evidence is resolved before application-owned
POV and assignment issues are appended. A blocking craft issue also forces
revise, as typed POV/assignment violations already do. Advisory length
normalization remains in force; no high mean score can clear a remaining blocker.

Pin the scene-only craft rubric to `prose_quality`, `dramatic_progress`, and
`character_consistency`, each scored once on the existing 1-5 scale. Rubric name
`scene_craft`, version `1`, and unweighted mean are application-owned.
The model-facing schema excludes generated rubric identity/overall score;
application validation rejects missing, duplicate, or invented dimensions.
Scores are not a compliance score and do not replace the canonical blind human
whole-story rubric. There is no new model-authored compliance certificate.

Prompt guidance asks the critic to consider the whole scene before claiming a
missing outcome, including embodied and indirect realization. A truly absent or
incompatible outcome remains blocking. A demand for stronger dramatization or
an unrequired new mechanism is craft advice. No word-based semantic gate,
automatic ruling on the disputed scenes, or hidden permission to invent story
events is introduced.

## Compatibility and scope

Canonical Critique and CritiqueIssue schemas are unchanged: persisted evidence
remains exact quotations. Existing artifacts and historical rubric dimensions
remain readable. No SQL migration or API regeneration is needed.

Old wire responses are not silently accepted as v29. Historical probes, reports,
prompts, registries, and source campaign databases are not rewritten or retagged.
Run new tests in a new diagnostic directory with a separately pinned request
manifest. Do not resume a historical campaign under the new contract.

Writer instructions, model/profile routing, graph transitions, continuity,
adjudication, Bible reducers, budgets, retries, revision limits, and mandatory
Blueprint approval remain unchanged. 31b is not promoted into Local, Cloud, or
Hybrid production defaults.

## Verification and promotion

Offline tests cover all three finding routes, source immutability, exact
resolution, stale/unknown/duplicate rejection, old-wire rejection, old-artifact
readability, fixed rubric dimensions, and hard gates despite high craft scores.
Simulated missing/achieved-outcome controls verify the boundary, not an ability
to infer literary truth.

The v29 transfer declaration preserves the three frozen scene invocation IDs and
historical report hashes. Novel labels and the Local-002/003 judgments retain
explicit pending human-adjudication status. A live expanded full-critic control
suite and bounded revision/re-critique tests are still required. No live model
test or canary is launched by this implementation. Step 19 remains IN PROGRESS;
v23/v25 remain the canary baselines.

