# Formal Cloud-versus-baseline evaluation: Blueprint generation

September 29, 2026. **Checkpoint result: 12/12 fresh Blueprints prepared, awaiting
human approval.** The measurements below preserve that checkpoint snapshot.
There were no terminal Blueprint failures. At that checkpoint, item 4 and product
Step 19 were **IN PROGRESS**.

**Subsequent approval:** the user explicitly approved all twelve exact versions
in chat: "I approve these blueprints." The approval was imported on September 29;
the receipt at 16:55:51 UTC confirms twelve persisted human decisions, twelve
successful Blueprint workflows and zero additional model calls. The original
blank form is preserved as `blueprints/approvals.blank.csv`; the completed form,
`blueprint-approval-authorization.json` and `blueprint-approval-import.json` bind
the decision to the packet below. Baseline and production execution followed
under the frozen settings. Approval was given as generated, without editorial
review or edits; it is not a human quality score. Subsequent results belong in the
[execution report](step-19-formal-cloud-v33-execution-2026-09-29.md).

**September 30 update:** all eleven eligible formal comparisons have completed
human review, and the campaign evidence seal is verified. Item 4 is complete;
Step 19 remains open for unmet acceptance criteria, unknown cost and independent
repeatability. See the
[review results](step-19-formal-cloud-v33-execution-2026-09-29.md#human-review-completed--2026-09-30).

This is the preparation phase of campaign
`042918c2-8a50-49fd-831b-c1a93553d4f6`, following the
[frozen setup protocol](step-19-formal-cloud-v33-setup-2026-09-29.md).
It is not a completed twelve-story production result or a quality assessment.

## Execution and accounting

The user requested generation and stated an intention to approve the resulting
Blueprints without editorial review, to observe the system's autonomous output.
The existing `PrepareBlueprints` phase ran all twelve cases sequentially using
`gemma4:31b-cloud`, Blueprint prompt v9 / graph v4. The subsequent production
configuration remains prompt v33 / graph v9. No prompts, budgets, retry allowances,
or application source were changed, and no terminal failure was rerun.

| Measure | Observed result |
| --- | --- |
| First workflow start | 16:43:46 UTC / 18:43:46 Europe/Belgrade |
| Last workflow checkpoint update | 16:50:34 UTC / 18:50:34 Europe/Belgrade |
| Preparation interval | 408.155 seconds, approximately 6 minutes 48 seconds |
| Prepared and awaiting approval | 12/12 |
| Terminal failures | 0 |
| Model invocations | 74: 72 succeeded, 2 failed validation |
| Input tokens, including failed calls | 197,928 |
| Output tokens, including failed calls | 77,883 |
| Human decisions persisted | 0 |
| Production / baseline runs | 0 / 0 |
| Cost acceptance | Unknown; no supported dollar-cost evidence |

Times are taken from persisted workflow timestamps. The interval excludes later
offline packaging and documentation. All failed attempts remain in the token and
call totals.

| Prompt | State | Calls | Failed calls | Input tokens | Output tokens |
| --- | --- | ---: | ---: | ---: | ---: |
| OH-V01-001 | Awaiting approval | 7 | 1 | 21,314 | 10,383 |
| OH-V01-002 | Awaiting approval | 6 | 0 | 16,120 | 5,884 |
| OH-V01-003 | Awaiting approval | 6 | 0 | 16,381 | 6,896 |
| OH-V01-004 | Awaiting approval | 6 | 0 | 15,939 | 6,026 |
| OH-V01-005 | Awaiting approval | 7 | 1 | 19,678 | 7,504 |
| OH-V01-006 | Awaiting approval | 6 | 0 | 14,653 | 4,950 |
| OH-V01-007 | Awaiting approval | 6 | 0 | 16,046 | 6,556 |
| OH-V01-008 | Awaiting approval | 6 | 0 | 15,799 | 5,988 |
| OH-V01-009 | Awaiting approval | 6 | 0 | 16,017 | 6,354 |
| OH-V01-010 | Awaiting approval | 6 | 0 | 14,884 | 5,508 |
| OH-V01-011 | Awaiting approval | 6 | 0 | 14,459 | 5,176 |
| OH-V01-012 | Awaiting approval | 6 | 0 | 16,638 | 6,658 |

## Recovered validation failures

Both failures occurred on the Blueprint integrator's first response and recovered
on its existing second attempt:

- **OH-V01-001:** `schema_validation_failed`; the twelfth beat's `character_ids`
  list was empty, violating its minimum of one item.
- **OH-V01-005:** `schema_validation_failed`; three scene-plan entries omitted
  `scene_number`, with a related minimum-length validation error on `scene_plans`.

Both provider responses ended with `stop`. These were structured-output failures,
not recorded provider timeouts or output-limit truncations. Ten cases needed the
normal six calls; two needed seven. This distinction preserves the failed-call
evidence while recognizing that all cases reached the checkpoint.

## Exact approval set

The packaged set contains OH-V01-001 through OH-V01-012, with exact Blueprint and
critique version IDs, content digests, run IDs and interrupt IDs. Its canonical
packet SHA-256 is:

`2027946824d2245f821bedb1f1b7b80dc3bbae9e0f7a85e7c0a7e965fbab0447`

In `data/benchmarks/v0.1/formal-cloud-v33-2026-09-29/`:

- `blueprints/approval-manifest.md` identifies the exact versions without story
  titles, premises, plots, character information or automated quality scores.
- `blueprints/packet.json` and `blueprints/guide.md` retain the complete generated
  dossier. They have not been presented as required reading in this conversation.
- `blueprints/approvals.csv` has twelve rows with every approval and notes field
  still blank. No human approval has been inferred from the user's future intent.
- `blueprint-generation-authorization.json` records the generation authorization
  and the user's intended approach at launch.
- `blueprint-checkpoint.json` records this checkpoint's per-case invocation
  accounting, validation errors, exact artifact references and evidence hashes.
- `record_blueprint_checkpoint.py` retains the offline validation and manifest
  creation procedure; it makes no model calls and opens SQLite read-only.
- Timestamped `logs/*PrepareBlueprints*` and `logs/*PackageBlueprints*` preserve
  the phase outputs. The original setup receipts remain unchanged.

The user's choice superseded the generated guide's default editorial checklist.
The subsequent approval was recorded **as generated, without
editorial review or edits**. This was authorization for production, not a claim
that the user checked artifact fidelity or assigned quality scores. Do not claim
plot exposure solely from an approval that did not involve reading the content;
record any actual exposure separately for the later randomized story comparison.

## Verification and remaining work

The packaging preflight verified all 123 frozen runtime/configuration file hashes,
the campaign inputs and report binding, database schema 0008, SQLite integrity,
foreign keys and Cloud profile. The packet validated all twelve Blueprint and
critique content digests; their persisted version hashes matched. The blank CSV
matched the canonical generated form exactly. At that checkpoint, all twelve
workflows were paused at `approval` with reason `HUMAN_APPROVAL`; there were no
production or baseline workflows and no human decisions. The checkpoint recorder passed Ruff lint and
format checks. No application-code change required a new regression suite.

The checkpoint campaign report had zero terminal story results, as expected.
Subsequent approval, its offline import, the direct-model baseline arm, all three
declared production batches and formal human scoring are complete, as recorded
in the execution report. Cost qualification and item 5's independent repeatability
evidence remain outstanding.
