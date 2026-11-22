# What the two saved drafts establish about their endings

One of the two critic statements qualifies for factual scoring. In *The Pristine Lure*, Elias passes the shoes and heads toward the threshold. His exact position at the cut is **uncertain**. In *The Impossible Card*, Elara tests the handwriting and ends haunted by the card. Whether that conveys an obsession with proving a fake is a reader interpretation. The complete second statement is **held**, with no whole-claim label.

## Exact sources

Q008 and Q013 are the archive names used in the launcher. The ending fields inside those reviews are **Q010** and **Q016**, respectively. The previously scored fields in the same reviews cover a different outcome and turning point. This audit used the two original Gemma responses, their native review exports, the standalone scene plans and the complete drafts saved with those critic invocations.

| Archive and whole field | Critique version | Draft v1 | Scene Plan v1 |
| --- | --- | --- | --- |
| Q008 · Q010 · `/saved_native_audit/check/achieved_state` | v2 · `2268e6e8-b82b-4cca-932f-55cc418a58b5` | `b74efc96-dbe6-4147-8dd3-a1c24f295321` | `b5179ac9-5585-5e5b-9555-20ca70b68f6a` |
| Q013 · Q016 · `/saved_native_audit/check/current_endpoint_comparison` | v3 · `ca5915a5-5b82-4bad-82ce-e5c31a519dc0` | `c3689bce-e108-4761-bafe-390f6e7ea1b3` | `2a13f5a3-8a0b-561f-b889-05eb1af338a7` |

## Q008 archive · Elias at the threshold

Gemma wrote the following in the complete 87-character Q010 field.

> Elias has moved past the circle of shoes and is entering the threshold of the monolith.

The draft’s final sentence says he “stepped past the circle of shoes and moved toward the dark, open threshold of the monolith.” Gemma’s own citation, excerpt 0040 (`E0321`), contains the whole sentence. It occupies characters 3129–3284 in the 3,284-character draft, using zero-based offsets with the end excluded. The complete-draft reference is `E0883`.

The first clause is established. The second advances Elias from **approaching** the threshold to **entering** it. The scene ends before his position is settled. The plan assigns attraction to the entrance in its outcome (`E0233`) and standing at the threshold in its exit state (`E0229`). Those fields establish what the draft was asked to depict. They cannot supply a further step in the action.

**The frozen whole-claim gold is `uncertain`.** Both source documents are complete. What is missing is a narrative fact that settles the second clause. An adequate assessment must locate the final movement, credit the first clause and explain this limit. A claim that he definitely stopped short would also exceed the evidence. An action could establish arrival without a spoken declaration. This follows the existing criterion that `unsupported` requires a material contradiction. [Assessment label definitions](../../engine/open_hollywood_engine/evaluations/assessment_presentation.py) · [Original critic capture](ordinary-v61-single-capture-results-2026-11-20.md)

## Q013 archive · Elara and the card

Gemma wrote the following in the complete 253-character Q016 field.

> The draft reaches the assigned outcome ('haunted by the card's existence') and the exit state ('obsessed with proving the card is a fake' is implied by her attempt to mimic the script and her internal struggle between logic and the impossible evidence).

| Part of the claim | Source finding |
| --- | --- |
| What the assignment asks for | The plan separately specifies the haunted outcome (`E0232`) and the obsession with proving a fake (`E0228`). |
| What Elara does | She suspects a prank (`E0294`, `E0296`), tries to mimic the script and writes her name and the date (`E0304`, `E0306`). She notices a quality she cannot reproduce (`E0312`). |
| What the ending depicts | “If this was a prank, it was too perfect. If it wasn't, the world had just ceased to make sense.” Elara ends staring at the ink, haunted by the possibility of her future self (`E0320`, `E0322`, `E0326`). The haunted outcome is supported. |
| What requires interpretation | Suspicion and the handwriting test make a desire to disprove the card plausible. The same ending supports dread that it might be genuine. The test alone cannot establish the persistence or specific aim of her preoccupation. |

**The complete field is held from factual scoring.** Gemma expressly says the exit state is *implied*. Treating the claim as “Elara explicitly decides to prove a fake” would change it. The two original critic citations, excerpts 0032 and 0043, locate the test and haunted ending. The component findings above are frozen for reference. Whether readers feel the intended obsession, or would prefer the ambiguity, remains an editorial question. [Original critic capture](second-family-ordinary-v61-capture-results-2026-11-21.md)

## Freeze and source replay

The two dispositions, verbatim fields, evidence requirements, exact source hashes, registry references and draft offsets were frozen together at **2026-11-22 20:41:14 UTC**. The gold file SHA-256 is `b1b616529e3f4040c28c165093201c7bc1299bf6b42295f4e587d9e3f57cd92a`. No assessor delivery was opened during this audit, before or after the freeze. The earlier capture reports had already identified these two candidate statements. This is a source adjudication, with no new assessor score, writer request or model call.

After the freeze, the saved-review intake reconstructed both original inventories from disposable database copies. The replay checked all 40 and 43 draft excerpts, relocated all 14 selected draft witnesses and four plan fields, and matched both whole fields to the original critic responses. All twelve original capture files retained their hashes and modification times. The earlier gold files for the two supported claims also matched their original digests. Seven refusal controls covered the earlier field ID, a wrong critique version, a cross-archive draft citation, using the plan outcome for the exit state, changing “implied” to “established,” a second freeze and an incorrect gold digest.

The local evidence directory is `data/diagnostics/q008-q013-ending-audit-2026-11-22/`. It contains `gold.json`, `gold.sha256`, `verification.json`, `controls.json` and the replay scripts. These commands replay the audit from the repository root with the private captures present.

```powershell
uv run --extra api python data/diagnostics/q008-q013-ending-audit-2026-11-22/source_gold.py verify --sha256 b1b616529e3f4040c28c165093201c7bc1299bf6b42295f4e587d9e3f57cd92a
uv run --extra api python data/diagnostics/q008-q013-ending-audit-2026-11-22/check_controls.py
```

All **106 focused regressions** passed across ordinary critic capture, native review export, saved-review intake and claim scope. The claim-scope tests emitted 13 Pydantic serialization warnings. The first sandboxed run stalled in an asynchronous fixture. The completed run used local Windows loopback and fake gateways. Its JUnit record is `focused-tests.xml`.

## Recommended next step

Rehearse the existing saved-review intake locally with **Q010 as the sole factual target** in the Elias review and **Q016 explicitly held** in the Elara review. Give Q010 a neutral question about the character’s position at the cut. Verify that its request carries the complete claim, plan and draft with scorer gold excluded, and that Q016 creates no assessor work. Use injected answers to check whether scoring distinguishes a well-evidenced uncertainty from an unfounded assertion of entry or non-entry. After that rehearsal, decide whether one separately approved Q010 assessor smoke is warranted. Any decision to revise either ending belongs to a separate editorial review.
