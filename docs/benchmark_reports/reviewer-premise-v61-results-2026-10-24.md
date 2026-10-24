# D2/premise-check comparison: preflight stop

Date: 2026-10-24. **STOPPED BEFORE INFERENCE — 0/32 MODEL CALLS USED.**
Frozen outcome: **`incomplete_no_advancement`**. There are no new reviewer
outputs or comparative findings. Production remains **prompt 61 / graph 9 /
fulfillment policy 1**; live inference is **PAUSED** and the full workflow
canary remains **ON HOLD**.

## Approved scope and observed stop

The user approved the [frozen D2/premise-check plan](../handoffs/reviewer-premise-frozen-plan-2026-10-24.md),
including full unpublished original/revision prose and context to Ollama Cloud
through the local daemon, at most 32 attempts, sixteen per arm, with zero retries.
Approval is bound to plan SHA-256:

`388c3402b1f6c3f09b35f1f121d290e3e4374aecaa2d1384ec32b67c16b93681`.

The local frozen assets and source fingerprints verified. The runner then
queried the local daemon's `/api/version`. The version helper returned a
nonempty string that did **not exactly match the frozen `0.40.9` baseline**.
The runner raised `ValueError: daemon baseline changed` and wrote the terminal
record and its seal before checking model metadata or reserving a model call.

The frozen plan explicitly makes identity/version drift a terminal stop with
no retry or resume. The runner was not restarted, the baseline was not changed,
and no follow-up daemon discovery or inference was attempted. The original
preparation, cases, requests, card, schema, sampling settings and scoring remain
intact.

| Accounting | Observed |
| --- | ---: |
| Planned model attempts | 32 |
| Reserved model attempts | **0** |
| Dispatched model attempts | **0** |
| Complete model responses | **0** |
| Retry/replacement calls | **0** |
| D2 / PC model attempts | **0 / 0** |
| Sentinel | Not reached |
| Model digest/capability preflight | Not reached |
| Full prose/context sent for generation | None |

No provider generation usage was produced. The terminal record preserves
`provider_usage.state = not_dispatched`, with input/output token fields and
actual cost null. Aggregate sums over completed calls are zero; they are not
provider-reported usage or a verified bill. The analysis preserves the terminal
flag on aggregate usage coverage and does not infer a charge from a reference
rate estimate over an empty ledger.

## Inspection and evidentiary limit

Local inspection verified the terminal error chain, exact plan/approval binding,
zero reservations and dispatches, absence of a cell directory, release of the
operator lock and rejection of terminal resume. The supported terminal export
contains the terminal record and an empty review/key set. Empty source-bound
notes were sealed before scoring; there were **zero reports and zero assessment
fields to inspect**. No invalid model response was repaired or given credit.

The frozen decision is `incomplete_no_advancement` because the comparison did
not execute. Validity, semantic recovery, unsupported-premise rates, preservation
of successful controls and story quality are **not measured**. Empty arm counts
must not be interpreted as 0/16 reviewer accuracy or a failed treatment screen.
The empty recovery-opportunity inventory also supplies no evidence about a
model performance ceiling.

One local observability gap is now concrete: the initial version check compares
the returned string before persisting it. Its terminal record retains the error
but **not the observed version or raw `/api/version` response**. The capture
transport forwards version requests without saving their bodies. Consequently,
the saved evidence establishes an exact-baseline mismatch but cannot name the
returned version. A bounded read of the local server log did not recover a
matching version line. No version has been guessed or substituted from an
installed client binary. An automatic update is plausible given prior sessions,
but its exact version/cause is not established by this capture.

## Verification and preserved artifacts

**14 offline post-run tests pass**, with HTTP client sends blocked. Ruff
lint/format and strict mypy pass on three new private analysis scripts. Checks
cover the unchanged preparation and approval, terminal accounting, model-metadata
absence, supported empty export and frozen decision replay, source/notes/terminal
tampering, unplanned-cell rejection and refusal to resume. The existing 132-test
preparation verification remains sealed; it is not reported as a new live result.
No production or frontend source changed, so unrelated application suites and
the production build were not repeated.

Local evidence:

- Preparation and approval: `data/diagnostics/reviewer-premise-v61-2026-10-24/`.
- Terminal run: `data/diagnostics/reviewer-premise-v61-2026-10-24-live/`.
  Its only files are `TERMINAL.json` and `terminal-seal.json`.
- Analysis: `data/diagnostics/reviewer-premise-v61-2026-10-24-analysis/`.
  Includes preflight diagnosis, supported inspection export, sealed empty notes,
  frozen decision, accounting, terminal execution manifest and verification.

The execution manifest binds both terminal files and the approval. A separate
analysis manifest binds the post-run artifacts, execution manifest and this
report. The tracker records both hashes; documentation closure binds the tracker
and issue-index update. Existing issue bodies and all fourteen user-posted
GitHub links are preserved; no external issue was changed or closed.

## Next prerequisite

Before another run, prepare an explicit baseline amendment rather than resuming
this terminal ledger:

1. Locally add and test persistence of the initial version response **before**
   comparison, including expected/observed versions, response status and the
   terminal failure path. Keep credentials out of captures.
2. Obtain the current daemon/model metadata through an authorized metadata-only
   preflight, then freeze its verified baseline and a new execution identity.
   Preserve the original terminal evidence and keep the same cases, exact model
   messages, schema, settings, schedule, scoring, stops and **32-call ceiling**.
   No model calls have been consumed or justify enlarging that ceiling.
3. Show the concrete amendment for approval before generation. Do not treat the
   unused budget or the old approval as permission to bypass the version stop.

No further experiment, prompt change or live continuation is prepared or executed
by this report. Historical critic/writer evidence and the nine human ties remain
unchanged. Future story-quality review still concerns feel/emotion, flow,
character and story-breaking details, with mechanical evidence prepared by
machines. **Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**
