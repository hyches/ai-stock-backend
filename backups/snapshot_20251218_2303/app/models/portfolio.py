from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StockWeight(BaseModel):
    """Model for stock weight in portfolio"""
    symbol: str = Field(..., description="Stock ticker symbol")
    weight: float = Field(..., ge=0, le=1, description="Weight of stock in portfolio (0-1)")

class PortfolioInput(BaseModel):
    """Input model for portfolio optimization"""
    stocks: List[str] = Field(..., min_items=1, description="List of stock symbols to optimize")
    capital: float = Field(..., gt=0, description="Total capital to invest")
    risk_tolerance: float = Field(0.5, ge=0, le=1, description="Risk tolerance (0-1, where 0 is conservative and 1 is aggressive)")
    min_weight: float = Field(0.05, ge=0, le=0.2, description="Minimum weight for any stock (0-0.2)")
    max_weight: float = Field(0.3, ge=0.2, le=1, description="Maximum weight for any stock (0.2-1)")
    sector_constraints: Optional[dict] = Field(None, description="Maximum allocation per sector (e.g., {'Technology': 0.4})")

class PortfolioMetrics(BaseModel):
    """Model for portfolio performance metrics"""
    expected_return: float = Field(..., description="Expected annual return (%)")
    volatility: float = Field(..., description="Portfolio volatility (standard deviation)")
    sharpe_ratio: float = Field(..., description="Sharpe ratio (risk-adjusted return)")
    max_drawdown: float = Field(..., description="Maximum drawdown (%)")
    sector_allocation: dict = Field(..., description="Allocation by sector")

class PortfolioOutput(BaseModel):
    """Output model for portfolio optimization"""
    weights: List[StockWeight] = Field(..., description="Optimized weights for each stock")
    metrics: PortfolioMetrics = Field(..., description="Portfolio performance metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of optimization")
    cash_allocation: float = Field(..., description="Amount of cash to hold")
    rebalance_frequency: str = Field("monthly", description="Recommended rebalancing frequency") 