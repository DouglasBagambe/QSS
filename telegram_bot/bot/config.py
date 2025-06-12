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
    bot_token: str = os.getenv("BOT_TOKEN", "7868189425:AAEpPFleueIoIEEnXzP2zISDdTXCX9enD-g")
    admin_id: str = os.getenv("ADMIN_ID", "123456789")  # Replace with your actual admin ID
    signal_secret: str = os.getenv("SIGNAL_SECRET", "default_secret_key")
    password: str = "baganaga"
    
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
        # Log configuration status
        logger.info("Initializing configuration...")
        
        # Check for critical variables
        if not self.bot_token:
            logger.error("BOT_TOKEN is not set!")
            raise ValueError("BOT_TOKEN is required")
            
        if not self.admin_id:
            logger.warning("ADMIN_ID is not set. Some features may be limited.")
            
        if not self.signal_secret:
            logger.warning("SIGNAL_SECRET is not set. Using default value.")
            
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.USERS_FILE), exist_ok=True)
        
        logger.info("Configuration initialized successfully")
            
    def update_last_signal(self, signal_data: Dict[str, Any]):
        """Update the last signal data"""
        self.last_signal = signal_data

# Initialize config
try:
    config = Config()
    logger.info("Configuration loaded successfully")
except Exception as e:
    logger.error(f"Failed to initialize configuration: {e}")
    raise 