# October 17 archive qualification and remaining intake replay

Date: 2026-11-12. Local work only; live calls **PAUSED**, canary **ON HOLD**.

## Outcome

The two October 17 archive contracts are registered for **seven explicitly selected
ordinary reviews**. N06–N12 replay through the tracked read-only intake with their
existing complete fields, scope declarations, work briefs and holds.

The replay retains **90 whole fields: ten pending claims, six holds and 74
unselected fields**. Together with the previous five reviews, all twelve audited
reviews now have verified intake: **151 fields, sixteen pending claims, nine holds
and 126 unselected fields**. These are pending assessment units, not new model
judgments or completed assessments. Prior gold remains external and unchanged.

Decision: [ADR 0048](../adr/0048-oct17-probe-intake-contracts.md), extending
[ADR 0047](../adr/0047-read-only-ordinary-review-intake.md).

## Qualified sources and exact selection

| Review | Trial | Fields | Pending | Holds |
| --- | --- | ---: | ---: | ---: |
| N06 | `s19201-elara-compound-outcome-initial` | 12 | 1 | 1 |
| N07 | `s19201-elara-embedded-initial` | 12 | 2 | 0 |
| N08 | `s19201-elara-missing-decision-initial` | 12 | 1 | 0 |
| N09 | `s19201-elena-compound-outcome-initial` | 14 | 2 | 2 |
| N10 | `s19401-elara-craft-craft_source-ordinary` | 14 | 2 | 2 |
| N11 | `s19401-elara-embedded-post-E0` | 13 | 1 | 1 |
| N12 | `s19401-elara-embedded-post-E1` | 13 | 1 | 0 |

N06–N09 belong to `fulfillment-contrasts-v61-2026-10-17`; N10–N12 belong to
`fulfillment-adjudication-edits-v61-2026-10-17`. The CLI requires each experiment's
sibling preparation and `-live` directory. N11/N12 additionally require the
contrasts pair for their parent review. Other October 17 trial IDs, judgment-only
arms and writer outputs are not admitted as ordinary reviews.

The registered contrasts contract pins:

- Plan: `9d01888c27a0aa45eaa126cf47824540591ce3867aa5324c44dbc48fb8371b9e`.
- Preparation closure: `8991649304da976309c4b10b2570fbbb0a51f94bc1f2d6931fc884c4adb8df0f`.
- Live closure: `995a563aab7b041c3d14d5545d43ffe7acaf8b2a6a2a2fa248912183b67b2439`.

The registered adjudication/edits contract pins:

- Plan: `765fd0499eb2ddb87f97e32cdfcb65b338b544c9be2e452f34bc16e4da0368a2`.
- Preparation closure: `6bc44e4df0e2f8ff278f513421ef458417ae738dea9d503fde65437fbf2d0968`.
- Live closure: `628f9108c682a0c108319f61109cbc48b715a0350c2c0c0669dae2678d36255b`.

Trust is selected by the live closure's exact bytes. The application verifies all
preparation/live members and operator evidence, not merely these root hashes.
The CLI and authored intake plans have no trust-pin override. Historical programs
are read as evidence where necessary and never executed.

## What the qualification established

The contracts differ in observable ways. The contrasts plan uses `case_sha256`
plus `prepared_sha256`, and its manifests include null `writer_source_policy`.
The adjudication/edits plan uses `file_sha256`, its sent records contain the full
request snapshot, and its receipts omit response length and finish reason. The
adapter verifies full sent/request equality and the model capture's terminal
`stop`, response hash and usage for that format. It preserves omitted metadata;
the October 16 and contrasts receipt requirements remain intact.

Craft-source and E0/E1 records have distinct manifest types. The admitted critics
retain ordinary production semantics. E1's writer dependency alone uses an
exact-edit response. Its original occurrence selections, nonoverlapping ranges,
UTF-8 byte offsets, replacement text, full materialized draft and edit audit are
reproduced locally and match the saved post-review input. E0's raw draft matches
its saved result. Neither check establishes that the edits were necessary or good.

Both post-reviews use N07's normalized critique. Their writer inputs preserve the
parent's complete input prefix, and their current candidate preserves the exact
writer result. The inherited critique UUID is derived in the October 16 namespace;
the revision UUID is derived in the contrasts namespace. These identities are
retained rather than regenerated in the later experiment's namespace.

The parent is authenticated under its own seal and stored as separately namespaced
operator provenance. Both archive pairs are protected from output writes. Recovered
history does not become critic-visible evidence; only the actual saved messages,
visible repair quotations and current prose locations populate the intake registry.

## Semantic scope retained

The new pending units correspond to P07–P14 and U01–U02 from the prior admission
audit: eight previously labeled supported fields and two uncertain fields. Those
labels were not copied into the pending work or re-established by software tests.
Only derived work/statement IDs and exact location references were rebound.

H04–H09 remain holds. H05 explicitly remains mixed factual/editorial scope; H09
remains an editorial-effect hold because style praise is not a zero-duplication
claim. The other holds preserve their unresolved source or interpretation questions.
No clause was dropped to obtain an easier factual judgment. The existing H03
private-flourish ambiguity and all earlier claims/gold remain unchanged.

This verifies handling of compound obligations, repair history and unavailable
authority. It does not establish semantic truth, evidence sufficiency, neutral
authored interpretation, necessary editing, writer preservation or story quality.
Human assessment of feel, flow, character and story-breaking effects remains a
separate requirement.

## Verification and local artifacts

**447 applicable tests pass, including 22 new archive-qualification tests.** The
final 22-test rerun also passes after the parent-input and per-reader cache checks.
Ruff, formatting and strict mypy pass for **242 repository Python files plus the
private acceptance helper**. The 56 existing Pydantic warnings come from deliberate
mutation fixtures. SQLite tests use isolated migrated databases and fake gateways;
Windows event-loop restrictions required their execution outside the sandbox.
There are no frontend/build changes, so frontend/build commands do not apply.

Both real CLI modes—inventory and declared intake—pass for all seven reviews.
All **44 output files** reuse with identical bytes and modification times. The
private acceptance blocks networking and SQLite. It preserves all **1,293** members
of the prior admission audit and **73** members of the previous intake acceptance.
The **1,166 original source pins** are unchanged. Independently re-collecting N01–N05
produces exactly their previous intake sources.

Private artifacts remain in ignored local data:

- [Acceptance](../../data/diagnostics/oct17-intake-qualification-2026-11-12/acceptance.json)
  and [verification](../../data/diagnostics/oct17-intake-qualification-2026-11-12/verification.json).
- [Contrasts intake](../../data/diagnostics/oct17-intake-qualification-2026-11-12/contrasts/intake/index.md)
  and [exact CLI arguments](../../data/diagnostics/oct17-intake-qualification-2026-11-12/contrasts/cli-arguments.json).
- [Craft/post-review intake](../../data/diagnostics/oct17-intake-qualification-2026-11-12/edits/intake/index.md)
  and [exact CLI arguments](../../data/diagnostics/oct17-intake-qualification-2026-11-12/edits/cli-arguments.json).

No provider, input-count, catalog or daemon call occurred. No user application
database was opened. Production prompts/profiles/graph/gates, canonical artifacts,
writer routing and the Blueprint checkpoint remain unchanged.

## Recommended next step

Perform a **bounded local completion-path rehearsal** on at most six of the sixteen
pending units, covering a compound obligation, visible repair history and unavailable
authority. Carry their unchanged full context, scope and briefs through the existing
assessment renderer, completion validator and read-only export boundary. Use clearly
authored response fixtures to exercise complete, uncertain, malformed, stale and
incomplete outcomes; never count those fixtures as new model or semantic evidence.

Acceptance should require exact source/field binding, complete active-unit coverage,
preserved holds/unselected fields, refusal of stale or insufficient completions and
no writer permission or database mutation. Report any interface gap before adding
an adapter. This would test the connection from admitted work to an inspectable
assessment result without opening autonomous repair.

Keep inference paused. The twelve reviews still supply no unambiguous naturally
contradicted admissions and no fresh scene family. A later comparison needs a
materially different question and defensible whole-claim contrasts; repeating the
supported cases cannot establish negative precision or generalization. No new live
plan or budget is frozen here.

Tracker and issue index updated; all fourteen issue bodies and posted URLs unchanged.
CW-007/CW-013 remain open; CW-014 unqualified. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; full workflow canary ON HOLD.**
