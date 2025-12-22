import logging
import os
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler

def setup_logger(name="jain_digitizer"):
    """
    Configures a centralized logger with both console (Rich) and file handlers.
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "app.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # 1. Rich Console Handler
    rich_handler = RichHandler(rich_tracebacks=True, markup=True)
    rich_handler.setLevel(logging.INFO)
    rich_formatter = logging.Formatter("%(message)s")
    rich_handler.setFormatter(rich_formatter)

    # 2. Rotating File Handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(rich_handler)
    logger.addHandler(file_handler)

    return logger

# Create a default instance
logger = setup_logger()

