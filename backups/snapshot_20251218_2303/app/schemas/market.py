from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StockSuggestion(BaseModel):
    """Stock search suggestion"""
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    exchange: str = Field(..., description="Exchange")
    type: str = Field(..., description="Security type")

class StockDetails(BaseModel):
    """Detailed stock information"""
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    price: float = Field(..., description="Current price")
    change: float = Field(..., description="Price change")
    changePercent: float = Field(..., description="Price change percentage")
    volume: int = Field(..., description="Trading volume")
    marketCap: float = Field(..., description="Market capitalization")
    pe: float = Field(..., description="Price-to-earnings ratio")
    eps: float = Field(..., description="Earnings per share")
    dividend: float = Field(..., description="Dividend amount")
    dividendYield: float = Field(..., description="Dividend yield")
    high52Week: float = Field(..., description="52-week high")
    low52Week: float = Field(..., description="52-week low")
    avgVolume: float = Field(..., description="Average volume")
    beta: float = Field(..., description="Beta coefficient")
    sector: str = Field(..., description="Sector")
    industry: str = Field(..., description="Industry")
    description: str = Field(..., description="Company description")
    website: str = Field(..., description="Company website")
    employees: int = Field(..., description="Number of employees")
    founded: int = Field(..., description="Founded year")
    headquarters: str = Field(..., description="Headquarters location")

class HistoricalData(BaseModel):
    """Historical stock data"""
    date: str = Field(..., description="Date")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="High price")
    low: float = Field(..., description="Low price")
    close: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")

class MarketOverview(BaseModel):
    """Market overview statistics"""
    totalMarketCap: float = Field(..., description="Total market capitalization")
    totalVolume: int = Field(..., description="Total trading volume")
    gainers: int = Field(..., description="Number of gaining stocks")
    losers: int = Field(..., description="Number of losing stocks")
    unchanged: int = Field(..., description="Number of unchanged stocks")

class PopularStock(BaseModel):
    """Popular stock information"""
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    price: float = Field(..., description="Current price")
    change: float = Field(..., description="Price change")
    changePercent: float = Field(..., description="Price change percentage")
    volume: int = Field(..., description="Trading volume")

class StockNews(BaseModel):
    """Stock news item"""
    title: str = Field(..., description="News title")
    summary: str = Field(..., description="News summary")
    source: str = Field(..., description="News source")
    publishedAt: str = Field(..., description="Publication date")
    url: str = Field(..., description="News URL")

class StockAnalysis(BaseModel):
    """Stock analysis and ratings"""
    buy: int = Field(..., description="Buy rating percentage")
    hold: int = Field(..., description="Hold rating percentage")
    sell: int = Field(..., description="Sell rating percentage")
    targetPrice: float = Field(..., description="Target price")
    recommendation: str = Field(..., description="Overall recommendation")

class StockFinancials(BaseModel):
    """Stock financial data"""
    revenue: float = Field(..., description="Total revenue")
    netIncome: float = Field(..., description="Net income")
    assets: float = Field(..., description="Total assets")
    liabilities: float = Field(..., description="Total liabilities")
    equity: float = Field(..., description="Stockholder equity")
    cash: float = Field(..., description="Cash and cash equivalents")
    debt: float = Field(..., description="Total debt")

class StockPeer(BaseModel):
    """Peer company information"""
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    price: float = Field(..., description="Current price")
    change: float = Field(..., description="Price change")
    changePercent: float = Field(..., description="Price change percentage")
    marketCap: float = Field(..., description="Market capitalization")