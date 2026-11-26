"""Replay four one-edit explanations against the two sealed, complete drafts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from open_hollywood_engine.evaluations.review_evidence import require, text_hash

from scripts.ordinary_v61_capture import file_hash
from scripts.wading_path_be.rehearsal import FIXTURES, read

BASE = FIXTURES.parents[1] / "data/diagnostics"
READER = BASE / "scope-independent-reading-2026-11-26"
EXPECTED = FIXTURES / "scope_boundary_rehearsal_expected.json"
PAIRS = FIXTURES / "scope_boundary_rehearsal_pairs.json"
EXPECTED_SHA = "426b8952f98b46e79659a2e9330ec906063126312ce06bcc6f6b9b3cfb8028d3"
PAIRS_SHA = "faf00f94cf6c4ad6bfc9e7aacaf0ca7cdb05f3069065901948d932cc34e6393b"
AUDIT_SHA = "76a0d09279eb58c7d8017911292ebebe21eaf8fe92532c1d699ce496fbca1d7d"


def sealed(path: Path, expected: str) -> dict[str, Any]:
    require(file_hash(path) == expected, "boundary_seal_changed")
    return dict(read(path))


def edited(reason: str, edit: dict[str, Any]) -> str:
    before, after = edit["before"], edit["after"]
    require(bool(before) and before != after and reason.count(before) == 1, "ambiguous_edit")
    return reason.replace(before, after, 1)


def score(
    reason: str,
    annotations: dict[str, str],
    requirements: dict[str, list[str]],
    witnesses: dict[str, Any],
) -> dict[str, Any]:
    """Compute coverage from human-readable semantic annotations on these fixed texts."""
    require(
        all(anchor and anchor in reason for anchor in annotations.values())
        and annotations.keys() <= witnesses.keys() | {"scene_wide_denial"},
        "unbound_annotation",
    )
    overreach = annotations.get("scene_wide_denial")
    missing = {
        axis: sorted(set(needs) - annotations.keys()) for axis, needs in requirements.items()
    }
    return dict(
        explanation=reason,
        annotations=annotations,
        factual_sufficiency=int(not missing["factual"] and not overreach),
        diagnostic_completeness=int(not missing["diagnostic"] and not overreach),
        missing=missing,
        unsupported_denial=overreach,
    )


def check_scores(scored: dict[str, Any], expected: list[int]) -> None:
    require(
        [scored["factual_sufficiency"], scored["diagnostic_completeness"]] == expected,
        "boundary_score_changed",
    )


def replay() -> dict[str, Any]:
    expected, fixtures = sealed(EXPECTED, EXPECTED_SHA), sealed(PAIRS, PAIRS_SHA)
    packet = sealed(READER / "reader/packet.json", expected["packet_sha256"])
    reader = sealed(READER / "reader/sealed-reading.json", expected["reader_sha256"])
    joined = sealed(READER / "operator/comparison.json", expected["comparison_sha256"])
    audit = sealed(BASE / "sol-astra-scope-score-audit-2026-11-25/audit.json", AUDIT_SHA)
    require(
        fixtures["cases"].keys() == expected["cases"].keys()
        and fixtures["controls"].keys() == expected["controls"].keys(),
        "boundary_inventory",
    )
    for version, src in fixtures["sources"].items():
        prose = packet["sources"][version]["text"]
        require(text_hash(prose) == src["prose_sha256"], "wrong_source_version")
        for span in src["witnesses"].values():
            start, end = span["start"], span["end"]
            require(
                0 <= start < end <= len(prose) and text_hash(prose[start:end]) == span["sha256"],
                "wrong_source_span",
            )

    pairs: dict[str, Any] = {}
    for cell, item in fixtures["cases"].items():
        criterion = expected["cases"][cell]
        family, alias = criterion["family"], criterion["alias"]
        old = audit["families"][family]["rows"][cell]
        linked = joined["families"][family][cell]
        primary = reader["rows"][alias]
        require(
            alias == linked["alias"]
            and linked["reader"] == primary
            and item["scoring_id"] == linked["original_scoring_id"] == old["scoring_id"]
            and item["claim"] == linked["claim"] == old["claim"]
            and item["source_version"] == linked["source_version"] == old["source_version"],
            "wrong_saved_explanation",
        )
        source = fixtures["sources"][item["source_version"]]
        stem = f"{old['generation_slot']:02}-{cell}-generation-outcome.json"
        terminal = sealed(
            BASE / f"{family}-sol-astra-scope-2026-11-25" / "output" / stem,
            old["generation_terminal_sha256"],
        )
        (answer,) = (
            json.loads(part["text"])["assessments"]["A001"]
            for msg in json.loads(terminal["body"])["output"]
            if msg["type"] == "message"
            for part in msg["content"]
            if part["type"] == "output_text"
        )
        original = item["explanation"]
        require(
            original == answer["reason"] == linked["reason"] == old["reason"]
            and answer["evidence"] == [source["passage_ref"]] == old["cited"]
            and source["prose_sha256"] == old["prose_sha256"],
            "saved_delivery_drift",
        )
        requirements = expected["requirements"][cell.split("-")[0]]
        annotations = item["saved_annotations"]
        edit = item["revision"]
        saved = score(original, annotations, requirements, source["witnesses"])
        revised = score(
            edited(original, edit),
            annotations | edit["annotations"],
            requirements,
            source["witnesses"],
        )
        check_scores(saved, criterion["saved"])
        check_scores(saved, [int(primary[k] == "pass") for k in expected["axes"]])
        check_scores(revised, criterion["revision"])
        pairs[cell] = dict(
            source_version=item["source_version"],
            citation=source["passage_ref"],
            claim=item["claim"],
            original_returned_label=answer["support"],
            gold=old["gold"],
            generation_terminal_sha256=old["generation_terminal_sha256"],
            alternative=primary["alternative"],
            saved=saved,
            revision=revised,
        )

    controls = {}
    for name, item in fixtures["controls"].items():
        spec = expected["controls"][name]
        cell = spec["case"]
        pair = pairs[cell]
        base = pair[item["base"]]
        edit = item["edit"]
        result = score(
            edited(base["explanation"], edit),
            base["annotations"] | edit["annotations"],
            expected["requirements"][cell.split("-")[0]],
            fixtures["sources"][pair["source_version"]]["witnesses"],
        )
        check_scores(result, spec["expected"])
        controls[name] = dict(cell=cell, **result)
    return dict(
        expectations_sha256=EXPECTED_SHA,
        fixtures_sha256=PAIRS_SHA,
        pairs=pairs,
        controls=controls,
        live_calls=0,
    )


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, ensure_ascii=False))
