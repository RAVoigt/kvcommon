import logging
from typing import Callable

from flask_apscheduler import APScheduler
from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.events import EVENT_JOB_MISSED
from apscheduler.events import JobExecutionEvent
from kvcommon.flask import metrics
from kvcommon.logger import get_logger


LOG = get_logger("kvc-flask-scheduler")


# Filter to reduce log spam from APScheduler
class SuppressThreadPoolExecutorLogging(logging.Filter):
    def filter(self, record):
        return "ThreadPoolExecutor" not in record.getMessage()


LOG.addFilter(SuppressThreadPoolExecutorLogging())


class SchedulerEventTracker(object):

    @staticmethod
    def _job_event_track(job_id: str, event: str):
        LOG.debug(f"Scheduler Event Listener: {event}: Job <'{job_id}'>")
        metrics.incr(metrics.SCHEDULER_JOB_EVENT.labels(job_id=job_id, event=event.lower()))

    @staticmethod
    def event_listener(event):
        if isinstance(event, JobExecutionEvent):
            event_str = "Unknown"
            if event.exception or event.code == EVENT_JOB_ERROR:
                event_str = "Error"
            else:
                if event.code == EVENT_JOB_EXECUTED:
                    event_str = "Executed"
                elif event.code == EVENT_JOB_MISSED:
                    event_str = "Missed"
            SchedulerEventTracker._job_event_track(job_id=event.job_id, event=event_str)
        else:
            LOG.warning(
                f"Scheduler Event Listener: Unexpected event type: '{type(event).__name__}'"
            )


class Scheduler:
    ap_scheduler: APScheduler

    def __init__(self) -> None:
        scheduler = APScheduler()
        scheduler.api_enabled = True
        self.ap_scheduler = scheduler

    def add_job_on_interval(
        self,
        job_func: Callable,
        job_id: str,
        interval_seconds: int = 300,
        misfire_grace_time: int = 900,
    ):
        LOG.debug("Scheduler: Adding job with ID: '%s', Interval: %s (s)", job_id, interval_seconds)

        @self.ap_scheduler.task(
            "interval", id=job_id, seconds=interval_seconds, misfire_grace_time=misfire_grace_time
        )
        def job():
            # wrapping the job in a closure
            LOG.debug(f"Scheduler: Executing Job<{job_id}>")
            job_func()

    def start(self, flask_app):
        self.ap_scheduler.init_app(flask_app)
        logging.getLogger("apscheduler").setLevel(logging.WARNING)

        self.ap_scheduler.add_listener(
            SchedulerEventTracker.event_listener,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED,
        )
        self.ap_scheduler.start()


scheduler = Scheduler()
