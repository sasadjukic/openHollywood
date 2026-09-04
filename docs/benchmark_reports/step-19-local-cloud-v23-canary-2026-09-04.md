# Step 19 Local/Cloud prompt-v23 canary diagnostics — 2026-09-04

## Provenance and scope

This diagnostic covers
`data/benchmarks/v0.1/v23-canary-2026-09-04/report.json` and compares it with
the prompt-v22 canary in
`data/benchmarks/v0.1/v22-canary-2026-09-04/report.json`. The v23 run used the
same corpus, cases, profile snapshots, seeds, Blueprint contract, and workflow
versions as v22; the scene-production prompt changed from v22 to v23. This is
therefore a clean prompt-contract comparison.

Ten Local/Cloud agentic cases were attempted. Local OH-V01-006 remains the
known Blueprint-stage negative control and never entered production. Of the
nine production-runnable cases, six completed, two reached the continuity
revision limit, and Local OH-V01-002 paused. The pause coincided with Windows
correcting a two-hour system-clock error after an Ubuntu-to-Windows dual boot;
it is environmental evidence, not an Open Hollywood active-time defect. No
runtime clock change is part of the v24 contract.

Human review fields remain unset in this execution report. Completion counts
below measure technical production success, not blind story quality.

## What worked

| Measure | v22 | v23 |
| --- | ---: | ---: |
| Production-runnable completions | 3/9 | 6/9 |
| Successful production model attempts | 101/113 | 179/182 |
| Structurally valid continuity attempts | 23/35 | 49/51 |
| Local structurally valid continuity attempts | 2/12 | 26/26 |
| Completed-story advisory word range | mixed, including 6,636 words | 3,514–4,263; all in range |

Prompt v23 removed the redundant non-world certificate fields responsible for
all six v22 terminal failures. None of those `conflict_kind`, lexical
assessment, or exact-copy failures recurred. Three isolated structured-output
failures—a writer assignment mismatch and two incomplete continuity
objects—recovered on the one bounded retry. Cloud remained strong, and Local
continuity throughput recovered completely.

The story-wide length contract also behaved as intended. Every completed story
landed inside the advisory 2,500–5,000-word range without turning a per-scene
allocation into a revision gate.

## Remaining production defects

Local OH-V01-001 exhausted revisions in a semantic repair ping-pong. A
continuity report first requested resistance or a localized field, the writer
made that repair, and a later report demanded an energetic field before a
subsequent report returned to effectively the same wording. The application
remembered only the immediately preceding report, so the same semantic concern
could return under a new identity and appear newly exposed.

Local OH-V01-003 exposed a different failure. Its second revision repaired the
original location and character mismatch, but the third candidate replaced
almost the entire scene with material assigned to the following scene. Draft
similarity fell to approximately 0.024. The critic nevertheless returned PASS
and treated the wrong viewpoint as minor; continuity then found four blockers.
Across Local revisions, 5 of 12 adjacent draft pairs had similarity below
0.10, compared with approximately 0.87 and 0.93 for the two Cloud revisions.
The Local writer was often rewriting instead of patching.

All 49 successful v23 critiques returned PASS, including 25 with minor issues.
The OH-V01-003 viewpoint/scene-assignment miss proves that PASS was not a
reliable structural gate. Terminal cases also still collapsed to the generic
message “blocking continuity findings remain at the revision limit,” which hid
the actual blocker identities and recurrence pattern from `report.json`.

## Production contract v24

Production graph v4 and prompt contract v24 implement the following bounded
changes:

- Writer and critic prompts receive only the current scene's Blueprint slice:
  current characters, relationships, location, applicable World Rules, beats,
  and Scene Plan. Future scene plans and future-only characters are omitted,
  while story-wide theme, conflict, ending, and style guidance remains visible.
- Every revision receives an application-built repair ledger and an explicit
  preserve/prohibit contract. When critique already passed and continuity is
  the only reason to revise, word-sequence similarity to the prior draft must
  remain at least 0.35. A broader rewrite is a retryable
  `scene_revision_scope_exceeded` contract failure, and successful invocations
  persist the measured similarity.
- Checkpoint state now retains the complete, bounded continuity history for the
  current scene. The supervisor sees compact historical blocker identity and
  repair direction; the application maps a recurring semantic requirement,
  canonical claim, or World Rule back to its first stable finding ID and marks
  it `still_blocking` instead of `newly_exposed`.
- Blueprint `story_role` and relationship `history` prose no longer qualify as
  selectable contradiction claims. They remain creative planning context, not
  immutable story facts. Exact names, initial knowledge, location constraints,
  canonical Story Bible state, and World Rules remain enforceable.
- An explicit wrong viewpoint, wrong assigned character, future-scene drift,
  or replacement of the planned goal, turning point, outcome, or exit state is
  promoted to a blocking critique and forces REVISE; it cannot survive as a
  minor issue on PASS.
- Revision-limit failures use the stable
  `continuity_revision_limit_reached` cause and include bounded finding IDs,
  categories, bases, and re-check dispositions without embedding story prose.

The graph version advances because continuity history changes durable
checkpoint state. No persistence migration is needed: the checkpoint remains
JSON-safe, reference-only state.

Implementation verification passes across the repository: Ruff lint and
formatting over 134 Python files, strict mypy over 134 source files, all 276
pytest tests, frontend formatting/lint/type checking, all 11 Vitest tests, and
the production build.

## v24 canary acceptance criteria

The next canary should reuse the same corpus, cases, profiles, and seeds. Its
technical acceptance checks are: no future-scene leakage in writer or critic
prompts; no continuity-only revision below the 0.35 similarity floor; stable
IDs for semantic recurrences; no minor/PASS disposition for an explicit scene
assignment defect; zero v22 certificate regressions; and cause-oriented
terminal evidence for any revision-limit failure.

A completed technical canary is not the final quality verdict. Public review
packets must still be scored blind so `mandatory_requirements_present`,
`target_format_valid`, rubric scores, and pairwise preference are populated by
human judgment rather than inferred from model self-review.
