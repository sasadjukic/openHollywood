"""Operator-only grading contract, frozen with the requests."""

from typing import Literal

from open_hollywood_engine.evaluations.review_evidence import Digest, Record

Grade = Literal["pass", "fail"]


class Reading(Record):
    case: Literal["SE", "XE", "VE"]
    factual_sufficiency: Grade
    diagnostic_completeness: Grade
    reason_excerpt: str
    draft_excerpt: str
    factual_basis: str
    diagnostic_basis: str
    false_denial_excerpt: str | None


class Decisions(Record):
    approval_sha256: Digest
    sheet_sha256: Digest
    decisions: dict[str, Reading]


CRITERIA = {
    "SE": {
        "factual": "Explain that the joint stop and remaining short establish the closing "
        "position, leaving an earlier joint visit unresolved. Mere absence of a narrated "
        "arrival cannot exclude the event.",
        "diagnostic": "Also locate the plenum entry, the sightline to the housing and the "
        "joint measured stop and stay. Explain the limit for the earlier interval.",
    },
    "XE": {
        "factual": "Ground exclusion of a joint visit in the retrospective observation that "
        "neither person ever came closer than three strides throughout the scene.",
        "diagnostic": "Locate the sweep from the initial huddle through the last moment in "
        "the plenum and distinguish this whole-scene witness from the closing distance.",
    },
    "VE": {
        "factual": "Ground the any-time claim in the retrospective account of both people "
        "reaching the housing together earlier.",
        "diagnostic": "Locate the joint arrival after entry and before the light steadied, "
        "their return up the passage and the compatible later stop.",
    },
}
RULES = {
    "judgment": "One point for the exact returned whole-claim label against frozen gold.",
    "factual_sufficiency": "Grade the reason and its citations on their own. Award one point "
    "for a source-supported answer to the whole claim without overreach.",
    "diagnostic_completeness": "Award one point for a factually sufficient explanation that "
    "also locates all case-specific observations. Equivalent locators and faithful paraphrases "
    "count. Naming an interval alone does not locate what the passage shows.",
    "false_denial": "Independently mark an actual assertion that the pair never reached the "
    "housing during the scene where that denial is unwarranted (SE or VE). Quote it. A wrong "
    "label alone, a denial confined to narration or the closing interval, or the warranted "
    "whole-scene denial on XE does not trigger this flag.",
    "mask": "Seal grades, source/answer excerpts, rationales and denial annotations for every "
    "eligible explanation before joining labels. Hide model, presentation, returned label, "
    "repeat and dispatch order. Explanations may themselves reveal the conclusion.",
    "threshold": "Astra X requires at least 3/4 fresh SE answers correct on judgment and "
    "factual sufficiency jointly, at least two more than each other arm, and all three "
    "points on each Astra X control. Other arms' control scores are reported separately. "
    "Any missing eligible generation makes the comparison inconclusive. A qualifying repeat "
    "supports only a held-out production-length family. Keep B as default.",
}
