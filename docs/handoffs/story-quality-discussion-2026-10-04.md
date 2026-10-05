# Open Hollywood story quality discussion handoff

Prepared 2026-10-04 for the user and the next development chat.

The next conversation should begin with the user's additional observations and a
discussion of what makes these stories work or fall short. We have enough human
review evidence to investigate literary quality now. The immediate scope is to
understand the problems and choose a focused direction together; implementation
and new generation experiments will be scoped after that discussion.

## Current project state

The user has pushed v34 and updated `main`. At preparation, the working tree was
clean at commit `c0af3bd8519b18d9ed48bbb45fbe06f084f2589c`, the merge of
`codex/continuity-validation-v34`. Recheck Git state in the new chat because later
changes may supersede this snapshot.

- Development stage: **v0.1 in development**; v0.1-alpha is not complete.
- Current production contract: **prompt v34 / graph v9**.
- Current testing model: **`gemma4:31b` through Ollama Cloud**, requested through
  the local daemon as `gemma4:31b-cloud`.
- **Engineering item 5 is COMPLETE** as the repeatability assessment and formal
  evidence-sealing task. Every eligible human comparison was reviewed, all three
  campaigns were sealed and verified, and the consolidated report exists.
- **Product Step 19 remains IN PROGRESS.** Repeated technical acceptance has not
  been established, agentic preference remains below the accepted threshold, and
  monetary cost is unknown. Completing the assessment does not mean it passed.
- Step 20 has not been marked started. This handoff opens the quality discussion;
  update the authoritative tracker when an implementation scope is agreed.

No further repeat is needed to finish item 5. Preserve its endpoint and address
new findings through separately identified corrective work and experiments.

## Evidence to carry forward

| Evidence set | Completion and review status |
| --- | --- |
| September 12 manual run | 10/10 stories completed under v29; all reviewed |
| September 13 manual run | 12/12 completed across v29–v33; all reviewed |
| September 29 formal comparison | 11/12 Cloud and 12/12 baseline completed; all 11 eligible pairs reviewed and sealed |
| October v33 Repeat 1 | 12/12 Cloud and 12/12 baseline; 12 reviewed pairs |
| October v33 Repeat 2 | 12/12 Cloud and 12/12 baseline; 12 reviewed pairs |
| October v33 Repeat 3 | 10/12 Cloud and 12/12 baseline; 10 reviewed pairs |
| October 4 v34 continuity probes | Two isolated responses validated first attempt; each retained a blocker |

The three repeated runs remain **34/36 Cloud completions**, with **36/36 baseline
completions** and **184/192 accepted Cloud scenes**. The v34 probes do not change
those results and are not completed stories.

Across the 34 reviewed repeat pairs, weighted means were **4.1059 Cloud / 4.1529
baseline**. Preferences were **7 Cloud wins, 10 baseline wins and 17 ties**:
**45.59% Cloud preference** when ties receive half credit, below the unchanged
60% threshold. Cloud preference was below that threshold in each repeat.

The Cloud means for **character depth and consistency** and **voice and prose
quality** were **3.0 in every repeat**. These are especially useful starting
signals. Coherence and continuity scored well in completed, reviewed stories;
those scores do not validate every automated critic or continuity judgment.

Interpret the evidence within its limits:

- The manual reviews are qualitative assessments of operator-selected stories,
  separate from formal paired scores. Many Blueprints were approved blindly to
  see what the system could produce with little human steering. The user regards
  these outputs as first drafts and sees a promising foundation.
- From Repeat 1 onward, originality was rated as originality of the generated
  text given its premise. Dialogue ratings also allowed strong work needing minor
  editing, even when somewhat long. September's differently calibrated scores
  should not be pooled as identical evidence.
- The repeats reused the same premises, model configuration and per-prompt seeds,
  with fresh artifacts and no copied prior-story memory. Similar stories do not
  show that the model learned from earlier runs or became less creative over time.
  There was one reviewer, with increasing familiarity with the corpus.
- Cloud stories were generally longer than baselines. Word targets remain
  advisory; this comparison does not isolate length as a cause of preference.
- Repeats 1–2 used Ollama 0.35.0; Repeat 3 used the authorized 0.35.1 exception.
  Remote model weights and seed enforcement were not independently pinned.

## Four working areas for the discussion

These consolidate the previous discussion and the user's reviews. They are
directions to refine with the user's new observations, not a chosen implementation
plan or a set of new acceptance rules.

### Character depth and meaningful variety

The user finds that characters often remain close to their artifact descriptions,
with limited exploration of background, private motives and relationships. Names
and professions recur, and many characters inhabit financially secure professional
worlds: architects, designers, lawyers and similar occupations.

Across repeated premises, familiar choices recur too: bereaved fathers in the
stroller horror stories; a brother and sister debating scars or tattoos when
identifying their father's body; similar characters and settings in the
memory-currency stories. These are reviewer observations, not a fresh systematic
count of the manuscripts.

A useful hypothesis to examine is that variety must affect decisions. Changing a
name or occupation may leave the same story intact. Economic pressure, obligation,
complicity or a private desire could change what someone conceals, risks or refuses.
Inspect where these choices originate in pre-production and how drafting develops
them before assigning responsibility to the writer alone.

### Conflict and group dynamics with earned endings

The reviews describe linear protagonist–antagonist relationships, limited group
reactions and weak development of bonds with supporting characters. Earlier
feedback also identified endings as a concern. Faithful artifact execution can
still produce an emotionally thin story.

The priest/criminal premise is a useful example: the user suggested a corrupt
priest, a culpable protected person, or protection that goes badly wrong. These
are examples of different dramatic possibilities, not mandatory plot replacements.
The frozen premise already permits moral complexity, changing leverage and agency
for the protected person.

Discussion should examine whether distinct interests actually alter alliances,
choices and consequences, and whether the ending grows from those choices. More
backstory or more conflict-related wording alone would not establish improvement.

### Dialogue that continues to change the scene

The user often prefers the shorter exchanges; longer dialogue can become
repetitive or lose force. This observation coexists with high formal dialogue
scores and does not invalidate those grades.

A question for review is what each exchange changes: information, leverage,
commitment, a relationship or a decision. Longer exchanges may earn their space;
there is no agreed dialogue-length cap. We should inspect whether the dialogue
process helps characters act on distinct motives or merely restates the situation.

### Prose variety and purposeful description

The AI-patterns document and manual review summary identify contrastive framing,
sibling/triplet framing, incongruous metaphors, recurring names, scene-ending
summaries and repeated word combinations. The sensory-language concern is
specifically the repeated construction in which a sensory trigger leads to two
descriptors, often involving air and ozone. Modifiers and sensory detail themselves
are not the problem.

The user reported roughly twenty contrastive constructions in some short stories,
with more than thirty reported for one story, and repeated pairings such as ozone
with scorched plastic. These observations motivate investigation; they are not
automatic detector outputs or approved numeric limits.

The desired description reveals the place through what matters to the character
and the scene. A linguist entering a vault, for example, may attend to signs,
instructions or documents. Sensory detail can still serve that purpose. Review
repetition in context, including its distribution across the whole story, rather
than treating every occurrence of a construction as a defect.

## User preferences and product constraints

- **No bans** on contrastive framing, triplets, sensory language, particular words
  or professions. The goal is purposeful use and less clustered repetition. A
  preference expressed strongly in an individual review is not permission to turn
  it into a universal prohibition or hard quota.
- **Keep existing retry allowances, limits and prompt length.** Prefer clearer
  responsibilities and better use of existing passes and context over additional
  repeated instructions, agent calls or revision loops.
- Preserve the autonomous short-prose workflow and its one mandatory human
  checkpoint: approval of the exact Story Blueprint before drafting.
- Preserve canonical story truth, immutable artifacts, observable calls and
  bounded context. Real contradictions and explicit story obligations still matter;
  literary advice should not become an unsupported continuity blocker.
- The UI remains chat- and artifact-centered, without a general-purpose
  manuscript editor. The user has raised passage comments/rewrite requests and
  learning from preferences as ideas for discussion. Neither feature has been
  selected or implemented for this work. Any preference-memory proposal needs an
  explicit scope and provenance; storing feedback would not itself train model
  weights or guarantee future behavior.
- The user plans limited testing with other models after v0.1-alpha, potentially
  GPT and Gemini, but has not selected models. Keep improvements provider-neutral;
  this discussion is not a request to switch models now.

## Continuity issues that remain open

The v34 changes address two response-contract failures. Both authorized frozen-input
Cloud probes validated in one attempt, but neither cleared its scene's continuity
gate. No writer or adjudicator ran in those probes.

- **OH-V01-002:** the repeated-handwriting-verification allegation returned through
  the new-findings route. Historical identity matching restored its old ID and
  `still_blocking` disposition, so the guard for newly exposed findings did not
  apply. Repeated investigation can be redundant without contradicting an earlier
  investigation. Both the semantic judgment and the recurrence path need attention.
- **OH-V01-010:** the missing time cue became advisory as intended. A separate
  back-door finding requested a deletion explanation already present immediately
  after the cited passage. This suggests poor use of adjacent counterevidence;
  the Blueprint's timing and secret still need a complete contextual comparison.

Keep these visible as targeted reliability work. They do not prevent a quality
discussion, but they matter when judging whether revisions preserve good prose
and whether future production is dependable. The findings remain documented in
ADR 0018; do not describe the stories as recovered or reopen the sealed repeats.

## How to begin the new chat

Start by hearing the user's additional observations. Preserve the distinction
used in the manual reviews: recognizable writing patterns, faithfulness to story
artifacts, and the reader's overall literary judgment.

Then use a few concrete passages and their source artifacts to distinguish the
observed weakness from a hypothesis about its cause. For example, determine
whether a flat relationship was already underspecified in the Blueprint, lost
during drafting, or flattened during revision. The human reviews establish what
the reader experienced; they do not by themselves identify the responsible stage.

After discussion, agree on one bounded first change and how its effect will be
assessed. Potential approaches such as more consequential character planning,
context-aware repetition diagnostics, bounded editorial feedback or explicit
preference artifacts remain options, not decisions recorded by this handoff.

For later experiments, preserve v34 as the starting comparison and record new
versions separately. Keep technical completion, human quality and preference as
distinct outcomes. A focused revision test can establish a local effect, while
a separately scoped fresh production test is needed to assess story completion.
Use blind human comparisons for quality claims, retain failures, and examine
both the targeted improvement and any damage to already-effective passages.
Different premises or varied seeds may help investigate variety, but constitute
a new experiment. Existing scores and acceptance thresholds remain unchanged.

## Reading order and evidence locations

All links below are relative to the repository. The workspace used for this
handoff is `C:\Users\sasad\Desktop\Projects\openHollywood`.

1. [Updated AI patterns](../september_2026_manual_test_reviews/AI-patterns.md)
   and [manual review summary](../september_2026_manual_test_reviews/review-summary.md).
   Read these as the user's observations and preferences, with the no-bans
   clarification above.
2. [All 22 manual reviews](../september_2026_manual_test_reviews/), including
   [Alyssa](../september_2026_manual_test_reviews/Alyssa-review.md) as an example
   of the three-part review format. Select additional reviews with the user.
3. [Consolidated v33 repeatability assessment](../benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md),
   especially the final consolidated assessment and reviewer observations.
4. [Earlier formal comparison](../benchmark_reports/step-19-formal-cloud-v33-execution-2026-09-29.md)
   and the [September 12](../benchmark_reports/manual-v29-cloud-production-2026-09-12.md)
   and [September 13](../benchmark_reports/manual-v29-v33-cloud-production-2026-09-13.md)
   manual diagnostics, as needed for provenance.
5. [v34 decisions and live probe findings](../adr/0018-current-continuity-rechecks-and-compact-coverage.md).
6. [Authoritative tracker](../../open_hollywood_bible/step_by_step_implementation.md),
   [product contract and evaluation criteria](../../open_hollywood_bible/product_contract_and_benchmarks.md),
   [important decisions](../../open_hollywood_bible/important_decisions.md) and root
   [AGENTS.md](../../AGENTS.md) before proposing implementation changes.

Raw repeated-run stories, CSVs, private mappings and diagnostics remain under
`data/benchmarks/v0.1/formal-cloud-v33-repeat-{1,2,3}-2026-10-02/`. The consolidated
register is under `data/benchmarks/v0.1/v33-cloud-repeatability-2026-10-02/`.
The v34 probe packets and reports are under
`data/diagnostics/v34-continuity-validation-2026-10-04/live/`.
These local directories are Git-ignored and may be absent in another checkout.
Consult available repository reports first; do not infer missing manuscripts,
scores or diagnostics. The user's new observations may refine these priorities.
