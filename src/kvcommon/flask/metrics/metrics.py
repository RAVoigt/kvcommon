from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import Info
from prometheus_client import Summary

from kvcommon.exceptions import KVCFlaskException


class FlaskMetricsException(KVCFlaskException):
    pass


# https://prometheus.io/docs/practices/naming/


def incr(metric: Counter | Gauge):
    metric.inc()


def decr(gauge: Gauge):
    gauge.dec()


def set_app_info(app_version: str):
    APP_INFO.info(dict(version=app_version))


APP_INFO = Info("app", "Application info")


SCHEDULER_JOB_EVENT = Counter(
    "scheduler_job_event_total",
    "Counter of scheduled job events by event enum",
    labelnames=[
        "job_id",
        "event",
    ],
)

# Total time spent from start to finish on a request
SERVER_REQUEST_SECONDS = Histogram(
    "server_request_seconds",
    "Time taken for server to handle request",
    labelnames=["path"],
)

HTTP_RESPONSE_COUNT = Counter(
    "http_request_status_proxy_total",
    "Count of HTTP response statuses returned by server",
    labelnames=[
        "code",
    ],
)
