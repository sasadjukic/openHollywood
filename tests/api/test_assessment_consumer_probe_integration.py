"""Synthetic journal to original probe publisher to consumer; no real network."""

from pathlib import Path

import pytest
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_consumer as service
from open_hollywood_api.services import assessment_observed_completion as publisher

from tests.api.test_assessment_consumer import pins
from tests.api.test_assessment_observed_completion import Capture
from tests.api.test_assessment_observed_completion import captured as captured
from tests.api.test_assessment_observed_completion import frozen as frozen
from tests.api.test_assessment_observed_completion import offline as offline
from tests.api.test_assessment_openai_compact_smoke import load


def test_supported_probe_publisher_to_complete_consumer(
    captured: Capture,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    assert publisher.publish_observed(captured.registration.name, captured.output) == "created"
    registered = service._Registration(
        captured.registration.name,
        captured.output,
        storage._sha((captured.output / "manifest.json").read_bytes()),
        "registered_diagnostic_probe",
        ("N06", "N07", "N10", "N11"),
        27,
    )
    monkeypatch.setattr(service, "REGISTERED", (registered,))
    before = pins(captured.output)
    output = tmp_path / "consumer"
    assert service.export_consumer(registered.name, output) == "created"
    saved = pins(output)
    assert len(saved) == 37
    assert service.export_consumer(registered.name, output) == "reused"
    assert saved == pins(output) and before == pins(captured.output)
    for name in registered.works:
        view = load(output / f"consumer.{name}.json")
        original = load(captured.output / f"{name}.completion.json")
        assert view["source_origin"] == "registered_diagnostic_probe"
        assert view["authority_record"] is None
        assert view["observation_binding"] == original["observation_binding"]
        assert len(view["fields"]) == 6
        assert [r["original_field"] for r in view["fields"]] == [
            f["field"] for f in original["intake"]["findings"]
        ]
        assert view["usage"] == original["terminal"]["usage"]
        assert not view["writer_dispatch_authorized"]
