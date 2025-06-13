from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class MarketStructure(BaseModel):
    """Market structure analysis"""
    trend: str
    strength: float
    support_levels: List[float]
    resistance_levels: List[float]
    breakouts: List[Dict[str, any]]
    last_update: datetime = Field(default_factory=datetime.now)

class TechnicalIndicators(BaseModel):
    """Technical indicators data"""
    rsi: float
    macd: Dict[str, float]
    bollinger_bands: Dict[str, List[float]]
    moving_averages: Dict[str, float]
    volume_profile: Dict[str, float]
    last_update: datetime = Field(default_factory=datetime.now)

class TradingSignal(BaseModel):
    """Trading signal from indicator"""
    pair: str
    direction: str  # "BUY" or "SELL"
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    confidence: float
    timeframe: str
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "ACTIVE"  # ACTIVE, CLOSED, CANCELLED
    pips_moved: Optional[float] = None
    profit_loss: Optional[float] = None

class MarketNews(BaseModel):
    """Market news and events"""
    title: str
    description: str
    impact: str  # HIGH, MEDIUM, LOW
    currency: str
    timestamp: datetime
    source: str

class MarketPrediction(BaseModel):
    """AI market predictions"""
    pair: str
    timeframe: str
    prediction: str
    confidence: float
    target_price: float
    stop_loss: float
    timestamp: datetime = Field(default_factory=datetime.now)

class PerformanceMetrics(BaseModel):
    """Trading performance metrics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_profit: float
    average_loss: float
    profit_factor: float
    max_drawdown: float
    period: str  # DAILY, WEEKLY, MONTHLY
    timestamp: datetime = Field(default_factory=datetime.now)

class MarketData(BaseModel):
    """Complete market data structure"""
    pair: str
    timeframe: str
    current_price: float
    structure: MarketStructure
    indicators: TechnicalIndicators
    active_signals: List[TradingSignal]
    recent_news: List[MarketNews]
    predictions: List[MarketPrediction]
    performance: PerformanceMetrics
    last_update: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True 