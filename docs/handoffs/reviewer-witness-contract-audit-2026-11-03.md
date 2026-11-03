# Source/field binding and quotation-scope audit — 2026-11-03

Status: **COMPLETE LOCALLY. No new inference or production change.**

The [Luna MA/WB comparison](../benchmark_reports/reviewer-luna-witness-v61-results-2026-11-03.md)
exposed two application-contract problems. Independent source and field enums
permit impossible combinations. Separately, the model-visible instructions ask
for a quotation that locates a section, while the frozen scoring requires the
quotation itself to contain the material evidence. A local schema prototype
eliminates the first ambiguity; two explicit evidence views make the second
distinction reviewable. Neither establishes factual support or better stories.

All historical scores remain **MA 50 grounded / eleven citation-only / one
semantic**, versus **WB 51 / nine / two**. WB remains unqualified. This audit
does not repair outputs or award new paragraph-based credit.

## Evidence preserved and authenticated

Private audit bundle: `data/diagnostics/reviewer-witness-contract-audit-2026-11-03/`.
It preserves **275 exact files**, authenticates **3,178 historical source pins**,
and retains all **124 fixed judgments and 103 WB witnesses**, including successes,
paired losses, unavailable-state rules and original source-inspection notes.
Historical Python is copied as inert evidence and never imported or executed.

All sixteen saved requests equal their frozen requests. All **32 recorded request
body hashes and endpoint paths** match the corresponding frozen generation/count
wires. Full source contents, versions, field text, paragraph boundaries, registry
entries and work fingerprints agree across the requests and local assessment
renderer. The sixteen presentations contain 2,016 registry entries, including
repeated presentations; these are not independent source observations. There is
no evidence here of an application field shift or lost source context.

The invocation input-version list and the citable-source namespace serve different
purposes. H1 carries five additional historical invocation IDs, W2 three; F3/F4
carry exactly their four citable versions. These historical lists are inherited
unchanged from the baseline. Every citable version is present, and WB's schema
admits only the four model-visible source versions. This audit does not establish
the complete ancestry semantics of every ancillary historical ID. Such IDs must
not become citable merely because they appear in invocation metadata.

## Source identity and field identity must be bound together

The old witness shape has independent `version_id` and `field` enums. Membership
in each enum does not prove the field belongs to that version. The local candidate
changes only the witness item schema: a nested `anyOf` has one closed branch per
immutable source version, with only that source's registered string fields.
Quotation length, evidence-array bounds, claim workload and all other constraints
remain unchanged. Source identity comes from the verified model-visible registry.

| Family | Combinations allowed before | Actual source/field pairs retained | Impossible pairs excluded |
| --- | ---: | ---: | ---: |
| H1 | 1,200 | 302 | 898 |
| W2 | 208 | 54 | 154 |
| F3 | 208 | 54 | 154 |
| F4 | 208 | 54 | 154 |
| Total | **1,824** | **464** | **1,360** |

Exhaustive local checks retain every legitimate pair and reject exactly the five
saved witnesses with impossible combinations:

- H1-PC Q001 pairs the scene-plan version with `/scene_plans/0/outcome`;
  Q002/Q005 use `/scene_plans/0/exit_state`; Q007 uses
  `/scene_plans/0/turning_point`. Those prefixed paths belong to another source.
- F3-CP Q005 pairs the blueprint version with `/turning_point`, which belongs to
  the separate scene-plan source.

All **94 located witnesses remain admissible**. Four other witnesses also remain
schema-admissible but unresolved: two altered literals and two quotations crossing
registry entries. Together with the five impossible pairs, these reproduce all
nine unresolved witnesses across eight judgments/four calls.

Applying the candidate to the saved outputs would reject **two complete WB
responses**, H1-PC and F3-CP. This is validation of a constraint, **not five model
recoveries**. How the model generates under that constraint remains unknown.
The local native-schema transform preserves the candidate, but server acceptance
and live generation have not been tested. The checker exhausts the finite
version/field combinations and witness shape/length rules; it is not a general
JSON Schema conformance validator.

## A quotation's address and its evidentiary scope are separate

The historical model-visible clause requests text “sufficient to locate one
occurrence inside one registry entry” and says the application cites the containing
field/paragraph. The frozen scoring instead requires the exact submitted quotation
to cover each material premise. Both requirements are coherent individually;
they are different contracts.

| Contract | What the exact quotation does | What can supply evidence |
| --- | --- | --- |
| `exact_span` | Identifies and supplies a precise evidentiary span | Only the submitted, resolved spans; surrounding text is reading context |
| `section_locator` | Addresses one immutable registry section | The exact containing field or prose paragraph selected by that address |

Under either contract, a missing, ambiguous, cross-entry or wrongly bound quote
remains unresolved. The application does not correct spelling, normalize a
near-match, search another source, invent an occurrence number or extend into an
adjacent section. The returned unit is explicit, with version, field, offsets and
text. Location success leaves evidence adequacy, factual support, craft and edit
necessity **unassessed**. Neither view grants writer or whole-relation authority.

The local renderer displays the complete assessment work and source context,
the literal witness, its location status, the selected evidence unit and the
containing section. Both modes preserve unresolved results and render source text
as data. The prototype is private; the tracked read-only component and production
prompts are unchanged.

Three actual fixtures demonstrate why the distinction matters:

- **F3-CP Q001:** the quote includes preparation and the still-outside state but
  omits the preceding internal motive in S057.
- **F4-PC Q001 and F4-CP Q001:** the quoted spans likewise omit the opening
  internal reasoning in S057 while retaining preparation.

Their compound claims require internal reasoning **and** preparation. The exact
spans omit a required premise; the containing sections include it. These are
authored source comparisons, not new automated semantic verdicts. They establish
a real instruction/scoring ambiguity, not the model's internal reason for choosing
short quotations. The original citation-only scores remain frozen.

For a future evidence-selection diagnostic, recommend **explicit section-locator
semantics in both arms**. This puts quotation addresses at the same evidence-unit
granularity as direct MA section references. Preserve `exact_span` as a separate
contract when precise complete quotations are actually required, and state that
requirement in both instructions and scoring. Never switch modes after seeing
the outputs or silently use surrounding text to rescue a failed exact-span claim.

## Semantic failures and story quality remain separate

The H1 private-flourish failure survives perfect location: general handwriting
agreement does not establish the particular planned private-flourish verification.
The historical H1-PC MA success/WB loss and shared H1-CP failure are preserved.
A structural-pacing concern might still be reasonable editorial advice, but its
specific-event premise needs evidence. The schema cannot settle that judgment.

Within each historical case/order block, MA and WB have matched selections. H1's
PC and CP blocks, however, contain different admitted selections; its cross-order
contrast is **not a source-order-only experiment**. W2/F3/F4 retain identical
selections across orders. Preserve the H1 blocks as historical controls and use
identical selections across orders for newly authored families.

None of these checks evaluates emotional effect, flow or character quality.
Mechanical validation should supply reviewable evidence to humans, while humans
assess the overall reading experience and story-breaking details. A paragraph is
an evidence address, not a unit of literary merit. Even a successful future
binding pilot would not authorize writer edits or qualify a production critic.

## Verification

**374 offline tests pass**: 163 new audit regressions, 88 applicable original
frozen-harness tests and 123 tracked assessment-work/result tests. The unchanged
preparation-stage test requiring absent live/approval files is deliberately
deselected after the completed run; it is not a runtime failure. Tests cover
every saved witness, the full source/field matrix, exact source/request identity,
both evidence views, literal boundaries, ambiguity, Unicode, JSON pointers,
source/registry drift, renderer safety and denied network/database operations.

Repository Ruff, formatting and strict mypy pass for **224 Python files**. The
four new private scripts pass their corresponding explicit checks. Deterministic
replay reproduces the audit artifacts. Original evidence and source fingerprints
remain unchanged. The final combined mocked suite ran outside the Windows sandbox
because of its async-test stall; all HTTP calls in that harness use mock transport.
The new audit blocks HTTP, sockets/DNS and SQLite. No credential was accessed.

No new generation, token-count, model-catalog or daemon request was made. No
tracked application code, dependency, schema, frontend, production profile or
prompt changed. The earlier full repository suite is not claimed as rerun.

## Proposed next step — prepare a separate 16-call schema comparison

The local evidence justifies testing a new, narrow hypothesis: **coupling source
and field identities at generation time reduces binding errors without losing
grounded judgments**, under an explicitly shared section-locator contract.

This is a proposal, **not a frozen plan or live authorization**:

1. Prepare U/C arms on `gpt-6-luna` with the same high reasoning, full source
   context, whole-claim workload and explicit section-locator instructions.
   **U** retains independent source/field enums; **C** uses source-bound field
   branches. The witness-item schema is the only between-arm treatment. The
   common evidence-scope clarification is a declared baseline amendment; these
   new controls must not be described as byte-identical historical WB requests.
2. Use H1 and F3 as two known-failure families and author two fresh families,
   each in both presentation blocks: **eight matched pairs, sixteen attempts**.
   Retain historical H1 selections within each block; keep fresh selections
   identical across orders. Cover wrong source/path pairing, altered/repeated
   literals, cross-paragraph quotations, motive-plus-action coverage, and the
   specific-event versus structural-reading contrast. Four families remain four
   independent stories, not eight.
3. Freeze complete per-claim labels and adequate **section-level** evidence
   criteria before inference. Inspect source identity, literal location, whole
   claim, material explanation and evidence adequacy separately. Equivalent
   adequate sections are allowed; a correct location alone earns no support.
   Do not narrow evaluation to the five schema-targeted witnesses or discard
   failed deliveries. Retain resource usage and every fixed unavailable slot.
4. Provisionally require all pairs delivered, at least two distinct family/claim
   citation recoveries, no grounded or semantic loss, and all fresh C judgments
   grounded. Reversed presentations do not count as distinct recoveries. If U
   has no failures to recover, report feasibility/repeatability only. Fix the
   final screen, native-schema mock checks and exact artifact pins during local
   preparation, before asking for execution approval.
5. Freeze **sixteen attempts, zero retries or replacement generations**. Carry
   forward the current per-request resource limits unless preparation identifies
   a reason for an explicit amendment. Freeze total token/cost reservations and
   terminal rules for identity drift, unsupported schema, invalid/empty/truncated
   delivery, transport failure, cancellation and unknown usage. No extra smoke
   generation is implied. Preserve terminal evidence and request fresh approval
   for any later continuation.

Do not combine this comparison with active-slot, narrower-workload, writer-edit
or model-choice changes. Its result could justify a later read-only integration
decision, not autonomous edit authority. All fourteen issues remain open:
**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**

## Local artifact map

- `preservation.json` and `captures/`: immutable evidence copies and source pins.
- `candidate-schemas.json`: source-bound schemas and local native transforms.
- `judgment-regressions.json` / `witness-regressions.json`: all saved judgments,
  witness outcomes and both explicit evidence views, without rescoring.
- `coverage-observations.json` / `contract-comparison.json`: three real shortened
  quotations and the instruction/scoring distinction.
- `renderer-examples.json`: valid, invalid-binding and shortened-quote examples
  in each evidence mode, retaining full work context.
- `wire-authentication.json` / `presentation-notes.json`: exact dispatched-body
  verification, namespace limits and historical order-block caveat.
- `audit.json`, `verification.json`, `verification-logs/` and `closure.json`:
  metrics, commands/results and final publication fingerprints.

The bundle remains local under ignored diagnostic storage. Public documentation
contains findings and pointers; no external issue was edited or closed.
