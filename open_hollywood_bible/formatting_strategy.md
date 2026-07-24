# Formatting strategy

Formatting matters because format is part of the creative contract.

Support an explicit `work_format` from the beginning:

- Prose short story
- Novel
- Screenplay
- TV pilot
- Stage play

For screenplay-family output, use Fountain as the canonical intermediate representation. It is readable as plain text, versionable, and convertible into formatted pages.

Recommended canonical outputs:

- Story and novel: structured Markdown/HTML
- Screenplay and TV: Fountain
- Internal artifact data: JSON/Pydantic schemas
- Export: PDF, DOCX, HTML, plain text; EPUB later

Formatting should be deterministic. Do not ask a model to imitate screenplay spacing and hope it remains valid. The model writes structured screenplay content; a parser and renderer produce the final document.

## Implemented v0.1 boundary

Short-prose export is implemented through one immutable `ProseManuscript`
contract assembled from the latest approved Scene Draft versions. It requires
three to eight complete scenes with unique IDs and contiguous numbering.
Markdown, searchable US-Letter PDF, and editable US-Letter DOCX are pure
rendering operations over that contract. Identical input produces identical
bytes, and the API reports exact source-version lineage and a content hash.

Fountain is implemented as a separate typed screenplay renderer following the
official syntax for title pages, forced scene headings and action, characters,
parentheticals, dialogue, transitions, sections, synopses, centered text, and
page breaks. It is not exposed as a v0.1 short-prose export and never attempts
to infer screenplay elements from prose.
