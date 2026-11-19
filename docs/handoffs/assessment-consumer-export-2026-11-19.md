# Tracked read-only assessment consumer export — 2026-11-19

## Outcome

Implemented the consumer boundary recommended by the
[seven-work rehearsal](assessment-consumer-rehearsal-2026-11-19.md). The application
service and operator CLI export either complete fixed registration, with authenticated
sources and all original context retained. This is a local inspection component;
production prompts, model routing, workflow gates and writer behavior are unchanged.
No new provider call, input count, metadata check or database access occurred.

The two successful exports retain **63 original fields**, **15 selected whole claims**,
**4 holds**, **44 unselected fields**, **30 declared material components** and **47
citation occurrences**. All model judgments remain attributed and semantically
unassessed. There is no whole-review verdict, editorial approval or writer permission.

## Implementation and use

- [Consumer exporter](../../apps/api/open_hollywood_api/services/assessment_consumer.py)
  authenticates only the fixed registered publications and delegates upstream
  reauthentication to the supported original publishers.
- [Typed projection and renderer](../../apps/api/open_hollywood_api/services/assessment_consumer_projection.py)
  derive whole-field consumer records from existing native records. They are internal
  projection helpers, not a caller-receipt admission interface.
- [Operator CLI](../../scripts/assessment_consumer.py) accepts registration and output
  only. [ADR 0061](../adr/0061-registered-read-only-assessment-consumer.md) records the
  contract and its limits.

```powershell
uv run --extra api python scripts/assessment_consumer.py `
  --source authored-smoke-2026-11-15 `
  --output data/diagnostics/consumer-authored-operator

uv run --extra api python scripts/assessment_consumer.py `
  --source compact-smoke-2026-11-14 `
  --output data/diagnostics/consumer-probe-operator
```

Use a new destination. An exact repeat reuses the complete export without rewriting
bytes or mtimes. Partial/conflicting destinations remain intact and are refused.
There is no source-path, receipt, trust, origin or work-subset override. A missing or
changed reference publication is refused before the publisher is called.

| Registration | Fixed works | Original members | Consumer export members |
| --- | --- | ---: | ---: |
| `authored-smoke-2026-11-15` | F01, F02, F03 | 43 | 51 |
| `compact-smoke-2026-11-14` | N06, N07, N10, N11 | 27 | 37 |

The pinned original manifest digests are respectively
`dae565b39755dbc58c252f98bfb6267e5a632fdfb5ff886e61640efe3005fca0`
and `465786a0d70d1ae5997d02bbc023a59f55b1f9aa300114f05c684b430746c283`.
All **70** original members are preserved byte-exact. Original filenames remain intact,
except the original manifest becomes `source-manifest.json`, so native relative links
still resolve. Each work adds `consumer.<work>.json` and `consumer.<work>.md`; the new
`README.md` indexes the views. The final `manifest.json` records hashes, original-member
mapping, provenance, implementation and the explicit absence of production association.

## Admission and presentation decisions

Require original manifest/member pins, complete work inventory, supported publisher
exact reuse, closed journal, both endpoint slots per work, valid rebound raw result,
whole-work completion, known input/output/reasoning/cached-input usage and no accounting
hold or budget violation. Recheck all protected upstream members and implementation
around rendering/publication. Use existing exclusive writes, link/junction checks,
secret refusal and manifest-last completion. No new durability guarantee is claimed.

The whole export is refused if any work fails. The private rehearsal's authored fault
views are not accepted as observed results and are not a public fallback route. A
future failed-delivery view would need a separately qualified source contract; the
original terminal audits remain available for inspection.

Every original field remains visible. Held and unselected fields receive no model
judgment. A delivered `uncertain` label stays a delivered model judgment. The namespaced
identity prevents repeated field IDs from joining different requests or registrations.
Original claims, selection findings, declarations, component obligations, work briefs,
model judgments and evidence locations remain separate.

Authored construction scope/authority is unchanged in retained sources; the separate
request-bound authority record accompanies the projection. Probe exports have no
invented authority record. Literal complete-field spans remain distinct from both
declared source coverage and material sufficiency. Model text is rendered as fenced
literal JSON with fixed navigation links; it cannot create new active headings or links
in the consumer view.

All **7** canonical review IDs are null, all production artifact-version associations
are absent, and association status is `not_qualified`. Local journal provenance is
not a provider signature. The retained labels—7 supported, 3 unsupported, 5 uncertain—
describe model output, not an accuracy score. All five semantic/editorial/craft holds
remain unassessed, actual billed cost unknown and writer permission false.

## Verification

The local qualification exports all seven saved works through both supported publisher
paths and checks exact reuse. It compares each field, selection finding, identity,
judgment, declaration, brief, authority, citation and usage record with the accepted
rehearsal. It verifies **21** generated source/result links and all **88** output members.
**84** altered saved-envelope controls are refused (12 per work); these are authored
software mutations, not new model failures.

Tracked tests cover full inventory, held/unselected separation, delivered uncertainty,
literal rendering, source/manifest/member drift, unknown usage, incomplete slots,
wrong request/origin, invalid results, source/destination overlap, drift during rendering
and writes, retained partial/conflicting output, path traversal, secret refusal and
namespaced identity. Definite judgments with complete citations remain semantically
unassessed; definite labels without evidence are refused by the native boundary.
Both injected journal-to-publisher-to-consumer paths are tested without external access.

**54 new tests pass**: 52 consumer/renderer/admission cases and two injected end-to-end
publisher integrations. **245 existing native tests pass** for work, result, intake,
claim scope, work briefs and authority. The combined initial run passed 293 tests;
after adding six semantic/cardinality/identity controls, the final consumer suite
passed all 52. There are **299 distinct passing tests** overall. The 56 retained
serializer warnings come from unchanged deliberately malformed native fixtures.
Ruff, formatting and strict mypy pass on **308 Python files**, including the two
private qualification/preservation helpers. The initial secret-refusal test used
an unsupported context-manager interface; it was corrected to inject the existing
active secret guard, and now passes. No production behavior was changed for that fix.

Preservation verifies **3,313 earlier sealed members**, the separate **64-member**
authored-control seal, **636 archive pins**, **1,476** source/preparation/result files
and mtimes, all three closed smoke journals, all **88** new export members/mtimes and
**833 of 836** baseline files outside the three intended documentation edits. All
fourteen issue bodies and posted URLs remain unchanged. **726** local documentation
links and `git diff --check` pass. The source/documentation snapshots and local evidence
receive a separate acceptance seal. The full seven-work export/reuse/inspection run
took **365.24 seconds**, all local; this is not model inference latency.
No frontend, API route, persisted schema or dependency changed; no production build
or migration is applicable. Full-repository pytest was not run. Existing frozen
publishers and native engine modules remain byte-identical.

Private evidence root: `data/diagnostics/assessment-consumer-export-2026-11-19/`.
Start at `authored/README.md` and `probe/README.md`. `qualification.json` records the
seven-work comparison and 84 refusal controls; `publication-pins.json` retains output
hashes/mtimes. Test/quality logs, preservation results and a separate acceptance seal
make this local run reproducible. Provider/socket/HTTP entry points and database
operations are blocked during saved-data qualification.

## Recommended next step

Do a **bounded local production-association audit/design** before any UI attachment.
Inspect up to six compatible saved production reviews. Use immutable review and
artifact-version IDs plus exact content hashes to define a read-only association contract. Check missing, mismatched, stale and ambiguous
associations; retain the seven diagnostic exports as deliberately unassociated controls.
Do not attach them by filename, scene title, prose similarity or field ID. If suitable
production evidence is unavailable, record that gap rather than fabricate linkage.

No further inference is needed for this boundary. A later production-inspector slice
should expose the attributed assessment beside the exact original artifact, without
changing workflow decisions or adding a human checkpoint. Future story-quality tests
should still evaluate feel, flow, character and story-breaking effects independently
of factual binding and mechanical evidence checks.

CW-007/CW-013 remain open; CW-014 unqualified. **Step 19 IN PROGRESS; Step 20 NOT
STARTED; production prompts unchanged; live calls PAUSED; full workflow canary ON HOLD.**
