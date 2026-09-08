# Step 19: v27 isolated specialist probes

## Evidence and scope

Eight predeclared saved-input probes ran on 2026-09-08 from commit
`d97bf2c75337229d20a43f01e359c51fb2cf83dd`, using prompt v27 / graph v7.
The local diagnostic directory is
`data/diagnostics/v27-isolated-2026-09-08-2006`.

- Report SHA-256:
  `2574714908ceb6af5b52f794ab0413e97089d28e24e70810aed806de2f660b33`.
- Local 005 request SHA-256:
  `2d83249ad2cef06bb65094ebd86f00b21019c2f8aa7b21ffe6cfd7b96327ed0f`.
- Local 005 result SHA-256:
  `4e1d4d38914259c4d4b64fe0cb225bb8c510303f9418df8d6a06f3c0fa21ef8b`.

These are isolated specialist responses, not full story completions, independent
canaries, human ratings, or new canonical artifacts. Source inputs were read-only;
all ten protected files retained their recorded hashes. The machine report's
`semantic_review_status: pending` is preserved; this document records the subsequent
assistant diagnostic assessment separately, not a human quality review.

## What worked

All eight responses validated on the first attempt: eight calls, 59,000 reported
input tokens and 3,647 output tokens, about 115 seconds of monotonic elapsed time.
No structural repair calls were needed.

The five Local critics and Cloud 002 all returned `pass` without issues. In
particular, Local 002's first-person interiority and Local 003's approved
investigator deductions no longer caused the earlier hard viewpoint blockers.
This supports response reliability and recovery on those fixed inputs, not
general correctness of every critic judgment.

Both Local Bible probes passed the real reducer. Local 002 retained the resolved
`relationship_elara_to_future` thread's original scene `s3` and resolution;
Local 003 retained `thread_memory_anchor_shift` at `scene_4` with its original
resolution. Their returned deltas had no thread changes and added the current
scene's timeline event. Exact historical thread objects were unchanged. This
confirms the intended history-preservation check, not comprehensive story-memory
quality or completeness of every extracted fact.

## Why the canary was held

Local 005 was the positive control for genuine other-character private access.
Its scene explicitly assigns Elara, but `draft_evidence_0044` states:

> Cora felt the familiar, hot burn of being intellectually dismissed.

The following sentence continues Cora's private interpretation. The approved
style asks for literary, internalized prose and emotionally weighted dialogue;
it does not specifically authorize switching to Cora's private perspective.
This is different from Elara's inference about Cora or Cora speaking about her
feelings. Nevertheless, the critic awarded 5/5, praised viewpoint adherence, and
returned no issues. The assistant assessment is a missed private-state violation.

Eight valid responses therefore did not constitute eight semantically successful
checks. The likely prompt weakness is conflating plausible emotional inference
or generic internalized style with authorized access to another character's
private experience. This is an inference from the supplied prompt and output,
not access to the model's hidden reasoning.

No v27 full canary was prepared or launched. There is no new production completion
score to compare with v23/v25, which remain the pinned baselines.

## Targeted follow-up

Prompt v28 / unchanged graph v7 clarifies that boundary and supplies compact,
non-canonical contrasting examples; see ADR 0009. It does not change the writer,
add calls, require proof of alignment, or implement a keyword-based semantic gate.

The new `benchmarks/v0.1/production-probes-v28.json` selects the same historical
Local 002, 003, and 005 critic inputs, with explicit expected viewpoint outcomes.
At most two calls per probe are permitted, using their original model, seed, and
per-call budgets. A different valid craft judgment is not automatically a failure;
inspect the specific viewpoint finding and its exact evidence.

The follow-up probes are prepared, not run. The full canary remains on hold.
Offline regression checks can establish prompt delivery and response handling,
but only live semantic inspection can show whether the model now catches the
positive control without restoring the false blockers. Step 19 remains
IN PROGRESS; repeatability and blind human review remain outstanding.

## v28 implementation verification

- Ruff lint and format checks: pass.
- Strict mypy: pass across 150 Python files.
- Full Python suite: 412 passed, including 16 new viewpoint controls.
- Frontend formatting, lint, type checks, and all 11 tests: pass.
- Production build: pass.
- All three follow-up selections load and compile read-only with exact artifact
  hashes; Local 005's declared evidence reference matches the saved sentence.
- Syntax-tree comparison confirms that only the critic's specialist instructions
  changed. Writer, continuity, adjudication, and Bible specialist instructions
  remain unchanged; the shared production prompt version advances to 28.
- Thirteen protected historical/probe file hashes remain unchanged, including the
  pinned v23/v25 evidence and completed v27 report/request/result cited above.
- No live model calls or canary launches were made for this implementation.

These checks verify the implementation and its boundaries, not the live model's
ability to distinguish the semantic cases. That remains the next isolated test.
