from typing import Dict, Optional
import numpy as np
from datetime import datetime, timedelta

class RiskManager:
    def __init__(self):
        # Account parameters
        self.account_balance = 0.0
        self.max_risk_per_trade = 0.02  # 2% per trade
        self.max_daily_risk = 0.05     # 5% daily
        self.max_open_trades = 5
        self.max_daily_trades = 10
        
        # Trade tracking
        self.open_trades = {}
        self.daily_trades = []
        self.daily_pnl = 0.0
        self.last_reset = datetime.now()
        
        # Risk metrics
        self.win_rate = 0.0
        self.profit_factor = 0.0
        self.average_win = 0.0
        self.average_loss = 0.0
        self.max_drawdown = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        # Correlation tracking
        self.correlated_pairs = {
            'EUR/USD': ['GBP/USD', 'EUR/GBP'],
            'GBP/USD': ['EUR/USD', 'EUR/GBP'],
            'USD/JPY': ['EUR/JPY', 'GBP/JPY'],
            'XAU/USD': ['XAG/USD'],
            'BTC/USD': ['ETH/USD']
        }

    def update_account_balance(self, balance: float):
        """
        Update account balance
        """
        self.account_balance = balance
        self._check_daily_reset()

    def _check_daily_reset(self):
        """
        Reset daily metrics if it's a new day
        """
        if datetime.now().date() > self.last_reset.date():
            self.daily_trades = []
            self.daily_pnl = 0.0
            self.last_reset = datetime.now()

    def calculate_position_size(self, signal: Dict) -> Optional[float]:
        """
        Calculate position size based on risk parameters
        """
        if not self._validate_trade(signal):
            return None
        
        # Calculate risk amount
        risk_amount = self.account_balance * self.max_risk_per_trade
        
        # Calculate stop distance in pips
        entry = signal['entry']
        stop_loss = signal['stop_loss']
        stop_distance = abs(entry - stop_loss)
        
        # Calculate position size
        position_size = risk_amount / stop_distance
        
        # Adjust for correlation
        position_size = self._adjust_for_correlation(signal['symbol'], position_size)
        
        return position_size

    def _validate_trade(self, signal: Dict) -> bool:
        """
        Validate if trade meets risk management criteria
        """
        # Check daily trade limit
        if len(self.daily_trades) >= self.max_daily_trades:
            return False
        
        # Check open trades limit
        if len(self.open_trades) >= self.max_open_trades:
            return False
        
        # Check daily risk limit
        if abs(self.daily_pnl) >= self.account_balance * self.max_daily_risk:
            return False
        
        # Check correlation
        if not self._check_correlation(signal['symbol']):
            return False
        
        # Check win rate
        if self.total_trades > 0 and self.win_rate < 0.5:
            return False
        
        return True

    def _check_correlation(self, symbol: str) -> bool:
        """
        Check if symbol is correlated with open trades
        """
        correlated_pairs = self.correlated_pairs.get(symbol, [])
        
        for open_trade in self.open_trades.values():
            if open_trade['symbol'] in correlated_pairs:
                return False
        
        return True

    def _adjust_for_correlation(self, symbol: str, position_size: float) -> float:
        """
        Adjust position size based on correlation
        """
        correlated_pairs = self.correlated_pairs.get(symbol, [])
        correlated_exposure = 0.0
        
        for open_trade in self.open_trades.values():
            if open_trade['symbol'] in correlated_pairs:
                correlated_exposure += open_trade['position_size']
        
        # Reduce position size if there's correlated exposure
        if correlated_exposure > 0:
            position_size *= (1 - correlated_exposure / self.account_balance)
        
        return position_size

    def update_trade_status(self, trade_id: str, status: str, pnl: float):
        """
        Update trade status and metrics
        """
        if trade_id in self.open_trades:
            trade = self.open_trades[trade_id]
            
            if status == 'closed':
                # Update metrics
                self.total_trades += 1
                if pnl > 0:
                    self.winning_trades += 1
                    self.average_win = (self.average_win * (self.winning_trades - 1) + pnl) / self.winning_trades
                else:
                    self.losing_trades += 1
                    self.average_loss = (self.average_loss * (self.losing_trades - 1) + pnl) / self.losing_trades
                
                # Update win rate and profit factor
                self.win_rate = self.winning_trades / self.total_trades
                if self.average_loss != 0:
                    self.profit_factor = abs(self.average_win / self.average_loss)
                
                # Update daily metrics
                self.daily_pnl += pnl
                self.daily_trades.append({
                    'trade_id': trade_id,
                    'symbol': trade['symbol'],
                    'pnl': pnl,
                    'timestamp': datetime.now()
                })
                
                # Remove from open trades
                del self.open_trades[trade_id]
                
                # Update max drawdown
                self._update_max_drawdown()

    def _update_max_drawdown(self):
        """
        Update maximum drawdown
        """
        if self.total_trades > 0:
            current_drawdown = abs(self.average_loss) / self.account_balance
            self.max_drawdown = max(self.max_drawdown, current_drawdown)

    def get_risk_metrics(self) -> Dict:
        """
        Get current risk metrics
        """
        return {
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'average_win': self.average_win,
            'average_loss': self.average_loss,
            'max_drawdown': self.max_drawdown,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'daily_pnl': self.daily_pnl,
            'open_trades': len(self.open_trades),
            'daily_trades': len(self.daily_trades)
        }

    def should_take_trade(self, signal: Dict) -> bool:
        """
        Determine if trade should be taken based on risk parameters
        """
        # Check basic validation
        if not self._validate_trade(signal):
            return False
        
        # Check win rate threshold
        if self.total_trades > 0 and self.win_rate < 0.5:
            return False
        
        # Check profit factor threshold
        if self.total_trades > 0 and self.profit_factor < 1.5:
            return False
        
        # Check drawdown threshold
        if self.max_drawdown > 0.1:  # 10% max drawdown
            return False
        
        # Check daily loss threshold
        if self.daily_pnl < -self.account_balance * 0.03:  # 3% daily loss limit
            return False
        
        return True 