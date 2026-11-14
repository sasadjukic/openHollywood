# Compact version-two four-work OpenAI smoke results

Date: 2026-11-14

Status: approved execution, terminal audit and claim inspection **COMPLETE**.
**Four counts, then four generation attempts; zero retries.** All four works
delivered complete, source-bound assessments. Production prompts unchanged;
further live calls **PAUSED**; full workflow canary **ON HOLD**.

## Outcome

The [frozen version-two plan](assessment-openai-compact-smoke-plan-2026-11-14.md)
ran once with `gpt-6.1-sol` / `high`. Every input count passed before any generation.
All eight requests returned HTTP 200. All four generations returned the requested
model, completed normally, mapped without issues and bound every original active
claim. The closed terminal audit records four completion-eligible works, six
delivered assessments, no accounting holds and no unknown generation usage.

Inspection against the unchanged declarations, complete source texts and work
briefs supports all six returned judgments: **four supported, two uncertain**.
The uncertainty is appropriate for claims about an unavailable next-scene opening.
No unsupported material premise or evidence-coverage defect was identified in these
six assessments. This is a bounded source inspection, not a pooled accuracy score,
new automated semantic gold or a blind human review.

The concrete delivery obstacle observed in the original smoke is resolved for
these four requests. N06's count fell from **350,749 to 62,243 tokens**, a reduction
of **288,506 (82.25%)**, under the same 272,000-input reservation. The compact
presentation retains the qualified source texts, scope and citation bindings;
it does not shorten the story. Only N06 has a measured original-presentation count:
the other three original count slots were never dispatched. There is no measured
version-one generation baseline or controlled latency/model-quality comparison.

## Authorization and fixed slots

Approval covered the full frozen unpublished prose/context at both endpoints:
`https://api.openai.com/v1/responses/input_tokens` and
`https://api.openai.com/v1/responses`. Each received four requests in its frozen
order, with all counts first. No model-list, metadata, polling, recovery or other
provider request was added. The existing approved credential was used in memory.

Approved plan bytes SHA-256:
`fa814d8c09b897ad8c6c9b902ef99a9eec7b24a49a8923ec4f2643253d8181f5`.

All eight outgoing bodies match their frozen manifests. Original intakes, messages,
whole reviews, declarations, briefs, six active claims, 51 fields, four holds,
41 unselected fields and 3,658 locators are preserved. Qualified operator provenance
remains in its exact locally bound file, outside both endpoint bodies. It is not
model-visible story authority. No diagnostic message, response schema, resource
setting or production prompt changed during execution.

| Fixed slot | Work | Terminal result | Count / generation input tokens | Exchange seconds |
| --- | --- | --- | ---: | ---: |
| Count 1 | N06 | HTTP 200; admitted | 62,243 | 1.788 |
| Count 2 | N07 | HTTP 200; admitted | 66,620 | 0.475 |
| Count 3 | N10 | HTTP 200; admitted | 66,729 | 0.309 |
| Count 4 | N11 | HTTP 200; admitted | 64,624 | 1.596 |
| Generation 1 | N06 | HTTP 200; complete; native binding complete | 62,243 | 10.101 |
| Generation 2 | N07 | HTTP 200; complete; native binding complete | 66,620 | 25.374 |
| Generation 3 | N10 | HTTP 200; complete; native binding complete | 66,729 | 16.571 |
| Generation 4 | N11 | HTTP 200; complete; native binding complete | 64,624 | 18.199 |

There are no undispatched slots or remaining attempts. The one-shot journal is
closed with reason `complete`; it cannot be resumed. Existing failure stops remain
unchanged. This successful run does not itself exercise every failure branch
previously qualified with injected transport.

## Inspection of every returned claim

| Work / claim | Returned judgment | Source inspection |
| --- | --- | --- |
| N06 / Q001 | Supported | The assignment explicitly requires no sill crossing at scene end. The complete current draft explicitly ends with crossing and entry. Both quoted attributions are present. |
| N07 / Q004 | Supported | The explicit outside/no-crossing exit and the final completed entry directly conflict. Earlier outside wording does not override the subsequent result. |
| N07 / Q005 | Uncertain | Current boundary overrun is established, but the supplied next-scene summary does not establish that scene's opening state. Planned interaction with Thorne cannot prove that it begins with Elara already inside. |
| N10 / Q003 | Supported | Complete current prose depicts entry; the current exit explicitly forbids crossing. The explanation distinguishes anticipated action from the later completed result. |
| N10 / Q007 | Uncertain | The exit restriction is established; the next-scene beginning remains unavailable. Current-scene crossing cannot establish future opening placement. |
| N11 / Q003 | Supported | The visible repair test records the earlier crossing allegation; the complete current draft ends outside without completed entry; the current exit requires that state. Historical allegation is kept separate from independently verified historical event truth. |

Every returned reference resolves exactly to its original registry location, field,
document version and source hash. Material coverage was inspected in addition to
mechanical binding:

- **N06:** E0221/E0876 locate the compound outcome in the saved plan and assignment;
  E0904 is the complete current draft. Plan `d4c5015b-8ffd-557d-8ce3-5d829a163ebb`
  and draft `a8e052b9-4b2d-51bb-8751-b11f36d2a6a3` match the explanation.
- **N07:** Q004 cites the exit, current-plan identity, policy and complete draft
  (E0869/E0882/E0887/E0904). Q005 adds all four supplied next-scene leaves
  (E0883–E0886), reaching the eight-reference cap. Complete visible context confirms
  that no separate next-scene entry state or opening prose is supplied. An identity
  citation alone would not establish that absence.
- **N10:** Q003 cites complete draft E0907, both authorized exit fields
  E0217/E0872 and policy E0890. Q007 cites both exits, every next-scene leaf
  E0886–E0889 and the full draft. The current draft version is
  `66b76662-fc4d-530c-bbeb-7dd84d90489a`. Its duplicated jamb sentence is visible
  but outside the active claims; this smoke does not score duplication detection.
- **N11:** E0693/E0697/E0698 bind the saved allegation and original critique/draft
  identities; E0943 covers complete current draft
  `5a350a78-9448-5abb-8fae-73317af549c5`; E0203 locates the current plan's exit.
  The reason explicitly limits the historical evidence to what the reviewer alleged.
  It does not require or pretend to possess the whole earlier draft in this work.

For N07/N10/N11 the current plan is `7de4c877-9153-5b24-9910-85fff0202312`.
The future summary is bound to blueprint `30b1045e-7f76-5932-9ea9-79acd162f6e7`,
scene_2. Its outcome and turning point concern following Thorne and his claim about
the lost children. They provide no opening-state specification. Missing evidence
therefore remains uncertainty, not contradiction. N11's correction is only the
specified boundary defect; it does not establish that all criticisms were resolved.

The returned explanations contain some redundant authorized citations, but no
material unsupported inference was identified. Full-prose locators are valid under
this frozen field-level contract; this is not a test of precise paragraph selection.
All four holds and 41 unselected fields remain outside the assessment target.
Mechanical audit fields for semantic support/evidence adequacy remain `unassessed`;
this separate inspection does not rewrite model captures or promote them into gold.

## Resource accounting

| Work | Generation input | Output, including reasoning | Reasoning subset | Cached input | Conservative generation estimate |
| --- | ---: | ---: | ---: | ---: | ---: |
| N06 | 62,243 | 508 | 321 | 0 | $0.1606875 |
| N07 | 66,620 | 1,276 | 803 | 0 | $0.1793100 |
| N10 | 66,729 | 851 | 405 | 0 | $0.1753325 |
| N11 | 64,624 | 781 | 516 | 0 | $0.1693700 |
| Total | **260,216** | **3,416** | **2,045** | **0** | **$0.6847000** |

All generations stayed within 272,000 input, 32,000 output including reasoning,
$1 conservative estimate and 600 network seconds per work. The recorded dispatch
window was **258.717 seconds**, within 3,600 seconds, excluding initial local source
authentication and final audit. Per-exchange times above measure transport, not
total operator elapsed time or model-only compute time.

Input counts independently total 260,216 and happen to match generation input
usage. They are not added to generation usage. Count responses have no generation
usage counters. Reasoning is already included in output and is not charged twice
in the estimate. All four generation usage records are known; none is under an
accounting hold.

The **$0.6847** estimate uses the frozen conservative rate basis: all input at the
$2.50/M cache-write allowance and output at $10/M, without a cache discount. It is
below the $4 reservation. **Actual billed cost remains unknown**; count charges
are not inferred or assumed free. No new pricing or account query was made.

## Evidence and verification

Private preparation: `data/diagnostics/assessment-openai-compact-smoke-2026-11-14/`.
Private results: `data/diagnostics/assessment-openai-compact-smoke-results-2026-11-14/`.

- `authorization.json` and `preflight.log` retain approval and local verification.
- `capture/` copies all 19 journal files byte for byte: header, plan, eight durable
  intents, eight outcomes and final stop. The original fixed journal is retained.
- `audit/` is the supported read-only terminal export, with transport and model
  observation true and origin `observed_openai_transport`. It reconstructs native
  receipts, source binding, all eight slots and four whole-work completions.
- `summary.json` and `assessment-captures.json` retain usage, statuses and bound
  finals. `inspection.json` fills every frozen slot and claim; `manual-review.json`
  records the separate source-based inspection, not a human preference rating.
- Exact request/response identifiers, safe mapped finals and response-body digests
  are retained privately. Raw HTTP response bytes were not retained. The application
  journal is integrity evidence, not provider-signed attestation.

Before dispatch, all **85 sealed preparation members**, **11 current implementation/
documentation snapshots** and **51 frozen files** matched. Supported local
verification passed for all four registered works and the live journal was absent.
After execution, the supported terminal audit and its exact repeat pass without
rewriting journal or export bytes/mtimes. Independent inspection verifies order,
intent/body/manifest links, count admission, all original active IDs, literal source
locations, nullable usage and accounting. Ruff, formatting and strict mypy pass on
**282 files**, including the private inspection helper.

The preparation's **407 tests** remain prior qualification evidence; they were not
rerun here. No runtime or test implementation changed in this execution task.
Documentation links, UTF-8/LF and `git diff --check` pass; no frontend/build or
database migration check applies.

Final preservation verifies **1,668 earlier sealed members**, **636 archive source
pins**, **793 of 796 baseline files** outside the three declared documentation
updates, the original closed version-one journal, all fourteen issue bodies and
posted URLs. Existing edits from preparation are preserved. Only README, the issue
index and tracker are updated alongside this report and private results. The frozen
approval document stays a historical record. Final source snapshots, preservation
records and a results seal retain the completed handoff.

## What this establishes and next step

This is observed evidence that the compact read-only path can count, deliver, bind
and complete these four works with full visible source context. The six inspected
assessments also preserve the declared distinctions between current and future
scope, whole-claim uncertainty and historical allegation. It does not establish
repeatability, fresh-family generalization, natural-negative coverage, ordinary
review precision, editing necessity, writer preservation or improved story quality.
The four works share a scene family and heavily overlapping prose. No frontier-model
comparison or new human preference assessment was performed.

Next, **preserve the four real deliveries as local regressions and audit the handoff
from the smoke's observed terminal receipts to the read-only assessment/export
component**. Reuse these exact captures without inference. Check source/request
binding, observed-versus-authored origin, all six active IDs, held/unselected scope,
usage and completion coverage end to end. The smoke already exports complete native
results; establish which existing downstream contracts accept them before proposing
an adapter. Never relabel these captures as authored fixtures or treat a complete
delivery as semantic approval or writer permission.

After that local check, assess whether a small prospective repeat with fresh scene
families and supported/contradicted/unavailable controls is warranted. Do not freeze
another budget or widen production routing from this smoke alone. Keep human review
focused on feel, flow, character and story-breaking details while the application
owns mechanical source/coverage checks.

CW-007/CW-013 remain open; CW-014 unqualified. Step 19 **IN PROGRESS**, Step 20
**NOT STARTED**. Production prompts, profiles, graph, gates and human checkpoints
remain unchanged. Further live calls **PAUSED**; full workflow canary **ON HOLD**.
No user database writes, writer dispatch, external issue edits or issue closure.
