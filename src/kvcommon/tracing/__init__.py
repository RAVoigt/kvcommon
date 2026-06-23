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


def auto_trace_span(name=None):
    def decorator(func):
        # Extract the real raw function so we can safely read __module__ and __name__
        raw_func = _unwrap_function(func)

        module_name = raw_func.__module__
        tracer = trace.get_tracer(module_name)
        span_name = name or raw_func.__name__

        # If it's a property, we must wrap the getter execution
        if isinstance(func, property):
            @wraps(raw_func)
            def property_wrapper(*args, **kwargs):
                with tracer.start_as_current_span(span_name):
                    return raw_func(*args, **kwargs)
            return property(property_wrapper)

        # For staticmethod, classmethod, or normal functions
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
