"""Only independent craft findings can own links to original craft repairs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

CRAFT_LINK_RULE = (
    "Only an independent craft issue (assignment_finding_ref=null) may select repair_test_id, "
    "and only when it repeats that exact original craft claim with identical category and "
    "severity and its repair check is unmet. Explain equivalence in that check's assessment. "
    "Omit repair_test_id or use null for a new defect or any assignment repetition. "
    "A consolidated complaint cannot be a separate historical craft link. Never emit issue:N "
    "in repair_checks.current_finding_refs: craft checks always use [], including when unmet. "
    "An unmet original remains actionable without any current link. Do not rename a claim, "
    "change severity or reclassify a repetition to create a link."
)


def eligible_craft_repairs(
    issue: Mapping[str, Any], tests: Sequence[Mapping[str, Any]]
) -> list[str]:
    if "assignment_finding_ref" not in issue or issue["assignment_finding_ref"] is not None:
        return []
    return [
        test["test_id"]
        for test in tests
        if not test["category"].startswith("scene_assignment:")
        and (test["category"], test["severity"]) == (issue.get("category"), issue.get("severity"))
    ]


def bind_craft_repair_schema(schema: dict[str, Any], tests: Sequence[Mapping[str, Any]]) -> None:
    """Constrain non-null links on the same object as the classification choice."""
    schema["properties"]["repair_test_id"] = {
        "type": ["string", "null"],
        "default": None,
        "description": CRAFT_LINK_RULE,
    }
    groups: dict[tuple[str, str], list[str]] = {}
    for test in tests:
        if not test["category"].startswith("scene_assignment:"):
            groups.setdefault((test["category"], test["severity"]), []).append(test["test_id"])
    schema["anyOf"] = [
        {"properties": {"repair_test_id": {"type": "null"}}},
        *[
            {
                "required": ["repair_test_id"],
                "properties": {
                    "category": {"const": category},
                    "severity": {"const": severity},
                    "assignment_finding_ref": {"type": "null"},
                    "repair_test_id": {"type": "string", "enum": ids},
                },
            }
            for (category, severity), ids in groups.items()
        ],
    ]


class CraftRepairLinkError(ValueError):
    def __init__(self, location: str, message: str) -> None:
        super().__init__(message)
        self.location = location


def project_craft_repair_links(
    raw: dict[str, Any], tests: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Translate explicit ownership to internal routes; never clear invalid wire links."""
    checks = raw.get("repair_checks")
    known = {test["test_id"]: test for test in tests}
    if isinstance(checks, dict):
        for test_id, check in checks.items():
            if not isinstance(check, dict):
                continue  # Normal repair coverage/shape validation reports this.
            refs = check.get("current_finding_refs")
            craft = test_id in known and not known[test_id]["category"].startswith(
                "scene_assignment:"
            )
            if (craft and refs != []) or (
                isinstance(refs, list)
                and any(isinstance(ref, str) and ref.startswith("issue:") for ref in refs)
            ):
                raise CraftRepairLinkError(
                    f"repair_checks.{test_id}.current_finding_refs",
                    CRAFT_LINK_RULE,
                )
    result = deepcopy(raw)
    issues = result.get("issues")
    if not isinstance(issues, list):
        return result
    for index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            continue
        target = issue.pop("repair_test_id", None)
        if target is None:
            continue
        if not isinstance(target, str) or target not in eligible_craft_repairs(issue, tests):
            raise CraftRepairLinkError(f"issues.{index}.repair_test_id", CRAFT_LINK_RULE)
        check = checks.get(target) if isinstance(checks, dict) else None
        if not isinstance(check, dict) or check.get("status") != "unmet":
            raise CraftRepairLinkError(
                f"issues.{index}.repair_test_id",
                "A craft link requires its original repair check to be unmet.",
            )
        # This raw issue index is application-owned and never a model-selectable route.
        # The existing normalization validates the issue, evidence, claim category and
        # severity before it can replace a carried original repair.
        result["repair_checks"][target]["current_finding_refs"].append(f"issue:{index}")
    return result
