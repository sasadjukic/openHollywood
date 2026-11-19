# Saved-review OpenAI request and journal qualification — 2026-11-19

The count and generation requests for the registered v61 fixture retained the same
full claim, story and review context. Both exact artifact selections reproduced the
previously qualified Q010 assessment and its citation to the original draft. Only a
matching, closed generation qualified for local publication. Every HTTP response
came from an in-memory fixture. Live calls totaled **zero**.

## What reached each endpoint

The fixture used the repository’s existing Sol-high mapping and compact diagnostic
instructions. For each selection, the input-count body exactly matched the generation
body’s model, input messages, reasoning setting and response schema. Generation used
disabled truncation. The local request manifest binds both endpoint byte hashes, the
source receipt and both immutable versions. The selected role travels in both bodies.

| Selected artifact | Exact version | Count body, bytes | Generation body, bytes |
| --- | --- | ---: | ---: |
| Original critique | `ed49f50a-5be9-49e6-86c1-fb3dded0d425` | 142,130 | 142,277 |
| Reviewed draft | `95438a97-06fa-45f7-a2f8-ae784779a54d` | 142,129 | 142,276 |

The verification compared each serialized body against the earlier sealed intake and
offline request. It checked both complete original critic messages, the visible
assignment, the entire draft, the whole saved critique and native audit, all 14 review
field dispositions, the active claim and its original span, declarations and work brief.
All **483** compact evidence references resolved to the original document version,
field pointer, exact quote, offsets and hashes. E0483 resolved to the complete prose
of the reviewed draft. The operator-provenance document contributed its identity,
version and digest. Its body, archive paths, receipt and injected final stayed local.

Q010 reads “Simulated fulfilled obligation, not semantic evidence.” This fixture can
demonstrate exact claim delivery and citation binding. Its authored support label
supplies no evidence about reviewer accuracy or the writing’s quality. The raw critic
response remains unavailable. Its saved normalized critique and audit were available
in full to both endpoints.

## Journal controls

| Case | Count intents | Generation intents | Observed result |
| --- | ---: | ---: | --- |
| Complete, critique selected | 1 | 1 | Published and reused with identical bytes and file modification times. |
| Complete, draft selected | 1 | 1 | Published with the draft selection and the same bound assessment and citation. |
| Interrupted generation | 1 | 1 | One possibly-sent attempt, unknown generation usage, no result and publication refused. |
| Count of 24,001 against a 24,000 reservation | 1 | 0 | Count rejected and journal closed. Publication refused. |
| Wrong draft version in count body | 0 | 0 | Refused before count intent or mock dispatch. |
| Wrong draft version in generation body | 1 | 0 | Correct count retained. Refused before generation intent or mock dispatch. |

Each journal has its own identifier. Every intent is written and flushed before mock
dispatch and binds the exact endpoint bytes to the request manifest. Each outcome
binds to its intent and to the known injected reply. Audit checks the closing record,
then binds the observed final to the native work using the new request manifest digest.
The earlier offline request digest remains in the source record. An interrupted
journal cannot resume or retry. Regression controls also cover a terminal taken from
a different journal for the same request, an edited and rehashed response, a missing
closing record, a different selected role and a different version with the same content
digest. None qualifies for publication.

The fixed **100 input and 20 output tokens** in the successful reply are authored
counters. The missing terminal has null generation usage. The byte sizes above are
measurements of serialized requests. Actual token requirements, provider acceptance,
latency and billed cost remain unmeasured. Source preparation, counting and the
missing-terminal case were exercised with access to the earlier authored answer blocked.

## Verification and reproduction

The [fixture runner](../../scripts/saved_review_openai_fixture.py) supports `capture`,
`audit` and `publish`. The [operator commands](../../README.md) use the registered
private capture. The [seven regression cases](../../tests/api/test_saved_review_openai_fixture.py)
create portable fixture workspaces and inspect requests at the mock transport boundary.
The [application service](../../apps/api/open_hollywood_api/services/saved_review_openai_fixture.py)
uses the existing provider serializer, response mapper, native result binder and
manifest-last publisher. The qualification adds a local diagnostic path. [ADR 0066](../adr/0066-saved-review-openai-fixture-journal.md)

Private evidence is under `data/diagnostics/assessment-saved-review-openai-2026-11-19/`.
`verification.json` records the version IDs, endpoint hashes, outcomes and refusals.
Inside `qualified/`, each case has its exact requests and journal, plus an audit
directory. The two successful selections also have publication directories. The replay
preserved the 109 members and two seals from the preceding qualifications and the
production database, WAL and SHM, including modification times.

All **2,600 collected Python tests passed** in six isolated groups, with zero skips.
The seven new regressions passed with networking blocked in their disposable workspaces.
The full run recorded 56 Pydantic serialization warnings in the existing claim-scope,
authority and work-brief tests. Ruff, formatting and strict mypy passed across 326 repository Python files. The
preservation check also verified 3,620 members of 30 older seals and 1,788 source-file
hashes and modification times.

## Recommended next step

Audit up to **six previously unadmitted saved ordinary v61 reviews** for one substantive,
whole factual claim. Record its exact review and draft versions, source scope, expected
judgment and the evidence that establishes it. Fix the judgment before looking at an
assessor’s output. Keep claims about feel, flow or whether a revision improves the prose
in the human editorial review.

If a claim qualifies, replay its request through this local context and version check
before proposing a bounded live smoke. If the workspace contains only the known v33
reviews and the Q010 placeholder, record the missing source and propose how to obtain
one supported review. Step 19 remains in progress. Production prompts are unchanged,
live calls are paused and the full workflow canary is on hold.
