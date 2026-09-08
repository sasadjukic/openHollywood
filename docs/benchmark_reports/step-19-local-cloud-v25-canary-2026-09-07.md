# Step 19: v25 canary evidence and v26 follow-up

## Outcome and baseline policy

The v25 canary matches v23 on completed productions and improves scene throughput.
Neither is yet a human-quality benchmark winner. Preserve both as references,
as requested by the operator, until a subsequent matched run beats them.

| Measure | v23 / graph 3 | v24 / graph 4 | v25 / graph 5 |
|---|---:|---:|---:|
| Completed production-runnable cases | 6/9 | 4/9 | 6/9 |
| Local completions, excluding inherited Blueprint failure | 2/5 | 0/5 | 2/5 |
| Cloud completions | 4/4 | 4/4 | 4/4 |
| Accepted scenes | 32/44 | 24/44 | 38/44 |
| Local production model attempts | 90 | 62 | 110 |
| Cloud production model attempts | 92 | 87 | 90 |
| Local production input tokens | 655,700 | 366,537 | 782,070 |
| Cloud production input tokens | 856,556 | 705,184 | 779,662 |

Sources are the matching `plan.json`, `report.json`, and read-only `campaign.db`
under `data/benchmarks/v0.1/v23-canary-2026-09-04`,
`v24-canary-2026-09-05`, and `v25-canary-2026-09-07`. The two reference report
digests are committed in `benchmarks/v0.1/canary-baselines.json`. The frozen
corpus, selected cases, profile snapshots, seeds, and approved Blueprints match.

Local OH-V01-006 is the inherited Blueprint error for omitted beats `beat5` and
`beat6`, case `1a7d4aed-05d6-5dc1-b1d6-54c1f85d18de`. It never entered production.
Exclude only that exact inherited error, not other Blueprint or production
failures. Raw completion remains 6/10. The two-hour correction during v23 was
the operator-confirmed Ubuntu/Windows dual-boot host-clock issue, not an Open
Hollywood defect. Compare provider latency, not affected host timestamps.

## What improved and what remained broken

- Local OH-V01-001 first completed in v25 (5/5 scenes). Local OH-V01-004 recovered
  (4/4). All four Cloud cases again completed (21/21 scenes). The six complete
  stories were within the advisory 2,500–5,000-word range.
- OH-V01-002 accepted 3/5 scenes and passed scene 4's reviews before Bible update
  failed. OH-V01-003 accepted 4/5 and passed the final scene's reviews before the
  same failure. Existing resolved threads were echoed in a later delta. The
  adapter preserved their historical `resolved_scene_id`, while enclosing delta
  validation required resolutions to originate in the current accepted scene.
  This is an application-boundary mismatch, not evidence of bad scene prose.
- OH-V01-005 stopped after 1/4 accepted scenes. Its next scene's goal was to
  pursue evidence, its outcome was a personal argument, and its exit remained
  unresolved. Continuity demanded conclusive evidence while citing historical
  timeline content that did not impose that obligation. The same scene's critic
  passed. Another dusk objection was invalidated, showing v25's release path
  worked in some cases but did not reliably resolve the semantic dispute.
- OH-V01-002 also exposed repair recurrence: a prior problem was declared
  resolved, then reintroduced with different wording despite evidence quoting
  the repaired temporal-bleed mechanism. Summary hashes cannot establish
  semantic equivalence. A separate first-scene viewpoint issue was treated as
  minor by the critic; stronger explicit auditing is needed without reviving
  v24's keyword-based false positives.
- Across v25, 191/200 production attempts were schema-valid. Six Local and three
  Cloud attempts failed validation, including recovered retries. There were 16
  recheck decisions: 13 resolved, one invalidated, two still blocking. Revisions
  generally preserved drafts better, but reliable semantic decisions are still
  the limiting factor. Cloud input rose 10.6% versus v24 for the same four
  completions; more calls and tokens are not automatically better production.
- No human evaluations were recorded. Mandatory semantic requirements and
  target-format gates remain unknown in all six outputs. Technical completion
  is not a substitute for story quality or preference.

The committed regression fixture contains selected safe persisted facts and
excerpts plus reconstructed model-output shapes. Failed raw responses were not
stored. These tests are not a claim of byte-for-byte replay of missing responses.

## Six implemented follow-ups: graph v6 / prompt v26

1. **Correct Bible deltas.** Unchanged already-resolved threads are omitted from
   the current scene's update, preserving their original resolution and scene.
   Reopening or rewriting resolved history is rejected with field-specific
   repair guidance. The domain reducer independently prevents changing an
   existing resolution's scene or explanation. Newly resolved threads still
   receive the current accepted scene as their origin.
2. **Adjudicate terminal non-world disputes once.** A compact, registered node
   compares selected authority, current draft, assignment, and review history
   at the existing revision cap. It can release unsupported demands without
   rewriting prose. Actual/uncertain contradictions stay blocking; other gates
   remain untouched. The existing role/profile, call budgets, secret guards,
   cancellation, two-attempt limit, and durable replay apply. See ADR 0007.
3. **Guard repair recurrence.** Bounded history now includes original allegation
   text. A recheck cannot declare a finding released and introduce a renamed
   non-world blocker using the same canonical source and only the evidence
   just cited for that release. It must correct the prior decision or identify
   a genuinely distinct incompatible assertion. This is a conservative
   partition guard, not a semantic equivalence detector; it never silently
   deletes an alleged real contradiction.
4. **Strengthen regression and positive controls.** Reconstructed v25 fixtures
   exercise the real materializer/domain/reducer boundary, persisted production
   workflow, and replay. A required structured viewpoint audit distinguishes
   actual viewpoint drift from observable third-party behavior; explicit
   violations become hard assignment findings even when overall critique says
   PASS. Tests retain real and uncertain blockers, protect World Rules, and
   exercise missing/invalid adjudication partitions and bounded retry failure.
5. **Separate diagnostic layers.** New failed attempts record provider transport,
   response decoding, application materialization, domain validation, assignment
   validation, or canonical transition as appropriate. Report failure histories
   project the optional layer while remaining backward-compatible. Successful
   continuity/adjudication attempts retain bounded, secret-redacted selected
   source claims, explanations, and decisions. Older failures remain
   `legacy_unknown`; existing evidence is not retroactively rewritten.
6. **Measure repeatability and human quality separately.** Offline tooling checks
   frozen plans, attempted cases, approved Blueprint hashes, and pinned baseline
   report hashes, then reports retained/new/lost successes, accepted scenes,
   all production attempts, tokens, provider latency, and failure/adjudication
   breakdowns. Cross-version A/B packets pair only completed stories for the
   same case, hide run/model provenance, and bind private origins and submitted
   reviews to exact content/packet digests. Blank scores cannot become success.
   Unpaired failures remain visible in the technical comparison. The repeat
   protocol is documented in `benchmarks/README.md`.

## Verification and limits

The full Python suite passes 376 tests, including persisted v26 success,
uncertainty, rejection, bounded repair, and idempotent successful replay. The
comparison tool was checked read-only against the preserved real v23/v25 files;
it reproduces the recorded completion and scene counts without model calls.
Ruff lint/format and strict mypy pass across 146 Python files. Frontend
formatting/lint/type checks, all 11 Vitest tests, and the production build pass.

No v26 canary, human approval, or human scoring was performed for this change.
No host-clock settings, frozen prompts, stored canary reports, source databases,
revision limit, or existing canary cost ceiling were changed. Offline passing
tests demonstrate boundary behavior, not improved live semantic judgments.
Step 19 remains **IN PROGRESS**; the formal campaign and blind review remain pending.
