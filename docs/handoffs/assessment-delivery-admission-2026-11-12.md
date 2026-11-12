# Saved assessment delivery admission and adapter readiness

Date: 2026-11-12. Status: bounded local audit and verification **COMPLETE**.
Production prompts unchanged; live calls **PAUSED**; canary **ON HOLD**.

**Six saved deliveries qualify under their existing native B archive contract.
None qualifies as a completion of the four current intake work items.** The
registered archive exporter already supports these original deliveries. A second
archive-only adapter would duplicate that capability; the next useful step is a
local design for a prospective intake-bound request and terminal receipt contract.

This is a provenance/admission audit, not new inference, rescoring or evidence that
the model's semantic judgments or story quality improved.

## Bounded selection

Select the first repeat, both presentation orders and all three scene families from
the registered November 7 B archive: `BH-1-{A,B,C}-B-{SC,CS}`. This fixes six
deliveries before inspection. The controls contain authored scenes and claims;
their saved assessment responses are historical model deliveries, distinct from
the authored responses used in the current publisher rehearsal.

The current registered exporter authenticates the immutable repository-shaped
`captures/` snapshot from the earlier B/H audit against its registered results seal
and plan. It verifies 636 source members, but only the six selected deliveries are
admitted/inspected here. Historical code is read as pinned evidence, never executed.
All six entries equal their previously saved native exports exactly.

| Delivery | Family / order | Original delivery and binding | Saved input / output / reasoning tokens | Current intake admission |
| --- | --- | --- | --- | --- |
| BH-1-A-B-SC | Seed-house sluice / sources first | Valid, complete | 6,021 / 808 / 258 | No matching work |
| BH-1-A-B-CS | Seed-house sluice / claims first | Valid, complete | 6,021 / 813 / 235 | No matching work |
| BH-1-B-B-SC | Observatory booking / sources first | Valid, complete | 5,991 / 818 / 239 | No matching work |
| BH-1-B-B-CS | Observatory booking / claims first | Valid, complete | 5,991 / 872 / 254 | No matching work |
| BH-1-C-B-SC | Cinema reel / sources first | Valid, complete | 5,878 / 916 / 293 | No matching work |
| BH-1-C-B-CS | Cinema reel / claims first | Valid, complete | 5,878 / 1,077 / 458 | No matching work |

All six record `gpt-6.1-sol`, high reasoning, two HTTP requests (count and generation),
one generation dispatch, HTTP 200 at both endpoints and a completed terminal response.
Each covers six slots and retains twelve context documents. Total: **36 delivered
slots, eighteen distinct authored claims and twelve historical-copy bindings**.
These are retained historical observations, not 36 new calls or new gold judgments.

## What the recorded evidence establishes

The frozen logical request equals the saved sent-request record. Its full messages,
work fingerprint, active batch and unit selection reconcile. Count/generation body
hashes match their corresponding structured requests and endpoint paths. The saved
assistant final matches the retained response text and native raw-final digest;
native binding and whole-work completion replay successfully for each original work.

The pinned capture implementation checks POST, `https://api.openai.com`, the two
allowed endpoint paths and equality of the outgoing parsed JSON with the frozen
body before dispatch. This is exact **logical request-body** evidence; it is not a
retained byte-for-byte recording of the original HTTP request serialization.

The saved usage matches terminal response fields and native receipts. Reasoning
tokens are a subset of output tokens. Input-count results reconcile; cached-input
counts are zero for this selection. Original cell elapsed time is retained. All six
have **unknown actual billed cost**: the saved reference estimates remain estimates
under their historical pricing assumptions, not invoices or current pricing claims.

The archive preserves original auxiliary records and derived operator views
separately. Original declarations/briefs came from authored prototype work with
different message/work identities. The existing exporter validates their original
identities and rebinds operator-side identities to the actual B work without changing
semantic text. The B request's source/claim/brief sections establish what that
assessment saw; the separate operator receipt was absent from its input. None of
this certifies the visibility of an earlier critic or invents production provenance.

### Retention limits

The capture deliberately retains allowlisted terminal, model and usage fields and
assistant message items. It omits response-level IDs, HTTP headers, reasoning items
and original raw HTTP response bytes. A digest of the original raw response remains,
but cannot be recomputed from the retained sanitized body. The sanitized response
record itself is authenticated by the archive seal, and the complete final text is
retained and bound separately.

These omissions do not invalidate the existing registered export contract. They do
limit its claims: it provides registered local archive integrity and recorded capture
behavior, not a provider-signed attestation, an account billing record or a complete
raw HTTP replay. A future adapter must state its actual retention contract instead
of filling absent metadata. It should not start saving credentials, arbitrary
headers or reasoning content to compensate for these limits.

## Why these deliveries cannot complete the current intake

Compare every selected delivery with each of N06, N07, N10 and N11: **24 bounded
identity checks, zero matches**. These four works contain the six current pending
Elara claims, whereas the selected B deliveries assess different authored scene
families and whole claims.

| Binding | Observed result across the 24 comparisons |
| --- | --- |
| Source origin and native work fingerprint | Different |
| Whole report fields and active unit IDs | Different; B uses Q1–Q6, current work uses Q001-style IDs |
| Declarations and work briefs | Different |
| Batch name | All use `batch-001`; this shared name carries no cross-work authority |
| Native binder with the original saved receipt | All refuse with `mixed_work_scope` |
| Current preparation contract | Explicit authored offline input; `provider_request=false`, `model_input=false` |

The four current preparation bundles are authored inputs, and their completion
bundles explicitly say `authored_fixture` and `model_evidence=false`. They are not
saved provider requests or model deliveries. This finding is bounded to these
selected captures and target works; it is not an exhaustive assertion that no other
usable saved delivery exists anywhere in the repository.

Do not rename units, rewrite a work fingerprint, synthesize a provider request or
replace the original receipt to make an old response attach. That would change the
claimed provenance rather than recover a missing link.

### Keep digest namespaces separate

The records reuse the field name `request_sha256` for different purposes:

| Identity | Meaning in these records |
| --- | --- |
| Frozen request fingerprint | Canonical hash of the complete frozen request record; binds native scope and delivery receipt |
| Generation-body fingerprint | Canonical hash of the actual logical Responses body; appears in the generation dispatch and provider metadata |
| Count-body fingerprint | Canonical hash of the input-count body; appears in the count dispatch |
| Raw-final fingerprint | Hash of exact final-text UTF-8 bytes |
| Current authored input fingerprint | Hash of the new offline input document's exact bytes; not a provider request |

Using either body hash in place of the frozen request fingerprint, while retaining
the actual saved receipt, is refused by the native binder with `wrong_request_receipt`.
The audit checks both substitutions for all six deliveries: **twelve refusals**.
Future manifests must name and link these identities explicitly rather than equating
same-shaped SHA-256 strings.

## Verification

**369 applicable existing regression tests pass**, with the 56 existing Pydantic
warnings from deliberate mutation fixtures. Ruff, formatting and strict mypy pass
for **251 files**: 250 repository Python files plus the private audit helper. No
frontend/build check is applicable to this documentation and local-audit change.

The actual audit blocks socket, HTTP and SQLite access. All six original deliveries
replay, all 24 target attachments are refused and all twelve hash-namespace
substitutions are refused. It rechecks the 636 source members' hashes and modification
times and preserves **821 members** under the earlier native-export, B/H-audit and
authored-publisher seals. The selected export JSON remains byte-equivalent to the
current authenticated export. Ordinary-review source pins and preceding implementation
files are also retained.
No source, request, response, terminal record, usage, gold, model prompt, provider
profile or exporter eligibility is changed. No application code or tracked test is
changed by this audit.

Private evidence is retained under
`data/diagnostics/assessment-delivery-admission-2026-11-12/`:

- [Fixed selection](../../data/diagnostics/assessment-delivery-admission-2026-11-12/plan.json).
- [Admission summary](../../data/diagnostics/assessment-delivery-admission-2026-11-12/summary.json).
- [24 target comparisons](../../data/diagnostics/assessment-delivery-admission-2026-11-12/target-comparisons.json).
- [Twelve hash-namespace refusals](../../data/diagnostics/assessment-delivery-admission-2026-11-12/hash-namespace-checks.json).
- [Pinned capture-retention audit](../../data/diagnostics/assessment-delivery-admission-2026-11-12/capture-retention-audit.json).
- [Verification](../../data/diagnostics/assessment-delivery-admission-2026-11-12/verification.json).

Each per-delivery JSON record points to its exact saved native export and records
request/work/body/final fingerprints, terminal metadata, usage and admission outcome.
Full original prose and model finals stay in the existing private exports.

## Readiness and recommended next step

| Capability | Readiness |
| --- | --- |
| Existing registered native B archive export | Already implemented and verified; reuse it |
| Attach these six deliveries to current intake | Not qualified; zero matching bindings |
| Broader intake-linked authenticated-delivery adapter | Not ready to implement/qualify from this selection alone |
| Bounded local request/terminal contract design | Ready; the audit identifies the missing boundary |
| Another live comparison | Not proposed or frozen here |

Next, design a **prospective intake-bound request manifest and terminal receipt**
locally. Before dispatch, it must fix the authenticated intake/source pins, unchanged
work/declarations/briefs, batch/units, exact assessment presentation, provider settings
and separate count/generation body hashes. The terminal record must bind that frozen
manifest to dispatch evidence, raw final, outcome and known/unknown usage without
accepting caller approval or promoting missing/incomplete delivery to success.

Keep safe retained response metadata and its own digest explicit. Any provider IDs
available in a future capture should be recorded under a declared safe contract;
missing IDs stay missing. Reuse current native binding/completion and the existing
registered exporter where applicable. Do not create a duplicate archive-only adapter.

Verify the proposed contract locally with authored success, refusal, length,
non-200, interrupted-delivery, unknown-usage and mismatched-source/body fixtures.
Existing tests cover several such software refusals, but this six-delivery selection
contains **no real failed/partial/unknown-token delivery**. It cannot qualify those
branches by observation. Only after this design is checked should implementation
or a separately approved frozen inference plan be considered.

Delivery authentication remains distinct from whole-claim truth, evidence adequacy,
editorial effect and necessary revision. Natural-negative, fresh-family and human
story-quality gaps remain. No writer permission or new human checkpoint is introduced.

CW-007/CW-013 remain open; CW-014 unqualified. Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.
