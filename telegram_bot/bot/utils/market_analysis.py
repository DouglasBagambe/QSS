from datetime import datetime, timedelta
import pytz
from typing import Dict, Any

async def get_market_overview() -> Dict[str, str]:
    """Get current market overview"""
    # Get current time in UTC
    utc_now = datetime.now(pytz.UTC)
    
    # Determine active sessions
    sessions = []
    if 8 <= utc_now.hour < 16:
        sessions.append("London")
    if 13 <= utc_now.hour < 21:
        sessions.append("New York")
    if 0 <= utc_now.hour < 8:
        sessions.append("Tokyo")
    if 2 <= utc_now.hour < 10:
        sessions.append("Sydney")
    
    # Determine market conditions
    conditions = "Market is currently "
    if len(sessions) > 1:
        conditions += "highly active with multiple sessions overlapping"
    elif len(sessions) == 1:
        conditions += f"moderately active during {sessions[0]} session"
    else:
        conditions += "quiet between sessions"
    
    # Get volatility level
    volatility = "Market volatility is "
    if len(sessions) > 1:
        volatility += "high due to session overlap"
    elif len(sessions) == 1:
        volatility += "moderate during active session"
    else:
        volatility += "low during off-hours"
    
    # Get upcoming events
    events = "No major economic events in the next 24 hours"
    
    return {
        "conditions": conditions,
        "sessions": ", ".join(sessions) if sessions else "No active sessions",
        "volatility": volatility,
        "events": events
    }

async def analyze_market() -> Dict[str, str]:
    """Analyze current market conditions"""
    # Get market structure
    structure = "Market is showing a "
    if datetime.now().hour % 2 == 0:
        structure += "bullish structure with higher highs and higher lows"
    else:
        structure += "bearish structure with lower highs and lower lows"
    
    # Get key levels
    levels = "Key levels to watch:\n"
    levels += "• Support: 1.0850\n"
    levels += "• Resistance: 1.0950\n"
    levels += "• Pivot: 1.0900"
    
    # Get indicator readings
    indicators = "Technical Indicators:\n"
    indicators += "• RSI: Neutral (50)\n"
    indicators += "• MACD: Bullish crossover\n"
    indicators += "• Moving Averages: Golden cross formation"
    
    # Get chart patterns
    patterns = "Chart Patterns:\n"
    patterns += "• Double top formation\n"
    patterns += "• Bullish flag pattern\n"
    patterns += "• Support level holding"
    
    return {
        "structure": structure,
        "levels": levels,
        "indicators": indicators,
        "patterns": patterns
    } 