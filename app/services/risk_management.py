from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.trading import Portfolio, Position, Trade
from app.core.config import settings

class RiskManagementService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_portfolio_risk(
        self,
        portfolio_id: int,
        lookback_days: int = 252
    ) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise ValueError(f"Portfolio with ID {portfolio_id} not found")

        # Get historical trades
        trades = self.db.query(Trade).filter(
            Trade.portfolio_id == portfolio_id,
            Trade.created_at >= datetime.utcnow() - pd.Timedelta(days=lookback_days)
        ).all()

        if not trades:
            return {}

        # Calculate returns
        returns = pd.Series([trade.pnl for trade in trades])
        
        # Calculate risk metrics
        metrics = {
            'volatility': self._calculate_volatility(returns),
            'var_95': self._calculate_var(returns, 0.95),
            'var_99': self._calculate_var(returns, 0.99),
            'cvar_95': self._calculate_cvar(returns, 0.95),
            'cvar_99': self._calculate_cvar(returns, 0.99),
            'max_drawdown': self._calculate_max_drawdown(returns),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'sortino_ratio': self._calculate_sortino_ratio(returns),
            'calmar_ratio': self._calculate_calmar_ratio(returns),
            'beta': self._calculate_beta(returns),
            'correlation': self._calculate_correlation(returns)
        }

        return metrics

    def calculate_position_risk(
        self,
        position_id: int
    ) -> Dict[str, float]:
        """Calculate risk metrics for a specific position"""
        position = self.db.query(Position).filter(Position.id == position_id).first()
        if not position:
            raise ValueError(f"Position with ID {position_id} not found")

        # Calculate position metrics
        metrics = {
            'unrealized_pnl': position.unrealized_pnl,
            'realized_pnl': position.realized_pnl,
            'total_pnl': position.unrealized_pnl + position.realized_pnl,
            'return': (position.unrealized_pnl + position.realized_pnl) / (position.quantity * position.average_price),
            'risk_exposure': position.quantity * position.current_price,
            'stop_loss_distance': (position.current_price - position.stop_loss) / position.current_price if position.stop_loss else None,
            'take_profit_distance': (position.take_profit - position.current_price) / position.current_price if position.take_profit else None
        }

        return metrics

    def calculate_portfolio_allocation(
        self,
        portfolio_id: int
    ) -> Dict[str, float]:
        """Calculate portfolio allocation metrics"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise ValueError(f"Portfolio with ID {portfolio_id} not found")

        positions = self.db.query(Position).filter(
            Position.portfolio_id == portfolio_id,
            Position.status == 'open'
        ).all()

        if not positions:
            return {}

        # Calculate total portfolio value
        total_value = sum(position.quantity * position.current_price for position in positions)

        # Calculate allocation
        allocation = {}
        for position in positions:
            position_value = position.quantity * position.current_price
            allocation[position.symbol] = position_value / total_value

        return allocation

    def calculate_risk_limits(
        self,
        portfolio_id: int
    ) -> Dict[str, float]:
        """Calculate risk limits for portfolio"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            raise ValueError(f"Portfolio with ID {portfolio_id} not found")

        # Get portfolio risk metrics
        risk_metrics = self.calculate_portfolio_risk(portfolio_id)

        # Calculate risk limits based on portfolio risk level
        risk_limits = {
            'max_position_size': self._calculate_max_position_size(portfolio),
            'max_drawdown_limit': self._calculate_max_drawdown_limit(portfolio),
            'var_limit': self._calculate_var_limit(portfolio),
            'leverage_limit': self._calculate_leverage_limit(portfolio),
            'concentration_limit': self._calculate_concentration_limit(portfolio)
        }

        return risk_limits

    def _calculate_volatility(self, returns: pd.Series) -> float:
        """Calculate annualized volatility"""
        return returns.std() * np.sqrt(252)

    def _calculate_var(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence) * 100)

    def _calculate_cvar(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Conditional Value at Risk"""
        var = self._calculate_var(returns, confidence)
        return returns[returns <= var].mean()

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate Maximum Drawdown"""
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns / rolling_max - 1
        return abs(drawdowns.min())

    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe Ratio"""
        excess_returns = returns - risk_free_rate/252
        if len(excess_returns) < 2:
            return 0.0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino Ratio"""
        excess_returns = returns - risk_free_rate/252
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) < 2:
            return 0.0
        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()

    def _calculate_calmar_ratio(self, returns: pd.Series) -> float:
        """Calculate Calmar Ratio"""
        annual_return = returns.mean() * 252
        max_drawdown = self._calculate_max_drawdown(returns)
        if max_drawdown == 0:
            return float('inf')
        return annual_return / max_drawdown

    def _calculate_beta(self, returns: pd.Series) -> float:
        """Calculate Beta"""
        # This is a placeholder - implement actual beta calculation
        # You would need market returns data
        return 1.0

    def _calculate_correlation(self, returns: pd.Series) -> float:
        """Calculate Correlation"""
        # This is a placeholder - implement actual correlation calculation
        # You would need market returns data
        return 0.0

    def _calculate_max_position_size(self, portfolio: Portfolio) -> float:
        """Calculate maximum position size based on risk level"""
        risk_multipliers = {
            'low': 0.05,
            'medium': 0.10,
            'high': 0.20
        }
        return portfolio.current_balance * risk_multipliers.get(portfolio.risk_level, 0.05)

    def _calculate_max_drawdown_limit(self, portfolio: Portfolio) -> float:
        """Calculate maximum drawdown limit based on risk level"""
        risk_multipliers = {
            'low': 0.10,
            'medium': 0.20,
            'high': 0.30
        }
        return risk_multipliers.get(portfolio.risk_level, 0.10)

    def _calculate_var_limit(self, portfolio: Portfolio) -> float:
        """Calculate VaR limit based on risk level"""
        risk_multipliers = {
            'low': 0.02,
            'medium': 0.05,
            'high': 0.10
        }
        return portfolio.current_balance * risk_multipliers.get(portfolio.risk_level, 0.02)

    def _calculate_leverage_limit(self, portfolio: Portfolio) -> float:
        """Calculate leverage limit based on risk level"""
        risk_multipliers = {
            'low': 1.0,
            'medium': 2.0,
            'high': 3.0
        }
        return risk_multipliers.get(portfolio.risk_level, 1.0)

    def _calculate_concentration_limit(self, portfolio: Portfolio) -> float:
        """Calculate concentration limit based on risk level"""
        risk_multipliers = {
            'low': 0.10,
            'medium': 0.20,
            'high': 0.30
        }
        return risk_multipliers.get(portfolio.risk_level, 0.10) 