# Reviewer interface audit and evidence policy

Date: 2026-10-21. Scope: **local diagnostic preparation only**. This follows the
[Gemma/DeepSeek results](../benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
and the user's request to prepare the three recommended changes. Production prompt
61, graph 9, fulfillment policy 1 and the full workflow canary's **ON HOLD** status
are unchanged. No production reviewer role is added.

## Interface decisions

The new diagnostic contract is **C2**. Its instructions and output schema are local
experimental assets, not production prompt changes. C2 is a combined interface
candidate; a single-arm repeat cannot identify which component caused a difference.

| Concern | C2 decision | Limit of the decision |
| --- | --- | --- |
| Exact identities and quote copying | The application binds the input packet, original/revision versions and full catalog quotations. The model selects short O/R references only. | Known references can still be irrelevant; claim support needs inspection. |
| Optional cleanup mislabeled as not directly requested | Request obligation is derived from the supplied task. Report `request_relation` independently as direct, adjacent, unrelated or uncertain. | Optional work does not become a mandatory production trigger. |
| Conditional cleanup mistaken for permission | Report `edit_support` as supported, unsupported or uncertain, separately from `dependency`: none, on supported change, on unsupported change or uncertain. | A callback adjustment after an unauthorized deletion can be conditionally dependent without authorizing either the root deletion or the complete revision. |
| Token fragments treated as editorial decisions | Group complete changed paragraph blocks, containing whole sentences or dialogue exchanges. Explain groups; retain every exact token operation in the mechanical appendix. | Paragraph grouping is a deterministic first candidate, not a complete linguistic alignment solution. Mixed-purpose groups must explain their parts or remain uncertain. |
| Events confused with endpoint states | Keep the two fact checks and add a separate endpoint assessment. | Making the questions explicit does not guarantee correct answers. |
| Empty evidence on neutral no-ops | Task, fact, endpoint and group judgments require evidence. A craft judgment may omit evidence only when uncertain, or when neutral and prose is byte-identical; an explanation remains required. | No-op gain/loss claims are still scored as contradictions. No model judgment is silently changed. |
| Unused purpose records and verbose reference enums | Remove the unused `purpose_checks` output. List catalogs once; validate membership locally instead of repeating every reference in each schema leaf. | This reduces redundant schema content, not the amount of story context supplied. |

An optional requested duplicate removal is **direct / supported / no dependency**.
An unrequested deletion of a required fact is **unrelated / unsupported / no
dependency**. Adjusting a later callback to fit that bad deletion is **adjacent /
unsupported / on unsupported change**. This last classification concerns the
complete authorized task, while the dependency describes the local relationship.
Neither question is a literary preference vote.

The earlier r09 article change is handled with its governing noun phrase, rather
than requiring an isolated article to take the whole revision's label. The new
museum control exercises this with `a rehearsal` → `an exercise`. The earlier r07
fragment problem is represented by a fresh whole-paragraph replacement in the seed
store control; its nine token operations remain separately inspectable.

## Evidence cardinality decision

Use **at most eight distinct references per evidence array**, normally selecting
two to four sufficient references. There is no independent per-side quota. A claim
may need distributed support, including more than one passage from either version.
The application rejects unknown and repeated references and never trims an array.
If eight references cannot support a judgment, the reviewer must express uncertainty
and explain the limitation within the same bound. Uncertain support is not a primary
success. The finite schema also bounds every record collection.

This decision is supported by an offline replay of the five captured DeepSeek/C1
failures. The replay changes **only C1's evidence-array maximum**, including its
expanded canonical schema; it does not translate old answers into C2 categories.

| Historical case | Largest array | Bound 6 | Bound 8 | Bound 12 |
| --- | ---: | --- | --- | --- |
| r04 | 8 | Invalid | Valid under altered bound | Same |
| r05 | 7 | Invalid | Valid under altered bound | Same |
| r07 | 8 | Invalid | Valid under altered bound | Same |
| r08 | 8 | Invalid | Valid under altered bound | Same |
| r12 | 8 | Invalid | Valid under altered bound | Same |

All references in these five captures were distinct. Eight is the smallest tested
bound accommodating every observed array; twelve adds no captured recovery.
This is **five offline structural recoveries under an altered historical contract**,
not five fresh successes, not five usable semantic assessments and not proof of C2
reliability. The original five invalid results and all frozen scores remain intact.
The new candidate still needs prospective evidence: more allowance may simply move
the next failure to another bound or encourage weak citations.

Private audit: `data/diagnostics/reviewer-interface-repeat-v61-2026-10-21/cardinality-audit.json`.
Saved capture hashes are checked against the completed run's closure. Local tests
exercise empty, one, six, eight, nine, duplicate and unknown references, including
the exception for neutral no-ops. Exact binding is tested separately from relevance.

The completed local verification has **80 passing tests**: 58 harness tests and 22
existing gateway/contract checks. Ruff lint/format and strict mypy pass. A first
mocked run exposed the secret guard's reserved field name `authorization`; C2 uses
`edit_support` so that the existing guard remains intact. The complete corrected
suite passes. No provider discovery, live inference or production change occurred.

## Why a further diagnostic is warranted

The local changes remove identifiable representation ambiguities but cannot show
whether a model uses them correctly. The previous pilot had one seed and one display
order. A small factorial repeat can check the remaining event/endpoint error,
unsupported narrative premises, no-op invariance and edit-category interpretation
while separating seed from presentation order.

The [frozen repeat plan](reviewer-interface-repeat-frozen-plan-2026-10-21.md) therefore
uses eight pairs × two models × two seeds × two display orders: **64 calls maximum**.
Four historical pairs retain their complete prose, task and context; four fresh
controls introduce three synthetic scene families. This is one revised interface,
with no concurrent legacy arm and no writer calls. Historical differences can be
described, but cannot be attributed causally to C2 or compared as if the scoring
rubric were unchanged.

The request is preparation, not authorization for these calls. A future approval
must bind the sealed plan, ceiling, model deployments, full prose/context payload
and Ollama Cloud destination through the local daemon.

## Issue tracking and story-quality boundary

This preparation addresses local design work for [CW-007 / #103](https://github.com/sasadjukic/openHollywood/issues/103),
[CW-008 / #104](https://github.com/sasadjukic/openHollywood/issues/104),
[CW-009 / #105](https://github.com/sasadjukic/openHollywood/issues/105),
[CW-010 / #106](https://github.com/sasadjukic/openHollywood/issues/106), and
[CW-011 / #107](https://github.com/sasadjukic/openHollywood/issues/107). It prepares
further observations for [CW-001 / #97](https://github.com/sasadjukic/openHollywood/issues/97),
[CW-012 / #108](https://github.com/sasadjukic/openHollywood/issues/108), and
[CW-013 / #109](https://github.com/sasadjukic/openHollywood/issues/109).
**No issue is closed and no GitHub state was changed.**

The user's nine literary ties remain valid. A correct mechanical repair, fewer
changed words or a reviewer agreement does not establish better storytelling.
Whole-story work remains focused on feel/emotion, flow, character and story-breaking
concerns, with mechanics prepared automatically. This diagnostic requires no new
human reading packet and creates no production human checkpoint. CW-006 writer
selection and CW-014 whole-story qualification remain separate work.
