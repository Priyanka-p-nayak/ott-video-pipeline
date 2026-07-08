"""Centralized logging configuration for the whole application."""

import logging
import os

LOG_FOLDER = 'logs'
LOG_FILE = os.path.join(LOG_FOLDER, 'app.log')


def setup_logger(name: str) -> logging.Logger:
    """
    Create and return a configured logger instance.

    name: usually pass __name__ from the calling file, so log messages
          show exactly which file/module produced them.
    """
    os.makedirs(LOG_FOLDER, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if the logger is called multiple times
    if not logger.handlers:
        file_handler = logging.FileHandler(LOG_FILE)
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger