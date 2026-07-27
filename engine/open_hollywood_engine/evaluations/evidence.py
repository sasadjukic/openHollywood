"""Deterministic, tamper-evident preservation of formal campaign evidence."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from enum import StrEnum
from io import BytesIO
from typing import Annotated, Literal, Self
from uuid import UUID
from zipfile import ZIP_STORED, BadZipFile, ZipFile, ZipInfo

from pydantic import Field, StringConstraints, model_validator

from open_hollywood_engine.evaluations.contracts import (
    BenchmarkCorpus,
    BenchmarkPlan,
    BenchmarkRunReport,
    BenchmarkSummary,
    BlindAnswerKey,
    BlindPublicBundle,
    EvaluationModel,
    HumanReviewBundle,
    Sha256,
    canonical_sha256,
)
from open_hollywood_engine.evaluations.reporting import summarize_benchmark

EVIDENCE_SCHEMA_VERSION: Literal["1"] = "1"
UsdAmount = Annotated[str, StringConstraints(pattern=r"^\d+(\.\d+)?$")]


class EvidenceConfidentiality(StrEnum):
    """Audience boundary for one archived evidence member."""

    PUBLIC = "public"
    PRIVATE = "private"


class EvidenceRole(StrEnum):
    """Required semantic files in one sealed campaign archive."""

    CORPUS = "corpus"
    PLAN = "plan"
    REPORT = "report"
    PUBLIC_BUNDLE = "public_bundle"
    ANSWER_KEY = "answer_key"
    REVIEWS = "reviews"
    SUMMARY = "summary"


_EVIDENCE_LAYOUT: dict[EvidenceRole, tuple[str, EvidenceConfidentiality]] = {
    EvidenceRole.CORPUS: ("public/corpus.json", EvidenceConfidentiality.PUBLIC),
    EvidenceRole.PUBLIC_BUNDLE: (
        "public/blind-comparisons.json",
        EvidenceConfidentiality.PUBLIC,
    ),
    EvidenceRole.PLAN: ("private/campaign-plan.json", EvidenceConfidentiality.PRIVATE),
    EvidenceRole.REPORT: ("private/campaign-report.json", EvidenceConfidentiality.PRIVATE),
    EvidenceRole.ANSWER_KEY: ("private/blind-answer-key.json", EvidenceConfidentiality.PRIVATE),
    EvidenceRole.REVIEWS: ("private/human-reviews.json", EvidenceConfidentiality.PRIVATE),
    EvidenceRole.SUMMARY: ("private/campaign-summary.json", EvidenceConfidentiality.PRIVATE),
}
_EVIDENCE_ROLE_ORDER = tuple(_EVIDENCE_LAYOUT)
_MANIFEST_PATH = "manifest.json"


class CampaignEvidenceFile(EvaluationModel):
    """Digest and audience metadata for one exact archive member."""

    role: EvidenceRole
    archive_path: str
    confidentiality: EvidenceConfidentiality
    size_bytes: int = Field(ge=1)
    sha256: Sha256

    @model_validator(mode="after")
    def validate_layout(self) -> Self:
        expected_path, expected_confidentiality = _EVIDENCE_LAYOUT[self.role]
        if (
            self.archive_path != expected_path
            or self.confidentiality is not expected_confidentiality
        ):
            raise ValueError("campaign evidence file does not match the registered layout")
        return self


class CampaignEvidenceManifest(EvaluationModel):
    """Self-describing seal for a complete formal campaign evidence set."""

    schema_version: Literal["1"]
    campaign_id: UUID
    corpus_id: str
    corpus_version: str
    corpus_sha256: Sha256
    plan_sha256: Sha256
    public_bundle_sha256: Sha256
    normal_cloud_run_budget_usd: UsdAmount
    planned_case_count: int = Field(ge=1)
    terminal_result_count: int = Field(ge=1)
    successful_case_count: int = Field(ge=0)
    comparison_count: int = Field(ge=1)
    review_count: int = Field(ge=1)
    reviewer_count: int = Field(ge=1)
    files: tuple[CampaignEvidenceFile, ...]

    @model_validator(mode="after")
    def validate_files(self) -> Self:
        if tuple(file.role for file in self.files) != _EVIDENCE_ROLE_ORDER:
            raise ValueError("campaign evidence manifest must contain every file in stable order")
        if len({file.archive_path for file in self.files}) != len(self.files):
            raise ValueError("campaign evidence archive paths must be unique")
        if self.terminal_result_count != self.planned_case_count:
            raise ValueError("formal campaign evidence requires a terminal result for every case")
        return self

    @property
    def content_sha256(self) -> str:
        """Return the canonical digest of the manifest itself."""
        return canonical_sha256(self.model_dump(mode="json"))


def build_campaign_evidence_archive(
    *,
    corpus: BenchmarkCorpus,
    plan: BenchmarkPlan,
    report: BenchmarkRunReport,
    public_bundle: BlindPublicBundle,
    answer_key: BlindAnswerKey,
    reviews: HumanReviewBundle,
    summary: BenchmarkSummary,
    normal_cloud_run_budget_usd: Decimal,
) -> tuple[CampaignEvidenceManifest, bytes]:
    """Validate, canonically encode, and seal one complete campaign."""
    documents = _validated_documents(
        corpus=corpus,
        plan=plan,
        report=report,
        public_bundle=public_bundle,
        answer_key=answer_key,
        reviews=reviews,
        summary=summary,
        normal_cloud_run_budget_usd=normal_cloud_run_budget_usd,
    )
    encoded = {role: _canonical_json_bytes(document) for role, document in documents.items()}
    manifest = _manifest(
        corpus=corpus,
        plan=plan,
        report=report,
        public_bundle=public_bundle,
        answer_key=answer_key,
        reviews=reviews,
        normal_cloud_run_budget_usd=normal_cloud_run_budget_usd,
        encoded=encoded,
    )
    archive = BytesIO()
    with ZipFile(archive, mode="w", compression=ZIP_STORED) as target:
        _write_member(
            target,
            _MANIFEST_PATH,
            _canonical_json_bytes(manifest),
            confidentiality=EvidenceConfidentiality.PUBLIC,
        )
        for role in _EVIDENCE_ROLE_ORDER:
            path, confidentiality = _EVIDENCE_LAYOUT[role]
            _write_member(
                target,
                path,
                encoded[role],
                confidentiality=confidentiality,
            )
    return manifest, archive.getvalue()


def verify_campaign_evidence_archive(
    archive: bytes,
) -> CampaignEvidenceManifest:
    """Verify member hashes and all cross-document campaign invariants."""
    try:
        with ZipFile(BytesIO(archive), mode="r") as source:
            names = source.namelist()
            expected_names = [
                _MANIFEST_PATH,
                *(_EVIDENCE_LAYOUT[role][0] for role in _EVIDENCE_ROLE_ORDER),
            ]
            if names != expected_names or len(set(names)) != len(names):
                raise ValueError("campaign evidence archive has an unexpected member layout")
            raw_manifest = source.read(_MANIFEST_PATH)
            manifest = CampaignEvidenceManifest.model_validate_json(raw_manifest)
            members = {file.role: source.read(file.archive_path) for file in manifest.files}
    except (BadZipFile, KeyError, json.JSONDecodeError) as error:
        raise ValueError("campaign evidence archive is invalid") from error

    for file in manifest.files:
        content = members[file.role]
        if len(content) != file.size_bytes or hashlib.sha256(content).hexdigest() != file.sha256:
            raise ValueError(f"campaign evidence member {file.archive_path!r} failed its digest")

    corpus = BenchmarkCorpus.model_validate_json(members[EvidenceRole.CORPUS])
    plan = BenchmarkPlan.model_validate_json(members[EvidenceRole.PLAN])
    report = BenchmarkRunReport.model_validate_json(members[EvidenceRole.REPORT])
    public_bundle = BlindPublicBundle.model_validate_json(members[EvidenceRole.PUBLIC_BUNDLE])
    answer_key = BlindAnswerKey.model_validate_json(members[EvidenceRole.ANSWER_KEY])
    reviews = HumanReviewBundle.model_validate_json(members[EvidenceRole.REVIEWS])
    summary = BenchmarkSummary.model_validate_json(members[EvidenceRole.SUMMARY])
    budget = Decimal(manifest.normal_cloud_run_budget_usd)
    expected_manifest, expected_archive = build_campaign_evidence_archive(
        corpus=corpus,
        plan=plan,
        report=report,
        public_bundle=public_bundle,
        answer_key=answer_key,
        reviews=reviews,
        summary=summary,
        normal_cloud_run_budget_usd=budget,
    )
    if manifest != expected_manifest or archive != expected_archive:
        raise ValueError("campaign evidence archive is not in canonical sealed form")
    return manifest


def _validated_documents(
    *,
    corpus: BenchmarkCorpus,
    plan: BenchmarkPlan,
    report: BenchmarkRunReport,
    public_bundle: BlindPublicBundle,
    answer_key: BlindAnswerKey,
    reviews: HumanReviewBundle,
    summary: BenchmarkSummary,
    normal_cloud_run_budget_usd: Decimal,
) -> dict[EvidenceRole, EvaluationModel]:
    if normal_cloud_run_budget_usd < 0:
        raise ValueError("normal cloud run budget must not be negative")
    if (
        plan.corpus_id != corpus.corpus_id
        or plan.corpus_version != corpus.corpus_version
        or plan.corpus_sha256 != corpus.content_sha256
    ):
        raise ValueError("campaign plan does not match the frozen corpus")
    if report.campaign_id != plan.campaign_id or report.plan_sha256 != plan.content_sha256:
        raise ValueError("campaign report does not match the plan")
    planned_ids = {case.case_id for case in plan.cases}
    result_ids = {result.case_id for result in report.results}
    if len(result_ids) != len(report.results) or result_ids != planned_ids:
        raise ValueError("formal campaign report needs exactly one result per planned case")
    if public_bundle.campaign_id != plan.campaign_id:
        raise ValueError("public review packet belongs to a different campaign")
    public_digest = canonical_sha256(public_bundle.model_dump(mode="json"))
    if (
        answer_key.campaign_id != plan.campaign_id
        or answer_key.public_bundle_sha256 != public_digest
    ):
        raise ValueError("private answer key does not match the public review packet")
    comparison_ids = {comparison.comparison_id for comparison in public_bundle.comparisons}
    answer_ids = {answer.comparison_id for answer in answer_key.answers}
    if (
        not comparison_ids
        or len(comparison_ids) != len(public_bundle.comparisons)
        or len(answer_ids) != len(answer_key.answers)
        or answer_ids != comparison_ids
    ):
        raise ValueError("public comparisons and private answers must match exactly")
    if reviews.campaign_id != plan.campaign_id or reviews.public_bundle_sha256 != public_digest:
        raise ValueError("human reviews do not match the public review packet")
    reviewed_ids = {review.comparison_id for review in reviews.reviews}
    if reviewed_ids != comparison_ids:
        raise ValueError("formal evidence needs at least one human review per comparison")
    expected_summary = summarize_benchmark(
        plan=plan,
        results=report.results,
        answer_key=answer_key,
        review_bundle=reviews,
        normal_cloud_run_budget_usd=float(normal_cloud_run_budget_usd),
    )
    if summary != expected_summary:
        raise ValueError("campaign summary does not match the sealed evidence")
    return {
        EvidenceRole.CORPUS: corpus,
        EvidenceRole.PLAN: plan,
        EvidenceRole.REPORT: report,
        EvidenceRole.PUBLIC_BUNDLE: public_bundle,
        EvidenceRole.ANSWER_KEY: answer_key,
        EvidenceRole.REVIEWS: reviews,
        EvidenceRole.SUMMARY: summary,
    }


def _manifest(
    *,
    corpus: BenchmarkCorpus,
    plan: BenchmarkPlan,
    report: BenchmarkRunReport,
    public_bundle: BlindPublicBundle,
    answer_key: BlindAnswerKey,
    reviews: HumanReviewBundle,
    normal_cloud_run_budget_usd: Decimal,
    encoded: dict[EvidenceRole, bytes],
) -> CampaignEvidenceManifest:
    files = tuple(
        CampaignEvidenceFile(
            role=role,
            archive_path=_EVIDENCE_LAYOUT[role][0],
            confidentiality=_EVIDENCE_LAYOUT[role][1],
            size_bytes=len(encoded[role]),
            sha256=hashlib.sha256(encoded[role]).hexdigest(),
        )
        for role in _EVIDENCE_ROLE_ORDER
    )
    reviewer_ids = {review.reviewer_id for review in reviews.reviews}
    return CampaignEvidenceManifest(
        schema_version=EVIDENCE_SCHEMA_VERSION,
        campaign_id=plan.campaign_id,
        corpus_id=corpus.corpus_id,
        corpus_version=corpus.corpus_version,
        corpus_sha256=corpus.content_sha256,
        plan_sha256=plan.content_sha256,
        public_bundle_sha256=answer_key.public_bundle_sha256,
        normal_cloud_run_budget_usd=format(normal_cloud_run_budget_usd, "f"),
        planned_case_count=len(plan.cases),
        terminal_result_count=len(report.results),
        successful_case_count=sum(result.output is not None for result in report.results),
        comparison_count=len(public_bundle.comparisons),
        review_count=len(reviews.reviews),
        reviewer_count=len(reviewer_ids),
        files=files,
    )


def _canonical_json_bytes(document: EvaluationModel) -> bytes:
    return (
        json.dumps(
            document.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _write_member(
    archive: ZipFile,
    path: str,
    content: bytes,
    *,
    confidentiality: EvidenceConfidentiality,
) -> None:
    info = ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_STORED
    info.create_system = 3
    mode = 0o644 if confidentiality is EvidenceConfidentiality.PUBLIC else 0o600
    info.external_attr = (0o100000 | mode) << 16
    archive.writestr(info, content)
