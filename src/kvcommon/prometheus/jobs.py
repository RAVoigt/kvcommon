import typing as t

from kvcommon.asynchronous.jobs.metrics import JobTimer


from . import PROMETHEUS_AVAILABLE
if PROMETHEUS_AVAILABLE:
    from prometheus_client import Histogram
    from prometheus_client import Summary
    from kvcommon.prometheus import RobustSummary
    from kvcommon.prometheus import RobustHistogram


class JobTimerPrometheus(JobTimer):
    _metric: Histogram | Summary
    _start_time: float | None = None

    def __init__(
            self,
            metric: Histogram | Summary | RobustHistogram | RobustSummary,
            start_callback: t.Callable | None = None
        ) -> None:
        self._metric = metric

        def callback_stop(duration: float):
            metric.observe(duration)

        super().__init__(stop_callback=callback_stop, start_callback=start_callback)
