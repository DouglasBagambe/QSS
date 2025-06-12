from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import os
from pathlib import Path

class PerformanceTracker:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.trades_file = self.data_dir / "trades.json"
        self.stats_file = self.data_dir / "stats.json"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.trades_file.exists():
            self.trades_file.write_text("[]")
        if not self.stats_file.exists():
            self.stats_file.write_text("{}")
    
    def add_trade(self, trade_data: Dict[str, Any]):
        """Add a new trade to the history"""
        trades = self._load_trades()
        trade_data["timestamp"] = datetime.now().isoformat()
        trades.append(trade_data)
        self._save_trades(trades)
        self._update_stats()
    
    def get_trade_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get trade history for the specified number of days"""
        trades = self._load_trades()
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            trade for trade in trades
            if datetime.fromisoformat(trade["timestamp"]) > cutoff_date
        ]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        stats = self._load_stats()
        if not stats:
            stats = self._calculate_stats()
            self._save_stats(stats)
        return stats
    
    def _load_trades(self) -> List[Dict[str, Any]]:
        """Load trades from file"""
        return json.loads(self.trades_file.read_text())
    
    def _save_trades(self, trades: List[Dict[str, Any]]):
        """Save trades to file"""
        self.trades_file.write_text(json.dumps(trades, indent=2))
    
    def _load_stats(self) -> Dict[str, Any]:
        """Load stats from file"""
        return json.loads(self.stats_file.read_text())
    
    def _save_stats(self, stats: Dict[str, Any]):
        """Save stats to file"""
        self.stats_file.write_text(json.dumps(stats, indent=2))
    
    def _update_stats(self):
        """Update performance statistics"""
        stats = self._calculate_stats()
        self._save_stats(stats)
    
    def _calculate_stats(self) -> Dict[str, Any]:
        """Calculate performance statistics from trade history"""
        trades = self._load_trades()
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "average_profit": 0.0,
                "average_loss": 0.0,
                "profit_factor": 0.0,
                "total_profit": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0
            }
        
        winning_trades = [t for t in trades if t.get("profit", 0) > 0]
        losing_trades = [t for t in trades if t.get("profit", 0) <= 0]
        
        total_profit = sum(t.get("profit", 0) for t in winning_trades)
        total_loss = abs(sum(t.get("profit", 0) for t in losing_trades))
        
        return {
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(trades) if trades else 0.0,
            "average_profit": total_profit / len(winning_trades) if winning_trades else 0.0,
            "average_loss": total_loss / len(losing_trades) if losing_trades else 0.0,
            "profit_factor": total_profit / total_loss if total_loss else float("inf"),
            "total_profit": total_profit - total_loss,
            "max_drawdown": self._calculate_max_drawdown(trades),
            "sharpe_ratio": self._calculate_sharpe_ratio(trades)
        }
    
    def _calculate_max_drawdown(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate maximum drawdown from trade history"""
        if not trades:
            return 0.0
        
        balance = 0.0
        peak = 0.0
        max_drawdown = 0.0
        
        for trade in trades:
            balance += trade.get("profit", 0)
            peak = max(peak, balance)
            drawdown = peak - balance
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate Sharpe ratio from trade history"""
        if not trades:
            return 0.0
        
        returns = [t.get("profit", 0) for t in trades]
        avg_return = sum(returns) / len(returns)
        std_dev = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
        
        return avg_return / std_dev if std_dev else 0.0

async def get_performance_stats() -> Dict[str, Any]:
    """Get formatted performance statistics for display"""
    tracker = PerformanceTracker()
    stats = tracker.get_performance_stats()
    
    if not stats:
        return {
            "win_rate": 0,
            "total_trades": 0,
            "profit_factor": 0,
            "current_month": "No data",
            "last_month": "No data",
            "best_pairs": "No data",
            "avg_risk": 0,
            "max_drawdown": 0
        }
    
    # Format best performing pairs
    best_pairs = sorted(
        stats["pair_performance"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    best_pairs_str = "\n".join(f"• {pair}: ${pnl:,.2f}" for pair, pnl in best_pairs)
    
    # Get current and last month performance
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    last_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    
    current_month_pnl = stats["monthly_performance"].get(current_month, 0)
    last_month_pnl = stats["monthly_performance"].get(last_month, 0)
    
    return {
        "win_rate": round(stats["win_rate"], 2),
        "total_trades": stats["total_trades"],
        "profit_factor": round(
            abs(stats["total_pnl"] / stats["worst_trade"]) if stats["worst_trade"] != 0 else 0,
            2
        ),
        "current_month": f"${current_month_pnl:,.2f}",
        "last_month": f"${last_month_pnl:,.2f}",
        "best_pairs": best_pairs_str,
        "avg_risk": 1.0,  # Default risk percentage
        "max_drawdown": round(
            abs(stats["worst_trade"] / stats["total_pnl"]) * 100 if stats["total_pnl"] != 0 else 0,
            2
        )
    } 