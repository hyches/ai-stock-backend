import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from app.utils.data_fetcher import DataFetcher
from app.utils.risk_management import RiskManager
from app.core.config import settings

class PortfolioManager:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.risk_manager = RiskManager()

    def rebalance_portfolio(self, portfolio: Dict[str, Any], target_weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Rebalance portfolio to target weights
        Returns list of trades needed to rebalance
        """
        current_positions = portfolio.get("positions", [])
        portfolio_value = portfolio.get("current_balance", 0)
        
        # Calculate current weights
        current_weights = {}
        for pos in current_positions:
            current_weights[pos["symbol"]] = (pos["quantity"] * pos["current_price"]) / portfolio_value
        
        # Calculate target positions
        target_positions = {}
        for symbol, weight in target_weights.items():
            target_value = portfolio_value * weight
            current_price = self.data_fetcher.get_current_price(symbol)
            if current_price:
                target_positions[symbol] = int(target_value / current_price)
        
        # Calculate trades needed
        trades = []
        for symbol, target_quantity in target_positions.items():
            current_position = next((pos for pos in current_positions if pos["symbol"] == symbol), None)
            current_quantity = current_position["quantity"] if current_position else 0
            
            if target_quantity != current_quantity:
                trades.append({
                    "symbol": symbol,
                    "action": "buy" if target_quantity > current_quantity else "sell",
                    "quantity": abs(target_quantity - current_quantity),
                    "current_price": self.data_fetcher.get_current_price(symbol)
                })
        
        return trades

    def optimize_portfolio(self, symbols: List[str], risk_level: str = "medium") -> Dict[str, float]:
        """
        Optimize portfolio weights using Modern Portfolio Theory
        """
        # Get historical data
        data = {}
        for symbol in symbols:
            hist_data = self.data_fetcher.get_historical_data(symbol)
            if not hist_data.empty:
                data[symbol] = hist_data['close']
        
        if not data:
            return {}
        
        # Calculate returns
        df = pd.DataFrame(data)
        returns = df.pct_change().dropna()
        
        # Calculate mean returns and covariance matrix
        mean_returns = returns.mean()
        cov_matrix = returns.cov()
        
        # Generate random portfolios
        num_portfolios = 1000
        results = []
        
        for _ in range(num_portfolios):
            weights = np.random.random(len(symbols))
            weights = weights / np.sum(weights)
            
            portfolio_return = np.sum(mean_returns * weights)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            results.append({
                "weights": weights,
                "return": portfolio_return,
                "risk": portfolio_risk,
                "sharpe": portfolio_return / portfolio_risk
            })
        
        # Find optimal portfolio based on risk level
        if risk_level == "low":
            optimal_portfolio = max(results, key=lambda x: x["sharpe"])
        elif risk_level == "high":
            optimal_portfolio = max(results, key=lambda x: x["return"])
        else:  # medium
            optimal_portfolio = max(results, key=lambda x: x["sharpe"])
        
        # Convert weights to dictionary
        weights_dict = {symbol: weight for symbol, weight in zip(symbols, optimal_portfolio["weights"])}
        
        return weights_dict

    def calculate_portfolio_metrics(self, portfolio: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate portfolio performance metrics
        """
        positions = portfolio.get("positions", [])
        if not positions:
            return {
                "total_value": 0,
                "total_return": 0,
                "daily_return": 0,
                "volatility": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0
            }
        
        # Calculate total portfolio value
        total_value = sum(pos["quantity"] * pos["current_price"] for pos in positions)
        
        # Calculate returns
        returns = []
        for pos in positions:
            if "historical_prices" in pos:
                returns.extend(np.diff(np.log(pos["historical_prices"])))
        
        if not returns:
            return {
                "total_value": total_value,
                "total_return": 0,
                "daily_return": 0,
                "volatility": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0
            }
        
        returns = np.array(returns)
        
        # Calculate metrics
        total_return = np.prod(1 + returns) - 1
        daily_return = np.mean(returns)
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        
        # Calculate Sharpe ratio
        risk_free_rate = 0.02  # 2% risk-free rate
        excess_returns = returns - risk_free_rate/252
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
        # Calculate maximum drawdown
        cumulative_returns = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        return {
            "total_value": total_value,
            "total_return": total_return,
            "daily_return": daily_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown
        }

    def calculate_position_metrics(self, position: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate individual position metrics
        """
        if not position or "historical_prices" not in position:
            return {
                "current_value": 0,
                "unrealized_pnl": 0,
                "realized_pnl": 0,
                "total_return": 0,
                "daily_return": 0,
                "volatility": 0
            }
        
        current_price = position["current_price"]
        quantity = position["quantity"]
        average_price = position["average_price"]
        
        # Calculate current value and P&L
        current_value = quantity * current_price
        unrealized_pnl = (current_price - average_price) * quantity
        
        # Calculate returns
        returns = np.diff(np.log(position["historical_prices"]))
        
        return {
            "current_value": current_value,
            "unrealized_pnl": unrealized_pnl,
            "realized_pnl": position.get("realized_pnl", 0),
            "total_return": np.prod(1 + returns) - 1 if len(returns) > 0 else 0,
            "daily_return": np.mean(returns) if len(returns) > 0 else 0,
            "volatility": np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0
        } 