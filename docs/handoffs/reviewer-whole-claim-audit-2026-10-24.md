# Local delivery and whole-claim audit — 2026-10-24

Status: **complete locally; no inference or daemon discovery**. Production remains
**prompt 61 / graph 9 / fulfillment policy 1**. Live calls are paused and the full
workflow canary is **ON HOLD**.

The [24-call diagnostic](../benchmark_reports/reviewer-claims-v61-results-2026-10-24.md)
remains **22/24 valid, 49/72 correct labels and 7/24 fully usable responses**.
This audit preserves every capture, frozen request, gold label and historical score.
It adds reproducible local regressions and identifies an evaluation ambiguity that
should be addressed before interpreting another comparison.

## Deliverables and verification

The private bundle is
[`data/diagnostics/reviewer-whole-claim-audit-v61-2026-10-24/`](../../data/diagnostics/reviewer-whole-claim-audit-v61-2026-10-24/).
It contains:

- Two unchanged invalid captures with raw-response and receipt fingerprints.
- Twenty-four authored boundary mutations, covering all three claim positions.
- Eighteen source-bound claim inventories and all **66 valid captured judgments**,
  including the original inspection notes, exact reasons, references and versions.
- Sixteen authored contrasts separating factual assertions, constraints, grounded
  literary readings, version ownership, explanation overstatement and uncertainty.
- A [readable fixture register](../../data/diagnostics/reviewer-whole-claim-audit-v61-2026-10-24/fixture-register.md),
  source manifest, replayable audit, tests and verification records.

**90 offline tests pass: 74 new audit tests and sixteen unchanged preceding
execution tests.** Ruff lint/format and strict mypy pass on the three new scripts.
Real HTTP is blocked during tests and the initial build. The checks exercise the
actual validation boundary, captured rejection, source/annotation tampering,
version/offset bindings and exact historical score replay. Initial formatting and
static import-path issues were corrected; final verification uses the repository's
engine directory and the diagnostic's actual import paths.

These fixtures test validation and recorded adjudication behavior. They do not
establish an automatic semantic truth detector or new model performance. No
production, frontend, API or worker code changed, so unrelated product builds and
broad suites were not rerun. Full prose and raw responses remain local and ignored
by Git. Original issue bodies and user-posted GitHub links remain intact.

## Delivery boundaries remain strict

| Capture | Preserved failure | Regression behavior |
| --- | --- | --- |
| `CV-K-OR-2` | C02 repeats `evidence`; both values are R012/R013 | Reject identical duplicate keys as well as conflicting duplicates; do not normalize |
| `CV-B-RO-1` | C03 has nine valid distinct refs, above the eight-ref maximum | Reject overflow even when every ref belongs to the packet; do not trim |

Both captures are HTTP 200 normal stops with complete usage. Neither is a
truncation or a namespace error. The first also labels C02 `supported` while its
reason concludes that the claim is unsupported as stated. That conflict remains
inside an invalid capture; removing a repeated key would not reconcile it.

The 24 authored mutations exercise identical/conflicting evidence-key duplication,
eight versus nine references, duplicate/unknown references, empty evidence for a
definite judgment, and permissible empty evidence for uncertainty. Eight-reference
and uncertain-empty controls demonstrate structural acceptance only. They receive
no semantic credit and are not repaired model responses.

## Whole-claim findings

### Clear failures persist independently of the ambiguous cases

Of the thirteen frozen false acceptances, **ten concern explicit factual targets**:
four H/C01 status contradictions, three valid K/C02 status contradictions and
three valid B/C02 claims that consultation was explicitly required before deciding.
These are repeated observations of three unique claims, not ten independent
failure classes.

The reasons reveal different observable behaviors:

- H/RO/1 supports grammaticality and a contrived feel but omits the false status
  premise when accepting the whole claim.
- H/OR/1 recognizes the consistent timing, then substitutes the character's resolve
  for the immediately preceding factual status named in the claim.
- K/OR/1 and K/RO/1 explicitly recognize compatible factual statements, excuse the
  supplied wording, and approve a different, plausible core claim.
- Other H/K reasons repeat the false contradiction. B/C02 reasons quote or discuss
  the before-explaining condition but endorse the stronger before-deciding claim.

This supports testing whether an explicit, inspectable assessment of material
premises changes the final whole-claim judgment. It does not establish an internal
model mechanism. A true constraint violation cannot establish a separate factual
contradiction or an invented prerequisite.

### Two probes need clearer scope in future evaluation

The audit flags **B/C03 and G/C03** as sensitive to interpretation. This is a
qualification of the earlier analysis, not a silent historical rescore.

**B/C03** says the action “undermines the deferred-consultation logic.” The frozen
adjudication treated this as an unsupported consultation-before-action dependency,
consistent with the associated B/C02 explanation. However, the standalone claim
does not explicitly state a ban on action. It can also express a defensible craft
reading: acting now may make the planned consultation feel less considered.
The three valid replies largely repeat that ambiguous formulation. They should
not be presented as three unequivocal assertions of a formal prerequisite.

**G/C03** calls admission a reversal of an “earlier choice” to keep the gate locked.
The frozen reading treats this as an imported choice inside revision chronology.
The wording can also be read as comparing the original's choice with the revision.
All four replies express uncertainty while noticing the missing premise. Their
abstentions remain abstentions under frozen scoring; they are not proof of failure
on an unambiguously specified within-revision chronology test. M/C01 is a cleaner
control because it explicitly says the locking and retrieval occur within the
revision.

For future tests, keep these exact historical inputs as secondary observations,
but do not let their disputed wording decide a factual-recovery gate. Add explicit
contrasts between a claimed prohibition and a qualified impression, and between
within-version chronology and across-version comparison. A subjective criticism
does not become false merely because it is not the only reasonable reading.

### Correct labels still require bounded explanations

`CV-M-RO-1:C01` correctly rejects locking followed by retrieval, but adds that
packing is the revision's only plate-handling action. The complete source also
contains finding the plate and loosening its attached screw. The local contrast
retains the narrow supported rejection while testing the unsupported exhaustive
addition separately. This is an explanation error, not established literary harm.

The positive controls remain important: the prior run retained all **37 supported
controls in valid responses**. L's four responses were fully usable; M's four label
triples were correct. Retain grounded urgency, impulsiveness, naturalness and
continuity readings alongside real constraint violations. A policy that rejects
all interpretive criticism would be a regression.

## Adjudication policy for local contrasts

The inventory records factual assertions, assignment constraints and defensible
literary interpretations separately. Each record retains complete source identity,
the exact claim and its frozen judgment; authored checks are labeled as authored.
The two ambiguous probes include an explicit alternative reading.

A small local helper combines **already adjudicated material checks**: a known
unsupported material assertion prevents a supported whole-claim verdict; otherwise
unresolved material support remains uncertain; fully supported material permits
supported. This applies to the authored conjunctive cases only. It does not parse
arbitrary prose, discover premises, resolve metaphor, interpret disjunctions or
determine whether a clause is material. It is not installed in production and
never substitutes a new label into a saved response.

The contrasts also distinguish an assertion about what the complete source says
from a forecast about an unshown future reaction. Missing support for the former
can justify rejection; the latter can remain genuinely unresolved. Qualified craft
readings require defensible source grounding, not proof of unique reader preference.
An unsupported factual clause cannot be excused by uncertainty about a different
literary or future-outcome clause.

The authored label/reason consistency examples demonstrate what should be flagged
once semantic annotations are supplied. No phrase search or unrestricted automatic
consistency classifier was added; a reason mentioning the word “unsupported” is
not itself sufficient to determine its conclusion.

## Next bounded experiment

The local evidence justifies proposing an isolated comparison of the unchanged
fixed-claim verifier with an observable material-premise assessment in the existing
reason field. The [36-call proposal](reviewer-material-claims-proposal-2026-10-24.md)
retains all six existing families, adds three fresh families and uses both source
orders. It separates clear factual recovery from the two scope-sensitive probes.

This is **a proposal only**: no new cases, requests, prompt card, live approval or
budget reservation have been frozen. Production prompts remain unchanged.
Provider investigation remains deferred. Preserve the nine human ties and future
review emphasis on feel/emotion, flow, character and story-breaking concerns.
Neither this audit nor a successful verifier comparison would establish better
stories or authorize another production role.

**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**
