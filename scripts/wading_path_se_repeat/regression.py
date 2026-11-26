"""Replay the six observed Astra X deliveries against their sealed readings, offline."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require
from open_hollywood_engine.models.assessment_openai import map_response
from open_hollywood_engine.models.openai_catalog import OpenAIModelSpec

from scripts.ordinary_v61_capture import file_hash
from scripts.q008_sol_smoke import Terminal
from scripts.q010_uncertainty_plan import REPO, digest
from scripts.wading_path_observations.regression import inventory

from . import plan
from .rubric import Decisions

APPROVAL = "91d46c7d2e445a47d72ede07919e5a44c666aa987a3705cb4bdf9bb8013698c8"
READINGS_SHA = "342777e1f71431e637d3328d6435ff92f2f697588486d9db7635358fdbe98106"
ARCHIVE_SHA = "abd2159feb1abfd60e201f28991581353be52337ff050752a8d815285538e739"
ARCHIVE = plan.ROOT.parent / "wading-path-se-repeat-astra-x-regression-2026-11-26"
FIXTURE = REPO / "tests/fixtures/wading_path_se_repeat_astra_x_observed.json"


def selected_slots(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [s for s in manifest["slots"] if s["cell"].split("-")[1] == "AX"]


def stem(slot: dict[str, Any]) -> str:
    return f"output/{slot['slot']:02d}-{slot['cell']}-{slot['stage']}"


def verified(archive: Path) -> Path:
    capture = archive / "capture"
    manifest = (archive / "capture-manifest.json").read_bytes()
    require(digest(manifest) == ARCHIVE_SHA, "repeat_archive_seal")
    require(
        {k: file_hash(p) for k, p in inventory(capture).items()} == json.loads(manifest),
        "repeat_archive_members",
    )
    return capture


def preserve() -> None:
    if ARCHIVE.exists():
        verified(ARCHIVE)
        return
    source = plan.ROOT
    require(file_hash(source / "plan.json") == APPROVAL, "repeat_approval")
    members = ["plan.json", "drafts.json", "gold.json", "sealed-evidence-decisions.json"]
    for slot in selected_slots(json.loads((source / "plan.json").read_bytes())):
        prefix = stem(slot)
        members.extend((slot["filename"], prefix + "-intent.json", prefix + "-outcome.json"))
    with TemporaryDirectory(dir=ARCHIVE.parent) as tmp:
        staged = Path(tmp) / "archive"
        capture = staged / "capture"
        for name in members:
            target = capture / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, target)
        hashes = {k: file_hash(p) for k, p in inventory(capture).items()}
        (staged / "capture-manifest.json").write_bytes(encoded(hashes))
        verified(staged)
        staged.rename(ARCHIVE)


def replay(archive: Path = ARCHIVE) -> dict[str, Any]:
    root = verified(archive)
    plan_bytes = (root / "plan.json").read_bytes()
    sealed = (root / "sealed-evidence-decisions.json").read_bytes()
    require(
        digest(plan_bytes) == APPROVAL and digest(sealed) == READINGS_SHA, "repeat_registration"
    )
    manifest = json.loads(plan_bytes)
    form = Decisions.model_validate_json(sealed)
    require(form.approval_sha256 == APPROVAL, "repeat_grading_registration")
    gold = json.loads((root / "gold.json").read_bytes())
    drafts = json.loads((root / "drafts.json").read_bytes())
    spec = OpenAIModelSpec.model_validate(manifest["model_specs"]["A"])
    counts: dict[str, dict[str, Any]] = {}
    rows = {}
    for slot in selected_slots(manifest):
        name, stage = slot["cell"], slot["stage"]
        case = name.split("-")[0]
        prefix = stem(slot)
        request = (root / slot["filename"]).read_bytes()
        message = (root / (prefix + "-intent.json")).read_bytes()
        raw = (root / (prefix + "-outcome.json")).read_bytes()
        intent = json.loads(message)
        terminal = Terminal.model_validate_json(raw)
        require(
            intent["cell"] == name
            and digest(request) == intent["http_body_sha256"] == slot["body_bytes_sha256"]
            and intent["request_sha256"] == slot["native_request_sha256"]
            and terminal.intent_sha256 == digest(message)
            and terminal.http_status == 200
            and terminal.error is None,
            "repeat_slot_binding",
        )
        assert terminal.body is not None
        body = terminal.body.encode()
        require(digest(body) == terminal.raw_sha256, "repeat_response_body")
        mapped = map_response(stage, 200, body, spec)
        require(not mapped.issues and not mapped.error_codes, "repeat_mapping")
        receipt = dict(
            slot=slot["slot"], request_sha256=digest(request), terminal_sha256=digest(raw)
        )
        if stage == "input_count":
            require(mapped.state == "counted", "repeat_count")
            counts[name] = dict(**receipt, input_tokens=mapped.counted_input_tokens)
            continue
        require(
            mapped.state == "complete"
            and mapped.returned_model == "gpt-6.2-astra"
            and mapped.usage.input_tokens == counts[name]["input_tokens"],
            "repeat_generation",
        )
        assert mapped.raw_final is not None
        assessments = json.loads(mapped.raw_final)["assessments"]
        key, draft = gold[case], drafts[case]
        answer = assessments[key["unit"]]
        user = json.loads(json.loads(request)["input"][1]["content"])
        doc = next(
            d
            for d in user["native_work_view"]["context"]["documents"]
            if d["identity"] == draft["document_id"]
        )
        require(
            set(assessments) == {"A001"}
            and answer["evidence"] == [draft["ref"]] == ["E1420"]
            and user["claim_scope"]["statement"]["quote"] == key["claim"]
            and user["claim_scope"]["assessment_target"] == manifest["explicit_event_scope"]
            and doc["version"] == draft["document_version"] == key["draft_version"]
            and doc["structured_content"]["prose"] == draft["quote"]
            and digest(draft["quote"].encode()) == draft["field_sha256"] == key["prose_sha256"],
            "repeat_draft_binding",
        )
        answer_id = digest(encoded([intent["request_sha256"], mapped.raw_final]))
        scoring_id = digest(encoded([APPROVAL, terminal.intent_sha256, answer_id]))
        reading = form.decisions[scoring_id]
        require(
            reading.case == case
            and reading.reason_excerpt == answer["reason"]
            and reading.draft_excerpt in draft["quote"],
            "repeat_reading_binding",
        )
        rows[name] = dict(
            model=mapped.returned_model,
            reasoning=json.loads(request)["reasoning"]["effort"],
            unit=key["unit"],
            claim=key["claim"],
            draft_version=doc["version"],
            prose_sha256=key["prose_sha256"],
            citations=answer["evidence"],
            returned=answer["support"],
            gold=key["gold"],
            judgment="pass" if answer["support"] == key["gold"] else "fail",
            reason=answer["reason"],
            scoring_id=scoring_id,
            false_scene_wide_denial=reading.false_denial_excerpt is not None,
            **reading.model_dump(exclude={"reason_excerpt", "case"}),
            count=counts[name],
            generation=receipt,
            usage=mapped.usage.model_dump(mode="json"),
        )
    return dict(
        approval_sha256=APPROVAL,
        archive_sha256=ARCHIVE_SHA,
        evidence_decisions_sha256=READINGS_SHA,
        rows=rows,
    )


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--preserve", action="store_true")
    if cli.parse_args().preserve:
        preserve()
    require(encoded(replay()) == FIXTURE.read_bytes(), "repeat_portable_fixture")
    print("Verified the four SE repeats and both Astra X controls.")
