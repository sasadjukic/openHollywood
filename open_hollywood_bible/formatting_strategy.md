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