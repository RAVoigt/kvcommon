from __future__ import annotations
import asyncio
import dataclasses
import datetime
import logging
import queue
import time
import typing as t

from kvcommon.asynchronous.utils import run_callable_safely
from kvcommon.asynchronous.utils import LoopType
from kvcommon.datetime import EPOCH
from kvcommon.datetime import NEVER
from kvcommon.datetime import utcnow
from kvcommon.logger import get_logger

from .metrics import JobTimer
from .status import JobState
from .status import JobStatus


LOG = get_logger("kvc_job")


@dataclasses.dataclass(kw_only=True)
class JobFunc:
    func: t.Callable | t.Coroutine
    func_args: t.Tuple | None = ()
    func_kwargs: t.Dict[str, t.Any] | None = None

    async def run(self, loop: LoopType, id: str) -> t.Any:
        # LOG.debug("Job '%s' running", id)
        func_args = self.func_args or ()
        func_kwargs = self.func_kwargs or {}
        return await run_callable_safely(loop, func=self.func, *func_args, **func_kwargs)


class JobParams:
    """
    Parameters for a Job. Used for convenient encapsulation when subclassing Job.

    Parameters:
        func (function or coroutine): The main job function to be executed
        id (str): A short (unique) id for the job
        interval (datetime.timedelta or float or int): Interval (in seconds) between job iterations.
            Interpret as "delay before execution" for one-off jobs.
        delay_first_run (bool):
            True: Job waits one interval before execution. Used as delay duration for one-off jobs.
            False: Job runs immediately
        repeat (bool): Only relevant for Job base class or custom job classes.
            Always true for PeriodicJob, always False for OneOffJob
            True: Job runs periodically, waiting interval seconds between each cycle
            False: Job runs just once then marks itself as Finished.
        stop_on_exception (bool): Has no effect on one-off jobs - Only affects periodic/repeating jobs.
            True: Job stops if an unhandled exception is raised during its execution
            False: Job repeats even if its previous execution raised an exception
        log_level (int): Log level (logging.DEBUG, logging.INFO, etc.) to use for the job's internal logger
        func_args (tuple): Positional args for the job func
        func_kwargs (dict): Named args for the job func
    """

    func: t.Callable | t.Coroutine
    func_args: t.Tuple[t.Any]
    func_kwargs: t.Dict[str, t.Any]
    id: str
    interval: datetime.timedelta = dataclasses.field(init=False)
    delay_first_run: bool = False
    repeat: bool = True
    stop_on_exception: bool = False
    log_level: int = logging.INFO

    def __init__(
        self,
        func: t.Callable | t.Coroutine,
        id: str,
        interval: datetime.timedelta | float | int,
        delay_first_run: bool = False,
        repeat: bool = True,
        stop_on_exception: bool = False,
        log_level: int = logging.INFO,
        func_args: t.Tuple | None = None,
        func_kwargs: t.Dict | None = None,
    ):
        if isinstance(interval, (int, float)):
            interval = datetime.timedelta(seconds=interval)
        self.func = func
        self.func_args = tuple() if func_args is None else func_args
        self.func_kwargs = dict() if func_kwargs is None else func_kwargs
        self.id = id
        self.interval = interval
        self.delay_first_run = delay_first_run
        self.repeat = repeat
        self.stop_on_exception = stop_on_exception
        self.log_level = log_level

        if self.interval.total_seconds() <= 0:
            if self.repeat:
                raise ValueError("Interval cannot be zero for periodic jobs")
            self.delay_first_run = False


class Job:
    """
    Base Class for a Job to be run by the async job scheduler.

    Parameters:
        params (JobParams): Dataclass of params for encapsulation
    """

    _id: str
    _status: JobStatus
    _func: JobFunc
    _logger: logging.Logger
    _prehooks: list[JobFunc]
    _posthooks: list[JobFunc]
    _timer: JobTimer | None = None

    def __init__(
            self,
            params: JobParams,
            # prehooks: list[JobFunc] | None = None,
            # posthooks: list[JobFunc] | None = None,
            timer: JobTimer | None = None
        ) -> None:
        self._id = params.id
        # self._prehooks = []
        # self._posthooks = []
        if params.repeat:
            logger_name = f"job:{params.id}"
        else:
            logger_name = f"job:{params.id}"
        self._logger = get_logger(logger_name)
        self._logger.setLevel(params.log_level)

        self._func = JobFunc(func=params.func, func_args=params.func_args, func_kwargs=params.func_kwargs)
        self._status = JobStatus(
            interval=params.interval,
            delay=params.delay_first_run,
            repeat=params.repeat,
            stop_on_exception=params.stop_on_exception,
            logger=self._logger,
        )
        # if prehooks:
        #     for prehook in prehooks:
        #         self.add_prehook(prehook)
        # if posthooks:
        #     for posthook in posthooks:
        #         self.add_posthook(posthook)
        if timer:
            if not isinstance(timer, JobTimer):
                raise TypeError("Expected type for timer param: JobTimer")
            self._timer = timer

    # @property
    # def has_prehooks(self):
    #     return len(self._prehooks) > 0

    # @property
    # def has_posthooks(self):
    #     return len(self._posthooks) > 0

    # def add_prehook(self, hook: JobFunc) -> int:
    #     self._prehooks.append(hook)
    #     return len(self._prehooks) - 1

    # def add_posthook(self, hook: JobFunc):
    #     self._posthooks.append(hook)
    #     return len(self._posthooks) - 1

    @property
    def LOG(self) -> logging.Logger:
        return self._logger

    @property
    def id(self) -> str:
        return self._id

    @property
    def state(self) -> JobState:
        return self._status.state

    @property
    def func(self) -> t.Callable | t.Coroutine:
        return self._func.func

    @property
    def func_args(self) -> tuple | None:
        return self._func.func_args

    @property
    def func_kwargs(self) -> dict | None:
        kwargs = self._func.func_kwargs
        if kwargs is not None:
            return kwargs.copy()

    @property
    def interval(self) -> datetime.timedelta:
        return self._status.interval

    @property
    def periodic(self) -> bool:
        return self._status.periodic

    def resume(self, reason: str | None = None):
        if self._status._current_state == JobState.ACTIVE:
            return
        self.LOG.info("Resuming" if not reason else f"Resuming due to: '{reason}'")
        self._status.start()

    def pause(self, reason: str | None = None):
        if self._status._current_state == JobState.SUSPENDED:
            return
        self.LOG.info("Pausing" if not reason else f"Pausing due to: '{reason}'")
        self._status.pause()

    def stop(self, reason: str | None = None):
        if self._status._current_state == JobState.FINISHED:
            return
        self.LOG.info("Stopping" if not reason else f"Stopping due to: '{reason}'")
        self._status.stop()

    async def run(self, loop: LoopType, error_queue: queue.Queue | None = None):
        """
        An async job that runs indefinitely on a fixed time interval.
        This function will be scheduled to run on the background event loop.
        """
        id = self.id
        interval = self.interval
        status = self._status
        is_periodic_job = status.periodic
        delay_first_run = status.delay_first_run

        # Initial run timing
        now_outer = utcnow()
        next_run_time = now_outer + self.interval
        next_monotonic_time = time.monotonic() + interval.total_seconds()

        # self.LOG.debug("Initial :: Now: '%s' - Next: '%s' - Next monotonic: '%s'", now_outer, next_run_time, next_monotonic_time)

        if self.periodic:
            self.LOG.debug("Periodic Job Started - Running every %s seconds.", interval)
        else:
            if delay_first_run:
                self.LOG.debug("One-off Job Started - Running once (after delay of %s seconds).", interval)
            else:
                self.LOG.debug("One-off Job Started - Running once.")

        while status.should_continue:
            if status.state == JobState.SUSPENDED:
                # self.LOG.debug("Skipping execution for paused job")
                await asyncio.sleep(1)
                continue

            status.start()

            if status.execution_count <= 0 and delay_first_run == False:
                # We haven't run before, and first-time delay is disabled -> Run immediately
                wait_time = 0
            else:
                # Calculate time to wait before running from now until next_monotonic_time
                wait_time = next_monotonic_time - time.monotonic()

            if wait_time <= 0:
                if status.execution_count >= 1:
                    # If this isn't the first run, then we're here because job run is late
                    self.LOG.warning("Job '%s' missed run time '%s' - Executing immediately.", id, next_run_time.time())
                # else:
                #     # First run with no delay
                #     self.LOG.debug("Loop:: '%s' NOT Waiting before execution", id)
            else:
                # Wait until it's time to run the job again
                # self.LOG.debug("Loop:: Waiting: '%s'", wait_time)
                await asyncio.sleep(wait_time)

            # TODO: Return results?
            any_exc = False
            try:
                if self._timer:
                    self._timer.start()

                # for prehook in self._prehooks:
                #     await prehook.run(loop, id)

                await self._func.run(loop, id)

                # for posthook in self._posthooks:
                #     await posthook.run(loop, id)

                if self._timer:
                    self._timer.stop()

            except Exception as ex:
                # self.LOG.error("Exception in Job '%s': '%s'", id, type(ex).__name__)
                any_exc = True
                if error_queue:
                    error_queue.put(JobExceptionStruct(job=self, exception=ex))
                if status.stop_on_exception:
                    next_run_time = NEVER
                    self.stop()

            finally:

                now_inner = utcnow()
                if is_periodic_job:
                    while next_run_time <= now_inner:
                        next_run_time += interval
                    monotonic_delta = (next_run_time - now_inner).total_seconds()
                    next_monotonic_time = time.monotonic() + monotonic_delta
                else:
                    next_run_time = NEVER
                    self.stop()

                status.record_run(current_run_time=now_inner, next_run_time=next_run_time, any_exceptions=any_exc)

                if not is_periodic_job:
                    break


class PeriodicJob(Job):
    """
    A periodic job that executes repeatedly on its interval
    """

    def __init__(
        self,
        params: JobParams,
        # prehooks: list[JobFunc] | None = None,
        # posthooks: list[JobFunc] | None = None,
        timer: JobTimer | None = None
    ) -> None:
        params.repeat = True
        # super().__init__(params=params, prehooks=prehooks, posthooks=posthooks, timer=timer)
        super().__init__(params=params, timer=timer)


class OneOffJob(Job):
    """
    A one-off job that executes after a delay (using its interval as delay) and does not repeat
    """

    def __init__(
        self,
        params: JobParams,
        # prehooks: list[JobFunc] | None = None,
        # posthooks: list[JobFunc] | None = None,
        timer: JobTimer | None = None
    ) -> None:
        params.repeat = False
        # super().__init__(params=params, prehooks=prehooks, posthooks=posthooks, timer=timer)
        super().__init__(params=params, timer=timer)


@dataclasses.dataclass(kw_only=True)
class JobExceptionStruct:
    job: Job
    exception: BaseException
