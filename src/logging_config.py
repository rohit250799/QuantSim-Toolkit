import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def make_file_handler(filename: str, level: int) -> logging.FileHandler:
    """Makes file handler to write logs to the correct log file"""
    handler = logging.FileHandler(LOG_DIR / filename)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return handler


def configure_logging() -> None:
    """Stores all the configurations of the logger"""
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        force=True
    )

    logging.getLogger("app").addHandler(
        make_file_handler("app.log", logging.INFO)
    )

    logging.getLogger("db").addHandler(
        make_file_handler("db_logs.log", logging.DEBUG)
    )

    logging.getLogger("market_data").addHandler(
        make_file_handler("market_data.log", logging.DEBUG)
    )

    logging.getLogger("validation").addHandler(
        make_file_handler("validation.log", logging.DEBUG)
    )

    logging.getLogger("pytest").addHandler(
        make_file_handler("pytest_errors.log", logging.ERROR)
    )

    logging.getLogger("analytics").addHandler(
        make_file_handler("analytics.log", logging.DEBUG)
    )

    logging.getLogger("flow").addHandler(
        make_file_handler("flow.log", logging.DEBUG)
    )

    logging.getLogger("cli").addHandler(
        make_file_handler("cli.log", logging.DEBUG)
    )

    # Global error sink
    logging.getLogger().addHandler(
        make_file_handler("errors.log", logging.ERROR)
    )

