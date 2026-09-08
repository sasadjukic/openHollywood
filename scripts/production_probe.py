"""Opt-in, isolated specialist probes against immutable historical canary inputs.

Inspect is read-only and performs no model calls. Run writes only a new diagnostic
directory, never a campaign database/report or canonical artifact. These are NOT
canary completions or human reviews. At most two sequential calls are permitted.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sqlite3
from collections.abc import Mapping
from contextlib import closing
from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services.production_model_executor import (
    _OUTPUT_MODELS,
    _critic_evidence_catalog,
    _Execution,
    _materialize_output_data,
    _messages,
    _messages_sha256,
    _Operation,
    _output_schema,
    _require_matching_response,
    _source_story_bible,
    _structured_failure_issues,
    _temperature,
    _validate_output,
)
from open_hollywood_api.services.structured_output import normalize_json_document
from open_hollywood_engine.artifacts import ArtifactKind, StoryBibleUpdate, apply_story_bible_update
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.models import (
    InvocationContext,
    ModelCallBudget,
    ModelDeployment,
    ModelGateway,
    ModelGatewayError,
    ModelRequest,
    ModelSelection,
    ModelSettings,
    OllamaGateway,
    OllamaHost,
)
from open_hollywood_engine.secrets import SecretLeakError
from open_hollywood_engine.workflows import (
    SCENE_PRODUCTION_GRAPH_VERSION,
    SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
    ArtifactReference,
    SceneProductionError,
)

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Probe:
    database: Path
    source_invocation_id: UUID
    operation: _Operation
    execution: _Execution
    task: object
    manifest: dict[str, Any]


def load_probe(database: Path, invocation_id: UUID) -> Probe:
    """Recover full exact artifact versions in the original request's input order."""
    database = database.resolve(strict=True)
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        invocation = connection.execute(
            "SELECT * FROM agent_invocations WHERE id=?", (invocation_id.hex,)
        ).fetchone()
        if invocation is None:
            raise ValueError("source invocation does not exist")
        settings = json.loads(invocation["request_settings"])
        operation = _Operation(settings["operation"])
        if operation not in {_Operation.CRITIQUE, _Operation.STORY_BIBLE_UPDATE}:
            raise ValueError("isolated probes support critique and story_bible_update only")
        run = connection.execute(
            "SELECT * FROM workflow_runs WHERE id=?", (invocation["workflow_run_id"],)
        ).fetchone()
        if run is None or run["workflow_name"] != "scene_production":
            raise ValueError("source must be an existing scene-production invocation")
        state = json.loads(run["input_state"])
        payload = json.loads(invocation["prompt_text"].rsplit("\n\n", 1)[1])
        assignment = payload["assignment"]
        rows = connection.execute(
            "SELECT v.*, a.artifact_key, a.artifact_type, a.project_id FROM artifact_versions v "
            "JOIN artifacts a ON a.id=v.artifact_id JOIN agent_invocation_inputs i "
            "ON i.artifact_version_id=v.id WHERE i.agent_invocation_id=?",
            (invocation_id.hex,),
        ).fetchall()
        by_id = {str(UUID(row["id"])): row for row in rows}
        ordered_ids = [item["artifact_version_id"] for item in payload["input_artifacts"]]
        if set(ordered_ids) != set(by_id) or len(ordered_ids) != len(by_id):
            raise ValueError("source request and exact input lineage disagree")
        if operation is _Operation.CRITIQUE and state["approved_blueprint_version_id"] not in by_id:
            raise ValueError("approved Blueprint is absent from source input lineage")
        inputs = []
        references: dict[str, ArtifactReference] = {}
        hashes = {}
        for version_id in ordered_ids:
            row = by_id[version_id]
            content = json.loads(row["content"])
            if (
                row["project_id"] != run["project_id"]
                or canonical_sha256(content) != row["content_sha256"]
            ):
                raise ValueError("source artifact content/provenance digest mismatch")
            inputs.append(
                {
                    "artifact_version_id": version_id,
                    "artifact_key": row["artifact_key"],
                    "artifact_kind": row["artifact_type"],
                    "content": content,
                }
            )
            references[version_id] = ArtifactReference(
                kind=ArtifactKind(row["artifact_type"]),
                artifact_key=row["artifact_key"],
                version_id=UUID(version_id),
                schema_version=row["schema_version"],
            )
            hashes[version_id] = row["content_sha256"]
        if operation is _Operation.STORY_BIBLE_UPDATE:
            bibles = [item["content"] for item in inputs if item["artifact_kind"] == "story_bible"]
            if (
                len(bibles) != 1
                or bibles[0].get("source_blueprint_version_id")
                != state["approved_blueprint_version_id"]
            ):
                raise ValueError("Bible does not descend from the run's approved Blueprint")
        budget = settings["budget"]
        execution = _Execution(
            workflow_run_id=UUID(run["id"]),
            project_id=UUID(run["project_id"]),
            profile_id=UUID(state["model_profile_id"]),
            configuration_sha256=state["model_profile_configuration_sha256"],
            selection=ModelSelection(
                provider=invocation["provider"],
                model_identifier=invocation["model_identifier"],
                deployment=ModelDeployment(settings["deployment"]),
            ),
            specialist_role=invocation["specialist_role"],
            input_version_ids=tuple(UUID(value) for value in ordered_ids),
            inputs=tuple(inputs),
            constraints=state["benchmark_constraints"],
            call_budget=ModelCallBudget(
                max_input_tokens=budget["max_input_tokens"],
                max_output_tokens=budget["max_output_tokens"],
                max_cost_usd=Decimal(budget["max_cost_usd"]),
            ),
            seed=settings["run_seed"],
            task_fingerprint=f"isolated:{invocation_id}",
            unit_id=assignment["unit_id"],
            unit_number=assignment["unit_number"],
            unit_count=assignment["unit_count"],
            revision_number=assignment["revision_number"],
            attempt_number=1,
            previous_failure=None,
            fallback_history=(),
        )

        def reference(kind: str) -> ArtifactReference:
            matches = [item for item in inputs if item["artifact_kind"] == kind]
            if kind == "scene_draft":
                matches = [
                    item
                    for item in matches
                    if item["content"].get("scene_id") == execution.unit_id
                    and (
                        operation is _Operation.STORY_BIBLE_UPDATE
                        or item["content"].get("revision_number") == execution.revision_number
                    )
                ]
            if len(matches) != 1:
                raise ValueError(f"probe requires one unambiguous {kind} input")
            return references[matches[0]["artifact_version_id"]]

        task = SimpleNamespace(draft=reference("scene_draft"))
        if operation is _Operation.STORY_BIBLE_UPDATE:
            task = SimpleNamespace(
                unit=SimpleNamespace(unit_id=execution.unit_id, unit_number=execution.unit_number),
                accepted_draft=reference("scene_draft"),
                source_story_bible=reference("story_bible"),
                continuity_report=reference("continuity_report"),
            )
        manifest = {
            "evidence_type": "isolated_specialist_probe_not_canary",
            "schema_version": "1",
            "source_database": str(database),
            "source_invocation_id": str(invocation_id),
            "source_workflow_run_id": str(execution.workflow_run_id),
            "source_prompt_version": settings["prompt_template_version"],
            "source_prompt_sha256": invocation["prompt_sha256"],
            "candidate_prompt_version": SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
            "candidate_graph_version": SCENE_PRODUCTION_GRAPH_VERSION,
            "input_artifact_sha256": hashes,
            "model": execution.selection.model_identifier,
            "deployment": execution.selection.deployment.value,
            "operation": operation.value,
            "scene_id": execution.unit_id,
            "revision_number": execution.revision_number,
            "seed": execution.seed,
            "per_call_budget": budget,
            "maximum_calls": 2,
            "maximum_input_tokens": 2 * budget["max_input_tokens"],
            "maximum_output_tokens": 2 * budget["max_output_tokens"],
            "maximum_cost_usd": str(2 * Decimal(budget["max_cost_usd"])),
            "maximum_active_seconds": 1800,
        }
    active_secret_guard().ensure_safe((execution, manifest), destination="isolated_probe")
    return Probe(database, invocation_id, operation, execution, task, manifest)


def probe_request(probe: Probe, execution: _Execution) -> ModelRequest:
    schema = _output_schema(
        probe.operation,
        continuity_schema_variant=None,
        critic_evidence_refs=tuple(
            item["evidence_ref"] for item in _critic_evidence_catalog(execution)
        )
        if probe.operation is _Operation.CRITIQUE
        else None,
    )
    messages = _messages(
        probe.operation,
        execution,
        schema,
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    request = ModelRequest(
        model_identifier=execution.selection.model_identifier,
        messages=messages,
        budget=execution.call_budget,
        invocation=InvocationContext(
            specialist_role=execution.specialist_role,
            prompt_template_version=SCENE_PRODUCTION_PROMPT_TEMPLATE_VERSION,
            input_artifact_version_ids=execution.input_version_ids,
            model_profile_id=execution.profile_id,
        ),
        settings=ModelSettings(
            temperature=_temperature(probe.operation),
            top_p=0.95,
            seed=execution.seed,
            thinking=False,
        ),
        response_schema=schema if execution.selection.deployment is ModelDeployment.LOCAL else None,
    )
    active_secret_guard().ensure_safe(request, destination="isolated_probe_request")
    return request


def _write_new(path: Path, value: object) -> None:
    active_secret_guard().ensure_safe(value, destination="isolated_probe_output")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(
            value,
            stream,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            default=lambda item: dict(item) if isinstance(item, Mapping) else _unsupported_json(),
        )
        stream.write("\n")


def _unsupported_json() -> None:
    raise TypeError("probe output contains a non-JSON value")


async def run_probe(
    probe: Probe, gateway: ModelGateway, output: Path, *, allow_cloud: bool = False
) -> dict[str, Any]:
    if probe.execution.selection.deployment is ModelDeployment.CLOUD and not allow_cloud:
        raise ValueError("Cloud probe requires explicit --allow-cloud")
    output = output.resolve()
    if output.is_relative_to(probe.database.parent) or output.is_relative_to(
        ROOT / "data/benchmarks"
    ):
        raise ValueError("diagnostics must be outside protected canary directories")
    output.mkdir(parents=True, exist_ok=False)
    _write_new(output / "manifest.json", probe.manifest)
    execution = probe.execution
    attempts: list[dict[str, Any]] = []
    for attempt in (1, 2):
        request = probe_request(probe, execution)
        record: dict[str, Any] = {
            "attempt": attempt,
            "prompt_sha256": _messages_sha256(request.messages),
            "status": "started",
        }
        _write_new(
            output / f"attempt-{attempt}-request.json",
            {
                **record,
                "messages": [
                    {"role": message.role.value, "content": message.content}
                    for message in request.messages
                ],
                "response_schema": dict(request.response_schema)
                if request.response_schema
                else None,
            },
        )
        try:
            async with asyncio.timeout(900):
                response = await gateway.generate(request)
            record.update(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                estimated_cost_usd=str(response.estimated_cost_usd),
                latency_ms=response.timing.total_ms,
            )
            active_secret_guard().ensure_safe(response, destination="isolated_probe_response")
            record.update(
                finish_reason=response.finish_reason,
                response_sha256=hashlib.sha256(response.content.encode()).hexdigest(),
                response_length=len(response.content),
            )
            _require_matching_response(response, execution)
            materialized = _materialize_output_data(
                probe.operation,
                probe.task,
                execution,
                json.loads(normalize_json_document(response.content)),
            )
            result = _OUTPUT_MODELS[probe.operation].model_validate(materialized)
            _validate_output(probe.operation, probe.task, result)
            if isinstance(result, StoryBibleUpdate):
                successor = apply_story_bible_update(_source_story_bible(execution), result)
                record["successor_bible"] = successor.model_dump(mode="json")
            record.update(status="validated", result=result.model_dump(mode="json"))
        except (
            ValueError,
            ModelGatewayError,
            SceneProductionError,
            SecretLeakError,
            TimeoutError,
        ) as error:
            record.update(
                status="failed",
                error_type=type(error).__name__,
                error=active_secret_guard().redact_text(str(error))[:2000],
            )
            if isinstance(error, ValueError) and not isinstance(error, SecretLeakError):
                issues = _structured_failure_issues(error)
                record["validation_issues"] = [
                    {key: active_secret_guard().redact_text(value) for key, value in issue.items()}
                    for issue in issues
                ]
                execution = replace(
                    execution,
                    attempt_number=2,
                    previous_failure={
                        "error_code": "schema_validation_failed",
                        "validation_issues": record["validation_issues"],
                    },
                )
            else:
                record["retryable_structural_failure"] = False
                if isinstance(error, ModelGatewayError) and error.usage is not None:
                    record.update(
                        input_tokens=error.usage.input_tokens,
                        output_tokens=error.usage.output_tokens,
                    )
        except asyncio.CancelledError:
            _write_new(output / f"attempt-{attempt}-result.json", {**record, "status": "cancelled"})
            raise
        _write_new(output / f"attempt-{attempt}-result.json", record)
        attempts.append(record)
        if record["status"] == "validated" or "validation_issues" not in record:
            break
    summary = {
        "evidence_type": "isolated_specialist_probe_not_canary",
        "status": attempts[-1]["status"],
        "attempts": len(attempts),
        "input_tokens": sum(item.get("input_tokens", 0) for item in attempts),
        "output_tokens": sum(item.get("output_tokens", 0) for item in attempts),
        "output_directory": str(output),
    }
    _write_new(output / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inspect", "run"))
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--invocation-id", required=True, type=UUID)
    parser.add_argument("--output-directory", type=Path)
    parser.add_argument("--allow-cloud", action="store_true")
    args = parser.parse_args()
    probe = load_probe(args.database, args.invocation_id)
    if args.command == "inspect":
        request = probe_request(probe, probe.execution)
        print(
            json.dumps(
                {**probe.manifest, "candidate_prompt_sha256": _messages_sha256(request.messages)},
                indent=2,
            )
        )
        return 0
    if args.output_directory is None:
        parser.error("run requires --output-directory (a new directory outside canary evidence)")

    async def run() -> dict[str, Any]:
        async with OllamaGateway(host=OllamaHost.LOCAL, timeout_seconds=900) as gateway:
            return await run_probe(
                probe, gateway, args.output_directory, allow_cloud=args.allow_cloud
            )

    summary = asyncio.run(run())
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "validated" else 1


if __name__ == "__main__":
    raise SystemExit(main())
