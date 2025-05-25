import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from app.utils.data_fetcher import DataFetcher
from app.core.config import settings

class RiskManager:
    def __init__(self):
        self.data_fetcher = DataFetcher()

    def calculate_position_size(self, portfolio_value: float, symbol: str, risk_per_trade: float = 0.02) -> Tuple[int, float, float]:
        """
        Calculate position size based on portfolio value and risk parameters
        Returns: (quantity, stop_loss, take_profit)
        """
        # Get current price and volatility
        data = self.data_fetcher.get_historical_data(symbol)
        if data.empty:
            return 0, 0, 0

        current_price = data['close'].iloc[-1]
        atr = self._calculate_atr(data)
        
        # Calculate stop loss and take profit levels
        stop_loss_pct = atr * 2  # 2 ATR for stop loss
        take_profit_pct = atr * 3  # 3 ATR for take profit
        
        stop_loss = current_price * (1 - stop_loss_pct)
        take_profit = current_price * (1 + take_profit_pct)
        
        # Calculate position size
        risk_amount = portfolio_value * risk_per_trade
        position_size = risk_amount / (current_price - stop_loss)
        
        # Round to nearest whole number
        quantity = int(position_size)
        
        return quantity, stop_loss, take_profit

    def calculate_portfolio_risk(self, positions: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate portfolio risk metrics
        """
        if not positions:
            return {
                "total_value": 0,
                "total_risk": 0,
                "var_95": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0
            }

        # Calculate total portfolio value
        total_value = sum(pos["quantity"] * pos["current_price"] for pos in positions)
        
        # Calculate portfolio returns
        returns = []
        for pos in positions:
            if "historical_prices" in pos:
                returns.extend(np.diff(np.log(pos["historical_prices"])))
        
        if not returns:
            return {
                "total_value": total_value,
                "total_risk": 0,
                "var_95": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0
            }
        
        # Calculate risk metrics
        returns = np.array(returns)
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        var_95 = np.percentile(returns, 5) * np.sqrt(252)  # 95% VaR
        
        # Calculate maximum drawdown
        cumulative_returns = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        # Calculate Sharpe ratio
        risk_free_rate = 0.02  # 2% risk-free rate
        excess_returns = returns - risk_free_rate/252
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
        return {
            "total_value": total_value,
            "total_risk": volatility,
            "var_95": var_95,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio
        }

    def calculate_correlation_matrix(self, symbols: List[str]) -> pd.DataFrame:
        """
        Calculate correlation matrix for a list of symbols
        """
        # Get historical data for all symbols
        data = {}
        for symbol in symbols:
            hist_data = self.data_fetcher.get_historical_data(symbol)
            if not hist_data.empty:
                data[symbol] = hist_data['close']
        
        # Create DataFrame with all prices
        df = pd.DataFrame(data)
        
        # Calculate returns
        returns = df.pct_change().dropna()
        
        # Calculate correlation matrix
        corr_matrix = returns.corr()
        
        return corr_matrix

    def calculate_position_limits(self, portfolio_value: float, symbol: str, risk_level: str = "medium") -> Dict[str, float]:
        """
        Calculate position limits based on portfolio value and risk level
        """
        # Define risk parameters based on risk level
        risk_params = {
            "low": {
                "max_position_size": 0.05,  # 5% of portfolio
                "max_sector_exposure": 0.15,  # 15% of portfolio
                "max_leverage": 1.0
            },
            "medium": {
                "max_position_size": 0.10,  # 10% of portfolio
                "max_sector_exposure": 0.25,  # 25% of portfolio
                "max_leverage": 1.5
            },
            "high": {
                "max_position_size": 0.20,  # 20% of portfolio
                "max_sector_exposure": 0.40,  # 40% of portfolio
                "max_leverage": 2.0
            }
        }
        
        params = risk_params.get(risk_level, risk_params["medium"])
        
        return {
            "max_position_value": portfolio_value * params["max_position_size"],
            "max_sector_value": portfolio_value * params["max_sector_exposure"],
            "max_leverage": params["max_leverage"]
        }

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Average True Range
        """
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(window=period).mean().iloc[-1]
        return atr 