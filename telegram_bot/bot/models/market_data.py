from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class MarketStructure(BaseModel):
    """Market structure analysis"""
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    trend: str = Field(..., description="Current market trend")
    strength: float = Field(..., description="Trend strength")
    support_levels: List[float] = Field(default_factory=list, description="Support price levels")
    resistance_levels: List[float] = Field(default_factory=list, description="Resistance price levels")
    breakouts: List[Dict[str, Any]] = Field(default_factory=list, description="Price breakouts")
    patterns: List[str] = Field(default_factory=list, description="Detected chart patterns")
    volume_profile: Dict[str, Any] = Field(default_factory=dict, description="Volume profile analysis")
    market_profile: Dict[str, Any] = Field(default_factory=dict, description="Market profile analysis")
    order_flow: Dict[str, Any] = Field(default_factory=dict, description="Order flow analysis")
    wave_structure: Optional[str] = Field(None, description="Elliott wave structure")
    harmonic_patterns: List[str] = Field(default_factory=list, description="Detected harmonic patterns")
    divergences: List[str] = Field(default_factory=list, description="Detected divergences")
    last_update: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class MarketAnalysis(BaseModel):
    """Market analysis data"""
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    symbol: str = Field(..., description="Trading symbol")
    timeframe: str = Field(..., description="Analysis timeframe")
    structure: MarketStructure = Field(..., description="Market structure analysis")
    indicators: Dict[str, Any] = Field(default_factory=dict, description="Technical indicators")
    signals: List[str] = Field(default_factory=list, description="Trading signals")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

class Signal(BaseModel):
    """Trading signal"""
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    symbol: str = Field(..., description="Trading symbol")
    direction: str = Field(..., description="Signal direction (BUY/SELL)")
    entry_price: float = Field(..., description="Entry price")
    stop_loss: float = Field(..., description="Stop loss price")
    take_profit: float = Field(..., description="Take profit price")
    timeframe: str = Field(..., description="Signal timeframe")
    pattern: Optional[str] = Field(None, description="Triggering pattern")
    confidence: float = Field(..., description="Signal confidence (0-1)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Signal timestamp")
    analysis: Optional[MarketAnalysis] = Field(None, description="Market analysis")

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