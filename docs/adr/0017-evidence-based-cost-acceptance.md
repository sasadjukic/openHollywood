# ADR 0017: Evidence-based cost acceptance

- Status: Accepted
- Date: 2026-09-19

## Context

The Ollama adapter populates `estimated_cost_usd` with zero without receiving a
per-call dollar charge. The evaluator previously treated that value as known and
could pass the Cloud cost criterion. Historical positive amounts also lack an
explicit provenance field. Numeric values, subscription capacity and configured
ceilings alone cannot establish actual cost acceptance.

Baseline report reconstruction additionally omitted failed attempts when a later
attempt succeeded. Agentic reports already aggregate Blueprint and production
invocations, including recovered failures. Both paths need complete cost evidence.

## Decision

Provider-neutral responses and persisted invocations carry `ModelCostBasis`:
`unknown`, `provider_reported` or `local_inference`. Unknown is the default.
Provider-reported amounts must be finite and nonnegative, with explicit zero
allowed. Local inference declares zero provider charge only for local deployment;
it excludes hardware, electricity and other operating costs. No current adapter
may label an unreported Cloud amount as a local or verified zero.

Migration 0008 adds the invocation basis with an UNKNOWN default. It preserves
existing numeric amounts, foreign keys, artifacts and history; no backfill infers
provenance from provider names, values or deployment. New successful and rejected
responses persist their basis. Interrupted or unreported calls remain unknown.
Existing runtime amount fields and budget enforcement behavior remain unchanged.

New benchmark outputs include one cost record for every invocation ID, with a
null amount for unknown evidence. The complete story total exists only when all
records are known. Agentic coverage includes the Blueprint and production runs;
baseline coverage now includes all attempts and preserves cost/usage from a
rejected response. Replaying either path uses the persisted evidence.

Summary schema 2 reports known/unknown planned-case coverage for every target.
Missing cases, failed cases without complete outputs and incomplete invocation
evidence remain unknown. A target median is available only with complete coverage.
The Cloud/Hybrid acceptance criterion is null until all planned applicable cases
have complete story costs; then their median is compared with the unchanged
acceptance budget. Baseline costs are reported separately. Partial known samples
cannot pass the full campaign's cost criterion.

The current Ollama Cloud adapter remains unknown; Local responses explicitly
record zero provider charge. This adds neither live price lookups nor token-rate
estimates or subscription allocations. Future pricing or billing integrations
must provide their own reproducible evidence. Unknown cost also means current
runtime dollar ceilings cannot prove an actual billed-spend cap.

## Historical compatibility

Optional output evidence is omitted when absent, preserving old report content.
Current summaries always use the new evidence policy, including for older plans.
New seals use evidence schema 2 and require a schema-2 summary, so an old numeric
cost pass cannot be submitted as a new qualified result. A seal may record null
cost acceptance: archive completeness is distinct from qualification.

Schema-1 archives verify under their original cost arithmetic and retain exact
canonical bytes and hashes. That path is private to archive verification, with no
legacy-policy switch in the summary/seal CLI. Verification output identifies the
policy used. A fixed synthetic pre-change archive tests this compatibility and
the rejection of its old cost pass by current summary/seal operations.

## Rollout and scope

Apply the normal Alembic upgrade to the active database before starting the
updated application or database-backed harness. Preserve old campaign databases
and evidence; reanalysis should write separately. No user production database or
historical report is migrated or rewritten during implementation.

Production prompt v33, graph v9, model selection, retry allowances and all runtime
limits remain unchanged. No pricing assumptions, provider adapters, paid calls or
literary judgments are added. Item 2 is an accounting implementation, not evidence
that the current model meets the cost budget. Step 19 remains IN PROGRESS.

## Verification

All 560 Python tests passed, including 22 new cost cases and a populated migration
round trip. Ruff lint/format and strict mypy passed on 163 files. Frontend format,
lint, type checks, all 11 Vitest tests and the production build passed.

Checks cover unknown versus explicit zero, over-budget reported cost, non-finite
values, complete invocation/case coverage, mixed local/Cloud evidence, baseline
recovery, rejected-response persistence and missing Blueprint/production costs.
The pre-change synthetic archive remains byte-identical and verifiable, while
current summaries and seals cannot reuse its unsupported cost pass.

Read-only checks of all six actual v29/v33 canary plans/reports preserved their
bytes and plan bindings and classified their Cloud costs as unknown. No live
model request, user-database migration or historical-evidence rewrite was made.
