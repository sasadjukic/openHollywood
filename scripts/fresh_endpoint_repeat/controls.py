"""Verify the eight sealed endpoint controls and build local work previews. No provider calls."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from open_hollywood_engine.evaluations.assessment_authored_source import _document
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceLocation,
    EvidenceRegistry,
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentContext,
    AssessmentWork,
    ReportField,
    SelectedStatement,
    partition_work,
)
from open_hollywood_engine.evaluations.assessment_work_brief import AuthoredWorkBrief
from open_hollywood_engine.evaluations.review_evidence import (
    SavedMessage,
    require,
    text_hash,
)

from scripts.verify_q010_endpoint_controls import Packet as Packet

ROOT = Path(__file__).resolve().parents[2] / "data/diagnostics/q010-fresh-controls-2026-11-23"
SEAL = "3d8fbde2a94e340d2c46a938b53d27b3d3ca06e44f110f577e99a44b23c9d3bc"


def work_brief(packet: Packet) -> AuthoredWorkBrief:
    questions = {
        "The Vermilion Pouch": (
            "Has Lale stamped the routing slip, and is the vermilion pouch in the receiving pan "
            "when the closing bell rings?"
        ),
        "The Nicked Composing Stick": (
            "Has Orsa broken the blue seal, and is Neri holding the nicked composing stick "
            "when the skylight shutters meet?"
        ),
    }
    return AuthoredWorkBrief(
        unit_id=packet.claim_id,
        question=questions[packet.title],
        temporal_scope=packet.instant,
        source_authority=packet.authority,
        evidence_obligation="Locate the evidence for each part and explain what it establishes.",
    )


def native_work(packet: Packet, digest: str) -> AssessmentWork:
    """Accept only reader-visible source material. Scorer gold is a separate file."""
    docs = []
    entries = []
    for src in packet.sources:
        require(text_hash(src.text) == src.text_sha256, "control_source_hash")
        doc = _document(src.ref, "source", {"role": src.role, "text": src.text}).model_copy(
            update={"version": src.version}
        )
        docs.append(doc)
        entries.append(
            EvidenceLocation(
                ref=src.ref,
                document_id=doc.identity,
                document_version=doc.version,
                document_sha256=doc.content_sha256,
                field_pointer="/text",
                field_sha256=src.text_sha256,
                start=0,
                end=len(src.text),
                quote=src.text,
            )
        )
    field = ReportField(field_id=packet.claim_id, pointer="/claim", text=packet.claim)
    registry = EvidenceRegistry(entries=tuple(entries))
    context = AssessmentContext(
        provenance="synthetic_fixture",
        origin_sha256=digest,
        documents=(
            *docs,
            _document("report", "report", {"claim": packet.claim}),
            _document("registry", "registry", registry.model_dump(mode="json")),
        ),
        report_fields=(field,),
        statements=(
            SelectedStatement(
                unit_id=field.field_id,
                field_id=field.field_id,
                start=0,
                end=len(field.text),
                quote=field.text,
            ),
        ),
        messages=(
            SavedMessage(
                role="user",
                content=encoded(
                    {
                        "packet": packet.model_dump(mode="json"),
                        "work_brief": work_brief(packet).model_dump(mode="json"),
                    }
                ).decode(),
            ),
        ),
    )
    return partition_work(context, 1)


def verify(frozen: Path = ROOT / "frozen") -> dict[str, object]:
    seal_bytes = (frozen / "seal.json").read_bytes()
    require(hashlib.sha256(seal_bytes).hexdigest() == SEAL, "control_seal")
    seal = json.loads(seal_bytes)
    gold_bytes = (frozen / "gold.json").read_bytes()
    require(hashlib.sha256(gold_bytes).hexdigest() == seal["gold_sha256"], "control_gold_hash")
    require(
        hashlib.sha256((frozen / "scoring.json").read_bytes()).hexdigest()
        == seal["scoring_sha256"],
        "scoring_drift",
    )
    gold = json.loads(gold_bytes)
    keys = {f"R{i:02d}" for i in range(1, 9)}
    require(
        set(seal["packets_sha256"]) == keys
        and {p.name for p in (frozen / "packets").iterdir()} == {k + ".json" for k in keys}
        and len(gold["cases"]) == 8
        and {r["case_id"] for r in gold["cases"]} == keys,
        "control_inventory",
    )
    dispositions = {
        "confirmed": "supported",
        "contradicted": "unsupported",
        "unresolved": "uncertain",
        "missing_source": "uncertain",
    }
    matrix = Counter((r["family"], r["state"]) for r in gold["cases"])
    require(matrix == Counter((f, s) for f in ("D", "T") for s in dispositions), "control_matrix")
    fingerprints = {}
    for row in gold["cases"]:
        key = row["case_id"]
        raw = (frozen / "packets" / (key + ".json")).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        require(
            digest == seal["packets_sha256"][key] == row["packet_sha256"], "control_packet_hash"
        )
        packet = Packet.model_validate_json(raw)
        require(
            packet.case_id == key
            and packet.instant == row["instant"]
            and packet.scene_draft_version == row["scene_draft_version"]
            and packet.claim == row["claim"]
            and row["first_component"] == "established"
            and len(row["propositions"]) == 2
            and row["whole_claim_gold"] == dispositions[row["state"]],
            "control_claim_binding",
        )
        work = native_work(packet, digest)
        (batch,) = work.batches
        scope = scope_for_batch(work, batch.batch_id, digest)
        schema = json.loads(encoded(assessment_response_schema(work, scope)))
        assessments = schema["properties"]["assessments"]
        require(
            scope.active_unit_ids == (packet.claim_id,)
            and assessments["required"] == [packet.claim_id]
            and set(assessments["properties"]) == {packet.claim_id},
            "control_scope",
        )
        sources = {src.ref: src for src in packet.sources}
        item = assessments["properties"][packet.claim_id]["properties"]
        require(
            set(item["support"]["enum"]) == {"supported", "unsupported", "uncertain"}
            and set(item["evidence"]["items"]["enum"]) == set(sources),
            "control_schema",
        )
        missing = row["state"] == "missing_source"
        require(
            set(sources) == ({"S01", "S03"} if missing else {"S01", "S02", "S03"})
            and sources["S01"].role == "prior eyewitness account"
            and sources["S03"].role == "source inventory"
            and (missing or sources["S02"].version == packet.scene_draft_version)
            and row["second_witness"]["ref"] == ("S03" if missing else "S02")
            and {w["ref"] for w in row["first_witness_any"]}
            == ({"S01"} if missing else {"S01", "S02"}),
            "control_availability_or_coverage",
        )
        for w in [*row["first_witness_any"], row["second_witness"]]:
            src = sources[w["ref"]]
            require(
                src.version == w["version"]
                and 0 <= w["start"] < w["end"] <= len(src.text)
                and src.text[w["start"] : w["end"]] == w["quote"],
                "control_witness",
            )
        end = row["second_witness"]
        require(end["end"] == len(sources[end["ref"]].text), "control_wrong_instant")
        fingerprints[key] = work.fingerprint
    return {
        "seal_sha256": SEAL,
        "gold_sha256": seal["gold_sha256"],
        "scoring_sha256": seal["scoring_sha256"],
        "native_work_sha256": fingerprints,
        "labels": dict(Counter(r["whole_claim_gold"] for r in gold["cases"])),
        "live_calls": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
