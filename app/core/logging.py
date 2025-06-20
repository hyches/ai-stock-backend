"""
Logging configuration for the AI Stock Portfolio Platform Backend.

This module sets up application-wide logging with both console and rotating file handlers.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from app.core.config import settings
import os

def setup_logging():
    """
    Set up logging for the application.

    Ensures the logs directory exists, configures a logger with both console and rotating file handlers,
    and applies the log format and level from settings.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Create logger
    logger = logging.getLogger("ai_stock_analysis")
    logger.setLevel(settings.LOG_LEVEL)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )

    # Create formatters
    formatter = logging.Formatter(settings.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging() 