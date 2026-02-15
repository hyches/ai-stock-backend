from pydantic import BaseModel
from typing import List, Optional

class CompetitorMetrics(BaseModel):
    symbol: str
    name: str
    market_cap: float
    revenue: float
    profit_margin: float
    pe_ratio: float
    dividend_yield: float
    beta: float
    sentiment_score: Optional[float] = None

class CompetitorAnalysis(BaseModel):
    symbol: str
    competitors: List[CompetitorMetrics]
    market_position: str  # market_leader, major_player, significant_player, niche_player 