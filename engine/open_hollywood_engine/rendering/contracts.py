"""Provider-neutral contracts for deterministic manuscript rendering."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from open_hollywood_engine.artifacts import SceneDraft


class RenderingInvariantError(ValueError):
    """Raised when artifact inputs cannot form one deterministic document."""


@dataclass(frozen=True, slots=True)
class ManuscriptScene:
    """One accepted prose scene in final manuscript order."""

    scene_id: str
    scene_number: int
    title: str
    prose: str

    def __post_init__(self) -> None:
        if not self.scene_id.strip():
            raise RenderingInvariantError("scene_id must not be empty")
        if self.scene_number < 1:
            raise RenderingInvariantError("scene_number must be positive")
        if not self.title.strip():
            raise RenderingInvariantError("scene title must not be empty")
        if not self.prose.strip():
            raise RenderingInvariantError("scene prose must not be empty")


@dataclass(frozen=True, slots=True)
class ProseManuscript:
    """A complete v0.1 short-prose manuscript."""

    title: str
    scenes: tuple[ManuscriptScene, ...]
    author: str | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise RenderingInvariantError("manuscript title must not be empty")
        if self.author is not None and not self.author.strip():
            raise RenderingInvariantError("author must be omitted or non-empty")
        if not 3 <= len(self.scenes) <= 8:
            raise RenderingInvariantError("a short-prose manuscript requires 3 to 8 scenes")

        scene_numbers = tuple(scene.scene_number for scene in self.scenes)
        expected_numbers = tuple(range(1, len(self.scenes) + 1))
        if scene_numbers != expected_numbers:
            raise RenderingInvariantError("scenes must be ordered and contiguously numbered from 1")
        scene_ids = tuple(scene.scene_id for scene in self.scenes)
        if len(set(scene_ids)) != len(scene_ids):
            raise RenderingInvariantError("scene IDs must be unique")

    @classmethod
    def from_scene_drafts(
        cls,
        *,
        title: str,
        drafts: tuple[SceneDraft, ...],
        author: str | None = None,
    ) -> ProseManuscript:
        """Build a manuscript only from complete, accepted-scene-shaped drafts."""
        if any(not draft.is_complete for draft in drafts):
            raise RenderingInvariantError("every exported scene draft must be complete")
        return cls(
            title=title,
            author=author,
            scenes=tuple(
                ManuscriptScene(
                    scene_id=draft.scene_id,
                    scene_number=draft.scene_number,
                    title=draft.title,
                    prose=draft.prose,
                )
                for draft in drafts
            ),
        )


class FountainElementKind(StrEnum):
    """Supported deterministic Fountain element types."""

    SCENE_HEADING = "scene_heading"
    ACTION = "action"
    CHARACTER = "character"
    PARENTHETICAL = "parenthetical"
    DIALOGUE = "dialogue"
    TRANSITION = "transition"
    SECTION = "section"
    SYNOPSIS = "synopsis"
    CENTERED = "centered"
    PAGE_BREAK = "page_break"


@dataclass(frozen=True, slots=True)
class FountainElement:
    """One explicitly typed screenplay element."""

    kind: FountainElementKind
    text: str = ""
    section_level: int = 1
    dual_dialogue: bool = False

    def __post_init__(self) -> None:
        if self.kind is FountainElementKind.PAGE_BREAK:
            if self.text:
                raise RenderingInvariantError("page breaks cannot contain text")
        elif not self.text.strip():
            raise RenderingInvariantError(f"{self.kind.value} text must not be empty")
        if self.kind is FountainElementKind.SECTION and not 1 <= self.section_level <= 6:
            raise RenderingInvariantError("Fountain section level must be between 1 and 6")
        if self.dual_dialogue and self.kind is not FountainElementKind.CHARACTER:
            raise RenderingInvariantError("dual_dialogue is valid only for character elements")


@dataclass(frozen=True, slots=True)
class FountainScreenplay:
    """A typed screenplay document rendered without prose-to-script guessing."""

    title: str
    elements: tuple[FountainElement, ...]
    author: str | None = None
    credit: str = "Written by"

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise RenderingInvariantError("screenplay title must not be empty")
        if self.author is not None and not self.author.strip():
            raise RenderingInvariantError("author must be omitted or non-empty")
        if not self.credit.strip():
            raise RenderingInvariantError("credit must not be empty")
        if not self.elements:
            raise RenderingInvariantError("screenplay must contain at least one element")

        prior_kind: FountainElementKind | None = None
        for element in self.elements:
            if element.kind is FountainElementKind.PARENTHETICAL and prior_kind not in {
                FountainElementKind.CHARACTER,
                FountainElementKind.DIALOGUE,
            }:
                raise RenderingInvariantError(
                    "a Fountain parenthetical must follow character or dialogue"
                )
            if element.kind is FountainElementKind.DIALOGUE and prior_kind not in {
                FountainElementKind.CHARACTER,
                FountainElementKind.PARENTHETICAL,
                FountainElementKind.DIALOGUE,
            }:
                raise RenderingInvariantError(
                    "Fountain dialogue must follow character, parenthetical, or dialogue"
                )
            prior_kind = element.kind
