from dataclasses import dataclass
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Config:
    bot_token: str = os.getenv("BOT_TOKEN")
    admin_id: str = os.getenv("ADMIN_ID")
    signal_secret: str = os.getenv("SIGNAL_SECRET")
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
        if not all([self.bot_token, self.admin_id, self.signal_secret, self.password]):
            raise ValueError("Missing required environment variables")
            
    def update_last_signal(self, signal_data: Dict[str, Any]):
        """Update the last signal data"""
        self.last_signal = signal_data

config = Config() 