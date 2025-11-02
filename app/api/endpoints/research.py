from fastapi import APIRouter, HTTPException
import yfinance as yf
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd

router = APIRouter()

# Pydantic Models for Data Validation
class StockInfo(BaseModel):
    symbol: str
    longName: Optional[str] = None
    currency: Optional[str] = None
    dayHigh: Optional[float] = None
    dayLow: Optional[float] = None
    fiftyTwoWeekHigh: Optional[float] = None
    fiftyTwoWeekLow: Optional[float] = None
    marketCap: Optional[float] = None
    volume: Optional[float] = None
    averageVolume: Optional[float] = None
    trailingPE: Optional[float] = None
    forwardPE: Optional[float] = None
    trailingEps: Optional[float] = None
    dividendYield: Optional[float] = None
    priceToSalesTrailing12Months: Optional[float] = None
    beta: Optional[float] = None
    longBusinessSummary: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None

class HistData(BaseModel):
    Date: str
    Open: float
    High: float
    Low: float
    Close: float
    Volume: int

class NewsData(BaseModel):
    title: str
    publisher: str
    link: str
    providerPublishTime: int

class RecommendationData(BaseModel):
    firm: str
    toGrade: str
    fromGrade: Optional[str] = None
    action: Optional[str] = None

class ComprehensiveStockData(BaseModel):
    info: StockInfo
    history: List[HistData]
    news: List[NewsData]
    recommendations: List[RecommendationData]

@router.get("/{symbol}", response_model=ComprehensiveStockData)
def get_comprehensive_stock_data(symbol: str):
    """
    Fetches comprehensive stock data for a given symbol from Yahoo Finance.
    This includes company info, historical price data, news, and analyst recommendations.
    """
    try:
        ticker = yf.Ticker(symbol)

        # yfinance returns an empty info dict for invalid tickers
        if not ticker.info:
            raise HTTPException(status_code=404, detail=f"Stock symbol '{symbol}' not found.")

        # History
        hist_df = ticker.history(period="1y").reset_index()
        hist_df['Date'] = pd.to_datetime(hist_df['Date']).dt.strftime('%Y-%m-%d')
        history_data = hist_df.to_dict(orient='records')

        # News
        news_data = ticker.news

        # Recommendations
        recs_df = ticker.recommendations.reset_index() if ticker.recommendations is not None else pd.DataFrame()
        recommendations_data = recs_df.to_dict(orient='records')

        # Assemble the data
        data = ComprehensiveStockData(
            info=StockInfo(**ticker.info),
            history=history_data,
            news=news_data,
            recommendations=recommendations_data
        )
        
        return data

    except Exception as e:
        print(f"An error occurred: {e}")
        # Catch any other exceptions and return a generic server error
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
