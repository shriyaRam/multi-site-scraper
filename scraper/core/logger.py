# scraper/core/logger.py

import logging
from logging.handlers import RotatingFileHandler
import os


class Logger:
    """
    Central logging utility
    """

    def __init__(self, name=__name__, log_filename="scraper.log"):
        self.name = name

        # Determine logs directory relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        log_dir = os.path.join(project_root, "logs")
        os.makedirs(log_dir, exist_ok=True)

        self.log_path = os.path.join(log_dir, log_filename)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            self._add_handlers()

    def _add_handlers(self):
        """Internal helper to attach file + console handlers."""

        # Rotating file handler when file size grows to 5MB
        file_handler = RotatingFileHandler(
            self.log_path,
            maxBytes=5_000_000,
            backupCount=3
        )
        # set format of the log
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        file_handler.setLevel(logging.INFO)

        # send logs to terminal 
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("[%(levelname)s] %(message)s")
        )
        console_handler.setLevel(logging.INFO)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get(self):
        """Return the configured logger instance"""
        return self.logger