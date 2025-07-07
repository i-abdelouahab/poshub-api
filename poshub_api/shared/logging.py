import logging

import structlog


def configure_logging(debug: bool = False) -> None:
    """Configure structured logging for the application.

    Args:
        debug: Whether to enable debug logging.
    """
    logging_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        format="%(message)s",
        level=logging_level,
        handlers=[logging.StreamHandler()],
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if debug:
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
