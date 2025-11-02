from __future__ import annotations
import dataclasses
import datetime
import logging
import typing as t
from enum import StrEnum

from kvcommon.datetime import EPOCH
from kvcommon.datetime import NEVER
from kvcommon.datetime import utcnow
from kvcommon.logger import get_logger


LOG = get_logger("kvc_job")


class JobState(StrEnum):
    READY = "ready"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    FINISHED = "finished"


@dataclasses.dataclass(kw_only=True)
class TimeDifferential:
    late: bool = False
    delta: datetime.timedelta

    @property
    def delta_seconds(self) -> float:
        delta_seconds = self.delta.total_seconds()
        if self.late:
            return -(delta_seconds)
        return delta_seconds


class JobStatus:
    _executions: int = 0
    # _max_executions: int | None = None
    _delay: bool = False
    _repeat: bool = False
    _continue: bool = True
    _stop_on_exception: bool = False
    _interval: datetime.timedelta
    # _max_duration: datetime.timedelta
    _current_state: JobState = JobState.READY
    _run_time_prev: datetime.datetime = NEVER
    _run_time_next: datetime.datetime = NEVER
    _run_time_first: datetime.datetime = NEVER
    _logger: logging.Logger

    def __init__(
        self,
        interval: datetime.timedelta | float | int,
        delay: bool = False,
        repeat: bool = True,
        stop_on_exception: bool = False,
        logger: logging.Logger = LOG
    ) -> None:
        if isinstance(interval, (int, float)):
            interval = datetime.timedelta(seconds=interval)
        self._interval = interval
        self._repeat = repeat
        self._delay = delay
        self._stop_on_exception = stop_on_exception
        self._logger = logger

    def __repr__(self) -> str:
        return f"<JobStatus|{self.__str__()}>"

    def __str__(self) -> str:
        out = f"Runs:'{self._executions}'"
        f"|Prev:'{self._run_time_prev.isoformat()}'"
        f"|Next:'{self._run_time_next.isoformat()}'"
        return out

    @property
    def LOG(self) -> logging.Logger:
        return self._logger

    @property
    def should_continue(self) -> bool:
        return self._continue

    @property
    def stop_on_exception(self) -> bool:
        return self._stop_on_exception

    @property
    def delay_first_run(self) -> bool:
        return self._delay

    @property
    def periodic(self) -> bool:
        return self._repeat

    @property
    def state(self) -> JobState:
        return self._current_state

    @property
    def interval(self) -> datetime.timedelta:
        return self._interval

    @property
    def execution_count(self) -> int:
        return self._executions

    @property
    def has_run(self) -> bool:
        return self._executions >= 1

    @property
    def is_due(self) -> bool:
        return utcnow() > self._run_time_next

    @property
    def is_late(self) -> bool:
        return utcnow() > (self._run_time_next + self._interval)

    @property
    def time_differential(self) -> TimeDifferential:
        """
        Returns the time before (ready) / after (late) this job is next scheduled to run
        """
        now = utcnow()
        if now <= self._run_time_next:
            delta = self._run_time_next - now
            late = False
        else:
            delta = now - self._run_time_prev
            late = True
        return TimeDifferential(late=late, delta=delta)

    @property
    def lateness(self) -> datetime.timedelta | None:
        diff = self.time_differential
        if diff.late:
            return diff.delta
        return None

    @property
    def lateness_seconds(self) -> float:
        diff = self.time_differential
        if diff.late:
            return diff.delta_seconds
        return 0.0

    @property
    def run_time_first(self) -> datetime.datetime:
        return self._run_time_first

    @property
    def run_time_prev(self) -> datetime.datetime:
        return self._run_time_prev

    @property
    def run_time_next(self) -> datetime.datetime:
        return self._run_time_next

    def start(self):
        self._current_state = JobState.ACTIVE

    def pause(self):
        self._current_state = JobState.SUSPENDED
        # self._continue = False

    def stop(self):
        self._current_state = JobState.FINISHED
        self._continue = False

    def _ensure_first_run_time(self, dt: datetime.datetime | None):
        if self._run_time_first == NEVER:
            if not dt:
                dt = utcnow()
            self._run_time_first = dt

    def _update_prev_run_time(self, dt: datetime.datetime | None):
        if not dt:
            dt = utcnow()
        self._run_time_prev = dt

    def record_run(self, current_run_time: datetime.datetime, next_run_time: datetime.datetime, any_exceptions: bool = False):
        self._executions += 1
        if self.execution_count <= 1:
            self._ensure_first_run_time(current_run_time)
        self._update_prev_run_time(current_run_time)
        self._run_time_next = next_run_time

        log_str = "Execution completed"
        if any_exceptions:
            log_str = f"{log_str} (with ERRORS)"
        if self.periodic:
            log_str = f"{log_str} - Cycles: {self.execution_count}"
        else:
            log_str = f"{log_str} (One-Off)"
        self.LOG.debug(log_str)
