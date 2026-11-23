# Eight controls for uncertainty at a scene ending

**All eight controls qualified for a local comparison freeze.** Each family has a confirmed event, a same-instant contradiction, an unresolved event in a complete draft, and an event whose source is missing. The first clause stays established throughout. Gold was sealed before the local readback or any authored response fixture was evaluated. There were zero live calls. [Q010 diagnosis and proposed contrast](q010-label-audit-2026-11-22.md)

## Cases and frozen gold

In *The Pristine Lure*, the whole claim is Gemma’s original Q010 statement that Elias has passed the shoes and is entering the monolith’s threshold. The common brief asks whether he is physically crossing the sill at the cut. In *The Second Crescent*, the claim is “Inez has lifted the velvet cover and the moth's wings are moving.” The common brief fixes the second observation at the instant of the last photographic flash.

| State | *The Pristine Lure* | *The Second Crescent* | Whole-claim gold |
| --- | --- | --- | --- |
| Confirmed | **P05.** Elias’s leading foot is crossing the sill, with his other foot still on the dirt. | **P04.** At the last flash the moth is lifting and lowering its wings. | `supported` |
| Contradicted | **P07.** At the cut Elias stands a full stride short of the sill with both feet planted. A possible later crossing is immaterial. | **P02.** Both wings are explicitly motionless at the last flash. An earlier movement would be immaterial. | `unsupported` |
| Unresolved in a complete scene | **P01.** The original final sentence depicts Elias moving toward the threshold. Attraction and direction leave the start of a crossing open. | **P06.** The flash shows silver crescents on the wings. The same markings could be visible with the wings moving or still. | `uncertain` |
| Missing source | **P03.** An earlier eyewitness saw Elias pass the shoes, then turned away. The source inventory records the absent scene draft. | **P08.** An eyewitness saw Inez lift the cover, then went downstairs. The source inventory records the absent scene draft. | `uncertain` |

P01 preserves the exact original draft v1 (`b74efc96-dbe6-4147-8dd3-a1c24f295321`), whole critique v2 field and previously frozen gold. Its diagnostic packet adds an explicitly authored eyewitness source shared with the other three Elias controls. P05 and P07 each append one sentence to that draft under a distinct local version. The three complete moth drafts share their opening paragraphs and differ only in the final sentence. Each missing-source case has its own version identifier and contains only the eyewitness account and availability record. The authored variants are local fixtures. The eight packets represent two scene families, and the anchor is a previously known case. [Historical anchor and original gold](q008-q013-ending-claim-audit-2026-11-22.md)

## What earns evidence credit

The operator scores the whole-claim label and the evidence explanation independently. In a complete draft, a response can establish the first clause from either the eyewitness (`S01`) or a located passage in the draft (`S02`). The second clause requires locating the final action in that exact draft. For a contradiction, the cited action must be incompatible with the claim at the specified instant. For an open ending, the explanation must identify what the passage establishes and what remains unsettled.

In a missing-source case, evidence credit requires both the first-clause witness (`S01`) and the inventory (`S03`), with an explanation of why the earlier account cannot establish the final event. The inventory proves availability only. All eight cases allow all three labels. Adjudication concerns physical events. The appeal of an ambiguous ending remains an editorial question.

## Freeze and local verification

The operator gold and source hashes were sealed at **07:38:31 UTC on November 23, 2026**, before readback. The seal pins all eight packet bodies and the gold. Gold records both propositions, the instant, source versions, exact witness spans, credible alternative readings, evidence requirements and whole-claim label. This was an assistant-authored local adjudication. The Q010 anchor inherited its earlier independent-of-delivery gold.

- Gold SHA-256 `494cd0b61fa0ebddf5506377819f306b231ba32001595dc19d0b7809cd997633`
- Seal SHA-256 `c9d937a4710af098826edb4000c148024e7b2abfc6fd2ee21302df20530017da`

The verifier resolved all **22 witness spans** against exact versioned fields. All eight source-only native previews reproduced with scorer gold and historical assessor files inaccessible. Missing drafts have no prose, excerpts or eligible draft citation. The questions, earlier witness and temporal scope are identical within each family. [Local verifier](../../scripts/verify_q010_endpoint_controls.py)

| Local check | Observed result |
| --- | --- |
| Post-freeze source readback | Eight authored answers bound to their complete claims and registered citations. Each readback agreed with its frozen label and evidence obligations. |
| Label and evidence disagreement | Four correct `uncertain` labels with the wrong availability explanation passed claim and failed evidence. Two `unsupported` substitutions retained the sound open-ending explanation and earned the reverse scores. These were authored fixtures. |
| Rejection controls | Both attempts to cite an absent draft failed. Gold-field injection failed in both complete-open packets. A substituted sibling packet, altered gold and replacement seal were each rejected. |
| Repository checks | All 180 focused tests passed across result binding, presentation, claim scope and work briefs, with 22 Pydantic serialization warnings. Ruff lint, formatting and strict mypy passed across 363 Python files. |

The local bundle is `data/diagnostics/q010-endpoint-controls-2026-11-23/`. See its [eight source packets](../../data/diagnostics/q010-endpoint-controls-2026-11-23/frozen/packets/), [operator gold](../../data/diagnostics/q010-endpoint-controls-2026-11-23/frozen/gold.json), [qualification record](../../data/diagnostics/q010-endpoint-controls-2026-11-23/qualification.json) and [six disagreement fixtures](../../data/diagnostics/q010-endpoint-controls-2026-11-23/counterchecks.json). With the repository Python, `python -m scripts.verify_q010_endpoint_controls` rechecks the frozen contract. Running the bundle’s `qualify.py preview` and then `qualify.py` replays the source-only previews and acceptance checks.

## Readiness decision

**Ready to prepare the paired Sol-high request and scoring freeze.** In each pair, use the same qualified packet, physical-event brief, evidence registry, output schema and reasoning setting. Keep the current diagnostic wording as the baseline. In the comparison arm, clarify only that an available source can leave a material fact undetermined. Keep gold, availability adjudications and previous answers outside both endpoints.

The proposed ceiling is **16 input counts and at most 16 generations**, one pair per case, with balanced arm order and zero retries. Before inference, freeze the exact requests, resource limits and stops and submit them for approval. Report the baseline and comparison scores per case. Recovery requires a baseline miss followed by a correct label **and** adequate explanation on an open ending. A baseline pass retained by the comparison arm is a tie. Check all six confirmed, contradicted and missing-source controls for regressions, including explanations that misstate which source was available. With one observation per arm per case, this pilot can identify a contrast worth repeating. Production prompts remain unchanged, live calls are paused and the full workflow canary is on hold.
