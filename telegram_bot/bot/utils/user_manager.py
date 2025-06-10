import json
import os
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from ..config import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserPreferences:
    risk_mode: str = config.DEFAULT_RISK_MODE
    risk_percentage: float = config.RISK_MODES[config.DEFAULT_RISK_MODE]
    is_authorized: bool = False

class UserManager:
    def __init__(self):
        self.users: Dict[int, UserPreferences] = {}
        self._load_users()
    
    def _load_users(self):
        """Load users from JSON file"""
        if os.path.exists(config.USERS_FILE):
            try:
                with open(config.USERS_FILE, 'r') as f:
                    data = json.load(f)
                    self.users = {
                        int(user_id): UserPreferences(**prefs)
                        for user_id, prefs in data.items()
                    }
            except Exception as e:
                print(f"Error loading users: {e}")
                self.users = {}
    
    def _save_users(self):
        """Save users to JSON file"""
        os.makedirs(os.path.dirname(config.USERS_FILE), exist_ok=True)
        with open(config.USERS_FILE, 'w') as f:
            json.dump(
                {str(user_id): asdict(prefs) for user_id, prefs in self.users.items()},
                f,
                indent=2
            )
    
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        return user_id in self.users and self.users[user_id].is_authorized
    
    def authorize_user(self, user_id: int) -> None:
        """Authorize a user"""
        logger.info(f"Authorizing user {user_id}")
        if user_id not in self.users:
            self.users[user_id] = UserPreferences(is_authorized=True)
        else:
            self.users[user_id].is_authorized = True
        self._save_users()
        logger.info(f"User {user_id} authorized and saved.")
    
    def set_risk_mode(self, user_id: int, mode: str) -> bool:
        """Set user's risk mode"""
        if mode not in config.RISK_MODES:
            return False
        
        if user_id not in self.users:
            self.users[user_id] = UserPreferences()
        
        self.users[user_id].risk_mode = mode
        self.users[user_id].risk_percentage = config.RISK_MODES[mode]
        self._save_users()
        return True
    
    def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences"""
        return self.users.get(user_id)
    
    def set_risk_percentage(self, user_id: int, percentage: float) -> None:
        """Set custom risk percentage"""
        if user_id not in self.users:
            self.users[user_id] = UserPreferences()
        
        self.users[user_id].risk_percentage = max(0.1, min(5.0, percentage))
        self._save_users()

# Global user manager instance
user_manager = UserManager() 