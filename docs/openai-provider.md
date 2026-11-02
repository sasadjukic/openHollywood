# OpenAI inference alongside Ollama

OpenAI is an optional cloud provider. Existing selections, production prompts,
graph versions, benchmark evidence and the mandatory Story Blueprint approval
remain unchanged. Adding a provider does not authorize a story run or campaign.

## Windows runtime setup

The stable `ModelSecret.OPENAI_API_KEY` handle resolves **`OPENAI_OH_KEY`** for this
application. The ordinary `OPENAI_API_KEY` variable is not used for inference.
Credentials are resolved only by the backend transport. Never put them in Vite
configuration, model-profile JSON, a source file, a dotenv file or a prompt.

New Windows processes inherit their parent's environment. An existing terminal,
IDE, Codex process or worker may not see a newly set Windows User variable.
Restart the parent application, or import the existing User value into the API
terminal's process memory before starting the worker:

```powershell
$env:OPENAI_OH_KEY = [Environment]::GetEnvironmentVariable('OPENAI_OH_KEY', 'User')
uv run --extra api uvicorn open_hollywood_worker.app:app --reload
```

This reads the existing variable without displaying it, changing its stored
Windows value or writing a file. Restart the API/worker after changing its model
configuration. The frontend needs no credential or provider environment variable.
Ollama Local and signed-in local Ollama Cloud keep their existing behavior.
Direct Ollama Cloud catalog discovery still uses `OLLAMA_API_KEY`.

## Select or change models

Open the workspace's model settings. The cloud dropdown now labels each entry
with its provider. Choose **Cloud** to route all specialists to an OpenAI model,
or **Hybrid** to combine an Ollama local model with an OpenAI cloud model. Select
the required slots and click **Use Cloud**, **Use Hybrid**, or **Save active preset**.
Choose an `ollama` entry to switch back. Saving a preset affects new runs;
existing runs retain their frozen model configuration.

`GET /api/v1/models/catalog` combines independent sources. An unavailable provider
does not hide working sources. OpenAI results intersect account-visible model IDs
with reviewed text-generation, structured-output, limits and pricing records.
Listing a model does not prove that a generation will succeed under the account's
billing limits, regional access or permissions.

Reviewed IDs as of 2026-11-02:

| Models | Effective default reasoning | Notes |
|---|---|---|
| `gpt-5.6-luna` | `none` | Economical connectivity test model |
| `gpt-6.1-sol` | `low` | Premium model; does not support disabling reasoning |
| `gpt-5.4`, `gpt-5.4-2026-03-05` | `none` | Alias and exact snapshot |
| `gpt-5.4-nano`, `gpt-5.4-nano-2026-03-17` | `none` | Deprecated upstream; offered only while account-visible |

Reviewed sources: [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[GPT-5.4](https://developers.openai.com/api/docs/models/gpt-5.4), and
[GPT-5.4 nano](https://developers.openai.com/api/docs/models/gpt-5.4-nano).

For API configuration, use `PUT /api/v1/model-profiles/{profile_id}` with a
`cloud_model` object containing `provider: "openai"`, the chosen
`model_identifier`, and `deployment: "cloud"`. Include the local model when
configuring Hybrid. `POST /api/v1/model-profiles/{profile_id}/activate` activates
that preset. `GET /api/v1/model-profiles` supplies the stable IDs. The API rejects
unreviewed OpenAI IDs and models lacking strict structured output.

The evaluation harness also routes frozen OpenAI/Ollama selections by exact
provider and deployment. Its existing Ollama endpoint flags apply only to Ollama.
OpenAI uses the standard global API endpoint and a 900-second execution timeout.
Plan new comparisons explicitly; do not modify or resume historical campaigns
merely to switch providers. The legacy diagnostic `production_probe.py` remains
an explicitly Ollama-specific tool.

## Explicitly extend the reviewed catalog

`GET /v1/models` does not report sufficient capability or pricing information.
Unknown IDs are deliberately not treated as compatible by prefix matching. To
register a newer model, review its official model page, validate its Responses
text/strict-output support, and create a **secret-free** JSON array with one or
more `OpenAIModelSpec` records. Set `OPEN_HOLLYWOOD_OPENAI_MODELS_PATH` to that
file's absolute path in the backend terminal. It extends or overrides the bundled
records; it does not activate any profile.

This is a complete example using an already reviewed model:

```json
[
  {
    "model_identifier": "gpt-6.1-sol",
    "response_model_identifiers": ["gpt-6.1-sol"],
    "context_window": 1050000,
    "max_input_tokens": 272000,
    "max_output_tokens": 128000,
    "supports_text": true,
    "supports_structured_output": true,
    "reasoning_efforts": ["low", "medium", "high", "xhigh", "max"],
    "default_reasoning_effort": "low",
    "input_usd_per_million": "2.00",
    "cached_input_usd_per_million": "0.10",
    "output_usd_per_million": "10.00",
    "input_charge_multiplier": "1.25",
    "pricing_version": "openai-standard-2026-11-02"
  }
]
```

Use exact allowed response IDs; an alias must explicitly allow its documented
snapshot. Recheck rates before paid evaluations. The current adapter caps reviewed
input at 272,000 tokens to avoid long-context price changes and requests the
standard service tier. Regional endpoints, tools, media, background jobs and
automatic model substitution are outside this adapter. A model such as GPT-5.4
Pro that lacks strict structured output is not eligible for the story profile
catalog. See the [official model catalog](https://developers.openai.com/api/docs/models)
and the [GPT-5.4 Pro capability record](https://developers.openai.com/api/docs/models/gpt-5.4-pro).

## Budgets, validation and provenance

Each generation first calls the non-generating input-token count endpoint with
the same model, messages and schema. Input, context, maximum output and a
conservative dollar reservation must fit the invocation's remaining envelope
before generation. The output cap includes reasoning tokens. Cached input is
accounted separately; reasoning is already included in output and is never
charged twice by the application. Models with cache-write premiums use a
conservative input multiplier because separate write usage may not be reported.

Responses has no seed parameter. The requested seed remains in run provenance,
and provider metadata explicitly records that it was omitted. Sampling settings
are sent only when compatible with the effective reasoning effort. Requested
`thinking=False` maps to the reviewed model default (`none` where supported;
`low` for GPT-6.1 Sol). An explicit supported effort overrides that default.
Effective settings, rates/version, schema/request hashes, reported model ID,
cached and reasoning token counts are retained with invocation metadata. Exact
artifact versions and application schema/semantic validation remain authoritative.
Reproducible inputs do not imply deterministic model output.

Strict schemas are copied and adapted without changing canonical domain models
or creative messages. Defaults become required fields, constants become enums,
and object properties are closed. Open maps and unsupported composition fail
before generation. UUID formatting and all domain constraints remain validated
by the application. Refused, incomplete and invalid responses cannot produce
accepted artifacts. Available usage and estimates persist for rejected responses.

The adapter performs no internal retries. Definite rate-limit rejections use the
existing bounded workflow retry policy. Billing/quota errors, refusals, truncation
and uncertain transport/server failures stop without an automatic repeat charge.
Cancellation propagates through the existing durable worker cleanup. Interrupting
a local connection cannot guarantee that remote generation stopped; missing usage
and actual billed charges remain unknown. Rate-derived estimates retain
`cost_basis=unknown` under ADR 0017 and cannot pass verified-cost acceptance.

Requests set `store=false`, `background=false`, and `truncation=disabled`.
No hosted conversation, tool call, previous response, raw reasoning or encrypted
reasoning is retained. `store=false` disables Responses application storage;
it does **not** itself grant Zero Data Retention or remove standard abuse
monitoring. See [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data),
[token counting](https://developers.openai.com/api/docs/guides/token-counting),
and [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).

## Connectivity check

`uv run --extra api python scripts/openai_smoke.py` lists reviewed account-visible
models without inference. Adding `--run --model gpt-5.6-luna` explicitly makes
one synthetic generation, with a 512-input/128-output token envelope and a $0.005
ceiling. It prints safe usage metadata only, never a key or full provider payload.
It does not touch a project database, active profile or benchmark campaign.

The single authorized check on 2026-11-02 passed with valid `{"ok":true}` output:
40 input tokens, 16 output tokens, zero reasoning tokens, `finish_reason=stop`,
and `store=false`. The conservative estimate was **$0.0000292**, against a
**$0.0001636** reservation and **$0.005** ceiling. Actual billing was not fetched.
This is connectivity evidence only; OpenAI story quality and production
repeatability have not been evaluated.
