# Material-claim assessment comparison — proposal, 2026-10-24

Status: **provisional 36-call design; not prepared, frozen or approved for inference**.
The [local audit](reviewer-whole-claim-audit-2026-10-24.md) is complete. Production
**prompt 61 / graph 9 / fulfillment policy 1** and the existing workflow remain
unchanged. The full workflow canary stays **ON HOLD**.

## Question and isolated change

Does requiring a brief, visible assessment of the supplied claim's material
premises help the model judge that exact claim, without losing grounded literary
criticism or inventing additional facts in its explanation?

The preceding premise-check arm asked for a general factual check while generating
a full review. The completed fixed-claim diagnostic simplified the task but still
allowed reasons to excuse false wording and endorse a looser core. The proposed
change makes the evidence assessment observable in the **existing `reason` field**.
It does not add a model, a second verification call, an evidence enum or a new schema.

| Arm | Proposed behavior |
| --- | --- |
| CV | Exact existing fixed-claim system/contract, schema and settings |
| MC | Same request plus one diagnostic instruction requiring brief source-based checks of material factual assertions, a separate grounded craft assessment where relevant, and a verdict on the entire claim as worded |

MC's reason should identify whether the material assertions are supported,
contradicted, not established as claimed, or genuinely unresolved. It must not
replace the supplied proposition with a plausible core, broaden a condition to a
different action, or treat non-unique literary taste as a factual defect. This is
a short evidence summary, not a request for an internal reasoning trace. The
existing 2,000-character reason limit, eight-reference maximum and all output
fields remain unchanged. No exact instruction text is authored or changed in this
local audit; preparation would freeze it for review before inference.

The experiment tests the instruction package's observable effect. It cannot prove
the order or nature of internal reasoning. Delivery and reason completeness must
be reported separately, since the new instruction could increase output burden.

## Proposed matrix: 36 calls, zero retries

**Nine families × two arms × two source orders = 36 attempts**, eighteen per arm.
Each response still assesses three claims: **27 unique claims and 108 attempted
claim judgments**. Repeated claims and closely related families are not independent
samples.

- Keep H/B/G/K/L/M complete source packets and all eighteen claims unchanged.
  CV wire payloads for these twelve family/order cells must match the first
  repetition of the preceding run exactly; administrative execution IDs may differ.
  Retain L and M as positive controls rather than testing only prior failures.
- Add three new scene families, provisionally a floodgate inspection, a bookbinding
  workshop and a seed archive. Cover compatible factual status versus a real
  prerequisite violation; explaining versus deciding/action; and original/revision
  ownership. Exact stories and claims are future preparation work.
- Each fresh family supplies one explicit false factual claim and two supported
  controls, retaining genuine constraints and a defensible craft interpretation.
  Include matched phrasing that distinguishes a formal condition from a qualified
  impression and within-revision events from across-version comparison.
- Use both original/revision and revision/original presentation orders. Balance arm
  order across cells. No extra exact repetitions: the preceding run already showed
  matching labels in all ten pairs with both deliveries valid. New context and a
  contemporaneous control are more informative within this allowance.

Keep complete prose/context, versioned catalogs, claim positions, temperature 0.2,
top-p 0.95, seed 20261022, thinking=false and the existing DeepSeek tag unchanged.
Do not add demonstrations, gold excerpts, material-clause annotations or historical
judgments to requests. The model must identify the premises itself.

The last verified metadata is **Ollama 0.40.10 / DeepSeek**. No discovery occurred in
this audit. Preparation must explicitly pin the accepted baseline; approved live
preflight must match it or stop. No silent model/version refresh.

## Proposed scoring and decision rules

Freeze source-bound expected labels, material-scope annotations and full-reason
inspection rules before any call. Retain exact historical gold for the unchanged
claims, and disclose B/C03 and G/C03 as **secondary scope-sensitive probes**. Report
their labels, reasons and historical-gold correctness separately; do not use them
to decide factual recovery or claim a newly proven model failure.

This leaves **25 unambiguous claims × two orders = 50 primary claim opportunities
per arm**, plus four secondary opportunities. Primary opportunities comprise 32
supported and eighteen unsupported judgments per arm. Delivery failures count for
every affected opportunity; no trimming, repair, normalization or silent omission.

Report valid delivery, exact labels, abstentions, entire-reason support, citation
support and fully usable claims separately. A correct label with an unsupported
new explanation remains unusable. Retain all-three historical-gold usability as a
descriptive secondary metric; it must not hide the scope caveats. Representative
citations remain assessed against the complete source, with no new demand that
every incidental observation receive its own citation.

Proposed screen for retaining MC as promising evidence:

1. At least **17/18 valid responses**, including **5/6 fresh responses**, and no
   paired loss of a valid CV delivery.
2. At least **four paired primary claim recoveries across two families**. Count a
   recovery only when both responses are valid, CV fails the exact label or whole
   explanation, and MC is fully usable. Include one unchanged claim recovered in
   both orders and at least one recovery in a fresh family. Invalid-to-valid gains
   are delivery gains, not semantic recoveries.
3. No paired loss of a usable primary CV claim, and no newly rejected or abstained
   supported control where CV was correctly supported. No additional unsupported
   explanation in a primary MC claim that CV handled with a grounded reason.

If valid CV failures do not provide the required recovery opportunities, report
**insufficient opportunity** without adding cases, calls or retries. Independent
delivery or protected-control failures still count; they cannot be hidden by that
label. Report matched outcomes by family, origin and order, not only aggregate
percentages. The thresholds are a small diagnostic screen, not a statistical
generalization or a production qualification standard.

Mask arm/order identifiers during source inspection as far as possible, seal notes
before decoding, and acknowledge that the reason style may reveal treatment.
Inspect all returned reasons and both invalid and valid deliveries. No new human
review of near-identical samples is required for this factual diagnostic.

## Proposed ceilings and stops

| Resource | Proposed ceiling |
| --- | ---: |
| Total attempts / per arm | **36 / 18** |
| Retries or repair calls | **0** |
| Input / output per call | 24,000 / 8,000 tokens |
| Aggregate input / output | 864,000 / 288,000 tokens |
| Active time per call / aggregate | 300 / 10,800 seconds |
| Archived-rate reservation / planning allowance | **$0.60480 / $0.75** |

The estimate uses the previously archived rates, not a fresh price lookup or a
provider-enforced spend cap. Actual billing remains unknown.

Use the first eight calls for H and the fresh status/condition family, both arms
and orders. Stop if either arm delivers zero valid responses, or the same structural
failure appears at least three times across both families. A single structurally
invalid normal-stop response consumes its attempt and receives no retry.

Stop the run on non-200 responses, transport errors, timeout, cancellation,
truncation/non-stop completion, unexpected thinking, missing/invalid/excess usage,
version/model drift, source/request/capture tampering or incomplete terminal
evidence. Count every dispatched attempt, including those with unknown usage.
Preserve the gateway error chain and durable initial/before/after version capture.
No terminal continuation or transferred allowance; resume after a clean cell
boundary only within the untouched frozen remainder and original ceiling.

## Conditions before execution and after a positive result

Local preparation must create exact fresh cases, scope-audited claims, both arms'
requests, wire-payload checks, scoring/stop tests and a sealed plan. Verify historical
CV equivalence, the diagnostic-only treatment diff and zero changes to production
prompts. Present the frozen plan before seeking separate live approval for full
unpublished prose/context to Ollama Cloud through the local daemon.

Even a positive result would support a later, separately designed full-review
integration comparison. It would not qualify an automatic verifier, authorize a
writer or establish better story quality. Preserve the nine human ties; future
quality work still needs reader judgments of feel, flow, character and story-breaking
problems, with mechanical evidence prepared by the application.

Provider investigation remains deferred. **No new inference is authorized by this
proposal; Step 19 remains IN PROGRESS, Step 20 NOT STARTED, and the canary ON HOLD.**
