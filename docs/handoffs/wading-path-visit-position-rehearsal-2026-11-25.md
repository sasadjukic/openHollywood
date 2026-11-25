# The Wading Path · Rehearsal of a full-scene exclusion

**All ten grounded fixture answers earned both points.** On the new draft, an answer citing only the final three-stride gap earned **1 for judgment and 0 for evidence** when rejecting a visit during scene four. The identical answer earned **1 and 1** when rejecting presence at the housing at the cut. These are local authored responses. The previous Sol deliveries remain separately scored. [Rehearsal scores](../../data/diagnostics/wading-path-visit-position-rehearsal-2026-11-25/scores.json)

## Source and gold freeze

The two claims ask whether Elias and Maya reached the master breaker panel housing at some time during scene four, and whether both are there at the final narrated instant. The four existing drafts keep their exact versions and evidence criteria. The fifth preserves all 4,945 characters of the measured-stop draft, including the sentence placing both people three strides short and keeping them there. After a paragraph break, it adds this one retrospective observation:

> From the moment they huddled in the center of the flooded room to this last moment in the plenum, neither Elias nor Maya had ever been closer than three full strides to the master breaker panel housing.

The added paragraph occupies 4947–5149 in diagnostic version `4da86d35-9337-54d8-896b-c212ba05516c`. Offsets are zero-based and end-exclusive. It adds no movement. It supplies a continuous minimum distance extending back to the opening huddle. We froze all five source versions, both claims, ten labels and their evidence criteria before authoring answers. The gold SHA-256 is `77f6f1044007dbc79f0b31330b50c66b9beb9bd17ea2960087b0d4919eebc8e6`. [Frozen gold and criteria](../../tests/fixtures/wading_path_visit_position_gold.json) · [Freeze receipt](../../data/diagnostics/wading-path-visit-position-rehearsal-2026-11-25/gold-freeze.json) · [Complete diagnostic draft](../../data/diagnostics/wading-path-visit-position-rehearsal-2026-11-25/exclusion-source.json)

## Ten case scores

Each row gives the authored answer’s label, checked against frozen gold. Judgment earns one point for an exact match. Evidence earns a separate point when the explanation and cited prose establish the required person, place and time, or identify what the prose leaves open. Evidence was graded on a worksheet containing the claim, version, reason and resolved quotations with the returned label and fixture name hidden. The evidence decisions were sealed before joining the two scores. [Authored answers](../../tests/fixtures/wading_path_visit_position_answers.json) · [Masked worksheet](../../data/diagnostics/wading-path-visit-position-rehearsal-2026-11-25/masked-evidence.json) · [Evidence decisions](../../tests/fixtures/wading_path_visit_position_evidence.json)

| Draft | Claim | Gold and returned label | Judgment / 1 | Evidence / 1 |
| --- | --- | --- | ---: | ---: |
| Original | Visit during scene | Uncertain | 1 | 1 |
| Original | At housing at cut | Uncertain | 1 | 1 |
| Explicit arrival | Visit during scene | Supported | 1 | 1 |
| Explicit arrival | At housing at cut | Supported | 1 | 1 |
| Measured stop | Visit during scene | Uncertain | 1 | 1 |
| Measured stop | At housing at cut | Unsupported | 1 | 1 |
| Arrival then retreat | Visit during scene | Supported | 1 | 1 |
| Arrival then retreat | At housing at cut | Unsupported | 1 | 1 |
| Full-scene exclusion | Visit during scene | Unsupported | 1 | 1 |
| Full-scene exclusion | At housing at cut | Unsupported | 1 | 1 |

## What the final gap proves

The stress answer returned `unsupported` and cited only 4806–4945, the same verbatim paragraph in the measured-stop and exclusion drafts. Its entire reason was “Elias and Maya stop three full strides short of the housing and stay there through the cut.” The two visit rows below are additional answers to existing cases. The cut rows reuse their primary answers.

| Draft | Claim | Judgment / 1 | Evidence / 1 | Basis |
| --- | --- | ---: | ---: | --- |
| Measured stop | Visit during scene | 0 | 0 | An earlier visit remains open. The final gap covers only the endpoint. |
| Full-scene exclusion | Visit during scene | 1 | 0 | The added paragraph rules out a visit. The answer neither cites nor explains that interval. |
| Measured stop | At housing at cut | 1 | 1 | Both people stop short and stay there. |
| Full-scene exclusion | At housing at cut | 1 | 1 | The same persistent gap covers the cut. The retrospective adds no subsequent motion. |

The grounded exclusion answer earned its evidence point by citing the opening huddle (0–488) and the new paragraph (4947–5149). A separate label-only test changed its judgment to `uncertain` while holding the claims, citations, reason and evidence decision fixed. Judgment fell to 0 and evidence stayed at 1. The five passing observed controls also replayed with both points. The observed R1 and P1 failures on the original retained zero on each axis. [Earlier live results](wading-path-three-claims-sol-high-results-2026-11-24.md) · [Local scorer and replay](../../scripts/wading_path_three_claims/visit_position.py)

## Verification and readiness

With the private source archive available, run `python -m scripts.wading_path_three_claims.visit_position` using the repository interpreter. All 52 focused tests passed. They check both scores, exact source versions and spans, the unchanged parent prefix, and rejection of altered gold, stale versions, missing claims and unreviewed citations. Repository-wide Ruff lint, formatting and strict mypy passed across 447 Python files. The rehearsal made zero provider calls. [Regression tests](../../tests/evaluations/test_wading_path_visit_position_rehearsal.py) · [Verification record](../../data/diagnostics/wading-path-visit-position-rehearsal-2026-11-25/verified.xml)

**Ready to freeze a bounded Sol-high B comparison.** Use the measured stop, full-scene exclusion and explicit arrival, with one request per claim on each draft. The first pair tests whether Sol changes only the visit judgment when the evidence gains scene-wide coverage. The arrival control requires affirmative evidence for both claims and exposes a default negative answer. This gives six counts before up to six generations, zero retries, subject to a separate request freeze and approval. Require both scores on every eligible answer. A correct negative supported only by the final gap continues to fail evidence for the visit. The original R1 and P1 would need their own later reassessment to establish recovery. B remains the default, production prompts are unchanged and the full workflow canary stays on hold.
