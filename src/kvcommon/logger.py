import logging
import typing as t

log_format_style: t.Literal["%", "{"] = "{"
log_format_percent = "%(asctime)s - [%(levelname)8s] - [%(name)12s]: %(message)s"
log_format_braces = "{asctime} - [{levelname:^8}] - [{name:^14}]: {message}"


if log_format_style == "{":
    log_format_string = log_format_braces
else:
    log_format_string = log_format_percent

log_format_time = "[%Y-%m-%d %H:%M:%S]"


def get_logger(
    name: t.Optional[str] = None,
    console_log_level=logging.DEBUG,
    logging_format_string: str | None = log_format_string,
    logging_format_time: str | None = log_format_time,
    logging_format_style: t.Literal["%", "{"] = log_format_style,
    filters: t.Iterable[logging.Filter] | None = None,
) -> logging.Logger:
    logger = logging.getLogger(name=name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(console_log_level)

    logging_format_string = logging_format_string or log_format_string
    logging_format_time = logging_format_time or log_format_time

    try:
        formatter = logging.Formatter(logging_format_string, logging_format_time, style=logging_format_style)
    except ValueError:
        # In case of mismatches in format string vs requested style
        logging.warning(
            "Mismatch in log format style ('%s') versus log format string ('%s') - Falling back to defaults for safety",
            logging_format_style, logging_format_string
        )
        if logging_format_style == "%":
            formatter = logging.Formatter(log_format_percent, logging_format_time, style=logging_format_style)
        elif logging_format_style == "{":
            formatter = logging.Formatter(log_format_braces, logging_format_time, style=logging_format_style)

    ch = logging.StreamHandler()
    ch.setLevel(console_log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if filters is not None:
        for filter in filters:
            logger.addFilter(filter)

    return logger
