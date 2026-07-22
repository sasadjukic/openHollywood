# ADR 0006: Runtime secret handles and leak guards

- Status: Accepted
- Date: 2026-07-22

## Context

Cloud inference requires credentials, but Open Hollywood deliberately persists prompts, story artifacts, workflow events, invocation traces, and portable database files. Passing ordinary credential strings through those domain and persistence structures would make accidental disclosure likely.

The current v0.1 slice runs as a local browser, FastAPI service, and worker.
Tauri packaging and its platform-backed secret storage arrive later, so the
engine also needs a storage-neutral credential boundary now.

## Decision

Represent model credentials with stable `ModelSecret` handles and opaque,
redacting `SecretValue` objects. Workflows and model profiles may retain only a handle. A `SecretStore` resolves the value at runtime, immediately before the provider transport is constructed.

Use process environment variables as the first `SecretStore` implementation.
It reads values on demand, never loads or writes dotenv files, and can later be replaced by a Tauri Stronghold adapter without changing workflow or gateway contracts.

Apply fail-closed leak guards at two boundaries:

1. The model gateway rejects a configured credential in a request before any
   prompt leaves the process, and rejects a provider response that contains it.
2. The SQLAlchemy session rejects configured credentials, opaque secret values,
   and credential-labelled fields before any durable record is flushed.

Database export code must run the full-table secret audit before copying or
serializing SQLite. Committed fixture files are audited against credentials
configured in the test process. Errors expose only safe handles and field
paths, never values or provider response bodies.

## Consequences

- Story artifacts, prompts, traces, events, profiles, and database exports share one enforceable secret policy.
- Provider adapters receive plaintext only at the HTTP authentication boundary.
- Model profiles remain portable because they contain handles, not machine-local credential values.
- Raw SQL can bypass the ORM guard, so every database exporter must invoke the independent export audit.
- Environment variables are an interim local runtime source, not frontend
persistence or the final desktop secret store.
