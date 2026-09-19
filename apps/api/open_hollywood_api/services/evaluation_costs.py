"""Project persisted invocation provenance into portable benchmark evidence."""

from collections.abc import Iterable

from open_hollywood_engine.evaluations import BenchmarkInvocationCost
from open_hollywood_engine.models import ModelCostBasis

from open_hollywood_api.persistence.models import AgentInvocation


def invocation_cost_evidence(
    invocations: Iterable[AgentInvocation],
) -> tuple[BenchmarkInvocationCost, ...]:
    """Keep unknown costs explicit, including interrupted or failed calls."""
    return tuple(
        BenchmarkInvocationCost(
            invocation_id=row.id,
            basis=row.cost_basis,
            amount_usd=(
                None
                if row.cost_basis is ModelCostBasis.UNKNOWN
                else format(row.estimated_cost_usd, ".6f")
            ),
        )
        for row in invocations
    )
