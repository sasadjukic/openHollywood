# Observed assessment completion publisher — 2026-11-14

The read-only completion publisher now has a separate observed-delivery branch
for the four saved compact-smoke works. It reuses the supported audit and native
binding/completion components. It makes no model, input-count or metadata calls.
Production prompts remain unchanged; the full workflow canary remains on hold.

Implementation: `apps/api/open_hollywood_api/services/assessment_observed_completion.py`.
Operator: `scripts/assessment_observed_completion.py`.
Decision: [ADR 0056](../adr/0056-observed-assessment-completion-publication.md).
Basis: [existing downstream audit](assessment-observed-handoff-audit-2026-11-14.md)
and [original observed results](assessment-openai-compact-smoke-results-2026-11-14.md).

## Admission and publication

The only registered source is `compact-smoke-2026-11-14`. The registration fixes
the original plan and audit manifest digests; the plan fixes the live journal,
registered probe intakes, compact presentation/provenance and exact request sets.
The service recollects those sources and requires the supported audit to reproduce
its existing three files exactly. Caller receipts, origin flags, replacements and
partial-work selections are not inputs.

All eight endpoint slots and all four original works must be closed and complete.
The publisher recomputes each terminal, native binding and whole-work completion.
It also checks accounting separately: known input, output, reasoning and cached
input counters; known elapsed time; no reservation violations or accounting holds.
This addresses the audit's finding that native completion can coexist with an
unknown cache counter or excessive usage. The source audit retains failure evidence;
the success publisher does not salvage successful siblings or partial runs.

The 27-member export includes the original full audit, four exact intakes, four
exact request sets, four local-provenance/source-receipt pairs, four full completion
envelopes, four native evidence views, and a manifest written last. Envelopes retain
all original scope decisions, full source context, endpoint/response identities,
raw final, usage and whole-work completion. Views link to these envelopes because
a native view alone is not a delivery-authentication record. Original intake result
and receipt placeholders remain null. No receipt is relabeled as an authored final.

Every observed envelope explicitly distinguishes `registered_diagnostic_probe`
source origin from `observed_openai_transport` assessment origin. The shared terminal
reducer's fixture labels are excluded. Original preparation/source receipts remain
unchanged and continue to describe preparation/source authentication only.

Publication rechecks source membership/bytes and implementation after the existing
audit, after rendering and before its final manifest. It reuses existing path,
secret, size, exclusive-write and exact-repeat protections. A changed/partial/extra
output is refused, never repaired or deleted. Authored publication, B export and
the frozen compact transport implementations are unchanged.

## Saved-capture verification

All four original deliveries publish successfully, and a second complete invocation
returns exact reuse without changing output bytes or mtimes. The reference audit,
original journal, presentations and request preparations also retain their bytes
and mtimes. The bundle has **27 files / 43,354,478 bytes**, below the unchanged 64 MiB
publication bound.

| Work | Active claims | Held fields | Unselected fields | Publication |
| --- | ---: | ---: | ---: | --- |
| N06 | 1 | 1 | 10 | Complete, bound, accounting clear |
| N07 | 2 | 0 | 10 | Complete, bound, accounting clear |
| N10 | 2 | 2 | 10 | Complete, bound, accounting clear |
| N11 | 1 | 1 | 11 | Complete, bound, accounting clear |

All six active claims, four holds and 41 unselected fields remain intact. Exact
intakes, request sets, local provenance and source receipts match their original
bytes; full native views reproduce their original work and bound result. Usage
remains **260,216 input / 3,416 output**, including **2,045 reasoning** and zero
cached input tokens. Actual bills remain unknown. These are retained observations,
not a new inference run.

**38 new local boundary tests pass** (176.41 seconds). Authored fixtures cover
observed/fixture origin, closure/slot/work coverage, fabricated approvals/billing,
unknown cached usage and excessive input despite complete binding, parseable length
failure, missing/duplicate/extra claims, unknown evidence refs, body hash and result
changes, source/audit/journal drift, protected paths, partial/extra outputs,
manifest-last write/source/implementation failures, secret refusal and exact reuse.
Fixture headers used in tests are authored under a temporary test-only registry;
they do not qualify as model observations or enter the real source registration.

**457 existing compatibility tests pass** (495.96 seconds), with 22 pre-existing
Pydantic serializer warnings from deliberate mutation fixtures. Combined with the
new tests, **495 applicable tests pass**. Ruff, formatting and strict mypy pass on
**285 files** (284 repository files plus the private qualification helper).
Documentation links, UTF-8/LF and `git diff --check` pass. Private implementation/
documentation snapshots and an acceptance seal preserve this verification.
No frontend build or migration applies: this adds only a local operator service,
CLI and tests, with no API route, persisted schema or client change.

Preservation verifies **1,825 earlier sealed members**, **636 archive source pins**,
and **795 of 798 baseline files** outside the three intended documentation updates.
Both closed smoke journals, all fourteen issue bodies and all fourteen posted URLs
remain intact. No database, provider profile, graph, gate, production prompt or
human checkpoint changed. No external issue was edited.

Private root: `data/diagnostics/assessment-observed-completion-2026-11-14/`.
The supported publication is `verified-publication/` under that root; its
`N06.completion.json`, `N07.completion.json`, `N10.completion.json` and
`N11.completion.json` are the full per-work envelopes.

The earlier inspection remains the semantic evidence: four supported judgments,
two uncertainties about unavailable future openings, with historical allegation
separated from event truth. This operation adds no model observation or new gold.
Publication state stays `bound_unassessed`; support, adequacy, editorial effect,
edit necessity and craft are not approved, and writer permission remains false.

## Operator use

```powershell
uv run --extra api python scripts/assessment_observed_completion.py `
  --source compact-smoke-2026-11-14 `
  --output data/exports/observed-completion-001
```

Use a new destination or an exact existing publication. Original source/audit/journal
locations are protected. This command is local and never resumes the closed smoke.
The fixed registration deliberately does not accept arbitrary saved reviews or
future runs. There is no public trust-pin override.

The journal establishes local application integrity, not provider-signed proof.
Original raw HTTP bytes remain unavailable; no new raw bytes or actual bill are
invented. `live_calls: 0` describes publication, while the original four counts and
four generations remain present in the audit.

## Proposed next step

Do a bounded local admission/design pass for a prospective full-path qualification:
up to nine whole factual claims across three fresh scene families, with one
supported, contradicted and unavailable control per family where defensible.
Select claims with complete sources and explicit obligation and authority scope.
Include endpoint coverage and historical-source contrasts;
do not turn editorial preference or required revision into factual gold.

Once those controls qualify, prepare a small end-to-end assessment-to-publication
plan with exact sources/requests, scoring, budget and stops for approval. Qualify
any new source registration explicitly. Another same-family smoke is unnecessary
for this boundary; these four successes do not demonstrate broad story-quality
improvement. No new live budget or experiment is frozen in this change.

Human review remains focused on feel, flow, character and story-breaking effects.
Mechanical scope, evidence location, delivery and accounting remain application
responsibilities. CW-007/CW-013 remain open; CW-014 unqualified. Step 19 **IN PROGRESS**;
Step 20 **NOT STARTED**. Live calls **PAUSED**; full workflow canary **ON HOLD**.
