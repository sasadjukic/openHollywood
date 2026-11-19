"""Synthetic journal to original publisher to consumer; no real model observations."""

from pathlib import Path

import pytest
from open_hollywood_api.services import assessment_authored_observed_completion as publisher
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_consumer as service

from tests.api.test_assessment_authored_observed_completion import Capture
from tests.api.test_assessment_authored_observed_completion import captured as captured
from tests.api.test_assessment_authored_observed_completion import frozen as frozen
from tests.api.test_assessment_authored_observed_completion import offline as offline
from tests.api.test_assessment_authored_observed_completion import (
    real_preparation as real_preparation,
)
from tests.api.test_assessment_consumer import pins
from tests.api.test_assessment_openai_authored_smoke import load


def test_supported_authored_publisher_to_complete_consumer(
    captured: Capture,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    assert publisher.publish_observed(captured.registration.name, captured.output) == "created"
    registered = service._Registration(
        captured.registration.name,
        captured.output,
        storage._sha((captured.output / "manifest.json").read_bytes()),
        "authored_diagnostic",
        ("F01", "F02", "F03"),
        43,
    )
    monkeypatch.setattr(service, "REGISTERED", (registered,))
    before = pins(captured.output)
    output = tmp_path / "consumer"
    assert service.export_consumer(registered.name, output) == "created"
    saved = pins(output)
    assert len(saved) == 51
    assert service.export_consumer(registered.name, output) == "reused"
    assert saved == pins(output) and before == pins(captured.output)
    for name in registered.works:
        view = load(output / f"consumer.{name}.json")
        original = load(captured.output / f"{name}.completion.json")
        assert view["source_origin"] == "authored_diagnostic"
        assert view["authority_record"] == original["request_bound_authority"]
        assert view["observation_binding"] == original["observation_binding"]
        assert len(view["fields"]) == 4
        assert sum(r["model_judgment"] is not None for r in view["fields"]) == 3
        assert view["usage"] == original["terminal"]["usage"]
        assert not view["writer_dispatch_authorized"]
