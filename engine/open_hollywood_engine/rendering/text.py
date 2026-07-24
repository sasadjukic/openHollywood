"""Deterministic plain-text renderers."""

from __future__ import annotations

import re

from open_hollywood_engine.rendering.contracts import (
    FountainElement,
    FountainElementKind,
    FountainScreenplay,
    ProseManuscript,
)


def render_markdown(manuscript: ProseManuscript) -> str:
    """Render a complete prose manuscript as stable CommonMark text."""
    blocks = [f"# {_escape_markdown_heading(manuscript.title.strip())}"]
    if manuscript.author is not None:
        blocks.append(f"*By {_escape_markdown_emphasis(manuscript.author.strip())}*")
    for scene in manuscript.scenes:
        heading = _escape_markdown_heading(scene.title.strip())
        blocks.extend(
            (
                f"## Scene {scene.scene_number}: {heading}",
                _normalize_prose(scene.prose),
            )
        )
    return "\n\n".join(blocks) + "\n"


def render_fountain(screenplay: FountainScreenplay) -> str:
    """Render typed screenplay elements using unambiguous Fountain syntax."""
    title_page = [f"Title: {screenplay.title.strip()}", f"Credit: {screenplay.credit.strip()}"]
    if screenplay.author is not None:
        title_page.append(f"Author: {screenplay.author.strip()}")
    body = [_render_fountain_element(element) for element in screenplay.elements]
    return "\n".join(title_page) + "\n\n" + "\n\n".join(body) + "\n"


def _render_fountain_element(element: FountainElement) -> str:
    text = _normalize_line_endings(element.text).strip()
    match element.kind:
        case FountainElementKind.SCENE_HEADING:
            return f".{text.removeprefix('.')}"
        case FountainElementKind.ACTION:
            return "\n".join(f"!{line}" if line else "" for line in text.splitlines())
        case FountainElementKind.CHARACTER:
            suffix = " ^" if element.dual_dialogue else ""
            return f"{text.upper()}{suffix}"
        case FountainElementKind.PARENTHETICAL:
            return text if text.startswith("(") and text.endswith(")") else f"({text})"
        case FountainElementKind.DIALOGUE:
            return text
        case FountainElementKind.TRANSITION:
            return f">{text.removeprefix('>')}"
        case FountainElementKind.SECTION:
            return f"{'#' * element.section_level} {text}"
        case FountainElementKind.SYNOPSIS:
            return f"= {text}"
        case FountainElementKind.CENTERED:
            return f"> {text.removeprefix('>').removesuffix('<').strip()} <"
        case FountainElementKind.PAGE_BREAK:
            return "==="


def _normalize_prose(value: str) -> str:
    normalized = _normalize_line_endings(value).strip()
    return re.sub(r"\n{3,}", "\n\n", normalized)


def _normalize_line_endings(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _escape_markdown_heading(value: str) -> str:
    return re.sub(r"([\\`*_{}\[\]<>#+.!|-])", r"\\\1", value)


def _escape_markdown_emphasis(value: str) -> str:
    return re.sub(r"([\\*_])", r"\\\1", value)
