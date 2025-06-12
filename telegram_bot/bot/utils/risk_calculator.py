from typing import Dict, Any
from decimal import Decimal

class RiskCalculator:
    def __init__(self):
        self.risk_modes = {
            "conservative": {
                "max_risk_per_trade": Decimal("0.01"),  # 1%
                "max_daily_risk": Decimal("0.03"),      # 3%
                "max_open_trades": 3,
                "stop_loss_pips": 50
            },
            "moderate": {
                "max_risk_per_trade": Decimal("0.02"),  # 2%
                "max_daily_risk": Decimal("0.05"),      # 5%
                "max_open_trades": 5,
                "stop_loss_pips": 75
            },
            "aggressive": {
                "max_risk_per_trade": Decimal("0.03"),  # 3%
                "max_daily_risk": Decimal("0.08"),      # 8%
                "max_open_trades": 8,
                "stop_loss_pips": 100
            }
        }
    
    def calculate_position_size(self, account_balance: float, risk_mode: str = "moderate") -> Dict[str, Any]:
        """Calculate position size based on account balance and risk mode"""
        if risk_mode not in self.risk_modes:
            risk_mode = "moderate"
        
        risk_params = self.risk_modes[risk_mode]
        balance = Decimal(str(account_balance))
        
        # Calculate maximum risk amount
        max_risk_amount = balance * risk_params["max_risk_per_trade"]
        
        # Calculate position sizes for different lot sizes
        position_sizes = {
            "micro": float(max_risk_amount / Decimal("1000")),  # 0.01 lots
            "mini": float(max_risk_amount / Decimal("10000")),  # 0.1 lots
            "standard": float(max_risk_amount / Decimal("100000"))  # 1.0 lots
        }
        
        return {
            "risk_mode": risk_mode,
            "max_risk_amount": float(max_risk_amount),
            "position_sizes": position_sizes,
            "max_open_trades": risk_params["max_open_trades"],
            "stop_loss_pips": risk_params["stop_loss_pips"],
            "max_daily_risk": float(balance * risk_params["max_daily_risk"])
        }
    
    def get_risk_guidelines(self, risk_mode: str = "moderate") -> Dict[str, str]:
        """Get risk management guidelines for the selected mode"""
        if risk_mode not in self.risk_modes:
            risk_mode = "moderate"
        
        guidelines = {
            "conservative": {
                "description": "Conservative risk management for capital preservation",
                "guidelines": [
                    "Maximum 1% risk per trade",
                    "Maximum 3% daily risk",
                    "Maximum 3 open trades",
                    "50 pip stop loss",
                    "Focus on high-probability setups only",
                    "Strict entry and exit rules"
                ]
            },
            "moderate": {
                "description": "Balanced risk management for steady growth",
                "guidelines": [
                    "Maximum 2% risk per trade",
                    "Maximum 5% daily risk",
                    "Maximum 5 open trades",
                    "75 pip stop loss",
                    "Mix of high and medium probability setups",
                    "Flexible entry and exit rules"
                ]
            },
            "aggressive": {
                "description": "Aggressive risk management for maximum growth",
                "guidelines": [
                    "Maximum 3% risk per trade",
                    "Maximum 8% daily risk",
                    "Maximum 8 open trades",
                    "100 pip stop loss",
                    "Takes advantage of all valid setups",
                    "Dynamic entry and exit rules"
                ]
            }
        }
        
        return guidelines[risk_mode]

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