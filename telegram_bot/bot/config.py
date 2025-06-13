from dataclasses import dataclass
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@dataclass
class Config:
    # Required variables with defaults
    bot_token: str = os.getenv("BOT_TOKEN", "7868189425:AAEpPFleueIoIEEnXzP2zISDdTXCX9enD-g")
    admin_id: str = os.getenv("ADMIN_ID", "123456789")  # Must be a numeric ID or bot username
    signal_secret: str = os.getenv("SIGNAL_SECRET", "@BAganaga4")
    password: str = os.getenv("PASSWORD", "baganaga")
    
    # Risk modes configuration
    RISK_MODES = {
        "aggressive": 2.0,  # 2% risk
        "balanced": 1.0,    # 1% risk
        "conservative": 0.5 # 0.5% risk
    }
    
    # Default risk mode
    DEFAULT_RISK_MODE = "balanced"
    
    # File paths
    USERS_FILE = "data/users.json"
    
    # MT5 Integration
    mt5_enabled: bool = True
    last_signal: Optional[Dict[str, Any]] = None
    
    # Signal settings
    SIGNAL_COOLDOWN = 300  # 5 minutes between signals
    MAX_SIGNALS_PER_HOUR = 12
    
    def __post_init__(self):
        try:
            # Log configuration status
            logger.info("Initializing configuration...")
            
            # Validate admin_id is numeric or bot username
            if not self.admin_id.isdigit() and not self.admin_id.startswith("https://t.me/"):
                logger.warning(f"ADMIN_ID should be numeric or bot URL, got: {self.admin_id}")
                self.admin_id = "123456789"  # Fallback to default
            
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.USERS_FILE), exist_ok=True)
            
            # Log the configuration (excluding sensitive data)
            logger.info(f"Bot Token: {'*' * len(self.bot_token)}")
            logger.info(f"Admin ID: {self.admin_id}")
            logger.info(f"Signal Secret: {'*' * len(self.signal_secret)}")
            logger.info("Configuration initialized successfully")
            
        except Exception as e:
            logger.error(f"Error during configuration initialization: {e}")
            # Don't raise the error, just log it
            pass
            
    def update_last_signal(self, signal_data: Dict[str, Any]):
        """Update the last signal data"""
        self.last_signal = signal_data

# Initialize config
try:
    config = Config()
    logger.info("Configuration loaded successfully")
except Exception as e:
    logger.error(f"Failed to initialize configuration: {e}")
    # Create a default config if initialization fails
    config = Config()
    logger.info("Using default configuration")

# Initialize and validate configuration
Config.validate() 