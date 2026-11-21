# Q013 downstream assessment qualification

**Decision, 2026-11-21.** Q013 qualifies for preparation of a one-claim `gpt-6.1-sol` high-reasoning smoke using the original critique selection. The exact draft selection reaches the same work. Assessing it twice would repeat the question. This qualification used local fixtures and made zero provider calls. Sol’s factual judgment, evidence choice, token usage and latency on Q013 remain unmeasured.

## Both exact selections

Q013 is Gemma’s complete 185-character turning-point explanation for *The Impossible Card*. It claims that Elara notices the card is dated October 14, 2034, recognizes the present is October 14, 2024, and understands the ten-year difference. The saved v61 critic invocation is `1751730f-4547-465f-afa5-81ef9b8b29fb`. Replay authenticated its original HTTP response, terminal, SQLite capture and exact inputs, then rebuilt the intake from a disposable database copy. [Original capture and gold freeze](second-family-ordinary-v61-capture-results-2026-11-21.md)

| Selection | Exact artifact version | Input-count body | Generation body | Request manifest SHA-256 |
| --- | --- | ---: | ---: | --- |
| Original critique v3 | `ca5915a5-5b82-4bad-82ce-e5c31a519dc0` | 281,286 bytes | 281,433 bytes | `59ad7cd95b4d22e3541e3d7f190d30c37ea8132b02e4e6c76a7d5dec5fce170f` |
| Reviewed draft v1 | `c3689bce-e108-4761-bafe-390f6e7ea1b3` | 281,285 bytes | 281,432 bytes | `47f1bc0e1778e7663c2a6cfcde86e69bc36b28109373a171747ec63067054169` |

Each selection carried both version identities, the whole claim, the original two critic messages, the 3,435-character draft, the work brief and all 17 review-field dispositions. Q013 was the sole active unit. The compact presentation represented five context documents and retained the local provenance document’s identity and digest. All 920 evidence locations resolved to the original fields, text, offsets and hashes. The count and generation bodies for each selection carried identical model input and schema. Across selections, only the selected-artifact field differed in the model-facing packet.

## Gold exclusion

Request preparation and the transport rehearsal ran with scorer-file reads and network connections blocked. A separate scorer-side check compared all four request bodies to the admitted source and the frozen gold. The expected judgment, scorer rationale, adequacy rubric, chosen witness list, selection rationale, gold digest and injected answer were excluded. The original claim and the draft passages needed to assess it were present.

The work brief asks the assessor to bind the two dates to their roles and locate Elara’s observation and the time interval. Its only declared evidence reference is the complete draft, `E0920`. The independent scorer can resolve the card inscription, the 2034 date, Elara staring at the numbers, the present date and the explicit ten-year realization at `E0282`, `E0284`, `E0286`, `E0288` and `E0290`. The plan at `E0237` establishes intent. Scoring requires coverage in the draft and accepts equivalent precise passages. Frozen gold SHA-256 is `0e9747397ead04c270566f6e27173a859a5eb50338ab235ced2758d3dc9b40d0`.

## Wrong versions and Q008’s receipt

| Control | Result |
| --- | --- |
| Genuine critique v2 (`3128c91a-1b2f-4b57-9c50-f89ddee061c4`) and draft v2 (`7cbed44f-b4c3-4736-a912-3ea2fad713f3`), each with its own correct content hash | Both existed under the correct project and artifact. Q013 rejected each during selection, before a request could be dispatched. |
| Changed selected version in a count or generation body | The native outgoing-byte check rejected the altered endpoint before its intent or dispatch. Changing the generation body allowed only the preceding valid mock count. |
| Completed Q013 journal or delivery from the other selection | Export rejected the foreign manifest. Result binding and usage accounting each rejected the foreign request digest despite the common work and batch. |
| Q008’s genuine, previously observed Sol delivery | The Q008 publisher authenticated its original receipt and final. Both Q013 selections rejected result binding and usage accounting with `mixed_work_scope`, even though both cases used `batch-001`. |
| Q008’s original Gemma HTTP receipt and terminal | Both selections rejected the prior critic’s source with `saved_review_capture_receipt_binding`. |

The two legitimate Q013 entry points identify one assessment question. If a future read-only lookup shows the same observed delivery from either artifact, its receipt must still identify the selection that originated the request.

For each exact selection, an injected `uncertain` answer citing `E0920` exercised result binding, fixture publication and repeat opening. The authored answer deliberately differs from the frozen `supported` gold. A rejected count, missing generation terminal, missing closure or altered terminal prevented publication. Two additional controls preserved terminal and closure records. A truncated response failed with `incomplete_response` and a completed response omitting Q013 failed with `active_result_coverage`. These exercises produced no observed Q013 assessment or usage record.

## Replay and next step

Q008’s completed smoke pins the historical adapter files by digest. A separate Q013 diagnostic registration uses the existing packet renderer, OpenAI wire mapper and receipt checks while preserving Q008 replay. The rehearsal supplied the Q013 plan and authored replies to the native fixture journal, which ran its outgoing-byte check, count gate, terminal audit, result binding and fixture publication. Registration `saved-v61-q013-2026-11-21` pins 11 source members, including the 24,580,096-byte database. Its seal is `ee479205f2bddddd57b66e69bdeae0b444bdf7ae29cc443616f864d7c32b9636`. The six original capture members and the gold retained their recorded hashes.

Private evidence is in `data/diagnostics/q013-downstream-2026-11-21/`. The `qualified/` directory holds both fixture journals, publications and verification receipts. `receipt-and-version-controls.json` records the genuine adjacent versions and cross-case rejections. With the local registrations present, these commands rebuild the requests and rerun the receipt controls.

```powershell
$root = 'data/diagnostics/q013-downstream-2026-11-21'
uv run --extra api python -m scripts.q013_assessment --selection "$root/original_review.json"
uv run --extra api python -m scripts.q013_assessment --selection "$root/reviewed_draft.json"
uv run --extra api python -m scripts.verify_q013_selection_binding
```

The final renderer reproduced all four checked body digests. Both selections passed eight journal scenarios apiece and the four additional terminal controls. All 2,644 distinct Python tests passed. Ruff lint, formatting and strict mypy passed across 348 Python files.

**Next step.** Prepare a single-use approval manifest and durable journal for the critique selection. Freeze one full-context OpenAI input count, at most one generation, and zero retries. The local mapping caps input at 96,000 tokens, output at 32,000 tokens, and the reservation at USD 0.60. An injected count of 96,000 passed and 96,001 stopped generation. The actual count requires the approved endpoint. Freeze claim correctness and evidence coverage as separate scores and submit the plan before either endpoint is contacted. Step 19 stays in progress, production prompts are unchanged, and the full workflow canary remains on hold.
