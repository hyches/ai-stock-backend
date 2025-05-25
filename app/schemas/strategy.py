from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Shared properties
class StrategyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    symbols: List[str] = Field(default_factory=list)
    timeframe: str = Field(..., min_length=1, max_length=10)

# Properties to receive on strategy creation
class StrategyCreate(StrategyBase):
    pass

# Properties to receive on strategy update
class StrategyUpdate(StrategyBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    timeframe: Optional[str] = Field(None, min_length=1, max_length=10)
    is_active: Optional[bool] = None

# Properties shared by models stored in DB
class StrategyInDBBase(StrategyBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Properties to return to client
class Strategy(StrategyInDBBase):
    pass

# Properties stored in DB
class StrategyInDB(StrategyInDBBase):
    pass

# Properties for strategy list
class StrategyList(StrategyInDBBase):
    pass

# Properties for strategy performance
class StrategyPerformance(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    winning_pnl: float
    losing_pnl: float
    profit_factor: float
    average_win: float
    average_loss: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    signals: int

    class Config:
        orm_mode = True 