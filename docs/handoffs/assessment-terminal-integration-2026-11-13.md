# Tracked fixture request preparation and terminal auditing

Date: 2026-11-13. Narrow fixture implementation and local verification **COMPLETE**.
Production prompts unchanged; live calls **PAUSED**; canary **ON HOLD**.

The application now prepares an immutable request set from registered probe intake,
captures authored responses through an injected transport, and exports a read-only
terminal audit. It verifies actual outgoing bytes, records intent before transport,
and reconstructs successful, failed and interrupted outcomes without granting model
provenance or semantic approval. The existing authored completion publisher and
registered B archive exporter remain unchanged.

## Implemented boundary

New tracked components:

- Pure [assessment delivery contracts](../../engine/open_hollywood_engine/evaluations/assessment_delivery.py).
- [Application preparation/capture/audit service](../../apps/api/open_hollywood_api/services/assessment_delivery.py).
- [Operator CLI](../../scripts/assessment_delivery.py).
- Authored transport fixture helper, domain regressions and application/CLI tests.
- Six runtime schemas under `docs/contracts/`, separate from the historical design schemas.
- A bounded native registry parsing improvement found during full-context verification.

The implementation extends [ADR 0050](../adr/0050-intake-bound-assessment-request-terminal-design.md).
All supported requests have `provider=fixture`, `model=fixture-only-no-model`, an
`.invalid` destination, authored origin and false live authorization. Only an
`httpx.MockTransport` can be injected; no `httpx.Client`, real/default transport,
provider credential, model catalog, count service or generation endpoint is used.
Production prompt text, profiles, routing, gates and human checkpoints are unchanged.
Injected callbacks are trusted local test code; this interface is not a sandbox
for arbitrary Python. The CLI creates only the in-process authored fixture handler.

The source collector still authenticates registered diagnostic-probe archives and
their lineage, recompiles the original intake and compares exact saved bytes. This
slice retains the complete original work, declarations, briefs, report fields,
holds and unselected material. It does not admit production SQLite intake or widen
the registered archive contracts. Tests use authored source archives and isolated
test databases where existing exporter regressions require them; no user database
is opened by the new component.

## Operator commands

Prepare a new fixture-only request set for one compatible intake work:

```powershell
uv run --extra api python scripts/assessment_delivery.py prepare `
  --intake PATH_TO_INTAKE/review-01.json `
  --run-id local-terminal-check-001 `
  --output data/exports/fixture-requests-001
```

Preparation writes `intake.json`, `source-receipt.json`, `request-set.json`,
`fixtures.template.json`, a full literal `view.md`, then `manifest.json` last.
The request set preserves original batch order, unique attempts and budget slots.
Each batch permits at most one count and one generation fixture invocation, with
zero retries. `--without-count` freezes a generation-only path at preparation;
it cannot be used to bypass a failed count in an existing request set.

Copy `fixtures.template.json` outside the immutable preparation directory. Supply
an author and one authored reply for each fixed endpoint. The blank author makes
the untouched template invalid. A reply contains `attempt_id`, `stage`, `behavior`,
`http_status` and `response_body_utf8`. Response bodies follow the
[safe response schema](../contracts/assessment-fixture-safe-response-1.schema.json);
failure fixtures may deliberately supply malformed bodies. The
[fixture suite schema](../contracts/assessment-transport-fixtures-1.schema.json)
also permits explicit interruption, cancellation and transport-error behavior.
Fixture files are authored test inputs, never new model observations.

```powershell
uv run --extra api python scripts/assessment_delivery.py capture-fixture `
  --intake PATH_TO_INTAKE/review-01.json `
  --preparation data/exports/fixture-requests-001 `
  --fixtures PATH_TO_AUTHORED_FIXTURES.json `
  --output data/exports/fixture-journal-001

uv run --extra api python scripts/assessment_delivery.py audit `
  --intake PATH_TO_INTAKE/review-01.json `
  --preparation data/exports/fixture-requests-001 `
  --journal data/exports/fixture-journal-001 `
  --output data/exports/fixture-audit-001
```

Use distinct new directories outside source archives, intake, preparation and
fixture inputs. Exact preparation/audit repeats verify and reuse bytes without
rewriting them. Capture always refuses an existing journal, including completed
journals. No resume, resend, cleanup or silent repair is provided. The capture
command reports `complete`, `halted`, `cancelled_before_dispatch`, or an interruption
with exit code 130; malformed source/input/destination errors return a redacted
error and exit code 2. A halted capture is still eligible for terminal auditing.

## Capture, terminal and completion decisions

The application regenerates the request set under its implementation identity and
rechecks source/preparation before each endpoint. The identity covers the new domain
and adapter, shared source/publication helper, intake/binding/completion modules,
registered probe adapter, and installed Python/Pydantic/httpx versions.

At the transport callback boundary it compares the actual method, complete URL and
exact UTF-8 body against the frozen endpoint. Only default host/content-length
headers are allowed. It derives body hashes from those actual bytes, writes an
exclusive intent event, flushes and calls `fsync`, and only then invokes the mock
transport. The outcome and final stop event are also written and flushed separately.
Journal files have fixed names, sequence numbers and a byte-hash chain from the header.

| Observation | Recorded behavior |
| --- | --- |
| Actual body, destination, method or headers differ | Refuse before transport invocation; no false dispatch record |
| Count fails or returns no usable count | Consume its intent, retain its evidence and stop before generation |
| Complete generation passes native binding with known usage | Retain the result and permit the next already prepared fixture endpoint |
| Complete generation binds with partial/unknown usage | Retain the valid result and unknown counters; stop the entire fixture run |
| HTTP 500 body claims completion | Actual HTTP status wins; valid-looking final JSON receives no completion credit |
| Refusal, length, empty/malformed final, bad slots/citations or unexpected model | Retain failure; do not salvage successful slots |
| Unsafe, oversized, malformed or undeclared response envelope | Retain a safe capture-error record, actual HTTP status and any complete observed-body digest; usage remains unknown |
| Intent exists without an outcome | Audit derives an interrupted exchange, consumes that attempt and keeps usage/elapsed time unknown |
| All responses exist but final stop event is missing | Native binding facts remain visible; completed-publication eligibility stays false |

The `safe-response` parser excludes undeclared observed response fields. Available
response IDs, returned model, finish reason, final text, usage and ordered safe
daemon/gateway/provider error chains are retained. Known zero differs from unknown;
count estimates never fill generation usage. The exact retained response hash and
observed raw HTTP-body digest have separate fields. Observed raw HTTP bytes, headers
and reasoning content are not copied into outcome records. The original authored
fixture input is retained separately as `fixtures.json`; it must not be mistaken
for independent evidence of what the transport returned.

Auditing reads the journal without modifying it, validates its prefix/order/bodies,
rebuilds terminal evidence and invokes the current native binder and whole-work
completion. Caller-provided binding, completion and writer-approval flags are not
inputs. A failed or absent batch prevents successful whole-work publication.
A final successful batch with unknown usage can still be bound while the run is
halted; that fact does not establish known cost or authorize further dispatch.

The seven audit files are `intake.json`, `source-receipt.json`, `request-set.json`,
`journal.json`, `audit.json`, literal `view.md` and the final publication manifest.
`publication_state` is `bound_unassessed` only for closed, completely bound work;
otherwise it is `incomplete_terminal_audit`. Successfully exporting an audit does
not mean the assessment succeeded. Both states retain the full original intake.

Token counts and measured callback intervals are explicitly **authored fixture
data**, not inference cost or model latency. A missing outcome contributes an unknown
elapsed endpoint rather than a fabricated latency; native time totals show only
known intervals. Actual billed cost remains null, model evidence false, semantics
and evidence adequacy unassessed, and writer permission false everywhere.

## Local validation cost

Profiling N06 found repeated strict JSON parsing in the existing native registry
validator: it parsed a complete source document again for each distinct cited field.
The validator now parses each referenced source once **within that invocation**.
Every document/version/hash, field, offset, paragraph and quote check remains.
There is no cross-request or cross-validation cache. Two regressions verify bounded
parse count, fresh parsing on a later call, duplicate-key rejection and changed-field
rejection. This is the only change to existing engine behavior; it changes validation
work, not acceptance criteria, prompts or assessment judgments.

One instrumented N06 preparation-load/audit sample decreased from **75.894 seconds
to 20.536 seconds**, with the same 53 registry validation calls. These are local
samples under concurrent checks, not a benchmark or model-latency result. Full-source
recollection, regeneration and repeated validation still carry noticeable overhead;
this operator path is not qualified as an interactive production gate.

## Verification

**602 applicable tests pass**: 80 new delivery/registry regressions plus 522 existing
checks, with 56 existing Pydantic warnings from deliberate mutation fixtures. The
final combined suite completed in 410.98 seconds. It includes native assessment,
scope/brief/authority, completion, intake, ordinary/probe evidence and archive export.
Ruff, formatting and strict mypy pass for **257 files**: 256 repository Python files
and the private replay helper. Six runtime schema snapshots match their parsers.

The new tests cover actual outgoing bytes and forbidden headers, intent flush ordering,
interruption/cancellation, refusal/length/non-200/malformed response, missing/duplicate
slots and wrong citations/model, unknown/partial/zero usage, count failure and global
stops, source/journal drift, oversized response, disk failure, protected paths,
redacted errors, exact output reuse, forged origin, tampered journal and missing final
stop. New fixture tests and actual-intake replay block network and SQLite. Existing
saved-review exporter tests use isolated SQLite fixtures and fake gateways; their
asynchronous fixture stalled in the sandbox, so the final combined suite ran outside
it with a dedicated test directory. No user database or live inference was involved.
Frontend/OpenAPI/build checks are not applicable to this Python operator-only change.

Preservation checks confirm **723 prior files** unchanged outside seven documented
existing-file edits, **900 earlier sealed evidence members** intact, and **1,166
original source pins** unchanged. The seven edits are five documentation files,
the native registry parser and its regression tests. No existing issue body or
posted GitHub URL is changed.

The tracked CLI also passes the same **four actual intake works / six unchanged
authored assessments**: N06, N07, N10 and N11. All **51 report fields, four holds and
41 unselected fields** remain exact. Each work creates six preparation files, seven
journal files and seven audit files; exact preparation/audit reuse leaves bytes and
mtimes unchanged. All four repeated capture attempts are refused without callback
execution. There are four fixture count invocations and four fixture generation
invocations, **zero live calls** and no semantic rescore. Every original authored
raw final is retained byte-for-byte.

The private acceptance root is
`data/diagnostics/assessment-terminal-integration-2026-11-13/`. It retains the replay
program, exact four-work preparations, authored fixture files, journals, audits,
verification and preservation records. Earlier design evidence and user changes
remain intact. Historical programs are not executed.
Accepted four-work outputs are under `verified/`. The earlier N06/N07 outputs and
`before-registry-reuse/` snapshot are preserved as superseded/partial verification,
not counted as final acceptance and not rewritten to match the new implementation.

Evidence: [four-work acceptance](../../data/diagnostics/assessment-terminal-integration-2026-11-13/acceptance.json),
[verification](../../data/diagnostics/assessment-terminal-integration-2026-11-13/verification.json),
[preservation](../../data/diagnostics/assessment-terminal-integration-2026-11-13/preservation.json),
and [local profile comparison](../../data/diagnostics/assessment-terminal-integration-2026-11-13/performance.json).

Resource limits: twelve original batches/active units, at most 24 endpoint intents,
49 journal events plus header/fixture file, 64 MiB preparation/journal/publication
bounds, 16 MiB journal members, 4 MiB fixture input, and 1 MiB observed response.
Native 64,000-character/256,000-byte final, reference and reason limits remain.
Paths, secret checks, source rechecks, exclusive publication, exact reuse and
manifest-last completion reuse the existing authored publisher boundary.

## Qualification limits and next step

This qualifies a local fixture mechanism. Local hashes and an authored-origin
journal are not provider signatures or authenticated model deliveries. No parser
here accepts `authenticated_model_delivery`; real model origins cannot be enabled
by relabeling fixture inputs. Original design schemas remain historical and are
not runtime contracts. No database migration, API route, workflow registration,
automatic factual gate or additional human checkpoint is added.

The journal flush tests establish ordering and conservative recovery from a process
interruption, not filesystem-wide atomicity or a power-loss guarantee. A partial or
malformed journal member is refused; it is never rewritten. Any observed source,
preparation or journal drift prevents successful publication.

Next, **qualify one real provider wire-format adapter locally**, reusing established
OpenAI assessment rendering and saved request/terminal examples. Keep those saved
deliveries bound to their original work; use authored provider-format failures for
missing observation branches. Verify exact outgoing generation/count bodies, safe
response mapping, model identity, stop/cancellation behavior and usage without
network access. Then prepare a separately approved small intake-bound live smoke
test; no live budget or inference plan is frozen by this implementation.

The mechanism improves traceability and failure accounting. It does not establish
claim truth, adequate evidence, necessary rewriting or story quality. Future craft
work still needs separate editorial assessment and human judgments of feel, flow,
character and story-breaking effects. CW-007/CW-013 remain open; CW-014 unqualified.
Step 19 **IN PROGRESS**; Step 20 **NOT STARTED**; production prompts unchanged;
live calls **PAUSED**; full workflow canary **ON HOLD**.
