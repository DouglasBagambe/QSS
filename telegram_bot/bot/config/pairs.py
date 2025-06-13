"""Trading pairs configuration"""

# Available trading pairs
TRADING_PAIRS = [
    "EURUSD",  # Euro/US Dollar
    "GBPUSD",  # British Pound/US Dollar
    "USDJPY",  # US Dollar/Japanese Yen
    "USDCHF",  # US Dollar/Swiss Franc
    "AUDUSD",  # Australian Dollar/US Dollar
    "USDCAD",  # US Dollar/Canadian Dollar
    "GBPJPY",  # British Pound/Japanese Yen
    "EURJPY",  # Euro/Japanese Yen
    "XAUUSD",  # Gold/US Dollar
    "XAGUSD",  # Silver/US Dollar
    "NAS100",  # Nasdaq 100 Index
    "US300",   # S&P 500 Index
]

# Pair display names
PAIR_DISPLAY_NAMES = {
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDJPY": "USD/JPY",
    "USDCHF": "USD/CHF",
    "AUDUSD": "AUD/USD",
    "USDCAD": "USD/CAD",
    "GBPJPY": "GBP/JPY",
    "EURJPY": "EUR/JPY",
    "XAUUSD": "XAU/USD",
    "XAGUSD": "XAG/USD",
    "NAS100": "NAS100",
    "US300": "US300",
}

# Pair descriptions
PAIR_DESCRIPTIONS = {
    "EURUSD": "Euro/US Dollar - Most traded currency pair",
    "GBPUSD": "British Pound/US Dollar - Cable",
    "USDJPY": "US Dollar/Japanese Yen - The Ninja",
    "USDCHF": "US Dollar/Swiss Franc - Swissy",
    "AUDUSD": "Australian Dollar/US Dollar - Aussie",
    "USDCAD": "US Dollar/Canadian Dollar - Loonie",
    "GBPJPY": "British Pound/Japanese Yen - The Dragon",
    "EURJPY": "Euro/Japanese Yen - The Yen Cross",
    "XAUUSD": "Gold/US Dollar - Gold",
    "XAGUSD": "Silver/US Dollar - Silver",
    "NAS100": "Nasdaq 100 Index - Tech Stocks",
    "US300": "S&P 500 Index - US Stocks",
}

# Default pairs for quick access
DEFAULT_PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD"]

# Pairs grouped by category
PAIR_CATEGORIES = {
    "Major Pairs": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD"],
    "Cross Pairs": ["GBPJPY", "EURJPY"],
    "Commodities": ["XAUUSD", "XAGUSD"],
    "Indices": ["NAS100", "US300"],
} 