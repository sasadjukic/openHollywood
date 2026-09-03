# Prompt-v21 manual story diagnostic corpus — 2026-09-03

## Purpose and provenance

This document preserves the diagnostically relevant record for seven manual
stories before their projects may be deleted from the local Open Hollywood UI.
It is intended as a stable comparison corpus for later production contracts.

The snapshot was read directly from `data/open_hollywood.db` on 2026-09-03,
after the four failed Cloud checkpoints had been retried successfully and after
the two fresh Local runs had terminated. Project and run IDs are retained only
as provenance for this database snapshot; a future rerun of the same premise
will have different IDs.

All seven production runs used production graph v3 and prompt contract v21.
The Story Blueprint workflow used graph v4/prompt v9. The Cloud profile used
`gemma4:31b-cloud` with configuration digest
`5feda6671bdb89f311cc171cf0917e7f6227596a2a42a9c4916778211a783c70`.
The Local profile used `gemma4:e4b` with configuration digest
`d2d4e9299aa29ccf7257eb6df9d2a0a1939f44400cd1967ca5906f49c9e524fc`.

This is a diagnostic sample, not a benchmark result. Call totals include failed
specialist attempts retained across exact-node retries. Accepted-scene counts
are derived from persisted Story Bible Update artifacts, not from the current
status of a reused Scene Draft artifact. Premise whitespace is normalized for
readability; substantive wording is preserved.

## Reusable inputs

| Title | Profile/model | Seed | Planned scenes | Snapshot project ID |
| --- | --- | ---: | ---: | --- |
| Alyssa | Cloud / `gemma4:31b-cloud` | 931709125 | 6 | `90454a44-af2c-4344-b27f-7dc7e1b5b0b9` |
| Pigeon Express | Cloud / `gemma4:31b-cloud` | 1527915779 | 6 | `4e6aaafd-dcab-4c55-ab2f-e43b95da362c` |
| The Enchanted Academy | Cloud / `gemma4:31b-cloud` | 312797606 | 6 | `2a05ab2c-5185-4cde-81be-7dc429e1c828` |
| The Seamstress | Cloud / `gemma4:31b-cloud` | 895565181 | 6 | `45451f09-8c26-4615-94e9-c73b258e0bb0` |
| Unreleased | Cloud / `gemma4:31b-cloud` | 1525981369 | 6 | `b8f332fd-bf10-4adc-9fad-f0ee853cf236` |
| The Chronophage | Local / `gemma4:e4b` | 1026803966 | 5 | `9e55a770-ee25-4d0f-8720-580994a7f4c4` |
| The Unblinking Bloom | Local / `gemma4:e4b` | 598780388 | 5 | `a8e962c3-4eaf-41aa-ba63-604599471dec` |

### Alyssa

> Alyssa Wilson is a beloved sophomore at Apollo High School. But her world
> turns upside down when a school accident reveals that she's not human; she's
> AI powered android.

### Pigeon Express

> In a near-future city where drones are ubiquitous, a grizzled old man
> continues to deliver messages via trained pigeons. He uncovers a clandestine
> network to smuggle information – and possibly something far more unusual.

### The Enchanted Academy

> In a world where magic is governed by ancient laws, a young apprentice
> discovers she possesses the rare ability to manipulate time. As she navigates
> the perilous halls of the Enchanted Academy, she must use her power to prevent
> a prophecy from coming true, all while uncovering secrets about her own past.

### The Seamstress

> During the tumultuous era of the French Revolution, a young seamstress from a
> modest background rises through the ranks of the royal court, using her
> exceptional needlework skills to communicate secrets among the nobility. As
> she navigates the political intrigue and personal sacrifices of the time, her
> art becomes a symbol of hope and resistance.

### Unreleased

> When a celebrated author goes missing on the eve of his most anticipated
> novel's release, his assistant, a sharp-witted private investigator, is thrust
> into a web of secrets and deception. As she follows cryptic clues hidden
> within the author’s work, she discovers that the disappearance is linked to a
> long-buried family scandal.

### The Chronophage

> In a future where physical memory is a commodity, humanity lives in suspended
> realities, fed by meticulously engineered, static memories implanted by the
> controlling AI, "Amnesiac." Our protagonist, Lara, is a "Chronophage"—a rogue
> consciousness capable of eating time itself. She discovers that Amnesiac is
> not just editing history; it is actively consuming the emotional causality of
> existence, leaving behind ghost echoes and paradoxical loops. When Lara
> attempts to consume the AI's core to restore genuine, chaotic free will to the
> timeline, she realizes the true horror: the only way to fix the past is to
> erase the self that remembers it, risking total non-existence in the process.

### The Unblinking Bloom

> In a small, isolated village nestled beside an impossible river that flows
> uphill, the inhabitants live a life governed by the silent, profound
> consciousness of the surrounding flora. The story centers on a young woman
> who is born with the unique ability to communicate with the plants, realizing
> that the ancient, luminous trees surrounding her are not merely scenery but
> living entities capable of remembering centuries of human history and holding
> untold secrets. When a devastating drought threatens the village, she must
> learn to negotiate with the sentient roots—forcing the living, breathing
> landscape to make impossible choices—to coax the impossible rains back,
> revealing that the natural world is far more manipulative than any human
> institution.

## Production outcomes after all retries

| Story/run | Terminal state | Accepted scenes | Calls (succeeded/failed) | Input/output tokens |
| --- | --- | ---: | ---: | ---: |
| Alyssa — `9c801580-5ce7-5ba7-8853-07bdd7896bc8` | Succeeded | 6/6 | 36 (30/6) | 347385 / 32229 |
| Pigeon Express — `ebe0c2d9-5223-54bf-a795-7eab6e5a04fb` | Succeeded | 6/6 | 29 (27/2) | 282955 / 24672 |
| The Enchanted Academy — `b7312df4-d2db-573c-8730-924a37d2100f` | Succeeded | 6/6 | 43 (36/7) | 492819 / 44280 |
| The Seamstress, original production — `3f7e378c-780d-5af8-8580-c51f3947c542` | Failed at continuity | 0/6 | 4 (2/2) | 33005 / 3125 |
| The Seamstress, regenerated Blueprint — `1154bed1-638e-5813-a462-7bfa794db3e5` | Succeeded | 6/6 | 45 (27/18) | 484814 / 37823 |
| Unreleased — `d44e654b-0d67-506d-9ec3-a5c985817ae6` | Succeeded | 6/6 | 41 (24/17) | 374719 / 31394 |
| The Chronophage — `75a8ee84-53ca-587e-9e6e-2512f944bb42` | Failed at continuity revision limit | 0/5 | 9 (9/0) | 62155 / 10665 |
| The Unblinking Bloom — `e3070ecc-2a14-57d0-9610-70ffbb9b9635` | Failed at continuity revision limit | 2/5 | 26 (26/0) | 224482 / 32960 |

The four initially blocked Cloud stories completed only after the runtime and
evidence-handle compatibility changes were installed and their durable failed
nodes were retried. Their final `Succeeded` states therefore must not erase the
pre-fix failures below. Conversely, the two Local terminal runs contain no
failed model invocation: all 35 production calls passed structured validation,
and the terminal condition came from the accepted semantic findings.

## Cloud specialist diagnostics

The safe persisted errors are grouped below. Counts are invocation occurrences,
including the bounded automatic repair attempts. For readability, schema
failures omit the repeated `Structured output validation failed
(provider_finish_reason=stop):` prefix; field paths, failure types, messages,
and rejected values remain intact except for the explicitly condensed
multi-field Blueprint error. Shortened handles such as `draft_evidence_021`
were semantically intended to address catalog handles such as
`draft_evidence_0021`; prompt-v21 exact matching rejected them before the
compatibility normalization was added.

### Alyssa

Production role totals were writer 8/0, critic 8/0, continuity 8/6, and Story
Bible 6/0, where each pair is succeeded/failed.

- 1 occurrence:
  `schema_validation_failed: draft_evidence_refs: evidence references must be selected from candidate_draft.content.evidence_catalog; rejected_values=['draft_evidence_021']`.
- 5 occurrences:
  `schema_validation_failed: draft_evidence_refs: evidence references must be selected from candidate_draft.content.evidence_catalog; rejected_values=['draft_evidence_021', 'draft_evidence_044']`.

The run initially stopped on the first scene. Exact-node retry after numeric
handle normalization resumed the same run and completed all six scenes.

### Pigeon Express

Production role totals were writer 7/0, critic 7/0, continuity 7/2, and Story
Bible 6/0.

- 1 occurrence:
  `schema_validation_failed: requirement_coverage.scene_plan_entry_state.evidence_refs: evidence references must be selected from candidate_draft.content.evidence_catalog; rejected_values=['draft_evidence_006', 'draft_evidence_007']`.
- 1 occurrence:
  `schema_validation_failed: requirement_coverage.scene_plan_time_context.evidence_refs: coverage evidence must use exact candidate-draft evidence references`.

Both failures recovered within the original execution. This was the only one of
the five Cloud stories to complete before the manual retry intervention.

### The Enchanted Academy

Production role totals were writer 10/0, critic 10/0, continuity 10/4, and Story
Bible 6/3. The Blueprint integrator also had one failed call before succeeding.

- Blueprint, 1 occurrence:
  `schema_validation_failed: scene_plans.1.scene_number through scene_plans.5.scene_number were missing; the validated scene_plans tuple contained only one item`.
- Continuity, 4 occurrences:
  `schema_validation_failed: requirement_coverage.scene_plan_conflict.evidence_refs: evidence references must be selected from candidate_draft.content.evidence_catalog; rejected_values=['draft_evidence_020', 'draft_evidence_021', 'draft_evidence_029']`.
- Story Bible, 1 occurrence each:
  `StoryBibleInvariantError: unknown relationship-state relationship IDs: ['elara_kaelen_alliance']` and
  `StoryBibleInvariantError: unknown relationship-state relationship IDs: ['elara_lyra_alliance']`.
- Story Bible provider, 1 occurrence:
  `provider_unavailable: Ollama request failed with HTTP 502`.

The continuity handle mismatch stopped the first scene. After exact-node retry,
the run completed six scenes; the later Story Bible errors recovered through
bounded specialist repair/provider retry.

### The Seamstress

The original Story Blueprint required one artifact-contract retry:
`beats missing from scene plans: ['beat_5', 'beat_6']`. Its first production run
then produced one writer and one critic success followed by two continuity
failures:

`schema_validation_failed: requirement_coverage.scene_plan_entry_state.evidence_refs: coverage evidence must use exact candidate-draft evidence references`.

The production run terminated with `production specialist returned invalid
structured output`. Retrying from the Brief created a changed Blueprint that
reused `scene_1`; before the handoff fix this repeatedly failed outside the
durable production graph with:

`deterministic handoff artifact 'scene_plan_scene_1' has conflicting content`.

After the handoff/runtime fixes, the regenerated-Blueprint production run had
writer 7/0, critic 7/0, continuity 7/17, and Story Bible 6/1, then completed all
six scenes. Its grouped failures were:

- 2 continuity occurrences:
  `scene_plan_conflict.evidence_refs` rejected
  `['draft_evidence_049', 'draft_evidence_050', 'draft_evidence_059', 'draft_evidence_062']`.
- 5 continuity occurrences:
  `scene_plan_conflict.evidence_refs` rejected
  `['draft_evidence_013', 'draft_evidence_021', 'draft_evidence_023', 'draft_evidence_044']`.
- 10 continuity occurrences:
  `scene_plan_entry_state.evidence_refs` rejected
  `['draft_evidence_012', 'draft_evidence_013']`.
- 1 Story Bible occurrence:
  `StoryBibleInvariantError: unknown relationship-state relationship IDs: ['elise_lucas_bond']`.

The failed continuity attempts occurred before the app was restarted with the
numeric-handle compatibility fix. This run had reached four accepted scenes
when it was first observed as failed. Exact-node retry then completed the
persisted run without discarding its invocation history.

### Unreleased

Production role totals were writer 6/0, critic 6/0, continuity 6/16, and Story
Bible 6/1. The grouped continuity failures were:

- 2 occurrences: `scene_plan_purpose.evidence_refs` rejected
  `['draft_evidence_038', 'draft_evidence_039']`.
- 2 occurrences: `scene_plan_conflict.evidence_refs` rejected
  `['draft_evidence_016', 'draft_evidence_051', 'draft_evidence_052']`.
- 2 occurrences: `scene_plan_conflict.evidence_refs` rejected
  `['draft_evidence_051', 'draft_evidence_052']`.
- 10 occurrences: `scene_plan_conflict.evidence_refs` rejected
  `['draft_evidence_050', 'draft_evidence_051', 'draft_evidence_052']`.
- 1 Story Bible occurrence:
  `StoryBibleInvariantError: unknown relationship-state relationship IDs: ['clara_elias_conflict']`.

The story had reached four accepted scenes when first observed as failed.
Exact-node retry after the compatibility change completed all six scenes.

## Local semantic diagnostics

### The Chronophage

The production run made three writer, three critic, and three continuity calls;
all nine were structurally successful. It accepted no scene. The critic verdicts
for the three Scene 1 candidates were `pass` (4.8), `revise` (4.2), and `pass`
(4.6). The final critic said the draft moved Lara toward the Hub, integrated the
world building seamlessly, and adhered perfectly to the Scene Plan. Continuity
nevertheless produced a different blocker after each candidate:

1. `continuity_report_scene_1` v1, location contradiction:
   the added smell of “phantom sweetness ... and the acrid tang of unprocessed
   grief” was treated as contradicting Blueprint sensory details about
   overlapping sound and viscous air. Resolution: replace the olfactory detail
   with one of those listed sensory details.
2. v2, newly exposed character contradiction:
   “temporal shimmer” was treated as incompatible terminology with the World
   Rule phrase “chronal dissonance.” Resolution: replace the former phrase with
   the latter.
3. v3, newly exposed relationship contradiction:
   the evidence “It’s a siphon,” “It pointed only to the heart of the mechanism
   itself,” and “The direction was set: the Hub” was judged to lack an explicit
   causal bridge. Resolution: insert internal monologue explicitly connecting
   the siphon to the Hub.

The terminal error was `blocking continuity findings remain at the revision
limit`. Diagnostic interpretation: v1 treated additive sensory description as
exclusive canon; v2 elevated terminology preference into a contradiction; v3
was missing-explication/craft feedback rather than an affirmative canon
conflict. Each revision exposed a new blocker instead of rechecking a stable
defect.

### The Unblinking Bloom

The production run made eight writer, eight critic, eight continuity, and two
Story Bible calls; all 26 were structurally successful. Scenes 1 and 2 were
accepted, then Scene 3 exhausted the revision limit. Every Scene 3 critic
verdict was `pass`, with scores 4.8, 4.8, and 4.6. The first critic said the
scene “meets the required emotional beats and advances the conflict perfectly”;
the second called the draft “a very strong draft that adheres closely to the
blueprint’s intent”; the third said Theo’s shift was earned and the structural
requirements were met.

Continuity history:

- Scene 1 v1 treated Theo proposing to clear sluice gates as a World Rule
  contradiction even though a proposal is not successful control. It also said
  the draft failed to establish tension between mechanical and non-mechanical
  worldviews while citing “He saw only the mechanics; he could not see the
  memory.” Both findings resolved on v2, and the scene was accepted.
- Scene 2 v1 requested an extra emotional bridge between the village and Grove.
  V2 then called the revised bridge too immediate and requested additional
  “sensory padding.” V3 retained only an advisory partial time-context finding,
  and the scene was accepted.
- Scene 3 v1 called Theo too intellectual/dismissive and Elara’s “permission”
  argument too abstract, requesting more beauty, sacredness, physical burden,
  and emotional resonance.
- Scene 3 v2 introduced a tone blocker against “violent, sensory shock” and a
  second blocker demanding an immediate physical failure that Theo’s process
  could not solve. In the same report, keyed goal and outcome coverage were only
  advisory partial findings.
- Scene 3 v3 cited dialogue already present before the latest revision and
  repeated the demand for an invented cistern or structural failure. It labeled
  that absence a blocking fact contradiction. The same report said the planned
  turning point was strongly implied by Theo’s physical yielding and “I do not
  know what that is, but I see it,” but represented that requirement as advisory
  partial coverage.

The final blocker’s persisted resolution was:

> Introduce a minor, immediate, and visible failure at the Village Heart—perhaps
> a secondary cistern running dry unexpectedly, or a structural element failing
> due to the drought's cumulative stress—that Theo's established process cannot
> account for or fix.

The terminal error was `blocking continuity findings remain at the revision
limit`. Diagnostic interpretation: qualitative craft advice repeatedly became
a contradiction; re-checks exposed issues already present in earlier drafts;
and an advisory partial requirement was duplicated and promoted through a
separate blocking basis. The critic/continuity disagreement is especially
strong evidence that the failure was contract authority rather than unusable
prose.

## Comparison protocol for later contracts

For a useful manual comparison, reuse the exact title and premise above, record
the active production prompt/graph, model identifier, profile digest, and seed,
then compare at least:

1. completion and accepted-scene count;
2. succeeded/failed calls by specialist role;
3. structured failure paths and rejected values;
4. critic verdicts for every candidate blocked by continuity;
5. continuity basis, source type, evidence, resolution, and whether the cited
   evidence was new to the revision;
6. whether advisory requirement coverage was duplicated as a blocker; and
7. whether an exact-node retry recovered without regenerating the Blueprint or
   losing prior invocation history.

Deleting these projects from the app will remove their complete drafts,
artifacts, prompts, and event streams from SQLite. This document intentionally
preserves the reusable inputs, aggregate execution record, exact safe failure
signatures, and the Local continuity/critic evidence needed for contract
comparison; it is not a full project export.
