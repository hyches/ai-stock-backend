from typing import Dict, List, Optional
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from app.models.sentiment import SentimentAnalysis, NewsSentiment, SocialSentiment, AnalystRating
import requests
from textblob import TextBlob
import numpy as np
from app.core.config import Settings
from app.core.cache import get_cache, set_cache
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

settings = Settings()

class SentimentAnalyzer:
    """
    Service for analyzing stock sentiment using news and social media data.
    """
    
    def __init__(self):
        self.news_api_key = settings.ALPHA_VANTAGE_API_KEY # Corrected to use a valid key from settings
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 3600  # 1 hour cache TTL
        
    async def analyze_sentiment(self, symbol: str) -> SentimentAnalysis:
        """
        Analyze sentiment for a given stock symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            SentimentAnalysis object with sentiment scores
        """
        try:
            logger.info(f"Starting sentiment analysis for {symbol}")
            
            # Check cache
            cache_key = f"sentiment_{symbol}"
            cached_data = await get_cache(cache_key)
            if cached_data:
                logger.info(f"Returning cached sentiment data for {symbol}")
                return SentimentAnalysis(**cached_data)

            # Get news sentiment
            news_sentiment = await self._analyze_news_sentiment(symbol)
            
            # Get social media sentiment
            social_sentiment = await self._analyze_social_sentiment(symbol)
            
            # Get analyst recommendations
            analyst_rating = await self._get_analyst_rating(symbol)
            
            # Calculate overall sentiment score
            overall_score = self._calculate_overall_score(
                news_sentiment,
                social_sentiment,
                analyst_rating
            )
            
            result = SentimentAnalysis(
                overall_score=overall_score,
                news_sentiment=news_sentiment,
                social_sentiment=social_sentiment,
                analyst_rating=analyst_rating.rating,
                price_target=analyst_rating.price_target
            )
            
            # Cache the result
            await set_cache(cache_key, result.dict(), ttl=self.cache_ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis for {symbol}: {str(e)}")
            raise ValueError(f"Failed to analyze sentiment for {symbol}: {str(e)}")
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _analyze_news_sentiment(self, symbol: str) -> NewsSentiment:
        """Analyze sentiment from news articles"""
        try:
            # Get news articles
            articles = await self._fetch_news_articles(symbol)
            
            if not articles:
                logger.warning(f"No news articles found for {symbol}")
                return NewsSentiment(score=0.0, article_count=0)
            
            # Calculate sentiment scores
            sentiments = []
            for article in articles:
                if not article.get('title') or not article.get('description'):
                    continue
                # Use TextBlob for sentiment analysis
                blob = TextBlob(article['title'] + " " + article['description'])
                sentiments.append(blob.sentiment.polarity)
            
            if not sentiments:
                logger.warning(f"No valid sentiment scores calculated for {symbol}")
                return NewsSentiment(score=0.0, article_count=0)
            
            # Calculate weighted average
            avg_sentiment = np.mean(sentiments)
            
            return NewsSentiment(
                score=avg_sentiment,
                article_count=len(articles)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment for {symbol}: {str(e)}")
            return NewsSentiment(score=0.0, article_count=0)
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _analyze_social_sentiment(self, symbol: str) -> SocialSentiment:
        """Analyze sentiment from social media"""
        # This is a placeholder as we don't have a real social media API
        logger.info(f"Social media sentiment for {symbol} is a placeholder.")
        return SocialSentiment(score=0.5, post_count=100) # Return a neutral score
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _get_analyst_rating(self, symbol: str) -> AnalystRating:
        """Get analyst recommendations and price targets"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            if not info or 'recommendationKey' not in info:
                logger.warning(f"No analyst data found for {symbol}")
                return AnalystRating(rating='hold', price_target=info.get('regularMarketPrice', 0.0))
            
            return AnalystRating(
                rating=info.get('recommendationKey', 'hold'),
                price_target=info.get('targetMeanPrice', info.get('regularMarketPrice', 0.0))
            )
            
        except Exception as e:
            logger.error(f"Error getting analyst rating for {symbol}: {str(e)}")
            return AnalystRating(rating='hold', price_target=0.0)
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _fetch_news_articles(self, symbol: str) -> List[Dict]:
        """Fetch news articles from Alpha Vantage API"""
        try:
            if not self.news_api_key:
                logger.warning("Alpha Vantage API key not configured")
                return []
                
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'apikey': self.news_api_key,
                'limit': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code != 200 or "feed" not in data:
                logger.error(f"Alpha Vantage API error for {symbol}: {data}")
                return []
                
            articles = data.get('feed', [])
            if not articles:
                logger.warning(f"No news articles found for {symbol}")
                
            return articles
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch news for {symbol}: {e}")
            return []

    def _calculate_overall_score(
        self,
        news_sentiment: NewsSentiment,
        social_sentiment: SocialSentiment,
        analyst_rating: AnalystRating
    ) -> float:
        """
        Calculate a weighted overall sentiment score.
        """
        # Define weights for each sentiment source
        weights = {
            'news': 0.4,
            'social': 0.3,
            'analyst': 0.3
        }

        # Normalize analyst ratings to a -1 to 1 scale
        rating_map = {
            'strong_buy': 1.0,
            'buy': 0.75,
            'hold': 0.0,
            'sell': -0.75,
            'strong_sell': -1.0
        }
        analyst_score = rating_map.get(analyst_rating.rating, 0.0)

        # Calculate weighted average
        overall_score = (
            news_sentiment.score * weights['news'] +
            social_sentiment.score * weights['social'] +
            analyst_score * weights['analyst']
        )
        
        return round(overall_score, 4) 