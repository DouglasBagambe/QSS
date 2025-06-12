from typing import Dict, Any
from decimal import Decimal

def calculate_risk(balance: float, risk_percentage: float = 1.0) -> float:
    """Calculate risk amount based on account balance and risk percentage"""
    return balance * (risk_percentage / 100)

def calculate_position_size(balance: float, risk_percentage: float = 1.0, 
                          stop_loss_pips: float = 50) -> float:
    """Calculate position size based on risk parameters"""
    risk_amount = calculate_risk(balance, risk_percentage)
    pip_value = 0.0001  # Standard pip value for most pairs
    position_size = risk_amount / (stop_loss_pips * pip_value)
    return round(position_size, 2)

def calculate_risk_reward_ratio(entry_price: float, stop_loss: float, 
                              take_profit: float) -> float:
    """Calculate risk-reward ratio for a trade"""
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    return round(reward / risk, 2)

def calculate_max_drawdown(trades: list) -> float:
    """Calculate maximum drawdown from a list of trades"""
    if not trades:
        return 0.0
    
    peak = trades[0]
    max_drawdown = 0.0
    
    for trade in trades:
        if trade > peak:
            peak = trade
        drawdown = (peak - trade) / peak * 100
        max_drawdown = max(max_drawdown, drawdown)
    
    return round(max_drawdown, 2)

def calculate_win_rate(trades: list) -> float:
    """Calculate win rate from a list of trades"""
    if not trades:
        return 0.0
    
    winning_trades = sum(1 for trade in trades if trade > 0)
    return round(winning_trades / len(trades) * 100, 2)

def calculate_profit_factor(trades: list) -> float:
    """Calculate profit factor from a list of trades"""
    if not trades:
        return 0.0
    
    gross_profit = sum(trade for trade in trades if trade > 0)
    gross_loss = abs(sum(trade for trade in trades if trade < 0))
    
    if gross_loss == 0:
        return float('inf')
    
    return round(gross_profit / gross_loss, 2)

def get_risk_metrics(balance: float, trades: list) -> Dict[str, Any]:
    """Get comprehensive risk metrics"""
    return {
        "account_balance": balance,
        "max_drawdown": calculate_max_drawdown(trades),
        "win_rate": calculate_win_rate(trades),
        "profit_factor": calculate_profit_factor(trades),
        "recommended_risk": calculate_risk(balance),
        "position_size": calculate_position_size(balance)
    } 