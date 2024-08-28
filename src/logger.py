import logging
import os

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s] - %(message)s')
    console_handler.setFormatter(console_format)
    
    # File handler for ERROR level
    error_file_handler = logging.FileHandler('error.log')
    error_file_handler.setLevel(logging.ERROR)
    error_format = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s] - %(message)s')
    error_file_handler.setFormatter(error_format)

    # File handler for DEBUG level
    debug_file_handler = logging.FileHandler('debug.log')
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(console_format)

    logger.addHandler(console_handler)
    logger.addHandler(error_file_handler)
    logger.addHandler(debug_file_handler)
    
    return logger
