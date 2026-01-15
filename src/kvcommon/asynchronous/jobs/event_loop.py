from __future__ import annotations
import asyncio
import logging
import signal
import threading
import typing as t

from kvcommon.asynchronous.utils import LoopType
from kvcommon.logger import get_logger


LOG = get_logger("kvc_async_loop")


def start_async_loop(loop: LoopType, ready_event: threading.Event, logger: logging.Logger = LOG):
    """
    Function to run in the background thread.
    It simply starts the event loop and lets it run forever.
    """

    logger.debug("Event loop starting...")
    # Set the loop as the current one for this thread
    asyncio.set_event_loop(loop)
    ready_event.set()

    # This call blocks the thread until loop.stop() is called
    loop.run_forever()
    logger.debug("Event loop stopped.")


def _signal_handler(loop):
    loop.stop()


def _add_signal_handlers_to_loop(loop: LoopType, logger: logging.Logger = LOG):
    # Set up signal handlers for graceful shutdown:
    try:
        # loop.add_signal_handler(signal.SIGINT, _signal_handler, loop) # Handled by main thread
        loop.add_signal_handler(signal.SIGQUIT, _signal_handler, loop)
        loop.add_signal_handler(signal.SIGTERM, _signal_handler, loop)
        loop.add_signal_handler(signal.SIGHUP, _signal_handler, loop)  # TODO: Rich SIGHUP handling
    except NotImplementedError:
        logger.warning("Signal handlers not supported on this platform.")


def get_or_create_loop(add_handlers: bool = True, logger: logging.Logger = LOG, adopt_loop: LoopType | None = None) -> LoopType:
    try:
        # Try to get pre-existing thread-local event loop
        loop = adopt_loop or asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Loop is closed")

    except RuntimeError:
        # If no loop is set, or if the loop is closed, create a new one.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)  # Thread-local

    loop = t.cast(LoopType, loop)  # AbstractEventLoop is too abstract for code introspection

    if add_handlers:
        _add_signal_handlers_to_loop(loop, logger=logger)

    return loop


async def cancel_residual_loop_tasks(loop: LoopType, logger: logging.Logger = LOG):
    logger.debug("Cleanup: Cancelling any residual loop tasks")
    all_tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task(loop)]
    if not all_tasks:
        logger.info("Cleanup: No residual tasks to cancel.")
        return

    logger.warning("Cleanup: Cancelling %s residual tasks...", len(all_tasks))
    for task in all_tasks:
        task.cancel()

    await asyncio.gather(*all_tasks, return_exceptions=True)
    logger.info("Cleanup: All residual tasks finished.")
