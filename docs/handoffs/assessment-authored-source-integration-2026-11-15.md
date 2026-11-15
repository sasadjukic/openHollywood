# Explicit authored-source integration qualification — 2026-11-15

The three [admitted authored packets](assessment-fresh-claim-admission-2026-11-15.md)
now pass a tracked, read-only source, presentation and fixture-completion path.
All nine whole factual claims bind and export; three editorial summaries remain
unselected. **371 tests pass**, plus Ruff, formatting and strict mypy. There were
zero provider, input-count, metadata or daemon calls.

This completes local source integration. It does not authenticate a model delivery
or freeze an executable live plan. Production prompts remain unchanged, live calls
paused and the full workflow canary on hold.

## What changed

The existing intake requires saved/model-review provenance. The existing observed
publisher accepts only its registered November 14 run. Changing either label to
accept these authored controls would obscure their origin. Instead, add:

- `engine/open_hollywood_engine/evaluations/assessment_authored_source.py`:
  explicit source/presentation/submission contracts, native validation and fixture
  completion with source origin separate from delivery origin.
- `apps/api/open_hollywood_api/services/assessment_authored_source.py`:
  fixed registration, archive authentication and immutable read-only exports.
- `scripts/assessment_authored_source.py`: local `prepare` and `publish-fixture`
  commands, with no run command, trust pin or origin override.
- Independent authored test fixtures and 54 new boundary tests.

[ADR 0057](../adr/0057-explicit-authored-assessment-sources.md) records the decision.
No existing runtime module, production prompt, request, journal, database schema,
dependency or route was changed. Earlier documentation and user edits are retained.

## Source authentication and presentation

The fixed registration is `fresh-claims-2026-11-15`, with admission manifest SHA-256
`2578f9b350175768d208773484ddde4fc459e78b9d77354db94fdec4d61fcfef`.
The adapter verifies all 31 original admission members and both construction-file
digests. It never executes the historical construction helper. A replacement
manifest signed only by its own hashes is insufficient.

Each family retains the exact original work, scope, declarations, briefs, authority
and source-packet bytes. Validation recomputes full-context binding, whole fields,
scope, obligations and historical exact-copy checks. F02 keeps the older full scene
and authentic quotation without treating that quotation as complete semantic evidence.

The separately versioned presentation uses the existing diagnostic system instruction
verbatim. Its data packet retains complete sources, all twelve review fields across
the three families, nine active claims, sixteen component obligations and the two
F02 historical bindings. Gold stays outside input: mutation tests use opaque gold
sentinels, and actual-input checks exclude gold rationales and witness explanations.
Gold remains assistant-authored, not independent human validation.

Original local scope identities remain local identities. The presentation explicitly
supplies the authored records for a possible new assessment; it does not claim a
historical critic saw them. The old compact presentation's saved-intake/provenance
assumptions remain unchanged. This new data presentation has not been measured by
an input-count endpoint or qualified for transport/resource ceilings.

## Actual-packet rehearsal and inspection

Private evidence root:
`data/diagnostics/assessment-authored-source-integration-2026-11-15/`.

| Family | Authored fixture judgments in Q001–Q003 order | Input characters¹ | Preparation / publication members | Result |
| --- | --- | ---: | ---: | --- |
| F01, ferry | supported / unsupported / uncertain | 35,818 | 12 / 13 | All three claims bound |
| F02, kiln | unsupported / uncertain / supported | 52,363 | 12 / 13 | All three claims bound |
| F03, print room | uncertain / supported / unsupported | 38,752 | 12 / 13 | All three claims bound |

¹ User-message Unicode characters, not model tokens. Full presentation JSON sizes
are 45,142 / 63,758 / 48,504 UTF-8 bytes. No provider request envelope exists yet.

The authored responses reproduce admission labels, example adequate citation sets
and rationales only to exercise binding and rendering. They are **not new model
observations or an accuracy score**. Inspection covers every fixed claim, whole
field, selected citation, full-source projection and original authority. Supported,
contradicted and unavailable controls all survive the path with their scope intact.

All six bundles exactly reuse their bytes and modification times. The original
admission directory's 72 non-cache files, including its seal, remain unchanged.
The native source's result/receipt placeholders remain null. Each completion has a
distinct fixture-input identity and derived authority copy; original local scope
and authority remain untouched. All token counters and billing remain null under
`not_applicable_no_inference`. Native null-usage counts do not imply lost telemetry.

Read `verification.json` for the nine inspections; `prepared/F01` through `F03`
contain source/presentation exports. `published/F01` through `F03` contain full
`envelope.json` records and native `view.md` projections. `F01-fixture.json` through
`F03-fixture.json` are explicitly authored inputs, stored outside source archives.
The earlier `trial-F01` directory records a preliminary preparation and is not the
final qualification artifact.

## Verification and preservation

- **371 tests pass: 54 new and 317 existing**, covering native work/result/scope/
  brief/authority/intake plus existing authored completion and publication.
  The 56 existing Pydantic warnings come from intentional malformed mutation fixtures.
- Tests reject source/member/construction drift, self-signed replacement manifests,
  wrong families, mixed source/presentation pins, incomplete or extra units,
  duplicate IDs/keys, bad references, truncated/extra-field replies and forged
  delivery/usage/approval fields. Templates cannot be submitted unedited.
- Tests also cover literal full-context rendering, gold exclusion, original authority
  retention, semantic non-approval, protected/link paths, file bounds, secret rejection,
  source/submission drift during publication, partial outputs and exact reuse.
  Network and database entry points are blocked in the new tests and actual rehearsal.
- Ruff, formatting and strict mypy pass across **291 files**, including both private
  qualification/preservation helpers. No frontend or persistence change requires a client build
  or migration. Repository-wide pytest was not run; the applicable suites are logged.
- Preserve **1,959 earlier sealed members**, the separate **64-member authored-control
  seal**, **636 archive pins**, both original smoke journals, **801 baseline files**
  outside the three documentation updates, and all fourteen issue bodies/posted URLs.
  Keep current source/documentation snapshots, output pins, logs and an acceptance seal.

## Operator commands

Both commands are local and accept only the fixed registered source/families:

```powershell
uv run --extra api python scripts/assessment_authored_source.py prepare `
  --source fresh-claims-2026-11-15 --family F01 `
  --output data/exports/authored-source-F01

uv run --extra api python scripts/assessment_authored_source.py publish-fixture `
  --source fresh-claims-2026-11-15 --family F01 `
  --submission PATH_TO_EXPLICIT_AUTHORED_FIXTURE.json `
  --output data/exports/authored-completion-F01
```

Copy the blank template outside the immutable preparation/archive, name its author
and supply one complete authored response. Exact repeats verify/reuse existing bytes.
Partial or conflicting exports are retained and refused; no repair/resume occurs.

## Recommended next step

Qualify a separate source-aware OpenAI mapping and durable-journal path **locally**
for these three registered works. Reuse the established serializer, terminal usage
auditing and publisher invariants, but explicitly preserve authored **source** origin
when a future assessment has observed **delivery** origin. Test exact input-count/
generation mapping, all active slots, resource admission, terminal failures, unknown
usage and full-work publication eligibility using injected responses. Keep original
saved-review mappings and frozen runs intact.

If that qualifies, prepare a small three-work smoke proposal: provisionally three
counts before three generation attempts, no retries, with exact requests, limits,
whole-claim scoring and stop rules. Request approval before sending prose/context
to either endpoint. This is a recommendation, not a frozen or authorized budget.
The observed publisher will also need a separately qualified registration for the
new source/delivery contract; an authored fixture cannot supply it.

The production benefit is a traceable assessment path that can test factual
generalization without confusing fixture origin with observed success. Natural
critic precision, editorial judgments, edit necessity, writer preservation and
story quality remain separate work. Human review remains focused on feel, flow,
character and story-breaking effects; mechanical evidence remains application-owned.
CW-007/CW-013 stay open, CW-014 unqualified. Step 19 remains IN PROGRESS; Step 20
NOT STARTED. Production prompts unchanged; live calls PAUSED; canary ON HOLD.
