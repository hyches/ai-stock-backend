import pytest
from unittest.mock import patch, MagicMock
from app.services.sentiment import SentimentAnalyzer
from app.models.sentiment import SentimentAnalysis, NewsSentiment, SocialSentiment, AnalystRating

@pytest.fixture
def sentiment_analyzer():
    return SentimentAnalyzer()

@pytest.fixture
def mock_news_response():
    return {
        'articles': [
            {
                'title': 'Positive news about AAPL',
                'description': 'Apple stock is performing well'
            },
            {
                'title': 'Negative news about AAPL',
                'description': 'Apple faces challenges'
            }
        ]
    }

@pytest.fixture
def mock_stock_info():
    return {
        'recommendationKey': 'buy',
        'targetMeanPrice': 150.0
    }

@pytest.mark.asyncio
async def test_analyze_sentiment(sentiment_analyzer, mock_news_response, mock_stock_info):
    with patch('requests.get') as mock_get, \
         patch('yfinance.Ticker') as mock_ticker:
        
        # Mock news API response
        mock_get.return_value.json.return_value = mock_news_response
        mock_get.return_value.status_code = 200
        
        # Mock stock info
        mock_ticker.return_value.info = mock_stock_info
        
        # Test sentiment analysis
        result = await sentiment_analyzer.analyze_sentiment('AAPL')
        
        assert isinstance(result, SentimentAnalysis)
        assert -1 <= result.overall_score <= 1
        assert isinstance(result.news_sentiment, NewsSentiment)
        assert isinstance(result.social_sentiment, SocialSentiment)
        assert result.analyst_rating == 'buy'
        assert result.price_target == 150.0

@pytest.mark.asyncio
async def test_analyze_news_sentiment(sentiment_analyzer, mock_news_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_news_response
        mock_get.return_value.status_code = 200
        
        result = await sentiment_analyzer._analyze_news_sentiment('AAPL')
        
        assert isinstance(result, NewsSentiment)
        assert -1 <= result.score <= 1
        assert result.article_count == 2

@pytest.mark.asyncio
async def test_get_analyst_rating(sentiment_analyzer, mock_stock_info):
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker.return_value.info = mock_stock_info
        
        result = await sentiment_analyzer._get_analyst_rating('AAPL')
        
        assert isinstance(result, AnalystRating)
        assert result.rating == 'buy'
        assert result.price_target == 150.0

@pytest.mark.asyncio
async def test_analyze_sentiment_error_handling(sentiment_analyzer):
    with patch('requests.get') as mock_get, \
         patch('yfinance.Ticker') as mock_ticker:
        
        # Mock API error
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {'message': 'API Error'}
        
        # Mock stock info error
        mock_ticker.return_value.info = {}
        
        # Test error handling
        result = await sentiment_analyzer.analyze_sentiment('AAPL')
        
        assert isinstance(result, SentimentAnalysis)
        assert result.overall_score == 0.0
        assert result.news_sentiment.article_count == 0
        assert result.social_sentiment.post_count == 0
        assert result.analyst_rating == 'hold'
        assert result.price_target == 0.0

@pytest.mark.asyncio
async def test_sentiment_caching(sentiment_analyzer, mock_news_response, mock_stock_info):
    with patch('requests.get') as mock_get, \
         patch('yfinance.Ticker') as mock_ticker:
        
        # Mock responses
        mock_get.return_value.json.return_value = mock_news_response
        mock_get.return_value.status_code = 200
        mock_ticker.return_value.info = mock_stock_info
        
        # First call
        result1 = await sentiment_analyzer.analyze_sentiment('AAPL')
        
        # Second call should use cache
        result2 = await sentiment_analyzer.analyze_sentiment('AAPL')
        
        assert result1 == result2
        assert mock_get.call_count == 1  # API called only once 