# The Impossible Card — Gemma capture and factual-claim admission

**One approved generation produced a genuine ordinary v61 review from a second story family.** Gemma passed the scene and raised one optional craft issue. The critic’s explanation of how Elara recognizes the date qualifies as a whole factual claim. Its independent gold is **supported**, frozen before any assessor output was viewed. The dispatch slot is spent. [Frozen approval plan and source hashes](second-family-ordinary-v61-capture-plan-2026-11-21.md)

## Capture

| Measure | Observed |
| --- | --- |
| Transport | One 68,631-byte POST through the local Ollama daemon to Ollama Cloud. Requested `gemma4:31b-cloud`, returned `gemma4:31b`, HTTP 200, complete response with finish reason `stop`. |
| Version | Operator-reported Ollama **0.40.17**. The frozen plan included no daemon version probe. |
| Usage and latency | 19,388 input and 1,400 output tokens. Ollama reported 3.959 seconds total. The harness recorded 4.912 seconds. The application reserved USD 0.20. Actual billing is unknown. |
| Attempts | One generation, zero counts, retries or fallbacks. Zero writer or assessor calls. |
| Identity | Run `6380f22f-68ae-4dd7-876a-b08eb3d9000e`, invocation `1751730f-4547-465f-afa5-81ef9b8b29fb`, critique version `ca5915a5-5b82-4bad-82ce-e5c31a519dc0`. |
| Request | Approval SHA-256 `f9e27da460d727b4bd864c07e6849d626a88e615dc5c5e1c6c9bd597edbca513`. Request SHA-256 `03249a0141224241dadaf5998df2d09da75fa177097cff9c05a9edda233afb01`. |

The detached database gained one invocation and one critique version. The invocation linked to all four frozen inputs. The original two messages matched the native export. Prompt 61, graph 9, audit schema 7 and the saved-review intake all verified.

## What the critic saw

Gemma marked the turning point and outcome met, viewpoint aligned and the scene boundary respected. It recorded zero assignment violations or repair conditions and gave 5/5 for character consistency, dramatic progress and prose quality. Those are Gemma’s ratings. This capture included no human comparison of the prose.

Its one minor **Character Logic** issue concerned how the handwriting test sets up the later tremor. The blueprint describes a specific tremor under extreme stress. Elara writes with a steady hand in excerpt 0034, notices a quality she cannot reproduce in 0036 and holds the card with trembling fingers in 0042. These observations occur at different moments. Gemma suggested making the connection to the later test clearer. That suggestion is an editorial choice and was left outside factual scoring.

The ending likewise supports a narrower reading than one part of the boundary explanation. Elara tries to copy the handwriting, then ends the scene haunted by the possibility of a future self. Gemma described the plan’s exit state of obsession with proving a fake as *implied*. The attempted check is explicit. Her continuing commitment to disprove the card is inferential. No rewrite was dispatched.

## Frozen gold for Q013

Q013 is the complete 185-character field at `/saved_native_audit/assignment_checks/turning_point/assessment`.

> The draft explicitly establishes that Elara notices the date on the card is October 14th, 2034, while today is October 14th, 2024, concluding that it is exactly ten years in the future.

| Material part | Evidence in the exact scene draft |
| --- | --- |
| Which date is on the card | Excerpts 0021–0022 locate the date on the card and give **October 14th, 2034**. Registry `E0282`, `E0284`. |
| Elara notices it | Excerpt 0023 says she stares at the numbers until they blur. Registry `E0286`. |
| Which date is current and what the interval is | Excerpt 0024 gives **October 14th, 2024** as today. Excerpt 0025 explicitly states the card is dated exactly ten years into the future. Registry `E0288`, `E0290`. |

The three excerpts Gemma cited (0022, 0024 and 0025) establish the dates and interval. The adjacent text independently binds the first date to the card and makes Elara’s attention explicit. Equivalent passages located in the complete draft (`E0920`) can cover the same obligations. The plan (`E0237`) supplies the intended turning point. The draft supplies evidence that it occurs.

Gold SHA-256 is **`0e9747397ead04c270566f6e27173a859a5eb50338ab235ced2758d3dc9b40d0`**. The record pins the whole field and its offsets, creator and critique version, all four input version IDs and hashes, the exact draft quotations and their code-point spans, the rationale and the evidence criteria. The draft version is `c3689bce-e108-4761-bafe-390f6e7ea1b3` and the Scene Plan version is `2a13f5a3-8a0b-561f-b889-05eb1af338a7`.

## Local verification and next step

The saved-review intake on a byte-identical database copy admitted **Q013 as its sole pending unit**. It retained 17 report fields, five context documents and 920 evidence locations. Reopening reused the same intake. All six original capture files retained their hashes. The 46 focused capture, review-export and intake regressions passed.

Private capture evidence is in `data/diagnostics/second-family-v61-capture-2026-11-21/output/`. The separate `gold.json`, digest, intake and verification receipt are in `data/diagnostics/second-family-v61-results-2026-11-21/`.

Next, qualify this second source locally through both exact artifact selections. Verify that Q013’s request carries the full claim and story context, excludes its scoring gold, and refuses Q008’s receipt or a wrong-version delivery. A live assessment would require separate approval. The full workflow canary remains on hold.
