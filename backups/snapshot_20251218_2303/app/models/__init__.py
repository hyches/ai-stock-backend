"""
Database models for the AI Stock Portfolio Platform Backend.

This subpackage defines SQLAlchemy ORM models for users, trading, alerts, portfolios, reports, and other core entities.
"""

# Import all SQLAlchemy models to ensure they are registered
from .user import User
from .database import Stock, Portfolio, PortfolioWeight
from .trading import Strategy, Position, Trade, Signal
from .alert import Alert
from .report import Report
from .zerodha import ZerodhaToken, PaperTrade

__all__ = [
    "User",
    "Stock", 
    "Portfolio",
    "PortfolioWeight",
    "Strategy",
    "Position", 
    "Trade",
    "Signal",
    "Alert",
    "Report",
    "ZerodhaToken",
    "PaperTrade"
] 