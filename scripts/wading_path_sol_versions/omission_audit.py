"""Read the paired explanations, claim scopes and prefix metadata without provider access."""

from __future__ import annotations

import json
from os.path import commonprefix
from pathlib import Path
from typing import Any

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.ordinary_v61_capture import file_hash

from . import plan, regression


def audit(archive: Path = regression.ARCHIVE) -> dict[str, Any]:
    capture = regression.verified(archive)
    run = capture / "run"
    scores = json.loads((capture / "operator/scores.json").read_bytes())
    sheet = json.loads((capture / "operator/evidence-sheet.json").read_bytes())["rows"]
    reasons = {r["scoring_id"]: r for r in sheet}
    terminals = json.loads((capture / "operator/audit.json").read_bytes())["slots"]
    key = json.loads((run / "gold.json").read_bytes())
    locations = json.loads((capture / "operator/cited-locations.json").read_bytes())
    rows, inputs, wire = {}, {}, {}
    for slot in terminals:
        if not slot["eligible"]:
            continue
        name = slot["cell"]
        case, arm = name.split("-")
        gen = json.loads((run / f"requests/{name}-generation.json").read_bytes())
        count = json.loads((run / f"requests/{name}-input_count.json").read_bytes())
        require(
            count == {k: gen[k] for k in ("model", "input", "text", "reasoning")},
            "prefix_count_drift",
        )
        (terminal,) = (run / "output").glob(f"*-{name}-generation-outcome.json")
        raw = json.loads(json.loads(terminal.read_bytes())["body"])
        history = gen["input"]
        user = json.loads(history[1]["content"])
        inputs[name] = history
        scope = user["claim_scope"]
        decision = scores["rows"][name]
        explanation = reasons[slot["scoring_id"]]
        loc = locations[case]["E1420"]
        require(
            scope["statement"]["quote"] == key[case]["claim"]
            and loc["document_version"] == key[case]["draft_version"]
            and explanation["case"] == case
            and explanation["citations"] == ["E1420"]
            and raw["model"] == gen["model"] == plan.MODELS[arm],
            "sol_pair_binding",
        )
        rows[name] = dict(
            model=raw["model"],
            claim=key[case]["claim"],
            draft_version=loc["document_version"],
            gold=key[case]["gold"],
            returned=decision["returned"],
            judgment=decision["judgment"],
            evidence=decision["evidence"],
            reason=explanation["reason"],
            citations=explanation["citations"],
            evidence_basis=decision["basis"],
            generation_terminal_sha256=file_hash(terminal),
        )
        details = raw["usage"]["input_tokens_details"]
        wire[name] = dict(
            input_roles=[i.get("role") for i in history],
            input_item_types=[i.get("type") for i in history],
            request_fields=sorted(gen),
            system_sha256=canonical_sha256(history[0]),
            schema_sha256=canonical_sha256(gen["text"]),
            reasoning=gen["reasoning"],
            store=gen["store"],
            truncation=gen["truncation"],
            claim_predicates=scope["claim_predicates"],
            evidence_predicates=scope["evidence_predicates"],
            unresolved_qualifiers=scope["unresolved_qualifiers"],
            brief=user["work_brief"],
            source_scopes=scope["source_scopes"],
            input_transformations=raw.get("input_transformations"),
            has_cache_diagnostics="prompt_cache_diagnostics" in raw,
            output_item_types=[i["type"] for i in raw["output"]],
            encrypted_reasoning_items=sum(
                i["type"] == "reasoning" and bool(i.get("encrypted_content")) for i in raw["output"]
            ),
            cached_read_tokens=details["cached_tokens"],
            cache_write_tokens=details["cache_write_tokens"],
        )

    pairs = {}
    for narration, event in (("SN", "SE"), ("XN", "XE"), ("VN", "VE")):
        require(
            all(inputs[case + "-61"] == inputs[case + "-62"] for case in (narration, event)),
            "paired_content",
        )
        a, b = (inputs[k + "-61"] for k in (narration, event))
        require(a[0] == b[0], "instruction_drift")
        pairs[narration + "/" + event] = dict(
            system_chars=len(a[0]["content"]),
            shared_user_chars=len(commonprefix([a[1]["content"], b[1]["content"]])),
            narration_user_chars=len(a[1]["content"]),
            event_user_chars=len(b[1]["content"]),
        )
    return dict(
        archive_sha256=regression.SEAL,
        live_calls=0,
        observations=dict(
            approval_sha256=regression.APPROVAL,
            evidence_decisions_sha256=regression.EVIDENCE_SEAL,
            rows=rows,
        ),
        request_audit=wire,
        within_history_prefix=pairs,
    )
