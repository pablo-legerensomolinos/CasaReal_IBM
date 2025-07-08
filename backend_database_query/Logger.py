import os
import logging
import logging.handlers
import sys

from .connectors.Singleton import Singleton

# Ensure the logs directory exists
os.makedirs('logs', exist_ok=True)


class Logger(metaclass=Singleton):
    def __init__(self, logger_name, level: str = "ERROR"):
        # Create a logger
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

        # Create a handler for writing logs to stdout
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(level)
        stdout_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'))

        # Create a handler for writing logs to a file
        file_handler = logging.handlers.RotatingFileHandler(
            filename=f'logs/{logger_name}.log',
            backupCount=2,
            maxBytes=10240 # 10KB
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'))

        # Add both handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stdout_handler)
