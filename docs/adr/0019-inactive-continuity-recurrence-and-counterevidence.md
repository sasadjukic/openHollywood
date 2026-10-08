# ADR 0019 Inactive continuity recurrence and counterevidence

- Status: Accepted
- Date: 2026-10-08
- Qualification: Offline checks pass; four live probes assessed; semantic recovery not established

## Problem

The two remaining v34 probe findings are described in
[ADR 0018](0018-current-continuity-rechecks-and-compact-coverage.md).
Matching a historical allegation preserves its ID and assigns `still_blocking`.
The changed-evidence guard previously checked only `newly_exposed` findings,
allowing an inactive historical allegation to bypass that boundary.

The OH-V01-010 reviewer requested a deletion explanation already present beside
its cited passage. Whether the complete scene is consistent with the Blueprint's
statement about the current system flagging the back-door still requires a
contextual judgment. A nearby explanation is evidence to consider, not an
automatic exemption from a real contradiction.

## Decision

Use production prompt v35 / graph v9 on temporary branch
`codex/continuity-stabilization-v35`.

Determine eligibility for unchanged contradiction evidence from the latest
report's active model-finding IDs, independently of historical identity or
disposition. A non-world contradiction absent from that active set must pass
the existing changed-excerpt test. If every cited excerpt already occurs in the
previous candidate, reject the review response through the existing bounded
structural repair path. Do not silently discard the finding or declare the
manuscript correct. A repeated invalid response fails at the same limit.

Preserve historical IDs and canonical recheck dispositions for audit compatibility.
Active original blockers may retain unchanged evidence. Reintroduced assertions
with changed evidence remain eligible to block. World Rules, forbidden shortcuts,
requirement coverage, and initial-review behavior retain their existing gates.

Replace continuity guidance with compact instructions to read adjacent sentences
and the whole draft, assess the strongest counterevidence in the existing
`conflict_explanation`, and explain why it fails to reconcile a claimed conflict.
Repeating an investigation does not itself deny its earlier result. Do not ask
for an explanation already present. Genuine incompatible assertions about the
same subject and applicable time remain blockers. No lexical rule or automatic
semantic classifier decides that these particular stories are valid.

Structural repair policy version 9 explains that only active latest-report
rechecks can retain unchanged evidence. Model/profile settings, writer and critic
instructions, graph routing, adjudication, budgets, timeouts, revision counts,
and exact Blueprint approval are unchanged. No schema migration, dependency,
API contract regeneration, or new model call is added to production.

## Offline evidence

The new regression file contains 14 cases covering inactive recurrence, changed
assertions, active blockers, stale recheck keys, independent finding routes, and
persisted workflow repair/terminal failure. The workflow cases verify that the
invalid review is repaired without an additional writer call and is not recorded
as an established manuscript defect.

Repository verification passed: 643 Python tests, 11 frontend tests, Ruff lint
and formatting, strict mypy, frontend formatting/lint/type checks, and the
production build. These checks establish implementation behavior; they do not
qualify live model judgments or full-story completion.

Read-only reconstruction matches both saved v34 request hashes and preserves
the frozen database's SHA-256:
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

| Frozen input | v34 message characters | v35 message characters | System characters v34 to v35 |
| --- | ---: | ---: | --- |
| OH-V01-002 scene 2 revision 2 | 39,997 | 39,958 | 9,437 to 9,398 |
| OH-V01-010 scene 2 initial draft | 40,495 | 40,479 | 7,171 to 7,155 |

Both prepared contradiction controls also have shorter matched requests. These
are character measurements on these inputs, not model token measurements or a
universal size guarantee.

The actual 002 probe's five cited excerpts all differ from its previous draft.
Consequently, the repaired guard applies but does not reject that captured
finding. The change closes a demonstrated general bypass; it does not by itself
resolve 002's semantic mistake. Changed text is not proof of a new incompatible
assertion. Live evaluation must assess the revised guidance separately.

Local reconstruction code, baseline source, request packets, and hashes are under
`data/diagnostics/v35-continuity-stabilization-2026-10-08/`. The completed comparison
uses `offline-verified/` and `offline-results.json`; earlier partial offline
packets document prompt-size and replay investigations and are not live results.

## Bounded live checks — 2026-10-08

The experiment has four isolated continuity probes, each permitting at
most one structural retry, for eight calls total:

1. Exact frozen OH-V01-002 inputs, inspecting repeated-verification judgments.
2. The same case with a labeled diagnostic assertion that the handwriting never
   matched Elena's script; that new contradiction should remain blocking.
3. Exact frozen OH-V01-010 inputs, inspecting adjacent counterevidence and timing.
4. The same case with a labeled diagnostic assertion that Elias never created a
   back-door in any code version; that new contradiction should remain blocking.

Controls receive separate fixture IDs and content hashes. They are not approved
story changes and are never written to canonical artifacts. The original
database is read-only. A validated JSON response is not a semantic pass, and
these probes are not full-story completions or a repeatability assessment.

At the frozen 24,000 input / 8,000 output token limit per call, eight calls have
a published-rate estimate of at most USD 0.05248 using the October 8
[Gemma cloud rates](https://ollama.com/library/gemma4:31b-cloud), assuming all input
is uncached. This estimate is separate from actual charges, which remain unknown.
Historical test costs and the accepted cost gate are unchanged.

Automatic approval review initially rejected the launch because explicit
permission to send these private story inputs and controls to Ollama Cloud was
required. No inference occurred in that rejected launch. The user then explicitly
approved the four probes and their payload, destination, call limit, and estimate.

All four probes validated on their first attempt: four calls, no structural
retries, 39,384 input tokens and 4,467 output tokens. Ollama 0.35.1 routed the
existing `gemma4:31b-cloud` alias to remote `gemma4:31b`, with alias digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Every live request hash matched its prepared v35 packet. The frozen database
hash remained unchanged. Requests, manifests, validated findings, response
hashes, usage, and runtime metadata are in the diagnostic directory's `live/`.

| Probe | Input / output tokens | Published-rate estimate, USD | Assessment |
| --- | ---: | ---: | --- |
| 002 frozen draft | 9,632 / 1,021 | 0.00175688 | Repeated verification still blocks; target judgment not corrected. |
| 002 contradiction control | 9,672 / 1,311 | 0.00187848 | Injected denial is correctly blocked; repeated-verification objection also remains. |
| 010 frozen draft | 10,016 / 1,096 | 0.00184064 | Still blocks, but now requests reconciliation with the current-system flag rather than the already-present deletion explanation. |
| 010 contradiction control | 10,064 / 1,039 | 0.00182456 | Injected denial is blocked; the repair explanation also confuses a physical override with a code back-door. |

Total published-rate estimate: **USD 0.00730056**, assuming uncached input.
Actual charges remain unknown. The runner's inherited numeric-zero cost fields
are unknown-cost placeholders; the separate estimate fields are calculated
from recorded token usage and the dated rates above. These estimates do not
qualify the formal cost gate or alter historical cost evidence.

Both positive controls retained their injected contradictions as blockers.
This is narrow evidence that the new instructions did not simply suppress every
finding, not proof of sound reasoning across cases. In particular, 010's control
correctly cites the injected assertion but its recommended repair mixes the
digital and physical meanings of back-door. The saved validated reports omit
model-only certification fields, so this assessment uses the retained findings,
repair assessments and recommendations; it does not reconstruct unrecorded
explanations.

For 002, the selected canonical assertion says verification happened in scene 1;
it does not prohibit doing it again. Scene 2's approved assignment explicitly
sets verification of a private flourish as its turning point. The historical
report still supplies a recommendation to remove that sequence. Its summary
returns in both probes despite an empty active recheck list. Historical advice
anchoring the model is a supported investigation target, not an established
causal explanation from this experiment.

For 010, the selected Blueprint secret includes the current system flagging the
code back-door as a threat. The revised recommendation acknowledges a distinction
between deleted redundancies and that flag. A deletion explanation alone does
not settle this timing/identity question; neither the scene nor its blocker is
declared definitively correct here.

## Disposition and next boundary

Retain this branch as a tested implementation candidate. The deterministic
inactive-recurrence fix is covered, but semantic recovery and repeatability
remain unqualified. Do not expand to a full-story run on this evidence or reroll
the same probe until it passes. No writer or adjudicator call ran.

The next focused investigation is the projection of inactive historical review
advice into current model context: distinguish prior allegations from current
authority while preserving identity, audit history, current hard requirements,
and exact canonical assertions. Compare a separate versioned candidate against
these frozen results and positive controls before considering a bounded
full-story check. Do not change runtime limits or bypass real contradictions.

Product Step 19 remains IN PROGRESS. Step 20 and the story-quality implementation
sequence have not started. No sealed campaign results or acceptance thresholds
change with this implementation.
