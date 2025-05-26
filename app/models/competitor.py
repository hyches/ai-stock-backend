from pydantic import BaseModel
from typing import List, Optional

class CompetitorMetrics(BaseModel):
    """
    CompetitorMetrics holds financial and sentiment data for a company.
    Parameters:
        - symbol (str): The stock ticker symbol identifying the company.
        - name (str): The full name of the company.
        - market_cap (float): The company's market capitalization in dollars.
        - revenue (float): The company's revenue in dollars.
        - profit_margin (float): The company's profit margin expressed as a percentage.
        - pe_ratio (float): The company's price-to-earnings ratio.
        - dividend_yield (float): The company's dividend yield expressed as a percentage.
        - beta (float): Measure of the company's stock volatility compared to the market.
        - sentiment_score (Optional[float]): The sentiment analysis score from social/community inputs, if available.
    Processing Logic:
        - Provides a structured way to store various financial metrics of a company.
        - Sentiment score is optional and may not be available for all companies.
    """
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