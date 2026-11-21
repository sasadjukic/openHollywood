"""Portable journal, exact-version lookup and manifest-last controls for the Q008 publisher."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_openai_fixture as wire
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretValue

from scripts import publish_q008_completion as publisher
from scripts import q008_sol_smoke as smoke
from tests.api.test_saved_review_completion import anyio_backend as anyio_backend
from tests.api.test_saved_review_completion import archive as archive
from tests.api.test_saved_review_completion import prepared as prepared
from tests.api.test_saved_review_completion import source as source

pytestmark = pytest.mark.usefixtures("anyio_backend")


@pytest.fixture
async def registered(
    archive: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> wire._Plan:
    plan = wire._prepare("unit", None)
    # Issue an isolated test registration. Only the HTTP transport is simulated.
    monkeypatch.setattr(smoke, "source", lambda: plan)
    monkeypatch.setattr(smoke, "ROOT", tmp_path / "smoke")
    monkeypatch.setattr(smoke, "REPO", tmp_path)
    monkeypatch.setattr(smoke, "IMPLEMENTATION", ())
    scorer = tmp_path / "operator"
    scorer.mkdir()
    gold = scorer / "gold.json"
    gold.write_bytes(encoded({"test_gold": True}))
    monkeypatch.setattr(smoke, "GOLD", gold)
    monkeypatch.setattr(smoke, "GOLD_SHA", storage._sha(gold.read_bytes()))
    approval = smoke.freeze()
    monkeypatch.setattr(publisher, "APPROVAL", approval)
    endpoints = iter(plan.wire.endpoints)

    def response(request: httpx.Request) -> httpx.Response:
        endpoint = next(endpoints)
        assert request.content == endpoint.body_utf8.encode()
        return httpx.Response(200, content=wire._reply(plan, endpoint, "complete"))

    assert (
        await smoke._execute(
            smoke.ROOT,
            approval,
            httpx.MockTransport(response),
            SecretValue("publisher-test"),
            "observed_openai_transport",
        )
        == "bound_unassessed"
    )
    audit = smoke.audit(smoke.ROOT, approval)
    bound = audit["bound_result"]
    assert isinstance(bound, dict) and isinstance(bound["receipt"], dict)
    audit_sha = storage._sha(encoded(audit))
    monkeypatch.setattr(publisher, "AUDIT_SHA", audit_sha)
    score = scorer / "score.json"
    score.write_bytes(
        encoded(
            {
                "approval_sha256": approval,
                "audit_sha256": audit_sha,
                "gold_sha256": smoke.GOLD_SHA,
                "scoring_origin": "test operator",
                "result_final_sha256": bound["receipt"]["result_sha256"],
            }
        )
    )
    monkeypatch.setattr(publisher, "SCORE", score)
    monkeypatch.setattr(publisher, "SCORE_SHA", storage._sha(score.read_bytes()))
    members = {f.name: storage._sha(f.read_bytes()) for f in (smoke.ROOT / "output").iterdir()}
    monkeypatch.setattr(publisher, "JOURNAL_SHA", storage._sha(encoded(members)))

    def no_inference(*args: object, **kwargs: object) -> None:
        pytest.fail("Publication tried to access inference")

    monkeypatch.setattr(smoke, "_secret", no_inference)
    monkeypatch.setattr(httpx.AsyncClient, "send", no_inference)
    monkeypatch.setattr(httpx.Client, "send", no_inference)
    return plan


def snapshot(folder: Path) -> dict[str, tuple[bytes, int]]:
    return {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in folder.iterdir()}


def test_cross_selection_create_and_reuse(registered: wire._Plan, tmp_path: Path) -> None:
    review, draft = registered.source.pin.review, registered.source.pin.draft
    manifests = []
    for one, two in ((review, draft), (draft, review)):
        dest = tmp_path / one.role
        assert publisher.publish(one, dest) == "created"
        before = snapshot(dest)
        assert publisher.publish(two, dest) == "reused"
        assert snapshot(dest) == before
        manifest = json.loads(before["manifest.json"][0])
        manifests.append(manifest)
        assert manifest["files_sha256"] == {
            k: storage._sha(raw) for k, (raw, _) in before.items() if k != "manifest.json"
        }
        assert manifest["lookup_selections"] == [s.model_dump(mode="json") for s in (review, draft)]
        delivery = json.loads(before["delivery.json"][0])
        assert delivery["delivery_id"] == manifest["delivery_id"]
        assert delivery["observed_request_selection"] == review.model_dump(mode="json")
        assert delivery["request_manifest_sha256"] == registered.digest
        assert delivery["usage"] == dict(
            input_tokens=100, output_tokens=20, cached_input_tokens=0, reasoning_tokens=5
        )
        assert delivery["actual_billed_cost"] is None and delivery["craft"] == "unassessed"
        assert (
            not delivery["writer_dispatch_authorized"]
            and not delivery["production_attachment_eligible"]
        )
        assert before["operator-score.json"][0] == publisher.SCORE.read_bytes()
    assert manifests[0] == manifests[1]


def test_wrong_identity_and_journal(registered: wire._Plan, tmp_path: Path) -> None:
    review, draft = registered.source.pin.review, registered.source.pin.draft
    dest = tmp_path / "denied"
    for exact, other in ((review, draft), (draft, review)):
        for field, mismatch in (
            ("role", other.role),
            ("version_id", str(uuid4())),
            ("artifact_id", other.artifact_id),
            ("project_id", str(uuid4())),
            ("content_sha256", other.content_sha256),
        ):
            with pytest.raises(EvidenceError, match="q008_wrong_selection"):
                publisher.publish(exact.model_copy(update={field: mismatch}), dest)
        with pytest.raises(EvidenceError, match="q008_unsupported_journal"):
            publisher.publish(exact, dest, journal=tmp_path / "injected")
    assert not dest.exists()


@pytest.mark.parametrize(
    ("fault", "reason"),
    [
        ("unclosed", "q008_delivery_incomplete"),
        ("missing_usage", "q008_delivery_incomplete"),
        ("interrupted_generation", "q008_delivery_incomplete"),
        ("fixture_header", "q008_unsupported_journal"),
        ("fixture_journal", "q008_unsupported_journal"),
        ("draft_request", "q008_frozen_wire_drift"),
        ("changed_score", "q008_operator_score_changed"),
        ("changed_terminal", "q008_journal_chain"),
    ],
)
def test_rejects_ineligible_delivery(
    registered: wire._Plan, tmp_path: Path, fault: str, reason: str
) -> None:
    journal = smoke.ROOT / "output"
    stop = journal / "stop.json"
    outcome = journal / "generation-outcome.json"
    if fault == "unclosed":
        stop.unlink()
    elif fault == "interrupted_generation":
        outcome.unlink()
        stop.unlink()
    elif fault == "missing_usage":
        terminal = json.loads(outcome.read_bytes())
        body = json.loads(terminal["body"])
        del body["usage"]
        terminal["body"] = encoded(body).decode()
        terminal["raw_sha256"] = storage._sha(terminal["body"].encode())
        outcome.write_bytes(encoded(terminal))
        stop.write_bytes(smoke._stop(outcome.read_bytes(), "accounting_hold"))
    elif fault == "fixture_header":
        header = journal / "header.json"
        value = json.loads(header.read_bytes())
        value["origin"] = "injected_transport_fixture"
        header.write_bytes(encoded(value))
    elif fault == "fixture_journal":
        (journal / "journal.json").write_text("{}")
    elif fault == "draft_request":
        draft = wire._prepare("unit", registered.source.pin.draft)
        assert draft.digest != registered.digest
        (smoke.ROOT / "request-manifest.json").write_bytes(draft.files["request-manifest.json"])
    elif fault == "changed_score":
        publisher.SCORE.write_bytes(b"{}")
    else:
        terminal = json.loads(outcome.read_bytes())
        terminal["elapsed_seconds"] += 1
        outcome.write_bytes(encoded(terminal))
    dest = tmp_path / "denied"
    with pytest.raises(EvidenceError, match=reason):
        publisher.publish(registered.source.pin.draft, dest)
    assert not dest.exists()


def test_conflicts_and_source_drift(
    registered: wire._Plan, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review, draft = registered.source.pin.review, registered.source.pin.draft
    with pytest.raises(EvidenceError, match="completion_protected_path"):
        publisher.publish(review, smoke.ROOT / "published")
    dest = tmp_path / "published"
    publisher.publish(review, dest)
    (dest / "delivery.json").write_bytes(b"{}")
    altered = snapshot(dest)
    with pytest.raises(EvidenceError, match="completion_output_conflict"):
        publisher.publish(draft, dest)
    assert snapshot(dest) == altered
    write = storage._write_new

    def drift(target: Path, data: bytes) -> None:
        write(target, data)
        if target.name == "delivery.json":
            publisher.SCORE.write_bytes(b"{}")

    monkeypatch.setattr(storage, "_write_new", drift)
    partial = tmp_path / "partial"
    with pytest.raises(EvidenceError, match="q008_operator_score_changed"):
        publisher.publish(draft, partial)
    assert partial.exists() and not (partial / "manifest.json").exists()
