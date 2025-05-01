import logging
import typing as t

logging_format_string = "%(asctime)s - [%(levelname)8s] - [%(name)12s]: %(message)s"
logging_format_time = "[%Y-%m-%d %H:%M:%S]"


def get_logger(
    name: t.Optional[str] = None,
    console_log_level=logging.DEBUG,
    logging_format_string: str = logging_format_string,
    logging_format_time: str = logging_format_time,
    filters: t.Iterable[logging.Filter] | None = None,
) -> logging.Logger:
    logger = logging.getLogger(name=name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(console_log_level)

    formatter = logging.Formatter(logging_format_string, logging_format_time)

    ch = logging.StreamHandler()
    ch.setLevel(console_log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if filters is not None:
        for filter in filters:
            logger.addFilter(filter)

    return logger
