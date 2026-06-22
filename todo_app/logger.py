"""Logging setup with rotating file handlers.

Output targets:
    - app_handler  → logs/app.log   (DEBUG+, 10 MB × 5 rotations)
    - err_handler  → logs/error.log (ERROR+, 10 MB × 5 rotations)
    - console      → stderr         (WARNING+, or DEBUG+ when --debug)
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")


def setup_logging(level: str = "INFO") -> None:
    """Initialize the root logger with rotating files and console output.

    Only configures handlers once — subsequent calls are no-ops.
    """
    LOG_DIR.mkdir(exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Guard against double-initialisation.
    if root_logger.handlers:
        return

    # --- app log: everything DEBUG and above ---
    app_handler = RotatingFileHandler(
        filename=LOG_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(fmt)

    # --- error log: only ERROR and above ---
    error_handler = RotatingFileHandler(
        filename=LOG_DIR / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(fmt)

    # --- console: WARNING+ by default, DEBUG+ in debug mode ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if level == "DEBUG" else logging.WARNING)
    console_handler.setFormatter(fmt)

    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    root_logger.info("Logging initialised (level=%s)", level)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger with the given dotted name."""
    return logging.getLogger(name)
