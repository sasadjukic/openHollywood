"""Deterministic context-packet compiler with fail-closed token budgets."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from open_hollywood_engine.artifacts import ArtifactKind, artifact_json_schema
from open_hollywood_engine.context.contracts import (
    AgentDependencyManifest,
    ArtifactDependencyRule,
    ContextBudgetExceededError,
    ContextDependencyError,
    ContextPacket,
    ContextPacketRequest,
    DependencyManifestRegistry,
    NearbySummary,
    OmittedContext,
    StoryBibleSection,
    TokenCounter,
    Utf8ByteTokenCounter,
    VersionedArtifact,
)

_PACKET_FORMAT = "open_hollywood_context_packet_v1"


@dataclass(frozen=True, slots=True)
class _CompilationParts:
    required_artifacts: tuple[VersionedArtifact, ...]
    optional_artifacts: tuple[VersionedArtifact, ...]
    story_bible_sections: tuple[StoryBibleSection, ...]
    required_summaries: tuple[NearbySummary, ...]
    optional_summaries: tuple[NearbySummary, ...]
    omitted_context: tuple[OmittedContext, ...]


class ContextPacketCompiler:
    """Compile only manifest-declared context into a reproducible JSON packet."""

    def __init__(
        self,
        manifests: DependencyManifestRegistry,
        token_counter: TokenCounter | None = None,
    ) -> None:
        self._manifests = manifests
        self._token_counter = token_counter or Utf8ByteTokenCounter()
        if not self._token_counter.identifier.strip():
            raise ValueError("token counter identifier must not be empty")

    def compile(self, request: ContextPacketRequest) -> ContextPacket:
        """Validate dependencies, shed optional context, and render a bounded packet."""
        manifest = self._manifests.get(request.specialist_role)
        parts = self._prepare_parts(request, manifest)
        included_artifacts = list(parts.required_artifacts)
        included_summaries = list(parts.required_summaries)
        omitted = list(parts.omitted_context)

        content = self._render(
            request,
            manifest,
            artifacts=included_artifacts,
            story_bible_sections=parts.story_bible_sections,
            summaries=included_summaries,
        )
        estimated_tokens = self._count(content)
        if estimated_tokens > request.budget.packet_tokens:
            raise ContextBudgetExceededError(
                required_tokens=estimated_tokens,
                available_tokens=request.budget.packet_tokens,
            )

        for artifact in parts.optional_artifacts:
            trial_artifacts = [*included_artifacts, artifact]
            trial_content = self._render(
                request,
                manifest,
                artifacts=trial_artifacts,
                story_bible_sections=parts.story_bible_sections,
                summaries=included_summaries,
            )
            trial_tokens = self._count(trial_content)
            if trial_tokens <= request.budget.packet_tokens:
                included_artifacts = trial_artifacts
                content = trial_content
                estimated_tokens = trial_tokens
            else:
                omitted.append(
                    OmittedContext(
                        category="artifact",
                        identifier=str(artifact.version_id),
                        reason="token_budget",
                    )
                )

        for summary in parts.optional_summaries:
            trial_summaries = sorted(
                [*included_summaries, summary],
                key=_summary_sort_key,
            )
            trial_content = self._render(
                request,
                manifest,
                artifacts=included_artifacts,
                story_bible_sections=parts.story_bible_sections,
                summaries=trial_summaries,
            )
            trial_tokens = self._count(trial_content)
            if trial_tokens <= request.budget.packet_tokens:
                included_summaries = trial_summaries
                content = trial_content
                estimated_tokens = trial_tokens
            else:
                omitted.append(
                    OmittedContext(
                        category="nearby_summary",
                        identifier=str(summary.source_artifact_version_id),
                        reason="token_budget",
                    )
                )

        input_version_ids = self._input_version_ids(
            request,
            included_artifacts,
            parts.story_bible_sections,
            included_summaries,
        )
        return ContextPacket(
            specialist_role=request.specialist_role,
            manifest_version=manifest.manifest_version,
            output_artifact_kind=manifest.output_artifact_kind,
            content=content,
            content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            estimated_tokens=estimated_tokens,
            token_counter=self._token_counter.identifier,
            budget=request.budget,
            input_artifact_version_ids=input_version_ids,
            omitted_context=tuple(omitted),
        )

    def _prepare_parts(
        self,
        request: ContextPacketRequest,
        manifest: AgentDependencyManifest,
    ) -> _CompilationParts:
        self._validate_unique_sources(request)
        required_artifacts, optional_artifacts = self._partition_artifacts(
            request.artifacts,
            manifest.artifact_dependencies,
        )
        story_bible_sections = self._select_story_bible_sections(request, manifest)
        required_summaries, optional_summaries, omitted = self._partition_summaries(
            request.nearby_summaries,
            manifest,
        )
        return _CompilationParts(
            required_artifacts=required_artifacts,
            optional_artifacts=optional_artifacts,
            story_bible_sections=story_bible_sections,
            required_summaries=required_summaries,
            optional_summaries=optional_summaries,
            omitted_context=omitted,
        )

    @staticmethod
    def _partition_artifacts(
        artifacts: tuple[VersionedArtifact, ...],
        rules: tuple[ArtifactDependencyRule, ...],
    ) -> tuple[tuple[VersionedArtifact, ...], tuple[VersionedArtifact, ...]]:
        by_kind: dict[ArtifactKind, list[VersionedArtifact]] = defaultdict(list)
        for artifact in artifacts:
            by_kind[artifact.kind].append(artifact)

        declared_kinds = {rule.kind for rule in rules}
        unexpected = {artifact.kind for artifact in artifacts} - declared_kinds
        if unexpected:
            names = sorted(kind.value for kind in unexpected)
            raise ContextDependencyError(f"undeclared artifact dependencies: {names}")

        required: list[VersionedArtifact] = []
        optional: list[VersionedArtifact] = []
        for rule in rules:
            matches = sorted(by_kind[rule.kind], key=_artifact_sort_key)
            if len(matches) < rule.minimum_count:
                raise ContextDependencyError(
                    f"{rule.kind.value} requires at least {rule.minimum_count} dependencies; "
                    f"received {len(matches)}"
                )
            if rule.maximum_count is not None and len(matches) > rule.maximum_count:
                raise ContextDependencyError(
                    f"{rule.kind.value} allows at most {rule.maximum_count} dependencies; "
                    f"received {len(matches)}"
                )
            (required if rule.required else optional).extend(matches)
        return tuple(required), tuple(optional)

    @staticmethod
    def _select_story_bible_sections(
        request: ContextPacketRequest,
        manifest: AgentDependencyManifest,
    ) -> tuple[StoryBibleSection, ...]:
        if not manifest.story_bible_sections:
            return ()
        if request.story_bible is None:
            raise ContextDependencyError("the dependency manifest requires a story bible")
        available = {section.name: section for section in request.story_bible.sections}
        missing = [name for name in manifest.story_bible_sections if name not in available]
        if missing:
            raise ContextDependencyError(f"missing story-bible sections: {missing}")
        return tuple(available[name] for name in manifest.story_bible_sections)

    @staticmethod
    def _partition_summaries(
        summaries: tuple[NearbySummary, ...],
        manifest: AgentDependencyManifest,
    ) -> tuple[
        tuple[NearbySummary, ...],
        tuple[NearbySummary, ...],
        tuple[OmittedContext, ...],
    ]:
        if manifest.maximum_nearby_summaries == 0 and summaries:
            raise ContextDependencyError("nearby summaries are not declared for this role")
        ordered = sorted(summaries, key=_summary_sort_key)
        if len(ordered) < manifest.minimum_nearby_summaries:
            raise ContextDependencyError(
                "nearby summaries require at least "
                f"{manifest.minimum_nearby_summaries}; received {len(ordered)}"
            )

        omitted: list[OmittedContext] = []
        if len(ordered) > manifest.maximum_nearby_summaries:
            excluded = ordered[: -manifest.maximum_nearby_summaries]
            ordered = ordered[-manifest.maximum_nearby_summaries :]
            omitted.extend(
                OmittedContext(
                    category="nearby_summary",
                    identifier=str(summary.source_artifact_version_id),
                    reason="manifest_limit",
                )
                for summary in excluded
            )

        required_count = manifest.minimum_nearby_summaries
        if required_count == 0:
            return (), tuple(reversed(ordered)), tuple(omitted)
        required = ordered[-required_count:]
        optional = ordered[:-required_count]
        return tuple(required), tuple(reversed(optional)), tuple(omitted)

    @staticmethod
    def _validate_unique_sources(request: ContextPacketRequest) -> None:
        artifact_keys = [artifact.artifact_key for artifact in request.artifacts]
        if len(set(artifact_keys)) != len(artifact_keys):
            raise ContextDependencyError("only one version per artifact_key may enter a packet")

        version_ids = [artifact.version_id for artifact in request.artifacts]
        version_ids.extend(
            summary.source_artifact_version_id for summary in request.nearby_summaries
        )
        if request.story_bible is not None:
            version_ids.append(request.story_bible.source_artifact_version_id)
        if len(set(version_ids)) != len(version_ids):
            raise ContextDependencyError("context source artifact version IDs must be unique")

    def _count(self, content: str) -> int:
        count = self._token_counter.count(content)
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError("token counter must return a non-negative integer")
        return count

    @staticmethod
    def _render(
        request: ContextPacketRequest,
        manifest: AgentDependencyManifest,
        *,
        artifacts: Iterable[VersionedArtifact],
        story_bible_sections: Iterable[StoryBibleSection],
        summaries: Iterable[NearbySummary],
    ) -> str:
        selected_story_bible_sections = tuple(story_bible_sections)
        story_bible: dict[str, Any] | None = None
        if selected_story_bible_sections:
            if request.story_bible is None:
                raise ContextDependencyError("selected story-bible sections require a snapshot")
            story_bible = {
                "schema_version": request.story_bible.schema_version,
                "sections": [
                    {"content": section.content, "name": section.name}
                    for section in selected_story_bible_sections
                ],
                "source_artifact_version_id": str(request.story_bible.source_artifact_version_id),
            }
        payload: dict[str, Any] = {
            "assignment": request.assignment,
            "direct_dependencies": [
                {
                    "artifact_key": artifact.artifact_key,
                    "artifact_kind": artifact.kind.value,
                    "artifact_version_id": str(artifact.version_id),
                    "content": artifact.content.model_dump(mode="json"),
                    "schema_version": artifact.schema_version,
                }
                for artifact in artifacts
            ],
            "evaluation_rubric": request.evaluation_rubric,
            "format": _PACKET_FORMAT,
            "manifest_version": manifest.manifest_version,
            "nearby_summaries": [
                {
                    "artifact_key": summary.artifact_key,
                    "artifact_version_id": str(summary.source_artifact_version_id),
                    "content": summary.content,
                    "sequence": summary.sequence,
                }
                for summary in summaries
            ],
            "output_contract": {
                "artifact_kind": manifest.output_artifact_kind.value,
                "json_schema": artifact_json_schema(manifest.output_artifact_kind),
            },
            "specialist_role": request.specialist_role,
            "story_bible": story_bible,
            "user_constraints": list(request.user_constraints),
        }
        serialized = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return f"{_PACKET_FORMAT}\n{serialized}"

    @staticmethod
    def _input_version_ids(
        request: ContextPacketRequest,
        artifacts: Iterable[VersionedArtifact],
        story_bible_sections: tuple[StoryBibleSection, ...],
        summaries: Iterable[NearbySummary],
    ) -> tuple[UUID, ...]:
        version_ids = [artifact.version_id for artifact in artifacts]
        if story_bible_sections and request.story_bible is not None:
            version_ids.append(request.story_bible.source_artifact_version_id)
        version_ids.extend(summary.source_artifact_version_id for summary in summaries)
        if len(set(version_ids)) != len(version_ids):
            raise ContextDependencyError("compiled input artifact version IDs must be unique")
        return tuple(version_ids)


def _artifact_sort_key(artifact: VersionedArtifact) -> tuple[str, str]:
    return artifact.artifact_key, str(artifact.version_id)


def _summary_sort_key(summary: NearbySummary) -> tuple[int, str, str]:
    return summary.sequence, summary.artifact_key, str(summary.source_artifact_version_id)
