"""Deterministic renderer and exporter coverage."""

from __future__ import annotations

from io import BytesIO

import pytest
from docx import Document
from open_hollywood_engine.artifacts import SceneDraft
from open_hollywood_engine.rendering import (
    FountainElement,
    FountainElementKind,
    FountainScreenplay,
    ProseManuscript,
    RenderingInvariantError,
    export_docx,
    export_pdf,
    render_fountain,
    render_markdown,
)
from pypdf import PdfReader


def _manuscript() -> ProseManuscript:
    return ProseManuscript.from_scene_drafts(
        title="The #Untouched Stroller",
        author="Mara *Vukovic*",
        drafts=tuple(
            SceneDraft(
                scene_id=f"scene_{number}",
                scene_number=number,
                title=f"Threshold {number}",
                revision_number=1,
                prose=(
                    f"Mara stopped before the concrete threshold in scene {number}.\r\n\r\n"
                    "The new stroller waited beneath a skin of dust."
                ),
                is_complete=True,
            )
            for number in range(1, 4)
        ),
    )


def test_markdown_renderer_is_stable_and_escapes_heading_markup() -> None:
    rendered = render_markdown(_manuscript())

    assert rendered.startswith("# The \\#Untouched Stroller\n\n*By Mara \\*Vukovic\\**\n\n")
    assert "## Scene 1: Threshold 1" in rendered
    assert "\r" not in rendered
    assert rendered.endswith("\n")


def test_fountain_renderer_uses_explicit_typed_elements() -> None:
    screenplay = FountainScreenplay(
        title="Night Shift",
        author="Ada Writer",
        elements=(
            FountainElement(
                kind=FountainElementKind.SCENE_HEADING,
                text="INT. ARCHIVE - NIGHT",
            ),
            FountainElement(
                kind=FountainElementKind.ACTION,
                text="THE LIGHTS FAIL.\nAda reaches for the ledger.",
            ),
            FountainElement(kind=FountainElementKind.CHARACTER, text="Ada"),
            FountainElement(
                kind=FountainElementKind.PARENTHETICAL,
                text="under her breath",
            ),
            FountainElement(kind=FountainElementKind.DIALOGUE, text="Not again."),
            FountainElement(kind=FountainElementKind.TRANSITION, text="CUT TO:"),
        ),
    )

    assert render_fountain(screenplay) == (
        "Title: Night Shift\n"
        "Credit: Written by\n"
        "Author: Ada Writer\n\n"
        ".INT. ARCHIVE - NIGHT\n\n"
        "!THE LIGHTS FAIL.\n!Ada reaches for the ledger.\n\n"
        "ADA\n\n"
        "(under her breath)\n\n"
        "Not again.\n\n"
        ">CUT TO:\n"
    )


def test_rendering_invariants_reject_incomplete_or_disordered_scenes() -> None:
    drafts = tuple(
        SceneDraft(
            scene_id=f"scene_{number}",
            scene_number=number,
            title=f"Scene {number}",
            revision_number=0,
            prose="Prose.",
            is_complete=number != 2,
        )
        for number in range(1, 4)
    )

    with pytest.raises(RenderingInvariantError, match="must be complete"):
        ProseManuscript.from_scene_drafts(title="Story", drafts=drafts)

    reordered = (_manuscript().scenes[1], _manuscript().scenes[0], _manuscript().scenes[2])
    with pytest.raises(RenderingInvariantError, match="contiguously numbered"):
        ProseManuscript(title="Story", scenes=reordered)


def test_pdf_export_is_deterministic_searchable_and_paginated() -> None:
    first = export_pdf(_manuscript())
    second = export_pdf(_manuscript())

    assert first == second
    assert first.startswith(b"%PDF-")
    reader = PdfReader(BytesIO(first))
    assert len(reader.pages) == 4
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "The #Untouched Stroller" in text
    assert "Scene 3: Threshold 3" in text


def test_docx_export_is_deterministic_editable_and_paginated() -> None:
    first = export_docx(_manuscript())
    second = export_docx(_manuscript())

    assert first == second
    assert first.startswith(b"PK")
    document = Document(BytesIO(first))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "The #Untouched Stroller" in text
    assert "Scene 3: Threshold 3" in text
    page_width = document.sections[0].page_width
    left_margin = document.sections[0].left_margin
    assert page_width is not None
    assert left_margin is not None
    assert page_width.inches == pytest.approx(8.5)
    assert left_margin.inches == pytest.approx(1)
