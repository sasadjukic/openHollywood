# Step 19 Local/Cloud prompt-v24 canary diagnostics — 2026-09-05

## Evidence and comparison limits

This report compares the completed campaigns in
`data/benchmarks/v0.1/v24-canary-2026-09-05/` and
`data/benchmarks/v0.1/v23-canary-2026-09-04/`, using their `report.json`,
`plan.json`, and read-only `campaign.db` records. The corpus, selected cases,
approved Blueprint inputs, model-profile snapshots, and seeds were preserved.
Production changed from graph v3/prompt v23 to graph v4/prompt v24; the
Blueprint and dialogue contracts stayed unchanged.

Each campaign selected six Local and four Cloud cases. Local OH-V01-006 is the
known permanent Blueprint failure and never entered production. The production
denominator is therefore nine. These are single runs on fixed examples, not a
statistical estimate of general reliability. Provider model aliases and model
generation can vary, and multiple contract changes were introduced together.
The evidence identifies deterministic application defects and observed model
behavior; it cannot assign every outcome to one prompt change without a
controlled replay or ablation.

Local OH-V01-002's v23 pause coincided with Windows correcting a two-hour clock
error after Ubuntu-to-Windows dual boot. The operator confirmed this host
behavior. It remains an environmental event, not evidence of an Open Hollywood
active-time defect; v25 makes no runtime clock change.

## Outcomes

| Measure | v23 | v24 |
| --- | ---: | ---: |
| Production-runnable completions | 6/9 | 4/9 |
| Local completions, excluding permanent Blueprint failure | 2/5 | 0/5 |
| Cloud completions | 4/4 | 4/4 |
| Local continuity revision-limit failures | 2 | 4 |
| Local terminal Story Bible validation failures | 0 | 1 |
| Environmental production pauses | 1 | 0 |
| Successful production model attempts | 179/182 | 144/149 |
| Successful continuity attempts | 49/51 | 40/41 |
| Successful Local continuity attempts | 26/26 | 18/19 |

The fall from six to four completed stories is entirely Local: OH-V01-004 and
OH-V01-005 completed in v23 and failed in v24. Cloud preserved all four
completions. Local OH-V01-001 and OH-V01-003 failed both runs, though OH-V01-003
reached a different failure boundary in v24. OH-V01-002's v23 clock pause is
not comparable to its v24 semantic failure as an application regression.

| Local case | v23 terminal point | v24 terminal point | Accepted scenes, v23 → v24 |
| --- | --- | --- | ---: |
| OH-V01-001 | Scene 2, revision 2, continuity | Scene 1, revision 2, continuity | 1 → 0 |
| OH-V01-002 | Scene 3 Bible update, environmental pause | Scene 1, revision 2, continuity | 2 → 0 |
| OH-V01-003 | Scene 1, revision 2, continuity | Scene 1, revision 1, Bible validation | 0 → 0 |
| OH-V01-004 | Completed | Scene 3, revision 2, continuity | 4 → 2 |
| OH-V01-005 | Completed | Scene 2, revision 2, continuity | 4 → 1 |
| OH-V01-006 | Blueprint failure | Same Blueprint failure | No production |

Fewer total model calls in v24 do not by themselves show improved efficiency:
Local runs stopped earlier. Cloud provides a useful completed-output comparison.

## Segments that improved

| Cloud production-only measure | v23 | v24 |
| --- | ---: | ---: |
| Model attempts | 92 | 87 |
| Successful model attempts | 90 | 87 |
| Scene revisions | 2 | 1 |
| Provider input tokens | 856,556 | 705,184 |
| Sum of recorded invocation latencies | 437.4 s | 338.4 s |

Cloud input tokens fell 17.7% and recorded invocation latency fell 22.6% while
all four stories completed. Across the same 87 successful operation/scene/
revision stages, writer input fell 20.4% and critic input fell 19.0%; continuity
input fell 3.0% and Bible input fell 0.7%. This is consistent with the intended
benefit of the smaller writer/critic Blueprint view. Latency remains an
observation from these runs, not a guaranteed speedup. The execution report's
totals also include reused Blueprint work; the table isolates production calls.

| Completed Cloud story | v23 words | v24 words |
| --- | ---: | ---: |
| OH-V01-001 | 3,514 | 3,257 |
| OH-V01-002 | 3,889 | 3,525 |
| OH-V01-003 | 4,231 | 4,122 |
| OH-V01-004 | 4,263 | 4,525 |

All completed v24 stories stayed within the advisory 2,500–5,000-word range.
The redundant v22 non-world certificate failures did not return. All Cloud
structured calls succeeded on their first attempt in v24.

Revision restraint improved. Recomputing both campaigns with v24's actual
case-folded word/punctuation `SequenceMatcher(..., autojunk=False)` metric gives
Local revision medians of 0.7015 in v23 and 0.7465 in v24. Five of twelve v23
transitions were below 0.35; none of the ten persisted v24 transitions were.
The v24 minimum was 0.3951. One proposed Local rewrite scored 0.303, was rejected,
and recovered on the bounded retry at 0.3951. The guard was not a terminal
failure. These figures use one comparable metric and should not be mixed with
the character-oriented similarity figures in earlier exploratory diagnostics.

Cloud OH-V01-004's sole v24 revision scored 0.9968: the writer explicitly tied
Maya's electronic negotiation to an already mentioned three-second jammer
window. The next continuity report cleared the `isolation_protocol` finding.
This demonstrates precise editing, although whether that fictional loophole
respects the rule is still a semantic judgment.

Cloud OH-V01-001 avoided its v23 final-scene revision. Part of the difference is
the generated Bible: v23 attributed the stroller's creation/placement to Vane,
while v24 described a ritualistic lure without that exclusive attribution.
The approved final Scene Plan explicitly asks the entity to reset its lure.
The saved revision therefore cannot be attributed solely to better checking.

## Why Local regressed

### Keyword promotion turned craft advice into hard critique failures

The v24 normalizer promoted any critique mentioning topics such as `POV` or
`next scene`, without requiring an actual assignment violation. Two persisted
findings demonstrate the error:

- OH-V01-003 scene 1 says the scene is correct and explicitly calls its advice
  “a note for the next scene, not a failure of the current one.” It nevertheless
  became BLOCKING/REVISE. Initial continuity had no blockers, so this critique
  alone scheduled another draft.
- OH-V01-004 scene 2 calls the effect correct and recommends minor polish to
  the POV character's reaction. It too became BLOCKING/REVISE.

All 49 v23 critiques passed. In v24, 37 of 40 passed and three requested
revision; two of those three contain the false promotions above. All 22 Cloud
critiques still passed with no issues, so Cloud did not exercise the stricter
critic behavior. Raw failed/provider responses are not retained; the original
model verdict is unavailable, but the deterministic promotion defect and the
meaning of the persisted feedback are directly observable.

Critic requirement timing also differed from continuity. OH-V01-001 scene 1
received a blocking missing-stroller critique based on a story-wide benchmark
requirement. The critic saw full-story obligations while continuity deferred
those obligations until the ending. A scene-specific omission must be justified
against what is due in that scene, not merely against eventual story content.

These unnecessary revisions increase exposure to model drift. They do not
prove that removing the critique alone would make each complete story succeed;
that requires a fresh controlled run. The continuity-only similarity guard also
does not apply when critique itself requires revision.

### Stable finding IDs did not guarantee stable meanings

The continuity supervisor still treated plausible developments, thematic
preferences, and absent details as contradictions. Canonical source handles
and exact draft excerpts established provenance, but did not establish that
the assertions were incompatible.

- OH-V01-001's location finding complained that abandoned shoes lacked enough
  narrative weight, despite revised prose presenting them as echoes of lives
  interrupted. A location name cannot establish that thematic requirement.
- OH-V01-002 attached a date contradiction to the canonical character name
  `Elara Vance`, then retained a stale 2034 allegation against revised 2024
  evidence. A later temporal-bleed complaint cited a relationship label even
  though the requested light/ink interaction was already on the page.
- OH-V01-004 blocked Elias regaining rhetorical footing even though the exact
  Scene Plan expressly directs him to do so. Subsequent rechecks shifted the
  concern toward insufficiently palpable Clara agency while preserving the
  earlier finding identity and repair direction.
- OH-V01-005 called Elara's scoff inconsistent with the previous ending, which
  itself says she scoffed. Later the concern became an unestablished photograph,
  while the retained repair still addressed the scoff. The plan permits focus
  on a debatable object or document in the room.

The v24 recurrence key primarily identified a canonical source or rule, so
different allegations against one source could collapse into one finding.
Rechecks inherited the old summary and recommended repair while accepting a
new freeform assessment, and prior blockers were exempted from the qualitative
downgrade. Cumulative history improved traceability but could also preserve an
unsupported judgment. The repeated revision-limit message is the final symptom;
the underlying problem is inconsistent semantic adjudication.

### OH-V01-003 reached the Bible boundary and exposed a separate schema gap

Its revised scene cleared critique and continuity, including recovery from a
rejected newly-exposed finding whose evidence was not new to that revision.
The next specialist failed twice with `a resolved story thread requires scene
and resolution`. No scene was accepted because the Bible update did not commit.

The canonical schema requires both a resolution explanation and a resolution
scene, but v24's model schema did not express that status-dependent requirement.
The application only filled the scene when a non-null scene was already
supplied. Retained diagnostics do not reveal which field was absent, so the
repair must cover both halves without inventing explanatory story content.

The approved OH-V01-003 Blueprint also contains a possible naming ambiguity:
character prose mentions the Hawthorne building while a registered location is
the Hallways of Blackwood Tower. This deserves an advisory source-level
observation; the text alone does not prove the names refer to the same place.

## Production graph v5 / prompt contract v25

The implementation under review addresses the observed application defects
while preserving scoped context, repair ledgers, the bounded similarity guard,
and the one mandatory Blueprint checkpoint:

- Replace keyword critique escalation with an explicit assignment-violation
  array. Each item selects an assigned anchor, quotes exact current-draft
  evidence, explains the mismatch, and recommends a repair. The application
  validates shape, anchor existence, and excerpt provenance before producing
  a blocking issue. It does not infer a violation from an ordinary craft note.
- Give critic and continuity the same due-now requirement timing, including
  final-scene assessment of story-wide requirements.
- Present smaller canonical assertions with scope information rather than
  whole source objects as one claim. Provide continuity the current assignment
  and instruct it to consider the plan and accepted ending as counterevidence.
  Keep names in nonselectable identity context and retain atomic character
  location/knowledge assertions. A name or relationship label cannot establish
  a date or a physical mechanism. Explicit non-conflict dispositions replace
  keyword-based downgrading: neither additive repair wording nor a mention of
  emotional resonance can release a concrete contradiction by itself.
- Permit explicit `invalidated` and `advisory` recheck outcomes with current
  evidence and assessment. Reassess qualitative residuals through those explicit
  decisions rather than parsing craft keywords from a still-blocking assessment; allow
  obsolete repair instructions to be corrected. Recurrence identity includes
  the normalized original allegation as well as the source; it deliberately
  does not claim to recognize arbitrary semantic paraphrases.
  Actually deliver the previously unused recheck instructions. Persist all
  recheck decisions with exact evidence handles, redacted assessment hashes,
  and final blocking outcomes so released findings can also be audited.
- Use status-dependent open/resolved Story Bible thread output branches.
  Derive resolution-scene lineage in the application, require actual nonempty
  explanation text, and return field-specific safe retry instructions.
- Persist nonblocking, source-linked observations for unregistered building
  names in approved character descriptions. Do not rename immutable approved
  content or automatically declare an alias conflict.
- Fail with `critique_revision_limit_reached` when hard critique issues remain
  at the cap, even if continuity clears. Soft quality revisions retain their
  bounded acceptance behavior. The former ability to accept a blocking
  critique at the cap was a latent inconsistency, not exercised by v24's
  accepted scenes. Graph v5 records the additional hard-issue state.

These are schema, evidence-provenance, routing, and prompt improvements. Exact
quotes and an explanation are not a proof of contradiction; semantic
correctness still depends on the model and must be evaluated. A required
explanation may also increase structured-output pressure on the Local model.
The regression fixtures and offline tests cover known bad decisions and real
blocking cases, but cannot establish the v25 production completion rate.

## Verification and next evidence

Repository verification passes: Ruff lint and formatting over 141 Python files,
strict mypy over 141 files, all 341 pytest tests, frontend formatting/lint/type
checks, all 11 Vitest tests, and the production build. `git diff --check` also
passes. The tests use offline fixtures; no provider calls or v25 canary have
been started as part of this implementation. Canonical artifact schemas and
SQLite tables are unchanged; graph v5 versions the new checkpoint field and
hard-critique acceptance behavior. A fresh canary should
reuse the usual six Local/four Cloud cases and fixed approved inputs while
recording graph v5/prompt v25. In addition to completions, compare false critique
promotions, invalidated/advisory rechecks, exact recurrence behavior, Bible
repair recovery, input sizes, and revision preservation. Targeted ablations on
the formerly successful Local OH-V01-004/OH-V01-005 cases would help distinguish
individual prompt effects from generation variance.

Both databases contain zero final human evaluations. Completed reports still
leave `mandatory_requirements_present` and `target_format_valid` unset. Technical
completion must therefore remain separate from blind rubric scores, preference,
and final semantic quality. The full formal benchmark and blind review remain
pending, and Step 19 remains **IN PROGRESS**.
