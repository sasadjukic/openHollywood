# Frozen ER/SE claim-form comparison

Date: 2026-10-27. **LOCAL PREPARATION — 0/24 inference calls used. Awaiting separate live approval.**

This prepares the [24-call proposal](reviewer-claim-object-proposal-2026-10-27.md)
following the [claim-object audit](reviewer-claim-object-audit-2026-10-27.md).
The question is whether the reviewer distinguishes an uncertain narrated relation
from an unsupported claim that a bounded source establishes that relation. It is
a test of claim-form discrimination, not retrospective recovery or story quality.

## Intervention and unchanged controls

| Item | Frozen choice |
| --- | --- |
| Model | `deepseek-v4.1-flash:cloud`, both forms |
| Thinking | `think: "high"`, both forms |
| SE control | Claim that the supplied observations establish the specified simultaneous relation |
| ER contrast | Claim that those particular observations concern the specified states at the same instant |
| Instructions | Unchanged EC factual-label definitions, supported/craft standard and component contract |
| Matrix | Six families × two presentation orders × two claim forms = **24 attempts** |
| Allocation | Twelve per form, one per cell, **zero retries, replacements or reallocations** |
| Sampling | Temperature 0.2, top-p 0.95, seed 20261022 |
| Transport | Non-streaming; no provider format override |
| Destination after approval | Ollama Cloud through local daemon `http://127.0.0.1:11434` |
| Evidence bounds | Eight distinct references and 2,000 summed reason characters per whole claim |

Only **C02.A01's proposition and its corresponding text in whole claim C02** change
within each pair, with the necessary local claim/component identities and hashes.
The source packet, conditional C02.A02, assignment/craft claims, schema, registry,
system messages and sampling settings are identical. Restoring the SE target text
in each ER wire request reproduces the complete SE wire request exactly. There is
no new hint, source-scope card, label enum, reasoning-effort arm or writer call.

All **four historical EC J1/J2 wire requests**, in both presentation orders, remain
exact controls under the canonical serializer. Their wording includes “actually
establish.” Both forms retain the existing EC definitions:

```text
Unsupported means it includes a material factual premise that the sources refute. Use uncertain when a material factual proposition is neither established nor refuted by the supplied material, including explicitly unresolved alternatives.
```

**The SE gold is prospectively source-entailment gold.** For preserved J1/J2 it is
unsupported, whereas their historical event-relation gold was uncertain. This
explicit evaluation-design choice does not change the previous requests, outputs,
scores or no-advancement decision. A correct SE answer does not refute the event.
The source-insufficiency finding requires review of the entire bounded packet;
it is not a rule that unstated story events are false.

ER concerns the temporal relation of the particular narrated observations. The
same-time positive control asserts a relation between conflicting descriptions,
not that mutually exclusive physical states are possible in the real world.

## Frozen cases and claims

| Family | Scene | Observation timing | ER target | SE target |
| --- | --- | --- | --- | --- |
| J1, preserved | Pool appeal; gate photographs | Explicitly unresolved | Uncertain | Unsupported |
| J2, preserved | Bakery; lamp repair-book entries | Absent | Uncertain | Unsupported |
| K1, fresh | Ferry refund; ticket-grille drawings | Explicitly unresolved | Uncertain | Unsupported |
| K2, fresh | Theatre costume room; hook inventory entries | Absent | Uncertain | Unsupported |
| K3, fresh | Orchard water allocation; sluice descriptions | Explicitly identical instant | Supported | Supported |
| K4, fresh | Museum bell return; latch condition notes | Explicitly different times | Unsupported | Unsupported |

The fresh originals contain **314, 308, 329 and 324 words**, respectively. They have
different character goals, relationships and narrative actions. Each revision
retains the assigned discovery and decision while changing its assigned endpoint.
The conditional component is supported in every form/family; qualified craft and
assignment checks remain separate. There are no writer-generated scenes or human
story-preference judgments in this preparation.

The freeze has **twelve family/form case records, 36 whole-claim records and 84
material-component records** over six shared source packets. Both presentation
orders yield **36 whole claims / 84 components per arm**, including twelve targets,
72 non-target components and twelve conditional controls. Across both arms there
are 72 whole-claim and 168 component opportunities. Invalid attempts remain in
denominators and receive no semantic credit.

All gold, source-scope judgments and witness annotations are withheld from requests.
Each case has an explicit complete-packet scope record bound to its packet, claims,
component map and registry. In absent-timing cases, unrelated narrative times and
entry order do not date the observations. Both temporal alternatives remain
unestablished; neither absence nor uncertainty supplies an opposite-event premise.

All **36 whole-claim witness unions** fit the existing eight-reference limit; the
maximum is **six**. Authored feasibility examples also fit the reason-character
limit. The witness audit includes assignment leaves as well as matching prose.
Alternative complete and accurate evidence is acceptable: this is not an exact
reference-list metric or a machine proof of semantic truth.

The private [casebook](../../data/diagnostics/reviewer-claim-form-v61-2026-10-27/casebook.md)
contains complete originals, revisions, context, both claim forms, components and
withheld source judgments. Machine evidence remains separate from human review
of overall feel, flow, character and story-breaking details.

## Schedule, scoring and interpretation

Paired forms are adjacent: **six pairs are SE-first and six ER-first**. Each family
appears in original/revision and revision/original order. The first eight cells
are J1/J2 in both forms and orders, counted within 24. These order repetitions are
not independent families.

Freeze primary labels and final-text source judgments separately. Source inspection
requires exact quote/version/context bindings, accurate reasons and citations,
complete material coverage and an annotation addressing the exact claim object.
For unknown cases, ER needs an event-unknown explanation and SE a source-insufficiency
explanation; substituting a true conditional does not answer either target.
For known-time controls, inspect the actual observation relation or source-entailment
judgment as appropriate. An accurate unknown-limit explanation with an incorrect
label remains distinguishable from invented timing.

A useful discrimination signal requires all of the following:

- **24/24 valid reports**.
- **8/8 unknown-timing matched pairs** correctly and usefully discriminate ER
  uncertain from SE unsupported across J1/J2/K1/K2 in both orders.
- **8/8 individual same/different-time control targets** are correct and grounded.
- **24/24 separate conditional components** remain usable.
- No protected SE-to-ER loss in valid delivery, usable non-target components,
  supported assignment/craft labels, or accurate complete reasons/citations.

Each whole-claim aggregate is judged against its own form. Correct differing C02
labels are not losses. Shared non-target defects and control-side defects are
reported even when they do not create a directional paired-loss flag. This remains
a narrow diagnostic screen, not blanket report reliability or production qualification.

The decisions are `retain_claim_form_discrimination_signal_only` if all screens
pass, `retain_limited_evidence_no_advancement` for a completed run with failed
screens, and `incomplete_no_advancement` for unfinished or terminal execution.
No historical failures supply missing contemporary observations. No output repair
or thinking trace earns semantic credit.

Export final assessments with arm/order/trial metadata and resource observations
hidden; seal source-inspection notes before decoding the key. **Claim form remains
visible in the claim text**, so this is partial masking. The inspector must not use
thinking as evidence. Report invalid/unobserved cells separately, along with known
versus fresh transfer, whole/component usability, paired latency/generated-token
ratios and resources per usable complete report. Unreported token splits stay unknown.

## Budget and stops

| Budget | Ceiling |
| --- | --- |
| Total attempts | **24**, twelve per arm |
| Per-call input / combined generated tokens | **24,000 / 16,000** |
| Requested context | **40,000** |
| Per-call active time | **600 seconds** |
| Aggregate input / generated reservation | **576,000 / 384,000 tokens** |
| Aggregate active time | **14,400 seconds**, four hours |

Thinking and final output share the generation cap. These reservations are ceilings,
not usage forecasts. Using the explicitly **archived 2026-10-22 reference rates**
of $0.30 input/$1.20 output per million, without discounts, the reservation estimate
is **$0.63360**. The retained planning allowance is $1.00. Current billing is not
verified and a billed-dollar cap is not enforceable; call/token/time limits are.

- After the first eight cells, stop if either form has **zero valid reports out of
  four**, or ER repeats the same blocking delivery signature across J1 and J2.
- Stop globally on non-200/transport/gateway error, truncation/incomplete finish,
  missing/excess usage, invalid supplied timing/token breakdown, missing nonempty
  high thinking, time breach, daemon/model drift, tampering, cancellation or
  ambiguous dispatch. Preserve raw error chains and unknown terminal usage.
- Reserve before dispatch. No terminal retry/resume, probe, replacement, budget
  reallocation or early stopping based on semantic results. Continuation is allowed
  only from a clean completed boundary into the original unspent schedule.

Live execution requires separate approval bound to the sealed plan, **24 total /
12 per form**, full unpublished prose/context and frozen claims/components, both
high-thinking forms and the Ollama Cloud destination via the local daemon.

## Metadata, verification and handoff

Metadata-only capture of `/api/version`, `/api/tags` and `/api/show` on 2026-10-27
confirms **Ollama 0.40.11** and the unchanged selected DeepSeek metadata/digest:
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
The initial sandbox socket denial and subsequent successful three-response capture
are retained separately. No story content was sent and no inference occurred.

The private ignored bundle is
`data/diagnostics/reviewer-claim-form-v61-2026-10-27/`.
It contains exact prepared/wire requests, cases/claims/components, prospective gold,
source-scope audits, registries, schemas, source witnesses, examples, schedule,
budget/stops/scoring, metadata, operator/export/scoring scripts, tests and casebook.
The final seal is `plan.json`; **5,234 historical source fingerprints** are retained.
The largest quarter-byte prompt estimate is **8,769 tokens** against a 24,000 input
reservation; actual tokenizer counts remain unknown until a provider response.

**393 offline tests pass:** 230 current preparation checks, 110 claim-object
regressions and all 53 prior execution checks. Ruff lint/format and strict mypy pass
on twelve preparation scripts. Tests block real HTTP and exercise all 24 gateway
dispatches with mocks, exact controls, isolated claim changes, prospective scoring,
negation/attribution regressions, strict duplicate-ID rejection, source binding,
budgets, metadata drift, sentinels, terminal export, clean restart and approval
enforcement. Initial module-export/type errors were corrected locally; the initial
and successful verification records are retained. Frontend/build checks are not
applicable because application code, dependencies and production configuration
remain unchanged. No `approval.json` or live execution directory exists.

Tracker and issue index are updated; all fourteen issue bodies and posted links
remain unchanged. No external issue is edited or closed. Production **prompt 61 /
graph 9 / fulfillment policy 1**, Blueprint approval and nine prior human ties remain
unchanged. Selective production thinking, writer work and provider attribution stay
deferred. **Step 19 IN PROGRESS; Step 20 NOT STARTED; inference PAUSED;
full workflow canary ON HOLD.**
