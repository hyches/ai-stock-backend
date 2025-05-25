import logging
import sys
from logging.handlers import RotatingFileHandler
from app.config import Settings
settings = Settings()

def setup_logging():
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