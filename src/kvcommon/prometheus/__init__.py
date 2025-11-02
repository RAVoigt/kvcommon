import typing as t

PROMETHEUS_AVAILABLE = False

try:
    from prometheus_client import Counter
    from prometheus_client import Gauge
    from prometheus_client import Histogram
    from prometheus_client import Info
    from prometheus_client import Summary
    from prometheus_client.metrics import MetricWrapperBase
    from .utils import robust_labels

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from kvcommon.logger import get_logger


LOG = get_logger("kvc-prometheus")


if PROMETHEUS_AVAILABLE:

    T = t.TypeVar("T", bound="MetricWrapperBase")
    F = t.TypeVar("F", bound=t.Callable[..., t.Any])


    class RobustCounter(Counter):
        def labels(self: T, *labelvalues: t.Any, **labelkwargs: t.Any) -> T:
            return robust_labels(Counter, self, labelvalues=labelvalues, labelkwargs=labelkwargs)

    class RobustGauge(Gauge):
        def labels(self: T, *labelvalues: t.Any, **labelkwargs: t.Any) -> T:
            return robust_labels(Gauge, self, labelvalues=labelvalues, labelkwargs=labelkwargs)

    class RobustHistogram(Histogram):
        def labels(self: T, *labelvalues: t.Any, **labelkwargs: t.Any) -> T:
            return robust_labels(Histogram, self, labelvalues=labelvalues, labelkwargs=labelkwargs)

    class RobustInfo(Info):
        def labels(self: T, *labelvalues: t.Any, **labelkwargs: t.Any) -> T:
            return robust_labels(Info, self, labelvalues=labelvalues, labelkwargs=labelkwargs)

    class RobustSummary(Summary):
        def labels(self: T, *labelvalues: t.Any, **labelkwargs: t.Any) -> T:
            return robust_labels(Summary, self, labelvalues=labelvalues, labelkwargs=labelkwargs)
