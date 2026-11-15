# Authored-source OpenAI mapping and journal qualification — 2026-11-15

The three registered authored packets now have a separately versioned OpenAI
mapping, durable injected-transport journal and read-only terminal audit. The
successful local rehearsal binds all nine whole claims. Failure rehearsals retain
the HTTP 500 error and unknown usage, and preserve an interrupted generation as
consumed without granting completion. **388 tests pass** (47 new/341 existing),
plus Ruff, formatting and strict mypy on **295 files**.

No provider, input-count, model-metadata or daemon call was made. Production
prompts are unchanged, live calls paused and the full workflow canary on hold.
The earlier [authored-source integration](assessment-authored-source-integration-2026-11-15.md)
and every frozen saved-review/observed path remain unchanged.

## Implementation and decision

[ADR 0058](../adr/0058-authored-source-openai-fixture-journal.md) records the contract.

- `engine/open_hollywood_engine/models/assessment_openai_authored.py` regenerates
  the exact authored presentation before calling the shared serializer, and adds
  explicit request/set/terminal records. It reuses the existing response mapper,
  protocol records, native binder and conservative resource checks.
- `apps/api/open_hollywood_api/services/assessment_openai_authored_delivery.py`
  authenticates the registered sources, prepares requests, captures injected
  outcomes and replays the journal into whole-work completion and evidence views.
- `scripts/assessment_openai_authored_delivery.py` exposes only `prepare`,
  `capture-fixture` and `audit`. There is no live switch or caller origin override.
- Four JSON schemas under `docs/contracts/` describe the new request set, fixture
  input, journal event and terminal. The new tests use independently authored small
  source fixtures; the private rehearsal additionally uses all three admitted packets.

The version-two saved-review lifecycle is the implementation reference. Its frozen
files were preserved; the authored path does not manufacture old intake types to
reuse them. Source origin remains `authored_diagnostic`, delivery origin remains
`injected_fixture`, and native work remains `synthetic_fixture`.

## Exact input and journal behavior

All three counts precede any generation: F01/F02/F03 counts, then F01/F02/F03
generations. The fixture set has six fixed slots and no retries. Each request binds
its source, whole work, source receipt, exact presentation/schema, settings and
implementation. Its identity is distinct from the original local scope hash and
the endpoint body digests. Both endpoints receive full prose/context.

| Family | Input-count body bytes | Generation body bytes | Active whole claims |
| --- | ---: | ---: | ---: |
| F01, ferry | 44,623 | 44,770 | 3 |
| F02, kiln | 63,287 | 63,434 | 3 |
| F03, print room | 47,997 | 48,144 | 3 |

These are exact UTF-8 sizes, not token measurements. The previously qualified
diagnostic messages are unchanged. Full sources, all twelve review fields, nine
active claims, sixteen material obligations and two historical-copy bindings
survive mapping and rendering. Three editorial summaries remain unselected;
operator gold stays outside the request bodies.

Intent is written and fsynced before the injected callback. Actual outgoing bytes,
headers and destination are checked, and sources, preparation, implementation and
fixtures are rechecked after intent but before transport. A failure there leaves
a consumed pending slot. Journals cannot be resumed, repaired or reused for capture.
Audit reconstructs terminal status and completion from every fixed slot, including
undispatched ones, and preserves failures without salvaging a successful subset.

Completion eligibility requires a closed successful journal, complete binding of
all three works, no pending intent and no accounting hold. Native binding alone is
insufficient. Missing input/output/reasoning/cached-input usage remains null; known
usage above input/output/context/cost reservations is separately marked excessive.
Actual billing remains null. Cumulative known fixture transport time is checked
between exchanges; real HTTP deadline/cancellation behavior is a future-wrapper check.

## Three actual-packet rehearsals

Private root:
`data/diagnostics/assessment-authored-openai-qualification-2026-11-15/`.

| Scenario | Count slots consumed | Generation slots consumed | Retained result | Eligible |
| --- | ---: | ---: | --- | --- |
| Complete | 3 | 3 | All nine claims bind; all four usage counters retained | Yes, fixture only |
| F02 generation HTTP 500 | 3 | 2 | F01 binds; F02 keeps `http_500` / `server_error` and unknown usage; F03 undispatched | No |
| F03 generation interrupted | 3 | 3 | F01/F02 bind; F03 intent consumed, elapsed/usage unknown, journal open | No |

All successful finals are unchanged **authored** responses from the preceding local
rehearsal. They are not saved provider outputs relabeled as responses to new requests.
Counts (1,000 per packet) and usage (1,000 input, 400 output, 100 reasoning,
100 cached input) are invented fixture data. There is no new accuracy score or
evidence of model reliability, actual latency, actual cost or token fit.

Inspection checks every successful whole claim and citation, every failed/pending
slot, full-source preservation and original authority. The nine evidence views
across the three scenarios retain whole work and appropriate result presence;
F02 keeps both exact-copy bindings. Derived request-bound authority is separate
from the original source authority. Source result/receipt placeholders stay null.

The preparation has ten members. Journals have 15 / 13 / 13 members; every audit
has fourteen members. Preparation and all three audits exactly reuse bytes and
modification times. No journal or original source is rewritten by audit.

`verification.json` records bodies and scenario results; `render-inspection.json`
records all nine evidence-view inspections. `prepared/` holds the request set;
`journals/` and `audits/` each contain `complete`, `generation-500` and
`pending-generation`. Read `audit.json` for full source/request/terminal/usage
records and each `F01-evidence.md` through `F03-evidence.md` for native projections.

## Verification and preservation

The applicable suites cover the new mapping/journal and unchanged shared mapping,
compact journal, authored-source integration and native work/result behavior.
Tests cover exact outgoing bytes, durable ordering, all six interrupted positions,
count failures, non-200 generation, transport cancellation/errors, refusal, length,
empty/malformed/duplicate-ID finals, bad citations, missing/extra fields, wrong
models, unknown usage, all four resource dimensions, time stops, origin forgery,
source/request/fixture binding, journal tampering, no retries and immutable export.

**388 applicable tests pass (47 new/341 existing)** with no warnings in the final
suites, including final-slot accounting holds after all nine claims bind. Ruff, formatting and strict mypy pass on **295 files**, including
the local qualification and preservation helpers. Final compatibility counts and
quality logs are recorded in `acceptance.json`, `tests-second.log`,
`tests-additional.log`, `tests-final-slot.log`, `tests-regression.log`, `ruff.log`,
`format.log` and `mypy.log`.
An initial test-only credential guard conflicted with the existing process secret
scanner; the fixture now supplies an empty configured-secret set while retaining
pattern-based refusal and blocking real secret resolution. Production guards were
not changed. No frontend, route, persistence schema or dependency changed; no client
build or migration is required. Repository-wide pytest was not run.

Preservation checks pass for **2,094 earlier sealed members**, the separate
**64-member authored-control seal**, **636 archive pins**, **808 baseline files**
outside the three documentation updates, both original smoke journals and all
fourteen issue bodies/posted URLs. Both authored-source archives retain all **208**
non-cache files and modification times. The new preparation/journals/audits retain
**93** output members. Keep exact source/code/schema/documentation snapshots, logs,
output pins and an acceptance seal. No external issue
or repository publication occurred.

## Operator commands

```powershell
uv run --extra api python scripts/assessment_openai_authored_delivery.py prepare `
  --source fresh-claims-2026-11-15 --settings PATH_TO_LOCAL_SETTINGS.json `
  --run-id LOCAL_FIXTURE_RUN --output data/exports/authored-openai-preparation

uv run --extra api python scripts/assessment_openai_authored_delivery.py capture-fixture `
  --source fresh-claims-2026-11-15 `
  --preparation data/exports/authored-openai-preparation `
  --fixtures PATH_TO_AUTHORED_PROVIDER_FIXTURES.json `
  --output data/exports/authored-openai-journal

uv run --extra api python scripts/assessment_openai_authored_delivery.py audit `
  --source fresh-claims-2026-11-15 `
  --preparation data/exports/authored-openai-preparation `
  --journal data/exports/authored-openai-journal `
  --output data/exports/authored-openai-audit
```

These commands make no network calls. Fill the generated template outside immutable
source/preparation trees, retain every fixed slot and name its fixture author.
The accepted settings snapshot is copied byte-for-byte from November 14: Sol/high,
272,000 input / 32,000 output reservation, $1 conservative estimate per generation
and 600 seconds cumulative known fixture transport. Its metadata/prices are historical
qualification data, not a fresh provider check or an approved live budget.

## Recommended next step

Prepare the three-work smoke locally, including qualification of the real-transport
wrapper and its explicit observed-delivery audit with injected fixtures. Preserve
authored **source** origin when future assessment **delivery** is observed; do not
promote these fixture journals or use the old saved-review observed registration.
Check credential isolation, no retries/redirects, cancellation/deadlines, exact
outgoing bodies, usage/accounting and publication eligibility before freezing.

Then show a concrete plan for **three input counts before three generation attempts,
no retries**, with exact requests, current reviewed settings/resource limits,
whole-claim gold/adequate-evidence criteria and stop rules. Live approval must cover
full prose/context at both endpoints. No live budget is frozen or authorized here.

This would test delivery and factual assessment across the fresh families through
the tracked path. It would not qualify natural critic precision, editorial effect,
edit necessity, writer preservation or story quality. Human review remains focused
on feel, flow, character and story-breaking effects; mechanical checks remain
application-owned. CW-007/CW-013 remain open; CW-014 unqualified. Step 19 remains
IN PROGRESS; Step 20 NOT STARTED; prompts unchanged; live calls PAUSED; canary ON HOLD.
