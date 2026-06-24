import logging
import logging.handlers
import queue
import typing as t

async_log_queue = queue.Queue(-1)
_global_listener: t.Optional[logging.handlers.QueueListener] = None

log_format_style: t.Literal["%", "{"] = "{"
log_format_percent = "%(asctime)s - [%(levelname)8s] - [%(name)12s]: %(message)s"
log_format_braces = "{asctime} - [{levelname:^8}] - [{name:^14}]: {message}"
log_format_string = log_format_braces if log_format_style == "{" else log_format_percent
log_format_time = "[%Y-%m-%d %H:%M:%S]"


def get_async_queue_listener() -> logging.handlers.QueueListener | None:
    return _global_listener


def _make_formatter(
    fmt_str: str | None,
    fmt_time: str | None,
    fmt_style: t.Literal["%", "{"],
) -> logging.Formatter:
    active_str = fmt_str or log_format_string
    active_time = fmt_time or log_format_time

    try:
        return logging.Formatter(active_str, active_time, style=fmt_style)
    except ValueError:
        # Fallback if there's a mismatch between style and string variables
        fallback = log_format_braces if fmt_style == "{" else log_format_percent
        return logging.Formatter(fallback, active_time, style=fmt_style)


def init_async_logging() -> None:
    """
    Call this ONCE at your app startup (e.g., in Quart's before_serving).
    It registers a single console handler inside a single background thread.
    """
    global _global_listener
    if _global_listener is not None:
        return
    base_console_handler = logging.StreamHandler()
    _global_listener = logging.handlers.QueueListener(async_log_queue, base_console_handler)
    _global_listener.start()


def get_logger(
    name: t.Optional[str] = None,
    console_log_level=logging.DEBUG,
    logging_format_string: str | None = None,
    logging_format_time: str | None = None,
    logging_format_style: t.Literal["%", "{"] = log_format_style,
    filters: t.Iterable[logging.Filter] | None = None,
    async_logger: bool = False,
    async_root_logger: bool = False
) -> logging.Logger:
    global _global_listener

    formatter = _make_formatter(logging_format_string, logging_format_time, logging_format_style)

    if (async_logger or async_root_logger) and _global_listener is None:
        init_async_logging()

    if async_root_logger:
        root_logger = logging.getLogger()
        if not any(isinstance(h, logging.handlers.QueueHandler) for h in root_logger.handlers):
            q_handler = logging.handlers.QueueHandler(async_log_queue)
            root_logger.addHandler(q_handler)

    logger = logging.getLogger(name=name)
    logger.setLevel(console_log_level)

    if logger.handlers:
        logger.handlers.clear()

    if async_logger:
        handler = logging.handlers.QueueHandler(async_log_queue)
        handler.setFormatter(formatter)
        logger.propagate = False  # Avoid duplicating to an async root
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(console_log_level)
        # If it's a standard logger, disable propagation if the root logger is ALSO async
        if async_root_logger or logging.getLogger().handlers:
            logger.propagate = False

    logger.addHandler(handler)

    if filters is not None:
        for f in filters:
            logger.addFilter(f)

    return logger
