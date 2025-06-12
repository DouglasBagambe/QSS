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
    
    def add_trade(self, pair: str, entry_price: float, exit_price: float,
                  position_size: float, pnl: float, timestamp: datetime = None):
        """Add a new trade to the tracker"""
        if timestamp is None:
            timestamp = datetime.now()
        
        trade = {
            "pair": pair,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "position_size": position_size,
            "pnl": pnl,
            "timestamp": timestamp.isoformat()
        }
        
        trades = self._load_trades()
        trades.append(trade)
        self._save_trades(trades)
        self._update_stats()
    
    def _load_trades(self) -> List[Dict[str, Any]]:
        """Load trades from file"""
        return json.loads(self.trades_file.read_text())
    
    def _save_trades(self, trades: List[Dict[str, Any]]):
        """Save trades to file"""
        self.trades_file.write_text(json.dumps(trades, indent=2))
    
    def _update_stats(self):
        """Update performance statistics"""
        trades = self._load_trades()
        stats = {
            "total_trades": len(trades),
            "winning_trades": sum(1 for t in trades if t["pnl"] > 0),
            "losing_trades": sum(1 for t in trades if t["pnl"] < 0),
            "total_pnl": sum(t["pnl"] for t in trades),
            "best_trade": max((t["pnl"] for t in trades), default=0),
            "worst_trade": min((t["pnl"] for t in trades), default=0),
            "average_trade": sum(t["pnl"] for t in trades) / len(trades) if trades else 0,
            "win_rate": sum(1 for t in trades if t["pnl"] > 0) / len(trades) * 100 if trades else 0,
            "pair_performance": self._calculate_pair_performance(trades),
            "monthly_performance": self._calculate_monthly_performance(trades)
        }
        self.stats_file.write_text(json.dumps(stats, indent=2))
    
    def _calculate_pair_performance(self, trades: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance by trading pair"""
        pair_pnl = {}
        for trade in trades:
            pair = trade["pair"]
            if pair not in pair_pnl:
                pair_pnl[pair] = 0
            pair_pnl[pair] += trade["pnl"]
        return pair_pnl
    
    def _calculate_monthly_performance(self, trades: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance by month"""
        monthly_pnl = {}
        for trade in trades:
            timestamp = datetime.fromisoformat(trade["timestamp"])
            month_key = timestamp.strftime("%Y-%m")
            if month_key not in monthly_pnl:
                monthly_pnl[month_key] = 0
            monthly_pnl[month_key] += trade["pnl"]
        return monthly_pnl
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        if not self.stats_file.exists():
            return {}
        return json.loads(self.stats_file.read_text())
    
    def get_recent_trades(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent trades"""
        trades = self._load_trades()
        return sorted(trades, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_pair_stats(self, pair: str) -> Dict[str, Any]:
        """Get statistics for a specific pair"""
        trades = [t for t in self._load_trades() if t["pair"] == pair]
        if not trades:
            return {}
        
        return {
            "total_trades": len(trades),
            "winning_trades": sum(1 for t in trades if t["pnl"] > 0),
            "total_pnl": sum(t["pnl"] for t in trades),
            "win_rate": sum(1 for t in trades if t["pnl"] > 0) / len(trades) * 100,
            "average_trade": sum(t["pnl"] for t in trades) / len(trades)
        }
    
    def get_monthly_stats(self, year: int, month: int) -> Dict[str, Any]:
        """Get statistics for a specific month"""
        trades = [
            t for t in self._load_trades()
            if datetime.fromisoformat(t["timestamp"]).year == year
            and datetime.fromisoformat(t["timestamp"]).month == month
        ]
        if not trades:
            return {}
        
        return {
            "total_trades": len(trades),
            "winning_trades": sum(1 for t in trades if t["pnl"] > 0),
            "total_pnl": sum(t["pnl"] for t in trades),
            "win_rate": sum(1 for t in trades if t["pnl"] > 0) / len(trades) * 100,
            "average_trade": sum(t["pnl"] for t in trades) / len(trades)
        }

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