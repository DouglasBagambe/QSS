from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Trading pairs to monitor
SYMBOLS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD",  # Major Forex
    "EUR/GBP", "EUR/JPY", "GBP/JPY", "AUD/JPY", "EUR/AUD", "GBP/AUD",  # Crosses
    "XAU/USD", "XAG/USD",  # Precious Metals
    "BTC/USD", "ETH/USD", "BNB/USD",  # Major Cryptos
    "SPX500", "US30", "US100", "UK100", "DE30", "JP225"  # Major Indices
]

# Timeframes to analyze
TIMEFRAMES = ["4h", "1h", "30m", "15m"]

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Exchange configuration
EXCHANGE_ID = "binance"  # Primary exchange
EXCHANGE_API_KEY = os.getenv('EXCHANGE_API_KEY')
EXCHANGE_SECRET = os.getenv('EXCHANGE_SECRET')

# Strategy parameters
RISK_REWARD_RATIO = 2.0  # Minimum risk-reward ratio for signals
MAX_RISK_PER_TRADE = 0.02  # Maximum risk per trade (2% of account)
MIN_PIPS_FOR_ENTRY = 10  # Minimum pips for valid entry
MIN_CONFIDENCE = 0.6  # Minimum confidence score for signals

# Session times (UTC)
LONDON_SESSION_START = 7  # 07:00 UTC
LONDON_SESSION_END = 16   # 16:00 UTC
NY_SESSION_START = 12     # 12:00 UTC
NY_SESSION_END = 21       # 21:00 UTC

# Technical parameters
ORDER_BLOCK_LOOKBACK = 20  # Number of candles to look back for order blocks
FAIR_VALUE_GAP_THRESHOLD = 0.0002  # Minimum size for fair value gap
LIQUIDITY_CLUSTER_SIZE = 3  # Number of candles to form a liquidity cluster
SWING_STRENGTH_THRESHOLD = 0.0005  # Minimum size for swing high/low
BOS_CONFIRMATION_CANDLES = 3  # Number of candles to confirm BOS

# Market structure parameters
TREND_STRENGTH_THRESHOLD = 0.001  # Minimum price movement for trend
SUPPORT_RESISTANCE_LOOKBACK = 50  # Number of candles to look back for S/R levels
BREAKOUT_CONFIRMATION = 3  # Number of candles to confirm breakout

# Risk management
MAX_OPEN_TRADES = 5  # Maximum number of open trades
MAX_DAILY_TRADES = 10  # Maximum number of trades per day
MAX_DAILY_LOSS = 0.05  # Maximum daily loss (5% of account)
TRAILING_STOP_ACTIVATION = 0.01  # Activate trailing stop at 1% profit
TRAILING_STOP_DISTANCE = 0.005  # Trailing stop distance (0.5%)

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = "logs/qss_ai.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_ROTATION = "1 day"  # Rotate logs daily
LOG_BACKUP_COUNT = 7  # Keep 7 days of logs

# Performance monitoring
PERFORMANCE_METRICS = {
    'win_rate': 0.0,
    'profit_factor': 0.0,
    'average_win': 0.0,
    'average_loss': 0.0,
    'max_drawdown': 0.0,
    'total_trades': 0,
    'winning_trades': 0,
    'losing_trades': 0
}

# Alert thresholds
ALERT_THRESHOLDS = {
    'win_rate': 0.5,  # Alert if win rate falls below 50%
    'profit_factor': 1.5,  # Alert if profit factor falls below 1.5
    'max_drawdown': 0.1,  # Alert if drawdown exceeds 10%
    'daily_loss': 0.03  # Alert if daily loss exceeds 3%
} 