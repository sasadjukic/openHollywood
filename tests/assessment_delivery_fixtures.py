"""Authored transport data: no live model observations, credentials or semantic gold."""

from __future__ import annotations

from typing import Any

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_delivery import (
    Exchange,
    RequestManifest,
    RequestSet,
    RetainedResponse,
    TerminalEvidence,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import text_hash


def safe_response(final: str | None = None, **changes: Any) -> RetainedResponse:
    return RetainedResponse.model_validate_json(
        encoded(
            {
                "contract": "assessment-fixture-safe-response-1",
                "http_status": 200,
                "state": "complete",
                "response_id": "fixture-response",
                "returned_model": "fixture-only-no-model",
                "finish_reason": "stop",
                "raw_final": final,
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 20,
                    "reasoning_tokens": 5,
                    "cached_input_tokens": 0,
                },
                "counted_input_tokens": None,
                "error_chain": [],
                **changes,
            }
        )
    )


def fixtures_for(request_set: RequestSet, raw_finals: dict[str, str]) -> dict[str, Any]:
    return {
        "contract": "assessment-transport-fixtures-1",
        "origin": "authored_fixture",
        "authored_by": "Authored transport test",
        "cancel_before_dispatch": False,
        "request_set_canonical_sha256": request_set.payload_canonical_sha256,
        "replies": [
            {
                "attempt_id": m.payload.attempt_id,
                "stage": e.stage,
                "behavior": "response",
                "http_status": 200,
                "response_body_utf8": safe_response(
                    None if e.stage == "input_count" else raw_finals[m.payload.batch_id],
                    counted_input_tokens=777 if e.stage == "input_count" else None,
                ).model_dump_json(),
            }
            for m in request_set.payload.requests
            for e in m.payload.endpoints
        ],
    }


def evidence_for(manifest: RequestManifest, raw: str, **changes: Any) -> TerminalEvidence:
    exchanges = []
    for endpoint in manifest.payload.endpoints:
        response = (
            safe_response(counted_input_tokens=777)
            if endpoint.stage == "input_count"
            else safe_response(raw, **changes)
        )
        body = response.model_dump_json()
        exchanges.append(
            Exchange(
                stage=endpoint.stage,
                endpoint_canonical_sha256=canonical_sha256(endpoint.model_dump(mode="json")),
                dispatched_body_bytes_sha256=endpoint.body_bytes_sha256,
                dispatched_body_canonical_sha256=endpoint.body_canonical_sha256,
                disposition="response",
                observed_http_status=response.http_status,
                retained_response=response,
                retained_response_canonical_sha256=canonical_sha256(
                    response.model_dump(mode="json")
                ),
                observed_raw_http_bytes_sha256=text_hash(body),
                raw_http_bytes_retained=False,
                local_error_chain=(),
            )
        )
    return TerminalEvidence(
        contract="assessment-fixture-terminal-evidence-1",
        origin="authored_fixture",
        request_payload_canonical_sha256=manifest.payload_canonical_sha256,
        attempt_id=manifest.payload.attempt_id,
        exchanges=tuple(exchanges),
        active_seconds=0.5,
        unknown_elapsed_endpoints=0,
    )
