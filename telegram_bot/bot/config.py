from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Config:
    bot_token: str = os.getenv("BOT_TOKEN")
    admin_id: str = os.getenv("ADMIN_ID")
    signal_secret: str = os.getenv("SIGNAL_SECRET")
    password: str = os.getenv("PASSWORD")
    
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
    
    def __post_init__(self):
        if not all([self.bot_token, self.admin_id, self.signal_secret, self.password]):
            raise ValueError("Missing required environment variables")

config = Config() 