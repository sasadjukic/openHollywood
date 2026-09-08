# ADR 0007: Bounded terminal continuity adjudication

- Status: Accepted
- Date: 2026-09-08

## Context

The v25 canary retained a Local continuity allegation whose selected historical
claim did not imply the alleged obligation. Exact IDs and quotes validate
provenance, not semantic incompatibility. Additional rewriting can distort an
otherwise approved scene and does not guarantee a better continuity decision.

## Decision

Production graph v6 registers `continuity_adjudication` at the existing revision
cap, only when a non-world contradiction remains and no hard critic blocker
remains. It reuses the continuity-supervisor role and existing Local/Cloud/Hybrid
profile routing, not an unconstrained additional agent or a new human checkpoint.

The node reviews the same immutable candidate, exact disputed findings, selected
canonical claims, current-scene assignment, and bounded review history. Previous
reviewer advice is not canonical authority. The compact keyed response must
adjudicate every disputed finding exactly once and cite exact current evidence.
Supported incompatibilities and uncertainty stay blocking. Unsupported claims,
requirement-only demands, compatible developments, and established repairs may
be made advisory. No prose is changed and no new finding may be introduced.

Other findings are copied unchanged. World Rules, missing requirements,
forbidden shortcuts, and hard critic gates cannot be released by this node.
The usual post-review acceptance checks still run. There is one adjudication
node visit per scene with at most two model attempts, subject to the existing
per-call and aggregate token/cost/time limits and cancellation. It creates an
immutable continuity report with exact input lineage and checkpoint references.
The maximum call/graph envelopes reserve this bounded work; the canary cost
ceiling and drafting revision cap are not increased.

## Consequences

- Unsupported terminal judgments can be reviewed without another draft rewrite.
- A valid adjudication is still a model judgment, not proof of semantic truth.
  False-positive and false-negative controls, live canaries, and blind human
  review remain required. The same profile can repeat the same mistaken judgment.
- Malformed decisions receive bounded repair; exhausted or uncertain reviews
  fail closed. Selected authority, assessment, disposition, and failure layer
  are retained in secret-redacted diagnostics.
- New executions use graph v6 / prompt v26. Older canary databases and checkpoints
  must not be retagged or resumed under the new graph. No persisted SQL schema
  change is required; graph state remains reference-only.
