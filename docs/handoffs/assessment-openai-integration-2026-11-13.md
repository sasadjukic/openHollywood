# Intake-bound OpenAI manifest and durable journal integration

Date: 2026-11-13

Status: local implementation and verification **COMPLETE**.
Production prompts unchanged; live calls **PAUSED**; full workflow canary **ON HOLD**.

## Result and boundary

The qualified OpenAI mapping now has a tracked, source-bound local path for request
preparation, injected capture and immutable terminal audit. It retains the original
intake work and derives completion from the actual ordered journal. It accepts only
authored fixtures; no network client or model-origin receipt is enabled.

This follows the [mapping qualification](assessment-openai-mapping-2026-11-13.md)
and [fixture implementation](assessment-terminal-integration-2026-11-13.md).
[ADR 0051](../adr/0051-intake-bound-openai-assessment-rehearsal.md) records the decision.

## Implementation and decisions

- [Presentation](../../engine/open_hollywood_engine/evaluations/assessment_presentation.py):
  render a new diagnostic instruction appropriate to each original active batch.
  Include the complete original work, original messages/documents/registry, scope
  declarations, work briefs and all held/unselected dispositions. Source instructions
  are evidence data. The original native work, batch and claim identities stay intact.
- [Manifests](../../engine/open_hollywood_engine/models/assessment_openai_manifest.py):
  freeze source and receipt pins, presentation, explicit model/resource settings,
  exact count/generation bodies, implementation identity, unique attempt slots,
  whole-work coverage, zero retries and `live_authorized: false`. Native payload,
  endpoint/body and final-response digests remain separate namespaces.
- [Mapping](../../engine/open_hollywood_engine/models/assessment_openai.py):
  preserve the original-message entry point and add an intake-specific entry point
  that verifies the regenerated presentation without replacing native work messages.
  Reuse the previously qualified production serializer and safe response mapper.
- [Service](../../apps/api/open_hollywood_api/services/assessment_openai_delivery.py)
  and [CLI](../../scripts/assessment_openai_delivery.py): authenticate registered
  sources and recheck them before each callback; journal/fsync actual outgoing intent
  before injected transport; derive native binding and completion from durable events;
  publish exact immutable bundles through the existing read-only boundary.

Five strict [runtime schemas](../contracts/) document settings, request set, fixtures,
journal events and derived terminal records. Schema validity alone does not establish
source authentication, dispatch provenance, semantic truth or writer permission.

The new presentation is an explicit diagnostic change requiring review in any future
live freeze. It is neither a production prompt change nor an unchanged historical B
control. Historical `model_input: false` flags remain in the full packet and describe
the original input contract. The new instruction distinguishes that history from
current presentation and prevents operator provenance becoming story authority.

## Local operator commands

Use an explicit settings file matching
[`assessment-openai-rehearsal-settings-1`](../contracts/assessment-openai-rehearsal-settings-1.schema.json).
There is no live command, credential option or implicit provider request.

```powershell
uv run --extra api python scripts/assessment_openai_delivery.py prepare `
  --intake PATH_TO_INTAKE.json --settings PATH_TO_SETTINGS.json `
  --run-id local-openai-001 --output data/exports/openai-requests-001

uv run --extra api python scripts/assessment_openai_delivery.py capture-fixture `
  --intake PATH_TO_INTAKE.json --preparation data/exports/openai-requests-001 `
  --fixtures PATH_TO_AUTHORED_FIXTURES.json --output data/exports/openai-journal-001

uv run --extra api python scripts/assessment_openai_delivery.py audit `
  --intake PATH_TO_INTAKE.json --preparation data/exports/openai-requests-001 `
  --journal data/exports/openai-journal-001 --output data/exports/openai-audit-001
```

Copy `fixtures.template.json` outside the immutable preparation directory, name its
author and fill its fixed provider-format replies. Only `httpx.MockTransport` is
admitted. Fixture responses can exercise real request serialization and response
parsing, but cannot authenticate a model delivery. Old synthetic fixture commands
and accepted artifacts retain their existing contracts.

Preparation emits six members; terminal audit emits seven. Capture refuses every
existing journal. Exact preparation/audit repeats reuse bytes and mtimes. Partial,
changed or extra output members are refused rather than repaired.

## Failure accounting and stops

Every callback has a flushed intent and separately hashed outcome. A dangling intent
consumes its slot with unknown elapsed interval and usage. Count failure prevents
generation. Incomplete/ambiguous/empty/refused/invalid finals cannot bind. Wrong model,
source/body drift, unsafe response content and conflicting delivery evidence fail
closed. Error text is redacted; safe structured failures remain inspectable.

All four usage counters must be known before another batch. Cached/reasoning usage
is not assumed zero. A final batch can bind while the audit retains an accounting
hold; binding, accounting and completion eligibility are separate fields. No later
batch may proceed after failed binding, unknown usage or exhausted transport time.
Actual billed cost stays `null`, including successful fixture runs.

Audit checks strict duplicate-free JSON, event order/hash chain, exact endpoint/body
identity and terminal consistency. It reconstructs the complete original work without
salvaging a successful subset. An incomplete journal can be exported for inspection,
but a missing terminal stop prevents completion eligibility. All origins remain
`injected_fixture`; model evidence and writer dispatch stay false.

Limits are 12 batches/24 endpoint callbacks/49 events, 64 MiB per journal/output bundle,
16 MiB per output member, 4 MiB fixture input and 1 MiB response capture. The configured
time ceiling covers cumulative observed mock transport intervals; it neither preempts
an in-progress callback nor bounds validation and publication time. A live adapter
will need separately verified cancellation and wall-time behavior.

## Four-work verification

All four actual works pass preparation, fixture capture, terminal audit and exact
reuse. Their six authored finals remain byte-identical to the previous completion
rehearsal; native bindings use each original work and its new request-payload hash.

| Work | Active claims | All fields | Holds | Unselected | Generation body bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| N06 | 1 | 12 | 1 | 10 | 1,314,610 |
| N07 | 2 | 12 | 0 | 10 | 1,353,088 |
| N10 | 2 | 14 | 2 | 10 | 1,467,491 |
| N11 | 1 | 13 | 1 | 11 | 2,198,269 |
| Total | 6 | 51 | 4 | 41 | 6,333,458 |

Each work invokes one mock count and one mock generation: **four plus four fixture
callbacks; zero live calls**. All four duplicate-capture attempts are refused.
Preparation and audit repeats preserve every byte and mtime. Original source,
declarations, briefs, full context and all intake dispositions remain unchanged.

Rehearsal settings use the existing saved/built-in `gpt-6.1-sol` specification with
`high`, 24,000 reserved input tokens, 32,000 output tokens, $0.60 maximum estimated
cost per generation, and 600 cumulative transport seconds per work. These are
explicit local fixture settings, not newly verified model access, current prices
or a live budget. Each authored reply reports 100 input, 20 output, five reasoning
and zero cached tokens; those numbers test control flow and are not measurements.

Actual provider input counts and context fit remain **unknown**. The packet includes
the full registry and operator provenance as well as source prose, so serialized
request bytes are much larger than original critic messages. Passing the local
fixture count does not demonstrate fit within the 24,000-token reservation.

The combined relevant suite passes **794 tests**: 732 existing plus **62 new**
presentation and integration tests, with 56 existing mutation warnings (599.61 seconds).
Coverage includes count/HTTP failures, incomplete/refused/empty/ambiguous finals,
duplicate IDs, unknown usage, interrupted intents, cancellation, failed later batches,
fsync refusal, source/body/journal drift, invalid fixture origin, runtime schema
agreement, output limits, protected paths and immutable publication. New tests and
the actual-work replay prohibit network and database access. Existing async/SQLite
regressions use isolated test fixtures outside the sandbox; no user database is used.

Ruff, formatting and strict mypy pass on **265 Python files** (264 repository files
and the private replay helper). `git diff --check` and new-file UTF-8/LF checks pass.
Frontend/build/OpenAPI checks are not applicable: no frontend, API route, API schema,
dependency or persistence changes were made.

Preservation checks pass for **1,097 earlier sealed members**, **636 selected
archive source pins**, and **741 baseline files** outside the five declared existing
file edits. All fourteen issue bodies and posted URLs remain unchanged.

Private evidence root: `data/diagnostics/assessment-openai-integration-2026-11-13/`.
Accepted four-work bundles are under `verified/`; each retains preparation, fixture
input, journal, audit and acceptance record. No source artifact is edited. Network,
HTTP client sending and SQLite access are blocked in the actual-work replay.

## Recommended next step

Prepare a count-gated smoke plan for separate approval: provisionally **four generation
attempts and four input-count requests**, one batch per current work, zero retries.
Review the exact new presentation and its size; freeze reviewed model metadata,
source pins, input/output/cost/wall-time ceilings, scoring and stops. During that
preparation, qualify the real transport and observed-origin boundary locally with
injected fixtures. Do not promote current fixture journals to model deliveries.

Require each real input count to fit the frozen reservation before generation. A
failed or over-budget count stops the relevant dispatch and is reported; it does not
authorize input trimming, a larger budget or a prompt change. Full retained packets
are substantially larger than the original critic messages. If resource fit fails,
return to a separate local presentation/resource design before another live plan.

No live plan is frozen or approved here. A smoke test would qualify delivery and
native completion on this path, not reviewer correctness or story quality. Whole-claim
truth, evidence adequacy, editorial effects and necessary revision still need their
own qualification. Humans continue to judge feel, flow, character and story-breaking
problems; mechanical binding does not authorize rewriting.

CW-007/CW-013 remain open; CW-014 remains unqualified. No issue body is closed, writer
permission granted, user database accessed or human checkpoint added. Step 19 remains
**IN PROGRESS** and Step 20 **NOT STARTED**.
