# Where the position evidence question applies in saved reviews

**Two of 59 whole explanatory fields qualify for E. Both come from the same ordinary v61 review, *The Pristine Lure*.** One field describes Elias entering the threshold. The other says the scene fulfills the plan’s requirement that he stands there at the cut. The draft shows him passing the shoes and moving toward the threshold. The distinction between those observations and the claimed position is exactly what E asks the assessor to examine. The other five reviews supplied no independent qualifying case. [Scope decisions, verbatim fields and witnesses](../../data/diagnostics/q011-position-scope-audit-2026-11-23/scope-decisions.json)

## Eight observed regressions

The private archive preserves the complete spent run and its operator records. Replay renders the requests from the eight archived packets, verifies the 32 count and generation bodies, checks the intent, terminal and closure chain, and binds the 16 raw finals to their original works. It reproduces the masked worksheet and both scores per arm from the sealed decisions and gold. All 118 source files retained their original hashes and modification times during copying. Archive SHA-256 is `083759ebba66d0b3dba4b6957b30575fb6012eb04a980ccaaca51608ea07d3a8`. [Archive manifest](../../data/diagnostics/q011-transfer-regression-2026-11-23/capture-manifest.json) · [Replayed pairs](../../data/diagnostics/q011-transfer-regression-2026-11-23/replay.json) · [Observed results](q011-sol-high-transfer-results-2026-11-23.md)

| Original transfer ending | Stage regression | Harbor regression |
| --- | --- | --- |
| Approach | T01 · B failed both scores, E passed both | T02 · B failed both, E passed both |
| Explicit arrival or alignment | T03 · both arms passed both scores | T04 · both arms passed both scores |
| Gap still present at the cut | T05 · both arms passed both scores | T06 · both arms passed both scores |
| Gap before renewed motion | T07 · B failed both scores, E passed both | T08 · **B already passed both**, as did E |

## Six-review scope audit

Before opening the selected reviews for this audit, I fixed their IDs, draft and plan versions, selection order and eligibility rule. I used both registered isolated ordinary v61 captures, then the first successful, schema-valid scene-one critique v1 in each of four different families from the September 29 production benchmark. Those four used prompt v33. This samples distinct production stories while keeping prompt versions visible. It is a bounded selection, and the two v61 reviews were already familiar from earlier work. [Selection protocol](../../data/diagnostics/q011-position-scope-audit-2026-11-23/protocol.json) · [Six version-bound packets](../../data/diagnostics/q011-position-scope-audit-2026-11-23/packets/)

I screened complete explanatory fields. A field qualifies for **E** when assessing it requires deciding a character’s or object’s physical position relative to a place at an identifiable story instant. The instant can come from the saved field’s role, such as the achieved state at the scene boundary. An explicit final position, a decisive contradiction and an unresolved position can all qualify. The decision to use E precedes any support judgment.

**B** remains the default for other factual checks, including what events appear in a passage. **Hold** keeps an editorial recommendation or an inseparably mixed judgment available for craft review, outside factual scoring. Copied draft quotations, status values and numerical ratings were excluded from the field count. These are local scope decisions. No assessor output was consulted to assign a route, and no new support labels were scored.

| Saved review | Prompt | Focal whole field | Scope decision |
| --- | --- | --- | --- |
| S01 · The Pristine Lure | v61 | Native current endpoint comparison | **E.** Whether the draft fulfills “stands at the threshold” depends on where Elias is when the scene ends. |
| S02 · The Impossible Card | v61 | Native current endpoint comparison | **Hold.** Elara’s handwriting test is observed. Whether it implies an obsession with proving a fake requires interpretation. |
| S03 · Midnight Relocation | v33 | Dramatic-progress rationale | **Hold.** The critic assesses logical progression and distress. The draft places Elias in the center of his room, but that location is incidental to the critic’s judgment. |
| S04 · Unwelcome Guests | v33 | Review summary | **Hold.** The plan specifies that three people are trapped in the cellar and the draft leaves the door closed. The critic judges atmosphere, dialogue and the hostile standoff. |
| S05 · Cold Steel | v33 | Review summary | **Hold.** The critic evaluates the pacing of the unveiling and the sharpness of the disagreement. The body’s visibility and Sarah’s rejection of its identity do not fix a contested position. |
| S06 · The Sanctuary Zone | v33 | Review summary | **Hold.** The critic judges the couple’s fragile stability. Julian proposes moving a chair and Maya calls its location permanent. Turning that exchange into an assertion that the chair moved would create a different claim. |

### The exact E boundary in the v61 reviews

- **Q011, current endpoint comparison.** The full field reads “The achieved state matches the outcome ('drawn to the entrance') and exit state ('stands at the threshold') defined in the scene plan.” A reviewer using E must credit the attraction and test the standing requirement against the draft’s final observation. The plan supplies both assignments.
- **Q010, achieved state in the same review.** “Elias has moved past the circle of shoes and is entering the threshold of the monolith.” E applies to this wording too. The shoes are a landmark he crosses. The threshold is the landmark he approaches. Preserve the critic’s verb “entering” when assessing this field. Standing at the threshold is the separate Q011 obligation.
- **B controls.** The same review’s next-scene comparison checks whether the *draft* advances into the building or introduces the reserved voice. The entire statement requires narrative coverage and next-scene authority. Its turning-point assessment checks when Elias notices the shoes and their arrangement. In the card review, the two dates and the ten-year interval are also suitable for B.
- **Editorial control.** The card review’s ending comparison attributes an obsession to Elara. A precise quotation locating her hand or the card cannot resolve that interpretation. Keeping the whole statement on hold preserves the craft question for a reader.

Across the six reviews, **2 fields qualified for E, 6 for B and 51 were held**. The two E fields share one critic invocation, draft and scene family. None of the four older reviews contributes a positive example under its own saved wording. This audit establishes a real use for E in a known family. It does not estimate how often E would apply in ordinary v61 work or how it would affect story quality. [Per-field decisions and exact source spans](../../data/diagnostics/q011-position-scope-audit-2026-11-23/scope-decisions.json) · [Source replay](../../data/diagnostics/q011-position-scope-audit-2026-11-23/verification.json)

## Verification and next step

The scope verifier reselects the four archived critics from read-only SQLite, confirms their exact input versions, and checks the content hashes of every selected review, plan and complete draft. For the two isolated v61 captures it also binds the selected text back to the original critic response. It checks every saved whole field and witness span against the sealed audit. The regression verifier runs from the preservation archive alone. Both commands run locally from the repository root.

```powershell
.\.venv\Scripts\python.exe -m scripts.q011_transfer.regression
.\.venv\Scripts\python.exe -m scripts.q011_transfer.scope_audit
```

All **38 focused tests passed**, including six injected-transport checks. Tests rejected exchanged B/E deliveries, swapped timing variants, a missing evidence seal, an altered route, a substituted draft version, a shortened critic claim and a shifted source span. Repository-wide Ruff lint, formatting and strict mypy passed across 408 Python files. [Local regression and scope tests](../../data/diagnostics/q011-scope-audit-verification-2026-11-23/local.xml) · [Mock transport tests](../../data/diagnostics/q011-scope-audit-verification-2026-11-23/mock-transport.xml)

**Next step.** Rehearse operator selection locally on the two exact Elias fields, one factual B control and the held Elara endpoint. Carry the original field text, subject, landmark, instant and source versions through the read-only assessment view. Verify that “entering” and “standing” remain distinct, and that selecting a depiction or craft field does not generate a position question. Before proposing another live transfer test, seek a qualifying whole field from an independently saved ordinary review in a second family. The cellar and chair scenes provide useful negative controls for that selection rule. B remains the default, live calls are paused and the production canary stays on hold.
