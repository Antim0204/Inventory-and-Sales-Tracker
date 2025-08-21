import logging
import sys

def setup_logger(name: str = "app"):
    """Return a configured logger with JSON-like structured output."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt=(
                '{"level": "%(levelname)s", '
                '"time": "%(asctime)s", '
                '"name": "%(name)s", '
                '"message": "%(message)s"}'
            ),
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
