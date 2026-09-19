# Step 19 failure-path verification

Date: 2026-09-19. Scope: item 3 of the remaining Step 19 engineering work.

This verification uses isolated migrated SQLite databases, deterministic model
fixtures and injected HTTP/file/process failures. No live model request, user
database write or historical benchmark rewrite was performed. Production prompt
v33, graph v9, model routing, revision/retry allowances and budgets are unchanged.

## Defects reproduced and fixed

### Interrupted Blueprint calls remained running after recovery

A simulated process exit during the premise call left its persisted invocation
RUNNING. A new Blueprint service successfully completed preparation, but the old
call still appeared active. The regression failed on that exact assertion before
the fix.

Blueprint resumption now reconciles orphaned calls before executing the graph.
It uses the same reconciliation routine as production: mark the old call failed
with `interrupted_execution`, retain its input/version history, record detection
time separately from unknown provider completion, and emit the affected invocation
IDs in recovery diagnostics. The abandoned active interval is discarded. An
unknown provider outcome does not become a known zero charge.
The old call still counts toward aggregate budgets and cost evidence, but process
loss supplies no rejected model response and is excluded from repair instructions.

Successful invocations and their immutable outputs are preserved. Separate tests
interrupt between output persistence and the graph's completion/checkpoint write;
resumption reuses that output without another model call. This is distinct from
an interruption before any response was durably recorded, which may require a new
provider call. Exactly-once remote billing is not asserted.

### Worker shutdown could interrupt cancellation cleanup

The worker cancelled active execution directly and then cancelled the claimant
awaiting that same execution. The second cancellation could prevent the model
executor from recording a terminal invocation. A blocked-provider shutdown test
reproduced the stale RUNNING record before the fix.

Shutdown now cancels each active task once and awaits its cleanup before closing
the claimant. Repeated stop commands also avoid cancelling a task already handling
cancellation. A restarted worker resumes unfinished shutdown work, respects a
durable user stop, processes an independent story, and still pauses for mandatory
Blueprint approval before drafting.

### Parallel recovery verification depended on timing

The old test signalled completion after artifact persistence, before the observer
and LangGraph pending writes completed, then waited 10 ms before failing a sibling.
That delay did not establish the durability condition its assertions required.
The earlier intermittent failure cannot independently identify which boundary was
reached in that historical run.

The test now releases the failing sibling only after the SQLite checkpointer has
committed the successful World's pending writes. The assertion still requires
that recovery execute only Character, Integration and Evaluation. No production
delay or weaker assertion was introduced. The committed-output recovery tests
separately cover the earlier window, where executor replay may run but must avoid
another model request or artifact version.

## Verification matrix

Test paths below are relative to the repository's `tests/` directory. New cases
use the actual application persistence, graph/services or HTTP adapter as noted.

| Failure or boundary | Verified outcome | Test evidence |
| --- | --- | --- |
| Cloud HTTP 401/403, 404, 429, 503; connection failure; read timeout; malformed JSON | Direct baseline stops after one attempt. Blueprint uses at most its existing two attempts for retryable faults and one for terminal faults. All calls become terminal, cost remains unknown, no output is promoted, and raw provider bodies/credentials are absent from persisted errors. | `evaluations/test_failure_paths.py::test_cloud_faults_persist_terminal_attempts_without_unbounded_retry` (16 cases, real Ollama adapter with mock HTTP transport) |
| Process loss during Blueprint call | The old call becomes terminal with unknown provider outcome; the completed brief is reused; replay remains at human approval. | `evaluations/test_failure_paths.py::test_blueprint_restart_reconciles_open_call_and_preserves_completed_work[open_call]` |
| Blueprint output committed before graph completion | Exact premise/brief versions survive; neither needs another provider call. | Same test, `committed_output` |
| Completed parallel sibling checkpoint followed by sibling failure | A new graph service resumes only the unfinished sibling and downstream work; artifact count remains unchanged by replay. | `workflows/test_blueprint_workflow.py::test_failed_parallel_superstep_resumes_without_repeating_successful_sibling` |
| Process loss during scene 2 continuity | Scene 1 stays accepted at its exact version; scene 2 draft/critique are reused; the orphaned call is reconciled. | `evaluations/test_failure_paths.py::test_production_recovery_keeps_accepted_scene_and_exact_artifact_lineage[open_call]` |
| Scene 2 continuity timeout exhausts retry allowance | Two attempts reference identical inputs and leave a failed run. Explicit subsequent execution recovers without repeating accepted scenes or prior scene 2 work. | Same test, `timeout_exhausted` |
| Scene 2 continuity output committed before graph completion | Recovery reuses that report without another continuity call; prior artifact hashes and accepted scene lineage remain intact. | Same test, `committed_output` |
| Worker shutdown / durable user stop during a provider call | Shutdown awaits terminal call cleanup. Restart resumes shutdown work but never auto-resumes a stopped run. Duplicate stop commands are idempotent; an independent story continues. | `worker/test_runtime.py::test_worker_cancels_active_call_and_restarts_only_unfinished_work` (2 cases) |
| Disk-full error during partial temporary report write / persistent Windows replacement lock | Previous report bytes survive; temporary and lock files are cleaned up; lock retries remain bounded. Once writable, the report is reconstructed from persisted story output without another provider call. | `evaluations/test_failure_paths.py::test_report_write_failure_preserves_prior_bytes_and_replays_persisted_story` (2 cases) |
| Rejected review output and bounded structured recovery | Unvalidated critique/continuity evidence stays diagnostic; it cannot become story truth or promote an invalid artifact. | Existing `api/test_production_failure_evidence.py` |
| Uncertain, upheld or repeatedly malformed adjudication | The original blockers remain; adjudication cannot bypass revision limits, address unrelated allegations or release independent hard blockers. | Existing `api/test_production_v26.py`, `api/test_production_v32.py` and `api/test_production_v33.py` |
| Budget exhaustion, pause/resume and explicit node retry | Budget enforcement happens before another call; retries preserve source history and exact prerequisites. | Existing `api/test_run_controls.py`, `workflows/test_run_controls.py`, `workflows/test_production_runtime.py` |
| Failed case / handoff isolation and baseline interruption | Failed cases remain visible while independent cases proceed; failed production handoff is terminal; interrupted baseline attempts remain in report cost lineage. | Existing `evaluations/test_harness.py`, `evaluations/test_agentic_production.py`, `api/test_production_workflow_hardening.py` |

The additions comprise 25 parametrized cases. The existing parallel recovery test
was corrected in place.

## Validation and remaining scope

All **585 Python tests passed**. The 30 affected provider, Blueprint and worker
tests also passed after the final repair-context adjustment. Ruff lint/format and
strict mypy passed on **165 files**. Frontend formatting, lint, type checks, all
**11 Vitest tests** and the production build passed. `git diff --check` passed.

Item 3 is **COMPLETE** for the application/harness failure paths in this matrix.

These are engineering failure-injection results. They do not establish live
critic/adjudicator accuracy, story quality, provider availability or cost
qualification. A synthetic `BaseException` models process loss at a selected
boundary; it is not a physical Windows crash or power-loss test. Injected ENOSPC
covers report-file failure, not SQLite corruption or an actually full disk.
Packaged desktop/OS failure testing remains Step 21 work.

Step 19 remains IN PROGRESS. Its next items are the full premise-to-story Cloud
comparison against the direct baseline, independent repeatability and formal
evidence sealing after real human review. Item 3 adds no live campaign results.

No database migration or API-contract regeneration is needed for this change.
