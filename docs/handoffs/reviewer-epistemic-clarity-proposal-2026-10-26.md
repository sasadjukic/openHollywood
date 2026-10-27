# Proposed high-thinking epistemic-clarity comparison

Date: 2026-10-26. **PROPOSAL ONLY: 32 calls maximum. Not prepared, frozen or
approved for inference.**

This follows the [local epistemic/scope audit](reviewer-epistemic-scope-audit-2026-10-26.md).
The audit found actual overlap between the legacy definitions of `unsupported`
and `uncertain`, affecting fourteen of sixteen uncertain-source target responses.
It also preserved one conditional answer that misses the frozen observed-instance
target. The next test should address this measurement problem before treating
those labels as evidence of a general model reasoning deficit.

## Question and isolated change

Does removing the factual-label overlap improve consistent evidence-status
reporting under **high thinking**, while preserving the recovered factual relations,
assignment checks and defensible craft judgments?

| Arm | Proposed treatment |
| --- | --- |
| TH | Unchanged NC instructions and response contract with `think: "high"`; contemporary control |
| EC | Same high-thinking request, changing only the system definitions of factual `unsupported` and `uncertain` to make them disjoint |

EC would reserve unsupported for a source-refuted material factual premise and
uncertain for a material proposition that is neither established nor refuted,
including expressly unresolved alternatives. Supported and the qualified-craft
standard remain unchanged. The existing component schema, evidence registry,
eight-reference whole-claim union, 2,000 summed reason-character bound and
application-owned whole-claim aggregation remain unchanged.

Do not add another output enum, a premise-decomposition arm, a new conditional
instruction, a reasoning-effort arm or a writer treatment. The intervention is
clarification of an overlapping instrument, not a repetition of the earlier ES
enum experiment. That experiment changed target vocabulary under non-thinking;
this one holds the demonstrated high-thinking mode fixed and keeps the schema.
The observed/conditional contrasts below are inputs shared by both arms.

Exact revised wording and the allowed message diff must be frozen during local
preparation. This proposal does not modify a prompt file or create requests.

## Proposed matrix

**Eight full-scene families × two presentation orders × two arms = 32 attempts,
sixteen per arm, zero retries.** Keep paired arms adjacent and balance which arm
is first: eight TH-first and eight EC-first pairs.

| Family | Purpose |
| --- | --- |
| Existing H observatory | Preserve the recovered factual-status versus intention/rule distinction and craft controls |
| Existing F3 reservoir cards | Reproduce explicit uncertainty and the historical conditional-scope failure |
| Existing G5 radio ledger | Preserve absent measurement timing versus presentation order |
| Fresh J1 full scene | Opposite depictions with explicitly unresolved common timing |
| Fresh J2 full scene | Opposite observations with no timing information |
| Fresh J3 full scene | Genuine incompatible literal states at an explicitly identical instant |
| Fresh J4 full scene | Compatible opposite states at explicitly different times |
| Fresh J5 full scene | Authorization status versus early action, with separate real obligation/intention conflicts |

The six known-family TH control requests should remain byte-identical to their
historical high-thinking counterparts, subject to a matching execution baseline.
Any unavoidable baseline/request change requires an explicit amendment before
inference; it must not be hidden behind the word unchanged.

Fresh scenes should vary character goals, relationships and narrative shape,
rather than merely renaming the earlier discovery-and-relative template. Retain
full original/revision/context, assignment and qualified-craft checks. They are
authored fixtures; no writer generation is included.

In J1–J4, supply **separate material components** for:

- An explicit claim about what these particular observations actually establish.
- The conditional claim that mutually exclusive literal states of the same
  referent at the same instant cannot both hold.

Use identical source packets, claims and component maps in TH and EC. Do not
state the gold answer or provide labeled premise statuses to either model.
Unknown-instance cases should allow a supported conditional alongside an
uncertain actual-instance claim; the genuine and sequential controls prevent
“always uncertain” from looking successful. The existing F3 wording stays intact
in the historical control; the fresh contrast tests transfer to explicit scope.

Preparation must verify that complete material evidence fits the unchanged union
and reason limits. If it cannot, revise the proposed case design before freezing,
not the evidence cap after results arrive. Final case text, component counts and
source witnesses are not frozen by this proposal.

## Proposed evaluation and decision rules

Keep two conclusions separate:

1. **Contract alignment:** EC returns the intended uncertainty label with accurate,
   complete reasons where TH gives a grounded unestablished explanation labeled
   unsupported. Count this as clearer label alignment, not a newly discovered
   fact or reasoning recovery. Seek at least six paired alignment opportunities
   across F3/G5/J1/J2, with both orders in at least two families; otherwise disclose
   insufficient paired opportunity. Historical failures cannot supply missing
   contemporary opportunities.
2. **Observed-scope recovery:** a control actually accepts an unestablished observed
   relation or substitutes a conditional for it, and EC gives a grounded complete
   answer to the actual proposition. Claim a replicated scope-recovery signal only
   with contemporary errors in at least two families including a fresh one, both
   recovered without a new converse error. If the failure does not recur, report
   that it was not reproduced; label alignment alone does not prove this recovery.

For a useful contract candidate, propose requiring all sixteen EC reports valid,
all eight EC uncertainty targets usable, all eight H/J3/J4/J5 preservation targets
usable, and all eight fresh conditional components usable. Also require no
protected paired losses in previously usable whole claims, non-target components,
craft/assignment labels or grounded complete explanations/citations. Record
overlapping losses as overlapping. These are small-sample diagnostic screens,
not production qualification.

Report frozen primary labels and source-adjudicated semantic behavior separately.
Preserve the legacy control's permitted unsupported-as-unestablished reading;
do not describe it as an invented negative fact. Score actual conditional
substitution, invented timing, assignment-label inversions, delivery and missing
evidence separately. Invalid responses stay in attempted denominators and receive
no semantic credit. A partial run cannot advance.

Mask final assessments before source inspection and seal notes before decoding
the key. Exclude thinking text, arm/order identifiers and resource observations;
disclose partial masking. Capture latency, reported input/generated/cached tokens,
available timing splits and time/tokens per completely usable report. Missing
reasoning-token breakdowns remain unknown. No arbitrary speed threshold is added.

## Proposed budget and stops

- **32 attempts maximum**, sixteen per arm, one per cell, no retries or replacements.
- Both arms use the same selected DeepSeek cloud tag and `think: "high"`.
- Retain the shared requested temperature 0.2, top-p 0.95, seed 20261022,
  non-streaming transport and no provider format override.
- Per call: **24,000 input / 16,000 total generated tokens / 600 active seconds**;
  requested context 40,000. Thinking and final output share the generation cap.
- Aggregate reservations: **768,000 input / 512,000 generated tokens / 19,200
  active seconds**. These are ceilings, not forecasts or a billing guarantee.
- First eight cells: F3/G5, both orders and both arms, included in the ceiling.
  Stop if either arm has zero valid deliveries in its four attempts or EC repeats
  the same blocking delivery signature across both sentinel families. No semantic
  early stopping or budget reallocation.
- Preserve the established global terminal stops for non-200/transport/gateway
  failure, truncation/incomplete response, missing or excessive usage, invalid
  supplied timing/breakdowns, absent high-thinking observation, time breach,
  daemon/model drift, tampering, cancellation or ambiguous dispatch. Preserve raw
  errors, reservations and known/unknown usage; do not resume a terminal cell.

The last observed daemon version was 0.40.11 in the prior run. This audit made no
new daemon query. Local preparation should obtain metadata-only observations,
verify the current baseline, freeze exact cases/requests/scoring/stops, exercise
all dispatches through mocks, and present the plan before live approval. Cost
estimates must remain explicitly separate from confirmed billing.

## What this would authorize later

Nothing live is authorized now. The next step, if chosen, is local preparation
and verification of this 32-call plan. Inference requires separate approval of
the frozen budget, payload and Ollama Cloud destination.

Even a clean result would support a diagnostic interface and consideration of
selective high-thinking claim verification. It would not establish improved
writing, justify thinking in every role, remove the Blueprint checkpoint, enable
production routing, or release the canary. Lower-thinking efficiency, provider
attribution and writer tests remain separate questions. Humans retain overall
feel/emotion, flow, character and story-breaking review with machine-prepared
mechanical evidence.

**Production prompts unchanged; no selective-thinking rollout; live calls PAUSED;
full workflow canary ON HOLD.**
