# ADR 0040: Optional OpenAI Responses provider

- Status: Accepted
- Date: 2026-11-02
- Refines: ADR 0004, ADR 0006 and ADR 0017

## Context

The operator requested an additional OpenAI inference provider and explicitly
authorized reuse of the application-only Windows User `OPENAI_OH_KEY` plus one
small synthetic live check. This does not change the current evaluation campaign
or authorize another story. Runtime model selection must remain flexible enough
for future economical and premium comparisons.

## Decision

Add a concrete `httpx` Responses adapter behind `ModelGateway`, without a new
provider framework or SDK dependency. Route exact provider/deployment pairs in
the worker and frozen evaluation plans; do not infer the provider from model ID
prefixes. Existing single-provider gateways and Ollama deployment routing remain
compatible. Profiles and domain/workflow contracts contain no provider SDK types.

Resolve the existing `ModelSecret.OPENAI_API_KEY` handle from `OPENAI_OH_KEY`.
No credential is persisted or passed to the frontend. The existing environment
secret guard covers that value at persistence/export boundaries; the adapter
checks request and response payloads and emits normalized errors without raw
transport bodies. Windows User values are imported into process memory by the
operator, never copied into dotenv files or silently rewritten.

Intersect dynamic account discovery with explicit reviewed capabilities, limits,
allowed response model IDs and dated price records. Allow secret-free local
record extensions for new models. Strict-output models can be selected through
the existing Cloud and Hybrid profile UI; unknown IDs and unsupported model
settings fail closed. Persist effective settings and unsupported seed/sampling
omissions as provider metadata. Do not alter creative prompts or graph behavior.

Count input before generation; reserve the bounded output including reasoning
and conservative standard-tier cost before dispatch. Keep usage and estimates
on refusals, truncation and rejected responses. Retain published-rate estimates
as `unknown` actual cost under ADR 0017. Cache-write premiums are bounded
conservatively and long-context pricing is excluded by an input limit.

Use stateless `store=false`, no background job, disabled input truncation, no
tools and no provider-side conversation memory. Adapt closed structured schemas
at the transport boundary and retain application/domain validation. Do not
persist reasoning content. Apply existing bounded workflow retries only to
definite retryable rejections; uncertain transport failures do not auto-replay a
possibly billed call. Preserve cooperative cancellation and durable cleanup.

Usage details and transport metadata fit the existing invocation JSON alongside
the existing token/cost columns. There is no persisted schema change or migration.
Historical artifacts, prompts, evidence and selected profiles are untouched.

## Verification and limits

Mock transport tests cover mapping, pricing, reasoning, refusal, truncation,
normalized errors, secret safety, cancellation, model selection and budgets.
Real durable workflow tests with synthetic responses exercise OpenAI Cloud and
mixed-provider Hybrid, including the mandatory Blueprint approval boundary.
The single authorized live structured-output check succeeded with GPT-5.6 Luna;
details and setup are in [the provider guide](../openai-provider.md).

This adds provider capability, not production-quality qualification. Rate
records require review before future paid tests; discovered access does not
guarantee billing/permission availability. Remote cancellation and unknown
charges after transport interruption cannot be guaranteed by a local client.
Step 19 remains IN PROGRESS and Step 20 remains NOT STARTED.
