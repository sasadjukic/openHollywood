# Source-bound completion envelope and read-only publisher design

Date: 2026-11-12. Status: bounded local design COMPLETE; application publisher
implementation **NOT STARTED**. Production prompts unchanged; live calls **PAUSED**;
canary **ON HOLD**.

The existing components can derive a source-bound, mechanically complete envelope
for all six rehearsed claims while retaining their full intake. The proposed first
implementation accepts authored responses over registered probe sources only. It
does not authenticate new model deliveries or qualify semantic judgments.

## Scope and evidence

Reuse exactly the [previous rehearsal](assessment-completion-rehearsal-2026-11-12.md)
selection and authored baseline responses. No new admission, gold judgment,
repartitioning or semantic recovery is claimed.

| Review | Active units | Report fields | Holds | Unselected |
| --- | --- | ---: | ---: | ---: |
| N06 | Q001 / P07 | 12 | 1 | 10 |
| N07 | Q004 / P08; Q005 / U01 | 12 | 0 | 10 |
| N10 | Q003 / P12; Q007 / U02 | 14 | 2 | 10 |
| N11 | Q003 / P13 | 13 | 1 | 11 |
| Total | 6 in 4 unchanged works | 51 | 4 | 41 |

All complete messages, prose, reports, provenance, declarations and briefs remain
present. Source review ID, work fingerprint, batch ID and unit ID are separate
identity layers: Q003 in N10 and N11 does not identify the same claim.

The source check re-collects both original intake bundles through the registered
probe adapter. Their seven recorded review IDs are needed to verify the complete
collection hashes; only the four selected works and six existing units enter the
completion checks. Historical Python programs are neither imported nor executed.

## Trust boundary and submission

[Proposed ADR 0049](../adr/0049-source-bound-assessment-completion-publication.md)
records the decisions. The [JSON schema](../contracts/assessment-completion-submission-design-1.schema.json)
specifies the proposed authored submission shape; it is documentation, not a runtime
API or a standalone source verifier.

| Layer | Accepted input | What the application must establish |
| --- | --- | --- |
| Original review | Explicit local source locator and saved intake bundle | Registered source closure and lineage; current collector result equals original source; saved plan recompiles to the exact intake |
| Submission | Required authored origin/author, exact source pins, one raw response per existing batch | Strict JSON, no duplicate keys/extra properties, unchanged work/declarations/briefs, exact input digest and batch coverage |
| Result | Native binder output, never caller-supplied approval | Raw response hash, exact active slots, valid evidence locations and native schema |
| Completion | Recomputed from bound receipts | All expected batches exactly once; complete delivery and complete binding |
| Publication | Application-derived envelope and manifest | Full retained intake, explicit unassessed semantics, false writer permission, secret-safe and unchanged source/output boundaries |

The source pin contains required `source_origin=diagnostic_probe`, review ID,
byte hashes of the saved intake and its manifest, source canonical hash, work
fingerprint and canonical hashes of declarations and briefs. Source/manifest paths
are locators supplied separately, not caller-selected trust roots. The registered
adapter must independently verify them. Neither a manifest with self-consistent
hashes nor an object named `VerifiedSource` is authentication.

The submission contains only `contract`, `origin=authored_fixture`, `authored_by`,
`source` and `attempts`. Each attempt contains a unique fixture ID, original batch
ID, exact offline input byte hash and raw final text. No receipts, usage, completion,
semantic approval or writer-dispatch fields are accepted from the submitter.

The offline input includes the entire unchanged work, declarations, briefs, active
batch, schema and source pin. It explicitly is **not a provider request or model
input**. Its digest occupies the existing receipt's request-binding slot solely in
this authored branch. Native `model_assessment` and receipt fields remain synthetic
test data, prominently labeled at the enclosing boundary and in rendered views.

Future authenticated model delivery needs its own qualified request/terminal
adapter; the authored submission cannot activate it by changing a label. Actual
delivery must bind exact wire inputs, terminal outcome, raw response and known or
unknown usage. This design does not authorize another inference run. Likewise,
production SQLite sources remain outside this publisher's first qualification,
although the current intake already supports them.

## Derivation and publication

1. Read bounded strict UTF-8 input, resolve allowed source paths, authenticate the
   original archive through the registered collector and verify the saved intake
   bundle's members, collection hash and plan hash. Recompile the original intake;
   require full equality, including dispositions. Refuse sources with no pending work.
2. Require exact source pins and original batch coverage. Regenerate each full
   offline input document and verify its byte hash. Validate each unchanged raw final
   with the existing native binder using an internally constructed fixture receipt.
3. Recompute completion from the bound receipts. Complete delivery without complete
   binding is insufficient. Missing, duplicate, stale, malformed, extra or failed
   results cannot produce a completed publication; do not salvage a subset or retry.
4. Derive the envelope, render it literally and check all output for secrets before
   writes. Re-collect original sources and compare after rendering and again before
   the final manifest. Refuse observed drift; never rewrite source artifacts.
5. Write a new destination exclusively, with manifest last. Exact repeated publication
   verifies all expected bytes and reuses them without writes. Refuse partial, changed
   or extra files. Do not silently clean up a partial destination.

The complete envelope embeds the unchanged original intake, source-adapter receipt,
authored submission, raw/bound results and native completion. The original intake's
assessment/completion fields remain null; derived results live alongside it. The
application derives all status flags; it does not copy approval from a submission.

| Proposed file | Contents |
| --- | --- |
| `intake.json` | Exact original intake bytes |
| `submission.json` | Canonical authored submission with exact raw-final strings |
| `source-receipt.json` | Adapter-derived verification evidence and source locators; not a model-delivery receipt |
| `envelope.json` | Full derived envelope and explicit nonqualification |
| `view.md` | Literal complete envelope with authored notice and safe code fence |
| `manifest.json` | Hashes of the other five files, source pins, canonical envelope hash, implementation identity and publication state; written last |

Use distinct `_bytes_sha256` and `_canonical_sha256` names. Byte digests include
UTF-8 whitespace; canonical digests use the existing canonical JSON function.
Do not regenerate original artifact versions or source IDs, or hash a file into
itself. The private design manifest hashes its five data files; the enclosing
design acceptance seal pins the two helper implementations. The future application
manifest must include its own implementation identity directly.

`publication_state=bound_unassessed` is the only successful state in this slice.
Evidence adequacy, factual support, semantic interpretation, editorial effect,
edit necessity and craft remain unassessed; writer permission is always false.
Definite labels with valid but inadequate citations may bind. Scope is not a
citation whitelist. N11's eleven-location scope retains the existing eight-ref
response ceiling; the unchanged baseline explicitly supplies five references.

Usage is `not_applicable_no_inference`. Receipt token fields are null and zero
elapsed time is synthetic. Native known-token totals of zero and unknown-usage
counters are bookkeeping for fixture inputs, not observed provider usage or cost.

## Bounds and implementation acceptance gates

The first application slice is one original work per invocation, at most twelve
active units and twelve original batches, exactly one attempt per batch, no retries.
Keep existing stricter native limits, including eight evidence refs per response
unit and the 1,200-character reason limit. Raw final text is at most 64,000 Unicode
characters / 256,000 UTF-8 bytes. Proposed publisher-owned limits: 4 MiB submission,
16 MiB individual intake/offline input, 64 MiB complete output. Registered archive
collection retains its existing independent bounds; these are not overrides.

Measured original intake sizes are 2,148,086–3,594,790 bytes; generated offline inputs
are 1,096,471–1,819,571 bytes. The four complete preview bundles range from
6,480,131 to 10,824,946 bytes, including their manifests. Full context fits without
truncation or a citation-limit increase. Implementation must check the entire output
including the final manifest before any write.

Before calling the application publisher implemented, require tracked tests for:

- Recollection under existing registered source contracts; no caller trust pins;
  source/plan/intake/request/response drift refusal and whole-work completion.
- Strict parsing, byte/character bounds, secret checks before writes, literal
  Markdown escaping and explicit authored status in both machine and human views.
- Disjoint output/source/preparation/external-parent/input paths; reject symlinks,
  junctions, traversal and an output ancestor of a protected path.
- Exclusive creation, manifest-last failure handling, same-byte/mtime reuse and
  refusal of partial, extra or changed output. Inject drift during rendering and
  before manifest creation. Do not claim an atomic transaction across source trees.
- No database writes, provider imports/calls, workflow dispatch or writer permission;
  the same six-claim replay must keep all holds and unselected fields unchanged.

These filesystem and race-handling requirements are **design obligations, not a
qualified implementation**. The private prototype only derives buffers; its helper
saves local previews. It is not a general CLI, route or application publisher.

## Verification

Four real-source, authored-response previews bind all six selected units and retain
all 51 report fields, four holds and 41 unselected fields. All 24 preview files
verify byte/mtime-exact reuse. A separate two-batch authored toy checks full-batch
coverage; it is not a seventh admission or model observation.

The design checks refuse **29 mutated submissions/source bindings**, including
caller authority/usage, future model origin, missing discriminators, stale source
pins, cross-work substitution, stale input, duplicate/missing/unknown batches,
malformed/missing claims, unchecked origin mutation, byte drift, partial two-batch
completion and duplicate fixture identities. Six additional parser checks refuse
duplicate top-level/nested keys, invalid UTF-8, oversized submission/raw final and
caller-supplied receipts. Valid controls pass through the same JSON parser.

**268 applicable existing tests pass**, including the 25 completion rehearsal tests.
There are 56 existing warnings from deliberate Pydantic mutation fixtures. Ruff,
formatting and strict mypy pass for **246 files**: 244 repository Python files and
two private design helpers. Initial pytest temporary-directory access failed;
rerunning with a fresh workspace temporary directory passed. An initial sketch
used Python-mode strict tuple validation for JSON lists; the corrected parser checks
duplicate keys first and then uses JSON-mode validation. Valid controls and every
mutation were rechecked. No runtime code was changed to accommodate the design.

The schema is generated and checked through Pydantic and native component
validation; no separate JSON Schema validator was installed or claimed. The real
source rehearsal blocks HTTP, socket and SQLite access. Earlier private seals and
1,166 original source pins remain intact. Production code, tests, registered
exporter eligibility, dependencies and all fourteen issue bodies remain unchanged.

Private evidence, intentionally outside Git:

- [Executable design sketch](../../data/diagnostics/assessment-completion-design-2026-11-12/prototype.py)
- [Source/composition verifier](../../data/diagnostics/assessment-completion-design-2026-11-12/verify_design.py)
- [Acceptance and exact size counts](../../data/diagnostics/assessment-completion-design-2026-11-12/acceptance.json)
- [Final verification](../../data/diagnostics/assessment-completion-design-2026-11-12/verification.json)
- [Design acceptance seal](../../data/diagnostics/assessment-completion-design-2026-11-12/acceptance-seal.json)

## Recommended next step

Implement the small **authored-fixture / registered-probe completion publisher**
as a tracked read-only application service and operator command, with the pure
envelope contract and acceptance checks above. Replay these same four works and
six claims, then verify exact output reuse and source preservation. Do not widen
the native B archive exporter or add model delivery, SQLite completion publication
or production workflow routing in that slice.

After that boundary is qualified, design a separate adapter for authenticated saved
assessment deliveries. Only then assess whether another bounded inference experiment
would answer a materially new question. No live plan or budget is frozen now.

This improves inspectability and provenance in the application; it does not show
that a model has become a better critic or writer. Authored unsupported labels are
not natural negative controls, and these related Elara samples do not establish
fresh-family generalization. Necessary editing and human judgments of feel, flow,
character and story-breaking effects still need separate evidence.

Tracker and issue index updated. CW-007/CW-013 remain open; CW-014 unqualified.
Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.
