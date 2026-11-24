"""Single-use Price of Life capture with an input allowance sized from the first receipt."""

from typing import Literal
from unittest.mock import patch

from pydantic import create_model

from scripts import ordinary_v61_capture as capture
from scripts import price_of_life_v61_capture as original

ROOT = capture.REPO / "data/diagnostics/price-of-life-v61-budget-capture-2026-11-24"
WIRE_SHA = "cbc5c84f2c535fe4a8a9067ae05f7c8d3ee53cc7117cdd752ce06e228ec5be01"

# Reuse the frozen single-dispatch contract while keeping the old registration replayable.
BudgetPlan = create_model(
    "PriceOfLifeBudgetPlan",
    __base__=capture.Plan,
    contract=(Literal["single-ordinary-v61-critic-budget-2"], ...),
    input_tokens=(Literal[28000], ...),
    context_tokens=(Literal[36000], ...),
    previous_approval_sha256=(
        Literal["71eaf9118ef23fb95c6e4b9357985f362b58b47ce5dc329afcbfb2642b286e16"],
        ...,
    ),
    previous_terminal_sha256=(
        Literal["2019dd08cd7245445bcd5f9507fce83946030472a5ca11d0bd2b6c37a72ba302"],
        ...,
    ),
)


def main() -> int:
    with patch.multiple(
        capture,
        Plan=BudgetPlan,
        ROOT=ROOT,
        WIRE_SHA=WIRE_SHA,
        MESSAGE_SHA=original.MESSAGE_SHA,
        load_task=original.load_task,
    ):
        return capture.main()


if __name__ == "__main__":
    raise SystemExit(main())
