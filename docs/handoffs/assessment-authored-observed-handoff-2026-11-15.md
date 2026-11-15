# Authored-source observed regressions and downstream audit

Date: 2026-11-15.

The three [observed smoke deliveries](assessment-authored-three-work-smoke-results-2026-11-15.md)
are preserved as local regressions. Exact replay retains all nine original claims,
full source context, three unselected editorial summaries and every citation.
The existing read-only smoke audit already exports these observations correctly.

The remaining integration gap is a **registered completion-publication path for
observed deliveries over authored sources**. The authored-source publisher accepts
authored fixtures; the observed publisher accepts the earlier registered probe smoke.
Both correctly refuse this different combination. This is a bounded publication
gap, not a new model failure or lost assessment result.

**78 local scenario checks pass. No new provider calls were made.** Production
prompts and application/runtime contracts are unchanged; further live calls stay
PAUSED and the full workflow canary stays ON HOLD.

## Preserved regression evidence

Private root: `data/diagnostics/assessment-authored-observed-handoff-2026-11-15/`.

| Regression | Preserved assessment contrasts |
| --- | --- |
| F01 ferry | Required boarding and endpoint compliance; false throughout-prohibition; unavailable later draft |
| F02 kiln | True action versus false historical violation; unavailable report; critic allegation versus complete old prose |
| F03 printroom | Unavailable certificate; complete signature/stamp conditions; conditional promise versus completed procedure |

`regressions/F01.json`, `F02.json` and `F03.json` retain each complete original
source, exact request manifest, observed terminal, native receipt/result and expected
binding/completion state. Their source origin remains `authored_diagnostic`, delivery
origin remains `observed_openai_transport`, and native work provenance remains
`synthetic_fixture`. These labels describe different events; do not change native
source provenance merely because its assessment was produced by a model.

`captures/` contains **50 byte-identical files**: the fifteen-file journal, ten-file
request preparation, seventeen-file original audit, four result/inspection records
and four frozen plan/settings/gold records. `source-inputs/` additionally preserves
**22 exact input/receipt files**: six original inputs and a source receipt per family,
plus the original admission manifest. These copies are regression evidence, not
new trust registrations. Supported replay still authenticates the original registered
archive, source construction hashes, exact requests and closed observed journal.

`verified/smoke-audit/` reproduces the original seventeen-member audit byte for byte
and reuses it without rewriting. Nine additional native/brief/authority views show
all three works. `authored-variants/` contains explicitly labelled counterfactuals;
they are not additional model outputs. In altered exchanges, the original HTTP-body
digest is cleared and the response ID identifies a local counterfactual. Full-journal
variants explicitly use injected delivery origin and never occupy the live path.

The prior **9/9** label and **16/16** material-component inspection is preserved
unchanged. This audit creates no new semantic gold, human preference rating or pooled
model-accuracy result.

## What currently works

| Boundary | Observed result | What must remain outside that boundary |
| --- | --- | --- |
| Authored smoke audit | Six fixed slots, three complete works, observed delivery origin and accounting clearance reconstructed | Factual/evidence/editorial approval remains unassessed |
| Native result binding | Exact original claims, request identity, raw-final digest and literal citation locations reproduced | Provider authentication, billing and semantic truth |
| Native whole-work completion | All original units and batches complete, with no writer permission | Cached-token/accounting checks and observed provenance |
| Native result/brief views | Full work, source text, original fields, declarations and briefs retained | These are projections, not a complete source-and-delivery envelope |
| Authority view | Historical bindings and component obligations retained using separately derived request-bound authority | Original local authority must remain unchanged in the source envelope |
| Authored-source fixture publisher | Rejects observed-origin submissions and caller receipts | Must not relabel observed responses as authored fixtures |
| Registered observed publisher | Refuses the new authored source/smoke identifiers | Its current probe source, compact plan, four-work layout and registration are different |

Relevant code is the [authored source adapter](../../apps/api/open_hollywood_api/services/assessment_authored_source.py),
[authored smoke audit](../../apps/api/open_hollywood_api/services/assessment_openai_authored_smoke.py),
[registered observed publisher](../../apps/api/open_hollywood_api/services/assessment_observed_completion.py),
[native binding](../../engine/open_hollywood_engine/evaluations/assessment_result.py) and
[whole-work completion](../../engine/open_hollywood_engine/evaluations/assessment_work.py).
[ADR 0057](../adr/0057-explicit-authored-assessment-sources.md) deliberately preserves
the authored-source distinction; [ADR 0059](../adr/0059-authored-three-work-observed-smoke.md)
defines the successful observed smoke wrapper.

## Material findings

**The original local identity is not the provider request identity.** Binding an
observed receipt against the source's original scope is refused for all three works.
Both count-body and generation-body hashes also fail as substitutes for the request
manifest identity. The authority renderer requires a separate derived authority bound
to that observed request. This succeeds without mutating the original scope or
authority. A future completion envelope should carry both identities explicitly.

**Observed origin comes from the authenticated outer journal.** The shared terminal
reducer retains its fixture-specific contract and delivery label. The actual smoke
wrapper correctly excludes those labels and supplies authenticated observed origin.
Native receipts/results carry neither source nor delivery origin. Exporting the
shared reducer or a native view directly would lose that distinction. Source receipts
and construction records saying zero live calls remain true about construction;
they must not be rewritten to describe this later inference.

**Completion alone cannot release accounting.** For each of the three deliveries,
an authored unknown-cache variant and an excessive-input variant retain complete
native binding. Native `unknown_usage_attempts` remains zero because its counters
cover input/output, not cached usage. The outer terminal correctly holds accounting.
The actual observed run has no such problem.

The newer authored smoke audit already includes accounting clearance in its overall
eligibility gate. This differs from the older compact-audit limitation recorded on
November 14. Full-journal final-slot variants prove that unknown cached usage or
excess input blocks **all three works**, even when all nine claims bind. A missing
closing stop also blocks all works despite complete native results; interruption
retains the unknown consumed final slot. No successful subset qualifies.

**Delivery eligibility is not evidence of observed origin.** A complete injected-origin
copy can satisfy delivery/accounting eligibility while both transport/model-observation
flags remain false. A future observed publisher must require the registered plan,
closed observed journal and exact audit, rather than trusting an eligibility boolean
or caller-supplied receipt.

**Literal binding is not evidence sufficiency.** Three authored false-reason controls
still bind structurally, with support/evidence adequacy unassessed and writer
permission false. An additional F02 control replaces the complete old-prose citation
with the authentic short locator, while retaining the old review citation. It still
binds, but those citations cannot prove intactness, re-covering and non-removal.
The real F02 delivery used the complete old prose correctly. This is an expected
semantic boundary, not a newly discovered model error or a reason to accept the
short locator as complete evidence.

**The current operator export is sufficient for inspection.** All full sources,
original scope/authority, complete observed terminal data, requests and evidence
views already exist in the supported smoke export. A new publisher is justified
only for admitting this source/delivery combination into the tracked completion
component. It should not add a second transport, reconstruct missing raw HTTP bytes,
invent a saved-review intake or broaden trust to arbitrary paths/hashes.

## Local verification

| Outcome | Scenarios | Meaning |
| --- | ---: | --- |
| Bound, semantically unassessed | 7 | Three exact observed replays, three authored false reasons, one insufficient-locator control |
| Bound with accounting hold | 6 | Unknown-cache and excessive-input controls for each family |
| Boundary confirmed | 6 | Three native-view limitations and three shared-reducer origin checks |
| Complete fixture only | 1 | Injected-origin copy remains non-observed despite delivery eligibility |
| Every work held | 4 | Final unknown cache, excess input, pending generation or missing close |
| Failed without credit | 3 | Parseable but truncated terminal responses |
| Incomplete | 3 | Missing original receipt |
| Unresolved binding | 3 | Valid delivery receipt without native binding |
| Refused | 45 | Cross-work/request/body/scope/authority mismatch, stale finals, missing/duplicate/extra claims, invalid refs and incompatible publication origins/contracts |
| **Total** | **78** | Software scenarios over three saved deliveries; zero inference |

The replay denies socket connections, HTTP/client/provider transport, live/qualification
entry points and database access. No provider authentication or user database
access occurs. Existing secret-refusal guards remain active. The original sources and
all copied evidence retain their bytes and mtimes; repeated audit publication exactly
reuses its files. The private `replay.py` is executable local regression coverage.

**254 applicable existing tests pass** (186.52 seconds). The run records **34
Pydantic serializer warnings** from unchanged authority tests that deliberately
inject malformed values; these are retained in `tests-regression.log`. All **78**
local scenarios pass in `replay-final.log`. Ruff, formatting and strict mypy pass on
**298 files**, including the two private replay/preservation helpers. No application, domain, schema, dependency or tracked-test
implementation changed. No frontend build or migration applies; repository-wide
pytest was not run.

Preservation includes **2,556 prior sealed members**, the separate **64-member**
authored-control seal, **636 archive pins**, **826 of 829 baseline files** outside
README, issue index and tracker updates, both earlier closed smoke journals, the
latest fifteen-file closed journal and **688** original authored/preparation/result
files and mtimes. All fourteen issue bodies and posted URLs remain unchanged.
Earlier uncommitted preparation work is preserved. New regressions, local checks,
source/documentation snapshots and verification evidence receive their own seal.

## Recommended next step

Implement a **narrow registered observed-authored completion publisher**, locally,
using these three saved deliveries. Keep the existing smoke audit as the reference.
This task has audited that boundary; it has not installed a new publication adapter.

1. Register only the exact authored smoke plan and existing audit. Reuse the supported
   audit to reauthenticate sources, journal, requests and terminal mappings. Reject
   caller receipts, origin overrides, paths/hashes that register themselves, fixture
   journals and successful subsets. Accept all F01/F02/F03 works together.
2. Preserve each complete original `AuthoredSource`, its six exact input members and
   source receipt alongside the exact request/presentation, observed terminal,
   endpoint slots and native completion. Carry derived request-bound authority as a
   separate value. Keep the source construction identity, original authority and all
   unselected fields unchanged. Do not fabricate `CompletionContext`/`IntakeResult`.
3. Require observed origin, complete journal/work/slot coverage and separate accounting
   clearance. Retain all four usage counters, failure evidence and unknown billing.
   Use explicit source and delivery labels, unassessed semantic/editorial/evidence/
   craft fields and false writer permission. Prior assistant inspection is separate
   evidence, not automatic release authority.
4. Reuse the existing guarded, manifest-last exclusive publication and exact-reuse
   machinery. Protect all source/preparation/journal/audit paths, recheck after
   rendering and before finalization, and preserve failed partial outputs. Qualify
   the three exact successes and the local mismatch/origin/accounting/closure controls
   before exposing the new path. Keep both existing publishers unchanged.

Use a separate application adapter and preserve the frozen implementations. The
current authored-source fingerprint includes every `assessment_*.py` evaluation
module; adding a new module there would also change that fingerprint. Reuse the
existing domain records instead of silently invalidating these saved preparations.

No further model calls or new live budget are needed for this implementation.
After it is verified, assess the next production integration boundary separately;
this result does not authorize automated revisions or a workflow canary.
Human review remains focused on feel, flow, character and story-breaking effects.
CW-007/CW-013 remain open; CW-014 unqualified. **Step 19 IN PROGRESS; Step 20 NOT
STARTED; prompts unchanged; live calls PAUSED; canary ON HOLD.**
