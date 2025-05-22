import pytest
from unittest.mock import patch, MagicMock
from app.services.competitor import CompetitorAnalyzer
from app.models.competitor import CompetitorAnalysis, CompetitorMetrics

@pytest.fixture
def competitor_analyzer():
    return CompetitorAnalyzer()

@pytest.fixture
def mock_stock_info():
    return {
        'longName': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'marketCap': 2000000000000,
        'totalRevenue': 100000000000,
        'profitMargins': 0.2,
        'trailingPE': 25.0,
        'dividendYield': 0.02,
        'beta': 1.2,
        'companyOfficers': [
            {'symbol': 'MSFT'},
            {'symbol': 'GOOGL'}
        ]
    }

@pytest.fixture
def mock_competitor_info():
    return {
        'longName': 'Microsoft Corporation',
        'marketCap': 1500000000000,
        'totalRevenue': 80000000000,
        'profitMargins': 0.25,
        'trailingPE': 30.0,
        'dividendYield': 0.01,
        'beta': 1.1
    }

@pytest.mark.asyncio
async def test_analyze_competitors(competitor_analyzer, mock_stock_info, mock_competitor_info):
    with patch('yfinance.Ticker') as mock_ticker, \
         patch('app.services.sentiment.SentimentAnalyzer.analyze_sentiment') as mock_sentiment:
        
        # Mock stock info
        mock_ticker.return_value.info = mock_stock_info
        
        # Mock competitor info
        mock_ticker.side_effect = [
            MagicMock(info=mock_stock_info),  # Main stock
            MagicMock(info=mock_competitor_info),  # First competitor
            MagicMock(info=mock_competitor_info)   # Second competitor
        ]
        
        # Mock sentiment analysis
        mock_sentiment.return_value.overall_score = 0.5
        
        # Test competitor analysis
        result = await competitor_analyzer.analyze_competitors('AAPL')
        
        assert isinstance(result, CompetitorAnalysis)
        assert result.symbol == 'AAPL'
        assert len(result.competitors) == 2
        assert result.market_position in ['market_leader', 'major_player', 'significant_player', 'niche_player']
        
        # Check competitor metrics
        competitor = result.competitors[0]
        assert isinstance(competitor, CompetitorMetrics)
        assert competitor.symbol == 'MSFT'
        assert competitor.name == 'Microsoft Corporation'
        assert competitor.market_cap == 1500000000000
        assert competitor.sentiment_score == 0.5

@pytest.mark.asyncio
async def test_get_competitors(competitor_analyzer, mock_stock_info):
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker.return_value.info = mock_stock_info
        
        competitors = competitor_analyzer._get_competitors('AAPL', mock_stock_info)
        
        assert len(competitors) == 2
        assert 'MSFT' in competitors
        assert 'GOOGL' in competitors

@pytest.mark.asyncio
async def test_analyze_competitor(competitor_analyzer, mock_competitor_info):
    with patch('yfinance.Ticker') as mock_ticker, \
         patch('app.services.sentiment.SentimentAnalyzer.analyze_sentiment') as mock_sentiment:
        
        mock_ticker.return_value.info = mock_competitor_info
        mock_sentiment.return_value.overall_score = 0.5
        
        result = await competitor_analyzer._analyze_competitor('MSFT')
        
        assert isinstance(result, CompetitorMetrics)
        assert result.symbol == 'MSFT'
        assert result.name == 'Microsoft Corporation'
        assert result.market_cap == 1500000000000
        assert result.sentiment_score == 0.5

@pytest.mark.asyncio
async def test_calculate_market_position(competitor_analyzer, mock_stock_info):
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker.return_value.info = mock_stock_info
        
        competitors = [
            CompetitorMetrics(
                symbol='MSFT',
                name='Microsoft',
                market_cap=1000000000000,
                revenue=50000000000,
                profit_margin=0.2,
                pe_ratio=25.0,
                dividend_yield=0.02,
                beta=1.1,
                sentiment_score=0.5
            )
        ]
        
        position = competitor_analyzer._calculate_market_position('AAPL', competitors)
        
        assert position in ['market_leader', 'major_player', 'significant_player', 'niche_player']

@pytest.mark.asyncio
async def test_competitor_analysis_error_handling(competitor_analyzer):
    with patch('yfinance.Ticker') as mock_ticker:
        # Mock API error
        mock_ticker.return_value.info = {}
        
        # Test error handling
        result = await competitor_analyzer.analyze_competitors('INVALID')
        
        assert isinstance(result, CompetitorAnalysis)
        assert result.symbol == 'INVALID'
        assert len(result.competitors) == 0
        assert result.market_position == 'unknown' 