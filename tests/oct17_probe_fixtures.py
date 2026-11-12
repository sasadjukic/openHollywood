"""Authored October 17 format fixtures. No unpublished prose or historical code."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.probe_review_evidence import (
    CONTRASTS,
    EDITS,
    OCT17_SELECTIONS,
    ProbeArchiveContract,
)
from open_hollywood_engine.evaluations.review_evidence import SavedMessage, messages_hash

from tests.probe_review_fixtures import ProbeFixture, encoded, make_probe_fixture


def refresh(fixture: ProbeFixture) -> ProbeArchiveContract:
    """Re-seal authored test data only, never available to the CLI."""
    docs = fixture.documents
    requests = [
        (name, body)
        for (area, name), body in docs.items()
        if area == "live" and name.startswith("requests/")
    ]
    for name, request in requests:
        trial = request["manifest"]["trial"]
        request["prompt_sha256"] = messages_hash(
            tuple(SavedMessage.model_validate(m) for m in request["messages"])
        )
        docs["live", f"probes/{trial}/manifest.json"] = deepcopy(request["manifest"])
        sent = docs["live", f"probes/{trial}/attempt-1-request.json"]
        if fixture.experiment == EDITS:
            docs["live", f"probes/{trial}/attempt-1-request.json"] = deepcopy(request)
        else:
            sent.update(messages=request["messages"], prompt_sha256=request["prompt_sha256"])
        receipt = docs["live", f"probes/{trial}/attempt-1-result.json"]
        capture = docs["live", f"probes/{trial}/attempt-1-model-output.json"]
        digest = hashlib.sha256(capture["content"].encode()).hexdigest()
        capture["response_sha256"] = digest
        receipt.update(prompt_sha256=request["prompt_sha256"], response_sha256=digest)
        if fixture.experiment == EDITS:
            receipt.pop("response_length", None)
            receipt.pop("finish_reason", None)
        else:
            receipt["response_length"] = len(capture["content"])
        docs["live", name.replace("requests/", "outcomes/")]["response_sha256"] = digest
        reservation = docs["live", name.replace("requests/", "reservations/")]
        reservation.update(
            request_sha256=hashlib.sha256(encoded(request)).hexdigest(),
            prompt_sha256=request["prompt_sha256"],
        )
        if request["manifest"]["stage"] != "post":
            docs["prepared", f"prepared/{trial}.json"] = deepcopy(request)
    plan = docs["prepared", "plan.json"]
    if fixture.experiment == CONTRASTS:
        plan["case_sha256"] = plan.pop("cases_sha256", plan.get("case_sha256"))
        plan["prepared_sha256"] = {
            name.removeprefix("prepared/"): hashlib.sha256(encoded(body)).hexdigest()
            for (area, name), body in docs.items()
            if area == "prepared" and name.startswith("prepared/")
        }
    else:
        plan.pop("cases_sha256", None)
        plan.pop("prepared_sha256", None)
        plan["file_sha256"] = {
            name: hashlib.sha256(encoded(body)).hexdigest()
            for (area, name), body in docs.items()
            if area == "prepared" and name != "plan.json"
        }
    plan_hash = hashlib.sha256(encoded(plan)).hexdigest()
    for (area, name), body in docs.items():
        if area == "live" and name.startswith("reservations/"):
            body["plan_sha256"] = plan_hash
    return fixture.seal()


def make_oct17(root: Path, mode: str) -> tuple[ProbeFixture, ProbeFixture | None]:
    original = make_probe_fixture(root, post=mode == "post")
    experiment = CONTRASTS if mode == "contrast" else EDITS
    initial_trial = OCT17_SELECTIONS[CONTRASTS][1]
    craft_trial = OCT17_SELECTIONS[EDITS][0]
    writer_trial = "s19401-elara-embedded-writer-E0"
    post_trial = OCT17_SELECTIONS[EDITS][1]
    replacements = {
        original.experiment: experiment,
        "s1-control-initial": craft_trial if mode == "craft" else initial_trial,
        "s1-control-writer-evidence": writer_trial,
        "s1-control-post-evidence": post_trial,
    }
    if mode == "post":
        writer = original.documents["live", "requests/s1-control-writer-evidence-attempt-1.json"]
        post = original.documents["live", "requests/s1-control-post-evidence-attempt-1.json"]
        for item, namespace in (
            (writer["inputs"][-1], "production-fulfillment-v61-2026-10-16"),
            (post["inputs"][-1], CONTRASTS),
        ):
            old = item["artifact_version_id"]
            new = str(
                uuid5(
                    NAMESPACE_URL,
                    f"{namespace}:AUTHORED-ONLY:{item['artifact_kind']}:"
                    f"{canonical_sha256(item['content'])}",
                )
            )
            replacements[old] = new
            replacements[old.replace("-", "")] = new.replace("-", "")
    docs: dict[tuple[str, str], dict[str, Any]] = {}
    for (area, name), body in original.documents.items():
        content = json.dumps(body)
        for old, new in replacements.items():
            name, content = name.replace(old, new), content.replace(old, new)
        docs[area, name] = json.loads(content)
    fixture = ProbeFixture(
        root,
        docs,
        experiment,
        post_trial if mode == "post" else craft_trial if mode == "craft" else initial_trial,
    )
    for (area, name), body in docs.items():
        if area != "live" or not name.startswith("requests/"):
            continue
        manifest = body["manifest"]
        if mode == "craft":
            manifest.update(
                stage="craft_source",
                arm="ordinary",
                block="craft",
                request_projection="ordinary_production",
            )
        elif manifest["stage"] == "initial":
            manifest.update(experiment=CONTRASTS, writer_source_policy=None)
        else:
            manifest.update(
                arm="E0",
                block="fixed_edits",
                request_projection="ordinary_production",
                writer_source_policy="fixed_saved_ordinary_review",
            )
    parent = None
    if mode == "post":
        parent_docs = {
            key: body
            for key, body in docs.items()
            if initial_trial in key[1] or key == ("prepared", "cases.json")
        }
        parent_docs["prepared", "plan.json"] = {
            "experiment": CONTRASTS,
            "cases_sha256": hashlib.sha256(
                encoded(parent_docs["prepared", "cases.json"])
            ).hexdigest(),
        }
        parent = ProbeFixture(root, deepcopy(parent_docs), CONTRASTS, initial_trial)
        fixture.documents = {key: body for key, body in docs.items() if initial_trial not in key[1]}
    return fixture, parent
