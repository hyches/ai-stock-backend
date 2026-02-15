"""
Tax Calculator for Indian Markets (STCG/LTCG)
=============================================
Computes Short-Term and Long-Term Capital Gains based on holding period.
"""

import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TaxCalculator:
    """
    Calculates tax liability for equity trades.
    Note: Rules are specific to Indian Equity Markets.
    - LTCG: Holding period > 1 year (12 months)
    - STCG: Holding period <= 1 year
    """
    
    def __init__(self, stcg_rate: float = 0.15, ltcg_rate: float = 0.10):
        self.stcg_rate = stcg_rate
        self.ltcg_rate = ltcg_rate
        self.ltcg_exemption = 100000 # 1 Lakh exemption on LTCG

    def calculate_tax(self, closed_trades: List[Dict]) -> Dict[str, Any]:
        """
        Calculates STCG and LTCG for a list of trades.
        Each trade should have: symbol, buy_price, sell_price, quantity, buy_date, sell_date.
        """
        stcg_total = 0.0
        ltcg_total = 0.0
        
        details = []
        
        for trade in closed_trades:
            buy_date = pd.to_datetime(trade['buy_date'])
            sell_date = pd.to_datetime(trade['sell_date'])
            holding_period = (sell_date - buy_date).days
            
            profit = (trade['sell_price'] - trade['buy_price']) * trade['quantity']
            
            is_long_term = holding_period > 365
            
            tax_type = "LTCG" if is_long_term else "STCG"
            if is_long_term:
                ltcg_total += profit
            else:
                stcg_total += profit
                
            details.append({
                "symbol": trade['symbol'],
                "profit": profit,
                "holding_days": holding_period,
                "type": tax_type
            })
            
        # Final tax estimation (simplified)
        stcg_tax = max(0, stcg_total * self.stcg_rate)
        # LTCG has 1L exemption
        ltcg_taxable = max(0, ltcg_total - self.ltcg_exemption)
        ltcg_tax = ltcg_taxable * self.ltcg_rate
        
        return {
            "summary": {
                "total_stcg": stcg_total,
                "total_ltcg": ltcg_total,
                "stcg_tax_est": stcg_tax,
                "ltcg_tax_est": ltcg_tax,
                "total_tax_est": stcg_tax + ltcg_tax
            },
            "trade_details": details
        }

# Singleton
tax_calculator = TaxCalculator()
