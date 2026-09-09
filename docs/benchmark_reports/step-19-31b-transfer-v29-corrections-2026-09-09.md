# Step 19: 31b critic transfer and v29 corrections

Date: 2026-09-09

## Evidence, not a canary score

The frozen candidate stage under
`data/diagnostics/31b-next-stage-2026-09-09-1837` made 33 Cloud calls without
retries. Novel POV controls: 24/24 valid and target-correct against provisional,
assistant-authored labels. Full-critic transfer: 9/9 raw POV decisions correct,
but only 6/9 complete responses valid. These are three scenes sampled three
times, not nine independent stories.

The Local-005 positive control correctly identified Cora's unauthorized
interiority at historical evidence ordinal 0044 in all three samples.
Local-002 failed exact-evidence validation in all three samples because
`draft_evidence_0040` was returned where an exact quotation was required.
Resolving that ID in offline copies removed the mechanical error; those copies
do not count as live successes. Local-002's proposed physical-compulsion repair
and Local-003's unqualified praise remain separate judgment questions.

Historical transfer report SHA-256:
`b1ce6e090a537ecdbb7ad6421bc8a27199b5be6f2777824d55a0b5dbf3a0f3a9`.

## Implemented correction

Prompt v29 / graph v7 is developed on `codex/v29-production-contract`.
ADR 0010 describes the unified, version-bound evidence interface and fixed
scene-craft rubric. All three critic finding routes now select exact current
handles. The server supplies persisted quotations and deterministic hard-gate
verdicts. Rubric identity and mean are application-owned; each of the three
craft dimensions must appear exactly once.

No canonical schema, database migration, frontend API, writer behavior, routing,
continuity logic, graph node, budget, or retry allowance changes.
Existing critiques remain readable; old wire fields are deliberately not
reinterpreted under the new prompt version.

Generic outcome guidance preserves both genuine missing-outcome blockers and
advisory suggestions to strengthen an already-achieved beat. It does not settle
the disputed historical scenes or expose held-out answers as prompt examples.

## Verification

All documented Python checks pass: Ruff lint/format, strict mypy across 151
source files, and 449 tests (including 37 new critic-contract controls). Frontend
format/lint/type checks pass, all 11 Vitest tests pass, and the production build
succeeds. Git whitespace checks pass.

Read-only compilation of Local-002/003/005 through both Local and Cloud paths
passes with matching call-specific schemas and verified immutable input hashes.
The current draft catalogs retain 40, 45, and 61 excerpts respectively; Cora's
historical 0044 excerpt remains exact under its version-bound handle. All 425
files protected by the completed transfer plan and the final v28 review's bound
reports remain byte-identical. The local verification helper is preserved at
`data/diagnostics/v29-implementation-2026-09-09/check-frozen-inputs.py`.

These are offline checks, not proof of provider grammar compatibility, live model
understanding, or completed story quality. Actual model token usage and behavior
under the changed rubric/reference format still require a new frozen evaluation.

## Next evaluation boundary

`benchmarks/v0.1/critic-transfer-v29.json` declares the next frozen comparison,
not a running job or production promotion. It preserves all three historical
invocation IDs, expected POV outcomes, and report hashes. It also explicitly
requires expanded non-POV positive/negative controls before promotion.

Before a live expanded run, freeze complete control artifacts and adjudicate
their expectations. Human review of the novel labels and Local-002 outcome /
Local-003 quality remains pending. The bounded critic-to-writer revision loop
must subsequently demonstrate correct repairs without invented mechanics or
surrounding residual POV errors.

No live generation or canary is part of this implementation. Keep the v23/v25
baselines and Step 19 IN PROGRESS.
