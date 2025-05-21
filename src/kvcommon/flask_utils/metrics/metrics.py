import typing as t
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


def inc(metric: Counter | Gauge, amount: int = 1, labels: dict | None = None):
    if labels:
        metric.labels(**labels).inc(amount=amount)
    else:
        metric.inc(amount=amount)


def dec(gauge: Gauge, amount: int = 1, labels: dict | None = None):
    if labels:
        gauge.labels(**labels).dec(amount=amount)
    else:
        gauge.dec()


def set_to(gauge: Gauge, value: int = 1, labels: dict | None = None):
    if labels:
        gauge.labels(**labels).set(value=value)
    else:
        gauge.set(value=value)


def add_prefix(label: str, prefix: str | None = None) -> str:
    if not prefix:
        return label
    return f"{prefix}_{label}"


def get_info_metric(
    metric_name: str,
    label_names: list[str],
    description: str = "App Info",
    multiprocess_mode: t.Literal[
        "all", "liveall", "min", "livemin", "max", "livemax", "sum", "livesum", "mostrecent", "livemostrecent"
    ] = "mostrecent",
) -> Gauge:
    """
    Info metrics don't play nicely with multiproc prometheus, so we use a gauge instead with a mode such as "max" or "mostrecent"
    """
    return Gauge(
        metric_name,
        description,
        labelnames=label_names,
        multiprocess_mode=multiprocess_mode,
    )

_APP_INFO_metrics: dict[str, Gauge]
_HTTP_RESPONSE_COUNT_metrics: dict[str, Counter]
_SCHEDULER_JOB_EVENT_metrics: dict[str, Counter]
_SERVER_REQUEST_SECONDS_metrics: dict[str, Histogram]


class DefaultMetrics(metaclass=SingletonMeta):
    """
    Wrap these default metrics in this singleton so they can be instantiated on-demand.
    Avoid registering unwanted metrics accidentally just by importing. Return pre-existing metrics by name.
    """

    @staticmethod
    def APP_INFO(
        metric_name: str,
        label_names: list[str],
        description: str = "App Info",
        multiprocess_mode: t.Literal[
            "all", "liveall", "min", "livemin", "max", "livemax", "sum", "livesum", "mostrecent", "livemostrecent"
        ] = "mostrecent",
    ) -> Gauge:

        metric: Gauge | None = _APP_INFO_metrics.get(metric_name, None)
        if not metric:
            metric = get_info_metric(metric_name, label_names, description=description, multiprocess_mode=multiprocess_mode)
            _APP_INFO_metrics[metric_name] = metric

        return metric

    @staticmethod
    def HTTP_RESPONSE_COUNT(
        name_prefix: str | None = None,
        description: str = "Count of HTTP response statuses returned by server",
        labelnames: list[str] | None = None,
        full_name_override: str | None = None,
    ) -> Counter:
        if full_name_override:
            metric_name = full_name_override
        else:
            metric_name = add_prefix("scheduler_job_event_total", name_prefix)
        if not labelnames:
            labelnames = ["path"]
        metric: Counter | None = _HTTP_RESPONSE_COUNT_metrics.get(metric_name, None)
        if not metric:
            metric = Counter(metric_name, description, labelnames=labelnames)
            _HTTP_RESPONSE_COUNT_metrics[metric_name] = metric
        return metric

    @staticmethod
    def SCHEDULER_JOB_EVENT(
        name_prefix: str | None = None,
        description: str = "Count of scheduled job events by job id and event",
        labelnames: list[str] | None = None,
        full_name_override: str | None = None,
    ) -> Counter:
        if full_name_override:
            metric_name = full_name_override
        else:
            metric_name = add_prefix("scheduler_job_event_total", name_prefix)
        if not labelnames:
            labelnames = ["job_id", "event"]
        metric: Counter | None = _SCHEDULER_JOB_EVENT_metrics.get(metric_name, None)
        if not metric:
            metric = Counter(metric_name, description, labelnames=labelnames)
            _SCHEDULER_JOB_EVENT_metrics[metric_name] = metric
        return metric

    @staticmethod
    def SERVER_REQUEST_SECONDS(
        name_prefix: str | None = None,
        description: str = "Time taken for server to handle request",
        labelnames: list[str] | None = None,
        full_name_override: str | None = None,
    ) -> Histogram:
        if full_name_override:
            metric_name = full_name_override
        else:
            metric_name = add_prefix("scheduler_job_event_total", name_prefix)
        if not labelnames:
            labelnames = ["path"]
        metric: Histogram | None = _SERVER_REQUEST_SECONDS_metrics.get(metric_name, None)
        if not metric:
            metric = Histogram(metric_name, description, labelnames=labelnames)
            _SERVER_REQUEST_SECONDS_metrics[metric_name] = metric
        return metric
