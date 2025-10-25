import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
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
from app.services.sentiment_analysis import SentimentAnalysis
from app.services.ml_predictions import get_price_predictions
try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

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
        """Calculate sentiment scores using TextBlob or keyword-based fallback"""
        # Example: fetch news headlines (mocked here)
        news = [
            f"{symbol} stock surges on strong earnings",
            f"Analysts are bullish on {symbol}",
            f"{symbol} faces regulatory challenges"
        ]
        social = [
            f"I love {symbol} stock!",
            f"{symbol} is risky right now"
        ]
        def analyze(texts):
            if TextBlob:
                scores = [TextBlob(t).sentiment.polarity for t in texts]
            else:
                # Fallback: +1 for 'love', -1 for 'risky', else 0
                scores = [1 if 'love' in t else -1 if 'risky' in t else 0 for t in texts]
            return sum(scores) / len(scores) if scores else 0
        news_sentiment = analyze(news)
        social_sentiment = analyze(social)
        overall_score = (news_sentiment + social_sentiment) / 2
        analyst_rating = "Buy" if overall_score > 0 else "Sell"
        price_target = 100.0 + 10 * overall_score  # Dummy logic
        return SentimentAnalysis(
            overall_score=overall_score,
            news_sentiment=news_sentiment,
            social_sentiment=social_sentiment,
            analyst_rating=analyst_rating,
            price_target=price_target
        )
        
    def _get_competitors(self, symbol: str) -> List[str]:
        """Get list of competitors using a static mapping"""
        competitors_map = {
            'AAPL': ['MSFT', 'GOOGL', 'SAMSUNG'],
            'MSFT': ['AAPL', 'GOOGL', 'IBM'],
            'GOOGL': ['AAPL', 'MSFT', 'META'],
            'TSLA': ['GM', 'F', 'NIO'],
            'AMZN': ['WMT', 'EBAY', 'BABA'],
        }
        return competitors_map.get(symbol.upper(), ['COMP1', 'COMP2'])
        
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

class ResearchReport:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.stock = yf.Ticker(symbol)
        self.historical_data = self.stock.history(period="1y")
        
    def generate_report(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "company_name": self.stock.info.get("longName", "Honeywell Automation India Ltd"),
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "current_price": self.stock.info.get("currentPrice", 0),
            "summary": self._generate_summary(),
            "technical_analysis": self._analyze_technical(),
            "fundamental_analysis": self._analyze_fundamental(),
            "ml_predictions": self._get_predictions(),
            "sentiment_analysis": self._analyze_sentiment(),
            "risk_assessment": self._assess_risk(),
            "recommendation": self._generate_recommendation()
        }
    
    def _generate_summary(self) -> str:
        return f"""
        Honeywell Automation India Ltd (HONAUT.NS) is a leading provider of automation and control solutions in India.
        The company operates in the industrial automation sector and has shown consistent growth in recent years.
        Current market position and recent developments suggest a positive outlook for the company.
        """
    
    def _analyze_technical(self) -> Dict[str, Any]:
        indicators = calculate_technical_indicators(self.historical_data)
        return {
            "trend": {
                "sma_20": indicators.get("sma_20", 0),
                "sma_50": indicators.get("sma_50", 0),
                "sma_200": indicators.get("sma_200", 0),
                "trend_strength": "Bullish" if indicators.get("sma_20", 0) > indicators.get("sma_50", 0) else "Bearish"
            },
            "momentum": {
                "rsi": indicators.get("rsi", 0),
                "macd": indicators.get("macd", 0),
                "signal": indicators.get("signal", 0)
            },
            "volatility": {
                "bollinger_upper": indicators.get("bollinger_upper", 0),
                "bollinger_lower": indicators.get("bollinger_lower", 0),
                "atr": indicators.get("atr", 0)
            }
        }
    
    def _analyze_fundamental(self) -> Dict[str, Any]:
        return {
            "financial_metrics": {
                "pe_ratio": self.stock.info.get("trailingPE", 0),
                "eps": self.stock.info.get("trailingEps", 0),
                "dividend_yield": self.stock.info.get("dividendYield", 0),
                "market_cap": self.stock.info.get("marketCap", 0)
            },
            "growth_metrics": {
                "revenue_growth": self.stock.info.get("revenueGrowth", 0),
                "earnings_growth": self.stock.info.get("earningsGrowth", 0),
                "profit_margins": self.stock.info.get("profitMargins", 0)
            },
            "valuation": {
                "book_value": self.stock.info.get("bookValue", 0),
                "price_to_book": self.stock.info.get("priceToBook", 0),
                "enterprise_value": self.stock.info.get("enterpriseValue", 0)
            }
        }
    
    def _get_predictions(self) -> Dict[str, Any]:
        predictions = get_price_predictions(self.symbol)
        return {
            "price_targets": {
                "1_week": predictions.get("1w", 0),
                "1_month": predictions.get("1m", 0),
                "3_months": predictions.get("3m", 0)
            },
            "confidence_score": predictions.get("confidence", 0),
            "prediction_factors": predictions.get("factors", [])
        }
    
    def _analyze_sentiment(self) -> Dict[str, Any]:
        sentiment = SentimentAnalysis(self.symbol)
        return {
            "overall_sentiment": sentiment.overall,
            "news_sentiment": sentiment.news,
            "social_sentiment": sentiment.social,
            "analyst_ratings": sentiment.analyst_ratings
        }
    
    def _assess_risk(self) -> Dict[str, Any]:
        return {
            "market_risk": "Medium",
            "volatility_risk": "Low",
            "liquidity_risk": "Low",
            "sector_risk": "Medium",
            "risk_factors": [
                "Market competition",
                "Economic conditions",
                "Regulatory changes",
                "Technology disruption"
            ]
        }
    
    def _generate_recommendation(self) -> Dict[str, Any]:
        current_price = self.stock.info.get("currentPrice", 0)
        technical_analysis = self._analyze_technical()
        
        # Calculate entry points based on technical levels
        support_levels = [
            technical_analysis["volatility"]["bollinger_lower"],
            technical_analysis["trend"]["sma_50"],
            current_price * 0.95  # 5% below current price
        ]
        
        # Sort support levels and get the highest one below current price
        valid_supports = [s for s in support_levels if s < current_price]
        optimal_entry = max(valid_supports) if valid_supports else current_price * 0.95
        
        return {
            "rating": "BUY",
            "target_price": self._get_predictions()["price_targets"]["3_months"],
            "time_horizon": "3-6 months",
            "entry_points": {
                "optimal_entry": round(optimal_entry, 2),
                "aggressive_entry": round(current_price * 0.98, 2),  # 2% below current
                "conservative_entry": round(current_price * 0.92, 2),  # 8% below current
                "current_price": round(current_price, 2)
            },
            "position_sizing": {
                "initial_position": "25% of intended allocation",
                "scale_in_levels": [
                    f"25% at {round(optimal_entry, 2)}",
                    f"25% at {round(optimal_entry * 0.98, 2)}",
                    f"25% at {round(optimal_entry * 0.96, 2)}",
                    f"25% at {round(optimal_entry * 0.94, 2)}"
                ]
            },
            "rationale": """
            Strong technical indicators, positive fundamental metrics, and favorable ML predictions
            suggest a potential upside. The company's market position and growth prospects support
            a positive outlook. Consider accumulating on dips with a 3-6 month investment horizon.
            """,
            "risk_level": "Moderate",
            "stop_loss": round(current_price * 0.9, 2),  # 10% below current price
            "risk_reward_ratio": round((self._get_predictions()["price_targets"]["3_months"] - optimal_entry) / (optimal_entry - self._get_predictions()["price_targets"]["3_months"] * 0.9), 2)
        }

def generate_research_report(symbol: str) -> Dict[str, Any]:
    report = ResearchReport(symbol)
    return report.generate_report() 