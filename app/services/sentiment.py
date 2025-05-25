from typing import Dict, List, Optional
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from app.models.sentiment import SentimentAnalysis, NewsSentiment, SocialSentiment, AnalystRating
import requests
from textblob import TextBlob
import numpy as np
from app.config import Settings
settings = Settings()
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Service for analyzing stock sentiment using news and social media data.
    """
    
    def __init__(self):
        self.news_api_key = settings.NEWS_API_KEY
        self.twitter_api_key = settings.TWITTER_API_KEY
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
            if cache_key in self.cache:
                cache_data, cache_time = self.cache[cache_key]
                if (datetime.now() - cache_time).seconds < self.cache_ttl:
                    logger.info(f"Returning cached sentiment data for {symbol}")
                    return cache_data
            
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
            self.cache[cache_key] = (result, datetime.now())
            
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
        try:
            # Get social media posts
            posts = await self._fetch_social_posts(symbol)
            
            if not posts:
                logger.warning(f"No social media posts found for {symbol}")
                return SocialSentiment(score=0.0, post_count=0)
            
            # Calculate sentiment scores
            sentiments = []
            for post in posts:
                if not post.get('text'):
                    continue
                blob = TextBlob(post['text'])
                sentiments.append(blob.sentiment.polarity)
            
            if not sentiments:
                logger.warning(f"No valid sentiment scores calculated for {symbol}")
                return SocialSentiment(score=0.0, post_count=0)
            
            # Calculate weighted average
            avg_sentiment = np.mean(sentiments)
            
            return SocialSentiment(
                score=avg_sentiment,
                post_count=len(posts)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing social sentiment for {symbol}: {str(e)}")
            return SocialSentiment(score=0.0, post_count=0)
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _get_analyst_rating(self, symbol: str) -> AnalystRating:
        """Get analyst recommendations and price targets"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            if not info:
                logger.warning(f"No analyst data found for {symbol}")
                return AnalystRating(rating='hold', price_target=0.0)
            
            return AnalystRating(
                rating=info.get('recommendationKey', 'hold'),
                price_target=info.get('targetMeanPrice', 0.0)
            )
            
        except Exception as e:
            logger.error(f"Error getting analyst rating for {symbol}: {str(e)}")
            return AnalystRating(rating='hold', price_target=0.0)
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _fetch_news_articles(self, symbol: str) -> List[Dict]:
        """Fetch news articles from News API"""
        try:
            if not self.news_api_key:
                logger.warning("News API key not configured")
                return []
                
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': symbol,
                'apiKey': self.news_api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code != 200:
                logger.error(f"News API error for {symbol}: {data.get('message')}")
                return []
                
            articles = data.get('articles', [])
            if not articles:
                logger.warning(f"No news articles found for {symbol}")
                
            return articles
            
        except requests.Timeout:
            logger.error(f"News API timeout for {symbol}")
            return []
        except Exception as e:
            logger.error(f"Error fetching news articles for {symbol}: {str(e)}")
            return []
            
    async def _fetch_social_posts(self, symbol: str) -> List[Dict]:
        """Fetch social media posts (placeholder implementation)"""
        # TODO: Implement actual social media API integration
        return []
        
    def _calculate_overall_score(
        self,
        news_sentiment: NewsSentiment,
        social_sentiment: SocialSentiment,
        analyst_rating: AnalystRating
    ) -> float:
        """Calculate overall sentiment score"""
        try:
            # Weight the different sentiment sources
            weights = {
                'news': 0.4,
                'social': 0.3,
                'analyst': 0.3
            }
            
            # Convert analyst rating to numeric score
            analyst_score = {
                'strong_buy': 1.0,
                'buy': 0.75,
                'hold': 0.5,
                'sell': 0.25,
                'strong_sell': 0.0
            }.get(analyst_rating.rating.lower(), 0.5)
            
            # Calculate weighted average
            overall_score = (
                weights['news'] * news_sentiment.score +
                weights['social'] * social_sentiment.score +
                weights['analyst'] * analyst_score
            )
            
            return overall_score
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {str(e)}")
            return 0.0 