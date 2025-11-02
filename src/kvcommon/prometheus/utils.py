import typing as t

PROMETHEUS_AVAILABLE = False

try:
    from prometheus_client import Counter
    from prometheus_client.metrics import MetricWrapperBase

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    pass

from kvcommon.logger import get_logger


LOG = get_logger("kvc-prometheus")


if PROMETHEUS_AVAILABLE:

    T = t.TypeVar("T", bound="MetricWrapperBase")
    F = t.TypeVar("F", bound=t.Callable[..., t.Any])

    LABEL_ERRORS_MISMATCH = Counter(
        "kvc_prometheus_labels_error_mismatch",
        "Count of errors caused by calls to .labels() on prometheus metrics in python with incorrect label names",
        ['expected', 'provided']
    )
    LABEL_ERRORS_COUNT = Counter(
        "kvc_prometheus_labels_error_count",
        "Count of errors caused by calls to .labels() on prometheus metrics in python with incorrect number of label values",
        ['num_labels', 'num_values']
    )

    def _incr_errors_mismatch(expected_labels: list[str], provided_labels: list[str]):
        try:
            LABEL_ERRORS_MISMATCH.labels(expected=expected_labels, provided=provided_labels).inc()
        except Exception as ex:
            LOG.error("Error emitting metrics about metrics errors!: %s", ex)

    def _incr_errors_count(num_labels: int, num_values: int):
        try:
            LABEL_ERRORS_COUNT.labels(num_labels=num_labels, num_values=num_values).inc()
        except Exception as ex:
            LOG.error("Error emitting metrics about metrics errors!: %s", ex)

    def _check_label_names(
        metric_cls_name: str, self_labelnames: tuple[str], labelkwargs: dict | None, raise_on_mismatch: bool = False
    ):
        if not labelkwargs:
            LOG.warning("Prometheus client exception suggested label mismatch, but no labelkwargs passed")
            return
        sorted_labelkwargs = sorted(labelkwargs)
        sorted_selflabelnames = sorted(self_labelnames)
        if sorted_labelkwargs != sorted_selflabelnames:
            err_str = f"{metric_cls_name}: Incorrect label names:: Provided keys: '{sorted_labelkwargs}' -- Expected keys: '{sorted_selflabelnames}'"
            LOG.error(err_str)
            _incr_errors_mismatch(expected_labels=sorted_selflabelnames, provided_labels=sorted_labelkwargs)
            if raise_on_mismatch:
                raise ValueError(err_str)

    def _check_label_count(
        metric_cls_name: str, self_labelnames: tuple[str], labelvalues: tuple | None, raise_on_mismatch: bool = False
    ):
        if not labelvalues:
            LOG.warning("Prometheus client exception suggested label miscount, but no labelvalues passed")
            return
        num_values = len(labelvalues)
        num_labels = len(self_labelnames)
        if num_values != num_labels:
            err_str = (
                f"{metric_cls_name}: Incorrect label count:: # of values: '{num_values}' -- # of labels: '{num_labels}'"
            )
            LOG.error(err_str)
            _incr_errors_count(num_labels=num_labels, num_values=num_values)
            if raise_on_mismatch:
                raise ValueError(err_str)

    def robust_labels(cls: t.Type, self: T, *labelvalues: t.Any, **labelkwargs: t.Any) -> T:
        """
        An implementation of the .labels() method from prometheus_client metrics classes that treats
        incorrect labels as something to log as an error, not an execution-halting exception.
        """
        try:
            return super(cls, self).labels(*labelvalues, **labelkwargs)  # type: ignore

        except ValueError as ex:
            if "Incorrect label names" in str(ex):
                _check_label_names(
                    cls.__name__, self_labelnames=self._labelnames, labelkwargs=labelkwargs, raise_on_mismatch=False
                )
            if "Incorrect label count" in str(ex):
                _check_label_count(
                    cls.__name__, self_labelnames=self._labelnames, labelvalues=labelvalues, raise_on_mismatch=False
                )

            # Return self so that the call-chain can continue
            return self
