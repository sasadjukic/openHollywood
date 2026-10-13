"""One authored source for assignment repairs; citations do not establish entailment."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

MAX_REPAIRS = 70
MAX_CONDITIONS = 8
MAX_REPAIR_CHARS = 600
REPAIR_CONDITION_RULE = (
    "Author mandatory assignment advice only in assignment_repair_conditions. "
    "Set recommended_resolution=null in every assignment check, assignment violation and "
    "viewpoint violation. For each generic issue with non-null assignment_finding_ref, set "
    "recommendation=null too, at every severity. Independent craft keeps its ordinary "
    "recommendation and no condition record. The application renders assignment advice from "
    "your conditions. Return one record per "
    "unmet check or assignment violation (repair_ref=assignment:<anchor>) or viewpoint violation "
    "(viewpoint). A linked generic issue reuses its finding's conditions: never add an "
    "issue:<index> "
    "record. Put every mandatory condition, including any raised by repeated criticism, in that "
    "one native set. Use [] when none. "
    "Each record has repair_ref and conditions (1-8); each condition has condition (one required "
    "repair/end-state condition), source_refs (1-3 objects with source_ref and exact_quote copied "
    "from repair_source_catalog), and support_assessment explaining why that source requires "
    "this condition here. Separate required facts, order, immediacy, cause, motivation and "
    "completion. The application joins condition strings with one space, in their listed order, "
    "without paraphrasing or adding advice; keep the joined text within 600 characters per set. "
    "Assess source applicability and support, including permissions/exceptions: valid citations "
    "prove traceability only. Repair the assigned minimum; preserve fulfilled facts. Unassigned "
    "preferences stay outside mandatory conditions in the existing optional-craft route. "
    "No conditions for met checks, independent craft, application-written boundary policy or "
    "immutable historical advice. Boundary restatements reuse the existing application policy "
    "and any consolidated native conditions; extra assigned repairs belong in a native finding. "
    "Never cite draft/reviewer prose as authority. Malformed conditions are review "
    "errors, not story defects."
)


def condition_obligation_rule(rule: str) -> str:
    """Change only the wire-field wording, preserving the complete v55 meaning of met."""
    old = (
        "draft_evidence_refs, and recommended_resolution (null when met; a targeted 1-600 "
        "character repair when unmet)."
    )
    assert old in rule
    return rule.replace(
        old,
        "draft_evidence_refs, and recommended_resolution=null. An unmet check needs its "
        "mandatory advice in assignment_repair_conditions, rendered by the application.",
        1,
    )


class RepairConditionError(ValueError):
    def __init__(self, location: str, message: str) -> None:
        super().__init__(message)
        self.location = location


def repair_source_catalog(
    inputs: Sequence[Mapping[str, Any]], scoped: Sequence[Mapping[str, Any]]
) -> list[dict[str, str]]:
    """Resolve visible source strings to original version/path, before context filtering."""
    selected = {str(item["artifact_version_id"]): item for item in scoped}
    sources: list[dict[str, str]] = []

    def walk(value: object, shown: object, path: str, artifact: Mapping[str, Any]) -> None:
        if isinstance(value, dict) and isinstance(shown, dict):
            for key, child in value.items():
                if artifact["artifact_kind"] != "scene_plan" and (
                    key == "id" or key.endswith("_id") or key.endswith("_ids")
                ):
                    continue
                if key in shown:
                    escaped = key.replace("~", "~0").replace("/", "~1")
                    walk(child, shown[key], f"{path}/{escaped}", artifact)
        elif isinstance(value, list) and isinstance(shown, list):
            for index, child in enumerate(value):
                match = next(
                    (
                        item
                        for item in shown
                        if item == child
                        or (
                            isinstance(item, dict)
                            and isinstance(child, dict)
                            and item.get("id") is not None
                            and item.get("id") == child.get("id")
                        )
                    ),
                    None,
                )
                if match is not None:
                    walk(child, match, f"{path}/{index}", artifact)
        elif isinstance(value, str) and value.strip() and value == shown:
            identity = json.dumps(
                [artifact["artifact_version_id"], path, value], ensure_ascii=False
            )
            sources.append(
                {
                    "source_ref": "repair_source_"
                    + hashlib.sha256(identity.encode()).hexdigest()[:24],
                    "artifact_kind": str(artifact["artifact_kind"]),
                    "artifact_version_id": str(artifact["artifact_version_id"]),
                    "source_path": path,
                    "text": value,
                }
            )

    fields = {
        "scene_plan": (
            "id",
            "point_of_view_character_id",
            "character_ids",
            "location_id",
            "turning_point",
            "outcome",
            "exit_state",
            "continuity_requirements",
        ),
        "story_blueprint": (
            "voice_and_style_guide",
            "world_rules",
            "characters",
            "locations",
            "relationships",
        ),
        "story_bible": (
            "established_facts",
            "prohibited_contradictions",
            "character_states",
            "relationship_states",
            "location_states",
            "timeline",
            "threads",
        ),
    }
    for artifact in inputs:
        kind = artifact.get("artifact_kind")
        shown = selected.get(str(artifact.get("artifact_version_id")))
        if kind not in fields or shown is None:
            continue
        original, visible = artifact.get("content"), shown.get("content")
        if isinstance(original, dict) and isinstance(visible, dict):
            for field in fields[kind]:
                if field in original and field in visible:
                    walk(original[field], visible[field], f"/content/{field}", artifact)
    return sources


def repair_conditions_schema(source_refs: Sequence[str] | None = None) -> dict[str, Any]:
    text = {"type": "string", "minLength": 1, "maxLength": MAX_REPAIR_CHARS}
    citation = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "source_ref": {
                "type": "string",
                **({"enum": list(source_refs)} if source_refs else {}),
            },
            "exact_quote": text,
        },
        "required": ["source_ref", "exact_quote"],
    }
    condition = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "condition": text,
            "source_refs": {"type": "array", "minItems": 1, "maxItems": 3, "items": citation},
            "support_assessment": text,
        },
        "required": ["condition", "source_refs", "support_assessment"],
    }
    return {
        "type": "array",
        "maxItems": MAX_REPAIRS,
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "repair_ref": {"type": "string", "minLength": 1, "maxLength": 80},
                "conditions": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": MAX_CONDITIONS,
                    "items": condition,
                },
            },
            "required": ["repair_ref", "conditions"],
        },
    }


def bind_condition_advice_schema(schema: dict[str, Any]) -> None:
    """Constrain only model-authored assignment advice; canonical schema stays unchanged."""
    props = schema["properties"]
    for check in props["assignment_checks"]["properties"].values():
        for variant in check["anyOf"]:
            variant["properties"]["recommended_resolution"] = {"type": "null"}
    violations = props["assignment_violations"].get("items")
    if violations:
        violations["properties"]["recommended_resolution"] = {"type": "null"}
    for check in props["point_of_view_check"].get("anyOf", []):
        if "recommended_resolution" in check["properties"]:
            check["properties"]["recommended_resolution"] = {"type": "null"}
    issue = schema["$defs"]["CritiqueIssue"]
    issue["properties"]["recommendation"] = {
        "anyOf": [{"type": "null"}, {"type": "string", "minLength": 1}],
        "description": "null for assignment restatements; text only for independent craft",
    }
    issue.setdefault("allOf", []).append(
        {
            "if": {
                "properties": {"assignment_finding_ref": {"type": "null"}},
                "required": ["assignment_finding_ref"],
            },
            "then": {"properties": {"recommendation": {"type": "string", "minLength": 1}}},
            "else": {"properties": {"recommendation": {"type": "null"}}},
        }
    )


def _repair_slots(raw: dict[str, Any]) -> dict[str, tuple[dict[str, Any], str]]:
    slots: dict[str, tuple[dict[str, Any], str]] = {}
    checks = raw.get("assignment_checks")
    if isinstance(checks, dict):
        for anchor, check in checks.items():
            if isinstance(check, dict) and check.get("status") == "unmet":
                slots[f"assignment:{anchor}"] = check, "recommended_resolution"
    violations = raw.get("assignment_violations")
    if isinstance(violations, list):
        for item in violations:
            if isinstance(item, dict):
                ref = f"assignment:{item.get('anchor')}"
                if ref in slots:
                    raise RepairConditionError("assignment_violations", "do not repeat an anchor")
                slots[ref] = item, "recommended_resolution"
    viewpoint = raw.get("point_of_view_check")
    if isinstance(viewpoint, dict) and viewpoint.get("status") == "violation":
        slots["viewpoint"] = viewpoint, "recommended_resolution"
    return slots


def render_assignment_repairs(
    raw: dict[str, Any], sources: Sequence[Mapping[str, str]]
) -> dict[str, Any]:
    """Strictly validate then render into a copy. Never certify or rewrite semantic support."""
    result = deepcopy(raw)
    location = "assignment_repair_conditions"
    records = result.pop(location, None)
    slots = _repair_slots(result)
    catalog = {source["source_ref"]: source for source in sources}

    def fail(path: str, message: str) -> None:
        raise RepairConditionError(path, message)

    def text(value: object, path: str) -> str:
        if not isinstance(value, str) or not value.strip() or len(value) > MAX_REPAIR_CHARS:
            fail(path, "use 1-600 nonblank characters")
        assert isinstance(value, str)
        return value

    if not isinstance(records, list) or len(records) > MAX_REPAIRS:
        fail(location, "provide the required bounded array, including [] when none")
    assert isinstance(records, list)
    # A second advice channel is invalid even if its text happens to match rendering.
    for ref, (slot, field) in slots.items():
        if field not in slot or slot[field] is not None:
            fail(location, f"set {ref}.{field}=null; conditions are the only authored advice")
    issues = result.get("issues")
    if isinstance(issues, list):
        for index, issue in enumerate(issues):
            if (
                isinstance(issue, dict)
                and issue.get("assignment_finding_ref") is not None
                and ("recommendation" not in issue or issue["recommendation"] is not None)
            ):
                fail(location, f"set issue:{index}.recommendation=null; reuse the finding")
    seen: set[str] = set()
    for index, entry in enumerate(records):
        path = f"{location}.{index}"
        if not isinstance(entry, dict) or set(entry) != {"repair_ref", "conditions"}:
            fail(path, "provide exactly repair_ref and conditions")
        ref = entry["repair_ref"]
        if not isinstance(ref, str) or ref not in slots or ref in seen:
            fail(f"{path}.repair_ref", "select each current model-written assignment repair once")
        seen.add(ref)
        conditions = entry["conditions"]
        if not isinstance(conditions, list) or not 1 <= len(conditions) <= MAX_CONDITIONS:
            fail(f"{path}.conditions", "provide 1-8 separately supported mandatory conditions")
        fragments = []
        for ci, condition in enumerate(conditions):
            cp = f"{path}.conditions.{ci}"
            if not isinstance(condition, dict) or set(condition) != {
                "condition",
                "source_refs",
                "support_assessment",
            }:
                fail(cp, "provide exactly condition, source_refs and support_assessment")
            fragments.append(text(condition["condition"], f"{cp}.condition"))
            text(condition["support_assessment"], f"{cp}.support_assessment")
            citations = condition["source_refs"]
            if not isinstance(citations, list) or not 1 <= len(citations) <= 3:
                fail(f"{cp}.source_refs", "cite 1-3 exact current source passages")
            cited: set[tuple[str, str]] = set()
            for si, citation in enumerate(citations):
                sp = f"{cp}.source_refs.{si}"
                if not isinstance(citation, dict) or set(citation) != {"source_ref", "exact_quote"}:
                    fail(sp, "provide exactly source_ref and exact_quote")
                source_ref = citation["source_ref"]
                if not isinstance(source_ref, str) or source_ref not in catalog:
                    fail(
                        f"{sp}.source_ref", "select a source from the current repair_source_catalog"
                    )
                quote = text(citation["exact_quote"], f"{sp}.exact_quote")
                if quote not in catalog[source_ref]["text"]:
                    fail(f"{sp}.exact_quote", "copy a contiguous exact passage from the source")
                if (source_ref, quote) in cited:
                    fail(sp, "do not repeat the same source passage within a condition")
                cited.add((source_ref, quote))
        advice = " ".join(fragments)
        if len(advice) > MAX_REPAIR_CHARS:
            fail(f"{path}.conditions", "joined conditions must fit 600 characters; never truncate")
        slot, field = slots[ref]
        slot[field] = advice
    if seen != set(slots):
        fail(location, "cover all native assignment repairs; omit restatements, met and craft")
    return result
