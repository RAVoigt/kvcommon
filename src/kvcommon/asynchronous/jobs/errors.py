from __future__ import annotations
import asyncio
import logging
import queue
import typing as t
from concurrent.futures import Future

from kvcommon.logger import get_logger

from .job import JobExceptionStruct
from .job import JobParams
from .job import PeriodicJob


if t.TYPE_CHECKING:
    from .job import Job


LOG = get_logger("kvc_scheduler")


def future_check_for_exception(future: Future, job: Job, error_queue: queue.Queue | None = None):
    if future.cancelled():
        # LOG.debug("Future for Job '%s' was cancelled.", job.id)
        return
    ex = future.exception()
    if ex:
        if isinstance(ex, asyncio.CancelledError):
            LOG.debug("Job '%s' stopped gracefully via CancelledError.", job.id)
            return
        LOG.error("Job '%s' Exception: %s", job.id, ex)

        if error_queue:
            error_queue.put(JobExceptionStruct(job=job, exception=ex))


async def emit_queued_error(error_queue: queue.Queue, logger: logging.Logger = LOG):
    try:
        job_exception: JobExceptionStruct = error_queue.get_nowait()
        ex = job_exception.exception
        ex_name = type(ex).__name__
        logger.exception("Job '%s' raised: '%s' - %s", job_exception.job.id, ex_name, ex, exc_info=ex)
        error_queue.task_done()
    except queue.Empty:
        pass
    await asyncio.sleep(0.1)


def get_error_poller_task(error_queue: queue.Queue, interval: float | int = 1, logger: logging.Logger = LOG):
    return PeriodicJob(
        JobParams(
            func=emit_queued_error,
            id="errors",
            interval=interval,
            stop_on_exception=False,
            func_kwargs=dict(error_queue=error_queue, logger=logger),
        )
    )
