# Approved SE/BS/ER daemon-baseline amendment

Date: 2026-10-28. **User-approved version-only amendment; combined ceiling 36 calls.**

The user approved execution of the [frozen SE/BS/ER plan](reviewer-source-sufficiency-frozen-plan-2026-10-27.md)
with one stated change: Ollama is now **0.40.12**. Metadata-only discovery confirms
that version and unchanged selected DeepSeek tag, digest, capabilities, model
information and thinking configuration. The three metadata requests made no
inference calls and sent no story prose.

| Item | Original freeze | Amended execution |
| --- | --- | --- |
| Expected daemon | 0.40.11 | **0.40.12** |
| Private identity | `reviewer-source-sufficiency-v61-2026-10-27` | `reviewer-source-sufficiency-amendment-v61-2026-10-28` |
| Original calls used | 0 | **0** |
| Combined call ceiling | 36 | **36**, twelve per form |
| Retries/replacements | 0 | **0** |

All **56 experimental input files**, including all **36 prepared requests**, are
byte-identical. This includes cases, full prose/context, claims/components, gold,
schema, source-scope audits, registries, witnesses, schedule, budget, scoring,
stops, runtime snapshot and casebook. Generated wire requests are unchanged.
The twelve historical SE/ER wire controls remain exact. All forms still request
high thinking. No prompt, source, scoring or allowance change is introduced.

The original seal and all original files remain intact. The amendment adds current
metadata and a separate execution identity, updates the expected version and
approval binding, and adjusts the local mismatch fixture to remain a mismatch.
It requires the amended plan hash, original parent hash and approved 0.40.12 in
the approval record. All later version observations must match 0.40.12; unexpected
drift remains terminal. Existing terminal preservation, no-retry rules, delivery
sentinel and clean-boundary continuation rules remain in effect.

Original plan SHA-256:
`f584207f9f58be93cd4ae6341095dc6b35d31ff75c7aafcc38b2b1ca7a75a708`.

Selected DeepSeek digest:
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.

The amended local checks include every experimental-file equality check, approval
parent/version rejection, and the full mocked schedule, source/scoring, terminal,
budget, delivery and historical regression suites. All **419 offline tests**, Ruff lint/format and strict mypy pass. Results are
sealed with the amended bundle before inference. The initial verification caught
stale 0.40.11 expectations in the version-test fixtures; those fixtures were
corrected to 0.40.12 and the full suite rerun successfully. This document records the user's current
authorization; it does not ask for a second approval of the same version change.

Execution will use the frozen full unpublished prose/context/claims/components
payload through the local Ollama daemon to Ollama Cloud. Production **prompt 61 /
graph 9 / fulfillment policy 1** and Blueprint approval are unchanged. The canary
remains **ON HOLD**. A later results report will distinguish observations under
0.40.12 from historical 0.40.11 results; any difference cannot be attributed to
daemon version alone because the run does not randomize provider versions.
