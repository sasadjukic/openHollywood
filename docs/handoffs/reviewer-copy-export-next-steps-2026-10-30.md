# Proposed next step: audit saved ordinary-critic probe provenance

Date: **2026-10-30**. **PROPOSAL ONLY.** Inference **PAUSED**, production prompts
unchanged, canary **ON HOLD**. Proposed model/daemon call budget: **zero**.

The [tracked operator export](reviewer-copy-export-results-2026-10-30.md) is
locally qualified. Its workspace inventory found no compatible SQLite reviews.
Repeating the same inventory or creating new reviews solely to populate the
export would not resolve a model-behavior question.

The [October 16 ordinary-v61 comparison](../benchmark_reports/production-fulfillment-v61-results-2026-10-16.md)
already records seventeen validated critic reviews in
`data/diagnostics/production-fulfillment-v61-2026-10-16-live/`, with preparation
and approval records in the sibling prepared directory. Their ordinary critic
contract makes them a possible source for mechanical review assistance, while
their probe origin makes them distinct from actual saved production invocations.

Recommended bounded local pass:

1. **Inventory the existing successful critic captures and pin at most twelve
   exact trial IDs before inspecting their prose.** Cover clean controls,
   unmet controls, embedded-defect judgments and both writer-arm post-reviews
   where available. Keep failed attempts excluded and linked to their successful
   retry where applicable; do not replace missing cells or change sealed scores.
2. **Audit completeness of each selected capture.** Require the frozen request,
   full source packet and its version/hash bindings, exact response, validation
   outcome, selected draft handles, saved native checks and successful-attempt
   identity. Establish what was shown versus recovered locally. Report missing
   provenance explicitly; never infer it from similar wording or a passing label.
3. **Decide whether a separately labeled adapter is warranted.** If enough exact
   evidence survives, specify a `diagnostic_probe` source contract that can reuse
   the deterministic comparison core. Preserve the original probe/trial identity
   and full original review. Do not mint a canonical critique version, a successful
   production invocation, or a completed workflow to make the existing SQLite
   adapter accept it. If required evidence is absent, retain the coverage gap.
4. **Report a concrete semantic-selection question only if the evidence supports
   one.** Separate correct handle resolution from whether the selected passage
   supports the complete obligation. Keep attribution, negation, event truth and
   endpoint scope explicit. Record a specific observed failure and source ground
   truth before proposing any new live comparison.

This proposal does not add another live experiment or request set. Any later
inference needs its own materially different hypothesis, frozen controls,
scoring, stops and explicit approval. Exact text comparison remains mechanical
assistance for human review, not a story-quality score or writer repair gate.
