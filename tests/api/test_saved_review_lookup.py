"""Portable mixed-selection regressions at the authenticated publisher boundary."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from uuid import uuid4

import pytest
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services.assessment_consumer_projection import Usage
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import compile_intake
from open_hollywood_engine.evaluations.assessment_result import (
    BoundAssessmentResult,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentReceipt
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, text_hash

from scripts import lookup_q008_completion as legacy
from scripts import lookup_saved_review_completion as shared
from scripts import publish_saved_review_completion as publisher
from tests.api.test_q008_publisher import snapshot
from tests.assessment_intake_fixtures import authored_source, choice_for, plan_for


@dataclass
class Bundle:
    review: ArtifactSelection
    draft: ArtifactSelection
    files: dict[str, bytes]
    bound: BoundAssessmentResult


@pytest.fixture
def bundles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Bundle]:
    sources = {}
    for registration, field, tokens in ((shared.Q008, "Q001", 10), (shared.Q013, "Q002", 20)):
        case = registration.case
        review = ArtifactSelection(
            role="original_review",
            project_id=str(uuid4()),
            artifact_id=str(uuid4()),
            version_id=str(uuid4()),
            content_sha256="a" * 64,
        )
        draft = review.model_copy(
            update={
                "role": "reviewed_draft",
                "artifact_id": str(uuid4()),
                "version_id": str(uuid4()),
            }
        )
        source = authored_source()
        work = compile_intake(source, plan_for(source, choice_for(source, field))).pending_work
        assert work is not None
        scope = scope_for_batch(work, work.batches[0].batch_id, text_hash(case))
        (unit,) = scope.active_unit_ids
        raw = encoded(
            {
                "assessments": {
                    unit: {"support": "uncertain", "evidence": [], "reason": "Authored fixture."}
                }
            }
        ).decode()
        receipt = AssessmentReceipt(
            work_sha256=scope.work_sha256,
            batch_id=scope.batch_id,
            request_sha256=scope.request_sha256,
            attempt_id=case + "-fixture",
            status="valid",
            result_sha256=text_hash(raw),
            assessed_unit_ids=(unit,),
            input_tokens=tokens,
            output_tokens=4,
            reasoning_tokens=2,
            active_seconds=1.0,
        )
        bound = bind_assessment_result(work, scope, receipt, raw)
        selectors = [s.model_dump(mode="json") for s in (review, draft)]
        delivery = {
            "observed_request_selection": selectors[0],
            "generation_model": "fixture",
            "counted_input_tokens": tokens,
            "actual_billed_cost": None,
            "usage": {
                "input_tokens": tokens,
                "output_tokens": 4,
                "reasoning_tokens": 2,
                "cached_input_tokens": 1,
            },
            "semantic_support": "unassessed",
            "evidence_adequacy": "unassessed",
            "edit_necessity": "unassessed",
            "craft": "unassessed",
            "production_attachment_eligible": False,
            "writer_dispatch_authorized": False,
        }
        labels = (
            ("whole_claim_label", "plan_evidence", "draft_ending_evidence")
            if case == "q008"
            else ("claim_correctness", "evidence_coverage")
        )
        files = {
            "delivery.json": encoded(delivery),
            "operator-score.json": encoded(
                {
                    "scoring_origin": "fixture operator",
                    "passed_judgments": len(labels),
                    "possible_judgments": len(labels),
                    **{k: {"score": "pass"} for k in labels},
                }
            ),
            "stop.json": encoded({"fixture_closed": True}),
        }
        files["manifest.json"] = encoded(
            {
                "lookup_selections": selectors,
                "delivery_id": receipt.attempt_id,
                "files_sha256": {k: storage._sha(v) for k, v in files.items()},
            }
        )
        folder = tmp_path / case
        folder.mkdir()
        for name, raw_bytes in files.items():
            (folder / name).write_bytes(raw_bytes)
        registration = replace(
            registration,
            directory=folder,
            manifest_sha256=storage._sha(files["manifest.json"]),
            selector_sha256=(
                storage._sha(encoded(selectors[0])),
                storage._sha(encoded(selectors[1])),
            ),
        )
        monkeypatch.setattr(shared, case.upper(), registration)
        sources[case] = Bundle(review, draft, files, bound)

    def collect(
        case: str, selected: ArtifactSelection
    ) -> tuple[dict[str, bytes], BoundAssessmentResult]:
        bundle = sources[case]
        assert selected == bundle.review
        return bundle.files, bundle.bound

    monkeypatch.setattr(publisher, "collect_observed", collect)
    monkeypatch.setattr(legacy, "PUBLICATION", shared.Q008.directory)
    monkeypatch.setattr(legacy, "MANIFEST_SHA", shared.Q008.manifest_sha256)
    return sources


def test_mixed_lookup_and_original_command(
    bundles: dict[str, Bundle], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    q008, q013 = bundles["q008"], bundles["q013"]
    selections = (q013.draft, q008.review, q013.review, q008.draft, q013.draft, q008.review)
    args: list[str] = []
    for i, s in enumerate(selections):
        path = tmp_path / f"selection-{i}.json"
        path.write_text(s.model_dump_json(), encoding="utf-8")
        args.extend(("--selection", str(path)))
    assert shared.main(args) == 0
    result = shared.Inventory.model_validate_json(capsys.readouterr().out)
    assert tuple(row.selection for row in result.lookups) == selections
    assert [row.delivery_id for row in result.lookups] == [
        "q013-fixture",
        "q008-fixture",
        "q013-fixture",
        "q008-fixture",
        "q013-fixture",
        "q008-fixture",
    ]
    assert [v.request_selection for v in result.accounting_records] == [q008.review, q013.review]
    assert (
        [v.delivery_id for v in result.assessments]
        == [v.delivery_id for v in result.accounting_records]
        == ["q008-fixture", "q013-fixture"]
    )
    assert result.generation_totals == Usage(
        input_tokens=30, output_tokens=8, reasoning_tokens=4, cached_input_tokens=2
    )
    assert result.assessments[0].operator_score["possible_judgments"] == 3
    assert result.assessments[1].operator_score["possible_judgments"] == 2
    assert result.assessments[1].operator_score["evidence_coverage"] == {"score": "pass"}
    reversed_view = shared.lookup(selections[::-1])
    assert reversed_view.lookups == result.lookups[::-1]
    assert (
        reversed_view.assessments == result.assessments
        and reversed_view.accounting_records == result.accounting_records
    )
    assert legacy.main(args) == 0
    old = legacy.Inventory.model_validate_json(capsys.readouterr().out)
    assert (
        old.assessments == result.assessments[:1]
        and old.accounting_records == result.accounting_records[:1]
    )
    assert all(
        row.status == ("available" if row.selection in (q008.review, q008.draft) else "unavailable")
        for row in old.lookups
    )


@pytest.mark.parametrize("role", ["review", "draft"])
def test_last_exact_selection_and_same_text_neighbor(bundles: dict[str, Bundle], role: str) -> None:
    q008, q013 = bundles["q008"], bundles["q013"]
    exact = q013.review if role == "review" else q013.draft
    other = q013.draft if role == "review" else q013.review
    adjacent = exact.model_copy(update={"version_id": str(uuid4())})
    healthy = shared.lookup((q008.draft, exact))
    kept = shared.lookup((adjacent, q008.draft, other, adjacent))
    assert (
        kept.assessments == healthy.assessments
        and kept.accounting_records == healthy.accounting_records
    )
    assert [row.status for row in kept.lookups] == [
        "unavailable",
        "available",
        "available",
        "unavailable",
    ]
    changed = shared.lookup((adjacent, q008.draft, adjacent))
    assert (
        changed.assessments == healthy.assessments[:1]
        and changed.accounting_records == healthy.accounting_records[:1]
    )
    assert changed.generation_totals == healthy.accounting_records[0].generation_usage
    assert (
        changed.lookups[0].reason == "exact_selection_unavailable"
        and changed.lookups[0] == changed.lookups[-1]
    )
    assert changed.lookups[0].delivery_id is None and changed.lookups[0].claim_id is None
    assert shared.lookup((adjacent,)).generation_totals is None
    assert shared.lookup((q008.draft, exact)) == healthy


@pytest.mark.parametrize(
    ("fault", "reason"),
    [
        ("usage", "publication_member_changed"),
        ("score", "publication_member_changed"),
        ("resealed", "publication_manifest_changed"),
        ("closure", "publication_incomplete"),
        ("absent", "publication_missing"),
        ("source", "publication_unavailable"),
    ],
)
def test_refresh_isolates_fault_and_recovers(
    bundles: dict[str, Bundle], fault: str, reason: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    q008, q013 = bundles["q008"], bundles["q013"]
    selections = (q013.draft, q008.review, q013.review, q008.draft, q013.draft)
    healthy = shared.lookup(selections)
    folder = shared.Q013.directory
    if fault == "absent":
        folder.rename(folder.with_suffix(".held"))
    elif fault == "closure":
        (folder / "stop.json").unlink()
    elif fault == "score":
        (folder / "operator-score.json").write_bytes(b"{}")
    elif fault in ("usage", "resealed"):
        value = json.loads(q013.files["delivery.json"])
        value["usage"]["input_tokens"] += 1
        altered = encoded(value)
        (folder / "delivery.json").write_bytes(altered)
        if fault == "resealed":
            manifest = json.loads(q013.files["manifest.json"])
            manifest["files_sha256"]["delivery.json"] = storage._sha(altered)
            (folder / "manifest.json").write_bytes(encoded(manifest))
    collect = publisher.collect_observed

    def recheck(
        case: str, selection: ArtifactSelection
    ) -> tuple[dict[str, bytes], BoundAssessmentResult]:
        if fault == "source" and case == "q013":
            raise EvidenceError("private score details")
        return collect(case, selection)

    with monkeypatch.context() as m:
        m.setattr(publisher, "collect_observed", recheck)
        state = snapshot(folder) if folder.exists() else None
        refreshed = shared.lookup(selections)
        assert [r.reason for r in refreshed.lookups] == [reason, None, reason, None, reason]
        assert all(
            r.delivery_id is None and r.claim_id is None for r in refreshed.lookups if r.reason
        )
        assert (
            refreshed.assessments == healthy.assessments[:1]
            and refreshed.accounting_records == healthy.accounting_records[:1]
        )
        assert refreshed.generation_totals == healthy.accounting_records[0].generation_usage
        only = shared.lookup((q013.review, q013.draft))
        assert (
            not only.assessments and not only.accounting_records and only.generation_totals is None
        )
        assert state == (snapshot(folder) if folder.exists() else None)
    if fault == "absent":
        folder.with_suffix(".held").rename(folder)
    else:
        for name, data in q013.files.items():
            (folder / name).write_bytes(data)
    assert shared.lookup(selections) == healthy
