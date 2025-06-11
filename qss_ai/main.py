import asyncio
import logging
import schedule
import time
from datetime import datetime
from typing import Dict

from exchange.market_data import MarketDataProvider
from strategy.smartflow import QuantumSmartFlowStrategy
from telegram.signal_sender import SignalSender
from config.settings import (
    SYMBOLS,
    TIMEFRAMES,
    LONDON_SESSION_START,
    LONDON_SESSION_END,
    NY_SESSION_START,
    NY_SESSION_END
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/qss_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QSSMonitor:
    def __init__(self):
        self.market_data = MarketDataProvider()
        self.strategy = QuantumSmartFlowStrategy()
        self.signal_sender = SignalSender()
        self.last_signals = {}  # Track last signals to avoid duplicates

    def is_trading_session(self) -> bool:
        """
        Check if current time is within trading sessions
        """
        current_hour = datetime.utcnow().hour
        
        # Check London session
        if LONDON_SESSION_START <= current_hour < LONDON_SESSION_END:
            return True
            
        # Check New York session
        if NY_SESSION_START <= current_hour < NY_SESSION_END:
            return True
            
        return False

    async def analyze_market(self):
        """
        Analyze all markets and send signals if conditions are met
        """
        if not self.is_trading_session():
            logger.info("Outside trading hours, skipping analysis")
            return

        try:
            # Get market data for all symbols and timeframes
            market_data = self.market_data.get_all_market_data()
            
            for symbol in SYMBOLS:
                logger.info(f"Analyzing {symbol}")
                
                # Get data for all timeframes
                symbol_data = market_data.get(symbol, {})
                if not symbol_data:
                    continue
                
                # Analyze each timeframe
                for timeframe in TIMEFRAMES:
                    df = symbol_data.get(timeframe)
                    if df is None or df.empty:
                        continue
                    
                    # Get signal from strategy
                    signal = self.strategy.analyze(df)
                    
                    if signal:
                        # Add symbol and timeframe to signal
                        signal['symbol'] = symbol
                        signal['timeframe'] = timeframe
                        
                        # Check if this is a new signal
                        signal_key = f"{symbol}_{timeframe}_{signal['type']}"
                        if signal_key not in self.last_signals:
                            # Send signal to Telegram
                            success = await self.signal_sender.send_signal(signal)
                            if success:
                                logger.info(f"Signal sent for {symbol} on {timeframe}")
                                self.last_signals[signal_key] = datetime.now()
                            else:
                                logger.error(f"Failed to send signal for {symbol} on {timeframe}")
                
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")

    def cleanup_old_signals(self):
        """
        Clean up signals older than 24 hours
        """
        current_time = datetime.now()
        self.last_signals = {
            k: v for k, v in self.last_signals.items()
            if (current_time - v).total_seconds() < 86400  # 24 hours
        }

async def main():
    monitor = QSSMonitor()
    
    # Schedule cleanup of old signals every hour
    schedule.every().hour.do(monitor.cleanup_old_signals)
    
    while True:
        # Run scheduled tasks
        schedule.run_pending()
        
        # Analyze markets
        await monitor.analyze_market()
        
        # Wait for 5 minutes before next analysis
        await asyncio.sleep(300)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("QSS Monitor stopped by user")
    except Exception as e:
        logger.error(f"QSS Monitor stopped due to error: {str(e)}") 