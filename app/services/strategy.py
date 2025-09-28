from typing import List, Optional, Dict, Any
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from app.models.trading import Strategy, Signal, Trade, Position
from app.schemas.strategy import StrategyCreate, StrategyUpdate
from app.core.config import settings
from app.strategies.base import BaseStrategy
from app.strategies.trend_following import TrendFollowingStrategy

class StrategyService:
    def __init__(self, db: Session):
        self.db = db
        self.strategy_map = {
            "trend_following": TrendFollowingStrategy,
            # Add more strategies here
        }

    def get(self, id: int) -> Optional[Strategy]:
        """Get strategy by ID"""
        return self.db.query(Strategy).filter(Strategy.id == id).first()

    def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None
    ) -> List[Strategy]:
        """Get multiple strategies"""
        query = self.db.query(Strategy)
        if user_id:
            query = query.filter(Strategy.user_id == user_id)
        return query.offset(skip).limit(limit).all()

    def create(self, *, obj_in: StrategyCreate, user_id: int) -> Strategy:
        """Create new strategy"""
        db_obj = Strategy(
            user_id=user_id,
            name=obj_in.name,
            type=obj_in.type,
            description=obj_in.description,
            parameters=obj_in.parameters,
            symbols=obj_in.symbols,
            timeframe=obj_in.timeframe,
            is_active=True
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self,
        *,
        db_obj: Strategy,
        obj_in: StrategyUpdate
    ) -> Strategy:
        """Update strategy"""
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, *, id: int) -> Strategy:
        """Delete strategy"""
        obj = self.db.query(Strategy).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj

    def activate(self, strategy: Strategy) -> None:
        """Activate strategy"""
        strategy.is_active = True
        self.db.add(strategy)
        self.db.commit()

    def deactivate(self, strategy: Strategy) -> None:
        """Deactivate strategy"""
        strategy.is_active = False
        self.db.add(strategy)
        self.db.commit()

    def get_performance(
        self,
        strategy: Strategy,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get strategy performance metrics"""
        # Get signals
        signals_query = self.db.query(Signal).filter(
            Signal.strategy_id == strategy.id
        )
        if start_date:
            signals_query = signals_query.filter(
                Signal.created_at >= datetime.fromisoformat(start_date)
            )
        if end_date:
            signals_query = signals_query.filter(
                Signal.created_at <= datetime.fromisoformat(end_date)
            )
        signals = signals_query.all()

        # Get trades
        trades_query = self.db.query(Trade).join(Position).filter(
            Position.strategy_id == strategy.id
        )
        if start_date:
            trades_query = trades_query.filter(
                Trade.created_at >= datetime.fromisoformat(start_date)
            )
        if end_date:
            trades_query = trades_query.filter(
                Trade.created_at <= datetime.fromisoformat(end_date)
            )
        trades = trades_query.all()

        # Calculate metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        losing_trades = len([t for t in trades if t.pnl < 0])
        
        total_pnl = sum(t.pnl for t in trades)
        winning_pnl = sum(t.pnl for t in trades if t.pnl > 0)
        losing_pnl = sum(t.pnl for t in trades if t.pnl < 0)
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        profit_factor = abs(winning_pnl / losing_pnl) if losing_pnl != 0 else float('inf')
        
        avg_win = winning_pnl / winning_trades if winning_trades > 0 else 0
        avg_loss = losing_pnl / losing_trades if losing_trades > 0 else 0
        
        # Calculate returns
        returns = [t.pnl for t in trades]
        if returns:
            import numpy as np
            returns_array = np.array(returns)
            sharpe_ratio = np.mean(returns_array) / np.std(returns_array) * np.sqrt(252) if np.std(returns_array) != 0 else 0
            sortino_ratio = np.mean(returns_array) / np.std(returns_array[returns_array < 0]) * np.sqrt(252) if len(returns_array[returns_array < 0]) > 0 else 0
            max_drawdown = self._calculate_max_drawdown(returns_array)
        else:
            sharpe_ratio = 0
            sortino_ratio = 0
            max_drawdown = 0

        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "winning_pnl": winning_pnl,
            "losing_pnl": losing_pnl,
            "profit_factor": profit_factor,
            "average_win": avg_win,
            "average_loss": avg_loss,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "max_drawdown": max_drawdown,
            "signals": len(signals)
        }

    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = cumulative_returns / rolling_max - 1
        return abs(drawdowns.min()) 