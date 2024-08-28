import os
from loguru import logger
import sys


def get_logger(name: str):
    env = os.getenv("ENV", "production")

    # Remove default handler
    logger.remove()

    # Add new configuration based on the environment
    if env == "development":
        # Debug level logging with stacktraces for development
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            backtrace=True,
            diagnose=True,
        )

    # Error level logging with clean messages for production
    logger.add(
        sys.stderr,
        level="ERROR",
        format="<red>{time:YYYY-MM-DD HH:mm:ss.SSS}</red> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        backtrace=env == "development",
        diagnose=env == "development",
    )

    return logger.bind(name=name)
