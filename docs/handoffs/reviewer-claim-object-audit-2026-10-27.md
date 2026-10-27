# Local duplicate-ID, attribution and claim-object audit

Date: 2026-10-27. **LOCAL WORK COMPLETE; zero inference or daemon calls.**

This follows the [TH/EC results](../benchmark_reports/reviewer-epistemic-clarity-v61-results-2026-10-27.md).
It preserves the completed experiment and separates three questions that can
legitimately receive different judgments: whether a narrated relation holds,
whether a bounded source establishes that relation, and what a particular source
sentence explicitly asserts. It changes neither production prompts nor historical
scores. The [next proposed experiment](reviewer-claim-object-proposal-2026-10-27.md)
is a **24-call claim-form comparison**, not yet prepared, frozen or approved.

## Evidence preserved

The local bundle contains byte-identical copies of all **32 raw captures**, all
**219 valid component regressions**, exact case/request/source bindings, and the
sealed prior source judgments. The prior result still reproduces:

- TH/EC each **15/16 valid**; usable targets **6/16 versus 10/16**.
- **Seven alignment opportunities, three recoveries**, confined to preserved cases.
- **No reproduced scope-recovery opportunity** among valid controls; the exact
  historical TH/F3/RO failure cell is invalid and semantically unavailable.
- Frozen decision **`retain_limited_evidence_no_advancement`**.

Both normal-stop duplicate-ID failures are now reusable local fixtures:
**TH/F3/RO** and **EC/J3/RO**. Each repeats `claim_id` in all three claim objects,
for **six duplicate-key occurrences across two responses**. Both remain rejected
by strict parsing, with zero semantic credit. There is no repaired parse, retry,
or new explanation of the model's internal cause.

Six source-bound attribution/precision fixtures retain their original judgments:

| Capture | Preserved issue and limit |
| --- | --- |
| TH/J4/OR, TH/J4/RO, EC/J4/RO | “No claim that” becomes an explicit denial in the explanation; distinguish the cited sentence from the full scene's independent timing evidence |
| EC/J2/RO | “One lamp … another” slips from one lamp/two entries to different lamps; preserve the wording as written without claiming to know the intended referent |
| TH/J5/RO | An empty chair does not establish the manager's absence; the primary non-authorization conclusion has independent evidence |
| TH/H/OR | “Immediately preceding resolve” remains an **uncertain precision concern**: it may mean the most recent resolve, not the preceding sentence |

Positive controls preserve genuine contradiction, compatible different-time
observations, real obligation/intention conflicts, qualified craft and all fifteen
valid fresh conditional components. A defensible craft explanation is not required
to use the exact withheld witness list. These fixtures concern evidence reliability;
they do not rate how the stories feel to a reader.

## The claim-object distinction

Let **P** mean that the two particular literal opposite-state observations concern
the same referent at the same instant. “Event relation” here means a judgment of
the narrated observations under the supplied story evidence, not a claim about
real-world truth or permission to infer arbitrary facts from fictional inconsistency.

| Question | With complete sources that leave timing unknown |
| --- | --- |
| P: did these particular observations share an instant? | **Uncertain** |
| Not P: were they not simultaneous? | **Uncertain** |
| Does this bounded source establish P? | **Unsupported** after an explicit, complete insufficiency audit |
| Does this bounded source fail to establish P? | **Supported** under that same audited scope |
| Does the source establish not P? | **Unsupported** when it establishes neither temporal alternative |
| Does a named sentence explicitly assert not P? | Requires inspection of that sentence; absence of a positive assertion is insufficient |

The negative source finding is about a **specified, fully reviewed text**. It must
not become a general closed-world rule that every missing story fact is false.
An unreviewed or incomplete source scope cannot certify source-wide absence or
non-entailment; it remains unknown. A quoted, unverified assertion can exist in a
source without establishing the narrated event. Source authority still needs
separate adjudication.

The audit binds six full-packet relation records: F3, G5 and J1–J4. In F3/J1 timing
is expressly unresolved; in G5/J2 it is absent. J3 explicitly gives the same instant;
J4 explicitly gives different times. Unknown event relations stay unknown under
negation. Negating **“the source establishes P”** does not yield **“the source
establishes not P.”** Assertion and entailment are also distinct predicates.

### Why this matters for the fresh TH/EC failures

All **eight valid J1/J2 target answers** use unsupported, while their frozen primary
gold is uncertain. The actual claim text says the observations **“actually
establish”** simultaneous incompatible states. That wording supports a reading
about the source's evidential sufficiency. Under the prospective source-entailment
interpretation, unsupported is consistent with the complete packet's missing or
unresolved timing. The underlying event relation still remains uncertain.

Across all fifteen valid unknown-source target answers, there are **eleven
unsupported and four uncertain** labels. Their source judgments remain separately
recorded, including EC/J2/RO's referent slip. The audit does **not** change the
historical gold, count new recoveries, declare the original experiment successful,
or prove which interpretation the model used internally. Claim wording and scene
family were not independently varied in TH/EC. A new prospective contrast is
needed to distinguish claim-form sensitivity from other causes.

The explicit prospective choice is:

- **Event-relation claim:** judge the described observation relation; an unresolved
  relation remains uncertain.
- **Source-entailment claim:** judge whether the specifically bounded source
  establishes that relation. A completed insufficiency audit can refute this
  stronger claim without refuting the event.
- **Source-assertion claim:** judge what the specifically named span says, with
  the polarity and attribution scope preserved.
- **Craft claim:** retain the existing defensible-qualified-interpretation standard;
  do not demand unique factual entailment of an aesthetic response.

These are local evaluation-design decisions for a proposed diagnostic, not a new
production output enum, automatic classifier, or deployed acceptance gate.

## Full source versus cited sentence

J4 is the useful counterexample. R011/R012 place the hatch observations at nine
and ten, explicitly an hour apart. The **full packet establishes non-simultaneity**.
R013 says there is **“no claim that”** the two states occurred together. That
particular sentence does not itself explicitly assert the negation.

The audit therefore includes a separate R013-only record. Its source-assertion
judgment cannot borrow R011/R012's full-packet entailment. It remains possible for
the overall target label to be correct and an explanation's attribution to R013
to be wrong. This is a source-scope error, not evidence that the model missed the
different timestamps. The full-packet record does not pretend that the explicit
different-time wording elsewhere is absent.

The additional authored controls make related distinctions concrete:

- Two entries can concern one lamp; another entry is not another lamp.
- A manager can stand beside an empty chair. The same empty-chair premise is
  compatible with presence or absence; explicit location evidence changes the answer.
- A resolve can be the most recent prior resolve while two sentences intervene.
  The ambiguous captured phrase stays qualified rather than being converted into
  a certain adjacency error.
- A literal conditional can be supported without evidence that its antecedents
  actually occurred. An abrupt transition can support a qualified craft reading
  without inventing a factual contradiction.

## Local implementation and verification

The diagnostic-only utility explicitly represents the claim kind, proposition,
inner/outer negation and source scope. It consumes **independently authored,
source-adjudicated statuses**. It does not read prose and decide truth, infer
support from a label, supply a missing premise, or dispatch a writer.

It rejects changed claim identity/bindings, mismatched source scopes, missing or
unknown statuses, and negative source certifications without completed scope
review. A negative test deliberately supplies a false established-event premise:
the arithmetic then returns the wrong answer while still reporting
`semantic_truth_verified: false` and `writer_dispatch_allowed: false`. Hashes and
truth tables cannot replace source adjudication.

**163 offline tests pass:** 110 new audit checks plus all 53 preceding execution
checks. Ruff lint/format and strict mypy pass on four scripts. The first type check
found a missing explicit module export; that local typing issue was corrected and
the successful verification is retained alongside the initial record. Tests block
all real HTTP. There are **48 authored claim/negation contrasts**, **twelve authored
attribution controls**, six full-packet audits and one selected-span audit.
All **5,179 historical fingerprints** verify; historical results and sealed notes
are unchanged. Frontend/build checks are not applicable because application source,
dependencies and production configuration did not change.

Private bundle: `data/diagnostics/reviewer-claim-object-audit-v61-2026-10-27/`.
It includes complete captures, component and duplicate-ID fixtures, attribution
fixtures, claim-object/source-scope audits, authored controls, tests, verification,
source fingerprints and the audit seal. The tracker and issue index are updated;
all fourteen issue bodies and posted links remain unchanged. No external issue is
edited or closed.

**Zero new model or daemon calls.** Production prompt **61**, graph **9** and
fulfillment policy **1**, Blueprint approval and the nine prior human ties remain
unchanged. Humans retain feel/emotion, flow, character and story-breaking review
with machine-prepared mechanical evidence. Selective thinking, writer tests and
provider attribution remain deferred. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; full workflow canary ON HOLD.**
