# ADR 0047: Read-only ordinary-review intake and explicit scope

- Status: Accepted
- Date: 2026-11-12
- Extends: ADRs 0038–0039 and 0041–0044. Preserves ADRs 0045–0046.

## Context

The [bounded admission audit](../handoffs/ordinary-review-admission-2026-11-12.md)
admitted fourteen supported and two uncertain whole fields, with nine holds.
Several apparent negative claims mixed a factual violation with an editorial
effect or used a named procedure as shorthand for dramatic function. Choosing a
reading implicitly would manufacture gold. The local pending-work prototype was
verified, but lacked a tracked operator intake path.

The user authorized implementing that path and clarifying scope. Inference remains
paused; this decision does not activate autonomous assessment or writer routing.

## Decision

Add the pure `evaluations.assessment_intake` component, an offline application
adapter, and `scripts/assessment_intake.py`. Reuse the existing authenticated
SQLite ordinary-review and registered October 16 probe export contracts. Do not
register the two additional October 17 archives as part of this change.

The command selects one to twelve explicit review IDs. Without an authored plan,
it exports an inventory and empty plan template; inventory selects nothing for
assessment. With a source-bound plan, it exports pending work and visible holds.
It makes no provider, input-count, catalog, worker or workflow call.

Source authentication is owned by the existing exporters. The SQLite path uses
their read-only transaction and compatible/non-result behavior. The probe path
uses their pinned archive contract, successful-attempt and parent/writer lineage,
actual messages, raw response, normalized review and native audit. Historical
programs remain inert. Neither the CLI nor plan accepts replacement trust pins.

Saved-review intake does not invent unavailable raw model output. Its report
explicitly combines the saved normalized critique and native audit. Probe intake
uses the raw model JSON and retains the normalized/audit versions separately in
operator provenance. Actual original IDs stay there; native assessment work is a
derived diagnostic and receives no canonical review identity or completion receipt.

## Whole fields, full context and authority

Inventory enumerates populated explanatory fields in deterministic JSON-pointer
order, retaining each entire field. It does not extract claims or split compound
statements. The complete report remains available, including fields outside the
inventory and fields not selected for assessment.

Each explicit choice carries a field ID, authored reading and interpretation,
optional hold reason, native whole-statement scope declaration and native work
brief. The plan binds the source and inventory-work fingerprints. Selection,
declaration, brief, reference and whole-field identities are revalidated. Unknown,
duplicate, stale or shortened selections are rejected; valid but incomplete scope
becomes a hold. Unselected fields stay visible without receiving gold.

Full original messages, report and current prose are retained in inventory and
pending work. Citation locations refer only to the actual visible request and
catalog-complete current prose. Recovered full input bodies, historical files,
receipt data and saved provenance remain separately labeled and are excluded from
the evidence registry. They cannot retroactively become critic-visible authority.
An original visible repair quotation can still be cited in its actual location.

Only structurally consistent explicit factual/procedural choices become active
pending units. Their native declarations and briefs are rebound to the resulting
work fingerprint without rewriting their content. Holds remain visible outside
active selections. If everything is held or unselected, pending work is null;
there is no empty successful assessment.

## Procedural versus editorial policy

This policy applies to prospective intake. It does not rescore historical captures
or choose a new reading for existing ambiguous gold.

| Authored reading | Evidence obligation and disposition |
| --- | --- |
| `factual` | Assess the entire stated event, choice, obligation, endpoint, attribution or availability claim. Preserve material means, temporal and source qualifiers. Consistent scope may enter pending work. |
| `literal_procedure` | A named procedure requires an `observed_procedure` predicate and declared definition plus draft evidence. A generic result alone does not establish its specified means or steps. Missing definition/performance scope remains a hold. |
| `editorial_effect` | Pacing, dramatic function, lost suspense, emotional effect and craft require separate assessment. They remain holds for this factual intake even when their factual context is clear. |
| `mixed` | Do not award whole-field factual credit by dropping an editorial clause. Preserve the complete field as a hold. |
| `ambiguous` | Preserve plausible readings and the unresolved question. Do not silently turn a dramatic-effect reading into literal procedure completion, or vice versa. |

The field saying a generic match achieves the named private-flourish turning point
(H03 in the admission audit) remains ambiguous. A future deliberate literal reading
would be a new declared interpretation, not a correction of the original field or
an automatically established negative control. “Consumes the dramatic work” does
not prove that the named procedure occurred; absence of that procedure does not
prove that the dramatic work is intact.

Purposeful action may establish a decision; no special word or decision sentence
is required. A future scene's exact starting state needs actual source authority.
Absence in complete available prose differs from an unavailable document; missing
evidence does not automatically mean false. Exact copying and citation binding do
not establish full-claim support. Style praise is not a zero-repetition assertion.

Readings, definitions, source roles, material inventories and briefs are authored
assertions. The component cannot detect a factual label attached to editorial text
or prove that free-text interpretation is correct. Its semantic-interpretation and
brief-neutrality flags remain false. There is no keyword classifier or inferred gold.

## Publication and limits

The adapter recomputes results and re-collects original sources before publication,
including after rendering. It preserves literal Unicode, escapes embedded markup
with dynamic fences, guards all output for secrets, rejects linked/protected paths,
and publishes the manifest last. Exact repeats verify and reuse every file without
writes; partial, altered or extra output is refused. No caller-supplied disposition
can bypass recomputation or source authentication.

Limits: twelve selected reviews, 256 inventoried fields per review, 128 explicit
choices per plan, at most twelve units per native batch, 4 MiB plan input and
64 MiB rendered output. Existing source-read and context-document bounds remain
in force. These are local tooling limits, not inference budgets or story-length rules.

All semantic conclusions, evidence adequacy, edit necessity, editorial effect and
craft remain unassessed by the software. No result, receipt, inferred gold or writer
permission is generated. No database schema, dependency, API/client contract,
production prompt/profile/graph/gate or human checkpoint changes. This operator
diagnostic is not an additional mandatory step in the normal production flow.

## Qualification

Tracked authored tests cover whole-field identity, full-context retention, procedure
definitions, editorial/mixed/ambiguous holds, unavailable sources, missing scope,
bad bindings, multi-batch inventory, explicit semantic limits, source drift, safe
publication and read-only SQLite behavior. The five newly admitted reviews within
the existing registered probe contract are verified separately with live calls and
database access blocked. The seven other reviews remain unsupported by this path.

See the [implementation and acceptance report](../handoffs/assessment-intake-integration-2026-11-12.md).
Step 19 remains IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.
