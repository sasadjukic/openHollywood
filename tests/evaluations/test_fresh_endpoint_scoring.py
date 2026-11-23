"""Check the prospective decisions, including baseline ceiling and incomplete delivery."""

from __future__ import annotations

from copy import deepcopy

import pytest
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.fresh_endpoint_repeat.scoring import checked, gate
from scripts.q010_uncertainty_plan import digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet


def test_masked_judgment_binding() -> None:
    report: Audit = {
        "approval": "a" * 64,
        "origin": "observed_openai_transport",
        "ledger": "dispatched",
        "closed": True,
        "state": "bound_unassessed",
        "slots": [
            {
                "eligible": True,
                "cell": "R06-C",
                "scoring_id": "b" * 64,
                "final": {
                    "assessments": {
                        "Q021": {
                            "support": "unsupported",
                            "evidence": ["S02"],
                            "reason": "The pouch disappears behind the hood before the bell.",
                        }
                    }
                },
            }
        ],
    }
    sheet = evidence_sheet(report)
    assert "arm" not in sheet[0] and "support" not in sheet[0]
    entry = {"case": "R06", "outcome": "pass", "basis": "The endpoint is hidden at the bell."}
    form = {
        "approval_sha256": report["approval"],
        "sheet_sha256": digest(encoded(sheet)),
        "decisions": {"b" * 64: entry},
    }
    assert checked(report, encoded(form)).decisions["b" * 64].outcome == "pass"
    changes: tuple[dict[str, object], ...] = (
        {"sheet_sha256": "0" * 64},
        {"approval_sha256": "0" * 64},
        {"decisions": {}},
        {"decisions": {"b" * 64: {**entry, "case": "R02"}}},
        {"decisions": {"b" * 64: {**entry, "basis": " "}}},
    )
    for change in changes:
        with pytest.raises(EvidenceError):
            checked(report, encoded({**form, **change}))


def test_fresh_transfer_decision() -> None:
    states = dict(
        zip(
            [f"R{i:02}" for i in range(1, 9)],
            (
                "confirmed",
                "unresolved",
                "missing_source",
                "contradicted",
                "missing_source",
                "unresolved",
                "confirmed",
                "contradicted",
            ),
            strict=True,
        )
    )
    pairs = {k: {"B": (True, True), "C": (True, True)} for k in states}
    assert gate(pairs, states)["decision"] == "no_recovery_headroom"
    pairs["R02"]["B"] = (False, True)
    assert gate(pairs, states)["decision"] == "fresh_transfer_signal"
    assert not gate(pairs, states)["movement_case_recovered"]
    pairs["R06"]["B"] = (True, False)
    assert gate(pairs, states)["movement_case_recovered"]
    pairs["R01"] = {"B": (True, False), "C": (False, False)}
    assert gate(pairs, states)["decision"] == "hold"
    assert gate(pairs, states)["control_axis_losses"] == [{"case": "R01", "axis": "claim"}]
    partial = deepcopy(pairs)
    partial["R01"].pop("C")
    assert gate(partial, states)["decision"] == "inconclusive"
