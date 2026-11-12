# ADR 0049: Source-bound assessment completion and read-only publication

- Status: Accepted; narrow authored-fixture/probe implementation
- Date: 2026-11-12
- Builds on: ADRs 0041–0043 and 0046–0048

## Problem

The ordinary-review intake can produce pending assessment work, and native binding
and completion can validate authored responses. No supported application boundary
previously published those completions. The registered B archive exporter has a
different, deliberately restricted provenance contract and must remain unchanged.

## Decision

Implement the pure `evaluations.assessment_completion` component, the read-only
application service and `scripts/assessment_completion.py`. `prepare` publishes
exact offline inputs and a deliberately incomplete authored submission template;
`publish` accepts the completed submission and produces a completion bundle.
Both use the same source authentication and immutable-publication boundary.

Publish one complete original work item at a time, preserving the exact intake,
full source context, declarations, work briefs, holds and unselected fields. Reuse
the existing assessment binder and completion validator. Do not select more claims,
split whole claims, repartition work or infer new scope at publication.

Initially accept only **authored_fixture assessment submissions** over
**registered diagnostic_probe intake sources**. Authenticate original reviews
through the existing registered probe collector, including its preparation/live
closures and external parent lineage. Compare the recollected source and recompiled
intake against the saved bundle and exact submitted source pins. The bundle's hashes
are consistency checks, not an independent root of trust. No public trust-pin override.

Source authentication, new response origin and derived completion are separate
facts. A real archived critic source does not make an authored assessment response
a model delivery. Caller-provided receipts, binding flags, completion, token usage,
support approval and writer permission are forbidden. An origin label, Python type
or matching hash cannot establish provider provenance.

Use the native parser and [authored submission schema](../contracts/assessment-authored-submission-1.schema.json).
The JSON schema documents shape; source authentication and native result binding
remain application decisions. All discriminators are explicit and required. The
earlier `*-design-1` contracts remain historical previews and are not accepted by
the application parser. Existing raw authored responses are reused unchanged under
new explicit application input hashes; old previews are never rewritten.

For each original batch, regenerate an exact UTF-8 offline input document containing
the full unchanged work, declarations, briefs, active units and response schema.
Require its digest to match the authored attempt. Generate synthetic receipts
internally; then bind every raw response and recompute whole-work completion.
Require every batch exactly once, complete delivery **and** complete binding.
Never publish a successful subset of an invalid or incomplete work item.

Publish `bound_unassessed`, with semantic interpretation, evidence adequacy, factual
support, editorial effect, edit necessity and craft explicitly unassessed and writer
permission false. Citation binding does not prove adequacy; declared scope is not
a whitelist. Preserve existing cardinality and namespace rules. Authored usage is
`not_applicable_no_inference`, with null token fields, synthetic zero elapsed time
and independently recorded zero live calls. Native unknown-usage counters must not
be reported as real inference cost or missing provider telemetry.

## Publisher contract

The application service derives a complete envelope before any publication,
run secret checks without redacting the bound bytes, and re-collect sources before
writing the final manifest. Fixed output names are `intake.json`, `submission.json`,
`source-receipt.json`, `envelope.json`, `view.md` and `manifest.json`. The literal
Markdown view retains the complete envelope and prominent authored-origin notice.

The completion manifest records hashes of the other five files, source bindings, canonical
envelope hash and implementation identity. It is written last. Explicit local paths
stay outside the submission data. Refuse linked paths, overlap with protected source
trees or input files, traversal, partial/changed/extra output and nonexclusive writes.
An exact repeat verifies every byte without rewriting files. A partial publication
is not complete and is never silently reused, repaired or deleted. There is no claim
of a filesystem-wide atomic snapshot; source changes observed at either check refuse
completion. Detailed bounds and implementation acceptance checks are in the report.

Preparation writes `input-NN.json`, `submission.template.json` and its own
`assessment-authored-preparation-1` manifest. Its state is `authored_inputs_only`;
blank author/raw-final fields deliberately fail submission validation. Copy the
template outside the immutable preparation directory before authoring. Preparation
does not produce a completion or change a prompt.

This design does not widen the registered B exporter or create a workflow route,
database schema, automatic assessment gate or additional mandatory human checkpoint.

## Deferred branches and consequences

`authenticated_model_delivery` requires a separately qualified adapter that binds
the exact saved provider request, transport/terminal evidence, raw response and
honest usage to the same source/work/batch. Failed, truncated or missing deliveries
must retain their failure and unknown usage rather than acquire synthetic receipts.
Model inference remains a separately budgeted and approved activity. The initial
submission contract rejects this origin entirely.

The existing intake supports saved production reviews; this first completion slice
does not yet qualify that source branch. It needs an isolated read-only database
qualification before inclusion. No real database is inspected by this component.

The design is checked on the same six claims and explicitly authored data. It adds
no evidence of model reliability, necessary revision or story quality. Natural
negative and fresh-family gaps remain. Human assessment of feel, flow, character
and story-breaking effects remains separate from mechanical completion.

See the [original design](../handoffs/assessment-completion-design-2026-11-12.md)
and [implementation report](../handoffs/assessment-completion-publisher-2026-11-12.md).
Step 19 IN PROGRESS; Step 20 NOT STARTED. Production prompts unchanged;
live calls PAUSED; canary ON HOLD.
