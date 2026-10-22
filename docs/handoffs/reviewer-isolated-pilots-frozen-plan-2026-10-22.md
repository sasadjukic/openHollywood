# Frozen reviewer pilots: delivery, temporal scope and fulfillment vocabulary

Date: **2026-10-22**. Status: **FROZEN LOCALLY; AWAITING LIVE APPROVAL**.

This implements the [three-pilot proposal](reviewer-isolated-comparisons-proposal-2026-10-22.md)
following the [32-capture audit](reviewer-delivery-semantics-audit-2026-10-22.md).
The ceiling is **48 calls**, divided into three independent allowances of 16.
Preparation makes **zero inference and zero daemon discovery calls**. A read-only
public pricing check sent no prose or project context. No live approval record exists.

Production prompt **61**, graph **9**, fulfillment policy **1**, production schemas,
provider behavior and human checkpoints remain unchanged. The full workflow canary
stays **ON HOLD**. These are diagnostic prompt variants in a private local bundle.

## Frozen matrix

Each pilot has four packets × two arms × two presentation orders × one seed.
O always identifies the original and R the revision, even when R is displayed first.

| Pilot | Model | Control | Candidate | Case order; first two form the sentinel block | Calls |
| --- | --- | --- | --- | --- | ---: |
| D: delivery | `gemma4:31b-cloud` | C2 unchanged | D1: schema presentation order only | h02, F01, h03, F04 | 16 |
| T: temporal scope | `deepseek-v4.1-flash:cloud` | C2 unchanged | T1: one temporal-scope instruction addition | h04, F02, h03, F01 | 16 |
| R: fulfillment vocabulary | `deepseek-v4.1-flash:cloud` | C2 unchanged | R1: declared field/category renaming only | n03, F05, h03, F06 | 16 |

The complete schedule fixes all 48 dispatches. Pilots run D, T, R. Within a case,
the arms are adjacent for each presentation order. Which arm goes first and which
presentation order goes first are counterbalanced. Each eight-call sentinel covers
two different families and four answers per arm.

There are **nine unique packets**: four historical packets remain byte-equivalent
as canonical JSON, and five new authored micro-scenes use new scene families.
The shared h03 C2 control is intentionally repeated within T and R: **48 scheduled
cells contain 46 unique wire payloads**. Its pilot identity remains in the ledger,
not in a hidden model-message marker. Reused packets and the shared seed do not
become independent story samples.

Seed **20261022**, temperature **0.2**, top-p **0.95**, thinking **false** are fixed
for every cell. This seed also occurred in the historical C2 run; the concurrent
controls support the present comparisons, not a claim of independent seed replication.

## Exact treatment boundaries

**D1** aligns `properties` and `required` order at every object. The root order is:

```text
task_checks, fact_checks, endpoint_check, group_assessments, craft,
literary_comparison, mandatory_failure, mandatory_failure_assessment,
overall_assessment
```

Nested fields follow their existing required order. Membership, types, enum values,
limits and evidence requirements are identical to C2. System instructions, prose,
context, task IDs and the final-contract prose are unchanged. Output member order
is not a validity condition; duplicated fields still fail regardless of their values.

**T1** appends exactly this text to the C2 system instruction, changing no other message:

```text
TEMPORAL SCOPE CHECK
Separate whether an event occurred, whether a state continued for its required interval,
and whether the expressly assigned endpoint holds. Later withdrawal or departure does not
erase an earlier event, but can violate a continuing condition or the endpoint. A missing
earlier fact does not itself invalidate a separately satisfied final state. Require a
specific cause only where the assignment expressly requires that causal connection.
A forbidden transition can be logically coherent. Call statements contradictory only when
they assert incompatible facts about the same referent at the same time and within the same
narrative scope; distinguish successive states, character claims and uncertain narration.
Report each failure under its own requirement and ground the explanation in the full text.
```

This is one bundled temporal-scope instruction. The pilot cannot attribute an effect
to an individual sentence within it. Case names and expected answers are absent.

**R1** renames `request_relation` to `request_fulfillment` and uses this reversible
mapping, retaining the C2 definitions:

| C2 value | R1 value | Meaning retained |
| --- | --- | --- |
| `direct` | `fulfills` | Does what the requested task asks |
| `adjacent` | `supports_other_edit` | Supports another change |
| `unrelated` | `does_not_fulfill` | Does not carry out the task |
| `uncertain` | `uncertain` | One supported categorical judgment is unavailable |

The field and enums change in the schema. The system's category references change
consistently, with two grammatical adjustments: optional cleanup “has
request_fulfillment fulfills and is supported”; conditional cleanup “may have
request_fulfillment supports_other_edit and dependency on_unsupported_change.”
Ordinary uses of “unrelated changes” and “indirect narration” remain unchanged.
No new authorization policy is added. `edit_support`, `dependency`, all other
judgments, grouping, evidence rules and source messages are unchanged.

Strictly validate R1's own schema first. Only then map those declared aliases into
C2 names for paired analysis and masked inspection. Accept neither mixed schemas
nor old enum values in an R1 answer. This is vocabulary normalization, not repair
of duplicate keys, wrong identities, missing evidence or model judgments.

The local isolation checks compare every message transformation, preserve every
historical control message exactly, and confirm equal accepted schema constraints
for D1. No candidate change is shared with either other pilot.

## Cases, scope and scoring decisions

Full prose, contexts, assignments, catalogs, diffs and edit groups are frozen in the
[local casebook](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/casebook.md).
Fresh scene prose follows the [contrast design](reviewer-semantic-contrast-design-2026-10-22.md).
F03 and the other deferred contrasts have **no slots** in this freeze.

| Case | Required fact results; endpoint | Other frozen interpretation |
| --- | --- | --- |
| h02, Elara | Both retained; satisfied | Requested duplicate removed; supported direct repair |
| h03, Elena | Date realization lost, decision retained; satisfied | Required retention unmet. Root edit unsupported; callback cleanup depends on it. No cause-specific endpoint invented. |
| h04, safehouse | Both retained; violated | Departure breaches the endpoint without erasing discovery/truce or contradicting earlier staying. |
| n03, seed store | Discovery retained, agreement lost; satisfied | Refusal does not fulfill retention. Passing a pencil cannot prove the missing agreement. |
| F01, observatory | Both retained; satisfied | Optional exit fulfilled and permitted. Staying earlier and leaving later are compatible. |
| F02, tram depot | Both retained; satisfied | Same-time stillness and motion contradict. Identify that defect separately from the assigned discovery, decision and pre-contact endpoint. |
| F04, pottery | Both retained; satisfied | Exact no-op permitted by the optional request; no comparative loss. |
| F05, bakery | Both retained; satisfied | Optional duplicate repair fulfilled and supported. Optional does not mean unrelated. |
| F06, ferry office | Expiration discovery lost, decision retained; satisfied | Required retention unmet; separately requested optional duplicate removal met. Three complete groups have different permissions. |

F02 deliberately scopes its required task to the two facts and endpoint. Therefore
its `mandatory_failure` answer is **false**, while its new contradiction must be
identified in the explanation or overall assessment. This does not declare the
contradiction acceptable prose or change a production gate. It tests whether a
critic can identify a defect without routing it to an unrelated requirement.

F06 resolves a compound-request ambiguity before inference: retention is one required
task and duplicate removal a separate optional task. Both arms see these exact tasks.
Its three sentence groups, including complete source spans and exact token-operation
ownership, are: changing expiration (unsupported, does not fulfill retention),
removing the horn duplicate (supported, fulfills the repair), and changing the
callback (unsupported, supports the unauthorized root change). The unchanged C2
paragraph grouping remains in use for every other case. A correct small repair
does not make the whole revision acceptable, and a bad root does not erase that repair.

Machine scoring checks strict delivery, exact IDs/reference binding, bounded evidence,
declared labels and no-op invariance. Frozen inspection anchors bind quotations to
their original versions. These anchors and expected answers are **withheld** from
requests; absence claims and semantic support still require reading the full text.

Operator inspection checks every consequential explanation for source support,
scope, invented causes, false contradictions and comparative premises. Reviews are
shuffled and stripped of model/pilot/arm/seed/order labels. R1 field aliases are
normalized after validation; case membership or explanation wording may still reveal a condition.
Seal inspection notes before unmasking. This is masked operator inspection, not
independent human literary validation. Uncertain support is recorded and excluded
from primary usability; alternative readings remain separate sensitivity analyses.

For each pilot report delivery, labels, supported usability and paired OR/RO contrasts
separately. Invalid/truncated attempts remain failures. Unstarted slots after a stop
are unobserved, not failed or successful. Never pool partial gains across pilots.

The frozen advancement function requires:

1. All **8/8 candidate answers** delivered validly.
2. No loss of a paired control success: delivery for D, supported usability for T/R.
3. Supported, correct permissible/no-op candidate controls in both orders: D h02/F01/F04;
   T F01; R F05. F02's correct assignment labels alone do not satisfy its contradiction target.
4. Targeted improvement over C2 in **both orders of at least one family**. D's target
   is delivery; T/R gains require usable, supported temporal/fulfillment judgments.

A stopped pilot is incomplete and cannot pass on four candidate answers. A complete
passing pilot permits preparing a broader diagnostic only. It does not promote a
production reviewer, select a writer or establish whole-story improvement.

## Budget, stop and resume rules

| Limit | Frozen value |
| --- | ---: |
| Inference calls | **48 maximum**, D/T/R **16 each** |
| Calls by deployment | Gemma **16**, DeepSeek **32** |
| Attempts per cell | **1** |
| Retries, correction calls, writers, fallback models, canary | **0** |
| Input / output tokens per call | **24,000 / 8,000** |
| Context reservation per call | **32,000** |
| Aggregate input / output reservation | **1,152,000 / 384,000** |
| Active time per call / aggregate | **300 / 14,400 seconds** |
| Reference-rate estimate / planning allowance | **$0.64256 / $0.80** |

The rate estimate assumes undiscounted per-million input/output prices of
$0.14/$0.40 for [Gemma](https://ollama.com/library/gemma4:31b-cloud) and
$0.30/$1.20 for [DeepSeek](https://ollama.com/library/deepseek-v4.1-flash), checked
October 22. Actual billing is unknown; the allowance is not an enforceable billed
cap. Maximum message-size estimate is **14,914 tokens** using UTF-8 bytes divided
by four, not exact tokenization; captured usage must obey the actual limits.

After each pilot's first **eight completed calls**, stop that pilot if either arm
has **0/4 valid answers**, or one arm has the **same blocking structural signature
in at least 3/4 answers spanning both sentinel families**. This applies to the C2
control too. Thus an unchanged Gemma control that remains wholly invalid stops D,
even if D1 succeeds. That is useful preliminary evidence, not an eight-cell pass.

Duplicate-key signatures retain the exact object path; schema paths normalize array
indices. Missing/invalid evidence is classified by field while respecting legal
no-op/uncertain exceptions. Other failures use their deterministic validation category.
Truncation is a failed cell, not a structural signature, but counts toward zero valid
answers. Neither identical duplicates nor repairable-looking answers are salvaged.

Stop decisions are durable and bound to the plan and all eight receipts. Recompute
them on resume. An interruption after the eighth sealed receipt but before its
decision record can reconstruct that decision without another model call. Missing
decision records before later dispatches, altered decisions, skipped required cells,
or a dispatch into a stopped pilot fail closed. Unused slots never transfer.

Before a live invocation dispatches, both archived model identities/capabilities must
match discovery; repeat the check before each cell. The expected local manifest
digests are:

- Gemma: `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
- DeepSeek: `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.

Metadata was inherited without daemon discovery. Drift stops execution rather than
silently adopting a new deployment. A local manifest and a seed cannot guarantee
fixed remote weights or deterministic cloud generation.

Reserve every cell durably before dispatch, capture actual wire/request bytes and
raw provider responses, and seal receipts before continuing. Rebuild completed
evidence before each new reservation. An unresolved reservation, altered source/code,
missing capture/usage, identity drift, unexpected thinking, unclassified finish,
time/token excess, cancellation, transport/auth/rate-limit failure or unknown outcome
stops the **entire run**. Do not retry or silently resume a terminal failure. A lock
prevents concurrent operators. Metadata discovery does not consume inference slots.

## Verification, artifacts and approval boundary

Final verification: **152 tests pass** — 130 diagnostic tests and 22 gateway/contract
checks. These cover all 48 actual adapter wire requests, restart/replay, all 32
historical duplicate captures, field/alias validation, exact quote binding, required
evidence, group ownership, unchanged controls, isolated candidate differences,
sentinel thresholds, interruption recovery, forbidden budget transfer and terminal
failures. Ruff lint/format and strict mypy pass across **ten private scripts**.
All HTTP during tests uses in-memory mocks; no inference result is claimed. No
application-wide frontend build is applicable to this isolated preparation.

Local ignored bundle:
`data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/`.

- [Frozen cases](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/cases.json),
  [casebook](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/casebook.md)
  and [exact diagnostic instructions](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/candidate-instructions.json).
- [Schedule](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/schedule.json),
  [48 requests](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/prepared/),
  [scoring](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/scoring.json),
  [inspection anchors](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/inspection-anchors.json)
  and [stop rules](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/stop-rules.json).
- [Runner](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/execute.py),
  [advancement rule](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/analysis.py),
  [verification](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/verification.json)
  and [preparation seal](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/plan.json).

These links preserve local evidence; they do not publish private captures on GitHub.
The seal binds exact files, production adapter dependencies and this plan. The tracker
records its SHA-256 separately to avoid a self-referential document hash.

Live execution requires a new approval bound to that seal, **48-call ceiling**, both
deployments, **full unpublished original/revision prose and context**, and **Ollama
Cloud through the local Ollama daemon**. No approval for this new experiment is
inferred from earlier runs. Do not create a live transport before that approval check.

The nine human ties remain valid. Human review continues to concern feel, emotion,
flow, character and story-breaking details; machines prepare mechanical and assignment
evidence for inspection. Keep literary preference descriptive and permit meaningful
prose variation. **Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**
