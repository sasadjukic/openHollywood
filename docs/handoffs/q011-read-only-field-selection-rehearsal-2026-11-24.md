# Selecting the two Elias position claims in a saved review

The same draft and final instant produced two distinct evidence questions. In *The Pristine Lure*, Q010 asks whether Elias **is entering** the threshold. Q011 asks whether the scene fulfills the plan that he **stands at** the threshold. The read-only intake preserved the whole sentence and its other obligation in both cases. The two controls show why neither the word “threshold” nor the name of the endpoint field is sufficient to select the position question. [Four saved previews](../../data/diagnostics/q011-selection-rehearsal-2026-11-24/selections.json)

## Four selections

Each row was explicitly selected from the earlier six-review audit. **B** is the default factual brief. **E** adds a question asking what draft observation establishes, rules out or leaves open the particular position, and when that observation applies. **Hold** leaves the whole interpretation for a reader. [Earlier scope decisions](q011-transfer-regressions-and-ordinary-scope-2026-11-23.md)

| Review and field | Route | What the operator preview retained |
| --- | --- | --- |
| Elias Q010 · achieved state | E | The critic says Elias has moved past the circle of shoes **and** “is entering the threshold of the monolith.” The complete draft is the authority for both actions. The added question asks about entering at the cut. |
| Elias Q011 · current endpoint comparison | E | The critic says the achieved state matches both “drawn to the entrance” and “stands at the threshold.” The plan supplies both assignments. The draft supplies evidence of fulfillment. The added question asks about standing at the cut. |
| Elias Q012 · next-scene comparison | B | The critic says the draft stops at the threshold and covers neither entry into the building nor Julian Vane’s disembodied voice. The brief checks narrative coverage against the complete draft and current plan. The linked Blueprint supplies the scene-two voice reservation. |
| Elara Q016 · current endpoint comparison | Hold | The critic reads Elara’s attempt to mimic the script and her inner conflict as implying an obsession with proving the card is fake. The complete interpretation remains available for human review. Selecting it creates zero active units and no factual brief. |

Q012 was chosen as the factual control because it uses the same threshold, draft and critic as both E fields. Its subject is what the draft narrates. Q016 uses the same native field pointer as Q011 in a different review. The handwriting action is observable, while the inference about Elara’s motive is an integral part of the selected statement.

## Source and selection checks

The rehearsal reopened the original v61 critic captures and checked the saved whole fields against the raw critic finals and the sealed scope decisions. The three Elias fields use critique v2 and draft v1 of *The Pristine Lure*. Elara’s field uses critique v3 and draft v1 of *The Impossible Card*. The saved previews record the invocation, exact critique, draft, scene plan and Blueprint version IDs for each selection. The scene-two reservation was also checked against the corresponding scene in the linked Blueprint. [Original selection protocol](../../data/diagnostics/q011-position-scope-audit-2026-11-23/protocol.json)

Each factual selection passed through the existing intake and work-brief preview with the complete documents and original messages. Each produced one pending unit. The Q010 and Q011 units have distinct work hashes and their target spans reproduce the original verbs. On return to Q010 after the controls, the same preview and work hash were reproduced. All four remained unassessed. This rehearsal measures selection and source binding. It adds no observation about assessor accuracy or story quality. [Replay script](../../scripts/q011_transfer/selection_rehearsal.py) · [Regression tests](../../tests/evaluations/test_q011_selection_rehearsal.py)

## Verification

All **126 focused tests passed**, including seven new rehearsal regressions. They rejected an exchanged position predicate, a substituted whole field, the wrong review and a changed draft version. The offline replay reproduced all four previews and left the source files byte-identical. The two asynchronous saved-review intake cases passed with Windows local loopback enabled and provider traffic blocked. The existing claim-scope and brief tests emitted 22 Pydantic serialization warnings. Repository-wide Ruff lint, formatting and strict mypy passed across 410 Python files. [124 local cases](../../data/diagnostics/q011-selection-rehearsal-2026-11-24/selection-and-intake.xml) · [Two asynchronous cases](../../data/diagnostics/q011-selection-rehearsal-2026-11-24/async-intake.xml)

Replay from the repository root with `python -m scripts.q011_transfer.selection_rehearsal` in the project environment. The command reads the private archive and prints the four selections.

## Next step

Keep B as the default. Screen up to six previously unscreened saved ordinary reviews from other scene families locally, prioritizing v61. Admit a whole field only if it makes a factual claim about a person’s or object’s position relative to a landmark at an identifiable instant and the exact draft, plan and review are available. Record each reviewed version and the reason for admission or exclusion. Incidental location language in a craft judgment does not qualify.

If an independent family qualifies, freeze the verbatim field, predicate, instant, source versions, and separate judgment and evidence criteria before viewing assessor output or proposing a paired B/E run. If none qualifies, record the coverage gap. Both ordinary E examples still come from one Elias review. Live inference remains paused and the full workflow canary stays on hold.
