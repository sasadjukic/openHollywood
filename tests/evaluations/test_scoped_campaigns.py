"""Cloud-first matrices, evidence completeness and historical compatibility."""

from __future__ import annotations

import hashlib
from decimal import Decimal
from pathlib import Path
from typing import TypedDict
from uuid import UUID, uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.services.evaluation_campaign import _selected_agentic_cases
from open_hollywood_api.services.model_profiles import BUILTIN_PROFILE_IDS, ModelProfileStore
from open_hollywood_engine.evaluations import (
    BenchmarkCorpus,
    BenchmarkPlan,
    BenchmarkProfileSnapshot,
    BenchmarkRunReport,
    BenchmarkScope,
    BenchmarkSummary,
    BlindAnswerKey,
    BlindPublicBundle,
    HumanReviewBundle,
    build_benchmark_plan,
    build_blind_bundle,
    build_campaign_evidence_archive,
    canonical_sha256,
    load_benchmark_corpus,
    parse_review_csvs,
    render_review_csv,
    run_benchmark_plan,
    summarize_benchmark,
    verify_campaign_evidence_archive,
)
from open_hollywood_engine.models import (
    MODEL_PRESETS,
    ModelDeployment,
    ModelProfileConfiguration,
    ModelProfileMode,
    ModelSelection,
)
from sqlalchemy import Engine

from scripts.evaluation_harness import (
    _agentic_target_keys,
    _current_runtime_versions,
    create_plan_from_database,
    main,
)
from tests.evaluations.test_harness import FixtureExecutor, _complete_review_form
from tests.evaluations.test_harness import benchmark_plan as benchmark_plan

CORPUS_PATH = Path(__file__).resolve().parents[2] / "benchmarks/v0.1/corpus.json"
CAMPAIGN_ID = UUID("ac310000-0000-4000-8000-000000000001")


class EvidenceInputs(TypedDict):
    corpus: BenchmarkCorpus
    plan: BenchmarkPlan
    report: BenchmarkRunReport
    public_bundle: BlindPublicBundle
    answer_key: BlindAnswerKey
    reviews: HumanReviewBundle
    summary: BenchmarkSummary
    normal_cloud_run_budget_usd: Decimal


def cloud_plan(
    provider: str = "ollama", model: str = "cloud-fixture"
) -> tuple[BenchmarkCorpus, BenchmarkPlan]:
    corpus = load_benchmark_corpus(CORPUS_PATH)
    selection = ModelSelection(
        provider=provider, model_identifier=model, deployment=ModelDeployment.CLOUD
    )
    snapshot = BenchmarkProfileSnapshot.from_configuration(
        profile_id=BUILTIN_PROFILE_IDS[ModelProfileMode.CLOUD],
        configuration=MODEL_PRESETS[ModelProfileMode.CLOUD].configuration(cloud_model=selection),
    )
    return corpus, build_benchmark_plan(
        campaign_id=CAMPAIGN_ID,
        corpus=corpus,
        baseline_model=selection,
        profiles={ModelProfileMode.CLOUD: snapshot},
        workflow_versions=_current_runtime_versions(),
        scope=BenchmarkScope.CLOUD_FIRST,
    )


@pytest.mark.parametrize(
    ("provider", "model"),
    [
        ("ollama", "gemma-fixture"),
        ("openai", "future-gpt-fixture"),
        ("google", "future-gemini-fixture"),
    ],
)
def test_cloud_scope_preserves_provider_neutral_frozen_configuration(
    provider: str, model: str
) -> None:
    corpus, plan = cloud_plan(provider, model)
    assert len(plan.cases) == 24
    assert plan.schema_version == "2" and plan.scope is BenchmarkScope.CLOUD_FIRST
    assert plan.target_keys == ("baseline", "cloud")
    assert all(
        case.target_key == ("baseline" if i % 2 == 0 else "cloud")
        for i, case in enumerate(plan.cases)
    )
    plan.require_matching_corpus(corpus)
    assert BenchmarkPlan.model_validate_json(plan.model_dump_json()) == plan
    assert plan.cases[0].baseline_model is not None
    assert plan.cases[0].baseline_model.provider == provider
    assert plan.cases[0].baseline_model.model_identifier == model
    assert plan.cases[1].profile is not None
    selection = ModelProfileConfiguration.from_data(
        plan.cases[1].profile.configuration
    ).selection_for("scene_writer")
    assert selection.provider == provider and selection.model_identifier == model
    assert cloud_plan(provider, model)[1].content_sha256 == plan.content_sha256
    assert cloud_plan(provider, model + "-changed")[1].content_sha256 != plan.content_sha256


def test_cloud_planning_only_requires_cloud_configuration(
    migrated_database_path: Path,
    database_engine: Engine,
    tmp_path: Path,
) -> None:
    store = ModelProfileStore(create_session_factory(database_engine))
    store.configure_profile(
        BUILTIN_PROFILE_IDS[ModelProfileMode.CLOUD],
        local_model=None,
        cloud_model=ModelSelection(
            provider="ollama", model_identifier="cloud-fixture", deployment=ModelDeployment.CLOUD
        ),
    )
    output = tmp_path / "plan.json"
    assert (
        main(
            [
                "plan",
                "--scope",
                "cloud-first",
                "--database",
                str(migrated_database_path),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    plan = BenchmarkPlan.model_validate_json(output.read_bytes())
    assert len(plan.cases) == 24 and plan.scope is BenchmarkScope.CLOUD_FIRST
    assert plan.cases[0].baseline_model == plan.cases[2].baseline_model
    with pytest.raises(ValueError, match="complete"):
        create_plan_from_database(
            campaign_id=uuid4(), corpus_path=CORPUS_PATH, database_path=migrated_database_path
        )


def test_cloud_planning_still_requires_complete_cloud_profile(migrated_database_path: Path) -> None:
    with pytest.raises(ValueError, match="complete"):
        create_plan_from_database(
            campaign_id=uuid4(),
            corpus_path=CORPUS_PATH,
            database_path=migrated_database_path,
            scope=BenchmarkScope.CLOUD_FIRST,
        )


def test_scope_changes_defaults_but_cannot_silently_select_excluded_targets(tmp_path: Path) -> None:
    corpus, plan = cloud_plan()
    assert _agentic_target_keys(None, plan) == frozenset({"cloud"})
    selected = _selected_agentic_cases(plan, corpus, None)
    assert len(selected) == 12 and all(case.target_key == "cloud" for case in selected)
    with pytest.raises(ValueError, match="present in the campaign"):
        _selected_agentic_cases(plan, corpus, frozenset({"local", "cloud"}))
    path = tmp_path / "plan.json"
    path.write_text(plan.model_dump_json(), encoding="utf-8")
    with pytest.raises(ValueError, match="present in the campaign"):
        main(["prepare-agentic", "--plan", str(path), "--target", "local"])


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_scope",
        "missing_baseline",
        "missing_cloud",
        "duplicate_target",
        "wrong_scope",
        "legacy_scope",
    ],
)
def test_scoped_plan_rejects_ambiguous_or_incomplete_matrices(mutation: str) -> None:
    _, plan = cloud_plan()
    data = plan.model_dump(mode="json")
    if mutation == "missing_scope":
        data.pop("scope")
    elif mutation == "missing_baseline":
        data["cases"] = data["cases"][1:]
    elif mutation == "missing_cloud":
        data["cases"] = data["cases"][:-1]
    elif mutation == "duplicate_target":
        duplicate = dict(data["cases"][0], case_id=str(uuid4()))
        data["cases"].append(duplicate)
    elif mutation == "wrong_scope":
        data["scope"] = "all-profiles"
    else:
        data["schema_version"] = "1"
    with pytest.raises(ValueError):
        BenchmarkPlan.model_validate(data)


@pytest.mark.parametrize("mutation", ["missing_prompt", "changed_seed"])
@pytest.mark.anyio
async def test_scoped_plan_must_match_entire_frozen_corpus_before_execution(mutation: str) -> None:
    corpus, plan = cloud_plan()
    cases = (
        plan.cases[2:]
        if mutation == "missing_prompt"
        else (plan.cases[0].model_copy(update={"run_seed": 123}), *plan.cases[1:])
    )
    changed = plan.model_copy(update={"cases": cases})
    executor = FixtureExecutor()
    with pytest.raises(ValueError, match="scoped plan"):
        await run_benchmark_plan(plan=changed, corpus=corpus, executor=executor)
    assert executor.calls == []
    with pytest.raises(ValueError, match="scoped plan"):
        build_blind_bundle(
            plan=changed, corpus=corpus, results=(), blinding_key=b"0123456789abcdef"
        )


@pytest.mark.anyio
async def test_cloud_campaign_resumes_all_cases_packages_twelve_pairs_and_seals(
    tmp_path: Path,
) -> None:
    corpus, plan = cloud_plan()
    first = FixtureExecutor()
    partial = await run_benchmark_plan(
        plan=plan, corpus=corpus, executor=first, target_keys=frozenset({"cloud"})
    )
    assert len(partial.results) == 12
    resumed = FixtureExecutor()
    report = await run_benchmark_plan(
        plan=plan, corpus=corpus, executor=resumed, prior_results=partial.results
    )
    assert len(resumed.calls) == 12 and len(report.results) == 24
    public, answers = build_blind_bundle(
        plan=plan, corpus=corpus, results=report.results, blinding_key=b"0123456789abcdef"
    )
    assert len(public.comparisons) == 12
    assert "cloud-fixture" not in public.model_dump_json()
    reviews = parse_review_csvs(
        public, (_complete_review_form(render_review_csv(public, reviewer_id="fixture")),)
    )
    summary = summarize_benchmark(
        plan=plan, results=report.results, answer_key=answers, review_bundle=reviews
    )
    assert [m.target for m in summary.target_metrics] == ["baseline", "cloud"]
    assert all(m.technical_success_rate == 1 for m in summary.target_metrics)
    assert summary.criteria.technical_completion_at_least_95_percent is True
    inputs = EvidenceInputs(
        corpus=corpus,
        plan=plan,
        report=report,
        public_bundle=public,
        answer_key=answers,
        reviews=reviews,
        summary=summary,
        normal_cloud_run_budget_usd=Decimal("2.00"),
    )
    manifest, archive = build_campaign_evidence_archive(**inputs)
    assert manifest.planned_case_count == manifest.terminal_result_count == 24
    assert manifest.comparison_count == manifest.review_count == 12
    assert verify_campaign_evidence_archive(archive) == manifest
    assert build_campaign_evidence_archive(**inputs)[1] == archive
    archive_path = tmp_path / "evidence.zip"
    archive_path.write_bytes(archive)
    assert main(["verify-evidence", "--archive", str(archive_path)]) == 0
    for index in [0, 1]:  # Neither a baseline nor a Cloud result may be omitted.
        missing = report.model_copy(
            update={"results": report.results[:index] + report.results[index + 1 :]}
        )
        changed = inputs.copy()
        changed["report"] = missing
        with pytest.raises(ValueError, match="exactly one result per planned case"):
            build_campaign_evidence_archive(**changed)
    cloud_incomplete = summarize_benchmark(
        plan=plan, results=report.results[:1] + report.results[2:]
    )
    assert cloud_incomplete.criteria.technical_completion_at_least_95_percent is False
    assert (
        next(m for m in cloud_incomplete.target_metrics if m.target == "cloud").planned_cases == 12
    )
    # A self-consistently rehashed packet still cannot omit a required comparison.
    omitted = public.model_copy(update={"comparisons": public.comparisons[:-1]})
    omitted_answers = answers.model_copy(
        update={
            "answers": answers.answers[:-1],
            "public_bundle_sha256": canonical_sha256(omitted.model_dump(mode="json")),
        }
    )
    omitted_reviews = parse_review_csvs(
        omitted, (_complete_review_form(render_review_csv(omitted, reviewer_id="fixture")),)
    )
    changed = inputs.copy()
    changed["public_bundle"] = omitted
    changed["answer_key"] = omitted_answers
    changed["reviews"] = omitted_reviews
    with pytest.raises(ValueError, match="cover all scoped successful comparisons"):
        build_campaign_evidence_archive(**changed)
    # Rehashed replacement prose cannot masquerade as a generated story.
    first_pair = public.comparisons[0]
    replacement = "Substituted story."
    replacement_document = first_pair.candidate_a.model_copy(
        update={
            "content": replacement,
            "content_sha256": hashlib.sha256(replacement.encode()).hexdigest(),
        }
    )
    forged = public.model_copy(
        update={
            "comparisons": (
                first_pair.model_copy(update={"candidate_a": replacement_document}),
                *public.comparisons[1:],
            )
        }
    )
    forged_answers = answers.model_copy(
        update={"public_bundle_sha256": canonical_sha256(forged.model_dump(mode="json"))}
    )
    forged_reviews = parse_review_csvs(
        forged, (_complete_review_form(render_review_csv(forged, reviewer_id="fixture")),)
    )
    changed = inputs.copy()
    changed["public_bundle"] = forged
    changed["answer_key"] = forged_answers
    changed["reviews"] = forged_reviews
    with pytest.raises(ValueError, match="match exact scoped case outputs"):
        build_campaign_evidence_archive(**changed)


@pytest.mark.anyio
async def test_legacy_all_profile_plan_hash_summary_and_seal_are_preserved(
    benchmark_plan: tuple[BenchmarkCorpus, BenchmarkPlan],
) -> None:
    corpus, scoped = benchmark_plan
    legacy_data = scoped.model_dump(mode="json")
    legacy_data.pop("scope")
    legacy_data["schema_version"] = "1"
    expected_hash = canonical_sha256(legacy_data)
    plan = BenchmarkPlan.model_validate(legacy_data)
    assert plan.content_sha256 == expected_hash
    assert plan.model_dump(mode="json") == legacy_data
    assert BenchmarkPlan.model_validate_json(plan.model_dump_json()).content_sha256 == expected_hash
    report = await run_benchmark_plan(plan=plan, corpus=corpus, executor=FixtureExecutor())
    public, answers = build_blind_bundle(
        plan=plan, corpus=corpus, results=report.results, blinding_key=b"0123456789abcdef"
    )
    reviews = parse_review_csvs(
        public, (_complete_review_form(render_review_csv(public, reviewer_id="fixture")),)
    )
    summary = summarize_benchmark(
        plan=plan, results=report.results, answer_key=answers, review_bundle=reviews
    )
    assert len(summary.target_metrics) == 4 and len(public.comparisons) == 60
    inputs = EvidenceInputs(
        corpus=corpus,
        plan=plan,
        report=report,
        public_bundle=public,
        answer_key=answers,
        reviews=reviews,
        summary=summary,
        normal_cloud_run_budget_usd=Decimal("2.00"),
    )
    manifest, archive = build_campaign_evidence_archive(**inputs)
    assert verify_campaign_evidence_archive(archive) == manifest
    assert manifest.planned_case_count == 48
    cloud_only = report.model_copy(
        update={
            "results": tuple(
                r
                for r, c in zip(report.results, plan.cases, strict=True)
                if c.target_key == "cloud"
            )
        }
    )
    changed = inputs.copy()
    changed["report"] = cloud_only
    with pytest.raises(ValueError, match="exactly one result per planned case"):
        build_campaign_evidence_archive(**changed)
