"""Verify the actual mock wire against independent, freshly created saved-review evidence."""

from __future__ import annotations

import json
from pathlib import Path
from shutil import copyfile
from typing import Any
from uuid import uuid4

import httpx
import pytest
from open_hollywood_api.services import saved_review_completion
from open_hollywood_api.services import saved_review_openai_fixture as service
from open_hollywood_engine.evaluations.assessment_compact_presentation import (
    NOTICE,
    PROVENANCE_ID,
    SYSTEM,
    compact,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import _field
from open_hollywood_engine.evaluations.review_evidence import JsonObject, text_hash
from open_hollywood_engine.models.assessment_openai import WireEndpoint

from scripts.saved_review_openai_fixture import main
from tests.api.test_saved_review_completion import anyio_backend as anyio_backend
from tests.api.test_saved_review_completion import archive as archive
from tests.api.test_saved_review_completion import offline as offline
from tests.api.test_saved_review_completion import pin_files, read
from tests.api.test_saved_review_completion import prepared as prepared
from tests.api.test_saved_review_completion import source as source
from tests.production_assessment_fixtures import FixtureRegistration, response_for, sha

pytestmark = pytest.mark.anyio


async def test_capture_receipt_binds_raw_reply_and_creator(
    archive: Path, source: FixtureRegistration
) -> None:
    registered = saved_review_completion._open("unit")
    prepared_source = saved_review_completion._prepare(registered, source.selections[0])
    pin = prepared_source.pin
    folder = registered.root / "capture"
    folder.mkdir()
    content = "Synthetic critic message for receipt binding."
    http = encoded(
        {
            "http_status": 200,
            "response": {"done": True, "done_reason": "stop", "message": {"content": content}},
        }
    )
    run_id = str(uuid4())
    terminal = encoded(
        {
            "origin": "isolated_provider_capture",
            "status": "captured",
            "dispatch_state": "dispatched",
            "database_sha256": pin.database_capture_sha256,
            "critique_version": pin.review.version_id,
            "invocation_id": pin.invocation_id,
            "run_id": run_id,
            "http_status": 200,
            "http_sha256": sha(http),
        }
    )
    for name, body in (("terminal.json", terminal), ("http.json", http)):
        (folder / name).write_bytes(body)
    capture_archive = saved_review_completion._Archive(
        registered.registration,
        {
            **registered.hashes,
            "work/capture/terminal.json": sha(terminal),
            "work/capture/http.json": sha(http),
        },
    )
    creator: JsonObject = {
        "invocation_id": pin.invocation_id,
        "workflow_run_id": run_id,
        "response_sha256": text_hash(content),
    }
    assert saved_review_completion._capture_receipt(
        capture_archive, {"invocation": creator}, pin
    ) == {"critic_http_receipt_sha256": sha(http), "critic_terminal_sha256": sha(terminal)}
    for change in (
        {"invocation_id": str(uuid4())},
        {"response_sha256": text_hash("another reply")},
    ):
        with pytest.raises(ValueError, match="capture_receipt_binding"):
            saved_review_completion._capture_receipt(
                capture_archive, {"invocation": {**creator, **change}}, pin
            )


def assert_visible_context(body: dict[str, Any], source: FixtureRegistration, side: int) -> None:
    original = json.loads(source.request)
    system, user = body["input"]
    assert system == {"role": "system", "content": SYSTEM} and user["role"] == "user"
    packet = json.loads(user["content"])
    assert set(packet) == {
        "contract",
        "selected_artifact",
        "original_review",
        "reviewed_draft",
        "batch_id",
        "active_unit_ids",
        "native_work_view",
        "original_scope_declarations",
        "original_work_briefs",
        "whole_intake_dispositions",
        "availability_notice",
    }
    assert (
        packet["availability_notice"] == NOTICE
        and packet["batch_id"] == original["batch"]["batch_id"]
    )
    assert packet["selected_artifact"] == source.selections[side].model_dump(mode="json")
    assert [packet["original_review"], packet["reviewed_draft"]] == [
        s.model_dump(mode="json") for s in source.selections
    ]
    assert packet["active_unit_ids"] == ["Q010"]
    assert packet["original_scope_declarations"] == original["declarations"]
    assert packet["original_work_briefs"] == original["briefs"]
    assert packet["whole_intake_dispositions"] == [
        f.model_dump(mode="json") for f in source.intake.findings
    ]
    assert body["text"]["format"]["schema"] == original["response_schema"]
    view = packet["native_work_view"]
    visible = {d["identity"]: d for d in view["context"]["documents"]}
    native = original["work"]
    docs = native["context"]["documents"]
    assert list(visible) == [d["identity"] for d in docs]
    for doc in docs:
        row = visible[doc["identity"]]
        meta = {k: v for k, v in doc.items() if k != "content_json"}
        assert all(row[k] == v for k, v in meta.items())
        content = json.loads(doc["content_json"])
        if doc["kind"] == "registry":
            assert set(row) == set(meta) | {"columns", "whole_field_locations"}
            assert row["columns"] == ["ref", "document_id", "field_pointer"]
            refs = []
            for ref, identity, pointer in row["whole_field_locations"]:
                target = visible[identity]
                quote = _field(target["structured_content"], pointer)
                refs.append(
                    dict(
                        ref=ref,
                        document_id=identity,
                        document_version=target["version"],
                        document_sha256=target["content_sha256"],
                        field_pointer=pointer,
                        field_sha256=text_hash(quote),
                        start=0,
                        end=len(quote),
                        quote=quote,
                        paragraph=None,
                    )
                )
            assert refs == content["entries"]
        elif doc["identity"] == PROVENANCE_ID:
            assert row == meta | {"local_only": True}
        else:
            assert row == meta | {"structured_content": content}
    # Compare every remaining field, including both original messages and the full claim spans.
    view["context"]["documents"] = docs
    assert view == native
    for forbidden in (
        "source-receipt.json",
        "archive_seal_sha256",
        "fixture_manifest_sha256",
        "source_data_origin",
        str(source.database),
        response_for(source),
    ):
        assert forbidden not in user["content"]


@pytest.mark.parametrize("side", [0, 1], ids=["critique", "draft"])
async def test_actual_endpoint_bodies_and_closed_publication(
    archive: Path,
    source: FixtureRegistration,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    side: int,
) -> None:
    before = pin_files(archive)
    journal, output = tmp_path / "journal", tmp_path / "published"
    selected = tmp_path / "selection.json"
    selected.write_bytes(encoded(source.selections[side].model_dump(mode="json")))
    args = [
        "--source",
        "unit",
        "--selection",
        str(selected),
        "--journal",
        str(journal),
        "--scenario",
        "complete",
    ]
    received = []
    original = httpx.MockTransport.handle_request

    def inspect(mock: httpx.MockTransport, request: httpx.Request) -> httpx.Response:
        stage = "input_count" if request.url.path.endswith("/input_tokens") else "generation"
        assert (journal / (stage + "-intent.json")).is_file()
        assert request.content == (journal / (stage + "-request.json")).read_bytes()
        assert "authorization" not in request.headers
        body = json.loads(request.content)
        assert_visible_context(body, source, side)
        received.append((request.url.path, body))
        return original(mock, request)

    monkeypatch.setattr(httpx.MockTransport, "handle_request", inspect)
    assert main(["capture", *args]) == 0
    assert [p for p, _ in received] == ["/v1/responses/input_tokens", "/v1/responses"]
    count, generate = (v for _, v in received)
    assert count == {k: generate[k] for k in ("model", "input", "text", "reasoning")}
    assert generate["truncation"] == "disabled"
    journal_before = pin_files(journal)
    assert main(["publish", *args, "--output", str(output)]) == 0
    result = read(output / "audit.json")
    assert result["state"] == "bound_unassessed" and result["fixture_publication_eligible"]
    assert result["completion"]["complete_delivery"] and not result["model_evidence"]
    assert result["result"]["raw_final"] == response_for(source)
    assert (
        result["result"]["units"][0]["evidence_locations"][0]["document_version"]
        == source.selections[1].version_id
    )
    assert result["result"]["receipt"]["request_sha256"] == sha(
        (journal / "request-manifest.json").read_bytes()
    )
    assert result["result"]["receipt"]["request_sha256"] != sha(source.request)
    assert (
        result["counted_input_tokens"] == 100 and result["generation_usage"]["output_tokens"] == 20
    )
    assert result["actual_billed_cost"] is None and not result["writer_dispatch_authorized"]
    assert not result["production_attachment_eligible"] and result["live_calls"] == 0
    stamps = {p: (p.stat().st_mtime_ns, p.read_bytes()) for p in output.iterdir()}
    assert main(["publish", *args, "--output", str(output)]) == 0
    assert all(v == (p.stat().st_mtime_ns, p.read_bytes()) for p, v in stamps.items())
    assert main(["capture", *args]) == 2 and len(received) == 2
    assert pin_files(journal) == journal_before and pin_files(archive) == before


@pytest.mark.parametrize(
    ("scenario", "state", "attempts", "pending"),
    [
        ("missing-terminal", "missing_generation_terminal", 1, 1),
        ("count-rejected", "count_rejected", 0, 0),
    ],
)
async def test_open_or_rejected_exchange_cannot_publish(
    archive: Path,
    tmp_path: Path,
    scenario: service.Scenario,
    state: str,
    attempts: int,
    pending: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbid_prior_answer(*args: object) -> None:
        pytest.fail("Preparation, count and an unobserved generation must stand on source alone")

    monkeypatch.setattr(saved_review_completion, "_audit", forbid_prior_answer)
    journal = tmp_path / "journal"
    service.capture("unit", None, journal, scenario)
    service.export("unit", None, journal, scenario, tmp_path / "audit")
    result = read(tmp_path / "audit/audit.json")
    assert result["state"] == state and result["possibly_sent_without_terminal"] == pending
    assert (
        result["fixture_count_attempts"] == 1 and result["fixture_generation_attempts"] == attempts
    )
    assert result["result"] is None and result["generation_usage"] is None
    assert (
        not result["completion"]["complete_delivery"] and not result["fixture_publication_eligible"]
    )
    with pytest.raises(ValueError, match="publication_incomplete"):
        service.export("unit", None, journal, scenario, tmp_path / "out", publish=True)
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("stage", ["input_count", "generation"])
async def test_wrong_version_body_refused_before_mock_dispatch(
    archive: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stage: str,
) -> None:
    original = service._request

    def substitute(endpoint: WireEndpoint) -> httpx.Request:
        if endpoint.stage != stage:
            return original(endpoint)
        body = json.loads(endpoint.body_utf8)
        packet = json.loads(body["input"][1]["content"])
        packet["reviewed_draft"]["version_id"] = str(uuid4())
        body["input"][1]["content"] = compact(packet)
        return original(endpoint.model_copy(update={"body_utf8": encoded(body).decode()}))

    monkeypatch.setattr(service, "_request", substitute)
    journal = tmp_path / "journal"
    with pytest.raises(ValueError, match="wire_bytes"):
        service.capture("unit", None, journal, "complete")
    assert not (journal / (stage + "-intent.json")).exists()
    assert (journal / "input_count-outcome.json").exists() == (stage == "generation")
    with pytest.raises(ValueError, match="publication_incomplete"):
        service.export("unit", None, journal, "complete", tmp_path / "out", publish=True)


async def test_cross_selected_version_and_damaged_terminal_refused(
    archive: Path,
    source: FixtureRegistration,
    tmp_path: Path,
) -> None:
    journal, out = tmp_path / "journal", tmp_path / "out"
    service.capture("unit", source.selections[0], journal, "complete")
    second = tmp_path / "second-journal"
    service.capture("unit", source.selections[0], second, "complete")
    assert (second / "request-manifest.json").read_bytes() == (
        journal / "request-manifest.json"
    ).read_bytes()
    assert (
        read(second / "journal.json")["journal_id"] != read(journal / "journal.json")["journal_id"]
    )
    copyfile(journal / "generation-outcome.json", second / "generation-outcome.json")
    with pytest.raises(ValueError, match="outcome_binding"):
        service.export("unit", None, second, "complete", out, publish=True)
    for wrong in (
        source.selections[1],
        source.selections[0].model_copy(update={"version_id": str(uuid4())}),
    ):
        with pytest.raises(ValueError, match="version|selection"):
            service.export("unit", wrong, journal, "complete", out, publish=True)
    stop = journal / "stop.json"
    original = stop.read_bytes()
    stop.unlink()
    service.export("unit", None, journal, "complete", tmp_path / "open")
    assert read(tmp_path / "open/audit.json")["state"] == "missing_stop"
    with pytest.raises(ValueError, match="publication_incomplete"):
        service.export("unit", None, journal, "complete", out, publish=True)
    stop.write_bytes(original)
    outcome = journal / "generation-outcome.json"
    value = read(outcome)
    value["response_utf8"] = "{}"
    value["response_bytes_sha256"] = text_hash("{}")
    outcome.write_bytes(encoded(value))
    stop.write_bytes(encoded({"kind": "stop", "previous_sha256": sha(outcome.read_bytes())}))
    with pytest.raises(ValueError, match="outcome_binding"):
        service.export("unit", None, journal, "complete", out, publish=True)
    assert not out.exists()
