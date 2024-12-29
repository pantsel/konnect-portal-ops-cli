"""
This module provides a custom logger with colored output for different log levels.
"""

import logging
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors to log levels.
    """
    # Define color codes for log levels
    COLORS = {
        "DEBUG": "\033[94m",    # Blue
        "INFO": "\033[92m",     # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",    # Red
        "CRITICAL": "\033[95m", # Magenta
    }
    RESET = "\033[0m"  # Reset color

    def format(self, record):
        # Add color to the log level name
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

class Logger(logging.Logger):
    """
    Singleton logger class with colored console output.
    """
    _instance: Optional[logging.Logger] = None

    def __new__(cls, name: str = "app", level: int = logging.DEBUG):
        if not cls._instance:
            cls._instance = cls._initialize_logger(name, level)
        return cls._instance

    @staticmethod
    def _initialize_logger(name: str, level: int) -> logging.Logger:
        """
        Initialize the singleton logger instance.

        Args:
            name (str): Name of the logger.
            level (int): Logging level.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Avoid duplicate handlers
        if not logger.handlers:

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # Colored formatter for console
            colored_formatter = ColoredFormatter(
                fmt='%(asctime)s - %(name)s - %(levelname)-8s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # Set formatters
            console_handler.setFormatter(colored_formatter)

            # Add handlers
            logger.addHandler(console_handler)

        return logger
