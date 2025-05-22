import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.models.report import (
    ReportResponse, FinancialMetrics, TechnicalIndicators,
    SentimentAnalysis
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Service for generating stock research reports.
    """
    
    def __init__(self):
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
        
    async def generate_report(
        self,
        symbol: str,
        include_technical: bool = True,
        include_sentiment: bool = True,
        include_competitors: bool = True,
        format: str = "pdf"
    ) -> ReportResponse:
        """
        Generate a research report for a given stock.
        
        Args:
            symbol: Stock ticker symbol
            include_technical: Whether to include technical analysis
            include_sentiment: Whether to include sentiment analysis
            include_competitors: Whether to include competitor analysis
            format: Report format (pdf or json)
            
        Returns:
            ReportResponse object containing the generated report
        """
        try:
            logger.info(f"Starting report generation for {symbol}")
            
            # Fetch stock data
            stock = yf.Ticker(symbol)
            info = stock.info
            
            if not info:
                raise ValueError(f"No data found for {symbol}")
                
            # Get historical data for technical analysis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=200)
            hist = stock.history(start=start_date, end=end_date)
            
            # Calculate financial metrics
            financials = self._calculate_financial_metrics(info)
            
            # Calculate technical indicators if requested
            technicals = None
            if include_technical and not hist.empty:
                technicals = self._calculate_technical_indicators(hist)
                
            # Calculate sentiment if requested
            sentiment = None
            if include_sentiment:
                sentiment = self._calculate_sentiment(symbol)
                
            # Get competitors if requested
            competitors = None
            if include_competitors:
                competitors = self._get_competitors(symbol)
                
            # Generate summary and recommendations
            summary = self._generate_summary(symbol, info, financials, technicals, sentiment)
            recommendations = self._generate_recommendations(financials, technicals, sentiment)
            risk_factors = self._identify_risk_factors(financials, technicals, sentiment)
            
            # Create report response
            report = ReportResponse(
                symbol=symbol,
                company_name=info.get('longName', symbol),
                sector=info.get('sector', ''),
                industry=info.get('industry', ''),
                current_price=info.get('currentPrice', 0.0),
                financials=financials,
                technicals=technicals,
                sentiment=sentiment,
                competitors=competitors,
                summary=summary,
                recommendations=recommendations,
                risk_factors=risk_factors
            )
            
            # Generate PDF if requested
            if format.lower() == "pdf":
                report.report_url = self._generate_pdf(report)
                
            logger.info(f"Successfully generated report for {symbol}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report for {symbol}: {str(e)}")
            raise
            
    def _calculate_financial_metrics(self, info: Dict) -> FinancialMetrics:
        """Calculate financial metrics from stock info"""
        return FinancialMetrics(
            revenue=info.get('totalRevenue', 0) / 1_000_000,  # Convert to millions
            net_income=info.get('netIncome', 0) / 1_000_000,
            eps=info.get('trailingEps', 0),
            pe_ratio=info.get('trailingPE', 0),
            market_cap=info.get('marketCap', 0) / 1_000_000,
            dividend_yield=info.get('dividendYield', 0) * 100 if info.get('dividendYield') else None,
            debt_to_equity=info.get('debtToEquity', 0),
            profit_margin=info.get('profitMargins', 0) * 100
        )
        
    def _calculate_technical_indicators(self, hist: pd.DataFrame) -> TechnicalIndicators:
        """Calculate technical indicators from historical data"""
        # Calculate moving averages
        ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        
        # Calculate RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))
        
        # Calculate MACD
        exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
        exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        
        return TechnicalIndicators(
            ma_50=ma_50,
            ma_200=ma_200,
            rsi=rsi,
            macd=macd.iloc[-1],
            volume_avg=hist['Volume'].mean()
        )
        
    def _calculate_sentiment(self, symbol: str) -> SentimentAnalysis:
        """Calculate sentiment scores (placeholder implementation)"""
        # TODO: Implement actual sentiment analysis
        return SentimentAnalysis(
            overall_score=0.5,
            news_sentiment=0.6,
            social_sentiment=0.4,
            analyst_rating="Buy",
            price_target=0.0
        )
        
    def _get_competitors(self, symbol: str) -> List[str]:
        """Get list of competitors (placeholder implementation)"""
        # TODO: Implement actual competitor analysis
        return []
        
    def _generate_summary(
        self,
        symbol: str,
        info: Dict,
        financials: FinancialMetrics,
        technicals: Optional[TechnicalIndicators],
        sentiment: Optional[SentimentAnalysis]
    ) -> str:
        """Generate AI summary of the stock"""
        # TODO: Implement actual AI summary generation
        return f"Summary for {symbol}"
        
    def _generate_recommendations(
        self,
        financials: FinancialMetrics,
        technicals: Optional[TechnicalIndicators],
        sentiment: Optional[SentimentAnalysis]
    ) -> List[str]:
        """Generate investment recommendations"""
        recommendations = []
        
        # Financial recommendations
        if financials.pe_ratio > 30:
            recommendations.append("High P/E ratio suggests overvaluation")
        if financials.debt_to_equity and financials.debt_to_equity > 2:
            recommendations.append("High debt levels may pose risks")
            
        # Technical recommendations
        if technicals:
            if technicals.rsi > 70:
                recommendations.append("RSI indicates overbought conditions")
            elif technicals.rsi < 30:
                recommendations.append("RSI indicates oversold conditions")
                
        # Sentiment recommendations
        if sentiment and sentiment.overall_score < -0.5:
            recommendations.append("Negative sentiment may impact short-term performance")
            
        return recommendations
        
    def _identify_risk_factors(
        self,
        financials: FinancialMetrics,
        technicals: Optional[TechnicalIndicators],
        sentiment: Optional[SentimentAnalysis]
    ) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        # Financial risks
        if financials.profit_margin < 5:
            risks.append("Low profit margins may impact growth")
        if financials.debt_to_equity and financials.debt_to_equity > 1.5:
            risks.append("High debt levels increase financial risk")
            
        # Technical risks
        if technicals:
            if technicals.ma_50 < technicals.ma_200:
                risks.append("Bearish technical trend")
                
        # Sentiment risks
        if sentiment and sentiment.overall_score < -0.3:
            risks.append("Negative market sentiment")
            
        return risks
        
    def _generate_pdf(self, report: ReportResponse) -> str:
        """Generate PDF report"""
        try:
            # Create PDF file path
            pdf_path = self.report_dir / f"{report.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            heading_style = styles['Heading2']
            normal_style = styles['Normal']
            
            # Build PDF content
            content = []
            
            # Title
            content.append(Paragraph(f"Research Report: {report.company_name}", title_style))
            content.append(Spacer(1, 12))
            
            # Summary
            content.append(Paragraph("Summary", heading_style))
            content.append(Paragraph(report.summary, normal_style))
            content.append(Spacer(1, 12))
            
            # Financial Metrics
            content.append(Paragraph("Financial Metrics", heading_style))
            financial_data = [
                ["Metric", "Value"],
                ["Revenue", f"${report.financials.revenue:.2f}M"],
                ["Net Income", f"${report.financials.net_income:.2f}M"],
                ["EPS", f"${report.financials.eps:.2f}"],
                ["P/E Ratio", f"{report.financials.pe_ratio:.2f}"],
                ["Market Cap", f"${report.financials.market_cap:.2f}M"],
                ["Profit Margin", f"{report.financials.profit_margin:.2f}%"]
            ]
            if report.financials.dividend_yield:
                financial_data.append(["Dividend Yield", f"{report.financials.dividend_yield:.2f}%"])
            if report.financials.debt_to_equity:
                financial_data.append(["Debt/Equity", f"{report.financials.debt_to_equity:.2f}"])
                
            financial_table = Table(financial_data)
            financial_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(financial_table)
            content.append(Spacer(1, 12))
            
            # Technical Analysis
            if report.technicals:
                content.append(Paragraph("Technical Analysis", heading_style))
                technical_data = [
                    ["Indicator", "Value"],
                    ["50-day MA", f"${report.technicals.ma_50:.2f}"],
                    ["200-day MA", f"${report.technicals.ma_200:.2f}"],
                    ["RSI", f"{report.technicals.rsi:.2f}"],
                    ["MACD", f"{report.technicals.macd:.2f}"],
                    ["Avg Volume", f"{report.technicals.volume_avg:,.0f}"]
                ]
                technical_table = Table(technical_data)
                technical_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                content.append(technical_table)
                content.append(Spacer(1, 12))
                
            # Recommendations
            content.append(Paragraph("Recommendations", heading_style))
            for rec in report.recommendations:
                content.append(Paragraph(f"• {rec}", normal_style))
            content.append(Spacer(1, 12))
            
            # Risk Factors
            content.append(Paragraph("Risk Factors", heading_style))
            for risk in report.risk_factors:
                content.append(Paragraph(f"• {risk}", normal_style))
                
            # Build PDF
            doc.build(content)
            
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise 