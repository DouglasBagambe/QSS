import ccxt
import pandas as pd
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

class ExchangeInterface(ABC):
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        pass

    @abstractmethod
    def get_exchange_info(self) -> Dict:
        pass

class BinanceExchange(ExchangeInterface):
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching OHLCV data: {str(e)}")
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> float:
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching current price: {str(e)}")
            return 0.0

    def get_exchange_info(self) -> Dict:
        try:
            return self.exchange.load_markets()
        except Exception as e:
            print(f"Error fetching exchange info: {str(e)}")
            return {}

class FTXExchange(ExchangeInterface):
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.exchange = ccxt.ftx({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching OHLCV data: {str(e)}")
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> float:
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching current price: {str(e)}")
            return 0.0

    def get_exchange_info(self) -> Dict:
        try:
            return self.exchange.load_markets()
        except Exception as e:
            print(f"Error fetching exchange info: {str(e)}")
            return {}

class ExchangeFactory:
    @staticmethod
    def create_exchange(exchange_id: str, api_key: Optional[str] = None, api_secret: Optional[str] = None) -> ExchangeInterface:
        exchanges = {
            'binance': BinanceExchange,
            'ftx': FTXExchange
        }
        
        if exchange_id.lower() not in exchanges:
            raise ValueError(f"Unsupported exchange: {exchange_id}")
            
        return exchanges[exchange_id.lower()](api_key, api_secret) 