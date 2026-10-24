# Extra-field audit and unsupported-explanation fixtures

Date: **2026-10-24**. **COMPLETE LOCALLY: zero inference and zero daemon discovery.**
Production remains **prompt 61 / graph 9 / fulfillment policy 1**, live calls are
**PAUSED**, and the full workflow canary remains **ON HOLD**.

This follows the [C2/D1/D2 results](../benchmark_reports/reviewer-layout-v61-results-2026-10-23.md).
The extra fields originate in the captured provider response, not in the frozen
input or the application's evidence binding. The local validator already rejects
them correctly. The audit does not identify the model's internal reason for
generating them and supplies no accepted repair or candidate promotion.

## What the delivery audit establishes

The exact failed cell is **L-A00-D2-OR**. Its raw response contains two additional
members: `craft.voice.effect_note` and `craft.naturalness.effect_note`, both empty
strings. The displayed schema permits exactly `effect`, `assessment` and
`evidence` in each craft object, requires all three, and sets
`additionalProperties=false`. The final contract already says to return exactly
that schema. The request uses prompt-level schema instructions, without a
provider-enforced response schema.

The audit replays all **48 current captures**, preserving **40 valid / 8 invalid**
and the existing receipts and decisions. It checks the exact archived requests
against wire requests and finds **no `effect_note` in any of the 48 requests or
wire payloads**, or in the **48 pinned input/runtime source files**. Historical
analysis files that discuss the defect are separately identified; they were not
inputs to the failed request.

A bounded inventory covers **160 raw captures**: the 64-cell interface repeat,
48-cell C2/M1 run and 48-cell C2/D1/D2 run. The quoted `effect_note` key appears
only twice, both in this one response. This is a census of those selected bundles,
not all previous experiments or a model error-rate estimate. Models, cases,
layouts and daemon versions differ across them.

All four craft effects in the failed response are **mixed**, while only two
objects have the extra field. All four already contain nonblank assessments and
evidence. The extras therefore do not fill missing explanations, and the capture
does not support a deterministic “mixed implies effect_note” rule. Empty optional
placeholders are consistent with an improvised output template, but that is a
hypothesis, not an observed generation mechanism. Training contamination,
provider hidden context and a particular token-level cause are not established.

The response is HTTP 200 with a normal stop, well inside the output allowance.
The unchanged boundary validator rejects the first extra field before attaching
application-owned evidence. A separate structural inspection records the second
extra field as well. The validator did not invent or silently drop either one.
There is no evidence here of an outage, truncation or a local field-insertion bug.

**Decision:** retain strict closed-object validation. Do not accept empty extra
members, strip them, or treat the affected report as valid. Keep D2's absence of
observed group-ID duplication as limited component evidence only; its previous
failed qualification remains unchanged.

## Fixtures added

The new local bundle contains three complementary fixture sets:

| Set | Coverage | What it verifies |
| --- | --- | --- |
| Closed-field mutations | **20** authored variants: four craft dimensions × five extra-field values | Empty string, null, text, boolean and nested object are rejected under all three archived layouts and the unchanged application boundary |
| Captured premise examples | **26** field-level examples: all eleven unsupported claims from nine reports, plus fifteen supported controls | Exact field text, complete source packet, source/report hashes, original adjudication and version/offset quotations stay bound |
| Authored response contrasts | **9** examples: four supported/unsupported pairs and one uncertain interpretation | Explicit source-support judgments affect complete usability while labels, mandatory arithmetic and genuine findings remain visible |

The strict-field tests also verify that uncertainty can use the existing
assessment with empty evidence under the established exception, but cannot add
`effect_note`; the extra field cannot replace a required assessment either.
These are mutations of a valid control in memory. The rejected captured response
is never edited, repaired or credited.

The negative premise fixtures cover:

- **Invented prerequisites:** deferring a conversation does not prohibit a
  broadcast; wanting another opinion before explaining does not establish
  consultation before acting or deciding; an appointment alone does not prohibit
  an earlier crossing. Explicit endpoint restrictions still apply.
- **Independent motivation:** the footbridge scene retains routine post-flood
  inspection and knowledge of older timber after the visible split is removed.
  Losing the immediate hazard does not prove that every reason disappeared.
- **Invented sensory content:** tape hiss and lack of identification do not
  establish an unidentified speaking voice.
- **Exaggerated consequences:** unpicking one shoulder seam establishes the
  forbidden alteration, not destruction of the entire garment.
- **Identity versus incompatibility:** exact two and exact three at one instant
  concern the same crate but are conflicting claims, not identical claims.

Supported controls preserve the boundaries that matter for creative work:
weaker tension, consultative tone and awkward preparation can be reasonable
literary interpretations without inventing a strict prerequisite. Identical
time/object references are not identical counts. An actual adjacent duplicate
can be removed without changing the story. Existing loaves do not mean that a
new order was started. The historical “creates or compounds” disjunction remains
supported as previously adjudicated; it is not silently changed into an assertion
that the original already contained the contradiction.

The supported prose of **D1 F-broad/OR** is also retained alongside its incorrect
`request_relation=direct` label. Correct explanatory prose does not repair a
different wrong field. Likewise, correct mandatory aggregation does not validate
an explanation. The authored uncertainty fixture remains **uncertain**, neither
false nor supported, and does not become a fully usable report.

These fixtures preserve **assistant-adjudicated examples**, including judgments
that are open to further human interpretation. Their tests verify evidence
binding, coverage, rejection and scoring behavior. They **do not automatically
infer semantic truth from prose**, constitute a new blind review, or demonstrate
that a model now avoids the failures. Authored examples are explicitly labeled
as response-only controls, not new model receipts; they have no fabricated raw
response hashes or usage. No prompt or source story was changed.

## Verification and preservation

**94 offline tests pass: 74 new audit/fixture tests and 20 unchanged previous
execution tests.** HTTP transports are blocked. Ruff lint/format and strict mypy
pass on all three new private scripts. Verification uses a fresh repository-local
temporary directory. Initial lint findings and a missing optional type annotation
were corrected locally; the saved static-check record retains the initial mypy
failure and the final pass. No frozen harness or historical scores changed.

The prior 21-file analysis seal, 435-file execution manifest, frozen preparation,
source/runtime fingerprints and public results all verify. The historical
**14/11/15 valid** and **11/7/12 usable** counts for C2/D1/D2 remain unchanged.
The eight invalid responses stay invalid; D1 and D2 still receive
`retain_limited_evidence_no_advancement`.

Private bundle:
[reviewer-field-premise-audit-v61-2026-10-24](../../data/diagnostics/reviewer-field-premise-audit-v61-2026-10-24/).
It contains the provenance audit and capture census, strict-field variants,
26 captured premise fixtures with complete context, nine authored contrasts,
the readable fixture register, source hashes, tests, verification and final seal.
Full fictional prose and raw evidence remain local and ignored by Git.

Offline replay from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-field-premise-audit-v61-2026-10-24/local_audit.py verify
.venv/Scripts/python.exe -X utf8 -m pytest data/diagnostics/reviewer-field-premise-audit-v61-2026-10-24/test_local_audit.py data/diagnostics/reviewer-layout-v61-2026-10-23-analysis/test_execution.py -q
```

If Windows' default temporary directory is unavailable, choose a fresh
repository-local `--basetemp`; never use an evidence directory. No live command
is supplied by the new audit module. Application/frontend source is unchanged,
so unrelated application suites and the production build were not repeated.
The tracker and local issue index are updated; all fourteen user-posted GitHub
links and original issue bodies are preserved, with no external issue change.

## Next decision

The local evidence does not justify a production parser relaxation or a new
extra-field prompt patch by itself. The more substantial unresolved pattern is
that correct targets coexist with unsupported explanatory premises. A plausible
interpretation is that a clear endpoint violation invites extra justificatory
claims; the captures cannot establish that internal reasoning process.

The [next bounded proposal](reviewer-premise-comparison-proposal-2026-10-24.md)
therefore isolates explanation grounding while treating delivery as a protected
outcome. It proposes **32 new attempts**, unchanged D2 controls, one diagnostic
premise-check treatment, fresh counterexamples and both display orders. D2 is an
unqualified diagnostic baseline, not a promoted production reviewer. The proposal
is **not frozen and not approved**; no new prompts, requests, live plan or approval
record has been created.

Preserve the nine human ties. A wording defect in a critic's explanation is not
automatically a story-quality defect, and exact prose preservation is not the
quality target. Humans should continue to assess feel/emotion, flow, character
and story-breaking details, with mechanical evidence prepared by machines.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**
