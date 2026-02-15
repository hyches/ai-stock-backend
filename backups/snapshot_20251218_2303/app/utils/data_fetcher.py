import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.trading import Strategy

class DataFetcher:
    def __init__(self):
        self.db = SessionLocal()

    def get_historical_data(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Get historical price data for a symbol
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        try:
            # Get data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                return pd.DataFrame()
            
            # Rename columns to match our schema
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {str(e)}")
            return None

    def get_strategy(self, strategy_id: int) -> Optional[Strategy]:
        """
        Get strategy from database
        """
        try:
            return self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
        except Exception as e:
            print(f"Error fetching strategy {strategy_id}: {str(e)}")
            return None

    def get_market_data(self, symbols: list) -> Dict[str, pd.DataFrame]:
        """
        Get market data for multiple symbols
        """
        market_data = {}
        for symbol in symbols:
            data = self.get_historical_data(symbol)
            if not data.empty:
                market_data[symbol] = data
        return market_data

    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get company information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow")
            }
        except Exception as e:
            print(f"Error fetching company info for {symbol}: {str(e)}")
            return {}

    def get_news(self, symbol: str, limit: int = 10) -> list:
        """
        Get news for a symbol
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news[:limit]
            
            return [{
                "title": item.get("title"),
                "publisher": item.get("publisher"),
                "link": item.get("link"),
                "published": item.get("providerPublishTime"),
                "type": item.get("type")
            } for item in news]
        except Exception as e:
            print(f"Error fetching news for {symbol}: {str(e)}")
            return []

    def get_recommendations(self, symbol: str) -> pd.DataFrame:
        """
        Get analyst recommendations
        """
        try:
            ticker = yf.Ticker(symbol)
            recommendations = ticker.recommendations
            
            if recommendations is not None and not recommendations.empty:
                return recommendations
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching recommendations for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_earnings(self, symbol: str) -> pd.DataFrame:
        """
        Get earnings data
        """
        try:
            ticker = yf.Ticker(symbol)
            earnings = ticker.earnings
            
            if earnings is not None and not earnings.empty:
                return earnings
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching earnings for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """
        Get balance sheet data
        """
        try:
            ticker = yf.Ticker(symbol)
            balance_sheet = ticker.balance_sheet
            
            if balance_sheet is not None and not balance_sheet.empty:
                return balance_sheet
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching balance sheet for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_income_statement(self, symbol: str) -> pd.DataFrame:
        """
        Get income statement data
        """
        try:
            ticker = yf.Ticker(symbol)
            income_stmt = ticker.income_stmt
            
            if income_stmt is not None and not income_stmt.empty:
                return income_stmt
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching income statement for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_cash_flow(self, symbol: str) -> pd.DataFrame:
        """
        Get cash flow data
        """
        try:
            ticker = yf.Ticker(symbol)
            cash_flow = ticker.cashflow
            
            if cash_flow is not None and not cash_flow.empty:
                return cash_flow
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching cash flow for {symbol}: {str(e)}")
            return pd.DataFrame() 