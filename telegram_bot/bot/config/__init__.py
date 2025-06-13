"""Configuration module for the bot."""
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration class."""
    # Bot settings
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = os.getenv("ADMIN_ID")
    SIGNAL_SECRET = os.getenv("SIGNAL_SECRET")
    
    # Default settings
    DEFAULT_RISK_MODE = "moderate"
    RISK_MODES = {
        "conservative": 0.5,
        "moderate": 1.0,
        "aggressive": 2.0
    }
    
    # Trading settings
    DEFAULT_TIMEFRAME = "H1"
    DEFAULT_PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD"]
    
    # Notification settings
    ENABLE_NOTIFICATIONS = True
    NOTIFICATION_INTERVAL = 300  # 5 minutes
    
    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is not set")
        if not cls.ADMIN_ID:
            raise ValueError("ADMIN_ID is not set")
        if not cls.SIGNAL_SECRET:
            raise ValueError("SIGNAL_SECRET is not set")
        
        # Validate ADMIN_ID is numeric
        try:
            cls.ADMIN_ID = int(cls.ADMIN_ID)
        except ValueError:
            logging.warning(f"ADMIN_ID should be numeric, got: {cls.ADMIN_ID}")
            cls.ADMIN_ID = 123456789  # Default fallback
        
        logging.info(f"Bot Token: {'*' * len(cls.BOT_TOKEN)}")
        logging.info(f"Admin ID: {cls.ADMIN_ID}")
        logging.info(f"Signal Secret: {'*' * len(cls.SIGNAL_SECRET)}")
        logging.info("Configuration initialized successfully")

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Validate configuration
Config.validate() 