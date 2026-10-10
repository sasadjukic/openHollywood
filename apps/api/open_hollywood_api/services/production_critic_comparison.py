"""Wire-only comparison of craft claims with current assignment findings."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

COMPARISON_RULE = (
    "Compare the underlying defective state and required repair, not category, severity or "
    "shared quotations. With assignment_finding_ref=null, explain the distinct evidence-backed "
    "craft problem that remains after minimally correcting the reported assignment defects. "
    "An automatic consequence of the same breach is not a separate defect. With a non-null "
    "ref, explain why this is the same defect and repair; any severity may declare a repetition. "
    "Split mixed criticism: link the repeated part and retain only the distinct craft part. "
    "If there are no current assignment findings, say so and use finding_refs=[]."
)


def assignment_comparison_schema(allowed_refs: Sequence[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "finding_refs": {
                "type": "array",
                "maxItems": 8 if allowed_refs else 0,
                "uniqueItems": True,
                "items": {
                    "type": "string",
                    **({"enum": list(allowed_refs)} if allowed_refs else {}),
                },
                "description": "Select only findings actually reported in this response. For "
                "independent craft cover every distinct assignment finding (one alias of each "
                "consolidated finding suffices). For a repetition include its selected target.",
            },
            "assessment": {"type": "string", "minLength": 1, "maxLength": 1000},
        },
        "required": ["finding_refs", "assessment"],
        "description": COMPARISON_RULE,
    }


def comparison_error(
    value: object, *, restatement_ref: object, finding_groups: Sequence[Sequence[str]]
) -> str | None:
    """Validate coverage and shape, never infer the truth of the semantic judgment."""
    if (
        not isinstance(value, dict)
        or set(value) != {"finding_refs", "assessment"}
        or not isinstance(value.get("assessment"), str)
        or not value["assessment"].strip()
        or len(value["assessment"]) > 1000
    ):
        return "return finding_refs and a nonblank comparison assessment of at most 1000 characters"
    refs = value.get("finding_refs")
    reported = {ref for group in finding_groups for ref in group}
    if (
        not isinstance(refs, list)
        or len(refs) > 8
        or any(not isinstance(ref, str) or ref not in reported for ref in refs)
        or len(set(refs)) != len(refs)
    ):
        return "select up to 8 distinct references to current reported assignment findings only"
    if restatement_ref is not None:
        if restatement_ref not in refs:
            return "include the exact selected restatement target in the comparison"
    elif any(not set(refs).intersection(group) for group in finding_groups):
        return (
            "compare independent craft with every reported assignment finding; "
            "one alias per consolidated finding suffices"
        )
    return None


def assignment_finding_groups(findings: Sequence[Mapping[str, Any]]) -> list[list[str]]:
    return [
        list(finding["_current_finding_refs"])
        for finding in findings
        if str(finding.get("category", "")).startswith("scene_assignment:")
    ]
