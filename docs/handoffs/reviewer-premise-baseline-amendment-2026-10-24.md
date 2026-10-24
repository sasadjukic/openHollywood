# Frozen D2/premise-check baseline amendment

Date: 2026-10-24. **PREPARED AND VERIFIED; AWAITING INFERENCE APPROVAL.**
The authorized metadata-only probe confirms **Ollama 0.40.10** and unchanged
DeepSeek model metadata. **Zero inference calls** occurred. The comparison
retains its **32-call total ceiling**. Production remains **prompt 61 / graph 9 /
fulfillment policy 1** and the full workflow canary remains **ON HOLD**.

This amends the [original frozen plan](reviewer-premise-frozen-plan-2026-10-24.md)
after its [zero-call version-mismatch stop](../benchmark_reports/reviewer-premise-v61-results-2026-10-24.md).
The original plan, approval, terminal ledger, inspection, report and seals remain
unchanged. The original terminal ledger cannot resume.

## Exact amendment

| Item | Original | Amended |
| --- | --- | --- |
| Expected daemon | 0.40.9 | **0.40.10**, verified through the daemon |
| Version evidence | Initial mismatch lost the returned version | Persist and seal request/response observations before validation, at initial preflight and before/after each generation |
| Execution identity | `reviewer-premise-v61-2026-10-24` | `reviewer-premise-amendment-v61-2026-10-24` |
| Previous model calls used | 0 | **0** |
| Remaining / combined model-call ceiling | 32 / 32 | **32 / 32** |

All **43 experimental input files**, including the **32 prepared requests**, are
copied byte-for-byte. The wire payload generated for each request is identical
to the original. This includes the complete original/revision prose and context,
both D2 and PC prompts, exact premise-check card, schemas, artifact versions,
evidence catalogs, cases, acceptance labels, paragraph groups, order, settings,
budget, scoring and stop rules. Runtime fingerprints also match. The amendment
adds no repair, replacement, judge call, inference allowance or production change.

The same trial names are retained inside a **separate run directory and plan
hash**. Approval must bind the amended hash, original parent hash and zero prior
model calls. An old approval is rejected. There is no new inference approval
record or amended live run directory at preparation closure.

Original plan SHA-256:
`388c3402b1f6c3f09b35f1f121d290e3e4374aecaa2d1384ec32b67c16b93681`.

Preserved prior terminal-analysis SHA-256:
`884a6395eb1e5fcea7f7cc7171921c62e08fdd3790cf9d759fdf044cab13c4a7`.

## Current metadata evidence

The user authorized current daemon/model metadata discovery for this amendment.
The preparation probe made exactly four metadata requests to
`http://127.0.0.1:11434`, in this order:

1. `GET /api/version` — **0.40.10**.
2. `GET /api/tags` — select `deepseek-v4.1-flash:cloud`.
3. `POST /api/show` with only that model name and `verbose: false`.
4. `GET /api/version` — **0.40.10** again.

The model check was recorded at **2026-10-24 07:30:31 UTC**. The selected tag,
digest, normalized model details, capability list, model information and thinking
configuration all match the archived snapshot exactly. The digest remains:

`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.

The probe transport permits only those four ordered operations and rejects
generation and mutation endpoints before dispatch. No prose, story context or
generation request was sent. Request/response metadata and both version
observations are preserved in a separately sealed metadata bundle; no headers
or credentials are captured. This confirms the current baseline, not historical
information missing from the old terminal record. The old observed-version field
remains unknown.

## Version-capture fix and failure handling

The amended diagnostic runner saves a request record before each version query.
After reading the response, it saves an observation and a seal **before** any
status, JSON shape or version-match rejection. Each observation records:

- Execution/plan binding, stage, expected version and UTC start/completion times.
- Request method and local destination, with headers explicitly excluded.
- Response status, exact body bytes as base64, decoded text and a body hash.
- Observed version when available, parse error when applicable, and outcome.

A valid version response must have HTTP 200, unique-key JSON, a nonblank version
string and an exact match to 0.40.10. Malformed or missing version data, non-200
responses, version drift, transport errors, timeouts and cancellation retain
evidence and stop. Transport failures preserve the exception chain and null
status/body/version fields rather than fabricating a response. Observation
writes are exclusive and durable; existing files cannot be overwritten by retry.

Every complete cell now seals its before/after observations as well as its
existing wire request, raw generation response and receipt. Initial observations
have independent seals and are checked on ledger replay. A missing, orphaned,
tampered or unmatched observation blocks continuation. Clean cell-boundary
restart takes a fresh initial version observation without repeating model calls.

Terminal records include failed version observations and hash their files,
including initial failures before any cell exists. Supported terminal export
preserves the version failure's own response status separately from a captured
generation response's status. Before dispatch, usage remains `not_dispatched`;
after an unresolved dispatched call, usage remains `unknown`. Neither becomes
an invented zero charge. Terminal resume remains forbidden.

The version checker is fixed in the new private diagnostic harness. The old
frozen harness and its terminal evidence are not edited or retroactively repaired.

## Unchanged comparison and budget

**Eight cases × D2/PC × OR/RO = 32 attempts**, sixteen per arm, zero retries or
replacements. Historical cases remain A00, B10, E-compound and F-narrow; fresh
families remain G-voice, H-before, I-cause and J-duplicate. The exact schedule
still begins with the **eight-call B10/H-before sentinel**, four calls per arm.

Both arms use `deepseek-v4.1-flash:cloud`, temperature **0.2**, top-p **0.95**,
seed **20261022**, thinking false and streaming false. Per-call limits remain
**24,000 input / 8,000 output / 32,000 context tokens / 300 active seconds**.
Aggregate reservations remain **768,000 input / 256,000 output tokens / 9,600
active seconds**. The archived-rate reservation remains **$0.53760** within the
**$0.75 planning allowance**; it is not verified billing or an enforceable billed
cost cap. The four metadata requests consume no model-call allowance.

The first-eight sentinel stops if either arm has zero valid reports, or if the
same normalized structural signature occurs in at least three of its four
reports across both families. All original terminal conditions, unknown-usage
handling, exclusive operator lock, reserve-before-dispatch, exact-wire checks,
source seals and no-retry policy remain in force. A further automatic update
after this preparation will be captured and stopped, not silently accepted.

Scoring is unchanged: masked source-bound inspection of every assessment field,
supported targets, group labels, optional-edit success, genuine contradiction
detection and full-report usability. PC requires **15/16 valid**, including
**7/8 fresh valid**, plus **three paired semantic recoveries across two families
and one historical case in both orders**, with no protected losses or new fresh
blanket false rejection. Delivery-only gains earn no semantic credit.
`insufficient_recovery_opportunity` remains distinct, and cannot hide an
independent delivery/regression failure. Incomplete runs cannot advance.

This remains diagnostic evidence only. No literary winner, minimal-edit reward,
whole-story quality gain, writer improvement or new human checkpoint is implied.
The nine human ties and future emphasis on feel/emotion, flow, character and
story-breaking details remain unchanged.

## Verification, artifacts and approval boundary

**177 offline tests pass:** 110 inherited comparison/harness tests, 45
version-capture/amendment tests and 22 unchanged gateway/contract tests. Tests
exercise all 32 exact requests through mocked HTTP, both-arm sentinels,
complete-matrix restart and ceilings, initial/before/after version failures,
non-200/malformed/missing/duplicate/invalid-UTF-8 responses, transport errors,
terminal export, tampering, metadata-only endpoint guards and old-approval
rejection. Real HTTP transports were blocked. Async mocks ran outside the known
Windows sandbox event-loop restriction. They are not model performance evidence.

Ruff lint/format and strict mypy pass on seven private scripts. One initial
type-check error in the observation reader was fixed with a local type annotation;
initial and final verification records are retained. No production/frontend
source changed, so unrelated application suites and the production build were
not repeated.

Private preparation:
`data/diagnostics/reviewer-premise-amendment-v61-2026-10-24/`.
The bundle contains copied inputs, a request/wire equivalence inventory,
baseline amendment, current metadata captures, updated runner/analysis,
version-capture tests and verification. Its immutable `plan.json` seals these
files, historical source fingerprints and this public plan. The tracker records
the plan hash; a separate documentation closure binds tracker/index updates.

Offline verification from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-premise-amendment-v61-2026-10-24/amendment_experiment.py verify
```

The next step is review of this amendment, then explicit approval for generation
under its new plan hash: **at most 32 model calls**, sending the same full
unpublished prose/context to **Ollama Cloud through the local daemon**. Only then
may the new runner execute the frozen schedule. Today's authorization covered
the fix, metadata discovery and preparation, not inference. **Step 19 IN
PROGRESS; Step 20 NOT STARTED; inference PAUSED; canary ON HOLD.**
