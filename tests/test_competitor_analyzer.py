import pytest
from unittest.mock import MagicMock, patch
from app.services.competitor import CompetitorAnalyzer
from app.services.sentiment import SentimentAnalyzer
from app.models.competitor import CompetitorAnalysis

@pytest.mark.asyncio
async def test_analyze_competitors():
    with patch('yfinance.Ticker') as mock_ticker:
        mock_info = {
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
        }
        mock_ticker.return_value.info = mock_info

        mock_sentiment_analyzer = MagicMock(spec=SentimentAnalyzer)
        mock_sentiment_analyzer.analyze_sentiment.return_value = MagicMock(overall_score=0.5)

        competitor_analyzer = CompetitorAnalyzer(mock_sentiment_analyzer)
        competitor_analysis = await competitor_analyzer.analyze_competitors("AAPL")

        assert isinstance(competitor_analysis, CompetitorAnalysis)
        assert competitor_analysis.symbol == "AAPL"
        assert len(competitor_analysis.competitors) > 0
