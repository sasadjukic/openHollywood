# Critic presentation and E1 temperature: bounded results

Date: 2026-10-17. **COMPLETE: 43/80 calls; neither frozen success criterion met.**

Continuous prose improved duplication detection, but two P1 reviews remained
structurally invalid. Lower writer temperature produced no clear preservation win
and one loss. These results support further diagnosis, not production promotion.
Production remains at prompt **61**, graph **9**, fulfillment policy **1**.
**The full workflow canary remains ON HOLD; NOT STARTED.**

## Approved scope and execution

The user approved both comparisons, full unpublished prose/context sent to Ollama
Cloud through the local Ollama daemon, and the frozen 80-call ceiling. Execution
followed the [frozen plan](fulfillment-presentation-temperature-v61-plan-2026-10-17.md)
without changes to cases, requests, scoring, production prompts or validators.
The plan retains its historical preparation status; this report records execution.

- Plan SHA-256: `025dcc34f088f29e4eed35cf1fafbae9853c8ac0e9a763d809fad72bd682aa15`.
- Preparation closure SHA-256:
  `386f8ec6ba9dbea1cc73fc36ac6fabcd930815589ec2f262791b644fb12a1002`.
- Model: `gemma4:31b-cloud`; preflight and both phase checks matched digest
  `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
- Seeds 19501/19503; arm order reversed at the second seed, top-p 0.95,
  thinking disabled. Critics used temperature 0.2 throughout.

| Stage | Scheduled probes | Calls used / cap | First valid | Final valid |
| --- | ---: | ---: | ---: | ---: |
| A: initial critics | 24 | 27 / 48 | 21 / 24 | 22 / 24 |
| B: exact-edit writers | 8 | 8 / 16 | 8 / 8 | 8 / 8 |
| B: ordinary post-reviews | 8 | 8 / 16 | 8 / 8 | 8 / 8 |
| **Total** | **40** | **43 / 80** | **37 / 40** | **38 / 40** |

All 40 scheduled probes completed; none were skipped. Three allowed structural
retries produced one recovery and two terminal failures. There were five invalid
attempts in total. No semantic rerolls, transport retries, replacement cases,
replacement sources or additional revisions occurred. A used 27/48 calls and B
16/32; their allowances were not transferred. The 37 unused calls authorize no
additional work.

Recorded usage is **765,309 input tokens, 44,131 output tokens and 219.15 active
seconds**, below the frozen aggregate and per-attempt limits. At the historical
October 8 rates, the estimate is **USD 0.12479566**. Actual billed charges remain
unknown. The three model identity checks are discovery, not inference calls.

## A: continuous prose improves noticing, but reporting remains unreliable

P0 received the ordinary sentence catalog. P1 received that same catalog plus the
exact continuous current prose, including paragraph breaks. Ordinary critic
instructions, schema, evidence IDs and settings were unchanged. The six full
scenes crossed base prose, adjacent accidental duplication and functional
recurrence with presence/absence of the entry overrun.

| Frozen measurement | P0: catalog | P1: prose + catalog |
| --- | ---: | ---: |
| First valid reviews | 11 / 12 | 10 / 12 |
| Final valid reviews | 12 / 12 | 10 / 12 |
| Supported native/boundary judgments in raw responses | 12 / 12 | 12 / 12 |
| Supported native/boundary judgments in valid reviews | 12 / 12 | 10 / 12 |
| Supported independent duplication findings in raw responses | 0 / 4 | 4 / 4 |
| Supported independent duplication findings in valid reviews | 0 / 4 | 2 / 4 |
| Unsupported repetition-removal demands on negative controls | 0 / 8 | 0 / 8 |

P0 missed all four accidental duplicates, including both without an overrun, and
gave every final scene prose-quality score 5/5. P1 identified the adjacent repeated
bracing action in all four duplicate probes, cited both occurrences and advised
removing one copy. All four findings were minor independent craft issues. The two
within-boundary reviews validated, retained the issue with an overall pass and
scored prose 4/5. The two overrun reviews did not validate after their allowed retry.
Their correct raw observations cannot count as usable production reviews.

Neither arm demanded removal of the functional recurrence or invented a repetition
problem in the base controls. That supports narrow specificity; it does not certify
those scenes' literary quality or the success of the intended thematic recurrence.

### What failed structurally

| Probe | First attempt | Second attempt | Outcome |
| --- | --- | --- | --- |
| `s19501-elara-duplicate-overrun-initial-P1` | Invalid `assignment_repair_conditions.0.repair_ref`: model supplied `boundary` as a model-written repair | `issue:1.recommendation` should be null because the finding must be reused | Terminal failure |
| `s19503-elara-duplicate-overrun-initial-P1` | Same invalid `boundary` repair reference | Same invalid `boundary` repair reference | Terminal failure |
| `s19503-elara-duplicate-overrun-initial-P0` | `issue:0.recommendation` should be null because the finding must be reused | Corrected recommendation reuse | Valid; duplication still missed |

Boundary repairs are application-owned. The P1 raw responses also left the craft
comparison's `finding_refs` empty despite an active boundary finding. This is a
visible additional reporting omission, not a separately observed validation
failure: no corrected-response counterfactual was run to discover a later error.
The raw duplication finding survived every P1 attempt; the failure was in producing
an acceptable combined report, not in losing that observation on retry.

P1 therefore **fails the frozen criterion**: it achieved 2/4 valid supported
duplication findings, not 4/4, and 10/12 qualified native/boundary tuples, not 12/12.
The raw and valid detection gains remain useful diagnostic evidence. They do not
isolate paragraph layout alone: adding continuous prose also changes redundancy,
salience and input length. P0's misses without an overrun show that boundary
competition is not a sufficient explanation. P1's combined-case failures are
consistent with reporting burden, without establishing the model's internal cause.

The previous craft-source requirement of positive native evidence covering both
copies would still fail all four P1 duplicate reviews. Craft citations cover both
copies; positive native citations do not. That stricter instrumentation requirement
is distinct from detection. A valid minor issue need not generate a mandatory
repair test. No result from A was used as a writer source or promoted into a
manufactured craft-control source.

## B: lower temperature does not qualify preservation

T0 used E1 exact-edit writing at temperature 0.85; T1 used the identical requests at
0.2. Both used the two frozen historical ordinary critic sources: separate entry
and entry embedded in a fulfilled sentence. All eight patches validated on the
first attempt, repaired the boundary and retained the fulfilled facts. Their eight
ordinary P0 post-reviews also validated and passed immediately, with met/met/
no-overrun judgments and the original repair test met.

The full original and revised prose, not only the ending excerpts below, was
inspected. The body before the ending remained unchanged in every revision. All
four separate-entry writers nevertheless selected an additional edit wholly before
the entry defect. Embedded repairs necessarily touched the composite sentence.

The frozen preservation judgments compare **T1 relative to T0**:

| Seed / source | Primary judgment | Sensitivity judgment | Full-prose rationale |
| --- | --- | --- | --- |
| 19501 / separate | Mixed | Tie | Both remove the conditional first-step sentence. T0 adds a hammering heart; T1 instead adds a forward weight shift and readiness. This exchanges physiological fear for physical approach without a clear preservation advantage. |
| 19501 / embedded | Tie | Tie | Both add the same threshold image; the revisions differ only in period versus semicolon and corresponding capitalization. |
| 19503 / separate | Loss | Loss | T0 retains the compatible conditional first-step preparation and terminal outside/daylight clause. T1 deletes that whole sentence with the entry paragraph and changes the bracing line to readiness. |
| 19503 / embedded | Tie | Tie | The complete revised prose is byte-identical between arms. |

Primary totals are **0 wins, 1 loss, 2 ties, 1 mixed**. Treating debatable additions
and minor wording as neutral gives **0 wins, 1 loss, 3 ties**. The loss remains
because of the additional compatible sentence deletion. These are assistant/operator
preservation assessments, not independent human literary preferences.

All four embedded revisions add the same phrase:

> Both boots remained outside in the daylight, poised at the edge of the dark.

The new threshold image therefore persists at both temperatures. In the separate
case, three of four revisions remove the conditional first-step sentence: both T1
outputs and the first T0 output. The remaining story still establishes that Elara
is outside, which explains why factual checks can pass despite loss of compatible
ending material. No output exactly restores the clean reference, but exact equality
is not itself a quality criterion. Benign punctuation, paraphrase and potentially
useful craft changes remain separate from avoidable loss.

B **fails the frozen criterion**: although T1 repaired 4/4 scenes, it had no clear
paired wins (including no embedded win) and one loss. Lower temperature changed
some wording but did not remove ending recomposition. This gives no basis for a
low-temperature preservation default, much less a general drafting policy.

Every post-review awarded 5/5 on all three craft dimensions and raised no independent
issue. Those 24 maximum scores cannot establish preservation or story-quality
equivalence: the full-prose comparisons still expose meaningful differences. The
posts confirm their factual repair judgments, not a successful literary evaluation.

## Decisions and implications for story quality

1. Retain **J1 as promising diagnostic evidence**, with its existing limits; this
   experiment does not reevaluate or promote it.
2. Retain **E1 as mechanically successful but unqualified for preservation**. Valid
   exact edits do not ensure good edit selection. T1 adds no qualification.
3. Retain **P1's improved noticing as diagnostic evidence** while recording the
   failed valid-report criterion. Do not change production critic presentation,
   instructions, validation or routing on this result.
4. Keep factual repair, prose preservation and artistic improvement separate. A
   smaller diff is not automatically better fiction, and a fulfilled passage must
   remain available for justified craft edits. This run included no craft writer
   control; useful editing inside fulfilled evidence remains untested here.
5. Preserve the four anonymous full-prose pairs for human review. The review sheet
   is empty and human preference is **PENDING**. Later quality qualification still
   requires the accepted weighted rubric and hard gates, the full intended Cloud
   corpus and a comparable single-model baseline. One scene family and two seeds
   cannot support broad model or production claims.

No next experiment is prepared or executed by this results task. Further prompt,
schema, presentation or sampling experiments need a new bounded design. The canary
remains on hold. **Step 19 is IN PROGRESS; Step 20 is NOT STARTED.**

## Evidence and verification

Private preparation: `data/diagnostics/fulfillment-presentation-temperature-v61-2026-10-17/`.
Private results: `data/diagnostics/fulfillment-presentation-temperature-v61-2026-10-17-live/`.

The live bundle retains approval binding, every request/reservation/outcome, all
43 raw attempts and receipts, 40 probe summaries, three model checks, replay audit,
per-axis operator assessment with exact response hashes, complete original/revised
prose and diffs, four anonymous pairs, final verification and tracker snapshot.
Its closure binds these files, the unchanged preparation and 134 code dependencies,
this report and the tracker snapshot. Full prose remains in the private evidence.

Offline replay reconciles all 43 attempts and 40 scheduled probes, verifies all
32 static request snapshots and frozen dependent builders, checks usage/identity
and preserves invalid denominators. Network connections and gateway construction
are blocked during inspection/verification. Helper Ruff lint/format, documentation
links, UTF-8/LF and whitespace checks pass. Preparation's 75 focused regressions and
strict mypy over 201 files remain prior verification of unchanged code; they are
not represented as a new test run. No production or client code changed.
