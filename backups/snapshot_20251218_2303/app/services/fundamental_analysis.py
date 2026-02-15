from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.zerodha_service import ZerodhaService
from app.core.cache import redis_cache
import logging

logger = logging.getLogger(__name__)

class FundamentalAnalysis:
    """
    Provides methods for comprehensive fundamental analysis of stocks, including
    financial ratios, valuation, growth, quality, risk, industry comparison, and credit analysis.
    """
    def __init__(self) -> None:
        """
        Initialize FundamentalAnalysis with ZerodhaService and cache TTL.
        """
        self.zerodha_service = ZerodhaService()
        self.cache_ttl = 3600  # 1 hour

    async def get_comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive fundamental analysis for a given symbol.
        Args:
            symbol (str): Stock symbol.
        Returns:
            Dict[str, Any]: Dictionary containing various analysis metrics.
        """
        return {
            "financial_ratios": await self._calculate_financial_ratios(symbol),
            "valuation_metrics": await self._calculate_valuation_metrics(symbol),
            "growth_metrics": await self._calculate_growth_metrics(symbol),
            "quality_metrics": await self._calculate_quality_metrics(symbol),
            "risk_metrics": await self._calculate_risk_metrics(symbol),
            "industry_comparison": await self._get_industry_comparison(symbol),
            "credit_analysis": await self._perform_credit_analysis(symbol)
        }

    async def _calculate_financial_ratios(self, symbol: str) -> Dict[str, Any]:
        """
        Calculate key financial ratios for a given symbol.
        Args:
            symbol (str): Stock symbol.
        Returns:
            Dict[str, Any]: Dictionary of financial ratios.
        """
        try:
            # Get financial statements
            balance_sheet = await self._get_balance_sheet(symbol)
            income_stmt = await self._get_income_statement(symbol)
            cash_flow = await self._get_cash_flow(symbol)

            return {
                "liquidity_ratios": {
                    "current_ratio": self._calculate_current_ratio(balance_sheet),
                    "quick_ratio": self._calculate_quick_ratio(balance_sheet),
                    "cash_ratio": self._calculate_cash_ratio(balance_sheet)
                },
                "profitability_ratios": {
                    "gross_margin": self._calculate_gross_margin(income_stmt),
                    "operating_margin": self._calculate_operating_margin(income_stmt),
                    "net_margin": self._calculate_net_margin(income_stmt),
                    "roa": self._calculate_roa(income_stmt, balance_sheet),
                    "roe": self._calculate_roe(income_stmt, balance_sheet),
                    "roic": self._calculate_roic(income_stmt, balance_sheet)
                },
                "efficiency_ratios": {
                    "asset_turnover": self._calculate_asset_turnover(income_stmt, balance_sheet),
                    "inventory_turnover": self._calculate_inventory_turnover(income_stmt, balance_sheet),
                    "receivables_turnover": self._calculate_receivables_turnover(income_stmt, balance_sheet)
                },
                "leverage_ratios": {
                    "debt_to_equity": self._calculate_debt_to_equity(balance_sheet),
                    "debt_to_assets": self._calculate_debt_to_assets(balance_sheet),
                    "interest_coverage": self._calculate_interest_coverage(income_stmt)
                }
            }
        except Exception as e:
            logger.error("Error calculating financial ratios: %s", str(e))
            return {}

    async def _calculate_valuation_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        Calculate valuation metrics for a given symbol.
        Args:
            symbol (str): Stock symbol.
        Returns:
            Dict[str, Any]: Dictionary of valuation metrics.
        """
        try:
            market_data = await self._get_market_data(symbol)
            financials = await self._get_financial_statements(symbol)

            return {
                "price_metrics": {
                    "pe_ratio": self._calculate_pe_ratio(market_data, financials),
                    "forward_pe": self._calculate_forward_pe(market_data, financials),
                    "peg_ratio": self._calculate_peg_ratio(market_data, financials),
                    "price_to_book": self._calculate_price_to_book(market_data, financials),
                    "price_to_sales": self._calculate_price_to_sales(market_data, financials)
                },
                "enterprise_value_metrics": {
                    "ev_to_ebitda": self._calculate_ev_to_ebitda(market_data, financials),
                    "ev_to_sales": self._calculate_ev_to_sales(market_data, financials),
                    "ev_to_ebit": self._calculate_ev_to_ebit(market_data, financials)
                },
                "dividend_metrics": {
                    "dividend_yield": self._calculate_dividend_yield(market_data, financials),
                    "payout_ratio": self._calculate_payout_ratio(financials),
                    "dividend_growth": self._calculate_dividend_growth(financials)
                }
            }
        except Exception as e:
            logger.error("Error calculating valuation metrics: %s", str(e))
            return {}

    async def _calculate_growth_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        Calculate growth metrics for a given symbol.
        Args:
            symbol (str): Stock symbol.
        Returns:
            Dict[str, Any]: Dictionary of growth metrics.
        """
        try:
            financials = await self._get_financial_statements(symbol)
            
            return {
                "revenue_growth": self._calculate_revenue_growth(financials),
                "earnings_growth": self._calculate_earnings_growth(financials),
                "free_cash_flow_growth": self._calculate_fcf_growth(financials),
                "book_value_growth": self._calculate_book_value_growth(financials),
                "dividend_growth": self._calculate_dividend_growth(financials)
            }
        except Exception as e:
            logger.error("Error calculating growth metrics: %s", str(e))
            return {}

    async def _calculate_quality_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        Calculate quality metrics for a given symbol.
        Args:
            symbol (str): Stock symbol.
        Returns:
            Dict[str, Any]: Dictionary of quality metrics.
        """
        try:
            financials = await self._get_financial_statements(symbol)
            
            return {
                "earnings_quality": {
                    "accruals_ratio": self._calculate_accruals_ratio(financials),
                    "earnings_persistence": self._calculate_earnings_persistence(financials),
                    "earnings_smoothness": self._calculate_earnings_smoothness(financials)
                },
                "business_quality": {
                    "gross_margin_stability": self._calculate_margin_stability(financials),
                    "asset_turnover_stability": self._calculate_turnover_stability(financials),
                    "capital_efficiency": self._calculate_capital_efficiency(financials)
                },
                "management_quality": {
                    "capital_allocation": self._calculate_capital_allocation(financials),
                    "investment_efficiency": self._calculate_investment_efficiency(financials),
                    "working_capital_management": self._calculate_wc_management(financials)
                }
            }
        except Exception as e:
            logger.error("Error calculating quality metrics: %s", str(e))
            return {}

    async def _calculate_risk_metrics(self, symbol: str) -> Dict[str, Any]:
        """
        Calculate risk metrics for a given symbol.
        Args:
            symbol (str): Stock symbol.
        Returns:
            Dict[str, Any]: Dictionary of risk metrics.
        """
        try:
            market_data = await self._get_market_data(symbol)
            financials = await self._get_financial_statements(symbol)
            
            return {
                "market_risk": {
                    "beta": self._calculate_beta(market_data),
                    "volatility": self._calculate_volatility(market_data),
                    "value_at_risk": self._calculate_var(market_data)
                },
                "financial_risk": {
                    "leverage_ratio": self._calculate_leverage_ratio(financials),
                    "interest_coverage": self._calculate_interest_coverage(financials),
                    "debt_service_coverage": self._calculate_debt_service_coverage(financials)
                },
                "business_risk": {
                    "operating_leverage": self._calculate_operating_leverage(financials),
                    "business_concentration": self._calculate_business_concentration(financials),
                    "geographic_concentration": self._calculate_geographic_concentration(financials)
                }
            }
        except Exception as e:
            logger.error("Error calculating risk metrics: %s", str(e))
            return {}

    async def _perform_credit_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Perform credit analysis for a given symbol.
        Args:
            symbol (str): Stock symbol.
        Returns:
            Dict[str, Any]: Dictionary of credit analysis metrics.
        """
        try:
            financials = await self._get_financial_statements(symbol)
            
            return {
                "credit_ratios": {
                    "interest_coverage": self._calculate_interest_coverage(financials),
                    "debt_service_coverage": self._calculate_debt_service_coverage(financials),
                    "debt_to_ebitda": self._calculate_debt_to_ebitda(financials),
                    "net_debt_to_ebitda": self._calculate_net_debt_to_ebitda(financials)
                },
                "liquidity_analysis": {
                    "current_ratio": self._calculate_current_ratio(financials),
                    "quick_ratio": self._calculate_quick_ratio(financials),
                    "cash_ratio": self._calculate_cash_ratio(financials),
                    "working_capital_ratio": self._calculate_working_capital_ratio(financials)
                },
                "cash_flow_analysis": {
                    "operating_cash_flow_ratio": self._calculate_operating_cash_flow_ratio(financials),
                    "free_cash_flow_ratio": self._calculate_free_cash_flow_ratio(financials),
                    "cash_flow_coverage": self._calculate_cash_flow_coverage(financials)
                }
            }
        except Exception as e:
            logger.error("Error performing credit analysis: %s", str(e))
            return {}

    # Helper methods for calculations
    def _calculate_current_ratio(self, balance_sheet: pd.DataFrame) -> float:
        """
        Calculate current ratio.
        Args:
            balance_sheet (pd.DataFrame): Balance sheet dataframe.
        Returns:
            float: Current ratio.
        """
        current_assets = balance_sheet['total_current_assets']
        current_liabilities = balance_sheet['total_current_liabilities']
        return current_assets / current_liabilities

    def _calculate_quick_ratio(self, balance_sheet: pd.DataFrame) -> float:
        """
        Calculate quick ratio.
        Args:
            balance_sheet (pd.DataFrame): Balance sheet dataframe.
        Returns:
            float: Quick ratio.
        """
        current_assets = balance_sheet['total_current_assets']
        inventory = balance_sheet['inventory']
        current_liabilities = balance_sheet['total_current_liabilities']
        return (current_assets - inventory) / current_liabilities

    # Add more calculation methods for other metrics...

fundamental_analysis = FundamentalAnalysis() 