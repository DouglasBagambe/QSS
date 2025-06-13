import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Configure logging for the bot"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler (rotating log files)
    file_handler = RotatingFileHandler(
        'logs/bot.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific loggers
    logging.getLogger('aiogram').setLevel(logging.INFO)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    logging.info("Logging system initialized") 