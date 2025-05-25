from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class StrategyType(str, Enum):
    TREND = "trend"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    STAT_ARB = "stat_arb"

class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    NEUTRAL = "neutral"

class TradeAction(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TradeStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    CLOSED = "closed"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class PositionStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"

class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: StrategyType
    parameters: Dict[str, Any]
    is_active: bool = True

class StrategyCreate(StrategyBase):
    pass

class StrategyUpdate(StrategyBase):
    pass

class Strategy(StrategyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SignalBase(BaseModel):
    strategy_id: int
    symbol: str
    signal_type: SignalType
    confidence: float
    metrics: Dict[str, Any]

class SignalCreate(SignalBase):
    pass

class Signal(SignalBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TradeBase(BaseModel):
    signal_id: int
    symbol: str
    action: TradeAction
    quantity: int
    price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: TradeStatus
    pnl: Optional[float] = None

class TradeCreate(TradeBase):
    pass

class TradeUpdate(TradeBase):
    pass

class Trade(TradeBase):
    id: int
    created_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None
    initial_balance: float
    current_balance: float
    risk_level: RiskLevel

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(PortfolioBase):
    pass

class Portfolio(PortfolioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PositionBase(BaseModel):
    portfolio_id: int
    symbol: str
    quantity: int
    average_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    status: PositionStatus

class PositionCreate(PositionBase):
    pass

class PositionUpdate(PositionBase):
    pass

class Position(PositionBase):
    id: int
    created_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BacktestResultBase(BaseModel):
    strategy_id: int
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_balance: float
    final_balance: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    metrics: Dict[str, Any]

class BacktestResultCreate(BacktestResultBase):
    pass

class BacktestResult(BacktestResultBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 