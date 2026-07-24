"""Provider-neutral Local, Cloud, and Hybrid preset tests."""

import pytest
from open_hollywood_engine.models import (
    BLUEPRINT_SPECIALIST_ROLES,
    DIALOGUE_SPECIALIST_ROLES,
    MODEL_PRESETS,
    MODEL_PROFILE_SCHEMA_VERSION,
    PRODUCTION_SPECIALIST_ROLES,
    REGISTERED_SPECIALIST_ROLES,
    ModelDeployment,
    ModelProfileConfiguration,
    ModelProfileMode,
    ModelSelection,
)


def _selection(
    deployment: ModelDeployment,
    identifier: str,
) -> ModelSelection:
    return ModelSelection(
        provider="ollama",
        model_identifier=identifier,
        deployment=deployment,
    )


def test_presets_assign_every_registered_specialist_role() -> None:
    for preset in MODEL_PRESETS.values():
        assert set(preset.role_assignments) == set(REGISTERED_SPECIALIST_ROLES)


def test_local_and_cloud_presets_route_every_role_to_one_model() -> None:
    local_model = _selection(ModelDeployment.LOCAL, "qwen3:8b")
    cloud_model = _selection(ModelDeployment.CLOUD, "creative-cloud")
    local = MODEL_PRESETS[ModelProfileMode.LOCAL].configuration(local_model=local_model)
    cloud = MODEL_PRESETS[ModelProfileMode.CLOUD].configuration(cloud_model=cloud_model)

    assert all(local.selection_for(role) == local_model for role in BLUEPRINT_SPECIALIST_ROLES)
    assert all(cloud.selection_for(role) == cloud_model for role in BLUEPRINT_SPECIALIST_ROLES)
    assert all(local.selection_for(role) == local_model for role in DIALOGUE_SPECIALIST_ROLES)
    assert all(cloud.selection_for(role) == cloud_model for role in DIALOGUE_SPECIALIST_ROLES)
    assert all(local.selection_for(role) == local_model for role in PRODUCTION_SPECIALIST_ROLES)
    assert all(cloud.selection_for(role) == cloud_model for role in PRODUCTION_SPECIALIST_ROLES)


def test_hybrid_routes_structured_preparation_and_evaluation_locally() -> None:
    local_model = _selection(ModelDeployment.LOCAL, "qwen3:8b")
    cloud_model = _selection(ModelDeployment.CLOUD, "creative-cloud")
    hybrid = MODEL_PRESETS[ModelProfileMode.HYBRID].configuration(
        local_model=local_model,
        cloud_model=cloud_model,
    )

    assert hybrid.selection_for("brief_architect") == local_model
    assert hybrid.selection_for("blueprint_critic") == local_model
    assert hybrid.selection_for("character_architect") == cloud_model
    assert hybrid.selection_for("blueprint_integrator") == cloud_model
    assert hybrid.selection_for("character_actor") == cloud_model
    assert hybrid.selection_for("dialogue_director") == cloud_model
    assert hybrid.selection_for("scene_writer") == cloud_model
    assert hybrid.selection_for("scene_critic") == local_model
    assert hybrid.selection_for("continuity_supervisor") == local_model
    assert hybrid.selection_for("story_bible_maintainer") == local_model


def test_configuration_round_trips_through_secret_free_json() -> None:
    configured = MODEL_PRESETS[ModelProfileMode.HYBRID].configuration(
        local_model=_selection(ModelDeployment.LOCAL, "qwen3:8b"),
        cloud_model=_selection(ModelDeployment.CLOUD, "creative-cloud"),
    )

    restored = ModelProfileConfiguration.from_data(configured.to_data())

    assert restored == configured
    assert restored.is_complete
    assert "api_key" not in str(restored.to_data())


def test_incomplete_and_mismatched_model_slots_fail_closed() -> None:
    incomplete = MODEL_PRESETS[ModelProfileMode.HYBRID].configuration()
    assert not incomplete.is_complete
    with pytest.raises(LookupError, match="local model is not configured"):
        incomplete.selection_for("brief_architect")

    with pytest.raises(ValueError, match="local model slot"):
        MODEL_PRESETS[ModelProfileMode.LOCAL].configuration(
            local_model=_selection(ModelDeployment.CLOUD, "creative-cloud")
        )


def test_initial_profile_data_upgrades_for_all_later_roles() -> None:
    legacy = (
        MODEL_PRESETS[ModelProfileMode.HYBRID]
        .configuration(
            local_model=_selection(ModelDeployment.LOCAL, "qwen3:8b"),
            cloud_model=_selection(ModelDeployment.CLOUD, "creative-cloud"),
        )
        .to_data()
    )
    legacy["schema_version"] = "1"
    legacy["role_assignments"] = {
        role: legacy["role_assignments"][role] for role in BLUEPRINT_SPECIALIST_ROLES
    }

    restored = ModelProfileConfiguration.from_data(legacy)

    assert restored.schema_version == MODEL_PROFILE_SCHEMA_VERSION
    assert restored.selection_for("character_actor").model_identifier == "creative-cloud"
    assert restored.selection_for("scene_writer").model_identifier == "creative-cloud"


def test_step_fourteen_profile_data_upgrades_for_production_roles() -> None:
    legacy = (
        MODEL_PRESETS[ModelProfileMode.HYBRID]
        .configuration(
            local_model=_selection(ModelDeployment.LOCAL, "qwen3:8b"),
            cloud_model=_selection(ModelDeployment.CLOUD, "creative-cloud"),
        )
        .to_data()
    )
    legacy["schema_version"] = "2"
    legacy["role_assignments"] = {
        role: legacy["role_assignments"][role]
        for role in (*BLUEPRINT_SPECIALIST_ROLES, *DIALOGUE_SPECIALIST_ROLES)
    }

    restored = ModelProfileConfiguration.from_data(legacy)

    assert restored.schema_version == MODEL_PROFILE_SCHEMA_VERSION
    assert restored.selection_for("scene_writer").model_identifier == "creative-cloud"
    assert restored.selection_for("scene_critic").model_identifier == "qwen3:8b"
    assert restored.selection_for("continuity_supervisor").model_identifier == "qwen3:8b"


def test_step_fifteen_profile_data_upgrades_for_continuity_roles() -> None:
    legacy = (
        MODEL_PRESETS[ModelProfileMode.HYBRID]
        .configuration(
            local_model=_selection(ModelDeployment.LOCAL, "qwen3:8b"),
            cloud_model=_selection(ModelDeployment.CLOUD, "creative-cloud"),
        )
        .to_data()
    )
    legacy["schema_version"] = "3"
    legacy["role_assignments"] = {
        role: legacy["role_assignments"][role]
        for role in (
            *BLUEPRINT_SPECIALIST_ROLES,
            *DIALOGUE_SPECIALIST_ROLES,
            "scene_writer",
            "scene_critic",
        )
    }

    restored = ModelProfileConfiguration.from_data(legacy)

    assert restored.schema_version == MODEL_PROFILE_SCHEMA_VERSION
    assert restored.selection_for("continuity_supervisor").model_identifier == "qwen3:8b"
    assert restored.selection_for("story_bible_maintainer").model_identifier == "qwen3:8b"
