import pytest
from unittest.mock import MagicMock, patch
from app.services.report_generator import ReportGenerator
from app.models.report import ReportResponse

@pytest.mark.asyncio
async def test_generate_report():
    with patch('yfinance.Ticker') as mock_ticker:
        mock_info = {
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'currentPrice': 150.0,
            'totalRevenue': 365817000000,
            'netIncome': 94680000000,
            'trailingEps': 5.61,
            'trailingPE': 26.7,
            'marketCap': 2400000000000,
            'dividendYield': 0.006,
            'debtToEquity': 1.5,
            'profitMargins': 0.25,
        }
        mock_ticker.return_value.info = mock_info
        mock_ticker.return_value.history.return_value = MagicMock()

        report_generator = ReportGenerator()
        report = await report_generator.generate_report("AAPL")

        assert isinstance(report, ReportResponse)
        assert report.symbol == "AAPL"
        assert report.company_name == "Apple Inc."
        assert report.financials.revenue == 365817.0
