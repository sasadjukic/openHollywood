# Open Hollywood endings audit — October 5, 2026

**Finding: the stories show substantial repetition in particular resolutions and
in the language of closure. The narrower claim that most endings present a
choice between personal survival and saving the world is not supported.** This
audit establishes patterns in the available texts; it does not assign an
objective score to their emotional effect or prove what caused the repetition.

The [complete catalog](endings-audit-catalog-2026-10-05.md) records every inspected
ending. The [coding ledger](endings-audit-ledger-2026-10-05.json) includes source
locations, case IDs, content hashes, summaries, closing excerpts, and literal
phrase flags. The local extracted manuscripts linked from the catalog are
readable copies; the original evidence was not edited.

## Coverage and method

| Evidence group | Open Hollywood texts | Direct-model baseline texts |
| --- | ---: | ---: |
| September 12–13 manual sample | 22 | — |
| September 29 formal campaign | 11 | 12 |
| October 2 repeat 1 | 12 | 12 |
| October 2 repeat 2 | 12 | 12 |
| October 2 repeat 3 | 10 | 12 |
| Recovered July/August formal evidence | 20 | 48 |
| **Primary archive examined** | **87** | **96** |
| Additional August 19 Local diagnostic version, kept separate | 1 | — |

There are **184 distinct text hashes**, comprising 183 primary texts and one
additional diagnostic generation. The latter reused the August Local priest /
criminal case and workflow IDs with different prose and a different production
prompt. It is not an independent premise or another formal campaign success.

The recent campaigns supply 45 completed Open Hollywood texts and 48 baselines.
All 48 baselines are included, including the three without a completed Open
Hollywood counterpart. Failures have no completed ending and are excluded from
ending denominators, not silently treated as successes. This is not a new
benchmark preference or acceptance assessment.

The historical archive is incomplete. The [August 9 production report](../benchmark_reports/step-19-autonomous-production-round-2026-08-09.md)
records 26 completed agentic stories, but its JSON report retained only 20.
Six Local completions, prompts 007–012, could not be recovered as those original
generations from the available database artifacts. A later canary version of 009
is not a substitute. Eleven baseline texts absent from that JSON report were
recovered from the immutable pre-production approval database, bringing the
historical baseline total to 48. July 29 has a plan but no completed report in
the inspected archive; no outcome is inferred from its plan. Consequently this
is all recoverable evidence within the defined scope, not proof of coverage of
every story ever generated.

Canaries, engineering batches, aborted drafts, intermediate scene revisions, and
other diagnostic runs are outside the primary scope. The August 19 exception
was initially discovered in a directory named `formal-2026-08-19`; its actual
[diagnostic status](../benchmark_reports/step-19-local-v7-regression-2026-08-19.md)
is preserved here. Historical Cloud, Hybrid, and Local counts are respectively
5, 11, and 4; they are not pooled into a current-profile claim.

The reading unit was the closing sequence, not just the last sentence: typically
the final 450–640 words for the manual/recent Open Hollywood texts, 330–370 for
recent baselines, and 260–300 for historical texts, with earlier action consulted
where needed to resolve a classification. Existing fuller readings of the named
manual stories also informed their summaries. Outcome and resolution labels are
interpretations by one analyst, the assistant, supported by the prose; they are
not independently validated human ratings. Labels summarize a dominant ending
and do not exhaust everything occurring in that story.

All 162 benchmark/diagnostic text hashes were checked against their stored
`content_sha256`; all 22 manual manuscript files matched their evidence
manifests. All formal plans inspected use the same frozen corpus hash. Repeated
prompts and seeds are deliberate dependencies: the 45 recent stories represent
12 prompts, not 45 independent creative tests. Provider seed enforcement and
remote weights are not independently pinned.

## Repetition within the recent Open Hollywood campaigns

These counts cover September 29 plus all three October 2 campaigns. Denominators
are completed Open Hollywood versions of the indicated prompt. “Same pattern”
means the specified causal or relational resolution, not identical prose.

| Prompt | Recurring resolution | Observed | What the prompt actually constrains |
| --- | --- | ---: | --- |
| 001: immaculate stroller | A bereaved parent is absorbed into the building; the stroller resets to recruit another victim. | 4/4 | Requires the stroller's significance and the building's history; does not require parental absorption or a reset trap. |
| 002: future birthday card | Reject prestigious advancement, erase the lonely future self, and reclaim a less controlled life. | 3/3 | Requires a causal explanation and consequential choice; does not prescribe career versus intimacy or self-erasure. |
| 003: moving apartment | Emotional acknowledgment or connection stabilizes the architecture. Two versions merge apartments; two accept grief. | 4/4 | Requires rules and an explanation; does not require therapeutic architecture. |
| 004: priest and criminal | The protected woman rejects their self-serving protection and asserts autonomy; the two men lose their moral authority. | 4/4 | Requires changed relationships and conflicting motives; does not require this exact reversal. |
| 005: father's body | New knowledge unites estranged siblings, who leave the morgue in solidarity. The identity explanations vary. | 4/4 | Requires different knowledge and an emotionally credible truth; reunion is not mandatory. |
| 006: incompatible romance | Loving separation respects supposedly irreconcilable needs for stability and change. | 4/4 | Invites an unconventional, honest choice; does not require breaking up. |
| 007: unreliable narrator | Prosopagnosia explains the supposed intruder/stranger as a loved partner. Three end in connection despite impairment; repeat 3 emphasizes isolation. | 4/4 | Requires a psychological cause; does not specify face blindness or a partner misidentified as an intruder. |
| 008: memory currency | Paying for a loved woman's health destroys the protagonist's capacity to love her. | 3/4 | Requires personal economic consequences. Repeat 1 instead sells grief for comfort after her death. |
| 009: success-as-tragedy | An architect achieves professional success and discovers his partner is irretrievably gone. | 4/4 | Explicitly requires success destroying what matters; architecture, romantic abandonment, and this staging are additional choices. |
| 010: constrained suspense | A lethal smart home traps its occupants; improvised manual intervention disables it and permits survival. | 3/3 | Requires one location/night, ordinary danger, no weapons or supernatural explanation; does not require a smart-home trap. |
| 011: quiet literary change | Estrangement gives way to shared quiet and physical closeness. Siblings, partners, and mother/son vary. | 4/4 | Explicitly requires quiet, earned change without villain, death, or twist; the repeated gestures and silence framing are more specific. |
| 012: five concealed accounts | Reconstructing the event binds the five through collective culpability. Two end in self-incrimination; one in a mutual-hostage pact. | 3/3 | Requires one coherent reconstruction; does not require those legal or relational consequences. |

This is a narrower and better-supported diagnosis than “all endings are alike.”
The endings differ across genres and prompts, yet individual prompts repeatedly
select a very small range of realizations. There are also meaningful internal
differences: the apartment mechanism, the corpse's identity, and the emotional
outcome of the face-blindness story should not be flattened into identical plots.

## Is “help yourself or help the world” the dominant ending?

No, under an explicit conservative coding rule. Count a **costly rescue** when
the resolution trades the protagonist's life, enduring bodily/personal capacity,
memory, freedom, or power to protect someone else. This is broader than a literal
binary choice, because it includes coerced bargains and a third-way solution.
Do not count ordinary risk, a breakup, lost prestige, regret, or being consumed
by an enemy as the same thing.

**Six of the 22 manual stories** fit that broader description:

| Story | Price and beneficiary |
| --- | --- |
| Neon Echoes | Personal memories lost to release one trapped consciousness. |
| Pigeon Express | Elias dies protecting Mara and the seeds that preserve the possibility of biological resistance. |
| The Enchanted Academy | Elara loses chronomancy while destroying the imposed magical order. This rejects a prescribed binary. |
| The Chronophage | Lara erases herself to free humanity. The original user premise already specified self-erasure as the price. |
| The Unblinking Bloom | Elara loses autonomy to restore the village's water; a coerced bargain ending in imprisonment. |
| The Bone Labyrinth | Elara becomes a permanent seal to prevent the dormant entity's awakening. |

Five have a collective beneficiary or purpose; one helps an individual. This
does not mean five literal “save yourself or save the world” scenes. The recent
45-story Open Hollywood formal set has **three clear costly rescues**, all
individual-beneficiary versions of the memory-currency prompt, and **zero clear
collective-rescue versions** under this rule. The stroller stories are traps,
not successful altruistic bargains. This coding was applied to the 67 core Open
Hollywood texts; no sacrifice-rate claim is made for the historical or baseline
appendices.

There are important boundary cases. The Seamstress saves others, then burns her
work to protect herself; that is not equivalent to sacrificing her life for
them. The Alchemist's Latitude abandons a wished-for restored status while
preserving the crew. These are consequential relinquishments, but expanding the
definition to include every abandoned aspiration would blur the user's question.

## A broader repeated emotional movement

The manual sample more often invites this comparison: **the protagonist stops
trying to control, perfect, preserve, or recover something; the ending reframes
the resulting loss as authenticity, connection, peace, or freedom.** Examples
include Alyssa, The Museum of Intense Experiences, The Alchemist's Latitude,
One Bad Year, Perfect Silence, Lyra, The Glitch in the Grid, and The Silence of
the Seventh Sense. The concrete outcomes vary; the repeated valuation of them
helps explain why they may feel related.

Three especially revealing last-movement comparisons are:

- Perfect Silence: Arthur is “finally at peace in the ruins of his own design.”
- Lyra: Lucien loses his companion and feels “for the first time, truly alive.”
- The Chronophage: Lara disappears and “in that total oblivion, she was finally free.”

These are three different plot outcomes presented through a similar concluding
revaluation. The recurrence is evidence; whether any one is moving is a separate
judgment. Nor is every loss redeemed: Bloom ends in conscious imprisonment,
Ossuary in consumption, and Root Ritual in forced destruction.

Literal phrasing was also checked mechanically in each text's **last 250
whitespace-delimited words**, case-insensitively. Each cell counts texts with at
least one whole phrase/word match, not total occurrences. These flags overlap.

| Closing-language marker | Manual OH (22) | Recent formal OH (45) | Recent direct baselines (48) |
| --- | ---: | ---: | ---: |
| `silence` | 10 | 30 | 23 |
| `no longer` | 14 | 21 | 20 |
| `for the first time` | 8 | 12 | 16 |

These ordinary expressions are not defects by themselves. Their frequency,
combined with the recurring contrast between the old self and the newly
authentic/free self, supports a finding about repeated presentation. The
baseline frequencies also prevent assigning this tendency solely to the agentic
workflow. No automatic lexical ban follows from these counts.

## Baselines and counterexamples

The recent baseline romances divide **2/4 separations and 2/4 continuing
relationships with separate homes/distance**, versus 4/4 separations in Open
Hollywood. All four recent Open Hollywood unreliable-narrator mysteries choose
prosopagnosia; the four baselines instead use isolation/dissociation, concealed
murder, suppressed culpability, or avoidance of a loved person's decline.
These demonstrate available alternatives in the sampled outputs, not a general
creativity score or a controlled attribution of cause.

Other patterns cross both systems. All four recent baseline family-body stories
also move toward sibling connection. The baseline tragedy prompt also repeatedly
destroys intimacy through achievement, as the prompt partly demands. Historical
texts show many of these same families; they do not establish that a recent
production-prompt change introduced them.

The manual sample contains real departures: Unreleased exposes wrongdoing;
Space Detective chooses disclosure despite threatened war; The Butter Incident
turns a disaster into unexpected praise; Root Ritual gives Mara active,
unsuccessful resistance. The audit does not support describing every protagonist
as acquiescent or every ending as a sacrifice.

## What this supports discussing next

Repetition is established; lack of emotional impact is not thereby proved.
One plausible contributor is that numerous endings supply an explicit
interpretation of the protagonist's experience, sometimes immediately declaring
a loss liberating. Another is the previously inspected weakness of the struggle
that earns the outcome. A third is reduced surprise across repeated premises.
These explanations can coexist, and this audit does not measure their relative
importance.

The useful next reading is the causal path into selected endings: what the
character tried to preserve, what actions genuinely threatened it, what changed
their choice, and what particular aftermath lets the reader feel the cost.
Compare a successful and an unsuccessful example of the same ending type before
deciding that the type itself needs replacing. More varied outcomes alone would
not ensure more affecting stories.

No runtime, prompt contract, graph, benchmark grade, or implementation-tracker
status was changed. This audit is discussion evidence, not an approved solution
sequence. Candidate solutions from the earlier conversation remain in the
[discussion notes](../handoffs/story-quality-discussion-notes-2026-10-05.md).
