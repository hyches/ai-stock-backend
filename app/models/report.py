from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class FinancialMetrics(BaseModel):
    """Model for financial metrics"""
    revenue: float = Field(..., description="Annual revenue in millions")
    net_income: float = Field(..., description="Annual net income in millions")
    eps: float = Field(..., description="Earnings per share")
    pe_ratio: float = Field(..., description="Price to earnings ratio")
    market_cap: float = Field(..., description="Market capitalization in millions")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield percentage")
    debt_to_equity: Optional[float] = Field(None, description="Debt to equity ratio")
    profit_margin: float = Field(..., description="Profit margin percentage")

class TechnicalIndicators(BaseModel):
    """Model for technical indicators"""
    ma_50: float = Field(..., description="50-day moving average")
    ma_200: float = Field(..., description="200-day moving average")
    rsi: float = Field(..., description="Relative Strength Index")
    macd: float = Field(..., description="MACD indicator")
    volume_avg: float = Field(..., description="Average trading volume")

class SentimentAnalysis(BaseModel):
    """Model for sentiment analysis"""
    overall_score: float = Field(..., ge=-1, le=1, description="Overall sentiment score (-1 to 1)")
    news_sentiment: float = Field(..., ge=-1, le=1, description="News sentiment score")
    social_sentiment: float = Field(..., ge=-1, le=1, description="Social media sentiment score")
    analyst_rating: str = Field(..., description="Average analyst rating")
    price_target: float = Field(..., description="Average price target")

class ReportRequest(BaseModel):
    """Input model for research report generation"""
    symbol: str = Field(..., description="Stock ticker symbol")
    include_technical: bool = Field(True, description="Include technical analysis")
    include_sentiment: bool = Field(True, description="Include sentiment analysis")
    include_competitors: bool = Field(True, description="Include competitor analysis")
    format: str = Field("pdf", description="Report format (pdf or json)")

class ReportResponse(BaseModel):
    """Output model for research report"""
    symbol: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Company name")
    sector: str = Field(..., description="Company sector")
    industry: str = Field(..., description="Company industry")
    current_price: float = Field(..., description="Current stock price")
    financials: FinancialMetrics = Field(..., description="Financial metrics")
    technicals: Optional[TechnicalIndicators] = Field(None, description="Technical indicators")
    sentiment: Optional[SentimentAnalysis] = Field(None, description="Sentiment analysis")
    competitors: Optional[List[str]] = Field(None, description="List of main competitors")
    summary: str = Field(..., description="AI-generated summary")
    recommendations: List[str] = Field(..., description="List of recommendations")
    risk_factors: List[str] = Field(..., description="List of risk factors")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    report_url: Optional[str] = Field(None, description="URL to download PDF report") 