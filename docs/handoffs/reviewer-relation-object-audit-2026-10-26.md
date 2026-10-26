# Local relation-object and delivery audit

Date: 2026-10-26. **Complete locally; no new inference or daemon calls.**

This implements the local recommendations in the [NC/ES results](../benchmark_reports/reviewer-evidence-status-v61-results-2026-10-26.md).
The historical decision remains **retain_limited_evidence_no_advancement**.
Production prompt 61 / graph 9 / fulfillment policy 1 remain unchanged. The full
workflow canary remains **ON HOLD**. No new experiment is frozen or authorized.

## Preserved evidence

The private bundle is
`data/diagnostics/reviewer-relation-object-audit-v61-2026-10-26/`.
It contains byte-identical copies of all **28 raw response captures**, the source
cases and receipts, **48 selected component regressions**, the separate invalid
delivery fixture, **eleven authored relation objects**, and eight explicit
reason-to-relation audits. Regression tags overlap; these are not 48 independent
model observations. All historical labels, gold, inspection notes and scores stay
unchanged.

The new delivery fixture is **E-NC-F1-RO**. It returned HTTP 200, `stop`, and 341
output tokens, but repeated `claim_id` in each of three claim objects. Values were
C01/C01, C02/C02 and C03/C03. It remains **one invalid report with three duplicate
members**, without loose-JSON salvage, repair, retry or semantic credit. The exact
content SHA-256 is
`f8a02f9047706be4fe991e5aefbfe36c093229f698c9473b86d87a0424495312`.

The component fixtures retain:

- All eight H/U false factual-contradiction judgments across NC/ES and both orders.
- The two NC endpoint label/reason disagreements, F1/OR and F3/OR: accurate
  explanations describe violations, while the labels incorrectly reject them.
- Six H craft abstentions, the NC-H-RO craft explanation with a false factual
  premise, and two incomplete intention witnesses. NC-H-OR overlaps the abstention
  group; NC-U-OR's wrong-relation explanation overlaps the target-failure group.
- The other nineteen valid target observations, retaining NC/Y's disclosed label
  ambiguity rather than recoding it as success. True simultaneous contradictions,
  compatible sequential states and explicitly unresolved timing remain distinct.
- Two actual rule violations, two intention conflicts and seven successful
  qualified craft assessments as protected positive controls.

## What the relation audit establishes

| Family | Requested factual pair | Separate intention pair | Separate obligation pair |
| --- | --- | --- | --- |
| H, observatory | R014: not yet consulted; R015: rotates before consultation. **Compatible facts.** | R012: resolve to wait; R015: acts before consultation. **Intention conflict.** | C010: consultation required first; R015: early action. **Rule violation.** |
| U, greenhouse | R012: not yet authorized; R013: starts before authorization. **Compatible facts.** | R010: resolve to wait; R013: starts early. **Intention conflict.** | C010: authorization required first; R013: early start. **Rule violation.** |

The model can correctly identify the last two relations while getting the first
wrong. A fact being true does not make every asserted relation between true facts
true. Breaking a promise does not establish that permission or consultation has
already occurred. The criticism may identify a real problem while still giving
the wrong reason for the specific claim under review.

Six captured target reasons address the requested factual pair but infer a false
contradiction. **NC-U-OR** explicitly changes the comparison to the resolve in
R010; that intention conflict is real, but it does not answer the requested
status/action relation, and R010 is absent from its citations. **ES-U-OR** conflates
the resolve and factual status in one explanation. These classifications are
explicit assistant source adjudications, not a keyword classifier or a claim to
know the model's internal reasoning.

Each authored relation object binds the packet, claims, component map and evidence
registry, identifies the exact claim/component and relation kind, and preserves
two assertion slots with exact excerpts, source namespaces, versions and authored
roles. Timing/identity witnesses remain explicit, including unresolved timing.
The eleven objects cover seven factual relations and the four H/U intention/rule
relations. Y and F3 have two different assertion excerpts within one source unit;
sharing a reference does not collapse the assertions into one proposition.

The local identity checker rejects stale bindings, a different claim or relation,
changed sources/roles, missing or duplicate slots, and substituted intention
witnesses. It checks agreement with an **authored fixture**. It does not discover
the correct relation from prose, prove the authored conclusion, validate a model's
free-text explanation automatically, or correct a returned label. A model-generated
relation type would still need source adjudication. No production interface was
changed.

ES-U-OR/C03.A02 demonstrates a separate citation problem: its impatience explanation
depends on the stated resolve, but cites only R013. R010 already appears in a sibling
component, so explicitly citing it here would add **zero** references to the
whole-claim union. This is not an unavoidable eight-reference budget conflict.
The sibling's citation does not silently repair this component's incomplete proof.

## Story-quality boundary

Keep actual assignment violations actionable without turning every intention/action
conflict into a factual impossibility. A character may break a promise, act
impulsively or change their mind; deciding whether that feels convincing is an
editorial question. A qualified craft reading needs defensible source support,
not unique factual entailment. Conversely, a plausible craft conclusion cannot
excuse a false factual premise in its explanation.

Retain the genuine-conflict, uncertainty and successful craft controls. Neither
mechanical label accuracy nor these assistant fixtures establish better prose.
The nine prior human ties remain unchanged. Humans continue to assess feel and
emotion, flow, character and story-breaking details, with mechanics prepared by
machines. No writer edits or new human preference claims are authorized here.

## Materially different hypothesis required before inference

The [model-attribution assessment](deepseek-model-attribution-assessment-2026-10-26.md)
identifies an untested operating variable: the saved DeepSeek requests explicitly
use `think: false`, while captured metadata supports `high` thinking. My preferred
next hypothesis is: **the requested non-thinking mode contributes to substituting
an obligation or intention conflict for the requested factual relation.** This is
a hypothesis, not a finding that thinking will fix it.

A future mode comparison should preserve the exact NC control instructions,
full source packets, claim wording and output contract, changing only the requested
supported thinking mode. Include known H/U failures and fresh families with the
same semantic contrasts; genuine same-instant conflicts; compatible sequences;
explicitly unresolved and merely unestablished timing; and protected obligation,
endpoint and qualified-craft assessments. Use both presentation orders and count
families separately from repeated observations.

Its distinguishing predictions are:

1. Grounded recoveries in thinking mode across known and fresh families, without
   protected losses, support a mode-dependent limitation of this deployment.
2. Continued errors in both modes weaken that explanation under the tested
   conditions; they do not establish a universal model incapacity.
3. Delivery failures or exhausted output allowances must remain delivery outcomes,
   not be interpreted as proof of semantic inability. A gain only on familiar
   scenes is insufficient for advancement.

Before freezing, verify supported mode metadata, provider-specific parameter
handling and accounting for reasoning plus final output. Preserve hard per-call
and aggregate token/time limits, raw terminal evidence, unknown usage and zero
unbudgeted retries. Thinking can change effective sampling behavior; describe this
as a comparison of supported operating modes, not a perfectly isolated measure
of additional internal computation. Freeze requests, scoring, stops and a new
budget separately, then obtain live approval. **No budget or requests are prepared
by this proposal.**

A separate later alternative is the previously suggested full-scene versus faithful
isolated-assertion-pair probe. Success only on the isolated pair would support
context sensitivity; failure in both would not. Removing surrounding context also
reduces task burden, so that probe cannot by itself prove which neighboring sentence
caused the error. Do not combine both interventions initially, or use an isolation
result to remove production story context. Another enum or wording variant alone
does not meet the new-hypothesis requirement. Provider attribution remains deferred.

## Verification and closure

**175 offline tests pass: 120 new audit regressions plus all 55 prior execution
tests.** Real HTTP is blocked. Ruff lint/format and strict mypy pass on both new
scripts. Checks cover all raw replays, strict duplicate rejection, relation/source
identity, historical adjudication bindings, wrong-pair versus wrong-inference
distinctions, craft controls and the zero-cost omitted witness. All **3,632 source
fingerprints** verify, including the earlier frozen preparation and sealed analysis.

The source analysis seal remains
`02fac6153e5efd3b829a4554d668304976538d040bd5b868e2a3b58f02a4f507`.
The new audit seal binds its scripts, fixtures, verification, both public notes and
documentation closure. Private captures remain ignored by Git; the public notes
and tracker/index record the findings. No production/API/worker/frontend change
requires a new application build. All fourteen issue bodies and posted GitHub
links are preserved; no external issue is changed or closed.

**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**
