# Reviewer terminal evidence support, 2026-10-22

**Implemented and verified locally. No live inference or daemon discovery occurred.**
The diagnostic harness now has explicit non-200 fixtures, a tested failure handler
that preserves the gateway exception chain, and an offline terminal audit/export
command. The original sealed preparation and interrupted execution remain intact.

The user reports sufficient funds for the tests. The captured HTTP 500 supplies no
account-balance or billing explanation; server availability, load or maintenance
remain plausible but unconfirmed causes. Missing per-attempt usage stays unknown
as an evidence property, independently of the available funds.

## Scope and decisions

The implementation lives in a separate local support bundle:
`data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/`.

- `terminal_evidence.py` provides offline `audit` and `export` commands and the
  terminal-record/length-exception helpers.
- `mock_runner.py` integrates those helpers into a successor of the frozen runner.
  It accepts only `httpx.MockTransport` with offline mode enabled; it has no live
  execution command. Existing request construction, validation, scoring, schedule,
  budget reservation, sentinel decisions and completed-cell replay are reused.
- `http-fixtures.json` records sixteen explicit non-200 response fixtures.
  `test_terminal.py` tests the handler, accounting and export boundaries.

This support is specific to the isolated reviewer pilot format. Legacy compatibility
is pinned to the exact October 22 interrupted bundle manifest; arbitrary older or
unsealed terminal records are rejected. No production provider adapter, prompt,
schema, graph, database or application UI changed. No dependency was added.

## Failure behavior

Non-200 responses never enter the answer evaluator or the special length-failure
path. The original `ModelGatewayError` remains the raised exception, including its
code and retryability metadata. Its cause/context chain is recorded with exception
types, relationships and messages; registered secrets are redacted and request
headers are not recorded. A provider's `retryable` flag does not authorize a retry.

New terminal records bind the plan, failed reservation, exact captured files and
HTTP/body hashes, with a separate terminal seal. They distinguish reserved calls
from dispatched attempts. Unreported input/output tokens and actual cost are null,
not zero. The full reservation stays attached to a failed dispatched attempt.
Measured attempt duration, when available, is separate from provider usage.

The supported audit verifies completed receipts normally, then checks the final
unfinished reservation and terminal evidence separately. It rejects altered data,
missing seals, skipped cells and dispatch after a sentinel/terminal stop. An audit
can be complete while the experiment remains incomplete. It never synthesizes a
successful receipt, releases a reservation or makes a stopped run resumable.

The export writes into a new directory outside the source. It includes:

- An audit with known completed-response usage and separate unknown failed usage.
- The completed-response inspection packet and its key, using the frozen shuffle
  and normalized assessments. Invalid responses remain invalid; a failed HTTP
  attempt has no assessment and is not added as a review sample.
- A separate terminal-attempt inventory with source bindings.
- A manifest of exported and source files, checked for source changes during export.

Existing destinations are rejected rather than overwritten. A process interruption
that leaves an incomplete terminal seal still fails verification; this change is
not automatic recovery or a new continuation policy.

## Verification

**58 tests pass: 36 local diagnostic tests plus 22 existing gateway/contract tests.**
Ruff lint/format and strict mypy pass on the three new Python files. Tests use
in-memory HTTP responses; real transports are blocked in the diagnostic tests.

The sixteen non-200 fixtures cover 400, 401, 403, 404, 408, 429, 500, 502, 503 and
504 responses, plus HTML/empty error bodies, a false length envelope, misleading
usage fields, a redirect and an empty 204 response. An error body that resembles a
successful length response is still terminal, and its numeric fields are not
accepted as complete usage evidence.

Additional checks cover transport failure and its gateway cause chain, timeout,
cancellation, invalid/missing usage, preflight failure before any reservation,
normal valid/invalid/length outcomes, source/terminal tampering and export overwrite
protection. The entire 48-cell schedule passes through mocks, including restart
at a completed-cell boundary. A separate mock reproduces D's eight-cell stop,
T's one complete response and the following HTTP 500, with no later dispatch.

The original runner's actual failure was also audited and exported offline:
**10 reserved/dispatched attempts, 9 complete responses, 1 unknown-usage failure,
D stopped, 38 unstarted cells**. Its nine reports retain the previous inspection
results; this export does not call for another human review or rescore the run.
The historical terminal still records `ValueError`, with the previously saved
gateway error chain retained as a historical operator observation. It is not
rewritten to pretend the new handler produced the original record.

The original preparation seal remains:
`7256b677fab8fa4f226a0a3e0595339809c6f2af35147e751055df8fe6595cbe`.

The original execution manifest remains:
`a7f9e0973d5f93009834461109baa3c76d348bb83cd94f2a9524eb29f7207903`.

The first local suite passed 35 tests. One later invocation named a nonexistent
gateway test file and collected no tests; the corrected final invocation passed
all 58. Both earlier XML records remain available. No model request was retried.
Application-wide build checks were not repeated because production source did not
change; the affected diagnostic and provider-boundary checks above were run.

## Local commands and evidence

From the repository root, audit the stopped run without writing to it:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/terminal_evidence.py audit --source data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live
```

To create another inspection export, use a new destination name:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/terminal_evidence.py export --source data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live --output data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/historical-export-copy
```

The verified export already exists at
[historical-export](../../data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/historical-export/).
See its [audit](../../data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/historical-export/audit.json),
[terminal attempts](../../data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/historical-export/terminal-attempts.json)
and [manifest](../../data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/historical-export/export-manifest.json).
The [fixtures](../../data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/http-fixtures.json),
[verification](../../data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/verification.json)
and [support manifest](../../data/diagnostics/reviewer-terminal-evidence-v61-2026-10-22/support-manifest.json)
remain in the ignored local bundle; no private prose is published by this work.

## Status before another run

The requested local terminal-evidence work is complete. It does not reopen the
previous run. Any later live continuation needs an explicit policy and a new
seal/approval for the executable changes, carrying forward the ten consumed
attempts and D's sentinel stop. The current bundle deliberately supplies only
offline audit/export and mock runner integration.

The [interrupted pilot results](../benchmark_reports/reviewer-isolated-pilots-v61-results-2026-10-22.md)
remain unchanged: limited D1 delivery evidence, one unsupported T1 explanation,
and no R1 observation. All critic/writer issues remain open. Production remains
**prompt 61 / graph 9 / fulfillment policy 1**. The canary is **ON HOLD**;
Step 19 remains **IN PROGRESS**, Step 20 **NOT STARTED**. Human judgments about
feel/emotion, flow, character and story-breaking concerns remain separate from
transport failures and mechanical report validity.
