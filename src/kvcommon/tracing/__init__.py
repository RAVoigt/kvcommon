import typing as t
from functools import wraps
from opentelemetry import trace


def _unwrap_function(func) -> t.Callable:
    """Extracts the raw underlying function from Python descriptors."""
    if isinstance(func, (staticmethod, classmethod)):
        return func.__func__
    if isinstance(func, property):
        return func.fget # type: ignore
    return func


def auto_trace_span(name_or_func=None):
    # Used without parentheses: '@auto_trace_span'
    if callable(name_or_func):
        func = name_or_func
        raw_func = _unwrap_function(func)

        module_name = raw_func.__module__
        tracer = trace.get_tracer(module_name)
        span_name = raw_func.__name__

        @wraps(raw_func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name):
                return raw_func(*args, **kwargs)
        return wrapper

    # Used with parentheses '@auto_trace_span()' or '@auto_span("custom_name")'
    def decorator(func):
        raw_func = _unwrap_function(func)
        module_name = raw_func.__module__
        tracer = trace.get_tracer(module_name)

        span_name = name_or_func if isinstance(name_or_func, str) else raw_func.__name__

        # Handle property descriptor wrapping
        if isinstance(func, property):
            @wraps(raw_func)
            def property_wrapper(*args, **kwargs):
                with tracer.start_as_current_span(span_name):
                    return raw_func(*args, **kwargs)
            return property(property_wrapper)

        @wraps(raw_func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name):
                return raw_func(*args, **kwargs)

        if isinstance(func, staticmethod):
            return staticmethod(wrapper)
        if isinstance(func, classmethod):
            return classmethod(wrapper)

        return wrapper

    return decorator
