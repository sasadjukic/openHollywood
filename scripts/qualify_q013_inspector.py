"""Exercise both Q013 selections and failure controls through loopback HTTP and the inspector."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from uuid import UUID
from xml.etree import ElementTree

import httpx
from open_hollywood_api.app import LOCAL_WEB_ORIGINS, create_q013_readonly_app
from open_hollywood_api.readonly_workspace import serve_loopback
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import q013_inspector as api
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_api.services.review_evidence_export import readonly_connection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts import lookup_saved_review_completion as consumer
from scripts.qualify_q008_inspector import _details

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/diagnostics/q013-inspector-api-2026-11-22"


def _neighbor(database: Path, selected: ArtifactSelection) -> ArtifactSelection:
    with readonly_connection(database) as conn:
        row = conn.execute(
            "SELECT id,content_sha256 FROM artifact_versions "
            "WHERE artifact_id=? AND version_number=2",
            (UUID(selected.artifact_id).hex,),
        ).fetchone()
    require(row is not None, "adjacent_version_missing")
    return selected.model_copy(update={"version_id": str(UUID(row[0])), "content_sha256": row[1]})


def _read(client: httpx.Client, base: str, selected: ArtifactSelection) -> api.Q013InspectorView:
    response = client.get(
        f"{base}/api/v1/artifact-versions/{selected.version_id}/q013-assessment",
        params=selected.model_dump(exclude={"version_id"}),
    )
    response.raise_for_status()
    require(
        response.headers.get("cache-control") == "no-store"
        and response.headers.get("access-control-allow-origin") == LOCAL_WEB_ORIGINS[0],
        "inspector_response_headers",
    )
    view = api.Q013InspectorView.model_validate_json(response.content)
    (row,) = view.lookups
    require(row.selection == selected, "inspector_response_selection")
    return view


def _empty(view: api.Q013InspectorView, reason: str) -> None:
    (row,) = view.lookups
    require(
        row.status == "unavailable"
        and row.reason == reason
        and row.delivery_id is None
        and row.claim_id is None
        and not view.assessments
        and not view.accounting_records
        and view.generation_totals is None,
        "unavailable_with_display",
    )


def _inspector(scratch: Path, registered: str, copied: str) -> int:
    web = ROOT / "apps/web"
    report = scratch / "inspector.xml"
    completed = subprocess.run(
        [
            "node",
            str(web / "node_modules/vitest/vitest.mjs"),
            "run",
            "src/components/Q013Assessment.test.tsx",
            "--reporter=junit",
            f"--outputFile={report}",
        ],
        cwd=web,
        env={
            **os.environ,
            "VITE_API_URL": registered,
            "OH_Q013_COPY_URL": copied,
            "OH_Q013_INSPECTOR_SCRATCH": scratch.name,
        },
        check=False,
        timeout=360,
    )
    shutil.copyfile(report, OUTPUT / "inspector.xml")
    completed.check_returncode()
    tests = ElementTree.parse(report).findall(".//testcase")
    require(
        len(tests) == 4
        and all(all(c.tag not in {"error", "failure", "skipped"} for c in test) for test in tests),
        "missing_mounted_inspector_checks",
    )
    return len(tests)


def qualify() -> None:
    review, draft = api._registered_pair()
    database = api.REGISTERED.path
    publication = consumer.Q013.directory

    def stamps() -> dict[Path, tuple[str, int]]:
        return {
            p: (storage._sha(p.read_bytes()), p.stat().st_mtime_ns)
            for p in (*api.SOURCE.rglob("*"), *publication.iterdir())
            if p.is_file()
        }

    before = stamps()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="replay-", dir=OUTPUT) as tmp:
        scratch = Path(tmp)
        copy = scratch / "identical.db"
        shutil.copyfile(database, copy)
        require(
            not copy.samefile(database) and copy.read_bytes() == database.read_bytes(),
            "identical_workspace_control",
        )
        adjacent_review, adjacent_draft = (_neighbor(copy, s) for s in (review, draft))
        selections = {
            "review": review,
            "draft": draft,
            "adjacent": adjacent_draft,
            "adjacentReview": adjacent_review,
        }
        details = _details(copy, selections)
        require(
            [d.selected_version.version_number for d in details.values()] == [3, 1, 2, 2],
            "incorrect_version_numbers",
        )
        fixture = scratch / "publication"
        shutil.copytree(publication, fixture)
        with (
            serve_loopback(create_q013_readonly_app(database, consumer.lookup)) as registered,
            serve_loopback(create_q013_readonly_app(copy, consumer.lookup)) as copied,
            httpx.Client(
                timeout=60, trust_env=False, headers={"Origin": LOCAL_WEB_ORIGINS[0]}
            ) as client,
        ):
            first, second = (_read(client, registered, s) for s in (review, draft))
            (assessment,), (account,) = first.assessments, first.accounting_records
            require(
                first.lookups[0].status == second.lookups[0].status == "available"
                and first.assessments == second.assessments
                and first.accounting_records == second.accounting_records
                and first.generation_totals == second.generation_totals == account.generation_usage
                and account.request_selection == review
                and assessment.claim_id == "Q013"
                and assessment.model_assessment.support == "supported"
                and list(assessment.model_assessment.evidence) == ["E0920"]
                and assessment.operator_score.model_dump()
                == {"claim_correctness": "pass", "evidence_coverage": "pass"}
                and account.preflight_input_count == 62835
                and account.generation_usage.model_dump()
                == {
                    "input_tokens": 62835,
                    "output_tokens": 427,
                    "reasoning_tokens": 255,
                    "cached_input_tokens": 0,
                },
                "unexpected_registered_delivery",
            )
            for s in (adjacent_review, adjacent_draft):
                _empty(_read(client, registered, s), "exact_selection_unavailable")
            for s in (review, draft):
                _empty(_read(client, copied, s), "unregistered_workspace")
            (scratch / "cases.json").write_bytes(
                encoded(
                    {
                        "project": review.project_id,
                        "details": {k: v.model_dump(mode="json") for k, v in details.items()},
                        "expected": first.model_dump(mode="json"),
                    }
                )
            )
            with patch.object(consumer, "Q013", replace(consumer.Q013, directory=fixture)):
                count = _inspector(scratch, registered, copied)
                for s, expected in ((review, first), (draft, second)):
                    require(_read(client, registered, s) == expected, "copied_delivery_recovery")
            for s, expected in ((review, first), (draft, second)):
                require(_read(client, registered, s) == expected, "original_delivery_changed")
    require(before == stamps() and set(database.parent.iterdir()) == {database}, "source_changed")
    summary = {
        "exact_versions": {k: v.version_id for k, v in selections.items()},
        "delivery": account.delivery_id,
        "preflight_input_count": account.preflight_input_count,
        "generation_usage": account.generation_usage.model_dump(),
        "operator_scores": assessment.operator_score.model_dump(),
        "assessment_evidence": ["E0920"],
        "identical_copy": "unregistered_workspace",
        "adjacent_versions": "exact_selection_unavailable",
        "damaged_refresh": "publication_member_changed",
        "restored_delivery_verified": True,
        "mounted_inspector_tests": count,
        "preserved_files": len(before),
        "provider_calls": 0,
    }
    (OUTPUT / "verification.json").write_bytes(encoded(summary))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    qualify()
