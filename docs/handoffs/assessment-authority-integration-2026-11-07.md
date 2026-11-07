# Read-only historical authority and evidence obligations

Date: 2026-11-07. Implementation complete; verification is recorded below.
**Live calls PAUSED; full workflow canary ON HOLD.**

The tracked assessment component now checks historical quotation bindings and
shows an explicit evidence obligation for each authored material claim component.
It keeps historical assertions, historical excerpts, earlier assignment authority,
current assignment authority and requested repairs distinct. The integration is
read-only: it does not generate model input, change production behavior, grade
semantic truth or authorize a writer.

This implements the first recommended step from the
[historical authority/materiality audit](reviewer-historical-authority-audit-2026-11-07.md).
The [new component](../../engine/open_hollywood_engine/evaluations/assessment_authority.py)
consumes the existing work, active scope, declarations and work-brief contracts.
[ADR 0045](../adr/0045-read-only-assessment-authority-and-obligations.md) records
the contract and its limits.

## What changed

- **Separate source roles.** The scope vocabulary now represents historical
  attribution, event/violation and requested repair. Historical violation needs
  historical excerpt and historical assignment roles. A requested repair cannot
  fill an assignment obligation solely by occupying the same evidence slot.
  These are checks on authored declarations, not automatic source classification.
- **Claim-specific obligations.** Each obligation binds to an existing selected
  unit and material-component index in the exact scope declaration. It carries
  predicates, required source roles and illustrative references. Missing
  components remain findings; invented or duplicate indices are rejected.
  Predicate/role mismatches stay visible. Citation examples are not a whitelist.
- **Recomputed copying.** Historical bindings join a registry section to an old
  document version, JSON-text hash, field pointer/hash, Unicode offsets and exact
  text. Repeated text uses explicit offsets. Changed proof is rejected; an absent
  body remains unverified. A successful binding means the text matches the supplied
  body, not that the critic's interpretation or requested edit is justified.
- **Separate visibility and proof.** Old bodies remain outside the unchanged work
  and recorded messages. Excerpt/full-body visibility are separate request-bound
  adapter declarations. The preview does not claim to authenticate an archive,
  verify model visibility or infer chronology from opaque version identifiers.
  The adapter remains responsible for those facts and the original critique link.
- **Complete read-only preview.** The renderer retains the full work, original
  fields and selections, scope/brief findings, proof bodies and computed bindings
  inside literal dynamic fences. It revalidates any optional native result.
  Historical quote-witness captures are not converted into native receipts.

Existing renderers, result schema, completion accounting and callers are unchanged.
The scope extension adds vocabulary without changing serialized defaults or the
meaning of earlier roles. No production prompt, profile, graph, gate, provider
adapter, exporter eligibility, API/client schema, persistence or dependency changed.
There is no new human checkpoint.

## Saved-capture integration

The local bridge authenticates all **595 members** of the preceding audit seal
and reads the frozen cases, works, requests and verified historical source chains
as data. It imports no historical inference harness. The original analysis,
failure/recovery pairs, requests, gold and receipts remain unchanged:
**U 52/64; B 63/64 grounded**, eleven recoveries, zero regressions; B's original
qualification gate still failed.

All **32 saved works** render with their exact full context and message/request
bindings intact. The local preview authors only these five unique whole fields:

| Field | Local declaration and evidence obligations | Result of structural checks |
| --- | --- | --- |
| R1 Q003 | Historical crossing/violation, current obligation, current outside ending | All eight repetitions remain pending: the historical event/violation versus reported-target reading and earlier assignment authority are unresolved. |
| R3 Q002 | Assigned realization, both current dates, depicted realization | Eight structurally consistent declarations; realization remains material. |
| R3 Q003 | Historical date-claim attribution, both current dates, required date relation | Eight structurally consistent prospective declarations; no extra realization predicate. |
| R3 Q004 | Card discovery, ten-year realization, purposeful journal decision | Eight structurally consistent declarations; realization remains material. |
| R4 Q003 | Historical unresolved-choice attribution, current purposeful action, required decision | Eight structurally consistent declarations. |

Thus **40 authored repeated units** produce **32 structurally consistent and
eight unresolved findings**. The other **88 active units** remain visibly
undeclared in this bounded bridge. They were not dropped or silently interpreted.
These are declaration findings, not new model success/failure counts.

All **40 repeated historical bindings**, covering the same **five unique
quotations**, match the supplied old bodies. Historical bodies and their local
proof never enter the original work/messages or become retroactive model citations.
The new serialized local body hash binds its exact supplied JSON representation;
the bridge separately checks the recovered content against the preceding audit's
canonical source fingerprint.

The frozen B brief text is retained for the selected fields. Its presence beside
a U capture is explicitly a local preview, not a claim that U saw that brief.
R3 Q003's new obligation packet is a **prospective authored interpretation**. The
old realization-based gold and B's final citation failure are retained, without
rescore. Q002/Q004 still require realization; the story assignment is unchanged.

Private evidence: [index](../../data/diagnostics/assessment-authority-integration-2026-11-07/README.md),
[all preview findings](../../data/diagnostics/assessment-authority-integration-2026-11-07/integration.json),
[R1 unresolved preview](../../data/diagnostics/assessment-authority-integration-2026-11-07/views/OB-1-R1-B-PC.md),
[R3 final B preview](../../data/diagnostics/assessment-authority-integration-2026-11-07/views/OB-2-R3-B-CP.md),
[R4 recovery preview](../../data/diagnostics/assessment-authority-integration-2026-11-07/views/OB-1-R4-B-PC.md).
Full unpublished prose remains in ignored local data.

## Verification and limits

The full Python suite passes **1,454 tests**, including **37 new tracked tests**.
The separate saved-capture integration suite passes **37 tests**: **1,491 distinct
passing tests**, with nothing deselected. Repository Ruff, formatting and strict
mypy pass for **230 Python files**; the same checks pass for all **three private
helpers**. All eight recorded checks pass, with root Python fingerprints unchanged
during verification. The 56 full-suite warnings are expected Pydantic serializer
warnings from deliberately unchecked fixtures (22 existing and 34 in the new tests).

New component/private tests deny HTTP, socket, database and secret-store access.
Verification subprocesses receive no provider credentials. Full-suite persistence
tests use their existing isolated test databases. The first full-suite attempt
stalled at Windows sandbox async startup and was stopped; its partial log is
retained. The authorized local run outside that sandbox passed in **268.53s**.
No inference, catalog, input-count or daemon calls were made. Frontend/build checks
are inapplicable: no frontend, generated API contract or dependency changed.

Checks use the uv-managed environment through `.venv/Scripts/python.exe -X utf8
-m`, equivalent to the README Python commands. See the
[repository verification](../../data/diagnostics/assessment-authority-integration-2026-11-07/verification.json)
and [private verification](../../data/diagnostics/assessment-authority-integration-2026-11-07/private-verification.json).

The new tracked tests cover exact source copying, Unicode/repeated text and
escaped/list pointers; altered hashes/versions/offsets; missing bodies and
visibility; missing/duplicate/foreign/inactive obligations; requested repair
versus assignment; stale work/request/declarations; literal full-context rendering;
and optional native results with unchanged completion/unknown-usage behavior.
The private tests replay the actual five-claim mapping and deliberately remove
realization evidence from Q002, substitute the repair request for Q003's assignment,
or remove old bodies and declarations.

A deliberately incorrect free-text requirement can still be structurally
consistent. The component reports semantic interpretation, evidence adequacy,
factual support, obligation existence, fulfillment, edit necessity and craft as
unassessed. Its hashes do not authenticate invented external data. No automated
brief author, semantic classifier, gold generator or source-truth oracle is claimed.
Completion and exact copying grant no whole-relation credit or writer permission.

## Recommended next step

Do a bounded local admission pass before preparing more inference. Inspect up to
**12 saved ordinary-review captures**, retaining exact whole claims and source
lineage, and try to assemble **three small packets** with both valid and invalid
authority inferences. Include the known control plus fresh scene families if
available. Explicitly distinguish supported, unsupported and unavailable/uncertain
claims; merely collecting more supported examples will not test false criticism.

The admission should establish whether each packet can separate authentic copying
from alleged events, requested repair from actual obligation, and a date relation
from a realization claim. Preserve unresolved whole-field readings rather than
quietly narrowing them. If natural negative examples or fresh families are not
available, report that gap. Clearly labeled authored controls can test a mechanism,
but cannot be presented as natural-error precision evidence.

If those local checks justify inference, prepare the proposed **24-attempt
Sol-high B/H comparison**: three packets × two conditions × two orders × two
exact repeats. B retains the explicit work brief; H adds the provenance/visibility
receipt, with equal claims, full context, prospective gold and workload. The
hypothesis is improved authority discrimination without converting allegations
into events, repair requests into assignments or copying into semantic approval.
Freeze requests, budget, scoring and stops and obtain approval before either
story-bearing endpoint. **No next experiment is frozen or approved by this change.**

This supports better factual assessment without treating a missing citation or
an oversized rubric as a reason to rewrite a story. It does not yet demonstrate
necessary editing, prose preservation or improved craft. Human quality review
should continue to focus on feel, flow, character and story-breaking details,
with mechanical checks supplied by the application.

CW-007/CW-013 remain open; CW-014 remains unqualified. All fourteen issue bodies
and posted URLs remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**
