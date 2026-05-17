"""Logging utility using loguru."""
from loguru import logger
import sys
from config.settings import LOG_LEVEL

# Remove default handler
logger.remove()

# Add custom handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True
)

# File handler for persistent logs
logger.add(
    "logs/system_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="30 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

def get_logger(name: str):
    """Get a logger instance with module name."""
    return logger.bind(name=name)
