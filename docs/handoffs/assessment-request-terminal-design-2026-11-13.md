# Intake-bound assessment request manifest and terminal receipt

Date: 2026-11-13. Status: bounded local design and verification **COMPLETE**;
runtime manifest/terminal adapter **NOT STARTED**.
Production prompts unchanged; live calls **PAUSED**; canary **ON HOLD**.

The proposed boundary links a verified intake to an exact request and then to its
terminal evidence. It separates successful assessment binding from delivery failure,
unknown usage and semantic qualification. This is ready for a narrow local
implementation, subject to the acceptance checks below; it does not qualify a real
provider adapter or authorize inference.

## Basis and scope

The [six-delivery audit](assessment-delivery-admission-2026-11-12.md) admitted all six
captures to their original B work, but refused all 24 attachments to current intake.
Its saved-response retention also distinguished logical request, endpoint body,
retained response and original raw HTTP digests. This design addresses those missing
links prospectively. It does not alter that historical evidence or add an archive
adapter duplicating the existing exporter.

Reuse N06/N07/N10/N11 and the same six authored completion responses. Preserve all
51 report fields, four holds and 41 unselected fields. Source reviews remain real
archived critic captures; **every new terminal scenario is authored fixture data**.
The complete intake, including operator provenance, stays in the local bundle;
the assessment presentation retains the unchanged full work, declarations and
briefs. Operator-only history does not become critic-visible authority.

The durable decisions are in [proposed ADR 0050](../adr/0050-intake-bound-assessment-request-terminal-design.md).
The current authored publisher and registered native B exporter remain unchanged.

## Request contract

One manifest represents one original batch. A whole-work plan must commit all
manifests in original order before dispatch, with unique attempts and exact batch
coverage. No repartition, claim extraction, changed interpretation or hidden retry.

| Binding | Required meaning |
| --- | --- |
| Source | Registered source kind/review, exact intake/manifest bytes, source/work/declaration/brief fingerprints, source-verification receipt hash |
| Assessment | Exact full-context presentation bytes, renderer contract, response schema, original batch and active units |
| Provider | Qualified adapter contract and implementation identity; selected provider/model/settings fixed explicitly |
| Endpoints | Ordered optional count then generation; method, destination and path; exact serialized JSON bytes and separate canonical body digest for each |
| Attempt | Unique ID, original ordinal budget slot, one generation allowance, zero retries; authorization supplied separately by a frozen run plan |
| Manifest identity | Canonical hash of the complete versioned payload; the hash wrapper is excluded to avoid recursion |

The [request schema](../contracts/assessment-request-manifest-design-1.schema.json)
is deliberately fixture-only: `provider=fixture`, `model=design-only-no-model`,
`.invalid` destination and `live_authorized=false`. Its full-context serialization
is a mechanical stand-in, **not a new assessment prompt or provider-compatible body**.
The synthetic 32,000-token output setting tests settings binding; it selects no real
provider resource limit. A future implementation must register the real renderer
and provider mapping and verify the actual outgoing bytes against them.

An operator-provided hash is not authentication. The application must recollect the
registered source, recompile the intake, compare with the saved exact intake and
regenerate the presentation/body before accepting a manifest. Recheck source and
intake before dispatch and publication. The pure prototype cannot authenticate a
filesystem, a network destination or the caller of its functions.

The future whole-work plan references manifest hashes; individual manifests do not
reference the plan. This keeps both immutable without a circular digest. Production
budget reservation, cancellation and approval remain application responsibilities.
No budget for real calls is created here.

## Terminal contract and accounting

The [terminal-evidence schema](../contracts/assessment-terminal-evidence-design-1.schema.json)
records observations. The [terminal-receipt schema](../contracts/assessment-terminal-receipt-design-1.schema.json)
describes an application-derived output. Parsing either schema alone proves no
delivery. Submitted receipts must be recomputed from the authenticated journal,
not accepted because their success flags or hashes agree internally.

| Outcome | Generation accounting | Completion behavior |
| --- | --- | --- |
| Cancelled before any dispatch intent | No generation attempt; usage not dispatched | Visible incomplete work, no synthetic successful receipt |
| Count failure, interrupted count or missing count result | Count attempt consumed; generation not started | Stop before generation; count error evidence remains |
| Generation intent followed by interruption, cancellation or transport error | One generation attempt consumed; usage unknown unless actually observed | Failed native receipt, no retry or successful subset |
| Non-200 response | Attempt consumed; retain available usage and ordered safe error chain | Transport failure, even if the body contains apparently valid final JSON |
| Length/refusal/unrecognized terminal | Attempt consumed; retain partial final and available usage | Failed receipt; no salvage of parseable slots |
| Complete response with empty/malformed/missing/extra/duplicate slots or invalid citations | Attempt consumed; retain exact final and usage | Invalid binding, no completion credit |
| Complete response with native binding | Attempt consumed; known, partial or unknown usage preserved | `bound_unassessed`; full work completes only when every original batch binds |

The optional count path is frozen before dispatch, not chosen after a count failure.
Only a successful count with a known count result may precede generation. Its result
is retained separately and never fills a missing generation token count. An adapter
without a count endpoint uses a generation-only manifest from the outset.

Persist intent before send, and compare destination/method/path plus actual body
bytes at the transport boundary. A crash after intent may have incurred usage even
when no response was captured. On restart, export that uncertainty; do not resend
automatically. A wholly missing terminal remains missing and prevents a completed
publication. A future recovery tool may derive an interrupted terminal from the
durable intent journal, preserving that origin; it cannot invent dispatch or usage.

Per-counter input/output/reasoning/cached-input usage remains nullable. Known
reasoning cannot exceed known output, and cached input cannot exceed known input.
Known generation input/output produce `usage_state=known`; optional subcounters
may still be null. Partial and unknown are distinct. Known zero is also distinct
from unknown. Actual billed cost is null throughout this first contract; estimates
belong in a separately labeled record. Unknown usage never becomes zero cost.
The native completion's known subtotals always accompany its unknown-attempt count.

All terminal paths deny further dispatch in this read-only design. A successful
binding with unknown usage can be exported truthfully, while further inference
remains stopped pending accounting. Neither delivery nor usage knowledge proves
factual support, adequate evidence, necessary editing, emotional effect or craft.

## Retention and trust

Distinct identities are mandatory:

1. Intake bytes and each source/work/auxiliary canonical fingerprint.
2. Exact assessment-presentation UTF-8 bytes.
3. Complete request payload canonical hash, used in the future native request slot.
4. Count body bytes and canonical body hash.
5. Generation body bytes and canonical body hash.
6. Exact raw-final UTF-8 hash.
7. Safe retained-response canonical hash.
8. Optional observed raw HTTP-body digest, explicitly marked as not replayable when
   the original bytes were not retained.

Keep safe response-level IDs, returned model, finish reason, HTTP status, terminal
state, final text, usage and ordered error links. Missing values remain null; IDs
are locators, not authentication. Refuse undeclared fields. Do not persist arbitrary
headers, keys, unrestricted exception objects or reasoning text. The adapter must
apply the existing secret guard before writes; unsafe capture is an incomplete
audit requiring a safe failure record, never redaction followed by a false success.
The fixture schema does not implement that future transport sanitizer.

The prototype fixes exact returned-model equality for completed fixture responses.
Real provider aliases/snapshots require an explicit mapping in the qualified adapter,
not permissive string matching or retroactive acceptance of a surprise model.

## Verification and limits

**26 scenario checks pass**: four full-context replays of the existing intake works
and 22 compact authored terminal scenarios. All six existing authored claim results
bind without source or scope changes. The compact matrix covers success, unknown,
partial and known-zero usage, refusal, length, non-200, interrupted/error/cancelled
generation, failed/unknown/interrupted count, cancellation before dispatch, empty and
malformed final, duplicate/missing/extra slots, bad citation, unrecognized terminal
and a predeclared generation-only endpoint.

**37 mutation refusals pass**, including changed source bytes, presentation/settings,
schema/batch/active units, manifest/body/final namespace substitution, endpoint order
and body drift, malformed terminal evidence, wrong attempt/model, usage inconsistency,
forbidden fields, forged model origin, missing and duplicate terminal coverage.
Separate two-batch fixtures verify both complete delivery and a single successful
batch whose failed partner prevents whole-work completion.

**369 existing tests pass**, with the 56 existing deliberate-mutation Pydantic
warnings, in 108.52 seconds. Ruff, formatting and strict mypy pass for **252 files**:
250 repository Python files plus the two private design helpers. No frontend,
OpenAPI or build check applies to this documentation/private-design change.

The checks reuse the native binder/completion component and registered source
collector, with network and SQLite blocked. No provider catalog, token-count or
inference access occurs. The actual intake bundle bytes/mtimes are checked before
and after each replay. Preservation verification confirms **721 existing files**
unchanged outside the four documentation updates, **841 earlier sealed members**
intact, and **1,166 original source pins** unchanged. All 26 accepted terminal
records round-trip under the generated schema models; all three public schemas
match their generated shapes. The existing secret guard also passes on the design
artifacts. Source success and authored response success
remain separately labeled; none of these checks is a new model observation.

The schema limits include at most twelve active units/manifests per work, two
endpoints, 16,777,216-character presentation/body strings inside a 64 MiB manifest
byte envelope, 1 MiB terminal-evidence envelope, 64,000-character/256,000-byte finals
and eight error links per chain. Existing native limits on reasons, references and
complete batch coverage remain unchanged. A tracked publisher still needs a whole
bundle bound and safe/exclusive filesystem qualification; schema bounds alone do
not provide them.

Private artifacts: `data/diagnostics/assessment-request-terminal-design-2026-11-13/`.
`prototype.py` is a pure, non-networked design; `verify_design.py` blocks network and
SQLite while authenticating sources and constructing explicitly authored receipts.
No archived Python is executed. Source prose and fixture finals remain private.
The three public schemas match the prototype's generated shapes. The first,
redundant full-context scenario matrix was interrupted to avoid repeatedly
recompiling the same large source. Its seven partial outputs remain under
`interrupted-initial-check/`, excluded from accepted scenarios. The final matrix
checks the four actual works once each and uses compact fixtures for branch coverage.

Key evidence:

- [Scenario and refusal results](../../data/diagnostics/assessment-request-terminal-design-2026-11-13/verification.json).
- [Quality-check record](../../data/diagnostics/assessment-request-terminal-design-2026-11-13/quality-checks.json).
- [Source/evidence preservation](../../data/diagnostics/assessment-request-terminal-design-2026-11-13/preservation.json).
- [Local prototype](../../data/diagnostics/assessment-request-terminal-design-2026-11-13/prototype.py)
  and [verifier](../../data/diagnostics/assessment-request-terminal-design-2026-11-13/verify_design.py).

Reproduce with `.venv/Scripts/python.exe -X utf8
data/diagnostics/assessment-request-terminal-design-2026-11-13/verify_design.py`.
Omit `--write-schemas` to check the existing schemas rather than regenerate them.
The script writes only its new design evidence directory; it does not update sources.

## Recommended next step

Implement the **narrow tracked manifest preparation and terminal-audit path**, still
locally, with these acceptance requirements:

1. Promote the pure contract/derivation under new runtime versions. Reuse the
   registered source collector and native binder/completion. Prepare the entire
   original work's request set and preserve full intake and visible holds.
2. Qualify an application-owned journal/capture boundary using injected transport:
   exact outgoing body comparison, safe metadata/error retention, durable intent,
   crash/cancel behavior, attempt accounting and unknown usage. Test actual callback
   observations rather than trusting caller-authored dispatch digests.
3. Provide read-only terminal audit/export for successes and failures, with separate
   completion eligibility, exact repeat reuse, source rechecks, secret/path bounds
   and manifest-last publication. Retain the current authored and registered B paths.

First use explicitly authored transport fixtures. A real provider-specific renderer
and adapter, then any frozen inference comparison, require separate qualification.
The six historical successes do not supply real interrupted/non-200/unknown-usage
coverage for this new path. Another live model test is not yet the next useful step.

This improves traceability and honest accounting; it does not solve semantic
assessment or qualify writer changes. Future story-quality work must still separate
factual checking from editorial judgment and assess feel, flow, character and
story-breaking effects. CW-007/CW-013 remain open; CW-014 remains unqualified.
Step 19 **IN PROGRESS**; Step 20 **NOT STARTED**. Prompts unchanged; live calls
**PAUSED**; full workflow canary **ON HOLD**.
