"""Exercise the sealed observed pair offline, independently of the spent live registration."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import NoReturn

import pytest
from open_hollywood_engine.evaluations.assessment_result import EvidenceRegistry
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.q011_arrival import regression


@pytest.fixture
def archive(monkeypatch: pytest.MonkeyPatch) -> Path:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the locally preserved Q011 pair")

    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("Observed regression replay must be offline")

    monkeypatch.setattr(socket.socket, "connect", offline)
    monkeypatch.setattr(socket.socket, "connect_ex", offline)
    monkeypatch.setattr(socket, "getaddrinfo", offline)
    return regression.ARCHIVE


def test_observed_pair_and_exact_evidence(archive: Path) -> None:
    assert regression.replay(archive)["decision"] == "hold"
    capture = archive / "capture"
    gold = json.loads((capture / "run/gold.json").read_bytes())["cases"]
    audit = json.loads((capture / "operator/audit.json").read_bytes())
    passages = []
    for case, delivery in zip(("A", "B"), audit["slots"][2:], strict=True):
        work = regression.archived_cell(capture, case).work
        (registry_doc,) = [d for d in work.context.documents if d.kind == "registry"]
        registry = EvidenceRegistry.model_validate_json(registry_doc.content_json)
        refs = {e.ref: e for e in registry.entries}
        answer = delivery["final"]["assessments"]["Q011"]
        assert answer["evidence"] == ["E0233", "E0229", "E0883"]
        for w in gold[case]["assignment"]:
            loc = refs[w["ref"]]
            assert (loc.document_version, loc.field_pointer, loc.quote) == (
                w["version"],
                w["pointer"],
                w["quote"],
            )
        full = refs["E0883"]
        assert gold[case]["draft_version"] == full.document_version
        assert full.document_version in answer["reason"]
        start, end = gold[case]["movement"]["span"]
        assert full.quote[start:end] == gold[case]["movement"]["text"]
        passages.append(full.quote)
    assert passages[1] == passages[0] + " Elias stood at the threshold."
    assert gold["A"]["arrival"] is None and gold["A"]["movement"]["span"][1] == len(passages[0])
    start, end = gold["B"]["arrival"]["span"]
    assert passages[1][start:end] == "Elias stood at the threshold." and end == len(passages[1])


@pytest.mark.parametrize(
    ("target", "replacement"),
    [
        ("run/output/03-A-B-generation-outcome.json", "run/output/04-B-B-generation-outcome.json"),
        ("source/A.json", "source/B.json"),
        ("run/sealed-evidence-decisions.json", None),
        ("run/gold.json", None),
        ("operator/scores.json", None),
    ],
)
def test_damaged_or_swapped_pair_is_refused(
    archive: Path, tmp_path: Path, target: str, replacement: str | None
) -> None:
    replica = tmp_path / "regression"
    shutil.copytree(archive / "capture", replica / "capture")
    shutil.copyfile(archive / "capture-manifest.json", replica / "capture-manifest.json")
    file = replica / "capture" / target
    if replacement:
        file.write_bytes((replica / "capture" / replacement).read_bytes())
    else:
        file.unlink()
    with pytest.raises(EvidenceError, match="q011_regression_(member|inventory)"):
        regression.replay(replica)
