"""One native condition set survives every explicit generic restatement route."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Any
from uuid import uuid4

import pytest
from open_hollywood_api.services.production_model_executor import (
    _critic_retained_classifications,
    _Execution,
    _scene_boundary_audit,
    _structured_failure_issues,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_revision_acceptance import critic_repair_tests

from tests.api.test_production_v29 import _raw, _refs
from tests.api.test_production_v37 import _fixture
from tests.api.test_production_v45 import _claim
from tests.api.test_production_v58 import _materialize, _record, _wire


def _repeat(execution: _Execution, ref: str, severity: str = "major") -> dict[str, Any]:
    claim = _claim(execution, repeated=True, severity=severity)
    claim.update(assignment_finding_ref=ref, recommendation=None)
    claim["assignment_comparison"]["finding_refs"] = [ref]
    return claim


@pytest.mark.parametrize("reverse", [False, True])
def test_two_findings_many_restatements_still_yield_two_exact_writer_repairs(reverse: bool) -> None:
    execution = _fixture()
    raw = _wire(execution)
    raw["assignment_checks"]["turning_point"]["status"] = "unmet"
    raw["assignment_repair_conditions"].append(
        _record(execution, "assignment:turning_point", "Establish the assigned turn.")
    )
    raw["issues"] = [
        _repeat(execution, f"assignment:{anchor}", severity)
        for anchor in ("turning_point", "outcome")
        for severity in ("note", "minor", "major", "blocking")
    ]
    if reverse:
        raw["issues"].reverse()
        raw["assignment_repair_conditions"].reverse()
    before = deepcopy(raw)
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 2 and result["verdict"] == "revise"
    expected = {
        r["repair_ref"]: r["conditions"][0]["condition"]
        for r in raw["assignment_repair_conditions"]
    }
    for issue in result["issues"]:
        ref = issue["category"].replace("scene_assignment:", "assignment:")
        assert issue["recommendation"] == expected[ref]
        assert issue["description"].count("Restatement (") == 4
    review = {
        "artifact_kind": "critique",
        "artifact_key": "test",
        "artifact_version_id": str(uuid4()),
        "content": result,
    }
    tests = critic_repair_tests((*execution.inputs, review), execution.unit_id)
    assert len(tests) == 2
    assert {t["requested_change"] for t in tests} == set(expected.values())
    audit: Any = _scene_boundary_audit(raw, execution)
    assert len(audit["assignment_repair_conditions"]) == 2
    for row in audit["assignment_restatements"]:
        assert row["repair_condition_refs"] == [row["assignment_finding_ref"]]
        assert row["recommendation"] == expected[row["assignment_finding_ref"]]
        assert not row["includes_boundary_policy"]
    assert raw == before


@pytest.mark.parametrize("same_evidence", [False, True])
def test_boundary_aliases_reuse_validated_groups_without_guessing_equivalence(
    same_evidence: bool,
) -> None:
    execution = _fixture("She read the letter. She matched the signature.")
    raw = _wire(execution)
    raw["scene_boundary_check"].update(status="overrun", draft_evidence_refs=_refs(execution)[:1])
    raw["assignment_checks"]["outcome"]["draft_evidence_refs"] = (
        _refs(execution)[:1] if same_evidence else _refs(execution)[1:2]
    )
    raw["issues"] = [_repeat(execution, ref) for ref in ("boundary", "assignment:outcome")]
    result = _materialize(raw, execution)
    assert len(result["issues"]) == (1 if same_evidence else 2)
    advice = " ".join(i["recommendation"] for i in result["issues"])
    assert advice.count("Establish her decision to verify.") == 1
    assert advice.count("remove unassigned material advancement") == 1
    audit: Any = _scene_boundary_audit(raw, execution)
    boundary, native = audit["assignment_restatements"]
    assert boundary["repair_condition_refs"] == (["assignment:outcome"] if same_evidence else [])
    assert boundary["includes_boundary_policy"]
    assert native["repair_condition_refs"] == ["assignment:outcome"]
    assert native["includes_boundary_policy"] == same_evidence
    if same_evidence:
        assert (
            boundary["recommendation"]
            == native["recommendation"]
            == result["issues"][0]["recommendation"]
        )


@pytest.mark.parametrize("ref", ["viewpoint", "assignment:scene_id"])
def test_other_native_finding_reuses_its_single_set(ref: str) -> None:
    execution = _fixture()
    raw = _wire(execution, unmet=False)
    if ref == "viewpoint":
        raw["point_of_view_check"] = _raw(execution, "pov")["point_of_view_check"]
        raw["point_of_view_check"]["recommended_resolution"] = None
    else:
        raw["assignment_violations"] = [
            {
                "anchor": "scene_id",
                "explanation": "Wrong scene.",
                "draft_evidence_refs": _refs(execution)[:1],
                "recommended_resolution": None,
            }
        ]
    raw["assignment_repair_conditions"] = [_record(execution, ref, "Restore the assigned fact.")]
    raw["issues"] = [_repeat(execution, ref)]
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 1
    assert result["issues"][0]["recommendation"] == "Restore the assigned fact."


@pytest.mark.parametrize(
    "bad",
    [
        "extra_copy",
        "missing_owner",
        "met_owner",
        "absent",
        "unknown",
        "object",
        "free_advice",
        "missing_null",
    ],
)
def test_restatement_cannot_create_or_override_its_owner(bad: str) -> None:
    execution = _fixture()
    raw = _wire(execution)
    raw["issues"] = [_repeat(execution, "assignment:outcome")]
    issue = raw["issues"][0]
    if bad == "extra_copy":
        raw["assignment_repair_conditions"].append(
            _record(execution, "issue:0", "New mandatory demand.")
        )
    elif bad == "missing_owner":
        raw["assignment_repair_conditions"] = []
    elif bad == "met_owner":
        raw["assignment_checks"]["outcome"]["status"] = "met"
        raw["assignment_repair_conditions"] = []
    elif bad in ("absent", "unknown", "object"):
        issue["assignment_finding_ref"] = {
            "absent": "boundary",
            "unknown": "assignment:stale",
            "object": {"ref": "assignment:outcome"},
        }[bad]
    elif bad == "free_advice":
        issue["recommendation"] = "New demand outside the owner."
    else:
        issue.pop("recommendation")
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


def test_independent_craft_with_same_evidence_remains_a_separate_repair() -> None:
    execution = _fixture()
    raw = _wire(execution)
    raw["issues"] = [
        _repeat(execution, "assignment:outcome"),
        _claim(execution, severity="blocking"),
    ]
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 2
    craft = next(i for i in result["issues"] if i["category"] == "Plot Pacing")
    assert craft["recommendation"] == raw["issues"][1]["recommendation"]


def test_valid_shared_classification_survives_comparison_repair_and_invalid_later_link() -> None:
    execution = _fixture()
    raw = _wire(execution)
    raw["issues"] = [_repeat(execution, "assignment:outcome")]
    valid = deepcopy(raw)
    raw["issues"][0]["assignment_comparison"] = "bad"
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    retry = replace(
        execution,
        attempt_number=2,
        previous_failure={
            "error_code": "schema_validation_failed",
            "validation_issues": list(_structured_failure_issues(failure.value)),
        },
    )
    retained = _critic_retained_classifications(retry)
    assert retained and retained[0]["assignment_finding_refs"] == ["assignment:outcome"]
    assert _materialize(valid, retry) == _materialize(valid, execution)
    valid["issues"][0]["assignment_finding_ref"] = "boundary"
    with pytest.raises(_StructuredOutputContractError) as later:
        _materialize(valid, retry)
    again = replace(
        retry,
        previous_failure={
            "error_code": "schema_validation_failed",
            "validation_issues": list(_structured_failure_issues(later.value)),
        },
    )
    assert _critic_retained_classifications(again) == retained
