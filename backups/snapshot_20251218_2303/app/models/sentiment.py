from pydantic import BaseModel
from typing import Optional

class NewsSentiment(BaseModel):
    score: float  # -1 to 1
    article_count: int

class SocialSentiment(BaseModel):
    score: float  # -1 to 1
    post_count: int

class AnalystRating(BaseModel):
    rating: str  # strong_buy, buy, hold, sell, strong_sell
    price_target: float

class SentimentAnalysis(BaseModel):
    overall_score: float  # -1 to 1
    news_sentiment: NewsSentiment
    social_sentiment: SocialSentiment
    analyst_rating: str
    price_target: Optional[float] = None 