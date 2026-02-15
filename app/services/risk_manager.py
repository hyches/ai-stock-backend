"""
Risk Management Suite
Portfolio VaR, position sizing, correlation analysis, and drawdown monitoring
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from scipy import stats
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Portfolio position"""
    symbol: str
    quantity: int
    average_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float


@dataclass
class PortfolioMetrics:
    """Portfolio risk metrics"""
    total_value: float
    cash: float
    positions_value: float
    total_pnl: float
    total_pnl_pct: float
    var_95: float  # 95% Value at Risk
    var_99: float  # 99% Value at Risk
    cvar_95: float  # Conditional VaR (Expected Shortfall)
    max_drawdown: float
    current_drawdown: float
    sharpe_ratio: float
    beta: float
    volatility: float


class RiskManager:
    """
    Professional risk management system
    """
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.historical_values: List[Tuple[datetime, float]] = []
        self.peak_value = initial_capital
        self.max_drawdown = 0.0
    
    def calculate_var(
        self,
        returns: np.ndarray,
        confidence: float = 0.95,
        method: str = "historical"
    ) -> float:
        """
        Calculate Value at Risk
        
        Args:
            returns: Array of portfolio returns
            confidence: Confidence level (0.95 for 95%)
            method: "historical", "parametric", or "monte_carlo"
        
        Returns:
            VaR value (positive number representing potential loss)
        """
        if len(returns) == 0:
            return 0.0
        
        if method == "historical":
            # Historical VaR
            var = np.percentile(returns, (1 - confidence) * 100)
            return abs(var)
        
        elif method == "parametric":
            # Parametric VaR (assumes normal distribution)
            mean = np.mean(returns)
            std = np.std(returns)
            z_score = stats.norm.ppf(1 - confidence)
            var = mean + z_score * std
            return abs(var)
        
        elif method == "monte_carlo":
            # Monte Carlo VaR
            simulated_returns = self._monte_carlo_simulation(returns, n_simulations=10000)
            var = np.percentile(simulated_returns, (1 - confidence) * 100)
            return abs(var)
        
        return 0.0
    
    def calculate_cvar(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Calculate Conditional VaR (Expected Shortfall)
        Average loss beyond VaR threshold
        
        Args:
            returns: Array of portfolio returns
            confidence: Confidence level
        
        Returns:
            CVaR value
        """
        if len(returns) == 0:
            return 0.0
        
        var_threshold = np.percentile(returns, (1 - confidence) * 100)
        tail_losses = returns[returns <= var_threshold]
        
        if len(tail_losses) == 0:
            return 0.0
        
        cvar = np.mean(tail_losses)
        return abs(cvar)
    
    def _monte_carlo_simulation(
        self,
        returns: np.ndarray,
        n_simulations: int = 10000,
        horizon: int = 1
    ) -> np.ndarray:
        """
        Monte Carlo simulation for VaR
        
        Args:
            returns: Historical returns
            n_simulations: Number of simulations
            horizon: Time horizon (days)
        
        Returns:
            Array of simulated returns
        """
        mean = np.mean(returns)
        std = np.std(returns)
        
        # Generate random returns
        simulated = np.random.normal(mean, std, (n_simulations, horizon))
        
        # Compound returns over horizon
        cumulative_returns = np.prod(1 + simulated, axis=1) - 1
        
        return cumulative_returns
    
    def calculate_position_size_kelly(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        max_risk_pct: float = 0.25
    ) -> float:
        """
        Kelly Criterion for position sizing
        
        Args:
            win_rate: Probability of winning (0-1)
            avg_win: Average win amount
            avg_loss: Average loss amount
            max_risk_pct: Maximum risk percentage (cap Kelly)
        
        Returns:
            Optimal position size as fraction of capital
        """
        if avg_loss == 0:
            return 0.0
        
        # Kelly formula: f = (p * b - q) / b
        # where p = win rate, q = loss rate, b = win/loss ratio
        b = avg_win / avg_loss
        q = 1 - win_rate
        
        kelly_fraction = (win_rate * b - q) / b
        
        # Cap at max_risk_pct (fractional Kelly)
        kelly_fraction = max(0, min(kelly_fraction, max_risk_pct))
        
        return kelly_fraction
    
    def calculate_position_size_fixed_fractional(
        self,
        capital: float,
        risk_per_trade_pct: float,
        entry_price: float,
        stop_loss_price: float
    ) -> int:
        """
        Fixed fractional position sizing
        
        Args:
            capital: Available capital
            risk_per_trade_pct: Risk percentage per trade (e.g., 2.0 for 2%)
            entry_price: Entry price
            stop_loss_price: Stop loss price
        
        Returns:
            Position size in shares
        """
        if entry_price == 0 or entry_price == stop_loss_price:
            return 0
        
        risk_amount = capital * (risk_per_trade_pct / 100)
        risk_per_share = abs(entry_price - stop_loss_price)
        
        position_size = int(risk_amount / risk_per_share)
        
        return position_size
    
    def calculate_position_size_volatility(
        self,
        capital: float,
        target_volatility: float,
        asset_volatility: float,
        current_price: float
    ) -> int:
        """
        Volatility-based position sizing
        
        Args:
            capital: Available capital
            target_volatility: Target portfolio volatility (annualized)
            asset_volatility: Asset volatility (annualized)
            current_price: Current asset price
        
        Returns:
            Position size in shares
        """
        if asset_volatility == 0 or current_price == 0:
            return 0
        
        # Position value = (Target Vol / Asset Vol) * Capital
        position_value = (target_volatility / asset_volatility) * capital
        position_size = int(position_value / current_price)
        
        return position_size
    
    def calculate_correlation_matrix(
        self,
        price_data: Dict[str, pd.Series]
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for portfolio holdings
        
        Args:
            price_data: Dictionary of symbol -> price series
        
        Returns:
            Correlation matrix DataFrame
        """
        if not price_data:
            return pd.DataFrame()
        
        # Calculate returns
        returns_data = {}
        for symbol, prices in price_data.items():
            returns_data[symbol] = prices.pct_change().dropna()
        
        # Create DataFrame
        returns_df = pd.DataFrame(returns_data)
        
        # Calculate correlation
        corr_matrix = returns_df.corr()
        
        return corr_matrix
    
    def calculate_portfolio_concentration(self, positions: Dict[str, Position]) -> Dict[str, float]:
        """
        Calculate portfolio concentration metrics
        
        Args:
            positions: Dictionary of positions
        
        Returns:
            Dictionary with concentration metrics
        """
        if not positions:
            return {'herfindahl_index': 0, 'max_position_pct': 0, 'top_5_concentration': 0}
        
        total_value = sum(p.market_value for p in positions.values())
        
        if total_value == 0:
            return {'herfindahl_index': 0, 'max_position_pct': 0, 'top_5_concentration': 0}
        
        # Calculate position weights
        weights = [p.market_value / total_value for p in positions.values()]
        
        # Herfindahl-Hirschman Index (HHI)
        hhi = sum(w ** 2 for w in weights)
        
        # Max position percentage
        max_position_pct = max(weights) * 100
        
        # Top 5 concentration
        sorted_weights = sorted(weights, reverse=True)
        top_5_concentration = sum(sorted_weights[:5]) * 100
        
        return {
            'herfindahl_index': hhi,
            'max_position_pct': max_position_pct,
            'top_5_concentration': top_5_concentration,
            'num_positions': len(positions)
        }
    
    def calculate_drawdown(self, equity_curve: pd.Series) -> Tuple[float, float, pd.Series]:
        """
        Calculate drawdown metrics
        
        Args:
            equity_curve: Series of portfolio values over time
        
        Returns:
            Tuple of (max_drawdown, current_drawdown, drawdown_series)
        """
        if len(equity_curve) == 0:
            return 0.0, 0.0, pd.Series()
        
        # Calculate running maximum
        running_max = equity_curve.expanding().max()
        
        # Calculate drawdown
        drawdown = (equity_curve - running_max) / running_max
        
        # Max drawdown
        max_drawdown = drawdown.min()
        
        # Current drawdown
        current_drawdown = drawdown.iloc[-1]
        
        return abs(max_drawdown), abs(current_drawdown), drawdown
    
    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Trading periods per year (252 for daily)
        
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        # Annualize returns and volatility
        excess_returns = returns.mean() * periods_per_year - risk_free_rate
        volatility = returns.std() * np.sqrt(periods_per_year)
        
        sharpe = excess_returns / volatility
        
        return sharpe
    
    def calculate_beta(
        self,
        asset_returns: pd.Series,
        market_returns: pd.Series
    ) -> float:
        """
        Calculate beta (systematic risk)
        
        Args:
            asset_returns: Asset returns
            market_returns: Market/benchmark returns
        
        Returns:
            Beta value
        """
        if len(asset_returns) == 0 or len(market_returns) == 0:
            return 0.0
        
        # Align series
        aligned = pd.DataFrame({
            'asset': asset_returns,
            'market': market_returns
        }).dropna()
        
        if len(aligned) < 2:
            return 0.0
        
        # Calculate covariance and variance
        covariance = aligned['asset'].cov(aligned['market'])
        market_variance = aligned['market'].var()
        
        if market_variance == 0:
            return 0.0
        
        beta = covariance / market_variance
        
        return beta
    
    def get_portfolio_metrics(
        self,
        positions: Dict[str, Position],
        cash: float,
        historical_returns: pd.Series,
        market_returns: Optional[pd.Series] = None
    ) -> PortfolioMetrics:
        """
        Calculate comprehensive portfolio metrics
        
        Args:
            positions: Current positions
            cash: Available cash
            historical_returns: Historical portfolio returns
            market_returns: Market benchmark returns (optional)
        
        Returns:
            PortfolioMetrics object
        """
        # Calculate total values
        positions_value = sum(p.market_value for p in positions.values())
        total_value = positions_value + cash
        total_pnl = sum(p.unrealized_pnl for p in positions.values())
        total_pnl_pct = (total_pnl / self.initial_capital * 100) if self.initial_capital > 0 else 0
        
        # Calculate VaR
        var_95 = self.calculate_var(historical_returns.values, confidence=0.95) * total_value
        var_99 = self.calculate_var(historical_returns.values, confidence=0.99) * total_value
        cvar_95 = self.calculate_cvar(historical_returns.values, confidence=0.95) * total_value
        
        # Calculate drawdown
        equity_curve = pd.Series([total_value])  # Simplified
        max_dd, current_dd, _ = self.calculate_drawdown(equity_curve)
        
        # Calculate Sharpe ratio
        sharpe = self.calculate_sharpe_ratio(historical_returns)
        
        # Calculate beta
        beta = 0.0
        if market_returns is not None:
            beta = self.calculate_beta(historical_returns, market_returns)
        
        # Calculate volatility
        volatility = historical_returns.std() * np.sqrt(252) if len(historical_returns) > 0 else 0.0
        
        return PortfolioMetrics(
            total_value=total_value,
            cash=cash,
            positions_value=positions_value,
            total_pnl=total_pnl,
            total_pnl_pct=total_pnl_pct,
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            max_drawdown=max_dd,
            current_drawdown=current_dd,
            sharpe_ratio=sharpe,
            beta=beta,
            volatility=volatility
        )
    
    def check_risk_limits(
        self,
        position_size: float,
        total_portfolio_value: float,
        max_position_pct: float = 10.0,
        max_sector_pct: float = 30.0
    ) -> Tuple[bool, str]:
        """
        Check if trade violates risk limits
        
        Args:
            position_size: Proposed position size
            total_portfolio_value: Total portfolio value
            max_position_pct: Maximum single position percentage
            max_sector_pct: Maximum sector concentration
        
        Returns:
            Tuple of (is_valid, reason)
        """
        if total_portfolio_value == 0:
            return False, "Portfolio value is zero"
        
        position_pct = (position_size / total_portfolio_value) * 100
        
        if position_pct > max_position_pct:
            return False, f"Position size {position_pct:.1f}% exceeds limit {max_position_pct}%"
        
        return True, "OK"
    
    def suggest_hedge_ratio(
        self,
        portfolio_beta: float,
        target_beta: float = 0.0
    ) -> float:
        """
        Suggest hedge ratio to achieve target beta
        
        Args:
            portfolio_beta: Current portfolio beta
            target_beta: Desired beta (0 for market neutral)
        
        Returns:
            Hedge ratio (fraction of portfolio to hedge)
        """
        if portfolio_beta == 0:
            return 0.0
        
        hedge_ratio = (portfolio_beta - target_beta) / portfolio_beta
        
        return max(0, min(hedge_ratio, 1))  # Clamp between 0 and 1


# Singleton instance
risk_manager = RiskManager()
