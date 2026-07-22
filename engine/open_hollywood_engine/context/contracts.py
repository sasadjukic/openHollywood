"""Provider-neutral contracts for deterministic, bounded agent context."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Protocol
from uuid import UUID

from open_hollywood_engine.artifacts import (
    ARTIFACT_SCHEMAS,
    SCHEMA_VERSION,
    ArtifactKind,
    ArtifactSchema,
)
from open_hollywood_engine.models.contracts import InvocationContext, ModelCallBudget

_ARTIFACT_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*$")


@dataclass(frozen=True, slots=True)
class ArtifactDependencyRule:
    """Allowed cardinality and budget behavior for one dependency kind."""

    kind: ArtifactKind
    required: bool
    minimum_count: int
    maximum_count: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.required, bool):
            raise ValueError("required must be a boolean")
        if not _is_integer(self.minimum_count) or self.minimum_count < 0:
            raise ValueError("minimum_count must be a non-negative integer")
        if self.required and self.minimum_count < 1:
            raise ValueError("required dependencies must have a positive minimum_count")
        if not self.required and self.minimum_count != 0:
            raise ValueError("budget-optional dependencies must have minimum_count zero")
        if self.maximum_count is not None:
            if not _is_integer(self.maximum_count) or self.maximum_count < 1:
                raise ValueError("maximum_count must be a positive integer")
            if self.maximum_count < self.minimum_count:
                raise ValueError("maximum_count must not be below minimum_count")


@dataclass(frozen=True, slots=True)
class AgentDependencyManifest:
    """Versioned declaration of context an exact specialist role may receive."""

    specialist_role: str
    manifest_version: str
    output_artifact_kind: ArtifactKind
    artifact_dependencies: tuple[ArtifactDependencyRule, ...] = ()
    story_bible_sections: tuple[str, ...] = ()
    minimum_nearby_summaries: int = 0
    maximum_nearby_summaries: int = 0

    def __post_init__(self) -> None:
        _require_text(self.specialist_role, "specialist_role")
        _require_text(self.manifest_version, "manifest_version")
        dependency_kinds = [rule.kind for rule in self.artifact_dependencies]
        _require_unique(dependency_kinds, "artifact dependency kinds")
        _require_unique(self.story_bible_sections, "story-bible section names")
        for section in self.story_bible_sections:
            _require_text(section, "story-bible section name")
        if not _is_integer(self.minimum_nearby_summaries) or self.minimum_nearby_summaries < 0:
            raise ValueError("minimum_nearby_summaries must be a non-negative integer")
        if not _is_integer(self.maximum_nearby_summaries) or self.maximum_nearby_summaries < 0:
            raise ValueError("maximum_nearby_summaries must be a non-negative integer")
        if self.minimum_nearby_summaries > self.maximum_nearby_summaries:
            raise ValueError("minimum_nearby_summaries must not exceed maximum_nearby_summaries")


class DependencyManifestRegistry:
    """Immutable lookup of one dependency manifest per registered specialist role."""

    def __init__(self, manifests: Iterable[AgentDependencyManifest]) -> None:
        by_role: dict[str, AgentDependencyManifest] = {}
        for manifest in manifests:
            if manifest.specialist_role in by_role:
                raise ValueError(
                    f"duplicate dependency manifest for role {manifest.specialist_role!r}"
                )
            by_role[manifest.specialist_role] = manifest
        if not by_role:
            raise ValueError("at least one dependency manifest is required")
        self._manifests: Mapping[str, AgentDependencyManifest] = MappingProxyType(by_role)

    @property
    def roles(self) -> tuple[str, ...]:
        """Return registered roles in deterministic lexical order."""
        return tuple(sorted(self._manifests))

    def get(self, specialist_role: str) -> AgentDependencyManifest:
        """Return the manifest for a registered role."""
        try:
            return self._manifests[specialist_role]
        except KeyError as exc:
            raise UnknownSpecialistRoleError(specialist_role) from exc


@dataclass(frozen=True, slots=True)
class VersionedArtifact:
    """Validated artifact content paired with its immutable persistence identity."""

    kind: ArtifactKind
    artifact_key: str
    version_id: UUID
    content: ArtifactSchema
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_artifact_key(self.artifact_key)
        _require_text(self.schema_version, "schema_version")
        expected_type = ARTIFACT_SCHEMAS[self.kind]
        if type(self.content) is not expected_type:
            raise ValueError(
                f"{self.kind.value} content must be {expected_type.__name__}, "
                f"not {type(self.content).__name__}"
            )
        if self.schema_version != self.content.schema_version:
            raise ValueError("artifact envelope and content schema versions must match")


@dataclass(frozen=True, slots=True)
class StoryBibleSection:
    """One named, already-bounded section from canonical story state."""

    name: str
    content: str

    def __post_init__(self) -> None:
        _require_text(self.name, "story-bible section name")
        _require_text(self.content, "story-bible section content")


@dataclass(frozen=True, slots=True)
class StoryBibleSnapshot:
    """Exact accepted artifact version supplying canonical story-bible sections."""

    source_artifact_version_id: UUID
    sections: tuple[StoryBibleSection, ...]
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.sections:
            raise ValueError("a story-bible snapshot requires at least one section")
        _require_unique((section.name for section in self.sections), "story-bible sections")
        _require_text(self.schema_version, "story-bible schema_version")


@dataclass(frozen=True, slots=True)
class NearbySummary:
    """Concise summary of a preceding versioned story unit."""

    source_artifact_version_id: UUID
    artifact_key: str
    sequence: int
    content: str

    def __post_init__(self) -> None:
        _require_artifact_key(self.artifact_key)
        if not _is_integer(self.sequence) or self.sequence < 1:
            raise ValueError("summary sequence must be a positive integer")
        _require_text(self.content, "summary content")


@dataclass(frozen=True, slots=True)
class ContextTokenBudget:
    """Input-token envelope available to a compiled packet."""

    max_input_tokens: int
    reserved_tokens: int = 0

    def __post_init__(self) -> None:
        if not _is_integer(self.max_input_tokens) or self.max_input_tokens < 1:
            raise ValueError("max_input_tokens must be a positive integer")
        if not _is_integer(self.reserved_tokens) or self.reserved_tokens < 0:
            raise ValueError("reserved_tokens must be a non-negative integer")
        if self.reserved_tokens >= self.max_input_tokens:
            raise ValueError("reserved_tokens must be below max_input_tokens")

    @property
    def packet_tokens(self) -> int:
        """Return tokens left after reserving system and message framing."""
        return self.max_input_tokens - self.reserved_tokens

    @classmethod
    def from_model_budget(
        cls,
        budget: ModelCallBudget,
        *,
        reserved_tokens: int = 0,
    ) -> ContextTokenBudget:
        """Create a packet envelope aligned with a model call's input limit."""
        return cls(
            max_input_tokens=budget.max_input_tokens,
            reserved_tokens=reserved_tokens,
        )


@dataclass(frozen=True, slots=True)
class ContextPacketRequest:
    """All available inputs for one deterministic context compilation."""

    specialist_role: str
    assignment: str
    evaluation_rubric: str
    budget: ContextTokenBudget
    user_constraints: tuple[str, ...] = ()
    artifacts: tuple[VersionedArtifact, ...] = ()
    story_bible: StoryBibleSnapshot | None = None
    nearby_summaries: tuple[NearbySummary, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.specialist_role, "specialist_role")
        _require_text(self.assignment, "assignment")
        _require_text(self.evaluation_rubric, "evaluation_rubric")
        for constraint in self.user_constraints:
            _require_text(constraint, "user constraint")


@dataclass(frozen=True, slots=True)
class OmittedContext:
    """Observable record of context excluded by a manifest or token budget."""

    category: str
    identifier: str
    reason: str


@dataclass(frozen=True, slots=True)
class ContextPacket:
    """Rendered, reproducible context ready for a single model request."""

    specialist_role: str
    manifest_version: str
    output_artifact_kind: ArtifactKind
    content: str
    content_sha256: str
    estimated_tokens: int
    token_counter: str
    budget: ContextTokenBudget
    input_artifact_version_ids: tuple[UUID, ...]
    omitted_context: tuple[OmittedContext, ...] = ()

    @property
    def remaining_tokens(self) -> int:
        """Return unused packet capacity, excluding the explicit reserve."""
        return self.budget.packet_tokens - self.estimated_tokens

    def invocation_context(
        self,
        *,
        prompt_template_version: str,
        model_profile_id: UUID | None = None,
    ) -> InvocationContext:
        """Create invocation lineage using exactly the versions rendered in this packet."""
        return InvocationContext(
            specialist_role=self.specialist_role,
            prompt_template_version=prompt_template_version,
            input_artifact_version_ids=self.input_artifact_version_ids,
            model_profile_id=model_profile_id,
        )


class TokenCounter(Protocol):
    """Replaceable provider/model-specific token estimator."""

    @property
    def identifier(self) -> str:
        """Return a stable algorithm and version identifier."""
        ...

    def count(self, text: str) -> int:
        """Estimate the tokens consumed by text."""
        ...


@dataclass(frozen=True, slots=True)
class Utf8ByteTokenCounter:
    """Conservative provider-neutral fallback that counts each UTF-8 byte."""

    identifier: str = field(default="utf8_bytes_v1", init=False)

    def count(self, text: str) -> int:
        """Return a deterministic upper-bound estimate for byte-tokenizing models."""
        return len(text.encode("utf-8"))


class ContextCompilationError(RuntimeError):
    """Base class for deterministic context compilation failures."""


class UnknownSpecialistRoleError(ContextCompilationError):
    """Raised when no dependency manifest exists for a requested role."""

    def __init__(self, specialist_role: str) -> None:
        super().__init__(f"no dependency manifest registered for role {specialist_role!r}")
        self.specialist_role = specialist_role


class ContextDependencyError(ContextCompilationError):
    """Raised when supplied artifacts do not satisfy the role manifest."""


class ContextBudgetExceededError(ContextCompilationError):
    """Raised when mandatory packet content cannot fit the token envelope."""

    def __init__(self, *, required_tokens: int, available_tokens: int) -> None:
        super().__init__(
            "mandatory context requires "
            f"{required_tokens} tokens but only {available_tokens} are available"
        )
        self.required_tokens = required_tokens
        self.available_tokens = available_tokens


def _require_text(value: str, label: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{label} must not be empty")


def _require_artifact_key(value: str) -> None:
    if len(value) > 150 or _ARTIFACT_KEY_PATTERN.fullmatch(value) is None:
        raise ValueError("artifact_key must be a lowercase stable identifier")


def _require_unique(values: Iterable[object], label: str) -> None:
    materialized = tuple(values)
    if len(set(materialized)) != len(materialized):
        raise ValueError(f"{label} must be unique")


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
