import asyncio
import functools
import inspect
import typing as t
from asyncio import AbstractEventLoop

from kvcommon.logger import get_logger


LoopType = asyncio.BaseEventLoop  # AbstractEventLoop is too abstract for code introspection


LOG = get_logger("kvc_async")


async def call_sync_async(
    func: t.Callable,
    func_args: t.Tuple | None = None,
    func_kwargs: t.Dict | None = None,
    loop: AbstractEventLoop | None = None,
):
    """
    Push a synchronous function to ThreadPoolExecutor with kwargs support
    """
    loop = asyncio.get_running_loop() if loop is None else loop
    func_args = tuple() if func_args is None else func_args
    func_kwargs = dict() if func_kwargs is None else func_kwargs

    partial_func = functools.partial(func, *func_args, **func_kwargs)
    return await loop.run_in_executor(None, partial_func)


async def run_callable_safely(loop: LoopType, func: t.Callable | t.Coroutine, *args: t.Tuple, **kwargs):
    """
    Runs an async function directly or pushes a sync function to the ThreadPoolExecutor.
    """

    if inspect.isfunction(func):
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)

        return await call_sync_async(func=func, func_args=args, func_kwargs=kwargs, loop=loop)


def is_running_async():
    """Checks if there's an active asyncio event loop in the current thread."""
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False
