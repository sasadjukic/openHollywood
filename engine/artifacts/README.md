# Artifacts

`open_hollywood_engine.artifacts` owns the provider-neutral Pydantic contracts
for structured creative output. The v0.1 catalog includes creative briefs,
characters, relationships, locations, world rules, beats, scene plans,
critiques, continuity findings, and the assembled story blueprint.

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
