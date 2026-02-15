from typing import List, Dict, Optional
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from app.models.competitor import CompetitorAnalysis, CompetitorMetrics
from app.services.sentiment import SentimentAnalyzer

logger = logging.getLogger(__name__)

class CompetitorAnalyzer:
    """
    Service for analyzing stock competitors and market position.
    """
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        
    async def analyze_competitors(self, symbol: str) -> CompetitorAnalysis:
        """
        Analyze competitors for a given stock symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            CompetitorAnalysis object with competitor metrics
        """
        try:
            logger.info(f"Starting competitor analysis for {symbol}")
            
            # Get company info
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get competitors
            competitors = self._get_competitors(symbol, info)
            
            # Analyze each competitor
            competitor_metrics = []
            for comp_symbol in competitors:
                metrics = await self._analyze_competitor(comp_symbol)
                if metrics:
                    competitor_metrics.append(metrics)
            
            # Calculate market position
            market_position = self._calculate_market_position(symbol, competitor_metrics)
            
            return CompetitorAnalysis(
                symbol=symbol,
                competitors=competitor_metrics,
                market_position=market_position
            )
            
        except Exception as e:
            logger.error(f"Error in competitor analysis: {str(e)}")
            raise
            
    def _get_competitors(self, symbol: str, info: Dict) -> List[str]:
        """Get list of competitors"""
        try:
            # Try to get competitors from Yahoo Finance
            competitors = info.get('companyOfficers', [])
            if competitors:
                return [comp['symbol'] for comp in competitors if 'symbol' in comp]
            
            # Fallback to sector-based competitors
            sector = info.get('sector', '')
            if sector:
                # Get top companies in the same sector
                sector_stocks = yf.Tickers(sector)
                return [stock for stock in sector_stocks.tickers if stock != symbol][:5]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting competitors: {str(e)}")
            return []
            
    async def _analyze_competitor(self, symbol: str) -> Optional[CompetitorMetrics]:
        """Analyze a single competitor"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get financial metrics
            metrics = CompetitorMetrics(
                symbol=symbol,
                name=info.get('longName', symbol),
                market_cap=info.get('marketCap', 0),
                revenue=info.get('totalRevenue', 0),
                profit_margin=info.get('profitMargins', 0),
                pe_ratio=info.get('trailingPE', 0),
                dividend_yield=info.get('dividendYield', 0),
                beta=info.get('beta', 1.0)
            )
            
            # Get sentiment
            sentiment = await self.sentiment_analyzer.analyze_sentiment(symbol)
            metrics.sentiment_score = sentiment.overall_score
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing competitor {symbol}: {str(e)}")
            return None
            
    def _calculate_market_position(self, symbol: str, competitors: List[CompetitorMetrics]) -> str:
        """Calculate market position relative to competitors"""
        try:
            # Get company metrics
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Calculate market share
            total_market_cap = sum(comp.market_cap for comp in competitors) + info.get('marketCap', 0)
            market_share = (info.get('marketCap', 0) / total_market_cap) * 100
            
            # Determine market position
            if market_share > 50:
                return "market_leader"
            elif market_share > 20:
                return "major_player"
            elif market_share > 5:
                return "significant_player"
            else:
                return "niche_player"
                
        except Exception as e:
            logger.error(f"Error calculating market position: {str(e)}")
            return "unknown" 