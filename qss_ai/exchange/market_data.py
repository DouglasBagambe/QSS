import pandas as pd
from typing import Dict, Optional
from .exchange_interface import ExchangeFactory
from ..config.settings import EXCHANGE_ID, SYMBOLS, TIMEFRAMES

class MarketDataProvider:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.exchange = ExchangeFactory.create_exchange(EXCHANGE_ID, api_key, api_secret)
        self.cache = {}
        self.cache_timeout = 60  # Cache timeout in seconds

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """
        Fetch OHLCV data for a symbol and timeframe
        """
        cache_key = f"{symbol}_{timeframe}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            df = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            self.cache[cache_key] = df
            return df
        except Exception as e:
            print(f"Error fetching OHLCV data for {symbol} on {timeframe}: {str(e)}")
            return pd.DataFrame()

    def get_all_market_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Get market data for all symbols and timeframes
        """
        market_data = {}
        
        for symbol in SYMBOLS:
            market_data[symbol] = {}
            for timeframe in TIMEFRAMES:
                df = self.fetch_ohlcv(symbol, timeframe)
                if not df.empty:
                    market_data[symbol][timeframe] = df
        
        return market_data

    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol
        """
        try:
            return self.exchange.get_current_price(symbol)
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {str(e)}")
            return 0.0

    def clear_cache(self):
        """
        Clear the data cache
        """
        self.cache.clear() 