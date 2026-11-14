# Compact version-two OpenAI mapping and manifest qualification

Date: 2026-11-14

Status: separate version-two mapping, manifest and local qualification **COMPLETE**.
No live plan or real-transport runner is frozen by this change.
Production prompts unchanged; live calls **PAUSED**; full workflow canary **ON HOLD**.

## Result and boundary

The separate compact presentation now has an explicit OpenAI mapping and
source-bound request manifest, fixture journal and read-only terminal export.
[ADR 0054](../adr/0054-compact-openai-mapping-and-manifest.md) records the decision.
The version-one renderer, mapper, manifests, journals and closed smoke are unchanged.
The compact diagnostic instructions implemented earlier are also unchanged.

The new path authenticates the registered intake and regenerates the exact compact
export before preparing or accepting endpoint bodies. It binds both that export's
manifest and `local-provenance.json` bytes. All original visible sources, messages,
claims, scope declarations, work briefs, whole-review dispositions and native
response schema remain intact. The local provenance body is absent from both
endpoint bodies; a digest is not permission to infer unavailable source content.

The implementation consists of:

- [Compact admission](../../engine/open_hollywood_engine/models/assessment_openai_compact.py),
  which admits only regenerated version-two messages to the shared wire serializer.
- [Version-two manifests and terminal reduction](../../engine/open_hollywood_engine/models/assessment_openai_compact_manifest.py),
  preserving original native source/work identities while assigning new request
  identities. The settings, exchange and wire records reuse the existing protocol
  contracts; their version numbers do not identify the presentation.
- [Application preparation, injected capture and audit](../../apps/api/open_hollywood_api/services/assessment_openai_compact_delivery.py)
  and the [operator CLI](../../scripts/assessment_openai_compact_delivery.py).
  Every command requires the verified compact export via `--presentation`.

There is no live transport, authentication header, current metadata request,
database route, UI change or new dependency. Existing process-environment
secret-refusal guards remain active; no credential is selected for authentication
or written into artifacts. The separate orchestration retains version-one
implementation hashes. Its conformance tests mirror the established lifecycle
and add version-two provenance and message-admission checks.

## Four-work qualification

The final-code rehearsal uses N06/N07/N10/N11 from the existing registered intake,
their already verified compact exports, and the same four authored batch responses
covering six claim assessments used in the earlier completion rehearsal. It
exercises the supported CLI, source
authentication, outgoing HTTP bytes, durable intent, response mapping, native
binding, whole-work completion and exact preparation/export reuse.

All **four works** complete native binding; all **eight injected endpoint slots**
were inspected. Exact preparation and terminal-export repeats preserve bytes and
mtimes; original intakes and compact exports are unchanged.

| Work | Active claims | Count body bytes | Generation body bytes | Native binding |
| --- | ---: | ---: | ---: | --- |
| N06 | 1 | 274,545 | 274,692 | Complete |
| N07 | 2 | 309,299 | 309,446 | Complete |
| N10 | 2 | 314,049 | 314,196 | Complete |
| N11 | 1 | 290,079 | 290,226 | Complete |

These are exact UTF-8 endpoint body sizes, including the response schema and JSON
escaping. They are not decoded user-message sizes or token counts.

The historical local settings are Sol/high, 272,000 maximum input tokens, 32,000
maximum output tokens, $1 maximum estimated generation cost per work and 600
transport seconds. These are reused solely as local qualification inputs. The
catalog metadata was reviewed on November 13; no current provider facts or future
live budget are established here. Each count fixture reports an invented **100**
tokens, and generation usage is authored test data. Neither is a token measurement,
bill or model performance result.

All 51 fields, six active claims, four holds and 41 unselected fields retain their
original disposition. The prior exact reconstruction covers 3,658 evidence IDs.
This qualification checks those same published messages at both endpoint bodies
and the original schema at native binding. It does not re-score the authored finals
as model evidence or gold. N11's visible historical allegation and repair evidence
remain in the original visible-request fields.

## Delivery and accounting checks

Count and generation requests use the same exact messages, model, reasoning and
structured response format. Generation retains its output cap and disabled
truncation. Before an injected callback, the application checks the actual method,
destination, body bytes and permitted headers, and fsyncs the bound intent. It
regenerates source, presentation and preparation before each subsequent dispatch.

Tests cover count rejection, non-200/error responses, incomplete/empty/refused or
wrong-model outputs, duplicate IDs, unknown usage/cache counters, interrupted and
cancelled requests, time limits, source/provenance/request drift and forged journal
events. An unresolved intent consumes its fixture slot with unknown elapsed time
and usage. Failed later batches cannot publish successful earlier batches as a
complete original work. Partial or changed output directories are refused.

Version-two terminals also record observed input/output/context/cost reservation
violations. Unknown usage or a violation creates an accounting hold and prevents
another dispatch. A bound response can remain structurally complete for inspection
while accounting is unresolved; this is separate from live permission and semantic
approval. `actual_billed_cost` stays null. No retry or journal resumption exists.

## Verification and preservation

- **729 relevant tests passed**: 71 new version-two tests in 349.67 seconds,
  and 658 existing source/scope/brief/authority/binding/completion/provider/smoke
  regressions in 547.48 seconds. The existing suite emits 56 known Pydantic
  serializer warnings from deliberately malformed mutation fixtures.
- Ruff, formatting and strict mypy pass on **279 files** (278 repository files
  plus the private actual-work helper). All four new JSON schemas match runtime.
- Tests use isolated fixtures. The actual-work helper blocks HTTP client sends,
  socket connections/DNS and SQLite; source authentication uses the real registered
  collector. Windows test execution ran outside the sandbox for filesystem and
  existing event-loop support; provider transport remained mocked or blocked.
- Preserved **1,426 earlier sealed members**, **636 selected archive source pins**,
  the original live journal's bytes/mtimes, **773 baseline files** outside four
  declared documentation updates, all fourteen issue bodies and posted URLs.
- Documentation links/UTF-8 and `git diff --check` pass. No frontend/build check
  applies: no client code, API route or persisted schema changed.

Private evidence is under
`data/diagnostics/assessment-openai-compact-2026-11-14/`:

- `verified/requests`, `verified/journals`, `verified/exports` contain the final-code
  qualification. `actual-summary.json` records all eight injected endpoint slots.
- `verify_actual.py` blocks network and SQLite. `verified-actual-run.log`, test logs,
  `verification.json`, source snapshots and the acceptance seal preserve the run.
- Earlier `requests`, `journals`, `exports` and `actual-run.log` are retained as a
  pre-qualification rehearsal. It was stopped when shared settings/exchange code
  was added to the implementation pin. Its request identity is obsolete, it is
  not reused, and no provider call occurred. The authoritative replay is `verified/`.

## Next step

Prepare a **new four-work count-gated smoke plan** for approval. Qualify a separate
version-two real-transport wrapper locally before freezing it. Reuse the same four
works, source bindings and compact presentation, with four input-count attempts,
four generation attempts and **zero retries**. Provisionally keep Sol/high and
272,000-input/32,000-output ceilings; review explicit cost, latency, model metadata
and exact endpoint bytes during preparation.

Count all four requests before any generation. Stop on failed, unknown or over-cap
counts; source/request/code drift; failed delivery or binding; unknown/over-budget
usage; cancellation; deadline; or journal failure. Do not trim, increase budgets,
substitute work or resume the old smoke. Freeze the exact bodies and stops and
obtain approval before either story-bearing endpoint is called.

The live question is whether the compact presentation fits and supports the same
assessment workload reliably. Structural delivery is not evidence adequacy, factual
truth, editorial merit, justified editing or story quality. Retain the human
feel/flow/character review boundary. CW-007/CW-013 remain open; CW-014 unqualified;
Step 19 remains **IN PROGRESS**, Step 20 **NOT STARTED**.
