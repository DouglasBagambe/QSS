import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from bot.models.market_data import (
    MarketData,
    TradingSignal,
    MarketNews,
    MarketPrediction,
    PerformanceMetrics
)

class DataManager:
    """Manages market data storage and retrieval"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._cache: Dict[str, MarketData] = {}
        
    def _get_pair_file(self, pair: str) -> Path:
        """Get file path for pair data"""
        return self.data_dir / f"{pair.lower()}.json"
    
    def save_market_data(self, data: MarketData) -> None:
        """Save market data to file"""
        file_path = self._get_pair_file(data.pair)
        data_dict = data.model_dump()
        data_dict["last_update"] = data_dict["last_update"].isoformat()
        
        with open(file_path, "w") as f:
            json.dump(data_dict, f, indent=2)
        
        self._cache[data.pair] = data
    
    def get_market_data(self, pair: str) -> Optional[MarketData]:
        """Get market data for pair"""
        # Check cache first
        if pair in self._cache:
            return self._cache[pair]
        
        # Load from file
        file_path = self._get_pair_file(pair)
        if not file_path.exists():
            return None
            
        with open(file_path, "r") as f:
            data_dict = json.load(f)
            data_dict["last_update"] = datetime.fromisoformat(data_dict["last_update"])
            return MarketData(**data_dict)
    
    def get_active_signals(self, pair: Optional[str] = None) -> List[TradingSignal]:
        """Get active trading signals"""
        signals = []
        for file_path in self.data_dir.glob("*.json"):
            data = self.get_market_data(file_path.stem)
            if data:
                if pair is None or data.pair == pair:
                    signals.extend([s for s in data.active_signals if s.status == "ACTIVE"])
        return signals
    
    def get_recent_news(self, hours: int = 24) -> List[MarketNews]:
        """Get recent market news"""
        news = []
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for file_path in self.data_dir.glob("*.json"):
            data = self.get_market_data(file_path.stem)
            if data:
                news.extend([n for n in data.recent_news if n.timestamp > cutoff])
        
        return sorted(news, key=lambda x: x.timestamp, reverse=True)
    
    def get_predictions(self, pair: Optional[str] = None) -> List[MarketPrediction]:
        """Get market predictions"""
        predictions = []
        for file_path in self.data_dir.glob("*.json"):
            data = self.get_market_data(file_path.stem)
            if data:
                if pair is None or data.pair == pair:
                    predictions.extend(data.predictions)
        return predictions
    
    def get_performance(self, pair: Optional[str] = None) -> List[PerformanceMetrics]:
        """Get performance metrics"""
        metrics = []
        for file_path in self.data_dir.glob("*.json"):
            data = self.get_market_data(file_path.stem)
            if data:
                if pair is None or data.pair == pair:
                    metrics.append(data.performance)
        return metrics
    
    def update_signal_status(self, pair: str, signal_id: str, status: str) -> bool:
        """Update signal status"""
        data = self.get_market_data(pair)
        if not data:
            return False
            
        for signal in data.active_signals:
            if str(signal.timestamp) == signal_id:
                signal.status = status
                self.save_market_data(data)
                return True
        return False
    
    def add_news(self, pair: str, news: MarketNews) -> None:
        """Add news to pair data"""
        data = self.get_market_data(pair)
        if data:
            data.recent_news.append(news)
            # Keep only last 100 news items
            data.recent_news = data.recent_news[-100:]
            self.save_market_data(data)
    
    def add_prediction(self, pair: str, prediction: MarketPrediction) -> None:
        """Add prediction to pair data"""
        data = self.get_market_data(pair)
        if data:
            data.predictions.append(prediction)
            # Keep only last 50 predictions
            data.predictions = data.predictions[-50:]
            self.save_market_data(data)
    
    def update_performance(self, pair: str, metrics: PerformanceMetrics) -> None:
        """Update performance metrics"""
        data = self.get_market_data(pair)
        if data:
            data.performance = metrics
            self.save_market_data(data) 