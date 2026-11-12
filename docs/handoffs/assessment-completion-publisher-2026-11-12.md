# Read-only authored completion publisher

Date: 2026-11-12. Status: narrow implementation and local qualification **COMPLETE**.
Production prompts unchanged; live calls **PAUSED**; canary **ON HOLD**.

The application now connects authenticated probe intake to an inspectable authored
completion. It preserves the original review and scope, recomputes native result
binding and completion, and publishes a new immutable output directory. It reads
source archives without changing them. These authored responses are not model
deliveries, semantic gold, quality improvements or permission to edit.

## Implemented boundary

| Component | Responsibility |
| --- | --- |
| `engine/open_hollywood_engine/evaluations/assessment_completion.py` | Strict authored submission, exact source/input binding, native result/completion composition and literal full-envelope rendering |
| `apps/api/open_hollywood_api/services/assessment_completion.py` | Registered source recollection, saved intake verification, secret checks, protected paths, publication and reuse |
| `scripts/assessment_completion.py` | Offline `prepare` and `publish` commands; summary-only status and redacted errors |
| [Submission schema](../contracts/assessment-authored-submission-1.schema.json) | Generated shape specification; application authentication remains separate |

[ADR 0049](../adr/0049-source-bound-assessment-completion-publication.md) is accepted
for this narrow slice. The [original design](assessment-completion-design-2026-11-12.md)
and private previews are retained. The application uses explicit new contracts;
historical `*-design-1` submissions are not silently promoted or rewritten.

The service takes input/output paths, not a caller-supplied envelope, source trust
pin override, delivery receipt or completion flag. It selects the registered archive
contract, verifies its existing closure and parent lineage through the current
collector, verifies the entire saved intake bundle and recompiles the selected
review's plan. A self-consistent intake manifest cannot authenticate a forged source.

Exactly one original pending work is published at a time. Whole claims, source
versions, declarations, briefs and batch membership remain unchanged. Every expected
batch must appear exactly once. Raw responses are checked against the regenerated
full offline input hash, then processed through the existing native binder and
completion function. Both complete delivery and complete binding are required.

The full envelope retains the original pending intake, including null original
assessment/completion fields, and stores derived results alongside it. Holds and
unselected fields remain visible. Unit IDs stay local to their original work.
Source authentication is distinct from the new assessment's authored origin.

Native receipt and `model_assessment` fields contain synthetic fixture inputs only.
Token fields remain null, active time is synthetic zero and usage is explicitly
`not_applicable_no_inference`. Native unknown-usage counters are not measured
provider usage. All factual support, evidence adequacy, semantic interpretation,
editorial effect, edit necessity and craft remain unassessed by the software;
writer permission remains false.

## Operator use

The [README command guide](../../README.md#read-only-authored-assessment-completion)
documents both commands. `prepare` exports exact full-context `input-NN.json` files,
an incomplete `submission.template.json` and a preparation manifest. Empty author
and raw-response fields deliberately fail submission validation. Copy the template
outside the immutable preparation directory, supply the local author and authored
responses, and retain all source/input pins and batch identities.

`publish` writes exactly six files: original `intake.json`, canonical `submission.json`,
`source-receipt.json`, `envelope.json`, literal `view.md` and `manifest.json`.
The manifest hashes the other five files, source binding, canonical envelope and
domain/application implementations. Preparation has a separate `authored_inputs_only`
state; completed publication is `bound_unassessed`.

Both commands reject linked paths, path traversal and overlap with source,
preparation, external-parent archives and the intake bundle. Completion publication
also protects its submission file, including output ancestors that would contain it.
Secret checks run before writes, without redacting bound bytes. The adapter re-reads
original sources after rendering and before writing the manifest. Submission bytes
are also rechecked. It creates directories and files exclusively and writes the
manifest last. Exact repeats verify bytes and retain modification times.

Partial, extra or changed output is refused. Injected failure during writes leaves
a partial directory without a success manifest; it is not repaired, overwritten or
deleted automatically. This is a bounded local publication protocol, not an atomic
transaction across all source directories or a defense against every possible
concurrent filesystem actor. Consumers must require a valid manifest and its files.

Limits remain explicit: twelve active units and twelve batches per work, one response
per batch, no retries, 4 MiB submission/plan/manifest, 16 MiB individual intake/input,
64 MiB saved intake bundle and complete publication including manifest. Raw finals
retain the 64,000-character / 256,000-byte bound; native citation/reason limits are
unchanged. Existing registered source-archive bounds still apply independently.

## Verification and six-claim replay

**544 applicable tests pass: 72 new (32 domain, 40 application/CLI) and 472 existing.**
Ruff, formatting and strict mypy pass for **251 files**: 250 repository Python files
plus the private acceptance helper. The 56 existing Pydantic warnings come from
deliberate mutation fixtures. The initial sandboxed suite stalled at an existing
async saved-review test; it was stopped and the complete suite passed outside the
Windows sandbox using isolated temporary databases and fake gateways. The actual
six-claim replay kept network and SQLite calls blocked throughout.

No dependency, persistence migration, API/client contract, frontend or build change
was required. Frontend/build commands are not applicable to this offline Python slice.

The tracked command successfully prepared, published and reused all four source
works. Every original intake, selected whole claim, declaration, work brief and
authored raw response is unchanged:

| Review | Units | Fields | Holds | Unselected | Authored labels | Publication |
| --- | --- | ---: | ---: | ---: | --- | --- |
| N06 | Q001 / P07 | 12 | 1 | 10 | supported | Created, then exact reuse |
| N07 | Q004 / P08; Q005 / U01 | 12 | 0 | 10 | supported; uncertain | Created, then exact reuse |
| N10 | Q003 / P12; Q007 / U02 | 14 | 2 | 10 | supported; uncertain | Created, then exact reuse |
| N11 | Q003 / P13 | 13 | 1 | 11 | supported | Created, then exact reuse |

Totals: **six claims, 51 fields, four holds and 41 unselected fields**. All **24
publication files** reuse with identical bytes and modification times. Twelve
preparation files also remain unchanged during publication. The supported/uncertain
labels are the earlier authored examples, not new conclusions. N11 retains its
explicit five citations under the existing eight-reference response limit.

The original 1,166 source pins and all 1,516 members of the five preceding private
evidence sets remain unchanged. All 711 existing baseline files outside the five
authorized documentation updates remain unchanged. Pre-change copies preserve the
previous design's documentation hashes as ADR 0049 moves from proposed to accepted.
No existing domain/adapter/test, production prompt, model profile, graph or gate was
modified. The registered B archive exporter's eligibility remains unchanged.

The new regression tests cover original/retry/post and October 17 source formats,
external parents, multi-batch coverage, full-context retention, explicit authorship,
strict parsing, source/input drift, forbidden caller authority, malformed/incomplete
responses, literal rendering and semantic nonqualification. Filesystem tests cover
protected paths, simulated symlink/junction refusals, exclusive directory/file
conflicts, partial/changed/extra output, drift after rendering/before manifest,
submission drift, injected disk failure, resource limits and secret refusal both
at input and after rendering. Blank templates and no-pending-work intakes cannot
become completed assessments. CLI errors do not expose validation input or prose.

The same N06/N07/N10/N11 work items and six authored responses from the earlier
rehearsal are replayed through the actual tracked command. No historical Python
program is executed. The acceptance helper blocks socket, HTTP and SQLite access.
Its outputs remain private under
`data/diagnostics/assessment-completion-publisher-2026-11-12/`.

- [Command replay and inspection](../../data/diagnostics/assessment-completion-publisher-2026-11-12/acceptance.json).
- [Preservation checks](../../data/diagnostics/assessment-completion-publisher-2026-11-12/preservation.json).
- [Verification record](../../data/diagnostics/assessment-completion-publisher-2026-11-12/verification.json).
- [Acceptance seal](../../data/diagnostics/assessment-completion-publisher-2026-11-12/acceptance-seal.json).

## Recommended next step

Do a bounded **local provenance/admission audit of up to six saved assessment
deliveries** before implementing a model-delivery adapter. Check whether each has
exact saved request, source/work/scope/batch identity, raw response, terminal outcome
and honest usage sufficient for its declared contract. Record missing or mismatched
bindings explicitly; do not reconstruct a provider request or promote a fixture to
model evidence. Existing registered B exports retain their present eligibility.

Use that audit to specify the smallest authenticated-delivery adapter and its local
failure fixtures. These six authored completions do not establish that any model
saw the new offline inputs. If usable matching deliveries are absent, define the
necessary request/terminal contract before proposing a separately approved bounded
live plan. No inference budget is frozen or spent here.

Saved SQLite completion publication and workflow/writer routing remain deferred.
This step improves application provenance and inspection, not measured critic or
writer reliability. Natural-negative, fresh-family, necessary-edit and story-quality
gaps remain. Human feel, flow, character and story-breaking judgments remain separate
from mechanical completion.

CW-007/CW-013 remain open; CW-014 unqualified. Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.
