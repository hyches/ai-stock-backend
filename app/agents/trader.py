# app/agents/trader.py

from app.agents.base import BaseAgent
from app.agents.analysts import TechnicalAnalyst, FundamentalAnalyst, SentimentAnalyst
from app.agents.researchers import BullResearcher, BearResearcher
import logging
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TraderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="TraderAgent", role="Final decision maker. Reconciles all inputs to make a trade recommendation.")
        
    async def decide(self, symbol: str, debate_summary: str) -> str:
        prompt = f"""
        As the Head Trader, you must make a final decision for {symbol} based on the following debate between your researchers:
        
        {debate_summary}
        
        Your decision must be one of: **BUY**, **SELL**, or **HOLD**.
        Provide:
        1. Final Decision (BUY/SELL/HOLD)
        2. Confidence level (0-100%)
        3. Primary reasoning for the decision
        4. Key risks to monitor
        """
        system_prompt = "You are the Chief Investment Officer. You are decisive, risk-aware, and prioritize capital preservation while seeking benchmark-beating returns."
        return await self.chat(system_prompt, prompt)

class AgentService:
    def __init__(self):
        self.tech_analyst = TechnicalAnalyst()
        self.fund_analyst = FundamentalAnalyst()
        self.sent_analyst = SentimentAnalyst()
        self.bull_researcher = BullResearcher()
        self.bear_researcher = BearResearcher()
        self.trader = TraderAgent()
        
    async def run_full_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Orchestrates the full multi-agent workflow.
        """
        logger.info(f"Starting multi-agent analysis for {symbol}")
        
        # 1. Run Analysts in parallel
        tech_task = self.tech_analyst.analyze(symbol)
        fund_task = self.fund_analyst.analyze(symbol)
        sent_task = self.sent_analyst.analyze(symbol)
        
        reports = await asyncio.gather(tech_task, fund_task, sent_task)
        analyst_reports_summary = f"""
        --- TECHNICAL REPORT ---
        {reports[0]}
        
        --- FUNDAMENTAL REPORT ---
        {reports[1]}
        
        --- SENTIMENT REPORT ---
        {reports[2]}
        """
        
        # 2. Run Researchers in parallel based on analyst reports
        bull_task = self.bull_researcher.research(symbol, analyst_reports_summary)
        bear_task = self.bear_researcher.research(symbol, analyst_reports_summary)
        
        cases = await asyncio.gather(bull_task, bear_task)
        debate_summary = f"""
        --- BULLISH CASE ---
        {cases[0]}
        
        --- BEARISH CASE ---
        {cases[1]}
        """
        
        # 3. Final decision from Trader
        final_decision = await self.trader.decide(symbol, debate_summary)
        
        return {
            "symbol": symbol,
            "analyst_reports": {
                "technical": reports[0],
                "fundamental": reports[1],
                "sentiment": reports[2]
            },
            "research_cases": {
                "bullish": cases[0],
                "bearish": cases[1]
            },
            "final_decision": final_decision
        }

agent_service = AgentService()
