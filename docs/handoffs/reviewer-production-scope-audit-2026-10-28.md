# BS/PO regressions and production source-scope audit

Date: **2026-10-28**. **COMPLETE — local work only; no inference or daemon calls.**

The five BS label failures and their successful PO counterparts are preserved,
with the controls and historical scores intact. The production audit finds useful
existing safeguards—immutable versions, scoped inputs, exact evidence references
and separate assignment checks—but no ready-made source of PO's complete,
case-specific obligation ledger. The experiment authored its observation pair,
three premises and finite source scope. Production cannot assume those inputs
from an artifact ID or a completed reviewer response.

The justified next question is whether **unchanged PO assessment generalizes to
distributed evidence and competing source roles**. The separate
[40-call proposal](reviewer-production-scope-proposal-2026-10-28.md) is not prepared,
frozen or approved. This audit adds diagnostic code and fixtures only; it does not
integrate PO into production or change prompts.

## Preserved evidence

Source: [completed BS/PO/ER comparison](../benchmark_reports/reviewer-source-obligations-v61-results-2026-10-28.md).
Private bundle: `data/diagnostics/reviewer-production-scope-audit-v61-2026-10-28/`.

| Preserved material | Count / location |
| --- | --- |
| Byte-identical raw responses, including ER anchors | 48; `captures/<trial>/raw-response.json` |
| Version-bound component regressions with raw and application-bound assessments, sealed notes and old metrics | 336; `captured-regressions.json` |
| All matched BS/PO pairs, with corresponding ER targets and conditional controls | 16; `bs-po-pairs.json` |
| Failed-BS/successful-PO pairs | 5; `label-recovery-pairs.json` |
| Raw PO primitive judgments and exact bound witnesses | 48; `po-primitive-regressions.json` |
| M3/M4/M5/M6 scope/time/identity targets across all arms and orders | 24; `scope-time-identity-controls.json` |
| Qualified BS/L1/OR craft concern and original sensitivity analysis | `qualified-craft-fixture.json`, `precision-sensitivity-preserved.json` |

The five exact pairs are **K2-OR, K2-RO, M1-OR, M1-RO and M2-OR**. Their captures
use `C-BS-<family>-<order>` and `C-PO-<family>-<order>`. Each BS target C02.A01
returns **uncertain** while correctly explaining missing common-time evidence.
PO's inspected premises yield **source unsupported / event uncertain**. These
are matched **label recoveries**, not newly recovered noticing or source grounding.
PO has no raw target verdict: that verdict is explicitly application-derived.

The original **BS 11/16, PO 16/16, ER 16/16** usable-target scores and
`retain_source_obligation_recovery_signal_only` decision are unchanged. The
qualified “seating Tavi” wording remains a sensitivity, not proven event invention.
Accepting it changes neither target scores nor the five recoveries. Raw thinking
is retained opaquely in the captures and is not used as semantic evidence.

The source analysis seal remains
`c1e08cca7c34677fedf596b1d8edb5d5dcb9be8c82fc53d0c665e78dc412a084`.
Requests, full scene pairs, context, claims, source offsets, receipts and sealed
inspection are bound through `sources.json`; historical files are not rewritten.

## What production already provides

This is an applicability audit of the current code, not evidence that production
context filtering caused the historical BS errors. Those errors occurred in the
frozen diagnostic packets.

| Production surface | Existing safeguard | What it does not establish |
| --- | --- | --- |
| `_load_inputs`, invocation recording in [production_model_executor.py](../../apps/api/open_hollywood_api/services/production_model_executor.py) | Loads exact artifact versions; records rendered prompt text/hash and execution identities | A version ID alone does not say which fields the reviewer saw or that the declared source is exhaustive |
| `_scene_assignment_contract`, `_critic_requirement_scope`, [production_critic_obligations.py](../../apps/api/open_hollywood_api/services/production_critic_obligations.py) | Separates approved current-scene anchors and due-now requirements; requires explicit assignment assessments | An intended outcome is not evidence that the corresponding event happened; these assignment obligations are not PO's identity/opposition/time premises |
| `_scene_scoped_prompt_inputs`, `_scene_boundary_contract` | Filters Blueprint characters, relationships, locations, beats and plans to the current scene; exposes limited adjacent reservations; withholds the ending before the final scene | The selected view is not the full Blueprint. Future reservations are assignments, not observations |
| `_critic_prompt_inputs`, `_critic_evidence_catalog`, `_resolve_critic_evidence_refs` | Replaces current draft prose with sentence evidence; accepts bounded references to that exact draft version and validates their resolution | Resolved quotes do not prove entailment, referent identity, simultaneity or exhaustive absence |
| [production_revision_acceptance.py](../../apps/api/open_hollywood_api/services/production_revision_acceptance.py) | Keeps exact repair lineage and original evidence; compacts prior critique and older/other-scene prose | A previous critique remains a fallible allegation; retained version identity does not mean the full historical manuscript is visible |
| `_continuity_canonical_source_catalog` | Retains artifact/source paths and canonical IDs; keeps timeline summary, time context and scene together; excludes ScenePlan obligation fields from contradiction canon | A canonical ID or a timestamp cannot by itself connect two particular observations. Existing scope annotations deliberately allow later changes and unmentioned details |
| [ContextPacketCompiler](../../engine/open_hollywood_engine/context/compiler.py) and [context contracts](../../engine/open_hollywood_engine/context/contracts.py) | Records budget/manifest omissions, selected Bible sections and included versions | Scene-production `_messages` constructs its own payload. The generic compiler's omission ledger must not be assumed to accompany this critic path |

Three deterministic, local probes exercise the actual production `_messages`
path using existing authored API test fixtures: initial scene, final scene and
revision with prior critique/old draft/another scene. The captured
`production-rendering-probes.json` stores canonical inputs alongside rendered
payloads and their hashes. It verifies that:

- The same artifact version can accompany a different rendered content view.
- The early scene excludes the proposed ending; the final scene retains it.
- The current draft becomes an evidence catalog. Revision inputs can retain
  old/other-scene identity while omitting their prose, with explicit scope tags.
- Rendering does not mutate canonical input artifacts.

These transformations are intentional context boundaries, not automatically
defects. Any future PO integration must describe them accurately.

## Decisions about obligations and source scope

**Keep three different objects separate:** the finite declared source **S**, its
visible rendered view **V**, and the story's wider truth. “S establishes this
relation” is not “this event is true,” nor is it “V contains a quoted witness.”
An unavailable part of S cannot silently disappear from the claim. A new claim
about V needs its own explicit scope and binding. An unspecified whole-story
inventory is not a complete finite source.

For a narrowly admitted literal two-observation claim, retain three independent
premises: same entity, literal incompatibility if simultaneous, and same
observation instant. Different entities refute identity without necessarily
refuting conditional incompatibility. A coat and no scarf are compatible even
for the same compartment at the same time. Record-entry order, a shared entry
timestamp, a planned deadline or nearby narrative time does not establish the
observations' common instant without an explicit source connection.

**Obligation creation remains a separate unsolved boundary.** Existing typed
assignment fields can identify obligations to check, and canon paths can locate
candidate facts. They do not safely decompose an arbitrary generated allegation
into PO's three premises. A future production adapter would have to identify and
bind the particular observations, their referents, literal scope and claim type.
This audit does not implement that extractor. Unresolved pair selection or
claim type must remain unadmitted, rather than invented by the projection code.

A prospective finite-source record should bind source version and field pointer,
full-value hash, rendered-view hash, view availability, source role, claim/map
hashes and observation-pair identity. Scope must come from the application's
declared inventory and actual rendering, not the model's confidence. Authority
also needs provenance: a critic claim cannot promote itself to canon; a summary
cannot silently substitute for omitted detail; one selected clock value cannot
erase an equally authoritative contradiction.

**Preserve abstention.** Missing review, an unknown inventory, unavailable material
needed by the claim and unresolved conflicting evidence must not become a
definite absence judgment. A completed ledger reports coverage; it does not prove
that the source was actually understood. Positive conclusions may have finite
sufficient witnesses without exhaustive source coverage; the local shadow check
uses a conservative full-view witness policy and is not a universal logic rule
or a production policy decision.

## Local boundary tests and their limits

`scope_contract.py` is an offline shadow validator around the unchanged earlier
projection algebra. The application-authored claim type, inventory, source roles
and observation pair are explicit trusted fixture inputs. It checks exact
bindings and visible witnesses; it does **not** infer these facts from prose.
Its output is always provisional, with semantic verification, production
admission and writer dispatch disabled.

**18 authored fixtures** cover complete missing-time evidence; unavailable,
summary and excerpt views; distributed positive evidence; different times;
conflicting authorities; unknown identity; compatible predicates; five unsuitable
witness roles; unknown inventory; incomplete review; and a false-premise control.
Mutation tests reject stale claim/packet/map/scope/pair bindings, changed content,
unknown or duplicate references, missing witnesses and duplicate obligations.

The negative control deliberately supplies a **well-formed false timing premise**.
Its hash and reference checks pass, and the old algebra produces the wrong
supported label. This is a preserved limitation, not a successful semantic test:
correct plumbing cannot rescue false model premises. Likewise, listing all
members as reviewed cannot establish real semantic coverage. Inspection of
primitive judgments, explanations and source alternatives remains necessary.

The recent live data do not yet test all these branches. All 16 PO literal-
opposition judgments were established; there was no compatible-predicate
negative control, ambiguous-identity case or competing-authority case. The
context-only positive and unavailable-appendix controls are valuable, but do not
qualify general provenance handling.

## Verification and next boundary

**188 offline tests pass: 104 current audit checks and all 84 preceding execution
checks.** Ruff lint/format and strict mypy pass on six local scripts.
**7,414 historical and production fingerprints** verify. Results are recorded in
`verification.json` and `source-verification.json`; verification attempts are
retained. The initial check exposed an audit-module name collision with an older
diagnostic and four explicit-export type errors. Renaming the new module and
declaring its exports resolves those local harness issues without changing
historical code, scores or production behavior.

The checks replay unchanged execution evidence, exact source bindings, controls,
sensitivity, local scope guards and real production rendering. Real HTTP is
blocked during tests. No application or frontend code changed, so frontend and
full production builds are outside this diagnostic-only verification scope.
`audit-seal.json` seals the private deliverables; `publication-closure.json` binds
the public audit/proposal, tracker and issue index while checking unchanged issue
bodies and posted links.

No additional inference is necessary to preserve the evidence or establish the
local interface limitations. A separately prepared comparison is justified only
for the unresolved **generalization** question described in the proposal.

Future story-quality work retains ambiguity, indirect action, emotion and
defensible interpretation. An unsupported contradiction allegation does not make
the story defective or authorize adding explanations, timestamps or literal
restatements. Even a supported factual defect still needs a separate necessity
and minimal-repair decision. Humans retain feel, flow, character and story-breaking
judgments, supplied with machine-prepared mechanical evidence. The nine prior
human ties remain unchanged.

Production **prompt 61 / graph 9 / fulfillment policy 1** and human checkpoints
are unchanged. No issue is closed or externally edited; all fourteen issue bodies
and posted GitHub links are preserved. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; full workflow canary ON HOLD.**
