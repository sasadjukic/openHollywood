# Native assessment archive exporter — implementation and verification

Date: 2026-11-12. **Completed locally. Live calls PAUSED; canary ON HOLD.**

The tracked read-only exporter now supports the registered November 7 B assessment
archive. **All twelve B captures were exported, and every native Markdown view is
byte-for-byte identical to its previously audited view.** Full work, original
messages/requests, raw finals, saved delivery/usage and separate operator receipts
remain intact. The tracker and operator instructions are updated.

This closes the supported-export gap identified by the
[B/H audit](reviewer-bh-b-export-audit-2026-11-07.md). It does not activate assessment
in the production graph or qualify model judgments as story defects or edit permission.

## Delivered path

- [Application service](../../apps/api/open_hollywood_api/services/assessment_archive_export.py)
  authenticates the archive, reconstructs native assessments and publishes bounded
  local exports using the unchanged domain contracts and authority renderer.
- [Operator CLI](../../scripts/assessment_archive_export.py) takes an archive path,
  one to twelve distinct explicit B trial IDs and an output destination. Errors
  are sanitized; prose and credentials are never printed as error details.
- [Tracked regression tests](../../tests/api/test_assessment_archive_export.py)
  use a [small authored archive](../../tests/assessment_archive_fixtures.py), with
  no dependency on private story material or provider availability.
- [ADR 0046](../adr/0046-read-only-native-assessment-archive-export.md) records the
  archive trust boundary, separate provenance and read-only limits. The root
  [README](../../README.md) includes the supported command.

The CLI uses the immutable `captures/` snapshot preserved by the prior audit.
It authenticates **636 original members** against the registered results seal
`f21a1a62a28c8e193bbf08fa849930f95ff954a0c858ebc934123e90b3515bde`
and approved plan
`53638172ce2ead7f42810934478ce59dac69630eacea0d73f8d6775691d60d90`.
It does not compare old public-document hashes with today's updated checkout.
The snapshot can be relocated while retaining its internal structure. Historical
programs remain inert bytes; no archived helper is imported or executed.

Only this registered native B contract is supported. No caller-supplied trust seal
is accepted through the CLI. Ordinary-review database lineage and the October 16
probe-export contract remain unchanged; neither is used to manufacture production
provenance for these assessments.

## What the export verifies and preserves

The service checks the exact frozen request/work identity, complete structured
message sections, actual count/generation dispatch hashes and endpoints, successful
delivery envelopes, actual response text, native result binding and complete work
coverage. It reconciles saved usage with delivery and response evidence. Failed
or incomplete deliveries are not promoted to valid exports. Consistently unknown
usage stays explicitly unknown; no cost or token count is invented.

The original authored declarations, briefs and authority are validated against
their original work before rebinding operator-side identities to the actual B
request. Original and derived auxiliary records remain separately inspectable.
Source bodies, semantic requirements and all historical inputs/results are unchanged.

Each capture has three files: complete JSON, native literal Markdown and an
operator-receipt JSON. The receipt was absent from B model input and adds no
historical model evidence. The index and manifest bind the selection order, archive
contract, source hashes, current implementation and output hashes. Gold and semantic
inspection annotations are excluded from exported assessment content.

All scope findings remain visible. A missing obligation or historical body produces
an explicit hold/finding rather than an invented repair. A wrong free-text obligation
may remain structurally consistent but explicitly semantically unverified. Copying
and citation binding still do not prove adequate evidence, whole-claim support,
edit necessity or craft. Domain authentication/visibility flags are not silently
flipped by the separate adapter audit. Writer permission is always false.

Before publication the service recomputes the export from authenticated sources,
rechecks source bytes after rendering and applies the existing secret guard.
Archive reads and output size are bounded; unsafe/linked paths are rejected.
New output is written exclusively with the manifest last. Exact repeats verify
and reuse every file without writes; partial, changed or extra output is refused.
An interrupted publication remains incomplete and cannot masquerade as a finished
bundle. No existing file is overwritten to repair it.

## Verification results

| Check | Observed result |
| --- | --- |
| Registered source closure | All 636 members authenticated. |
| Prior audit evidence | All 716 private audit members unchanged. |
| Selected captures | All twelve B captures, covering every family/order/repeat. |
| Native views | 12/12 byte-identical to the previously audited Markdown. |
| Original data | 12/12 full works, requests, raw finals and saved receipts unchanged. |
| Native coverage | 72 delivered units and 24 historical-copy bindings retained. |
| Operator receipts | 12/12 match the frozen case receipts; absent from B model input. |
| Publication | 38 files: twelve JSON/Markdown/receipt groups, index and manifest. |
| Repeat invocation | Exact reuse; all output modification times unchanged. |
| Inference and database | Network/database operations blocked during acceptance; zero live calls. |

**326 tests passed:** 58 new archive-export tests, 214 existing assessment tests
and 54 existing ordinary/probe exporter tests. They cover drift, incompatible seals,
request/source/copy/usage mismatches, failed/refused delivery, unknown usage, scope
holds, semantic limits, gold exclusion, linked/traversing paths, archive/output
bounds, changes during rendering, conflicting output, safe CLI errors and secret
checks before publication. The 56 Pydantic warnings originate in existing deliberate
mutation fixtures; no test failed in the final run.

Repository Ruff, formatting and strict mypy passed for **234 tracked Python files**;
the private acceptance helper passed the same checks, 235 files in the recorded
commands. No frontend, HTTP API schema, migration, dependency or packaging changes
were made, so frontend/build checks were not applicable. The existing ordinary/probe
exporters and all five assessment domain modules are unchanged.

Private artifacts:

- [Acceptance index](../../data/diagnostics/native-assessment-export-2026-11-12/README.md)
- [Export index](../../data/diagnostics/native-assessment-export-2026-11-12/export/index.md)
- [Export manifest](../../data/diagnostics/native-assessment-export-2026-11-12/export/manifest.json)
- [Exact CLI arguments](../../data/diagnostics/native-assessment-export-2026-11-12/cli-arguments.json)
- [Verification record](../../data/diagnostics/native-assessment-export-2026-11-12/verification.json)

Full unpublished prose and raw captures remain in ignored local data. The new
tracked tests contain authored test material only. This is software and retention
verification, not new model inference, independent human adjudication or rescoring.
The historical B 72/72 / H 72/72 ceiling tie is unchanged.

## Recommended next step

Do a **bounded local intake and admission check for harder ordinary-review claims**,
using the existing saved-review/probe exports and full version-specific sources.
Inspect up to twelve previously unadmitted saved reviews if available; do not
relabel the same authored ceiling controls as natural negative evidence.

For each candidate, record the exact whole claim, factual versus editorial scope,
actual assignment authority, required evidence and source availability. Admit
supported, contradicted or uncertain gold only when the whole-claim interpretation
is defensible; retain ambiguous claims as explicit holds. Check that the full work,
scope/brief declarations and operator provenance can enter the existing read-only
component without adding a hidden premise or changing what the original critic saw.

If no harder controls qualify, record the missing evidence instead of repeating
the ceiling comparison. Only after local admission should we propose another
bounded diagnostic. **No new live experiment or budget is frozen here.**

This moves toward reliable production assessment while keeping editorial judgments
separate. Human review remains about feel, flow, character and story-breaking
details. Successful factual assessment cannot by itself establish necessary edits,
writer preservation or better story quality.

Production prompts/profiles/graph/gates and the Blueprint checkpoint are unchanged.
No provider, catalog, input-count or daemon call occurred; no application database
was opened. All fourteen issue bodies and posted URLs remain unchanged. CW-007 and
CW-013 remain open; CW-014 remains unqualified. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; full workflow canary ON HOLD.**
