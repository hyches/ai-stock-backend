# app/agents/researchers.py

from app.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class BullResearcher(BaseAgent):
    def __init__(self):
        super().__init__(name="BullResearcher", role="Finds reasons to be optimistic and identifies growth opportunities.")
        
    async def research(self, symbol: str, analyst_reports: str) -> str:
        prompt = f"""
        Based on these analyst reports for {symbol}:
        {analyst_reports}
        
        Construct the strongest possible **BULLISH** case. 
        Focus on:
        1. Positive catalysts mentioned by analysts.
        2. Undiscovered growth potential or undervalued strengths.
        3. Why the bearish risks might be overstated.
        4. Target upside potential.
        """
        system_prompt = "You are a perma-bull researcher. Your job is to find the silver lining and justify a long position."
        return await self.chat(system_prompt, prompt)

class BearResearcher(BaseAgent):
    def __init__(self):
        super().__init__(name="BearResearcher", role="Identifies risks, red flags, and reasons for caution.")
        
    async def research(self, symbol: str, analyst_reports: str) -> str:
        prompt = f"""
        Based on these analyst reports for {symbol}:
        {analyst_reports}
        
        Construct the strongest possible **BEARISH** case.
        Focus on:
        1. Risks, red flags, and negative trends identified.
        2. Why the bullish assumptions might be flawed or overly optimistic.
        3. Potential downside scenarios and macro headwinds.
        4. Reasons to stay out or sell.
        """
        system_prompt = "You are a conservative bear researcher. Your job is to find the flaws and protect the portfolio from risk."
        return await self.chat(system_prompt, prompt)
