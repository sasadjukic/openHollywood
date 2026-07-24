# Artifacts

`open_hollywood_engine.artifacts` owns the provider-neutral Pydantic contracts
for structured creative output. The v0.1 catalog includes creative briefs,
developed premises, characters, relationships, locations, world rules, beats,
scene plans, critiques, continuity findings, and the assembled story blueprint.
The dialogue experiment adds a one-time director briefing, isolated character
turns, and structured director evaluations. Director evaluations validate
ordered emotional-arc progress, unambiguous thread status, and the closure
conditions required for a requested scene ending.
Scene production adds immutable `SceneDraft` versions with stable scene
identity, sequence, revision number, complete prose, and an explicit completion
flag. A draft advances only when its content validates and the production graph
has an independent `Critique` targeting that exact version.
Continuity supervision adds an exact-version `ContinuityReport`, a typed
`StoryBibleUpdate` delta, and a full immutable `StoryBible` successor after
every accepted scene. The pure reducer appends scene and timeline history,
upserts current entity state in stable order, preserves established facts,
allows mysteries and promises to resolve but never reopen, and rejects
duplicate or dangling canonical references.

All models reject unknown fields, strip surrounding whitespace, and are frozen
after validation. Collection fields use tuples so nested artifact content is
immutable in memory as well as append-only in persistence. `StoryBlueprint`
also validates stable IDs, ordered beat and scene numbers, specialist reference
integrity, and agreement with the creative brief's scene and character counts.

`ARTIFACT_SCHEMAS` is the canonical type registry. Use `artifact_json_schema()`
when requesting structured model output and `validate_artifact_json()` at the
model-response boundary. The persistence layer keeps artifact kind and schema
version in the immutable `ArtifactVersion` envelope; the current content schema
version is exported as `SCHEMA_VERSION`.
