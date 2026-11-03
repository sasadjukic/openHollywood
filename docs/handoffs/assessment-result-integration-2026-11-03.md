# Read-only assessment result integration

Date: **2026-11-03**. **IMPLEMENTED AND VERIFIED LOCALLY.**
Live calls **PAUSED**, canary **ON HOLD**.

The verified scope design and literal evidence-location renderer are now tracked
in `engine/open_hollywood_engine/evaluations/assessment_result.py`, alongside the
unchanged assessment-work/completion component. The decision is recorded in
[ADR 0042](../adr/0042-active-assessment-results-and-evidence-locations.md).
This completes the first next step from the
[scope/citation audit](reviewer-scope-citation-audit-2026-11-03.md).

## Implemented behavior

- `scope_for_batch` binds the exact work, active batch and caller-authenticated
  request hash. `assessment_response_schema` exposes exactly one required slot
  per active unit, with no model-authored claim identity.
- An explicit versioned evidence registry verifies source identity/version,
  source and field hashes, field pointer, exact code-point offsets and field or
  paragraph location. It validates every registry entry, not just selected IDs.
- `bind_assessment_result` accepts only a successful, matching receipt and exact
  raw-final hash. It rejects missing/extra/duplicate slots, malformed data,
  identity drift and failed-final salvage. No citation or claim is repaired.
- Bound results retain the original raw text and delivery receipt. A separate
  derived receipt feeds the existing `complete_work` function. Missing batches
  and unknown usage remain visible; no retry or inference operation is introduced.
- `render_assessment_result` recomputes the binding and displays the full work and
  context, original claims, model judgments and exact cited source sections as
  literal JSON. Embedded Markdown and HTML remain data.

Application location binding remains separate from model-authored support.
Evidence adequacy, factual support, editorial necessity and craft remain
**unassessed**. Whole-relation credit and writer permission remain **false**.
Correctly located but wrong/incomplete evidence is deliberately retained as such;
this component cannot decide its semantic adequacy.

## Compatibility and limits

The original `assessment-work-1` contract and its completion behavior are unchanged.
The new explicit registry does not automatically accept historical private
registries or production v61 catalogs. Authenticated adapters must translate and
verify their own source contracts deliberately. This integration adds no production
caller, provider serialization, export CLI, persistence or public API surface.

The engine validates internal identity and consistency. A future adapter must
still prove source availability and model-visible presentation, authenticate the
actual wire and terminal facts, and use the existing credential guard before
export/persistence. Native provider support for the schema has not been tested.

Response bounds match the local prototype: up to twelve active units, eight
distinct references per unit, 1,200 characters per reason, 8,000 reason characters
total and 64,000 raw-final characters. Empty evidence is allowed only for uncertain
judgments. These are local response limits, not story-quality or prose-length gates.

## Verification

Verification results are recorded locally under
`data/diagnostics/assessment-result-integration-2026-11-03/`.
The authored regression suite is tracked at
`tests/evaluations/test_assessment_result.py`; unpublished captures stay private.

The tests cover exact active coverage; two requested versus seven returned;
claim identity supplied by the application; duplicate/malformed output; failed
deliveries; wrong work/request/raw-response identity; source version, pointer,
hash, paragraph and offset errors; Unicode and repeated occurrences; incomplete
compound evidence and private-flourish/plan-versus-event contrasts; literal
rendering; unchanged full context; and existing completion/unknown-usage behavior.
Real HTTP, socket/DNS and SQLite access are blocked in the new tests.

There are **85 new authored tests**, and **123 focused tests** pass including the
38 existing work/completion tests. A mutation regression reproduced and fixed a
mutable-alias edge case in caller-constructed scope records; returned results now
retain a separately validated scope snapshot. Synthetic schema/result/rendered
examples are saved beside the local verification records.

The final full repository Python suite passes **1,363 tests**, including all
85 new regressions. The 123 focused tests overlap the full suite and are not
additional tests. Repository-wide Ruff lint/format and strict mypy pass across
**224 Python files**. The final verification pins both new Python files and
confirms their hashes did not change during the checks.

The 422 preserved capture files and all 3,153 historical source fingerprints
remain unchanged. No past delivery, judgment, score, request or retired allowance
was revised. All fourteen original issue bodies and posted links are preserved.

The installed uv-managed environment ran the README Python checks through
`.venv/Scripts/python.exe -X utf8 -m`. An initial uv-cache permission failure and
sandbox collection stall required running the final suite outside the Windows
sandbox. A superseded full run was stopped for the scope-snapshot fix; interrupted
runs are not counted as passes. Fixture setup corrections, the reproduced alias
failure and final results are recorded in `verification-history.md` and
`verification-final.json` in the private bundle. Full-suite database operations
use temporary test databases, not the application database.

Repeat the applicable checks from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 -m ruff check apps/api apps/worker engine scripts tests migrations
.venv/Scripts/python.exe -X utf8 -m ruff format --check apps/api apps/worker engine scripts tests migrations
.venv/Scripts/python.exe -X utf8 -m mypy apps/api apps/worker engine scripts tests migrations
.venv/Scripts/python.exe -X utf8 -m pytest
```

No frontend, generated API contract or build configuration changed; frontend
lint/type-check/tests/build are not applicable to this engine-only integration.

## Next step

Prepare the previously proposed **16-call Luna MA/quote-witness diagnostic** for
approval, if inference is desired. Keep historical H1/W2 full-MA controls, add two
fresh scene families, and use both presentation orders: eight paired cases,
sixteen calls maximum. Change only the treatment's evidence selection to bounded
exact quotations resolved by the application. Verify the witness adapter and
renderer locally, then freeze exact cases, requests, scoring, resources and stops.

Do **not** combine this citation treatment with the newly tracked active-slot
schema or a smaller assessment workload. A DeepSeek active-scope test remains a
separate possible experiment. Provider schema support and semantic improvement
are not established by these local checks. No new live requests, budget or
approval are created here; retired allowances remain closed.

Production prompt **61**, graph **9**, fulfillment policy **1** and active profiles
remain unchanged. No story rewrite or story-quality claim is made. Step 19 remains
**IN PROGRESS**, Step 20 **NOT STARTED**, and all fourteen issues remain open.
