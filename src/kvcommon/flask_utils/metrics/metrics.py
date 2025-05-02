from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import Info
from prometheus_client import Summary

from kvcommon.exceptions import KVCFlaskException
from kvcommon.singleton import SingletonMeta


class FlaskMetricsException(KVCFlaskException):
    pass


# https://prometheus.io/docs/practices/naming/


def incr(metric: Counter | Gauge):
    metric.inc()


def decr(gauge: Gauge):
    gauge.dec()


def metric_name_prefix(label: str, prefix: str | None = None) -> str:
    if not prefix:
        return label
    return f"{prefix}_{label}"


class DefaultMetrics(metaclass=SingletonMeta):
    """
    Wrap these default metrics in this singleton so they can be instantiated on-demand.
    Avoid registering unwanted metrics accidentally just by importing.
    """

    @staticmethod
    def APP_INFO(label_prefix: str | None = None) -> Info:
        return Info(metric_name_prefix("app", label_prefix), "Application info")

    @staticmethod
    def SCHEDULER_JOB_EVENT(label_prefix: str | None = None) -> Counter:
        return Counter(
            metric_name_prefix("scheduler_job_event_total", label_prefix),
            "Counter of scheduled job events by event enum",
            labelnames=["job_id", "event"],
        )

    @staticmethod
    def SERVER_REQUEST_SECONDS(label_prefix: str | None = None) -> Histogram:
        # Total time spent from start to finish on a request
        return Histogram(
            metric_name_prefix("server_request_seconds", label_prefix),
            "Time taken for server to handle request",
            labelnames=["path"],
        )

    @staticmethod
    def HTTP_RESPONSE_COUNT(label_prefix: str | None = None) -> Counter:
        return Counter(
            metric_name_prefix("http_request_status_total", label_prefix),
            "Count of HTTP response statuses returned by server",
            labelnames=["code"],
        )
