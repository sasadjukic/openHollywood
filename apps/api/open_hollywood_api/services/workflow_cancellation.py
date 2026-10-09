"""Finish durable cleanup before propagating graph cancellation to the caller."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from contextvars import ContextVar
from functools import wraps
from typing import Any

_invocations: ContextVar[set[asyncio.Task[Any]] | None] = ContextVar(
    "workflow_invocations", default=None
)


def tracked_invocation[**P, T](
    function: Callable[P, Coroutine[Any, Any, T]],
) -> Callable[P, Coroutine[Any, Any, T]]:
    """Track the actual specialist task, independently of graph wrapper futures."""

    @wraps(function)
    async def tracked(*args: P.args, **kwargs: P.kwargs) -> T:
        scope = _invocations.get()
        task = asyncio.current_task()
        if scope is None or task is None:
            return await function(*args, **kwargs)
        scope.add(task)
        try:
            return await function(*args, **kwargs)
        finally:
            scope.discard(task)

    return tracked


async def run_with_invocation_cleanup[T](operation: Awaitable[T]) -> T:
    """Join this graph call's specialist cleanup before propagating its failure.

    A graph wrapper can finish cancellation before its underlying specialist task.
    Context propagation lets concurrent workflows own separate task sets without
    changing provider-neutral engine protocols or relying on graph internals.
    """
    scope: set[asyncio.Task[Any]] = set()
    token = _invocations.set(scope)
    try:
        try:
            return await operation
        except BaseException:
            if scope:
                for task in tuple(scope):
                    if not task.done() and not task.cancelling():
                        task.cancel()
                results = await finish_cleanup(asyncio.gather(*scope, return_exceptions=True))
                for result in results:
                    if isinstance(result, BaseException) and not isinstance(
                        result, asyncio.CancelledError
                    ):
                        raise result from None
            raise
    finally:
        _invocations.reset(token)


async def finish_cleanup[T](operation: Awaitable[T]) -> T:
    """Join cleanup despite repeated cancellation; use only inside cancellation handling.

    Shielding alone leaves the caller before cleanup ends. Keep a strong reference,
    join it, then let the enclosing handler re-raise its original CancelledError.
    Cleanup failures still propagate instead of being reported as successful stops.
    """
    future = asyncio.ensure_future(operation)
    while not future.done():
        try:
            return await asyncio.shield(future)
        except asyncio.CancelledError:
            if future.done():
                return future.result()
    return future.result()
