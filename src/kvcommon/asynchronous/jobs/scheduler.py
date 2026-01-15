from __future__ import annotations
import asyncio
import concurrent.futures
import functools
import logging
import queue
import threading
import time
import typing as t
from concurrent.futures import Future
from enum import StrEnum

from kvcommon.logger import get_logger

from ..utils import LoopType
from .errors import future_check_for_exception
from .errors import get_error_poller_task
from .event_loop import cancel_residual_loop_tasks
from .event_loop import get_or_create_loop
from .event_loop import start_async_loop
from .job import Job
from .job import JobState
from .job import PeriodicJob


LOG = get_logger("kvc_scheduler")


class SchedulerState(StrEnum):
    SUSPENDED = "suspended"
    ACTIVE = "active"
    STOPPED = "stopped"


class JobScheduler:
    _event_loop: LoopType
    _loop_thread: threading.Thread | None
    _futures: t.Dict[str, Future]
    _jobs_all: t.Dict[str, Job]
    _jobs_running: t.Dict[str, Job]
    _started: bool = False
    _state: SchedulerState = SchedulerState.SUSPENDED
    _loop_sleep_time: float = 0.5
    _error_queue: queue.Queue
    _debug_mode: bool = False
    _normal_log_level = logging.INFO
    _error_poller: PeriodicJob

    def __init__(
        self,
        event_loop: LoopType | None = None,
        log_level=logging.INFO,
        debug_mode: bool = False,
    ) -> None:
        self._futures = dict()
        self._jobs_all = dict()
        self._jobs_running = dict()

        self._error_queue = queue.Queue()
        self._error_poller = get_error_poller_task(error_queue=self._error_queue)
        self._error_poller.pause("Startup")
        self.add_job(self._error_poller)

        self._event_loop = get_or_create_loop(add_handlers=True, logger=LOG, adopt_loop=event_loop)

        self._normal_log_level = log_level
        self.toggle_debug_mode(debug_mode)

    def toggle_debug_mode(self, new_state: bool | None = None):
        if new_state is None:
            self._debug_mode = not self._debug_mode
        else:
            self._debug_mode = new_state

        if self._debug_mode:
            LOG.setLevel(logging.DEBUG)
            # Emit warnings for slow/blocking tasks if True
            self._event_loop.set_debug(True)
        else:
            LOG.setLevel(self._normal_log_level)

    @property
    def debug_mode(self) -> bool:
        return self._debug_mode

    @property
    def event_loop(self) -> LoopType:
        return self._event_loop

    def add_job(self, job: Job):
        if job.id not in self._jobs_all.keys():
            self._jobs_all[job.id] = job

    def get_job(self, job_or_id: Job | str) -> Job:
        if isinstance(job_or_id, Job):
            job_or_id = job_or_id.id
        job = self._jobs_all.get(job_or_id, None)
        if not job:
            raise KeyError(f"Failed to retrieve job with id: '{job_or_id}'")
        return job

    def get_running_job(self, job_or_id: Job | str) -> Job:
        if isinstance(job_or_id, Job):
            job_or_id = job_or_id.id
        job = self._jobs_running.get(job_or_id, None)
        if not job:
            raise KeyError(f"Failed to retrieve job with id: '{job_or_id}'")
        return job

    def remove_job(self, job_or_id: Job | str):
        if isinstance(job_or_id, Job):
            job_or_id = job_or_id.id
        if job_or_id in self._jobs_all.keys():
            del self._jobs_all[job_or_id]
        if job_or_id in self._jobs_running.keys():
            del self._jobs_running[job_or_id]

    def _track_running_job(self, job_id: str, job: Job):
        if job_id in self._jobs_running:
            raise KeyError(f"Running Job already tracked! Duplicate: '{job_id}'")
        self._jobs_running[job_id] = job

    @property
    def keys_jobs_running(self) -> t.KeysView[str]:
        return self._jobs_running.keys()

    @property
    def keys_jobs_all(self) -> t.KeysView[str]:
        return self._jobs_all.keys()

    @property
    def count_jobs_all(self) -> int:
        return len(self._jobs_all)

    @property
    def count_jobs_running(self) -> int:
        return len(self._jobs_running)

    def _track_future(self, job_id: str, job_future: Future):
        if job_id in self._futures:
            raise KeyError(f"Job future already tracked! Duplicate: '{job_id}'")
        self._futures[job_id] = job_future

    @staticmethod
    def _wait_for_futures(cancelled_futures: Future | t.List[Future], timeout: int = 3):
        if isinstance(cancelled_futures, Future):
            cancelled_futures = [
                cancelled_futures,
            ]

        num_cancelled = len(cancelled_futures)
        LOG.debug("Waiting for %s jobs to finish cleanup..", num_cancelled)

        done, pending = concurrent.futures.wait(
            cancelled_futures, timeout=timeout, return_when=concurrent.futures.ALL_COMPLETED
        )

        LOG.debug(f"Cleanup summary: {len(done)} jobs finished, {len(pending)} jobs still running.")

        for p in pending:
            LOG.warning("Job timed out during cleanup: %s", p)

    def _cancel_future(self, job_id: str, defer_wait: bool = False) -> Future | None:
        job_future = self._futures.pop(job_id)
        if job_future and not (job_future.done() or job_future.cancelled()):
            LOG.debug("Cancelling job future: '%s'", job_id)
            job_future.cancel()

            # if not defer_wait:
            #     self._wait_for_futures(job_future)
            return job_future

    def _cancel_all_futures(self):
        job_ids = list(self._futures.keys())
        cancelled_futures = []
        for job_id in job_ids:
            cancelled = self._cancel_future(job_id, defer_wait=True)
            if cancelled is not None:
                cancelled_futures.append(cancelled)
        self._wait_for_futures(cancelled_futures=cancelled_futures)

    def _start_loop_thread(self):
        ready_event = threading.Event()
        loop_thread = threading.Thread(target=start_async_loop, args=(self._event_loop, ready_event, LOG), daemon=True)
        self._loop_thread = loop_thread

        LOG.debug(f"Starting loop thread")
        loop_thread.start()  # begins loop.run_forever()

        ready_timeout = 5
        LOG.debug("Warming up loop thread - Waiting <=%s..", ready_timeout)
        ready_event.wait(timeout=5)  # wait for loop to be ready

        if not ready_event.is_set():
            raise TimeoutError("Async loop failed to start.")

        return loop_thread

    def _keyboard_interrupt(self):
        self._state = SchedulerState.SUSPENDED
        LOG.debug("KeyboardInterrupt caught. Setting SchedulerState to SUSPENDED.")

    def _cleanup_thread(self):
        LOG.debug("Cancelling lingering futures..")
        self._cancel_all_futures()

        LOG.debug("Cleaning up threads..")
        if self._loop_thread and self._loop_thread.is_alive():
            self._loop_thread.join()
        # else:
        #     LOG.debug("No thread to join")

    def run_job(self, job: Job) -> Future:
        LOG.info("Running job with ID: '%s', periodic: '%s'", job.id, job.periodic)
        LOG.debug("args: '%s', kwargs: '%s'", job.func_args, job.func_kwargs)

        if job.id in self._jobs_running:
            raise KeyError(f"Job already running: {job.id}")

        job_future = asyncio.run_coroutine_threadsafe(
            job.run(loop=self._event_loop, error_queue=self._error_queue), self._event_loop
        )

        job_done_callback = functools.partial(
            future_check_for_exception, **dict(job=job, error_queue=self._error_queue)
        )
        job_future.add_done_callback(job_done_callback)

        self._track_future(job.id, job_future)
        self._track_running_job(job.id, job)

        return job_future

    def start(self):
        try:
            self._start_loop_thread()
            LOG.debug("Background thread event loop started.")

            self._state = SchedulerState.ACTIVE

            for job_id, job in self._jobs_all.items():
                self.run_job(job)

            while self._state == SchedulerState.ACTIVE:
                time.sleep(self._loop_sleep_time)
                jobs_to_run: list[str] = []
                jobs_to_remove: list[str] = []
                paused_jobs: list[str] = []

                for job_id in self.keys_jobs_all:
                    job = self.get_job(job_id)

                    # Untrack jobs that have finished/stopped fully
                    if job.state == JobState.FINISHED:
                        jobs_to_remove.append(job.id)

                    # Catch new jobs added since thread started
                    elif job.state == JobState.READY:
                        jobs_to_run.append(job.id)

                    elif job.state == JobState.SUSPENDED:
                        paused_jobs.append(job.id)

                for job_id in jobs_to_remove:
                    self.remove_job(job)

                for job_id in jobs_to_run:
                    self.run_job(job)

                if self.count_jobs_running > 1:
                    self._error_poller.resume("Running jobs")
                else:
                    self._error_poller.pause("No running jobs")

                if self.debug_mode:
                    num_paused = len(paused_jobs)
                    LOG.debug(
                        "Scheduler Main Loop: %s -- All Jobs: '%s' -- Running Jobs: '%s' -- Paused: '%s' ",
                        self._state,
                        self.count_jobs_all,
                        self.count_jobs_running - num_paused,
                        num_paused,
                    )

                # Check for thread health just in case
                if not self._loop_thread or not self._loop_thread.is_alive():
                    LOG.warning("Background loop thread is unexpectedly dead. Exiting.")
                    break

        except KeyboardInterrupt:
            self._keyboard_interrupt()

        self.stop()

    def stop(self):
        LOG.debug("Stopping..")
        self._state = SchedulerState.STOPPED

        try:
            cleanup_future = asyncio.run_coroutine_threadsafe(
                cancel_residual_loop_tasks(loop=self._event_loop, logger=LOG), self._event_loop
            )
            LOG.debug("Waiting for 'cancel_residual_loop_tasks'")
            cleanup_future.result(timeout=5)
        except Exception as ex:
            LOG.warning("Cleanup coroutine failed or timed out: %s", ex)
        finally:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
            self._cleanup_thread()
            LOG.info("Stopped - Scheuduler finished cleanup.")
