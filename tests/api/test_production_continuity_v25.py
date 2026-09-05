"""Offline negative and positive controls for the v24 continuity regressions."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import pytest
from open_hollywood_api.services.production_model_executor import (
    _consolidate_continuity_semantic_duplicates,
    _continuity_canonical_source_catalog,
    _continuity_entity_identity_context,
    _continuity_model_findings,
    _ContinuitySchemaVariant,
    _downgrade_qualitative_non_world_contradiction,
    _materialize_continuity_finding,
    _materialize_continuity_identity,
    _materialize_non_world_source_refs,
    _messages,
    _Operation,
    _output_schema,
    _strip_continuity_certification_fields,
    _StructuredOutputContractError,
)
from open_hollywood_engine.artifacts import ArtifactKind, ContinuityFinding

from tests.evaluations.test_agentic_production import (
    _schema_test_continuity_context,
    _v17_catalog_test_execution,
)

FIXTURES = json.loads(
    (Path(__file__).parents[1] / "fixtures" / "production_v24_regressions.json").read_text(
        encoding="utf-8"
    )
)


def test_catalog_preserves_atomic_facts_but_not_names_as_unrelated_authority() -> None:
    catalog = _continuity_canonical_source_catalog(
        (
            {
                "artifact_kind": ArtifactKind.STORY_BLUEPRINT.value,
                "artifact_key": "blueprint",
                "artifact_version_id": str(uuid4()),
                "content": {
                    "characters": [
                        {
                            "id": "elara",
                            "name": "Elara Vance",
                            "initial_knowledge": ["The card arrived yesterday."],
                        }
                    ],
                    "relationships": [{"id": "echo", "label": "Temporal Echo/Self-Confrontation"}],
                    "locations": [
                        {
                            "id": "plateau",
                            "name": "The Overgrown Plateau",
                            "constraints": ["The only entrance faces north."],
                        }
                    ],
                },
            },
        )
    )
    claims = {entry["claim"] for entry in catalog}
    assert claims == {"The card arrived yesterday.", "The only entrance faces north."}
    assert all("claim_id" in entry for entry in catalog)


def test_story_bible_objects_are_not_single_immutable_emotional_claims() -> None:
    catalog = _continuity_canonical_source_catalog(
        (
            {
                "artifact_kind": ArtifactKind.STORY_BIBLE.value,
                "artifact_key": "story_bible",
                "artifact_version_id": str(uuid4()),
                "content": {
                    "timeline": [
                        {
                            "id": "event_1",
                            "scene_id": "scene_1",
                            "sequence": 1,
                            "time_context": "Yesterday",
                            "summary": "Elias yielded the floor.",
                        }
                    ],
                    "character_states": [
                        {
                            "character_id": "elias",
                            "physical_state": "Broken wrist",
                            "emotional_state": "Defeated",
                            "current_goal": "Win the debate",
                        }
                    ],
                },
            },
        )
    )
    assert {entry["claim"] for entry in catalog} == {
        "Yesterday",
        "Elias yielded the floor.",
        "Broken wrist",
    }
    assert len({entry["claim_id"] for entry in catalog}) == 3
    assert all(
        "past_event_only" in entry["scope"]
        for entry in catalog
        if ".timeline" in entry["source_path"]
    )


def test_atomic_state_keeps_known_facts_and_last_location() -> None:
    catalog = _continuity_canonical_source_catalog(
        (
            {
                "artifact_kind": ArtifactKind.STORY_BIBLE.value,
                "artifact_key": "bible",
                "artifact_version_id": str(uuid4()),
                "content": {
                    "character_states": [
                        {
                            "character_id": "elara",
                            "current_location_id": "locked_cell",
                            "knowledge_fact_ids": ["secret_code"],
                            "physical_state": "Injured",
                        }
                    ]
                },
            },
        )
    )
    assert any(
        "locked_cell" in item["claim"] and item["categories"] == ["location"] for item in catalog
    )
    assert any(
        "secret_code" in item["claim"] and item["categories"] == ["character_knowledge"]
        for item in catalog
    )


def test_names_remain_available_in_nonselectable_identity_context() -> None:
    execution = _v17_catalog_test_execution(
        scene_plan={"character_ids": ["elara"], "location_id": "tower"}
    )
    blueprint = {
        "artifact_kind": "story_blueprint",
        "artifact_key": "blueprint",
        "artifact_version_id": str(uuid4()),
        "content": {
            "characters": [{"id": "elara", "name": "Elara Vance"}],
            "locations": [{"id": "tower", "name": "Blackwood Tower"}],
        },
    }
    identities = _continuity_entity_identity_context(
        replace(execution, inputs=(*execution.inputs, blueprint))
    )
    assert {item["name"] for item in identities} == {"Elara Vance", "Blackwood Tower"}
    assert all("identity_only" in cast(str, item["authority"]) for item in identities)
    assert all("claim_id" not in item for item in identities)


def test_additive_repair_wording_does_not_release_a_real_contradiction() -> None:
    finding = {
        "category": "character",
        "severity": "blocking",
        "basis": "contradiction",
        "summary": "A character established to have one arm lifts both hands.",
        "repair_assessment": "The second hand still contradicts the established physical state.",
        "recommended_resolution": "Add an established prosthesis before the two-handed action.",
        "_prior_finding_recheck": True,
    }
    assert _downgrade_qualitative_non_world_contradiction(finding) == finding


def test_different_allegations_on_one_source_do_not_merge() -> None:
    context = _schema_test_continuity_context()
    source = context.canonical_claim_ids[0]
    original = {
        "severity": "blocking",
        "basis": "contradiction",
        "canonical_claim_ids": [source],
        "summary": "Elara's dismissive reaction conflicts with the prior scene.",
    }
    different = {**original, "summary": "A photograph was not introduced before this scene."}
    first = cast(dict[str, Any], _materialize_continuity_identity(original, context, index=0))
    second = cast(dict[str, Any], _materialize_continuity_identity(different, context, index=1))
    assert first["id"] != second["id"]
    assert len(_consolidate_continuity_semantic_duplicates([first, second], context)) == 2
    duplicate = {
        **original,
        "summary": "  ELARA'S dismissive reaction conflicts with the prior scene. ",
    }
    assert len(_consolidate_continuity_semantic_duplicates([original, duplicate], context)) == 1


@pytest.mark.parametrize("index", [3, 4])
def test_qualitative_prior_recheck_can_explicitly_become_advisory(index: int) -> None:
    frozen = FIXTURES["continuity"][index]
    base = _schema_test_continuity_context(recheck=True)
    prior = {
        "id": "original",
        "category": frozen["canonical_category"],
        "severity": "blocking",
        "basis": "contradiction",
        "summary": frozen["summary"],
        "recommended_resolution": frozen["recommended_resolution"],
    }
    context = replace(
        base,
        previous_continuity_report={"content": {"findings": [prior]}},
        candidate_draft={
            "content": {
                "evidence_catalog": [
                    {
                        "evidence_ref": "draft_evidence_0001",
                        "exact_excerpt": frozen["recheck_evidence"],
                    }
                ]
            }
        },
    )
    findings = cast(
        list[dict[str, Any]],
        _continuity_model_findings(
            {
                "prior_finding_rechecks": {
                    "original": {
                        "status": "advisory",
                        "resolution_assessment": frozen["recheck_summary"],
                        "revised_draft_evidence_refs": ["draft_evidence_0001"],
                    }
                },
                "new_findings": [],
            },
            context,
        ),
    )
    advisory = findings[0]
    assert advisory["severity"] == "warning"
    assert frozen["recheck_summary"] in advisory["summary"]
    assert advisory.get("recommended_resolution") is None
    assert "repair_assessment" not in advisory
    persisted = _materialize_continuity_finding({**advisory, "id": "advisory_1"}, "scene_1")
    parsed = ContinuityFinding.model_validate(_strip_continuity_certification_fields(persisted))
    assert not parsed.blocks_approval


@pytest.mark.parametrize("recheck", [False, True])
def test_craft_keywords_cannot_override_a_genuine_direct_conflict(recheck: bool) -> None:
    finding = {
        "category": "fact",
        "severity": "blocking",
        "basis": "contradiction",
        "summary": "Mara is alive despite the established fact that Mara died.",
        "evidence": ["Mara was alive."],
        "conflict_disposition": "directly_incompatible",
        "conflict_explanation": (
            "The explicit assertion that Mara is alive contradicts her established death; "
            "changing emotional resonance cannot repair this."
        ),
        "recommended_resolution": "Correct the incompatible assertion.",
        "_prior_finding_recheck": recheck,
    }
    assert _downgrade_qualitative_non_world_contradiction(finding) == finding


@pytest.mark.parametrize(
    "disposition",
    [
        "craft_preference",
        "compatible_development",
        "insufficient_canonical_support",
    ],
)
def test_explicit_nonconflict_disposition_controls_initial_routing(disposition: str) -> None:
    finding = {
        "category": "timeline",
        "severity": "blocking",
        "basis": "contradiction",
        "summary": "The event is a compatible continuation.",
        "conflict_disposition": disposition,
    }
    advisory = cast(dict[str, Any], _downgrade_qualitative_non_world_contradiction(finding))
    assert advisory["severity"] == "warning"
    assert advisory["basis"] is None


@pytest.mark.parametrize("status", ["resolved", "invalidated", "advisory", "still_blocking"])
def test_every_recheck_status_requires_real_current_evidence(status: str) -> None:
    base = _schema_test_continuity_context(recheck=True)
    context = replace(
        base,
        previous_continuity_report={
            "content": {
                "findings": [
                    {
                        "id": "original",
                        "severity": "blocking",
                        "basis": "contradiction",
                        "category": "fact",
                    }
                ]
            }
        },
    )
    with pytest.raises(_StructuredOutputContractError, match="evidence references"):
        _continuity_model_findings(
            {
                "prior_finding_rechecks": {
                    "original": {
                        "status": status,
                        "resolution_assessment": "Unsupported original allegation.",
                        "repair_assessment": "The same contradiction remains.",
                        "revised_draft_evidence_refs": ["draft_evidence_9999"],
                    }
                },
                "new_findings": [],
            },
            context,
        )


@pytest.mark.parametrize("index", [3, 4])
def test_false_prior_claim_can_be_retracted_without_rewriting_prose(index: int) -> None:
    frozen = FIXTURES["continuity"][index]
    base = _schema_test_continuity_context(recheck=True)
    candidate = {
        **base.candidate_draft,
        "content": {
            "evidence_catalog": [
                {"evidence_ref": "draft_evidence_0001", "exact_excerpt": frozen["draft_evidence"]}
            ],
        },
    }
    context = replace(
        base,
        candidate_draft=candidate,
        previous_continuity_report={
            "content": {
                "findings": [
                    {
                        "id": "original",
                        "severity": "blocking",
                        "basis": "contradiction",
                        "category": frozen["canonical_category"],
                        "summary": frozen["summary"],
                        "related_scene_ids": ["scene_1"],
                    }
                ]
            }
        },
    )
    findings = cast(
        list[dict[str, Any]],
        _continuity_model_findings(
            {
                "prior_finding_rechecks": {
                    "original": {
                        "status": "invalidated",
                        "resolution_assessment": frozen["expected"],
                        "revised_draft_evidence_refs": ["draft_evidence_0001"],
                    }
                },
                "new_findings": [],
            },
            context,
        ),
    )
    assert len(findings) == 1
    assert findings[0]["severity"] == "warning"
    assert "invalidated prior finding original" in findings[0]["summary"]


def test_true_nonworld_contradiction_still_retains_grounded_source_and_identity() -> None:
    base = _schema_test_continuity_context(recheck=True)
    source_ref = base.canonical_claim_source_refs[base.canonical_claim_ids[0]]
    context = replace(
        base,
        previous_continuity_report={
            "content": {
                "findings": [
                    {
                        "id": "original",
                        "severity": "blocking",
                        "basis": "contradiction",
                        "category": "fact",
                        "summary": "The key action contradicts the established fact.",
                        "canonical_source_refs": [source_ref],
                        "recommended_resolution": "Correct the key action.",
                    }
                ]
            }
        },
    )
    findings = cast(
        list[dict[str, Any]],
        _continuity_model_findings(
            {
                "prior_finding_rechecks": {
                    "original": {
                        "status": "still_blocking",
                        "repair_assessment": "The same key action remains incompatible.",
                        "revised_draft_evidence_refs": ["draft_evidence_0001"],
                        "recommended_resolution": (
                            "Restore the explicitly established ownership of the key."
                        ),
                    }
                },
                "new_findings": [],
            },
            context,
        ),
    )
    grounded = _materialize_non_world_source_refs(findings[0], context)
    identified = cast(dict[str, Any], _materialize_continuity_identity(grounded, context, index=0))
    assert identified["id"] == "original"
    assert identified["recheck_disposition"] == "still_blocking"
    assert identified["canonical_source_refs"] == [source_ref]
    assert (
        identified["recommended_resolution"]
        == "Restore the explicitly established ownership of the key."
    )


def test_recheck_instructions_are_delivered_and_schema_stays_compact() -> None:
    context = _schema_test_continuity_context(recheck=True)
    schema = _output_schema(
        _Operation.CONTINUITY,
        continuity_schema_variant=_ContinuitySchemaVariant.RECHECK,
        continuity_model_context=context,
    )
    messages = _messages(
        _Operation.CONTINUITY,
        _v17_catalog_test_execution(),
        schema,
        continuity_schema_variant=_ContinuitySchemaVariant.RECHECK,
        continuity_model_context=context,
    )
    assert "SAME original incompatible assertion" in messages[0].content
    assert "invalidated" in messages[0].content
    assert "counterevidence" in messages[0].content
    payload = json.loads(messages[1].content)
    assert "scene_assignment_contract" in payload
    statuses = schema["$defs"]["PriorFindingRecheckEntry"]["anyOf"][0]["properties"]["status"][
        "enum"
    ]
    assert statuses == ["resolved", "invalidated", "advisory"]
    assert len(json.dumps(schema, separators=(",", ":")).encode()) < 8_000
