"""Prepare private inspector replay inputs using the normal workspace reader and Q008 lookup."""

from __future__ import annotations

import shutil
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from uuid import NAMESPACE_URL, UUID, uuid5

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_api.services.review_evidence_export import readonly_connection
from open_hollywood_api.services.workspace import WorkspaceStore
from open_hollywood_api.workspace_models import ArtifactVersionDetail
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import require, strict_object
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from scripts import lookup_q008_completion as consumer

OUTPUT = consumer.PUBLICATION.parents[1] / "q008-inspector-2026-11-21"


def _add_successor(database: Path, draft: ArtifactSelection) -> ArtifactSelection:
    child_id = uuid5(NAMESPACE_URL, "openHollywood/q008/rehearsal/same-text-v2")
    child = draft.model_copy(update={"version_id": str(child_id)})
    with closing(sqlite3.connect(database)) as db, db:
        db.execute("PRAGMA foreign_keys=ON")
        saved._verify_selection(db, draft)
        db.execute(
            "INSERT INTO artifact_versions (id,artifact_id,parent_version_id,version_number,"
            "schema_version,content,content_sha256,change_summary,created_at) "
            "SELECT ?,artifact_id,id,version_number+1,schema_version,content,content_sha256,"
            "'Same-text inspector fixture',created_at FROM artifact_versions WHERE id=?",
            (child_id.hex, UUID(draft.version_id).hex),
        )
        saved._verify_selection(db, child)
    return child


def _details(
    database: Path, selections: dict[str, ArtifactSelection]
) -> dict[str, ArtifactVersionDetail]:
    result = {}
    with readonly_connection(database) as raw:
        engine = create_engine("sqlite+pysqlite://", creator=lambda: raw, poolclass=StaticPool)
        try:
            with engine.connect() as conn, conn.begin():
                if not raw.in_transaction:
                    conn.exec_driver_sql("BEGIN")
                store = WorkspaceStore(sessionmaker(bind=conn))
                for key, s in selections.items():
                    saved._verify_selection(raw, s)
                    workspace = store.get_project_workspace(UUID(s.project_id))
                    record = store.get_artifact_version(UUID(s.version_id))
                    require(record.artifact in workspace.artifacts, "inspector_wrong_workspace")
                    detail = ArtifactVersionDetail.from_record(record)
                    require(
                        str(detail.selected_version.id) == s.version_id
                        and str(detail.artifact.id) == s.artifact_id
                        and detail.selected_version in detail.artifact.versions
                        and detail.content_sha256
                        == canonical_sha256(detail.content)
                        == s.content_sha256,
                        "inspector_version_mismatch",
                    )
                    result[key] = detail
        finally:
            engine.dispose()
    return result


def prepare() -> Path:
    archive = saved.CAPTURED_Q008.archive
    database = archive / "source/database/open_hollywood.db"
    selectors = [archive.parent / f"{role}.json" for role in ("original_review", "reviewed_draft")]
    review, draft = [ArtifactSelection.model_validate_json(p.read_bytes()) for p in selectors]
    originals = [database, *selectors, *consumer.PUBLICATION.iterdir()]
    stamps = {p: (storage._sha(p.read_bytes()), p.stat().st_mtime_ns) for p in originals}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=OUTPUT) as tmp:
        workspace = Path(tmp) / "workspace.db"
        sealed = saved._open(saved.CAPTURED_Q008.name, allow_capture=True)
        sealed.inventory("database", {"open_hollywood.db"})
        workspace.write_bytes(sealed.read("database/open_hollywood.db", database=True))
        adjacent = _add_successor(workspace, draft)
        selections = {"review": review, "draft": draft, "adjacent": adjacent}
        details = _details(workspace, selections)
        require(
            details["adjacent"].selected_version.parent_version_id == UUID(draft.version_id)
            and details["adjacent"].content == details["draft"].content,
            "inspector_fixture_lineage",
        )
        copy = Path(tmp) / "publication"
        shutil.copytree(consumer.PUBLICATION, copy)
        with patch.object(consumer, "PUBLICATION", copy):
            views = {key: consumer.lookup((s,)) for key, s in selections.items()}
            pair = consumer.lookup((review, draft, review))
            require(
                all(row.status == "available" for row in pair.lookups)
                and len(pair.assessments) == len(pair.accounting_records) == 1
                and all(
                    views[k].assessments == pair.assessments
                    and views[k].accounting_records == pair.accounting_records
                    and views[k].generation_totals == pair.generation_totals
                    for k in ("review", "draft")
                )
                and views["adjacent"].lookups[0].reason == "exact_selection_unavailable",
                "inspector_inventory_binding",
            )
            member = copy / "delivery.json"
            delivery = strict_object(member.read_text(encoding="utf-8"))
            usage = delivery["usage"]
            assert isinstance(usage, dict) and isinstance(usage["input_tokens"], int)
            usage["input_tokens"] += 1
            member.write_bytes(encoded(delivery))
            views["damaged"] = consumer.lookup((draft,))
            for key in ("adjacent", "damaged"):
                invalid = views[key]
                require(
                    not invalid.assessments
                    and not invalid.accounting_records
                    and invalid.generation_totals is None,
                    "inspector_unavailable_data",
                )
            require(
                views["damaged"].lookups[0].reason == "publication_member_changed",
                "inspector_damage_control",
            )
    require(
        all(
            (storage._sha(p.read_bytes()), p.stat().st_mtime_ns) == stamp
            for p, stamp in stamps.items()
        ),
        "inspector_source_changed",
    )
    packet = encoded(
        {
            "project": review.project_id,
            "details": {k: v.model_dump(mode="json") for k, v in details.items()},
            "views": {k: v.model_dump(mode="json") for k, v in views.items()},
        }
    )
    output = OUTPUT / "inspector-replay.json"
    if output.exists():
        require(output.read_bytes() == packet, "inspector_replay_conflict")
    else:
        with output.open("xb") as stream:
            stream.write(packet)
    return output


if __name__ == "__main__":
    print(prepare())
