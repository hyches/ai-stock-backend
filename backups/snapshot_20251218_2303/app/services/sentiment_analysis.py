from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import httpx
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from app.core.config import settings
from app.core.cache import redis_cache

class SentimentAnalysis:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.cache_ttl = 3600  # 1 hour

    async def get_comprehensive_sentiment(self, symbol: str) -> Dict:
        """Get comprehensive sentiment analysis"""
        return {
            "news_sentiment": await self._analyze_news_sentiment(symbol),
            "social_sentiment": await self._analyze_social_sentiment(symbol),
            "market_sentiment": await self._analyze_market_sentiment(symbol),
            "options_sentiment": await self._analyze_options_sentiment(symbol),
            "institutional_sentiment": await self._analyze_institutional_sentiment(symbol),
            "retail_sentiment": await self._analyze_retail_sentiment(symbol),
            "overall_sentiment": await self._calculate_overall_sentiment(symbol)
        }

    async def _analyze_news_sentiment(self, symbol: str) -> Dict:
        """Analyze news sentiment"""
        try:
            news_data = await self._fetch_news_data(symbol)
            
            return {
                "news_articles": {
                    "sentiment": self._analyze_text_sentiment(news_data['articles']),
                    "topics": self._extract_topics(news_data['articles']),
                    "sources": self._analyze_source_bias(news_data['articles'])
                },
                "earnings_calls": {
                    "sentiment": self._analyze_earnings_call_sentiment(symbol),
                    "key_points": self._extract_earnings_key_points(symbol)
                },
                "analyst_reports": {
                    "recommendations": self._analyze_analyst_recommendations(symbol),
                    "price_targets": self._analyze_price_targets(symbol),
                    "earnings_estimates": self._analyze_earnings_estimates(symbol)
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {str(e)}")
            return {}

    async def _analyze_social_sentiment(self, symbol: str) -> Dict:
        """Analyze social media sentiment"""
        try:
            social_data = await self._fetch_social_data(symbol)
            
            return {
                "twitter": {
                    "sentiment": self._analyze_text_sentiment(social_data['twitter']),
                    "volume": self._analyze_social_volume(social_data['twitter']),
                    "influencers": self._identify_influencers(social_data['twitter'])
                },
                "reddit": {
                    "sentiment": self._analyze_text_sentiment(social_data['reddit']),
                    "subreddit_analysis": self._analyze_subreddits(social_data['reddit']),
                    "discussion_topics": self._extract_discussion_topics(social_data['reddit'])
                },
                "stocktwits": {
                    "sentiment": self._analyze_text_sentiment(social_data['stocktwits']),
                    "message_flow": self._analyze_message_flow(social_data['stocktwits']),
                    "user_sentiment": self._analyze_user_sentiment(social_data['stocktwits'])
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing social sentiment: {str(e)}")
            return {}

    async def _analyze_market_sentiment(self, symbol: str) -> Dict:
        """Analyze market sentiment indicators"""
        try:
            market_data = await self._fetch_market_data(symbol)
            
            return {
                "fear_greed_index": self._calculate_fear_greed_index(market_data),
                "put_call_ratio": self._calculate_put_call_ratio(market_data),
                "short_interest": self._analyze_short_interest(market_data),
                "insider_trading": self._analyze_insider_trading(market_data),
                "institutional_ownership": self._analyze_institutional_ownership(market_data)
            }
        except Exception as e:
            logger.error(f"Error analyzing market sentiment: {str(e)}")
            return {}

    async def _analyze_options_sentiment(self, symbol: str) -> Dict:
        """Analyze options market sentiment"""
        try:
            options_data = await self._fetch_options_data(symbol)
            
            return {
                "options_flow": {
                    "call_put_ratio": self._calculate_call_put_ratio(options_data),
                    "volume_analysis": self._analyze_options_volume(options_data),
                    "open_interest": self._analyze_open_interest(options_data)
                },
                "implied_volatility": {
                    "iv_skew": self._calculate_iv_skew(options_data),
                    "iv_percentile": self._calculate_iv_percentile(options_data),
                    "iv_rank": self._calculate_iv_rank(options_data)
                },
                "options_activity": {
                    "unusual_activity": self._identify_unusual_activity(options_data),
                    "block_trades": self._analyze_block_trades(options_data),
                    "sweeps": self._analyze_sweeps(options_data)
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing options sentiment: {str(e)}")
            return {}

    async def _analyze_institutional_sentiment(self, symbol: str) -> Dict:
        """Analyze institutional investor sentiment"""
        try:
            institutional_data = await self._fetch_institutional_data(symbol)
            
            return {
                "institutional_activity": {
                    "buying_pressure": self._calculate_buying_pressure(institutional_data),
                    "selling_pressure": self._calculate_selling_pressure(institutional_data),
                    "net_flow": self._calculate_net_flow(institutional_data)
                },
                "fund_holdings": {
                    "etf_holdings": self._analyze_etf_holdings(institutional_data),
                    "mutual_fund_holdings": self._analyze_mutual_fund_holdings(institutional_data),
                    "hedge_fund_holdings": self._analyze_hedge_fund_holdings(institutional_data)
                },
                "institutional_ownership": {
                    "ownership_changes": self._analyze_ownership_changes(institutional_data),
                    "concentration": self._analyze_ownership_concentration(institutional_data),
                    "top_holders": self._identify_top_holders(institutional_data)
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing institutional sentiment: {str(e)}")
            return {}

    async def _analyze_retail_sentiment(self, symbol: str) -> Dict:
        """Analyze retail investor sentiment"""
        try:
            retail_data = await self._fetch_retail_data(symbol)
            
            return {
                "retail_activity": {
                    "buying_pressure": self._calculate_retail_buying_pressure(retail_data),
                    "selling_pressure": self._calculate_retail_selling_pressure(retail_data),
                    "net_flow": self._calculate_retail_net_flow(retail_data)
                },
                "retail_holdings": {
                    "ownership_changes": self._analyze_retail_ownership_changes(retail_data),
                    "concentration": self._analyze_retail_concentration(retail_data),
                    "average_position": self._calculate_average_position(retail_data)
                },
                "retail_behavior": {
                    "trading_patterns": self._analyze_trading_patterns(retail_data),
                    "holding_period": self._analyze_holding_period(retail_data),
                    "risk_tolerance": self._analyze_risk_tolerance(retail_data)
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing retail sentiment: {str(e)}")
            return {}

    async def _calculate_overall_sentiment(self, symbol: str) -> Dict:
        """Calculate overall sentiment score"""
        try:
            all_sentiment_data = await self._fetch_all_sentiment_data(symbol)
            
            return {
                "composite_score": self._calculate_composite_score(all_sentiment_data),
                "sentiment_trend": self._analyze_sentiment_trend(all_sentiment_data),
                "sentiment_strength": self._calculate_sentiment_strength(all_sentiment_data),
                "sentiment_consensus": self._calculate_sentiment_consensus(all_sentiment_data),
                "sentiment_forecast": self._generate_sentiment_forecast(all_sentiment_data)
            }
        except Exception as e:
            logger.error(f"Error calculating overall sentiment: {str(e)}")
            return {}

    def _analyze_text_sentiment(self, texts: List[str]) -> Dict:
        """Analyze sentiment of text using multiple methods"""
        vader_scores = [self.vader.polarity_scores(text) for text in texts]
        textblob_scores = [TextBlob(text).sentiment for text in texts]
        
        return {
            "vader": {
                "compound": np.mean([score['compound'] for score in vader_scores]),
                "pos": np.mean([score['pos'] for score in vader_scores]),
                "neg": np.mean([score['neg'] for score in vader_scores]),
                "neu": np.mean([score['neu'] for score in vader_scores])
            },
            "textblob": {
                "polarity": np.mean([score.polarity for score in textblob_scores]),
                "subjectivity": np.mean([score.subjectivity for score in textblob_scores])
            }
        }

    # Add more helper methods for other analyses...

sentiment_analysis = SentimentAnalysis() 