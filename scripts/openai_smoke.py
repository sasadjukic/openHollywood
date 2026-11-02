"""Explicit, synthetic OpenAI connectivity check; never runs a story or campaign."""

from __future__ import annotations

import argparse
import asyncio
import json
from decimal import Decimal

from open_hollywood_engine.models import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelGatewayError,
    ModelMessage,
    ModelRequest,
    ModelSettings,
    OpenAIGateway,
)


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--run", action="store_true", help="Authorize one synthetic generation")
    args = parser.parse_args()
    async with OpenAIGateway(timeout_seconds=45) as gateway:
        try:
            if not args.run:
                catalog = await gateway.list_models()
                print(
                    json.dumps(
                        {"available_reviewed_models": [item.model_identifier for item in catalog]}
                    )
                )
                return 0
            response = await gateway.generate(
                ModelRequest(
                    model_identifier=args.model,
                    messages=(
                        ModelMessage(MessageRole.USER, 'Return the JSON object {"ok":true}.'),
                    ),
                    budget=ModelCallBudget(512, 128, Decimal("0.005")),
                    invocation=InvocationContext("synthetic_connectivity", "openai-smoke-1"),
                    settings=ModelSettings(thinking=False),
                    response_schema={
                        "type": "object",
                        "properties": {"ok": {"type": "boolean"}},
                        "required": ["ok"],
                        "additionalProperties": False,
                    },
                )
            )
            valid = json.loads(response.content) == {"ok": True}
            print(
                json.dumps(
                    {
                        "ok": valid,
                        "model": response.model_identifier,
                        "provider_model": response.provider_model_identifier,
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                        "reasoning_tokens": response.usage.reasoning_tokens,
                        "estimated_cost_usd": str(response.estimated_cost_usd),
                        "dollar_budget": "0.005",
                        "reserved_cost_usd": response.metadata["reserved_cost_usd"],
                        "store": False,
                        "finish_reason": response.finish_reason,
                    }
                )
            )
            return 0 if valid else 1
        except ModelGatewayError as error:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error_code": error.code.value,
                        "detail": str(error),
                        "retryable": error.retryable,
                    }
                )
            )
            return 1
        except (ValueError, TypeError):
            print(json.dumps({"ok": False, "error_code": "invalid_synthetic_response"}))
            return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
