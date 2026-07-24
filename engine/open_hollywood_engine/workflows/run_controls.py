"""Provider-neutral run-control and aggregate-budget contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from types import MappingProxyType
from typing import Any
from uuid import UUID


class RunControlAction(StrEnum):
    """Idempotent commands accepted by a durable workflow run."""

    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    RETRY_FROM_NODE = "retry_from_node"
    UPDATE_BUDGET = "update_budget"


class RunControlStatus(StrEnum):
    """Persistence state of one idempotent control command."""

    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"


class RunPauseReason(StrEnum):
    """Why a nonterminal workflow is durably paused."""

    USER = "user"
    BUDGET = "budget"
    HUMAN_APPROVAL = "human_approval"


class BudgetLimit(StrEnum):
    """Deterministic aggregate limit that can pause a run."""

    GRAPH_STEPS = "max_graph_steps"
    MODEL_CALLS = "max_model_calls"
    INPUT_TOKENS = "max_input_tokens"
    OUTPUT_TOKENS = "max_output_tokens"
    COST = "max_cost_usd"
    WALL_CLOCK = "max_wall_clock_seconds"


@dataclass(frozen=True, slots=True)
class RunBudget:
    """Hard run ceilings plus the reservation required before the next call."""

    max_graph_steps: int = 64
    max_model_calls: int = 32
    max_input_tokens: int = 250_000
    max_output_tokens: int = 50_000
    max_cost_usd: Decimal = Decimal("2.00")
    max_wall_clock_seconds: int = 3_600
    per_call_input_tokens: int = 8_000
    per_call_output_tokens: int = 2_000
    per_call_cost_usd: Decimal = Decimal("0.25")

    def __post_init__(self) -> None:
        positive = {
            "max_graph_steps": self.max_graph_steps,
            "max_model_calls": self.max_model_calls,
            "max_input_tokens": self.max_input_tokens,
            "max_output_tokens": self.max_output_tokens,
            "max_wall_clock_seconds": self.max_wall_clock_seconds,
            "per_call_input_tokens": self.per_call_input_tokens,
            "per_call_output_tokens": self.per_call_output_tokens,
        }
        for name, value in positive.items():
            if not _is_integer(value) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        for name, decimal_value in (
            ("max_cost_usd", self.max_cost_usd),
            ("per_call_cost_usd", self.per_call_cost_usd),
        ):
            if not decimal_value.is_finite() or decimal_value < 0:
                raise ValueError(f"{name} must be a finite non-negative decimal")
        if self.per_call_input_tokens > self.max_input_tokens:
            raise ValueError("per_call_input_tokens cannot exceed max_input_tokens")
        if self.per_call_output_tokens > self.max_output_tokens:
            raise ValueError("per_call_output_tokens cannot exceed max_output_tokens")
        if self.per_call_cost_usd > self.max_cost_usd:
            raise ValueError("per_call_cost_usd cannot exceed max_cost_usd")

    def to_data(self) -> dict[str, int | str]:
        """Return the canonical JSON-safe persistence representation."""
        return {
            "max_graph_steps": self.max_graph_steps,
            "max_model_calls": self.max_model_calls,
            "max_input_tokens": self.max_input_tokens,
            "max_output_tokens": self.max_output_tokens,
            "max_cost_usd": str(self.max_cost_usd),
            "max_wall_clock_seconds": self.max_wall_clock_seconds,
            "per_call_input_tokens": self.per_call_input_tokens,
            "per_call_output_tokens": self.per_call_output_tokens,
            "per_call_cost_usd": str(self.per_call_cost_usd),
        }

    @classmethod
    def from_data(
        cls,
        value: Mapping[str, object],
        *,
        default_max_graph_steps: int = 64,
    ) -> RunBudget:
        """Load legacy or complete JSON data using explicit safe defaults."""
        defaults = cls(max_graph_steps=default_max_graph_steps)
        return cls(
            max_graph_steps=_integer(
                value.get("max_graph_steps", defaults.max_graph_steps),
                "max_graph_steps",
            ),
            max_model_calls=_integer(
                value.get("max_model_calls", defaults.max_model_calls),
                "max_model_calls",
            ),
            max_input_tokens=_integer(
                value.get("max_input_tokens", defaults.max_input_tokens),
                "max_input_tokens",
            ),
            max_output_tokens=_integer(
                value.get("max_output_tokens", defaults.max_output_tokens),
                "max_output_tokens",
            ),
            max_cost_usd=_decimal(
                value.get("max_cost_usd", defaults.max_cost_usd),
                "max_cost_usd",
            ),
            max_wall_clock_seconds=_integer(
                value.get(
                    "max_wall_clock_seconds",
                    defaults.max_wall_clock_seconds,
                ),
                "max_wall_clock_seconds",
            ),
            per_call_input_tokens=_integer(
                value.get(
                    "per_call_input_tokens",
                    defaults.per_call_input_tokens,
                ),
                "per_call_input_tokens",
            ),
            per_call_output_tokens=_integer(
                value.get(
                    "per_call_output_tokens",
                    defaults.per_call_output_tokens,
                ),
                "per_call_output_tokens",
            ),
            per_call_cost_usd=_decimal(
                value.get("per_call_cost_usd", defaults.per_call_cost_usd),
                "per_call_cost_usd",
            ),
        )

    def replace(self, updates: Mapping[str, object]) -> RunBudget:
        """Apply a strict partial update without accepting unknown fields."""
        unknown = set(updates) - set(self.to_data())
        if unknown:
            raise ValueError(f"unknown run-budget fields: {sorted(unknown)}")
        values: dict[str, Any] = {}
        for name, raw in updates.items():
            values[name] = (
                _decimal(raw, name)
                if name in {"max_cost_usd", "per_call_cost_usd"}
                else _integer(raw, name)
            )
        return replace(self, **values)


@dataclass(frozen=True, slots=True)
class RunUsage:
    """Observable aggregate usage consumed by one workflow run."""

    graph_steps: int = 0
    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: Decimal = Decimal("0")
    wall_clock_seconds: int = 0

    def __post_init__(self) -> None:
        for name, value in {
            "graph_steps": self.graph_steps,
            "model_calls": self.model_calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "wall_clock_seconds": self.wall_clock_seconds,
        }.items():
            if not _is_integer(value) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if not self.cost_usd.is_finite() or self.cost_usd < 0:
            raise ValueError("cost_usd must be a finite non-negative decimal")

    def to_data(self) -> dict[str, int | str]:
        """Return JSON-safe aggregate usage."""
        return {
            "graph_steps": self.graph_steps,
            "model_calls": self.model_calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": str(self.cost_usd),
            "wall_clock_seconds": self.wall_clock_seconds,
        }


@dataclass(frozen=True, slots=True)
class RunControlCommand:
    """One idempotent user command at the provider-neutral boundary."""

    id: UUID
    action: RunControlAction
    target_node: str | None = None
    budget_updates: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        if self.action is RunControlAction.RETRY_FROM_NODE:
            if self.target_node is None or not self.target_node.strip():
                raise ValueError("retry_from_node requires target_node")
        elif self.target_node is not None:
            raise ValueError("target_node is only valid for retry_from_node")
        if self.action is RunControlAction.UPDATE_BUDGET:
            if not self.budget_updates:
                raise ValueError("update_budget requires at least one budget field")
            object.__setattr__(
                self,
                "budget_updates",
                MappingProxyType(dict(self.budget_updates)),
            )
        elif self.budget_updates is not None:
            raise ValueError("budget_updates is only valid for update_budget")


def projected_budget_limits(
    budget: RunBudget,
    usage: RunUsage,
    *,
    includes_model_call: bool,
) -> tuple[BudgetLimit, ...]:
    """Return every hard limit the next node would reach or exceed."""
    limits: list[BudgetLimit] = []
    if usage.wall_clock_seconds >= budget.max_wall_clock_seconds:
        limits.append(BudgetLimit.WALL_CLOCK)
    if includes_model_call:
        if usage.model_calls + 1 > budget.max_model_calls:
            limits.append(BudgetLimit.MODEL_CALLS)
        if usage.input_tokens + budget.per_call_input_tokens > budget.max_input_tokens:
            limits.append(BudgetLimit.INPUT_TOKENS)
        if usage.output_tokens + budget.per_call_output_tokens > budget.max_output_tokens:
            limits.append(BudgetLimit.OUTPUT_TOKENS)
        if usage.cost_usd + budget.per_call_cost_usd > budget.max_cost_usd:
            limits.append(BudgetLimit.COST)
    return tuple(limits)


def budget_can_cover_usage(budget: RunBudget, usage: RunUsage) -> bool:
    """Return whether already-consumed usage fits within new hard ceilings."""
    return (
        usage.model_calls <= budget.max_model_calls
        and usage.input_tokens <= budget.max_input_tokens
        and usage.output_tokens <= budget.max_output_tokens
        and usage.cost_usd <= budget.max_cost_usd
        and usage.wall_clock_seconds <= budget.max_wall_clock_seconds
    )


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _integer(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    return value


def _decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a decimal")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{name} must be a decimal") from error
