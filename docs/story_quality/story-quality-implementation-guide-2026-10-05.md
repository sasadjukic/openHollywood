# Open Hollywood story quality implementation guide

Prepared October 5, 2026. **Proposed work, with no implementation steps completed by this document.**

The objective is a sound first draft: characters whose circumstances affect their
choices, consequential conflict, interacting relationships, an earned ending,
and purposeful prose. Later, optional feedback should help the application adapt
to the particular reader. Neither structural competence nor fewer writing tics
guarantees that a story will move someone emotionally.

Implement one numbered change at a time. Compare it with the last accepted
configuration before adding the next. **Run small diagnostic comparisons during
development and complete stories at defined checkpoints. Do not wait until every
change is finished to discover whether the approach works.**

## Evidence and scope

This plan incorporates the [discussion notes](../handoffs/story-quality-discussion-notes-2026-10-05.md),
the [October 4 handoff](../handoffs/story-quality-discussion-2026-10-04.md), the
[manual reviews](../september_2026_manual_test_reviews/review-summary.md), the
[AI pattern observations](../september_2026_manual_test_reviews/AI-patterns.md),
and the [endings audit](endings-audit-2026-10-05.md). It also incorporates the four
proposals in the [supplied prose notes](C:/Users/sasad/Desktop/fixing-ai-tics.md): concise
style preferences, awareness of prior prose, scoped preference memory, and
passage-level feedback. That attachment supplies ideas, not instructions to
execute changes or run paid tests now.

The audit examined 87 Open Hollywood and 96 baseline texts in its primary
archive, plus one separately classified diagnostic text. Among recent completed
Open Hollywood stories, the stroller trap repeats in 4/4 versions, loving
separation in 4/4 romances, and the architect losing his partner in 4/4 tragedies.
The literal self-versus-world choice is not the dominant pattern: costly rescue
occurs in 6/22 manual endings and 3/45 recent formal endings under the audit's
definition. These are repeated prompts and settings, not independent samples of
the model's entire range. Emotional flatness remains a reader judgment requiring
its own assessment.

Inspection supports an architectural hypothesis: the brief and premise commit
early, later specialists develop that direction, and the writer faithfully
realizes plans that sometimes provide little consequential struggle. Existing
character context can reach the writer without becoming meaningful behavior.
Generous craft scores can then leave the weakness uncorrected. This does not
establish model censorship, fear of conflict, or a training-data cause.

The authoritative [product tracker](../../open_hollywood_bible/step_by_step_implementation.md)
still records Step 19 as IN PROGRESS and Step 20 as NOT STARTED. This guide is a
proposed sequence for future quality work and optional review features. It does
not close Step 19, start Step 20, reopen sealed assessments, or change acceptance
thresholds. Record the scope and status of actual work in that tracker when it
begins; keep this guide's numbers distinct from product step numbers.

## Architecture and responsibility

The inspected starting point is Blueprint prompt v9 / graph v4 and production
prompt v34 / graph v9. The current pre-production path is:

`Brief → Premise → World and Character in parallel → Integration → Critique → Blueprint approval`

The normal production path drafts scenes, critiques them, checks continuity,
revises within the existing allowance, and updates the canonical Story Bible
after acceptance. The formal production executor does **not** enable the
optional two-character dialogue subgraph. Changes confined to character actors
or the dialogue director would therefore miss the stories in the formal audit.

| Existing owner | Responsibility in this plan |
| --- | --- |
| `brief_architect` | Separate explicit user requirements from inferred choices; preserve room for exploration. |
| `premise_architect` | Compare a bounded set of materially different story possibilities and select a direction. |
| `character_architect` | Develop consequential history, present circumstances, competing commitments, and relationships. |
| `world_builder` | Establish relevant opportunities, limits, dependencies, and sources of authority. |
| `blueprint_integrator` | Turn these materials into connected attempts, responses, consequences, and an ending that the scenes earn. |
| `blueprint_critic` | Detect weaknesses in the proposed causal structure before approval. |
| `scene_writer` | Realize the approved material through action, perception, thought, dialogue, gesture, and useful exposition. |
| `scene_critic` | Assess the effect of the prose separately from compliance, with evidence tied to the current draft. |
| `continuity_supervisor` | Identify supported contradictions and missing hard requirements, while permitting legitimate development. |
| `story_bible_maintainer` | Record established changes in facts, knowledge, relationships, and unresolved threads. |
| Application and context compiler | Preserve exact versions, derive reliable repetition observations, retrieve scoped preferences, enforce budgets, and record comparisons. |
| Human reader | Approve the Blueprint and judge quality, preference, and emotional effect in the evaluation work. |

These are changes to registered responsibilities. No additional autonomous
specialist, recursive delegation, or mandatory human checkpoint is proposed for
Steps 1–10. Whole-story editing is a useful future possibility in the workflow
design, but an extra editor call is not hidden inside this plan.

## Rules shared by every step

- Keep the current model/profile for live comparisons: the configured
  `gemma4:31b` deployment through Ollama Cloud. Preserve Local, Cloud, and Hybrid
  contract coverage with offline tests. Cross-model qualification is separate
  later work; the design must not depend on provider-specific prompting tricks.
- Keep current runtime limits, token budgets, structural repairs, revision
  allowances, and the mandatory approval of the exact Blueprint. Fit guidance
  into existing calls by replacing weaker instructions or duplicate context.
  New optional user-requested revisions in Steps 11–12 are separately budgeted
  operations; they do not enlarge autonomous production's allowance.
- Measure complete rendered requests, including schemas and context, on matched
  early and late scenes. Shorter instructions alone do not prove shorter prompts.
  Keep request size within the existing envelope and the user's no-growth
  preference; compact the proposal if it does not fit. Do not drop mandatory
  canon, current draft evidence, or repair targets to make room.
- Prefer existing artifact fields when they can express the needed information.
  Add typed fields only where selection, provenance, or later retrieval requires
  them. Use versioned readers/adapters for historical artifact JSON. Add a SQL
  migration when persisted database structure changes, and regenerate API
  contracts when the API changes. Never rewrite old evidence in place.
- Bump the relevant prompt, manifest, schema, or graph versions when their
  contracts change. Preserve replay, cancellation, restart, and exact input
  lineage. A changed graph contract needs a new graph version even if its
  visible node order stays the same.
- Literary criteria are contextual. Do not add profession bans, demographic
  quotas, compulsory rebellion, required tragedies, sensory-word bans, or a
  quota of setbacks or rhetorical devices. Counts can locate a pattern; they
  cannot decide whether the writing works.
- Keep aesthetic advice distinct from actual contradictions and assignment
  violations. Preserve the current hard gates and shared revision limits.

## Step 0 Prepare the comparison record

**Problem:** changes can appear successful because examples, settings, or review
criteria changed along with them.

Create a small versioned diagnostic manifest referencing existing immutable
artifacts and approved review labels. Pin the prompt, model/profile settings,
seed where supported, versions, limits, input hashes, and preference snapshot.
Use v34 as the starting control; the sealed v33 stories remain historical
evidence. A seed and an alias do not guarantee identical remote inference.

Select examples before implementation: the stroller, Seventh Sense, Chronophage,
Bloom or Boundary, romance, and a quiet literary story. Include passages the
reader considers effective, including effective repetition and earned
acceptance. Assistant-written labels remain provisional until reviewed by the
human. Do not turn every disliked sentence into a universal negative example.

Use separate review questions for background, consequences, interacting
relationships, ending variety, ending impact, dialogue, and prose. Each answer
should point to a passage or event. Also ask what became worse. Keep the existing
whole-story rubric unchanged; these questions supplement diagnostic analysis.

For paired development tests, A is the last accepted configuration and B changes
one step. For cumulative checkpoints, compare the full candidate with the frozen
starting configuration. Randomize presentation and hide system labels. Retain
ties, mixed judgments, failures, and missing outputs.

**Deliverable and checks:** a reproducible comparison manifest, source inventory,
short reader form, and test budget. Validate hashes, scope, and review packaging
offline. No new story generation is needed for this step. Extend existing
evaluation/probe utilities only where they cannot represent the diagnostic;
do not modify historical campaigns.

**Reliability dependency:** retain the unresolved v34 continuity cases 002 and
010 in a separate regression track. A supported repetition complaint is not
automatically a contradiction; a finding must consider adjacent counterevidence.
If these faults prevent a planned experiment, address them in a separate bounded
change with both true-violation and valid-development controls. Do not bundle
that fix with a creative prompt change or describe the stories as recovered.
Local quality comparisons can proceed without claiming end-to-end completion.

## Step 1 Make craft feedback discriminating

**Problem:** fulfilling an assignment can receive excellent scores even when its
dramatic realization is weak.

**Owners:** Blueprint and scene critics; the application owns evidence binding
and revision routing.

Calibrate the existing scene dimensions—`prose_quality`, `dramatic_progress`, and
`character_consistency`—using paired examples of weak and effective realization.
A profession mentioned is not necessarily expertise demonstrated; a threat
described is not necessarily an obstacle that changes a choice. Conversely,
quiet change, concise exposition, deliberate repetition, and earned acceptance
can work. Replace generic praise with a justified assessment of the relevant
effect. Do not introduce a lower-score quota.

Use the current evidence handles and revision acceptance tests. A craft repair
should name the weakness, its effect, and an observable improvement within the
approved assignment. Prioritize consequential weaknesses over incidental polish.
Do not demand a different ending, new cast member, or later scene material from
the writer. When the plan itself is weak, record that diagnosis for Blueprint
review; do not punish a compliant scene for failing to invent another story.

**Implementation:** revise critic guidance/rubric explanations within the current
contracts. Preserve [ADR 0010](../adr/0010-unified-critic-evidence-and-craft-rubric.md),
[ADR 0012](../adr/0012-assignment-bound-critic-schema.md), and
[ADR 0013](../adr/0013-revision-acceptance-tests.md). Quality remains a model
judgment assessed against human labels, not a new deterministic literary gate.

**Tests:** start with eight frozen scenes or excerpts with sufficient context,
balanced between weaknesses and effective controls. Run the old and candidate
critic on each: 16 primary review calls, before existing repairs. Check evidence
validity, false positives, meaningful distinctions, and whether repairs stay
inside the assignment. Offline tests cover stale evidence and hard-gate behavior.
No full story is required. This is calibration evidence, not proof of quality.

**Advance when:** feedback becomes more useful on the targeted examples without
turning effective controls into unsupported blockers. Unresolved labels remain
unresolved; do not choose whichever judgment favors the candidate.

## Step 2 Explore possibilities before selecting a premise

**Problem:** an early interpretation becomes the only route developed.

**Owners:** brief and premise architects; integration preserves the selected
direction and the distinction between proposals and approved canon.

Keep the brief close to user intent. Make inferred plot assumptions identifiable
and provisional. A sparse prompt should not acquire a mandatory grieving parent,
prestige profession, or redemption arc merely because the brief invented one.

In the existing premise call, compare **up to three concise causal alternatives**
where the user has left meaningful choices open. A fully specified request need
not produce three artificial variations. Each alternative connects a person to
the situation, a desire or obligation, a consequential past choice, opposition,
and a possible resolution. Names and occupations alone do not make alternatives
different. A morally compromised protagonist is a legitimate option within the
user's requested maturity and genre, not a required source of novelty.

Select one direction and give a short reason tied to the prompt and dramatic
potential. The user's worker, bereaved mother, sibling, ghost hunter, and murderer
examples illustrate causal differences; do not place them in a permanent menu
that every stroller story samples.

**Implementation:** add a compact typed exploration record to the premise output
and persist its selected candidate ID. Keep the selected premise projection
separate from rejected alternatives in downstream context. The latter are
reviewable proposal evidence, never character facts or Story Bible material.
The initial implementation preserves the graph order and selects one route
before the parallel specialists. It therefore tests bounded exploration first;
it does not claim that character development already occurs before selection.
Step 6 adds a restricted opportunity to refine the endpoint after specialist
work. A wholly different route requires the existing pre-approval regeneration
or fork mechanism, not an autonomous search loop.

**Tests:** compare four paired Blueprint runs, using stroller, romance, tragedy,
and ensemble prompts: eight Blueprint workflows, no manuscripts. Check real
causal differences, selection reasons, prompt fidelity, request size, and whether
the selected material survives integration. Test historical artifact readability,
candidate references, replay, and exclusion of rejected facts from canon.

**Advance when:** comparison produces inspectably different viable possibilities
without sacrificing coherence or output reliability. Four examples establish
feasibility, not a population diversity rate.

## Step 3 Make character background change the scene

**Problem:** dossiers describe people, but the prose repeatedly labels them.

**Owners:** character architect develops the material; integrator gives it an
occasion to matter; writer realizes it; critics assess the reader's experience.

Use the existing motivation, stakes, contradictions, secrets, knowledge, voice,
and relationship-history fields to select a small amount of consequential past
experience. Connect that experience to a present habit, sensitivity, obligation,
misjudgment, or capability. Work and financial circumstances can matter, but
occupation must not substitute for personality. Avoid adding a long biography
that the writer is then expected to recite.

Place an opportunity in an appropriate scene: the character notices something
others miss, interprets it through experience, acts, and changes what follows.
Also allow expertise to have limits. Demonstrating a skill and revealing the
personal history behind it are different achievements; review both where the
story promises both. Exposition remains available when it is the effective form.

For Seventh Sense, linguistic knowledge could affect an inference about sound
or notation. Foreign-language expedition records are another possible design
only if the relevant language skills and location history are established.
Neither detail is to be inserted into an already approved story as assumed canon.

**Implementation:** first improve the content of existing character and scene
fields. Keep factual commitments distinct from craft suggestions so a suggested
gesture does not become a mandatory continuity requirement. Trace the selected
detail from dossier to plan to writer request to prose before adding fields.

**Tests:** two paired diagnostics, each covering a connected two-scene passage:
one expertise case and one personal-history case. Generate and approve matched
new Blueprints because the planning changes are part of the experiment. This is
four Blueprint workflows and four two-scene continuations, not four completed
stories. Test that relevant character context survives compilation.

**Advance when:** the reader can identify what the background changes without
relying solely on the narrator's label. Reject gains that become dossier dumps
or repeated demonstrations of the same trait.

## Step 4 Give opposition consequences

**Problem:** protagonists reach predetermined outcomes without having to adapt.

**Owners:** character architect supplies competing commitments; world builder
supplies effective limits; integrator plans the struggle; writer follows it through.

Use existing scene goal, conflict, turning point, outcome, and entry/exit state
to describe a causal sequence: someone tries something, meets a meaningful
response or limitation, and must act in a changed situation. Record what they
want to protect and what an available tactic risks. Opposition can be another
person, an institution, the environment, a supernatural rule, or conflicting
commitments. Give an active opponent a response where appropriate.

Inspect world rules for accidental unlimited solutions. A power should not
automatically turn every defense into fuel unless that asymmetry creates a
different meaningful problem. Costs must affect options or relationships;
descriptions of pain alone are insufficient. Preserve quiet genres and deliberate
inevitability. Refusal, bargaining, concealment, and changed understanding can
constitute struggle; physical resistance is not universal.

**Implementation:** strengthen causal use of current World Rules, Beats, and
Scene Plans. Do not append a fixed obstacle checklist to every scene. Use the
critic's dramatic-progress dimension for the effect, while keeping an approved
outcome distinct from advice that it could be more forcefully realized.

**Tests:** two paired two-scene diagnostics with fresh approved Blueprints, four
Blueprint workflows in total. Use a Chronophage-like case with the same required
self-erasure outcome and a quiet interpersonal case. Compare attempts, responses,
changed options, and momentum. Include true rule breaches and legitimate changes
of knowledge in offline continuity controls.

**Advance when:** difficulty produces consequential choices without relying on
extra length, arbitrary setbacks, or a changed ending to manufacture improvement.

## Step 5 Develop interacting group dynamics

**Problem:** a community reacts as scenery and announced actions lack follow-through.

**Owners:** character architect and world builder establish the social situation;
integrator plans interactions; writer and Bible maintainer carry their consequences.

Within the existing two-to-five significant-character allocation, give the
relevant people different stakes, information, dependencies, and reasons to
trust authority. Decide what evidence might change a stance. Record relationships
needed by the story, including tensions beyond a single protagonist–elder link
where the cast warrants them. A complete relationship graph is unnecessary.

Plan how one person's response changes another's options. Obedience, disbelief,
panic, resistance, and cooperation should arise from circumstances, not a cast
of fixed reaction labels. Follow through on orders, restraint, rescue attempts,
betrayals, and refusals. Uniform compliance can work when the story develops its
causes and costs; a crowd that lacks critical information cannot be assessed as
knowingly accepting a sacrifice.

**Implementation:** use Character, Relationship, Beat, Scene Plan, and existing
Bible relationship/knowledge updates. Plan any new recurring causal participant
before approval. Background crowd members need not all receive dossiers. Preserve
the scoped development rules in [ADR 0015](../adr/0015-scoped-continuity-development.md).
Do not expand the optional two-actor dialogue subgraph into an ensemble engine.

**Tests:** two paired two-scene diagnostics, one Bloom/Boundary-like authority
case and one non-horror group case: four fresh approved Blueprint workflows.
Read an initial reaction and its later consequence together. Check that the
group changes available actions and that updated knowledge/trust reaches the
next scene. Code checks cover valid IDs, temporal scope, and immutable history.

**Checkpoint A:** after accepting this step, run two complete paired stories
against the frozen starting configuration: one horror/community prompt and one
non-horror prompt. Four new stories with fresh approved Blueprints test whether
the preceding gains survive autonomous production. Report completion separately
from literary preference; do not advance through a material regression blindly.

## Step 6 Broaden the endings considered

**Problem:** repeated prompts select the same narrow resolution even when the
prompt permits alternatives.

**Owners:** premise architect proposes endpoints; character/world specialists
make their implications concrete; integrator makes the final pre-approval choice.

Use the exploration record from Step 2 to compare what changes in the world,
what becomes of the protagonist's desire, how relationships change, and what
remains unresolved. Consider materially different causal outcomes, not simply
happy, sad, and ambiguous versions of the same event. Preserve requirements such
as hollow success in the tragedy prompt. Do not reward novelty that breaks setup.

Add one bounded reconsideration **inside the existing integration call** after
character and world work. The integrator may refine the endpoint within the
selected route when the new material supports it. This creates room for a later
insight without repeatedly generating whole alternative stories.

**Implementation:** this requires an explicit contract change. Today integration
must reach the declared ending and cannot rewrite its input artifacts. Define a
small typed finalization result for the premise's arc/ending and directly affected
character arcs, with source version IDs and rationale. Materialize changes as
new immutable artifact versions before assembling the Blueprint; bind the
Blueprint to those final versions and retain the provisional lineage. Update
node outputs, dependency selection, manifests, replay fingerprints, integrity
validation, and versioned readers together. Do not hide a contradictory ending
only inside the scene plans.

Keep this authority narrow: it cannot invent a new cast, alter user requirements,
or replace established world rules. If another route needs those changes, expose
the unresolved choice at the existing Blueprint review and use its bounded
revision/fork path. After approval, the writer earns the chosen ending; it does
not silently choose a new one. If compact finalization cannot fit the current
output/request budget, reduce duplicated output before broadening the contract.

**Tests:** use three repetition-sensitive prompts with two predeclared seeds per
prompt, paired across the last accepted and candidate configurations: 12 Blueprint
workflows. This is a separately labeled exploration experiment, not a change to
formal benchmark seeds. Compare candidate routes and selected resolutions using
the audit's causal categories plus room for newly observed categories. Test that
discarded and provisional endpoints never become approved canon by accident.

**Advance when:** the available choices are meaningfully broader and the selected
endings remain coherent. A small sample may still select the same ending; do not
rerun until diversity appears or mandate different endings across user stories.

## Step 7 Make the ending feel earned

**Problem:** even a different ending can feel flat when its price, choice, or
aftermath has not been developed.

**Owners:** integrator and writer; Blueprint and scene critics assess different stages.

Connect the final decision or defeat to specific earlier attempts, relationships,
and commitments. Establish what a character stands to lose before asking the
reader to feel that loss. Show enough consequence after the decisive event for
the change to become concrete. Avoid relying on an abstract closing explanation
that the character has finally found peace, connection, or authenticity.

The appropriate ending may involve acceptance, resistance, failure, victory,
compromise, or unresolved conflict. Do not require every protagonist to win or
fight physically. Preserve ambiguity when it is authorized; resolve the promises
that this particular story undertakes. A changed image or gesture can carry an
aftermath without a lengthy epilogue.

**Implementation:** improve existing beat setup/payoff links and the final scene
assignment. Reserve enough of the existing story-length allocation for the
consequence. Keep the current thread reducer honest: it must not invent a payoff
just to close a thread. The final scene's critic assesses its local realization
using Step 1's evidence discipline. Blueprint review and whole-story human
reading assess preparation across scenes; a scene-only score cannot certify
the ending's emotional impact.

**Tests:** two paired closing sequences with their relevant earlier setup, one
tragic/accepting and one non-tragic. Freeze the high-level outcome in both arms;
approve newly planned routes that lead to it. Budget four Blueprint workflows
and four two-scene closing continuations. Supply exact compatible prefixes and
Bible states in each arm. A different outcome is not allowed to explain a win
in this particular test.

**Advance when:** blind reading favors the preparation and consequence, rather
than only a novel twist. Record ending impact separately from Step 6's diversity.

## Step 8 Make dialogue change the situation

**Problem:** exchanges repeat the premise or voice a theme without affecting people.

**Owners:** integrator and scene writer in the formal path; dialogue director and
character actors receive equivalent guidance only in the optional path.

Give a relevant exchange competing immediate intentions, unequal knowledge, and
something that changes through speaking or withholding: access, trust, leverage,
commitment, interpretation, or a next action. People need not state their motives
accurately. Subtext should arise from the relationship, not obligatory evasiveness.
Voice can reflect a particular life without reducing someone to professional jargon.

**Implementation:** use existing plans, relationships, and voice fields. Improve
writer/critic instructions first. Keep optional dialogue routing, actor count,
round limits, and stopping behavior unchanged; its existing director evaluates
whether the exchange achieved its dramatic purpose when that path is enabled.

**Tests:** two paired exchanges using identical approved plans and surrounding
context, four diagnostic scene drafts. Include a disagreement and a quiet
conversation. Compare what becomes possible or impossible afterward, repetition,
and voice. Test the optional subgraph offline if its instructions/contracts change.
No additional full story is required at this step.

## Step 9 Give description a purpose

**Problem:** atmosphere can occupy attention that would otherwise reveal a person
or an event, and familiar sensory/metaphorical constructions can become filler.

**Owners:** world builder and premise architect supply useful material; writer
selects what matters; scene critic evaluates the result in context.

Trace repeated imagery back to location sensory details and the voice guide.
Treat location details as available material rather than a checklist to reproduce
on each visit. Prefer details that orient action, reveal a viewpoint, establish
a constraint, or change meaning with the scene. Preserve atmosphere that works.
Keep the existing sensory-detail field; removing sensory writing is not the goal.

Use the attached preference as a compact initial editorial instruction: select
contrastive framing and triplets for their effect, make sensory detail specific
to viewpoint or action, and let meaningful recurrence develop. Evaluate figurative
language for a coherent perceptual/emotional connection, not literal realism.
Support guidance with both effective and ineffective human-reviewed examples.

**Implementation:** replace generic style guidance within existing premise,
world, writer, and critic inputs. No cross-story preference database is needed
for this experiment. Record the exact temporary style instruction with the run.

**Tests:** three paired passages on fixed approved plans, six diagnostic drafts:
an atmospheric opening, an active scene, and a quiet scene. Compare specificity,
clarity, character perception, and atmosphere. Inspect both the source artifacts
and the prose to locate the source of change. Reduced adjective or metaphor
counts are not a success criterion.

## Step 10 Reduce accumulating prose tics

**Problem:** a locally reasonable construction becomes monotonous across scenes.

**Owner:** the application derives observations; writer and critic decide their
literary relevance within existing calls.

Build a compact deterministic observation packet from exact accepted scene
versions and, for criticism, the current candidate. Start with patterns that can
be located reliably: repeated words or phrases, lexical co-occurrences, and
similar scene openings. Include source spans and enough adjacent context to
inspect a claim. A detector may nominate a contrastive construction or triplet,
but should not pretend to identify all semantic repetition accurately.

For example, report that the word “air” occurs in the first sentence of two
earlier scenes, or that taste and ozone occur together in specified sentences.
Those are lexical observations, not proof of a shared descriptive purpose.
The model decides whether the recurrence serves a motif or voice, or adds little.
Changing only the
substance named after “taste” is not necessarily an improvement.

**Implementation:** make this a bounded derived context projection, not Story
Bible canon and not an additional LLM summarizer. Record detector version and
all source artifact IDs/hashes in invocation provenance. Recompute or invalidate
it when a source changes, a run forks, or a scene is replaced. Exclude rejected
drafts from accepted-story statistics; assess the current draft separately.
Keep a fixed small packet budget by replacing duplicate optional context.
Surface observations without automatic rejection or severity thresholds.

**Tests:** offline controls cover exact counts/spans, deliberate motifs, stale
versions, first-scene emptiness, forks, and context limits. Run three paired late
scene diagnostics with the same approved plans and accepted prefixes: six drafts.
Check both unwanted recurrence and damage to deliberate repetition or voice.

**Checkpoint B:** run two complete paired stories with fresh approved Blueprints,
comparing the cumulative Step 10 candidate with the frozen starting configuration.
Four full stories test accumulation and the interaction of all creative changes.
Review background, struggle, relationships, endings, and prose together; a gain
in one dimension does not erase a major loss in another.

## Step 11 Support precise human corrections

**Problem:** the reader cannot conveniently point to a passage and inspect a
controlled proposed revision.

**Owners:** artifact-review UI, API, and a registered bounded revision workflow
that reuses the scene writer and existing review capabilities.

Extend the artifact inspector: select a passage, attach a comment, request a
revision, inspect a diff, and accept or reject the proposed version. Bind the
comment to an immutable source version and exact selection. Retain the original.
This is an optional post-production activity, consistent with the existing
[UI design](../../open_hollywood_bible/ui_ux.md), not a general manuscript editor
or another checkpoint during normal generation.

**Implementation:** start with requests that preserve events, viewpoint, and the
approved outcome. Give the writer the containing scene and relevant canon, not
only an isolated sentence. Persist the proposed scene as a new version and make
changes outside the selection visible. On acceptance, create a coherent new
manuscript/version lineage. Do not replace an accepted scene ID inside an old
Bible whose immutable history records the earlier version.

Reuse dependency invalidation and Bible reduction to construct a consistent
revision branch and revalidate affected downstream dependencies. A request that
changes facts, cast, or plot must take the appropriate wider revision path;
it cannot masquerade as a local prose correction. Persist comments/revision state
with migrations as required and regenerate API types. Every requested operation
has a call budget, cancellation, replay, and a clear terminal result.

**Tests:** UI/API/workflow checks cover stale selections, repeated text, duplicate
requests, accept/reject, restart, immutable originals, and dependent-version
consistency. Use three bounded live requests: a local tic correction, a change
needing context, and a plot-changing request that must be scoped appropriately.
Each may involve several existing review calls; these are three revision jobs,
not three promised model calls. No new full-story campaign is necessary unless
the change also modifies autonomous production.

## Step 12 Remember preferences deliberately

**Problem:** useful feedback does not carry forward, or one correction is wrongly
generalized to every future story.

**Owners:** application persistence and context selection; the human chooses scope.

Offer an explicit “remember this preference” action. Store the feedback, reason,
source passage and accepted revision where available, scope, exceptions, and
version/provenance. Accepting a revision alone does not create a general rule.
Allow passage-only, story-wide, or future-story scope, with relevant genre/voice
conditions where the reader supplies them. Preferences must be inspectable,
editable, disableable, and removable.

Retrieve a small relevant set into the brief/style guidance and writer context.
Current explicit user instructions take precedence over remembered preferences;
resolve ambiguity visibly without silently accumulating contradictory commands.
Historical invocation snapshots remain reproducible. Removing a preference stops
its future retrieval without rewriting past story evidence.

**Implementation:** use a versioned application preference record, not model
fine-tuning or an ever-growing chat transcript. Begin with deterministic scope
matching, not a vector database. Record which exact preferences were applied.
Freeze the preference snapshot for each benchmark and mark personalized tests
separately. New user preferences affect subsequent runs; changing an approved
story's governing guidance requires an explicit revision branch.

**Tests:** two paired diagnostic drafts with memory off/on: one applicable
preference and one exception/control, four drafts in total. Offline tests cover
scope, precedence, removal, version pinning, and no cross-project leakage. UI tests
verify that accepting a rewrite does not silently enable remembering. Assess
generalization through new wording and situations, not only the stored example.

**Advance when:** the application uses and withholds preferences appropriately,
and the reader finds the result helpful. This establishes application memory;
it does not show that model weights learned the user's taste.

## Test schedule and cost planning

The quantities below are a starting diagnostic budget, not statistical power
claims or guaranteed completions. They are additional experimental work to plan
when implementing the guide. No live tests were run to prepare it.

| Stage | Initial live test allocation | Complete new stories |
| --- | --- | ---: |
| 0 | Existing evidence and offline packaging | 0 |
| 1 | 8 frozen review cases × 2 configurations | 0 |
| 2 | 4 prompt pairs, 8 Blueprint workflows | 0 |
| 3 | 2 pairs, 4 Blueprints plus 4 two-scene continuations | 0 |
| 4 | 2 pairs, 4 Blueprints plus 4 two-scene continuations | 0 |
| 5 | 2 pairs, 4 Blueprints plus 4 two-scene continuations | 0 |
| Checkpoint A | 2 complete prompt pairs with fresh Blueprints | 4 |
| 6 | 3 prompts × 2 seeds × 2 configurations, 12 Blueprints | 0 |
| 7 | 2 pairs, 4 Blueprints plus 4 closing continuations | 0 |
| 8 | 2 paired scene drafts on fixed plans | 0 |
| 9 | 3 paired passage/scene drafts on fixed plans | 0 |
| 10 | 3 paired late-scene drafts on fixed plans | 0 |
| Checkpoint B | 2 complete prompt pairs with fresh Blueprints | 4 |
| Core qualification after Step 10 | Frozen 12-prompt Cloud campaign plus 12 direct baselines | 24 |
| 11 | 3 bounded user-requested revision jobs | 0 |
| 12 | 2 paired memory comparisons | 0 |

This reserves **32 full-story attempts**: eight agentic outputs across the two
development checkpoints, then 12 agentic outputs and 12 direct baselines in the
formal campaign. Smaller diagnostics are additional. The listed Blueprint-only
and fragment experiments total 36 Blueprint workflows; the complete agentic
stories require another 20. Reuse an already generated control only when its
exact configuration, inputs, and experimental role match, and record that reuse.
These numbers can be reduced by explicitly narrowing the diagnostic set before
execution, not by removing failed or disappointing outputs afterward.

A Blueprint workflow contains multiple specialist calls. A scene continuation
may include writing, critique, continuity, Bible updates, and permitted repairs
or revisions. “One test” is therefore not “one model call.” Estimate tokens,
calls, latency, and worst-case allowances from observed runs before each batch.
Keep the established per-run and campaign ceilings. Unknown provider monetary
cost remains unknown; it must not be reported as zero or as a passed cost gate.

For narrative planning experiments, create new Blueprints and obtain the normal
approval before drafting. For writer-only comparisons, freeze the approved plan,
canon, prefix, and relevant inputs. A diagnostic continuation must start from a
compatible exact Bible/prefix or an explicitly labeled prepared fixture; never
splice one branch's accepted events into another. Fixture-based fragments are
not evidence of autonomous completion. Execute them through a scoped diagnostic
harness without changing canonical production or its stop conditions.

If a result is mixed, record it as inconclusive and decide on a bounded follow-up
before running it. Do not repeatedly reroll until the candidate wins. Preserve
strong controls throughout: quiet scenes, intentional motifs, earned surrender,
and prompts with required outcomes protect against overcorrection.

## Final assessment of the cumulative changes

Run the core formal campaign after Steps 1–10 and their checkpoints, **before
waiting for the optional feedback UI and preference memory in Steps 11–12**.
Use the frozen 12 prompts, seeds, direct-baseline contract, model/profile,
existing budgets, and exact versioned configuration. Generate fresh pre-production
and obtain the usual Blueprint approvals. Preserve all failed cases in the
technical denominator. Build blind review packets and use the established
whole-story rubric and acceptance criteria without changing old scores.

Evaluate the cumulative candidate against the direct baseline for qualification.
The paired development checkpoints provide the separate comparison with starting
Open Hollywood; historical v33 results alone cannot establish a causal gain over
the current system. Keep technical completion, continuity, human quality,
preference, cost evidence, and review coverage as distinct results. Existing
95% completion and 80% continuity targets, the weighted 3.5 quality target and
2.5 category floor, the declared preference criterion, and cost requirements
remain governed by the product contract and executable campaign configuration.

One complete campaign can screen the candidate. It does not by itself establish
stable diversity or repeatability. If it clears the existing gates, predeclare
the repeatability assessment required for the next promotion decision rather
than automatically reproducing all three historical runs after every step.
Report between-run resolution patterns alongside human judgments; four endings
with different words can still implement the same choice.

After Steps 11–12, assess targeted correction and personalization separately.
If either changes normal first-draft prompts or routing, rerun the relevant
paired checks and qualify that new frozen configuration. Preferences must not
change midway through a campaign.

## Implementation locations and engineering checks

| Area | Existing starting points |
| --- | --- |
| Pre-production instructions and outputs | [Blueprint executor](../../apps/api/open_hollywood_api/services/blueprint_model_executor.py), [node contracts](../../engine/open_hollywood_engine/workflows/contracts.py), [Blueprint graph](../../engine/open_hollywood_engine/workflows/blueprint_graph.py) |
| Artifact content and integrity | [Schemas](../../engine/open_hollywood_engine/artifacts/schemas.py), [Blueprint integrity](../../engine/open_hollywood_engine/artifacts/blueprint_integrity.py), [Story Bible reducer](../../engine/open_hollywood_engine/artifacts/story_bible.py) |
| Writer and critics | [Production executor](../../apps/api/open_hollywood_api/services/production_model_executor.py), [revision acceptance](../../apps/api/open_hollywood_api/services/production_revision_acceptance.py), [production graph](../../engine/open_hollywood_engine/workflows/production_graph.py) |
| Context and derived observations | [Context contracts](../../engine/open_hollywood_engine/context/contracts.py), [compiler](../../engine/open_hollywood_engine/context/compiler.py), role-specific request assembly in the executors |
| Optional dialogue | [Dialogue contracts](../../engine/open_hollywood_engine/workflows/dialogue_contracts.py), [dialogue graph](../../engine/open_hollywood_engine/workflows/dialogue_graph.py) |
| Human corrections | [Artifact inspector](../../apps/web/src/components/ArtifactInspector.tsx), [workspace service](../../apps/api/open_hollywood_api/services/workspace.py), new narrowly scoped review contracts and persistence |
| Evaluation | [Production probes](../../scripts/production_probe.py), [canary review](../../scripts/canary_review.py), [evaluation tests](../../tests/evaluations/), [workflow tests](../../tests/workflows/) |

Use relevant existing schema, context, API, workflow, and evaluation tests at
each implementation step. Add tests for changed boundaries and failure modes,
not assertions that a prompt contains a favored phrase or that a model has
objectively written a good story. Include output validation, old-version
readability, exact lineage, unchanged limits, idempotent replay, cancellation,
and restart where the change touches them. Production prompt changes need
semantic comparisons as well as passing code tests.

Before handing off an implemented change, run the applicable checks from the
[root README](../../README.md). The current commands are:

```text
uv run --extra api ruff check apps/api apps/worker engine scripts tests migrations
uv run --extra api ruff format --check apps/api apps/worker engine scripts tests migrations
uv run --extra api mypy apps/api apps/worker engine scripts tests migrations
uv run --extra api pytest
pnpm format:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Run `pnpm contracts:generate` when API contracts change. For the interactive
review steps, also perform an actual browser exercise of selection, revision,
diff, acceptance, and recovery; add suitable browser regression coverage when
that surface is implemented. Passing mocked UI tests alone does not demonstrate
the complete interaction.

Each completed step should leave a small reviewable change, its exact experiment
manifest, results including failures, and a decision to retain, revise, or revert
the change. Record implementation and evaluation status separately in the
authoritative tracker. A locally promising scene is a reason to continue testing,
not to declare the story-quality problem solved.
