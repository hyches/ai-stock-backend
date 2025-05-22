import pytest
from app.models.report import ReportRequest, ReportResponse
from app.services.report_generator import ReportGenerator
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
import os

@pytest.fixture
def mock_stock_info():
    """Fixture for mock stock info"""
    return {
        'symbol': 'AAPL',
        'longName': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'currentPrice': 150.0,
        'totalRevenue': 1000000000,
        'netIncome': 200000000,
        'trailingEps': 5.0,
        'trailingPE': 30.0,
        'marketCap': 2500000000,
        'dividendYield': 0.5,
        'debtToEquity': 1.5,
        'profitMargins': 0.2
    }

@pytest.fixture
def mock_historical_data():
    """Fixture for mock historical data"""
    dates = pd.date_range(end=datetime.now(), periods=200)
    return pd.DataFrame({
        'Close': [150.0] * 200,
        'Volume': [1000000] * 200
    }, index=dates)

@pytest.fixture
def report_generator():
    """Fixture for ReportGenerator instance"""
    return ReportGenerator()

@pytest.mark.asyncio
async def test_generate_report_basic(report_generator, mock_stock_info, mock_historical_data):
    """Test basic report generation"""
    with patch('app.services.report_generator.yf.Ticker') as mock_ticker:
        # Setup mock
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_stock_info
        mock_ticker_instance.history.return_value = mock_historical_data
        mock_ticker.return_value = mock_ticker_instance
        
        # Create test request
        request = ReportRequest(
            symbol="AAPL",
            include_technical=True,
            include_sentiment=True,
            include_competitors=True,
            format="pdf"
        )
        
        # Generate report
        report = await report_generator.generate_report(
            symbol=request.symbol,
            include_technical=request.include_technical,
            include_sentiment=request.include_sentiment,
            include_competitors=request.include_competitors,
            format=request.format
        )
        
        # Verify report
        assert report.symbol == "AAPL"
        assert report.company_name == "Apple Inc."
        assert report.sector == "Technology"
        assert report.current_price == 150.0
        assert report.financials is not None
        assert report.technicals is not None
        assert report.sentiment is not None
        assert report.report_url is not None

@pytest.mark.asyncio
async def test_generate_report_technical_analysis(report_generator, mock_stock_info, mock_historical_data):
    """Test report generation with technical analysis"""
    with patch('app.services.report_generator.yf.Ticker') as mock_ticker:
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_stock_info
        mock_ticker_instance.history.return_value = mock_historical_data
        mock_ticker.return_value = mock_ticker_instance
        
        request = ReportRequest(
            symbol="AAPL",
            include_technical=True,
            include_sentiment=False,
            include_competitors=False,
            format="json"
        )
        
        report = await report_generator.generate_report(
            symbol=request.symbol,
            include_technical=request.include_technical,
            include_sentiment=request.include_sentiment,
            include_competitors=request.include_competitors,
            format=request.format
        )
        
        # Verify technical analysis
        assert report.technicals is not None
        assert report.technicals.ma_50 is not None
        assert report.technicals.ma_200 is not None
        assert report.technicals.rsi is not None
        assert report.technicals.macd is not None

@pytest.mark.asyncio
async def test_generate_report_pdf_format(report_generator, mock_stock_info, mock_historical_data):
    """Test PDF report generation"""
    with patch('app.services.report_generator.yf.Ticker') as mock_ticker:
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_stock_info
        mock_ticker_instance.history.return_value = mock_historical_data
        mock_ticker.return_value = mock_ticker_instance
        
        request = ReportRequest(
            symbol="AAPL",
            include_technical=True,
            include_sentiment=True,
            include_competitors=True,
            format="pdf"
        )
        
        report = await report_generator.generate_report(
            symbol=request.symbol,
            include_technical=request.include_technical,
            include_sentiment=request.include_sentiment,
            include_competitors=request.include_competitors,
            format=request.format
        )
        
        # Verify PDF generation
        assert report.report_url is not None
        assert os.path.exists(report.report_url)
        assert report.report_url.endswith('.pdf')

@pytest.mark.asyncio
async def test_generate_report_error_handling(report_generator):
    """Test error handling in report generation"""
    with patch('app.services.report_generator.yf.Ticker') as mock_ticker:
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = None  # Simulate failed data fetch
        mock_ticker.return_value = mock_ticker_instance
        
        request = ReportRequest(
            symbol="INVALID",
            include_technical=True,
            include_sentiment=True,
            include_competitors=True,
            format="pdf"
        )
        
        # Verify error handling
        with pytest.raises(ValueError):
            await report_generator.generate_report(
                symbol=request.symbol,
                include_technical=request.include_technical,
                include_sentiment=request.include_sentiment,
                include_competitors=request.include_competitors,
                format=request.format
            )

@pytest.mark.asyncio
async def test_generate_report_recommendations(report_generator, mock_stock_info, mock_historical_data):
    """Test generation of recommendations and risk factors"""
    with patch('app.services.report_generator.yf.Ticker') as mock_ticker:
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = mock_stock_info
        mock_ticker_instance.history.return_value = mock_historical_data
        mock_ticker.return_value = mock_ticker_instance
        
        request = ReportRequest(
            symbol="AAPL",
            include_technical=True,
            include_sentiment=True,
            include_competitors=True,
            format="json"
        )
        
        report = await report_generator.generate_report(
            symbol=request.symbol,
            include_technical=request.include_technical,
            include_sentiment=request.include_sentiment,
            include_competitors=request.include_competitors,
            format=request.format
        )
        
        # Verify recommendations and risk factors
        assert len(report.recommendations) > 0
        assert len(report.risk_factors) > 0
        assert all(isinstance(rec, str) for rec in report.recommendations)
        assert all(isinstance(risk, str) for risk in report.risk_factors) 