# ADR 0016: Explicitly scoped benchmark campaigns

- Status: Accepted
- Date: 2026-09-19

## Context

The September 11 evaluation policy made Cloud the current qualification phase,
with Local and Hybrid deferred. The harness still required a 48-case baseline /
Local / Cloud / Hybrid plan and all three configured presets. Selecting only
Cloud for a canary did not change that plan's formal completion requirements.

The user also intends to test a few other models after v0.1-alpha, tentatively
including GPT and Gemini. Models have not been selected. Campaign scope must be
independent of provider/model identity while preserving exact model snapshots.

## Decision

New plans use plan schema 2 and explicitly declare one supported scope:

- `cloud-first`: every frozen corpus prompt has a Cloud agentic case and a direct
  baseline case. The v0.1 corpus yields 24 cases and, if all succeed, 12 blind pairs.
- `all-profiles`: every prompt has baseline, Local, Cloud and Hybrid cases. This
  remains the CLI default, with 48 cases and 60 eligible pairs if all succeed.

The builder requires exactly the selected profile snapshots. Database planning
validates only selected presets and derives the baseline from the Cloud
scene-writer selection. Scope changes neither seeds nor prompt/graph versions,
budgets, retries, model settings or the mandatory human Blueprint checkpoint.

Schema-2 validation rejects duplicate prompt/target pairs, incomplete matrices,
configuration drift within a target and a non-Cloud Cloud-first baseline. Before
execution, blinding or sealing, the plan must match the exact frozen corpus,
cover every prompt and declared target, and preserve the corpus seeds. Every
selected target has one frozen model/profile configuration for the campaign.

Preparation, Blueprint review/approval and production default to the plan's
agentic targets. Explicit targets outside that plan fail rather than silently
executing a different scope. Batching and resume keep the same plan and report.
Reports omit excluded targets but keep every planned case in their denominators.

Formal scoped archives require all terminal case results, all eligible successful
comparison pairs, exact report-bound story content, human review of every pair
and the recomputed summary. Failed cases remain recorded even though they cannot
supply completed prose for a blind pair. Archive integrity is distinct from
passing the acceptance criteria. The existing rubric and thresholds are unchanged.

## Historical compatibility

Plan schema 1 remains supported. Its absent scope field stays absent when
serialized, preserving canonical hashes and report, review and archive bindings.
Legacy summaries retain their original targets, and old plans still require all
of their planned results to seal. The new scoped corpus and comparison invariants
are not retroactively applied to old archives.

Create a fresh campaign when changing scope or model. Never rewrite the historical
48-case canary plans to make Cloud-only results appear formally complete. No SQL
migration is needed: this versions the campaign-plan file contract, not persisted
database tables. Existing production artifacts and prompts remain unchanged.

## Provider boundary and remaining work

Provider/model identifiers and full profile settings remain frozen and affect
plan hashes. Fixture tests exercise Ollama, hypothetical OpenAI and hypothetical
Google selections without network calls. These establish schema portability,
not live provider compatibility. The executable harness currently uses Ollama
transports; native GPT/Gemini adapters and model selection are future work.

This implements the first Step 19 engineering item only. Honest unknown-cost
accounting, remaining failure-path verification, the full premise-to-story Cloud
comparison against the direct baseline, and independent repeatability with actual
human review and formal evidence sealing remain outstanding. No live evaluation
or human score is produced by this implementation.

## Verification

All 537 Python tests passed in the final full run, including 16 new scoped-campaign
cases. Ruff lint/format and strict mypy passed on 160 files. Frontend formatting,
lint, type checks, all 11 Vitest tests and the production build passed.

The new tests cover Cloud-only configuration, provider-neutral snapshots,
rejected incomplete matrices, scope-aware selection and metrics, resumable
24-case execution, 12 blind pairs, deterministic sealing and rejected missing or
substituted evidence. Legacy 48-case serialization and sealing remain covered.
Read-only checks also confirmed unchanged canonical plan hashes and report
bindings in all six actual v29/v33 Cloud canary archives.

Two older operator fixtures were corrected to use complete matrices over smaller
test corpora. The initial full run also had one failure in the existing parallel
Blueprint recovery test; it passed both an isolated rerun and the final full run
without changes to that test or workflow code. Retain this intermittent result
for the remaining failure-path verification work; its cause is not established.
