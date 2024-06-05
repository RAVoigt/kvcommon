import logging
import typing as t

from .vars import KVC_LOG_DATEFMT
from .vars import KVC_LOG_FORMAT

logging_format_string = KVC_LOG_FORMAT or "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
logging_format_time = KVC_LOG_DATEFMT or "[%Y-%m-%d %H:%M:%S]"


def get_logger(
    name: t.Optional[str] = None,
    console_log_level=logging.DEBUG,
    logging_format_string: str = logging_format_string,
    logging_format_time: str = logging_format_time,
    filters: t.Iterable[logging.Filter] | None = None
):
    logger = logging.getLogger(name=name)
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
