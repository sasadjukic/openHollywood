"""Public API contracts for durable workflow run controls."""

from __future__ import annotations

from decimal import Decimal
from typing import Self
from uuid import UUID

from open_hollywood_engine.workflows import (
    RunControlAction,
    RunControlCommand,
    RunControlStatus,
    RunPauseReason,
)
from pydantic import BaseModel, ConfigDict, Field, model_validator

from open_hollywood_api.persistence.models import RunStatus
from open_hollywood_api.services.run_controls import RunControlResult


class RunBudgetPatch(BaseModel):
    """Strict partial update for aggregate run ceilings and call reservations."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_graph_steps: int | None = Field(default=None, ge=1, le=64)
    max_model_calls: int | None = Field(default=None, ge=1)
    max_input_tokens: int | None = Field(default=None, ge=1)
    max_output_tokens: int | None = Field(default=None, ge=1)
    max_cost_usd: Decimal | None = Field(default=None, ge=0)
    max_wall_clock_seconds: int | None = Field(default=None, ge=1)
    per_call_input_tokens: int | None = Field(default=None, ge=1)
    per_call_output_tokens: int | None = Field(default=None, ge=1)
    per_call_cost_usd: Decimal | None = Field(default=None, ge=0)

    def updates(self) -> dict[str, object]:
        """Return only fields explicitly supplied by the caller."""
        return self.model_dump(exclude_none=True)


class RunControlRequest(BaseModel):
    """One idempotent pause, resume, stop, retry, or budget command."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    command_id: UUID
    action: RunControlAction
    target_node: str | None = Field(default=None, min_length=1, max_length=100)
    budget: RunBudgetPatch | None = None

    @model_validator(mode="after")
    def validate_domain_contract(self) -> Self:
        """Apply provider-neutral action-specific invariants."""
        self.to_domain()
        return self

    def to_domain(self) -> RunControlCommand:
        """Convert this public request into the engine command."""
        return RunControlCommand(
            id=self.command_id,
            action=self.action,
            target_node=self.target_node,
            budget_updates=self.budget.updates() if self.budget is not None else None,
        )


class RunBudgetView(BaseModel):
    """Canonical hard limits active for one workflow run."""

    model_config = ConfigDict(frozen=True)

    max_graph_steps: int
    max_model_calls: int
    max_input_tokens: int
    max_output_tokens: int
    max_cost_usd: Decimal
    max_wall_clock_seconds: int
    per_call_input_tokens: int
    per_call_output_tokens: int
    per_call_cost_usd: Decimal


class RunUsageView(BaseModel):
    """Aggregate resources already consumed by one workflow run."""

    model_config = ConfigDict(frozen=True)

    graph_steps: int
    model_calls: int
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal
    wall_clock_seconds: int


class RunControlResponse(BaseModel):
    """Durable command and workflow state returned to the workspace."""

    model_config = ConfigDict(frozen=True)

    command_id: UUID
    workflow_run_id: UUID
    action: RunControlAction
    command_status: RunControlStatus
    workflow_status: RunStatus
    pause_reason: RunPauseReason | None
    target_node: str | None
    resulting_workflow_run_id: UUID | None
    checkpoint_id: str | None
    budget: RunBudgetView
    usage: RunUsageView
    error_message: str | None

    @classmethod
    def from_domain(cls, result: RunControlResult) -> RunControlResponse:
        """Convert application state without exposing checkpoints or prompts."""
        return cls(
            command_id=result.command_id,
            workflow_run_id=result.workflow_run_id,
            action=result.action,
            command_status=result.command_status,
            workflow_status=result.workflow_status,
            pause_reason=result.pause_reason,
            target_node=result.target_node,
            resulting_workflow_run_id=result.resulting_workflow_run_id,
            checkpoint_id=result.checkpoint_id,
            budget=RunBudgetView(
                max_graph_steps=result.budget.max_graph_steps,
                max_model_calls=result.budget.max_model_calls,
                max_input_tokens=result.budget.max_input_tokens,
                max_output_tokens=result.budget.max_output_tokens,
                max_cost_usd=result.budget.max_cost_usd,
                max_wall_clock_seconds=result.budget.max_wall_clock_seconds,
                per_call_input_tokens=result.budget.per_call_input_tokens,
                per_call_output_tokens=result.budget.per_call_output_tokens,
                per_call_cost_usd=result.budget.per_call_cost_usd,
            ),
            usage=RunUsageView(
                graph_steps=result.usage.graph_steps,
                model_calls=result.usage.model_calls,
                input_tokens=result.usage.input_tokens,
                output_tokens=result.usage.output_tokens,
                cost_usd=result.usage.cost_usd,
                wall_clock_seconds=result.usage.wall_clock_seconds,
            ),
            error_message=result.error_message,
        )
