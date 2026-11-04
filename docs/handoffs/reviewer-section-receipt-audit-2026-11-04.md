# Section receipts and private-event interpretation audit — 2026-11-04

**Complete locally. No inference, token-count, catalog or daemon calls.**

The three recommended steps from the [U/C results](../benchmark_reports/reviewer-source-field-v61-results-2026-11-04.md)
are complete. The captures now have executable regression coverage, source/field
identity is audited separately from literal and paragraph selection, and the
private-flourish claim is separated from its possible editorial interpretation.

The main finding is that **application-owned section receipts remove copying
responsibility, but do not solve evidence selection**. That capability already
exists in the tracked assessment component and older MA interface. Re-expressing
all 62 older MA selections as receipts preserves its eleven citation failures
and one semantic failure. Another receipt-format comparison alone is not justified.

There is a separate measurement question worth testing: the historical phrase
“consumes the turning point” can express functional story overlap, while the
frozen target asks whether a specific private verification was depicted. A small
changed-proposition diagnostic could distinguish those readings. It would not
qualify a critic or establish that a story needs rewriting.

Production prompts/profiles and application code remain unchanged. Historical
scores are unchanged: **U 55 grounded / six citation-only / one semantic;
C 57 / three / two**. C remains unqualified. Live calls are paused; the canary is
**ON HOLD**. All fourteen issues remain open.

## 1. Preserved captures and regression coverage

Private bundle: `data/diagnostics/reviewer-section-receipt-audit-2026-11-04/`.

The audit preserves **544 exact files** and verifies **3,521 historical source
fingerprints**. These include the complete U/C freeze, live responses and inspected
results, plus the earlier Luna MA/WB evidence needed for negative controls.
Copied historical Python is inert evidence. The reviewed pure locator/context
functions were deliberately ported into a separately tested local prototype.

The regression inventory retains:

- All **124 U/C judgments**, with original labels, material-explanation and
  adequacy decisions, notes and classifications. Tags identify both sides of
  the six recoveries, four losses, shared H1 semantic failure and fresh contrasts.
- All **232 witnesses**: **221 located, seven unavailable-field, three missing
  literals and one cross-entry quotation**. Every original location replays
  exactly; none is repaired or silently converted into a successful selection.
- All **62 earlier MA judgments**, including **50 grounded, eleven citation-only
  and one semantic**. Successful controls remain beside their failures.
- All sixteen U/C source presentations and **32 count/generation dispatch
  hashes**, checked against the frozen requests. The complete primary sources,
  source versions, fields and selected statement identities remain consistent.

The tests specifically protect distinctions that an aggregate score can hide:

| Saved case | Preserved distinction |
| --- | --- |
| C F5-CP Q005 | S056 and S032 adequately support the claim, but the extra wrong-source `scene_2` witness still fails binding |
| U H1-PC Q001 | S309 locates correctly but shows an event rather than the assignment obligation claimed |
| C F3-CP Q005 | A real planned-test quotation does not belong to the selected current-plan field |
| C F6-CP Q003 | An exact quotation spanning two paragraphs cannot be silently split into two section locators |
| H1-PC Q006 pair | Both arms locate S215 and S309; only U preserves the frozen specific-event distinction |
| F3/F5 versus F6 | Paraphrased performance of a private procedure differs from an explicitly unperformed procedure |

These are replay and boundary tests, not new model results or an automated
semantic truth detector. The original scored decisions remain the source of
regression expectations.

## 2. What application-owned section receipts can and cannot do

The private prototype creates a receipt catalog from the authenticated full work
record and existing tracked evidence registry. Each handle binds the work,
request, document/version, document hash, field pointer/hash, paragraph or whole
field, exact offsets and exact text. The application supplies those values;
the selector supplies only handles. All sections remain available, with no
gold-guided filtering or relevance labels.

The prototype checks **sixteen catalogs / 2,016 entries including repeated
presentations**. It revalidates complete catalogs, including uncited entries,
and rejects changed text, fields, versions, offsets, hashes, duplicate or foreign
handles and altered authority fields. Repeated literal text has separate occurrence
identities; a quotation-only lookup remains ambiguous instead of choosing one.
Rendering retains the entire work/context and displays exact selected sections.

| Operation | Local result | Remaining limitation |
| --- | --- | --- |
| Bind source to field | Exact registered relationship | A legitimate field may be irrelevant to the claim |
| Supply section text | Application renders immutable text | A selector may choose the wrong section |
| Preserve paragraph boundaries | One receipt per actual section; multiple sections require multiple handles | A necessary section may be omitted |
| Select repeated text | Distinct occurrence-bound handles | The application cannot infer which occurrence the model intended |
| Judge evidence adequacy or the claim | Remains unassessed | Requires semantic evaluation; location does not settle it |

The **221 already located witnesses** map to precisely the same complete sections
under the declared U/C locator contract. The eleven unresolved witnesses receive
no substitute receipt. The renderer examples that select the two date paragraphs
separately are explicitly **authored local examples**, not repaired model outputs
or credited recoveries.

This is substantially the responsibility split already provided by
[ADR 0042](../adr/0042-active-assessment-results-and-evidence-locations.md): the
model selects references and the application owns exact locations and text.
Changing an S-reference into a longer work-bound handle does not improve which
section is chosen. The new handle spelling is not recommended for production.

The old MA negative controls make that limit concrete. F3-PC Q002 selects the
vibration and later clapper-test paragraphs, omitting the actual touch. H1-CP
Q003 selects the date realization for a handwriting-match claim. Every chosen
reference can become an exact, valid section receipt; neither selection becomes
adequate. All **eleven citation failures and one semantic failure remain** in
the local projection. Historical responses and delivery receipts are untouched.

The prior [MA/PE experiment](../benchmark_reports/reviewer-paragraph-excerpts-v61-results-2026-11-01.md)
also already placed paragraph text beside references and observed the same H1
semantic error with correct locations. Simply adding more excerpt text is not
an untried solution. This audit supports the existing read-only provenance
boundary, not a new automatic acceptance or writer route.

## 3. Specific events and editorial overlap are different questions

The complete H1 draft explicitly establishes a general handwriting match in
S309. It does not depict a private-flourish verification. S215 specifies that
particular later verification. Independently, S290 forbids establishing a match
by the current endpoint, so the current draft does violate that assignment.

The broader next-scene plan also matters: S211 gives authentication as its
purpose, S212 describes comparing the card with journals, and S204 describes
evidence matching Elena's private writing. Those broader intentions can overlap
with the current draft's general comparison. This makes a pacing concern
intelligible, without proving that the narrow private procedure happened or
that changing the prose would improve the story.

| Question | Source-bound audit conclusion |
| --- | --- |
| Does the draft establish a general handwriting match? | Yes: explicitly observed in S309 |
| Does it depict the particular private-flourish verification? | Not established by the complete supplied draft |
| Does it violate the no-match current endpoint? | Yes: S309 compared with S290 |
| Does the next plan specify that private verification? | Yes: S215 is a statement about the plan |
| Does the early general match make the later authentication beat redundant or weaker? | Editorial hypothesis; quality and edit necessity remain unassessed |

The original “consumes the turning point” sentence combines a structural conclusion
with a factual causal premise. The frozen test deliberately interpreted it as a
specific-event claim. C's supported answer remains a failure under that contract;
the audit does not retroactively change its meaning, score or no-promotion result.
However, that observation alone does not show that a broader editorial reading
is irrational or that the model is incapable of useful pacing criticism.

The final explanations reveal the substitution directly. C H1-PC Q006 argues
that naming the flourish is unnecessary because general authentication resolves
the later turn. U uses the same two located sections and refuses that inference
about the specific event. Exact citation identity cannot choose between the
predicates being judged.

The fresh controls separate an additional issue. F3 and F5 perform the defining
private procedures through paraphrase and are correctly recognized; exact plan
wording is unnecessary. F6 expressly leaves its private test undone. H1 instead
does not establish the specific method, without expressly denying it. **Absence
of depiction and explicit negative evidence must not be pooled as the same
reasoning condition.** Neither permits invented off-page events.

Eight authored, source-bound audit records preserve these distinctions. Their
`supported`, `not_established` and `contradicted` annotations describe this local
inspection; they do not change production labels or establish a new model output
contract. Editorial effect has no factual verdict. All records leave craft,
edit necessity and writer authority unassigned.

## Verification

**724 applicable offline tests pass:** 386 new capture/receipt regressions,
215 applicable frozen U/C harness tests and 123 tracked assessment-work/result
tests. The one unchanged preparation-only no-approval/no-live assertion is
deselected because the approved comparison now has live artifacts.

Repository Ruff/format/strict mypy pass for **224 Python files**; the four local
audit scripts pass their corresponding checks. Deterministic preservation,
fixture generation, rendering and score replay preserve the same outputs. Source
and publication integrity checks preserve original issue bodies and posted URLs.
No external issue is changed or closed.

Development formatting/import-typing findings were corrected before final
verification. An initial recursive typing command encountered duplicate module
names in inert archived captures; final checks explicitly target only the four
audit scripts. The 386-test development suite and 724-test combined suite both
passed. The mixed mocked harness uses the established Windows asyncio workaround;
real external transport and database operations are blocked by the local guards.

No production code, frontend, dependency, schema, prompt or active profile changed.
The earlier full repository suite is not claimed as rerun. Credentials were not
accessed and no provider/metadata call was made. The bundle includes preservation,
regression inventories, receipt examples, semantic source notes, prior-work
boundaries, verification logs and publication closure.

## Proposed next step

Prepare a **provisional sixteen-call claim-interpretation diagnostic**, rather
than promoting a receipt-format change. It is **not frozen or approved**.

The question is whether the model distinguishes the specified event reliably
when the proposition expressly asks about its depiction, while treating the
mixed structural formulation differently. Earlier work already explored
epistemic labels, whole claims, source obligations and the editorial distinction.
The new test would isolate **the target proposition's predicate**, with unchanged
primary sources and unchanged surrounding workload; it is not a claim that
generic clarification or decomposition has never been tried.

- Use **H1 plus three fresh complete scene families**, covering actual specific
  performance through paraphrase, general identification without an explicit
  negative sentence, and general identification with an explicit private-test
  denial. Vary narrative goals and structure, not only names and props.
- Use both PC/CP source orders and two target formulations: **mixed structural
  consumption wording** and **explicit depiction of the specified private
  procedure**. Four families × two orders × two formulations = **16 attempts**,
  zero retries. Retain all other claims, complete primary context, evidence format,
  model/settings and resource limits within each source pair.
- Use the established U section-locator contract in both conditions. Do not add
  receipt aliases, excerpts, smaller batches or a new model treatment. Keep the
  historical H1 U controls byte-identical where applicable; record the changed
  target report field and selection as explicit amendments, not unchanged inputs.
- Score these as **different propositions**, not same-claim citation recoveries.
  Preserve the original mixed-claim factual-contract score separately. Inspect
  event entailment, the interpretation expressed in the final reason, selected
  evidence and unsupported editorial assertions independently. The story's
  actual emotional or pacing effect receives no machine factual gold.
- Require complete delivery, correct explicit-event distinctions across positive,
  implicit-absence and explicit-denial cases, and no losses on unchanged control
  claims. If the mixed control does not reproduce a failure, report feasibility
  only. If explicit wording still fails with adequate evidence, do not respond
  with an open-ended series of synonymous reminders.

Before inference, freeze fresh cases, distinct whole propositions, exact requests,
all per-claim scoring/coverage, total token/cost/time reservations and terminal
stops; verify the renderer/adapter and submit the plan for separate approval.
No new requests or approval were created by this audit. Current provider metadata
and budget terms would be checked during that preparation, not assumed unchanged.

Even a favorable result would clarify an assessment contract, not demonstrate
better stories or authorize autonomous edits. Human review stays focused on feel,
flow, character and story-breaking details. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**
