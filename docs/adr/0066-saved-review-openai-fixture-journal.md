# ADR 0066 — OpenAI request and fixture journal for a saved review

Accepted on 2026-11-19 for the registered local qualification.

Use the saved-review source receipt from [ADR 0065](0065-read-only-saved-review-completion-adapter.md)
as the root of a separately versioned OpenAI request. Rebuild the original work from
the sealed workspace before each endpoint and during export. Use the existing compact
assessment instructions, native schema, Responses serializer and response mapper.
The selected artifact and both exact review/draft identities belong in each request.
The archive registration, receipt and operator snapshot body belong in local evidence.

A request manifest identifies both immutable input versions, the source receipt, the native
work and the exact count and generation bodies. Its byte digest binds the native assessment
receipt. Each new journal has its own identifier and allows one count and, after an
admitted count, one generation. This keeps attempts distinct even when two captures
use identical request bytes. The fixture runner writes each intent durably before
calling its in-memory transport. An
open intent consumes the slot. The audit checks the actual journal against the source,
the endpoint bytes, the registered synthetic reply and the closing record.

The local publisher requires a closed journal and complete native binding. An operator
can also export an incomplete audit. The original authored final supplies only the
injected generation reply. Request preparation and input counting are independent of
that final. Token counters supplied by the fixture are synthetic. Live transport,
observed-model evidence and production assessment attachment are outside this contract.

[Verification and controls](../handoffs/assessment-saved-review-openai-2026-11-19.md)
