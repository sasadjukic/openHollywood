# Luna MA/quote-witness comparison results

Date: **2026-11-03**. **COMPLETE: 16/16 attempts, zero retries.**
Model **`gpt-6-luna`**, explicit high reasoning in both arms.
Production **prompt 61 / graph 9 / fulfillment policy 1** and active profiles
remain unchanged. Live inference is **PAUSED**; the canary remains **ON HOLD**.

**WB does not pass the frozen continuation screen.** It grounds **51/62**
judgments versus MA's **50/62**, but ten paired citation recoveries are offset
by **nine grounded-to-failure losses**, including **one new semantic error**.
Fresh grounding is **28/32 WB versus 27/32 MA**, short of the required 32/32 WB.
Retain the recoveries as diagnostic evidence, without promoting this witness
contract or assigning it writer authority.

## Execution and fixed scope

The user approved the [frozen plan](../handoffs/reviewer-luna-witness-frozen-plan-2026-11-03.md)
and full prose/context at both story-bearing OpenAI endpoints. Execution used
**sixteen Responses generations and sixteen preceding input-token-count requests**,
plus sixteen model-catalog preflights. The earlier preparation catalog GET is
separate. There was no smoke generation, retry, model substitution, prompt change,
budget amendment or reuse of a retired allowance.

All sixteen responses used the exact frozen wires and returned the expected model
identifier. All had valid structured delivery with exact requested claim coverage;
there were no refusals, truncations, transport failures, unknown token totals or
resource overruns. Every reserved attempt is accounted for, with **zero remaining
and zero retired**. This completes the approved comparison; it authorizes no new run.

The four historical MA controls changed only the model identifier from the older
Luna. H1/W2 and fresh F3/F4 were assessed in both presentation orders, giving eight
pairs and **124 fixed claim slots**. The WB intervention changed only evidence
output to exact version/field/quotation witnesses. Full context and whole claims
remained unchanged; the new active-slot schema and smaller-workload proposal were
not combined with this treatment.

Plan SHA-256:
`abd249390095bffd4a2430bbfd8234f69f688b5ca688398146d8d96b6b65931f`.
Private preparation, live and analysis directories share the prefix
`data/diagnostics/reviewer-luna-witness-v61-2026-11-03` with `-L-live` and
`-analysis` suffixes for the latter two. Raw final answers, sanitized response
envelopes, usage, exact inputs and immutable cell hashes are retained. Credentials
and hidden reasoning content are not retained.

## All-slot results

| Dimension | MA | WB |
| --- | ---: | ---: |
| Structurally valid calls | 8/8 | 8/8 |
| Fixed judgments inspected | 62 | 62 |
| Correct labels | 61 | 60 |
| Correct material explanations | 61 | 60 |
| Complete location binding | 62 | 54 |
| Grounded judgments | **50** | **51** |
| Citation-only failures | 11 | 9 |
| Semantic failures | 1 | 2 |
| Unavailable judgments | 0 | 0 |
| Fresh grounded judgments | **27/32** | **28/32** |

Correct labels and location binding are separate from adequate evidence. A valid
S-reference can point to the wrong paragraph; a correctly located quotation can
omit a required premise. Semantic failures take precedence in the mutually
exclusive totals, with additional citation problems retained in inspection notes.

| Family/order | MA grounded / citation / semantic | WB grounded / citation / semantic |
| --- | --- | --- |
| H1-PC | 7 / 0 / 0 | 2 / 4 / 1 |
| H1-CP | 3 / 3 / 1 | 6 / 0 / 1 |
| W2-PC | 8 / 0 / 0 | 7 / 1 / 0 |
| W2-CP | 5 / 3 / 0 | 8 / 0 / 0 |
| F3-PC | 6 / 2 / 0 | 8 / 0 / 0 |
| F3-CP | 6 / 2 / 0 | 6 / 2 / 0 |
| F4-PC | 8 / 0 / 0 | 7 / 1 / 0 |
| F4-CP | 7 / 1 / 0 | 7 / 1 / 0 |

The **ten citation-only-to-grounded recoveries** occur at F3-PC Q002/Q005,
F3-CP Q002, F4-CP Q005, H1-CP Q002/Q003/Q005 and W2-CP Q001/Q002/Q005.
They cover nine distinct frozen family/unit keys; F3 Q002 is counted once for
the distinct-recovery screen despite recovering in both orders. The threshold
is also met by the unambiguous fresh F3 Q002 and Q005 contrasts alone.

The **nine grounded losses** occur at F3-CP Q001, F4-PC/CP Q001, H1-PC
Q001/Q002/Q005/Q006/Q007 and W2-PC Q003. H1-PC Q006 is the new semantic loss;
the other eight are citation-only losses. F3-CP Q005 remains a citation failure
in both arms, through different mechanisms. Thus gross recoveries do not establish
a reliable improvement.

The complete-delivery and distinct-recovery conditions pass. The no-loss and
all-fresh-grounded conditions fail. H1-CP's contextual relation remains separately
unassessed in both arms: its match and endpoint components receive judgments,
but neither response explicitly judges the entire retained original relation.
No whole-relation credit is manufactured from the component labels.

## What failed, and what the evidence supports

**MA still selects incorrect or incomplete source sections.** Its eleven
citation-only failures have correct labels and material explanations but cite
adjacent paragraphs, omit a compound premise, or confuse current and next-scene
sections. For example, F3-PC Q002 describes the touch and persistent vibration
correctly but cites the vibration paragraph and the later clapper test, omitting
the actual touch. WB supplies the two relevant exact quotations. In H1-CP, MA
cites the date-realization paragraph for the decision and handwriting match;
WB correctly quotes the comparison paragraph.

**WB introduces source-identity and quotation-boundary failures.** Of its **103
witnesses**, **94 locate** and **nine remain unresolved**, affecting eight
judgments across four calls:

- **Five invalid source/field combinations:** H1-PC uses blueprint-style nested
  scene paths with the standalone scene-plan version in Q001/Q002/Q005/Q007;
  F3-CP Q005 uses a standalone `/turning_point` path with the blueprint version.
  The frozen native schema enumerates versions and field paths independently,
  so a globally allowed field can be invalid for the selected version. The
  application correctly rejects that binding; it does not borrow a matching
  quotation from another source.
- **Two altered quotations:** both H1 WB flourish claims return a shortened
  sentence ending after “flourish.” The actual plan continues with the private
  qualifier. The submitted sentence is not an exact substring and remains missing.
- **Two cross-paragraph quotations:** H1-PC Q007 and W2-PC Q003 combine current
  date and realization paragraphs into one witness. The text exists, but spans
  two registry entries; the frozen one-entry locator correctly leaves it unresolved.

These are validly shaped delivery outcomes under the freeze, not reasons to retry
or stop inference. All sixteen work records have complete delivery; twelve have
complete binding and four retain unresolved binding. No quote was repaired or
unresolved location credited.

**Correct location still does not guarantee complete evidence.** In F3-CP Q001
and F4-PC/CP Q001, WB quotes preparation and the still-outside state but cuts off
the preceding internal reasoning. The frozen claims expressly require internal
reasoning **and** preparation. The complete containing paragraph includes the
missing premise; the frozen scoring forbids automatically using it to pad the
submitted quotation. These are three citation-only failures, not a finding that
the character never made a decision or that the scene is emotionally ineffective.

This also exposes an **interface ambiguity worth auditing**. The frozen WB clause
asks for a quotation sufficient to locate one occurrence and says the application
cites its containing registry section. The frozen scoring instead requires the
quotation itself to cover the material premise. A good locator and a complete
evidentiary span are different requirements. The three shortened quotations fit
that distinction; this is a plausible application-contract contributor, not proof
of the model's internal cause. Scores remain as frozen. Resolving this ambiguity
would not by itself remove the wrong source/field combinations, altered literals,
cross-entry witnesses or new semantic loss.

**The private-flourish semantic error remains distinct.** Both arms support the
unsupported specific-turning-point claim in H1-CP; only WB makes that error in
H1-PC, where MA correctly distinguishes general handwriting agreement from the
particular private-flourish verification. WB's final explanations characterize
“consumes” as a structural consequence and accept the general match plus planned
flourish as enough. Those premises do not establish the complete specific-event
claim under the frozen contract. The wider pacing criticism could still be worth
an editor's consideration; that does not make its factual premise established.
This observation comes from final explanations, not an inference about hidden
reasoning or a proof that thinking mode caused the error.

Source inspection allows equivalent evidence and evaluates materiality. For
example, an explicit statement that the named private test was not performed
can refute a completion claim without separately citing its plan. A shortened
attribution quotation can be sufficient when it retains the named speaker's
rejection and contrary intention. These allowances do not permit an unrelated
reference, a missing compound premise or unresolved source identity. The per-slot
notes record the actual evidence and these distinctions.

## Resources and delivery headroom

| Resource | MA, eight calls | WB, eight calls |
| --- | ---: | ---: |
| Input tokens | 54,997 | 66,425 |
| Generated tokens, including reasoning | 20,621 | 28,470 |
| Reasoning tokens, included above | 15,452 | 16,872 |
| Cached input tokens, included in input | 1,607 | 7,175 |
| Active count/generation seconds | 186.08 | 221.97 |
| Median active seconds per call | 23.50 | 27.74 |
| Conservative reference cost | $0.017185125 | $0.022538125 |

Total: **121,422 input / 49,091 generated / 32,324 included reasoning tokens**,
408.06 active seconds and **$0.039723250 reference cost**. Actual billed cost is
unknown. Reference accounting follows the freeze's conservative $0.125 input /
$0.50 output per million tokens, including no assumed cache discount; it is not
an account invoice. Both the $0.176 token-max reference reservation and $0.48
application planning allowance were respected.

WB uses **20.8% more input**, **38.1% more generated tokens**, **9.2% more reasoning
tokens**, **19.3% more total active time** and **31.1% more reference cost**. Median
active latency rises 18.0%. These are descriptive observations over eight calls
per arm; caching and sequential service variation differ, so they are not a
general performance guarantee. Active time excludes local integrity-check and
inspection overhead.

The largest request used 17,975 of 24,000 allowed input tokens; the largest output
used 4,819 of 16,000 generated tokens; the slowest attempt took 37.04 of 600 active
seconds. This run supplies no evidence of truncation or exhausted delivery
resources as the explanation for its semantic/citation failures.

## Verification and limits

Every final answer was inspected against full source context and the frozen
whole-claim gold. Completed packets were inspected in deterministic opaque-ID
order within available batches, with arm labels omitted; inspection notes were
saved before the final decoding/aggregation file. Output shape and execution
context can reveal the arm. This is **assistant source inspection, not a fully
blind human study**. No hidden reasoning was inspected. All 124 fixed slots,
including the zero unavailable slots, remain in `inspected-slots.json`.

Post-approval verification passes **250 tests**, with the single frozen
preparation-stage assertion about absent approval/live files deliberately
deselected. It remains unchanged. Repository Ruff/format and strict mypy pass
for **224 Python files**; diagnostic checks cover the nine frozen scripts and
two result-analysis scripts. Deterministic scoring and receipt replay reproduce
the saved totals. All **32 frozen preparation files and 3,178 source pins** remain
unchanged. No tracked application code, frontend, dependency or schema was modified.
The earlier full repository suite is historical and is not claimed as rerun.

The model is the user-requested newer alias; historical control messages are
preserved, but this run does not causally compare model generations. There are
four scene families, two newly authored, with reordered observations rather than
eight independent stories. The aggregate one-judgment gain is not evidence of
better prose, pacing, emotional effect or production reliability.

## Recommended next local work

1. Preserve the exact paired recoveries and the new failures as regression
   fixtures: wrong version/field combinations, altered literals, cross-entry
   witnesses, correctly located but incomplete evidence, and the H1 semantic
   contrast. Preserve successes and unavailable-state handling as well.
2. Audit the witness contract in two separate parts. Locally test whether a
   version-bound field schema can reject the five impossible combinations without
   dropping valid alternatives. Separately examine whether the diagnostic intends
   quotations to be locators for full source sections or the exact evidentiary
   spans themselves. The current freeze chose the latter for scoring; do not
   retroactively grant paragraph-padding credit or repair historical outputs.
3. Keep the specific-event versus structural-pacing claim separate from citation
   mechanics. A stricter identity schema cannot establish semantic entailment.
   Only propose another isolated, bounded live comparison if those local checks
   justify a materially different hypothesis and a concrete evaluation contract.

The read-only assessment component remains useful for showing exact scope,
delivery, location and unresolved evidence to an operator. This comparison does
not qualify automatic critique acceptance, writer edits or story-quality gates.
No further inference is authorized or budgeted here. All fourteen issues remain
open; **Step 19 IN PROGRESS, Step 20 NOT STARTED; canary ON HOLD**.
