# app/agents/analysts.py

from app.agents.base import BaseAgent
from app.services.technical_analysis import technical_analysis
from app.services.fundamental_analysis import fundamental_analysis
from app.services.sentiment_analysis import sentiment_analysis
import json
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyst(BaseAgent):
    def __init__(self):
        super().__init__(name="TechnicalAnalyst", role="Analyzes chart patterns, indicators, and price action.")
        
    async def analyze(self, symbol: str) -> str:
        data = await technical_analysis.get_comprehensive_analysis(symbol)
        prompt = f"""
        Analyze the technical indicators for {symbol}:
        {json.dumps(data, indent=2, default=str)}
        
        Provide a concise report on:
        1. Current trend (Uptrend/Downtrend/Sideways)
        2. Key support and resistance levels
        3. Momentum (RSI/MACD status)
        4. Volatility regime
        5. A finalized recommendation: BULLISH, BEARISH, or NEUTRAL.
        """
        system_prompt = "You are a professional Technical Analyst at a top-tier trading firm. Be objective and precise."
        return await self.chat(system_prompt, prompt)

class FundamentalAnalyst(BaseAgent):
    def __init__(self):
        super().__init__(name="FundamentalAnalyst", role="Analyzes company financials, valuation, and growth.")
        
    async def analyze(self, symbol: str) -> str:
        data = await fundamental_analysis.get_comprehensive_analysis(symbol)
        prompt = f"""
        Analyze the fundamental health of {symbol}:
        {json.dumps(data, indent=2, default=str)}
        
        Provide a concise report on:
        1. Valuation (PE/PB vs industry)
        2. Profitability (Margins, ROE)
        3. Financial health (Debt levels, Liquidity)
        4. Growth prospects
        5. A finalized recommendation: BULLISH, BEARISH, or NEUTRAL.
        """
        system_prompt = "You are an expert Fundamental Analyst. Focus on intrinsic value and long-term sustainability."
        return await self.chat(system_prompt, prompt)

class SentimentAnalyst(BaseAgent):
    def __init__(self):
        super().__init__(name="SentimentAnalyst", role="Analyzes news, social media, and market mood.")
        
    async def analyze(self, symbol: str) -> str:
        data = await sentiment_analysis.get_comprehensive_sentiment(symbol)
        prompt = f"""
        Analyze the market sentiment for {symbol}:
        {json.dumps(data, indent=2, default=str)}
        
        Provide a concise report on:
        1. News sentiment score and key topics
        2. Social media buzz (Twitter/Reddit/Stocktwits)
        3. Institutional vs Retail sentiment
        4. Option market sentiment (Put/Call ratios)
        5. A finalized recommendation: BULLISH, BEARISH, or NEUTRAL.
        """
        system_prompt = "You are a Sentiment Expert. Gauge the 'mood' of the market and identify potential shifts in perception."
        return await self.chat(system_prompt, prompt)
