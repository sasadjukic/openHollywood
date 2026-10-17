# Critic routing and writer boundary framing: frozen local plan

Date: 2026-10-17. **PREPARED LOCALLY; LIVE EXECUTION NOT AUTHORIZED OR STARTED.**
Full workflow canary: **ON HOLD**. Production remains prompt 61 / graph 9 /
fulfillment policy 1. Step 19 is IN PROGRESS; Step 20 is NOT STARTED.

This implements the preparation authorized after the
[diagnosis and proposal](../handoffs/fulfillment-routing-ending-next-experiment-2026-10-17.md).
Both treatments exist only in the private diagnostic harness. The immutable source
reviews, production prompts, schemas, validators, runtime and canonical artifacts
are unchanged. Preparation made **zero inference, discovery or external network calls**.

## Frozen identity and reviewable artifacts

Private bundle: `data/diagnostics/fulfillment-routing-framing-v61-2026-10-17/`.
Source commit: `18ca05abba476524d7af38a1266f1b8a6ba57f97`.

Plan SHA-256: `cf143f6a1ee077a9c8c24b426b90009805b1d9897a517cb2782afdcf7cc4eb37`.

The plan binds six complete critic cases, two complete fixed writer sources,
32 exact static first requests, the 40-probe schedule, scoring rules, source seals,
six harness scripts and their imported code (121 files total), plus 1,002 final
fake-harness evidence files. `request-differences.json`
records every paired first/retry difference. `writer-sources.json` preserves full
source prose, artifacts, raw review, receipt, audit and ordinary fulfillment packet.
The eight post-review bodies and any structural retry depend on returned output;
their builders are frozen now, and each actual full body must be saved and hashed
before future dispatch. Mock bodies are verification evidence, not live inputs.

`preparation-closure.json` binds the plan, local checks, frozen report and tracker
snapshot. Diagnostic artifacts contain unpublished prose and remain under the
repository's ignored local `data/` directory. No `approval.json` or live-output
directory exists at freeze. Historical approvals and unused call slots do not apply.

## A. Critic route index

Run six cases at seeds **19301, 19303**, each with ordinary **C0** and diagnostic
**C1**. At 19301 use C0 then C1; at 19303 use C1 then C0. Within each seed use this
case order, preserving the exact sealed contrast-bundle artifact versions:

| Case | Turning point | Outcome | Boundary | Normalized verdict |
| --- | --- | --- | --- | --- |
| Elena clean | met | met | no overrun | pass |
| Elena separate established match | met | met | overrun | revise |
| Elena embedded established match | met | met | overrun | revise |
| Elena missing decision | met | unmet | no overrun | revise |
| Elena complete compound outcome | met | unmet | overrun | revise |
| Elara embedded entry | met | met | overrun | revise |

These are evaluator expectations, **never model-facing answers**. All 24 probes run
irrespective of semantic or structural results, subject to global stop rules.

C1 inserts only `critic_route_index`, immediately after `assignment` in the user
JSON, on both first and structural retry requests. Compact JSON formatting, all
other fields, system text, output schema, source catalog, settings and normal
structural-repair feedback remain identical. The index is conditional on the
model's own findings:

- Native turning point/outcome: `assignment_checks` only; only an unmet check owns
  `assignment:<anchor>` conditions. Do not turn met into unmet to create a route.
- Generic assignment mismatch: `assignment_violations`, with the schema's exact
  enum: `assigned_character_ids`, `location_id`, `scene_id`.
- Endpoint overrun: `scene_boundary_check`; only an actual overrun enables the
  `boundary` link. Boundary advice remains application-owned; no model-authored
  boundary condition record.
- Viewpoint: `point_of_view_check` and its existing `viewpoint` condition owner.
- Generic repetition: an actually reported blocking finding, exact link, null
  recommendation and reused conditions/application policy.
- Independent craft: ordinary issue, null assignment link, its own supported
  recommendation and required comparison. Preserve compound obligations and
  legitimate consolidation; do not suppress craft in fulfilled passages.

The exact full wording is in the 12 C1 static requests and paired-difference file.
There is no failed-clause diagnostic, raw rejected-response feedback, native-status
freezing, semantic answer key or extra retry.

Inspect every raw attempt and normalized receipt. Record first/final validity,
routing failures, native statuses, raw/normalized verdicts, source/condition support,
generic repetitions, independent craft and retry drift separately. A promising
signal requires fewer routing-failed probes than concurrent C0 **and all 12 C1
reviews correctly classified and supported**, without losing clean/missing/compound
controls. Also report attempt-level failures. Perfect C0 is non-reproduction;
structural recovery with semantic failure does not qualify.

For advice support, a pending comparison can satisfy “no match established.” An
explicitly optional inconclusive/negative example differs from requiring either
result as the only repair. The latter is overrestrictive when an unfinished
comparison also meets the approved requirement. An exact source quote alone does
not establish entailment. Report any interpretive uncertainty rather than hiding it
in a binary validity result.

## B. Writer boundary framing

Run two fixed sources at **19301, 19303**, with **W0** and **W1**, then one ordinary
post-critic for each valid writer. Within each seed, separate entry precedes
embedded entry. W0 precedes W1 at 19301; W1 precedes W0 at 19303. Each post-review
immediately follows its writer. New critic results from A never select these sources.

| Source case | Ordinary review | Successful attempt |
| --- | --- | ---: |
| Separate entry | October 16 `s19101-elara-separate-initial` | 2 |
| Embedded entry | October 17 `s19201-elara-embedded-initial` | 1 |

Both saved reviews replay through ordinary validators, certify both native facts
and contain only a boundary repair. The separate review's raw verdict is `reject`,
normalized ordinarily to `revise`; it is not silently changed in the frozen source.
The embedded review's outcome evidence includes the composite sentence containing
the forbidden entry. This is the necessary-edit-inside-cited-prose control.

Both arms receive the same exact version-bound fulfillment packet through the
existing production projector. W0 is the ordinary request. W1 changes only these
three fields in the single allowlisted boundary acceptance test:

| Field | W0 | W1 |
| --- | --- | --- |
| `category` | `scene_assignment:outcome` | `scene_boundary:exit_state` |
| `claim` opening | `Assigned outcome: "<exact outcome>".` | `Assigned exit state: "<exact exit state>".` |
| `requested_change` first sentence | “Restore the current scene's planned outcome and exit state: remove unassigned material advancement, not merely a later detail of an already established result.” | “Repair the violated current exit state: remove unassigned material advancement, not merely a later detail of an already established result.” |

The remaining claim, achieved/current/next comparisons, restatement, recommendation
suffix, evidence, IDs, severity, `accept_when`, positive packet and all other request
fields remain identical. W1 is labelled a diagnostic request projection in local
provenance; the canonical Critique is unchanged. Its projector authenticates the
entire ordinary view and exact allowlisted source artifacts before changing fields.
Native unmet conditions, mixed repairs, independent craft, extra tests, altered
packets, unknown sources or invalid receipts are rejected rather than removed.

Post-critics remain ordinary v61, using the full original feedback/tests, no W1
projection, no route index and no positive packet. Identical paired revised drafts
produce identical post-critic requests. There is no second prose revision.

Inspect all complete prose and diffs. First establish structural validity, boundary
repair and fulfilled facts. Then record new explicit restatement, changes outside
citations, necessary changes inside citations, unrelated ending edits, benign edits
and craft tradeoffs. The imminent-step sentence is compatible with remaining outside;
changing it is not required by this defect, but may still have artistic merit.
Punctuation repair is not automatically a loss; a larger rewrite with a concrete
craft benefit and an unrelated cost is mixed. Exact clean restoration and quotation
retention are descriptive, never quality gates.

Report four pairs as wins/ties/losses/mixed. Invalid or factual failures remain in
all-probe coverage and cannot count as preservation wins. A promising signal needs
**at least 3/4 preservation wins, including one in each case**, with no factual
regression or embedded-defect repair failure. Shared rewrites/ties confer no benefit.
Archive full originals and anonymous A/B revisions with a private deterministic
order key. Assistant inspection and mock exports are not blind human review.

## Budget, destination and stopping

| Block | Primary probes | Maximum attempts |
| --- | ---: | ---: |
| Critic routes: 6 cases × 2 arms × 2 seeds | 24 | 48 |
| Writers: 2 cases × 2 arms × 2 seeds | 8 | 16 |
| Ordinary post-critics | 8 | 16 |
| **Total** | **40** | **80** |

The **48-call critic block and 32-call writer/post block are nontransferable**.
Writer and post stages also have independent 16-attempt ceilings. Each probe permits
at most one structural retry, never a third attempt. A terminally invalid writer
skips only its own post-review; there are no replacements or reassigned slots.

Model: `gemma4:31b-cloud`, recorded digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Digest discovery/verification occurs only after separate live approval. Temperature
0.2 critic / 0.85 writer; top-p 0.95; thinking off. Each attempt allows 24,000 input
and 8,000 output tokens, with a 900-second timeout. Maximum reservation:
**1,920,000 input / 640,000 output tokens / 72,000 active seconds**.

The application retains its USD 0.20 per-call admission placeholder; this is not a
known provider charge. At the historical October 8 rates (USD 0.14/M input,
0.40/M output), the maximum estimate is **USD 0.52480**. Actual billed charges are
unknown; no current-price or enforceable billed-dollar claim is made.

Future execution sends **complete unpublished fictional prose, critique, Blueprint,
Scene Plan, Story Bible and diagnostic story context to Ollama Cloud through the
local Ollama daemon**. Local forwarding does not make inference local. Future
approval must bind this payload/destination, the exact plan hash, 80-call ceiling
and `full_workflow_canary_authorized=false` before gateway construction or discovery.
The plan's preparation authorization does not authorize that transmission.

Run sequentially. Persist full exact requests and durable hashed reservations
before dispatch, then capture complete raw responses, usage and outcomes. Failed,
cancelled and unknown dispatches consume their reservations. Stop on transport/auth,
model identity, integrity, budget, cancellation or unknown outcome. No automatic
transport retry or continuation from an incomplete probe. Completed replay uses
zero calls. Do not add roles, cases, semantic rerolls, canonical writes or full stories.

## Verification and remaining qualification

- Replayed all 32 prior receipts / 35 attempts, including failed attempts, and both
  fixed writer sources; verified predecessor code, preparation and live seals.
- Validated all 40 stage fixtures; checked all 32 static retry requests, 32 paired
  first/retry differences and four identical-output post-review pairs.
- Rejected 26 unsupported source/view variants. Four ordinary craft transmission
  checks preserve independent craft alongside positive evidence and original post
  feedback. The embedded fixture requires editing cited prose to repair the defect.
- Full fake-provider matrices verify structural recovery at critic/writer/post
  stages, a terminal critic failure, a valid wrong judgment, a terminal writer and
  its sole post skip, zero-call completed replay, all ceilings, order/identity/request
  guards, missing/old approval, unknown/incomplete outcomes and failure stops.
  The final run used **87 fake dispatches across independent ledgers**: 43 in the
  valid matrix, 41 in the fault matrix and three failure-dispatch fixtures.
  These are offline fixtures; they consume none of the future 80 live-call allowance.
- Focused regression suite: **91 passed**. Repository Ruff lint/format and strict
  mypy pass for 201 files; all six private scripts pass Ruff lint/format. No client
  changes, so frontend/build checks are not applicable to this diagnostic preparation.

The Windows sandbox blocked the first pytest temporary-directory setup and local
asyncio initialization. Final offline checks used a fresh workspace test directory
and permitted local event-loop initialization; the fake-provider harness blocks
network connects and real Ollama gateway construction during its exercise.

The two candidates test different hypotheses independently. C1 has no matched-length
placebo. W1 bundles three framing fields and cannot isolate which field matters.
The embedded writer control tests necessary repair, **not live independent craft
improvement in a met passage**. That qualification and blind human review remain
pending even if both comparisons succeed. Preservation is not a new literary score:
voice, character, tension and dialogue may justify edits in fulfilled passages.
There are no locked spans or extra explicit-decision requirements.

Complete-story quality still requires the accepted rubric/hard gates, full Cloud
corpus and comparable single-model baseline. No new normal-workflow human checkpoint
is introduced. **Canary ON HOLD; no production promotion from these diagnostics.**
