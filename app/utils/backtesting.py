import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from app.utils.data_fetcher import DataFetcher
from app.utils.technical_analysis import TechnicalAnalysis
from app.utils.risk_management import RiskManager
from app.core.config import settings

class Backtester:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.technical_analysis = TechnicalAnalysis()
        self.risk_manager = RiskManager()

    def run(self, strategy_id: int, symbol: str, start_date: str, end_date: str, initial_balance: float) -> Dict[str, Any]:
        """
        Run backtest for a strategy
        """
        # Get historical data
        data = self.data_fetcher.get_historical_data(symbol, start_date, end_date)
        if data.empty:
            return {
                "final_balance": initial_balance,
                "total_return": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0,
                "win_rate": 0,
                "metrics": {}
            }

        # Get strategy parameters
        strategy = self.data_fetcher.get_strategy(strategy_id)
        if not strategy:
            return {
                "final_balance": initial_balance,
                "total_return": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0,
                "win_rate": 0,
                "metrics": {}
            }

        # Initialize backtest variables
        balance = initial_balance
        position = 0
        trades = []
        equity_curve = [initial_balance]

        # Run backtest
        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            current_price = current_data['close'].iloc[-1]

            # Generate signals
            signals = self.technical_analysis.analyze(
                symbol=symbol,
                strategy_type=strategy.type,
                parameters=strategy.parameters
            )

            # Process signals
            for signal in signals:
                if signal["type"] == "buy" and position <= 0:
                    # Calculate position size
                    quantity, stop_loss, take_profit = self.risk_manager.calculate_position_size(
                        portfolio_value=balance,
                        symbol=symbol
                    )

                    if quantity > 0:
                        # Execute buy
                        cost = quantity * current_price
                        if cost <= balance:
                            position = quantity
                            balance -= cost
                            trades.append({
                                "date": current_data.index[-1],
                                "action": "buy",
                                "quantity": quantity,
                                "price": current_price,
                                "stop_loss": stop_loss,
                                "take_profit": take_profit
                            })

                elif signal["type"] == "sell" and position >= 0:
                    # Execute sell
                    if position > 0:
                        proceeds = position * current_price
                        balance += proceeds
                        trades.append({
                            "date": current_data.index[-1],
                            "action": "sell",
                            "quantity": position,
                            "price": current_price
                        })
                        position = 0

            # Check stop loss and take profit
            if position > 0:
                last_trade = next((t for t in reversed(trades) if t["action"] == "buy"), None)
                if last_trade:
                    if current_price <= last_trade["stop_loss"] or current_price >= last_trade["take_profit"]:
                        proceeds = position * current_price
                        balance += proceeds
                        trades.append({
                            "date": current_data.index[-1],
                            "action": "sell",
                            "quantity": position,
                            "price": current_price,
                            "reason": "stop_loss" if current_price <= last_trade["stop_loss"] else "take_profit"
                        })
                        position = 0

            # Update equity curve
            current_equity = balance + (position * current_price)
            equity_curve.append(current_equity)

        # Calculate performance metrics
        equity_curve = np.array(equity_curve)
        returns = np.diff(equity_curve) / equity_curve[:-1]
        
        total_return = (equity_curve[-1] - initial_balance) / initial_balance
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0
        
        # Calculate maximum drawdown
        running_max = np.maximum.accumulate(equity_curve)
        drawdowns = (equity_curve - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        # Calculate win rate
        winning_trades = sum(1 for t in trades if t["action"] == "sell" and t["price"] > t["price"])
        total_trades = len([t for t in trades if t["action"] == "sell"])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        return {
            "final_balance": equity_curve[-1],
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "metrics": {
                "num_trades": total_trades,
                "winning_trades": winning_trades,
                "average_return": np.mean(returns) if len(returns) > 0 else 0,
                "volatility": np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0,
                "equity_curve": equity_curve.tolist(),
                "trades": trades
            }
        }

    def optimize_parameters(self, strategy_id: int, symbol: str, start_date: str, end_date: str, 
                          initial_balance: float, param_grid: Dict[str, List[Any]]) -> Dict[str, Any]:
        """
        Optimize strategy parameters using grid search
        """
        best_result = None
        best_sharpe = float('-inf')
        
        # Generate parameter combinations
        param_combinations = self._generate_param_combinations(param_grid)
        
        # Test each parameter combination
        for params in param_combinations:
            # Update strategy parameters
            strategy = self.data_fetcher.get_strategy(strategy_id)
            if not strategy:
                continue
                
            strategy.parameters.update(params)
            
            # Run backtest
            result = self.run(
                strategy_id=strategy_id,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                initial_balance=initial_balance
            )
            
            # Update best result
            if result["sharpe_ratio"] > best_sharpe:
                best_sharpe = result["sharpe_ratio"]
                best_result = {
                    "parameters": params,
                    "metrics": result
                }
        
        return best_result

    def _generate_param_combinations(self, param_grid: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        Generate all combinations of parameters from grid
        """
        import itertools
        
        keys = param_grid.keys()
        values = param_grid.values()
        
        combinations = []
        for combination in itertools.product(*values):
            combinations.append(dict(zip(keys, combination)))
        
        return combinations 