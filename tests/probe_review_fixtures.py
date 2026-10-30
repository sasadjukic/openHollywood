"""Authored sealed archives; these are never counted as real model observations."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.probe_review_evidence import ProbeArchiveContract
from open_hollywood_engine.evaluations.review_evidence import (
    SavedMessage,
    catalog_v61,
    messages_hash,
)


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


@dataclass
class ProbeFixture:
    root: Path
    documents: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)
    experiment: str = "authored-probe-fixture"
    trial: str = "s1-control-initial"

    @property
    def live(self) -> Path:
        return self.root / (self.experiment + "-live")

    def path(self, area: str, name: str) -> Path:
        return (self.live if area == "live" else self.root / self.experiment) / name

    def seal(self) -> ProbeArchiveContract:
        # Re-sealing is deliberately test-only: production CLI trust is hard-pinned.
        prepared = {
            name: hashlib.sha256(encoded(value)).hexdigest()
            for (area, name), value in self.documents.items()
            if area == "prepared"
        }
        live = {
            name: hashlib.sha256(encoded(value)).hexdigest()
            for (area, name), value in self.documents.items()
            if area == "live"
        }
        prep_closure = {"evidence_sha256": prepared}
        plan_hash = prepared["plan.json"]
        prep_hash = hashlib.sha256(encoded(prep_closure)).hexdigest()
        closure = {
            "plan_sha256": plan_hash,
            "preparation_closure_sha256": prep_hash,
            "evidence_sha256": live,
            "operator_evidence_sha256": {},
        }
        contract = ProbeArchiveContract(
            experiment=self.experiment,
            plan_sha256=plan_hash,
            preparation_closure_sha256=prep_hash,
            live_closure_sha256=hashlib.sha256(encoded(closure)).hexdigest(),
        )
        for (area, name), value in {
            **self.documents,
            ("prepared", "preparation-closure.json"): prep_closure,
            ("live", "closure.json"): closure,
        }.items():
            path = self.path(area, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded(value))
        return contract


def make_probe_fixture(
    root: Path, *, retry: bool = False, unmet: bool = False, post: bool = False
) -> ProbeFixture:
    fixture = ProbeFixture(root)
    experiment = fixture.experiment
    case = "AUTHORED-ONLY"

    def artifact(kind: str, content: dict[str, Any]) -> dict[str, Any]:
        return {
            "artifact_kind": kind,
            "artifact_key": kind + "_scene_1" if kind in {"scene_draft", "critique"} else kind,
            "artifact_version_id": str(
                uuid5(NAMESPACE_URL, f"{experiment}:{case}:{kind}:{canonical_sha256(content)}")
            ),
            "content": deepcopy(content),
        }

    plan = artifact(
        "scene_plan",
        {
            "id": "scene_1",
            "turning_point": "A signal appears.",
            "outcome": "She decides to investigate.",
        },
    )
    original = artifact(
        "scene_draft",
        {
            "scene_id": "scene_1",
            "revision_number": 0,
            "prose": "She decides to investigate. She waits. She decides to investigate.",
        },
    )
    initial_inputs = [plan, original]
    requests: dict[str, dict[str, Any]] = {}
    replies: dict[str, tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any]]] = {}

    def request_for(
        trial: str, stage: str, inputs: list[dict[str, Any]], source: str | None
    ) -> dict[str, Any]:
        current = inputs[-1] if stage != "writer" else original
        manifest = {
            "experiment": experiment,
            "trial": trial,
            "stage": stage,
            "arm": "none" if stage == "initial" else "evidence",
            "kind": "control",
            "case_id": case,
            "seed": 1,
            "candidate_version_id": current["artifact_version_id"],
            "prompt_version": "61",
            "graph_version": "9",
            "critic_semantics": "ordinary_production",
            "source_commit": "authored-fixture",
            "synthetic_unapproved_context": True,
            "input_artifact_sha256": {
                i["artifact_version_id"]: canonical_sha256(i["content"]) for i in inputs
            },
            "source_trial": source,
            "evidence_type": "isolated_comparison_not_full_workflow_or_story_acceptance",
        }
        views = deepcopy(inputs)
        for view in views:
            if view["artifact_kind"] == "scene_draft":
                prose = view["content"].pop("prose")
                if view["artifact_version_id"] == current["artifact_version_id"]:
                    view["content"]["evidence_catalog"] = [
                        r.model_dump(mode="json")
                        for r in catalog_v61(prose, view["artifact_version_id"])
                    ]
                else:
                    view["context_scope"] = "repair_source_identity"
        payload = {
            "input_artifacts": views,
            "scene_assignment_contract": {**plan["content"], "scene_id": "scene_1"},
            "repair_acceptance_tests": []
            if stage != "post"
            else [
                {
                    "source_draft_version_id": original["artifact_version_id"],
                    "original_evidence": ["She waits."],
                }
            ],
        }
        messages = (
            SavedMessage(role="system", content="Authored fixture only; no inference."),
            SavedMessage(role="user", content=json.dumps(payload)),
        )
        request = {
            "manifest": manifest,
            "inputs": inputs,
            "model_identifier": "gemma4:31b-cloud",
            "messages": [m.model_dump(mode="json") for m in messages],
            "prompt_sha256": messages_hash(messages),
            "response_schema": None,
            "settings": {"seed": 1, "thinking": False},
            "budget": {"max_output_tokens": 1},
            "invocation": {
                "specialist_role": "scene_writer" if stage == "writer" else "scene_critic",
                "prompt_template_version": "61",
                "input_artifact_version_ids": [i["artifact_version_id"] for i in inputs],
                "model_profile_id": "00000000-0000-0000-0000-000000000001",
            },
        }
        requests[trial] = request
        return request

    def review_for(
        request: dict[str, Any], is_unmet: bool
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        current = request["inputs"][-1]
        catalog = catalog_v61(current["content"]["prose"], current["artifact_version_id"])
        check = {
            "status": "unmet" if is_unmet else "met",
            "assessment": "Authored fixture judgment, not semantic truth.",
            "draft_evidence_refs": [catalog[-1].evidence_ref],
            "recommended_resolution": None,
        }
        raw: dict[str, Any] = {
            "verdict": "revise" if is_unmet else "pass",
            "assignment_checks": {a: deepcopy(check) for a in ("turning_point", "outcome")},
            "assignment_repair_conditions": [
                {
                    "repair_ref": "assignment:" + a,
                    "conditions": [{"condition": "Add the required event."}],
                }
                for a in ("turning_point", "outcome")
            ]
            if is_unmet
            else [],
        }
        saved = deepcopy(raw["assignment_checks"])
        if is_unmet:
            for c in saved.values():
                c["recommended_resolution"] = "Add the required event."
        audit = {
            "schema_version": "7",
            "repair_advice_origin": "shared_finding_conditions",
            "assignment_checks": saved,
            "candidate_version_id": current["artifact_version_id"],
            "current_plan_version_id": plan["artifact_version_id"],
            "assignment_repair_conditions": raw["assignment_repair_conditions"],
        }
        result = {
            "verdict": raw["verdict"],
            "target_artifact_kind": "scene_draft",
            "target_artifact_key": current["artifact_key"],
            "target_artifact_version_id": current["artifact_version_id"],
            "issues": [],
        }
        return raw, audit, result

    initial = request_for(fixture.trial, "initial", initial_inputs, None)
    replies[fixture.trial] = review_for(initial, unmet)
    initial_trial = fixture.trial
    if post:
        writer = "s1-control-writer-evidence"
        writer_inputs = [*deepcopy(initial_inputs), artifact("critique", replies[initial_trial][2])]
        request_for(writer, "writer", writer_inputs, initial_trial)
        revised = {
            "scene_id": "scene_1",
            "revision_number": 1,
            "prose": "A signal appears. She decides to investigate.",
        }
        replies[writer] = (revised, None, revised)
        fixture.trial = "s1-control-post-evidence"
        post_request = request_for(
            fixture.trial, "post", [*writer_inputs, artifact("scene_draft", revised)], writer
        )
        replies[fixture.trial] = review_for(post_request, False)
    fixture.documents["prepared", "cases.json"] = {"fixture": True}
    fixture.documents["prepared", f"prepared/{initial_trial}.json"] = initial
    plan_record = {
        "experiment": experiment,
        "cases_sha256": hashlib.sha256(encoded({"fixture": True})).hexdigest(),
        "prepared_sha256": {initial_trial + ".json": hashlib.sha256(encoded(initial)).hexdigest()},
    }
    fixture.documents["prepared", "plan.json"] = plan_record
    plan_hash = hashlib.sha256(encoded(plan_record)).hexdigest()
    for trial, request in requests.items():
        n = 2 if retry and trial == initial_trial else 1
        fixture.documents["live", f"probes/{trial}/manifest.json"] = request["manifest"]
        fixture.documents["live", f"probes/{trial}/summary.json"] = {
            "status": "validated",
            "attempts": n,
        }
        raw, audit, result = replies[trial]
        for attempt in range(1, n + 1):
            content = json.dumps(raw)
            response_hash = hashlib.sha256(content.encode()).hexdigest()
            slot = f"{trial}-attempt-{attempt}.json"
            fixture.documents["live", "requests/" + slot] = deepcopy(request)
            fixture.documents["live", f"probes/{trial}/attempt-{attempt}-request.json"] = {
                "attempt": attempt,
                "messages": request["messages"],
                "response_schema": None,
                "prompt_sha256": request["prompt_sha256"],
            }
            receipt: dict[str, Any] = {
                "attempt": attempt,
                "status": "failed" if attempt < n else "validated",
                "prompt_sha256": request["prompt_sha256"],
                "response_sha256": response_hash,
                "response_length": len(content),
                "finish_reason": "stop",
                "input_tokens": 10,
                "output_tokens": 10,
            }
            if attempt < n:
                receipt["validation_issues"] = [
                    {"location": "fixture", "message": "Authored failure."}
                ]
            else:
                receipt["result"] = result
                if audit:
                    receipt["scene_boundary_audit"] = audit
            fixture.documents["live", f"probes/{trial}/attempt-{attempt}-result.json"] = receipt
            fixture.documents["live", f"probes/{trial}/attempt-{attempt}-model-output.json"] = {
                "content": content,
                "response_sha256": response_hash,
                "finish_reason": "stop",
                "model_identifier": "gemma4:31b-cloud",
                "provider": "ollama",
                "deployment": "cloud",
                "usage": {"input_tokens": 10, "output_tokens": 10},
                "cost_basis": "unknown",
                "estimated_cost_usd": "0",
            }
            fixture.documents["live", "reservations/" + slot] = {
                "trial": trial,
                "attempt": attempt,
                "plan_sha256": plan_hash,
                "request_sha256": hashlib.sha256(encoded(request)).hexdigest(),
                "prompt_sha256": request["prompt_sha256"],
            }
            fixture.documents["live", "outcomes/" + slot] = {
                "status": "returned",
                "response_sha256": response_hash,
                "input_tokens": 10,
                "output_tokens": 10,
            }
    return fixture
